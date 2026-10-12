"""D229 Data v3 freeze (P14-CP2): every frozen file hashes exactly as in the manifest, the manifest is pinned, it builds
on the frozen Data v2.1 manifest, nothing after 2021-12-31 is in scope, and the gate outcome is recorded unchanged. A
failing test means frozen infrastructure changed: stop, document, ask the owner, issue a new version."""
import json

from qresearch import config, datafreeze_v21, datafreeze_v3


def test_manifest_is_pinned_and_matches_every_file():
    assert datafreeze_v3.manifest_sha() == datafreeze_v3.MANIFEST_SHA256
    m = json.loads((config.REPO_ROOT / datafreeze_v3.MANIFEST).read_text())
    assert m["version"] == "v3" and m["builds_on_data_v21_manifest_sha256"] == datafreeze_v21.MANIFEST_SHA256
    assert sorted(m["files"]) == datafreeze_v3.files()
    changed = [f for f, h in m["files"].items() if datafreeze_v3.sha(f) != h]
    assert not changed, f"frozen Data v3 changed: {changed}"
    assert datafreeze_v3.build() == m
    assert all(r["status"] == "completed" and r["lean_version"] for r in m["runs"].values())


def test_outcome_and_window():
    m = json.loads((config.REPO_ROOT / datafreeze_v3.MANIFEST).read_text())
    assert m["status"] == "FROZEN" and m["outcome"] == "DATA V3 PASS"
    assert m["usable"] == ["F1", "F2", "F4", "F5", "F7", "F8"]
    assert m["reviews"] == dict(n=131, first="2011-01-31", last="2021-11-30")
    assert m["rules"]["window"]["sealed"] == ["2022-01-01 .. 2026-08-31"]
