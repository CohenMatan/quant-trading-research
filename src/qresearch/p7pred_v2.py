"""H022 on FROZEN Data Infrastructure v2 (owner D194, P7-CP6): pins for the canary, the 5,000 null worlds and the new
Data-v2 c_IC. The H022 specification, gates, null method and qr_p7_pred are UNCHANGED (qresearch.p7pred); only the
data infrastructure differs (qresearch.datafreeze_v2, manifest cf833f6f...).

The Data-v1 threshold qresearch.p7pred.C_IC (2.390976216956) is DATA_V1_ONLY / UNUSED_ON_V2 and is never used here.
C_IC_V2 is set ONLY from the 5,000 Data-v2 null worlds E024-01..05 and committed before any real H022 evaluation;
the real evaluation itself is NOT authorised (D194). tests/test_p7_h022_v2.py checks these pins.
"""
from __future__ import annotations

from . import datafreeze_v2, p7pred

DECISION = "D194"
DATA_FREEZE_MANIFEST_SHA256 = "cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb"
SPEC_SHA256 = p7pred.SPEC_SHA256                        # H022 spec unchanged
PRED_CODE_SHA256 = p7pred.CODE_SHA256["src/qresearch/lean/qr_p7_pred.py"]
NULL_METHOD = ("src/qresearch/lean/qr_p7_pred.py", "src/qresearch/lean/qr_h020_stats.py", "src/qresearch/lean/qr_xs.py")
HOST = "strategies/S024_h022_data_v2/main.py"           # X999 = byte copy (the canary)
CANARY_HOST = "strategies/X999_h022_v2_canary/main.py"
FROZEN_HOST = "strategies/X998_data_v2_export/main.py"  # uploaded byte-identical as qr_x998.py
E998_REFERENCE = "E998-01"                              # the frozen Data v2 export the canary's score side must equal
CANARY = "E999-01"
NULL_SEEDS = tuple(range(1, 5001))
NULL_BATCHES = tuple((1 + 1000 * i, 1000 * (i + 1)) for i in range(5))      # E024-01 .. E024-05
NULL_RUNS = ("E024-01", "E024-02", "E024-03", "E024-04", "E024-05")
RERUN_SEEDS = (1, 25)                                  # pre-specified determinism rerun E024-06 (independent run)
RERUN = "E024-06"

# set after the canary passed (P7-CP6), before any null world: the prepared H022 panel on frozen Data v2
PANEL_SHA256 = None
CANARY_COMMIT = None

# set after the 5,000 null worlds, committed before any real evaluation (none is authorised)
C_IC_V2 = None
NULL_RESULT = "research/phase7/cp6/P7_CP6_null.json"
NULL_RESULT_SHA256 = None


def manifest_ok() -> bool:
    return datafreeze_v2.MANIFEST_SHA256 == DATA_FREEZE_MANIFEST_SHA256 == datafreeze_v2.manifest_sha()
