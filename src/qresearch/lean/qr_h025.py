# H025 Insider Cluster Buying: pure in-host logic (owner D204; research/phase10/H025_spec.md, frozen). numpy only, no
# QuantConnect import: the same file is unit-tested offline (tests/test_p10_h025.py) and uploaded to the host S027.
#   * ledger rows (the packed SEC event ledger, qr_h025_events) -> events;
#   * review choice (the latest Data v2 monthly review strictly before the trigger date), identity (issuer CIK = the
#     Data v2 verified identity CIK of an eligible security at that review), multi-class rule;
#   * responses: TSR from the entry-session open to the 20th-session close with the verified split x dividend
#     multiplier (qr_p7_pred.response conventions), SPY TSR over the identical rows, excess = stock - SPY;
#   * matched null (FF12 x market-cap quintile cell, deterministic fallback), monthly series, Newey-West t (lag 2),
#     c_EVENT, gates G1-G5, diagnostics.
import csv
import hashlib
import io
import json
import math
import numpy as np

HOLD = 20
DIAG_HORIZONS = (5, 10, 40, 60)
NW_LAG = 2
R_NULL = 5000
ALPHA = 0.01
C_FLOOR = 2.326
G2_MIN = 0.02
MIN_EVENTS = 100
MIN_YEAR_EVENTS = 10
MIN_YEARS = 5
YEARS = tuple(range(2011, 2018))
FIRST_HALF = (2011, 2014)
SECOND_HALF = (2015, 2017)
MIN_POSITIVE_YEARS = 5
N_Q = 5
STATUS = ("ELIGIBLE", "ELIGIBLE_MULTICLASS", "NOT_ELIGIBLE", "IDENTITY_UNRESOLVED", "OUT_OF_WINDOW", "NO_REVIEW")


def cik_key(c):
    """Canonical CIK text (leading zeros dropped); None stays None."""
    if c is None:
        return None
    t = str(c).strip()
    return str(int(t)) if t.isdigit() else t


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def read_ledger(text):
    """Packed ledger CSV -> list of dicts (types restored)."""
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        r = dict(r)
        r["issuer_cik"] = cik_key(r["issuer_cik"])
        r["n_insiders"] = int(r["n_insiders"])
        r["cluster_value"] = float(r["cluster_value"])
        r["ceo_cfo"] = int(r["ceo_cfo"])
        r["director_only"] = int(r["director_only"])
        r["n_qualifying_filings"] = int(r["n_qualifying_filings"])
        r["median_delay_days"] = float(r["median_delay_days"])
        r["near_cluster"] = int(r["near_cluster"])
        out.append(r)
    return out


# ----------------------------------------------------------------------------------------------- review / identity
def latest_review(reviews, trigger_date):
    """The latest review date strictly before the trigger date (reviews: sorted ISO strings or dates), or None."""
    best = None
    for t in reviews:
        if str(t) < str(trigger_date):
            best = t
        else:
            break
    return best


def map_issuer(issuer_cik, elig_cik, adv, unresolved_symbols=None, symbol=None):
    """Identity of one event at its review. elig_cik: {sid: CIK string or None} for the ELIGIBLE securities at the
    review (Data v2 verified identity at the review); adv: {sid: ADV20}. Returns (status, sid or None).
    ELIGIBLE: exactly one eligible security carries the issuer CIK. ELIGIBLE_MULTICLASS: several (share classes) ->
    the one with the highest ADV20 (ties: smallest sid). NOT_ELIGIBLE: none, and no eligible security without a verified
    identity carries the as-filed symbol. IDENTITY_UNRESOLVED: none carries the CIK but an eligible security WITHOUT a
    verified identity carries the as-filed symbol (possible identity gap; excluded and reported, never mapped)."""
    key = cik_key(issuer_cik)
    hits = sorted(s for s, c in elig_cik.items() if c is not None and cik_key(c) == key)
    if len(hits) == 1:
        return "ELIGIBLE", hits[0]
    if len(hits) > 1:
        best = sorted(hits, key=lambda s: (-float(adv.get(s) or 0.0), s))[0]
        return "ELIGIBLE_MULTICLASS", best
    if unresolved_symbols and symbol and symbol in unresolved_symbols:
        return "IDENTITY_UNRESOLVED", None
    return "NOT_ELIGIBLE", None


def quintiles(mcap):
    """Market-cap quintile 1..5 by average rank among valid values (qr_p7_pred convention); invalid -> 0."""
    x = np.asarray(mcap, float)
    q = np.zeros(x.size, dtype=np.int64)
    ok = np.isfinite(x) & (x > 0)
    n = int(ok.sum())
    if n == 0:
        return q
    v = x[ok]
    order = np.argsort(v, kind="mergesort")
    r = np.empty(n)
    sv = v[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sv[j + 1] == sv[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    q[ok] = np.minimum(N_Q, np.floor(N_Q * (r - 0.5) / n).astype(np.int64) + 1)
    return q


# ----------------------------------------------------------------------------------------------- responses
def tsr(raw_open, raw_close, mult, e0, x0, unverified_rows=()):
    """TSR of one security bought at the open of row e0 and held to the close of row x0 (inclusive), the conventions
    of qr_p7_pred.response with t = e0 - 1, t_next = x0: entry = the first row in [e0, x0] with a valid open and close;
    exit = the close of x0, else the last real close in [entry, x0] (status 'truncated'); no bar -> 0.0 'no_bar';
    an unverified split in [e0, x0] -> NaN 'unverified_split'. Returns (value, status, entry_row, exit_row)."""
    O, C, m = (np.asarray(a, float) for a in (raw_open, raw_close, mult))
    if any(e0 <= int(u) <= x0 for u in unverified_rows):
        return float("nan"), "unverified_split", None, None
    rows = np.arange(e0, x0 + 1)
    ok = np.isfinite(O[rows]) & (O[rows] > 0) & np.isfinite(C[rows]) & (C[rows] > 0)
    if not ok.any():
        return 0.0, "no_bar", None, None
    e = int(rows[np.argmax(ok)])
    okc = np.isfinite(C[e:x0 + 1]) & (C[e:x0 + 1] > 0)
    x = e + int(np.flatnonzero(okc)[-1])
    return float((C[x] * m[x]) / (O[e] * m[e]) - 1.0), ("ok" if x == x0 else "truncated"), e, x


def excess(stock, spy_open, spy_close, spy_mult, e0, x0, unverified_rows=()):
    """(stock TSR - SPY TSR, stock TSR, SPY TSR, status). SPY is bought at the open of the stock's own entry row and
    held to the close of the PLANNED exit row x0 (a stock that stops trading early is cash afterwards: its TSR ends at
    its last real close while SPY runs to x0). No stock bar in the window or an unverified split -> NaN (the event is
    not evaluable; counted)."""
    v, st, e, x = tsr(stock[0], stock[1], stock[2], e0, x0, unverified_rows)
    if st == "unverified_split" or e is None:
        return float("nan"), float("nan"), float("nan"), st
    s = float((spy_close[x0] * spy_mult[x0]) / (spy_open[e] * spy_mult[e]) - 1.0)
    return v - s, v, s, st


# ----------------------------------------------------------------------------------------------- statistics
def nw_t(x, lag=NW_LAG):
    """(mean, se, t) with a Bartlett-kernel Newey-West standard error (qr_xs.nw_tstat convention)."""
    x = np.asarray(x, float)
    T = x.size
    if T < 2:
        return (float(x.mean()) if T else float("nan")), float("nan"), 0.0
    m = x.mean()
    e = x - m
    lrv = float(e @ e) / T
    for l in range(1, min(lag, T - 1) + 1):
        lrv += 2.0 * (1.0 - l / (lag + 1.0)) * float(e[l:] @ e[:-l]) / T
    se = math.sqrt(max(lrv, 0.0) / T)
    return float(m), se, (float(m) / se if se > 0 else 0.0)


def month_index(months):
    """Sorted unique months ('YYYY-MM') and the index of every event."""
    u = sorted(set(months))
    pos = {m: i for i, m in enumerate(u)}
    return u, np.array([pos[m] for m in months], dtype=np.int64)


def monthly_series(y, idx, n_months):
    s = np.bincount(idx, weights=y, minlength=n_months)
    c = np.bincount(idx, minlength=n_months)
    return s / c


def primary(y, idx, n_months):
    """Primary statistic of one assignment: t of the monthly mean-excess series (months without events omitted)."""
    return nw_t(monthly_series(y, idx, n_months))[2]


def summary(y, months, years):
    """Every gated quantity of one set of event excess returns (y aligned with months 'YYYY-MM' and years)."""
    y = np.asarray(y, float)
    years = np.asarray(years, dtype=np.int64)
    u, idx = month_index(list(months))
    ser = monthly_series(y, idx, len(u))
    m, se, t = nw_t(ser)
    by_year = {}
    for yr in YEARS:
        k = years == yr
        by_year[str(yr)] = dict(n=int(k.sum()), mean=float(y[k].mean()) if k.any() else None)
    h1 = (years >= FIRST_HALF[0]) & (years <= FIRST_HALF[1])
    h2 = (years >= SECOND_HALF[0]) & (years <= SECOND_HALF[1])
    return dict(n=int(y.size), mean=float(y.mean()), median=float(np.median(y)), win_rate=float((y > 0).mean()),
                months=len(u), monthly_mean=m, monthly_se=se, t=t, by_year=by_year,
                first_half=float(y[h1].mean()) if h1.any() else None,
                second_half=float(y[h2].mean()) if h2.any() else None,
                positive_years=sum(1 for v in by_year.values() if v["mean"] is not None and v["mean"] > 0),
                years_ge_10=sum(1 for v in by_year.values() if v["n"] >= MIN_YEAR_EVENTS))


def gates(s, c_event):
    g1 = s["t"] > c_event and s["mean"] > 0
    g2 = s["mean"] >= G2_MIN
    g3 = s["median"] > 0 and s["win_rate"] > 0.5
    g4 = (s["first_half"] is not None and s["first_half"] > 0 and s["second_half"] is not None
          and s["second_half"] > 0 and s["positive_years"] >= MIN_POSITIVE_YEARS)
    g5 = s["n"] >= MIN_EVENTS and s["years_ge_10"] >= MIN_YEARS
    return dict(G1=bool(g1), G2=bool(g2), G3=bool(g3), G4=bool(g4), G5=bool(g5),
                all=bool(g1 and g2 and g3 and g4 and g5))


def critical_value(null_t, alpha=ALPHA, floor=C_FLOOR):
    """c_EVENT = max(k-th largest null t, floor), k = ceil(alpha x R) (= the 50th largest of 5,000)."""
    v = np.sort(np.asarray(null_t, float))[::-1]
    k = max(1, int(math.ceil(alpha * v.size)))
    return float(max(v[k - 1], floor)), float(v[k - 1])


def sample_ok(n_by_year, n_total):
    return n_total >= MIN_EVENTS and sum(1 for v in n_by_year.values() if v >= MIN_YEAR_EVENTS) >= MIN_YEARS


# ----------------------------------------------------------------------------------------------- matched null
def match_pool(ev_sid, ev_cik, ev_sector, ev_q, cand):
    """Control candidates of one event: cand = list of (sid, cik, sector, quintile, blocked) for the eligible securities
    at the event's review with a finite response over the event window; blocked = True when the security has an H025
    cluster event (any, from the SEC ledger by verified CIK) whose entry is within HOLD - 1 sessions of this event's
    entry; candidates without a verified identity CIK never enter a pool. Hierarchy (frozen): L1 same FF12 and quintile; L2 same FF12, nearest quintile (distance 1, 2, .., lower
    quintile first at equal distance); L3 same quintile, any sector; L4 any eligible. Never the issuer itself (sid or
    CIK). Returns (level, sorted sids)."""
    base = [(s, sec, q) for s, c, sec, q, b in cand
            if s != ev_sid and not b and c is not None and cik_key(c) != cik_key(ev_cik)]
    p = sorted(s for s, sec, q in base if sec == ev_sector and q == ev_q and q > 0)
    if p:
        return "L1", p
    same = [(s, q) for s, sec, q in base if sec == ev_sector]
    if same and ev_q > 0:
        for d in range(1, N_Q):
            for qq in (ev_q - d, ev_q + d):
                p = sorted(s for s, q in same if q == qq)
                if p:
                    return "L2", p
    p = sorted(s for s, sec, q in base if q == ev_q and q > 0)
    if p:
        return "L3", p
    return "L4", sorted(s for s, sec, q in base)


def null_draw(pool_sizes, seed):
    """Index of the control drawn for every event in world `seed` (uniform within each pool; numpy PCG64 seeded with
    (seed, 25)). Deterministic for a given seed and pool sizes."""
    rng = np.random.Generator(np.random.PCG64([int(seed), 25]))
    u = rng.random(len(pool_sizes))
    n = np.asarray(pool_sizes, dtype=np.int64)
    return np.minimum((u * n).astype(np.int64), n - 1)


def null_world(pools_y, idx, n_months, seed, years=None, months=None):
    """One null world: every event's excess replaced by its drawn control's excess. pools_y: list of 1-D arrays."""
    d = null_draw([p.size for p in pools_y], seed)
    y = np.array([p[k] for p, k in zip(pools_y, d)])
    t = primary(y, idx, n_months)
    return dict(seed=int(seed), t=t, mean=float(y.mean()), median=float(np.median(y)), win=float((y > 0).mean()),
                draws_sha=hashlib.sha256(d.tobytes()).hexdigest()[:16])
