"""Narrow SEC-based universe repair + re-audit UCR-1 (owner D269, UR-2 option A): pins of the frozen protocol, the X806
host, the qr_ucr module, the point-in-time SEC builder, the offline evaluation rule and the two public SEC objects,
all committed BEFORE the one authorised run (E806-01; E806-02 only as the single retry after a documented
infrastructure failure). tests/test_rr_ucr.py checks these pins."""
from __future__ import annotations

import hashlib

from . import config, rr_sca

DECISION = "D269"
PROTOCOL = "research/rr/universe_repair/UCR_protocol.md"
PROTOCOL_SHA256 = "9280813d427de06166516cceb001d91f99144b0ffc5e00c97b4d07bc18f21201"
HOST = "strategies/X806_universe_repair_reaudit/main.py"
MODULE = "src/qresearch/lean/qr_ucr.py"
BUILDER = "research/rr/universe_repair/build_ucr_sec.py"
EVAL_RULES = "research/rr/universe_repair/UCR_eval.py"
CODE_SHA256 = {
    HOST: "6ab8a062dd2dde3886d54ad21ed054cf2c8d08fc0783b06e13cee3a5cafb0256",
    MODULE: "77135cd38a1edfa8e6b295cf00255c34adb36780328bdd135cc3309e4a85e9d5",
    BUILDER: "fb073368cdf73bf187b142f11ef20c9f77abbe9b95d8ac44ddb479bff6aa7c10",
    EVAL_RULES: "a78f4bbd3160862186daee457d1dc824b1a715ce3ee066f1ab79fd20c569f7aa",
    rr_sca.MODULE: "38045153a769367b41f42c9fb858c9064deaf53fc11558ea5a07fcc14672dba5",
}
UCR_MANIFEST = "research/rr/universe_repair/ucr_sec_v1_manifest.json"
UCR_REFERENCE_SHA256 = "ba3ab515f6fad602f8638279927c4b5b3c417577851f7748891ff23be52a4a82"
UCR_OBJECT_KEY = "rr/ucr_sec_v1.json"
SCA_REFERENCE_SHA256 = rr_sca.SEC_REFERENCE_SHA256
SCA_OBJECT_KEY = rr_sca.OBJECT_KEY
RUN = "E806-01"
RETRY = "E806-02"
PROGRAMME = "RR"
CYCLE = "UCR"


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def run_params() -> dict:
    return dict(ucr_protocol_sha256=PROTOCOL_SHA256,
                ucr_code_sha256={k.split("/")[-1]: v for k, v in CODE_SHA256.items() if k in (HOST, MODULE)},
                sca_object_key=SCA_OBJECT_KEY, sca_reference_sha256=SCA_REFERENCE_SHA256,
                ucr_object_key=UCR_OBJECT_KEY, ucr_reference_sha256=UCR_REFERENCE_SHA256)
