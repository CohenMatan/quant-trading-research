"""Phase 14, Data v3 targeted fundamental PIT / restatement hardening for H029 (owner D229): pins of the pre-registered
specification (research/phase14/data_v3/DATA_V3_spec.md), the offline builder and its packed tables (guard v3,
SEC validation reference), the in-host module qr_v3, the audit host X803 and the run.

Infrastructure / data quality only: no return, IC, wealth or feature-return statistic is ever computed. The audit
run E803-01 is the ONE in-cloud run (aggregates only); tests/test_p14_x803_host.py checks these pins.
"""
from __future__ import annotations

import hashlib

from . import config, datafreeze_v21

DECISION = "D229"
HYPOTHESIS = "H029"
PROGRAMME = "P14"
SPEC = "research/phase14/data_v3/DATA_V3_spec.md"
SPEC_SHA256 = "b4b8aa9b1c212e98bdf1aea7ed3ed577be21d9d1c195fa06ff54764452ab73d0"
CODE_SHA256 = {
    "src/qresearch/lean/qr_v3.py": "40bcf98d3aa62f625faa5c1f97a18c08d5a0d0d40bd9afcf300f5bf67fdcaccd",
    "src/qresearch/lean/qr_h029a.py": "3cff1e0361fdae6b6724d4f73866f45a9c7ead4f37dbf9a4b216d4f5e1d24961",
    "src/qresearch/data_v3.py": "6495dc021d692ef0aff1c99019ff6930ee39d8dca29cf01c3fe309a702b2fd87",
    "research/phase14/data_v3/build_data_v3.py": "840191d71bc6d1a58a75d45fd24d99adf64f04f22c81d57cf561906465b761cc",
    "strategies/X803_data_v3_audit/main.py": "59df5e0280a41482d1ea5bda68768a18ceaede03d882da9751190d97cd851ab1",
}
GUARD_SHA256 = "d4e1065baec3786d29d30397cf21fc7f8d298b52455e8b1f156b377bd680996a"       # raw JSON of the packed guard table (qr_data_v3_NN)
VAL_SHA256 = "2dbec426034970661526b7ab6e9774df0231022caf79e3c36ef8eccba9aed97b"         # raw JSON of the packed SEC validation reference (qr_v3val_NN)
HOST = "strategies/X803_data_v3_audit/main.py"
DATA_HOST = "strategies/X801_data_v21_export/main.py"
DATA_V21_MANIFEST_SHA256 = datafreeze_v21.MANIFEST_SHA256
AUDIT = "E803-01"
PERIODS = dict(development="2011-01-01 .. 2021-12-31: already-seen development data (fundamental availability only)",
               holdout="2022-01-01 .. 2026-08-31: programme-wide final Holdout, SEALED (nothing read)")


def sha256_file(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()
