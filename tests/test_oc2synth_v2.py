"""OC-2 synthetic calibration v2 (owner D249): software checks of the v2 generator, inference, scenario set,
classifier and the locked driver (engineering only; no scenario rejection rate or power is computed here)."""
import hashlib
import itertools
import json
import math
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path[:0] = [str(ROOT / "research/longhorizon/oc2/v2"), str(ROOT / "src")]
from qresearch import oc2synth_v2 as V  # noqa: E402
import OC2_V2_scenarios as S  # noqa: E402
import OC2_V2_run as R  # noqa: E402

V2 = ROOT / "research/longhorizon/oc2/v2"


def test_fixed_b_cv_reproducible_and_above_normal():
    cv = V.fixed_b_cv(draws=200_000, seed=118007)
    for a in V.CV:
        assert abs(cv[a] - V.CV[a]) < 0.04
    assert V.CV[0.05] > 1.6449 and V.CV[0.01] > 2.3263


def test_payoff_regimes_pinned():
    assert sorted(V.G_SD) == [0.06, 0.09, 0.12]
    assert V.G_SD[0.06] < V.G_SD[0.09] < V.G_SD[0.12]
    with pytest.raises(ValueError):
        V.payoff_sd(V.World("x", ic_sd=0.10))


def test_n7_budget_guard():
    with pytest.raises(ValueError):
        V.variance_budget(V.World("v1-N7", sigma_sector=0.05, sigma_factor=0.02), V.G_SD[0.09])
    for w in S.all_nulls() + S.POWER:
        if not w.iid:
            assert V.variance_budget(w, V.payoff_sd(w)) > 0.03


@pytest.mark.parametrize("n_scale,churn", [(0.1, 2.0), (1.0, 0.0)])
def test_n13_overlapping_response_finite(n_scale, churn):
    o = V.run_world(V.World("T-N13", priced=V.CONTROLS, horizon=3, n_scale=n_scale, churn=churn), 0, tag="TEST",
                    diag_rank=False)
    assert "failed" not in o
    assert all(math.isfinite(o[k]) for k in ("t", "mean_slope", "tq_annual", "se_nw7"))


def test_determinism_and_seed_separation():
    w = V.World("T-DET", priced=V.CONTROLS, n_scale=0.2)
    assert V.run_world(w, 1, tag="TEST") == V.run_world(w, 1, tag="TEST")
    assert V.seed_of("N4", 0, "DEV") != V.seed_of("N4", 0, "FINAL")
    assert V.seed_of("N4", 0) == V.seed_of("N4", 0, "FINAL")


def test_dimensions_and_missing_controls():
    w = V.World("T-DIM", priced=V.CONTROLS)
    P = V.Panel(w, 5)
    for t in range(-V.WARMUP, 0):
        P.step(t)
        P.returns_all()
    sample, live = P.step(0)
    assert set(sample) <= set(live)
    assert 0.90 < len(sample) / len(live) < 0.99           # 5% MAR complete-case
    assert len(live) == V.O.n_by_month()[0]
    assert P.controls(sample).shape == (len(sample), 8)
    assert P.returns_all().shape == (P.S,)
    sig = P.sig[sample]
    X, Xk = V.designs(sig, P.controls(sample), P.sec[sample])
    assert X.shape[1] == 1 + 8 * 4 + len(V.O.SECTORS) and Xk.shape[1] == 1 + 8 + len(V.O.SECTORS)


def test_rcs_basis_linear_tails():
    x = np.linspace(-5, 5, 2001)
    B = V.rcs_basis(x)
    lo, hi = x < V.KNOTS[0], x > V.KNOTS[-1]
    assert np.allclose(B[lo, 1:], 0.0)
    for j in range(1, B.shape[1]):
        d2 = np.diff(B[hi, j], 2)
        assert np.allclose(d2, 0.0, atol=1e-9)


def test_partial_slope_is_ols_coefficient():
    rng = np.random.default_rng(3)
    n = 500
    Z = rng.standard_normal((n, 8))
    sig = Z[:, 3] * 0.2 + rng.standard_normal(n)
    sec = rng.integers(0, len(V.O.SECTORS), n)
    y = rng.standard_normal(n) * 0.06
    X, _ = V.designs(sig, Z, sec)
    b = np.linalg.lstsq(X, y, rcond=None)[0][0]
    assert math.isclose(V.partial_slopes(X, y)[0], b, rel_tol=1e-8)


def test_nw_se_lag0_is_iid():
    b = np.random.default_rng(1).standard_normal(118)
    assert math.isclose(V.nw_se(b, 0), b.std() / math.sqrt(118), rel_tol=1e-12)
    assert V.NW_LAG == 7 and round(1.1447 * (4 * .25 / (1 - .25) ** 2 * 118) ** (1 / 3)) == 7    # Andrews AR(1), rho 0.5


def test_classifier_precedence():
    for comp, adq, size, ident, p in itertools.product([True, False], [True, False], [True, False], [True, False],
                                                        [0.5, 0.9]):
        o = V.classify(comp, adq, size, ident, p)
        if not comp or not adq:
            assert o.startswith("D")
        elif not size or not ident:
            assert o.startswith("C")
        else:
            assert o.startswith("A" if p >= 0.80 else "B")


def test_scenarios_cover_owner_list():
    assert sorted(S.NULLS) == list(range(1, 15))
    names = [w.name for w in S.all_nulls()] + [S.ORACLE.name] + [w.name for w in S.POWER]
    assert len(names) == len(set(names))
    assert set(S.IDENT) <= {w.name for w in S.all_nulls()}
    assert all(w.planted == 0 for w in S.all_nulls()) and all(w.planted > 0 for w in S.POWER)
    assert {w.name for w in S.POWER} >= {f"P{e}-{r}" for e in (2, 3, 4, 5) for r in (0.06, 0.09, 0.12)}
    assert R.POWER_CELL in {w.name for w in S.POWER}


def test_decide_rule():
    good = dict(n=4000, failures=0, failure_share=0.0, **{"rej_0.05": 0.05, "rej_0.01": 0.01,
                "rej_0.05_completed": 0.05, "rej_0.01_completed": 0.01}, full_rule=0.0, pic_sd=0.09,
                fresh_by_phase=list(R.STAGE1_FRESH), mean_n=float(np.mean(V.O.n_by_month())) * 0.95,
                corr=[V.O.RHO_F5[c] for c in V.O.CONTROLS])
    res = {"N0": dict(good), "N4": dict(good), "N5a": dict(good, **{"rej_0.05": 0.09}), "N2L": dict(good),
           R.POWER_CELL: dict(good, **{"rej_0.01": 0.85})}
    roles = {"N0": "gate", "N4": "gate", "N5a": "ident", "N2L": "ident", R.POWER_CELL: "power"}
    assert R.decide(res, roles, 1)["outcome"].startswith("C")
    assert R.decide(res, roles, 2)["outcome"].startswith("A")
    res["N2L"]["full_rule"] = 0.03
    assert R.decide(res, roles, 2)["outcome"].startswith("C")
    res["N0"]["failure_share"] = 0.02
    assert R.decide(res, roles, 2)["outcome"].startswith("D")


def test_driver_locked_until_frozen():
    if (V2 / "FROZEN.json").exists():
        pytest.skip("protocol frozen")
    with pytest.raises(SystemExit):
        R.frozen_or_refuse()


def test_no_real_data_paths():
    src = (ROOT / "src/qresearch/oc2synth_v2.py").read_text()
    for bad in ("open(", "read_text", "read_bytes", "Path(", "requests", "urllib", "qc_api", "sec_contact"):
        assert bad not in src
    for f in ("OC2_V2_scenarios.py", "OC2_V2_run.py", "OC2_V2_engineering.py", "OC2_V2_audit.py"):
        txt = (V2 / f).read_text()
        for bad in ("research/phase", "data_v3", "datafreeze", "requests", "urllib", "QC_API", "sec_contact"):
            assert bad not in txt, (f, bad)


def test_engineering_record():
    fp = V2 / "OC2_V2_engineering.json"
    if not fp.exists():
        return
    d = json.loads(fp.read_text())
    assert d["fixed_b_cv"]["identical"] and d["payoff_calibration"]["identical_to_pinned"]
    assert d["N7_budget"]["v1_parameters"].startswith("refused")
    assert d["all_worlds_run"]["failures"] == [] and d["determinism"]["identical"]
    for r, s in d["regimes"].items():
        assert abs(s["pic_sd"] / float(r) - 1) < 0.15 and s["failed"] == 0
    assert all(v["failed"] == 0 for v in d["N13"].values())


def test_draft_hashes_record():
    fp = V2 / "OC2_V2_draft_hashes.json"
    if not fp.exists():
        return
    d = json.loads(fp.read_text())
    for rel, h in d["files"].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel
