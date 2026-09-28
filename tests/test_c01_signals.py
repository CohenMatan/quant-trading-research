"""C01 signal modules: look-ahead (truncation) tests and hand-checked values."""
import math

import numpy as np
import pandas as pd
import pytest

from qresearch.lookahead import truncation_violations
from conftest import ROOT, load_module

S1 = load_module(ROOT / "strategies/S001_trend_reversal/signals.py", "s1")
S2 = load_module(ROOT / "strategies/S002_momentum/signals.py", "s2")
S3 = load_module(ROOT / "strategies/S003_52w_high/signals.py", "s3")
S4 = load_module(ROOT / "strategies/S004_momentum_pullback/signals.py", "s4")
S5 = load_module(ROOT / "strategies/S005_low_vol/signals.py", "s5")

P1 = {"rsi_max": 10, "max_hold": 10, "exit": "sma5"}


def prices(n=700, seed=3, drift=0.0005):
    rng = np.random.default_rng(seed)
    return pd.Series(100 * np.exp(np.cumsum(rng.normal(drift, 0.02, n))), index=pd.bdate_range("2010-01-04", periods=n))


def rolling(fn, window):
    return lambda s: s.rolling(window, min_periods=1).apply(lambda w: np.nan if (v := fn(list(w))) is None else v, raw=True)


@pytest.mark.parametrize("fn,window", [
    (lambda c: S1.entry_score(c, P1), 260),
    (lambda c: S1.entry_score(c, dict(P1, entry="ret3", ret3_max=-0.06)), 260),
    (lambda c: S1.rsi(c, 2), 10),
    (lambda c: S2.mom(c, 252, 21), 260),
    (lambda c: S2.mom(c, 126, 21), 260),
    (lambda c: S3.proximity(c), 260),
    (lambda c: S4.ret_between(c, 131, 5), 140),
    (lambda c: S4.ret_between(c, 5, 0), 140),
    (lambda c: S5.vol(c, 63), 260),
    (lambda c: S5.vol(c, 252), 260),
])
def test_no_lookahead(fn, window):
    assert truncation_violations(rolling(fn, window), prices(), n_checks=40) == []


def test_rsi_and_sma_hand_values():
    assert S1.rsi([10, 11, 12], 2) == 100.0
    assert S1.rsi([12, 11, 10], 2) == 0.0
    assert S1.rsi([10, 12, 11], 2) == pytest.approx(100 - 100 / (1 + 2 / 1))
    assert S1.sma([1, 2, 3, 4], 2) == 3.5 and S1.sma([1], 2) is None


def test_s001_entry_requires_uptrend_and_oversold():
    up = [100 + i * 0.5 for i in range(220)]
    dip = up + [up[-1] - 2, up[-1] - 4]                   # sharp 2-day drop, still above SMA200
    assert S1.entry_score(up, P1) is None                  # not oversold
    assert S1.entry_score(dip, P1) == 0.0                  # RSI(2) = 0
    down = [200 - i * 0.5 for i in range(220)]
    assert S1.entry_score(down + [down[-1] - 3], P1) is None   # below SMA200


def test_s001_exits():
    c = [10.0] * 10 + [11.0]
    assert S1.exit_signal(c, 3, P1)                        # close > SMA5
    assert S1.exit_signal([10.0] * 11, 10, P1)             # max hold
    assert not S1.exit_signal(c, 3, dict(P1, exit="time"))


def test_momentum_and_rankings():
    c = list(range(1, 300))
    assert S2.mom(c, 252, 21) == pytest.approx(c[-22] / c[-253] - 1)
    w = {"A": [1.0] * 253 + [2.0] * 22, "B": [1.0] * 253 + [1.5] * 22, "C": [1.0] * 10}
    assert S2.top_by_momentum(w, 252, 21, 5) == ["A", "B"]
    assert S2.is_rebalance_month(2011, 1, 2) and not S2.is_rebalance_month(2011, 2, 2) and S2.is_rebalance_month(2011, 3, 2)


def test_proximity_and_filters():
    assert S3.proximity([1.0] * 251 + [2.0]) == 1.0
    w = {"A": [1.0] * 260, "B": [2.0] * 100 + [1.0] * 160}
    assert S3.top_by_proximity(w, 1, False) == ["A"]
    assert S3.top_by_proximity(w, 5, True) == []           # flat A: 12-1 return is 0 -> excluded


def test_pullback_logic():
    base = [100 * (1.01 ** i) for i in range(136)]
    lead = base[:-5] + [base[-6] * 0.93] * 5              # leader, then -7% over the last 5 days
    flat = [100.0] * 136
    w = {"L": lead, "F": flat}
    L = S4.leaders(w, 0.5)
    assert L == {"L"}
    assert S4.pullback_entries(w, L, 0.05, set(), 5) == ["L"]
    assert S4.pullback_entries(w, L, 0.08, set(), 5) == []
    assert S4.pullback_entries(w, L, 0.05, {"L"}, 5) == []


def test_low_vol():
    calm = [100 * (1.0001 ** i) for i in range(260)]
    wild = [100 * (1.05 if i % 2 else 0.96) ** (i % 3) for i in range(260)]
    assert S5.vol(calm, 63) == pytest.approx(0.0, abs=1e-9)
    assert S5.lowest_vol({"calm": calm, "wild": wild}, 63, 1, False) == ["calm"]


def test_lean_algorithms_use_pure_signal_modules():
    for d, fn in (("S001_trend_reversal", "entry_score"), ("S002_momentum", "top_by_momentum"),
                  ("S003_52w_high", "top_by_proximity"), ("S004_momentum_pullback", "pullback_entries"),
                  ("S005_low_vol", "lowest_vol")):
        src = (ROOT / "strategies" / d / "main.py").read_text()
        assert f"from signals import" in src and fn in src and "qr_slot_weight" in src
