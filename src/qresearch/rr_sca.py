"""SEC Classification Audit SCA-1 (owner D267, UR-1 option A): pins of the frozen protocol, the X805 host, the qr_sca
module, the SEC builder, the offline evaluation rule and the public SEC reference object, all committed BEFORE the
one authorised run (E805-01; E805-02 only as the single retry after a documented infrastructure failure).
tests/test_rr_sca.py checks these pins."""
from __future__ import annotations

import hashlib

from . import config

DECISION = "D267"
PROTOCOL = "research/rr/sec_classification/SCA_protocol.md"
PROTOCOL_SHA256 = "a4cec4f5111adad28fe653f708fc1fd6264700f26538065ac16d5b8692e21b36"
HOST = "strategies/X805_sec_classification/main.py"
MODULE = "src/qresearch/lean/qr_sca.py"
BUILDER = "research/rr/sec_classification/build_sca_sec.py"
EVAL_RULES = "research/rr/sec_classification/SCA_eval.py"
CODE_SHA256 = {
    HOST: "eb88c69e9299c80b416bab339ee2786ac53d5cd3919c67fad072b98367d722ad",
    MODULE: "38045153a769367b41f42c9fb858c9064deaf53fc11558ea5a07fcc14672dba5",
    BUILDER: "db5ce7b5b1d81b101199f70cd8bd5b3f1cde5ade1dcc3f4b4fffd410e0c506fe",
    EVAL_RULES: "fa75577b7a119d6fe076c9c3921b066d50b82818e059d1f0279487ec527742bc",
}
SEC_MANIFEST = "research/rr/sec_classification/sca_sec_v1_manifest.json"
SEC_REFERENCE_SHA256 = "67bc9260f3c5bed6ac723a0ed4b177dee9f9be5814f482200438687b0984a747"
OBJECT_KEY = "rr/sca_sec_v1.json"
RUN = "E805-01"
RETRY = "E805-02"
PROGRAMME = "RR"
CYCLE = "SCA"


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def run_params() -> dict:
    return dict(sca_protocol_sha256=PROTOCOL_SHA256,
                sca_code_sha256={k.split("/")[-1]: v for k, v in CODE_SHA256.items() if k in (HOST, MODULE)},
                sec_object_key=OBJECT_KEY, sec_reference_sha256=SEC_REFERENCE_SHA256)
