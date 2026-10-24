"""OD-1 outcome-driven discovery study (owner D308): pins of the frozen protocol (research/od/OD1_protocol.md), the
host X808, the pure module qr_od1, the offline evaluation rule and the three public SEC objects (the two frozen H032
objects plus the OD-1 fundamental extension rr/od1_sec_v1.json), all committed BEFORE the one run E808-01 (E808-02
only after a documented infrastructure failure). tests/test_od1_pins.py checks these pins."""
from __future__ import annotations

import hashlib

from . import config, os1, rr_ucr

DECISION = "D308"
PROGRAMME = "OD"
PROTOCOL = "research/od/OD1_protocol.md"
PROTOCOL_SHA256 = "cc6b1d2cdff3b0aeaa6d3fe59d40e1a8595b841edcadcf93b5a567f3595f8bc6"
HOST = "strategies/X808_od1_outcomes/main.py"
MODULE = "src/qresearch/lean/qr_od1.py"
EVAL_RULES = "research/od/OD1_eval.py"
CODE_SHA256 = {
    HOST: "f7778bacafde1672dc4766695b44615c766cda3727967554c6dc238843880311",
    MODULE: "679aee8f51c4b340d519e48c8b57ac586a9bf5616e002f01f2cf62f6167eed82",
    EVAL_RULES: "99f0b4aa39793ebe19e80e59c8706010454b3cd72081c6f2d9d74aef7b617fbd",
}
RUN, RETRY = "E808-01", "E808-02"
OD1_OBJECT_KEY = "rr/od1_sec_v1.json"
OD1_REFERENCE_SHA256 = "8bafcedea8a3b0f377f2b8642d9988ebd353e644e0e4964e95e3403b9dfa3d4d"
OD1_MANIFEST = "research/od/od1_sec_v1_manifest.json"


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def run_params() -> dict:
    return dict(od1_protocol_sha256=PROTOCOL_SHA256,
                od1_code_sha256={"main.py": CODE_SHA256[HOST], "qr_od1.py": CODE_SHA256[MODULE],
                                 "qr_os1.py": os1.CODE_SHA256[os1.MODULE],
                                 "qr_ucr.py": rr_ucr.CODE_SHA256[rr_ucr.MODULE]},
                ucr_object_key=os1.UCR_OBJECT_KEY, ucr_reference_sha256=os1.UCR_REFERENCE_SHA256,
                os1_object_key=os1.OS1_OBJECT_KEY, os1_reference_sha256=os1.OS1_REFERENCE_SHA256,
                od1_object_key=OD1_OBJECT_KEY, od1_reference_sha256=OD1_REFERENCE_SHA256)
