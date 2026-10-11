# qr_h024.py — H024 Feature Redesign and Selection (owner D201; research/phase9/H024_spec.md, pinned by
# qresearch.p9h024). Pure numpy. The 11-feature library (spec section 4), the percentile transform and equal-weight
# model scores (section 5), the redundancy / component rule and the model library (section 6), the development gates
# D1-D6 and the robust-neighbourhood rule (section 9), the selection rule (section 10), the optimiser-null record
# (section 8) and the walk-forward / stability diagnostics (section 11). All per-column statistics, the response and
# the identity-tethered null are the frozen H022 / H023 ones (qr_h023.world / summarise / filters on top of
# qr_p7_pred and qr_xs, unchanged): every feature and every model is one column of one score matrix, and a null world
# re-indexes the whole score side (a partner's complete feature vector) with one tether permutation per date.
import json
import math
from itertools import combinations

import numpy as np

import qr_h023 as G
import qr_p7 as P7
import qr_p7_pred as R
import qr_xs as X

# ----------------------------------------------------------------------------------------------- frozen library
# spec section 3.2: the 13 ranked candidates (evidence tier -> PIT quality -> interpretability; no return used)
RANKED = ("MOM", "LOWVOL", "GPA", "ACC", "BM", "AG", "REV1M", "CBOP", "HI52", "CFP", "EQA", "SECTOR", "TREND")
FAMILY = dict(MOM="momentum", LOWVOL="risk", GPA="profitability", ACC="accruals", BM="valuation", AG="investment",
              REV1M="reversal", CBOP="profitability", HI52="momentum", CFP="valuation", EQA="leverage",
              SECTOR="sector", TREND="momentum")
EXCLUDED = dict(
    REVG="Score v1 revenue growth: direction theoretically ambiguous (growth 'better' in Score v1; past sales growth "
         "predicts lower returns, Lakonishok-Shleifer-Vishny 1994) -> excluded, not tested in both directions",
    NET_ISSUANCE="share-count levels unsafe (D107); implied shares need market caps missing for ~18% (D187)",
    INDUSTRY_MOMENTUM="tested in H021-A (sector ETF relative momentum, failed); overlaps V1-8",
    IDIO_VOL="redundant with total volatility; needs an extra factor model / window choice",
    EP="second valuation proxy; operating cash-flow yield kept as less accrual-sensitive",
    EARNINGS_DRIFT="H017; separate event data")
MAX_FEATURES = 15
MODEL_BUDGET = 500
SIZES = (2, 3, 4)
DIRECTION = dict(MOM=1, LOWVOL=-1, GPA=1, ACC=1, BM=1, AG=-1, REV1M=-1, CBOP=1, HI52=1, CFP=1, EQA=1)
SCOPE = dict(GPA="sector", EQA="sector")              # all other features: market-wide
MIN_SECTOR_GROUP = 10
COVERAGE_MIN = 0.90                                    # of the H022 population stock-months (canary, no return)
REDUNDANCY_RHO = 0.80                                  # median |Spearman| over the dates -> linked
ENTRY = 80.0
D6_FRAC = 0.40
NBR_MIN = 3
FOLD_YEARS = G.FOLD_YEARS                              # (2014, 2015, 2016, 2017)
R_NULL, ALPHA, CRIT_FLOOR = G.R_NULL, G.ALPHA, G.CRIT_FLOOR
# price windows (bars on the security's own valid bars inside its current life)
MOM_SKIP, MOM_LOOKBACK, VOL_WINDOW = 21, 252, 60       # = qr_p7_score (MOM, LOWVOL come from technical_inputs)
REV_WINDOW = 21
HI_WINDOW = 252
LARGE_DISTRIBUTION = 0.10                              # = qr_p7_score.LARGE_DISTRIBUTION
SPAN = 420                                             # = qr_p7_export.SPAN (slice with exactness fallback)
CONTROLS = ((40, 45, 15), (80, 10, 10))                # Score v1, H023 best (descriptive only, never candidates)


def model_count(sizes_by_component, ks=SIZES):
    return sum(math.prod(c) for k in ks for c in combinations(sizes_by_component, k))


def library_prefix(ranked=RANKED, family=FAMILY, budget=MODEL_BUDGET, cap=MAX_FEATURES):
    """Spec 3.3: the longest rank-order prefix (<= cap) whose family-constrained 2-4 feature model count <= budget."""
    best = ()
    for n in range(1, min(cap, len(ranked)) + 1):
        fams = {}
        for f in ranked[:n]:
            fams[family[f]] = fams.get(family[f], 0) + 1
        if model_count(list(fams.values())) <= budget:
            best = tuple(ranked[:n])
        else:
            break
    return best


LIBRARY = library_prefix()                            # ('MOM', 'LOWVOL', 'GPA', 'ACC', 'BM', 'AG', 'REV1M', 'CBOP', 'HI52', 'CFP', 'EQA')


# ----------------------------------------------------------------------------------------------- feature values
def price_features(C, P, t, unverified_rows=(), distributions=(), span=SPAN, gap=P7.LIFE_GAP):
    """REV1M and HI52 of ONE security at calendar row t (spec section 4): REV1M = P[b]/P[b-21] - 1 (22 valid bars in
    the current life); HI52 = C[b] / max(C[b-251..b]) (252 valid bars; invalid if an unverified split or a large
    (>= 10%) distribution lies inside the 252-bar window). Bars are the security's own valid bars (C and P both
    positive) in its current life (qr_p7.LIFE_GAP). Computed on the slice [t - span, t]; the full history is used
    whenever the slice holds fewer than HI_WINDOW valid bars (exactness, as qr_p7_export.tech_at)."""
    C, P = np.asarray(C, float), np.asarray(P, float)
    lo = max(0, int(t) - span)
    for attempt in (0, 1):
        v = P7.valid_rows(C[lo:t + 1], P[lo:t + 1])
        if attempt == 0 and lo > 0 and v.size < HI_WINDOW:
            lo = 0
            continue
        break
    out = dict(REV1M=None, HI52=None)
    if v.size == 0:
        return out
    b = v.size - 1
    s = int(P7.life_starts(v, gap)[b])
    n = b - s + 1
    c, p = C[lo:t + 1][v], P[lo:t + 1][v]
    if n >= REV_WINDOW + 1:
        out["REV1M"] = float(p[b] / p[b - REV_WINDOW] - 1.0)
    if n >= HI_WINDOW:
        first, last = int(v[b - HI_WINDOW + 1]), int(v[b])
        bad = any(first < int(e) - lo <= last for e in unverified_rows) or any(
            first < int(e) - lo <= last for e, f in distributions if f >= LARGE_DISTRIBUTION)
        if not bad:
            out["HI52"] = float(c[b] / c[b - HI_WINDOW + 1:b + 1].max())
    return out


def fund_features(vals, ta_prev, mcap):
    """GPA, ACC, EQA (= the frozen qr_p7_score.fundamental_inputs formulas), CBOP, BM, CFP, AG from the PIT values
    (rev, gp, ni, ocf True TTM, total assets, equity), the total assets recorded live at the review 12 months earlier
    and the review's point-in-time market cap. Invalid -> None."""
    rev, gp, ni, ocf, ta, eq = vals
    ok = lambda *xs: all(x is not None and math.isfinite(x) for x in xs)  # noqa: E731
    out = dict(GPA=None, ACC=None, EQA=None, CBOP=None, BM=None, CFP=None, AG=None)
    if ok(ta) and ta > 0:
        if ok(gp):
            out["GPA"] = gp / ta
        if ok(ocf, ni):
            out["ACC"] = (ocf - ni) / ta
        if ok(eq):
            out["EQA"] = eq / ta
        if ok(ocf):
            out["CBOP"] = ocf / ta
        if ok(ta_prev) and ta_prev > 0:
            out["AG"] = ta / ta_prev - 1.0
    if ok(mcap) and mcap > 0:
        if ok(eq) and eq > 0:
            out["BM"] = eq / mcap
        if ok(ocf):
            out["CFP"] = ocf / mcap
    return out


def feature_row(ti, pf, ff, features=LIBRARY):
    """One stock's raw library values in library order (NaN = invalid): MOM / LOWVOL from the frozen Score v1
    technical inputs (mom_12_1, vol60), REV1M / HI52 from price_features, the rest from fund_features."""
    src = dict(MOM=ti.get("mom_12_1"), LOWVOL=ti.get("vol60"), **pf, **ff)
    return [float(src[f]) if src.get(f) is not None and math.isfinite(src[f]) else float("nan") for f in features]


# ----------------------------------------------------------------------------------------------- transform / library
def percentiles(Xr, sector, features=LIBRARY):
    """Xr: (n, F) raw values of the H024 population on one date (all valid). p = (r - 1) / (n_G - 1) of the ORIENTED
    value Dir * x by average rank inside the scope group (market, or the FF12 group when it has >= 10 members)."""
    Xr = np.asarray(Xr, float)
    n, F = Xr.shape
    Pm = np.empty((n, F))
    sec = np.asarray(sector)
    for j, f in enumerate(features):
        v = DIRECTION[f] * Xr[:, j]
        r = X.avg_rank(v)
        Pm[:, j] = (r - 1.0) / (n - 1) if n > 1 else 0.5
        if SCOPE.get(f) == "sector":
            for g in np.unique(sec):
                ix = np.flatnonzero(sec == g)
                if ix.size >= MIN_SECTOR_GROUP:
                    rg = X.avg_rank(v[ix])
                    Pm[ix, j] = (rg - 1.0) / (ix.size - 1)
    return Pm


def components_of(features, family, links=()):
    """Connected components of the family relation and the redundancy links (pairs of feature ids)."""
    parent = {f: f for f in features}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a in features:
        for b in features:
            if a < b and family[a] == family[b]:
                parent[find(a)] = find(b)
    for a, b in links:
        if a in parent and b in parent:
            parent[find(a)] = find(b)
    comp = {f: find(f) for f in features}
    names = {r: i for i, r in enumerate(sorted(set(comp.values()), key=lambda r: min(f for f in features if comp[f] == r)))}
    return {f: names[comp[f]] for f in features}


def redundancy_links(median_abs_rho, features=LIBRARY, family=FAMILY, rho=REDUNDANCY_RHO):
    """Spec section 6: pairs from DIFFERENT families whose median over dates of |Spearman| >= 0.80."""
    out = []
    for i, a in enumerate(features):
        for j, b in enumerate(features):
            if i < j and family[a] != family[b] and median_abs_rho[i][j] >= rho:
                out.append(tuple(sorted((a, b))))
    return sorted(out)


def model_library(features=LIBRARY, family=FAMILY, links=()):
    """Every 2-, 3- or 4-feature set with at most one feature per component; ordered by size, then sorted ids."""
    comp = components_of(features, family, links)
    out = []
    for k in SIZES:
        for c in combinations(sorted(features), k):
            if len({comp[f] for f in c}) == k:
                out.append(c)
    return sorted(out, key=lambda m: (len(m), m))


def library_sha(models):
    return __import__("hashlib").sha256(json.dumps([list(m) for m in models], separators=(",", ":")).encode()).hexdigest()


class Library:
    """Columns: the F single features (oriented percentiles), the M models, then the 2 controls (descriptive)."""

    def __init__(self, models, features=LIBRARY):
        self.features = tuple(features)
        self.models = [tuple(m) for m in models]
        F, M = len(self.features), len(self.models)
        self.F, self.M = F, M
        self.fidx = {f: j for j, f in enumerate(self.features)}
        self.mcol = {m: F + i for i, m in enumerate(self.models)}
        self.ncol = F + M + len(CONTROLS)
        self.ctrl_cols = tuple(range(F + M, self.ncol))
        W = np.zeros((F, F + M))
        W[np.arange(F), np.arange(F)] = 1.0
        for i, m in enumerate(self.models):
            for f in m:
                W[self.fidx[f], F + i] = 1.0 / len(m)
        self.W = W
        self.k = np.array([len(m) for m in self.models])
        # leave-one-feature-out columns (k = 2 -> the remaining single feature's column)
        self.loo = np.full((M, 4), -1)
        for i, m in enumerate(self.models):
            for j, f in enumerate(m):
                rest = tuple(x for x in m if x != f)
                self.loo[i, j] = self.fidx[rest[0]] if len(rest) == 1 else self.mcol[rest]
        # neighbours: same size, exactly one feature replaced, result in the library
        nb = []
        for m in self.models:
            sm = set(m)
            nb.append(sorted(self.mcol[x] - F for x in self.models if len(x) == len(m) and len(sm ^ set(x)) == 2))
        self.nbr = nb
        self.sha = library_sha(self.models)


def score_matrix(Pm, lib, C=None):
    """(n, F + M [+ 2]) scores on 0..100: features 100 * p, models 100 * mean(p); controls (if C given) = Score v1
    total and H023 80/10/10 from the frozen layer subtotals (qr_h023 exact integer formula / 360)."""
    S = 100.0 * (Pm @ lib.W)
    if C is not None:
        Z = G.z_scores(C, list(CONTROLS)) / float(G.SCALE)
        S = np.column_stack([S, Z])
    return S


# ----------------------------------------------------------------------------------------------- prepared panel
def population(d, features=LIBRARY, horizon="y"):
    """Mask of the H024 population on one date: finite response and every library feature valid."""
    y = np.asarray(d[horizon], float)
    Xr = np.asarray(d["X"], float).reshape(len(y), -1)
    return np.isfinite(y) & np.all(np.isfinite(Xr), axis=1)


def prepare(dates, lib, horizon="y", controls=True):
    """dates: dicts with ids, X (n, F raw library values, NaN invalid), sector (FF12), C (layer subtotals), year, day
    and responses y / y2 / y3 over the H022 population. Keys as qr_h023.prepare so qr_h023.world / summarise apply."""
    out = []
    for d in dates:
        ok = population(d, lib.features, horizon)
        if ok.sum() < R.MIN_STOCKS:
            continue
        y = np.asarray(d[horizon], float)[ok]
        Pm = percentiles(np.asarray(d["X"], float)[ok], np.asarray(d["sector"])[ok], lib.features)
        S = score_matrix(Pm, lib, np.asarray(d["C"])[ok] if controls else None)
        n, g = S.shape
        yd = y - float(y.mean())
        ry = X.avg_rank(yd)
        RQ = G.avg_rank_cols(S)
        mid = (n + 1) / 2.0
        RQc, ryc = RQ - mid, ry - mid
        den = np.sqrt((RQc * RQc).sum(axis=0) * float(ryc @ ryc))
        Q = np.minimum(G.N_Q, np.floor(G.N_Q * (RQ - 0.5) / n).astype(np.int64) + 1)
        hi = S >= ENTRY
        cnt = np.zeros((G.N_Q, g), np.int64)
        for k in range(G.N_Q):
            cnt[k] = (Q == k + 1).sum(axis=0)
        out.append(dict(ids=np.asarray(d["ids"])[ok].tolist(), Z=np.empty((0, g)), RQc=RQc, ryc=ryc, den=den, Q=Q,
                        hi=hi, qcnt=cnt, nhi=hi.sum(axis=0), yd=yd, year=int(d["year"]), day=d.get("day"), n=n))
    return out


# ----------------------------------------------------------------------------------------------- gates and selection
def gates(s, lib, c_model):
    """D1-D5 (qr_h023.filters, frozen H023 formulas), D6 and the robust-neighbourhood rule N for the M model columns.
    Returns dict of boolean arrays over the models (length M) plus robust-neighbour lists."""
    F, M = lib.F, lib.M
    sl = slice(F, F + M)
    f = {k: v[sl] for k, v in G.filters(s, c_model).items()}
    ic = s["ic_mean"]
    icm = ic[sl]
    loo_ok = np.ones(M, bool)
    for j in range(4):
        col = lib.loo[:, j]
        has = col >= 0
        v = np.where(has, ic[np.where(has, col, 0)], np.inf)
        loo_ok &= ~has | ((v > 0) & (v >= D6_FRAC * icm))
    f["D6"] = loo_ok
    hi = np.nan_to_num(s["hi_ann"], nan=-np.inf)
    robust_col = (ic > 0) & (hi > 0) & (s["q5_minus_q1_ann"] > 0)
    rn = [[x for x in nb if robust_col[F + x]] for nb in lib.nbr]
    f["N"] = np.array([len(x) >= NBR_MIN for x in rn], bool)
    f["robust_nbrs"] = rn
    f["pre_D1"] = f["D2_5"] & f["D6"] & f["N"] & (icm > 0)
    f["qualified"] = f["D1"] & f["D2_5"] & f["D6"] & f["N"]
    return f


def select(s, lib, c_model):
    """Spec section 10 over the qualified models: smallest size -> highest median t of its robust neighbours ->
    highest t -> highest 80+ -> sorted feature ids. Returns (model index or None, gates, ranked qualified list)."""
    g = gates(s, lib, c_model)
    t = s["t_ic"][lib.F:lib.F + lib.M]
    hi = np.nan_to_num(s["hi_ann"][lib.F:lib.F + lib.M], nan=-np.inf)

    def key(i):
        rn = g["robust_nbrs"][i]
        med = float(np.median(t[rn])) if rn else -math.inf
        return (lib.k[i], -med, -t[i], -hi[i], lib.models[i])
    q = [i for i in range(lib.M) if g["qualified"][i]]
    ranked = sorted(q, key=key)
    return (ranked[0] if ranked else None), g, ranked


def cstar(s, lib):
    """Largest model t_IC among models passing D2-D6, N and mean IC > 0: a candidate exists for c iff c < cstar."""
    g = gates(s, lib, math.inf)
    t = s["t_ic"][lib.F:lib.F + lib.M]
    m = g["pre_D1"]
    return float(t[m].max()) if m.any() else -math.inf


# ----------------------------------------------------------------------------------------------- null
NULL_FIELDS = ("seed", "max_t_feature", "argmax_feature", "max_t_model", "argmax_model", "max_t_model_fold2014",
               "max_t_model_fold2015", "max_t_model_fold2016", "max_t_model_fold2017", "n_pre_d1", "cstar")


def null_record(prep, lib, seed):
    """One null world: the frozen identity tether re-indexes every stock's complete score side (all features, all
    models); every column is recomputed; maxima for c_FEATURE / c_MODEL / c_FOLD and the full-procedure summary."""
    w = G.world(prep, seed)
    s = G.summarise(w)
    t = s["t_ic"]
    tf, tm = t[:lib.F], t[lib.F:lib.F + lib.M]
    folds = [float(G.tstats(w["IC"][w["years"] < y][:, lib.F:lib.F + lib.M]).max()) for y in FOLD_YEARS]
    g = gates(s, lib, math.inf)
    return [int(seed), float(tf.max()), int(np.argmax(tf)), float(tm.max()), int(np.argmax(tm))] + folds + [
        int(g["pre_D1"].sum()), float(tm[g["pre_D1"]].max()) if g["pre_D1"].any() else -math.inf]


def critical_value(max_t):
    return G.critical_value(max_t)


# ----------------------------------------------------------------------------------------------- diagnostics
def fold(w, lib, year, c_fold):
    tr, ob = w["years"] < year, w["years"] == year
    if tr.sum() < 2 or not ob.any():
        return dict(year=year, selected=None, how="empty_window", observe_ic=float("nan"), observe_ic_series=[],
                    observe_hi_monthly=[], observe_hi_ann=float("nan"), train_months=int(tr.sum()),
                    observe_months=int(ob.sum()), c_fold=float(c_fold))
    s = G.summarise(w, rows=tr)
    pick, _, ranked = select(s, lib, c_fold)
    how = "strict"
    if pick is None:
        pick, how = int(np.argmax(s["t_ic"][lib.F:lib.F + lib.M])), "argmax_t_no_strict_candidate"
    col = lib.F + pick
    ic, hi = w["IC"][ob, col], w["HI"][ob, col]
    hm = float(np.nanmean(hi)) if np.isfinite(hi).any() else float("nan")
    return dict(year=year, train_months=int(tr.sum()), observe_months=int(ob.sum()), c_fold=float(c_fold),
                selected=list(lib.models[pick]), index=int(pick), how=how, n_strict=len(ranked),
                train_t=float(s["t_ic"][col]), train_ic=float(s["ic_mean"][col]), observe_ic=float(ic.mean()),
                observe_ic_series=ic.tolist(), observe_hi_monthly=hi.tolist(), observe_hi_ann=hm * G.ANN)


def walk_forward(w, lib, c_folds):
    fs = [fold(w, lib, y, c) for y, c in zip(FOLD_YEARS, c_folds)]
    ic = np.concatenate([np.asarray(f["observe_ic_series"], float) for f in fs])
    hi = np.concatenate([np.asarray(f["observe_hi_monthly"], float) for f in fs])
    m, se, t = X.nw_tstat(ic, G.NW_LAG) if ic.size else (float("nan"),) * 3
    sel = [set(f["selected"]) for f in fs if f["selected"]]
    overlap = [[len(a & b) for b in sel] for a in sel]
    freq = {}
    for f in fs:
        for x in f["selected"] or ():
            freq[x] = freq.get(x, 0) + 1
    return dict(folds=fs, overlap=overlap, feature_frequency=freq, pseudo_oos=dict(
        months=int(ic.size), ic_mean=m, se=se, t=t, positive_months=int((ic > 0).sum()),
        hi_ann=(float(np.nanmean(hi)) * G.ANN) if np.isfinite(hi).any() else float("nan")))


def stability(s, lib, g, folds, top=10):
    t = s["t_ic"][lib.F:lib.F + lib.M]
    topi = [int(i) for i in np.argsort(-t, kind="mergesort")[:top]]
    out = {}
    for f in lib.features:
        out[f] = dict(qualified=int(sum(1 for i in range(lib.M) if g["qualified"][i] and f in lib.models[i])),
                      top10=int(sum(1 for i in topi if f in lib.models[i])),
                      folds=int(sum(1 for x in folds if x["selected"] and f in x["selected"])))
    return out, [lib.models[i] for i in topi]


def evaluate(prep, lib, c_model, c_folds):
    """The one real development search: every column, gates, selection, walk-forward, stability, cstar."""
    w = G.world(prep)
    s = G.summarise(w)
    pick, g, ranked = select(s, lib, c_model)
    wf = walk_forward(w, lib, c_folds)
    stab, top = stability(s, lib, g, wf["folds"])
    return dict(world=w, summary=s, pick=pick, gates=g, ranked=ranked, walk_forward=wf, stability=stab, top10=top,
                cstar=cstar(s, lib), argmax_model=int(np.argmax(s["t_ic"][lib.F:lib.F + lib.M])))
