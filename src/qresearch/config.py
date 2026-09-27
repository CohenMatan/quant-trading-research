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

# Data split (D004, approved at CP1).
SPLITS: dict[str, tuple[date, date]] = {
    "IS": (date(1999, 1, 4), date(2014, 12, 31)),
    "VAL": (date(2015, 1, 1), date(2021, 12, 31)),
    "HOLDOUT": (date(2022, 1, 1), date(2026, 8, 31)),
}
LAST_UNLOCKED_DATE = SPLITS["VAL"][1]
# Split labels that are not a single segment. "FULL" = IS+VAL; used only for benchmarks and infrastructure runs.
COMPOSITE_SPLITS: dict[str, tuple[date, date]] = {
    "FULL": (SPLITS["IS"][0], SPLITS["VAL"][1]),
}

# Universe (D003, D010, approved at CP1).
MIN_MARKET_CAP = 2_000_000_000.0
DEFAULT_CASH = 100_000.0

# Experiment kinds recorded in the registry.
EXPERIMENT_KINDS = ("research", "benchmark", "infrastructure", "demo")
