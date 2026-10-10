"""D190 Data Infrastructure v2 freeze (P7-CP5f): every frozen file must hash exactly as in the manifest, the manifest
itself is pinned, the frozen rules and reference hashes are recorded, and the old c_IC is labelled data-v1-only. A
failing test means frozen infrastructure changed: stop, document, obtain owner approval and issue a new freeze version
before re-running anything affected."""
import json

import pytest

from qresearch import config, datafreeze_v2, p7pred, p7score

FROZEN = datafreeze_v2.MANIFEST_SHA256 is not None


def test_old_c_ic_is_labelled_data_v1_only():
    assert p7pred.C_IC == 2.390976216956
    assert p7pred.C_IC_STATUS == "DATA_V1_ONLY / UNUSED_ON_V2"
    assert "UNUSED_ON_V2" in datafreeze_v2.RULES["old_c_ic"]


def test_rules_restate_the_owner_approved_v2_rules():
    r = datafreeze_v2.RULES
    assert r["window"]["decisions"] == ["2011-01-31", "2017-11-30", 83]
    assert r["universe"]["min_market_cap"] == 2e9 and r["universe"]["sec_share_max_age_days"] == 135
    assert "no +90" in r["timing_m2"] and "no FileDate" in r["timing_m2"]
    m = r["mechanics"]
    assert (m["entry"], m["exit"], m["buffer"], m["K"], m["initial_cap"], m["sector_max_ff12"], m["grown_winner_cap"]) == \
        (80, 70, 5, 10, 0.10, 3, 0.20)
    assert m["regime_positions"] == dict(STRONG=10, NORMAL=8, WEAK=5, RISK_OFF=2) == p7pred.MECHANICS["REGIME_POSITIONS"]
    assert r["costs"] == dict(commission_per_order=7.0, slippage_bps_per_side=10, capital=[100000, 200000])


@pytest.mark.skipif(not FROZEN, reason="Data v2 not frozen (freeze gates not all passed)")
def test_manifest_is_pinned():
    assert datafreeze_v2.manifest_sha() == datafreeze_v2.MANIFEST_SHA256


@pytest.mark.skipif(not FROZEN, reason="Data v2 not frozen (freeze gates not all passed)")
def test_every_frozen_file_matches_the_manifest():
    m = json.loads((config.REPO_ROOT / datafreeze_v2.MANIFEST).read_text())
    assert m["version"] == datafreeze_v2.VERSION
    assert sorted(m["files"]) == datafreeze_v2.files()
    changed = [f for f, h in m["files"].items() if datafreeze_v2.sha(f) != h]
    assert not changed, f"frozen Data v2 infrastructure changed: {changed}"
    assert datafreeze_v2.build() == m


@pytest.mark.skipif(not FROZEN, reason="Data v2 not frozen (freeze gates not all passed)")
def test_manifest_records_score_reference_runs_and_gates():
    m = json.loads((config.REPO_ROOT / datafreeze_v2.MANIFEST).read_text())
    assert m["score_v1"]["spec_sha256"] == p7score.SPEC_SHA256
    ref = json.loads((config.REPO_ROOT / "research/phase7/data_v2/data_v2_reference.json").read_text())
    assert m["reference"]["table_sha256"] == ref["table_sha256"]
    assert set(m["runs"]) == set(datafreeze_v2.RUNS)
    assert all(r["status"] == "completed" and r["lean_version"] for r in m["runs"].values())
    # D192: frozen with an owner-approved gate K exception; the original gate results are preserved, never relabelled
    g = m["freeze_gates"]
    assert m["status"] == "FROZEN — OWNER-APPROVED GATE K EXCEPTION"
    assert g["all"] is False and g["K_identity_sanity_not_material"] is False and g["K_survivorship_bounds"] is False
    assert sorted(k for k, v in g.items() if v is False and k != "all") == \
        ["K_identity_sanity_not_material", "K_survivorship_bounds"]          # every other gate passed
    x = m["gate_k_exception"]
    assert x["decision"] == "D192" and x["resolution"] == "OWNER-APPROVED EXCEPTION"
    assert x["gate_k"] == "FAILED under the original pre-registered 3%-per-year identity-incidence criterion."
    assert "<= 3% every year (unchanged)" in x["criterion_incidence"] and "<= 1.0 point" in x["criterion_tilt"]
    assert x["residual"]["affected_securities"] == 161 == x["residual"]["identity_reject"] + x["residual"]["no_identity_row"]
    assert m["candidate_manifest_sha256"] == datafreeze_v2.CANDIDATE_MANIFEST_SHA256


@pytest.mark.skipif(not FROZEN, reason="Data v2 not frozen")
def test_preregistered_thresholds_were_not_changed_by_the_exception():
    from importlib import util
    spec = util.spec_from_file_location("x998a", config.REPO_ROOT / "research/phase7/data_v2/x998_analysis.py")
    a = util.module_from_spec(spec)
    spec.loader.exec_module(a)
    assert a.TH["identity_excluded_share_year"] == 0.03 and a.TH["identity_bias_points"] == 1.0
    s = json.loads((config.REPO_ROOT / "research/phase7/data_v2/x998_summary.json").read_text())
    assert s["freeze_gates"]["K_identity_sanity_not_material"] is False         # the original result stands


@pytest.mark.skipif(FROZEN, reason="frozen: the pinned-manifest tests apply")
def test_candidate_manifest_is_recorded_and_not_pinned():
    m = json.loads((config.REPO_ROOT / datafreeze_v2.MANIFEST).read_text())
    assert m["status"].startswith("CANDIDATE - NOT FROZEN") and m["freeze_gates"]["all"] is False
    assert m["reference"]["table_sha256"] == json.loads(
        (config.REPO_ROOT / "research/phase7/data_v2/data_v2_reference.json").read_text())["table_sha256"]
    assert set(m["runs"]) == set(datafreeze_v2.RUNS) and all(r["lean_version"] for r in m["runs"].values())
