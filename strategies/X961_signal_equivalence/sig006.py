"""S006 (H006) pure signal functions. Every window ends at the completed signal bar T (last element);
nothing after T is ever passed in. Orders from these signals execute at the T+1 open or later."""
from qr_indicators import atr, sma


def breakout_strength(highs, lows, closes, volumes, n, vol_mult, use_volume=True, trend_len=200):
    """Breakout on T: close_T above the highest high of T-N..T-1, volume_T >= vol_mult x the mean
    volume of T-50..T-1 (if use_volume), close_T above SMA(trend_len). Returns the breakout size in
    ATR20 units (ATR over the bars ending T) or None if there is no signal."""
    h, l, c, v = list(highs), list(lows), list(closes), list(volumes)
    need = max(n + 1, trend_len, 51, 22)
    if len(c) < need or len(h) < need or len(l) < need or len(v) < need:
        return None
    prior_high = max(h[-n - 1:-1])
    if not c[-1] > prior_high:
        return None
    if use_volume:
        avg_v = sum(v[-51:-1]) / 50
        if not (avg_v > 0 and v[-1] >= vol_mult * avg_v):
            return None
    trend = sma(c, trend_len)
    if trend is None or not c[-1] > trend:
        return None
    a = atr(h, l, c, 20)
    if not a or a <= 0:
        return None
    return (c[-1] - prior_high) / a


def peak_since_entry(closes, sessions_held, carried=None):
    """Highest close since entry (entry day included). Within the kept window (sessions_held + 1 <= len(closes))
    it is read from the window. Beyond it (D304: no time stop) it is carried: max(carried, close_T), where `carried`
    is the previous close's peak in today's price units; without one, the whole window (the original behaviour)."""
    c = list(closes)
    if sessions_held + 1 <= len(c):
        return max(c[-(sessions_held + 1):])
    return max(carried, c[-1]) if carried is not None else max(c)


def carried_peak(stored, closes, last_bar, window_full):
    """The previous close's highest-close-since-entry in today's price units. `stored` = (peak / close at storage,
    date of that bar) or None. One bar appended since storage -> closes[-2] is that close; none -> closes[-1].
    Only past a full window (otherwise None: the original whole-window behaviour)."""
    if stored is None or not window_full:
        return None
    ratio, when = stored
    return ratio * (closes[-1] if when == last_bar else closes[-2])


def exit_signal(highs, lows, closes, sessions_held, k, time_stop, carried=None):
    """Chandelier stop: close_T < highest close since entry - k x ATR20; or the time stop (None = no time stop,
    D304 Experiment B)."""
    if sessions_held is None:
        return False
    if time_stop is not None and sessions_held >= time_stop:
        return True
    c = list(closes)
    a = atr(highs, lows, c, 20)
    return a is not None and c[-1] < peak_since_entry(c, sessions_held, carried) - k * a
