# qr_xs.py — Phase 4 cross-sectional technical signal validation (H019 draft; research/phase4/P4_xs_spec.md, P4-CP3).
# Pure numpy, no QuantConnect imports (tests/test_xs.py). The same code would run inside LEAN for the real world and
# every null world, and locally on synthetic panels (research/phase4/P4_xs_power.py).
#
# DRAFT (P4-CP3): the constants below are the PROPOSED pre-registration. They are frozen (hash-pinned) only after the
# owner approves the specification, and before any real signal or forward return is computed.
#
# Signals (decision = the close of the last session of month m; all prices split- and dividend-adjusted as of that
# close):
#   S1 MOM   = P(end of m-1) / P(end of m-12) - 1                         (12-1 momentum; Jegadeesh-Titman; FF 'prior 2-12')
#   NUD      = (#up days - #down days) / #days over the same window         (daily returns from the first session after
#              the end of m-12 through the end of m-1; zero-return days count only in the denominator; >= 200 returns)
#              NUD = -sgn(PRET) x ID of Da, Gurun & Warachka (2014): the unsigned share of positive minus negative days
#   S2 SMOOTH= sequential sort (Da-Gurun-Warachka): MOM quintile first, then NUD within the quintile
#              score = quintile index (1..5) + within-quintile percentile of NUD in (0, 1]
#   S3 TREND = mean over L in {50, 100, 200} sessions of ln(P_t / SMA_L,t), P_t = the decision close (no skip)
#              (the normalised-moving-average signal of Han, Zhou & Zhu 2016 at the intermediate horizons, unweighted)
# Response: forward total return from the open of the first session after the decision through the close of the last
#   session of month m+H, cross-sectionally demeaned (equal-weighted mean over the same eligible cross-section).
# Statistics per decision date: Spearman rank IC; decile means of the demeaned response; for S2 / S3 the incremental
#   statistic = mean over the 5 MOM quintiles of the within-quintile partial rank correlation between the candidate's
#   own component (NUD for S2, TREND for S3) and the response, controlling for the MOM rank.
# Time series: mean, Newey-West (Bartlett) HAC t with a fixed lag; years / subperiods by decision date.
import math

import numpy as np

H_MONTHS = 3                      # primary forward horizon (months)
DIAG_HORIZONS = (1, 6)            # secondary diagnostics only, never gated
NW_LAG = 6                        # fixed HAC lag for the primary horizon (2 x H)
MA_LENGTHS = (50, 100, 200)       # trend-score horizons (sessions)
NUD_MIN_DAYS = 200                # minimum valid daily returns in the 11-month window
N_DECILES = 10
N_MOM_Q = 5
ECON_MIN_TOP = 0.03               # top-decile annualised demeaned excess >= 3% a year
MONO_MIN = 0.70                   # Spearman(decile index, mean decile excess) >= 0.70
BLOCK_MAX_SHARE = 0.5             # no two-year block > 50% of the total IC sum
SUBPERIODS = ((2010, 2013), (2014, 2017))
BLOCKS = ((2010, 2011), (2012, 2013), (2014, 2015), (2016, 2017))
ALPHA = 0.01                      # family-wise level: 0.05 / (1 + 4 prior momentum-family looks)
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


def nud(daily_returns, min_days=NUD_MIN_DAYS):
    """Net up-day share (#up - #down) / #valid days of one stock's daily returns over the formation window."""
    r = np.asarray(daily_returns, float)
    r = r[np.isfinite(r)]
    n = r.size
    if n < min_days:
        return math.nan
    return (int((r > 0).sum()) - int((r < 0).sum())) / n


def trend_score(closes, lengths=MA_LENGTHS):
    """Mean over L of ln(P_t / SMA_L) from the adjusted closes up to and including the decision close (oldest first)."""
    c = np.asarray(closes, float)
    L = max(lengths)
    if c.size < L or not np.all(np.isfinite(c[-L:])) or np.any(c[-L:] <= 0):
        return math.nan
    p = c[-1]
    return float(np.mean([math.log(p / c[-l:].mean()) for l in lengths]))


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


def smooth_momentum_score(mom, nud_v, q=N_MOM_Q):
    """S2: MOM quintile index (1..q) + within-quintile percentile of NUD in (0, 1] (sequential sort)."""
    mom, nud_v = np.asarray(mom, float), np.asarray(nud_v, float)
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
    """One decision date. sig = {'S1': mom, 'S2': smooth score, 'S3': trend}; comp = {'S2': nud, 'S3': trend} (the
    candidates' own components); y = forward returns of the same common-sample cross-section (any scale)."""
    yd = demean(y)
    out = {}
    for s in SIGNALS:
        d = buckets(sig[s], N_DECILES)
        out[s] = dict(ic=spearman(sig[s], yd),
                      dec=[float(yd[d == k].mean()) for k in range(N_DECILES)])
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
        m, se, t = nw_tstat(ic, lag)
        mdec = dec.mean(axis=0)
        r = dict(ic_mean=m, ic_se=se, t=t,
                 top_ann=float(mdec[-1]) * 12.0 / h,
                 spread_ann=float(mdec[-1] - mdec[0]) * 12.0 / h,
                 dec_mean=mdec.tolist(),
                 mono=spearman(np.arange(N_DECILES, dtype=float), mdec),
                 half_gap=float(mdec[N_DECILES // 2:].mean() - mdec[:N_DECILES // 2].mean()),
                 sub=[float(ic[(yrs >= a) & (yrs <= b)].mean()) for a, b in SUBPERIODS],
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
                    P2_monotonic=(r["mono"] >= MONO_MIN) and (r["half_gap"] > 0),
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
    """Identity-tethered within-date permutation. Each receiving stock is assigned the signals of a random partner
    (source) stock and keeps that partner for as long as both stay in the eligible cross-section; stocks left without
    a partner (entries, exits) are re-matched at random among the unmatched stocks of that date. On every date the
    null signal vector is therefore an exact permutation of the real one over the same eligible stocks (cross-section,
    universe and date structure preserved); a stock's null signal history is another stock's real history (signal
    persistence and the joint distribution of S1-S3 preserved); the link to the stock's own future return is broken."""

    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.map = {}

    def step(self, eligible):
        """eligible: sequence of stock ids (sorted by the caller). Returns src[i] = the stock whose signals receiver
        eligible[i] gets on this date."""
        E = list(eligible)
        Es = set(E)
        keep = {i: j for i, j in self.map.items() if i in Es and j in Es}
        used = set(keep.values())
        free_r = [i for i in E if i not in keep]
        free_s = [j for j in E if j not in used]
        perm = self.rng.permutation(len(free_s))
        for i, k in zip(free_r, perm):
            keep[i] = free_s[k]
        self.map = keep
        return [keep[i] for i in E]
