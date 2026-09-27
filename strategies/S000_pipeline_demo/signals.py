# S000 signals — pure, deterministic functions shared by the LEAN algorithm and the local tests.
# No LEAN imports: this module must run anywhere.
from __future__ import annotations

from typing import Mapping, Sequence


def trailing_return(closes: Sequence[float], lookback: int) -> float | None:
    """Return over the last `lookback` bars, using only the given (past) closes; None if too short."""
    if lookback < 1 or len(closes) < lookback + 1:
        return None
    a, b = float(closes[-lookback - 1]), float(closes[-1])
    if a <= 0 or b <= 0:
        return None
    return b / a - 1.0


def select_entries(windows: Mapping[str, Sequence[float]], liquidity: Mapping[str, float],
                   exclude: set[str], n_slots: int, lookback: int = 5, pool: int = 300) -> list[str]:
    """Pick up to n_slots names with the lowest trailing return among the `pool` most liquid ones.

    windows:   key -> adjusted closes up to and including the signal day (oldest first)
    liquidity: key -> average dollar volume (point in time)
    exclude:   keys already held or pending
    Ties are broken by key so the result is deterministic.
    """
    if n_slots <= 0:
        return []
    liquid = sorted((k for k in windows if k in liquidity), key=lambda k: (-liquidity[k], k))[:pool]
    scored = []
    for k in liquid:
        if k in exclude:
            continue
        r = trailing_return(windows[k], lookback)
        if r is not None:
            scored.append((r, k))
    scored.sort()
    return [k for _, k in scored[:n_slots]]
