# qr_os1 v1.0 — H032 / OS-1 revised (owner D278; research/os/H032_spec.md, frozen and SHA-256-pinned in
# qresearch.os1). Pure logic on plain records: no QuantConnect object, no I/O. STRICTLY POINT-IN-TIME: at a review
# day t it uses only SEC rows filed strictly before t (the UCR-1 object + the H032 extension object) and QuantConnect
# values observed on or before t.
#   identity   unique point-in-time registrant <-> QuantConnect security match (the UCR-1 rules, applied to every row)
#   sic        SIC of the registrant's latest periodic filing filed before t; financials = SIC 6000-6799
#   nsi        12-month split-adjusted net share issuance from cover-page counts; OS = -NSI (more repurchase = higher)
#   annual     F-OCF / F-REV inputs from the latest original 10-K / 10-KT filed before t (same-filing comparative)
#   plan       Top-N with a 2N retention buffer; random, filter-pool random and beta-matched control books
import bisect
import hashlib
import math
from datetime import date

import numpy as np
import qr_ucr as U

N = 15
BUFFER = 2 * N
PAIR_TOL = 45                    # old cover count: as-of date within 45 days of (new as-of date - 365)
NSI_BOUND = (2.0 / 3.0, 1.5)     # S1 / split-adjusted S0 outside -> missing (unit errors, split-date mismatches)
FY_STALE = 456                   # latest annual report: period end at most 456 days before t
FIN_SIC = (6000, 6799)           # H032 scope: financials and REITs excluded
COV_START, COV_MIN = 0.70, 0.65  # G-COV1: start at the first review >= 70% joint coverage; then >= 65% every review
GAP_MAX = 0.10                   # G-COV2 / G-COV3: coverage gap limit (fraction)
EXIT_MONTHS = 24                 # G-COV2: 'later disappearing' = last stream day before review + 24 months
BETA_DAYS, BETA_MIN = 252, 200   # ex-ante beta vs SPY: last 252 sessions, at least 200 paired daily returns
MOM_BACK, MOM_SKIP = 12, 1       # 12-1 momentum from review-day adjusted prices
SUB_A_END = (2015, 12)           # subperiod boundary fixed by the owner (A = start .. 2015-12, B = 2016-01 ..)
SHORT_A_MONTHS = 36              # subperiod A shorter than this -> reported SHORT, STOP for the owner (D278 item 4)
SEEDS_B2 = (20261121, 20261122, 20261123, 20261124, 20261125)
SEEDS_RND = (20261131, 20261132, 20261133, 20261134, 20261135)
SEEDS_BETA = (20261141, 20261142, 20261143, 20261144, 20261145)

FF12 = (                         # Fama-French 12 by SIC (copied from qr_xs_diag; data only)
    ("NoDur", ((100, 999), (2000, 2399), (2700, 2749), (2770, 2799), (3100, 3199), (3940, 3989))),
    ("Durbl", ((2500, 2519), (2590, 2599), (3630, 3659), (3710, 3711), (3714, 3714), (3716, 3716), (3750, 3751),
               (3792, 3792), (3900, 3939), (3990, 3999))),
    ("Manuf", ((2520, 2589), (2600, 2699), (2750, 2769), (3000, 3099), (3200, 3569), (3580, 3629), (3700, 3709),
               (3712, 3713), (3715, 3715), (3717, 3749), (3752, 3791), (3793, 3799), (3830, 3839), (3860, 3899))),
    ("Enrgy", ((1200, 1399), (2900, 2999))),
    ("Chems", ((2800, 2829), (2840, 2899))),
    ("BusEq", ((3570, 3579), (3660, 3692), (3694, 3699), (3810, 3829), (7370, 7379))),
    ("Telcm", ((4800, 4899),)),
    ("Utils", ((4900, 4949),)),
    ("Shops", ((5000, 5999), (7200, 7299), (7600, 7699))),
    ("Hlth", ((2830, 2839), (3693, 3693), (3840, 3859), (8000, 8099))),
    ("Money", ((6000, 6999),)),
)


def ff12(sic):
    if sic is None:
        return "Unclassified"
    s = int(sic)
    for name, ranges in FF12:
        if any(a <= s <= b for a, b in ranges):
            return name
    return "Other"


def financial(sic):
    return sic is not None and FIN_SIC[0] <= int(sic) <= FIN_SIC[1]


def ordinal(iso):
    return date.fromisoformat(iso).toordinal()


def add_months(o, k):
    d = date.fromordinal(o)
    m = d.month - 1 + k
    y, m = d.year + m // 12, m % 12 + 1
    for day in (d.day, 30, 29, 28):
        try:
            return date(y, m, day).toordinal()
        except ValueError:
            continue


class Ext:
    """The H032 extension object, aligned with qr_ucr.RepairRef: per registrant the SIC of every periodic filing
    (parallel to the UCR-1 filing list) and the original annual reports [filed, period_end, ocf, rev, rev_prior]."""

    def __init__(self, ext_doc, ref):
        self.sic, self.k_day, self.k = [], [], []
        for c in ref.ciks:
            e = ext_doc["r"][c]
            self.sic.append(list(e["s"]))
            rows = sorted(((ordinal(r[0]), r) for r in e["k"]), key=lambda x: x[0])
            self.k_day.append([a for a, _ in rows])
            self.k.append([r for _, r in rows])
        for i, c in enumerate(ref.ciks):
            if len(self.sic[i]) != len(ref.p_day[i]):
                raise ValueError(f"extension SIC list not parallel to the UCR-1 filings of CIK {c}")
        self.pit_violations = 0

    def sic_at(self, ref, i, t):
        j = bisect.bisect_left(ref.p_day[i], t) - 1
        if j < 0:
            return None
        if ref.p_day[i][j] >= t:
            self.pit_violations += 1
        return self.sic[i][j]

    def annual(self, i, t):
        """(ocf, growth, reason_ocf, reason_rev) from the latest original annual report filed before t."""
        q = bisect.bisect_left(self.k_day[i], t) - 1
        if q < 0:
            return None, None, "no_annual_report", "no_annual_report"
        filed = self.k_day[i][q]
        if filed >= t:
            self.pit_violations += 1
        r = self.k[i][q]
        if r[1] is None:
            return None, None, "no_period", "no_period"
        pe = ordinal(r[1])
        if pe >= filed:
            return None, None, "period_not_before_filing", "period_not_before_filing"
        if t - pe > FY_STALE:
            return None, None, "stale", "stale"
        ocf = r[2]
        ro = None if ocf is not None else "no_ocf"
        rev, prior = r[3], r[4]
        if rev is None:
            g, rr = None, "no_current_revenue"
        elif prior is None:
            g, rr = None, "no_same_filing_comparative"
        elif not prior > 0:
            g, rr = None, "prior_not_positive"
        else:
            g, rr = rev / prior - 1.0, None
        return ocf, g, ro, rr


class Splits:
    """QuantConnect split factor per security, recorded from the universe stream (stamp o = the day after the session
    it reflects). F(key, d) = the factor in effect at the close of day d, or None if the security was not yet seen."""

    def __init__(self):
        self.o, self.v = {}, {}

    def observe(self, key, o, sf):
        if not (sf == sf and sf > 0):
            return
        v = self.v.get(key)
        if v is None:
            self.o[key], self.v[key] = [o], [sf]
        elif abs(sf / v[-1] - 1.0) > 1e-9:
            self.o[key].append(o)
            v.append(sf)

    def F(self, key, d):
        o = self.o.get(key)
        if not o:
            return None
        j = bisect.bisect_right(o, d + 1) - 1
        return None if j < 0 else self.v[key][j]


def identity(ref, t, rows):
    """{row index: registrant index} by the UCR-1 point-in-time rules (unique live common claim of the prefix, unique
    QuantConnect ticker, no class-share ticker) and the reason counts. rows: [(key, raw ticker)]."""
    why = {}
    claims = {}
    for i in range(len(ref.ciks)):
        cur = ref.current(i, t)
        if cur is None or not cur[0]:
            continue
        if not cur[1]:
            continue
        claims.setdefault(cur[0], []).append(i)
    tmap = {}
    for j, (key, raw) in enumerate(rows):
        n = U.norm(raw)
        if n:
            tmap.setdefault(n, []).append(j)
    out = {}
    for pref, regs in claims.items():
        js = tmap.get(pref)
        if not js:
            continue
        if len(regs) > 1:
            why["contested_prefix"] = why.get("contested_prefix", 0) + 1
            continue
        if len(js) > 1:
            why["ambiguous_qc_ticker"] = why.get("ambiguous_qc_ticker", 0) + 1
            continue
        j = js[0]
        if any(ch in str(rows[j][1]) for ch in ".-"):
            why["multi_class_ticker"] = why.get("multi_class_ticker", 0) + 1
            continue
        out[j] = regs[0]
    return out, why


def nsi_score(ref, i, t, splits, key):
    """(OS = -NSI or None, reason, split_adjusted). Cover counts filed strictly before t only."""
    sh = ref.shares(i, t)
    if sh is None:
        return None, "no_fresh_shares", False
    s1, e1 = sh
    if e1 >= t:
        return None, "cover_after_decision", False
    best = None
    for day, val, end in zip(ref.s_day[i], ref.s_val[i], ref.s_end[i]):
        if day >= t:
            break
        dev = abs(end - (e1 - 365))
        if dev <= PAIR_TOL and (best is None or dev < best[0]):
            best = (dev, val, end)
    if best is None:
        return None, "no_prior_count", False
    s0, e0 = best[1], best[2]
    if e1 <= e0 or not s0 > 0 or not s1 > 0:
        return None, "bad_pair", False
    f1, f0 = splits.F(key, e1), splits.F(key, e0)
    if f1 is None or f0 is None:
        return None, "split_unknown", False
    adj = abs(f1 / f0 - 1.0) > 1e-9
    ratio = s1 / (s0 * f1 / f0)
    if not NSI_BOUND[0] <= ratio <= NSI_BOUND[1]:
        return None, "bound_split" if adj else "bound", adj
    return -math.log(ratio) * 365.0 / (e1 - e0), None, adj


def classify(ref, ext, splits, t, key, i):
    """One eligible security at review t, matched to registrant i (None = no point-in-time identity) ->
    (sic, fin, os, nsi_reason, split_adjusted, ocf, growth, reason_ocf, reason_rev, covered, passed).
    fin: True financial / False non-financial / None unknown (no identity or no SIC). The H032 coverage denominator is
    every eligible security with fin not True; covered = identity, known non-financial SIC, NSI, OCF and same-filing
    revenue growth all present; passed = covered and OCF > 0 and growth > 0."""
    if i is None:
        return None, None, None, "no_identity", False, None, None, "no_identity", "no_identity", False, False
    sic = ext.sic_at(ref, i, t)
    fin = None if sic is None else financial(sic)
    os_, nr, adj = nsi_score(ref, i, t, splits, key)
    ocf, g, ro, rr = ext.annual(i, t)
    covered = fin is False and os_ is not None and ocf is not None and g is not None
    passed = covered and ocf > 0 and g > 0
    return sic, fin, os_, nr, adj, ocf, g, ro, rr, covered, passed


def order(scores):
    """Keys by score descending, then ADV20 descending, then key. scores: {key: (score, adv)}."""
    return sorted(scores, key=lambda k: (-scores[k][0], -scores[k][1], k))


def plan(scores, held, n=N, buffer=BUFFER):
    """Top-n with retention: holdings ranked <= buffer stay; free slots filled from the top. -> sorted new holdings."""
    ranked = order(scores)
    rank = {k: r + 1 for r, k in enumerate(ranked)}
    out = [k for k in sorted(held) if k in rank and rank[k] <= buffer]
    have = set(out)
    for k in ranked:
        if len(out) >= n:
            break
        if k not in have:
            out.append(k)
            have.add(k)
    return sorted(out)


def rng_for(seed, k, extra=0):
    return np.random.default_rng([int(seed), int(k), int(extra)])


def random_step(pool, held, n_new, seed, k, n=N):
    """Turnover-matched random book: holdings that left the pool exit; further holdings, drawn at random, exit until
    the book has replaced as many names as the scored book entered at this review (n_new); free slots are then filled
    by a seeded draw from the pool. -> sorted new holdings."""
    pool = sorted(pool)
    ps = set(pool)
    keep = [x for x in sorted(held) if x in ps]
    rng = rng_for(seed, k)
    extra = min(max(0, int(n_new) - (len(held) - len(keep))), len(keep))
    if extra > 0:
        drop = set(keep[int(x)] for x in rng.choice(len(keep), size=extra, replace=False))
        keep = [x for x in keep if x not in drop]
    taken = set(held)
    cand = [x for x in pool if x not in taken]
    m = min(n - len(keep), len(cand))
    if m <= 0:
        return sorted(keep)
    pick = rng.choice(len(cand), size=m, replace=False)
    return sorted(keep + [cand[int(x)] for x in sorted(pick)])


def beta_step(pairs, b1_new, quint, seed, k):
    """Beta-matched book: one control per B1 holding, drawn from the B1 name's ex-ante beta quintile at the review of
    the draw; a control leaves when its B1 partner leaves or when it leaves the quintile map (the covered pool), and
    is then redrawn. pairs: {b1 key: control key}. -> (new pairs, attempted, matched)."""
    b1 = set(b1_new)
    out = {b: c for b, c in pairs.items() if b in b1 and c in quint}
    held = set(out.values())
    attempted = matched = 0
    need = [b for b in sorted(b1) if b not in out]
    for idx, b in enumerate(need):
        attempted += 1
        q = quint.get(b)
        if q is None:
            continue
        cand = sorted(x for x, qq in quint.items() if qq == q and x not in held and x not in b1)
        if not cand:
            continue
        c = cand[int(rng_for(seed, k, idx).integers(len(cand)))]
        out[b] = c
        held.add(c)
        matched += 1
    return out, attempted, matched


def betas(P, m):
    """OLS betas of daily log returns vs SPY. P: (n, L) adjusted closes in session order (NaN = missing), m: (L,) SPY.
    A return pair counts when both closes of both series exist; < BETA_MIN pairs -> NaN."""
    P = np.asarray(P, float)
    m = np.asarray(m, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = np.diff(np.log(np.where(P > 0, P, np.nan)), axis=1)
        rm = np.diff(np.log(np.where(m > 0, m, np.nan)))
    ok = np.isfinite(rs) & np.isfinite(rm)[None, :]
    cnt = ok.sum(axis=1)
    x = np.where(ok, rm[None, :], 0.0)
    y = np.where(ok, rs, 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        mx, my = x.sum(1) / cnt, y.sum(1) / cnt
        cov = (x * y).sum(1) / cnt - mx * my
        var = (x * x).sum(1) / cnt - mx * mx
        b = cov / var
    return np.where((cnt >= BETA_MIN) & (var > 0), b, np.nan)


def quintiles(values):
    """{key: 1..5} by value ascending (ties by key)."""
    ks = sorted(values, key=lambda k: (values[k], k))
    n = len(ks)
    return {k: 1 + (r * 5) // n for r, k in enumerate(ks)} if n else {}


def momentum(p_back, p_skip):
    """12-1 momentum: adjusted close at the review one month back / at the review twelve months back - 1."""
    if p_back is None or p_skip is None or not (p_back > 0 and p_skip > 0) or p_back != p_back or p_skip != p_skip:
        return None
    return p_skip / p_back - 1.0


def coverage_start(cov):
    """Index of the first review with joint coverage >= COV_START, or None. cov: fractions in review order."""
    return next((j for j, c in enumerate(cov) if c is not None and c >= COV_START), None)


def digest(seq):
    h = hashlib.sha256()
    for k, keys in seq:
        h.update((f"{k}|" + ",".join(keys) + "\n").encode())
    return h.hexdigest()
