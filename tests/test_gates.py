import numpy as np
import pandas as pd
import pytest

from qresearch import gates
from qresearch.trades import TRADE_COLUMNS


def eq_df(values, start="2010-01-04"):
    d = pd.bdate_range(start, periods=len(values)).strftime("%Y-%m-%d")
    return pd.DataFrame({"date": d, "equity": values, "cash": 0.0})


def trades_df(rets):
    rows = [dict(symbol_id=f"S{i}", symbol="X", entry_date="2011-01-03", exit_date="2011-01-14", status="closed",
                 cost=1000.0, proceeds=1000.0 * (1 + r), fees=14.0, pnl=1000.0 * r, ret=r, n_fills=2, max_qty=1,
                 exit_tag="x") for i, r in enumerate(rets)]
    return pd.DataFrame(rows, columns=TRADE_COLUMNS)


def test_episode_drawdown_and_year_share():
    s = pd.Series([100, 110, 99, 120.0], index=["2011-06-30", "2011-07-05", "2011-08-08", "2011-11-01"])
    assert gates.episode_drawdown(s, "2011-07-01", "2011-10-31") == pytest.approx(99 / 110 - 1)
    e = pd.Series([100.0, 150.0, 160.0], index=["2010-01-04", "2010-12-31", "2011-12-30"])
    assert gates.yearly_profit_share(e) == pytest.approx(50 / 60)


def test_strong_strategy_passes_and_weak_fails():
    rng = np.random.default_rng(0)
    n = 2010
    bench = 100 * np.cumprod(1 + rng.normal(0.0003, 0.01, n))
    strong = 100 * np.cumprod(1 + rng.normal(0.0012, 0.008, n))
    good_trades = trades_df(list(rng.normal(0.01, 0.03, 400)))
    chk = gates.is_screen(eq_df(strong), good_trades, eq_df(bench))
    assert gates.passed(chk), [c for c in chk if not c["ok"]]
    good_bench = 100 * np.cumprod(1 + rng.normal(0.0006, 0.008, n))      # benchmark Sharpe ~1.2
    weak = 100 * np.cumprod(1 + rng.normal(0.0001, 0.012, n))
    chk2 = gates.is_screen(eq_df(weak), trades_df(list(rng.normal(-0.001, 0.03, 50))), eq_df(good_bench))
    failed = {c["gate"] for c in chk2 if not c["ok"]}
    assert {"closed trades", "Sharpe", "Sharpe vs EW + 0.1"} <= failed


def test_thirds():
    v = list(100 * np.cumprod(np.full(300, 1.001)))
    assert all(x == x for x in gates.thirds_positive(eq_df(v)))
