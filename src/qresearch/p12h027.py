"""Phase 12, H027 Exposure-Controlled Learned Stock Score (owner D213): pins of the frozen pre-registration
(research/phase12/H027_spec.md), the in-host module qr_h027, the host S029 (subclass of the pinned S028, uploaded as
qr_s028), the H026 references the real H027 run must reproduce, and the run provenance.

Written and committed BEFORE any H027 null world or result. Data v2.1 = the D207 manifest with the D213 owner exception
(qresearch.datafreeze_v21). C_WEALTH_CONDITIONAL and the null result hash are set from the 5,000 LOWVOL-conditional null
worlds and merged before the ONE real development run. tests/test_p12_h027*.py check these pins. The H026 pins
(qresearch.p11h026) are never modified.
"""
from __future__ import annotations

import hashlib

from . import config, datafreeze_v21, p11h026

DECISION = "D213"
HYPOTHESIS = "H027"
SPEC = "research/phase12/H027_spec.md"
SPEC_SHA256 = "b7f01afee22041a24b5bea58a9833427f2db5769cf52fad9f78b41f9fb5ad42f"
CODE_SHA256 = {
    "src/qresearch/lean/qr_h027.py": "c6f9103199dd07167af729211dbdd862bf402618949e49a098adf2ef9e066a26",
    "strategies/S029_h027_exposure_controlled/main.py": "c9d5844e6759245451bd6729d2a4c1ade91c454e1d365516aab842975ff693b7",
    "research/hypotheses/H027.md": "b4aa848bb99312042af5848f84c28a86f1baf1edc0910d39a254f82052f5ebb5",
}
HOST = "strategies/S029_h027_exposure_controlled/main.py"
PARENT_HOST = p11h026.HOST                              # S028, uploaded byte-identical as qr_s028.py
DATA_V21_MANIFEST_SHA256 = datafreeze_v21.MANIFEST_SHA256

CLOSED = dict(p11h026.CLOSED, H026="REJECTED — LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY (E028-05)")
PERIODS = dict(development="2011-01-01 .. 2021-12-31: FULLY SEEN development data (H026 + post-mortem); development "
                           "evidence only",
               holdout="2022-01-01 .. 2026-08-31: programme-wide final Holdout, SEALED (nothing read)")

# H026 references (E028-05 / E028-04 / pins), reproduced by the real H027 run and the equivalence gate
H026_FEATURE_PANEL_SHA256 = p11h026.FEATURE_PANEL_SHA256
H026_RESPONSE_PANEL_SHA256 = p11h026.RESPONSE_PANEL_SHA256
H026_NULL_ROWS_SHA256 = "6f409d8029ff2ea3504d3ba817dd2bef20a1b9115029fb981328cf20dd64b45c"   # E028-04 rows, seeds 1-25
H026_REAL_WEALTH = 311396.7708031718
H026_REAL_S_WEALTH = 0.17148195882657039
H026_REAL_RISK = dict(vol=0.16392095895448963, maxdd=-0.26115171280531513, beta=0.7950372028988913,
                      down_capture=0.7755116820803101)        # P11-CP2 definitions (adequacy reference values)
H026_PEAK_MEMORY_MB = dict(canary_E028_01=7872.9, null_E028_02=7964.5, null_E028_03=8224.0, real_E028_05=7933.3)

# runs
CANARY = "E029-01"
NULL_RUNS = ("E029-02", "E029-03")
NULL_BATCHES = ((1, 2500), (2501, 5000))
RERUN = "E029-04"
RERUN_SEEDS = (1, 25)
REAL = "E029-05"

# set from the null runs, merged before the real run
C_WEALTH_CONDITIONAL = 0.05770235251912147         # 50th largest S_WEALTH of 5,000 (E029-02 / E029-03)
NULL_RESULT_SHA256 = "613aa1e29a496016e56c19647af605f89d93c2630b46df96c77091dc2a0ee553"   # P12_CP1_null.json
THRESHOLD_COMMIT = None
ADEQUATE = True                                     # pre-registered adequacy audit (spec section 5) passed
NULL_RESULT = "research/phase12/cp1/P12_CP1_null.json"

RESULT = "research/phase12/cp1/P12_CP1_result.json"
CANDIDATE = None


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()
