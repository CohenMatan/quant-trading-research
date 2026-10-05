"""P5-CP1 design reference (research/phase5): leakage canaries and architecture tests of the deterministic chart
algorithms and the frozen-format renderer. SYNTHETIC data only; no market data, no returns, no scores of real stocks."""
import hashlib
import math
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research" / "phase5"))
import p5_chart as C  # noqa: E402
import p5_render as R  # noqa: E402
import p5_synth as S  # noqa: E402

KEYS = ("o", "h", "l", "c", "v")


def cut(b, t):
    """The bars a decision at bar t may see: 0..t inclusive."""
    return {k: (b[k][:t + 1] if k in KEYS + ("week_id",) else b[k]) for k in b}


def perturb_future(b, t, seed=99):
    """Same bars up to t; every bar after t replaced by something completely different."""
    rng = np.random.default_rng(seed)
    out = {k: np.array(b[k], copy=True) for k in b}
    m = b["c"].size - t - 1
    f = np.exp(rng.normal(0.3, 0.2, m))
    for k in ("o", "h", "l", "c"):
        out[k][t + 1:] = out[k][t + 1:] * f
    out["h"][t + 1:] *= 1.5
    out["l"][t + 1:] *= 0.5
    out["v"][t + 1:] *= 7.0
    return out


def snap(b):
    return C.snapshot(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"])


def daily_png(b, s=None):
    s = snap(b) if s is None else s
    return R.render(b["o"], b["h"], b["l"], b["c"], b["v"], 126, R.daily_overlays(s, C.sma, b["c"], len(b["c"]))).png()


def weekly_png(b):
    W = C.weekly_bars(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"])
    return R.render(W["o"], W["h"], W["l"], W["c"], W["v"], 104, R.weekly_overlays(W["c"], C.sma)).png()


@pytest.fixture(scope="module", params=[("base", 7), ("random", 11), ("random", 23)])
def bars(request):
    kind, seed = request.param
    return S.make_bars(seed=seed, n=600, kind=kind)


# ---------------------------------------------------------------- leakage canaries (section 22)
@pytest.mark.parametrize("t", [400, 455, 520])
def test_snapshot_checklist_and_pixels_ignore_everything_after_t(bars, t):
    a, b = cut(bars, t), cut(perturb_future(bars, t), t)
    sa, sb = snap(a), snap(b)
    assert sa["pivots_daily"] == sb["pivots_daily"] and sa["pivots_weekly"] == sb["pivots_weekly"]
    assert sa["zones"] == sb["zones"] and sa["trendline"] == sb["trendline"] and sa["base"] == sb["base"]
    assert C.checklist(sa) == C.checklist(sb)
    assert daily_png(a, sa) == daily_png(b, sb) and weekly_png(a) == weekly_png(b)


@pytest.mark.parametrize("t", [400, 520])
def test_confirmed_pivots_are_a_prefix_of_the_full_history_pivots(bars, t):
    """A swing at bar i exists at t only if i <= t - k, and then exactly as it does with all data (no repainting)."""
    for k, get in ((C.PIVOT_K_DAILY, lambda x: (x["h"], x["l"], x["c"])),):
        full = C.swing_points(*get(bars), k)
        part = C.swing_points(*get(cut(bars, t)), k)
        assert all(i <= t - k for i, _, _ in part)
        assert part == [p for p in full if p[0] <= t - k]


def test_weekly_bars_use_only_sessions_up_to_t(bars):
    wk = bars["week_id"]
    t = next(i for i in range(450, 600) if wk[i] == wk[i - 2] and wk[i] == wk[i + 2])   # mid-week session
    W = C.weekly_bars(*(cut(bars, t)[k] for k in KEYS), cut(bars, t)["week_id"])
    days = np.flatnonzero(wk[:t + 1] == wk[t])
    assert W["c"][-1] == bars["c"][t] and W["h"][-1] == bars["h"][days].max()
    assert W["v"][-1] == pytest.approx(bars["v"][days].sum(), rel=1e-12)
    Wf = C.weekly_bars(*(bars[k] for k in KEYS), wk)
    j = len(W["c"]) - 1
    assert np.array_equal(W["c"][:-1], Wf["c"][:j]) and W["c"][-1] != Wf["c"][j]   # complete weeks equal; the partial one
    # differs from the eventual full-week bar (negative control: a renderer using full-week bars at t would leak)


def test_axis_canary_detects_a_future_driven_axis(bars):
    """Negative control: if the y-range were widened by a FUTURE high, the image would change, so the byte-equality
    canary above is sensitive to axis leakage."""
    t = 500
    a = cut(bars, t)
    s = snap(a)
    ov = R.daily_overlays(s, C.sma, a["c"], len(a["c"]))
    good = R.render(a["o"], a["h"], a["l"], a["c"], a["v"], 126, ov).png()
    ov["include_levels"] = ov["include_levels"] + [math.log(bars["h"][t + 1:].max() * 1.2)]
    bad = R.render(a["o"], a["h"], a["l"], a["c"], a["v"], 126, ov).png()
    assert good != bad


# ---------------------------------------------------------------- reproducibility and invariance (sections 20-21)
def test_rendering_is_byte_deterministic(bars):
    assert daily_png(bars) == daily_png(bars) and weekly_png(bars) == weekly_png(bars)
    png = daily_png(bars)
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and len(png) > 1000


def test_scale_invariance_later_adjustment_factors_cannot_leak(bars):
    """Multiplying the whole history by a constant (what a split or dividend factor dated after t does to every bar <= t)
    changes no structural fact, no checklist value and (log axis, no labels) essentially no pixel."""
    k = 3.7
    b2 = {key: (np.asarray(bars[key]) * k if key in ("o", "h", "l", "c") else bars[key]) for key in bars}
    s1, s2 = snap(bars), snap(b2)
    assert [(i, t) for i, t, _ in s1["pivots_daily"]] == [(i, t) for i, t, _ in s2["pivots_daily"]]
    assert s1["weekly_state"] == s2["weekly_state"] and s1["daily_state"] == s2["daily_state"]
    assert C.checklist(s1) == C.checklist(s2)
    p1 = R.render(bars["o"], bars["h"], bars["l"], bars["c"], bars["v"], 126,
                  R.daily_overlays(s1, C.sma, bars["c"], len(bars["c"]))).a
    p2 = R.render(b2["o"], b2["h"], b2["l"], b2["c"], b2["v"], 126,
                  R.daily_overlays(s2, C.sma, b2["c"], len(b2["c"]))).a
    assert np.mean(np.any(p1 != p2, axis=2)) < 0.001          # at most rounding at isolated pixels


# ---------------------------------------------------------------- algorithm definitions (sections 6-14)
def test_structure_states():
    P = lambda hs, ls: [(i, "H", math.log(x)) for i, x in hs] + [(i, "L", math.log(x)) for i, x in ls]
    tol = 0.01
    assert C.structure_state(P([(1, 100), (5, 110)], [(3, 90), (7, 95)]), 105, tol) == "strong_uptrend"
    assert C.structure_state(P([(1, 100), (5, 100.5)], [(3, 90), (7, 95)]), 98, tol) == "weak_uptrend"
    assert C.structure_state(P([(1, 100), (5, 95)], [(3, 90), (7, 85)]), 88, tol) == "downtrend"
    assert C.structure_state(P([(1, 100), (5, 110)], [(3, 90), (7, 95)]), 90, tol) == "deteriorating"
    assert C.structure_state(P([(1, 100), (5, 95)], [(3, 90), (7, 92)]), 93, tol) == "range"
    assert C.structure_state(P([(1, 100), (5, 95)], [(3, 90), (7, 92)]), 97, tol) == "strong_uptrend"   # break up
    assert C.structure_state(P([(1, 100)], [(3, 90)]), 95, tol) == "undefined"


def test_zones_are_anchored_and_bounded():
    tol = 0.01
    piv = [(i, "L", math.log(100 * (1 + 0.012 * i))) for i in range(10)]        # a ladder that single linkage chains
    zones = C.sr_zones(piv, tol, min_touches=1)
    assert all(z["hi"] - z["lo"] <= 4 * tol + 1e-12 for z in zones) and len(zones) > 1
    assert sum(z["touches"] for z in zones) == 10


def test_trendline_invalidation_is_permanent():
    n = 200
    c = np.exp(np.linspace(0, 0.3, n) + 0.02 * np.sin(np.arange(n) / 6))
    lc = np.log(c)
    troughs = [int(round(6 * (1.5 * math.pi + 2 * math.pi * k))) for k in range(5)]
    piv = [(i, "L", float(lc[i])) for i in troughs if i < n - 5]
    assert C.support_trendline(piv, lc, 0.005, 10) is not None
    lc2 = lc.copy()
    lc2[150] -= 0.2                                                            # one close far below every line
    tl = C.support_trendline(piv, lc2, 0.005, 10)
    assert tl is None or tl["i1"] > 150


def test_breakout_definition():
    rng = np.random.default_rng(1)
    n = 120
    c = 100 * np.exp(np.r_[np.zeros(117), [0.0, 0.01, 0.03]] + rng.normal(0, 0.001, n))
    h, l, v = c * 1.003, c * 0.997, np.full(n, 1e6)
    v[-2] = 2e6
    lvl = math.log(c[:-2].max())
    bo = C.breakout(h, l, c, v, lvl)
    assert bo is not None and bo["age"] == 1 and bo["relvol"] == pytest.approx(2.0, rel=0.05)
    assert C.breakout(h, l, c, v, math.log(c.max() * 1.01)) is None              # not above the level
    c2 = c.copy()
    c2[-10:] = c2[-1]
    assert C.breakout(h, l, c2, v, math.log(c2[-11] * 0.999)) is None            # first close above >= 5 sessions ago


def test_checklist_structure(bars):
    r = C.checklist(snap(bars))
    assert set(r["categories"]) == {"weekly_trend", "base", "trigger", "entry_risk"}
    assert all(0 <= x <= 5 for x in r["categories"].values()) and r["total"] == sum(r["categories"].values())
    assert r["eligible"] == (not r["disqualified"])


def test_demo_outputs_are_synthetic_and_reproducible():
    import json
    rec = json.loads((ROOT / "research/phase5/demo/demo_snapshots.json").read_text())
    for name, kind, seed in (("base", "base", 7), ("random", "random", 11)):
        b = S.make_bars(seed=seed, n=600, kind=kind)
        assert rec[name]["png_sha256"]["daily"] == hashlib.sha256(daily_png(b)).hexdigest()
        assert rec[name]["checklist"] == C.checklist(snap(b))
