# S004 signals (H004) — pullbacks within momentum leaders. No LEAN imports.
from __future__ import annotations

from typing import Mapping, Sequence


def ret_between(c: Sequence[float], start_back: int, end_back: int) -> float | None:
    """Return from c[-start_back-1] to c[-end_back-1] (both measured back from the last bar)."""
    if len(c) < start_back + 1 or c[-start_back - 1] <= 0:
        return None
    return c[-end_back - 1] / c[-start_back - 1] - 1.0


def sma(c: Sequence[float], n: int) -> float | None:
    if len(c) < n:
        return None
    return sum(list(c)[-n:]) / n


def leaders(windows: Mapping[str, Sequence[float]], top_frac: float) -> set[str]:
    """Top `top_frac` of names by the 126-day return ending 5 bars ago (t-131 -> t-5)."""
    scored = sorted((-r, k) for k, c in windows.items() if (r := ret_between(c, 131, 5)) is not None)
    n = int(len(scored) * top_frac)
    return {k for _, k in scored[:n]}


def pullback_entries(windows: Mapping[str, Sequence[float]], lead: set[str], drop: float,
                     exclude: set[str], n: int) -> list[str]:
    """Leaders whose 5-day return <= -drop; deepest pullback first; ties by key."""
    scored = []
    for k in lead:
        if k in exclude:
            continue
        r = ret_between(windows[k], 5, 0)
        if r is not None and r <= -drop:
            scored.append((r, k))
    scored.sort()
    return [k for _, k in scored[:max(n, 0)]]
