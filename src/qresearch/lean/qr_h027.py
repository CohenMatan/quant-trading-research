# qr_h027.py — H027 Exposure-Controlled Learned Stock Score (owner D213; research/phase12/H027_spec.md, pinned by
# qresearch.p12h027). Pure numpy on top of the FROZEN qr_h026 (imported unchanged) and the frozen identity tether
# qr_p7_pred.Tether; the same file is unit-tested offline and uploaded to the host S029.
#   * the real H027 portfolio IS the H026 procedure (qr_h026.run_world(months, None)); nothing here changes it;
#   * LOWVOL-conditional null: in each world LOWVOL stays with its own stock and the other ten features move TOGETHER as
#     one vector from a persistent tether donor (qr_p7_pred.Tether, no self-matching); returns, prices, SPY, calendar,
#     corporate actions, sectors and the universe are never permuted; the complete pipeline is rerun per world;
#   * LV15_CONTROL: Top-15 by LOWVOL alone (lowest 60-day volatility first), the same picker / sector cap / costs;
#   * risk metrics with the P11-CP2 definitions (monthly marks = last session of each calendar month, capital first);
#   * gates A1-A6, the pre-registered null-adequacy rule, the non-gating LOWVOL-factor regression (Newey-West lag 2).
import hashlib
import math
import numpy as np

import qr_h026 as H
import qr_p7_pred as R

LOWVOL = H.FEATURES.index("LOWVOL")
OTHER = tuple(i for i in range(len(H.FEATURES)) if i != LOWVOL)        # MOM GPA ACC BM AG REV1M CBOP HI52 CFP EQA
R_NULL = 5000
ALPHA = 0.01
A3_WEALTH_RATIO, A3_EXCESS_CAGR = 1.15, 0.02
A4_MIN_YEARS = 5
A5_RATIO = 1.25
ADEQUACY_MIN_SHARE = 0.01        # pre-registered: >= 1% of null worlds as defensive as the real portfolio, per measure
NW_LAG = 2
QUINTILE = 0.2
DETERMINISM_SEEDS = tuple(range(1, 26))
FIELDS = ("seed", "S_WEALTH", "wealth", "excess_cagr", "maxdd", "vol", "beta", "up_capture", "down_capture",
          "years_beating") + tuple(f"ret_{y}" for y in H.OUTER_YEARS) + tuple(f"lam_{y}" for y in H.OUTER_YEARS) + \
    ("coef_sha",)


# ----------------------------------------------------------------------------------------------- conditional null
def conditional_permuted(months, seed):
    """Feature matrices of one LOWVOL-conditional null world: column LOWVOL is the real one of each stock; the ten
    other columns are the donor's complete OTHER vector (persistent tether donor on the same date). seed None = real."""
    if seed is None:
        return [m["X"] for m in months]
    T = R.Tether(seed)
    other = np.array(OTHER, dtype=np.int64)
    out = []
    for m in months:
        pos = {s: i for i, s in enumerate(m["ids"])}
        src = np.array([pos[s] for s in T.step(m["ids"])], dtype=np.int64)
        X = m["X"].copy()
        if src.size:
            X[:, other] = m["X"][src][:, other]
        out.append(X)
    return out


def donors(months, seed):
    """The tether donor id of every recipient per month (canary: persistence and no self-matching)."""
    T = R.Tether(seed)
    return [dict(zip(m["ids"], T.step(m["ids"]))) for m in months]


def run_world_xs(months, Xs, capital=H.CAPITAL, k=H.K, slip=H.SLIPPAGE, full=False, seed=None):
    """qr_h026.run_world with the feature matrices supplied (identical arithmetic, line for line), so the conditional
    null reruns the complete procedure: inner lambda selection, annual Ridge fits, scores, Top-15, costs, SPY."""
    fit = H.Fitter(months, Xs)
    years = sorted({m["test_year"] for m in months})
    first = {y: H.year_months(months, y) for y in years}
    coef, ntrain = {}, {}
    for y in range(H.FIRST_INNER, H.OUTER_YEARS[-1] + 1):
        cut = months[first[y][0]]["cutoff_day"]
        for lam in H.LAMBDAS:
            b0, b, n = fit.fit(cut, lam)
            coef[(y, lam)] = (b0, b)
            ntrain[(y, lam)] = n
    inner = {}
    for y in range(H.FIRST_INNER, H.OUTER_YEARS[-1]):
        ms = [months[i] for i in first[y]]
        spy = H.spy_simulate(ms, capital)["wealth"]
        for lam in H.LAMBDAS:
            b = coef[(y, lam)][1]
            w = H.simulate(ms, [Xs[i] @ b for i in first[y]], capital, k, slip)["wealth"]
            inner[(y, lam)] = math.log(w / spy)
    lam_y, sel = {}, {}
    for Y in H.OUTER_YEARS:
        cand = []
        for lam in H.LAMBDAS:
            ls = [inner[(y, lam)] for y in range(H.FIRST_INNER, Y)]
            cand.append((sum(ls), min(ls), lam))
        best = max(cand, key=lambda c: (c[0], c[1], c[2]))
        lam_y[Y] = best[2]
        sel[Y] = cand
    idx = [i for Y in H.OUTER_YEARS for i in first[Y]]
    ms = [months[i] for i in idx]
    sc = [Xs[i] @ coef[(months[i]["test_year"], lam_y[months[i]["test_year"]])][1] for i in idx]
    days = np.concatenate([m["days"] for m in ms])
    h = H.simulate(ms, sc, capital, k, slip, daily=True, keep_trades=full)
    s = H.spy_simulate(ms, capital, daily=True)
    hm, smet = H.path_metrics(h["daily"], days, capital, h["wealth"]), H.path_metrics(s["daily"], days, capital,
                                                                                      s["wealth"])
    yh, ys = H.year_returns(h["daily"], days, capital), H.year_returns(s["daily"], days, capital)
    sw = math.log(h["wealth"] / s["wealth"])
    rk = risk(h["daily"], s["daily"], days, capital)
    beta = {Y: coef[(Y, lam_y[Y])][1] for Y in H.OUTER_YEARS}
    rec = dict(seed=seed, S_WEALTH=sw, wealth=h["wealth"], excess_cagr=hm["cagr"] - smet["cagr"], maxdd=hm["maxdd"],
               vol=hm["vol"], beta=rk["beta"], up_capture=rk["up_capture"], down_capture=rk["down_capture"],
               years_beating=sum(1 for y in H.OUTER_YEARS if yh[y] > ys[y]), years=[yh[y] for y in H.OUTER_YEARS],
               lam=[lam_y[Y] for Y in H.OUTER_YEARS], coef=[beta[Y].tolist() for Y in H.OUTER_YEARS],
               coef_sha=coef_sha(beta))
    if not full:
        return rec
    return dict(rec=rec, Xs=Xs, coef=coef, ntrain=ntrain, inner=inner, lam_y=lam_y, sel=sel, idx=idx, scores=sc,
                days=days, h=h, s=s, hm=hm, sm=smet, yh=yh, ys=ys)


def run_conditional(months, seed, **kw):
    """One LOWVOL-conditional null world (seed >= 1) or, with seed None, the real H026/H027 assignment."""
    return run_world_xs(months, conditional_permuted(months, seed), seed=seed, **kw)


def coef_sha(beta_by_year):
    return hashlib.sha256(np.array([beta_by_year[Y] for Y in H.OUTER_YEARS], float).round(15).tobytes()).hexdigest()[:16]


def row(rec):
    """A compact null-world row in FIELDS order (full coefficients travel separately for the determinism seeds)."""
    return [rec["seed"], rec["S_WEALTH"], rec["wealth"], rec["excess_cagr"], rec["maxdd"], rec["vol"], rec["beta"],
            rec["up_capture"], rec["down_capture"], rec["years_beating"]] + list(rec["years"]) + list(rec["lam"]) + \
        [rec["coef_sha"]]


# ----------------------------------------------------------------------------------------------- LV15 control
def lv15_scores(months):
    """LV15_CONTROL: rank by LOWVOL alone, lowest 60-day volatility first (X[:, LOWVOL] is the centred percentile of the
    raw volatility, so the score is its negative); ties -> security id (qr_h026.pick)."""
    return [-m["X"][:, LOWVOL] for m in months]


def lv15(ms, capital=H.CAPITAL, slip=H.SLIPPAGE, daily=True):
    return H.simulate(ms, lv15_scores(ms), capital, H.K, slip, daily=daily)


# ----------------------------------------------------------------------------------------------- risk metrics
def month_ends(days):
    """Indices of the last session of each calendar month in a session-day array."""
    mon = np.array([str(np.datetime64(int(d), "D"))[:7] for d in days])
    return [i for i in range(len(days)) if i == len(days) - 1 or mon[i + 1] != mon[i]]


def risk(eq_h, eq_s, days, capital):
    """Monthly beta to SPY and up / down capture (P11-CP2 definitions): month-end marks with the starting capital
    first; beta = cov / var (ddof 1); capture = mean strategy return / mean SPY return over SPY-up (-down) months."""
    ends = month_ends(days)
    mh = np.r_[capital, np.asarray(eq_h, float)[ends]]
    ms = np.r_[capital, np.asarray(eq_s, float)[ends]]
    rh, rs = mh[1:] / mh[:-1] - 1.0, ms[1:] / ms[:-1] - 1.0
    up, dn = rs > 0, rs < 0
    beta = float(np.cov(rh, rs, ddof=1)[0, 1] / np.var(rs, ddof=1))
    return dict(beta=beta, up_capture=float(rh[up].mean() / rs[up].mean()) if up.any() else float("nan"),
                down_capture=float(rh[dn].mean() / rs[dn].mean()) if dn.any() else float("nan"),
                corr=float(np.corrcoef(rh, rs)[0, 1]), months=int(rh.size), rh=rh, rs=rs)


# ----------------------------------------------------------------------------------------------- gates
def empirical_p(null_s, s_real):
    """(1 + #{null >= real}) / (1 + R): the convention of the prior phases (H026: 100 / 5001)."""
    a = np.asarray(null_s, float)
    return float((1 + int((a >= s_real).sum())) / (1 + a.size))


def adequacy(null_rows, real):
    """Pre-registered conditional-null risk adequacy: for EACH of volatility, MaxDD, beta and down-capture, at least
    ADEQUACY_MIN_SHARE of the null worlds are at least as defensive as the real portfolio (vol <= real, MaxDD >= real
    (shallower), beta <= real, down-capture <= real). Otherwise CONDITIONAL NULL INADEQUATE."""
    col = {f: i for i, f in enumerate(FIELDS)}
    out = {}
    for key, better in (("vol", np.less_equal), ("maxdd", np.greater_equal), ("beta", np.less_equal),
                        ("down_capture", np.less_equal)):
        x = np.array([r[col[key]] for r in null_rows], float)
        n = int(better(x, real[key]).sum())
        out[key] = dict(real=real[key], at_least_as_defensive=n, share=n / max(1, x.size),
                        ok=n >= math.ceil(ADEQUACY_MIN_SHARE * x.size))
    out["adequate"] = all(v["ok"] for v in out.values() if isinstance(v, dict))
    return out


def gates(h, s, lv, yh, ys, ylv, stress_h, stress_s, stress_lv, c_cond):
    """A1-A6 (spec section 10). h / s / lv: path metrics of H027 / SPY / LV15_CONTROL; y*: calendar-year returns;
    stress_*: terminal wealth with 0.20% slippage per side (same selections, no retraining). A1's empirical p is
    computed against the committed null rows offline; S > c (the 50th largest of 5,000) implies p <= 50 / 5001."""
    sw = math.log(h["wealth"] / s["wealth"])
    L = {y: math.log((1 + yh[y]) / (1 + ylv[y])) for y in H.OUTER_YEARS}
    a1 = sw > c_cond
    a2 = h["wealth"] > lv["wealth"] and h["cagr"] > lv["cagr"]
    a3 = h["wealth"] >= A3_WEALTH_RATIO * s["wealth"] and h["cagr"] - s["cagr"] >= A3_EXCESS_CAGR
    a4 = (sum(1 for v in L.values() if v > 0) >= A4_MIN_YEARS and sum(L[y] for y in (2015, 2016, 2017)) > 0
          and sum(L[y] for y in (2018, 2019, 2020, 2021)) > 0)
    a5 = abs(h["maxdd"]) <= A5_RATIO * abs(s["maxdd"]) and h["vol"] <= A5_RATIO * s["vol"]
    a6 = stress_h > stress_s and stress_h > stress_lv
    return dict(S_WEALTH=sw, L_vs_lv15=L, years_beating_lv15=sum(1 for v in L.values() if v > 0),
                A1=bool(a1), A2=bool(a2), A3=bool(a3), A4=bool(a4), A5=bool(a5), A6=bool(a6),
                all=bool(a1 and a2 and a3 and a4 and a5 and a6))


# ----------------------------------------------------------------------------------------------- diagnostics
def lowvol_factor(ms):
    """Per decision month: equal-weight return of the lowest-volatility quintile minus the equal-weight eligible
    population (open-valid stocks; open of the entry session -> close of the period end, r_oc)."""
    out = []
    for m in ms:
        ok = np.asarray(m["open_ok"], bool)
        if ok.sum() < 5:
            out.append(float("nan"))
            continue
        x = m["X"][ok, LOWVOL]
        r = np.asarray(m["r_oc"], float)[ok]
        q = x <= np.quantile(x, QUINTILE)
        out.append(float(r[q].mean() - r.mean()))
    return np.array(out, float)


def period_returns(eq, ms, capital):
    """Strategy (or SPY) return per decision period from the daily close marks: last mark of period m over the last
    mark of period m - 1 (the first period from the starting capital)."""
    ends = np.cumsum([len(m["days"]) for m in ms]) - 1
    v = np.r_[capital, np.asarray(eq, float)[ends]]
    return v[1:] / v[:-1] - 1.0


def nw_regression(y, x, lag=NW_LAG):
    """OLS y = a + g x + e with a Newey-West (Bartlett, lag) standard error for a. Returns a, g, t(a), R^2, n."""
    ok = np.isfinite(y) & np.isfinite(x)
    y, x = np.asarray(y, float)[ok], np.asarray(x, float)[ok]
    X = np.c_[np.ones_like(x), x]
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    n = y.size
    XtXi = np.linalg.inv(X.T @ X)
    S = (X * e[:, None]).T @ (X * e[:, None])
    for L in range(1, lag + 1):
        w = 1.0 - L / (lag + 1.0)
        G = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None])
        S += w * (G + G.T)
    V = XtXi @ S @ XtXi
    r2 = float(1 - (e @ e) / ((y - y.mean()) @ (y - y.mean())))
    return dict(alpha=float(b[0]), gamma=float(b[1]), t_alpha=float(b[0] / math.sqrt(V[0, 0])), r2=r2, n=int(n),
                alpha_annualised=float(b[0] * 12.0))
