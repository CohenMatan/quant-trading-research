"""C02 infrastructure: shared indicators, event slot planning, harness OHLC / month-end windows,
entry bookkeeping. Pure functions are checked against independent reference calculations."""
import types
from collections import deque

import numpy as np
import pandas as pd
import pytest

import qr_indicators as qi


def _ohlc(n=300, seed=3):
    rng = np.random.default_rng(seed)
    c = 50 * np.exp(np.cumsum(rng.normal(0, 0.015, n)))
    o = c * (1 + rng.normal(0, 0.004, n))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.006, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.006, n)))
    v = rng.integers(1_000_000, 3_000_000, n).astype(float)
    return o, h, l, c, v


def test_indicators_match_pandas_references():
    o, h, l, c, v = _ohlc()
    s = pd.Series(c)
    assert qi.sma(c, 20) == pytest.approx(s.rolling(20).mean().iloc[-1])
    assert qi.stdev(c, 20) == pytest.approx(s.rolling(20).std().iloc[-1])
    assert qi.median(v[-50:]) == pytest.approx(float(np.median(v[-50:])))
    prev = pd.Series(c).shift(1)
    tr = pd.concat([pd.Series(h), prev], axis=1).max(axis=1) - pd.concat([pd.Series(l), prev], axis=1).min(axis=1)
    assert qi.atr(h, l, c, 20) == pytest.approx(tr.iloc[1:].rolling(20).mean().iloc[-1])
    assert qi.bandwidth(c, 20, 2.0) == pytest.approx(4 * s.rolling(20).std().iloc[-1] / s.rolling(20).mean().iloc[-1])
    assert qi.sma(c[:5], 20) is None and qi.atr(h[:10], l[:10], c[:10], 20) is None


def test_pct_rank_last():
    assert qi.pct_rank_last([5, 4, 3, 2, 1, 0.5], 5) == 0.0
    assert qi.pct_rank_last([1, 2, 3, 4, 5, 6], 5) == 1.0
    assert qi.pct_rank_last([1, 2], 5) is None


def test_event_slot_planning():
    # 10 slots: 7 held (2 exiting, still occupying their slots until sold, D051), 1 pending buy
    held = [f"H{i}" for i in range(7)]
    t = qi.plan_event_targets(held, {"H0", "H1"}, {"P"}, ["H3", "P", "A", "B", "C", "D"], 10, 0.1)
    assert t == {"H0": 0.0, "H1": 0.0, "A": 0.1, "B": 0.1}            # 10 - 7 held - 1 pending = 2 free
    assert qi.plan_event_targets([], set(), set(), ["A", "A", "B"], 1, 0.1) == {"A": 0.1}
    assert qi.plan_event_targets(held, set(), set(), ["X"], 5, 0.1) == {}   # full: no entries


# ---------------------------------------------------------------- harness bookkeeping (stubbed LEAN)
@pytest.fixture
def algo(monkeypatch):
    from test_commission import _load_harness
    h = _load_harness(monkeypatch)
    a = object.__new__(h.QRAlgorithm)
    a.USES_OHLC, a.WINDOW_BARS, a.MONTHLY_BARS = True, 5, 24
    a.qr_close, a.qr_volume, a.qr_open, a.qr_high, a.qr_low = {}, {}, {}, {}, {}
    a.qr_month_close, a._qr_month_last, a._qr_entry = {}, {}, {}
    a._qr_session = 7
    a.time = pd.Timestamp("2014-06-09")
    return a


def test_split_and_dividend_rescale_every_kept_series(algo):
    s = "AAPL"
    for store, vals in ((algo.qr_close, [700.0, 707.0]), (algo.qr_open, [698.0, 701.0]),
                        (algo.qr_high, [705.0, 709.0]), (algo.qr_low, [695.0, 699.0]), (algo.qr_volume, [1e6, 2e6])):
        store[s] = deque(vals, maxlen=5)
    algo.qr_month_close[s] = deque([[201404, 590.0], [201405, 630.0]], maxlen=24)
    algo._qr_month_last[s] = [201406, 645.0]
    algo._qr_rescale(s, 1 / 7, volume_factor=7)                       # AAPL 7:1 split
    assert list(algo.qr_close[s]) == pytest.approx([100.0, 101.0])
    assert list(algo.qr_open[s]) == pytest.approx([698 / 7, 701 / 7]) and list(algo.qr_low[s])[0] == pytest.approx(695 / 7)
    assert list(algo.qr_volume[s]) == pytest.approx([7e6, 14e6])
    assert [c for _, c in algo.qr_month_close[s]] == pytest.approx([590 / 7, 90.0])
    assert algo._qr_month_last[s][1] == pytest.approx(645 / 7)
    algo._qr_rescale(s, 0.99, volume_factor=None)                     # dividend: prices only
    assert list(algo.qr_high[s])[1] == pytest.approx(709 / 7 * 0.99)
    assert list(algo.qr_volume[s]) == pytest.approx([7e6, 14e6])
    assert algo.qr_close[s].maxlen == 5 and algo.qr_month_close[s].maxlen == 24


def test_month_end_close_rolls_only_when_a_new_month_starts(algo):
    s = "KO"
    algo.qr_month_close[s] = deque(maxlen=24)
    algo._qr_month_step(s, 201401, 40.0)
    algo._qr_month_step(s, 201401, 41.0)                              # still January: no month-end yet
    assert list(algo.qr_month_close[s]) == []
    algo._qr_month_step(s, 201402, 39.0)                              # first February bar: Jan closes at 41
    assert list(algo.qr_month_close[s]) == [[201401, 41.0]]
    assert algo._qr_month_last[s] == [201402, 39.0]


def test_entry_bookkeeping(algo):
    held = {"X": 0.0}
    algo.portfolio = {"X": types.SimpleNamespace(quantity=0.0)}

    def fill(q_after, px):
        algo.portfolio["X"].quantity = q_after
        algo._qr_update_entry(types.SimpleNamespace(symbol="X", fill_price=px))
    algo._qr_session_day = algo.time.date()                            # the fill-day bar was already counted
    fill(100.0, 10.0)
    assert algo.qr_sessions_held("X") == 0 and algo._qr_entry["X"]["price"] == 10.0
    algo._qr_session = 12
    fill(150.0, 11.0)                                                   # adding to a position keeps the entry
    assert algo.qr_sessions_held("X") == 5
    fill(0.0, 12.0)
    assert algo.qr_sessions_held("X") is None


def test_entry_session_does_not_depend_on_lean_event_order(algo):
    """The open fill may arrive before the fill day's bar is counted; held must still be 0 that day."""
    algo.portfolio = {"X": types.SimpleNamespace(quantity=100.0)}
    algo._qr_session_day = (algo.time - pd.Timedelta(days=1)).date()  # signal day T counted, T+1 not yet
    algo._qr_update_entry(types.SimpleNamespace(symbol="X", fill_price=10.0))
    algo._qr_session += 1                                               # then the T+1 bar is counted
    algo._qr_session_day = algo.time.date()
    assert algo.qr_sessions_held("X") == 0


def test_c02_windows_are_opt_in_and_old_strategies_unchanged(root):
    src = (root / "src/qresearch/lean/qr_harness.py").read_text()
    assert "USES_OHLC = False" in src and "MONTHLY_BARS = 0" in src
    for sdir in ("S001_trend_reversal", "S002_momentum", "S003_52w_high", "S004_momentum_pullback", "S005_low_vol"):
        main = (root / "strategies" / sdir / "main.py").read_text()
        assert "USES_OHLC" not in main and "MONTHLY_BARS" not in main


def test_runner_ships_the_indicator_module(root):
    from qresearch import run
    files = run.assemble_files(dict(strategy_dir="strategies/S006_breakout", experiment_id="E006-01", start="2010-01-04",
                                    end="2017-12-29", cash=100000, universe={}, costs={}, portfolio={}, params={}),
                               None, False)
    assert "qr_indicators.py" in files and "signals.py" in files and "main.py" in files
