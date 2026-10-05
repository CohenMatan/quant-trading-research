"""P5-CP1 DESIGN REFERENCE: deterministic, point-in-time chart-structure algorithms (Phase 5, structured chart analysis).

STATUS: design reference only. NOT frozen, NOT a pre-registration, NOT run on any market data. Exercised only on synthetic
series (tests/test_p5_chart.py, research/phase5/p5_demo.py). Every threshold below is a practitioner convention or a
plumbing default written down BEFORE any real chart was computed; none was tuned, and any future freeze would be a
separate owner-approved specification.

Point-in-time contract: every function receives arrays that end at the decision bar t (index -1) and uses nothing after
it. A swing point at bar i is CONFIRMED only at bar i + k (k bars on its right), so at t only pivots with i <= t - k
exist. Weekly bars at t aggregate only the sessions <= t (the current week may be partial and is flagged). All price
geometry is in log space, so a constant rescaling of the whole history (e.g. a later split / dividend factor) changes
nothing (scale invariance).

Inputs: o, h, l, c, v = 1-D float arrays of daily bars (split-adjusted prices, oldest first, no NaN inside the window);
week_id = integer week label per bar (e.g. ISO year * 100 + ISO week).
"""
import math

import numpy as np

# ----------------------------------------------------------------------------------------------- conventions (unfrozen)
PIVOT_K_DAILY = 5            # one week on each side; confirmation delay 5 sessions
PIVOT_K_WEEKLY = 3           # three weeks on each side; confirmation delay 3 weeks
PIVOT_MIN_ATR = 1.0          # a swing must stand >= 1 ATR above / below the opposite extreme since the previous swing
ATR_N = 20
ZONE_HALF_ATR = 0.5          # S/R zone half-width = 0.5 ATR (volatility-scaled)
ZONE_MIN_TOUCHES = 2
LOOKBACK_DAILY = 252         # S/R, trendlines and pivots: at most one year of daily history
LOOKBACK_WEEKLY = 104        # two years of weekly history
TL_MIN_SPACING_DAILY = 10    # the two anchors of a trendline are >= 10 sessions apart
TL_MIN_SPACING_WEEKLY = 4
TL_TOL_ATR = 0.5             # a close more than 0.5 ATR below the line invalidates it (permanently)
BASE_MIN, BASE_MAX = 15, 325  # base length in sessions (3 to 65 weeks, O'Neil-style)
BASE_MAX_DEPTH = 0.33        # O'Neil: normal base depth <= 33%
BREAKOUT_FRESH = 5           # the first close above the level happened within the last 5 sessions
BREAKOUT_MAX_EXT = 0.05      # Minervini / O'Neil: buy within 5% of the pivot
RELVOL_BREAKOUT = 1.4        # O'Neil: breakout volume >= 40% above average (50-session)
CONTRACTION_MAX = 0.8        # ATR10 / ATR50 and V10 / V50 <= 0.8 = contraction / dry-up
NEAR_HIGH = 0.25             # Minervini: within 25% of the 52-week high


# ----------------------------------------------------------------------------------------------- basic indicators
def sma(x, n):
    """Trailing simple moving average; NaN until n values exist."""
    x = np.asarray(x, float)
    out = np.full(x.size, np.nan)
    if x.size >= n:
        cs = np.cumsum(np.r_[0.0, x])
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def true_range(h, l, c):
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    pc = np.r_[c[0], c[:-1]]
    return np.maximum(h, pc) - np.minimum(l, pc)


def atr(h, l, c, n=ATR_N):
    return sma(true_range(h, l, c), n)


def atr_pct(h, l, c, n=ATR_N):
    """ATR as a fraction of the close (scale-free; used for log-space tolerances)."""
    return atr(h, l, c, n) / np.asarray(c, float)


# ----------------------------------------------------------------------------------------------- weekly bars (PIT)
def weekly_bars(o, h, l, c, v, week_id):
    """Aggregate daily bars into weekly bars using ONLY the bars given (i.e. <= t). Returns dict of arrays and
    'partial' = True for the last week when its last session is t and the week may not be over (the caller knows whether
    t is the week's final session; here the last bar is flagged as partial unless closed=True is set by the caller)."""
    wk = np.asarray(week_id)
    starts = np.r_[0, np.flatnonzero(wk[1:] != wk[:-1]) + 1]
    ends = np.r_[starts[1:], wk.size] - 1
    o, h, l, c, v = (np.asarray(a, float) for a in (o, h, l, c, v))
    return dict(o=o[starts], h=np.maximum.reduceat(h, starts), l=np.minimum.reduceat(l, starts), c=c[ends],
                v=np.add.reduceat(v, starts), last_day=ends, week=wk[starts])


# ----------------------------------------------------------------------------------------------- swing points (PIT)
def swing_points(h, l, c, k, min_atr=PIVOT_MIN_ATR, atr_n=ATR_N):
    """Confirmed swing highs / lows of the series ending at t = len - 1.

    Bar i is a swing high if h[i] > max(h[i-k:i]) and h[i] >= max(h[i+1:i+k+1]) (ties resolved to the LEFT-most bar via
    the strict left inequality); it is confirmed at bar i + k, so only i <= t - k can qualify. Prominence filter: the
    swing high must exceed the lowest low since the previous accepted swing (of either kind) by >= min_atr x ATR(i)
    (and symmetrically for lows). Returns a chronological list of (i, 'H' | 'L', log price)."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    n = h.size
    a = atr(h, l, c, atr_n)
    out = []
    last_i = -1
    for i in range(k, n - k):
        hi = h[i] > h[i - k:i].max() and h[i] >= h[i + 1:i + k + 1].max()
        lo = l[i] < l[i - k:i].min() and l[i] <= l[i + 1:i + k + 1].min()
        if not (hi or lo):
            continue
        ai = a[i] if np.isfinite(a[i]) else np.nanmean(true_range(h, l, c)[max(0, i - atr_n + 1):i + 1])
        seg = slice(last_i + 1, i + 1)
        if hi and h[i] - l[seg].min() >= min_atr * ai:
            out.append((i, "H", math.log(h[i])))
            last_i = i
        elif lo and h[seg].max() - l[i] >= min_atr * ai:
            out.append((i, "L", math.log(l[i])))
            last_i = i
    return out


# ----------------------------------------------------------------------------------------------- market structure
STATES = ("strong_uptrend", "weak_uptrend", "range", "deteriorating", "downtrend", "undefined")


def structure_state(pivots, close, tol):
    """HH / HL market-structure state at t from the last two confirmed swing highs (H1, H2) and lows (L1, L2), and the
    current close; 'higher' / 'lower' means by more than tol (log), otherwise 'equal'.
      undefined      : fewer than two swing highs or two swing lows
      downtrend      : close below L2 (structure broken) with lower high AND lower low; or LH and LL
      deteriorating  : close below L2 (the last confirmed swing low) without a full LH + LL sequence
      (break up)     : close above H2 (the last confirmed swing high) -> strong_uptrend if HL, else weak_uptrend
      strong_uptrend : HH and HL, close at or above L2
      weak_uptrend   : one of HH / HL with the other 'equal' (no LH, no LL)
      range          : everything else (equal / contracting / expanding swings)"""
    H = [p for _, t, p in pivots if t == "H"]
    L = [p for _, t, p in pivots if t == "L"]
    if len(H) < 2 or len(L) < 2:
        return "undefined"
    dh, dl = H[-1] - H[-2], L[-1] - L[-2]
    hh, lh = dh > tol, dh < -tol
    hl, ll = dl > tol, dl < -tol
    lc = math.log(close)
    if lc < L[-1] - tol:
        return "downtrend" if (lh and ll) else "deteriorating"
    if lc > H[-1] + tol:                       # close above the last confirmed swing high: a higher high is forming
        return "strong_uptrend" if hl else "weak_uptrend"
    if hh and hl:
        return "strong_uptrend"
    if lh and ll:
        return "downtrend"
    if (hh and not ll and not hl) or (hl and not hh and not lh):
        return "weak_uptrend"
    return "range"


# ----------------------------------------------------------------------------------------------- support / resistance
def sr_zones(pivots, tol, lookback_start=0, min_touches=ZONE_MIN_TOUCHES):
    """Horizontal support / resistance zones from confirmed pivots (highs and lows both count; roles may flip).
    Deterministic ANCHORED clustering in sorted log-price order: a pivot joins the current cluster if it lies within
    2 x tol of the cluster's FIRST (lowest) member, so no zone can chain wider than 2 x tol (single linkage was rejected
    on the synthetic demo: it merged a whole base into one zone). Zone = [min - tol, max + tol] of its members; touches
    = member count; only pivots with index >= lookback_start; zones with fewer than min_touches touches are dropped.
    Returns a list of dicts sorted by price."""
    pts = sorted((p, i) for i, _, p in pivots if i >= lookback_start)
    zones, cur = [], []
    for p, i in pts:
        if cur and p - cur[0][0] > 2 * tol:
            zones.append(cur)
            cur = []
        cur.append((p, i))
    if cur:
        zones.append(cur)
    out = []
    for z in zones:
        if len(z) >= min_touches:
            ps = [p for p, _ in z]
            out.append(dict(lo=min(ps) - tol, hi=max(ps) + tol, touches=len(z), last=max(i for _, i in z),
                            first=min(i for _, i in z)))
    return out


def nearest_levels(zones, close):
    """(nearest zone fully above the close or containing it from below = resistance, nearest zone below = support)."""
    lc = math.log(close)
    above = [z for z in zones if z["lo"] > lc]
    below = [z for z in zones if z["hi"] < lc]
    res = min(above, key=lambda z: z["lo"]) if above else None
    sup = max(below, key=lambda z: z["hi"]) if below else None
    return res, sup


# ----------------------------------------------------------------------------------------------- trendlines
def support_trendline(pivots, logc, tol, min_spacing, lookback_start=0):
    """The ascending support line at t (log space) from two confirmed swing lows L1 < L2 (chronological, L2 above L1,
    >= min_spacing bars apart, both >= lookback_start). The line is valid at t if no close after L1 fell below it by
    more than tol (invalidated lines never revive). Touches = confirmed swing lows within tol of the line (incl. anchors).
    Selection among valid lines, deterministic: most touches, then the most recent L2, then the earliest L1.
    Returns dict(i1, i2, slope, value_at_t, touches) or None."""
    lows = [(i, p) for i, t, p in pivots if t == "L" and i >= lookback_start]
    n = logc.size
    best = None
    for a in range(len(lows)):
        for b in range(a + 1, len(lows)):
            (i1, p1), (i2, p2) = lows[a], lows[b]
            if i2 - i1 < min_spacing or p2 <= p1:
                continue
            slope = (p2 - p1) / (i2 - i1)
            idx = np.arange(i1, n)
            line = p1 + slope * (idx - i1)
            if np.any(logc[i1:] < line - tol):
                continue
            touches = sum(1 for i, p in lows if i >= i1 and abs(p - (p1 + slope * (i - i1))) <= tol)
            key = (touches, i2, -i1)
            if best is None or key > best[0]:
                best = (key, dict(i1=i1, i2=i2, slope=slope, value_at_t=float(line[-1]), touches=touches))
    return best[1] if best else None


# ----------------------------------------------------------------------------------------------- base / consolidation
def base_window(h, l, c, pivots, t_min=BASE_MIN, t_max=BASE_MAX):
    """The current base: from the most recent confirmed swing high that is the highest high of the preceding 126
    sessions (the 'left-side high') to t. Valid if its length is in [t_min, t_max] sessions. Returns (start, pivot log
    level) or None."""
    n = len(c)
    for i, typ, p in reversed(pivots):
        if typ != "H":
            continue
        length = n - 1 - i
        if length > t_max:
            return None
        if h[i] >= np.max(h[max(0, i - 126):i + 1]) and length >= t_min:
            return i, p
    return None


def base_metrics(h, l, c, v, pivots):
    """Base attributes at t (None if no valid base): length, depth below the left-side high, position of the close in
    the base range, contraction ratio ATR10/ATR50, volume dry-up V10/V50, tightness of the last 10 closes, number of
    pullbacks inside the base and whether their depths shrink (volatility-contraction sequence), base slope (log)."""
    bw = base_window(h, l, c, pivots)
    if bw is None:
        return None
    s, lvl = bw
    h, l, c, v = (np.asarray(a, float) for a in (h, l, c, v))
    seg_l = l[s:]
    depth = 1.0 - seg_l.min() / math.exp(lvl)
    rng = math.exp(lvl) - seg_l.min()
    pos = (c[-1] - seg_l.min()) / rng if rng > 0 else 1.0
    a10, a50 = atr(h, l, c, 10)[-1], atr(h, l, c, 50)[-1]
    v10, v50 = v[-10:].mean(), v[-50:].mean() if v.size >= 50 else np.nan
    tight = (c[-10:].max() - c[-10:].min()) / c[-1]
    inside = [(i, t, p) for i, t, p in pivots if i >= s]
    pulls = []
    for (i1, t1, p1), (i2, t2, p2) in zip(inside, inside[1:]):
        if t1 == "H" and t2 == "L":
            pulls.append(1.0 - math.exp(p2 - p1))
    x = np.arange(c.size - s)
    slope = float(np.polyfit(x, np.log(c[s:]), 1)[0]) if x.size >= 2 else 0.0
    return dict(start=int(s), length=int(c.size - 1 - s), level=float(lvl), depth=float(depth), pos=float(pos),
                atr_ratio=float(a10 / a50) if a50 > 0 else np.nan, vol_ratio=float(v10 / v50) if v50 > 0 else np.nan,
                tight10=float(tight), pullbacks=[float(x) for x in pulls],
                contracting=bool(len(pulls) >= 2 and all(b < a for a, b in zip(pulls, pulls[1:]))),
                slope=slope)


# ----------------------------------------------------------------------------------------------- breakout / trigger
def breakout(h, l, c, v, level_log, fresh=BREAKOUT_FRESH):
    """Breakout above an ESTABLISHED level (the base's left-side high or the top of a resistance zone): the first close
    above the level occurred within the last `fresh` sessions and no close since fell back below it. Returns dict or
    None: age (sessions since the first close above), extension above the level, close-location value and relative
    volume (V / V50 of the session before) on the breakout day, true range / ATR20 on that day."""
    c = np.asarray(c, float)
    lvl = math.exp(level_log)
    above = c > lvl
    if not above[-1]:
        return None
    j = c.size - 1
    while j > 0 and above[j - 1]:
        j -= 1
    age = c.size - 1 - j
    if age >= fresh or j == 0:
        return None
    h, l, v = (np.asarray(a, float) for a in (h, l, v))
    clv = (c[j] - l[j]) / (h[j] - l[j]) if h[j] > l[j] else 1.0
    v50 = v[max(0, j - 50):j].mean() if j > 0 else np.nan
    tr = true_range(h, l, c)[j]
    a20 = atr(h, l, c)[j - 1] if j >= ATR_N else np.nan
    return dict(day=int(j), age=int(age), ext=float(c[-1] / lvl - 1.0), clv=float(clv),
                relvol=float(v[j] / v50) if v50 > 0 else np.nan, tr_atr=float(tr / a20) if a20 > 0 else np.nan)


# ----------------------------------------------------------------------------------------------- volume behaviour
def volume_profile(c, v, n=50):
    """Up/down volume ratio over the last n sessions and the count of 'distribution' sessions (close down >= 1% on
    volume above the n-session average) among the last 25."""
    c, v = np.asarray(c, float), np.asarray(v, float)
    r = c[1:] / c[:-1] - 1.0
    vv = v[1:]
    w = slice(max(0, r.size - n), r.size)
    up, dn = vv[w][r[w] > 0].sum(), vv[w][r[w] < 0].sum()
    avg = vv[w].mean()
    w25 = slice(max(0, r.size - 25), r.size)
    dist = int(((r[w25] <= -0.01) & (vv[w25] > avg)).sum())
    return dict(updown=float(up / dn) if dn > 0 else np.inf, distribution_days=dist)


# ----------------------------------------------------------------------------------------------- the snapshot
def snapshot(o, h, l, c, v, week_id, spy_c=None):
    """All chart-structure facts at t (the last bar). Pure function of bars <= t. No score is computed here."""
    o, h, l, c, v = (np.asarray(a, float) for a in (o, h, l, c, v))
    n = c.size
    lc = np.log(c)
    ap = atr_pct(h, l, c)[-1]
    tol = ZONE_HALF_ATR * ap
    lb = max(0, n - LOOKBACK_DAILY)
    piv_d = swing_points(h, l, c, PIVOT_K_DAILY)
    zones = sr_zones(piv_d, tol, lookback_start=lb)
    res, sup = nearest_levels(zones, c[-1])
    tl = support_trendline(piv_d, lc, TL_TOL_ATR * ap, TL_MIN_SPACING_DAILY, lookback_start=lb)
    W = weekly_bars(o, h, l, c, v, week_id)
    piv_w = swing_points(W["h"], W["l"], W["c"], PIVOT_K_WEEKLY)
    wtol = ZONE_HALF_ATR * atr_pct(W["h"], W["l"], W["c"], 10)[-1] if W["c"].size >= 10 else tol
    ma10w, ma30w, ma40w = (sma(W["c"], k)[-1] for k in (10, 30, 40))
    ma30w_4 = sma(W["c"], 30)[-5] if W["c"].size >= 35 else np.nan
    hi52 = h[-252:].max()
    base = base_metrics(h, l, c, v, piv_d)
    level = None
    if base is not None and base["depth"] <= BASE_MAX_DEPTH:
        level = base["level"]
    elif res is not None:
        level = res["hi"]
    bo = None
    if base is not None:
        bo = breakout(h, l, c, v, base["level"])
    if bo is None and sup is not None:                      # a just-broken resistance zone is now the nearest support
        bo = breakout(h, l, c, v, sup["hi"])
    out = dict(
        n=int(n), close=float(c[-1]), atr_pct=float(ap),
        ma20=float(sma(c, 20)[-1]), ma50=float(sma(c, 50)[-1]), ma200=float(sma(c, 200)[-1]),
        ma10w=float(ma10w), ma30w=float(ma30w), ma40w=float(ma40w), ma30w_4ago=float(ma30w_4),
        hi52=float(hi52), dist_hi52=float(1.0 - c[-1] / hi52),
        weekly_state=structure_state(piv_w, c[-1], wtol), daily_state=structure_state(piv_d, c[-1], tol),
        pivots_daily=piv_d, pivots_weekly=piv_w, zones=zones,
        resistance=res, support=sup, trendline=tl, base=base, level=level, breakout=bo,
        volume=volume_profile(c, v),
        ext_ma20_atr=float((c[-1] / sma(c, 20)[-1] - 1.0) / ap),
        ext_ma50=float(c[-1] / sma(c, 50)[-1] - 1.0),
        weekly_partial=None,
    )
    if spy_c is not None:
        rs = c / np.asarray(spy_c, float)
        out["rs_new_high"] = bool(rs[-1] >= rs[-252:].max())
        out["rs_slope_13w"] = float(math.log(rs[-1] / rs[-66])) if rs.size > 66 else np.nan
    # nearest defined support below the close: S/R zone top, trendline value, or base low (the highest of them)
    cands = []
    if sup is not None:
        cands.append(math.exp(sup["hi"]))
    if tl is not None and tl["value_at_t"] < lc[-1]:
        cands.append(math.exp(tl["value_at_t"]))
    if base is not None:
        cands.append(float(np.min(l[base["start"]:])))
    below = [x for x in cands if x < c[-1]]
    out["support_px"] = max(below) if below else None
    out["risk_pct"] = float(1.0 - out["support_px"] / c[-1]) if below else None
    return out


# ----------------------------------------------------------------------------------------------- checklist (proposal)
def checklist(s):
    """The PROPOSED structured checklist (P5-CP1 section 15-17): four categories x five pre-registered binary conditions,
    each category = count of conditions met (0-5), total = sum (0-20), plus hard disqualifiers that are never offset by
    a high score. Unfrozen; shown so the rubric is concrete and testable on synthetic charts."""
    b, bo, ap = s["base"], s["breakout"], s["atr_pct"]
    W = [s["close"] > s["ma30w"], s["ma30w"] > s["ma30w_4ago"], s["ma10w"] > s["ma30w"],
         s["weekly_state"] in ("strong_uptrend", "weak_uptrend"), s["dist_hi52"] <= NEAR_HIGH]
    B = [b is not None, b is not None and b["depth"] <= BASE_MAX_DEPTH,
         b is not None and b["atr_ratio"] <= CONTRACTION_MAX, b is not None and b["vol_ratio"] <= CONTRACTION_MAX,
         b is not None and b["contracting"]]
    T = [bo is not None, bo is not None and bo["clv"] >= 0.5, bo is not None and bo["relvol"] >= RELVOL_BREAKOUT,
         s["close"] > s["ma50"] and s["ma20"] > s["ma50"], bo is not None and bo["tr_atr"] >= 1.0]
    R = [bo is None or bo["ext"] <= BREAKOUT_MAX_EXT, s["ext_ma20_atr"] <= 2.0,
         s["risk_pct"] is not None and s["risk_pct"] <= 0.08,
         s["risk_pct"] is not None and s["risk_pct"] <= 2.5 * ap,
         s["volume"]["distribution_days"] <= 4]
    cat = {k: int(sum(bool(x) for x in v)) for k, v in (("weekly_trend", W), ("base", B), ("trigger", T),
                                                         ("entry_risk", R))}
    dq = []
    if not (s["close"] > s["ma40w"]):
        dq.append("below_40w_ma")
    if s["ext_ma50"] > 0.25:
        dq.append("extended_25pct_above_ma50")
    if s["support_px"] is None:
        dq.append("no_definable_support")
    if s["weekly_state"] in ("downtrend",):
        dq.append("weekly_downtrend")
    return dict(categories=cat, total=int(sum(cat.values())), disqualified=dq, eligible=not dq)
