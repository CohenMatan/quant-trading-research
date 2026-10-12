"""H027 pure module (owner D213): the world function equals the frozen H026 procedure line for line; the
LOWVOL-conditional permutation keeps LOWVOL with its stock and moves the ten other features as one donor vector by a
persistent tether; returns are never permuted; LV15_CONTROL; risk metrics reproduce the P11-CP2 numbers from the
committed E028-05 paths; gates A1-A6; adequacy rule; Newey-West regression; planted synthetic worlds A and B."""
import json
import math
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_h026 as H  # noqa: E402
import qr_h027 as G  # noqa: E402
from test_p11_h026 import synth  # noqa: E402


def _rec_core(r):
    return {k: r[k] for k in ("S_WEALTH", "excess_cagr", "maxdd", "vol", "years_beating", "lam")}


def test_world_function_equals_frozen_h026():
    beta = np.zeros(11)
    beta[0], beta[4] = 0.02, -0.015
    ms = synth(beta, seed=3)
    for seed in (None, 1, 2):
        a = H.run_world(ms, seed)
        b = G.run_world_xs(ms, H.permuted(ms, seed), seed=seed)
        assert _rec_core(a) == _rec_core(b)
    real = G.run_conditional(ms, None)                       # seed None = the real H026 / H027 assignment
    assert _rec_core(real) == _rec_core(H.run_world(ms, None))


def test_conditional_permutation_keeps_lowvol_and_moves_the_other_vector():
    ms = synth(np.zeros(11), seed=4)
    Xs = G.conditional_permuted(ms, 11)
    dn = G.donors(ms, 11)
    other = list(G.OTHER)
    for m, X, d in zip(ms, Xs, dn):
        assert np.array_equal(X[:, G.LOWVOL], m["X"][:, G.LOWVOL])           # LOWVOL never permuted
        pos = {s: i for i, s in enumerate(m["ids"])}
        for i, s in enumerate(m["ids"]):
            assert d[s] != s                                                 # no self-matching
            assert np.array_equal(X[i, other], m["X"][pos[d[s]], other])     # one donor's complete OTHER vector
        assert sorted(map(tuple, X[:, other])) == sorted(map(tuple, m["X"][:, other]))
    # persistence: a recipient keeps its donor while both stay in the population (synth ids are persistent)
    assert all(dn[t] == dn[t + 1] for t in range(len(dn) - 1))
    # returns, sectors, open flags and SPY are never touched
    ms2 = synth(np.zeros(11), seed=4)
    for a, b in zip(ms, ms2):
        for k in ("r_oo", "r_oc", "daily", "sector", "open_ok"):
            assert np.array_equal(a[k], b[k])
        assert a["spy_oo"] == b["spy_oo"] and a["ids"] == b["ids"]


def test_null_world_deterministic_with_full_record():
    ms = synth(np.zeros(11), seed=5)
    a, b = G.run_conditional(ms, 9), G.run_conditional(ms, 9)
    assert a == b and len(G.row(a)) == len(G.FIELDS)
    assert len(a["coef"]) == 7 and all(len(c) == 11 for c in a["coef"])


def test_lv15_control_picks_lowest_volatility():
    ms = synth(np.zeros(11), seed=6)
    m = ms[30]
    sc = G.lv15_scores([m])[0]
    tgt = H.pick(m, sc)
    lowest = np.argsort(m["raw"][:, G.LOWVOL], kind="stable")
    # independent walk: lowest raw volatility first, sector cap 3
    out, cnt = [], {}
    for i in lowest:
        if cnt.get(m["sector"][i], 0) >= 3:
            continue
        out.append(int(i))
        cnt[m["sector"][i]] = cnt.get(m["sector"][i], 0) + 1
        if len(out) == 15:
            break
    assert sorted(tgt) == sorted(out)


def test_risk_metrics_reproduce_the_postmortem_from_committed_paths():
    sys.path[:0] = [str(ROOT / "research/phase7")]
    from P7_CP3R_extract import joined, lines
    import qr_p7_export as E
    o = json.loads(E.unpack(joined(lines("E028-05"), "QRWR")))
    r = G.risk(o["daily_h026"], o["daily_spy"], np.asarray(o["days"]), 100000.0)
    pm = json.loads((ROOT / "research/phase11/cp2/P11_CP2_postmortem.json").read_text())["path"]["risk"]
    assert r["beta"] == pytest.approx(pm["beta_monthly"], abs=1e-12)
    assert r["down_capture"] == pytest.approx(pm["down_capture"], abs=1e-12)
    assert r["up_capture"] == pytest.approx(pm["up_capture"], abs=1e-12)


def test_gates_and_adequacy_and_p():
    h = dict(wealth=311000.0, cagr=0.176, maxdd=-0.26, vol=0.164)
    s = dict(wealth=262000.0, cagr=0.148, maxdd=-0.34, vol=0.177)
    lv = dict(wealth=280000.0, cagr=0.159, maxdd=-0.22, vol=0.14)
    yh = {y: 0.12 for y in H.OUTER_YEARS}
    ylv = {y: 0.10 for y in H.OUTER_YEARS}
    g = G.gates(h, s, lv, yh, yh, ylv, 300000.0, 250000.0, 270000.0, 0.10)
    assert g["all"] and g["years_beating_lv15"] == 7
    g2 = G.gates(h, s, lv, yh, yh, {**ylv, 2015: 0.5}, 300000.0, 250000.0, 270000.0, 0.10)
    assert g2["A4"] is False or g2["years_beating_lv15"] == 6
    assert G.gates(h, s, dict(lv, wealth=320000.0), yh, yh, ylv, 3e5, 2.5e5, 2.7e5, 0.1)["A2"] is False
    assert G.gates(h, s, lv, yh, yh, ylv, 3e5, 2.5e5, 3.1e5, 0.1)["A6"] is False
    assert G.gates(h, s, lv, yh, yh, ylv, 3e5, 2.5e5, 2.7e5, 0.5)["A1"] is False
    assert G.empirical_p([0.1] * 99 + [0.0] * 4901, 0.1) == pytest.approx(100 / 5001)
    rows = [[0, 0, 0, 0, -0.3, 0.2, 1.0, 1.0, 1.0] + [0] * 15 + ["x"] for _ in range(100)]
    real = dict(vol=0.164, maxdd=-0.261, beta=0.795, down_capture=0.776)
    assert G.adequacy(rows, real)["adequate"] is False
    rows[0][G.FIELDS.index("vol")] = 0.15
    rows[0][G.FIELDS.index("maxdd")] = -0.2
    rows[0][G.FIELDS.index("beta")] = 0.7
    rows[0][G.FIELDS.index("down_capture")] = 0.7
    assert G.adequacy(rows, real)["adequate"] is True                     # 1 of 100 = 1% each


def test_newey_west_regression_recovers_alpha():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 0.02, 400)
    y = 0.004 + 0.5 * x + rng.normal(0, 0.01, 400)
    r = G.nw_regression(y, x)
    assert r["alpha"] == pytest.approx(0.004, abs=0.002) and r["gamma"] == pytest.approx(0.5, abs=0.1)
    assert r["t_alpha"] > 3 and 0 < r["r2"] < 1 and r["alpha_annualised"] == pytest.approx(12 * r["alpha"])


def _percentile(beta, seed, nulls):
    ms = synth(beta, seed=seed)
    real = G.run_conditional(ms, None)["S_WEALTH"]
    s = [G.run_conditional(ms, k)["S_WEALTH"] for k in range(1, nulls + 1)]
    return float(np.mean(np.array(s) < real))


def test_planted_worlds_a_and_b():
    """World A: only LOWVOL predicts returns -> the real-style model is NOT systematically above the conditional null.
    World B: LOWVOL plus GPA predict returns -> the real model beats the conditional null."""
    a_beta = np.zeros(11)
    a_beta[G.LOWVOL] = -0.03
    b_beta = a_beta.copy()
    b_beta[H.FEATURES.index("GPA")] = 0.03
    pa = [_percentile(a_beta, seed, 9) for seed in (21, 22, 23)]
    pb = [_percentile(b_beta, seed, 9) for seed in (21, 22, 23)]
    assert np.median(pa) < 0.9
    assert min(pb) >= 0.9
