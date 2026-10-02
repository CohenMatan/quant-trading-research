"""Frozen fundamental-data infrastructure for H016 (D114, owner 2026-10-02 item 8).

The exact files that define the data H016 may see — universe and Visa correction (harness), PIT timing (+90 fallback,
200-day freshness), quarantine and field-level releases, restatement blocks, SEC timing holds, the SEC survivorship
repair (identity mappings, priority tiers, correction table), True TTM, the field whitelist/blacklist, the historical
financial/REIT classification and the history-only warm-up — plus the offline rules and evidence that produced them.

`research/phase2/data_freeze_v1.json` lists every file's SHA-256; MANIFEST_SHA256 pins the manifest itself and
tests/test_data_freeze.py recomputes both. Once H016 research begins, nothing here may change because of its results.
A genuine bug: stop, document, ask the owner, then issue a NEW freeze version before re-running anything affected.
"""
from __future__ import annotations

import hashlib
import json

from . import config

VERSION = "v1"
MANIFEST = "research/phase2/data_freeze_v1.json"
MANIFEST_SHA256 = "17fffa03f0c2320a99a338071fd79d2d7b1771fd0fa28605720149aa545fff3e"

RUNTIME = ("src/qresearch/lean/qr_harness.py", "src/qresearch/lean/qr_indicators.py",
           "src/qresearch/lean/qr_fundamentals.py", "src/qresearch/lean/qr_industry.py",
           "src/qresearch/lean/qr_sec_corrections.py")
RUNTIME_GLOBS = ("src/qresearch/lean/qr_sec_data*.py",)
OFFLINE = ("src/qresearch/sec_pit.py", "src/qresearch/sec_pack.py", "src/qresearch/sec_edgar.py",
           "research/phase2/sec/rss_index.py", "research/phase2/sec/identity_v2.py", "research/phase2/sec/sic_history.py",
           "research/phase2/sec/build_table_v2.py", "research/phase2/sec/build_corrections.py",
           "research/phase2/sec/x979_analyse.py", "research/phase2/sec/x971_analyse.py")
EVIDENCE = ("research/phase2/sec/corrections.json", "research/phase2/sec/corrections_v2.json",
            "research/phase2/sec/identity_v2.json", "research/phase2/sec/timing_holds.json",
            "research/phase2/sec/quarantine_release.json", "research/phase2/sec/restatement_blocks.json",
            "research/phase2/sec/field_releases.json", "research/phase2/sec/x975_results.json")


def files() -> list[str]:
    root = config.REPO_ROOT
    out = list(RUNTIME) + list(OFFLINE) + list(EVIDENCE)
    for g in RUNTIME_GLOBS:
        out += sorted(str(p.relative_to(root)) for p in root.glob(g))
    return sorted(out)


def sha(path: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / path).read_bytes()).hexdigest()


def build() -> dict:
    fs = {f: sha(f) for f in files()}
    combined = hashlib.sha256("".join(f"{k}:{v}\n" for k, v in sorted(fs.items())).encode()).hexdigest()
    return {"version": VERSION, "files": fs, "combined_sha256": combined}


def write() -> str:
    m = build()
    text = json.dumps(m, indent=1, sort_keys=True) + "\n"
    (config.REPO_ROOT / MANIFEST).write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()


def manifest_sha() -> str:
    return hashlib.sha256((config.REPO_ROOT / MANIFEST).read_bytes()).hexdigest()
