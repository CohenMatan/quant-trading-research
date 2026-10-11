"""Phase 8, H023 Score v2 weight optimisation (owner D199): pins of the frozen pre-registration
(research/phase8/H023_spec.md), the grid module qr_h023 and the run provenance.

Written and committed BEFORE any H023 QuantConnect run. c_SEARCH, the fold thresholds and the null result hash are set
only from the 5,000 optimiser-null worlds (E025-02..06; rerun E025-07) and are committed and merged before the one real
development search E025-08. tests/test_p8_h023.py checks these pins. Data v2 (qresearch.datafreeze_v2), Score v1
(qresearch.p7score), the H022 population / response / null method (qresearch.p7pred) are unchanged.
"""
from __future__ import annotations

import hashlib
import json

from . import config, p7pred, p7pred_v2

DECISION = "D199"
HYPOTHESIS = "H023"
SPEC = "research/phase8/H023_spec.md"
SPEC_SHA256 = "34e8e738c1df263fb726f3936b7488dc70da7f84203e20e84683a2dfbb9cf470"
CODE_SHA256 = {
    "src/qresearch/lean/qr_h023.py": "60ac2fc67149c0a9b86dd95616b44bd154ca47d51c7fbefd389c9f6db47afce4",
    "research/hypotheses/H023.md": "3a2e1514eecd0484b636ce794278aa84fc8548664dd7f76f8717b590e6d47fbe",
    "strategies/S025_h023_score_v2/main.py": "beee5333de5e99babb0647167ea4feaf866fd93b1abf2975e8919e795e6dc554",
}
DATA_FREEZE_MANIFEST_SHA256 = p7pred_v2.DATA_FREEZE_MANIFEST_SHA256
H022_SPEC_SHA256 = p7pred.SPEC_SHA256
PRED_CODE_SHA256 = p7pred_v2.PRED_CODE_SHA256
PANEL_SHA256 = p7pred_v2.PANEL_SHA256                  # the prepared H022 panel on Data v2 (must be reproduced)
H022_NULL_WORLDS = p7pred_v2.NULL_WORLDS               # control-column integrity check of every H023 null world

# permanent records (owner D199)
H022_RECORD = dict(status="Rejected / NOT QUALIFIED", experiment="E024-07", data="Data v2", t_ic=0.47711861682625983,
                   ic_mean=0.0075504904395016096, hi_ann=-0.12573, mono=-0.40, gates="G1-G4 FAIL")
TRAINING_PERIOD = dict(decisions=("2011-01-31", "2017-11-30", 83), last_response_session="2017-12-29",
                       status="TRAINING / DEVELOPMENT (H023)")
SEALED = ("2018-01-01 .. 2021-12-31 (H023 external validation, sealed)", "2022-01-01 .. 2026-08-31 (Holdout, locked)")

# the grid and constants (tests check qr_h023 carries exactly these)
GRID_N = 92
CONTROL = (40, 45, 15)
CONTROL_INDEX = 42
CONSTANTS = dict(LAYER_MAX=(40, 45, 15), SCALE=360, MULT=(9, 8, 24), STEP=5, W_T=(10, 80), W_F=(10, 80), W_S=(0, 30),
                 TOTAL=100, ENTRY=80, THRESHOLDS=(75, 80, 85, 90), NW_LAG=2, ANN=12.0, N_Q=5,
                 BLOCKS=((2011, 2012), (2013, 2014), (2015, 2016), (2017, 2017)), ECON_MIN=0.03, MONO_MIN=0.90,
                 BLOCK_MAX_SHARE=0.5, D5=(60, 83, 2.0), R_NULL=5000, ALPHA=0.01, CRIT_FLOOR=2.326, PLATEAU_MIN=4,
                 PLATEAU_FRAC=0.80, FOLD_YEARS=(2014, 2015, 2016, 2017))
ADJACENT_PAIRS = 239
BOUNDARY_CONFIGS = 34

# runs
NULL_SEEDS = tuple(range(1, 5001))
NULL_BATCHES = tuple((1 + 1000 * i, 1000 * (i + 1)) for i in range(5))      # E025-02 .. E025-06
NULL_RUNS = ("E025-02", "E025-03", "E025-04", "E025-05", "E025-06")
RERUN_SEEDS = (1, 25)
RERUN = "E025-07"
CANARY = "E025-01"
REAL = "E025-08"
HOST = "strategies/S025_h023_score_v2/main.py"
PARENT_HOST = p7pred_v2.HOST                           # S024, uploaded byte-identical as qr_s024.py

# set after the canary (before any null world): digest of the per-stock layer subtotals of the prepared panel
COMPONENTS_SHA256 = "7652f7fca2c0bd68b9d23ba0a9eea4b2f850b1555ec3874ec9127a48b067509e"   # E025-01 (16/16)
CANARY_COMMIT = "54deb514b31fe90c4aeb321a3f1bcccf4be74aa5"

# set after the 5,000 optimiser-null worlds, merged before the real search
# P8-CP1 (D199): from the 5,000 optimiser-null worlds E025-02..06 (rerun E025-07 identical; every control column =
# the H022 / Data v2 null world of the same seed): max(50th largest null max_t_IC across the grid, 2.326); the floor
# does not bind. Pinned BEFORE the one real development search E025-08.
C_SEARCH = 2.9225785052912165
C_FOLD = {2014: 3.486801872690062, 2015: 3.5098267772816225, 2016: 3.5872288855328005,
          2017: 3.0235170098563535}   # walk-forward fold thresholds (diagnostic)
NULL_RESULT = "research/phase8/cp1/P8_CP1_null.json"
NULL_RESULT_SHA256 = "2819cd4c803684e4f19e93d3b97bedf73feab1d105e295227f501dc1ec997190"
NULL_WORLDS = "research/phase8/cp1/P8_CP1_null_worlds.json.gz"
THRESHOLD_COMMIT = "8b86665dc2624910dfe68b8e8ab89903edf8ada3"   # pinned the values above

# set only if a candidate exists (P8-CP1), before any 2018-2021 access
CANDIDATE = None


def sha(path: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / path).read_bytes()).hexdigest()


def candidate_record(weights, plateau, result_sha256, grid_sha256) -> dict:
    """The canonical record whose SHA-256 is the Score v2 Candidate hash (spec section 13)."""
    from . import p7score
    return dict(name="Score v2 Candidate", status="DEVELOPMENT CANDIDATE — NOT YET VALIDATED", hypothesis=HYPOTHESIS,
                weights=dict(technical=weights[0], fundamental=weights[1], sector=weights[2]),
                formula="Score_v2 = wT*Technical/40 + wF*Fundamental/45 + wS*Sector/15 (exact: 360*Score_v2 = "
                        "9*wT*Technical + 8*wF*Fundamental + 24*wS*Sector)",
                score_v1_spec_sha256=p7score.SPEC_SHA256, score_v1_code_sha256=dict(p7score.CODE_SHA256),
                data_v2_manifest_sha256=DATA_FREEZE_MANIFEST_SHA256, training_period=TRAINING_PERIOD,
                grid_sha256=grid_sha256, null_result_sha256=NULL_RESULT_SHA256, c_search=C_SEARCH,
                plateau_definition="spec section 9", selected_plateau=[list(w) for w in plateau],
                selection_rule="spec section 10", spec_sha256=SPEC_SHA256, real_result_sha256=result_sha256)


def record_sha(rec: dict) -> str:
    return hashlib.sha256(json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
