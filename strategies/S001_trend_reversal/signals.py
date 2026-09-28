# S001 signals (H001) — pure functions of past adjusted closes (oldest first). No LEAN imports.
from __future__ import annotations

from typing import Sequence


def sma(c: Sequence[float], n: int) -> float | None:
    if n < 1 or len(c) < n:
        return None
    return sum(list(c)[-n:]) / n


def rsi(c: Sequence[float], n: int = 2) -> float | None:
    """Cutler RSI: simple averages of the last n up and down moves (deterministic, window-local)."""
    if len(c) < n + 1:
        return None
    x = list(c)[-(n + 1):]
    ups = sum(max(b - a, 0.0) for a, b in zip(x, x[1:]))
    downs = sum(max(a - b, 0.0) for a, b in zip(x, x[1:]))
    if downs == 0:
        return 100.0
    return 100.0 - 100.0 / (1.0 + ups / downs)


def ret(c: Sequence[float], k: int) -> float | None:
    if len(c) < k + 1 or c[-k - 1] <= 0:
        return None
    return c[-1] / c[-k - 1] - 1.0


def entry_score(c: Sequence[float], p: dict) -> float | None:
    """Oversold score (lower = more oversold) if the entry rule holds, else None."""
    if len(c) < 201:
        return None
    if p.get("entry") == "ret3":
        r = ret(c, 3)
        if r is None or r > float(p["ret3_max"]):
            return None
        score = r
    else:
        r = rsi(c, 2)
        if r is None or r >= float(p["rsi_max"]):
            return None
        score = r
    s200 = sma(c, 200)
    if s200 is None or c[-1] <= s200:
        return None
    return score


def exit_signal(c: Sequence[float], age: int, p: dict) -> bool:
    if age >= int(p["max_hold"]):
        return True
    if p.get("exit") == "time":
        return False
    s5 = sma(c, 5)
    return s5 is not None and c[-1] > s5


def rank_entries(scores: dict, n: int) -> list:
    """Most oversold first; ties by key (deterministic)."""
    return [k for _, k in sorted((v, k) for k, v in scores.items())[:max(n, 0)]]
