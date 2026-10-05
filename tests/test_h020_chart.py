"""H020 leakage canaries, point-in-time timing, reproducibility and algorithm definitions of the frozen chart score
(src/qresearch/lean/qr_chart.py, qr_chart_render.py; research/phase5/H020_spec.md). SYNTHETIC data only: no market data,
no returns, no score of any real stock."""
import hashlib
import json
import math
import subprocess
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research" / "phase5"))
import h020_fixtures as F  # noqa: E402
import p5_synth as S  # noqa: E402
import qr_chart as C  # noqa: E402
import qr_chart_render as R  # noqa: E402

KEYS = ("o", "h", "l", "c", "v")


def cut(b, t):
    return {k: np.asarray(b[k])[:t + 1] for k in KEYS + ("week_id",)}


def perturb_future(b, t, seed=99, only=None):
    """Same bars up to t; every bar after t replaced by something completely different (only = restrict to fields)."""
    rng = np.random.default_rng(seed)
    out = {k: np.array(b[k], copy=True) for k in KEYS + ("week_id",)}
    m = out["c"].size - t - 1
    if only is None:
        f = np.exp(rng.normal(0.3, 0.2, m))
        for k in ("o", "h", "l", "c"):
            out[k][t + 1:] *= f
        out["h"][t + 1:] *= 1.5
        out["l"][t + 1:] *= 0.5
    if only is None or "v" in only:
        out["v"][t + 1:] *= 7.0 * np.exp(rng.normal(0, 1, m))
    return out


def pngs(b, s):
    return R.render_snapshot(b["o"], b["h"], b["l"], b["c"], b["v"], b["week_id"], s, C.sma, C.weekly_bars)


def week_ends(b, lo, hi):
    wk = b["week_id"]
    return [t for t in range(lo, hi) if wk[t] != wk[t + 1]]


@pytest.fixture(scope="module", params=[("random", 11), ("random", 23), ("base", 7)])
def bars(request):
    kind, seed = request.param
    return S.make_bars(seed=seed, n=1100 if kind == "random" else 700, kind=kind)


@pytest.fixture(scope="module")
def ebars():
    return F.build("E_valid_breakout")


# ---------------------------------------------------------------- canary 1: the complete snapshot + PNG bytes
def test_everything_at_t_ignores_everything_after_t(bars):
    """Daily + Weekly features, swing points, structure, S/R zones, trendlines, base, breakout, volume / volatility,
    entry risk, the 20 conditions, 5 disqualifiers, score and BOTH chart images are identical whatever follows t."""
    n = bars["c"].size
    for t in week_ends(bars, 560, n - 30)[::9][:5]:
        a = C.snapshot_at(bars, t)
        pb = perturb_future(bars, t)
        b = C.snapshot_at(pb, t)
        assert C.digest(a) == C.digest(b)
        assert pngs(cut(bars, t), a) == pngs(cut(pb, t), b)


def test_mid_week_decisions_are_also_point_in_time(bars):
    wk = bars["week_id"]
    t = next(i for i in range(600, bars["c"].size - 3) if wk[i] == wk[i - 2] and wk[i] == wk[i + 2])
    assert C.digest(C.snapshot_at(bars, t)) == C.digest(C.snapshot_at(perturb_future(bars, t), t))


def test_future_volume_alone_changes_nothing(bars):
    t = week_ends(bars, 600, bars["c"].size - 10)[3]
    pb = perturb_future(bars, t, only=("v",))
    a, b = C.snapshot_at(bars, t), C.snapshot_at(pb, t)
    assert C.digest(a) == C.digest(b) and pngs(cut(bars, t), a) == pngs(cut(pb, t), b)


def test_a_future_dependent_feature_would_be_caught(bars):
    """Negative control: the canary is sensitive. A snapshot computed one bar too late differs from the PIT one."""
    t = week_ends(bars, 600, bars["c"].size - 10)[2]
    pb = perturb_future(bars, t)
    assert C.digest(C.snapshot_at(bars, t + 1)) != C.digest(C.snapshot_at(pb, t + 1))


# ---------------------------------------------------------------- canary 2: future pivot confirmation
@pytest.mark.parametrize("k,atr_n", [(C.D_K, C.D_ATR)])
def test_swing_point_appears_exactly_at_confirmation(bars, k, atr_n):
    h, l, c = bars["h"], bars["l"], bars["c"]
    full = C.swing_points(h, l, c, k, atr_n, 10 ** 6)
    assert full
    for i, typ, p in full[-8:]:
        before = C.swing_points(h[:i + k], l[:i + k], c[:i + k], k, atr_n, 10 ** 6)          # t = i + k - 1
        at = C.swing_points(h[:i + k + 1], l[:i + k + 1], c[:i + k + 1], k, atr_n, 10 ** 6)   # t = i + k
        assert all(j != i for j, _, _ in before)
        assert (i, typ, p) in at


def test_confirmed_swing_points_never_repaint(bars):
    h, l, c = bars["h"], bars["l"], bars["c"]
    full = C.swing_points(h, l, c, C.D_K, C.D_ATR, 10 ** 6)
    for t in (500, 700, 900):
        if t >= c.size:
            continue
        part = C.swing_points(h[:t + 1], l[:t + 1], c[:t + 1], C.D_K, C.D_ATR, 10 ** 6)
        assert part == [p for p in full if p[0] <= t - C.D_K]


def test_swing_points_do_not_depend_on_where_the_history_starts(bars):
    """Local prominence window: dropping old history changes no swing point inside the scan window."""
    h, l, c = bars["h"], bars["l"], bars["c"]
    full = C.swing_points(h, l, c, C.D_K, C.D_ATR, C.D_SCAN)
    off = 150
    part = C.swing_points(h[off:], l[off:], c[off:], C.D_K, C.D_ATR, C.D_SCAN)
    assert [(i + off, t, p) for i, t, p in part] == full


def test_history_window_is_long_enough(bars, monkeypatch):
    """The snapshot reads the last HIST_SESSIONS sessions; with the full history it gives exactly the same facts."""
    if bars["c"].size <= C.HIST_SESSIONS + 50:
        pytest.skip("short fixture")
    keys = ("conditions", "disqualifiers", "score", "weekly_state", "daily_state", "atr_ratio", "vol_ratio", "risk",
            "support", "ma", "hi52", "distribution_days")
    for t in week_ends(bars, C.HIST_SESSIONS + 20, bars["c"].size - 2)[::15]:
        a = C.snapshot_at(bars, t)
        monkeypatch.setattr(C, "HIST_SESSIONS", 10 ** 6)
        b = C.snapshot_at(bars, t)
        monkeypatch.setattr(C, "HIST_SESSIONS", 756)
        assert C.canonical({k: a[k] for k in keys}) == C.canonical({k: b[k] for k in keys})
        for key in ("base", "breakout"):
            assert (a[key] is None) == (b[key] is None)
            if a[key] is not None:
                drop = {"anchor", "day"}
                assert C.canonical({x: y for x, y in a[key].items() if x not in drop}) == \
                    C.canonical({x: y for x, y in b[key].items() if x not in drop})


# ---------------------------------------------------------------- canary 3: future Weekly bars (partial-week control)
def test_weekly_bar_of_the_current_week_uses_only_sessions_up_to_t(bars):
    wk = bars["week_id"]
    t = next(i for i in range(600, bars["c"].size - 3) if wk[i] == wk[i - 2] and wk[i] == wk[i + 2])
    b = cut(bars, t)
    W = C.weekly_bars(*(b[k] for k in KEYS), b["week_id"])
    days = np.flatnonzero(wk[:t + 1] == wk[t])
    assert W["c"][-1] == bars["c"][t] and W["h"][-1] == bars["h"][days].max()
    assert W["v"][-1] == pytest.approx(bars["v"][days].sum(), rel=1e-12)
    Wf = C.weekly_bars(*(bars[k] for k in KEYS), wk)
    j = len(W["c"]) - 1
    assert np.array_equal(W["c"][:-1], Wf["c"][:j]) and W["c"][-1] != Wf["c"][j]   # negative control: the full-week
    # bar differs, so a feature built from completed-week data at a mid-week t would be caught by canary 1


# ---------------------------------------------------------------- canary 4: later-listed / short history
def test_insufficient_history_is_excluded_not_padded(bars):
    with pytest.raises(ValueError):
        C.snapshot_at(bars, C.MIN_SESSIONS - 2)
    C.snapshot_at(bars, C.MIN_SESSIONS - 1)                    # exactly 504 sessions: computable


# ---------------------------------------------------------------- canaries 5-7: support / trendlines / zones after t
def test_levels_are_built_only_from_pivots_confirmed_by_t(bars):
    for t in week_ends(bars, 560, bars["c"].size - 2)[::12]:
        s = C.snapshot_at(bars, t)
        n = s["sessions"]                                       # indices are inside the (window-relative) input
        last_ok = n - 1 - C.D_K
        assert all(i <= last_ok for i, _, _ in s["pivots_daily"])
        assert all(z["last"] <= last_ok for z in s["zones_daily"])
        for tl in (s["trend_support"], s["trend_resistance"]):
            if tl is not None:
                assert tl["i1"] < tl["i2"] <= last_ok
        assert all(i <= s["weeks"] - 1 - C.W_K for i, _, _ in s["pivots_weekly"])
        if s["support"] is not None:
            assert s["support"] < C.snapshot_at(bars, t)["ma"]["ma20"] * 10 and s["risk"] > 0


def test_support_that_forms_after_t_is_invisible_at_t():
    """A strong double bottom built AFTER t must not create support at t (and does once confirmed)."""
    b = F.build("A_clean_uptrend")
    t = 560
    s0 = C.snapshot_at(b, t)
    lvl = s0["support"]
    fut = {k: np.array(b[k], copy=True) for k in KEYS + ("week_id",)}
    for j in (t + 8, t + 30):                                  # two deep spikes down to the same price after t
        for k in ("l",):
            fut[k][j] = b["c"][t] * 0.93
    s1 = C.snapshot_at(fut, t)
    assert s1["support"] == lvl and C.digest(s1) == C.digest(s0)
    s2 = C.snapshot_at(fut, t + 50)
    assert any(abs(math.exp(p) - b["c"][t] * 0.93) < 1e-6 for _, ty, p in s2["pivots_daily"] if ty == "L")


def test_trendline_invalidation_is_permanent():
    n = 200
    lc = np.linspace(0, 0.3, n) + 0.02 * np.sin(np.arange(n) / 6)
    troughs = [int(round(6 * (1.5 * math.pi + 2 * math.pi * k))) for k in range(5)]
    piv = [(i, "L", float(lc[i])) for i in troughs if i < n - 5]
    assert C.trendline(piv, lc, 0.005, 0, "support") is not None
    lc2 = lc.copy()
    lc2[150] -= 0.2
    tl = C.trendline(piv, lc2, 0.005, 0, "support")
    assert tl is None or tl["i1"] > 150
    lc3 = lc2.copy()
    lc3[150] = lc[150]                                          # a recovery later never revives a line broken earlier:
    tl_ok = C.trendline(piv, lc3, 0.005, 0, "support")          # (the break is evaluated on all closes after i1)
    assert tl_ok is not None and tl_ok["i1"] <= troughs[0] + 1


def test_resistance_trendline_needs_falling_highs():
    n = 120
    lc = np.full(n, 0.0)
    piv = [(10, "H", 0.10), (40, "H", 0.08), (70, "H", 0.06)]
    tl = C.trendline(piv, lc, 0.005, 0, "resistance")
    assert tl is not None and tl["slope"] < 0 and tl["touches"] == 3
    assert C.trendline([(10, "H", 0.06), (40, "H", 0.08)], lc, 0.005, 0, "resistance") is None


# ---------------------------------------------------------------- canary 8: base duration
def test_base_length_counts_only_weeks_up_to_t(ebars):
    t = 600
    s = C.snapshot_at(ebars, t)
    W = C.weekly_bars(*(cut(ebars, t)[k] for k in KEYS), cut(ebars, t)["week_id"])
    assert s["base"]["length"] == W["c"].size - 1 - s["base"]["anchor"]
    assert s["base"]["anchor"] <= W["c"].size - 1 - C.W_K
    s_more = C.snapshot_at(ebars, 619)
    assert s_more["base"]["anchor"] == s["base"]["anchor"]       # same anchor, later t: the base is older,
    assert s_more["base"]["length"] == s["base"]["length"] + (s_more["weeks"] - s["weeks"])   # never pre-aged


# ---------------------------------------------------------------- canary 9: breakout confirmation and later closes
def test_breakout_at_t_is_unaffected_by_a_later_failure(ebars):
    t = ebars["c"].size - 1
    s = C.snapshot_at(ebars, t)
    assert s["conditions"]["T1"] and s["breakout"]["age"] == 1
    ext = {k: np.r_[np.asarray(ebars[k]), np.asarray(ebars[k])[-15:]] for k in KEYS}
    fail = ebars["c"][-1] * 0.92                                 # the breakout fails over the following days
    for k in ("o", "h", "l", "c"):
        ext[k][t + 1:] = fail * (1.004 if k == "h" else (0.996 if k == "l" else 1.0))
    d, wk = F._calendar(ext["c"].size)
    ext["week_id"] = wk
    assert C.digest(C.snapshot_at(ext, t)) == C.digest(s)
    assert not C.snapshot_at(ext, t + 10)["conditions"]["T1"]


def test_breakout_definition():
    rng = np.random.default_rng(1)
    n = 120
    c = 100 * np.exp(np.r_[np.zeros(117), [0.0, 0.01, 0.03]] + rng.normal(0, 0.001, n))
    o, h, l, v = c.copy(), c * 1.003, c * 0.997, np.full(n, 1e6)
    v[-2] = 2e6
    lvl = math.log(c[:-2].max())
    bo = C.breakout(o, h, l, c, v, lvl, 10)
    assert bo is not None and bo["age"] == 1 and bo["relvol"] == pytest.approx(2.0, rel=0.05)
    assert C.breakout(o, h, l, c, v, math.log(c.max() * 1.01), 10) is None      # not above the level
    assert C.breakout(o, h, l, c, v, lvl, n - 2) is None                         # run must start after the base start
    c2 = c.copy()
    c2[-10:] = c2[-1]
    assert C.breakout(o, h, l, c2, v, math.log(c2[-11] * 0.999), 10) is None     # first close above >= 5 sessions ago


# ---------------------------------------------------------------- canary 10: chart scaling (axis) negative control
def test_axis_canary_detects_a_future_driven_axis(bars):
    t = 650 if bars["c"].size > 700 else 600
    a = cut(bars, t)
    s = C.snapshot(*(a[k] for k in KEYS), a["week_id"])
    ov = R.daily_overlays(s, C.sma, a["c"], len(a["c"]))
    good = R.render(a["o"], a["h"], a["l"], a["c"], a["v"], 126, ov).png()
    ov["include_levels"] = ov["include_levels"] + [math.log(bars["h"][t + 1:].max() * 1.2)]
    assert good != R.render(a["o"], a["h"], a["l"], a["c"], a["v"], 126, ov).png()


def test_scale_invariance_later_adjustment_factors_cannot_leak(bars):
    """Multiplying all bars <= t by a constant (a split / dividend factor dated after t) changes no structural fact, no
    condition, disqualifier or score, and essentially no pixel."""
    t = bars["c"].size - 1
    b2 = {k: (np.asarray(bars[k]) * 3.7 if k in ("o", "h", "l", "c") else bars[k]) for k in KEYS + ("week_id",)}
    s1, s2 = C.snapshot_at(bars, t), C.snapshot_at(b2, t)
    assert [(i, x) for i, x, _ in s1["pivots_daily"]] == [(i, x) for i, x, _ in s2["pivots_daily"]]
    for k in ("conditions", "disqualifiers", "score", "weekly_state", "daily_state"):
        assert s1[k] == s2[k]
    d1, _ = pngs(cut(bars, t), s1)
    p1 = R.render(bars["o"], bars["h"], bars["l"], bars["c"], bars["v"], 126,
                  R.daily_overlays(s1, C.sma, bars["c"], len(bars["c"]))).a
    p2 = R.render(b2["o"], b2["h"], b2["l"], b2["c"], b2["v"], 126,
                  R.daily_overlays(s2, C.sma, b2["c"], len(b2["c"]))).a
    assert np.mean(np.any(p1 != p2, axis=2)) < 0.001


# ---------------------------------------------------------------- reproducibility
def _hashes():
    out = {}
    for name in F.SCENARIOS:
        b = F.build(name)
        s = C.snapshot_at(b, b["c"].size - 1)
        d, w = pngs(b, s)
        out[name] = (C.digest(s), hashlib.sha256(d).hexdigest(), hashlib.sha256(w).hexdigest())
    return out


def test_repeated_runs_are_byte_identical():
    assert _hashes() == _hashes()


def test_a_fresh_process_gives_the_same_bytes():
    code = ("import sys, json; sys.path[:0]=[%r, %r]; sys.path.insert(0, %r);"
            "import test_h020_chart as T; print(json.dumps(T._hashes()))" %
            (str(ROOT / "src" / "qresearch" / "lean"), str(ROOT / "research" / "phase5"), str(ROOT / "tests")))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True, cwd=str(ROOT))
    assert {k: tuple(v) for k, v in json.loads(out.stdout).items()} == _hashes()


# ---------------------------------------------------------------- algorithm definitions
def _P(hs, ls):
    return [(i, "H", math.log(x)) for i, x in hs] + [(i, "L", math.log(x)) for i, x in ls]


def test_structure_states():
    tol = 0.01
    st = C.structure_state
    assert st(_P([(1, 100), (5, 110)], [(3, 90), (7, 95)]), 105, tol) == "strong_uptrend"        # HH + HL
    assert st(_P([(1, 100), (5, 100.5)], [(3, 90), (7, 95)]), 98, tol) == "uptrend"              # EH + HL
    assert st(_P([(1, 100), (5, 110)], [(3, 90), (7, 90.4)]), 100, tol) == "uptrend"             # HH + EL
    assert st(_P([(1, 100), (5, 95)], [(3, 90), (7, 85)]), 88, tol) == "downtrend"               # LH + LL
    assert st(_P([(1, 100), (5, 110)], [(3, 90), (7, 95)]), 90, tol) == "deteriorating"          # close < L2 - tol
    assert st(_P([(1, 100), (5, 95)], [(3, 90), (7, 85)]), 80, tol) == "downtrend"               # break down, LH+LL
    assert st(_P([(1, 100), (5, 95)], [(3, 90), (7, 92)]), 93, tol) == "range"                   # LH + HL
    assert st(_P([(1, 100), (5, 110)], [(3, 90), (7, 85)]), 100, tol) == "range"                 # HH + LL
    assert st(_P([(1, 100)], [(3, 90)]), 95, tol) == "undefined"
    assert st(_P([(1, 100), (5, 110)], [(3, 90)]), 95, tol) == "undefined"


def test_close_above_the_last_swing_high_is_an_uptrend_regression():
    """P5-CP1 regression: a base breaking up above H2 after a lower high was classified as downtrend. Now: break up ->
    strong_uptrend if the lows are rising, else uptrend; never downtrend."""
    tol = 0.01
    assert C.structure_state(_P([(1, 100), (5, 95)], [(3, 90), (7, 92)]), 97, tol) == "strong_uptrend"
    assert C.structure_state(_P([(1, 100), (5, 95)], [(3, 90), (7, 85)]), 97, tol) == "uptrend"


def test_zones_are_anchored_never_chained():
    tol = 0.01
    piv = [(i, "L", math.log(100 * (1 + 0.012 * i))) for i in range(10)]        # a ladder single linkage would chain
    zs = C.zones(piv, tol, 0)
    assert len(zs) > 1 and all(z["hi"] - z["lo"] <= 4 * tol + 1e-12 for z in zs)
    assert all(z["touches"] >= C.ZONE_MIN_TOUCHES for z in zs)
    assert C.zones(piv, tol, 5) == [z for z in C.zones(piv[5:], tol, 0)]
    res, sup = C.nearest(zs, 104.0)
    assert res is None or res["lo"] > math.log(104.0)
    assert sup is None or sup["hi"] < math.log(104.0)


def test_base_definition():
    wh = np.array([10, 11, 12, 13, 14, 15, 16, 15, 14, 13, 14, 15, 14.5, 14, 14.6, 15.2, 15.5, 15.8, 15.9], float)
    W = dict(h=wh, l=wh * 0.98)
    piv = [(6, "H", math.log(16.0)), (9, "L", math.log(13 * 0.98)), (11, "H", math.log(15.0)),
           (13, "L", math.log(14 * 0.98))]
    bs = C.base(W, piv)
    assert bs["anchor"] == 6 and bs["length"] == 12 and bs["valid"]
    assert bs["depth"] == pytest.approx(1 - 13 * 0.98 / 16)
    assert bs["contracting"] and len(bs["pullbacks"]) == 2
    wh2 = wh.copy()
    wh2[11] = 16.5
    bs2 = C.base(dict(h=wh2, l=wh2 * 0.98), piv[:2] + [(11, "H", math.log(16.5))])   # latest swing high = new 26-wk high
    assert bs2["anchor"] == 11 and bs2["length"] == 7 and bs2["valid"]
    assert C.base(dict(h=wh[:10], l=wh[:10] * 0.98), piv[:2])["valid"] is False                # 3 weeks: too young


def test_score_groups_and_quality_level():
    def snap(score, dq):
        return dict(score=score, disqualified=dq)
    assert [C.score_group(snap(s, False)) for s in (0, 5, 6, 10, 11, 15, 16, 20)] == [1, 1, 2, 2, 3, 3, 4, 4]
    assert C.score_group(snap(20, True)) == 0 and C.quality_level(snap(20, True)) == -1
    assert C.quality_level(snap(7, False)) == 7


def test_no_condition_uses_a_weight_or_an_ai_component():
    src = (ROOT / "src" / "qresearch" / "lean" / "qr_chart.py").read_text()
    assert "score=int(sum(C.values()))" in src
    for banned in ("anthropic", "openai", "requests", "urllib", "http"):
        assert banned not in src.lower().replace("https://", "")
