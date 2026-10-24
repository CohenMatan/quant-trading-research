# qr_od1 v1.0 — OD-1 outcome-driven discovery study (owner D308; research/od/OD1_protocol.md, frozen and SHA-256-
# pinned in qresearch.od1). Pure logic on plain arrays: no QuantConnect object, no I/O. Features use only windows that
# END at the review session; labels are joined only by `summarize` at the end of the run. Aggregates only leave.
import bisect
import math
import warnings

import numpy as np

L = 253                                          # sessions in a feature window (252 returns)
HORIZONS = (3, 6, 12, 24)
TECH = ("MOM12_1", "MOM6_1", "MOM3", "REV1M", "HI52", "LO52", "TREND200", "SLOPE200", "MA50_200", "ID", "UPDAYS",
        "VOL63", "VOLRATIO", "MAXDD252", "RANGECOMP", "DVSURGE", "UPDV63", "BIGUP", "BIGDN", "RS6", "DOWNMKT", "BETA",
        "MONTHSUP", "SECREL6", "BREAKOUT", "BASE", "SIZE", "ACCUM63", "TRENDAGE", "EXT50")
FUND = ("REVYOY", "REVACCEL", "NICHG", "GMCHG", "ROA", "DROA", "AG", "OCFTA", "ACCR", "DLEV", "REPURCH", "EY", "SP",
        "BM", "GPA", "REVCONS", "NICONS")
FEATURES = TECH + FUND
BINARY = ("BREAKOUT", "BASE")
INTEGER = ("MONTHSUP", "REVCONS", "NICONS")
CONTROLS = ("MOM12_1", "SIZE", "BETA", "VOL63")
MISS_MAX = 0.10                                  # a window with more than 10% missing sessions -> feature missing
FRESH_DAYS, FY_DAYS, CONS_DAYS = 200, 456, 450
PREV_GAP = (50, 130)                             # previous periodic filing for REVACCEL: filed 50-130 days earlier
GRIDS = (("D1", "MOM12_1", "REVACCEL"), ("D2", "TREND200", "DROA"), ("D3", "MOM6_1", "NICHG"),
         ("D4", "HI52", "OCFTA"), ("D5", "BREAKOUT", "REVYOY"), ("D6", "RS6", "REVCONS"))
SEVERE = {3: -0.20, 6: -0.20, 12: -0.30, 24: -0.30}
BIG_WIN = 1.0                                    # TR >= +100% at h = 12
DEC = 10


def _ffill(a):
    """Forward-fill NaN along axis 1; leading NaN stay NaN."""
    idx = np.where(~np.isnan(a), np.arange(a.shape[1]), 0)
    np.maximum.accumulate(idx, axis=1, out=idx)
    return a[np.arange(a.shape[0])[:, None], idx]


def _miss(a, w):
    return np.mean(np.isnan(a[:, -w:]), axis=1)


def tech_features(C, V, S):
    """C, V: (n, L) adjusted closes and dollar volumes in session order (last column = review session; NaN = no row);
    S: (L,) SPY total-return index. Returns {name: (n,) float array}; SECREL6 and SIZE are filled by the caller."""
    n = C.shape[0]
    out = {k: np.full(n, np.nan) for k in TECH}
    if n == 0:
        return out
    c = _ffill(C)
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = c[:, 1:] / c[:, :-1] - 1.0
        lr = np.log(c[:, 1:] / c[:, :-1])
        rs = S[1:] / S[:-1] - 1.0
        lrs = np.log(S[1:] / S[:-1])
        v = V.copy()
        m253, m127, m63, m21 = _miss(C, 253), _miss(C, 127), _miss(C, 63), _miss(C, 21)
        ok253, ok127, ok63, ok21 = m253 <= MISS_MAX, m127 <= MISS_MAX, m63 <= MISS_MAX, m21 <= MISS_MAX
        last = c[:, -1]

        def put(name, val, ok):
            val = np.asarray(val, float)
            out[name] = np.where(ok & np.isfinite(val), val, np.nan)

        put("MOM12_1", c[:, -22] / c[:, 0] - 1, ok253)
        put("MOM6_1", c[:, -22] / c[:, -127] - 1, ok127)
        put("MOM3", last / c[:, -64] - 1, ok63)
        put("REV1M", last / c[:, -22] - 1, ok21)
        put("HI52", last / np.nanmax(c, axis=1), ok253)
        put("LO52", last / np.nanmin(c, axis=1) - 1, ok253)
        sma200 = np.nanmean(c[:, -200:], axis=1)
        put("TREND200", last / sma200 - 1, ok253)
        put("SLOPE200", sma200 / np.nanmean(c[:, -221:-21], axis=1) - 1, ok253)
        sma50 = np.nanmean(c[:, -50:], axis=1)
        put("MA50_200", sma50 / sma200 - 1, ok253)
        pos, neg = np.nanmean(r > 0, axis=1), np.nanmean(r < 0, axis=1)
        put("ID", np.sign(last / c[:, 0] - 1) * (neg - pos), ok253)
        put("UPDAYS", pos, ok253)
        put("VOL63", np.nanstd(lr[:, -63:], axis=1, ddof=1) * math.sqrt(252), ok63)
        put("VOLRATIO", np.nanstd(lr[:, -21:], axis=1, ddof=1) / np.nanstd(lr[:, -126:], axis=1, ddof=1), ok127)
        put("MAXDD252", np.nanmin(c / np.fmax.accumulate(c, axis=1), axis=1) - 1, ok253)
        w21 = (np.nanmax(c[:, -21:], axis=1) - np.nanmin(c[:, -21:], axis=1)) / np.nanmean(c[:, -21:], axis=1)
        w126 = (np.nanmax(c[:, -126:], axis=1) - np.nanmin(c[:, -126:], axis=1)) / np.nanmean(c[:, -126:], axis=1)
        rangecomp = w21 / w126
        put("RANGECOMP", rangecomp, ok127)
        vm = np.nanmean(v, axis=1)
        put("DVSURGE", np.nanmean(v[:, -20:], axis=1) / vm, ok253)
        r63, v63 = r[:, -63:], v[:, -63:]
        up = np.nansum(np.where(r63 > 0, v63, 0.0), axis=1)
        dn = np.nansum(np.where(r63 < 0, v63, 0.0), axis=1)
        put("UPDV63", np.where(dn > 0, up / dn, np.nan), ok63)
        put("BIGUP", np.sum(r > 0.05, axis=1).astype(float), ok253)
        put("BIGDN", np.sum(r < -0.05, axis=1).astype(float), ok253)
        put("RS6", (last / c[:, -127]) / (S[-1] / S[-127]) - 1, ok127)
        dmask = rs < 0
        put("DOWNMKT", np.nanmean(np.where(dmask[None, :], r - rs[None, :], np.nan), axis=1), ok253)
        # beta on ORIGINAL (unfilled) returns: a pair counts when both closes exist
        lro = np.log(C[:, 1:] / C[:, :-1])
        pair = np.isfinite(lro) & np.isfinite(lrs)[None, :]
        cnt = pair.sum(axis=1)
        x = np.where(pair, lrs[None, :], 0.0)
        y = np.where(pair, lro, 0.0)
        mx, my = x.sum(axis=1) / np.maximum(cnt, 1), y.sum(axis=1) / np.maximum(cnt, 1)
        cov = (np.where(pair, (x - mx[:, None]) * (y - my[:, None]), 0.0)).sum(axis=1)
        var = (np.where(pair, (x - mx[:, None]) ** 2, 0.0)).sum(axis=1)
        put("BETA", np.where((cnt >= 200) & (var > 0), cov / np.where(var > 0, var, 1.0), np.nan), cnt >= 200)
        blocks = np.stack([c[:, L - 1 - 21 * j] / c[:, L - 1 - 21 * (j + 1)] - 1 for j in range(12)], axis=1)
        put("MONTHSUP", np.sum(blocks > 0, axis=1).astype(float), ok253)
        newhigh = np.nanmax(c[:, -5:], axis=1) >= np.nanmax(c[:, :-5], axis=1)
        vs = np.nanmean(v[:, -5:], axis=1) / np.nanmean(v[:, -55:-5], axis=1)
        put("BREAKOUT", (newhigh & (vs >= 1.5)).astype(float), ok253)
        hi52 = last / np.nanmax(c, axis=1)
        put("BASE", ((hi52 >= 0.95) & (rangecomp <= 0.6)).astype(float), ok253)
        mv63 = np.nanmean(v63, axis=1)
        put("ACCUM63", np.sum((r63 > 0) & (v63 > 2.0 * mv63[:, None]), axis=1).astype(float), ok63)
        # trend age: consecutive sessions (<= 200) with close above its trailing 50-session mean
        cs = np.nancumsum(np.nan_to_num(c), axis=1)
        sma = np.full_like(c, np.nan)
        sma[:, 49:] = (cs[:, 49:] - np.concatenate([np.zeros((n, 1)), cs[:, :-50]], axis=1)) / 50.0
        above = c > sma
        age = np.zeros(n)
        alive = np.ones(n, bool)
        for j in range(1, 201):
            a = above[:, -j] & alive
            age += a
            alive &= a
        put("TRENDAGE", age, ok253)
        put("EXT50", last / sma50 - 1, ok63)
    return out


class Fund:
    """The OD-1 SEC extension object (rr/od1_sec_v1.json) aligned to qr_ucr.RepairRef registrant order: per registrant
    original periodic filings [filed, kind, period_end, rev, rev_py, ni, ni_py, gp, gp_py, ocf, ta, ta_py, eq, eq_py],
    usable strictly after the filing day; filings filed before FILED_FROM are discarded."""

    FILED_FROM = "2010-01-01"

    def __init__(self, doc, ciks):
        from datetime import date
        self.day, self.rows = [], []
        for c in ciks:
            rs = [r for r in doc["r"].get(c, []) if r[0] >= self.FILED_FROM]
            rs.sort(key=lambda r: r[0])
            self.day.append([date.fromisoformat(r[0]).toordinal() for r in rs])
            self.rows.append(rs)
        self.pe = [[(date.fromisoformat(r[2]).toordinal() if r[2] else None) for r in rs] for rs in self.rows]
        self.pit_violations = 0

    @staticmethod
    def _yoy(r):
        rev, py = r[3], r[4]
        if rev is None or py is None or not py > 0:
            return None
        return rev / py - 1.0

    def features(self, i, t, cap):
        """F01..F17 except REPURCH (from qr_os1) for registrant i at review day t (ordinal); cap = PIT market cap."""
        f = dict.fromkeys(FUND)
        if i is None:
            return f
        days, rows = self.day[i], self.rows[i]
        j = bisect.bisect_left(days, t) - 1
        if j < 0:
            return f
        if days[j] >= t:
            self.pit_violations += 1
            return f
        if t - days[j] <= FRESH_DAYS:
            r = rows[j]
            g = self._yoy(r)
            f["REVYOY"] = g
            if g is not None and j >= 1 and PREV_GAP[0] <= days[j] - days[j - 1] <= PREV_GAP[1]:
                g0 = self._yoy(rows[j - 1])
                if g0 is not None:
                    f["REVACCEL"] = g - g0
            ni, nip, ta = r[5], r[6], r[10]
            if ni is not None and nip is not None and ta is not None and ta > 0:
                f["NICHG"] = (ni - nip) / ta
            rev, revp, gp, gpp = r[3], r[4], r[7], r[8]
            if None not in (rev, revp, gp, gpp) and rev > 0 and revp > 0:
                f["GMCHG"] = gp / rev - gpp / revp
            if j >= 3 and t - days[j - 3] <= CONS_DAYS:
                ys = [self._yoy(rows[q]) for q in range(j - 3, j + 1)]
                if all(y is not None for y in ys):
                    f["REVCONS"] = float(sum(y > 0 for y in ys))
                ns = [(rows[q][5], rows[q][6]) for q in range(j - 3, j + 1)]
                if all(a is not None and b is not None for a, b in ns):
                    f["NICONS"] = float(sum(a > b for a, b in ns))
        # latest original annual report filed before t with period end at most FY_DAYS before t
        q = j
        while q >= 0 and rows[q][1] != "K":
            q -= 1
        if q >= 0 and self.pe[i][q] is not None and t - self.pe[i][q] <= FY_DAYS:
            r = rows[q]
            rev, ni, gp, ocf, ta, tap, eq, eqp = r[3], r[5], r[7], r[9], r[10], r[11], r[12], r[13]
            nip = r[6]
            if ta is not None and ta > 0:
                if ni is not None:
                    f["ROA"] = ni / ta
                    if nip is not None and tap is not None and tap > 0:
                        f["DROA"] = ni / ta - nip / tap
                if tap is not None and tap > 0:
                    f["AG"] = ta / tap - 1.0
                if ocf is not None:
                    f["OCFTA"] = ocf / ta
                    if ni is not None:
                        f["ACCR"] = (ni - ocf) / ta
                if eq is not None and eqp is not None and tap is not None and tap > 0:
                    f["DLEV"] = (ta - eq) / ta - (tap - eqp) / tap
                if gp is not None:
                    f["GPA"] = gp / ta
            if cap is not None and cap > 0:
                if ni is not None:
                    f["EY"] = ni / cap
                if rev is not None:
                    f["SP"] = rev / cap
                if eq is not None:
                    f["BM"] = eq / cap
        return f


# ------------------------------------------------------------------------------------------------ labels
def labels(P0, PH, LEFT, spy0, spyh, beta):
    """TR, EX, BA for one horizon: P0 / PH start / end adjusted prices (PH = last observed price if the security left
    the stream), spy0 / spyh SPY index, beta (NaN allowed)."""
    with np.errstate(all="ignore"):
        tr = PH / P0 - 1.0
        s = spyh / spy0 - 1.0
        ex = tr - s
        ba = tr - beta * s
    return tr, ex, ba, s


def bounds(groups):
    """Contiguous slices of a NON-DECREASING group array: {group: (start, stop)}."""
    g = np.asarray(groups)
    if g.size and np.any(np.diff(g) < 0):
        raise ValueError("observations must be ordered by review")
    u, start = np.unique(g, return_index=True)
    stop = list(start[1:]) + [g.size]
    return {int(a): (int(b), int(c)) for a, b, c in zip(u, start, stop)}


def _ranked(x, groups, q):
    out = np.full(x.shape, -1 if q else np.nan, dtype=int if q else float)
    for a, b in bounds(groups).values():
        seg = x[a:b]
        m = np.where(np.isfinite(seg))[0]
        n = m.size
        if n < (q or 2):
            continue
        o = a + m[np.argsort(seg[m], kind="mergesort")]
        out[o] = (np.arange(n) * q) // n if q else (np.arange(n) + 0.5) / n
    return out


def deciles(x, groups):
    """Cross-sectional deciles within each review (stable ties); NaN -> -1."""
    return _ranked(x, groups, DEC)


def terciles(x, groups):
    return _ranked(x, groups, 3)


def pct_rank(x, groups):
    """Within-review percentile rank in (0, 1); NaN stays NaN."""
    return _ranked(x, groups, 0)


def r6(x):
    if x is None:
        return None
    x = float(x)
    if not math.isfinite(x):
        return None
    return float(f"{x:.5g}")


def group_stats(sel, L_):
    """Statistics of one observation set. L_: dict of label arrays for one horizon (ex, tr, sr, ba, w, l, s, mae,
    left, k, firm)."""
    n = int(sel.sum())
    if n == 0:
        return dict(n=0)
    ex = L_["ex"][sel]
    exs = np.sort(ex)
    cut = int(math.floor(n * 0.99))
    trimmed = exs[:max(cut, 1)]
    return dict(n=n, reviews=int(np.unique(L_["k"][sel]).size), firms=int(np.unique(L_["firm"][sel]).size),
                mean_ex=r6(ex.mean()), med_ex=r6(np.median(ex)), trim_ex=r6(trimmed.mean()),
                mean_tr=r6(np.nanmean(L_["tr"][sel])),
                mean_sr=r6(np.nanmean(L_["sr"][sel])) if np.isfinite(L_["sr"][sel]).any() else None,
                mean_ba=r6(np.nanmean(L_["ba"][sel])) if np.isfinite(L_["ba"][sel]).any() else None,
                p_beat=r6((ex > 0).mean()), p_w=r6(L_["w"][sel].mean()), p_l=r6(L_["l"][sel].mean()),
                p_s=r6(L_["s"][sel].mean()), mae=r6(np.nanmean(L_["mae"][sel])), left=r6(L_["left"][sel].mean()))


STAT_KEYS = ("n", "reviews", "firms", "mean_ex", "med_ex", "trim_ex", "mean_tr", "mean_sr", "mean_ba", "p_beat", "p_w",
             "p_l", "p_s", "mae", "left")


def packed(sel, L_):
    """group_stats as a list in STAT_KEYS order (compact output; OD1_eval unpacks)."""
    d = group_stats(sel, L_)
    return [d.get(k) for k in STAT_KEYS]


def nw_t(x, lag):
    x = np.asarray([v for v in x if v is not None and math.isfinite(v)], float)
    n = x.size
    if n < 8:
        return None, n
    m = x.mean()
    e = x - m
    s = (e @ e) / n
    for k in range(1, min(lag, n - 1) + 1):
        s += 2 * (1 - k / (lag + 1)) * (e[k:] @ e[:-k]) / n
    return (r6(m / math.sqrt(s / n)) if s > 0 else None), n


def partial_ic(f, y, Z):
    """Pearson correlation of f and y after OLS residualisation of both on Z (with intercept); rows with any NaN
    dropped. f, y already rank-transformed."""
    ok = np.isfinite(f) & np.isfinite(y) & np.all(np.isfinite(Z), axis=1)
    if ok.sum() < 30:
        return None
    X = np.column_stack([np.ones(ok.sum()), Z[ok]])
    bf = np.linalg.lstsq(X, f[ok], rcond=None)[0]
    by = np.linalg.lstsq(X, y[ok], rcond=None)[0]
    a, b = f[ok] - X @ bf, y[ok] - X @ by
    den = math.sqrt((a @ a) * (b @ b))
    return None if den <= 1e-12 else float(a @ b / den)


def spearman(f, y):
    ok = np.isfinite(f) & np.isfinite(y)
    if ok.sum() < 30:
        return None
    a = np.argsort(np.argsort(f[ok])).astype(float)
    b = np.argsort(np.argsort(y[ok])).astype(float)
    a -= a.mean()
    b -= b.mean()
    den = math.sqrt((a @ a) * (b @ b))
    return None if den <= 0 else float(a @ b / den)


# ------------------------------------------------------------------------------------------------ end-of-run summary
FF12_NAMES = ("NoDur", "Durbl", "Manuf", "Enrgy", "Chems", "BusEq", "Telcm", "Utils", "Shops", "Hlth", "Money",
              "Other")
QS = (0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99)


def end_prices(MP, last_day, last_px, T, k, kk, r):
    """End adjusted price at review kk for observations (k, r): the review price if observed; else, if the security
    left the stream before review kk, its last observed price (left = 1); else the latest observed review price in
    (k, kk) (left = 0)."""
    ph = MP[r, kk].astype(float)
    left = np.zeros(r.size, bool)
    miss = ~np.isfinite(ph)
    if miss.any():
        T = np.asarray(T)
        gone = miss & (last_day[r] < T[kk])
        ph[gone] = last_px[r[gone]]
        left[gone] = True
        rest = np.where(miss & ~gone)[0]
        for j in rest:
            seg = MP[r[j], k[j] + 1:kk[j]]
            fin = np.where(np.isfinite(seg))[0]
            if fin.size:
                ph[j] = seg[fin[-1]]
    return ph, left


def build_labels(P, h):
    """Label arrays for horizon h (months). P: panel dict. Observations without a full horizon -> valid False."""
    k, r = P["k"], P["r"]
    K = len(P["T"])
    kk = k + h
    valid = kk <= K - 1
    kc = np.where(valid, kk, 0)
    p0 = P["MP"][r, k].astype(float)
    ph, left = end_prices(P["MP"], P["last_day"], P["last_px"], P["T"], k, kc, r)
    tr, ex, ba, s = labels(p0, ph, left, P["spy"][k], P["spy"][kc], P["X"][:, FEATURES.index("BETA")])
    valid &= np.isfinite(tr) & np.isfinite(ex) & (p0 > 0)
    # monthly-granularity maximum adverse movement within the horizon (path ends at the label's end price)
    mae = np.full(k.size, np.nan)
    for j in np.where(valid)[0]:
        seg = P["MP"][r[j], k[j] + 1:kc[j] + 1].astype(float)
        seg = seg[np.isfinite(seg)]
        lo = min(seg.min() if seg.size else ph[j], ph[j])
        mae[j] = min(lo / p0[j] - 1.0, 0.0)
    sec = P["sec"]
    sr = np.full(k.size, np.nan)
    w = np.zeros(k.size, bool)
    lo_ = np.zeros(k.size, bool)
    mid = np.zeros(k.size, bool)
    for a, b in bounds(k).values():
        m = a + np.where(valid[a:b])[0]
        if not m.size:
            continue
        q = ex[m].argsort(kind="mergesort").argsort(kind="mergesort") / max(m.size - 1, 1)
        w[m] = q >= 0.9
        lo_[m] = q <= 0.1
        mid[m] = (q >= 0.4) & (q <= 0.6)
        for s_ in np.unique(sec[m]):
            if s_ < 0:
                continue
            ms = m[sec[m] == s_]
            if ms.size >= 5:
                sr[ms] = tr[ms] - np.median(tr[ms])
    sev = tr <= SEVERE[h]
    big = tr >= BIG_WIN
    return dict(valid=valid, kk=kk, tr=tr, ex=ex, ba=ba, sr=sr, w=w, l=lo_, m=mid, s=sev, big=big, mae=mae,
                left=left, k=k, firm=P["firm"], spy=s)


def period_masks(P, LB):
    K = len(P["T"])
    disc = LB["valid"] & (LB["kk"] <= P["K1712"])
    stress = LB["valid"] & (P["k"] >= P["K1801"]) & (LB["kk"] <= K - 1)
    return dict(DISC=disc, STRESS=stress, ALL=LB["valid"])


def feature_groups(name, x, k):
    if name in BINARY:
        return np.where(np.isfinite(x), x.astype(int), -1), [0, 1]
    if name in INTEGER:
        g = np.where(np.isfinite(x), x, -1).astype(int)
        return g, sorted(int(v) for v in np.unique(g) if v >= 0)
    return deciles(x, k), list(range(DEC))


def summarize(P):
    """All OD-1 aggregates as a list of (section, key, payload)."""
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return _summarize(P)


def _summarize(P):
    out = []
    K = len(P["T"])
    years = np.asarray(P["years"])
    k = P["k"]
    X = P["X"]
    LBS = {h: build_labels(P, h) for h in HORIZONS}
    BD = bounds(k)
    SL = [BD.get(g, (0, 0)) for g in range(K)]
    # ---------------- Stage A: outcome distributions, concentration, gain paths
    A = {}
    for h, LB in LBS.items():
        PM = period_masks(P, LB)
        d = {}
        for pn, pm in PM.items():
            n = int(pm.sum())
            if not n:
                d[pn] = dict(n=0)
                continue
            d[pn] = dict(n=n, reviews=int(np.unique(k[pm]).size), firms=int(np.unique(P["firm"][pm]).size),
                         tr_q=[r6(v) for v in np.quantile(LB["tr"][pm], QS)],
                         ex_q=[r6(v) for v in np.quantile(LB["ex"][pm], QS)],
                         mean_tr=r6(LB["tr"][pm].mean()), mean_ex=r6(LB["ex"][pm].mean()),
                         p_beat=r6((LB["ex"][pm] > 0).mean()), p_s=r6(LB["s"][pm].mean()),
                         p_big=r6(LB["big"][pm].mean()), left=r6(LB["left"][pm].mean()),
                         left_w=r6(LB["left"][pm & LB["w"]].mean()), left_l=r6(LB["left"][pm & LB["l"]].mean()),
                         left_m=r6(LB["left"][pm & LB["m"]].mean()),
                         mae_w=r6(np.nanmean(LB["mae"][pm & LB["w"]])), mae_l=r6(np.nanmean(LB["mae"][pm & LB["l"]])),
                         mae_all=r6(np.nanmean(LB["mae"][pm])))
        yr = {}
        for y in sorted(set(years[k[LB["valid"]]])):
            m = LB["valid"] & (years[k] == y)
            yr[int(y)] = dict(n=int(m.sum()), mean_tr=r6(LB["tr"][m].mean()), med_tr=r6(np.median(LB["tr"][m])),
                              mean_ex=r6(LB["ex"][m].mean()), med_ex=r6(np.median(LB["ex"][m])),
                              p_beat=r6((LB["ex"][m] > 0).mean()), p_s=r6(LB["s"][m].mean()),
                              p_big=r6(LB["big"][m].mean()), spy=r6(np.mean(LB["spy"][m])))
        d["years"] = yr
        conc = []
        for g in range(K):
            a, b = SL[g]
            tr = np.sort(LB["tr"][a:b][LB["valid"][a:b]])[::-1]
            tot = tr.sum()
            n = tr.size
            if tot > 0 and n >= 100:
                conc.append([tr[:max(1, n // 100)].sum() / tot, tr[:max(1, n // 20)].sum() / tot,
                             tr[:max(1, n // 10)].sum() / tot, float((tr > 0).mean())])
        if conc:
            c = np.array(conc)
            d["concentration"] = dict(reviews=len(conc), top1_share_med=r6(np.median(c[:, 0])),
                                      top5_share_med=r6(np.median(c[:, 1])), top10_share_med=r6(np.median(c[:, 2])),
                                      p_positive_med=r6(np.median(c[:, 3])))
        if h == 12:
            path = []
            for j in np.where(LB["valid"] & LB["w"])[0]:
                seg = P["MP"][P["r"][j], k[j]:k[j] + 13].astype(float)
                if np.isfinite(seg).all() and seg[-1] > seg[0]:
                    m_ = np.log(seg[1:] / seg[:-1])
                    path.append([m_.max() / m_.sum(), float((m_ > 0).sum())])
            if path:
                pa = np.array(path)
                d["winner_path"] = dict(n=len(path), best_month_share_med=r6(np.median(pa[:, 0])),
                                        best_month_share_q75=r6(np.quantile(pa[:, 0], 0.75)),
                                        months_up_med=r6(np.median(pa[:, 1])),
                                        p_months_up_ge8=r6((pa[:, 1] >= 8).mean()))
        A[h] = d
    out.append(("outcomes", "all", A))
    # ---------------- source-consistency series (universe mean / median TR and EX per review)
    sc = {}
    for h in (3, 12):
        LB = LBS[h]
        rows = []
        for g in range(K):
            a, b = SL[g]
            v = LB["valid"][a:b]
            tr, ex = LB["tr"][a:b][v], LB["ex"][a:b][v]
            rows.append([int(v.sum()), r6(tr.mean()) if v.any() else None,
                         r6(np.median(tr)) if v.any() else None, r6(ex.mean()) if v.any() else None])
        sc[h] = rows
    out.append(("consistency", "all", sc))
    # ---------------- control ranks per review (partial IC)
    pr = {c: pct_rank(X[:, FEATURES.index(c)], k) for c in CONTROLS}
    roa_r = pct_rank(X[:, FEATURES.index("ROA")], k)
    sec = P["sec"]
    D = np.zeros((k.size, len(FF12_NAMES) - 1))
    for j in range(len(FF12_NAMES) - 1):
        D[:, j] = (sec == j)
    size_t = terciles(X[:, FEATURES.index("SIZE")], k)
    # ---------------- per-feature tables
    for fi, name in enumerate(FEATURES):
        x = X[:, fi].astype(float)
        if name in FUND:
            x = np.where(P["fin"], np.nan, x)
        grp, gl = feature_groups(name, x, k)
        xr = pct_rank(x, k)
        payload = dict(groups=gl, coverage={})
        for y in sorted(set(years)):
            m = years[k] == y
            payload["coverage"][int(y)] = r6(np.isfinite(x[m]).mean()) if m.any() else None
        tables, series, prof, brk = {}, {}, {}, {}
        ctrl = [c for c in CONTROLS if c != name]
        Zc = np.column_stack([pr[c] for c in ctrl] + ([roa_r] if name in FUND and name != "ROA" else []) + [D])
        for h, LB in LBS.items():
            PM = period_masks(P, LB)
            T_ = {}
            for pn, pm in PM.items():
                base = pm & (grp >= 0)
                row = {"univ": packed(base, LB)}
                for g in gl:
                    row[str(g)] = packed(base & (grp == g), LB)
                T_[pn] = row
            tables[h] = T_
            # per-review series
            top, bot = gl[-1], gl[0]
            spread, tmu, ic, pic = [], [], [], []
            yr_ = LB["ex"]
            yrk = pct_rank(np.where(LB["valid"], yr_, np.nan), k)
            for g in range(K):
                s0, s1 = SL[g]
                m = LB["valid"][s0:s1] & (grp[s0:s1] >= 0)
                if m.sum() < 30:
                    spread.append(None); tmu.append(None); ic.append(None); pic.append(None)
                    continue
                e = yr_[s0:s1][m]
                gg = grp[s0:s1][m]
                a, b = e[gg == top], e[gg == bot]
                spread.append(r6(a.mean() - b.mean()) if a.size and b.size else None)
                tmu.append(r6(a.mean() - e.mean()) if a.size else None)
                ic.append(r6(spearman(x[s0:s1][m], e)))
                pic.append(r6(partial_ic(xr[s0:s1][m], yrk[s0:s1][m], Zc[s0:s1][m])))
            series[h] = dict(spread=spread, top_minus_univ=tmu, ic=ic, pic=pic,
                             nw=dict(spread=nw_t(spread, h - 1), ic=nw_t(ic, h - 1), pic=nw_t(pic, h - 1)))
            if h in (6, 12):
                pp = {}
                q5 = np.full(xr.shape, -1)
                fx = np.isfinite(xr)
                q5[fx] = np.minimum((xr[fx] * 5).astype(int), 4)
                for pn, pm in PM.items():
                    gd = {}
                    for gname, gm in (("W", LB["w"]), ("L", LB["l"]), ("M", LB["m"]), ("all", np.ones(k.size, bool))):
                        mm = pm & gm & np.isfinite(xr)
                        gd[gname] = dict(n=int(mm.sum()), top_q=r6((q5[mm] == 4).mean()) if mm.any() else None,
                                         bot_q=r6((q5[mm] == 0).mean()) if mm.any() else None,
                                         mean_pct=r6(xr[mm].mean()) if mm.any() else None)
                    pp[pn] = gd
                prof[h] = pp
            if h == 12:
                b = {}
                pm = PM["ALL"] & (grp >= 0)
                ex_ = LB["ex"]
                for label_, part in (("year", years[k]), ("sector", sec), ("size", size_t),
                                     ("spy_up", (LB["spy"] > 0).astype(int))):
                    dd = {}
                    for v in np.unique(part[pm]):
                        mv = pm & (part == v)
                        u = ex_[mv].mean()
                        dd[str(int(v))] = {"n": int(mv.sum()), "univ": r6(u),
                                           **{str(g): r6(ex_[mv & (grp == g)].mean() - u)
                                              if (mv & (grp == g)).sum() >= 20 else None for g in gl}}
                    b[label_] = dd
                brk = b
        payload.update(tables=tables, profiles=prof, breakdowns=brk)
        out.append(("feature", name, payload))
        out.append(("series", name, series))
    # ---------------- combined grids (terciles x terciles within review)
    for gname, a_, b_ in GRIDS:
        xa = X[:, FEATURES.index(a_)].astype(float)
        xb = X[:, FEATURES.index(b_)].astype(float)
        both = np.isfinite(xa) & np.isfinite(xb) & ~P["fin"]
        xa, xb = np.where(both, xa, np.nan), np.where(both, xb, np.nan)
        ta = np.where(both, np.nan_to_num(xa), -1).astype(int) if a_ in BINARY else terciles(xa, k)
        if b_ == "REVCONS":
            tb = np.where(both, np.where(xb <= 1, 0, np.where(xb >= 3, 2, 1)), -1)
        else:
            tb = terciles(xb, k)
        cells = [(i, j) for i in sorted(set(ta[ta >= 0])) for j in (0, 1, 2)]
        G = dict(rows=a_, cols=b_, cells={}, series={}, breakdowns={})
        for h in (6, 12):
            LB = LBS[h]
            PM = period_masks(P, LB)
            for pn, pm in PM.items():
                base = pm & (ta >= 0) & (tb >= 0)
                G["cells"].setdefault(str(h), {}).setdefault(pn, {"univ": packed(base, LB)})
                for i, j in cells:
                    G["cells"][str(h)][pn][f"{i}{j}"] = packed(base & (ta == i) & (tb == j), LB)
            if h == 6:
                for i, j in cells:
                    s_ = []
                    for g in range(K):
                        s0, s1 = SL[g]
                        m = LB["valid"][s0:s1] & (ta[s0:s1] >= 0) & (tb[s0:s1] >= 0)
                        c_ = m & (ta[s0:s1] == i) & (tb[s0:s1] == j)
                        e = LB["ex"][s0:s1]
                        s_.append(r6(e[c_].mean() - e[m].mean()) if c_.sum() >= 5 else None)
                    G["series"][f"{i}{j}"] = dict(cmu=s_, nw=nw_t(s_, h - 1))
            if h == 12:
                pm = PM["ALL"] & (ta >= 0) & (tb >= 0)
                ex_ = LB["ex"]
                for label_, part in (("year", years[k]), ("sector", sec), ("size", size_t)):
                    dd = {}
                    for v in np.unique(part[pm]):
                        mv = pm & (part == v)
                        u = ex_[mv].mean()
                        dd[str(int(v))] = {f"{i}{j}": r6(ex_[mv & (ta == i) & (tb == j)].mean() - u)
                                           if (mv & (ta == i) & (tb == j)).sum() >= 20 else None for i, j in cells}
                    G["breakdowns"][label_] = dd
        out.append(("grid", gname, G))
    return out
