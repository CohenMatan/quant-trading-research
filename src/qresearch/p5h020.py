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
SPEC_SHA256 = "48e6feccbdb734d6918e28f332fe34154a529122bb6ed9ff3c76a95edca22b06"
PROVENANCE = "research/phase5/H020_threshold_provenance.md"
ADDENDUM = "research/phase5/H020_spec_addendum_1.md"      # pre-run clarifications (D154): sector diagnostic, TSR
ADDENDUM_SHA256 = "c653513cb9ec754270c92ac6c7828f5dae45c1bc4882d94f6552d3a883186498"
SCENARIOS = "research/phase5/h020_scenarios_expected.json"
SCENARIOS_SHA256 = "0cdec3e73c2d64351ee13abe02cf847c26120a6733be395c12a37415719db8b8"
CODE = ("src/qresearch/lean/qr_chart.py", "src/qresearch/lean/qr_chart_render.py", "src/qresearch/lean/qr_h020_stats.py")
CODE_SHA256 = {
    "src/qresearch/lean/qr_chart.py": "c9dc5b18c7ef28f6aa56b6a4b0e5a7296d29f2d17decce6c8c61723fb7e609e5",
    "src/qresearch/lean/qr_chart_render.py": "3bcf12077e7dc3e0c428a64b23cbea297cfbec6be9ebf99c7588c888f2784506",
    "src/qresearch/lean/qr_h020_stats.py": "426d37218f8a27707a2b18e8e99559555d03a1e36ff0ddb499d92df4a676b049",
}
HYPOTHESIS = "H020"
NULL_SEEDS = tuple(range(1, 5001))                   # R = 5,000 tethered within-date permutation worlds
NULL_BATCHES = tuple((1 + 1000 * i, 1000 * (i + 1)) for i in range(5))   # E021-01..05 (future, owner approval)
RUNS = ("E987-01", "E021-01", "E021-02", "E021-03", "E021-04", "E021-05", "E021-06")
HOST_CODE = ("src/qresearch/lean/qr_h020_panel.py", "src/qresearch/lean/qr_h020_diag.py",
             "strategies/X987_h020_chart/main.py")              # real-run plumbing (D154), hashed with the null pins

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
C_IC = 2.328878115                 # 50th largest of 5,000 null t_ic (E021-01..05)
C_INC = 2.264744985                # 50th largest of 5,000 null t_inc
NULL_RESULT = "research/phase5/H020_null_result.json"
NULL_RESULT_SHA256 = "4b26be842ce499696a82e29c8ddf84d386f590597f4f943f185d645d84be4e13"
CHART_PANEL_SHA256 = "aa5d3c51fb1203584adfc3604508fcfb0537af7f630381c51a11e34492cbb7d9"                     # the chart side the null was calibrated on (E021-01..05, all identical)
NULL_WORLDS_CSV_SHA256 = "fa936246d1af77dc99d75813ac30b43d22abee52a065ac795904969d96e35b2f"
THRESHOLD_COMMIT = None                       # the commit that pinned the values above (recorded in the next commit)


def sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def spec_hash() -> str:
    return sha256(SPEC)
