"""H032 / OS-1 revised (owner D278): pins of the frozen specification and evaluation protocol (research/os/H032_spec.md),
the X807 canary host, the qr_os1 and qr_ucr modules, the extension-object builder, the pre-registered comparative
verification, the offline canary evaluation rule and the two public SEC objects, all committed BEFORE the one authorised
canary run (E807-01; E807-02 only as the single retry after a documented infrastructure failure). No strategy return,
R1 / R2 run or Holdout access is authorised. tests/test_os1_canary.py checks these pins."""
from __future__ import annotations

import hashlib

from . import config, rr_ucr

DECISION = "D278"
SPEC = "research/os/H032_spec.md"
SPEC_SHA256 = "979af2e3944cfc75af617d959ed2e4354fe9f79e7cf48f6d608627cbc8db66aa"
HOST = "strategies/X807_os1_canary/main.py"
MODULE = "src/qresearch/lean/qr_os1.py"
BUILDER = "research/os/build_os1_sec.py"
VERIFY = "research/os/os1_verify_comparatives.py"
EVAL_RULES = "research/os/OS1_eval.py"
CODE_SHA256 = {
    HOST: "594688322074e4253d64b0e44bf98c2d3d80d6fc48ecfb8d3843375c8a9ace18",
    MODULE: "07d6b03c92ad3b4741fcb32e3e3029bcfbbcc0fba091f3ca45f3de8c6dc9592a",
    BUILDER: "d088c6bacf01a4b89d67b9e775070c9ca75f40fdb066aa907a9481f30edd7e58",
    VERIFY: "f859e9c73147c4f0d1abb4e973ca1b2345ffc4c8f6daae1ea8933c99e7b8eba9",
    EVAL_RULES: "c8316799f01893d9a47b36d0efa439be8ecc5b4a195c2611b8d07376f37d3ffa",
    rr_ucr.MODULE: rr_ucr.CODE_SHA256[rr_ucr.MODULE],
}
OS1_MANIFEST = "research/os/os1_sec_v1_manifest.json"
OS1_REFERENCE_SHA256 = "32bb0a666503e333ed20001074da687a12c557f28c85fa4b090b8b1983645b17"
OS1_OBJECT_KEY = "rr/os1_sec_v1.json"
UCR_REFERENCE_SHA256 = rr_ucr.UCR_REFERENCE_SHA256
UCR_OBJECT_KEY = rr_ucr.UCR_OBJECT_KEY
RUN = "E807-01"
RETRY = "E807-02"
PROGRAMME = "OS"
CYCLE = "H032"


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def run_params() -> dict:
    return dict(h032_spec_sha256=SPEC_SHA256,
                h032_code_sha256={k.split("/")[-1]: v for k, v in CODE_SHA256.items()
                                  if k in (HOST, MODULE, rr_ucr.MODULE)},
                ucr_object_key=UCR_OBJECT_KEY, ucr_reference_sha256=UCR_REFERENCE_SHA256,
                os1_object_key=OS1_OBJECT_KEY, os1_reference_sha256=OS1_REFERENCE_SHA256)
