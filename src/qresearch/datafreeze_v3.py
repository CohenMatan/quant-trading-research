"""Data v3 freeze (owner D229, P14-CP2): the targeted fundamental PIT / restatement hardening layer for H029.

Data v3 = the frozen Data v2.1 (qresearch.datafreeze_v21, unchanged; the H028 store and results untouched) + the
guard-v3 reference table qr_data_v3_NN, the v3 view / H029 signal module qr_v3 (with the frozen qr_h029a constructions
it imports) and the SEC validation reference qr_v3val_NN (audit only). Spec research/phase14/data_v3/DATA_V3_spec.md
(commit a43d706, before any build); audit run E803-01; gate outcome in research/phase14/cp2/P14_CP2_audit.json.

`research/phase14/data_v3/data_freeze_v3.json` lists every file's SHA-256, the Data v2.1 manifest it builds on, the
outcome, the per-review H029 input-panel digests (the H029 host must reproduce them exactly) and the run provenance.
MANIFEST_SHA256 pins it; tests/test_data_freeze_v3.py recomputes everything. Never change it because of an H029 / H030
result; a genuine bug: stop, document, ask the owner, issue v4.
"""
from __future__ import annotations

import hashlib
import json

from . import config, datafreeze_v21

VERSION = "v3"
MANIFEST = "research/phase14/data_v3/data_freeze_v3.json"
MANIFEST_SHA256 = "601d00623e97696bd81f5a18e4b604482eba2da67acf31b8085f2e455a2fefcb"   # D230 (P14-CP2)

RUNTIME = ("src/qresearch/lean/qr_v3.py", "src/qresearch/lean/qr_h029a.py")
RUNTIME_GLOBS = ("src/qresearch/lean/qr_data_v3_*.py", "src/qresearch/lean/qr_v3val_*.py")
OFFLINE = ("research/phase14/data_v3/DATA_V3_spec.md", "research/phase14/data_v3/build_data_v3.py",
           "src/qresearch/data_v3.py", "strategies/X803_data_v3_audit/main.py",
           "research/phase14/cp2/P14_CP2_analysis.py", "research/phase14/cp2/P14_CP2_configs.py")
EVIDENCE = ("research/phase14/data_v3/data_v3_reference.json", "research/phase14/cp2/P14_CP2_audit.json")
RUNS = ("E803-01",)

RULES = dict(
    builds_on="Data v2.1 (qresearch.datafreeze_v21 MANIFEST_SHA256, owner exception D213), every rule unchanged; the "
              "v2.1 store receives exactly the versions it always did (H028 unchanged)",
    guard_v3="restated SEC values (> 1.5% from every earlier as-known value) of quarterly revenue / gross profit / net "
             "income / operating cash flow (YTD differencing; never YTD as a quarter) and total assets, every Data v2.1 "
             "registrant and period, facts filed <= 2021-12-31; a fed version matching (0.5%) a restated value not yet "
             "public on its first-seen day and none public is excluded from the H029 v3 view only",
    v3_view="per period the latest visible fed version not v3-blocked; a period with only blocked versions is absent; "
            "current report = the latest-period visible full record (<= 200 days old)",
    signals="F1 same-quarter YoY revenue acceleration (all four revenues > 0); F2 TTM gross-margin change; F4 TTM OCF / "
            "assets change; F5 TTM ROA change; F7 -(S0/S1 - 1) from SEC cover counts, splits <= T, S0/S1 in [0.1, 10]; "
            "F8 TTM asset-turnover change (frozen qr_h029a Window / True-TTM rules); F3, F6 not computed",
    universe="U_H029 = Data v2.1 eligible universe minus SEC SIC 6000-6999 and no-SIC stocks; H029 score needs >= 5 of 6",
    window=dict(first_session="2011-01-03", last_session="2021-12-31", reviews="2011-01 .. 2021-11 (131)",
                history_only_warmup_from="2008-07-01", sealed=["2022-01-01 .. 2026-08-31"]),
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
    audit = json.loads((config.REPO_ROOT / "research/phase14/cp2/P14_CP2_audit.json").read_text())
    ref = json.loads((config.REPO_ROOT / "research/phase14/data_v3/data_v3_reference.json").read_text())
    runs = {}
    for e in RUNS:
        r = json.loads((config.REPO_ROOT / "experiments" / e / "result.json").read_text())
        pv = r["provenance"]
        runs[e] = dict(git_commit=pv["git_commit"], lean_version=pv["lean_version"], qc_backtest_id=pv["qc_backtest_id"],
                       status=r["status"], code_sha256=pv["code_sha256"], config_sha256=pv["config_sha256"])
    dig = audit["digests"]
    return dict(version=VERSION, status="FROZEN" if audit["outcome"] == "DATA V3 PASS" else "NOT FROZEN",
                outcome=audit["outcome"], usable=audit["usable"], decision="D229",
                builds_on_data_v21_manifest_sha256=datafreeze_v21.MANIFEST_SHA256,
                guard_sha256=ref["guard"]["raw_sha256"], val_sha256=ref["validation"]["raw_sha256"],
                panel_digests=dig, panel_digests_sha256=hashlib.sha256(json.dumps(dig, sort_keys=True).encode()).hexdigest(),
                reviews=dict(n=len(dig), first=min(dig), last=max(dig)), rules=RULES, runs=runs, files=fs)


def write() -> str:
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    (config.REPO_ROOT / MANIFEST).write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()


def manifest_sha() -> str:
    return sha(MANIFEST)
