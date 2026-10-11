"""Phase 9, H024 Feature Redesign and Selection (owner D201): pins of the frozen pre-registration
(research/phase9/H024_spec.md), the feature / engine module qr_h024, the host S026 and the run provenance.

Written and committed BEFORE any H024 QuantConnect run. The retained features, redundancy links, model-library hash
and population digest are set from the canary E026-01 (feature values only, no response) before any null world;
c_FEATURE, c_MODEL, the fold thresholds and the null result hash are set from the 5,000 null worlds E026-02..06
(rerun E026-07) and merged before the one real development search E026-08. tests/test_p9_h024*.py check these pins.
Data v2 (qresearch.datafreeze_v2), Score v1 (qresearch.p7score), the H022 population / response / null method
(qresearch.p7pred) and the H023 engine (qresearch.p8h023) are unchanged.
"""
from __future__ import annotations

import hashlib
import json

from . import config, p7pred_v2, p8h023

DECISION = "D201"
HYPOTHESIS = "H024"
SPEC = "research/phase9/H024_spec.md"
SPEC_SHA256 = "b28e580332bd350d20d34871c85f3288795e29810638881a0bc8893813cde4a5"
CODE_SHA256 = {
    "src/qresearch/lean/qr_h024.py": "f9b1c87e25ea3b98bda58496fab8eee55b47661116c622de5827362ba865465c",
    "strategies/S026_h024_features/main.py": "c09cdf42be463786e5214cc06c29cf8bb155c896716d555a5acf67805c55970a",
    "research/hypotheses/H024.md": "7dc2e65e7e485f679deac9f8f923bd1ae46c375ad746e0942cb0c25fb6dedb39",
    "research/phase9/P9_feature_inventory.md": "104526eebeb776f914ebab966e47c60183b1ccea5d60ecef39310ea9b99d87d2",
}
ENGINE_SHA256 = p8h023.CODE_SHA256["src/qresearch/lean/qr_h023.py"]       # the frozen H023 engine, reused
DATA_FREEZE_MANIFEST_SHA256 = p7pred_v2.DATA_FREEZE_MANIFEST_SHA256
PRED_CODE_SHA256 = p7pred_v2.PRED_CODE_SHA256
PANEL_SHA256 = p7pred_v2.PANEL_SHA256                  # the prepared H022 panel on Data v2 (must be reproduced)

# permanent records (owner D201)
H022_RECORD = dict(status="REJECTED", experiment="E024-07", t_ic=0.47711861682625983, ic_mean=0.0075504904395016096,
                   hi_ann=-0.12573, mono=-0.40, gates="G1-G4 FAIL")
H023_RECORD = dict(status="NO ROBUST SCORE V2 CANDIDATE", experiment="E025-08", best=(80, 10, 10), best_t_ic=0.972,
                   null_p=0.413, qualified=0, plateaus=0)
PERIODS = dict(development="2011-01-31 .. 2017-11-30 (83 decisions): DEVELOPMENT / TRAINING (H024)",
               validation="2018-01-01 .. 2021-12-31: SEALED VALIDATION",
               holdout="2022-01-01 .. 2026-08-31: SEALED HOLDOUT")

# the frozen library rule (spec sections 3-6; tests check qr_h024 carries exactly these)
LIBRARY_CANDIDATES = ("MOM", "LOWVOL", "GPA", "ACC", "BM", "AG", "REV1M", "CBOP", "HI52", "CFP", "EQA")
CONSTANTS = dict(MAX_FEATURES=15, MODEL_BUDGET=500, SIZES=(2, 3, 4), COVERAGE_MIN=0.90, REDUNDANCY_RHO=0.80,
                 ENTRY=80.0, D6_FRAC=0.40, NBR_MIN=3, MIN_SECTOR_GROUP=10, FOLD_YEARS=(2014, 2015, 2016, 2017))

# runs
NULL_SEEDS = tuple(range(1, 5001))
NULL_BATCHES = tuple((1 + 1000 * i, 1000 * (i + 1)) for i in range(5))      # E026-02 .. E026-06
NULL_RUNS = ("E026-02", "E026-03", "E026-04", "E026-05", "E026-06")
RERUN_SEEDS = (1, 25)
RERUN = "E026-07"
CANARY = "E026-01"
REAL = "E026-08"
HOST = "strategies/S026_h024_features/main.py"
PARENT_HOST = p7pred_v2.HOST                           # S024, uploaded byte-identical as qr_s024.py

# set from the canary E026-01 (feature values only; no response), before any null world
# E026-01 (16/17; check 6 = the D202 vendor snapshot change outside the population): every feature >= 90% covered
# (HI52 99.92%, all others 100%); largest median |rho| between different families 0.58 -> no redundancy link
FEATURES = ('MOM', 'LOWVOL', 'GPA', 'ACC', 'BM', 'AG', 'REV1M', 'CBOP', 'HI52', 'CFP', 'EQA')
LINKS = ()                                             # redundancy links (median |rho| >= 0.80, different families)
LIBRARY_SHA256 = "6af3616f30256226b44f2612fd5e227fd0e56a47445c621b2bfd63edf7d23922"
MODEL_COUNT = 415                                      # 52 two-, 138 three-, 225 four-feature models
POPULATION_SHA256 = "791a2d4c8972b2d10465762d8a0a675f159d37b6cfab3ff185b2e6712c3b0bc8"   # 34831 stock-months
CANARY_COMMIT = "86c0cf3786eabdab199fec92a21ddc906baf8bec"

# set after the 5,000 null worlds, merged before the real search
# P9-CP1 (D201): from the 5,000 null worlds E026-02..06 (rerun E026-07 identical; panel / population / library =
# pins in every batch): max(50th largest null maximum, 2.326); no floor binds. Pinned BEFORE the real search E026-08.
C_FEATURE = 3.4533403374111082
C_MODEL = 4.3672788679087295
C_FOLD = {2014: 5.226474685869657, 2015: 5.0028522952177354, 2016: 4.778611975498576,
          2017: 4.4241903365718285}   # walk-forward (diagnostic)
NULL_RESULT = "research/phase9/cp1/P9_CP1_null.json"
NULL_RESULT_SHA256 = "db1cb1923b9aa0580a9c62fbd1238db8827033128239a7fa7530802404d2fc89"
NULL_WORLDS = "research/phase9/cp1/P9_CP1_null_worlds.json.gz"
THRESHOLD_COMMIT = None

# set only if a candidate exists (P9-CP1), before any 2018-2021 access
CANDIDATE = None


def sha(path: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / path).read_bytes()).hexdigest()


def candidate_record(model, result_sha256) -> dict:
    """The canonical record whose SHA-256 is the H024 Score v3 Candidate hash (spec section 13)."""
    from . import p7score
    return dict(name="H024 Score v3 Candidate", status="DEVELOPMENT CANDIDATE — NOT YET VALIDATED", hypothesis=HYPOTHESIS,
                features=list(model), score="100 x mean of the oriented within-date percentiles (equal weights)",
                threshold=80, spec_sha256=SPEC_SHA256, feature_code_sha256=CODE_SHA256["src/qresearch/lean/qr_h024.py"],
                engine_sha256=ENGINE_SHA256, score_v1_code_sha256=dict(p7score.CODE_SHA256),
                data_v2_manifest_sha256=DATA_FREEZE_MANIFEST_SHA256, periods=PERIODS, library_sha256=LIBRARY_SHA256,
                population_sha256=POPULATION_SHA256, c_model=C_MODEL, c_feature=C_FEATURE,
                null_result_sha256=NULL_RESULT_SHA256, real_result_sha256=result_sha256)


def record_sha(rec: dict) -> str:
    return hashlib.sha256(json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
