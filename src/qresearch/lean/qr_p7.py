# qr_p7.py — Phase 7 (Multi-Factor Conviction Score) DATA / FIDELITY AUDIT helpers (P7-CP1, D165). Pure numpy, no
# QuantConnect imports (tests/test_p7_features.py, tests/test_p7_canaries.py). AUDIT ONLY: candidate technical
# features are computed to verify that they CAN be computed correctly and point-in-time; no return after a decision
# date, no ranking, no score, no threshold is computed anywhere in this module.
#
# Panel convention (rows = market sessions, columns = securities; NaN = no bar):
#   C, H, L  split-adjusted close / high / low (RAW x the split feed: the CHART series; not dividend-adjusted)
#   V        split-adjusted volume (RAW volume / split factor), so C * V = the raw dollar volume of the day
#   P        total-return close (RAW x split x dividend-feed factors: the TOTAL-RETURN series)
# Each feature of a security at decision row t is computed on that security's OWN VALID BARS up to and including row t
# (bar-based windows; a session without a bar is skipped, never filled). Every feature is a ratio of prices of one
# security inside a window ending at t, so factors dated after t cancel: the value equals the one a point-in-time
# computation on the history known at t gives (verified by the truncation canary).
import hashlib
import math

import numpy as np

FEATURES = ("sma50_ratio", "sma200_ratio", "sma50_over_sma200", "high252_ratio", "low252_ratio", "mom_12_1",
            "mom_6_1", "atr14_ratio", "vol60", "adv20_usd", "last_bar_age")
# bars of the security's own history a feature needs (inclusive of the bar at t)
MIN_BARS = dict(sma50_ratio=50, sma200_ratio=200, sma50_over_sma200=200, high252_ratio=252, low252_ratio=252,
                mom_12_1=253, mom_6_1=127, atr14_ratio=15, vol60=61, adv20_usd=20, last_bar_age=1)
SKIP = 21                      # momentum skip (bars)
LIFE_GAP = 60                  # P7-CP1 (D167): more than this many missing sessions between two bars starts a NEW
                               # security life; windows never reach back across it (QuantConnect ticker-based ids
                               # can carry two companies' histories joined across a long gap, e.g. GDI 2013 / 2017)
MAX_LAST_BAR_AGE = 5           # a security whose last bar is older than this many sessions at t is 'stale'


def life_starts(v, gap=LIFE_GAP):
    """v: sorted valid rows. Returns, for each valid bar, the index (into v) of the first bar of its life."""
    v = np.asarray(v)
    st = np.zeros(v.size, dtype=int)
    for i in range(1, v.size):
        st[i] = i if v[i] - v[i - 1] - 1 > gap else st[i - 1]
    return st


def valid_rows(*cols):
    m = np.ones(len(cols[0]), bool)
    for c in cols:
        c = np.asarray(c, float)
        m &= np.isfinite(c) & (c > 0)
    return np.flatnonzero(m)


# ----------------------------------------------------------------------------------------------- primary (vectorised)
def features_at(C, H, L, V, P, rows):
    """Primary implementation for ONE security: arrays over sessions, rows = decision rows (sorted). Returns
    {feature: array(len(rows))} (NaN where the security's own history is insufficient or it has no bar yet)."""
    C, H, L, V, P = (np.asarray(x, float) for x in (C, H, L, V, P))
    rows = np.asarray(rows, int)
    out = {f: np.full(rows.size, np.nan) for f in FEATURES}
    v = valid_rows(C, H, L, P)
    if v.size == 0:
        return out
    c, h, lo, p = C[v], H[v], L[v], P[v]
    dv = c * np.where(np.isfinite(V[v]), V[v], np.nan)
    cs = np.r_[0.0, np.cumsum(c)]
    lr = np.r_[np.nan, np.log(p[1:] / p[:-1])]
    prevc = np.r_[np.nan, c[:-1]]
    tr = np.maximum(h, prevc) - np.minimum(lo, prevc)
    pos = np.searchsorted(v, rows, side="right") - 1          # index of the last valid bar at or before t
    ls = life_starts(v)
    for k, b in enumerate(pos):
        if b < 0:
            continue
        n = b - ls[b] + 1                                      # bars available in the security's current life
        out["last_bar_age"][k] = rows[k] - v[b]
        last = c[b]
        if n >= 50:
            s50 = (cs[b + 1] - cs[b + 1 - 50]) / 50
            out["sma50_ratio"][k] = last / s50 - 1
        if n >= 200:
            s200 = (cs[b + 1] - cs[b + 1 - 200]) / 200
            out["sma200_ratio"][k] = last / s200 - 1
            out["sma50_over_sma200"][k] = s50 / s200 - 1
        if n >= 252:
            out["high252_ratio"][k] = last / h[b + 1 - 252:b + 1].max()
            out["low252_ratio"][k] = last / lo[b + 1 - 252:b + 1].min()
        if n >= 253:
            out["mom_12_1"][k] = p[b - SKIP] / p[b - 252] - 1
        if n >= 127:
            out["mom_6_1"][k] = p[b - SKIP] / p[b - 126] - 1
        if n >= 15:
            out["atr14_ratio"][k] = tr[b - 13:b + 1].mean() / last
        if n >= 61:
            out["vol60"][k] = lr[b - 59:b + 1].std()
        if n >= 20:
            w = dv[b - 19:b + 1]
            out["adv20_usd"][k] = w.mean() if np.isfinite(w).all() else np.nan
    return out


# ----------------------------------------------------------------------------------------------- independent (slow)
def features_slow(bars, sessions=None, gap=LIFE_GAP):
    """Independent implementation from a plain list of bars [(c, h, l, v, p)] of ONE security ending at the decision
    session (python loops, no cumulative sums, no shared code with features_at). `sessions` (optional, same length):
    each bar's session number, used to drop every bar before the last gap of more than `gap` missing sessions (the
    security-life rule). Returns {feature: value or None}."""
    out = {f: None for f in FEATURES}
    keep = [i for i, b in enumerate(bars) if all(x is not None and math.isfinite(x) and x > 0 for x in (b[0], b[1], b[2], b[4]))]
    if sessions is not None and keep:
        first = 0
        for a in range(len(keep) - 1, 0, -1):
            if sessions[keep[a]] - sessions[keep[a - 1]] - 1 > gap:
                first = a
                break
        keep = keep[first:]
    bars = [bars[i] for i in keep]
    n = len(bars)
    if n == 0:
        return out

    def mean(xs):
        t = 0.0
        for x in xs:
            t += x
        return t / len(xs)
    closes = [b[0] for b in bars]
    last = closes[-1]
    if n >= 50:
        out["sma50_ratio"] = last / mean(closes[-50:]) - 1
    if n >= 200:
        out["sma200_ratio"] = last / mean(closes[-200:]) - 1
        out["sma50_over_sma200"] = mean(closes[-50:]) / mean(closes[-200:]) - 1
    if n >= 252:
        out["high252_ratio"] = last / max(b[1] for b in bars[-252:])
        out["low252_ratio"] = last / min(b[2] for b in bars[-252:])
    if n >= 253:
        out["mom_12_1"] = bars[-1 - SKIP][4] / bars[-253][4] - 1
    if n >= 127:
        out["mom_6_1"] = bars[-1 - SKIP][4] / bars[-127][4] - 1
    if n >= 15:
        trs = []
        for i in range(n - 14, n):
            pc = bars[i - 1][0]
            trs.append(max(bars[i][1], pc) - min(bars[i][2], pc))
        out["atr14_ratio"] = mean(trs) / last
    if n >= 61:
        rs = [math.log(bars[i][4] / bars[i - 1][4]) for i in range(n - 60, n)]
        m = mean(rs)
        out["vol60"] = math.sqrt(mean([(r - m) ** 2 for r in rs]))
    if n >= 20:
        vs = [b[0] * b[3] for b in bars[-20:]]
        out["adv20_usd"] = mean(vs) if all(x is not None and math.isfinite(x) for x in vs) else None
    return out


def compare(a, b, rel_tol=1e-9):
    """(agree, max relative difference, mismatched feature names) between a primary and an independent value set;
    a None / NaN on one side and a value on the other is a mismatch."""
    worst, bad = 0.0, []
    for f in FEATURES:
        if f == "last_bar_age":
            continue
        x, y = a.get(f), b.get(f)
        xn = x is None or (isinstance(x, float) and not math.isfinite(x))
        yn = y is None or (isinstance(y, float) and not math.isfinite(y))
        if xn and yn:
            continue
        if xn != yn:
            bad.append(f)
            continue
        if f in ("sma50_ratio", "sma200_ratio", "sma50_over_sma200", "mom_12_1", "mom_6_1"):
            d = abs(x - y) / max(1.0, abs(y))           # values near 0: compare on the (1 + value) scale
        else:
            d = abs(x - y) / max(abs(y), 1e-12)
        worst = max(worst, d)
        if d > rel_tol:
            bad.append(f)
    return not bad, worst, bad


# ----------------------------------------------------------------------------------------------- breadth
def breadth(state, eligible):
    """Breadth on one date with a POINT-IN-TIME denominator. state: {sid: True/False/None} (None = insufficient
    history or stale); eligible: the securities eligible on that date. Returns (share above, n above, n with a
    state, n eligible, n insufficient). Securities that are not eligible on the date never enter."""
    n_el = len(eligible)
    up = known = 0
    for s in eligible:
        x = state.get(s)
        if x is None:
            continue
        known += 1
        up += int(bool(x))
    return (up / known if known else float("nan")), up, known, n_el, n_el - known


# ----------------------------------------------------------------------------------------------- sampling / stats
def pick(keys, k, salt):
    """Deterministic pseudo-random sample: the k keys with the smallest sha256(salt|key)."""
    return sorted(keys, key=lambda x: hashlib.sha256(f"{salt}|{x}".encode()).hexdigest())[:k]


def qstats(xs):
    xs = np.asarray([x for x in xs if x is not None and math.isfinite(x)], float)
    if xs.size == 0:
        return dict(n=0)
    return dict(n=int(xs.size), median=float(np.median(xs)), p95=float(np.quantile(xs, 0.95)),
                max=float(xs.max()), min=float(xs.min()))


# ----------------------------------------------------------------------------------------------- fundamentals
FUND_FIELDS = ("revenue_ttm4q", "gross_profit_ttm4q", "net_income_ttm4q", "operating_cash_flow_ttm4q",
               "total_assets", "stockholders_equity")
# coverage combinations reported by the audit (availability only; definitions fixed before any real data was seen)
COMBOS = {
    "technical_only": (),
    "tech+profitability_NI": ("net_income_ttm4q", "total_assets"),
    "tech+profitability_GP": ("gross_profit_ttm4q", "total_assets"),
    "tech+profitability_NI+cashflow": ("net_income_ttm4q", "total_assets", "operating_cash_flow_ttm4q"),
    "tech+profitability_NI+balance_sheet": ("net_income_ttm4q", "total_assets", "stockholders_equity"),
    "tech+all_core": ("revenue_ttm4q", "net_income_ttm4q", "operating_cash_flow_ttm4q", "total_assets",
                      "stockholders_equity"),
    "tech+all_core+GP": FUND_FIELDS,
}


def combos(have):
    """{combo: bool} for a set of available field names (technical availability is checked separately)."""
    return {k: all(f in have for f in req) for k, req in COMBOS.items()}


# ----------------------------------------------------------------------------------------------- cross-domain
def alignment(t, **dates):
    """One coherent point-in-time snapshot: every component date (ISO strings or None) must be <= t. Returns
    (ok, [components dated after t])."""
    late = [k for k, d in dates.items() if d is not None and str(d) > str(t)]
    return not late, late


# ----------------------------------------------------------------------------------------------- daily breadth states
def calendar_states(C, H, L, max_age=MAX_LAST_BAR_AGE):
    """For ONE security, states on EVERY calendar row (same definitions as features_at, from the last valid bar at
    or before the row): nbars (own bars so far), age (sessions since that bar), above50 / above200 (close > SMA;
    NaN if fewer bars than the window or the last bar is older than max_age), new_high / new_low (that bar's
    high / low is the 252-bar extreme; NaN if < 252 bars or stale). Used for breadth with point-in-time
    denominators; computed in one pass."""
    C, H, L = (np.asarray(x, float) for x in (C, H, L))
    D = C.size
    out = {k: np.full(D, np.nan) for k in ("nbars", "age", "above50", "above200", "new_high", "new_low")}
    v = valid_rows(C, H, L)
    if v.size == 0:
        return out
    c, h, lo = C[v], H[v], L[v]
    n = c.size
    cs = np.r_[0.0, np.cumsum(c)]
    ls = life_starts(v)
    idx = np.arange(n)
    nlife = idx - ls + 1                                      # bars in the current life
    s50 = np.full(n, np.nan)
    s200 = np.full(n, np.nan)
    s50[49:] = (cs[50:] - cs[:-50]) / 50
    s200[199:] = (cs[200:] - cs[:-200]) / 200
    s50[nlife < 50] = np.nan
    s200[nlife < 200] = np.nan
    a50 = np.where(np.isfinite(s50), (c > s50).astype(float), np.nan)
    a200 = np.where(np.isfinite(s200), (c > s200).astype(float), np.nan)
    hmax = np.full(n, np.nan)
    lmin = np.full(n, np.nan)
    from collections import deque
    dq, dl = deque(), deque()
    for i in range(n):
        if ls[i] == i:                                        # a new life: forget the previous one
            dq.clear()
            dl.clear()
        while dq and h[dq[-1]] <= h[i]:
            dq.pop()
        dq.append(i)
        while dl and lo[dl[-1]] >= lo[i]:
            dl.pop()
        dl.append(i)
        if dq[0] <= i - 252:
            dq.popleft()
        if dl[0] <= i - 252:
            dl.popleft()
        if nlife[i] >= 252:
            hmax[i], lmin[i] = h[dq[0]], lo[dl[0]]
    nh = np.where(np.isfinite(hmax), (h >= hmax).astype(float), np.nan)
    nl = np.where(np.isfinite(lmin), (lo <= lmin).astype(float), np.nan)
    pos = np.searchsorted(v, np.arange(D), side="right") - 1
    ok = pos >= 0
    p = np.where(ok, pos, 0)
    age = np.where(ok, np.arange(D) - v[p], np.nan)
    fresh = ok & (age <= max_age)
    out["nbars"] = np.where(ok, nlife[p], np.nan)
    out["age"] = age
    for k, arr in (("above50", a50), ("above200", a200), ("new_high", nh), ("new_low", nl)):
        out[k] = np.where(fresh, arr[p], np.nan)
    return out
