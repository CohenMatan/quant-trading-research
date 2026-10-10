"""Data Infrastructure v2 freeze (owner D190, P7-CP5f).

The exact files and rules that define the data Score v1 / H022 may see on QuantConnect's current default build: the
consolidated reference table (qr_data_v2*.py; data-v1 SEC correction layer, M2 filing reference and D111 cover-share
counts, verified identity extension, restatement-guard reference), the pure v2 layer (qr_v2.py), the packing format
(v2pack), the export / verification host X998, the offline builders and evidence, plus the unchanged Score v1 code
(pinned separately in qresearch.p7score / p7pred) and the data-v1 runtime modules it imports.

`research/phase7/data_v2/data_freeze_v2.json` lists every file's SHA-256, the frozen rules, the reference component
hashes and the verification-run provenance (E998-01..04); MANIFEST_SHA256 pins the manifest itself and
tests/test_data_freeze_v2.py recomputes everything. Nothing here may change because of any H022 result. A genuine bug:
stop, document, ask the owner, then issue a NEW freeze version (v3) before re-running anything affected.
"""
from __future__ import annotations

import hashlib
import json

from . import config

VERSION = "v2"
MANIFEST = "research/phase7/data_v2/data_freeze_v2.json"
MANIFEST_SHA256 = "cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb"   # D192: pinned (P7-CP5g)
# P7-CP5f (D191): gate K failed (identity sanity check, pre-set 3%-a-year exclusion limit), so the manifest was written as
# an unpinned CANDIDATE (SHA-256 d09f20fc..., commit 0837ce6).
# P7-CP5g (D192): the owner accepted the identity residual as an explicit exception to gate K and froze Data v2 exactly as
# built. The original gate results (x998_summary.json, freeze_gates) are kept unchanged: gate K stays FAILED; the
# exception is recorded beside it. No input, rule or threshold changed and nothing was rerun.
CANDIDATE_MANIFEST_SHA256 = "d09f20fcca4290faf664bc07511cce048f4458884c84871c53703d3cf27faddb"
FROZEN_STATUS = "FROZEN — OWNER-APPROVED GATE K EXCEPTION"
GATE_K_EXCEPTION = dict(
    decision="D192",
    gate_k="FAILED under the original pre-registered 3%-per-year identity-incidence criterion.",
    resolution="OWNER-APPROVED EXCEPTION",
    criterion_incidence="affected share of eligible stock-months <= 3% every year (unchanged)",
    observed_incidence="3.41% (2011), 3.74%, 4.24%, 5.10%, 5.65%, 5.98%, 6.93% (2017): failed every year",
    criterion_tilt="implied survivorship tilt on the fully scored population <= 1.0 point (unchanged)",
    observed_tilt="+0.47 points: passed",
    residual=dict(affected_securities=161, identity_reject=105, no_identity_row=56, affected_eligible_stock_months=4656,
                  affected_survival=0.8243, retained_fully_scored_survival=0.8748),
    reason="Although the incidence criterion failed, the measured survivorship impact is +0.47 percentage points, below "
           "the pre-registered 1.0-point survivorship limit and smaller than the already accepted +0.79-point overall "
           "Data v2 universe residual. This is an owner judgement made before any H022 real return, real IC, null "
           "threshold, or real gate result has been observed.",
    record="Data v2 did not technically pass every original freeze criterion. Gate K failed because the "
           "identity-affected population exceeded the pre-registered 3%-per-year incidence threshold. The owner "
           "knowingly accepts this residual without changing the threshold because the measured survivorship effect "
           "is only +0.47 percentage points, below the 1.0-point materiality bound, every PIT/integrity gate passed, "
           "and no real H022 result has yet been observed.")

RUNTIME = ("src/qresearch/lean/qr_v2.py", "src/qresearch/lean/qr_harness.py", "src/qresearch/lean/qr_indicators.py",
           "src/qresearch/lean/qr_fundamentals.py", "src/qresearch/lean/qr_industry.py",
           "src/qresearch/lean/qr_sec_corrections.py", "src/qresearch/lean/qr_p7.py",
           "src/qresearch/lean/qr_p7_score.py", "src/qresearch/lean/qr_p7_export.py", "src/qresearch/lean/qr_p7_mech.py",
           "src/qresearch/lean/qr_p7_pred.py", "src/qresearch/lean/qr_xs.py", "src/qresearch/lean/qr_xs_panel.py",
           "src/qresearch/lean/qr_xs_diag.py", "strategies/X998_data_v2_export/main.py")
RUNTIME_GLOBS = ("src/qresearch/lean/qr_data_v2*.py",)
OFFLINE = ("src/qresearch/v2pack.py", "research/phase7/data_v2/build_data_v2.py",
           "research/phase7/data_v2/x998_analysis.py", "research/phase7/cp5e/identity_extension.py",
           "research/phase7/cp5e/target_population.py", "research/phase7/cp5e/build_x997_ref.py",
           "src/qresearch/sec_pit.py", "src/qresearch/sec_edgar.py")
EVIDENCE = ("research/phase7/data_v2/data_v2_reference.json", "research/phase7/data_v2/x998_summary.json",
            "research/phase7/cp5e/identity_extension.json", "research/phase7/cp5e/target_population.json",
            "research/phase7/P7_score_spec.md", "research/phase7/P7_predictive_spec.md")
RUNS = ("E998-01", "E998-02", "E998-03", "E998-04")

# The frozen Data v2 rules (D190; P7-CP5e section 50). Changing any of them is a new freeze version.
RULES = dict(
    window=dict(first_session="2011-01-03", last_session="2017-12-29", decisions=["2011-01-31", "2017-11-30", 83],
                reviews="last session of each month 2011-01 .. 2017-12 (84)", weekly_checks="last session of each ISO week",
                history_only_warmup_from="2008-07-01", sealed=["2018-01-01 .. 2021-12-31", "2022-01-01 .. 2026-08-31"]),
    calendar="QuantConnect US equity session calendar; selection stamped the calendar day after the session (P7-CP1)",
    universe=dict(min_market_cap=2e9, rule="QuantConnect market_cap if > 0, else valid SEC market cap, else ineligible",
                  sec_market_cap="single unambiguous cover-page share count x raw close of the review session; usable "
                                 "from filing + 1 day; cover date at most 135 days old; no interpolation; no weighted "
                                 "shares; multi-class unresolved; D111 split logic (splits with ex-date <= review day)",
                  sec_share_max_age_days=135, v1_sec_correction_layer="unchanged, not broadened (495 securities)",
                  filters="common stock, primary listing, not financial / REIT by SEC SIC at filing; one class per "
                          "company; security-life rule qr_p7.LIFE_GAP; corporate-event exclusions (P7-CP1)"),
    identity=dict(rule="dated SEC identity v2 rows; verified extension rows (SAFE / BOUNDED only) used only while the "
                       "security's feed presence is continuous since the row start (gap <= 60 days)",
                  excluded="REJECT (105) and no-identity-row (56) securities have no SEC identity: eligible by market "
                           "cap, never fed fundamentals (H2)"),
    timing_m2="usable = max(first seen in QuantConnect's stream, SEC original periodic filing + 1 day); pre-XBRL "
              "filing dates from EDGAR submissions; no FileDate; no +90-day rule",
    first_seen_ledger="weekly revision scan; a report is fed once per (security, period end, usable day)",
    restatement_guard="quarterly revenue and total assets: a report whose value equals a later SEC re-report (> 0.5% "
                      "from the first-filed value) and not the first-filed value is blocked until that later filing "
                      "is public + 1 day (P7-CP5d methodology)",
    freshness=dict(max_record_age_days=200, ttm="True TTM (four quarters, P2-CP7)"),
    score="Score v1 exactly as pinned (qresearch.p7score SPEC_SHA256 / CODE_SHA256); H1-H7 unchanged",
    mechanics=dict(entry=80, exit=70, buffer=5, K=10, initial_cap=0.10, regime_positions=dict(STRONG=10, NORMAL=8,
                   WEAK=5, RISK_OFF=2), sector_max_ff12=3, grown_winner_cap=0.20, ranking="total, Fundamental, "
                   "Technical, ADV20, id", weekly="hard-DQ sell-only", cash_allowed=True,
                   execution="monthly review at the last session's close, orders at the next open"),
    costs=dict(commission_per_order=7.0, slippage_bps_per_side=10, capital=[100000, 200000]),
    build_policy="default_build_digest_verified: record the actual LEAN build of every run; digests must reproduce",
    compliance="aggregates and SHA-256 digests only; no vendor value, no return exported",
    old_c_ic="2.390976216956 = DATA_V1_ONLY / UNUSED_ON_V2 (qresearch.p7pred.C_IC_STATUS)")


def files() -> list[str]:
    root = config.REPO_ROOT
    out = list(RUNTIME) + list(OFFLINE) + list(EVIDENCE)
    for g in RUNTIME_GLOBS:
        out += sorted(str(p.relative_to(root)) for p in root.glob(g))
    return sorted(out)


def sha(path: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / path).read_bytes()).hexdigest()


def runs() -> dict:
    out = {}
    for e in RUNS:
        r = json.loads((config.REPO_ROOT / "experiments" / e / "result.json").read_text())
        pv = r["provenance"]
        out[e] = dict(git_commit=pv["git_commit"], lean_version=pv["lean_version"], qc_backtest_id=pv["qc_backtest_id"],
                      status=r["status"], code_sha256=pv["code_sha256"], config_sha256=pv["config_sha256"])
    return out


def build() -> dict:
    from . import p7pred, p7score
    fs = {f: sha(f) for f in files()}
    combined = hashlib.sha256("".join(f"{k}:{v}\n" for k, v in sorted(fs.items())).encode()).hexdigest()
    ref = json.loads((config.REPO_ROOT / "research/phase7/data_v2/data_v2_reference.json").read_text())
    comp = ref["components"]
    summ = json.loads((config.REPO_ROOT / "research/phase7/data_v2/x998_summary.json").read_text())
    gates = summ.get("freeze_gates") or {}
    failed = sorted(k for k, v in gates.items() if v is False and k != "all")
    if GATE_K_EXCEPTION is not None and all(k.startswith("K_") for k in failed):
        status = FROZEN_STATUS                  # D192: only gate K failed, and the owner accepted it as an exception
    else:
        status = "CANDIDATE - NOT FROZEN (failed: " + ", ".join(failed) + ")"
    return {"version": VERSION, "status": status, "gate_k_exception": GATE_K_EXCEPTION,
            "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA256, "files": fs, "combined_sha256": combined, "rules": RULES,
            "score_v1": dict(spec_sha256=p7score.SPEC_SHA256, code_sha256=p7score.CODE_SHA256,
                             predictive_spec_sha256=p7pred.SPEC_SHA256),
            "reference": dict(table_sha256=ref["table_sha256"], loader_version=ref["loader_version"],
                              packing=ref["packing"], project_files=ref["project_files_of_table"], chars=ref["chars"],
                              sec_v1_layer_sha256=comp["sec_v1"]["sha256"], sec_filings_and_shares_sha256=comp["f"]["sha256"],
                              identity_extension_sha256=comp["ext"]["sha256"], restatement_guard_sha256=comp["guard"]["sha256"],
                              identity_values_sha256=comp["idv"]["sha256"], diagnostics_sha256=comp["diag"]["sha256"],
                              sec_snapshot=ref["sources"], counts=ref["counts"]),
            "runs": runs(), "verification_digests": summ["E998-01"].get("digests_sha256") if isinstance(summ.get("E998-01"), dict) else None,
            "freeze_gates": summ.get("freeze_gates")}


def write() -> str:
    m = build()
    text = json.dumps(m, indent=1, sort_keys=True) + "\n"
    (config.REPO_ROOT / MANIFEST).write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()


def manifest_sha() -> str:
    return hashlib.sha256((config.REPO_ROOT / MANIFEST).read_bytes()).hexdigest()
