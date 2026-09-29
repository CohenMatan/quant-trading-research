"""S007 (H007) pure signal functions. Windows end at the completed signal bar T (last element)."""
from qr_indicators import atr, bandwidth, sma, stdev


def bandwidth_series(closes, n=20, k=2.0):
    """Bandwidth of every bar that has n closes behind it (oldest first)."""
    c = list(closes)
    return [bandwidth(c[: i + 1], n, k) for i in range(n - 1, len(c))]


def contracted_bw(bw_history, pct, lookback=250):
    """Setup on T-1: bandwidth(T-1) is in the lowest `pct` of its own previous `lookback` values.
    bw_history ends at T; the T value itself is not used for the setup."""
    b = [x for x in bw_history if x is not None]
    if len(b) < lookback + 2:
        return None
    last, prev = b[-2], b[-lookback - 2:-2]
    rank = sum(1 for x in prev if x < last) / lookback
    return rank if rank <= pct else None


def contracted_atr(highs, lows, closes, max_ratio):
    """Alternative setup on T-1: ATR10 / ATR100 over bars ending T-1 is at most max_ratio."""
    h, l, c = list(highs)[:-1], list(lows)[:-1], list(closes)[:-1]
    a10, a100 = atr(h, l, c, 10), atr(h, l, c, 100)
    if not a10 or not a100:
        return None
    r = a10 / a100
    return r if r <= max_ratio else None


def expansion(highs, lows, closes, volumes, band_k=2.0, tr_mult=1.5, vol_mult=1.2, trend_len=200,
              use_trend=True):
    """Trigger on T: close above the upper band (SMA20 + band_k x SD20 of closes ending T), true range
    of T >= tr_mult x ATR20 (bars ending T-1), volume_T >= vol_mult x mean volume of T-50..T-1, and
    (if use_trend) close above SMA(trend_len)."""
    h, l, c, v = list(highs), list(lows), list(closes), list(volumes)
    if len(c) < max(trend_len, 52, 22):
        return False
    m, sd = sma(c, 20), stdev(c, 20)
    if m is None or sd is None or not c[-1] > m + band_k * sd:
        return False
    a_prev = atr(h[:-1], l[:-1], c[:-1], 20)
    tr_t = max(h[-1], c[-2]) - min(l[-1], c[-2])
    if not a_prev or tr_t < tr_mult * a_prev:
        return False
    avg_v = sum(v[-51:-1]) / 50
    if not (avg_v > 0 and v[-1] >= vol_mult * avg_v):
        return False
    if use_trend:
        t = sma(c, trend_len)
        if t is None or not c[-1] > t:
            return False
    return True


def exit_signal(closes, sessions_held, min_hold=5, time_stop=40):
    """Exit when the close falls below SMA20 (from the min_hold-th session on), or the time stop."""
    if sessions_held is None:
        return False
    if sessions_held >= time_stop:
        return True
    m = sma(closes, 20)
    return sessions_held >= min_hold and m is not None and list(closes)[-1] < m
