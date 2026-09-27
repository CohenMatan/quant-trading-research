"""Holdout lock: no run may touch data after the validation end unless HOLDOUT_UNLOCK.md exists.

HOLDOUT_UNLOCK.md is created only after written owner approval at CP5. Its existence is the single
switch; the LEAN harness enforces the same rule a second time inside the cloud backtest.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from . import config


class HoldoutLockedError(RuntimeError):
    pass


def holdout_unlocked(unlock_file: Path | None = None) -> bool:
    return (unlock_file or config.HOLDOUT_UNLOCK_FILE).is_file()


def check_dates(start: date, end: date, unlock_file: Path | None = None) -> None:
    """Raise HoldoutLockedError if [start, end] reaches past the last unlocked date while locked."""
    if start > end:
        raise ValueError(f"start {start} is after end {end}")
    if end > config.LAST_UNLOCKED_DATE and not holdout_unlocked(unlock_file):
        raise HoldoutLockedError(
            f"End date {end} is after {config.LAST_UNLOCKED_DATE}: the holdout is locked. "
            "It can only be unlocked by owner approval at CP5 (HOLDOUT_UNLOCK.md)."
        )
