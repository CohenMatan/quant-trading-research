# qr_h020_stats.py — H020 future signal validation: per-date statistics, inference, gates and the null (research/phase5/
# H020_spec.md sections 15-19; P5-CP2). Pure numpy (reuses qr_xs). FROZEN CANDIDATE: constants pinned by qresearch.p5h020.
# NOT run on any real data in P5-CP2: exercised only on synthetic panels (tests/test_h020_stats.py, research/phase5/
# h020_power.py).
#
# One decision date = the cross-section of eligible stocks at a weekly decision close t with, per stock:
#   Q   quality level (-1 disqualified, else score 0..20) and G group (0 = disqualified, 1 = 0-5, 2 = 6-10, 3 = 11-15,
#       4 = 16-20) -- the chart side, the only thing the null permutes;
#   mom 12-1 momentum (TR close at t-21 sessions / at t-252 - 1)   -- Baseline A (stays with the stock);
#   trend 1{weekly close > 40-week MA}                               -- Baseline B (stays with the stock);
#   y   total return next open -> close 20 sessions later (4 weeks); y13 the 13-week diagnostic.
import math

import numpy as np

import qr_xs as X

NW_LAG = 3                      # 4-week responses at weekly decisions overlap by 3 weeks
DIAG_NW_LAG = 12                # 13-week diagnostic
ANN = 13.0                      # 4-week return x 13 = annual
ANN_DIAG = 4.0
HIGH_GROUPS, LOW_GROUPS = (3, 4), (0, 1)
N_GROUPS = 5
ECON_MIN_HIGH = 0.03            # High group >= +3%/yr over the cross-sectional average
MONO_MIN = 0.90                 # Spearman(group index, mean excess) over the groups with data
BLOCKS = ((2010, 2011), (2012, 2013), (2014, 2015), (2016, 2017))
BLOCK_MAX_SHARE = 0.5
ALPHA = 0.01
N_MOM_Q = 5
STATS = ("t_ic", "t_inc")
NULL_STRATIFIED = False         # frozen: one stratum (see strata())


def rank01(x):
    x = np.asarray(x, float)
    return (X.avg_rank(x) - 0.5) / x.size


def date_stats(Q, G, mom, trend, y):
    """One decision date (all arrays aligned, one entry per eligible stock with a response)."""
    Q, G, mom, trend, y = (np.asarray(a) for a in (Q, G, mom, trend, y))
    yd = np.asarray(y, float) - float(np.mean(y))
    ic = X.spearman(np.asarray(Q, float), yd)
    # incremental value: Fama-MacBeth rank regression of rank(y) on rank(Q), rank(mom) and the trend dummy
    Z = np.column_stack([rank01(Q), rank01(mom), np.asarray(trend, float)])
    b = X.ols_slopes(Z, rank01(yd))
    gm = [float(yd[G == g].mean()) if np.any(G == g) else float("nan") for g in range(N_GROUPS)]
    gn = [int((G == g).sum()) for g in range(N_GROUPS)]
    hi = np.isin(G, HIGH_GROUPS)
    lo = np.isin(G, LOW_GROUPS)
    return dict(ic=ic, inc=float(b[0]), g=gm, n=gn,
                high=float(yd[hi].mean()) if hi.any() else float("nan"),
                low=float(yd[lo].mean()) if lo.any() else float("nan"))


def summarise(series, years, lag=NW_LAG, ann=ANN):
    yrs = np.asarray(years)
    ic = np.array([d["ic"] for d in series])
    inc = np.array([d["inc"] for d in series])
    m_ic, se_ic, t_ic = X.nw_tstat(ic, lag)
    m_inc, se_inc, t_inc = X.nw_tstat(inc, lag)
    G = np.array([d["g"] for d in series], float)
    gmean = [float(np.nanmean(G[:, g])) if np.isfinite(G[:, g]).any() else float("nan") for g in range(N_GROUPS)]
    gweeks = [int(np.isfinite(G[:, g]).sum()) for g in range(N_GROUPS)]
    hi = np.array([d["high"] for d in series])
    lo = np.array([d["low"] for d in series])
    ok = [g for g in range(N_GROUPS) if np.isfinite(gmean[g])]
    mono = X.spearman(np.array(ok, float), np.array([gmean[g] for g in ok])) if len(ok) >= 3 else float("nan")
    half = ic.size // 2
    return dict(ic_mean=m_ic, ic_se=se_ic, t_ic=t_ic, inc_mean=m_inc, inc_se=se_inc, t_inc=t_inc,
                group_mean_ann=[g * ann for g in gmean], group_weeks=gweeks,
                group_n_mean=np.array([d["n"] for d in series]).mean(axis=0).tolist(),
                high_ann=float(np.nanmean(hi) * ann) if np.isfinite(hi).any() else float("nan"),
                low_ann=float(np.nanmean(lo) * ann) if np.isfinite(lo).any() else float("nan"),
                mono=mono, halves=[float(ic[:half].mean()), float(ic[half:].mean())],
                block_max=X.block_share_max(ic, yrs, BLOCKS),
                years={int(y): float(ic[yrs == y].mean()) for y in sorted(set(yrs.tolist()))})


def null_stats(s):
    """The two studentised statistics whose null quantiles are the critical values."""
    return {k: float(s[k]) for k in STATS}


def promotion(s, c):
    """Frozen gates, all five required. c = {'t_ic': c_ic, 't_inc': c_inc} from the null (critical_values). Promotion
    is an intersection-union test: G3 and G5 must BOTH reject at level ALPHA against their own null quantile, so the
    probability of a false promotion is <= ALPHA without a multiplicity correction (a single max(t_ic, t_inc) quantile
    would be dominated by t_ic, whose null is centred away from 0 when scores are correlated with momentum)."""
    g = dict(
        G1_economic=bool(np.isfinite(s["high_ann"]) and s["high_ann"] >= ECON_MIN_HIGH and
                         np.isfinite(s["low_ann"]) and s["high_ann"] > s["low_ann"]),
        G2_monotonic=bool(np.isfinite(s["mono"]) and s["mono"] >= MONO_MIN),
        G3_significant=bool(s["t_ic"] > c["t_ic"]),
        G4_stable=bool(all(h > 0 for h in s["halves"]) and s["block_max"] <= BLOCK_MAX_SHARE),
        G5_incremental=bool(s["t_inc"] > c["t_inc"] and s["inc_mean"] > 0),
    )
    g["pass"] = all(g.values())
    return g


def strata(mom, trend):
    """REJECTED null stratification (momentum quintile x trend, 10 labels), kept only for the design check
    research/phase5/h020_null_design_check.py: with these dynamic strata the tether keeps only ~56% of partners from
    one week to the next, the null IC series loses the persistence of real scores and the null is too narrow (synthetic
    size ~6% at a nominal 1%). The frozen null is UNSTRATIFIED (NULL_STRATIFIED = False)."""
    qb = X.buckets(np.asarray(mom, float), N_MOM_Q)
    return [int(q) * 2 + int(t) for q, t in zip(qb, np.asarray(trend, bool))]


class ChartTether:
    """H020 identity-tethered within-date permutation with DYNAMIC strata and NO self-matching. qr_xs.Tether (H019) was
    built for near-static strata; with momentum-quintile strata, a stock that changes stratum alone is freed both as a
    receiver and as a source and is re-matched to itself, and a self-match then persists (synthetic check: ~30% of
    receivers self-matched, the planted edge leaked into the null). Here:
      1. a receiver keeps its partner while both are in the cross-section, in the same stratum, and not identical;
      2. in each stratum the free receivers get a random permutation of the free sources;
      3. every fixed point i -> i is removed: swapped with another free assignment (k -> s becomes k -> i, i -> s) or,
         if i is the only free stock of its stratum, spliced into a random kept pair (r -> s becomes r -> i, i -> s);
         a stratum of one stock is the only case left as i -> i.
    On every date the null chart sides are an exact permutation of the real ones within each stratum."""

    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.map = {}

    def step(self, eligible, strata):
        E = list(eligible)
        lab = dict(zip(E, strata))
        keep = {i: j for i, j in self.map.items() if i != j and i in lab and j in lab and lab[i] == lab[j]}
        used = set(keep.values())
        for g in sorted(set(lab.values())):
            free_r = [i for i in E if lab[i] == g and i not in keep]
            free_s = [j for j in E if lab[j] == g and j not in used]
            perm = self.rng.permutation(len(free_s))
            asg = {i: free_s[k] for i, k in zip(free_r, perm)}
            for i in free_r:
                if asg[i] != i:
                    continue
                others = [k for k in free_r if k != i]
                if others:
                    k = others[int(self.rng.integers(len(others)))]
                    asg[i], asg[k] = asg[k], i
                else:
                    kept = sorted(r for r in keep if lab[r] == g)
                    if kept:
                        r = kept[int(self.rng.integers(len(kept)))]
                        asg[i], keep[r] = keep[r], i
            keep.update(asg)
        self.map = keep
        return [keep[i] for i in E]


def prepare(dates, horizon="y", stratified=NULL_STRATIFIED):
    """Everything that does not depend on the world, computed once per date: the eligible rows (finite response, >= 20
    stocks), demeaned response and its rank, rank(mom), trend, rank(Q), G and the null strata. A permutation of Q
    permutes rank(Q) identically (ranks are permutation-equivariant), so a world only re-indexes the chart side."""
    out = []
    for d in dates:
        y = np.asarray(d[horizon], float)
        ok = np.isfinite(y)
        if ok.sum() < 20:
            continue
        mom, trend = np.asarray(d["mom"], float)[ok], np.asarray(d["trend"], bool)[ok]
        yd = y[ok] - float(y[ok].mean())
        Q = np.asarray(d["Q"])[ok]
        out.append(dict(ids=np.asarray(d["ids"])[ok].tolist(), Q=Q, G=np.asarray(d["G"])[ok], yd=yd,
                        ry=X.avg_rank(yd), rq=X.avg_rank(np.asarray(Q, float)), rydm=rank01(yd), rmom=rank01(mom),
                        trend=trend.astype(float), year=d["year"],
                        strata=strata(mom, trend) if stratified else [0] * len(mom),
                        mom=mom, trend_b=trend, y=y[ok]))
    return out


def _pearson(a, b):
    a, b = a - a.mean(), b - b.mean()
    den = math.sqrt(float((a * a).sum() * (b * b).sum()))
    return float((a * b).sum() / den) if den > 0 else 0.0


def fast_date_stats(p, ix=None):
    """date_stats(...) of one prepared date with the chart side re-indexed by ix (None = the real assignment);
    identical to date_stats (tests/test_h020_stats.py)."""
    rq = p["rq"] if ix is None else p["rq"][ix]
    G = p["G"] if ix is None else p["G"][ix]
    yd = p["yd"]
    ic = _pearson(rq, p["ry"])
    Z = np.column_stack([(rq - 0.5) / rq.size, p["rmom"], p["trend"]])
    b = X.ols_slopes(Z, p["rydm"])
    cnt = np.bincount(G, minlength=N_GROUPS)
    sm = np.bincount(G, weights=yd, minlength=N_GROUPS)
    gm = [float(sm[g] / cnt[g]) if cnt[g] else float("nan") for g in range(N_GROUPS)]
    hi = cnt[list(HIGH_GROUPS)].sum()
    lo = cnt[list(LOW_GROUPS)].sum()
    return dict(ic=ic, inc=float(b[0]), g=gm, n=[int(x) for x in cnt],
                high=float(sm[list(HIGH_GROUPS)].sum() / hi) if hi else float("nan"),
                low=float(sm[list(LOW_GROUPS)].sum() / lo) if lo else float("nan"))


def run_world(prep, seed=None, lag=NW_LAG, ann=ANN, keep_series=False):
    """The complete H020 evaluation for one world. prep = prepare(dates, horizon) (dates = chronological dicts with
    numpy arrays ids (sorted), Q, G, mom, trend, y, y13 and the int year). seed None = the real world; otherwise the
    identity-tethered within-date permutation (ChartTether, frozen with ONE stratum): every receiver gets the chart side
    (Q, G) of a partner stock and keeps that partner while both stay in the cross-section, so a receiver's null score
    history is another stock's real score history (persistence, distribution, group counts and dates preserved).
    Momentum, trend and returns stay with the receiver: only the link between a stock's chart score and its own future
    return is broken. Everything downstream (groups, IC, incremental regression, monotonicity, stability, gates) is
    recomputed."""
    T = ChartTether(seed) if seed is not None else None
    series, years = [], []
    for p in prep:
        ix = None
        if T is not None:
            pos = {s: i for i, s in enumerate(p["ids"])}
            ix = np.array([pos[s] for s in T.step(p["ids"], p["strata"])])
        series.append(fast_date_stats(p, ix))
        years.append(p["year"])
    out = summarise(series, years, lag, ann)
    if keep_series:
        out["_series"], out["_years"] = series, years
    return out


def critical_values(null_worlds, alpha=ALPHA):
    """c_stat = the k-th largest null value of each statistic, k = ceil(alpha x R) (R = 5,000, alpha = 1% -> the 50th
    largest)."""
    return {k: X.critical_value([w[k] for w in null_worlds], alpha) for k in STATS}
