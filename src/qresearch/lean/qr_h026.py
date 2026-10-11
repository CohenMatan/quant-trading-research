# qr_h026.py — H026 Learned Stock Score Portfolio (owner D206; research/phase11/H026_spec.md, pinned by
# qresearch.p11h026). Pure numpy (+ the frozen identity tether qr_p7_pred.Tether); the same file is unit-tested offline
# and uploaded to the host S028.
#   * percentile transform x = 2p - 1, p = (rank - 1)/(n - 1) (average ranks) for features and labels;
#   * weighted Ridge (each review month total weight 1, unpenalised intercept) from per-month sufficient statistics,
#     with prefix sums over months ordered by label-exit date (label availability: exit date < cutoff);
#   * nested walk-forward: inner years 2013..Y-1 select lambda by sum ln(W/SPY) of year-long Top-15 simulations;
#   * the Top-15 FF12-capped portfolio simulator (sells, kept positions untouched, new positions at equity/15,
#     $7 per order, slippage per side, dead positions to cash at their last close), SPY buy-and-hold, metrics, gates;
#   * one null world = the complete procedure on tether-permuted complete feature vectors.
import math
import numpy as np

import qr_p7_pred as R

FEATURES = ("MOM", "LOWVOL", "GPA", "ACC", "BM", "AG", "REV1M", "CBOP", "HI52", "CFP", "EQA")
LAMBDAS = (0.01, 0.1, 1.0, 10.0, 100.0)
HORIZON = 63
K = 15
SECTOR_CAP = 3
CAPITAL = 100_000.0
COMMISSION = 7.0
SLIPPAGE = 0.001
STRESS_SLIPPAGE = 0.002
OUTER_YEARS = (2015, 2016, 2017, 2018, 2019, 2020, 2021)
FIRST_INNER = 2013
R_NULL = 5000
ALPHA = 0.01
DETERMINISM_SEEDS = tuple(range(1, 26))
D2_WEALTH_RATIO = 1.15
D2_EXCESS_CAGR = 0.02
D3_MIN_YEARS = 5
D3_MAX_SHARE = 0.5
D4_RATIO = 1.25
ANN = 252.0


# ----------------------------------------------------------------------------------------------- transforms
def avg_rank(x):
    """Average ranks 1..n (ties averaged) of a 1-D finite array."""
    x = np.asarray(x, float)
    n = x.size
    order = np.argsort(x, kind="mergesort")
    sx = x[order]
    r = np.empty(n)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sx[j + 1] == sx[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def centred_percentile(x):
    """x -> 2p - 1 with p = (avg rank - 1)/(n - 1) over the finite entries (NaN stays NaN); n = 1 -> 0."""
    x = np.asarray(x, float)
    out = np.full(x.size, np.nan)
    ok = np.isfinite(x)
    n = int(ok.sum())
    if n == 1:
        out[ok] = 0.0
    elif n > 1:
        out[ok] = 2.0 * (avg_rank(x[ok]) - 1.0) / (n - 1) - 1.0
    return out


def feature_matrix(raw):
    """(n, 11) raw feature values (all finite: the population rule) -> centred percentiles, column by column."""
    raw = np.asarray(raw, float)
    return np.column_stack([centred_percentile(raw[:, j]) for j in range(raw.shape[1])])


# ----------------------------------------------------------------------------------------------- returns
def tsr(raw_open, raw_close, mult, e0, x0, unverified_rows=()):
    """TSR bought at the open of row e0, held to the close of row x0 (the frozen qr_p7_pred.response conventions with
    t = e0 - 1, t_next = x0; = qr_h025.tsr): first valid open in [e0, x0]; exit = close of x0, else the last real close
    (cash afterwards); no bar -> (nan, 'no_bar'); unverified split in [e0, x0] -> (nan, 'unverified_split')."""
    O, C, m = raw_open, raw_close, mult
    if any(e0 <= int(u) <= x0 for u in unverified_rows):
        return float("nan"), "unverified_split", None, None
    rows = np.arange(e0, x0 + 1)
    ok = np.isfinite(O[rows]) & (O[rows] > 0) & np.isfinite(C[rows]) & (C[rows] > 0)
    if not ok.any():
        return float("nan"), "no_bar", None, None
    e = int(rows[np.argmax(ok)])
    okc = np.isfinite(C[e:x0 + 1]) & (C[e:x0 + 1] > 0)
    x = e + int(np.flatnonzero(okc)[-1])
    return float((C[x] * m[x]) / (O[e] * m[e]) - 1.0), ("ok" if x == x0 else "truncated"), e, x


def holding(raw_open, raw_close, mult, e, nxt, end, unverified_rows=()):
    """Portfolio arrays of ONE stock for one holding period: bought at the open of row e (must be a valid bar), held
    to the open of row nxt (the next entry) or, for the final period / liquidation, to the close of row end.
    Returns (open_ok, r_oo, alive_next, r_oc, alive_end, daily TR path over rows e..end, forward-filled)."""
    O, C, m = raw_open, raw_close, mult
    n = end - e + 1
    if any(e <= int(u) <= end for u in unverified_rows) or not (np.isfinite(O[e]) and O[e] > 0
                                                                and np.isfinite(C[e]) and C[e] > 0):
        return False, 0.0, False, 0.0, False, np.zeros(n)
    base = O[e] * m[e]
    c = C[e:end + 1]
    okc = np.isfinite(c) & (c > 0)
    tr = np.where(okc, c * m[e:end + 1] / base - 1.0, np.nan)
    for i in range(n):                                                  # forward-fill halts / after the last close
        if not np.isfinite(tr[i]):
            tr[i] = tr[i - 1] if i else 0.0
    last = int(np.flatnonzero(okc)[-1])
    r_oc = float(tr[-1])
    alive_end = bool(okc[-1])
    if nxt is not None and nxt < len(O) and np.isfinite(O[nxt]) and O[nxt] > 0:
        return True, float(O[nxt] * m[nxt] / base - 1.0), True, r_oc, alive_end, tr
    return True, float(tr[last]), False, r_oc, alive_end, tr


# ----------------------------------------------------------------------------------------------- Ridge
def month_stats(X, y):
    """Sufficient statistics of ONE review month with weight 1/N_t per training row (rows with finite y)."""
    ok = np.isfinite(y)
    n = int(ok.sum())
    if n == 0:
        return None
    Xv, yv = X[ok], y[ok]
    return dict(n=n, sx=Xv.sum(0) / n, sxx=Xv.T @ Xv / n, sy=float(yv.mean()), sxy=Xv.T @ yv / n)


def ridge_from_stats(stats, lam):
    """Weighted Ridge: minimise sum_t sum_i (1/N_t)(y - b0 - x.b)^2 + lam |b|^2 (intercept unpenalised).
    Returns (b0, b)."""
    W = float(len(stats))
    if W == 0:
        return 0.0, np.zeros(len(FEATURES))
    sx = sum(s["sx"] for s in stats)
    sxx = sum(s["sxx"] for s in stats)
    sy = sum(s["sy"] for s in stats)
    sxy = sum(s["sxy"] for s in stats)
    return _solve(W, sx, sxx, sy, sxy, lam)


def _solve(W, sx, sxx, sy, sxy, lam):
    mx, my = sx / W, sy / W
    A = sxx - W * np.outer(mx, mx)
    b = sxy - W * mx * my
    beta = np.linalg.solve(A + lam * np.eye(A.shape[0]), b)
    return float(my - mx @ beta), beta


def ridge_reference(X, y, w, lam):
    """Independent reference: augmented least squares with sqrt weights and an unpenalised intercept."""
    X, y, w = (np.asarray(a, float) for a in (X, y, w))
    p = X.shape[1]
    Z = np.column_stack([np.ones(len(y)), X]) * np.sqrt(w)[:, None]
    t = y * np.sqrt(w)
    P = np.zeros((p, p + 1))
    P[:, 1:] = np.sqrt(lam) * np.eye(p)
    coef = np.linalg.lstsq(np.vstack([Z, P]), np.r_[t, np.zeros(p)], rcond=None)[0]
    return float(coef[0]), coef[1:]


class Fitter:
    """Prefix sums of month statistics in label-exit order: fit(cutoff, lam) uses every month whose label exit day is
    strictly before the cutoff day (label availability)."""

    def __init__(self, months, Xs):
        self.order = sorted(range(len(months)), key=lambda i: (months[i]["exit_day"], i))
        self.exit = np.array([months[i]["exit_day"] for i in self.order], float)
        p = len(FEATURES)
        n = len(self.order)
        self.W = np.zeros(n + 1)
        self.sx = np.zeros((n + 1, p))
        self.sxx = np.zeros((n + 1, p, p))
        self.sy = np.zeros(n + 1)
        self.sxy = np.zeros((n + 1, p))
        for r, i in enumerate(self.order):
            s = month_stats(Xs[i], months[i]["label"])
            self.W[r + 1] = self.W[r] + (1 if s else 0)
            self.sx[r + 1] = self.sx[r] + (s["sx"] if s else 0)
            self.sxx[r + 1] = self.sxx[r] + (s["sxx"] if s else 0)
            self.sy[r + 1] = self.sy[r] + (s["sy"] if s else 0)
            self.sxy[r + 1] = self.sxy[r] + (s["sxy"] if s else 0)

    def n_before(self, cutoff_day):
        return int(np.searchsorted(self.exit, cutoff_day, side="left"))

    def fit(self, cutoff_day, lam):
        m = self.n_before(cutoff_day)
        if self.W[m] == 0:
            return 0.0, np.zeros(len(FEATURES)), 0
        b0, b = _solve(self.W[m], self.sx[m], self.sxx[m], self.sy[m], self.sxy[m], lam)
        return b0, b, int(self.W[m])

    def months_used(self, cutoff_day):
        return [self.order[r] for r in range(self.n_before(cutoff_day))]


# ----------------------------------------------------------------------------------------------- portfolio
def pick(month, score, k=K, cap=SECTOR_CAP):
    """Target list: walk down the score ranking (ties: security id) skipping full FF12 sectors and stocks without a
    valid open on the entry session; at most k."""
    ids, sec, ok = month["ids"], month["sector"], month["open_ok"]
    order = np.argsort(-np.asarray(score, float), kind="stable")      # ids are sorted: ties -> security id
    out, cnt = [], {}
    for i in order:
        if not ok[i]:
            continue
        s = sec[i]
        if cnt.get(s, 0) >= cap:
            continue
        out.append(int(i))
        cnt[s] = cnt.get(s, 0) + 1
        if len(out) == k:
            break
    return out


def simulate(months, scores, capital=CAPITAL, k=K, slip=SLIPPAGE, comm=COMMISSION, cap=SECTOR_CAP, daily=False,
             keep_trades=False):
    """Top-k portfolio over consecutive decision months (each month: entry open -> next month's entry open; the last
    month ends at its period's final close and is liquidated after costs). Returns dict(wealth, trades, commissions,
    slippage, turnover, holdings, cash_share, months, daily equity if requested, picks if requested)."""
    cash, hold = float(capital), {}
    nb = ns = 0
    com = slp = 0.0
    turnover, nhold, cashsh, picks = [], [], [], []
    path = []
    last = len(months) - 1
    for m_i, (m, sc) in enumerate(zip(months, scores)):
        tgt = pick(m, sc, k, cap)
        pos = {m["ids"][i]: i for i in tgt}
        traded = 0.0
        for sid in [s for s in hold if s not in pos]:
            v = hold.pop(sid)
            cash += v * (1.0 - slip) - comm
            com += comm
            slp += v * slip
            traded += v
            ns += 1
        eq = cash + sum(hold.values())
        new = [sid for sid in pos if sid not in hold]
        if new:
            t_val = eq / k
            need = len(new) * (t_val * (1.0 + slip) + comm)
            a = t_val if need <= cash else max((cash - comm * len(new)) / (len(new) * (1.0 + slip)), 0.0)
            if a > 0:
                for sid in new:
                    cash -= a * (1.0 + slip) + comm
                    com += comm
                    slp += a * slip
                    traded += a
                    hold[sid] = a
                    nb += 1
        turnover.append(traded / eq if eq > 0 else 0.0)
        nhold.append(len(hold))
        cashsh.append(cash / eq if eq > 0 else 1.0)
        if keep_trades:
            picks.append(sorted(hold))
        idx = np.array([pos[s] for s in hold], dtype=np.int64)
        vals = np.array([hold[s] for s in hold], float)
        if daily:
            dm = m["daily"][:, idx] if idx.size else np.zeros((m["daily"].shape[0], 0))
            path.append(cash + (vals * (1.0 + dm)).sum(1))
        if m_i == last:
            end = vals * (1.0 + m["r_oc"][idx])
            alive = m["alive_end"][idx]
            cash += float(end[~alive].sum()) + float((end[alive] * (1.0 - slip)).sum()) - comm * int(alive.sum())
            com += comm * int(alive.sum())
            slp += float(end[alive].sum()) * slip
            ns += int(alive.sum())
            hold = {}
        else:
            nv = vals * (1.0 + m["r_oo"][idx])
            alive = m["alive_next"][idx]
            hold = {s: float(v) for s, v, a in zip(list(hold), nv, alive) if a}
            cash += float(nv[~alive].sum())
    out = dict(wealth=cash, buys=nb, sells=ns, trades=nb + ns, commissions=com, slippage=slp,
               turnover=turnover, holdings=nhold, cash_share=cashsh, months=len(months))
    if daily:
        out["daily"] = np.concatenate(path) if path else np.zeros(0)
    if keep_trades:
        out["picks"] = picks
    return out


def spy_simulate(months, capital=CAPITAL, slip=SLIPPAGE, comm=COMMISSION, daily=False):
    """SPY bought at the first entry open (commission + slippage), total return, sold at the final close."""
    v = (capital - comm) / (1.0 + slip)
    path = []
    last = len(months) - 1
    for m_i, m in enumerate(months):
        if daily:
            path.append(v * (1.0 + m["spy_daily"]))
        v *= 1.0 + (m["spy_oc"] if m_i == last else m["spy_oo"])
    out = dict(wealth=v * (1.0 - slip) - comm)
    if daily:
        out["daily"] = np.concatenate(path) if path else np.zeros(0)
    return out


# ----------------------------------------------------------------------------------------------- metrics
def max_drawdown(eq):
    eq = np.asarray(eq, float)
    peak = np.maximum.accumulate(eq)
    return float((eq / peak - 1.0).min())


def underwater(eq):
    eq = np.asarray(eq, float)
    under = eq < np.maximum.accumulate(eq) - 1e-12
    longest = cur = 0
    for u in under:
        cur = cur + 1 if u else 0
        longest = max(longest, cur)
    return float(under.mean()), int(longest)


def path_metrics(eq, days, capital, wealth):
    """Metrics of one daily equity path (sessions `days`, day numbers) with final wealth after liquidation."""
    eq = np.asarray(eq, float)
    r = np.diff(np.r_[capital, eq]) / np.r_[capital, eq][:-1]
    years = (days[-1] - days[0] + 1) / 365.25
    sd = float(r.std(ddof=1))
    uw = underwater(eq)
    return dict(wealth=wealth, cagr=(wealth / capital) ** (1.0 / years) - 1.0, vol=sd * math.sqrt(ANN),
                sharpe=float(r.mean()) / sd * math.sqrt(ANN) if sd > 0 else 0.0, maxdd=max_drawdown(np.r_[capital, eq]),
                underwater_share=uw[0], underwater_longest=uw[1], years=years)


def year_returns(eq, days, capital, years=OUTER_YEARS):
    """Calendar-year returns from year-end close marks (first year from the starting capital)."""
    yrs = np.array([int(str(np.datetime64(int(d), "D"))[:4]) for d in days])
    out, prev = {}, capital
    for y in years:
        idx = np.flatnonzero(yrs == y)
        if idx.size == 0:
            continue
        v = float(eq[idx[-1]])
        out[y] = v / prev - 1.0
        prev = v
    return out


def gates(h, s, yh, ys, stress_h, stress_s, c_wealth):
    """D1-D5 (spec section 10). h / s: path metrics of H026 / SPY; yh / ys: yearly returns."""
    sw = math.log(h["wealth"] / s["wealth"])
    L = {y: math.log((1 + yh[y]) / (1 + ys[y])) for y in OUTER_YEARS}
    pos = [v for v in L.values() if v > 0]
    share = max(pos) / sum(pos) if pos else float("inf")
    d1 = sw > c_wealth and sw > 0
    d2 = h["wealth"] >= D2_WEALTH_RATIO * s["wealth"] and h["cagr"] - s["cagr"] >= D2_EXCESS_CAGR
    d3 = (sum(1 for v in L.values() if v > 0) >= D3_MIN_YEARS and sum(L[y] for y in (2015, 2016, 2017)) > 0
          and sum(L[y] for y in (2018, 2019, 2020, 2021)) > 0 and share <= D3_MAX_SHARE)
    d4 = abs(h["maxdd"]) <= D4_RATIO * abs(s["maxdd"]) and h["vol"] <= D4_RATIO * s["vol"]
    d5 = stress_h > stress_s
    return dict(S_WEALTH=sw, L=L, largest_share=share, D1=bool(d1), D2=bool(d2), D3=bool(d3), D4=bool(d4),
                D5=bool(d5), all=bool(d1 and d2 and d3 and d4 and d5))


def critical_value(null_s, alpha=ALPHA):
    """c_WEALTH = the k-th largest null S_WEALTH, k = ceil(alpha x R) (the 50th largest of 5,000)."""
    v = np.sort(np.asarray(null_s, float))[::-1]
    return float(v[max(1, int(math.ceil(alpha * v.size))) - 1])


# ----------------------------------------------------------------------------------------------- procedure
def year_months(months, year):
    return [i for i, m in enumerate(months) if m["test_year"] == year]


def permuted(months, seed):
    """Tether-permuted feature matrices (complete 11-feature vectors move together); seed None = real."""
    if seed is None:
        return [m["X"] for m in months]
    T = R.Tether(seed)
    out = []
    for m in months:
        pos = {s: i for i, s in enumerate(m["ids"])}
        src = T.step(m["ids"])
        out.append(m["X"][np.array([pos[s] for s in src], dtype=np.int64)])
    return out


def run_world(months, seed=None, capital=CAPITAL, k=K, slip=SLIPPAGE, full=False):
    """The complete H026 procedure (spec sections 5-8) on one assignment of feature vectors.
    months: decision months in date order, each with ids, sector, X, label, exit_day, cutoff_day (= its review day),
    test_year, open_ok, r_oo, r_oc, alive_next, alive_end, spy_oo, spy_oc (and daily / spy_daily / days for the outer
    years). Returns the null record (S_WEALTH and diagnostics) or, with full=True, every intermediate result."""
    Xs = permuted(months, seed)
    fit = Fitter(months, Xs)
    years = sorted({m["test_year"] for m in months})
    first = {y: year_months(months, y) for y in years}
    coef, ntrain = {}, {}
    for y in range(FIRST_INNER, OUTER_YEARS[-1] + 1):
        cut = months[first[y][0]]["cutoff_day"]
        for lam in LAMBDAS:
            b0, b, n = fit.fit(cut, lam)
            coef[(y, lam)] = (b0, b)
            ntrain[(y, lam)] = n
    inner = {}
    for y in range(FIRST_INNER, OUTER_YEARS[-1]):
        ms = [months[i] for i in first[y]]
        spy = spy_simulate(ms, capital)["wealth"]
        for lam in LAMBDAS:
            b = coef[(y, lam)][1]
            w = simulate(ms, [Xs[i] @ b for i in first[y]], capital, k, slip)["wealth"]
            inner[(y, lam)] = math.log(w / spy)
    lam_y, sel = {}, {}
    for Y in OUTER_YEARS:
        cand = []
        for lam in LAMBDAS:
            ls = [inner[(y, lam)] for y in range(FIRST_INNER, Y)]
            cand.append((sum(ls), min(ls), lam))
        best = max(cand, key=lambda c: (c[0], c[1], c[2]))
        lam_y[Y] = best[2]
        sel[Y] = cand
    idx = [i for Y in OUTER_YEARS for i in first[Y]]
    ms = [months[i] for i in idx]
    sc = [Xs[i] @ coef[(months[i]["test_year"], lam_y[months[i]["test_year"]])][1] for i in idx]
    days = np.concatenate([m["days"] for m in ms])
    h = simulate(ms, sc, capital, k, slip, daily=True, keep_trades=full)
    s = spy_simulate(ms, capital, daily=True)
    hm, smet = path_metrics(h["daily"], days, capital, h["wealth"]), path_metrics(s["daily"], days, capital, s["wealth"])
    yh, ys = year_returns(h["daily"], days, capital), year_returns(s["daily"], days, capital)
    sw = math.log(h["wealth"] / s["wealth"])
    rec = dict(seed=seed, S_WEALTH=sw, excess_cagr=hm["cagr"] - smet["cagr"], maxdd=hm["maxdd"], vol=hm["vol"],
               years_beating=sum(1 for y in OUTER_YEARS if yh[y] > ys[y]), lam=[lam_y[Y] for Y in OUTER_YEARS])
    if not full:
        return rec
    return dict(rec=rec, Xs=Xs, coef=coef, ntrain=ntrain, inner=inner, lam_y=lam_y, sel=sel, idx=idx, scores=sc,
                days=days, h=h, s=s, hm=hm, sm=smet, yh=yh, ys=ys)
