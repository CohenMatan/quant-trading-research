"""S013 (H013) pure helpers: no QuantConnect imports, unit-tested offline. Windows end at the
completed bar T (the decision close)."""
import math

WINDOW = 21


def daily_returns(closes, n=WINDOW):
    """The last n daily simple returns ending at the last close; None if fewer than n + 1 closes."""
    xs = list(closes)
    if len(xs) < n + 1:
        return None
    w = xs[-(n + 1):]
    return [w[i] / w[i - 1] - 1.0 for i in range(1, n + 1)]


def lottery_stat(closes, stat, n=WINDOW):
    """MAX = the largest daily return in the window; MAX5 = the mean of its 5 largest."""
    r = daily_returns(closes, n)
    if r is None:
        return None
    if stat == "max":
        return max(r)
    if stat == "max5":
        top = sorted(r, reverse=True)[:5]
        return sum(top) / len(top)
    raise ValueError(f"unknown statistic {stat!r}")


def excluded_ids(windows, q, stat, n=WINDOW):
    """Ids in the top fraction q of the statistic among ids with at least n returns: the floor(q x count)
    highest values, ties by id (ascending). Ids with fewer returns are never excluded."""
    vals = {}
    for k, w in windows.items():
        v = lottery_stat(w, stat, n)
        if v is not None:
            vals[k] = v
    k = int(math.floor(q * len(vals) + 1e-9))
    return set(sorted(vals, key=lambda s: (-vals[s], s))[:k])


def allowed_order(null_order, excluded):
    """The null's random order with excluded ids skipped (paired sampling: common random numbers)."""
    return [s for s in null_order if s not in excluded]
