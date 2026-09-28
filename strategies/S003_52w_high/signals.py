# S003 signals (H003) — proximity to the 52-week high. No LEAN imports.
from __future__ import annotations

from typing import Mapping, Sequence


def proximity(c: Sequence[float], n: int = 252) -> float | None:
    if len(c) < n:
        return None
    hi = max(list(c)[-n:])
    return c[-1] / hi if hi > 0 else None


def mom(c: Sequence[float], lookback: int = 252, skip: int = 21) -> float | None:
    if len(c) < lookback + 1 or c[-lookback - 1] <= 0:
        return None
    return c[-skip - 1] / c[-lookback - 1] - 1.0


def top_by_proximity(windows: Mapping[str, Sequence[float]], n: int, require_positive_mom: bool) -> list[str]:
    scored = []
    for k, c in windows.items():
        pr = proximity(c)
        if pr is None:
            continue
        if require_positive_mom:
            m = mom(c)
            if m is None or m <= 0:
                continue
        scored.append((-pr, k))
    scored.sort()
    return [k for _, k in scored[:n]]
