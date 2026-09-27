"""The single shared metrics module. Every strategy and benchmark is measured with this code.

Conventions (see DECISIONS.md):
  * Daily returns are close-to-close changes of total portfolio equity (includes dividends, costs).
  * Annualisation uses 252 trading days. Sharpe and Sortino use a 0% risk-free rate.
  * Trade statistics come from round-trip trades (price PnL net of fees, dividends excluded).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def returns_from_equity(equity: pd.Series) -> pd.Series:
    equity = equity.astype(float)
    return equity.pct_change().dropna()


def cagr(equity: pd.Series) -> float:
    idx = pd.to_datetime(equity.index)
    years = (idx[-1] - idx[0]).days / 365.25
    if years <= 0 or equity.iloc[0] <= 0:
        return float("nan")
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / years) - 1.0)


def sharpe(r: pd.Series) -> float:
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")


def sortino(r: pd.Series) -> float:
    dd = math.sqrt(float((np.minimum(r, 0.0) ** 2).mean()))
    return float(r.mean() / dd * math.sqrt(TRADING_DAYS)) if dd > 0 else float("nan")


def drawdown_series(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1.0


def max_drawdown(equity: pd.Series) -> float:
    return float(drawdown_series(equity).min())


def max_drawdown_duration(equity: pd.Series) -> int:
    """Longest stretch (in trading days) spent below a previous equity peak."""
    under = (drawdown_series(equity) < 0).to_numpy()
    best = cur = 0
    for u in under:
        cur = cur + 1 if u else 0
        best = max(best, cur)
    return int(best)


def period_returns(equity: pd.Series, freq: str) -> pd.Series:
    """Calendar-period returns ('YE' yearly, 'ME' monthly), first period measured from the start."""
    e = equity.copy()
    e.index = pd.to_datetime(e.index)
    last = e.resample(freq).last()
    prev = last.shift(1)
    prev.iloc[0] = e.iloc[0]
    return (last / prev - 1.0).dropna()


def trade_stats(trades: pd.DataFrame) -> dict:
    closed = trades[trades["status"] == "closed"] if len(trades) else trades
    n = int(len(closed))
    if n == 0:
        return dict(n_trades=0, n_open_trades=int(len(trades)), win_rate=float("nan"),
                    avg_win=float("nan"), avg_loss=float("nan"), expectancy=float("nan"),
                    profit_factor=float("nan"), avg_holding_days=float("nan"))
    ret = closed["ret"].astype(float)
    pnl = closed["pnl"].astype(float)
    wins, losses = ret[ret > 0], ret[ret <= 0]
    gross_win, gross_loss = pnl[pnl > 0].sum(), -pnl[pnl < 0].sum()
    hold = (pd.to_datetime(closed["exit_date"]) - pd.to_datetime(closed["entry_date"])).dt.days
    return dict(
        n_trades=n,
        n_open_trades=int((trades["status"] == "open").sum()),
        win_rate=float(len(wins) / n),
        avg_win=float(wins.mean()) if len(wins) else float("nan"),
        avg_loss=float(losses.mean()) if len(losses) else float("nan"),
        expectancy=float(ret.mean()),
        profit_factor=float(gross_win / gross_loss) if gross_loss > 0 else float("inf"),
        avg_holding_days=float(hold.mean()),
    )


def turnover(fills: pd.DataFrame, equity: pd.Series) -> float:
    """Annualised one-way turnover: traded value / 2 / average equity / years."""
    if len(fills) == 0:
        return 0.0
    traded = float((fills["quantity"].abs() * fills["price"]).sum())
    idx = pd.to_datetime(equity.index)
    years = max((idx[-1] - idx[0]).days / 365.25, 1e-9)
    return traded / 2.0 / float(equity.mean()) / years


def benchmark_relative(r: pd.Series, rb: pd.Series, equity: pd.Series, bench_equity: pd.Series) -> dict:
    j = pd.concat([r, rb], axis=1, join="inner").dropna()
    if len(j) < 3:
        return dict(excess_cagr=float("nan"), beta=float("nan"), correlation=float("nan"))
    a, b = j.iloc[:, 0], j.iloc[:, 1]
    var_b = b.var(ddof=1)
    common = equity.index.intersection(bench_equity.index)
    return dict(
        excess_cagr=cagr(equity.loc[common]) - cagr(bench_equity.loc[common]),
        beta=float(a.cov(b) / var_b) if var_b > 0 else float("nan"),
        correlation=float(a.corr(b)),
    )


def compute_metrics(equity_df: pd.DataFrame, trades: pd.DataFrame | None = None,
                    fills: pd.DataFrame | None = None,
                    benchmark: pd.Series | None = None) -> dict:
    """equity_df: columns date, equity, cash (cash optional). Returns a flat dict of metrics."""
    eq = pd.Series(equity_df["equity"].to_numpy(dtype=float),
                   index=pd.Index(equity_df["date"].astype(str)))
    r = returns_from_equity(eq)
    yearly = period_returns(eq, "YE")
    monthly = period_returns(eq, "ME")
    mdd = max_drawdown(eq)
    c = cagr(eq)
    m = dict(
        start=str(eq.index[0]), end=str(eq.index[-1]), n_days=int(len(eq)),
        final_equity=float(eq.iloc[-1]),
        total_return=float(eq.iloc[-1] / eq.iloc[0] - 1.0),
        cagr=c,
        ann_return=float(r.mean() * TRADING_DAYS),
        ann_volatility=float(r.std(ddof=1) * math.sqrt(TRADING_DAYS)),
        sharpe=sharpe(r), sortino=sortino(r),
        max_drawdown=mdd, max_drawdown_duration_days=max_drawdown_duration(eq),
        calmar=float(c / abs(mdd)) if mdd < 0 else float("nan"),
        worst_year=float(yearly.min()) if len(yearly) else float("nan"),
        worst_month=float(monthly.min()) if len(monthly) else float("nan"),
        best_year=float(yearly.max()) if len(yearly) else float("nan"),
        pct_positive_years=float((yearly > 0).mean()) if len(yearly) else float("nan"),
        yearly_returns={str(k.year): float(v) for k, v in yearly.items()},
        skew=float(r.skew()), kurtosis=float(r.kurt() + 3.0),
    )
    if "cash" in equity_df:
        gross = 1.0 - equity_df["cash"].to_numpy(dtype=float) / equity_df["equity"].to_numpy(dtype=float)
        m["exposure_mean"] = float(np.mean(gross))
        m["exposure_days_frac"] = float(np.mean(gross > 0.01))
        m["min_cash_frac"] = float(np.min(1.0 - gross))
    if trades is not None:
        m.update(trade_stats(trades))
    if fills is not None:
        m["turnover"] = turnover(fills, eq)
    if benchmark is not None:
        rb = returns_from_equity(benchmark)
        m.update(benchmark_relative(r, rb, eq, benchmark))
    return m


def slice_equity(equity_df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    d = equity_df["date"].astype(str)
    return equity_df[(d >= start) & (d <= end)].reset_index(drop=True)
