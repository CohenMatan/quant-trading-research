"""Shared pure indicator and slot-planning functions (C02). No QuantConnect imports, so the same
code runs in LEAN and in the local tests. Every function sees only the values passed to it; callers
pass windows that end at the completed bar T (the signal day)."""
from __future__ import annotations


def sma(xs, n):
    """Mean of the last n values, or None if fewer than n."""
    xs = list(xs)
    return sum(xs[-n:]) / n if n > 0 and len(xs) >= n else None


def stdev(xs, n):
    """Sample standard deviation of the last n values (None if fewer than n or n < 2)."""
    xs = list(xs)
    if n < 2 or len(xs) < n:
        return None
    w = xs[-n:]
    m = sum(w) / n
    return (sum((x - m) ** 2 for x in w) / (n - 1)) ** 0.5


def median(xs):
    w = sorted(xs)
    if not w:
        return None
    k = len(w) // 2
    return w[k] if len(w) % 2 else (w[k - 1] + w[k]) / 2.0


def true_ranges(highs, lows, closes):
    """True range of each bar from the second bar on: max(H, C_prev) - min(L, C_prev)."""
    h, l, c = list(highs), list(lows), list(closes)
    return [max(h[i], c[i - 1]) - min(l[i], c[i - 1]) for i in range(1, len(c))]


def atr(highs, lows, closes, n):
    """Simple average of the last n true ranges (None if not enough bars)."""
    tr = true_ranges(highs, lows, closes)
    return sum(tr[-n:]) / n if n > 0 and len(tr) >= n else None


def bandwidth(closes, n=20, k=2.0):
    """Bollinger bandwidth (upper - lower) / middle = 2k * sd / sma over the last n closes."""
    m, sd = sma(closes, n), stdev(closes, n)
    return None if m is None or sd is None or m <= 0 else 2.0 * k * sd / m


def pct_rank_last(xs, lookback):
    """Share of the previous `lookback` values strictly below the last value (0 = lowest)."""
    xs = [x for x in xs if x is not None]
    if len(xs) < lookback + 1:
        return None
    last, prev = xs[-1], xs[-lookback - 1:-1]
    return sum(1 for x in prev if x < last) / lookback


def plan_event_targets(held, exits, pending_buys, ranked_candidates, n_slots, weight):
    """Event-driven slot filling. held: symbols held now; exits: held symbols whose exit rule fired
    at this close; pending_buys: symbols with buy orders not yet filled; ranked_candidates: entry
    candidates, best first. Returns {symbol: target weight}: 0 for exits, `weight` for new entries
    filling free slots. Exiting positions still occupy their slot until the sale executes (D051)."""
    targets = {s: 0.0 for s in held if s in exits}
    busy = set(held) | set(pending_buys)
    free = n_slots - len(busy)
    for s in ranked_candidates:
        if free <= 0:
            break
        if s in busy:
            continue
        targets[s] = weight
        busy.add(s)
        free -= 1
    return targets
