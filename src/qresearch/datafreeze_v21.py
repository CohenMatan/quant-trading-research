"""Data Infrastructure v2.1 freeze (owner D206, P11-CP1).

Data v2.1 = the frozen Data v2 (qresearch.datafreeze_v2, unchanged) extended through 2021-12-31: the same builder with
one parameter (cut-off 2021-12-31; research/phase11/data_v21/build_data_v21.py), the packed table qr_data_v21*.py, and
host X801 = X998 with five line-level changes (tests/test_p11_data_v21.py). Nothing after 2021-12-31 is read.

`research/phase11/data_v21/data_freeze_v21.json` lists every file's SHA-256, the Data v2 manifest it extends, the
reference component hashes, the audit gates (x801_summary.json) and the run provenance (E801-01..04). MANIFEST_SHA256
pins it; tests/test_data_freeze_v21.py recomputes everything. Never change it because of an H026 result; a genuine bug:
stop, document, ask the owner, issue a new version.
"""
from __future__ import annotations

import hashlib
import json

from . import config, datafreeze_v2

VERSION = "v2.1"
MANIFEST = "research/phase11/data_v21/data_freeze_v21.json"
MANIFEST_SHA256 = None

RUNTIME = ("strategies/X801_data_v21_export/main.py",)
RUNTIME_GLOBS = ("src/qresearch/lean/qr_data_v21*.py",)
OFFLINE = ("research/phase11/data_v21/build_data_v21.py", "research/phase11/data_v21/x801_analysis.py",
           "research/phase11/data_v21/configs_x801.py")
EVIDENCE = ("research/phase11/data_v21/data_v21_reference.json", "research/phase11/data_v21/x801_summary.json")
RUNS = ("E801-01", "E801-02", "E801-03", "E801-04")

RULES = dict(
    extends="Data v2 (qresearch.datafreeze_v2 MANIFEST_SHA256), every rule unchanged (universe, SEC market-cap repair, "
            "M2 timing, identity, restatement guard, share class, corporate actions, life rule, review calendar, "
            "price / ADV filters, Score v1 disqualifiers)",
    change="cut-off 2017-12-31 -> 2021-12-31 for the SEC reference (filings, cover-page share counts, identity, "
           "restatement-guard re-reports, SIC history); the guard therefore also sees 2018-2021 re-reports of earlier "
           "periods (later public knowledge applied only from its own public date + 1 day)",
    window=dict(first_session="2011-01-03", last_session="2021-12-31",
                reviews="last session of each month 2011-01 .. 2021-11 reached by a run ending 2021-12-31 (131)",
                history_only_warmup_from="2008-07-01", sealed=["2022-01-01 .. 2026-08-31"]),
    sec_snapshot="cached SEC JSON snapshots contain later filings; every row is filtered to dates <= 2021-12-31 "
                 "before use (build_data_v21.py)",
    build_policy="default_build_digest_verified: record the actual LEAN build of every run; digests must reproduce",
    compliance="aggregates and SHA-256 digests only; no vendor value, no return exported")


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
    ref = json.loads((config.REPO_ROOT / "research/phase11/data_v21/data_v21_reference.json").read_text())
    summ = json.loads((config.REPO_ROOT / "research/phase11/data_v21/x801_summary.json").read_text())
    runs = {}
    for e in RUNS:
        r = json.loads((config.REPO_ROOT / "experiments" / e / "result.json").read_text())
        pv = r["provenance"]
        runs[e] = dict(git_commit=pv["git_commit"], lean_version=pv["lean_version"], qc_backtest_id=pv["qc_backtest_id"],
                       status=r["status"], code_sha256=pv["code_sha256"], config_sha256=pv["config_sha256"])
    status = "FROZEN" if summ.get("all_pass") else "NOT FROZEN (failed: " + ", ".join(
        sorted(k for k, v in summ["gates"].items() if not v)) + ")"
    return {"version": VERSION, "status": status, "extends_data_v2_manifest_sha256": datafreeze_v2.MANIFEST_SHA256,
            "files": fs, "combined_sha256": combined, "rules": RULES,
            "reference": {k: ref[k] for k in sorted(ref) if k != "file_sha256"},
            "runs": runs, "gates": summ["gates"], "thresholds": summ["thresholds"],
            "review_calendar_sha256": summ.get("review_calendar_sha256")}


def write() -> str:
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    (config.REPO_ROOT / MANIFEST).write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()


def manifest_sha() -> str:
    return hashlib.sha256((config.REPO_ROOT / MANIFEST).read_bytes()).hexdigest()
