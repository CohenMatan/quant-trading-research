"""S012 (H012) pure helpers: no QuantConnect imports, unit-tested offline. Every function sees only
the values passed to it; callers pass windows that end at the completed bar T (the decision close)."""
import math

QUARTER_MONTHS = (1, 4, 7, 10)


def realized_vol(closes, n):
    """RV(n): sample standard deviation (ddof 1) of the last n daily simple returns ending at the last
    close, x sqrt(252). None if fewer than n + 1 closes."""
    xs = list(closes)
    if n < 2 or len(xs) < n + 1:
        return None
    w = xs[-(n + 1):]
    r = [w[i] / w[i - 1] - 1.0 for i in range(1, n + 1)]
    m = sum(r) / n
    return math.sqrt(sum((x - m) ** 2 for x in r) / (n - 1)) * math.sqrt(252)


def exposure_target(closes, short, long=252):
    """e = min(1, RV(long) / RV(short)); None if either is unavailable or RV(short) is zero."""
    rl, rs = realized_vol(closes, long), realized_vol(closes, short)
    if rl is None or rs is None or rs <= 0:
        return None
    return min(1.0, rl / rs)


def band_exceeded(target, current, band):
    """Rescale only if the new exposure differs from the applied one by more than the band."""
    return abs(target - current) > band


def control_b(previous_targets, k=12):
    """Control B: mean of the variation's targets on the previous k rescale dates (strictly before
    today); None if there are none."""
    w = list(previous_targets)[-k:]
    return sum(w) / len(w) if w else None


def largest(caps, n):
    """The n largest ids by market cap; ties by id (ascending)."""
    return [k for k, _ in sorted(caps.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


def is_reconstitution(prev_month, month):
    """First session of January, April, July or October; also the first close of the backtest."""
    return prev_month is None or (month in QUARTER_MONTHS and month != prev_month)


def is_rescale_day(today, next_session, cadence):
    """Last session of the month (monthly) or of the ISO week (weekly), given the next session's date."""
    if cadence == "monthly":
        return (next_session.year, next_session.month) != (today.year, today.month)
    if cadence == "weekly":
        return next_session.isocalendar()[:2] != today.isocalendar()[:2]
    raise ValueError(f"unknown cadence {cadence!r}")


def history_targets(dates, closes, short, cadence, next_after_last, long=252):
    """Targets on the rescale dates inside a price history (oldest first), for Control B's first year:
    the same rule as live, each target computed only from closes up to its own date."""
    out = []
    for i, d in enumerate(dates):
        nxt = dates[i + 1] if i + 1 < len(dates) else next_after_last
        if is_rescale_day(d, nxt, cadence):
            e = exposure_target(closes[:i + 1], short, long)
            if e is not None:
                out.append((d, e))
    return out
