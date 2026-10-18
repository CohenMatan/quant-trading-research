"""Long-horizon Stage C (owner D242): the OF-A data / PIT feasibility audit protocol is frozen before any aggregate,
and the audit is non-return and Holdout-safe."""
import hashlib

from conftest import ROOT

PROTOCOL = ROOT / "research/longhorizon/stage_c/LH_StageC_protocol.md"
PROTOCOL_SHA256 = "ff97789b02007599f9e4bdb914dc8b56f50566c1d61e4015c2383a829a195a97"


def test_protocol_hash_pinned():
    assert hashlib.sha256(PROTOCOL.read_bytes()).hexdigest() == PROTOCOL_SHA256
