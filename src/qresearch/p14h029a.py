"""Phase 14, H029-A Business Improvement data-feasibility audit (owner D227): pins of the pre-registered audit
specification (research/phase14/H029A_audit_spec.md), the in-host module qr_h029a, the audit host X802 and the run.

Infrastructure / data quality only: no return, IC, wealth or feature-return statistic is ever computed. The audit
run E802-01 is the ONE in-cloud run (aggregates only); tests/test_p14_h029a*.py check these pins.
"""
from __future__ import annotations

import hashlib

from . import config, datafreeze_v21

DECISION = "D227"
HYPOTHESIS = "H029"
PROGRAMME = "P14"
SPEC = "research/phase14/H029A_audit_spec.md"
SPEC_SHA256 = "dcb689a3873422a4d1569632455fa472160131ac4dd99ebb68ced1729a8522aa"
CODE_SHA256 = {
    "src/qresearch/lean/qr_h029a.py": "3cff1e0361fdae6b6724d4f73866f45a9c7ead4f37dbf9a4b216d4f5e1d24961",
    "strategies/X802_h029a_feasibility_audit/main.py": "f823291c984148f6cd4f37aa3e49c06b48b5c238a2822c58fab1073a8caef9db",
}
HOST = "strategies/X802_h029a_feasibility_audit/main.py"
DATA_HOST = "strategies/X801_data_v21_export/main.py"
DATA_V21_MANIFEST_SHA256 = datafreeze_v21.MANIFEST_SHA256
AUDIT = "E802-01"
PERIODS = dict(development="2011-01-01 .. 2021-12-31: already-seen development data (fundamental availability only)",
               holdout="2022-01-01 .. 2026-08-31: programme-wide final Holdout, SEALED (nothing read)")


def sha256_file(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()
