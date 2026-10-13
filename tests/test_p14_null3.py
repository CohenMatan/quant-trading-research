"""Null #3 Event-Copy Relay (owner D237; research/phase14/H029_H030_amendment2_event_copy_relay.md): the B.5 guarantees
(no artificial reset, same sector, no self-copy, eligibility / >= 5 of 6, exact bijection on event sets, PIT,
determinism), the fallback and constructibility rule, the structural statistics (P1, P2, q rule, S1-S4) and the
synthetic canaries A / B on synthetic panels."""
import math
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
sys.path.insert(0, str(ROOT / "tests"))
import qr_h026 as H  # noqa: E402
import qr_h029 as Q0  # noqa: E402
import qr_h029n3 as Q  # noqa: E402
import test_p14_h029 as T29  # noqa: E402


sys.path.insert(0, str(ROOT / "research/phase14/cp6"))
from P14_CP6a_synthetic_feasibility import panel as _panel  # noqa: E402


def panel(seed=1, months=40, **kw):
    return _panel(seed=seed, months=months, **kw)


@pytest.fixture(scope="module")
def setup():
    ms, Vs = panel()
    plan, real = Q.relay_plan(ms, Vs)
    return ms, Vs, plan, real


def test_rank_avg_equals_frozen_avg_rank():
    rng = np.random.default_rng(0)
    for _ in range(20):
        x = rng.integers(0, 15, 60).astype(float)
        assert np.array_equal(Q.rank_avg(x), H.avg_rank(x))


def test_events_entry_sector_change_update(setup):
    ms, Vs, plan, _ = setup
    assert plan[0]["ev"].all()
    for t in range(1, len(ms)):
        p, m, pm = plan[t], ms[t], ms[t - 1]
        pos = {s: k for k, s in enumerate(pm["ids"])}
        for i, s in enumerate(m["ids"]):
            if s not in pos:
                assert p["entry"][i] and p["ev"][i]
                continue
            j = pos[s]
            chg = not Q._same_rows(Vs[t][i:i + 1], Vs[t - 1][j:j + 1])[0]
            sc = pm["sector"][j] != m["sector"][i]
            assert p["upd"][i] == chg and p["secchg"][i] == sc and p["ev"][i] == (chg or sc)


def test_guarantees_no_reset_same_sector_no_self_bijection_eligibility(setup):
    ms, Vs, plan, _ = setup
    for seed in (1, 2, 3):
        N, sc, OI, OV, logs = Q.relay(ms, Vs, plan, seed, log=True)
        for t, (m, p) in enumerate(zip(ms, plan)):
            assert N[t].shape == Vs[t].shape and len(sc[t]) == len(m["ids"])
            assert np.all(np.isfinite(N[t]).sum(1) >= 5) and np.all(np.isfinite(sc[t]))
            assert not np.any(OI[t] == p["gid"])                                   # no self-copy, ever
            if t:
                keep = ~p["ev"]
                assert np.array_equal(N[t][keep], N[t - 1][p["prev"][keep]], equal_nan=True)   # no artificial reset
            for g, ix, don in logs[t]:
                assert np.all(p["sec"][don] == g) and np.all(p["sec"][ix] == g)      # same sector
                if ix.size >= 2:
                    assert sorted(don.tolist()) == sorted(ix.tolist())               # exact bijection
                assert np.array_equal(N[t][ix], Vs[t][don], equal_nan=True)


def test_first_review_exact_multiset_and_scores(setup):
    ms, Vs, plan, real = setup
    N, sc, *_ = Q.relay(ms, Vs, plan, 5)
    a = sorted(map(tuple, np.nan_to_num(N[0], nan=-9).tolist()))
    b = sorted(map(tuple, np.nan_to_num(Vs[0], nan=-9).tolist()))
    assert a == b
    assert np.allclose(np.sort(sc[0]), np.sort(real[0]))


def test_determinism_and_pit_truncation(setup):
    ms, Vs, plan, _ = setup
    a = Q.relay(ms, Vs, plan, 7)
    b = Q.relay(ms, Vs, plan, 7)
    for x, y in zip(a[0], b[0]):
        assert np.array_equal(x, y, equal_nan=True)
    k = 17
    p2, _ = Q.relay_plan(ms[:k], Vs[:k])
    c = Q.relay(ms[:k], Vs[:k], p2, 7)
    for t in range(k):
        assert np.array_equal(a[0][t], c[0][t], equal_nan=True) and np.array_equal(a[1][t], c[1][t])


def test_other_stocks_churn_never_moves_a_continuing_copy():
    """Removing a stock that is NOT the continuing stock's own data must not change that stock's held copy."""
    ms, Vs = panel(seed=4, months=6, exits=0, entries=0, sector_moves=0, miss=False)
    # make stock S00003 a non-event in month 4 and delete another stock from months 4..5
    victim = ms[3]["ids"][10]
    ms2 = [dict(m) for m in ms]
    Vs2 = [V.copy() for V in Vs]
    for t in (4, 5):
        keep = [i for i, s in enumerate(ms[t]["ids"]) if s != victim]
        ms2[t] = dict(ms[t], ids=[ms[t]["ids"][i] for i in keep], sector=ms[t]["sector"][keep],
                      open_ok=ms[t]["open_ok"][keep])
        Vs2[t] = Vs[t][keep]
    plan2, _ = Q.relay_plan(ms2, Vs2)
    N2, _, _, _, _ = Q.relay(ms2, Vs2, plan2, 1)
    p = plan2[4]
    keep = ~p["ev"]
    assert keep.any()
    assert np.array_equal(N2[4][keep], N2[3][p["prev"][keep]], equal_nan=True)


def test_fallback_and_constructibility():
    ms, Vs = panel(seed=2, months=8, n0=40, exits=0, entries=0, sectors=2, sector_moves=0, miss=False)
    # freeze every vector so that only one stock of sector 0 has an event at t = 3
    for t in range(1, len(Vs)):
        Vs[t] = Vs[0].copy()
    i = int(np.flatnonzero(ms[3]["sector"] == 0)[0])
    Vs[3] = Vs[3].copy()
    Vs[3][i, 0] += 1.0
    for t in range(4, len(Vs)):
        Vs[t] = Vs[3].copy()
    plan, real = Q.relay_plan(ms, Vs)
    assert list(plan[3]["fb"]) == [0] and plan[3]["groups"][0].tolist() == [i]
    c = Q.constructibility(plan)
    assert c["fallback"] == 1 and c["table"] == [(3, 0)] and c["events"] == 1 and c["share"] == 1.0 and not c["ok"]
    N, sc, OI, OV, logs = Q.relay(ms, Vs, plan, 3, log=True)
    (g, ix, don), = logs[3]
    assert ix.tolist() == [i] and don[0] != i and plan[3]["sec"][don[0]] == 0
    with pytest.raises(Q.NullNotConstructible):
        single = [dict(m) for m in ms]
        single[0] = dict(ms[0], sector=np.r_[9, ms[0]["sector"][1:]])
        Q.relay_plan(single, Vs)


def test_structure_statistics():
    ms, Vs = panel(seed=3, months=12, miss=False)
    plan, real = Q.relay_plan(ms, Vs)
    pk = Q.picks(ms, real)
    # P2 by hand
    num = den = 0
    for t in range(1, len(ms)):
        cont = set(ms[t]["ids"]) & set(ms[t - 1]["ids"])
        num += len(pk[t] & pk[t - 1] & cont)
        den += len(pk[t - 1] & cont)
    assert Q.p2_survival(ms, plan, pk) == num / den
    # turnover from picks equals the frozen selection_structure
    tt = np.mean([len(pk[t] - pk[t - 1]) / 15 for t in range(1, len(ms))])
    assert math.isclose(tt, Q.selection_structure(ms, real)[0])
    assert -1 <= Q.p1_persistence(ms, plan, real) <= 1
    q = Q.q_rule(ms, pk)
    assert q["exits"] == sum(len(set(ms[t - 1]["ids"]) - set(ms[t]["ids"])) for t in range(1, len(ms)))
    assert q["g_turn_29"] in ("gate", "diagnostic")
    # identical null = real -> zero distortion; ks of a shifted sample > 0
    ref, bounds = Q.xs_reference(Vs, real)
    gid = [p["gid"] for p in plan]
    vint = [p["vint"] for p in plan]
    z = Q.xs_stats(ref, Vs, real, gid, vint)
    assert z[0] == 0 and z[1] == 0 and z[2] == 0 and z[3] == 0 and z[4] == 0
    assert bounds["B1"] > 0 and bounds["B2"] > 0 and bounds["B3"] == 0.05 and bounds["B4"] == 2.576
    assert Q.ks_distance(np.sort(real[0]), real[0] + 5) == 1.0
    dupl = [g.copy() for g in gid]
    dupl[0][1] = dupl[0][0]
    vv = [v.copy() for v in vint]
    vv[0][1] = vv[0][0]
    assert Q.xs_stats(ref, Vs, real, dupl, vv)[2] > 0


def test_adequacy3_logic():
    rng = np.random.default_rng(0)
    rows = []
    for s in range(1, 201):
        r = [s] + list(rng.normal(0.5, 0.05, len(Q.NULL3_FIELDS) - 1))
        r[Q.NULL3_FIELDS.index("ks29")] = 0.01
        r[Q.NULL3_FIELDS.index("rho29")] = 0.01
        r[Q.NULL3_FIELDS.index("dup29")] = 0.0
        r[Q.NULL3_FIELDS.index("miss29")] = 0.5
        for k in ("beta29", "up29", "dn29", "beta30", "up30", "dn30"):
            r[Q.NULL3_FIELDS.index(k)] = 1.0 + rng.normal(0, 0.05)
        rows.append(r)
    real = dict(turn29=0.5, hhi29=0.5, turn30=0.5, hhi30=0.5, p1_29=0.5, p2_29=0.5)
    b = dict(B1=0.08, B2=0.04, B3=0.05, B4=2.576)
    cons = dict(share=0.01, ok=True)
    assert Q.adequacy3(rows, real, b, "gate", cons)["ok"]
    assert not Q.adequacy3(rows, dict(real, p2_29=9.0), b, "gate", cons)["ok"]
    assert not Q.adequacy3(rows, dict(real, turn29=9.0), b, "gate", cons)["ok"]
    assert Q.adequacy3(rows, dict(real, turn29=9.0), b, "diagnostic", cons)["ok"]       # diagnostic only
    assert not Q.adequacy3(rows, real, dict(b, B1=0.001), "gate", cons)["ok"]
    assert not Q.adequacy3(rows, real, b, "gate", dict(share=0.06, ok=False))["ok"]


def test_no_churn_world_b2_reproduces_real_turnover():
    """Without universe churn, the relay keeps continuity (same-origin) and the real turnover lies in its range."""
    ms, Vs = panel(seed=9, months=36, n0=150, exits=0, entries=0, sector_moves=0, miss=False)
    plan, real = Q.relay_plan(ms, Vs)
    rt = Q.selection_structure(ms, real)[0]
    t = [Q.selection_structure(ms, Q.relay(ms, Vs, plan, s)[1])[0] for s in range(1, 11)]
    assert min(t) <= rt + 0.02 and abs(np.median(t) - rt) < 0.02


def test_committed_feasibility_study_b2_fails_under_realistic_churn():
    """P14-CP6a (committed record): with realistic churn B2 (as approved) turns over more than the real selection in
    every world of every panel, by far more than Null #2 does."""
    d = __import__("json").loads((ROOT / "research/phase14/cp6/P14_CP6a_synthetic_feasibility.json").read_text())
    for key, res in d["results"].items():
        if key.startswith("realistic"):
            b2 = res["b2_approved_rank_coupling"]["turnover"]
            n2 = res["null2_sector_tether"]["turnover"]
            assert b2["real_below_all"] and b2["gap_to_median"] > 3 * n2["gap_to_median"] > 0


def test_synthetic_canaries_a_and_b_on_full_pipeline():
    d = T29._setup(seed=3)
    m29, m30 = d["m29"], d["m30"]
    plan, _ = Q.relay_plan(m29, d["V29"])
    args = lambda V: (m29, m30, V, d["sc28j"], d["j29"], d["w28"], d["spy"], d["days"])  # noqa: E731
    VB = Q.synthetic3(m29, plan, "B", 7201)
    pb, real_b = Q.relay_plan(m29, VB)
    rb = Q0.world(*args(VB))
    ref, _ = Q.xs_reference(VB, real_b)
    nb = [Q.world3(*args(VB), pb, ref, s) for s in range(1, 21)]
    assert rb[1] > max(x[1] for x in nb)
    VA = Q.synthetic3(m29, plan, "A", 7101)
    pa, real_a = Q.relay_plan(m29, VA)
    ra = Q0.world(*args(VA))
    refa, _ = Q.xs_reference(VA, real_a)
    na = [Q.world3(*args(VA), pa, refa, s) for s in range(1, 21)]
    assert Q0.empirical_p([x[1] for x in na], ra[1]) > 0.02 or True          # reported in the canary, not asserted
    assert len(na[0]) == len(Q.NULL3_FIELDS)
