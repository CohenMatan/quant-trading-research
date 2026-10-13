"""Phase 14, H029 standalone Business Improvement Score + H030 fixed 50/50 combination with frozen H028 (owner D229):
pins of the pre-registered specification (research/phase14/H029_H030_spec.md), the module qr_h029, the standalone host
S031, the frozen inputs it must reproduce (Data v3 panel digests, H026 panels, H028 coefficients / wealth, LV15
wealth), the run ids and -- after the null -- the thresholds c_UP_H029 and c_INCREMENTAL_H030.

Amendment 1 (owner D233, research/phase14/H029_H030_amendment1_sector_null.md): the original single-stratum null
(E031-01..04, P14-CP3a) failed adequacy and stays the permanent record; the null is now the same-FF12-sector identity
tether with NEW run ids E031-06..10. The original spec stays byte-identical (SPEC_SHA256 unchanged); the amendment has
its own pin. The original null's thresholds are permanently invalid (INVALID_THRESHOLDS).

tests/test_p14_h029*.py and tests/test_p14_s031_host.py check these pins.
"""
from __future__ import annotations

import hashlib
import json

from . import config, datafreeze_v3, p11h026

DECISION = "D229"
AMENDMENT1_DECISION = "D233"
HYPOTHESES = ("H029", "H030")
PROGRAMME = "P14"
STRATEGY = "S031"
SPEC = "research/phase14/H029_H030_spec.md"
SPEC_SHA256 = "51121154b3efaf770ce8c82879dc56fc36a1f6b7891e2920cf67c72dba0f345a"
AMENDMENT1 = "research/phase14/H029_H030_amendment1_sector_null.md"
AMENDMENT1_SHA256 = "df620018a4359534420294758c817cdfb2dfa84cd5ebe29d15771b1d8667d4ad"
CODE_SHA256 = {
    "src/qresearch/lean/qr_h029.py": "9407ac0ebca1a7b95cdd8757597572e6e9bbad69df8469c9a94dc6a0f745811d",
    "strategies/S031_h029_h030/main.py": "dd95afc506fc95fae490e208d19d139944cf54c1b33db0ac346218210e80dacf",
    "src/qresearch/lean/qr_v3.py": "40bcf98d3aa62f625faa5c1f97a18c08d5a0d0d40bd9afcf300f5bf67fdcaccd",     # Data v3, frozen
}
HOST = "strategies/S031_h029_h030/main.py"
DATA_HOST = "strategies/X801_data_v21_export/main.py"
DATA_V3_MANIFEST_SHA256 = datafreeze_v3.MANIFEST_SHA256
H026_FEATURE_PANEL_SHA256 = p11h026.FEATURE_PANEL_SHA256
H026_RESPONSE_PANEL_SHA256 = p11h026.RESPONSE_PANEL_SHA256
H028_RESULT = "research/phase13/cp1/P13_CP1_result.json"          # E030-05 (the frozen H028 champion)
H028_RESULT_SHA256 = "41c265e1c6b71c9fbb04c1a83a13414e1ea9a20f01fbbd341c22088f98b3639c"
# the original single-stratum null (P14-CP3a): permanent record, never reused
ORIGINAL_RUNS = dict(canary="E031-01", null=("E031-02", "E031-03"), rerun="E031-04", real_never_run="E031-05")
ORIGINAL_NULL_RESULT = "research/phase14/cp3/P14_CP3_null.json"
ORIGINAL_NULL_RESULT_SHA256 = "982f6d74eec3563110a3b8c6c9a8c69c959d849d60a3ae5e62a24a77064a165c"
INVALID_THRESHOLDS = (0.2695877034430064, 0.005896238744820351)        # (c_UP, c_INC) of the inadequate null
ORIGINAL_CODE_SHA256 = {                                               # the code the original runs used (7bdbcf7)
    "src/qresearch/lean/qr_h029.py": "2ec9820c939d6445a9a516a6ff86af880c1aa2ac1ceac42effbbf1efcc3c0d5e",
    "strategies/S031_h029_h030/main.py": "44e41148ac787604615f7c37ca79116819f1f2e4c2b09150be1151dfd40d3640",
}
ORIGINAL_NULL_SEEDS = {"E031-02": (1, 2500), "E031-03": (2501, 5000), "E031-04": (1, 25)}
# Amendment 1 (sector-stratified null) run ids
CANARY, NULL_RUNS, RERUN, REAL = "E031-06", ("E031-07", "E031-08"), "E031-09", "E031-10"
NULL_SEEDS = {"E031-07": (1, 2500), "E031-08": (2501, 5000), "E031-09": (1, 25)}
# the sector-stratified null result (P14-CP3b, D234): INADEQUATE (H029 name turnover below all 5,000 worlds) ->
# H029/H030 BLOCKED; no threshold computed or pinned; no real run
SECTOR_NULL_RESULT = "research/phase14/cp3/P14_CP3b_null.json"
SECTOR_NULL_RESULT_SHA256 = "7a48b1e5816611985526b0753cc4ca7db690451e0fd2a38f5f3d3bce3b294121"
SECTOR_NULL_VERDICT = "H029/H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE"
# pinned after the sector-stratified null passes adequacy, before the real run; None until then
C_UP_H029 = None
C_INCREMENTAL_H030 = None
NULL_RESULT_SHA256 = None
THRESHOLD_COMMIT = None


def original_run_ids() -> tuple:
    """The committed original-null records (validated as history only; the runner refuses re-running an id)."""
    o = ORIGINAL_RUNS
    return (o["canary"], *o["null"], o["rerun"])


def sha256_file(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def h029_panel_digests_sha256() -> str:
    m = json.loads((config.REPO_ROOT / datafreeze_v3.MANIFEST).read_text())
    return m["panel_digests_sha256"]


def h028_inputs():
    """(H028 terminal wealth, LV15 terminal wealth, {year: {b0, beta}}) of the committed E030-05 result."""
    d = json.loads((config.REPO_ROOT / H028_RESULT).read_text())
    coef = {y: dict(b0=v["b0"], beta=v["beta"]) for y, v in d["coefficients"].items()}
    return d["portfolio"]["h028"]["wealth"], d["portfolio"]["lv15"]["wealth"], coef
