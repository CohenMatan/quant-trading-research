"""Phase 14, H029 standalone Business Improvement Score + H030 fixed 50/50 combination with frozen H028 (owner D229):
pins of the pre-registered specification (research/phase14/H029_H030_spec.md), the module qr_h029, the standalone host
S031, the frozen inputs it must reproduce (Data v3 panel digests, H026 panels, H028 coefficients / wealth, LV15
wealth), the run ids and -- after the null -- the thresholds c_UP_H029 and c_INCREMENTAL_H030.

tests/test_p14_h029*.py and tests/test_p14_s031_host.py check these pins.
"""
from __future__ import annotations

import hashlib
import json

from . import config, datafreeze_v3, p11h026

DECISION = "D229"
HYPOTHESES = ("H029", "H030")
PROGRAMME = "P14"
STRATEGY = "S031"
SPEC = "research/phase14/H029_H030_spec.md"
SPEC_SHA256 = "51121154b3efaf770ce8c82879dc56fc36a1f6b7891e2920cf67c72dba0f345a"
CODE_SHA256 = {
    "src/qresearch/lean/qr_h029.py": "2ec9820c939d6445a9a516a6ff86af880c1aa2ac1ceac42effbbf1efcc3c0d5e",
    "strategies/S031_h029_h030/main.py": "44e41148ac787604615f7c37ca79116819f1f2e4c2b09150be1151dfd40d3640",
    "src/qresearch/lean/qr_v3.py": "40bcf98d3aa62f625faa5c1f97a18c08d5a0d0d40bd9afcf300f5bf67fdcaccd",     # Data v3, frozen
}
HOST = "strategies/S031_h029_h030/main.py"
DATA_HOST = "strategies/X801_data_v21_export/main.py"
DATA_V3_MANIFEST_SHA256 = datafreeze_v3.MANIFEST_SHA256
H026_FEATURE_PANEL_SHA256 = p11h026.FEATURE_PANEL_SHA256
H026_RESPONSE_PANEL_SHA256 = p11h026.RESPONSE_PANEL_SHA256
H028_RESULT = "research/phase13/cp1/P13_CP1_result.json"          # E030-05 (the frozen H028 champion)
CANARY, NULL_RUNS, RERUN, REAL = "E031-01", ("E031-02", "E031-03"), "E031-04", "E031-05"
NULL_SEEDS = {"E031-02": (1, 2500), "E031-03": (2501, 5000), "E031-04": (1, 25)}
# pinned after the null (step 17-18), before the real run; None until then
C_UP_H029 = None
C_INCREMENTAL_H030 = None
NULL_RESULT_SHA256 = None
THRESHOLD_COMMIT = None


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
