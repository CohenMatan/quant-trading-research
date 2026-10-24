"""H006X exit-policy comparison (owner D304; research/tt/h006_exit/H006X_spec.md): pins of the frozen specification,
the S006 code and the offline evaluation rule, all committed BEFORE the three runs (Control A E006-04, Experiment B
E006-05, SPY E900-08; one documented infrastructure retry each: E006-06 / E006-07 / E900-09). tests/test_h006x_pins.py
checks these pins."""
from __future__ import annotations

import hashlib

from . import config

DECISION = "D304"
PROGRAMME = "TT"
CYCLE = "H006X"
SPEC = "research/tt/h006_exit/H006X_spec.md"
EVAL_RULES = "research/tt/h006_exit/H006X_eval.py"
MAIN = "strategies/S006_breakout/main.py"
SIGNALS = "strategies/S006_breakout/signals.py"
SPEC_SHA256 = "ae016962e71686aacc383b4da7336fe166ecc9c14b68eb17bbcba5192d42fb5e"
CODE_SHA256 = {
    MAIN: "da3e810179df7288892a2b8210c85471b3659beed89cac5aaa2be7d5f6efd65e",
    SIGNALS: "91ada940e221f3aa558e29223ccd92f4cbb83f3c16935e21cf86f96487c46a0f",
    EVAL_RULES: "3b60c2c70a7b15fe40cdf7be815698e1029f51a2cd247f30d18ea4d42bbc670c",
}
START, END = "2010-01-04", "2021-12-31"
A, B, SPY = "E006-04", "E006-05", "E900-08"
RETRY = {A: "E006-06", B: "E006-07", SPY: "E900-09"}
BASE = dict(n=55, vol_mult=1.5, use_volume=True, k=3.0, slots=10)
TIME_STOP = {A: 60, B: None}


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def arm(eid: str) -> str:
    """The arm an experiment id (or its retry) belongs to."""
    for k, v in RETRY.items():
        if eid in (k, v):
            return k
    raise KeyError(eid)


def run_params(eid: str) -> dict:
    a = arm(eid)
    if a == SPY:
        return dict(weight=0.98)
    return dict(BASE, time_stop=TIME_STOP[a], h006x_spec_sha256=SPEC_SHA256,
                h006x_code_sha256={"main.py": CODE_SHA256[MAIN], "signals.py": CODE_SHA256[SIGNALS]})
