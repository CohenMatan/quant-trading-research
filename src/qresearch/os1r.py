"""H032 R1 / R2 (owner D282): pins of the implementation and evaluation protocol (research/os/H032_R_protocol.md), the
S033 trading host, the trading layer qr_os1_trade, the shadow engine copy qr_os1_books and the offline evaluation rule,
together with the frozen H032 pins (qresearch.os1: specification, X807 host, qr_os1, qr_ucr, SEC objects); all
committed BEFORE R1 (E033-01; E033-02 only after a documented infrastructure failure). R2 (E033-03 / E033-04) only if R1
is valid and passes O1-O7 and O9. tests/test_os1_r.py checks these pins."""
from __future__ import annotations

import hashlib

from . import config, os1

DECISION = "D282"
PROTOCOL = "research/os/H032_R_protocol.md"
PROTOCOL_SHA256 = "dbe40049f3be7b0b562e95901050ffacde614f64945af2e97bf0b58b7c8d05fe"
HOST = "strategies/S033_h032_os1/main.py"
TRADE = "src/qresearch/lean/qr_os1_trade.py"
BOOKS = "src/qresearch/lean/qr_os1_books.py"
EVAL_RULES = "research/os/OS1_R_eval.py"
CODE_SHA256 = {
    HOST: "7c654a335c4c13e3c668f2504ebc5a7b0b073fc7f3faf0943e5d8d80d3f38728",
    TRADE: "e1c1a898045363964065b8bbf4e44a9e0e3c5257f3a9f166c7662f554145c967",
    BOOKS: "788a4d410f3e8a98b56fe869ab2c84c69d5c91e14017fc12ecb46902bb5aa8a4",
    EVAL_RULES: "0e157044d0ca3d2f35fcaababa3b2b8183d701a872ab769eca673d218d251184",
}
START_REVIEW = "2012-07-31"
WARMUP_FROM = "2009-05-01"
R1, R1_RETRY, R2, R2_RETRY = "E033-01", "E033-02", "E033-03", "E033-04"
SLIPPAGE_BPS = {R1: 10, R1_RETRY: 10, R2: 20, R2_RETRY: 20}
PROGRAMME = "OS"
CYCLE = "H032"


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def run_params() -> dict:
    code = {k.split("/")[-1]: v for k, v in CODE_SHA256.items() if k != EVAL_RULES}
    code["main.py"] = CODE_SHA256[HOST]
    code["qr_x807.py"] = os1.CODE_SHA256[os1.HOST]
    code["qr_os1.py"] = os1.CODE_SHA256[os1.MODULE]
    code["qr_ucr.py"] = os1.CODE_SHA256[os1.rr_ucr.MODULE]
    return dict(h032_spec_sha256=os1.SPEC_SHA256, h032_r_protocol_sha256=PROTOCOL_SHA256,
                h032_r_code_sha256=dict(sorted(code.items())), start_review=START_REVIEW,
                ucr_object_key=os1.UCR_OBJECT_KEY, ucr_reference_sha256=os1.UCR_REFERENCE_SHA256,
                os1_object_key=os1.OS1_OBJECT_KEY, os1_reference_sha256=os1.OS1_REFERENCE_SHA256)
