# qr_h029.py — H029 standalone Business Improvement Score and H030 fixed 50/50 combination with frozen H028 (owner D229;
# research/phase14/H029_H030_spec.md, pinned by qresearch.p14h029). Pure numpy on top of the FROZEN qr_h026 (portfolio,
# Fitter, metrics), qr_p7_pred (identity tether) and qr_v3 (Data v3 H029 score); unit-tested offline
# (tests/test_p14_h029.py) and uploaded to the standalone host S031.
#   * H028 component: one Ridge fit per outer year with lambda = 100 (the frozen qr_h028.run_world_fixed arithmetic,
#     replicated in fixed_fits / h028_scores and proven equal offline); never refit or modified in any world;
#   * H029 score: qr_v3.h029_score (equal-weight mean of centred percentiles, >= 5 of 6); no model of any kind;
#   * H030 score: blend() -- 0.50 x centred(H028) + 0.50 x centred(H029) over the joint universe; constant weights,
#     no weight parameter anywhere;
#   * null (Amendment 1, owner D233, research/phase14/H029_H030_amendment1_sector_null.md): the six-signal vectors move
#     whole through the persistent identity tether STRATIFIED BY THE RECIPIENT'S FF12 SECTOR at the review (the frozen
#     H020 ChartTether with strata, via qr_p7_pred) among the H029-eligible stocks of each evaluation month; a donor is
#     always another stock of the same sector (a self-match = STOP, never a cross-sector fallback); H028, returns,
#     sectors and eligibility stay with the recipient. The original single-stratum null (P14-CP3a) was inadequate;
#   * statistics: calendar month-end marks (qr_h027.risk convention, copied in risk()), S_UP, captures, year
#     contributions, gates N1-N5 / C1-C7, adequacy.
import math

import numpy as np

import qr_h026 as H
import qr_p7_pred as R
import qr_v3 as V3

LAMBDA = 100.0
assert LAMBDA in H.LAMBDAS
OUTER = H.OUTER_YEARS
R_NULL = 5000
ALPHA = 0.01
DETERMINISM_SEEDS = tuple(range(1, 26))
LOWVOL = H.FEATURES.index("LOWVOL")
EX_YEARS = (2018, 2020)
EARLY, LATE = (2015, 2016, 2017), (2018, 2019, 2020, 2021)
ADEQ_Q = (0.5, 99.5)
ADEQ_MEDIAN = (0.5, 1.5)
SYNTH_A_SEEDS = (7101, 7102, 7103, 7104, 7105)
SYNTH_B_SEED = 7201
SYNTH_NULLS = 50
SYNTH_B_NOISE = 0.05
NULL_FIELDS = ("seed", "s_up29", "w29", "up29", "dn29", "beta29", "vol29", "mdd29", "turn29", "hhi29",
               "s_inc30", "w30", "up30", "dn30", "beta30", "vol30", "mdd30", "turn30", "hhi30", "s_up30")


# ----------------------------------------------------------------------------------------------- H028 (frozen path)
def outer_index(months):
    """Indices of the evaluation months, outer year by outer year (the qr_h028.run_world_fixed order)."""
    return [i for Y in OUTER for i in H.year_months(months, Y)]


def fixed_fits(months, Xs):
    """{Y: (b0, beta, n)}: one Ridge fit per outer year, lambda = 100, on every month whose label exits before Y's
    first review (qr_h026.Fitter) -- the frozen H028 fits."""
    fit = H.Fitter(months, Xs)
    out = {}
    for Y in OUTER:
        cut = months[H.year_months(months, Y)[0]]["cutoff_day"]
        out[Y] = fit.fit(cut, LAMBDA)
    return out


def h028_scores(months, Xs, fits):
    """The frozen H028 raw scores X . beta_Y for the evaluation months (outer_index order)."""
    return [Xs[i] @ fits[months[i]["test_year"]][1] for i in outer_index(months)]


def lv15_scores(ms):
    """LV15_CONTROL (frozen qr_h027.lv15_scores): lowest 60-day volatility first."""
    return [-m["X"][:, LOWVOL] for m in ms]


# ----------------------------------------------------------------------------------------------- H029 / H030 scores
def h029_scores(Vs):
    return [V3.h029_score(V)[0] for V in Vs]


def blend(h028_raw, h029_raw):
    """H030 = 0.50 x centred(H028) + 0.50 x centred(H029) over the joint universe (spec 5). The ONLY blend."""
    return 0.5 * V3.centred(h028_raw) + 0.5 * V3.centred(h029_raw)


def joint(ids28, ids29):
    """(joint ids, positions in the H028 month, positions in the H029 month), ids sorted."""
    p28 = {s: i for i, s in enumerate(ids28)}
    p29 = {s: i for i, s in enumerate(ids29)}
    ids = sorted(set(p28) & set(p29))
    return ids, np.array([p28[s] for s in ids], dtype=np.int64), np.array([p29[s] for s in ids], dtype=np.int64)


def sub_month(m, ix, ids):
    """A month restricted to rows ix (holding arrays, sectors; SPY and calendar fields shared)."""
    out = dict(m)
    out["ids"] = list(ids)
    for k in ("sector", "open_ok", "r_oo", "alive_next", "r_oc", "alive_end"):
        out[k] = np.asarray(m[k])[ix]
    out["daily"] = m["daily"][:, ix]
    out.pop("X", None)
    return out


class NullNotConstructible(Exception):
    """STOP — SECTOR-STRATIFIED NULL NOT CONSTRUCTIBLE (owner D233 section 12)."""


def _sector_step(T, m):
    """One month of the sector-stratified tether: donor ids for m["ids"] (same FF12 sector, no self-match)."""
    ids = m["ids"]
    strata = [int(x) for x in np.asarray(m["sector"]).tolist()]
    src = T.step(ids, strata)
    for i, j in zip(ids, src):
        if i == j:
            raise NullNotConstructible(f"STOP — SECTOR-STRATIFIED NULL NOT CONSTRUCTIBLE ({m.get('day')}: {i})")
    return src


def tether_vectors(m29, Vs, seed):
    """Null world `seed` (Amendment 1): each recipient's complete six-signal vector replaced by its persistent tether
    donor's -- a donor from the recipient's own FF12 sector at the review (qr_h020_stats.ChartTether with the sector
    strata; persistent partners; no self-match) -- over the evaluation months in date order; seed None = real."""
    if seed is None:
        return list(Vs)
    T = R.H.ChartTether(seed)
    out = []
    for m, V in zip(m29, Vs):
        pos = {s: i for i, s in enumerate(m["ids"])}
        src = np.array([pos[s] for s in _sector_step(T, m)], dtype=np.int64)
        out.append(V[src] if src.size else V)
    return out


def donors(m29, seed):
    T = R.H.ChartTether(seed)
    return [dict(zip(m["ids"], _sector_step(T, m))) for m in m29]


# ----------------------------------------------------------------------------------------------- statistics
def month_ends(days):
    """Indices of the last session of each calendar month (frozen qr_h027.month_ends)."""
    mon = np.array([str(np.datetime64(int(d), "D"))[:7] for d in days])
    return [i for i in range(len(days)) if i == len(days) - 1 or mon[i + 1] != mon[i]]


def monthly(eq, days, capital=H.CAPITAL):
    """(monthly returns from calendar month-end marks with the capital first, 'YYYY-MM' labels)."""
    ends = month_ends(days)
    m = np.r_[capital, np.asarray(eq, float)[ends]]
    return m[1:] / m[:-1] - 1.0, [str(np.datetime64(int(days[i]), "D"))[:7] for i in ends]


def risk(rh, rs):
    """Beta and up / down capture (frozen qr_h027.risk definitions) from paired monthly returns."""
    rh, rs = np.asarray(rh, float), np.asarray(rs, float)
    up, dn = rs > 0, rs < 0
    return dict(beta=float(np.cov(rh, rs, ddof=1)[0, 1] / np.var(rs, ddof=1)),
                up_capture=float(rh[up].mean() / rs[up].mean()) if up.any() else float("nan"),
                down_capture=float(rh[dn].mean() / rs[dn].mean()) if dn.any() else float("nan"),
                corr=float(np.corrcoef(rh, rs)[0, 1]), months=int(rh.size))


def relative(rh, rs, labels):
    """Monthly relative log returns RL, S_UP, per-year up-month (U_y) and all-month (A_y) contributions, ex-2018/2020."""
    rh, rs = np.asarray(rh, float), np.asarray(rs, float)
    rl = np.log1p(rh) - np.log1p(rs)
    up = rs > 0
    yrs = np.array([int(x[:4]) for x in labels])
    U = {int(y): float(rl[up & (yrs == y)].sum()) for y in sorted(set(yrs.tolist()))}
    A = {int(y): float(rl[yrs == y].sum()) for y in sorted(set(yrs.tolist()))}
    ex = ~np.isin(yrs, EX_YEARS)
    return dict(rl=rl, s_up=float(rl[up].sum()), s_down=float(rl[rs < 0].sum()), U=U, A=A,
                ex1820=float(rl[ex].sum()), total=float(rl.sum()))


def concentration(contrib):
    """(max positive yearly contribution, total positive contribution, max share)."""
    pos = [max(v, 0.0) for v in contrib.values()]
    tot = float(sum(pos))
    mx = float(max(pos)) if pos else 0.0
    return mx, tot, (mx / tot if tot > 0 else float("inf"))


def selection_structure(ms, scores, k=H.K, cap=H.SECTOR_CAP):
    """Name turnover and FF12 Herfindahl of the per-month TARGET lists (qr_h026.pick; scores only, no returns)."""
    prev, turn, hhi = None, [], []
    for m, sc in zip(ms, scores):
        ix = H.pick(m, sc, k, cap)
        t = set(m["ids"][i] for i in ix)
        if prev is not None:
            turn.append(len(t - prev) / float(k))
        if ix:
            c = np.bincount(np.asarray(m["sector"])[ix].astype(np.int64)).astype(float)
            c = c[c > 0] / c.sum()
            hhi.append(float((c ** 2).sum()))
        prev = t
    return float(np.mean(turn)) if turn else float("nan"), float(np.mean(hhi)) if hhi else float("nan")


def evaluate(ms, scores, spy, days, capital=H.CAPITAL, slip=H.SLIPPAGE, keep=False):
    """One strategy's frozen Top-15 portfolio, its path metrics and monthly series vs the SPY path `spy`
    (dict(daily, wealth, r, labels))."""
    h = H.simulate(ms, scores, capital, H.K, slip, daily=True, keep_trades=keep)
    pm = H.path_metrics(h["daily"], days, capital, h["wealth"])
    r, lab = monthly(h["daily"], days, capital)
    rk = risk(r, spy["r"])
    rel = relative(r, spy["r"], lab)
    return dict(h=h, pm=pm, r=r, labels=lab, risk=rk, rel=rel, wealth=h["wealth"])


def spy_path(ms, days, capital=H.CAPITAL, slip=H.SLIPPAGE):
    s = H.spy_simulate(ms, capital, slip, daily=True)
    r, lab = monthly(s["daily"], days, capital)
    return dict(daily=s["daily"], wealth=s["wealth"], r=r, labels=lab,
                pm=H.path_metrics(s["daily"], days, capital, s["wealth"]))


# ----------------------------------------------------------------------------------------------- one world
def world(m29, m30, V29, sc28_j, j29, w28, spy, days, seed=None, keep=False):
    """H029 and H030 for one assignment of the six-signal vectors (seed None = real). m29: H029 evaluation months;
    m30: the joint months (H028 rows restricted to J); sc28_j: the real H028 raw scores on J; j29: positions of J in
    the H029 months; w28: the real H028 terminal wealth. H028 is never recomputed or permuted here."""
    Vp = tether_vectors(m29, V29, seed)
    sc29 = h029_scores(Vp)
    e29 = evaluate(m29, sc29, spy, days, keep=keep)
    sc30 = [blend(a, s[j]) for a, s, j in zip(sc28_j, sc29, j29)]
    e30 = evaluate(m30, sc30, spy, days, keep=keep)
    t29, h29 = selection_structure(m29, sc29)
    t30, h30 = selection_structure(m30, sc30)
    row = [seed, e29["rel"]["s_up"], e29["wealth"], e29["risk"]["up_capture"], e29["risk"]["down_capture"],
           e29["risk"]["beta"], e29["pm"]["vol"], e29["pm"]["maxdd"], t29, h29,
           math.log(e30["wealth"] / w28), e30["wealth"], e30["risk"]["up_capture"], e30["risk"]["down_capture"],
           e30["risk"]["beta"], e30["pm"]["vol"], e30["pm"]["maxdd"], t30, h30, e30["rel"]["s_up"]]
    if not keep:
        return row
    return dict(row=row, sc29=sc29, sc30=sc30, e29=e29, e30=e30, V=Vp)


# ----------------------------------------------------------------------------------------------- thresholds / gates
def critical_value(null_s, alpha=ALPHA):
    return H.critical_value(null_s, alpha)


def empirical_p(null_s, real):
    a = np.asarray(null_s, float)
    return float((1 + int((a >= real).sum())) / (1 + a.size))


def gates_h029(e29, spy, s_up_stress, c_up, p_up):
    rel, rk = e29["rel"], e29["risk"]
    early = sum(rel["U"].get(y, 0.0) for y in EARLY)
    late = sum(rel["U"].get(y, 0.0) for y in LATE)
    mx, tot, share = concentration(rel["U"])
    g = dict(S_UP=rel["s_up"], c_UP=c_up, p=p_up, up_capture=rk["up_capture"], down_capture=rk["down_capture"],
             maxdd=e29["pm"]["maxdd"], spy_maxdd=spy["pm"]["maxdd"], up_2015_2017=early, up_2018_2021=late,
             up_by_year=rel["U"], max_year_share=share, S_UP_stress=s_up_stress)
    g["N1"] = bool(rel["s_up"] > c_up and p_up <= ALPHA)
    g["N2"] = bool(rk["up_capture"] >= 1.0 and rel["s_up"] > 0)
    g["N3"] = bool(early > 0 and late > 0 and tot > 0 and mx <= 0.5 * tot)
    g["N4"] = bool(rk["down_capture"] <= 1.25 and abs(e29["pm"]["maxdd"]) <= 1.5 * abs(spy["pm"]["maxdd"]))
    g["N5"] = bool(s_up_stress > 0)
    g["all"] = all(g[k] for k in ("N1", "N2", "N3", "N4", "N5"))
    g["verdict"] = "H029 UPSIDE SIGNAL CANDIDATE" if g["all"] else "H029 UPSIDE SIGNAL REJECTED"
    return g


def gates_h030(e30, w28, spy, c_inc, p_inc, stress):
    """stress: dict(w30, w28, spy) terminal wealth at 0.20% slippage."""
    rel, rk = e30["rel"], e30["risk"]
    s_inc = math.log(e30["wealth"] / w28)
    mx, tot, share = concentration(rel["A"])
    g = dict(S_INC=s_inc, c_INC=c_inc, p=p_inc, w30=e30["wealth"], w28=w28, w_spy=spy["wealth"],
             up_capture=rk["up_capture"], down_capture=rk["down_capture"], S_UP=rel["s_up"], ex1820=rel["ex1820"],
             all_by_year=rel["A"], max_year_share=share, maxdd=e30["pm"]["maxdd"], spy_maxdd=spy["pm"]["maxdd"],
             vol=e30["pm"]["vol"], spy_vol=spy["pm"]["vol"], stress=stress)
    g["C1"] = bool(s_inc > c_inc and p_inc <= ALPHA)
    g["C2"] = bool(e30["wealth"] > w28 > spy["wealth"] and e30["wealth"] >= 1.05 * w28)
    g["C3"] = bool(rk["up_capture"] >= 1.0 and rel["s_up"] > 0)
    g["C4"] = bool(rk["down_capture"] <= 0.80)
    g["C5"] = bool(rel["ex1820"] > 0 and tot > 0 and mx <= 0.5 * tot)
    g["C6"] = bool(abs(e30["pm"]["maxdd"]) <= 1.25 * abs(spy["pm"]["maxdd"]) and e30["pm"]["vol"] <= 1.25 * spy["pm"]["vol"])
    g["C7"] = bool(stress["w30"] > stress["w28"] and stress["w30"] > stress["spy"])
    g["all"] = all(g[k] for k in ("C1", "C2", "C3", "C4", "C5", "C6", "C7"))
    g["verdict"] = ("H030 DEVELOPMENT CANDIDATE — PRE-REGISTERED H028 + H029 COMBINATION" if g["all"]
                    else "H030 FAILS — FIXED 50/50 COMBINATION DOES NOT QUALIFY")
    return g


# ----------------------------------------------------------------------------------------------- adequacy
def adequacy(rows, real_struct):
    """Spec 9 B / C. rows: null rows (NULL_FIELDS); real_struct: dict(turn29, hhi29, turn30, hhi30) of the real
    selection (scores only). Returns dict with ok flags."""
    a = np.asarray([r[1:] for r in rows], float)
    col = {f: a[:, i] for i, f in enumerate(NULL_FIELDS[1:])}
    out, ok = {}, True
    for k in ("turn29", "hhi29", "turn30", "hhi30"):
        lo, hi = np.percentile(col[k], ADEQ_Q)
        v = real_struct[k]
        good = bool(lo <= v <= hi)
        out[k] = dict(real=v, lo=float(lo), hi=float(hi), median=float(np.median(col[k])), ok=good)
        ok &= good
    for k in ("vol29", "beta29", "up29", "dn29", "vol30", "beta30", "up30", "dn30"):
        x = col[k]
        good = bool(np.all(np.isfinite(x)) and x.std() > 0)
        if k[:-2] in ("beta", "up", "dn"):
            good &= bool(ADEQ_MEDIAN[0] <= float(np.median(x)) <= ADEQ_MEDIAN[1])
        out[k] = dict(median=float(np.median(x)), sd=float(x.std()), ok=good)
        ok &= good
    out["ok"] = bool(ok)
    out["verdict"] = "ADEQUATE" if ok else "STOP — H029/H030 NULL INADEQUATE"
    return out


# ----------------------------------------------------------------------------------------------- synthetic (canary only)
def synthetic_vectors(m29, kind, seed):
    """Six identical columns (so qr_v3.h029_score returns the centred percentile of the one synthetic value):
    'A' = i.i.d. N(0, 1) noise (pure noise within sectors); 'B' = a planted WITHIN-SECTOR upside predictor:
    (r_oo - its FF12-sector mean in the month) x 1[SPY month up] + N(0, SYNTH_B_NOISE^2) (deliberate look-ahead,
    canary only; Amendment 1)."""
    rng = np.random.default_rng(seed)
    out = []
    for m in m29:
        n = len(m["ids"])
        if kind == "A":
            z = rng.normal(0.0, 1.0, n)
        else:
            up = 1.0 if m["spy_oo"] > 0 else 0.0
            r = np.nan_to_num(np.asarray(m["r_oo"], float))
            sec = np.asarray(m["sector"]).astype(np.int64)
            dm = r.copy()
            for g in np.unique(sec):
                k = sec == g
                dm[k] = r[k] - r[k].mean()
            z = dm * up + rng.normal(0.0, SYNTH_B_NOISE, n)
        out.append(np.repeat(z[:, None], 6, axis=1))
    return out
