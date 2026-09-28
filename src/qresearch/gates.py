"""Promotion gates (D036, approved 2026-09-28). Computed, never judged.

IS screen, evaluated per variation against the equal-weight benchmark over the same dates:
  trades >= 100; Sharpe >= 0.5 and >= EW Sharpe + 0.1; max DD <= 35% and no worse than EW;
  in each IS stress episode, drawdown no more than 5 points worse than EW's; profit factor >= 1.2;
  95% bootstrap CI of expectancy above 0; positive in >= 5 of 8 years; no year > 40% of profit;
  expectancy > 0 without the best 5% of trades.
The "Sharpe >= 0.4 at 2x slippage" condition needs a separate run and is checked in robustness.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import metrics, stats

IS_EPISODES = {
    "2010 May-Jun (flash crash)": ("2010-04-23", "2010-07-02"),
    "2011 Jul-Oct (US downgrade)": ("2011-07-01", "2011-10-31"),
    "2015 Aug-2016 Feb (China/oil)": ("2015-08-01", "2016-02-29"),
}


def _series(equity_df: pd.DataFrame) -> pd.Series:
    return pd.Series(equity_df["equity"].to_numpy(float), index=equity_df["date"].astype(str))


def episode_drawdown(eq: pd.Series, start: str, end: str) -> float:
    """Worst drawdown inside the window, measured from the running peak that starts at the window."""
    w = eq[(eq.index >= start) & (eq.index <= end)]
    if len(w) < 2:
        return float("nan")
    return float((w / w.cummax() - 1.0).min())


def yearly_profit_share(eq: pd.Series) -> float:
    """Largest single calendar year's share of total dollar profit (nan if total profit <= 0)."""
    e = eq.copy()
    e.index = pd.to_datetime(e.index)
    ends = e.resample("YE").last()
    starts = ends.shift(1)
    starts.iloc[0] = e.iloc[0]
    pnl = ends - starts
    total = float(e.iloc[-1] - e.iloc[0])
    if total <= 0:
        return float("nan")
    return float(pnl.max() / total)


def is_screen(equity_df: pd.DataFrame, trades: pd.DataFrame, bench_df: pd.DataFrame) -> list[dict]:
    eq = _series(equity_df)
    b = _series(bench_df)
    b = b[(b.index >= eq.index[0]) & (b.index <= eq.index[-1])]
    m = metrics.compute_metrics(equity_df, trades)
    mb = metrics.compute_metrics(pd.DataFrame({"date": b.index, "equity": b.values}))
    closed = trades[trades["status"] == "closed"] if len(trades) else trades
    out = []

    def add(name, ok, value, need):
        out.append(dict(gate=name, ok=bool(ok), value=value, required=need))

    add("closed trades", m.get("n_trades", 0) >= 100, m.get("n_trades", 0), ">= 100")
    add("Sharpe", m["sharpe"] >= 0.5, round(m["sharpe"], 3), ">= 0.50")
    add("Sharpe vs EW + 0.1", m["sharpe"] >= mb["sharpe"] + 0.1, round(m["sharpe"] - mb["sharpe"], 3),
        f">= +0.10 (EW {mb['sharpe']:.2f})")
    add("max drawdown", m["max_drawdown"] >= -0.35 and m["max_drawdown"] >= mb["max_drawdown"],
        round(m["max_drawdown"], 3), f">= -0.35 and >= EW {mb['max_drawdown']:.3f}")
    for name, (a, z) in IS_EPISODES.items():
        s, e = episode_drawdown(eq, a, z), episode_drawdown(b, a, z)
        add(f"episode {name}", s >= e - 0.05, round(s, 3), f">= EW {e:.3f} - 0.05")
    pf = m.get("profit_factor", float("nan"))
    add("profit factor", pf >= 1.2, round(pf, 3) if pf == pf else pf, ">= 1.20")
    lo = stats.bootstrap_mean_ci(closed["ret"].to_numpy(float))[0] if len(closed) > 1 else float("nan")
    add("expectancy 95% CI lower bound", lo > 0, round(lo, 5) if lo == lo else lo, "> 0")
    yr = m.get("yearly_returns", {})
    pos = sum(1 for v in yr.values() if v > 0)
    add("positive years", pos >= 5, f"{pos}/{len(yr)}", ">= 5 of 8")
    share = yearly_profit_share(eq)
    add("largest year share of profit", share == share and share <= 0.40, round(share, 3) if share == share else share, "<= 0.40")
    n = len(closed)
    ex = stats.expectancy_without_best(closed["ret"], max(1, math.ceil(0.05 * n))) if n else float("nan")
    add("expectancy without best 5%", ex == ex and ex > 0, round(ex, 5) if ex == ex else ex, "> 0")
    return out


def passed(checks: list[dict]) -> bool:
    return all(c["ok"] for c in checks)


def thirds_positive(equity_df: pd.DataFrame) -> list[float]:
    """Sharpe in each third of the period (robustness gate: each must be > 0)."""
    eq = _series(equity_df)
    parts = np.array_split(np.arange(len(eq)), 3)
    return [metrics.sharpe(metrics.returns_from_equity(eq.iloc[p])) for p in parts]
