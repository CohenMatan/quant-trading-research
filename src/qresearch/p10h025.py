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
SPEC_SHA256 = "f250e50ebc0dcfb0c4b0a176e9ad0e5bb3e5a850fdefef65bf9413724fb04768"
CODE_SHA256 = {
    "src/qresearch/h025_form4.py": "f8a75e78f26dacaf7899b5bbac2e8a4893bc7da103e40c49b4cfdc67bc088187",
    "research/phase10/h025_ledger.py": "c62d4689068d578b06bf5122ac68d14425f63f7290827ed63152cb68b01c13a5",
    "src/qresearch/lean/qr_h025.py": "817231ca33cac481cbd7eb770bc064dd830f40a952ff8b6bfb8c2549aa68876b",
    "strategies/S027_h025_insider/main.py": "70bcf0389709a0c9a49d48a4da304d0bdd4ca5cc49e7339b4f03beeb7d9bb394",
    "research/hypotheses/H025.md": "f3b3fcb259f336247a5e446bf13d5176a87bf3b3c6d96880343022be2b72b7ce",
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
PAYLOAD_SHA256 = "92632242eca7706421560002a20b297c79fab87f2c51ba3f7569f8147c0441ee"
SEC_LEDGER_CSV_SHA256 = "b757666098122f79bcccb95b2d63b41e6cc246e9e34201f12d0f92c0f3987e7c"
SEC_FILINGS_CSV_SHA256 = "6d9cd97f10788db3be07903e7f011155bf356ab89da90ef265ee63a119e30f88"
CALENDAR_SHA256 = "53ed9ff45b7c5146205b9163c6d5322ba90ebc8f1980e838219391cdb7746958"   # LEAN sessions 2010-10-01..2017-12-29

# runs
AUDIT = ("E027-01", "E027-02")
CANARY = "E027-03"
NULL_RUNS = ("E027-04", "E027-05")                     # all 5,000 worlds, then an identical rerun
NULL_SEEDS_RANGE = (1, 5000)
REAL = "E027-06"

# set from the audit runs (after the sample check and the independent rebuild)
# E027-01 / E027-02 (no response read): identical in-host rows; 605 primary events (sample gate PASS)
IN_HOST_LEDGER_SHA256 = "7adbb0b9d010a7435bf62aa1ca85683061d54a9db448c69d4106ba9228be18fe"
EVENT_LEDGER = "research/phase10/ledger/h025_event_ledger.csv.gz"     # SHA-256 of the uncompressed CSV
EVENT_LEDGER_SHA256 = "23d3a74a24ee1ac9273db5375f99068db239c9ec4cfc212cbea0a759317864c7"
PRIMARY_EVENTS = 605

# set from the null runs, merged before the real evaluation
RESPONSE_PANEL_SHA256 = "bc4d17c83a55335f623a1d705bf616dca89cda34d182888c0d81145866bb83b7"   # E027-04 (real responses hashed only)
# E027-04 + identical rerun E027-05 (5,000 matched null worlds; real responses hashed only)
C_EVENT = 2.4667415685289664
C_EVENT_RAW = 2.4667415685289664                      # 50th largest null t (> floor 2.326)
NULL_RESULT_SHA256 = "c1d55bcd5fce59fdb57cc7530723d28fe6ee3add7e8bd9d532e185d7420c5e34"   # research/phase10/cp1/P10_CP1_null.json
THRESHOLD_COMMIT = "49b61b6ce285c5b8b8ef6844c1b1564bbacfc458"   # the commit that pinned c_EVENT


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def ledger_manifest() -> dict:
    return json.loads((config.REPO_ROOT / LEDGER_MANIFEST).read_text())
