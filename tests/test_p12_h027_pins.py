"""H027 pins (owner D213): spec and code hash exactly as pinned; H026 pins and references unchanged; Data v2.1 = the
D207 manifest with the D213 owner exception; configs refuse unpinned or inadequate real runs."""
import json

import pytest

from qresearch import config, datafreeze_v21, experiment, p11h026, p12h027 as P
import qr_h026 as H
import qr_h027 as G


def test_spec_and_code_hashes():
    assert P.file_sha256(P.SPEC) == P.SPEC_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if P.file_sha256(f) != h]
    assert not changed, f"pinned H027 code changed: {changed}"
    # the frozen H026 code the H027 host builds on is unchanged
    assert all(p11h026.file_sha256(f) == h for f, h in p11h026.CODE_SHA256.items())
    assert P.DATA_V21_MANIFEST_SHA256 == datafreeze_v21.manifest_sha()


def test_h026_references_match_its_committed_result():
    r = json.loads((config.REPO_ROOT / "research/phase11/cp1/P11_CP1_result.json").read_text())
    assert P.H026_REAL_WEALTH == r["portfolio"]["h026"]["wealth"]
    assert P.H026_REAL_S_WEALTH == r["gates"]["S_WEALTH"]
    assert P.H026_FEATURE_PANEL_SHA256 == p11h026.FEATURE_PANEL_SHA256
    assert P.H026_RESPONSE_PANEL_SHA256 == p11h026.RESPONSE_PANEL_SHA256
    assert p11h026.C_WEALTH == 0.22454658263960384 and p11h026.CANDIDATE is None      # H026 untouched


def test_frozen_parameters():
    assert H.LAMBDAS == (0.01, 0.1, 1.0, 10.0, 100.0) and H.HORIZON == 63 and H.K == 15 and H.SECTOR_CAP == 3
    assert G.LOWVOL == 1 and len(G.OTHER) == 10 and G.R_NULL == 5000 and G.ADEQUACY_MIN_SHARE == 0.01
    assert P.NULL_BATCHES == ((1, 2500), (2501, 5000)) and P.RERUN_SEEDS == (1, 25)


def test_canary_config_validates_and_real_refused_until_pinned():
    cfg = json.loads((config.EXPERIMENTS_DIR / P.CANARY / "config.json").read_text())
    experiment.validate(cfg)
    if P.C_WEALTH_CONDITIONAL is None or P.ADEQUATE is not True:
        bad = dict(cfg, kind="research", split="DEV", experiment_id=P.REAL, params=dict(cfg["params"], mode="real"))
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)


def test_threshold_pinned_from_the_committed_null():
    if P.C_WEALTH_CONDITIONAL is None:
        return
    import hashlib
    path = config.REPO_ROOT / P.NULL_RESULT
    assert hashlib.sha256(path.read_bytes()).hexdigest() == P.NULL_RESULT_SHA256
    nr = json.loads(path.read_text())
    assert nr["c_wealth_conditional"] == P.C_WEALTH_CONDITIONAL and nr["worlds"] == G.R_NULL and nr["all_checks"]
    assert nr["adequacy"]["adequate"] is True and P.ADEQUATE is True
    assert nr["status"] == "ADEQUATE — c_WEALTH_CONDITIONAL MAY BE PINNED"
    assert nr["checks"]["rerun_1_25_rows_identical"] and nr["checks"]["rerun_1_25_coefficients_identical"]


def test_real_config_carries_the_pins():
    p = config.EXPERIMENTS_DIR / P.REAL / "config.json"
    if P.THRESHOLD_COMMIT is None or not p.exists():
        return
    cfg = json.loads(p.read_text())
    experiment.validate(cfg)
    pr = cfg["params"]
    assert pr["c_wealth_conditional"] == P.C_WEALTH_CONDITIONAL and pr["null_result_sha256"] == P.NULL_RESULT_SHA256
    assert pr["threshold_commit"] == P.THRESHOLD_COMMIT and pr["mode"] == "real"
    assert pr["h026_real_wealth"] == P.H026_REAL_WEALTH and pr["h026_real_s_wealth"] == P.H026_REAL_S_WEALTH


def test_committed_result_is_consistent_and_rejected():
    p = config.REPO_ROOT / P.RESULT
    if not p.exists():
        return
    r = json.loads(p.read_text())
    g = r["gates"]
    assert all(r["pins"].values()) and all(r["reproduction"].values()) and r["host_gates_reproduced"]
    assert g["all"] == all(g[k] for k in ("A1", "A2", "A3", "A4", "A5", "A6"))
    assert g["A4"] is False and g["all"] is False
    assert r["status"] == "H027 REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE"
    assert r["final_model"] is None and r["final_score_status"] is None and P.CANDIDATE is None
    assert g["S_WEALTH"] == P.H026_REAL_S_WEALTH and r["portfolio"]["h027"]["wealth"] == P.H026_REAL_WEALTH
    assert g["c_wealth_conditional"] == P.C_WEALTH_CONDITIONAL and g["null_worlds"] == G.R_NULL
