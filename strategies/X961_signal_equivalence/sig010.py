"""S010 (H010) pure signal functions.

TIMING (owner requirement, 2026-09-29): the gap day is T. The signal needs T's open, T's close
(the "hold" condition close_T >= open_T), T's low and T's volume, so it can only be evaluated after
day T is complete (at the T close). The resulting order is a market-on-open order for T+1: nothing
executes on T. Windows passed in end at bar T; ATR% and the volume baseline use bars ending T-1."""
from qr_indicators import atr, sma


def gap_hold(opens, highs, lows, closes, volumes, min_gap=0.02, gap_atr=1.5, require_hold=True,
             vol_mult=2.0, trend_len=200, floor=0.9):
    """Gap-and-hold on T. Gap = open_T / close_{T-1} - 1 >= max(min_gap, gap_atr x ATR20%(T-1));
    close_T >= open_T (if require_hold); volume_T >= vol_mult x mean volume T-50..T-1;
    close_T > floor x SMA(trend_len). Returns (gap in ATR units, low_T) or None."""
    o, h, l, c, v = list(opens), list(highs), list(lows), list(closes), list(volumes)
    if len(c) < max(trend_len, 52, 22) or min(len(o), len(h), len(l), len(v)) < len(c):
        return None
    prev = c[-2]
    a = atr(h[:-1], l[:-1], c[:-1], 20)
    if prev <= 0 or not a:
        return None
    atr_pct = a / prev
    gap = o[-1] / prev - 1.0
    if gap < max(min_gap, gap_atr * atr_pct):
        return None
    if require_hold and c[-1] < o[-1]:
        return None
    avg_v = sum(v[-51:-1]) / 50
    if not (avg_v > 0 and v[-1] >= vol_mult * avg_v):
        return None
    t = sma(c, trend_len)
    if t is None or not c[-1] > floor * t:
        return None
    return gap / atr_pct, l[-1]


def gap_day_low(lows, sessions_held):
    """Low of the gap day, which is the session before the entry session: with the window ending at
    the current bar, the entry bar is at -(held+1) and the gap day at -(held+2)."""
    if sessions_held is None:
        return None
    lw = list(lows)
    i = sessions_held + 2
    return lw[-i] if i <= len(lw) else None


def exit_signal(closes, sessions_held, gap_day_low, hold):
    """Invalidation: close below the gap day's low; or the time stop after `hold` sessions."""
    if sessions_held is None:
        return False
    if sessions_held >= hold:
        return True
    return gap_day_low is not None and list(closes)[-1] < gap_day_low
