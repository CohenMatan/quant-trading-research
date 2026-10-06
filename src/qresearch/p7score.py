"""Phase 7 Multi-Factor Conviction Score v1: pins of the pre-registration (research/phase7/P7_score_spec.md, P7-CP2,
owner D169) and of the score code. FROZEN CANDIDATE v1, written before any historical score, return or threshold.
tests/test_p7_score_spec.py checks the hashes and that the code carries exactly these constants. Any change after a
historical score exists needs a recorded owner decision taken before any return is seen.
"""
from __future__ import annotations

import hashlib

from . import config

SPEC = "research/phase7/P7_score_spec.md"
SPEC_VERSION = 1
SPEC_SHA256 = "7d3ae5df2fb5ecfaf8338e1a1d43f01c7a3060e73e33bf1007560981234eed9b"
CODE_SHA256 = {
    "src/qresearch/lean/qr_p7_score.py": "84b67317023683da5d6f35c640e6b8adcaf42a9b9e106c0ab8183a26edb91572",
    "src/qresearch/lean/qr_p7.py": "86abb2b2e9284f1dfaa89bddb6a57d354d399b3069822be8b8efb80dcb04bb5a",
}
OWNER_DECISION = "D169"
DEVELOPMENT_WINDOW = ("2011-01", "2017-12")
POINTS = dict(trend=15, momentum=15, risk=10, profitability=15, cash_conversion=10, balance_sheet=10, growth=10,
              sector=15)
CONSTANTS = dict(SMA_SHORT=50, SMA_LONG=200, SLOPE_LAG=21, MOM_LOOKBACK=252, MOM_SKIP=21, VOL_WINDOW=60,
                 YOY_MONTHS=12, LARGE_DISTRIBUTION=0.10, N_BANDS=5, MIN_SECTOR_GROUP=10, SECTOR_BREADTH_BAND=0.10,
                 REGIME_BREADTH_HIGH=0.60, REGIME_BREADTH_LOW=0.40, STALE_PRICE_SESSIONS=5, MIN_HISTORY=253)
HARD_DQ = ("H1_sector_not_scorable", "H2_fundamentals_missing_or_stale", "H3_insufficient_history",
           "H4_corporate_event_contamination", "H5_stale_price", "H6_broken_long_term_trend",
           "H7_financial_impairment")
DEFERRED = ("EntryThreshold", "ExitThreshold", "ReplacementBuffer", "MaxPositions", "RegimeExposureCeilings")


def sha256(rel: str) -> str:
    return hashlib.sha256((config.REPO_ROOT / rel).read_bytes()).hexdigest()
