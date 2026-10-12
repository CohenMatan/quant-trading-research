# qr_h028.py — H028 Fixed Strong Shrinkage Learned Stock Score (owner D217; research/phase13/H028_spec.md, pinned by
# qresearch.p13h028). Pure numpy on top of the FROZEN qr_h026 and qr_h027 (both imported unchanged); the same file is
# unit-tested offline and uploaded to the host S030.
#   * the ONLY scientific change from H027: every outer-year Ridge fit uses lambda = 100 (LAMBDA); there is no inner
#     lambda selection, no lambda comparison and no fallback (run_world_fixed never runs the inner-year loop);
#   * everything else is the frozen H026 / H027 code: Fitter (label availability), the cutoff at each outer year's
#     first review, scores = X @ beta, qr_h026.simulate (Top-15, sector cap, costs), spy_simulate, metrics;
#   * the LOWVOL-conditional null is qr_h027.conditional_permuted unchanged, with lambda = 100 in every world;
#   * `schedule` (canary / equality analysis only) fixes a per-year lambda so that the H027 real assignment
#     (0.01, 100 x 6) reproduces H027 exactly through this code path;
#   * replay(): an exact replica of qr_h026.simulate that also returns the post-rebalance weights and the per-month
#     orders and costs (its wealth must equal simulate's bit for bit);
#   * equality(): the pre-registered 2016-2021 H028-vs-H027 integrity analysis (spec section 6).
import hashlib
import math
import numpy as np

import qr_h026 as H
import qr_h027 as G

LAMBDA = 100.0
assert LAMBDA in H.LAMBDAS                       # a value of the frozen H026 / H027 grid, pre-declared (D217)
EQUAL_YEARS = tuple(y for y in H.OUTER_YEARS if y != H.OUTER_YEARS[0])      # 2016-2021
CAL_SEEDS = tuple(range(1, 101))                 # canary tolerance calibration worlds
TOL_FACTOR = 1.5                                 # tolerance = 1.5 x the largest calibration difference (spec 6)
TOL_FLOOR = dict(ret=0.0025, turnover=0.025)     # ... but never below 0.25 return points / 0.025 turnover
FIELDS = G.FIELDS
DETERMINISM_SEEDS = G.DETERMINISM_SEEDS


def fixed_schedule():
    return {Y: LAMBDA for Y in H.OUTER_YEARS}


# ----------------------------------------------------------------------------------------------- the procedure
def run_world_fixed(months, Xs, capital=H.CAPITAL, k=H.K, slip=H.SLIPPAGE, full=False, seed=None, schedule=None):
    """The H028 procedure on one assignment of feature matrices: for each outer year Y one Ridge fit with lambda =
    schedule[Y] (default LAMBDA = 100 for every year) on every month whose label exits before Y's first review, then
    the frozen scores / Top-15 / costs / SPY comparison. Arithmetic identical to qr_h026.run_world given the lambdas."""
    lam_y = fixed_schedule() if schedule is None else {Y: float(schedule[Y]) for Y in H.OUTER_YEARS}
    fit = H.Fitter(months, Xs)
    years = sorted({m["test_year"] for m in months})
    first = {y: H.year_months(months, y) for y in years}
    coef, ntrain, fits = {}, {}, []
    for Y in H.OUTER_YEARS:
        cut = months[first[Y][0]]["cutoff_day"]
        b0, b, n = fit.fit(cut, lam_y[Y])
        coef[(Y, lam_y[Y])] = (b0, b)
        ntrain[(Y, lam_y[Y])] = n
        fits.append((Y, lam_y[Y]))
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
    rk = G.risk(h["daily"], s["daily"], days, capital)
    beta = {Y: coef[(Y, lam_y[Y])][1] for Y in H.OUTER_YEARS}
    rec = dict(seed=seed, S_WEALTH=sw, wealth=h["wealth"], excess_cagr=hm["cagr"] - smet["cagr"], maxdd=hm["maxdd"],
               vol=hm["vol"], beta=rk["beta"], up_capture=rk["up_capture"], down_capture=rk["down_capture"],
               years_beating=sum(1 for y in H.OUTER_YEARS if yh[y] > ys[y]), years=[yh[y] for y in H.OUTER_YEARS],
               lam=[lam_y[Y] for Y in H.OUTER_YEARS], coef=[beta[Y].tolist() for Y in H.OUTER_YEARS],
               coef_sha=G.coef_sha(beta))
    if not full:
        return rec
    return dict(rec=rec, Xs=Xs, coef=coef, ntrain=ntrain, fits=fits, lam_y=lam_y, idx=idx, scores=sc, days=days, h=h,
                s=s, hm=hm, sm=smet, yh=yh, ys=ys)


def run_fixed_conditional(months, seed, **kw):
    """One LOWVOL-conditional null world (seed >= 1) or, with seed None, the real assignment, at lambda = 100."""
    return run_world_fixed(months, G.conditional_permuted(months, seed), seed=seed, **kw)


def row(rec):
    return G.row(rec)


# ----------------------------------------------------------------------------------------------- exact replay
def replay(months, scores, capital=H.CAPITAL, k=H.K, slip=H.SLIPPAGE, comm=H.COMMISSION, cap=H.SECTOR_CAP):
    """qr_h026.simulate line for line (no daily path), additionally recording per decision month the post-rebalance
    weights {security id: value / equity}, the cash share, the number of orders and the commission / slippage paid.
    Its final wealth must equal simulate's exactly (checked in tests and in-host)."""
    cash, hold = float(capital), {}
    per = []
    last = len(months) - 1
    for m_i, (m, sc) in enumerate(zip(months, scores)):
        tgt = H.pick(m, sc, k, cap)
        pos = {m["ids"][i]: i for i in tgt}
        traded, orders, com, slp = 0.0, 0, 0.0, 0.0
        for sid in [s for s in hold if s not in pos]:
            v = hold.pop(sid)
            cash += v * (1.0 - slip) - comm
            com += comm
            slp += v * slip
            traded += v
            orders += 1
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
                    orders += 1
        tot = cash + sum(hold.values())
        per.append(dict(day=m.get("day"), weights={s: v / tot for s, v in hold.items()}, cash_share=cash / tot,
                        turnover=traded / eq if eq > 0 else 0.0, orders=orders, commission=com, slippage=slp,
                        equity_after=tot))
        idx = np.array([pos[s] for s in hold], dtype=np.int64)
        vals = np.array([hold[s] for s in hold], float)
        if m_i == last:
            end = vals * (1.0 + m["r_oc"][idx])
            alive = m["alive_end"][idx]
            cash += float(end[~alive].sum()) + float((end[alive] * (1.0 - slip)).sum()) - comm * int(alive.sum())
            per[-1]["orders"] += int(alive.sum())
            per[-1]["commission"] += comm * int(alive.sum())
            per[-1]["slippage"] += float(end[alive].sum()) * slip
            hold = {}
        else:
            nv = vals * (1.0 + m["r_oo"][idx])
            alive = m["alive_next"][idx]
            hold = {s: float(v) for s, v, a in zip(list(hold), nv, alive) if a}
            cash += float(nv[~alive].sum())
    return dict(wealth=cash, months=per)


# ----------------------------------------------------------------------------------------------- 2016-2021 integrity
def equality(w8, w7, months):
    """Pre-registered H028-vs-H027 integrity analysis (spec section 6). w8 / w7: full results (run_world_fixed /
    qr_h026.run_world or run_world_fixed with the H027 schedule) on the SAME months and feature matrices.
    EXACT parts (any difference = STOP — UNEXPECTED PIPELINE DIFFERENCE): for every outer year 2016-2021 the lambda
    (100), intercept and 11 coefficients; every decision month's score vector; every month's target list and held
    name set; the number of orders in every month after the transition month. PATH-DEPENDENT parts (reported, bounded
    by the canary-calibrated tolerance): yearly returns, turnover and costs, which differ only because positions
    carried over from December are not resized (frozen mechanics), the $7 commission is fixed in dollars and new
    positions are sized from total equity."""
    ix8, ix7 = w8["idx"], w7["idx"]
    out = dict(same_idx=ix8 == ix7)
    yrs = EQUAL_YEARS
    lam_ok, coef_ok = True, True
    for Y in yrs:
        l8, l7 = w8["lam_y"][Y], w7["lam_y"][Y]
        lam_ok &= (l8 == LAMBDA and l7 == LAMBDA)
        b8, b7 = w8["coef"][(Y, l8)], w7["coef"].get((Y, l7))
        coef_ok &= b7 is not None and b8[0] == b7[0] and np.array_equal(b8[1], b7[1])
    out["lambda_100_both"] = bool(lam_ok)
    out["coefficients_identical"] = bool(coef_ok)
    ms = [months[i] for i in ix8]
    eq_months = [n for n, m in enumerate(ms) if m["test_year"] in yrs]
    out["scores_identical"] = all(np.array_equal(w8["scores"][n], w7["scores"][n]) for n in eq_months)
    out["targets_identical"] = all(H.pick(ms[n], w8["scores"][n]) == H.pick(ms[n], w7["scores"][n])
                                   for n in eq_months)
    p8, p7 = w8["h"].get("picks"), w7["h"].get("picks")
    out["held_sets_identical"] = None if p8 is None or p7 is None else all(p8[n] == p7[n] for n in eq_months)
    r8, r7 = replay(ms, w8["scores"]), replay(ms, w7["scores"])
    out["replay_exact"] = r8["wealth"] == w8["h"]["wealth"] and r7["wealth"] == w7["h"]["wealth"]
    trans = eq_months[0] if eq_months else None
    out["transition_month"] = ms[trans].get("day") if trans is not None else None
    out["orders_identical_after_transition"] = all(r8["months"][n]["orders"] == r7["months"][n]["orders"]
                                                   for n in eq_months if n != trans)
    per_year = {}
    for Y in yrs:
        ns = [n for n in eq_months if ms[n]["test_year"] == Y]
        rest = [n for n in ns if n != trans]
        l1 = [sum(abs(r8["months"][n]["weights"].get(s, 0.0) - r7["months"][n]["weights"].get(s, 0.0))
                  for s in set(r8["months"][n]["weights"]) | set(r7["months"][n]["weights"])) for n in ns]
        per_year[Y] = dict(
            ret_h028=w8["yh"][Y], ret_h027=w7["yh"][Y], ret_diff=w8["yh"][Y] - w7["yh"][Y],
            turnover_h028=float(sum(r8["months"][n]["turnover"] for n in rest)),
            turnover_h027=float(sum(r7["months"][n]["turnover"] for n in rest)),
            cost_h028=float(sum(r8["months"][n]["commission"] + r8["months"][n]["slippage"] for n in ns)),
            cost_h027=float(sum(r7["months"][n]["commission"] + r7["months"][n]["slippage"] for n in ns)),
            orders_h028=int(sum(r8["months"][n]["orders"] for n in ns)),
            orders_h027=int(sum(r7["months"][n]["orders"] for n in ns)),
            weight_l1_max=float(max(l1)) if l1 else 0.0, weight_l1_last=float(l1[-1]) if l1 else 0.0)
        per_year[Y]["turnover_diff"] = per_year[Y]["turnover_h028"] - per_year[Y]["turnover_h027"]
    out["per_year"] = per_year
    out["transition"] = None if trans is None else dict(
        turnover_h028=r8["months"][trans]["turnover"], turnover_h027=r7["months"][trans]["turnover"],
        orders_h028=r8["months"][trans]["orders"], orders_h027=r7["months"][trans]["orders"])
    out["exact_ok"] = bool(out["same_idx"] and lam_ok and coef_ok and out["scores_identical"]
                           and out["targets_identical"] and out["held_sets_identical"] is not False
                           and out["replay_exact"] and out["orders_identical_after_transition"])
    return out


def max_abs_diffs(eqs):
    """Largest |difference| per year 2016-2021 of yearly return and of turnover (ex transition) over equality()
    results (the canary calibration)."""
    return {str(Y): dict(ret=max(abs(e["per_year"][Y]["ret_diff"]) for e in eqs),
                         turnover=max(abs(e["per_year"][Y]["turnover_diff"]) for e in eqs)) for Y in EQUAL_YEARS}


def tolerance(cal):
    """Spec section 6: tolerance per year = max(TOL_FACTOR x the largest calibration difference, TOL_FLOOR)."""
    return {Y: {q: max(TOL_FACTOR * v[q], TOL_FLOOR[q]) for q in ("ret", "turnover")} for Y, v in cal.items()}


def within_tolerance(eqr, tol):
    bad = []
    for Y in EQUAL_YEARS:
        py, t = eqr["per_year"][Y], tol[str(Y)]
        if abs(py["ret_diff"]) > t["ret"] or abs(py["turnover_diff"]) > t["turnover"]:
            bad.append(Y)
    return dict(ok=not bad, exceeded=bad)


def schedule_h027(lam_list):
    return {Y: float(l) for Y, l in zip(H.OUTER_YEARS, lam_list)}


def tol_sha(tol):
    return hashlib.sha256(repr(sorted((k, sorted(v.items())) for k, v in tol.items())).encode()).hexdigest()
