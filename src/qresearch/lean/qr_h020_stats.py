# qr_h020_stats.py — H020 future signal validation: per-date statistics, inference, gates and the null (research/phase5/
# H020_spec.md sections 15-19; P5-CP2). Pure numpy (reuses qr_xs). FROZEN CANDIDATE: constants pinned by qresearch.p5h020.
# NOT run on any real data in P5-CP2: exercised only on synthetic panels (tests/test_h020_stats.py, research/phase5/
# h020_power.py).
#
# One decision date = the cross-section of eligible stocks at a weekly decision close t with, per stock:
#   Q   quality level (-1 disqualified, else score 0..20) and G group (0 = disqualified, 1 = 0-5, 2 = 6-10, 3 = 11-15,
#       4 = 16-20) -- the chart side, the only thing the null permutes (with the four category scores);
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


def family_stat(s):
    return max(s["t_ic"], s["t_inc"])


def promotion(s, c):
    """Frozen gates: all five required."""
    g = dict(
        G1_economic=bool(np.isfinite(s["high_ann"]) and s["high_ann"] >= ECON_MIN_HIGH and
                         np.isfinite(s["low_ann"]) and s["high_ann"] > s["low_ann"]),
        G2_monotonic=bool(np.isfinite(s["mono"]) and s["mono"] >= MONO_MIN),
        G3_significant=bool(s["t_ic"] > c),
        G4_stable=bool(all(h > 0 for h in s["halves"]) and s["block_max"] <= BLOCK_MAX_SHARE),
        G5_incremental=bool(s["t_inc"] > c and s["inc_mean"] > 0),
    )
    g["pass"] = all(g.values())
    return g


def strata(mom, trend):
    """Null strata: momentum quintile (within the date) x trend state -> 10 labels."""
    qb = X.buckets(np.asarray(mom, float), N_MOM_Q)
    return [int(q) * 2 + int(t) for q, t in zip(qb, np.asarray(trend, bool))]


def run_world(dates, seed=None, horizon="y", lag=NW_LAG, ann=ANN, keep_series=False):
    """The complete H020 evaluation for one world. dates = chronological list of dicts with numpy arrays ids (sorted),
    Q, G, mom, trend, y, y13 and the int year. seed None = the real world; otherwise the stratified identity-tethered
    within-date permutation: every receiver gets the chart side (Q, G) of a partner in the same momentum-quintile x
    trend stratum and keeps it while both stay in the cross-section and stratum. Momentum, trend and returns stay with the
    receiver, so only the link between a stock's chart score and its own future return (conditional on the baselines)
    is broken; everything downstream (groups, IC, incremental regression, monotonicity, stability, gates) is recomputed."""
    T = X.Tether(seed) if seed is not None else None
    series, years = [], []
    for d in dates:
        y = d[horizon]
        ok = np.isfinite(y)
        if ok.sum() < 20:
            continue
        ids = d["ids"][ok]
        Q, G, mom, trend, yv = d["Q"][ok], d["G"][ok], d["mom"][ok], d["trend"][ok], y[ok]
        if T is not None:
            pos = {s: i for i, s in enumerate(ids.tolist())}
            src = T.step(ids.tolist(), strata(mom, trend))
            ix = np.array([pos[s] for s in src])
            Q, G = Q[ix], G[ix]
        series.append(date_stats(Q, G, mom, trend, yv))
        years.append(d["year"])
    out = summarise(series, years, lag, ann)
    if keep_series:
        out["_series"], out["_years"] = series, years
    return out


def critical_value(F, alpha=ALPHA):
    return X.critical_value(F, alpha)
