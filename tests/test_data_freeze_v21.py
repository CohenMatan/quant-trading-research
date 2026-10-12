"""D206 Data Infrastructure v2.1 freeze (P11-CP1): every frozen file hashes exactly as in the manifest, the manifest is
pinned, it extends the frozen Data v2 manifest, and the pre-set audit thresholds and gate results are recorded unchanged.
A failing test means frozen infrastructure changed: stop, document, ask the owner, issue a new version."""
import json

import pytest

from qresearch import config, datafreeze_v2, datafreeze_v21

FROZEN = datafreeze_v21.MANIFEST_SHA256 is not None


def test_rules_extend_data_v2_without_2022_data():
    r = datafreeze_v21.RULES
    assert r["window"]["last_session"] == "2021-12-31" and r["window"]["sealed"] == ["2022-01-01 .. 2026-08-31"]
    assert "(131)" in r["window"]["reviews"]
    assert "every rule unchanged" in r["extends"]


@pytest.mark.skipif(not FROZEN, reason="Data v2.1 not frozen yet")
def test_manifest_is_pinned_and_matches_every_file():
    assert datafreeze_v21.manifest_sha() == datafreeze_v21.MANIFEST_SHA256
    m = json.loads((config.REPO_ROOT / datafreeze_v21.MANIFEST).read_text())
    assert m["version"] == "v2.1" and m["extends_data_v2_manifest_sha256"] == datafreeze_v2.MANIFEST_SHA256
    assert sorted(m["files"]) == datafreeze_v21.files()
    changed = [f for f, h in m["files"].items() if datafreeze_v21.sha(f) != h]
    assert not changed, f"frozen Data v2.1 infrastructure changed: {changed}"
    assert datafreeze_v21.build() == m
    assert set(m["runs"]) == set(datafreeze_v21.RUNS)
    assert all(r["status"] == "completed" and r["lean_version"] for r in m["runs"].values())


@pytest.mark.skipif(not FROZEN, reason="Data v2.1 not frozen yet")
def test_preregistered_audit_thresholds_unchanged():
    from importlib import util
    spec = util.spec_from_file_location("x801a", config.REPO_ROOT / "research/phase11/data_v21/x801_analysis.py")
    a = util.module_from_spec(spec)
    spec.loader.exec_module(a)
    assert a.TH == dict(repro_eligibility_share=0.99, new_year_mapping_min=0.90, new_year_scored_ratio_min=0.50)


@pytest.mark.skipif(not FROZEN, reason="Data v2.1 not frozen yet")
def test_only_the_specification_error_gate_failed_and_it_stays_failed():
    m = json.loads((config.REPO_ROOT / datafreeze_v21.MANIFEST).read_text())
    assert m["status"] == datafreeze_v21.FROZEN_STATUS
    assert sorted(k for k, v in m["gates"].items() if not v) == ["NEW_YEARS_MAPPING"]      # recorded, never relabelled
    c = m["mapping_specification_correction"]
    assert c["decision"] == "D207" and c["frozen_years_identical"] is True
    assert all(c["e801_01"][y]["with_sec_identity"] >= 0.90 for y in ("2018", "2019", "2020", "2021"))
    h = m["h022_population_2011_2017"]
    assert h["decisions"] == 83 and h["frozen_stock_months"] == 34863 and abs(h["relative_change"]) < 0.001
    assert m["reviews"] == dict(n=131, first="2011-01-31", last="2021-11-30")


def test_owner_exception_d213_recorded_without_rewriting_the_manifest():
    rec = json.loads((config.REPO_ROOT / datafreeze_v21.OWNER_EXCEPTION_RECORD).read_text())
    assert rec["decision"] == "D213" and rec["resolution"] == "OWNER-APPROVED EXCEPTION"
    assert rec["record_unchanged"] == "NEW_YEARS_MAPPING failed AS WRITTEN."
    assert rec["manifest_sha256"] == datafreeze_v21.MANIFEST_SHA256 == datafreeze_v21.manifest_sha()
    assert rec["manifest_changed"] is False and rec["data_v21_rebuilt"] is False
    m = json.loads((config.REPO_ROOT / datafreeze_v21.MANIFEST).read_text())
    assert m["gates"]["NEW_YEARS_MAPPING"] is False                      # the original result stands
