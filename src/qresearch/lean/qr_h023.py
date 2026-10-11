# qr_h023.py — H023 Score v2 weight search (owner D199; research/phase8/H023_spec.md, pinned by qresearch.p8h023).
# Pure numpy. Re-weights ONLY the three frozen Score v1 layer subtotals (Technical /40, Fundamental /45, Sector /15) of
# the frozen Data v2 H022 population; everything inside the layers, the population, the response, the 80 threshold, the
# Newey-West lag, the quintile / block conventions and the identity-tethered null are the frozen H022 ones (qr_p7_pred,
# qr_xs, qr_h020_stats, unchanged). The whole 92-configuration grid is evaluated in every world (real or null) with ONE
# tether permutation per date shared by all configurations, exactly as the real optimiser.
#
# Score_v2 = wT * Tech/40 + wF * Fund/45 + wS * Sect/15 (wT + wF + wS = 100). Computed EXACTLY as the integer
# Z = 360 * Score_v2 = 9 wT Tech + 8 wF Fund + 24 wS Sect, so ranks, ties, quintiles and the 80+ group (Z >= 28,800)
# carry no floating-point rounding; at 40 / 45 / 15, Z = 360 x the Score v1 total (identical ranks / groups).
import math
import warnings

import numpy as np

import qr_p7_pred as R
import qr_xs as X

LAYERS = ("technical", "fundamental", "sector")
LAYER_MAX = (40, 45, 15)
SCALE = 360                                   # lcm(40, 45, 15)
MULT = (9, 8, 24)                             # SCALE / LAYER_MAX
CONTROL = (40, 45, 15)                        # Score v1 (H022, Rejected): the control configuration
STEP = 5
W_T = tuple(range(10, 81, STEP))
W_F = tuple(range(10, 81, STEP))
W_S = tuple(range(0, 31, STEP))
TOTAL = 100
ENTRY = R.ENTRY                               # 80, fixed (not optimised)
THRESHOLDS = (75, 80, 85, 90)                 # structural counts
NW_LAG = R.NW_LAG                             # 2
ANN = R.ANN
N_Q = R.N_Q
BLOCKS = R.BLOCKS
# development filters D1-D5 (owner D199 section 17)
ECON_MIN = 0.03                               # D2
MONO_MIN = 0.90                               # D3
BLOCK_MAX_SHARE = 0.5                         # D4
D5_MONTHS, D5_OF, D5_MEAN = 60, 83, 2.0       # D5: 80+ stocks in >= 60 of the 83 months and mean count >= 2
# search null (section 14-16)
R_NULL = 5000
ALPHA = 0.01
CRIT_FLOOR = 2.326
# plateau (section 18) and selection (section 19)
PLATEAU_MIN = 4
PLATEAU_FRAC = 0.80
# walk-forward diagnostic (section 23): train on decision years < Y, observe decision year Y
FOLD_YEARS = (2014, 2015, 2016, 2017)
DIAG_HORIZONS = ((2, "y2"), (3, "y3"))        # diagnostics only (Newey-West lag = horizon, the H022 convention)


# ----------------------------------------------------------------------------------------------- grid
def grid():
    """The 92 pre-registered weight triplets (wT, wF, wS), lexicographic order; the control 40/45/15 is a member."""
    return tuple(sorted((t, f, s) for t in W_T for f in W_F for s in W_S if t + f + s == TOTAL))


GRID = grid()
CONTROL_INDEX = GRID.index(CONTROL)
_W = np.array(GRID, dtype=np.int64) * np.array(MULT, dtype=np.int64)        # (G, 3)


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def adjacency(G=GRID):
    """Neighbours: one 5-point transfer between two layers, the third unchanged (L1 distance 10 on the simplex)."""
    return {i: [j for j, b in enumerate(G) if l1(a, b) == 2 * STEP] for i, a in enumerate(G)}


ADJ = adjacency()


def on_boundary(w):
    """Grid boundary (owner section 6: report, never extend): wT or wF at 10 / 80, wS at 0 / 30."""
    return w[0] in (W_T[0], W_T[-1]) or w[1] in (W_F[0], W_F[-1]) or w[2] in (W_S[0], W_S[-1])


def layer_split(points):
    """Score v1 points tuple in qr_p7_export.DIMS order (trend, momentum, risk, profitability, cash_conversion,
    balance_sheet, growth, sector) -> the three frozen layer subtotals (Technical, Fundamental, Sector)."""
    p = [int(x) for x in points]
    return (p[0] + p[1] + p[2], p[3] + p[4] + p[5] + p[6], p[7])


def z_scores(C, G=None):
    """C: (n, 3) integer layer subtotals -> (n, G) integer 360 x Score_v2."""
    W = _W if G is None else np.array(G, dtype=np.int64) * np.array(MULT, dtype=np.int64)
    return np.asarray(C, dtype=np.int64).reshape(-1, 3) @ W.T


def score_v2(C, w):
    """Score_v2 of one configuration as a float (reporting only; decisions use the exact integer z_scores)."""
    C = np.asarray(C, dtype=np.int64).reshape(-1, 3)
    return (C @ (np.array(w, dtype=np.int64) * np.array(MULT, dtype=np.int64))) / SCALE


def avg_rank_cols(Z):
    """Column-wise average ranks 1..n (ties share the mean rank) — identical to qr_xs.avg_rank on every column."""
    Z = np.asarray(Z)
    n, g = Z.shape
    if n == 0:
        return np.empty((0, g))
    order = np.argsort(Z, axis=0, kind="mergesort")
    xs = np.take_along_axis(Z, order, axis=0)
    idx = np.broadcast_to(np.arange(n)[:, None], (n, g))
    newg = np.ones((n, g), bool)
    newg[1:] = xs[1:] != xs[:-1]
    start = np.maximum.accumulate(np.where(newg, idx, 0), axis=0)
    endg = np.ones((n, g), bool)
    endg[:-1] = xs[1:] != xs[:-1]
    end = np.minimum.accumulate(np.where(endg, idx, n - 1)[::-1], axis=0)[::-1]
    r = np.empty((n, g))
    np.put_along_axis(r, order, (start + end) / 2.0 + 1.0, axis=0)
    return r


# ----------------------------------------------------------------------------------------------- per date
def prepare(dates, horizon="y", G=None):
    """dates: the H022 prepared-panel dicts (qr_p7_pred.prepare input) with an added 'C' = (n, 3) integer layer
    subtotals aligned with ids. Same row rule as qr_p7_pred.prepare (finite response; dates with < MIN_STOCKS rows are
    skipped). Everything that does not depend on the null world is computed once."""
    G = GRID if G is None else tuple(G)
    g = len(G)
    out = []
    for d in dates:
        y = np.asarray(d[horizon], float)
        ok = np.isfinite(y)
        if ok.sum() < R.MIN_STOCKS:
            continue
        C = np.asarray(d["C"], dtype=np.int64).reshape(-1, 3)[ok]
        Z = z_scores(C, G)
        n = Z.shape[0]
        yd = y[ok] - float(y[ok].mean())
        ry = X.avg_rank(yd)
        RQ = avg_rank_cols(Z)
        mid = (n + 1) / 2.0
        RQc = RQ - mid
        ryc = ry - mid
        den = np.sqrt((RQc * RQc).sum(axis=0) * float(ryc @ ryc))
        Q = np.minimum(N_Q, np.floor(N_Q * (RQ - 0.5) / n).astype(np.int64) + 1)
        hi = Z >= ENTRY * SCALE
        cnt = np.zeros((N_Q, g), np.int64)
        for k in range(N_Q):
            cnt[k] = (Q == k + 1).sum(axis=0)
        out.append(dict(ids=np.asarray(d["ids"])[ok].tolist(), C=C, Z=Z, RQc=RQc, ryc=ryc, den=den, Q=Q, hi=hi,
                        qcnt=cnt, nhi=hi.sum(axis=0), yd=yd, year=int(d["year"]), day=d.get("day"),
                        thr=np.array([(Z >= t * SCALE).sum(axis=0) for t in THRESHOLDS]), regime=d.get("regime")))
    return out


def date_grid(p, ix=None):
    """One date, every configuration: (ic (G,), quintile means (G, 5), 80+ mean (G,), 80+ count (G,)). ix re-indexes
    the SCORE side (all three layer subtotals of a partner stock together) for a null world; the response stays."""
    g = p["Z"].shape[1]
    RQc = p["RQc"] if ix is None else p["RQc"][ix]
    Q = p["Q"] if ix is None else p["Q"][ix]
    hi = p["hi"] if ix is None else p["hi"][ix]
    yd = p["yd"]
    num = RQc.T @ p["ryc"]
    ic = np.where(p["den"] > 0, num / np.where(p["den"] > 0, p["den"], 1.0), 0.0)
    bins = (Q - 1) * g + np.arange(g)[None, :]
    sm = np.bincount(bins.ravel(), weights=np.repeat(yd, g), minlength=N_Q * g).reshape(N_Q, g)
    with np.errstate(invalid="ignore", divide="ignore"):
        qm = np.where(p["qcnt"] > 0, sm / p["qcnt"], np.nan).T
        hm = np.where(p["nhi"] > 0, (yd @ hi) / p["nhi"], np.nan)
    return ic, qm, hm, p["nhi"]


def world(prep, seed=None):
    """Raw per-date matrices of one world: IC (D, G), QM (D, G, 5), HI (D, G), NH (D, G), years (D,). seed None = the
    real assignment; otherwise the frozen identity-tethered null (qr_p7_pred.Tether(seed): one stratum, no
    self-matches, the H022 seeds), one permutation per date applied to the whole grid."""
    T = R.Tether(seed) if seed is not None else None
    D = len(prep)
    g = prep[0]["Z"].shape[1] if D else len(GRID)
    IC, HI, NH = np.empty((D, g)), np.empty((D, g)), np.empty((D, g), np.int64)
    QM = np.empty((D, g, N_Q))
    for i, p in enumerate(prep):
        ix = None
        if T is not None:
            pos = {s: j for j, s in enumerate(p["ids"])}
            ix = np.array([pos[s] for s in T.step(p["ids"])])
        IC[i], QM[i], HI[i], NH[i] = date_grid(p, ix)
    return dict(IC=IC, QM=QM, HI=HI, NH=NH, years=np.array([p["year"] for p in prep]))


# ----------------------------------------------------------------------------------------------- summaries
def nw_cols(A, lag=NW_LAG):
    """Column-wise qr_xs.nw_tstat: mean, Newey-West (Bartlett) SE and t of every column of A (T, G)."""
    A = np.asarray(A, float)
    T = A.shape[0]
    m = A.mean(axis=0)
    e = A - m
    lrv = (e * e).sum(axis=0) / T
    for l in range(1, min(lag, T - 1) + 1):
        lrv = lrv + 2.0 * (1.0 - l / (lag + 1.0)) * (e[l:] * e[:-l]).sum(axis=0) / T
    se = np.sqrt(np.maximum(lrv, 0.0) / T)
    t = np.where(se > 0, m / np.where(se > 0, se, 1.0), 0.0)
    return m, se, t


def tstats(IC, lag=NW_LAG):
    return nw_cols(IC, lag)[2]


def summarise(w, lag=NW_LAG, ann=ANN, rows=None):
    """Per-configuration summaries (arrays over the grid) with the qr_p7_pred.summarise formulas; rows = an optional
    boolean mask of dates (a walk-forward training prefix or an observation year)."""
    IC, QM, HI, NH, yrs = w["IC"], w["QM"], w["HI"], w["NH"], w["years"]
    if rows is not None:
        IC, QM, HI, NH, yrs = IC[rows], QM[rows], HI[rows], NH[rows], yrs[rows]
    D, g = IC.shape
    m, se, t = nw_cols(IC, lag)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        qmean = np.nanmean(QM, axis=0)                                      # (G, 5)
        hi_m = np.nanmean(HI, axis=0)
    hi_months = np.isfinite(HI).sum(axis=0)
    hi_m = np.where(hi_months > 0, hi_m, np.nan)
    half = D // 2
    mono = np.array([X.spearman(np.arange(1, N_Q + 1, dtype=float), qmean[c]) for c in range(g)])
    ys = sorted(set(yrs.tolist()))
    blocks = np.array([[IC[(yrs >= a) & (yrs <= b), c].sum() for a, b in BLOCKS] for c in range(g)])   # (G, 4)
    tot = IC.sum(axis=0)
    return dict(
        n_dates=D, ic_mean=m, ic_se=se, t_ic=t, q_mean=qmean, q_mean_ann=qmean * ann,
        q5_minus_q1_ann=(qmean[:, -1] - qmean[:, 0]) * ann, mono=mono,
        hi_monthly=hi_m, hi_ann=hi_m * ann, hi_months=hi_months, hi_n_mean=NH.mean(axis=0), hi_stock_months=NH.sum(axis=0),
        half1=IC[:half].mean(axis=0), half2=IC[half:].mean(axis=0),
        block_sum=blocks, ic_sum=tot,
        block_max=np.array([X.block_share_max(IC[:, c], yrs, BLOCKS) for c in range(g)]),
        years={y: IC[yrs == y].mean(axis=0) for y in ys}, positive_months=(IC > 0).sum(axis=0))


def base_ok(s):
    """Plateau membership conditions (section 18): mean IC > 0, 80+ annualised > 0, Q5 > Q1, both halves > 0."""
    hi = np.nan_to_num(s["hi_ann"], nan=-np.inf)
    return (s["ic_mean"] > 0) & (hi > 0) & (s["q5_minus_q1_ann"] > 0) & (s["half1"] > 0) & (s["half2"] > 0)


def filters(s, c_search):
    """Development filters D1-D5 (section 17) per configuration; D5 scales 60 of 83 months to a shorter window
    (walk-forward folds) as months_with_80 / months >= 60 / 83."""
    hi = np.nan_to_num(s["hi_ann"], nan=-np.inf)
    mono = np.nan_to_num(s["mono"], nan=-np.inf)
    n = s["n_dates"]
    d = dict(
        D1=(s["t_ic"] > c_search) & (s["ic_mean"] > 0),
        D2=hi >= ECON_MIN,
        D3=(mono >= MONO_MIN) & (s["q5_minus_q1_ann"] > 0),
        D4=(s["half1"] > 0) & (s["half2"] > 0) & (s["block_max"] <= BLOCK_MAX_SHARE),
        D5=(s["hi_months"] * D5_OF >= D5_MONTHS * n) & (s["hi_n_mean"] >= D5_MEAN))
    d["D2_5"] = d["D2"] & d["D3"] & d["D4"] & d["D5"]
    d["qualified"] = d["D1"] & d["D2_5"]
    return d


def components(members, adj=ADJ):
    """Connected components of a set of grid indices under the grid adjacency; each sorted, listed by smallest index."""
    left, out = set(members), []
    for i in sorted(members):
        if i not in left:
            continue
        comp, stack = [], [i]
        left.discard(i)
        while stack:
            k = stack.pop()
            comp.append(k)
            for j in adj[k]:
                if j in left:
                    left.discard(j)
                    stack.append(j)
        out.append(sorted(comp))
    return out


def plateaus(s, adj=ADJ):
    """Robust plateaus (section 18): (1) the connected regions of the configurations satisfying base_ok; (2) in each
    region keep the members with t_IC >= 80% of the region's highest t_IC; (3) every connected component of the kept
    members with >= 4 configurations is a robust plateau. Returns (regions, plateaus) as lists of sorted index lists."""
    ok = np.flatnonzero(base_ok(s)).tolist()
    regions = components(ok, adj)
    out = []
    for reg in regions:
        tmax = max(float(s["t_ic"][i]) for i in reg)
        keep = [i for i in reg if float(s["t_ic"][i]) >= PLATEAU_FRAC * tmax] if tmax > 0 else []
        out += [c for c in components(keep, adj) if len(c) >= PLATEAU_MIN]
    return regions, sorted(out, key=lambda c: c[0])


def _medoid(members, pool, s, G=GRID):
    """The L1 medoid: among `pool` (a subset of `members`), the configuration with the smallest total L1 weight
    distance to all plateau members; ties -> higher t_IC -> smaller L1 distance to 40/45/15 -> lexicographic weights."""
    def key(i):
        return (sum(l1(G[i], G[j]) for j in members), -float(s["t_ic"][i]), l1(G[i], CONTROL), G[i])
    return min(pool, key=key) if pool else None


def plateau_key(c, s):
    """Plateau ranking (section 19): size desc -> median t_IC desc -> median 80+ annualised desc -> first index."""
    t = float(np.median(s["t_ic"][c]))
    h = float(np.median(np.nan_to_num(s["hi_ann"][c], nan=-np.inf)))
    return (-len(c), -t, -h, c[0])


def select(s, c_search, adj=ADJ, G=GRID):
    """The frozen selection rule (spec section 7). A candidate exists iff some configuration is development-qualified
    (D1-D5) AND belongs to a robust plateau. Eligible plateaus = robust plateaus with >= 1 qualified member, ranked by
    plateau_key; the candidate = the L1 medoid of the winning plateau among its qualified members (distances to ALL
    its members). Also reported (not used): the unrestricted ranking / medoid over all plateaus."""
    regions, plats = plateaus(s, adj)
    f = filters(s, c_search)
    q = f["qualified"]
    ranked_all = sorted(plats, key=lambda c: plateau_key(c, s))
    eligible = [c for c in ranked_all if any(q[i] for i in c)]
    win = eligible[0] if eligible else None
    cand = _medoid(win, [i for i in win if q[i]], s, G) if win else None
    top = ranked_all[0] if ranked_all else None
    return dict(regions=regions, plateaus=plats, ranked=ranked_all, eligible=eligible, winner=win, candidate=cand,
                unrestricted_winner=top, unrestricted_medoid=_medoid(top, top, s, G) if top else None,
                filters=f, argmax=int(np.argmax(s["t_ic"])))


def cstar(s, adj=ADJ):
    """Null-world summary of the full procedure: the largest t_IC among robust-plateau members that pass D2-D5 with
    mean IC > 0. A candidate exists for a threshold c iff c < cstar (D1 is the only c-dependent condition), so the
    procedure's false-promotion rate at c_SEARCH is the share of null worlds with cstar > c_SEARCH. -inf if none."""
    _, plats = plateaus(s, adj)
    f = filters(s, np.inf)
    mem = sorted({i for c in plats for i in c if f["D2_5"][i] and s["ic_mean"][i] > 0})
    return max((float(s["t_ic"][i]) for i in mem), default=-math.inf)


# ----------------------------------------------------------------------------------------------- null worlds
NULL_FIELDS = ("seed", "max_t", "argmax", "t_control", "ic_control", "max_t_fold2014", "max_t_fold2015",
               "max_t_fold2016", "max_t_fold2017", "n_base", "n_plateaus", "largest_plateau", "cstar",
               "n_d2_5", "max_t_d2_5")


def null_record(prep, seed):
    """One optimiser-null world: the tethered null of the WHOLE grid; the maximum t_IC across the grid (full window and
    each walk-forward training prefix), the control column (= the H022 null world of the same seed), and the
    full-procedure summaries (plateaus, D2-D5, cstar)."""
    w = world(prep, seed)
    s = summarise(w)
    t = s["t_ic"]
    folds = [float(tstats(w["IC"][w["years"] < y]).max()) for y in FOLD_YEARS]
    _, plats = plateaus(s)
    f = filters(s, np.inf)
    d25 = np.flatnonzero(f["D2_5"] & (s["ic_mean"] > 0))
    a = int(np.argmax(t))
    return [int(seed), float(t[a]), a, float(t[CONTROL_INDEX]), float(s["ic_mean"][CONTROL_INDEX])] + folds + [
        int(base_ok(s).sum()), len(plats), max((len(c) for c in plats), default=0), cstar(s), int(d25.size),
        float(t[d25].max()) if d25.size else -math.inf]


def critical_value(max_t, alpha=ALPHA, floor=CRIT_FLOOR):
    """c = max(the k-th largest of the null maxima, k = ceil(alpha x R) (R = 5,000 -> the 50th largest), floor):
    the frozen one-sided empirical order-statistic convention of H022 (qr_xs.critical_value)."""
    return max(X.critical_value(list(max_t), alpha), floor)


# ----------------------------------------------------------------------------------------------- walk-forward
def fold(w, year, c_fold, G=GRID):
    """Expanding-window diagnostic: select on decision years < year by the frozen rule (D1 with the fold's own
    search-null threshold c_fold), observe decision year `year`. If the strict rule gives no candidate the fold uses the
    unrestricted plateau medoid, else the highest-t configuration (labelled)."""
    tr = w["years"] < year
    ob = w["years"] == year
    if tr.sum() < 2 or not ob.any():               # cannot happen on the 83-month panel (synthetic tests only)
        return dict(year=year, train_months=int(tr.sum()), observe_months=int(ob.sum()), c_fold=float(c_fold),
                    selected=None, index=None, how="empty_window", strict_candidate=False, plateaus=0,
                    train_t=float("nan"), train_ic=float("nan"), argmax=None, observe_ic=float("nan"),
                    observe_ic_series=[], observe_hi_ann=float("nan"), observe_hi_months=0, observe_hi_monthly=[])
    s = summarise(w, rows=tr)
    sel = select(s, c_fold, G=G)
    if sel["candidate"] is not None:
        pick, how = sel["candidate"], "strict"
    elif sel["unrestricted_medoid"] is not None:
        pick, how = sel["unrestricted_medoid"], "plateau_medoid_no_D1_D5"
    else:
        pick, how = sel["argmax"], "argmax_t"
    ic = w["IC"][ob, pick]
    hi = w["HI"][ob, pick]
    with np.errstate(invalid="ignore"):
        hm = float(np.nanmean(hi)) if np.isfinite(hi).any() else float("nan")
    return dict(year=year, train_months=int(tr.sum()), observe_months=int(ob.sum()), c_fold=float(c_fold),
                selected=list(G[pick]), index=int(pick), how=how, strict_candidate=sel["candidate"] is not None,
                plateaus=len(sel["plateaus"]), train_t=float(s["t_ic"][pick]), train_ic=float(s["ic_mean"][pick]),
                argmax=list(G[sel["argmax"]]), observe_ic=float(ic.mean()), observe_ic_series=ic.tolist(),
                observe_hi_ann=hm * ANN, observe_hi_months=int(np.isfinite(hi).sum()),
                observe_hi_monthly=hi.tolist())


def walk_forward(w, c_folds, G=GRID):
    """All four folds, pairwise L1 distances between the fold selections and the aggregate pseudo-out-of-sample IC
    (the four observation years' monthly ICs of their own fold selections, mean and Newey-West t, lag 2)."""
    fs = [fold(w, y, c, G) for y, c in zip(FOLD_YEARS, c_folds)]
    ic = np.concatenate([np.asarray(f["observe_ic_series"], float) for f in fs])
    hi = np.concatenate([np.asarray(f["observe_hi_monthly"], float) for f in fs])
    m, se, t = X.nw_tstat(ic, NW_LAG) if ic.size else (float("nan"), float("nan"), float("nan"))
    sel = [f for f in fs if f["selected"] is not None]
    dist = [[l1(a["selected"], b["selected"]) for b in sel] for a in sel]
    with np.errstate(invalid="ignore"):
        hm = float(np.nanmean(hi)) if np.isfinite(hi).any() else float("nan")
    return dict(folds=fs, distances=dist, max_distance=max((max(r) for r in dist), default=None), pseudo_oos=dict(
        months=int(ic.size), ic_mean=m, se=se, t=t, positive_months=int((ic > 0).sum()), hi_ann=hm * ANN))


# ----------------------------------------------------------------------------------------------- structure / report
QUANTILES = (0, 10, 25, 50, 75, 90, 100)


def structure(prep):
    """Score side only: the pooled Score_v2 distribution and the 75+ / 80+ / 85+ / 90+ counts per configuration."""
    Z = np.vstack([p["Z"] for p in prep])
    thr = np.array([p["thr"] for p in prep])                                    # (D, 4, G)
    return dict(stock_months=int(Z.shape[0]), quantiles=np.percentile(Z, QUANTILES, axis=0) / SCALE,
                mean=Z.mean(axis=0) / SCALE, thr_stock_months=thr.sum(axis=0), thr_mean=thr.mean(axis=0),
                thr_months=(thr > 0).sum(axis=0))


def evaluate(prep, c_search, c_folds, G=GRID):
    """The complete real development search: the whole grid, the frozen selection, the walk-forward diagnostic and the
    structural counts (the one real mapping; the host exports it, research/phase8/cp1/P8_CP1_result.py recomputes it)."""
    w = world(prep)
    s = summarise(w)
    return dict(world=w, summary=s, selection=select(s, c_search, G=G), walk_forward=walk_forward(w, c_folds, G),
                structure=structure(prep), cstar=cstar(s))
