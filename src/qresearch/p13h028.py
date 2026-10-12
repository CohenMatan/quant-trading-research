"""Phase 13, H028 Fixed Strong Shrinkage Learned Stock Score (owner D217): pins of the frozen pre-registration
(research/phase13/H028_spec.md), the in-host module qr_h028, the host S030 (subclass of the pinned S029, uploaded as
qr_s029), the H027 references the real run must reproduce, the canary-calibrated 2016-2021 tolerance table and the run
provenance.

Written and committed BEFORE any H028 null world or result. Data v2.1 = the D207 manifest with the D213 owner exception
(qresearch.datafreeze_v21). TOLERANCE is set from the canary E030-01 before any null world; C_WEALTH_H028 and the null
result hash from the 5,000 lambda-100 conditional null worlds, merged before the ONE real development run.
tests/test_p13_h028*.py check these pins. The H026 / H027 pins (qresearch.p11h026 / p12h027) are never modified.
"""
from __future__ import annotations

import hashlib

from . import config, datafreeze_v21, p11h026, p12h027

DECISION = "D217"
HYPOTHESIS = "H028"
SPEC = "research/phase13/H028_spec.md"
SPEC_SHA256 = "39b205c2b50172b8d7f89a013e08423e5cec8cfd632b574c0b90cc8aba6b7d18"
CODE_SHA256 = {
    "src/qresearch/lean/qr_h028.py": "f92eb5f6e6cadb23c6542052d4149ddc35c787649992a4f7795adf4ca1b3f0be",
    "strategies/S030_h028_fixed_shrinkage/main.py": "951670de2531293e66151dd9875e567c7c3292fe105860a475f0692fb1bec043",
    "research/hypotheses/H028.md": "8e8ce9c9c95e3d699c57ab4f1e15378c6a6fbf138541047b9687c673f6a9c646",
}
HOST = "strategies/S030_h028_fixed_shrinkage/main.py"
PARENT_HOST = p12h027.HOST                              # S029, uploaded byte-identical as qr_s029.py
LAMBDA = 100.0
DATA_V21_MANIFEST_SHA256 = datafreeze_v21.MANIFEST_SHA256

CLOSED = dict(p12h027.CLOSED, H027="REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE (E029-05, D216/D217)")
PERIODS = dict(development="2011-01-01 .. 2021-12-31: FULLY SEEN development data; H028 is explicitly post-hoc; "
                           "development evidence only",
               holdout="2022-01-01 .. 2026-08-31: programme-wide final Holdout, SEALED (nothing read)")

# references (pinned, unchanged): H026 panels; the real H027 (E029-05); the committed H027 conditional rows 1-25
H026_FEATURE_PANEL_SHA256 = p11h026.FEATURE_PANEL_SHA256
H026_RESPONSE_PANEL_SHA256 = p11h026.RESPONSE_PANEL_SHA256
H027_REAL_WEALTH = 311396.7708031718
H027_REAL_S_WEALTH = 0.17148195882657039
H027_LAMBDA_SCHEDULE = [0.01, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]           # E029-05, outer years 2015-2021
H027_REAL_RISK = p12h027.H026_REAL_RISK                 # adequacy step 1 reference (spec section 5)
H027_NULL_ROWS_SHA256 = "cfbbb8fda1137ae738680c0faae5f70fe9ad8ed5f665fcbf7c079742c4f979e6"  # E029-02 rows, seeds 1-25
H027_PEAK_MEMORY_MB = dict(canary_E029_01=7785.0, null_E029_02=7682.5, null_E029_03=7728.1, rerun_E029_04=7714.6,
                           real_E029_05=7750.7)

# runs
CANARY = "E030-01"
NULL_RUNS = ("E030-02", "E030-03")
NULL_BATCHES = ((1, 2500), (2501, 5000))
RERUN = "E030-04"
RERUN_SEEDS = (1, 25)
REAL = "E030-05"

# set from the canary (tolerance) and the null runs (threshold), merged before the real run
# spec 6.2: max(1.5 x the largest |difference| over canary calibration pairs 1-100, floor); pinned from E030-01
TOLERANCE = {
    "2016": dict(ret=0.009007340054033253, turnover=0.18431948944490628),
    "2017": dict(ret=0.004244822721305108, turnover=0.07091525372131358),
    "2018": dict(ret=0.0038521977289630582, turnover=0.025),
    "2019": dict(ret=0.0030989247820020216, turnover=0.025),
    "2020": dict(ret=0.0032547503506195063, turnover=0.025),
    "2021": dict(ret=0.00268444125519518, turnover=0.025),
}
TOLERANCE_SHA256 = "a754d355ae96b77d9a5c2d0c8a5a80ecda8e2ac24b5075c25f25645a7c0c0128"
C_WEALTH_H028 = None
NULL_RESULT_SHA256 = None
THRESHOLD_COMMIT = None
ADEQUATE = None
NULL_RESULT = "research/phase13/cp1/P13_CP1_null.json"

RESULT = "research/phase13/cp1/P13_CP1_result.json"
CANDIDATE = None


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()
