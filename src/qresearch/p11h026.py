"""Phase 11, H026 Learned Stock Score Portfolio (owner D206): pins of the frozen pre-registration
(research/phase11/H026_spec.md), the Data v2.1 extension (builder, host X801, frozen manifest), the in-host module
qr_h026 (features -> 63-session target -> weighted Ridge -> nested walk-forward -> Top-15 portfolio -> null), the host
S028 and the run provenance.

Written and committed BEFORE any H026 model fit, null world or portfolio result. DATA_V21_MANIFEST_SHA256 is set when
the Data v2.1 integrity gate passes (X801 runs E801-01..04); FEATURE_PANEL_SHA256 from the canary; RESPONSE_PANEL_SHA256,
C_WEALTH and the null result hash from the 5,000 null worlds, merged before the ONE real development run.
tests/test_p11_h026*.py check these pins.
"""
from __future__ import annotations

import hashlib

from . import config

DECISION = "D206"
HYPOTHESIS = "H026"
SPEC = "research/phase11/H026_spec.md"
SPEC_SHA256 = None
CODE_SHA256 = {}
HOST = "strategies/S028_h026_learned_score/main.py"
DATA_HOST = "strategies/X801_data_v21_export/main.py"

# permanent records (owner D206)
CLOSED = dict(H022="REJECTED (E024-07)", H023="NO ROBUST SCORE V2 CANDIDATE (E025-08)",
              H024="NO ROBUST H024 FEATURE MODEL (E026-08)", H025="REJECTED — NO ROBUST INSIDER-CLUSTER EDGE (E027-06)")
PERIODS = dict(development="2011-01-01 .. 2021-12-31: H026 DEVELOPMENT / MODEL-SELECTION DATA (2018-2021 is NOT "
                           "untouched validation for H026)",
               holdout="2022-01-01 .. 2026-08-31: programme-wide final Holdout, SEALED (nothing read)")

# Data v2.1 (X801 audit runs; manifest frozen when the integrity gate passes)
DATA_RUNS = ("E801-01", "E801-02", "E801-03", "E801-04")
DATA_V21_MANIFEST = "research/phase11/data_v21/data_freeze_v21.json"
DATA_V21_MANIFEST_SHA256 = None

# runs
CANARY = "E028-01"
NULL_RUNS = ("E028-02", "E028-03")                     # seeds 1..2500, 2501..5000
NULL_BATCHES = ((1, 2500), (2501, 5000))
RERUN = "E028-04"                                      # seeds 1..25 rerun independently (determinism)
RERUN_SEEDS = (1, 25)
REAL = "E028-05"

# set from the canary / null runs, merged before the real run
FEATURE_PANEL_SHA256 = None
RESPONSE_PANEL_SHA256 = None
C_WEALTH = None
NULL_RESULT_SHA256 = None
THRESHOLD_COMMIT = None

RESULT = "research/phase11/cp1/P11_CP1_result.json"
CANDIDATE = None


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()
