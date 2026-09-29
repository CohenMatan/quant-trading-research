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


def exit_signal(highs, lows, closes, sessions_held, k, time_stop):
    """Chandelier stop: close_T < highest close since entry - k x ATR20; or the time stop."""
    if sessions_held is None:
        return False
    if sessions_held >= time_stop:
        return True
    c = list(closes)
    since = c[-(sessions_held + 1):] if sessions_held + 1 <= len(c) else c
    a = atr(highs, lows, c, 20)
    return a is not None and c[-1] < max(since) - k * a
