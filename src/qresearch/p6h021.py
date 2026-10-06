"""Phase 6 H021-A sector relative-momentum falsification test: pins of the frozen specification
(research/phase6/H021A_spec.md v1, owner D160) and of the constants of src/qresearch/lean/qr_h021.py.

FROZEN 2026-10-06 before any null world or real statistic. tests/test_h021_spec.py checks the hashes and that the
code still carries exactly these constants. Nothing may change after a null world exists; c is pinned below, with the
hash of the committed null result and the panel digests, BEFORE the one real evaluation E022-06.
"""
from __future__ import annotations

import hashlib

from . import config

SPEC = "research/phase6/H021A_spec.md"
SPEC_VERSION = 1
SPEC_SHA256 = "d4a2b8864603965d52e09206d32246d368639eb52b277ee16e57d116fc960141"
CODE = ("src/qresearch/lean/qr_h021.py",)
CODE_SHA256 = {"src/qresearch/lean/qr_h021.py": "67820d91e783c24da1850ec03fa72f82d190becca30cba1bd4aa6df2136fc6cf"}
HYPOTHESIS = "H021"
OWNER_DECISION = "D160"
NULL_SEEDS = tuple(range(1, 5001))                                        # R = 5,000 derangement worlds
NULL_BATCHES = tuple((1 + 1000 * i, 1000 * (i + 1)) for i in range(5))    # E022-01..05
CANARY = "E989-02"                 # E989-01 failed on a plumbing KeyError (D161); the canary re-run
NULL_RUNS = ("E022-01", "E022-02", "E022-03", "E022-04", "E022-05")
REAL_RUN = "E022-06"
HOST_CODE = ("strategies/X989_h021_sector/main.py",)                      # hashed with the null pins

CONSTANTS = dict(
    UNIVERSE=("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"), LOOKBACK=6, TOP_K=3,
    FIRST_DECISION=(2000, 1), LAST_DECISION=(2017, 11), ECON_MIN=0.03,
    BLOCKS=((2000, 2005), (2006, 2011), (2012, 2017)), BLOCK_MAX_SHARE=0.5, ALPHA=0.01, R_NULL=5000,
    DIAG_HORIZONS=(3, 6), DIAG_PERIODS=(((2010, 1), (2017, 11)), ((2005, 1), (2017, 11))),
)

# Pinned after the null (E022-01..05) and BEFORE E022-06. None = not pinned (the real run is refused).
C = None                      # 50th largest of 5,000 null t_IC
NULL_RESULT = "research/phase6/H021A_null_result.json"
NULL_RESULT_SHA256 = None
NULL_WORLDS_CSV_SHA256 = None
PANEL_SHA256 = None           # digest(S, Y1) the null was calibrated on (canary and every batch identical)
DIAG_SHA256 = None            # digest of the diagnostic panels
HOST_SHA256 = None
THRESHOLD_COMMIT = None       # the commit that pinned the values above (recorded in the next commit)


def sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def spec_hash() -> str:
    return sha256(SPEC)
