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
