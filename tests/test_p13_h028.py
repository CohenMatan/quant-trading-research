"""H028 pure module (owner D217): lambda = 100 in every fit and no inner selection; with H027's schedule the fixed path
is the frozen qr_h026.run_world bit for bit; the exact replay; the 2016-2021 equality analysis (exact parts identical,
path-dependent parts bounded by the calibrated tolerance); the conditional null unchanged except lambda; planted
synthetic worlds A and B at lambda = 100."""
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_h026 as H  # noqa: E402
import qr_h027 as G  # noqa: E402
import qr_h028 as F  # noqa: E402
from test_p11_h026 import synth  # noqa: E402

SCH27 = F.schedule_h027([0.01, 100, 100, 100, 100, 100, 100])


def _ms(seed=3):
    beta = np.zeros(11)
    beta[0], beta[4] = 0.02, -0.015
    return synth(beta, seed=seed)


def test_fixed_lambda_every_fit_and_no_inner_selection(monkeypatch):
    ms = _ms()
    calls = dict(fit=[], sim=0)
    fit0, sim0 = H.Fitter.fit, H.simulate

    def fit_c(obj, cut, lam):
        calls["fit"].append(lam)
        return fit0(obj, cut, lam)

    def sim_c(*a, **kw):
        calls["sim"] += 1
        return sim0(*a, **kw)
    monkeypatch.setattr(H.Fitter, "fit", fit_c)
    monkeypatch.setattr(H, "simulate", sim_c)
    w = F.run_world_fixed(ms, [m["X"] for m in ms], full=True)
    assert calls["fit"] == [100.0] * 7 and calls["sim"] == 1                 # 7 fits, 1 portfolio simulation, no inner loop
    assert w["fits"] == [(Y, 100.0) for Y in H.OUTER_YEARS] and w["rec"]["lam"] == [100.0] * 7
    src = (ROOT / "src/qresearch/lean/qr_h028.py").read_text()
    assert "LAMBDAS:" not in src and "for lam in" not in src and "inner" not in src.split("def run_world_fixed")[1].split("def ")[0]


def test_h027_schedule_reproduces_frozen_run_world_bit_for_bit():
    ms = _ms()
    for seed in (None, 1, 2):
        Xs = G.conditional_permuted(ms, seed)
        a = G.run_world_xs(ms, Xs, full=True, seed=seed)                    # = qr_h026.run_world line for line
        b = F.run_world_fixed(ms, Xs, schedule=a["lam_y"], full=True, seed=seed)
        assert G.row(a["rec"]) == G.row(b["rec"])
        assert a["h"]["wealth"] == b["h"]["wealth"] and a["yh"] == b["yh"]
        for Y in H.OUTER_YEARS:
            ka, kb = (Y, a["lam_y"][Y]), (Y, b["lam_y"][Y])
            assert a["coef"][ka][0] == b["coef"][kb][0] and np.array_equal(a["coef"][ka][1], b["coef"][kb][1])
    r = H.run_world(ms, None, full=True)
    f = F.run_world_fixed(ms, [m["X"] for m in ms], schedule=r["lam_y"], full=True)
    assert r["h"]["wealth"] == f["h"]["wealth"] and r["rec"]["S_WEALTH"] == f["rec"]["S_WEALTH"]


def test_replay_is_exact():
    ms = _ms()
    w = F.run_world_fixed(ms, [m["X"] for m in ms], full=True)
    sub = [ms[i] for i in w["idx"]]
    r = F.replay(sub, w["scores"])
    assert r["wealth"] == w["h"]["wealth"]
    assert [x["turnover"] for x in r["months"]] == w["h"]["turnover"]
    assert sum(x["orders"] for x in r["months"]) == w["h"]["trades"]
    assert sum(x["commission"] for x in r["months"]) == pytest.approx(w["h"]["commissions"], abs=1e-9)
    for x in r["months"]:
        assert sum(x["weights"].values()) + x["cash_share"] == pytest.approx(1.0, abs=1e-12)


def test_equality_exact_parts_and_bounded_path_dependence():
    ms = _ms()
    eqs = []
    for sd in (1, 2, 3, 4):
        Xs = G.conditional_permuted(ms, sd)
        wa = F.run_world_fixed(ms, Xs, schedule=SCH27, full=True)
        wb = F.run_world_fixed(ms, Xs, full=True)
        e = F.equality(wb, wa, ms)
        assert e["exact_ok"] and e["coefficients_identical"] and e["scores_identical"] and e["held_sets_identical"]
        assert e["replay_exact"] and e["orders_identical_after_transition"] and e["lambda_100_both"]
        eqs.append(e)
    cal = F.max_abs_diffs(eqs)
    tol = F.tolerance(cal)
    assert all(tol[str(Y)]["ret"] >= F.TOL_FLOOR["ret"] for Y in F.EQUAL_YEARS)
    assert all(F.within_tolerance(e, tol)["ok"] for e in eqs)
    # a pipeline difference in 2016-2021 (different coefficients) is caught as NOT exact
    Xs = G.conditional_permuted(ms, 1)
    wa = F.run_world_fixed(ms, Xs, schedule=SCH27, full=True)
    wc = F.run_world_fixed(ms, Xs, schedule={**F.fixed_schedule(), 2018: 10.0}, full=True)
    assert not F.equality(wc, wa, ms)["exact_ok"]
    # a tolerance breach is caught
    bad = dict(eqs[0], per_year={Y: dict(v, ret_diff=v["ret_diff"] + 1.0) for Y, v in eqs[0]["per_year"].items()})
    assert not F.within_tolerance(bad, tol)["ok"]
    assert F.tol_sha(tol) == F.tol_sha({k: dict(v) for k, v in tol.items()})


def test_conditional_null_world_fixed_and_deterministic():
    ms = _ms(5)
    a, b = F.run_fixed_conditional(ms, 9), F.run_fixed_conditional(ms, 9)
    assert a == b and a["lam"] == [100.0] * 7 and len(F.row(a)) == len(F.FIELDS)
    real = F.run_fixed_conditional(ms, None)
    assert real == F.run_world_fixed(ms, [m["X"] for m in ms])


def _percentile(beta, seed, nulls):
    ms = synth(beta, seed=seed)
    real = F.run_fixed_conditional(ms, None)["S_WEALTH"]
    s = [F.run_fixed_conditional(ms, k)["S_WEALTH"] for k in range(1, nulls + 1)]
    return float(np.mean(np.array(s) < real))


def test_planted_worlds_a_and_b_at_lambda_100():
    a_beta = np.zeros(11)
    a_beta[G.LOWVOL] = -0.03
    b_beta = a_beta.copy()
    b_beta[H.FEATURES.index("GPA")] = 0.03
    pa = [_percentile(a_beta, seed, 9) for seed in (21, 22, 23)]
    pb = [_percentile(b_beta, seed, 9) for seed in (21, 22, 23)]
    assert np.median(pa) < 0.9
    assert min(pb) >= 0.9
