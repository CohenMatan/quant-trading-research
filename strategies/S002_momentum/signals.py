# S002 signals (H002) — momentum ranking on past adjusted closes. No LEAN imports.
from __future__ import annotations

from typing import Mapping, Sequence


def mom(c: Sequence[float], lookback: int, skip: int) -> float | None:
    """Return from t-lookback to t-skip (skip the most recent `skip` bars)."""
    if len(c) < lookback + 1 or c[-lookback - 1] <= 0:
        return None
    return c[-skip - 1] / c[-lookback - 1] - 1.0


def sma(c: Sequence[float], n: int) -> float | None:
    if len(c) < n:
        return None
    return sum(list(c)[-n:]) / n


def top_by_momentum(windows: Mapping[str, Sequence[float]], lookback: int, skip: int, n: int) -> list[str]:
    scored = []
    for k, c in windows.items():
        m = mom(c, lookback, skip)
        if m is not None:
            scored.append((-m, k))
    scored.sort()
    return [k for _, k in scored[:n]]


def is_rebalance_month(year: int, month: int, every: int) -> bool:
    """Monthly (every=1) or every `every` months starting from January."""
    return (month - 1) % every == 0
