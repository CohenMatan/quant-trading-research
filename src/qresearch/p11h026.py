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

from . import config, datafreeze_v21

DECISION = "D206"
HYPOTHESIS = "H026"
SPEC = "research/phase11/H026_spec.md"
SPEC_SHA256 = "3c29288506bacb4be8ba8379e9e831c9779d2ff0c29e2adbefe47ffe709edc89"
CODE_SHA256 = {
    "src/qresearch/lean/qr_h026.py": "3b6249d48e338510f64d8eed92461469ad252d0170bf0e88ad00af414693eab6",
    "strategies/S028_h026_learned_score/main.py": "c49902d9acf960d00ab4c87303f8b7a49f6cb56c7d847fd14cac145bc3db77ed",
    "strategies/X801_data_v21_export/main.py": "dc75e9fd7e1d9c4da6ca07b0588e67964f33013421c9a1f4416e7104278f54f1",
    "research/phase11/data_v21/build_data_v21.py": "5499488e97ce1662eb5d545108724afbe884d90f158a9db466375736cc94b214",
    "src/qresearch/lean/qr_h024.py": "f9b1c87e25ea3b98bda58496fab8eee55b47661116c622de5827362ba865465c",
    "src/qresearch/lean/qr_p7_pred.py": "bc6fd8e83e7c105e50bbd05fabb23c61ac5229216af6599320962195d83f8da5",
    "research/hypotheses/H026.md": "0ceea9d278c6f7f5170f5681a7687b43afd51bc1f2ddf61931bdbf6bb9e4a112",
}
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
DATA_V21_MANIFEST_SHA256 = datafreeze_v21.MANIFEST_SHA256          # D207

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
