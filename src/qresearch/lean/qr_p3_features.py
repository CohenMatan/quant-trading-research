# qr_p3_features.py — Phase 3 point-in-time technical features (research/phase3/P3_spec.md). Pure numpy, no
# QuantConnect imports (tests/test_p3_features.py). Input: right-aligned windows of ADJUSTED daily bars as known at
# today's close (column -1 = today; NaN = no bar yet), for the stocks eligible today, plus SPY closes. Output: every base
# condition's boolean mask and every primary's strength (ranking key). A condition whose look-back is not fully
# available for a stock is False for that stock. Nothing uses any bar after today.
import numpy as np

WINDOW = 280                 # bars kept per stock: max look-back = return(252, skip 21) needs 274 closes
RSI_SPAN = 100               # Wilder recursions (RSI, ADX) start 100 changes back (seed = simple mean of the first n)
EMA_SPAN = 200               # MACD EMAs start 200 bars back (seed = simple mean of the first span values)


def _last(x, k):
    return x[:, -k:]


def sma(c, n):
    w = _last(c, n)
    return np.where(np.isnan(w).any(axis=1), np.nan, np.nanmean(w, axis=1)) if c.shape[1] >= n else np.full(len(c), np.nan)


def ret(c, k, skip=0):
    """close[t-skip] / close[t-skip-k] - 1."""
    if c.shape[1] < k + skip + 1:
        return np.full(len(c), np.nan)
    a = c[:, -1 - skip]
    b = c[:, -1 - skip - k]
    return a / b - 1.0


def rsi(c, n, span=RSI_SPAN):
    """Wilder RSI over the last `span` changes, seeded by the simple mean of the first n changes."""
    if c.shape[1] < span + 1:
        return np.full(len(c), np.nan)
    d = np.diff(_last(c, span + 1), axis=1)
    g, l = np.clip(d, 0, None), np.clip(-d, 0, None)
    ag, al = g[:, :n].mean(axis=1), l[:, :n].mean(axis=1)
    for i in range(n, span):
        ag = (ag * (n - 1) + g[:, i]) / n
        al = (al * (n - 1) + l[:, i]) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = ag / al
        out = np.where(al == 0, np.where(ag == 0, 50.0, 100.0), 100.0 - 100.0 / (1.0 + rs))
    out[np.isnan(d).any(axis=1)] = np.nan
    return out


def ema_series(x, n):
    """EMA along axis 1 seeded by the simple mean of the first n values; returns the full series (NaN before seed)."""
    out = np.full_like(x, np.nan)
    a = 2.0 / (n + 1)
    e = x[:, :n].mean(axis=1)
    out[:, n - 1] = e
    for i in range(n, x.shape[1]):
        e = a * x[:, i] + (1 - a) * e
        out[:, i] = e
    return out


def macd(c, span=EMA_SPAN):
    """(MACD line, signal line) today: EMA12 - EMA26 of closes over the last `span` bars; signal = EMA9 of the line."""
    if c.shape[1] < span:
        nan = np.full(len(c), np.nan)
        return nan, nan
    w = _last(c, span)
    e12, e26 = ema_series(w, 12), ema_series(w, 26)
    line = e12 - e26
    sig = ema_series(line[:, 25:], 9)
    out_l, out_s = line[:, -1], sig[:, -1]
    bad = np.isnan(w).any(axis=1)
    out_l[bad] = np.nan
    out_s[bad] = np.nan
    return out_l, out_s


def adx(h, l, c, n=14, span=RSI_SPAN):
    """Wilder ADX(n) over the last `span` bars."""
    if c.shape[1] < span + 1:
        return np.full(len(c), np.nan)
    H, L, C = _last(h, span + 1), _last(l, span + 1), _last(c, span + 1)
    up, dn = H[:, 1:] - H[:, :-1], L[:, :-1] - L[:, 1:]
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = np.maximum.reduce([H[:, 1:] - L[:, 1:], np.abs(H[:, 1:] - C[:, :-1]), np.abs(L[:, 1:] - C[:, :-1])])
    atr, sp, sn = tr[:, :n].sum(axis=1), pdm[:, :n].sum(axis=1), ndm[:, :n].sum(axis=1)
    dxs = []
    for i in range(n, span):
        atr = atr - atr / n + tr[:, i]
        sp = sp - sp / n + pdm[:, i]
        sn = sn - sn / n + ndm[:, i]
        with np.errstate(divide="ignore", invalid="ignore"):
            pdi, ndi = 100 * sp / atr, 100 * sn / atr
            dxs.append(np.where(pdi + ndi > 0, 100 * np.abs(pdi - ndi) / (pdi + ndi), 0.0))
    dx = np.stack(dxs, axis=1)
    a = dx[:, :n].mean(axis=1)
    for i in range(n, dx.shape[1]):
        a = (a * (n - 1) + dx[:, i]) / n
    a[np.isnan(H).any(axis=1) | np.isnan(L).any(axis=1) | np.isnan(C).any(axis=1)] = np.nan
    return a


def pct_b(c, n=20, k=2.0):
    if c.shape[1] < n:
        return np.full(len(c), np.nan)
    w = _last(c, n)
    m, s = w.mean(axis=1), w.std(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(s > 0, (w[:, -1] - (m - k * s)) / (2 * k * s), np.nan)


def max_close(c, n):
    if c.shape[1] < n:
        return np.full(len(c), np.nan)
    w = _last(c, n)
    return np.where(np.isnan(w).any(axis=1), np.nan, w.max(axis=1))


def realised_vol(c, n=63):
    if c.shape[1] < n + 1:
        return np.full(len(c), np.nan)
    r = np.diff(np.log(_last(c, n + 1)), axis=1)
    return r.std(axis=1, ddof=1)


def rel_volume(v, a=20, b=120):
    if v.shape[1] < b:
        return np.full(len(v), np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        x = np.nanmean(_last(v, a), axis=1) / np.nanmean(_last(v, b), axis=1)
    x[np.isnan(_last(v, b)).any(axis=1)] = np.nan
    return x


def pct_rank(x, ascending=True):
    """Percentile rank in (0, 1] among the finite values (1/n = best for ascending=False... see top_fraction); NaN stays
    NaN. Ties broken by position (callers pass stocks in security-id order)."""
    out = np.full(len(x), np.nan)
    ok = np.isfinite(x)
    n = int(ok.sum())
    if n == 0:
        return out
    v = x[ok] if ascending else -x[ok]
    order = np.lexsort((np.arange(n), v))
    r = np.empty(n)
    r[order] = np.arange(1, n + 1)
    out[ok] = r / n
    return out


def features(c, h, l, v, spy_c):
    """All base quantities for today (arrays over the eligible stocks, security-id order)."""
    f = {}
    for L in (20, 50, 100, 150, 200):
        f[f"sma{L}"] = sma(c, L)
    for L in (100, 200):
        if c.shape[1] >= L + 21:
            prev = np.where(np.isnan(_last(c[:, :-21], L)).any(axis=1), np.nan, _last(c[:, :-21], L).mean(axis=1))
        else:
            prev = np.full(len(c), np.nan)
        f[f"slope{L}"] = f[f"sma{L}"] / prev - 1.0
    for K in (63, 126, 252):
        f[f"ret{K}"] = ret(c, K)
        f[f"rets{K}"] = ret(c, K, 21)
        sr = float(spy_c[-1] / spy_c[-1 - K] - 1.0) if len(spy_c) > K else np.nan
        f[f"xret{K}"] = f[f"ret{K}"] - sr
    for N in (63, 126, 252):
        f[f"max{N}"] = max_close(c, N)
    for n in (2, 5, 14):
        f[f"rsi{n}"] = rsi(c, n)
    f["pctb"] = pct_b(c)
    f["adx14"] = adx(h, l, c)
    f["macd"], f["macdsig"] = macd(c)
    f["vol63"] = realised_vol(c)
    f["volrank"] = pct_rank(f["vol63"], ascending=True)
    f["rv"] = rel_volume(v)
    f["close"] = c[:, -1]
    return f


def _gt(a, b):
    with np.errstate(invalid="ignore"):
        return np.nan_to_num(a, nan=-np.inf) > np.nan_to_num(b, nan=np.inf)


def _ok(*xs):
    m = np.ones(len(xs[0]), dtype=bool)
    for x in xs:
        m &= np.isfinite(x)
    return m


def primary(f, t, p):
    """(mask, strength) of a primary variant (type t, params p)."""
    c = f["close"]
    if t == "T1":
        s = c / f[f"sma{p['L']}"] - 1.0
        return _ok(s) & (s > 0), s
    if t == "T2":
        S, L = p["SL"]
        s = f[f"sma{S}"] / f[f"sma{L}"] - 1.0
        return _ok(s) & (s > 0), s
    if t == "T3":
        s = f[f"slope{p['L']}"]
        return _ok(s) & (s > 0), s
    if t == "M1":
        s = f[f"rets{p['K']}"]
        ok = _ok(s)
        n = int(ok.sum())
        k = max(1, int(round(p["q"] * n))) if n else 0
        r = pct_rank(s, ascending=False) * n          # 1 = best
        m = ok & (np.nan_to_num(r, nan=np.inf) <= k)
        return m, s
    if t == "M2":
        s = f[f"ret{p['K']}"]
        return _ok(s) & (s > 0), s
    if t == "M3":
        s = f[f"xret{p['K']}"]
        return _ok(s) & (s > 0), s
    if t == "B1":
        mx = f[f"max{p['N']}"]
        s = c / mx - 1.0
        return _ok(s) & (c >= (1 - p["x"]) * mx), s
    if t == "R1":
        n, th = p["nt"]
        x = f[f"rsi{n}"]
        return _ok(x) & (x <= th), -x
    if t == "R2":
        s = c / f["sma20"] - 1.0
        return _ok(s) & (c <= f["sma20"] * (1 - p["y"])), -s
    if t == "R3":
        x = f["pctb"]
        return _ok(x) & (x <= p["z"]), -x
    raise ValueError(t)


def confirm(f, t, p):
    c = f["close"]
    if t == "cT_sma200":
        return _gt(c, f["sma200"])
    if t == "cT_cross":
        return _gt(f["sma50"], f["sma200"])
    if t == "cT_adx":
        return _ok(f["adx14"]) & (np.nan_to_num(f["adx14"], nan=-1) >= p["a"])
    if t == "cT_macd0":
        return _ok(f["macd"]) & (np.nan_to_num(f["macd"], nan=-1) > 0)
    if t == "cM_r126":
        return _ok(f["ret126"]) & (np.nan_to_num(f["ret126"], nan=-1) > 0)
    if t == "cM_r252s":
        return _ok(f["rets252"]) & (np.nan_to_num(f["rets252"], nan=-1) > 0)
    if t == "cM_rsi":
        return _ok(f["rsi14"]) & (np.nan_to_num(f["rsi14"], nan=-1) >= p["r"])
    if t == "cM_macdsig":
        return _gt(f["macd"], f["macdsig"])
    if t == "cB_hi252":
        return _ok(f["max252"]) & (c >= 0.9 * np.nan_to_num(f["max252"], nan=np.inf))
    if t == "cR_rsi5":
        return _ok(f["rsi5"]) & (np.nan_to_num(f["rsi5"], nan=101) <= 30)
    if t == "cR_sma20":
        return _ok(f["sma20"]) & (c < np.nan_to_num(f["sma20"], nan=-np.inf))
    if t == "cP_rv":
        return _ok(f["rv"]) & (np.nan_to_num(f["rv"], nan=-1) >= p["v"])
    raise ValueError(t)


def risk(f, level):
    if level is None:
        return np.ones(len(f["close"]), dtype=bool)
    return _ok(f["volrank"]) & (np.nan_to_num(f["volrank"], nan=2.0) <= level)


class SignalTable:
    """Index arrays mapping the frozen configuration list onto primary / confirmation / risk variants, so that one day's
    configuration masks are composed from each base condition computed once."""

    def __init__(self, configs, primary_types, confirm_types, risk_levels):
        self.pv = sorted({(c["primary"][0], c["primary"][2]) for c in configs})
        self.cv = sorted({(c["confirm"][0], c["confirm"][2]) for c in configs if c["confirm"] is not None})
        self.rl = list(risk_levels)
        pidx = {k: i for i, k in enumerate(self.pv)}
        cidx = {k: i for i, k in enumerate(self.cv)}
        self.p_of = np.array([pidx[(c["primary"][0], c["primary"][2])] for c in configs])
        self.c_of = np.array([-1 if c["confirm"] is None else cidx[(c["confirm"][0], c["confirm"][2])] for c in configs])
        self.r_of = np.array([c["risk"] for c in configs])
        self.ptypes, self.ctypes = primary_types, confirm_types

    def evaluate(self, f):
        """(masks bool [configs x stocks], primary strengths [primary variants x stocks], primary index per config)."""
        n = len(f["close"])
        pm = np.zeros((len(self.pv), n), dtype=bool)
        ps = np.full((len(self.pv), n), np.nan)
        for i, (t, idx) in enumerate(self.pv):
            p = {name: vals[k] for (name, vals), k in zip(self.ptypes[t][1], idx)}
            pm[i], ps[i] = primary(f, t, p)
        cm = np.ones((len(self.cv) + 1, n), dtype=bool)            # last row = no confirmation
        for i, (t, idx) in enumerate(self.cv):
            p = {name: vals[k] for (name, vals), k in zip(self.ctypes[t][1], idx)}
            cm[i] = confirm(f, t, p)
        rm = np.stack([risk(f, lv) for lv in self.rl])
        masks = pm[self.p_of] & cm[self.c_of] & rm[self.r_of]
        return masks, ps, self.p_of
