"""H006X exit-policy comparison (owner D304): S006 time-stop removal and the carried highest-close-since-entry.
Control A (time stop 60) must behave exactly as the original S006 code; B's chandelier must use the true highest close
since entry beyond the 260-bar window, through split / dividend re-adjustments of the window."""
import random
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
from conftest import load_module  # noqa: E402
from qr_indicators import atr  # noqa: E402

S006 = load_module(ROOT / "strategies/S006_breakout/signals.py", "s006_signals_h006x")
WINDOW = 260


def original_exit_signal(highs, lows, closes, sessions_held, k, time_stop):
    """S006 exit_signal as run in C02 (E006-01..03), copied verbatim for the equivalence check."""
    if sessions_held is None:
        return False
    if sessions_held >= time_stop:
        return True
    c = list(closes)
    since = c[-(sessions_held + 1):] if sessions_held + 1 <= len(c) else c
    a = atr(highs, lows, c, 20)
    return a is not None and c[-1] < max(since) - k * a


def bars(n, seed):
    rng = random.Random(seed)
    c, h, l = [], [], []
    p = 50.0
    for _ in range(n):
        p *= 1 + rng.gauss(0.0005, 0.02)
        c.append(p)
        h.append(p * (1 + abs(rng.gauss(0, 0.01))))
        l.append(p * (1 - abs(rng.gauss(0, 0.01))))
    return h, l, c


def test_control_a_identical_to_original_code():
    for seed in range(40):
        h, l, c = bars(WINDOW, seed)
        for held in list(range(0, 75)) + [259, 260, 400, None]:
            for carried in (None, 1e9, 1.0):
                assert (S006.exit_signal(h, l, c, held, 3.0, 60, carried)
                        == original_exit_signal(h, l, c, held, 3.0, 60))


def test_no_time_stop_never_exits_on_time():
    h, l, c = [10.0] * WINDOW, [9.9] * WINDOW, [10.0] * WINDOW
    assert S006.exit_signal(h, l, c, 60, 3.0, 60) is True
    assert S006.exit_signal(h, l, c, 60, 3.0, None) is False
    assert S006.exit_signal(h, l, c, 5000, 3.0, None, 10.0) is False
    assert S006.exit_signal(h, l, c, 5000, 3.0, None, 12.0) is True          # carried peak far above: chandelier


def test_peak_within_window_and_beyond():
    c = [1.0, 5.0, 2.0, 3.0]
    assert S006.peak_since_entry(c, 1) == 3.0 and S006.peak_since_entry(c, 3) == 5.0
    assert S006.peak_since_entry(c, 10) == 5.0                               # no carry: original whole window
    assert S006.peak_since_entry(c, 10, 9.0) == 9.0 and S006.peak_since_entry(c, 10, 2.0) == 3.0


def test_carried_peak_bar_alignment():
    c = [1.0, 2.0, 4.0]
    assert S006.carried_peak(None, c, "d3", True) is None
    assert S006.carried_peak((1.5, "d2"), c, "d3", False) is None          # window not full: original behaviour
    assert S006.carried_peak((1.5, "d2"), c, "d3", True) == 3.0             # one bar appended since: closes[-2]
    assert S006.carried_peak((1.5, "d3"), c, "d3", True) == 6.0             # no new bar: closes[-1]


def simulate(n, seed, splits=(), gaps=()):
    """The main.py bookkeeping on a 260-bar deque over one long hold; returns (carried peak, true peak) per close,
    both in today's adjusted units. A split rescales the whole window (harness _qr_rescale); a gap = no bar that day."""
    rng = random.Random(seed)
    win = deque(maxlen=WINDOW)
    history = []                                   # the true closes since entry, re-adjusted like the window
    p = 40.0
    for _ in range(WINDOW):
        p *= 1 + rng.gauss(0.0005, 0.02)
        win.append(p)
    stored, out, last = None, [], 0
    entry_close = win[-1]
    history = [entry_close]
    held = 0
    peaks_carried = None
    for day in range(1, n + 1):
        held += 1
        if day in splits:
            f = splits[day]
            win = deque((x * f for x in win), maxlen=WINDOW)
            history = [x * f for x in history]
            if stored is not None:
                pass                                       # ratios are scale-free
        if day not in gaps:
            p = win[-1] * (1 + rng.gauss(0.0008, 0.02))
            win.append(p)
            history.append(p)
            last = day
        carried = S006.carried_peak(stored, win, last, len(win) == WINDOW)
        ref = S006.peak_since_entry(win, held, carried)
        stored = (ref / win[-1], last)
        peaks_carried = ref
        out.append((peaks_carried, max(history)))
    return out


def test_carried_peak_equals_true_peak_through_splits_and_gaps():
    for seed in range(10):
        path = simulate(900, seed, splits={300: 0.5, 555: 1 / 3.0, 700: 0.98}, gaps={301, 302, 650})
        for carried, true in path:
            assert abs(carried - true) <= 1e-9 * true


def test_without_carry_the_window_would_forget_the_peak():
    """Documents why the fidelity fix is needed: after a peak drops out of the 260-bar window, the original code's
    reference is lower than the true highest close since entry (the stop would be looser)."""
    c = [100.0] + [50.0] * (WINDOW - 1)
    win = c[-WINDOW:]
    assert S006.peak_since_entry(win, 300) == 100.0
    win2 = [50.0] * WINDOW                                 # the 100 has rolled out
    assert S006.peak_since_entry(win2, 301) == 50.0
    assert S006.peak_since_entry(win2, 301, 100.0) == 100.0
