"""Phase 10, H025 Insider Cluster Buying (owner D204): pins of the frozen pre-registration (research/phase10/H025_spec.md),
the SEC Form 4 parser / ledger builder, the in-host module qr_h025, the host S027 and the run provenance.

Written and committed BEFORE any H025 QuantConnect run, event eligibility state, null world or return. The SEC ledger
payload is pinned when the ledger is built (offline, SEC facts only); IN_HOST_LEDGER_SHA256 and EVENT_LEDGER_SHA256
are set from the no-return audit runs (E027-01 / E027-02) after the sample check and the independent rebuild;
RESPONSE_PANEL_SHA256, C_EVENT and the null result hash are set from the 5,000 matched null worlds and merged before
the ONE real development evaluation. tests/test_p10_h025*.py check these pins. Data v2 (qresearch.datafreeze_v2) and
the H022 response conventions (qresearch.p7pred_v2) are unchanged.
"""
from __future__ import annotations

import hashlib
import json

from . import config, p7pred_v2

DECISION = "D204"
HYPOTHESIS = "H025"
SPEC = "research/phase10/H025_spec.md"
SPEC_SHA256 = None
CODE_SHA256 = {
    "src/qresearch/h025_form4.py": None,
    "research/phase10/h025_ledger.py": None,
    "src/qresearch/lean/qr_h025.py": None,
    "strategies/S027_h025_insider/main.py": None,
    "research/hypotheses/H025.md": None,
}
DATA_FREEZE_MANIFEST_SHA256 = p7pred_v2.DATA_FREEZE_MANIFEST_SHA256
PRED_CODE_SHA256 = p7pred_v2.PRED_CODE_SHA256           # qr_p7_pred (response conventions; S024 parameter)
PARENT_HOST = p7pred_v2.HOST                            # S024, uploaded byte-identical as qr_s024.py
HOST = "strategies/S027_h025_insider/main.py"

# permanent records (owner D204)
CLOSED = dict(H022="REJECTED (E024-07)", H023="NO ROBUST SCORE V2 CANDIDATE (E025-08)",
              H024="NO ROBUST H024 FEATURE MODEL (E026-08)")
PERIODS = dict(development="2011-2017: H025 DEVELOPMENT / TRAINING",
               validation="2018-01-01 .. 2021-12-31: H025-SPECIFIC OOS VALIDATION, NOT PROGRAMME-WIDE PRISTINE "
                          "HOLDOUT (earlier unrelated hypotheses used parts of it); not accessed",
               holdout="2022-01-01 .. 2026-08-31: programme Holdout, untouched")
RULES = dict(form="4", code="P", acquired="A", ownership="D", roles=("Director", "Officer"),
             min_insider_usd=25_000.0, min_cluster_usd=100_000.0, min_insiders=2, window_calendar_days=10,
             cooldown_sessions=20, hold_sessions=20, nw_lag=2, null_worlds=5000, alpha=0.01, c_floor=2.326,
             g2_min=0.02, min_events=100, min_year_events=10, min_years=5)

# SEC ledger (offline build; research/phase10/ledger/h025_sec_ledger.json)
LEDGER_MANIFEST = "research/phase10/ledger/h025_sec_ledger.json"
PAYLOAD_SHA256 = None
CALENDAR_SHA256 = "53ed9ff45b7c5146205b9163c6d5322ba90ebc8f1980e838219391cdb7746958"   # LEAN sessions 2010-10-01..2017-12-29

# runs
AUDIT = ("E027-01", "E027-02")
CANARY = "E027-03"
NULL_RUNS = ("E027-04", "E027-05")                     # all 5,000 worlds, then an identical rerun
NULL_SEEDS_RANGE = (1, 5000)
REAL = "E027-06"

# set from the audit runs (after the sample check and the independent rebuild)
IN_HOST_LEDGER_SHA256 = None
EVENT_LEDGER = "research/phase10/ledger/h025_event_ledger.csv"
EVENT_LEDGER_SHA256 = None

# set from the null runs, merged before the real evaluation
RESPONSE_PANEL_SHA256 = None
C_EVENT = None
C_EVENT_RAW = None
NULL_RESULT_SHA256 = None
THRESHOLD_COMMIT = None


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def ledger_manifest() -> dict:
    return json.loads((config.REPO_ROOT / LEDGER_MANIFEST).read_text())
