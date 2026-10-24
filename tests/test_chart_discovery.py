"""TT chart discovery (D302): sampling rules and the blinded renderer, on synthetic fixtures only (no WIKI data)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "tt" / "chart_discovery"))
import render as rd  # noqa: E402
import sample as sp  # noqa: E402

DATES = [str(d.date()) for d in pd.bdate_range("2012-01-02", periods=400)]


def ticker_rows(n=400, seed=0, ticker="AAA"):
    rng = np.random.default_rng(seed)
    c = 20 * np.exp(np.cumsum(rng.normal(0, 0.015, n)))
    o = c * np.exp(rng.normal(0, 0.005, n))
    df = pd.DataFrame({"ticker": ticker, "date": DATES[:n], "open": o, "high": np.maximum(o, c) * 1.01,
                       "low": np.minimum(o, c) * 0.99, "close": c, "volume": rng.uniform(1e5, 1e6, n),
                       "ex-dividend": 0.0, "split_ratio": 1.0})
    for k in ("open", "high", "low", "close", "volume"):
        df["adj_" + k] = df[k]
    return df


def test_render_ignores_future_bars_byte_for_byte():
    g = ticker_rows()
    t = DATES[300]
    a, last_a = rd.chart_png(g[g["date"] <= t], t)
    fut = g.copy()
    fut.loc[fut["date"] > t, ["adj_close", "adj_high"]] *= 3.0           # any later change must not matter
    b, last_b = rd.chart_png(fut, t)
    assert a == b and last_a == last_b == t
    assert a[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_needs_252_bars():
    g = ticker_rows(n=260)
    try:
        rd.chart_png(g, DATES[200])
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_sma_partial_window_is_nan():
    x = np.arange(1.0, 11.0)
    s = rd.sma(x, 4)
    assert np.isnan(s[:3]).all() and s[3] == 2.5 and s[-1] == 8.5


def test_largest_remainder_sums_and_is_proportional():
    out = sp.largest_remainder({"a": 55367, "b": 4002, "c": 30}, 300)
    assert sum(out.values()) == 300 and out["c"] == 0 and out["b"] in (20, 21)


def test_exit_group():
    assert sp.exit_group({"leaver_month": False, "exit_type": "ACQUIRED"}) == "CONTINUING"
    assert sp.exit_group({"leaver_month": True, "exit_type": "UNKNOWN"}) == "STOPPED-FILING-ONLY"
    assert sp.exit_group({"leaver_month": True, "exit_type": "FAILED"}) == "FAILED"


def test_bad_flags_and_unexplained_ratio():
    g = ticker_rows(n=10)
    g.loc[3, "split_ratio"] = 2.0                                       # split row -> excluded window
    g.loc[6, "adj_close"] = g.loc[6, "close"] * 0.9                      # ratio change without an event
    g.loc[6, "adj_low"] = min(g.loc[6, "adj_low"], g.loc[6, "adj_close"])
    f = sp.bad_flags(g)
    assert f[3] and not f[1]
    assert sp.unexplained_tickers(g) == {"AAA"}
    assert sp.unexplained_tickers(ticker_rows(n=10)) == set()
