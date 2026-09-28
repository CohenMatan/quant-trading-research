"""Fixed project constants. Changing anything here that affects results needs a DECISIONS.md entry."""
from __future__ import annotations

from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
STRATEGIES_DIR = REPO_ROOT / "strategies"
INDEX_CSV = EXPERIMENTS_DIR / "INDEX.csv"
HOLDOUT_UNLOCK_FILE = REPO_ROOT / "HOLDOUT_UNLOCK.md"
LEAN_HARNESS = Path(__file__).resolve().parent / "lean" / "qr_harness.py"

# Data split schemes. Every experiment config names its scheme ("split_scheme"); configs without
# one belong to the CP1 scheme and remain valid only as history (and for --reproduce).
#
# "2010" (D034, proposed at the CP2 amendment; owner decision D033 to use MarketCap >= $2B from
# 2010 only): the official research period starts 2010-01-04. The holdout is unchanged.
CURRENT_SCHEME = "2010"
OFFICIAL_START = date(2010, 1, 4)
SCHEMES: dict[str, dict[str, tuple[date, date]]] = {
    "cp1": {  # D004, approved at CP1, superseded by D033/D034
        "IS": (date(1999, 1, 4), date(2014, 12, 31)),
        "VAL": (date(2015, 1, 1), date(2021, 12, 31)),
        "HOLDOUT": (date(2022, 1, 1), date(2026, 8, 31)),
        "FULL": (date(1999, 1, 4), date(2021, 12, 31)),
    },
    "2010": {
        "IS": (date(2010, 1, 4), date(2017, 12, 31)),
        "VAL": (date(2018, 1, 1), date(2021, 12, 31)),
        "HOLDOUT": (date(2022, 1, 1), date(2026, 8, 31)),
        # composite labels
        "FULL": (date(2010, 1, 4), date(2021, 12, 31)),     # benchmarks / infrastructure only
        "WF": (date(2010, 1, 4), date(2021, 12, 31)),       # walk-forward (research), see RESEARCH_PLAN §3
        "STRESS": (date(1999, 1, 4), date(2009, 12, 31)),   # optional finalist stress test, never selection
    },
}
SPLITS = {k: v for k, v in SCHEMES[CURRENT_SCHEME].items() if k in ("IS", "VAL", "HOLDOUT")}
COMPOSITE_SPLITS = {k: v for k, v in SCHEMES[CURRENT_SCHEME].items() if k not in SPLITS}
# The holdout lock is identical in both schemes.
LAST_UNLOCKED_DATE = date(2021, 12, 31)

# Universe (D003, D010, approved at CP1).
MIN_MARKET_CAP = 2_000_000_000.0
DEFAULT_CASH = 100_000.0

# Costs (D039, owner's actual brokerage): $7 per executed order, buy or sell; slippage is separate.
COMMISSION_MODEL = "fixed_per_order"
COMMISSION_PER_ORDER = 7.0

# Experiment kinds recorded in the registry.
# "stress" = optional 1999-2009 stress test of a finalist on an imperfect universe (D035): never counted
# as a trial, never used for optimisation, parameter selection or promotion.
# "sizing" = account-size re-test of a finalist (D044): same logic and settings, different cash; not a trial.
EXPERIMENT_KINDS = ("research", "benchmark", "infrastructure", "demo", "stress", "sizing")

# Approved portfolio rules for research (D025/D041/D044).
RESEARCH_PORTFOLIO = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 5000,
                      "max_positions": 15}
RESEARCH_CASH = 100_000.0
