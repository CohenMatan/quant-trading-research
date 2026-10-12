# qr_h029a.py — H029-A Business Improvement data-feasibility audit (owner D227; research/phase14/H029A_audit_spec.md).
# Pure functions, no QuantConnect imports (unit-tested offline: tests/test_p14_h029a.py). DATA QUALITY ONLY: candidate
# values are built from the frozen Data v2.1 point-in-time store exactly as known on the selection day; aggregates are
# counts, quantiles and correlations among INPUT values. No price, return or performance quantity is used here.
import math

import numpy as np

GAP = (80, 100)                     # consecutive fiscal quarters (frozen qr_fundamentals.TTM_GAP_DAYS)
FY_TOL = 0.01                       # fiscal-year reconciliation (frozen qr_fundamentals.TTM_FY_TOLERANCE)
MAX_AGE = 200                       # freshness of the current report (frozen DEFAULT_MAX_AGE_DAYS)
SHARE_MAX_AGE = 135                 # SEC cover count age (frozen D111 / Data v2 rule)
YEAR_DAYS, YEAR_TOL = 365, 45       # F7: prior cover count about one year earlier
FORMS = ("F1", "F1Q", "F2", "F3", "F4A", "F4B", "F5A", "F5B", "F6", "F7", "F8")
FAMILIES = dict(F1=("F1", "F1Q"), F2=("F2",), F3=("F3",), F4=("F4A", "F4B"), F5=("F5A", "F5B"), F6=("F6",),
                F7=("F7",), F8=("F8",))
SPAN = dict(F1=9, F1Q=6, F2=8, F3=8, F4A=8, F4B=8, F5A=8, F5B=8, F6=8, F8=8)
BASES = ("revenue", "gross_profit", "operating_income", "net_income", "operating_cash_flow")
# reasons a form is invalid (index into WHY)
WHY = ("ok", "no_fresh_report", "short_history", "not_consecutive", "ttm_missing", "denominator", "field_missing",
       "no_identity", "no_cover_count", "no_prior_count")
W = {k: i for i, k in enumerate(WHY)}
TTM_WHY = ("ok", "fewer than four visible quarters", "stale", "quarters not consecutive", "missing quarterly value",
           "no fiscal-year reconciliation inside the window", "no_window")
# pathology bits (U_NF stock-months; descriptive only)
PATH = ("rev_nonpos", "ta_nonpos", "eq_nonpos", "tiny_rev", "tiny_ta", "rev_jump", "ta_jump", "ni_flip", "oi_flip",
        "sh_jump")
PB = {k: 1 << i for i, k in enumerate(PATH)}
PERIODS = (("2011-2014", 2011, 2014), ("2015-2017", 2015, 2017), ("2018-2021", 2018, 2021))
QS = (1, 5, 25, 50, 75, 95, 99)


# ----------------------------------------------------------------------------------------------- PIT history
def chain(recs, i, n):
    """The n consecutive quarterly records ending at index i (oldest first), or None (frozen PITStore._chain)."""
    if i - n + 1 < 0:
        return None
    seg = recs[i - n + 1:i + 1]
    for a, b in zip(seg, seg[1:]):
        if not (GAP[0] <= (b.period_end - a.period_end).days <= GAP[1]):
            return None
    return seg


def base_recs(hist, base, today):
    """Visible records for one base, exactly as PITStore.ttm_detail filters them."""
    return sorted((r for r in hist.values() if r.available <= today
                   and not (r.partial and r.values.get(base + "_q") is None)), key=lambda r: r.period_end)


def ttm_at(recs, idx, base):
    """(value, reason): the frozen PITStore.ttm_detail rules applied to the window ending at recs[idx] (the caller
    applies freshness to the newest window). No interpolation, no back-filling."""
    if len(recs) < 4 or idx < 3:
        return None, "fewer than four visible quarters"
    win = chain(recs, idx, 4)
    if win is None:
        return None, "quarters not consecutive"
    qs = [r.values.get(base + "_q") for r in win]
    if any(q is None for q in qs):
        return None, "missing quarterly value"
    for k in range(4):
        j = idx - k
        fy = recs[j].values.get(base + "_ttm")
        ch = chain(recs, j, 4)
        if fy is None or ch is None or j < 1:
            continue
        i = j - 1
        while i > 0 and recs[i].partial and recs[i].values.get(base + "_ttm") is None:
            i -= 1
        prev_fy = recs[i].values.get(base + "_ttm")
        if prev_fy is not None and abs(prev_fy - fy) <= 1e-9 * max(abs(fy), 1.0):
            continue
        vals = [r.values.get(base + "_q") for r in ch]
        if any(v is None for v in vals):
            continue
        if abs(sum(vals) - fy) <= FY_TOL * abs(fy):
            return sum(qs), "ok"
    return None, "no fiscal-year reconciliation inside the window"


class Window:
    """The visible full-report grid of one company at `today`, anchored on the store's current report q0."""

    def __init__(self, hist, current, today):
        self.today, self.ok = today, False
        self.grid = sorted((r for r in hist.values() if r.available <= today and not r.partial),
                           key=lambda r: r.period_end)
        self.hist, self.cache, self.recs = hist, {}, {}
        # PIT sanity: nothing in the store may be dated after today (each must be 0)
        self.viol = sum(1 for r in hist.values() if r.available > today)
        if current is None or (today - current.period_end).days > MAX_AGE:
            return
        idx = [i for i, r in enumerate(self.grid) if r.period_end == current.period_end]
        if not idx:
            return
        self.i0, self.q0, self.ok = idx[0], current, True

    def span(self, n):
        """'ok' / 'short_history' / 'not_consecutive' for n consecutive quarters ending at q0."""
        if self.i0 + 1 < n:
            return "short_history"
        return "ok" if chain(self.grid, self.i0, n) is not None else "not_consecutive"

    def rec(self, k):
        return self.grid[self.i0 - k]

    def ttm(self, base, k):
        key = (base, k)
        if key not in self.cache:
            pe = self.rec(k).period_end
            if base not in self.recs:
                self.recs[base] = base_recs(self.hist, base, self.today)
            rb = self.recs[base]
            j = [i for i, r in enumerate(rb) if r.period_end == pe]
            self.cache[key] = ttm_at(rb, j[0], base) if j else (None, "no_window")
        return self.cache[key]

    def snap(self, field, k):
        return self.rec(k).values.get(field)

    def q(self, base, k):
        return self.rec(k).values.get(base + "_q")


def _ratio_change(a0, d0, a4, d4):
    if None in (a0, d0, a4, d4):
        return None, "ttm_missing"
    if d0 <= 0 or d4 <= 0:
        return None, "denominator"
    return a0 / d0 - a4 / d4, "ok"


def candidates(w):
    """{form: (oriented value or None, reason)} for the fundamental forms (F7 is computed separately)."""
    out = {}
    if not w.ok:
        return {f: (None, "no_fresh_report") for f in FORMS if f != "F7"}
    for f in FORMS:
        if f == "F7":
            continue
        sp = w.span(SPAN[f])
        if sp != "ok":
            out[f] = (None, sp)
            continue
        T = lambda b, k: w.ttm(b, k)[0]  # noqa: E731
        if f == "F1":
            r0, r1, r4, r5 = T("revenue", 0), T("revenue", 1), T("revenue", 4), T("revenue", 5)
            out[f] = ((None, "ttm_missing") if None in (r0, r1, r4, r5) else
                      (None, "denominator") if r4 <= 0 or r5 <= 0 else ((r0 / r4 - 1.0) - (r1 / r5 - 1.0), "ok"))
        elif f == "F1Q":
            r0, r1, r4, r5 = (w.q("revenue", k) for k in (0, 1, 4, 5))
            out[f] = ((None, "field_missing") if None in (r0, r1, r4, r5) else
                      (None, "denominator") if r4 <= 0 or r5 <= 0 else ((r0 / r4 - 1.0) - (r1 / r5 - 1.0), "ok"))
        elif f in ("F2", "F3", "F4A"):
            num = dict(F2="gross_profit", F3="operating_income", F4A="operating_cash_flow")[f]
            out[f] = _ratio_change(T(num, 0), T("revenue", 0), T(num, 4), T("revenue", 4))
        elif f in ("F4B", "F5A", "F5B", "F8"):
            num = dict(F4B="operating_cash_flow", F5A="net_income", F5B="gross_profit", F8="revenue")[f]
            a0, a4 = T(num, 0), T(num, 4)
            t0, t4 = w.snap("total_assets", 0), w.snap("total_assets", 4)
            if None in (a0, a4):
                out[f] = (None, "ttm_missing")
            elif t0 is None or t4 is None:
                out[f] = (None, "field_missing")
            else:
                out[f] = _ratio_change(a0, t0, a4, t4)
        elif f == "F6":
            d0, d4 = w.snap("total_debt", 0), w.snap("total_debt", 4)
            t0, t4 = w.snap("total_assets", 0), w.snap("total_assets", 4)
            if None in (d0, d4, t0, t4):
                out[f] = (None, "field_missing")
            elif t0 <= 0 or t4 <= 0:
                out[f] = (None, "denominator")
            else:
                out[f] = (-(d0 / t0 - d4 / t4), "ok")
    return out


def pathology(w):
    """Pathology bits of one stock-month (descriptive; needs the 8-quarter span)."""
    bits = 0
    if not w.ok:
        return bits
    eq = w.snap("stockholders_equity", 0)
    if eq is not None and eq <= 0:
        bits |= PB["eq_nonpos"]
    if w.span(8) != "ok":
        return bits
    T = lambda b, k: w.ttm(b, k)[0]  # noqa: E731
    r0, r4 = T("revenue", 0), T("revenue", 4)
    t0, t4 = w.snap("total_assets", 0), w.snap("total_assets", 4)
    if r0 is None or r4 is None or r0 <= 0 or r4 <= 0:
        bits |= PB["rev_nonpos"]
    if (t0 is not None and t0 <= 0) or (t4 is not None and t4 <= 0):
        bits |= PB["ta_nonpos"]
    if r4 is not None and 0 < r4 < 1e7:
        bits |= PB["tiny_rev"]
    if t4 is not None and 0 < t4 < 5e7:
        bits |= PB["tiny_ta"]
    if r0 and r4 and r0 > 0 and r4 > 0 and abs(r0 / r4 - 1.0) > 0.5:
        bits |= PB["rev_jump"]
    if t0 and t4 and t0 > 0 and t4 > 0 and abs(t0 / t4 - 1.0) > 0.5:
        bits |= PB["ta_jump"]
    for b, key in (("net_income", "ni_flip"), ("operating_income", "oi_flip")):
        a, c = T(b, 0), T(b, 4)
        if a is not None and c is not None and a * c < 0:
            bits |= PB[key]
    return bits


def seasonality(w):
    """(qoq0, qoq4, yoy0) of log quarterly revenue and the same for quarterly gross margin (NaN when absent)."""
    nan = float("nan")
    out = [nan] * 6
    if not w.ok or w.span(6) != "ok":
        return out
    r = [w.q("revenue", k) for k in range(6)]
    g = [w.q("gross_profit", k) for k in range(6)]
    if all(x is not None and x > 0 for x in (r[0], r[1], r[4], r[5])):
        out[0], out[1], out[2] = math.log(r[0] / r[1]), math.log(r[4] / r[5]), math.log(r[0] / r[4])
    m = [g[k] / r[k] if g[k] is not None and r[k] is not None and r[k] > 0 else None for k in range(6)]
    if all(m[k] is not None for k in (0, 1, 4, 5)):
        out[3], out[4], out[5] = m[0] - m[1], m[4] - m[5], m[0] - m[4]
    return out


def ttm_reasons(w):
    """Frozen ttm_detail outcome at q0 per base (index into TTM_WHY) and whether TTM also exists at q4."""
    out, at4 = [], []
    for b in BASES:
        if not w.ok:
            out.append(TTM_WHY.index("stale"))
            at4.append(False)
            continue
        v, why = w.ttm(b, 0)
        out.append(TTM_WHY.index(why) if why in TTM_WHY else TTM_WHY.index("no_window"))
        at4.append(w.i0 >= 4 and w.ttm(b, 4)[0] is not None)
    return out, at4


# ----------------------------------------------------------------------------------------------- F7 (SEC cover counts)
def _adjust(f, prev, splits, today):
    """Cover count restated to `today`'s share basis (frozen D111 rule of SECCorrections.shares_on)."""
    mult = 1.0
    for ex, fac in splits:
        if not (f.cover_date < ex <= today and fac > 0):
            continue
        m = 1.0 / fac
        if ex <= f.filed and prev is not None:
            r = f.shares / prev.shares
            if abs(math.log(r) - math.log(m)) < abs(math.log(r)):
                continue
        mult *= m
    return f.shares * mult


def dilution(filings, splits, today):
    """(oriented F7 value, reason, latest filing date): -(S0/S1 - 1). Only filings usable on `today` and splits dated
    on or before `today` can enter."""
    use = sorted((f for f in filings if f.available <= today and f.shares and f.cover_date is not None),
                 key=lambda x: (x.cover_date, x.filed, x.accn))
    if not use:
        return None, "no_cover_count", None
    f0 = use[-1]
    if (today - f0.cover_date).days > SHARE_MAX_AGE:
        return None, "no_cover_count", f0.filed
    target = f0.cover_date.toordinal() - YEAR_DAYS
    c = [f for f in use if abs(f.cover_date.toordinal() - target) <= YEAR_TOL]
    if not c:
        return None, "no_prior_count", f0.filed
    f1 = min(c, key=lambda x: (abs(x.cover_date.toordinal() - target), -x.filed.toordinal()))

    def prev(f):
        p = [x for x in use if x.cover_date < f.cover_date]
        return max(p, key=lambda x: (x.cover_date, x.filed)) if p else None
    s0, s1 = _adjust(f0, prev(f0), splits, today), _adjust(f1, prev(f1), splits, today)
    if not (s0 > 0 and s1 > 0):
        return None, "no_cover_count", f0.filed
    return -(s0 / s1 - 1.0), "ok", f0.filed


# ----------------------------------------------------------------------------------------------- aggregation
def avg_rank(x):
    """1-based average ranks (ties share their mean rank)."""
    x = np.asarray(x, float)
    if not x.size:
        return np.zeros(0)
    o = np.argsort(x, kind="mergesort")
    xs = x[o]
    first = np.r_[True, xs[1:] != xs[:-1]]
    starts = np.flatnonzero(first)
    ends = np.r_[starts[1:], x.size] - 1
    grp = np.cumsum(first) - 1
    r = np.empty(x.size)
    r[o] = (0.5 * (starts + ends) + 1.0)[grp]
    return r


def spearman(a, b, min_n=30):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < min_n:
        return float("nan")
    ra, rb = avg_rank(a[ok]), avg_rank(b[ok])
    sa, sb = ra.std(), rb.std()
    if sa == 0 or sb == 0:
        return float("nan")
    return float(((ra - ra.mean()) * (rb - rb.mean())).mean() / (sa * sb))


def qstats(x, qs=QS):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if not x.size:
        return dict(n=0)
    out = {f"p{q}": float(np.percentile(x, q)) for q in qs}
    out.update(n=int(x.size), min=float(x.min()), max=float(x.max()))
    return out


def rho_summary(series):
    s = np.asarray([v for v in series if math.isfinite(v)], float)
    if not s.size:
        return dict(months=0)
    return dict(months=int(s.size), median=float(np.median(s)), mean=float(s.mean()), p10=float(np.percentile(s, 10)),
                p90=float(np.percentile(s, 90)), median_abs=float(np.median(np.abs(s))))


def period_of(year):
    for name, a, b in PERIODS:
        if a <= year <= b:
            return name
    return None


def runs(seq):
    """Completed constant-run lengths (bounded by a change on both sides) of one stock's consecutive values."""
    out, n, started = [], 0, False
    for i in range(1, len(seq)):
        if seq[i] != seq[i - 1]:
            if started:
                out.append(n)
            started, n = True, 1
        else:
            n += 1
    return out


def aggregate(months, h024=None, h024_names=()):
    """months: list of dicts (review date str 'day', and per stock arrays): sid (list), nf (bool), ff (int), lmc,
    lpx, ladv (float), V (n x 11 oriented values, NaN = invalid), why (n x 11 int), dstale, age, d7 (float),
    revised (bool), path (int), seas (n x 6), ttmw (n x 5 int), ttm4 (n x 5 bool), viol (int).
    h024: {day: (sids, n x 11 oriented H024 features)} on the H026 population. Returns the export dictionary."""
    F = len(FORMS)
    out = dict(forms=list(FORMS), reviews=[m["day"] for m in months], monthly={}, sector={}, staleness={},
               update={}, dist={}, pathology={}, seasonality={}, ttm={}, revised={}, corr={}, h028_overlap={},
               patterns={}, pattern_periods={}, pit=dict(record_after_today=0, universe_rows_without_live_values=0))
    for k in ("nf_eligible", "all_eligible", "nf_nosic"):
        out["monthly"][k] = []
    for f in FORMS:
        out["monthly"][f] = dict(nf_valid=[], all_valid=[])
    pooled = {f: {p: [] for p, _, _ in PERIODS} for f in FORMS}
    stale = {f: {p: [] for p, _, _ in PERIODS} for f in FORMS}
    ages = {p: [] for p, _, _ in PERIODS}
    sect = {}
    path = {p: dict.fromkeys(PATH, 0) for p, _, _ in PERIODS}
    path_n = dict.fromkeys([p for p, _, _ in PERIODS], 0)
    ttm = {b: {p: [0] * len(TTM_WHY) for p, _, _ in PERIODS} for b in BASES}
    ttm4 = {b: {p: [0, 0] for p, _, _ in PERIODS} for b in BASES}
    why = {f: {p: [0] * len(WHY) for p, _, _ in PERIODS} for f in FORMS}
    rev = {f: [0, 0] for f in FORMS}
    seas_r = {k: [] for k in ("rev_qoq_abs", "rev_yoy_abs", "gm_qoq_abs", "gm_yoy_abs")}
    seas_rho = dict(rev=[], gm=[])
    corr = {(i, j): [] for i in range(F) for j in range(i + 1, F)}
    ov = {(i, j): [] for i in range(F) for j in range(len(h024_names))}
    hist_v = {}                     # sid -> list of (review index, values) for update frequency
    pat_p = {}
    for mi, m in enumerate(months):
        y = int(m["day"][:4])
        per = period_of(y)
        nf = np.asarray(m["nf"], bool)
        V = np.asarray(m["V"], float).reshape(-1, F)
        valid = np.isfinite(V)
        out["monthly"]["nf_eligible"].append(int(nf.sum()))
        out["monthly"]["all_eligible"].append(int(nf.size))
        out["monthly"]["nf_nosic"].append(int(np.sum(nf & (np.asarray(m["ff"]) < 0))))
        out["pit"]["record_after_today"] += int(m.get("viol", 0))
        out["pit"]["universe_rows_without_live_values"] += int(m.get("missing_rows", 0))
        for j, f in enumerate(FORMS):
            out["monthly"][f]["nf_valid"].append(int((valid[:, j] & nf).sum()))
            out["monthly"][f]["all_valid"].append(int(valid[:, j].sum()))
            pooled[f][per].extend(V[valid[:, j] & nf, j].tolist())
            sv = np.asarray(m["d7"] if f == "F7" else m["dstale"], float)[valid[:, j] & nf]
            stale[f][per].extend(sv.tolist())
            wy = np.asarray(m["why"])[nf, j]
            for c in range(len(WHY)):
                why[f][per][c] += int(np.sum(wy == c))
            if f != "F7":
                rv = np.asarray(m["revised"], bool)
                rev[f][0] += int(np.sum(valid[:, j] & nf & rv))
                rev[f][1] += int(np.sum(valid[:, j] & nf))
        ages[per].extend(np.asarray(m["age"], float)[nf & np.isfinite(np.asarray(m["age"], float))].tolist())
        ff = np.asarray(m["ff"])
        for g in np.unique(ff):
            sel = ff == g
            d = sect.setdefault(per, {}).setdefault(str(int(g)), dict(eligible=0, nf=0, valid=[0] * F))
            d["eligible"] += int(sel.sum())
            d["nf"] += int((sel & nf).sum())
            for j in range(F):
                d["valid"][j] += int((valid[:, j] & sel).sum())
        pb = np.asarray(m["path"], np.int64)[nf]
        path_n[per] += int(nf.sum())
        for k in PATH:
            path[per][k] += int(np.sum((pb & PB[k]) > 0))
        tw, t4 = np.asarray(m["ttmw"])[nf], np.asarray(m["ttm4"], bool)[nf]
        for bi, b in enumerate(BASES):
            for c in range(len(TTM_WHY)):
                ttm[b][per][c] += int(np.sum(tw[:, bi] == c))
            ttm4[b][per][0] += int(np.sum(t4[:, bi]))
            ttm4[b][per][1] += int(np.sum(tw[:, bi] == 0))
        S = np.asarray(m["seas"], float).reshape(-1, 6)[nf]
        seas_r["rev_qoq_abs"].extend(np.abs(S[np.isfinite(S[:, 0]), 0]).tolist())
        seas_r["rev_yoy_abs"].extend(np.abs(S[np.isfinite(S[:, 2]), 2]).tolist())
        seas_r["gm_qoq_abs"].extend(np.abs(S[np.isfinite(S[:, 3]), 3]).tolist())
        seas_r["gm_yoy_abs"].extend(np.abs(S[np.isfinite(S[:, 5]), 5]).tolist())
        seas_rho["rev"].append(spearman(S[:, 0], S[:, 1]))
        seas_rho["gm"].append(spearman(S[:, 3], S[:, 4]))
        Vn = V[nf]
        for (i, j) in corr:
            corr[(i, j)].append(spearman(Vn[:, i], Vn[:, j]))
        if h024 is not None and m["day"] in h024:
            hs, HX = h024[m["day"]]
            pos = {s: n for n, s in enumerate(m["sid"])}
            idx = [pos.get(s, -1) for s in hs]
            keep = [n for n, ix in enumerate(idx) if ix >= 0]
            A = np.full((len(hs), F), np.nan)
            for n in keep:
                A[n] = V[idx[n]]
            HX = np.asarray(HX, float).reshape(-1, len(h024_names))
            for (i, j) in ov:
                ov[(i, j)].append(spearman(A[:, i], HX[:, j]))
        # validity patterns (U_NF): per review counts; per period sums of log size / price / ADV and FF12 counts
        bits = (valid[nf] * (1 << np.arange(F))).sum(axis=1).astype(np.int64)
        cnt = {}
        for b in bits.tolist():
            cnt[b] = cnt.get(b, 0) + 1
        out["patterns"][m["day"]] = {str(k): v for k, v in sorted(cnt.items())}
        lmc, lpx, lad = (np.asarray(m[k], float)[nf] for k in ("lmc", "lpx", "ladv"))
        ffn = ff[nf]
        pp = pat_p.setdefault(per, {})
        for n, b in enumerate(bits.tolist()):
            e = pp.setdefault(b, [0, 0.0, 0.0, 0.0, {}])
            e[0] += 1
            e[1] += lmc[n] if np.isfinite(lmc[n]) else 0.0
            e[2] += lpx[n] if np.isfinite(lpx[n]) else 0.0
            e[3] += lad[n] if np.isfinite(lad[n]) else 0.0
            e[4][str(int(ffn[n]))] = e[4].get(str(int(ffn[n])), 0) + 1
        for n, s in enumerate(m["sid"]):
            if nf[n]:
                hist_v.setdefault(s, []).append((mi, V[n]))
    for f in FORMS:
        out["dist"][f] = dict({p: qstats(pooled[f][p]) for p, _, _ in PERIODS},
                              overall=qstats(sum((pooled[f][p] for p, _, _ in PERIODS), [])))
        out["staleness"][f] = dict({p: qstats(stale[f][p], (50, 75, 90, 95)) for p, _, _ in PERIODS},
                                   overall=qstats(sum((stale[f][p] for p, _, _ in PERIODS), []), (50, 75, 90, 95)))
        out["revised"][f] = dict(windows_with_revision=rev[f][0], valid=rev[f][1])
    out["why"] = {f: why[f] for f in FORMS}
    out["period_age"] = dict({p: qstats(ages[p], (50, 75, 90, 95)) for p, _, _ in PERIODS},
                             overall=qstats(sum(ages.values(), []), (50, 75, 90, 95)))
    out["sector"] = sect
    out["pathology"] = dict(counts=path, stock_months=path_n)
    out["ttm"] = dict(reasons=ttm, q4=ttm4, why_names=list(TTM_WHY))
    out["seasonality"] = dict({k: qstats(v, (50,)) for k, v in seas_r.items()},
                              rev_qoq_lag4_rho=rho_summary(seas_rho["rev"]), gm_qoq_lag4_rho=rho_summary(seas_rho["gm"]))
    out["corr"] = {f"{FORMS[i]}|{FORMS[j]}": rho_summary(v) for (i, j), v in corr.items()}
    out["h028_overlap"] = {f"{FORMS[i]}|{h024_names[j]}": rho_summary(v) for (i, j), v in ov.items()}
    out["pattern_periods"] = {p: {str(b): [e[0], e[1], e[2], e[3], e[4]] for b, e in sorted(d.items())}
                              for p, d in pat_p.items()}
    upd = {f: [0, 0, []] for f in FORMS}
    for s, seq in hist_v.items():
        for j, f in enumerate(FORMS):
            seg, prev_i = [], None
            for mi, v in seq + [(None, None)]:
                x = None if v is None else v[j]
                cont = mi is not None and prev_i is not None and mi == prev_i + 1 and x is not None and np.isfinite(x)
                if not cont and seg:                     # close the segment of consecutive valid months
                    upd[f][1] += len(seg) - 1
                    upd[f][0] += sum(1 for a_, b_ in zip(seg, seg[1:]) if a_ != b_)
                    upd[f][2].extend(runs(seg))
                    seg = []
                if x is not None and np.isfinite(x):
                    seg.append(round(float(x), 12))
                prev_i = mi
    for f in FORMS:
        rl = np.asarray(upd[f][2], float)
        out["update"][f] = dict(changed_pairs=upd[f][0], pairs=upd[f][1],
                                share_changed=upd[f][0] / upd[f][1] if upd[f][1] else None,
                                runs=int(rl.size), run_median=float(np.median(rl)) if rl.size else None,
                                run_p25=float(np.percentile(rl, 25)) if rl.size else None,
                                run_p75=float(np.percentile(rl, 75)) if rl.size else None)
    return out
