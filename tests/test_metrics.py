import math

import numpy as np
import pandas as pd
import pytest

from qresearch import metrics


def eq_df(values, start="2001-01-01"):
    idx = pd.bdate_range(start, periods=len(values)).strftime("%Y-%m-%d")
    return pd.DataFrame({"date": idx, "equity": values, "cash": [0.0] * len(values)})


def test_constant_growth_cagr_and_zero_vol():
    n = 253
    daily = 1.10 ** (1 / 252) - 1
    df = eq_df([100 * (1 + daily) ** i for i in range(n)])
    m = metrics.compute_metrics(df)
    days = (pd.Timestamp(df.date.iloc[-1]) - pd.Timestamp(df.date.iloc[0])).days
    assert m["cagr"] == pytest.approx((df.equity.iloc[-1] / 100) ** (365.25 / days) - 1, rel=1e-12)
    assert m["ann_volatility"] == pytest.approx(0.0, abs=1e-12)
    assert m["max_drawdown"] == 0.0
    assert math.isnan(m["calmar"])


def test_sharpe_sortino_known_values():
    r = np.array([0.01, -0.005, 0.02, -0.01, 0.0, 0.015])
    s = pd.Series(r)
    assert metrics.sharpe(s) == pytest.approx(r.mean() / r.std(ddof=1) * math.sqrt(252))
    dd = math.sqrt(np.mean(np.minimum(r, 0) ** 2))
    assert metrics.sortino(s) == pytest.approx(r.mean() / dd * math.sqrt(252))


def test_drawdown_and_duration():
    e = pd.Series([100, 120, 90, 95, 130, 100, 100, 131.0])
    assert metrics.max_drawdown(e) == pytest.approx(90 / 120 - 1)
    assert metrics.max_drawdown_duration(e) == 2     # two 2-day stretches below a prior peak
    assert metrics.max_drawdown_duration(pd.Series([1.0, 0.9, 0.8, 0.95, 1.0, 1.1])) == 3  # back at the peak = recovered


def test_calendar_returns():
    idx = ["2001-12-28", "2001-12-31", "2002-06-28", "2002-12-31", "2003-01-02"]
    e = pd.Series([100.0, 110.0, 99.0, 121.0, 60.5], index=idx)
    y = metrics.period_returns(e, "YE")
    assert list(y.round(10)) == [0.1, 0.1, -0.5]


def test_trade_stats():
    t = pd.DataFrame(dict(status=["closed"] * 4 + ["open"], ret=[0.1, -0.05, 0.2, -0.05, np.nan],
                          pnl=[100.0, -50.0, 200.0, -50.0, np.nan],
                          entry_date=["2001-01-01"] * 5, exit_date=["2001-01-11"] * 4 + [""]))
    s = metrics.trade_stats(t)
    assert s["n_trades"] == 4 and s["n_open_trades"] == 1
    assert s["win_rate"] == 0.5
    assert s["profit_factor"] == pytest.approx(3.0)
    assert s["expectancy"] == pytest.approx(0.05)
    assert s["avg_win"] == pytest.approx(0.15) and s["avg_loss"] == pytest.approx(-0.05)
    assert s["avg_holding_days"] == 10


def test_benchmark_relative_beta():
    rng = np.random.default_rng(3)
    rb = pd.Series(rng.normal(0.0004, 0.01, 1000))
    b = 100 * (1 + rb).cumprod()
    r2 = 2 * rb
    e2 = 100 * (1 + r2).cumprod()
    out = metrics.benchmark_relative(r2, rb, e2, b)
    assert out["beta"] == pytest.approx(2.0) and out["correlation"] == pytest.approx(1.0)


def test_turnover_and_exposure():
    df = eq_df([100.0, 100.0, 100.0])
    df["cash"] = [100.0, 50.0, 0.0]
    fills = pd.DataFrame(dict(quantity=[10.0, -10.0], price=[5.0, 5.0]))
    m = metrics.compute_metrics(df, fills=fills)
    assert m["exposure_mean"] == pytest.approx(0.5)
    assert m["min_cash_frac"] == 0.0
    years = 2 / 365.25
    assert m["turnover"] == pytest.approx(100 / 2 / 100 / years)
