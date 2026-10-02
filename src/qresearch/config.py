"""Fixed project constants. Changing anything here that affects results needs a DECISIONS.md entry."""
from __future__ import annotations

from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
STRATEGIES_DIR = REPO_ROOT / "strategies"
INDEX_CSV = EXPERIMENTS_DIR / "INDEX.csv"
WITHDRAWN_FILE = EXPERIMENTS_DIR / "WITHDRAWN.json"   # configs withdrawn before running (never run; D087)
HOLDOUT_UNLOCK_FILE = REPO_ROOT / "HOLDOUT_UNLOCK.md"
LEAN_HARNESS = Path(__file__).resolve().parent / "lean" / "qr_harness.py"

# Data split schemes. Every experiment config names its scheme ("split_scheme"); configs without
# one belong to the CP1 scheme and remain valid only as history (and for --reproduce).
#
# "2010" (D034, proposed at the CP2 amendment; owner decision D033 to use MarketCap >= $2B from
# 2010 only): the official research period starts 2010-01-04. The holdout is unchanged.
CURRENT_SCHEME = "2010"
OFFICIAL_START = date(2010, 1, 4)
WARMUP_EARLIEST = date(2008, 7, 1)   # D114: owner-approved history-only fundamentals warm-up (no performance)
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
        "DEV": (date(2010, 1, 4), date(2021, 12, 31)),      # Phase 2 development period (D094, research/phase2/P2_spec.md)
        "STRESS": (date(1999, 1, 4), date(2009, 12, 31)),   # optional finalist stress test, never selection
        "AUDIT": (date(1999, 1, 4), date(2021, 12, 31)),    # data audits (kind infrastructure) incl. warm-up
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

# Approved portfolio rules for research, by execution model. Configs name their model in
# "execution_model"; configs without one are history under "d044" (valid for reproduction only).
RESEARCH_PORTFOLIOS = {
    "d044": {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 5000, "max_positions": 15},
    # D051 (no borrowing): buys only from cash already held; 15% reserve for opening gaps
    "d051": {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 5000, "max_positions": 15,
             "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
}
# D115/D116: H016 only (owner 2026-10-02, option A): 20 positions, $4,000 minimum new position, D051 settled cash,
# 2% buffer and 15% gap reserve unchanged; the one-time top-up lives in qr_h016/S016. Earlier experiments untouched.
H016_PORTFOLIO = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 20,
                  "buy_funding": "settled_cash_only", "gap_reserve": 0.15}
CURRENT_EXECUTION_MODEL = "d051"
RESEARCH_PORTFOLIO = RESEARCH_PORTFOLIOS[CURRENT_EXECUTION_MODEL]
RESEARCH_CASH = 100_000.0
