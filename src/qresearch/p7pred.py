"""Phase 7 predictive test H022: pins of the frozen score / mechanics / predictive-test specification
(research/phase7/P7_predictive_spec.md v1, P7-CP4, owner D175) and of every module, study and test it names.

FROZEN v1 (2026-10-06), written before any real future return, IC or score-band return was computed.
tests/test_p7_pred_spec.py checks the hashes and that the code carries exactly these constants. Any change before the
real evaluation = STOP, owner decision, new version; nothing may change after any real future return is computed.
"""
from __future__ import annotations

import hashlib

from . import config

SPEC = "research/phase7/P7_predictive_spec.md"
SPEC_VERSION = 1
SPEC_SHA256 = "2c99f9623065a0d9576f35ea208733c47ce5ec3bbfe2f587ab2a9451b0061f58"
SPEC_SHA256_V1_ORIGINAL = "389f9364541588f78f504843bdce32067dc3004a26a64eab5c91331b5ffc2bd9"   # before the D177 wording-only fix (C3)
HYPOTHESIS = "H022"
CODE_SHA256 = {
    "src/qresearch/lean/qr_p7_score.py": "84b67317023683da5d6f35c640e6b8adcaf42a9b9e106c0ab8183a26edb91572",
    "src/qresearch/lean/qr_p7.py": "86abb2b2e9284f1dfaa89bddb6a57d354d399b3069822be8b8efb80dcb04bb5a",
    "src/qresearch/lean/qr_p7_export.py": "40e1410ef00a7e1cc610dc823561efe81530264e199c535022cda13c4eef203c",
    "src/qresearch/lean/qr_p7_mech.py": "838ffce8d9ab5fd37eb9392d4395153b7da46aaa3ce982ec66fae8cafa9bc726",
    "src/qresearch/lean/qr_p7_pred.py": "bc6fd8e83e7c105e50bbd05fabb23c61ac5229216af6599320962195d83f8da5",
    "src/qresearch/lean/qr_h020_stats.py": "426d37218f8a27707a2b18e8e99559555d03a1e36ff0ddb499d92df4a676b049",
    "src/qresearch/lean/qr_xs.py": "bd69bc6ae5e0598eebdb75114cfc0b740469cc545a2a25952174f56cd98b4358",
    "src/qresearch/lean/qr_xs_panel.py": "4dd5f6df09d9cad383065aca0f6a0350ed85ca40bfb081102b769d77a3c539b0",
    "src/qresearch/lean/qr_fundamentals.py": "0774343f24820ce4d847e27299107f2218f1a536184fb6d51db6e8f8c6106907",
    "strategies/X993_p7_score_mechanics_export/main.py": "912d841f1d1df36f86c3f5fae7498565dcb54266e3147e8c585958255e3fbe9e",
    "research/phase7/P7_power.py": "17952573cbad5874b3d6e8a5cd7c2e4fd64d8a53ca7ece11489eb053c8aeea3b",
    "research/phase7/P7_power.json": "f45d5145322f314b711c3a58ddb2e87ea89d5651ed47e0628b32c2dd4bac4c40",
    "tests/test_p7_pred.py": "e1c070bcc08897e13460be441653c98fdddaa01f9646c48d0eb822560ac6be0c",
    "tests/test_p7_cp3r.py": "912861b07ea2fb525b5fb54c9cc269078d9d740f48840218d205b0fc2aa0727c",
    "research/phase7/P7_CP5_result_template.md": "ffd3ffeb8c233bca982a066e210be88d7593198ccaf1866b6dc829c572198cf9",
    "research/hypotheses/H022.md": "54683a81ae334cc5babf584b6cde46e8b2200aa34944e910f5b3bb3a67b7158a",
}
SCORE_PINS = "qresearch.p7score"                      # Score v1 (unchanged since P7-CP2)
CONSTANTS = dict(HORIZON_MONTHS=1, DIAG_HORIZONS=(2, 3), NW_LAG=2, ANN=12.0, ENTRY=80, ECON_MIN=0.03, MONO_MIN=0.90,
                 N_Q=5, BLOCKS=((2011, 2012), (2013, 2014), (2015, 2016), (2017, 2017)), BLOCK_MAX_SHARE=0.5,
                 ALPHA=0.01, CRIT_FLOOR=2.326, R_NULL=5000, MIN_STOCKS=20, SECTOR_MIN=5)
MECHANICS = dict(SECTOR_MAX=3, REGIME_POSITIONS=dict(STRONG=10, NORMAL=8, WEAK=5, RISK_OFF=2),
                 INITIAL_POSITION_CAP=0.10, GROWN_WINNER_CAP=0.20, ENTRY=80, EXIT=70, BUFFER=5, K=10)
DECISIONS = ("2011-01-31", "2017-11-30", 83)          # first / last decision session, count
NULL_SEEDS = tuple(range(1, 5001))
NULL_BATCHES = tuple((1 + 1000 * i, 1000 * (i + 1)) for i in range(5))     # E023-01..05 (future, owner approval)
RUNS = ("X994 canary", "E023-01", "E023-02", "E023-03", "E023-04", "E023-05", "E023-06")
POWER_SEED_BASE = 20261006

# Future (after the owner's approval of the real evaluation): c_IC is pinned here with the hash of the committed null
# result BEFORE the one real evaluation E023-06. None = not pinned (the real run must be refused).
C_IC = None
NULL_RESULT_SHA256 = None
THRESHOLD_COMMIT = None
PANEL_SHA256 = None                                   # the prepared H022 panel the null was calibrated on

# P7-CP5 (D177): the execution host S023 (X994 = byte copy), pinned before the canary; the null and the real run use it
HOST = "strategies/S023_h022_predictive/main.py"
HOST_SHA256 = "9b8476e12203586d8d6471acebe180f5944b8b4ff0cb564691aac2ca32d9fa8a"


def sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()
