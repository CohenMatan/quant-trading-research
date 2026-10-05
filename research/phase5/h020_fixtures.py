"""H020 SYNTHETIC scenario fixtures (P5-CP2 section 40): deliberately constructed charts, NO market data, NO returns.

Each fixture = 620 sessions of split-adjusted daily bars built from scripted log-price segments (+ a deterministic
wiggle and a tiny seeded noise), a fixed intraday range, and a scripted volume path. TARGET lists the conditions /
disqualifiers / states each scenario is designed to exercise (the design expectation); the complete frozen output
(all 20 conditions, 5 disqualifiers, score, states, key features) is pinned in h020_scenarios_expected.json.
"""
import math

import numpy as np

N = 620


def _calendar(n, start="2008-01-02"):
    d = np.arange(np.datetime64(start), np.datetime64(start) + 3 * n)
    d = d[np.is_busday(d)][:n]
    iso = [x.astype(object).isocalendar() for x in d]
    return d, np.array([y * 100 + w for y, w, _ in iso])


def _bars(logc, rng_frac, vol, gaps=None, seed=0):
    """OHLC from closes: open = previous close (x gap factor), high / low = max / min(open, close) widened by rng_frac."""
    rng = np.random.default_rng(seed)
    c = 30.0 * np.exp(logc + rng.normal(0, 0.0005, logc.size))
    o = np.r_[c[0], c[:-1]]
    if gaps:
        for i, g in gaps.items():
            o[i] = c[i - 1] * g
    rf = np.broadcast_to(np.asarray(rng_frac, float), c.shape)
    h = np.maximum(o, c) * (1 + rf)
    l = np.minimum(o, c) * (1 - rf)
    d, wk = _calendar(c.size)
    return dict(o=o, h=h, l=l, c=c, v=np.asarray(vol, float), dates=d, week_id=wk)


def _segments(spec, n=N):
    """spec = [(sessions, total log move), ...] -> cumulative log path of length n (last segment padded)."""
    r = []
    for k, m in spec:
        r += [m / k] * k
    r = (r + [0.0] * n)[:n - 1]
    return np.r_[0.0, np.cumsum(r)]


def _wiggle(n, amp, period, phase=0.0):
    return amp * np.sin(2 * math.pi * np.arange(n) / period + phase)


def _base_path(depths, end_frac=0.97, n=N, adv=400, adv_move=0.6):
    """Advance of `adv` sessions, then a base: pullbacks of the given depths (each followed by a recovery to just below the
    left-side high), then a quiet drift to end_frac of the pivot by the last session."""
    spec = [(adv, adv_move)]
    level = 0.0                                         # log level relative to the pivot (end of the advance)
    for d in depths:
        down = math.log(1 - d)
        spec += [(20, down), (25, -down - 0.01)]
        level -= 0.01
    used = adv + 45 * len(depths)
    spec += [(n - used, math.log(end_frac) - level)]
    return _segments(spec, n)


def _vol(n, base=1e6, tail_mult=1.0, tail=40):
    v = np.full(n, base)
    v[-tail:] = base * tail_mult
    return v


def build(name):
    n = N
    if name == "A_clean_uptrend":
        lc = np.linspace(0, 0.9, n) + _wiggle(n, 0.04, 60)
        return _bars(lc, 0.006, _vol(n))
    if name == "B_range":
        lc = _wiggle(n, 0.10, 70) + _wiggle(n, 0.02, 13, 1.0)
        return _bars(lc, 0.008, _vol(n))
    if name == "C_healthy_base":
        lc = _base_path([0.15, 0.08, 0.04], end_frac=0.97)
        rf = np.r_[np.full(n - 20, 0.008), np.full(20, 0.003)]          # quiet last sessions (contraction)
        return _bars(lc, rf, _vol(n, tail_mult=0.6, tail=20))
    if name == "D_deep_base":
        lc = _base_path([0.45, 0.10], end_frac=0.97)
        return _bars(lc, 0.008, _vol(n))
    if name in ("E_valid_breakout", "J_expanding_breakout_volume", "J_control_quiet_breakout"):
        lc = _base_path([0.15, 0.08, 0.04], end_frac=0.97)
        lc[-2] = lc[-3] + math.log(1.035 / 0.97)                         # breakout day: close 3.5% above the pivot
        lc[-1] = lc[-2] + 0.004
        rf = np.r_[np.full(n - 20, 0.008), np.full(18, 0.003), [0.004, 0.004]]
        v = _vol(n, tail_mult=0.6, tail=20)
        v[-2] = 1e6 * (1.1 if name == "J_control_quiet_breakout" else 2.0)
        b = _bars(lc, rf, v)
        b["h"][-2] = b["c"][-2] * 1.002                                  # close near the high of the breakout day
        return b
    if name == "F_false_breakout":
        lc = _base_path([0.15, 0.08, 0.04], end_frac=0.97)
        lc[-3] = lc[-4] + math.log(1.03 / 0.97)                          # breaks out ...
        lc[-2] = lc[-3] - 0.01
        lc[-1] = lc[-4] - 0.005                                          # ... and closes back inside the base
        v = _vol(n, tail_mult=0.6, tail=20)
        v[-3] = 2e6
        return _bars(lc, 0.004, v)
    if name == "G_support_break":
        lc = np.linspace(0, 0.8, n) + _wiggle(n, 0.04, 60)
        lc[-12:] = lc[-13] + np.linspace(-0.02, -0.20, 12)               # sharp drop through supports
        return _bars(lc, 0.008, _vol(n))
    if name == "H_overextended":
        lc = np.r_[np.linspace(0, 0.5, n - 30), 0.5 + np.linspace(0.012, 0.36, 30)]
        return _bars(lc, 0.006, _vol(n))
    if name in ("I_contracting_volume", "I_control_flat_volume"):
        lc = _base_path([0.15, 0.08, 0.04], end_frac=0.97)
        v = _vol(n, tail_mult=0.55 if name == "I_contracting_volume" else 1.0, tail=25)
        return _bars(lc, 0.008, v)
    raise KeyError(name)


SCENARIOS = ("A_clean_uptrend", "B_range", "C_healthy_base", "D_deep_base", "E_valid_breakout", "F_false_breakout",
             "G_support_break", "H_overextended", "I_contracting_volume", "I_control_flat_volume",
             "J_expanding_breakout_volume", "J_control_quiet_breakout")

# Design expectations (what each fixture is built to show); value = required truth value
TARGET = {
    "A_clean_uptrend": dict(W1=True, W2=True, W3=True, W4=True, W5=True, D1=False, D2=False, weekly_state="strong_uptrend"),
    "B_range": dict(W4=False, T1=False, weekly_state="range"),
    "C_healthy_base": dict(B1=True, B2=True, B3=True, B4=True, B5=True, T1=False),
    "D_deep_base": dict(B1=True, B2=False, T1=False),
    "E_valid_breakout": dict(B1=True, T1=True, T2=True, T3=True, T4=True, T5=True, R1=True),
    "F_false_breakout": dict(B1=True, T1=False, T2=False, T3=False, T4=False),
    "G_support_break": dict(R5=False),
    "H_overextended": dict(D3=True, R3=False),
    "I_contracting_volume": dict(B1=True, B4=True),
    "I_control_flat_volume": dict(B1=True, B4=False),
    "J_expanding_breakout_volume": dict(T1=True, T3=True),
    "J_control_quiet_breakout": dict(T1=True, T3=False),
}
