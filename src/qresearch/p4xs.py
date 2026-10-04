"""Phase 4 cross-sectional technical signal validation (H019): pins of the pre-registration (research/phase4/
P4_xs_spec.md, v1, P4-CP3R) and of the constants of src/qresearch/lean/qr_xs.py that it names.

FROZEN CANDIDATE v1 (2026-10-04), awaiting the owner's explicit approval. tests/test_p4xs_spec.py checks the spec hash
and that qr_xs still carries exactly these constants. Any change before approval = a new version with a new hash;
nothing may change after any real signal, return or statistic is computed.
"""
from __future__ import annotations

import hashlib

from . import config

SPEC = "research/phase4/P4_xs_spec.md"
SPEC_VERSION = 1
SPEC_SHA256 = "3a0e36435543043ec0c6ddb30654a8d547b1b2bab7c1c9aca40b2bce2b445584"
HYPOTHESIS = "H019"
NULL_SEEDS = tuple(range(1, 5001))                # R = 5,000 identity-tethered within-date permutation worlds
NULL_BATCHES = tuple((1 + 1000 * i, 1000 * (i + 1)) for i in range(5))   # E020-01..05
CONSTANTS = dict(
    H_MONTHS=1, DIAG_HORIZONS=(3,), NW_LAG=2, DIAG_NW_LAG={3: 6},
    FIRST_DECISION=(2011, 2), LAST_DECISION=(2017, 11), LAST_DECISION_DIAG={3: (2017, 9)},
    HZZ_LAGS=(3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000), HZZ_BETA_MONTHS=12, ID_MIN_DAYS=200,
    N_DECILES=10, N_MOM_Q=5, N_MONO_Q=5, ECON_MIN_TOP=0.03, MONO_MIN=0.90, BLOCK_MAX_SHARE=0.5,
    BLOCKS=((2011, 2012), (2013, 2014), (2015, 2016), (2017, 2017)), ALPHA=0.01,
    SIGNALS=("S1", "S2", "S3"), INCREMENTAL=("S2", "S3"),
)
RUNS = ("E985-01", "E020-01", "E020-02", "E020-03", "E020-04", "E020-05", "E020-06")


def spec_hash() -> str:
    return hashlib.sha256((config.REPO_ROOT / SPEC).read_bytes()).hexdigest()
