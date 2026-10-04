# qr_xs.py — Phase 4 cross-sectional technical signal validation (H019; research/phase4/P4_xs_spec.md, P4-CP3R).
# Pure numpy, no QuantConnect imports (tests/test_xs.py). The same code runs inside LEAN for the real world and every
# null world, and locally on synthetic panels (research/phase4/P4_xs_power.py).
#
# P4-CP3R2 (v2, frozen candidate): the constants below are pinned with the specification by
# qresearch.p4xs (tests/test_p4xs_spec.py). Nothing here may change after any real signal or return is computed.
#
# Decision = the close of the last session of month m. Prices: daily closes; S1 / S2 use split- and dividend-adjusted
# closes (total-return convention, as CRSP 'ret'); S3 uses split-adjusted (not dividend-adjusted) closes, as in the
# published construction (abs(prc) / cfacpr).
#   S1 MOM  = P(end of m-1) / P(end of m-12) - 1                      (12-1 momentum: Jegadeesh-Titman; FF 'prior 2-12')
#   S2 FIP  = Da, Gurun & Warachka (2014): PRET = S1 (12 months, skipping the most recent month);
#             ID = sgn(PRET) x (%neg - %pos), %pos / %neg = shares of positive / negative daily returns among ALL
#             trading days of the same window (zero-return days count in the denominator only); sequential sort:
#             PRET quintile first, then, within the quintile, continuity in the direction of PRET, key = -sgn(PRET) x ID
#             (low ID = continuous information); score = quintile index (1..5) + within-quintile percentile of the key
#   S3 TF   = Han, Zhou & Zhu (2016) trend factor: A_L = mean of the last L split-adjusted closes / the decision close
#             for L in HZZ_LAGS (partial windows allowed, as in the Chen-Zimmermann reproduction); every month s a
#             cross-sectional OLS (with intercept) of month s+1 returns on A_L(s); E[beta_L] at decision t = mean of
#             the 12 most recent completed regressions (s = t-12 .. t-1; the last uses month-t returns, known at t);
#             S3 = sum_L E[beta_L] x A_L(t). Estimation cross-section = the H019 eligible universe.
# Response: total return from the open of the first session after the decision through the close of the last session
#   of month m+H, cross-sectionally demeaned (equal-weighted mean over the same common sample).
# Statistics per decision date: Spearman rank IC; decile and quintile means of the demeaned response (monotonicity is
#   judged on quintiles: for S2 the quintiles are the PRET backbone, the within-quintile refinement is tested by P6); for S2 / S3 the incremental
#   statistic = mean over the 5 MOM quintiles of the within-quintile partial rank correlation between the candidate's
#   own component (the FIP key for S2, S3 itself) and the response, controlling for the MOM rank.
# Time series: mean, Newey-West (Bartlett) HAC t with a fixed lag; halves / blocks / years by decision date.
import math

import numpy as np

H_MONTHS = 1                      # primary forward horizon (months): next month
DIAG_HORIZONS = (3,)              # secondary diagnostic only, never gated, never rescues a primary failure
NW_LAG = 2                        # fixed HAC lag for the primary (non-overlapping) horizon
DIAG_NW_LAG = {3: 6}              # HAC lag for the 3-month diagnostic (2 x H)
FIRST_RESEARCH_MONTH = (2010, 1)  # first research month-end (D034: research data from 2010-01-04); first regression
FIRST_DECISION = (2011, 1)        # first month with 12 completed trend-factor regressions (s = 2010-01 .. 2010-12)
LAST_DECISION = (2017, 11)        # the next-month return ends at the 2017-12-29 close
LAST_DECISION_DIAG = {3: (2017, 9)}
N_DECISIONS = 83                  # 2011-01 .. 2017-11
HZZ_LAGS = (3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000)
HZZ_BETA_MONTHS = 12
ID_MIN_DAYS = 1                   # ID is defined whenever PRET is (no extra minimum: none is published)
PRET_STALE_MAX = 5                # a month-end price may be the last bar at most 5 sessions before the month-end
N_DECILES = 10
N_MOM_Q = 5
ECON_MIN_TOP = 0.03               # top-decile annualised demeaned excess >= 3% a year
N_MONO_Q = 5                      # monotonicity is judged on equal-count quintiles of the signal
MONO_MIN = 0.90                   # Spearman(quintile index, mean quintile excess) >= 0.90 (<= one adjacent inversion)
BLOCK_MAX_SHARE = 0.5             # no block > 50% of the total IC sum
BLOCKS = ((2011, 2012), (2013, 2014), (2015, 2016), (2017, 2017))
ALPHA = 0.01                      # conservative pre-registered family-wise level (prior momentum experimentation)
SIGNALS = ("S1", "S2", "S3")
INCREMENTAL = ("S2", "S3")


# ----------------------------------------------------------------------------------------------- signal formulas
def mom_12_1(p_end_m1, p_end_m12):
    """12-1 momentum from adjusted month-end closes (vectorised); NaN where either close is missing or not positive."""
    a, b = np.broadcast_arrays(np.asarray(p_end_m1, float), np.asarray(p_end_m12, float))
    out = np.full(a.shape, np.nan)
    ok = np.isfinite(a) & np.isfinite(b) & (a > 0) & (b > 0)
    out[ok] = a[ok] / b[ok] - 1.0
    return out


def id_measure(daily_returns, pret, min_days=ID_MIN_DAYS):
    """Information discreteness of Da, Gurun & Warachka (2014): sgn(PRET) x (%neg - %pos) over the formation window.
    %pos / %neg = the shares of positive / negative daily returns among all trading-day returns observed in the window
    ('percentage of days during the formation period'; zero returns count in the denominator only). NaN if PRET is
    missing or no daily return is observed."""
    r = np.asarray(daily_returns, float)
    r = r[np.isfinite(r)]
    n = r.size
    if n < min_days or not np.isfinite(pret):
        return math.nan
    pos, neg = int((r > 0).sum()) / n, int((r < 0).sum()) / n
    return float(np.sign(pret)) * (neg - pos)


def fip_key(id_v, pret):
    """Within-PRET-quintile ordering key: -sgn(PRET) x ID = continuity in the direction of PRET. Higher = continuous
    winners (low ID among PRET > 0) and discrete losers (high ID among PRET < 0) = higher predicted relative return."""
    return -np.sign(np.asarray(pret, float)) * np.asarray(id_v, float)


def hzz_normalised_mas(closes, lags=HZZ_LAGS):
    """A_L = mean of the last L split-adjusted closes (fewer if the history is shorter; at least one) / the decision
    close. closes: oldest first, ending at the decision close. Returns an array over lags (NaN if no valid close)."""
    c = np.asarray(closes, float)
    c = c[np.isfinite(c) & (c > 0)]
    if c.size == 0:
        return np.full(len(lags), np.nan)
    p = c[-1]
    return np.array([c[-min(L, c.size):].mean() / p for L in lags])


def ols_slopes(X, y):
    """Cross-sectional OLS of y on X with an intercept, Stata 'regress' collinearity handling as in the Chen-Zimmermann
    replication (TrendFactor.py: regress(..., omit_collinear=True), coefficient 0 for an omitted variable): columns are
    taken in order and a column that does not raise the rank is omitted (slope 0). NaN slopes only if the remaining
    regression is under-identified (rows <= kept regressors + 1)."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    ok = np.all(np.isfinite(X), axis=1) & np.isfinite(y)
    X, y = X[ok], y[ok]
    n, p = X.shape
    if n < 2:
        return np.full(p, np.nan)
    Zf = np.column_stack([np.ones(n), X])
    r = np.zeros(p + 1)
    dg = np.abs(np.diag(np.linalg.qr(Zf, mode="r")))          # in-order (unpivoted) QR: r_jj ~ 0 <=> column j
    r[:dg.size] = dg
    tol = r.max() * max(Zf.shape) * np.finfo(float).eps * 10  # is spanned by the columns before it
    kept = [j for j in range(p) if r[j + 1] > tol]
    Z = Zf[:, [0] + [j + 1 for j in kept]]
    if n <= Z.shape[1]:
        return np.full(p, np.nan)
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    out = np.zeros(p)
    out[kept] = b[1:]
    return out


class TrendFactor:
    """Point-in-time Han-Zhou-Zhu expected-return model. add_regression(s, A_s, r_next) is called only once month s+1
    has ended (its returns are known); score(t, A_t) uses the 12 most recent completed regressions s = t-12 .. t-1
    and refuses any regression for s >= t (look-ahead guard)."""

    def __init__(self, months=HZZ_BETA_MONTHS):
        self.months = months
        self.betas = {}                                      # s (month index) -> slopes

    def add_regression(self, s, A_s, r_next):
        self.betas[s] = ols_slopes(A_s, r_next)

    def expected_betas(self, t):
        need = list(range(t - self.months, t))
        if any(s >= t for s in self.betas if s in need):
            raise ValueError("look-ahead")
        if not all(s in self.betas and np.all(np.isfinite(self.betas[s])) for s in need):
            return None
        return np.mean([self.betas[s] for s in need], axis=0)

    def score(self, t, A_t):
        eb = self.expected_betas(t)
        if eb is None:
            return np.full(len(A_t), np.nan)
        return np.asarray(A_t, float) @ eb


# ----------------------------------------------------------------------------------------------- ranking utilities
def avg_rank(x):
    """Average ranks 1..n (ties share the mean rank). x must be finite. Vectorised."""
    x = np.asarray(x, float)
    n = x.size
    if n == 0:
        return np.empty(0)
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    start = np.r_[0, np.flatnonzero(np.diff(xs)) + 1]
    end = np.r_[start[1:], n] - 1
    gid = np.repeat(np.arange(start.size), end - start + 1)
    r = np.empty(n)
    r[order] = ((start + end) / 2.0 + 1.0)[gid]
    return r


def ordinal_rank(x):
    """Ranks 1..n with ties broken by position (stable): deterministic equal-count buckets."""
    x = np.asarray(x, float)
    r = np.empty(x.size)
    r[np.argsort(x, kind="mergesort")] = np.arange(1, x.size + 1)
    return r


def buckets(score, k):
    """Equal-count buckets 0..k-1 by ordinal rank (bucket k-1 = highest score)."""
    n = len(score)
    return ((ordinal_rank(score) - 1) * k // n).astype(int)


def smooth_momentum_score(mom, key, q=N_MOM_Q):
    """S2: PRET (= MOM) quintile index (1..q) + within-quintile percentile of the FIP key in (0, 1] (sequential sort)."""
    mom, nud_v = np.asarray(mom, float), np.asarray(key, float)
    qb = buckets(mom, q)
    out = np.empty(mom.size)
    for b in range(q):
        ix = np.flatnonzero(qb == b)
        out[ix] = (b + 1) + avg_rank(nud_v[ix]) / ix.size
    return out


def spearman(x, y):
    rx, ry = avg_rank(x), avg_rank(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    d = math.sqrt(float((rx * rx).sum() * (ry * ry).sum()))
    return float((rx * ry).sum() / d) if d > 0 else 0.0


def partial_corr(r_yx, r_ym, r_xm):
    """Partial correlation of y and x controlling for m, from the three pairwise correlations."""
    d = math.sqrt(max((1 - r_ym ** 2) * (1 - r_xm ** 2), 0.0))
    return (r_yx - r_ym * r_xm) / d if d > 0 else 0.0


def within_quintile_partial_ic(comp, mom, y, q=N_MOM_Q):
    """Mean over MOM quintiles of the partial rank correlation of comp with y controlling for MOM (and per quintile)."""
    qb = buckets(mom, q)
    per = []
    for b in range(q):
        ix = np.flatnonzero(qb == b)
        c, m, yy = comp[ix], mom[ix], y[ix]
        per.append(partial_corr(spearman(yy, c), spearman(yy, m), spearman(c, m)))
    return float(np.mean(per)), per


# ----------------------------------------------------------------------------------------------- per-date statistics
def demean(r):
    r = np.asarray(r, float)
    return r - r.mean()


def date_stats(sig, comp, y):
    """One decision date. sig = {'S1': mom, 'S2': FIP score, 'S3': trend factor}; comp = {'S2': FIP key, 'S3': trend factor} (the
    candidates' own components); y = forward returns of the same common-sample cross-section (any scale)."""
    yd = demean(y)
    out = {}
    for s in SIGNALS:
        d = buckets(sig[s], N_DECILES)
        qn = buckets(sig[s], N_MONO_Q)
        out[s] = dict(ic=spearman(sig[s], yd),
                      dec=[float(yd[d == k].mean()) for k in range(N_DECILES)],
                      q5=[float(yd[qn == k].mean()) for k in range(N_MONO_Q)])
    for s in INCREMENTAL:
        out[s]["inc"], out[s]["inc_q"] = within_quintile_partial_ic(np.asarray(comp[s], float),
                                                                    np.asarray(sig["S1"], float), yd)
    return out


# ----------------------------------------------------------------------------------------------- time-series inference
def nw_tstat(x, lag=NW_LAG):
    """Mean / Newey-West (Bartlett) HAC standard error of a time series; (mean, se, t)."""
    x = np.asarray(x, float)
    T = x.size
    m = x.mean()
    e = x - m
    lrv = float(e @ e) / T
    for l in range(1, min(lag, T - 1) + 1):
        lrv += 2.0 * (1.0 - l / (lag + 1.0)) * float(e[l:] @ e[:-l]) / T
    se = math.sqrt(max(lrv, 0.0) / T)
    return float(m), se, (float(m) / se if se > 0 else 0.0)


def block_share_max(values, years, blocks=BLOCKS):
    """Largest share of the total sum contributed by one block (inf if the total is not positive)."""
    v, yr = np.asarray(values, float), np.asarray(years)
    tot = float(v.sum())
    if tot <= 0:
        return math.inf
    return max(float(v[(yr >= a) & (yr <= b)].sum()) / tot for a, b in blocks)


def summarise(series, years, h=H_MONTHS, lag=NW_LAG):
    """series[t] = date_stats(...) output for each decision date t (chronological); years[t] = decision year."""
    yrs = np.asarray(years)
    out = {}
    for s in SIGNALS:
        ic = np.array([d[s]["ic"] for d in series])
        dec = np.array([d[s]["dec"] for d in series])
        q5 = np.array([d[s]["q5"] for d in series]).mean(axis=0)
        m, se, t = nw_tstat(ic, lag)
        mdec = dec.mean(axis=0)
        r = dict(ic_mean=m, ic_se=se, t=t,
                 top_ann=float(mdec[-1]) * 12.0 / h,
                 spread_ann=float(mdec[-1] - mdec[0]) * 12.0 / h,
                 dec_mean=mdec.tolist(),
                 q_mean=q5.tolist(),
                 mono=spearman(np.arange(N_MONO_Q, dtype=float), q5),
                 q_gap=float(q5[-1] - q5[0]),
                 sub=[float(ic[:ic.size // 2].mean()), float(ic[ic.size // 2:].mean())],
                 block_max=block_share_max(ic, yrs),
                 years={int(y): float(ic[yrs == y].mean()) for y in sorted(set(yrs.tolist()))})
        if s in INCREMENTAL:
            inc = np.array([d[s]["inc"] for d in series])
            r["inc_mean"], r["inc_se"], r["t_inc"] = nw_tstat(inc, lag)
            r["inc_q_mean"] = np.array([d[s]["inc_q"] for d in series]).mean(axis=0).tolist()
        out[s] = r
    return out


def family_stat(summary):
    """The statistic whose null quantile is the critical value c: the max of the five studentised statistics."""
    return max([summary[s]["t"] for s in SIGNALS] + [summary[s]["t_inc"] for s in INCREMENTAL])


def promotion(summary, c):
    """Frozen promotion rule. Returns {signal: {criterion: bool, ..., 'pass': bool}}. S1 is a reference: its 'pass'
    means 'known effect reproduced', never a new discovery."""
    out = {}
    for s in SIGNALS:
        r = summary[s]
        crit = dict(P1_economic=(r["top_ann"] >= ECON_MIN_TOP) and (r["spread_ann"] > 0),
                    P2_monotonic=(r["mono"] >= MONO_MIN) and (r["q_gap"] > 0),
                    P3_statistical=r["t"] > c,
                    P4_stable=all(v > 0 for v in r["sub"]) and r["block_max"] <= BLOCK_MAX_SHARE)
        if s in INCREMENTAL:
            crit["P6_incremental"] = r["t_inc"] > c
        crit["pass"] = all(crit.values())
        out[s] = crit
    passed = [s for s in INCREMENTAL if out[s]["pass"]]
    out["selected"] = max(passed, key=lambda s: summary[s]["t_inc"]) if passed else None
    out["outcome"] = ("candidate" if passed else ("replication_only" if out["S1"]["pass"] else "none"))
    return out


def critical_value(null_family_stats, alpha=ALPHA):
    """c = the (1 - alpha) empirical quantile of the null family statistic: the k-th largest, k = ceil(alpha x R)."""
    v = np.sort(np.asarray(null_family_stats, float))[::-1]
    k = max(1, int(math.ceil(alpha * v.size)))
    return float(v[k - 1])


# ----------------------------------------------------------------------------------------------- tethered null
class Tether:
    """Identity-tethered within-date permutation, stratified by feature availability. Each receiving stock is assigned
    the complete feature vector (PRET, ID, the 11 moving-average ratios) of a random partner (source) stock of the
    same stratum, and keeps that partner while both stay in the cross-section and in the same stratum; stocks left
    without a partner are re-matched at random within their stratum on that date. Strata: 'full' (PRET and ID defined)
    and 'partial' (moving averages only; they enter the trend-factor regressions, never the evaluation). On every date
    the null features are an exact permutation of the real ones within each stratum over the same stocks; a stock's
    null feature history is another stock's real history; only the link to the stock's own returns is broken."""

    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.map = {}

    def step(self, eligible, strata=None):
        """eligible: stock ids (sorted by the caller); strata: labels aligned with eligible (None = one stratum).
        Returns src[i] = the stock whose features receiver eligible[i] gets on this date."""
        E = list(eligible)
        lab = dict(zip(E, strata)) if strata is not None else {i: 0 for i in E}
        keep = {i: j for i, j in self.map.items() if i in lab and j in lab and lab[i] == lab[j]}
        used = set(keep.values())
        for g in sorted(set(lab.values())):
            free_r = [i for i in E if lab[i] == g and i not in keep]
            free_s = [j for j in E if lab[j] == g and j not in used]
            perm = self.rng.permutation(len(free_s))
            for i, k in zip(free_r, perm):
                keep[i] = free_s[k]
        self.map = keep
        return [keep[i] for i in E]


# ----------------------------------------------------------------------------------------------- end-to-end pipeline
class Panel:
    """Point-in-time daily panel (rows = sessions, oldest first; columns = stocks; NaN = no bar), as collected inside
    LEAN or built synthetically. split_close: split-adjusted closes (S3); tr_close / tr_open: total-return-adjusted
    closes / opens (S1, S2, returns). month_end[k] = row of the last session of month k; months[k] = (year, month);
    elig[k] = eligibility (bool per stock) at that close, False outside the research period."""

    def __init__(self, split_close, tr_close, tr_open, month_end, months, elig):
        self.Q = np.asarray(split_close, float)
        self.P = np.asarray(tr_close, float)
        self.O = np.asarray(tr_open, float)
        self.me = list(month_end)
        self.months = list(months)
        self.elig = np.asarray(elig, bool)


def _last_valid(rows, r, stale=None):
    """Index into rows (sorted valid rows of one stock) of the last valid row <= r, or -1; optional staleness cap."""
    i = int(np.searchsorted(rows, r, side="right")) - 1
    if i < 0 or (stale is not None and r - rows[i] > stale):
        return -1
    return i


class Features:
    """All signal inputs and returns, computed once from a Panel (they do not depend on the world).
    For research month k (decision row d = me[k]): A[k] (N x 11), pret[k], idm[k]; dom[k] = eligible with a bar at d;
    full[k] = dom with PRET and ID defined; reg[k] = close(me[k]) -> close(me[k+1]) total return (trend-factor
    regression response for month k+1); fwd[h][k] = open(d+1) -> close(me[k+h]) total return (H019 response).
    A stock delisted or without bars inside a return window is valued at its last real close (0 thereafter)."""

    def __init__(self, panel, horizons=(H_MONTHS,) + tuple(DIAG_HORIZONS)):
        pn = panel
        K, N = len(pn.me), pn.P.shape[1]
        D = pn.P.shape[0]
        me = np.asarray(pn.me)
        nl = len(HZZ_LAGS)
        self.months = pn.months
        self.A = np.full((K, N, nl), np.nan)
        self.pret = np.full((K, N), np.nan)
        self.idm = np.full((K, N), np.nan)
        self.reg = np.full((K, N), np.nan)
        self.fwd = {h: np.full((K, N), np.nan) for h in horizons}
        bar = np.isfinite(pn.Q[me]) & np.isfinite(pn.P[me])
        self.dom = pn.elig & bar
        for j in range(N):
            ks = np.flatnonzero(self.dom[:, j])
            if ks.size == 0:
                continue
            qr = np.flatnonzero(np.isfinite(pn.Q[:, j]) & (pn.Q[:, j] > 0))
            pr = np.flatnonzero(np.isfinite(pn.P[:, j]) & (pn.P[:, j] > 0))
            qv, pv = pn.Q[qr, j], pn.P[pr, j]
            qcs = np.r_[0.0, np.cumsum(qv)]
            d = me[ks]
            # moving-average ratios: mean of the last min(L, n) split-adjusted closes / the decision close
            n = np.searchsorted(qr, d, side="right")
            for li, L in enumerate(HZZ_LAGS):
                w = np.minimum(L, n)
                self.A[ks, j, li] = (qcs[n] - qcs[n - w]) / w / pn.Q[d, j]
            # PRET and ID over the window (me[k-12], me[k-1]] of total-return closes
            dr = pv[1:] / pv[:-1] - 1.0                          # return ending at valid row pr[i+1]
            cpos = np.r_[0, np.cumsum(dr > 0)]
            cneg = np.r_[0, np.cumsum(dr < 0)]
            kk = ks[ks >= 12]
            if kk.size:
                r1, r12 = me[kk - 1], me[kk - 12]
                i1 = np.searchsorted(pr, r1, side="right") - 1
                i12 = np.searchsorted(pr, r12, side="right") - 1
                ok = (i1 >= 0) & (i12 >= 0) & (i1 > i12)
                ok &= (r1 - pr[np.maximum(i1, 0)] <= PRET_STALE_MAX) & (r12 - pr[np.maximum(i12, 0)] <= PRET_STALE_MAX)
                i1, i12, kk = i1[ok], i12[ok], kk[ok]
                pret = pv[i1] / pv[i12] - 1.0
                nret = i1 - i12                                   # daily returns pv[i12+1..i1] / previous - 1
                pos = cpos[i1] - cpos[i12]
                neg = cneg[i1] - cneg[i12]
                self.pret[kk, j] = pret
                self.idm[kk, j] = np.sign(pret) * (neg - pos) / nret
            # returns: regression response (close -> next month-end close) and forward responses (next open ->)
            for h, arr in [(1, self.reg)] + [(h, self.fwd[h]) for h in self.fwd]:
                kh = ks[ks + h < K]
                if kh.size == 0:
                    continue
                dd = me[kh]
                ie = np.searchsorted(pr, me[kh + h], side="right") - 1
                end = pv[ie]
                if arr is self.reg:
                    arr[kh, j] = end / pn.P[dd, j] - 1.0
                else:
                    nxt = np.minimum(dd + 1, D - 1)
                    op = pn.O[nxt, j]
                    start = np.where((dd + 1 < D) & np.isfinite(op), op, pn.P[dd, j])
                    end = np.where(pr[ie] > dd, end, start)
                    arr[kh, j] = end / start - 1.0
        self.full = self.dom & np.isfinite(self.pret) & np.isfinite(self.idm)


def run_world(F, seed=None, first_research=FIRST_RESEARCH_MONTH, first_decision=FIRST_DECISION,
              last_decision=LAST_DECISION, h=H_MONTHS, lag=NW_LAG, keep_series=False, keep_signals=False):
    """The complete H019 procedure for one world. seed None = the real world (identity mapping); otherwise a null
    world: the stratified tether maps every receiver to a partner's full feature vector, and EVERYTHING downstream is
    recomputed from the mapped features with the receivers' real returns: the trend-factor regressions and rolling
    coefficients, S2's two-stage sort, S3, the per-date statistics, the inference and the promotion inputs."""
    T = Tether(seed) if seed is not None else None
    tf = TrendFactor()
    months = F.months
    k0 = months.index(first_research)
    kd0, kd1 = months.index(first_decision), months.index(last_decision)
    prev = None
    series, years, sigs = [], [], []
    for k in range(k0, kd1 + 1):
        dom = np.flatnonzero(F.dom[k])
        full = F.full[k, dom]
        src = np.asarray(T.step(dom.tolist(), full.tolist()) if T is not None else dom, int)
        A_k = F.A[k, src]
        if prev is not None:                                         # month-k returns are known at the k close
            s, rec, A_s = prev
            tf.add_regression(s, A_s, F.reg[s, rec])
        prev = (k, dom, A_k)
        if k < kd0:
            continue
        s3 = tf.score(k, A_k)
        ok = F.full[k, src] & np.isfinite(s3)
        rec, sk = dom[ok], src[ok]
        pret, idm, s3 = F.pret[k, sk], F.idm[k, sk], s3[ok]
        y = F.fwd[h][k, rec]
        sig = {"S1": pret, "S2": smooth_momentum_score(pret, fip_key(idm, pret)), "S3": s3}
        series.append(date_stats(sig, {"S2": fip_key(idm, pret), "S3": s3}, y))
        years.append(months[k][0])
        if keep_signals:
            sigs.append(dict(k=k, rec=rec, src=sk, pret=pret, idm=idm, S2=sig["S2"], S3=s3, y=y))
    out = summarise(series, years, h, lag)
    if keep_series:
        out["_series"], out["_years"] = series, years
    if keep_signals:
        out["_signals"], out["_betas"] = sigs, dict(tf.betas)
    return out
