"""Phase 5 structured chart score (H020): pins of the pre-registration (research/phase5/H020_spec.md, v1, P5-CP2), of
the constants of src/qresearch/lean/qr_chart.py and qr_h020_stats.py that it names, and of the frozen synthetic
scenario table.

FROZEN CANDIDATE v1 (2026-10-05), awaiting the owner's explicit approval of H020 real score validation.
tests/test_h020_spec.py checks the hashes and that the code still carries exactly these constants. Any change before
approval = a new version with a new hash; nothing may change after any real chart score is computed.
"""
from __future__ import annotations

import hashlib

from . import config

SPEC = "research/phase5/H020_spec.md"
SPEC_VERSION = 1
SPEC_SHA256 = None                                   # set at the P5-CP2 freeze (tests/test_h020_spec.py)
PROVENANCE = "research/phase5/H020_threshold_provenance.md"
SCENARIOS = "research/phase5/h020_scenarios_expected.json"
SCENARIOS_SHA256 = None
CODE = ("src/qresearch/lean/qr_chart.py", "src/qresearch/lean/qr_chart_render.py", "src/qresearch/lean/qr_h020_stats.py")
HYPOTHESIS = "H020"
NULL_SEEDS = tuple(range(1, 5001))                   # R = 5,000 tethered within-date permutation worlds
NULL_BATCHES = tuple((1 + 1000 * i, 1000 * (i + 1)) for i in range(5))   # E021-01..05 (future, owner approval)
RUNS = ("E987-01", "E021-01", "E021-02", "E021-03", "E021-04", "E021-05", "E021-06")   # none run in P5-CP2

CHART_CONSTANTS = dict(
    D_K=5, W_K=3, PROM_ATR=1.0, PROM_WIN=2, D_ATR=20, W_ATR=10, TOL_ATR=0.5, D_SCAN=300, W_SCAN=104,
    ZONE_LOOKBACK=252, ZONE_MIN_TOUCHES=2, TL_MIN_SPACING=10, BASE_MIN_W=7, BASE_MAX_W=65, BASE_ANCHOR_W=26,
    BASE_MAX_DEPTH=0.33, CONTRACT_MAX=0.80, CONTRACT_RECENT=(14, 5), CONTRACT_REF=(64, 15), BO_FRESH=5,
    BO_MAX_EXT=0.05, BO_VOL=1.40, BO_VOL_N=50, BO_CLV=0.5, NEAR_HIGH=0.75, HIGH_N=252, MA_SLOPE_W=4, RISK_MAX=0.08,
    RISK_ATR=2.5, EXT_MA20_ATR=2.0, DIST_N=25, DIST_MAX=4, DIST_DROP=-0.002, EXT_MA50_DQ=0.25, GAP_DQ=0.85, GAP_N=10,
    MIN_SESSIONS=504, HIST_SESSIONS=756,
    CONDITIONS=("W1", "W2", "W3", "W4", "W5", "B1", "B2", "B3", "B4", "B5", "T1", "T2", "T3", "T4", "T5",
                "R1", "R2", "R3", "R4", "R5"),
    DISQUALIFIERS=("D1", "D2", "D3", "D4", "D5"),
)
STATS_CONSTANTS = dict(
    NW_LAG=3, DIAG_NW_LAG=12, ANN=13.0, ANN_DIAG=4.0, HIGH_GROUPS=(3, 4), LOW_GROUPS=(0, 1), N_GROUPS=5,
    ECON_MIN_HIGH=0.03, MONO_MIN=0.90, BLOCKS=((2010, 2011), (2012, 2013), (2014, 2015), (2016, 2017)),
    BLOCK_MAX_SHARE=0.5, ALPHA=0.01, STATS=("t_ic", "t_inc"), NULL_STRATIFIED=False,
)

# Future (after the owner's approval of real score validation): the null critical values are pinned here, with the
# hash of the committed null result, BEFORE the one real evaluation E021-06. None = not pinned (the real run is refused).
C_IC = None
C_INC = None
NULL_RESULT_SHA256 = None


def sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def spec_hash() -> str:
    return sha256(SPEC)
