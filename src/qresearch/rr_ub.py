"""Universe Baseline Audit UB-1 (owner D263): pins of the frozen protocol, the X804 host, the qr_ub statistics module
and the offline evaluation rule, all committed BEFORE the one authorised run (E804-01; E804-02 only as the single
retry after a documented infrastructure failure). tests/test_rr_ub*.py check these pins."""
from __future__ import annotations

import hashlib

from . import config

DECISION = "D263"
PROTOCOL = "research/rr/universe_baseline/UB_protocol.md"
PROTOCOL_SHA256 = "d5ce14e251cb910b463e05c8d5a611f00ee981eec5a586cb73de65d1fb7137ef"
HOST = "strategies/X804_universe_baseline/main.py"
MODULE = "src/qresearch/lean/qr_ub.py"
EVAL_RULES = "research/rr/universe_baseline/UB_eval.py"
CODE_SHA256 = {
    HOST: "feeaf55afa563faf11200b571500216ae06b471f8aaa437def44edbe727e76b6",
    MODULE: "dbb8eb671c153941d90a9aa023b305eadcf36cd9d4c8e8435a0632af024661ed",
    EVAL_RULES: "1cc63d14e12c31ce290f1780e1fd92ef5c0e8b16dbcb1bffecb2e0545b5a9ec7",
}
RUN = "E804-01"
RETRY = "E804-02"
PROGRAMME = "RR"
CYCLE = "UB"
RESULT = "research/rr/universe_baseline/UB_result_E804-01.json"


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def run_params() -> dict:
    return dict(ub_protocol_sha256=PROTOCOL_SHA256, ub_code_sha256={k.split("/")[-1]: v for k, v in CODE_SHA256.items()
                                                                     if k != EVAL_RULES})
