"""SYS-1 single-account development experiment (owner D251 / D252): pins of the frozen protocol
(research/longhorizon/sys1/SYS1_protocol.md), the account engine qr_sys1, the host S032 (subclass of the pinned H028
host S030, uploaded as qr_s030), the offline canary / evaluation rules, the frozen E030-05 references the canary must
reproduce and the run provenance.

Written and committed BEFORE any SYS-1 run. CANARY_RESULT_SHA256 is set from the committed assessment of the canary
E032-01, only if every mandatory check passes, before the ONE evaluation E032-02. tests/test_sys1*.py check these pins.
The H026 / H027 / H028 pins (qresearch.p11h026 / p12h027 / p13h028) are never modified. H028 remains REJECTED.
"""
from __future__ import annotations

import hashlib

from . import config, p13h028

DECISION = "D252"
DESIGN_DECISION = "D251"
SYSTEM = "SYS-1"
PROTOCOL = "research/longhorizon/sys1/SYS1_protocol.md"
PROTOCOL_SHA256 = "2a16618fdba23ab96a653704a29d1bbf0ea90b8cb6a132758a6a54336be05639"
ENGINE = "src/qresearch/lean/qr_sys1.py"
HOST = "strategies/S032_sys1_account/main.py"
CANARY_RULES = "research/longhorizon/sys1/SYS1_canary.py"
EVAL_RULES = "research/longhorizon/sys1/SYS1_eval.py"
CODE_SHA256 = {
    ENGINE: "ce27484afb48cf5fc50aa55ff7e19a575cbd668e222d42a75a466bf5009a5576",
    HOST: "1b7fb3b72fe7fd8d751a091340e1aaacdec4b87218cbdb38c3c8c622634552ce",
    CANARY_RULES: "0abf3439be28d6676c31c207e674262cff729b9778e0d658b73ecaa5a4750316",
    EVAL_RULES: "2aff3ebf430fe48fc86a188f5a8627dcdbecbf03d45a9d1c3a954c6ddb9770dc",
}
PARENT_HOST = p13h028.HOST                              # S030, uploaded byte-identical as qr_s030.py

# frozen E030-05 references (research/phase13/cp1/P13_CP1_result.json), reproduced exactly by canary C1-C3
FROZEN_H028 = dict(wealth=328294.90847351257, commissions=5789.0, buys=416, sells=411, slippage=8330.209577810972)
FROZEN_SPY_WEALTH = 262325.455801514
FROZEN_SPY_WEALTH_200K = 524676.2761604529                # E030-05 diagnostic capital_200k (SPY at $200,000)
FROZEN_LV15_WEALTH = 220156.03484878788
FROZEN_RESULT = p13h028.RESULT

# account (owner OD-1 .. OD-5)
CAPITAL = 200_000.0
SLEEVE = 0.5
MIN_TICKET = 5_000.0
ETF_IDS = {"splv": "SPLV UWBCA8CFMB1H", "usmv": "USMV V0WRDXSSH205"}    # E970 security-master identifiers
GATING_ETF = "splv"
CLASSIFICATIONS = ("NOT EXECUTABLE", "NOT SUPPORTED", "NOT FALSIFIED — DEVELOPMENT-CONSISTENT")

# runs (owner OD-7): one canary, one evaluation only after every mandatory canary check passes, at most two documented
# infrastructure retries in total (E032-03, E032-04, in that order, identical settings to the run they retry)
CANARY = "E032-01"
EVAL = "E032-02"
RETRIES = ("E032-03", "E032-04")
PROGRAMME = "LH"
CYCLE = "SYS1"

CANARY_RESULT = "research/longhorizon/sys1/SYS1_canary_E032-01.json"
CANARY_RESULT_SHA256 = None                         # set only after the canary passes, before E032-02
RESULT = "research/longhorizon/sys1/SYS1_result.json"

PERIODS = dict(development="2015-01 .. 2021-12 decisions (2011-2021 data): FULLY SEEN; development evidence only",
               holdout="2022-01-01 .. 2026-08-31: programme-wide final Holdout, SEALED (nothing read)")


def file_sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()


def run_params(mode: str) -> dict:
    """The S032 parameters: the E030-05 real-mode parameters (panel equivalence gate) + the SYS-1 pins."""
    import json
    base = json.loads((config.REPO_ROOT / "experiments" / p13h028.REAL / "config.json").read_text())["params"]
    p = dict(base)
    p.update(sys1_mode=mode, sys1_protocol_sha256=PROTOCOL_SHA256, sys1_code_sha256=CODE_SHA256[ENGINE],
             frozen_h028=dict(FROZEN_H028), frozen_spy_wealth=FROZEN_SPY_WEALTH,
             frozen_spy_wealth_200k=FROZEN_SPY_WEALTH_200K, frozen_lv15_wealth=FROZEN_LV15_WEALTH)
    if mode == "eval":
        p["canary_result_sha256"] = CANARY_RESULT_SHA256
    return p
