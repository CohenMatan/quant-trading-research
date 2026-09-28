# S005 signals (H005) — low volatility. No LEAN imports.
from __future__ import annotations

import math
from typing import Mapping, Sequence


def vol(c: Sequence[float], n: int) -> float | None:
    """Standard deviation of the last n daily log returns."""
    if len(c) < n + 1:
        return None
    x = list(c)[-(n + 1):]
    if min(x) <= 0:
        return None
    r = [math.log(b / a) for a, b in zip(x, x[1:])]
    m = sum(r) / n
    return math.sqrt(sum((v - m) ** 2 for v in r) / (n - 1))


def mom(c: Sequence[float], lookback: int = 252, skip: int = 21) -> float | None:
    if len(c) < lookback + 1 or c[-lookback - 1] <= 0:
        return None
    return c[-skip - 1] / c[-lookback - 1] - 1.0


def lowest_vol(windows: Mapping[str, Sequence[float]], n_days: int, n: int, require_positive_mom: bool) -> list[str]:
    scored = []
    for k, c in windows.items():
        v = vol(c, n_days)
        if v is None:
            continue
        if require_positive_mom:
            m = mom(c)
            if m is None or m <= 0:
                continue
        scored.append((v, k))
    scored.sort()
    return [k for _, k in scored[:n]]
