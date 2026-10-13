"""H029 / H030 pure module qr_h029 (owner D229; research/phase14/H029_H030_spec.md): the H028 component equals the
frozen qr_h028 lambda-100 path bit for bit; LV15 and the risk metrics equal frozen qr_h027; the blend is exactly 50/50
with no weight parameter; the tether null moves complete six-signal vectors, keeps eligibility and never touches H028;
worlds are deterministic; gates, adequacy and the synthetic A / B worlds behave as pre-registered."""
import inspect
import math
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_h026 as H  # noqa: E402
import qr_h027 as G  # noqa: E402
import qr_h028 as F  # noqa: E402
import qr_h029 as Q  # noqa: E402
import qr_v3 as V3  # noqa: E402
from test_p11_h026 import synth  # noqa: E402


def _ms(seed=3):
    beta = np.zeros(11)
    beta[0], beta[4] = 0.02, -0.015
    return synth(beta, seed=seed)


def _setup(seed=3, frac=0.8, miss=True):
    ms = _ms(seed)
    Xs = [m["X"] for m in ms]
    fits = Q.fixed_fits(ms, Xs)
    idx = Q.outer_index(ms)
    m28 = [ms[i] for i in idx]
    sc28 = Q.h028_scores(ms, Xs, fits)
    rng = np.random.default_rng(seed + 100)
    m29, V29, m30, sc28j, j29 = [], [], [], [], []
    for m, s in zip(m28, sc28):
        n = len(m["ids"])
        keep = np.sort(rng.choice(n, int(frac * n), replace=False))
        ids = [m["ids"][i] for i in keep]
        mm = Q.sub_month(m, keep, ids)
        mm["sector"] = np.array([int(s[1:]) % 6 for s in ids], dtype=np.int64)   # stable synthetic FF12 labels, >= 2 per sector
        V = rng.normal(size=(len(ids), 6))
        if miss:
            V[rng.random(len(ids)) < 0.3, rng.integers(0, 6)] = np.nan       # <= 1 missing per row
        m29.append(mm)
        V29.append(V)
        jids, p28, p29 = Q.joint(m["ids"], ids)
        m30.append(Q.sub_month(m, p28, jids))
        sc28j.append(s[p28])
        j29.append(p29)
    days = np.concatenate([m["days"] for m in m28])
    spy = Q.spy_path(m28, days)
    w28 = H.simulate(m28, sc28)["wealth"]
    return dict(ms=ms, Xs=Xs, m28=m28, sc28=sc28, m29=m29, V29=V29, m30=m30, sc28j=sc28j, j29=j29, days=days,
                spy=spy, w28=w28, fits=fits)


def test_h028_component_equals_frozen_fixed_path_bit_for_bit():
    S = _setup()
    w = F.run_world_fixed(S["ms"], S["Xs"], full=True)
    assert [m["day"] if "day" in m else m["cutoff_day"] for m in S["m28"]] == \
        [S["ms"][i].get("day", S["ms"][i]["cutoff_day"]) for i in w["idx"]]
    for Y in Q.OUTER:
        b0, b, _n = S["fits"][Y]
        assert np.array_equal(b, w["coef"][(Y, 100.0)][1]) and b0 == w["coef"][(Y, 100.0)][0]
    assert all(np.array_equal(a, b) for a, b in zip(S["sc28"], w["scores"]))
    assert S["w28"] == w["h"]["wealth"]


def test_lv15_and_risk_equal_frozen_h027():
    S = _setup()
    assert all(np.array_equal(a, b) for a, b in zip(Q.lv15_scores(S["m28"]), G.lv15_scores(S["m28"])))
    h = H.simulate(S["m28"], S["sc28"], daily=True)
    g = G.risk(h["daily"], S["spy"]["daily"], S["days"], H.CAPITAL)
    rh, _ = Q.monthly(h["daily"], S["days"])
    q = Q.risk(rh, S["spy"]["r"])
    for k in ("beta", "up_capture", "down_capture", "corr"):
        assert q[k] == pytest.approx(g[k], rel=1e-12, abs=1e-15)
    assert Q.month_ends(S["days"]) == G.month_ends(S["days"])


def test_blend_is_exactly_fifty_fifty_with_no_weight_parameter():
    rng = np.random.default_rng(1)
    a, b = rng.normal(size=30), rng.normal(size=30)
    assert np.array_equal(Q.blend(a, b), 0.5 * V3.centred(a) + 0.5 * V3.centred(b))
    assert list(inspect.signature(Q.blend).parameters) == ["h028_raw", "h029_raw"]
    src = inspect.getsource(Q)
    assert src.count("def blend") == 1 and "0.5 * V3.centred(h028_raw) + 0.5 * V3.centred(h029_raw)" in src
    for bad in ("0.6 *", "0.4 *", "0.7 *", "0.3 *", "0.2 *", "0.8 *", "weight=", "weights="):
        assert bad not in src, bad
    # H029 is never fitted: no Ridge / Fitter / lambda in the H029 code path
    h029_src = inspect.getsource(Q.h029_scores) + inspect.getsource(V3.h029_score) + inspect.getsource(V3.signals)
    for bad in ("Fitter", "ridge", "LAMBDA", "lstsq", "fit("):
        assert bad not in h029_src, bad
    vsrc = inspect.getsource(V3)
    assert '"F3"' not in vsrc and '"F6"' not in vsrc and V3.SIGNALS == ("F1", "F2", "F4", "F5", "F7", "F8")


def test_tether_moves_whole_vectors_keeps_eligibility_and_never_touches_h028():
    S = _setup()
    sc28_before = [s.copy() for s in S["sc28j"]]
    for seed in (1, 2):
        Vp = Q.tether_vectors(S["m29"], S["V29"], seed)
        dn = Q.donors(S["m29"], seed)
        prev = None
        for m, V, P, d in zip(S["m29"], S["V29"], Vp, dn):
            pos = {s: i for i, s in enumerate(m["ids"])}
            assert P.shape == V.shape and sorted(d) == m["ids"]                 # same eligible set
            for s, src in d.items():
                assert s != src                                                  # no self-match
                assert m["sector"][pos[s]] == m["sector"][pos[src]]              # Amendment 1: same FF12 sector
                assert np.array_equal(P[pos[s]], V[pos[src]], equal_nan=True)  # complete donor vector
            if prev is not None:
                kept = [s for s in m["ids"] if s in prev and prev[s] in pos and d[s] == prev[s]]
                assert len(kept) >= 0.5 * len([s for s in m["ids"] if s in prev and prev[s] in pos])
            prev = d
            assert np.all(np.isfinite(Q.h029_scores([P])[0]))                    # donors are eligible (>= 5 of 6)
        Q.world(S["m29"], S["m30"], S["V29"], S["sc28j"], S["j29"], S["w28"], S["spy"], S["days"], seed=seed)
        assert all(np.array_equal(a, b) for a, b in zip(S["sc28j"], sc28_before))
    assert Q.tether_vectors(S["m29"], S["V29"], None)[0] is S["V29"][0]


def test_sector_null_not_constructible_stops_without_fallback():
    S = _setup()
    m = dict(S["m29"][0])
    sec = np.asarray(m["sector"]).copy()
    sec[0] = 99                                                          # a sector with a single eligible stock
    m["sector"] = sec
    with pytest.raises(Q.NullNotConstructible):
        Q.tether_vectors([m], [S["V29"][0]], 1)


def test_sector_null_keeps_sector_composition_of_targets():
    """Within-sector reassignment keeps every sector's multiset of scores -> the score-only sector structure of the
    candidates is preserved month by month (what the single-stratum null broke, P14-CP3a)."""
    S = _setup()
    Vp = Q.tether_vectors(S["m29"], S["V29"], 3)
    for m, V, P in zip(S["m29"], S["V29"], Vp):
        sec = np.asarray(m["sector"])
        for g in np.unique(sec):
            a = np.sort(np.nan_to_num(V[sec == g], nan=-9.0), axis=0)
            b = np.sort(np.nan_to_num(P[sec == g], nan=-9.0), axis=0)
            assert np.array_equal(a, b)


def test_world_deterministic_and_row_layout():
    S = _setup()
    args = (S["m29"], S["m30"], S["V29"], S["sc28j"], S["j29"], S["w28"], S["spy"], S["days"])
    a, b = Q.world(*args, seed=5), Q.world(*args, seed=5)
    assert a == b and len(a) == len(Q.NULL_FIELDS) and a[0] == 5
    r = Q.world(*args, seed=None, keep=True)
    assert r["row"][0] is None and math.isfinite(r["row"][1]) and r["row"][10] == math.log(r["e30"]["wealth"] / S["w28"])
    # the real H030 score of each month is exactly the blend of the real H028 and real H029 scores on J
    for s30, a28, s29, j in zip(r["sc30"], S["sc28j"], r["sc29"], S["j29"]):
        assert np.array_equal(s30, Q.blend(a28, s29[j]))


def test_relative_statistics_and_concentration():
    labels = ["2015-01", "2015-02", "2018-01", "2018-02", "2020-03", "2021-05"]
    rs = np.array([0.02, -0.01, 0.03, -0.02, -0.10, 0.01])
    rh = np.array([0.03, -0.01, 0.02, -0.01, -0.05, 0.02])
    x = Q.relative(rh, rs, labels)
    rl = np.log1p(rh) - np.log1p(rs)
    assert x["s_up"] == pytest.approx(rl[[0, 2, 5]].sum())
    assert x["ex1820"] == pytest.approx(rl[[0, 1, 5]].sum())
    assert x["U"][2015] == pytest.approx(rl[0]) and x["A"][2020] == pytest.approx(rl[4])
    mx, tot, share = Q.concentration({2015: 0.1, 2016: -0.2, 2017: 0.3})
    assert (mx, tot) == (pytest.approx(0.3), pytest.approx(0.4)) and share == pytest.approx(0.75)


def _e(s_up, up, dn, mdd, wealth, U, A=None, ex=0.0, vol=0.15):
    return dict(rel=dict(s_up=s_up, U=U, A=A or U, ex1820=ex), risk=dict(up_capture=up, down_capture=dn),
                pm=dict(maxdd=mdd, vol=vol), wealth=wealth)


def test_gates_logic():
    spy = dict(pm=dict(maxdd=-0.30, vol=0.15), wealth=200_000.0)
    good = _e(0.3, 1.05, 1.0, -0.35, 0, {2015: 0.05, 2016: 0.05, 2017: 0.05, 2018: 0.05, 2019: 0.05, 2020: 0.05})
    g = Q.gates_h029(good, spy, 0.1, 0.2, 0.005)
    assert g["all"] and g["verdict"] == "H029 UPSIDE SIGNAL CANDIDATE"
    for mutate, gate in ((dict(p=0.02), "N1"), (dict(up=0.99), "N2"), (dict(conc=True), "N3"), (dict(dn=1.3), "N4"),
                         (dict(stress=-0.01), "N5")):
        e = _e(0.3, mutate.get("up", 1.05), mutate.get("dn", 1.0), -0.35, 0,
               {2015: 0.5, 2018: 0.05} if mutate.get("conc") else good["rel"]["U"])
        g = Q.gates_h029(e, spy, mutate.get("stress", 0.1), 0.2, mutate.get("p", 0.005))
        assert not g[gate] and not g["all"]
    A = {2015: 0.05, 2016: 0.05, 2017: 0.05, 2018: 0.05, 2019: 0.05, 2020: 0.05, 2021: 0.05}
    e30 = _e(0.1, 1.01, 0.75, -0.30, 330_000.0, A, A, ex=0.2)
    st = dict(w30=320_000.0, w28=300_000.0, spy=250_000.0)
    g = Q.gates_h030(e30, 320_000.0, spy, 0.05, 0.005, st)
    assert not g["C1"] or g["S_INC"] > 0.05
    assert g["C2"] is False                     # 330k < 1.05 x 320k
    g = Q.gates_h030(dict(e30, wealth=330_000.0), 300_000.0, spy, 0.05, 0.005, st)
    assert g["C2"] and g["C3"] and g["C4"] and g["C5"] and g["C6"] and g["C7"] and g["C1"] and g["all"]
    g = Q.gates_h030(dict(e30, wealth=330_000.0, risk=dict(up_capture=1.01, down_capture=0.81)), 300_000.0, spy,
                     0.05, 0.005, st)
    assert not g["C4"] and not g["all"]


def test_adequacy_rule():
    rng = np.random.default_rng(0)
    rows = [[s] + list(rng.normal([0, 3e5, 1, 0.8, 0.9, 0.18, -0.3, 0.6, 0.15, 0, 3e5, 1, 0.8, 0.9, 0.18, -0.3, 0.6,
                                   0.15, 0], 0.05)) for s in range(1, 201)]
    real = dict(turn29=0.6, hhi29=0.15, turn30=0.6, hhi30=0.15)
    assert Q.adequacy(rows, real)["ok"]
    bad = Q.adequacy(rows, dict(real, turn29=0.95))
    assert not bad["ok"] and bad["verdict"] == "STOP — H029/H030 NULL INADEQUATE"


def test_synthetic_a_not_and_b_beats_its_null():
    S = _setup(seed=4, miss=False)
    args = lambda V: (S["m29"], S["m30"], V, S["sc28j"], S["j29"], S["w28"], S["spy"], S["days"])  # noqa: E731
    VB = Q.synthetic_vectors(S["m29"], "B", Q.SYNTH_B_SEED)
    real = Q.world(*args(VB))[1]
    null = [Q.world(*args(VB), seed=s)[1] for s in range(1, 21)]
    assert real > max(null)
    VA = Q.synthetic_vectors(S["m29"], "A", Q.SYNTH_A_SEEDS[0])
    realA = Q.world(*args(VA))[1]
    nullA = [Q.world(*args(VA), seed=s)[1] for s in range(1, 21)]
    assert Q.empirical_p(nullA, realA) > 1 / 21


def test_critical_value_and_p_conventions():
    x = np.arange(5000, dtype=float)
    assert Q.critical_value(x) == 4950.0                      # the 50th largest of 5,000
    assert Q.empirical_p(x, 4999.0) == 2 / 5001
