"""S009 (H009) pure signal functions. Windows end at the completed signal bar T (last element).
ATR% and volume baselines are measured on bars ending T-1, so the shock day does not set its own bar."""
from qr_indicators import atr, median, sma


def volume_shock(highs, lows, closes, volumes, vol_mult=2.5, days=1, price_cap_atr=1.0,
                 base_len=50, floor=0.9):
    """Shock on T. days=1: volume_T >= vol_mult x median(volume T-50..T-1). days=5 (weekly
    formation): sum(volume T-4..T) >= vol_mult x median of the 50 rolling 5-day sums ending T-54..T-5.
    The price move over the same `days` must be within price_cap_atr x ATR20% x sqrt(days) (ATR on
    bars ending T-days), and close_T >= floor x SMA50. Returns the volume ratio or None."""
    h, l, c, v = list(highs), list(lows), list(closes), list(volumes)
    if len(c) < base_len + days + 25 or len(v) < base_len + days + 5:
        return None
    if days == 1:
        base = median(v[-base_len - 1:-1])
        cur = v[-1]
    else:
        sums = [sum(v[i - days + 1:i + 1]) for i in range(len(v) - base_len - days, len(v) - days)]
        base = median(sums)
        cur = sum(v[-days:])
    if not base or base <= 0 or cur < vol_mult * base:
        return None
    ref = c[-days - 1]
    a = atr(h[:-days], l[:-days], c[:-days], 20)
    if not a or ref <= 0:
        return None
    move = abs(c[-1] / ref - 1.0)
    if move > price_cap_atr * (a / ref) * days ** 0.5:
        return None
    m50 = sma(c, 50)
    if m50 is None or c[-1] < floor * m50:
        return None
    return cur / base


def exit_signal(sessions_held, hold):
    """Time exit only: `hold` sessions after entry."""
    return sessions_held is not None and sessions_held >= hold
