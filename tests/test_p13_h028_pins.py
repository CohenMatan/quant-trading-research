"""H028 pins (owner D217): spec and code hashes exactly as pinned; H026 / H027 pins and references unchanged; lambda =
100 only; configs refuse null runs before the tolerance table is pinned and real runs before c / adequacy."""
import json

import pytest

from qresearch import config, datafreeze_v21, experiment, p11h026, p12h027, p13h028 as P
import qr_h026 as H
import qr_h028 as F


def test_spec_and_code_hashes():
    assert P.file_sha256(P.SPEC) == P.SPEC_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if P.file_sha256(f) != h]
    assert not changed, f"pinned H028 code changed: {changed}"
    # the frozen H026 / H027 code the H028 host builds on is unchanged
    assert all(p11h026.file_sha256(f) == h for f, h in p11h026.CODE_SHA256.items())
    assert all(p12h027.file_sha256(f) == h for f, h in p12h027.CODE_SHA256.items())
    assert P.DATA_V21_MANIFEST_SHA256 == datafreeze_v21.manifest_sha()


def test_h027_references_match_its_committed_result():
    r = json.loads((config.REPO_ROOT / "research/phase12/cp1/P12_CP1_result.json").read_text())
    assert P.H027_REAL_WEALTH == r["portfolio"]["h027"]["wealth"]
    assert P.H027_REAL_S_WEALTH == r["gates"]["S_WEALTH"]
    assert P.H027_LAMBDA_SCHEDULE == [r["years"][str(y)]["lam"] for y in H.OUTER_YEARS]
    assert r["status"] == "H027 REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE"
    assert p12h027.C_WEALTH_CONDITIONAL == 0.05770235251912147 and p12h027.CANDIDATE is None      # H027 untouched
    assert p11h026.C_WEALTH == 0.22454658263960384 and p11h026.CANDIDATE is None                  # H026 untouched


def test_lambda_100_only():
    assert P.LAMBDA == F.LAMBDA == 100.0 and F.LAMBDA in H.LAMBDAS
    assert H.LAMBDAS == (0.01, 0.1, 1.0, 10.0, 100.0)            # the frozen H026 grid itself is untouched
    assert F.fixed_schedule() == {Y: 100.0 for Y in H.OUTER_YEARS}
    assert P.NULL_BATCHES == ((1, 2500), (2501, 5000)) and P.RERUN_SEEDS == (1, 25)
    assert F.TOL_FACTOR == 1.5 and F.TOL_FLOOR == dict(ret=0.0025, turnover=0.025) and F.CAL_SEEDS == tuple(range(1, 101))


def test_canary_config_validates_and_later_runs_refused_until_pinned():
    p = config.EXPERIMENTS_DIR / P.CANARY / "config.json"
    if not p.exists():
        return
    cfg = json.loads(p.read_text())
    experiment.validate(cfg)
    if P.TOLERANCE is None:
        bad = dict(cfg, experiment_id=P.NULL_RUNS[0], params=dict(cfg["params"], mode="null", seeds=[1, 2500]))
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
    if P.C_WEALTH_H028 is None or P.ADEQUATE is not True:
        bad = dict(cfg, kind="research", split="DEV", experiment_id=P.REAL, params=dict(cfg["params"], mode="real"))
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)


def test_tolerance_pinned_from_the_committed_canary():
    if P.TOLERANCE is None:
        return
    c = json.loads((config.REPO_ROOT / f"research/phase13/cp1/P13_CP1_canary_{P.CANARY}.json").read_text())
    assert c["passed"] == c["total"] and c["tolerance_table"] == P.TOLERANCE
    assert F.tol_sha(P.TOLERANCE) == P.TOLERANCE_SHA256 == c["tolerance_sha256"]


def test_threshold_pinned_from_the_committed_null():
    if P.C_WEALTH_H028 is None:
        return
    import hashlib
    path = config.REPO_ROOT / P.NULL_RESULT
    assert hashlib.sha256(path.read_bytes()).hexdigest() == P.NULL_RESULT_SHA256
    nr = json.loads(path.read_text())
    assert nr["c_wealth_h028"] == P.C_WEALTH_H028 and nr["worlds"] == 5000 and nr["all_checks"]
    assert nr["adequacy"]["adequate"] is True and P.ADEQUATE is True
    assert nr["status"] == "ADEQUATE — c_WEALTH_H028 MAY BE PINNED"
    assert nr["checks"]["rerun_1_25_rows_identical"] and nr["checks"]["rerun_1_25_coefficients_identical"]
    assert nr["checks"]["lambda_100_every_world"]


def test_real_config_carries_the_pins():
    p = config.EXPERIMENTS_DIR / P.REAL / "config.json"
    if P.THRESHOLD_COMMIT is None or not p.exists():
        return
    cfg = json.loads(p.read_text())
    experiment.validate(cfg)
    pr = cfg["params"]
    assert pr["c_wealth_h028"] == P.C_WEALTH_H028 and pr["null_result_sha256"] == P.NULL_RESULT_SHA256
    assert pr["threshold_commit"] == P.THRESHOLD_COMMIT and pr["mode"] == "real"
    assert pr["tolerance"] == P.TOLERANCE and pr["tolerance_sha256"] == P.TOLERANCE_SHA256
    assert pr["h027_lambda_schedule"] == P.H027_LAMBDA_SCHEDULE and cfg["kind"] == "research" and cfg["split"] == "DEV"


def test_committed_result_is_consistent_and_rejected():
    p = config.REPO_ROOT / P.RESULT
    if not p.exists():
        return
    r = json.loads(p.read_text())
    g = r["gates"]
    assert all(r["pins"].values()) and all(r["reproduction_h027"].values()) and r["host_gates_reproduced"]
    assert r["equality"]["exact"]["exact_ok"] and r["equality"]["tolerance_check"]["ok"]
    assert r["adequacy_step2"]["adequate"] is True
    assert g["all"] == all(g[k] for k in ("B1", "B2", "B3", "B4", "B5", "B6"))
    assert g["B4"] is False and g["all"] is False and g["B4_detail"]["L_2015_2017"] < 0
    assert r["status"] == "H028 REJECTED — FIXED STRONG SHRINKAGE DOES NOT ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM"
    assert r["final_model"] is None and r["final_score_status"] is None and P.CANDIDATE is None
    assert r["comparison"]["S_WEALTH"]["h027"] == P.H027_REAL_S_WEALTH
    assert g["c_wealth_h028"] == P.C_WEALTH_H028 and g["null_worlds"] == 5000
    assert all(v["lam"] == 100.0 for v in r["coefficients"].values())
