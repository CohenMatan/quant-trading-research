"""D114 data-infrastructure freeze for H016 (owner 2026-10-02 item 8): every frozen file must hash exactly as in the
manifest, and the manifest itself is pinned. A failing test means frozen infrastructure changed: stop, document,
obtain owner approval and issue a new freeze version before re-running anything affected."""
import json

from qresearch import config, datafreeze


def test_manifest_is_pinned():
    assert datafreeze.manifest_sha() == datafreeze.MANIFEST_SHA256


def test_every_frozen_file_matches_the_manifest():
    m = json.loads((config.REPO_ROOT / datafreeze.MANIFEST).read_text())
    assert m["version"] == datafreeze.VERSION
    assert sorted(m["files"]) == datafreeze.files()          # no frozen file added, removed or renamed
    changed = [f for f, h in m["files"].items() if datafreeze.sha(f) != h]
    assert not changed, f"frozen data infrastructure changed: {changed}"
    assert datafreeze.build()["combined_sha256"] == m["combined_sha256"]


def test_freeze_covers_the_owner_listed_components():
    fs = datafreeze.files()
    for must in ("src/qresearch/lean/qr_harness.py",          # universe rules, Visa correction, warm-up, timing
                 "src/qresearch/lean/qr_fundamentals.py",     # +90 fallback, 200-day freshness, quarantine and
                                                              # field-level release, restatement blocks, True TTM,
                                                              # whitelist/blacklist
                 "src/qresearch/lean/qr_industry.py",         # financial/REIT classification
                 "src/qresearch/lean/qr_sec_corrections.py",  # survivorship repair layer
                 "research/phase2/sec/identity_v2.py",        # identity matching and priority rules
                 "research/phase2/sec/corrections_v2.json",   # identity mappings / correction table (audit copy)
                 "research/phase2/sec/field_releases.json"):
        assert must in fs
    assert any(f.startswith("src/qresearch/lean/qr_sec_data") for f in fs)
