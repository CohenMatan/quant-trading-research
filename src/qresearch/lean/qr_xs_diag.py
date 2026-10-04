# qr_xs_diag.py — H019 diagnostics and plumbing checks (research/phase4/P4_xs_spec.md sections 8 and 10).
# Pure numpy, no QuantConnect imports (tests/test_xs_diag.py). Diagnostics are REPORTED ONLY: they never gate,
# promote, rescue or veto anything, and never change a rule or a signal. Nothing here alters qr_xs (pinned).
import hashlib
import math

import numpy as np

import qr_xs as X

# Fama-French 12 industries from SIC codes (Kenneth French Data Library 'Siccodes12'; from memory, see
# research/phase4/P4_CP3_references.md). Anything unmatched is 'Other'; no SIC = 'Unclassified' (its own group).
FF12 = (
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
FF12_NAMES = tuple(n for n, _ in FF12) + ("Other", "Unclassified")
TF_GROUPS = (("short_L3_20", (3, 5, 10, 20)), ("mid_L50_200", (50, 100, 200)), ("long_L400_1000", (400, 600, 800, 1000)))
MIN_GROUP = 10            # sector / size groups with fewer stocks on a date are skipped for that date


def ff12(sic):
    if sic is None:
        return "Unclassified"
    s = int(sic)
    for name, ranges in FF12:
        if any(a <= s <= b for a, b in ranges):
            return name
    return "Other"


# ----------------------------------------------------------------------------------------------- generic helpers
def acf(x, k):
    x = np.asarray(x, float) - np.mean(x)
    d = float((x * x).sum())
    return float((x[k:] * x[:-k]).sum() / d) if d > 0 else 0.0


def effective_sample(x, lags=12):
    """n / VIF with VIF = 1 + 2 sum_k (1 - k/(lags+1)) acf_k (Bartlett weights), as in the synthetic study."""
    x = np.asarray(x, float)
    vif = 1.0 + 2.0 * sum((1.0 - k / (lags + 1.0)) * acf(x, k) for k in range(1, lags + 1))
    return dict(vif=vif, ess=(x.size / vif if vif > 0 else float("nan")), acf_1_4=[acf(x, k) for k in range(1, 5)])


def ts(x, lag=X.NW_LAG):
    m, se, t = X.nw_tstat(x, lag)
    return dict(mean=m, se=se, t=t, n=int(np.asarray(x).size))


def group_demeaned_corr(sig, y, groups):
    """Correlation of cross-sectional ranks after removing group means of both (groups with < MIN_GROUP members are
    dropped): the within-group (e.g. sector-neutral) rank IC of one date."""
    sig, y, g = np.asarray(sig, float), np.asarray(y, float), np.asarray(groups)
    keep = np.zeros(sig.size, bool)
    for v in set(g.tolist()):
        ix = g == v
        if ix.sum() >= MIN_GROUP:
            keep |= ix
    if keep.sum() < 3 * MIN_GROUP:
        return float("nan")
    rs, ry = X.avg_rank(sig[keep]), X.avg_rank(y[keep])
    gg = g[keep]
    for v in set(gg.tolist()):
        ix = gg == v
        rs[ix] -= rs[ix].mean()
        ry[ix] -= ry[ix].mean()
    d = math.sqrt(float((rs * rs).sum() * (ry * ry).sum()))
    return float((rs * ry).sum() / d) if d > 0 else 0.0


def retention(prev_ids, prev_sig, ids, sig, k):
    """Share of the previous top bucket (1/k of the previous cross-section) still in the top bucket, among names
    present on both dates."""
    common = np.intersect1d(prev_ids, ids)
    if common.size < 2 * k:
        return float("nan")
    pi = np.searchsorted(prev_ids, common)
    ci = np.searchsorted(ids, common)
    bp = X.buckets(prev_sig[pi], k) == k - 1
    bc = X.buckets(sig[ci], k) == k - 1
    return float((bp & bc).sum() / bp.sum()) if bp.sum() else float("nan")


def rank_autocorr(prev_ids, prev_sig, ids, sig):
    common = np.intersect1d(prev_ids, ids)
    if common.size < 10:
        return float("nan")
    return X.spearman(prev_sig[np.searchsorted(prev_ids, common)], sig[np.searchsorted(ids, common)])


# ----------------------------------------------------------------------------------------------- panel facts
def bars_upto(Q, me):
    """(K, N) number of valid split-adjusted closes at or before each month-end row (history length)."""
    v = (np.isfinite(Q) & (Q > 0)).astype(np.int32)
    c = np.cumsum(v, axis=0)
    return c[np.asarray(me)]


def universe_counts(F, first_research=X.FIRST_RESEARCH_MONTH, last=(2017, 12)):
    k0, k1 = F.months.index(first_research), F.months.index(last)
    rows = []
    for k in range(k0, k1 + 1):
        rows.append(dict(month="%04d-%02d" % F.months[k], dom=int(F.dom[k].sum()), full=int(F.full[k].sum())))
    return rows


def coverage(F, nb, decisions_k, regression_k):
    """History coverage (spec section 8.8): share of the regression set (all eligible stocks with a bar, months s)
    and of the evaluation set (decision months, PRET / ID defined) with fewer than L bars, per L; mean over months."""
    out = {}
    for name, ks, mask in (("regression", regression_k, F.dom), ("evaluation", decisions_k, F.full)):
        per = {L: [] for L in X.HZZ_LAGS}
        for k in ks:
            j = np.flatnonzero(mask[k])
            if j.size == 0:
                continue
            for L in X.HZZ_LAGS:
                per[L].append(float((nb[k, j] < L).mean()))
        out[name] = {str(L): (float(np.mean(v)) if v else None) for L, v in per.items()}
        out[name + "_first_last"] = {str(L): ([v[0], v[-1]] if v else None) for L, v in per.items()}
    return out


def distribution_exposure(F, me, bigdist, ks, window=max(X.HZZ_LAGS), ahead=0):
    """Share of regression-set observations (eligible with a bar at month-end k) whose 1,000-bar moving-average window
    contains a large non-split distribution (spin-off / special): the observations whose A_L would differ under CRSP's
    spin-off price factor. bigdist[j] = rows of such distributions of stock j. ahead = months after the month-end also
    covered (forward-return windows)."""
    tot = hit = 0
    stocks = set()
    for k in ks:
        d = me[k]
        hi = me[min(k + ahead, len(me) - 1)]
        for j in np.flatnonzero(F.dom[k]):
            tot += 1
            rows = bigdist.get(int(j), ())
            if any(d - window < r <= hi for r in rows):
                hit += 1
                stocks.add(int(j))
    return dict(observations=tot, exposed=hit, share=(hit / tot if tot else 0.0), stocks=len(stocks))


def features_digest(F, ks):
    """SHA-256 of the world-independent inputs for months ks (identical inputs across the null and real runs)."""
    h = hashlib.sha256()
    for k in ks:
        for a in (F.dom[k], F.full[k], F.pret[k], F.idm[k], F.A[k], F.reg[k]) + tuple(F.fwd[hh][k] for hh in
                                                                                       sorted(F.fwd)):
            h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def world_digest(sm):
    h = hashlib.sha256()
    for s in X.SIGNALS:
        r = sm[s]
        vals = [r["ic_mean"], r["t"], r["top_ann"], r["spread_ann"], r["mono"]] + list(r["dec_mean"])
        if s in X.INCREMENTAL:
            vals += [r["inc_mean"], r["t_inc"]]
        h.update(np.asarray(vals, float).tobytes())
    return h.hexdigest()


# ----------------------------------------------------------------------------------------------- real-run diagnostics
def tf_expected_betas(betas, k):
    need = list(range(k - X.HZZ_BETA_MONTHS, k))
    return np.mean([betas[s] for s in need], axis=0)


def real_diagnostics(F, sm, mcap, sector, r1m):
    """Section 8 diagnostics for the real world. sm = run_world(F, keep_series=True, keep_signals=True).
    mcap[k] / sector[k]: arrays over all stocks (market cap at the month-end, FF12 label); r1m[k]: trailing 1-month
    total return of every stock (P(me k) / P(me k-1) - 1)."""
    sigs, series, years = sm["_signals"], sm["_series"], np.asarray(sm["_years"])
    betas = sm["_betas"]
    out = {}
    # per-year table
    py = {}
    for s in X.SIGNALS:
        ic = np.array([d[s]["ic"] for d in series])
        top = np.array([d[s]["dec"][-1] for d in series])
        rows = {}
        for y in sorted(set(years.tolist())):
            m = years == y
            v = ic[m]
            sd = float(v.std(ddof=1)) if v.size > 1 else float("nan")
            rows[int(y)] = dict(n=int(m.sum()), ic=float(v.mean()),
                                t=(float(v.mean() / (sd / math.sqrt(v.size))) if sd and sd > 0 else float("nan")),
                                top_ann=float(top[m].mean() * 12.0), sign=int(np.sign(v.mean())))
        py[s] = rows
    out["per_year"] = py
    # calendar sub-periods requested by the owner (reporting only; P4 uses the frozen halves and blocks)
    cal = {}
    for s in X.SIGNALS:
        ic = np.array([d[s]["ic"] for d in series])
        dec = np.array([d[s]["dec"] for d in series])
        cal[s] = {}
        for name, (a, b) in (("2011_2013", (2011, 2013)), ("2014_2017", (2014, 2017))):
            m = (years >= a) & (years <= b)
            r = ts(ic[m])
            r.update(top_ann=float(dec[m, -1].mean() * 12), bottom_ann=float(dec[m, 0].mean() * 12),
                     spread_ann=float((dec[m, -1] - dec[m, 0]).mean() * 12))
            if s in X.INCREMENTAL:
                inc = np.array([d[s]["inc"] for d in series])[m]
                r["inc"] = ts(inc)
            cal[s][name] = r
    out["calendar_subperiods"] = cal
    # sector-neutral, size halves, correlations, turnover, S3 decomposition
    secn = {s: [] for s in X.SIGNALS}
    size = {s: {"small": [], "large": []} for s in X.SIGNALS}
    szc = {s: [] for s in X.SIGNALS}
    cc = {p: [] for p in ("S1_S2", "S1_S3", "S2_S3", "S1_r1m", "S2_r1m", "S3_r1m")}
    rac = {s: [] for s in X.SIGNALS}
    ret10 = {s: [] for s in X.SIGNALS}
    ret5 = {s: [] for s in X.SIGNALS}
    comp_ic = {g: [] for g, _ in TF_GROUPS}
    comp_inc = {g: [] for g, _ in TF_GROUPS}
    ebpath = []
    sec_counts = {}
    prev = None
    lag_ix = {L: i for i, L in enumerate(X.HZZ_LAGS)}
    for rec in sigs:
        k, ids = rec["k"], rec["rec"]
        yd = X.demean(rec["y"])
        sg = {"S1": rec["pret"], "S2": rec["S2"], "S3": rec["S3"]}
        sec = np.asarray([sector[k][j] for j in ids])
        for v in sec.tolist():
            sec_counts[v] = sec_counts.get(v, 0) + 1
        mc = np.asarray(mcap[k][ids], float)
        big = mc >= np.median(mc)
        lm = np.log(np.maximum(mc, 1.0))
        for s in X.SIGNALS:
            secn[s].append(group_demeaned_corr(sg[s], yd, sec))
            for nm, m in (("small", ~big), ("large", big)):
                size[s][nm].append(X.spearman(sg[s][m], yd[m]))
            szc[s].append(X.spearman(sg[s], lm))
        r1 = np.asarray(r1m[k][ids], float)
        okr = np.isfinite(r1)
        cc["S1_S2"].append(X.spearman(sg["S1"], sg["S2"]))
        cc["S1_S3"].append(X.spearman(sg["S1"], sg["S3"]))
        cc["S2_S3"].append(X.spearman(sg["S2"], sg["S3"]))
        for s in X.SIGNALS:
            cc[s + "_r1m"].append(X.spearman(sg[s][okr], r1[okr]) if okr.sum() > 10 else float("nan"))
        if prev is not None:
            for s in X.SIGNALS:
                rac[s].append(rank_autocorr(prev[0], prev[1][s], ids, sg[s]))
                ret10[s].append(retention(prev[0], prev[1][s], ids, sg[s], 10))
                ret5[s].append(retention(prev[0], prev[1][s], ids, sg[s], 5))
        prev = (ids, sg)
        eb = tf_expected_betas(betas, k)
        ebpath.append(["%04d-%02d" % F.months[k]] + [float(v) for v in eb])
        A = F.A[k, rec["src"]]
        for g, Ls in TF_GROUPS:
            ix = [lag_ix[L] for L in Ls]
            comp = A[:, ix] @ eb[ix]
            comp_ic[g].append(X.spearman(comp, yd))
            comp_inc[g].append(X.within_quintile_partial_ic(comp, sg["S1"], yd)[0])
    nanmean = lambda v: float(np.nanmean(v)) if np.isfinite(v).any() else float("nan")
    out["sector_neutral_ic"] = {s: ts(np.nan_to_num(v)) for s, v in secn.items()}
    out["sector_obs"] = sec_counts
    out["size_half_ic"] = {s: {nm: ts(v) for nm, v in d.items()} for s, d in size.items()}
    out["corr_log_mcap"] = {s: nanmean(np.asarray(v)) for s, v in szc.items()}
    out["signal_corr"] = {p: nanmean(np.asarray(v)) for p, v in cc.items()}
    out["turnover"] = {s: dict(rank_autocorr=nanmean(np.asarray(rac[s])), top_decile_retention=nanmean(np.asarray(ret10[s])),
                               top_quintile_retention=nanmean(np.asarray(ret5[s]))) for s in X.SIGNALS}
    out["tf_decomposition"] = {g: dict(ic=ts(comp_ic[g]), incremental=ts(comp_inc[g])) for g, _ in TF_GROUPS}
    out["tf_expected_beta_path"] = dict(lags=list(X.HZZ_LAGS), rows=ebpath)
    out["realised_power"] = {}
    for s in X.SIGNALS:
        ic = np.array([d[s]["ic"] for d in series])
        r = dict(ic_sd=float(ic.std(ddof=1)), ic_se_nw=sm[s]["ic_se"], **effective_sample(ic))
        if s in X.INCREMENTAL:
            inc = np.array([d[s]["inc"] for d in series])
            r.update(inc_sd=float(inc.std(ddof=1)), inc_se_nw=sm[s]["inc_se"], inc_ess=effective_sample(inc)["ess"])
        out["realised_power"][s] = r
    return out


# ----------------------------------------------------------------------------------------------- plumbing checks
def slow_features(Q, P, me, k, j):
    """Independent, loop-based recomputation of PRET, ID and A_L for stock j at month k (pure Python over the
    panel column; no shared code with qr_xs.Features)."""
    d = me[k]
    qrows = [r for r in range(0, d + 1) if Q[r, j] == Q[r, j] and Q[r, j] > 0]
    A = []
    for L in X.HZZ_LAGS:
        w = qrows[-L:] if len(qrows) >= L else qrows
        A.append(sum(Q[r, j] for r in w) / len(w) / Q[d, j] if w else float("nan"))
    pret = idm = float("nan")
    if k >= 12:
        prow = [r for r in range(0, d + 1) if P[r, j] == P[r, j] and P[r, j] > 0]
        r1, r12 = me[k - 1], me[k - 12]
        a = [r for r in prow if r <= r1]
        b = [r for r in prow if r <= r12]
        if a and b and r1 - a[-1] <= X.PRET_STALE_MAX and r12 - b[-1] <= X.PRET_STALE_MAX and a[-1] > b[-1]:
            pret = P[a[-1], j] / P[b[-1], j] - 1.0
            win = [r for r in prow if b[-1] <= r <= a[-1]]
            rets = [P[win[i], j] / P[win[i - 1], j] - 1.0 for i in range(1, len(win))]
            pos = sum(1 for x in rets if x > 0)
            neg = sum(1 for x in rets if x < 0)
            sg = 1.0 if pret > 0 else (-1.0 if pret < 0 else 0.0)
            idm = sg * (neg - pos) / len(rets)
    return pret, idm, A


def slow_ols(Xm, y):
    """Independent OLS with an intercept via the normal equations (full-rank samples only)."""
    Xm, y = np.asarray(Xm, float), np.asarray(y, float)
    ok = np.all(np.isfinite(Xm), axis=1) & np.isfinite(y)
    Z = np.column_stack([np.ones(int(ok.sum())), Xm[ok]])
    b = np.linalg.solve(Z.T @ Z, Z.T @ y[ok])
    return b[1:]


def s2_structure_violations(pret, key, s2):
    """S2 two-stage sort checks on one date: the integer part of S2 is the PRET quintile (1..5) and, within each
    quintile, S2 orders stocks exactly as the key. Returns the number of violating stocks / pairs."""
    qb = X.buckets(pret, X.N_MOM_Q)
    bad = int((np.ceil(s2 - 1) != qb + 1).sum())
    for b in range(X.N_MOM_Q):
        ix = np.flatnonzero(qb == b)
        o = np.argsort(key[ix], kind="mergesort")
        sv = s2[ix][o]
        bad += int((np.diff(sv) < -1e-12).sum())
    return bad
