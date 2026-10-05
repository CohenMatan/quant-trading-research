# qr_chart.py — H020 structured chart score (research/phase5/H020_spec.md; P5-CP2). Pure numpy, no QuantConnect
# imports (tests/test_h020_chart.py, tests/test_h020_scenarios.py). The same code runs locally on synthetic fixtures and,
# after owner approval, inside LEAN on the real panel.
#
# FROZEN CANDIDATE (P5-CP2, 2026-10-05): every constant below is pinned with the specification by qresearch.p5h020
# (tests/test_h020_spec.py). Nothing here may change after any real chart score or return is computed. Threshold
# provenance: research/phase5/H020_threshold_provenance.md. Practitioner rules are hypotheses / frameworks, not proof.
#
# Point-in-time contract: every function receives bars of ONE stock ending at the decision bar t (index -1, the last
# session of an ISO week) and uses nothing after it. Prices are split-adjusted (RAW x split feed), volume is split-adjusted
# (RAW volume / split price factors), all geometry is in log price (scale-invariant). A swing point at bar i is CONFIRMED
# only at bar i + k; its prominence test uses only a fixed local window, so the set of swing points does not depend on
# where the history scan starts (no repainting, no scan-start dependence).
import math

import numpy as np

# ----------------------------------------------------------------------------------------------- frozen constants
D_K, W_K = 5, 3                 # swing confirmation: 5 sessions (daily), 3 weeks (weekly) on each side
PROM_ATR = 1.0                  # a swing must stand >= 1 ATR above (below) the lowest low (highest high) of the
PROM_WIN = 2                    # ... PROM_WIN x k bars before it (local window, scan-start independent)
D_ATR, W_ATR = 20, 10           # ATR lengths (simple mean of true range): daily 20 sessions, weekly 10 weeks
TOL_ATR = 0.5                   # 'equal level' / zone / trendline tolerance = 0.5 ATR (as a log-price fraction)
D_SCAN, W_SCAN = 300, 104       # swing-point scan windows: last 300 sessions, last 104 weeks
ZONE_LOOKBACK = 252             # daily S/R zones from pivots of the last 252 sessions
ZONE_MIN_TOUCHES = 2
TL_MIN_SPACING = 10             # trendline anchors >= 10 sessions apart (daily), within ZONE_LOOKBACK
BASE_MIN_W, BASE_MAX_W = 7, 65  # base length in weeks (O'Neil cup-with-handle range)
BASE_ANCHOR_W = 26              # the base anchor is the highest weekly high of the prior 26 weeks (inclusive)
BASE_MAX_DEPTH = 0.33           # O'Neil: usual correction up to ~33%
CONTRACT_MAX = 0.80             # ATR and volume contraction ratio threshold
CONTRACT_RECENT = (14, 5)       # contraction window: sessions t-14 .. t-5 (10 sessions, excludes the trigger window)
CONTRACT_REF = (64, 15)         # reference window: sessions t-64 .. t-15 (50 sessions)
BO_FRESH = 5                    # breakout: first close above the level within the last 5 sessions
BO_MAX_EXT = 0.05               # within 5% of the pivot (O'Neil)
BO_VOL = 1.40                   # breakout-day volume >= 1.4 x mean of the 50 prior sessions (O'Neil: +40% to +50%)
BO_VOL_N = 50
BO_CLV = 0.5                    # breakout-day close in the upper half of its range
NEAR_HIGH = 0.75                # close >= 0.75 x 52-week high (Minervini: within 25%)
HIGH_N = 252
MA_SLOPE_W = 4                  # 40-week MA rising over 4 weeks (Minervini: 200-day MA up for at least 1 month)
RISK_MAX = 0.08                 # support <= 8% below the close (O'Neil 7-8% loss rule, applied to support)
RISK_ATR = 2.5
EXT_MA20_ATR = 2.0
DIST_N, DIST_MAX, DIST_DROP = 25, 4, -0.002   # IBD distribution day (applied to the stock): <= 4 in 25 sessions
EXT_MA50_DQ = 0.25              # disqualifier: close > 1.25 x 50-day MA
GAP_DQ, GAP_N = 0.85, 10        # disqualifier: an open <= 0.85 x prior close within the last 10 sessions
MIN_SESSIONS = 504              # universe rule: >= 2 years of bars (every condition computable)
HIST_SESSIONS = 756             # the snapshot reads only the last 756 sessions (every look-back fits inside; the result
#                                 does not depend on how much older history exists -- tested)
STATES = ("strong_uptrend", "uptrend", "range", "deteriorating", "downtrend", "undefined")
CONDITIONS = ("W1", "W2", "W3", "W4", "W5", "B1", "B2", "B3", "B4", "B5", "T1", "T2", "T3", "T4", "T5",
              "R1", "R2", "R3", "R4", "R5")
DISQUALIFIERS = ("D1", "D2", "D3", "D4", "D5")
CATEGORIES = dict(W="weekly_trend_structure", B="base_quality", T="trigger_breakout", R="entry_risk_support")


# ----------------------------------------------------------------------------------------------- indicators
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


def atr(h, l, c, n):
    return sma(true_range(h, l, c), n)


# ----------------------------------------------------------------------------------------------- weekly bars
def weekly_bars(o, h, l, c, v, week_id):
    """ISO-week bars from the stock's own sessions given (all <= t): open = first open, high = max, low = min, close =
    last close, volume = sum; last_idx = daily index of each week's last session."""
    wk = np.asarray(week_id)
    st = np.r_[0, np.flatnonzero(wk[1:] != wk[:-1]) + 1]
    en = np.r_[st[1:], wk.size] - 1
    o, h, l, c, v = (np.asarray(a, float) for a in (o, h, l, c, v))
    return dict(o=o[st], h=np.maximum.reduceat(h, st), l=np.minimum.reduceat(l, st), c=c[en],
                v=np.add.reduceat(v, st), first_idx=st, last_idx=en, week=wk[st])


# ----------------------------------------------------------------------------------------------- swing points
def swing_points(h, l, c, k, atr_n, scan):
    """Confirmed swing points among the last `scan` bars (only bars i <= n-1-k can be confirmed).
    Swing high at i: h[i] > max(h[i-k:i]) and h[i] >= max(h[i+1:i+k+1]) (equal highs: the left-most one) and
    h[i] - min(l[i-PROM_WIN*k : i+1]) >= PROM_ATR x ATR_i. Swing low symmetric. A bar that is both: the high is taken.
    Requires i >= max(k, PROM_WIN*k, atr_n - 1) inside the array. Returns a chronological list of (i, 'H'|'L', log)."""
    h, l, c = (np.asarray(a, float) for a in (h, l, c))
    n = h.size
    a = atr(h, l, c, atr_n)
    m = PROM_WIN * k
    lo_i = max(k, m, atr_n - 1, n - scan)
    out = []
    for i in range(lo_i, n - k):
        ai = a[i]
        if not np.isfinite(ai) or ai <= 0:
            continue
        if h[i] > h[i - k:i].max() and h[i] >= h[i + 1:i + k + 1].max() and h[i] - l[i - m:i + 1].min() >= PROM_ATR * ai:
            out.append((i, "H", math.log(h[i])))
        elif l[i] < l[i - k:i].min() and l[i] <= l[i + 1:i + k + 1].min() and h[i - m:i + 1].max() - l[i] >= PROM_ATR * ai:
            out.append((i, "L", math.log(l[i])))
    return out


# ----------------------------------------------------------------------------------------------- market structure
def classify(H1, H2, L1, L2, tol):
    """Swing labels: HH / LH / EH (equal high) for H2 vs H1; HL / LL / EL for L2 vs L1 (beyond tol in log)."""
    hh = "HH" if H2 - H1 > tol else ("LH" if H1 - H2 > tol else "EH")
    hl = "HL" if L2 - L1 > tol else ("LL" if L1 - L2 > tol else "EL")
    return hh, hl


def structure_state(pivots, close, tol):
    """State at t from the last two confirmed swing highs (H1, H2) and lows (L1, L2) and the close:
      undefined       fewer than two swing highs or two swing lows
      close < L2 - tol (break down): downtrend if LH and LL, else deteriorating
      close > H2 + tol (break up):   strong_uptrend if HL, else uptrend
      otherwise: HH+HL strong_uptrend; LH+LL downtrend; (HH+EL) or (EH+HL) uptrend; anything else range."""
    H = [p for _, t, p in pivots if t == "H"]
    L = [p for _, t, p in pivots if t == "L"]
    if len(H) < 2 or len(L) < 2:
        return "undefined"
    hh, hl = classify(H[-2], H[-1], L[-2], L[-1], tol)
    lc = math.log(close)
    if lc < L[-1] - tol:
        return "downtrend" if (hh == "LH" and hl == "LL") else "deteriorating"
    if lc > H[-1] + tol:
        return "strong_uptrend" if hl == "HL" else "uptrend"
    if hh == "HH" and hl == "HL":
        return "strong_uptrend"
    if hh == "LH" and hl == "LL":
        return "downtrend"
    if (hh == "HH" and hl == "EL") or (hh == "EH" and hl == "HL"):
        return "uptrend"
    return "range"


# ----------------------------------------------------------------------------------------------- support / resistance
def zones(pivots, tol, start):
    """Horizontal zones from confirmed swing highs AND lows with index >= start (roles flip). Anchored clustering in
    sorted log price: a pivot joins the current zone if within 2 x tol of the zone's lowest member (no chaining).
    Zone = [min - tol, max + tol]; kept if touches >= ZONE_MIN_TOUCHES. Sorted by price."""
    pts = sorted((p, i) for i, _, p in pivots if i >= start)
    groups, cur = [], []
    for p, i in pts:
        if cur and p - cur[0][0] > 2 * tol:
            groups.append(cur)
            cur = []
        cur.append((p, i))
    if cur:
        groups.append(cur)
    out = []
    for g in groups:
        if len(g) >= ZONE_MIN_TOUCHES:
            ps = [p for p, _ in g]
            out.append(dict(lo=min(ps) - tol, hi=max(ps) + tol, touches=len(g), first=min(i for _, i in g),
                            last=max(i for _, i in g)))
    return out


def nearest(zs, close):
    """(nearest zone entirely above the close = resistance, nearest zone entirely below = support); a zone that contains
    the close is neither."""
    lc = math.log(close)
    above = [z for z in zs if z["lo"] > lc]
    below = [z for z in zs if z["hi"] < lc]
    return (min(above, key=lambda z: z["lo"]) if above else None,
            max(below, key=lambda z: z["hi"]) if below else None)


# ----------------------------------------------------------------------------------------------- trendlines
def trendline(pivots, logc, tol, start, kind):
    """kind 'support': two confirmed swing lows L1 < L2 (L2 higher), 'resistance': two confirmed swing highs (H2 lower);
    anchors >= TL_MIN_SPACING bars apart, both >= start. Valid at t iff no close after the first anchor is beyond the
    line by more than tol (below for support, above for resistance): a broken line is dead for ever. Touches = pivots of
    the same type within tol of the line at their index (anchors included). Selection: most touches, then the most
    recent second anchor, then the earliest first anchor. Returns dict(i1, i2, slope, value, touches) or None."""
    typ, sgn = ("L", 1.0) if kind == "support" else ("H", -1.0)
    pts = [(i, p) for i, t, p in pivots if t == typ and i >= start]
    n = logc.size
    best = None
    for a in range(len(pts)):
        for b in range(a + 1, len(pts)):
            (i1, p1), (i2, p2) = pts[a], pts[b]
            if i2 - i1 < TL_MIN_SPACING or sgn * (p2 - p1) <= 0:
                continue
            slope = (p2 - p1) / (i2 - i1)
            line = p1 + slope * (np.arange(i1, n) - i1)
            if np.any(sgn * (logc[i1:] - line) < -tol):
                continue
            touches = sum(1 for i, p in pts if i >= i1 and abs(p - (p1 + slope * (i - i1))) <= tol)
            key = (touches, i2, -i1)
            if best is None or key > best[0]:
                best = (key, dict(i1=i1, i2=i2, slope=slope, value=float(line[-1]), touches=touches))
    return best[1] if best else None


# ----------------------------------------------------------------------------------------------- base (weekly)
def base(W, wpiv):
    """The current base on WEEKLY bars. Anchor = the most recent confirmed weekly swing high j whose high is the highest
    weekly high of weeks j-26 .. j. Length L = last week index - j. Valid iff BASE_MIN_W <= L <= BASE_MAX_W (a younger or
    older anchor = no valid base; earlier anchors are not searched). Depth = 1 - lowest weekly low since j / anchor high.
    Pullbacks = for each confirmed swing high (anchor first) followed by a confirmed swing low inside the base: 1 - low /
    high; contracting = at least two pullbacks, each strictly smaller than the previous."""
    wh, wl = W["h"], W["l"]
    last = wh.size - 1
    anchor = None
    for i, t, p in reversed(wpiv):
        if t == "H" and wh[i] >= wh[max(0, i - BASE_ANCHOR_W):i + 1].max():
            anchor = i
            break
    if anchor is None:
        return None
    L = last - anchor
    inside = [(i, t, p) for i, t, p in wpiv if i >= anchor]
    pulls = []
    hi = None
    for i, t, p in inside:
        if t == "H":
            hi = p
        elif hi is not None:
            pulls.append(1.0 - math.exp(p - hi))
            hi = None
    return dict(anchor=int(anchor), level=float(math.log(wh[anchor])), length=int(L),
                valid=bool(BASE_MIN_W <= L <= BASE_MAX_W), depth=float(1.0 - wl[anchor:].min() / wh[anchor]),
                pullbacks=[float(x) for x in pulls],
                contracting=bool(len(pulls) >= 2 and all(b < a for a, b in zip(pulls, pulls[1:]))))


# ----------------------------------------------------------------------------------------------- breakout (daily)
def breakout(o, h, l, c, v, level_log, base_start_day):
    """Breakout above the base anchor level P = exp(level_log): the current run of closes > P started at day j0 >
    base_start_day (the anchor week's last session) within the last BO_FRESH sessions. Returns dict or None."""
    c = np.asarray(c, float)
    P = math.exp(level_log)
    n = c.size
    if not c[-1] > P:
        return None
    j0 = n - 1
    while j0 > 0 and c[j0 - 1] > P:
        j0 -= 1
    age = n - 1 - j0
    if age >= BO_FRESH or j0 <= base_start_day or j0 < BO_VOL_N:
        return None
    rng = h[j0] - l[j0]
    return dict(day=int(j0), age=int(age), ext=float(c[-1] / P - 1.0),
                clv=float((c[j0] - l[j0]) / rng) if rng > 0 else 1.0,
                relvol=float(v[j0] / np.mean(v[j0 - BO_VOL_N:j0])) if np.mean(v[j0 - BO_VOL_N:j0]) > 0 else float("nan"))


# ----------------------------------------------------------------------------------------------- the snapshot
def snapshot(o, h, l, c, v, week_id):
    """All H020 chart facts and the frozen checklist at t = the last bar given (a weekly decision: the last session of
    its ISO week). Inputs: one stock's split-adjusted daily bars, oldest first, >= MIN_SESSIONS bars. Returns a dict with
    'conditions' (20 booleans), 'disqualifiers' (5 booleans), 'categories', 'score', 'disqualified' and every feature."""
    o, h, l, c, v = (np.asarray(a, float) for a in (o, h, l, c, v))
    n = c.size
    if n < MIN_SESSIONS:
        raise ValueError("H020 snapshot needs >= %d sessions (universe rule)" % MIN_SESSIONS)
    if n > HIST_SESSIONS:
        o, h, l, c, v = (a[-HIST_SESSIONS:] for a in (o, h, l, c, v))
        week_id = np.asarray(week_id)[-HIST_SESSIONS:]
        n = HIST_SESSIONS
    lc = np.log(c)
    a20 = atr(h, l, c, D_ATR)
    atrp = a20[-1] / c[-1]
    tol = TOL_ATR * atrp
    W = weekly_bars(o, h, l, c, v, week_id)
    nw = W["c"].size
    watrp = atr(W["h"], W["l"], W["c"], W_ATR)[-1] / W["c"][-1]
    wtol = TOL_ATR * watrp
    dpiv = swing_points(h, l, c, D_K, D_ATR, D_SCAN)
    wpiv = swing_points(W["h"], W["l"], W["c"], W_K, W_ATR, W_SCAN)
    zstart = n - ZONE_LOOKBACK
    dz = zones(dpiv, tol, zstart)
    res, sup = nearest(dz, c[-1])
    wz = zones(wpiv, wtol, nw - W_SCAN)
    wres, wsup = nearest(wz, c[-1])
    tl_s = trendline(dpiv, lc, tol, zstart, "support")
    tl_r = trendline(dpiv, lc, tol, zstart, "resistance")
    ma10w, ma30w, ma40w = (sma(W["c"], k) for k in (10, 30, 40))
    ma20, ma50, ma200 = (sma(c, k) for k in (20, 50, 200))
    hi52 = h[-HIGH_N:].max()
    wstate = structure_state(wpiv, c[-1], wtol)
    dstate = structure_state(dpiv, c[-1], tol)
    bs = base(W, wpiv)
    valid_base = bs is not None and bs["valid"]
    bo = None
    if valid_base:
        bo = breakout(o, h, l, c, v, bs["level"], int(W["last_idx"][bs["anchor"]]))
    r0, r1 = n - 1 - CONTRACT_RECENT[0], n - CONTRACT_RECENT[1]          # sessions t-14 .. t-5
    f0, f1 = n - 1 - CONTRACT_REF[0], n - CONTRACT_REF[1]                # sessions t-64 .. t-15
    tr = true_range(h, l, c)
    atr_ratio = float(tr[r0:r1].mean() / tr[f0:f1].mean())
    vol_ratio = float(v[r0:r1].mean() / v[f0:f1].mean()) if v[f0:f1].mean() > 0 else float("nan")
    ret = c[1:] / c[:-1] - 1.0
    dist = int(((ret[-DIST_N:] <= DIST_DROP) & (v[1:][-DIST_N:] > v[:-1][-DIST_N:])).sum())
    cands = []
    if sup is not None:
        cands.append(math.exp(sup["hi"]))
    if tl_s is not None and tl_s["value"] < lc[-1]:
        cands.append(math.exp(tl_s["value"]))
    if bs is not None and valid_base and c[-1] > math.exp(bs["level"]):
        cands.append(math.exp(bs["level"]))                              # broken base pivot = support (role flip)
    lows = [p for i, t, p in dpiv if t == "L"]
    if lows and lows[-1] < lc[-1]:
        cands.append(math.exp(lows[-1]))                                 # the most recent confirmed swing low below
    #                                                                      the close (stop under the last pullback)
    support = max(cands) if cands else None
    risk = (1.0 - support / c[-1]) if support is not None else None
    gaps = o[-GAP_N:] / c[-GAP_N - 1:-1]
    C = dict(
        W1=bool(W["c"][-1] > ma30w[-1]),
        W2=bool(ma40w[-1] > ma40w[-1 - MA_SLOPE_W]),
        W3=bool(ma10w[-1] > ma30w[-1]),
        W4=wstate in ("strong_uptrend", "uptrend"),
        W5=bool(c[-1] >= NEAR_HIGH * hi52),
        B1=bool(valid_base),
        B2=bool(valid_base and bs["depth"] <= BASE_MAX_DEPTH),
        B3=bool(valid_base and atr_ratio <= CONTRACT_MAX),
        B4=bool(valid_base and vol_ratio <= CONTRACT_MAX),
        B5=bool(valid_base and bs["contracting"]),
        T1=bo is not None,
        T2=bool(bo is not None and bo["ext"] <= BO_MAX_EXT),
        T3=bool(bo is not None and bo["relvol"] >= BO_VOL),
        T4=bool(bo is not None and bo["clv"] >= BO_CLV),
        T5=bool(c[-1] > ma50[-1]),
        R1=bool(risk is not None and risk <= RISK_MAX),
        R2=bool(risk is not None and risk <= RISK_ATR * atrp),
        R3=bool((c[-1] / ma20[-1] - 1.0) / atrp <= EXT_MA20_ATR),
        R4=bool(dist <= DIST_MAX),
        R5=dstate in ("strong_uptrend", "uptrend", "range"),
    )
    D = dict(
        D1=bool(W["c"][-1] < ma40w[-1]),
        D2=wstate == "downtrend",
        D3=bool(c[-1] > (1.0 + EXT_MA50_DQ) * ma50[-1]),
        D4=support is None,
        D5=bool(np.any(gaps <= GAP_DQ)),
    )
    cat = {k: int(sum(C[x] for x in CONDITIONS if x[0] == k)) for k in "WBTR"}
    return dict(
        conditions=C, disqualifiers=D, categories=cat, score=int(sum(C.values())), disqualified=bool(any(D.values())),
        weekly_state=wstate, daily_state=dstate, base=bs, breakout=bo, support=support, risk=risk,
        atr_pct=float(atrp), atr_ratio=atr_ratio, vol_ratio=vol_ratio, distribution_days=dist,
        zones_daily=dz, resistance=res, support_zone=sup, zones_weekly=wz, weekly_resistance=wres, weekly_support=wsup,
        trend_support=tl_s, trend_resistance=tl_r, pivots_daily=dpiv, pivots_weekly=wpiv,
        ma=dict(ma20=float(ma20[-1]), ma50=float(ma50[-1]), ma200=float(ma200[-1]), ma10w=float(ma10w[-1]),
                ma30w=float(ma30w[-1]), ma40w=float(ma40w[-1]), ma40w_4ago=float(ma40w[-1 - MA_SLOPE_W])),
        hi52=float(hi52), weeks=int(nw), sessions=int(n),
        base_start_day=(int(W["last_idx"][bs["anchor"]]) if valid_base else None))


def quality_level(snap):
    """Q for validation: -1 if disqualified, else the score 0..20."""
    return -1 if snap["disqualified"] else snap["score"]


def score_group(snap):
    """Pre-declared groups: G0 = disqualified, G1 = 0-5, G2 = 6-10, G3 = 11-15, G4 = 16-20."""
    if snap["disqualified"]:
        return 0
    s = snap["score"]
    return 1 if s <= 5 else (2 if s <= 10 else (3 if s <= 15 else 4))


def snapshot_at(bars, t):
    """The snapshot a decision at bar t may compute: bars 0..t only (the PIT cut used by the leakage canaries and by the
    host). bars = dict with o, h, l, c, v, week_id arrays."""
    s = slice(0, t + 1)
    return snapshot(*(np.asarray(bars[k])[s] for k in ("o", "h", "l", "c", "v")), np.asarray(bars["week_id"])[s])


def canonical(x):
    """A snapshot (or any part of it) as plain JSON-able data: dict keys sorted, floats as 12-significant-digit strings
    (stable across platforms), NaN / inf as strings. digest() hashes it."""
    if isinstance(x, dict):
        return {str(k): canonical(x[k]) for k in sorted(x)}
    if isinstance(x, (list, tuple)):
        return [canonical(y) for y in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return "%.12g" % float(x)
    return x


def digest(snap):
    import hashlib
    import json
    return hashlib.sha256(json.dumps(canonical(snap), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
