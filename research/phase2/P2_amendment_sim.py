"""Phase 2 methodology amendment (owner request "Approve Revised Methodology With Three Required
Adjustments", 2026-09-30): simulations only. No H014 result, no Holdout data.

Part A - hypothesis-budget schedules. Hypotheses are screened ONE AT A TIME (the realistic process): the
first hypothesis whose best candidate clears its development margin is frozen and consumes the Holdout;
it is accepted if its Holdout Sharpe difference vs EW is >= +0.10. At most 3 hypotheses. Same normal model
as P2_methodology_sim.py (se = sqrt(2(1-rho)/years), rho 0.76 calibrated on committed IS books; 2
candidates per hypothesis with error correlation 0.8; development 12 years, Holdout 4.67 years).
Schedules compared: fixed 0.20; 0.20/0.25/0.30; 0.20/0.30/0.40; an "equal error budget" schedule
(each later hypothesis gets the development false-pass probability p1/k, Bonferroni-style); fixed 0.25;
fixed 0.30.

Part B - G1 return-risk rule. 12-year daily paths from the two-state regime market of the C03 power
study (calm 12% / turbulent 35% vol, turbulent drift -30%/yr, t(6) shocks; EW Sharpe about 0.9 with
realistic crash drawdowns). Candidate = a x market + independent noise with correlation 0.76 to EW, total
volatility beta x EW's, drift set so its TRUE Sharpe = EW's + delta. beta 1.0 (same risk), 0.7 (lower
exposure), 1.3 (higher risk). Rules: the old G1 (drawdown no deeper than EW) vs the revised G1.

    PYTHONPATH=src python research/phase2/P2_amendment_sim.py -> research/phase2/P2_amendment_sim.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import multivariate_normal

sys.path.insert(0, "src")
sys.path.insert(0, "research/cycles")

RHO, DEV_Y, HOLD_Y, M_HOLD = 0.76, 12.0, 4.67, 0.10
REPS = 400_000
SEED = 20261003
ANN = math.sqrt(252)


def se(years, rho):
    return math.sqrt(2 * (1 - rho) / years)


def p_dev_pass_null(m, rho):
    """P(max of 2 correlated (0.8) candidates' development dSR >= m | no edge)."""
    s = se(DEV_Y, rho)
    cov = [[1, 0.8], [0.8, 1]]
    return float(1 - multivariate_normal(mean=[0, 0], cov=cov).cdf([m / s, m / s]))


def margin_for(p, rho):
    lo, hi = 0.0, 1.5
    for _ in range(60):
        mid = (lo + hi) / 2
        if p_dev_pass_null(mid, rho) > p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def schedules(rho):
    p1 = p_dev_pass_null(0.20, rho)
    return {"fixed 0.20": [0.20, 0.20, 0.20], "0.20/0.25/0.30": [0.20, 0.25, 0.30],
            "0.20/0.30/0.40": [0.20, 0.30, 0.40],
            "equal error budget (p1/k)": [round(margin_for(p1 / k, rho), 3) for k in (1, 2, 3)],
            "fixed 0.25": [0.25, 0.25, 0.25], "fixed 0.30": [0.30, 0.30, 0.30]}


def sequential(rng, deltas, margins, rho, reps=REPS):
    """Screen hypotheses in order; the first to clear its margin goes to the Holdout (used once)."""
    k = len(deltas)
    deltas = np.asarray(deltas, float)
    z = rng.standard_normal((reps, k, 2))
    z[:, :, 1] = 0.8 * z[:, :, 0] + 0.6 * z[:, :, 1]
    dev = (deltas[None, :, None] + se(DEV_Y, rho) * z).max(axis=2)
    passed = dev >= np.asarray(margins[:k])[None, :]
    first = np.where(passed.any(axis=1), passed.argmax(axis=1), -1)
    reached = first >= 0
    true_first = np.where(reached, deltas[np.clip(first, 0, k - 1)], 0.0)
    hold = true_first + se(HOLD_Y, rho) * rng.standard_normal(reps)
    acc = reached & (hold >= M_HOLD)
    return dict(reach=float(reached.mean()), accept=float(acc.mean()),
                accept_real=float((acc & (true_first > 0)).mean()), accept_null=float((acc & (true_first <= 0)).mean()))


def part_a(rng):
    out = {}
    for rho in (0.70, 0.76, 0.85):
        sch = schedules(rho)
        res = {}
        for name, m in sch.items():
            r = dict(margins=m, dev_false_pass_per_hypothesis=[round(p_dev_pass_null(x, rho), 4) for x in m])
            for k in (1, 2, 3):
                r[f"false_accept_all_null_K{k}"] = sequential(rng, [0.0] * k, m, rho)["accept"]
            for d in (0.3, 0.5):
                for pos in (0, 1, 2):
                    deltas = [0.0, 0.0, 0.0]
                    deltas[pos] = d
                    s = sequential(rng, deltas, m, rho)
                    r[f"real_{d}_as_hypothesis_{pos + 1}"] = dict(accept_real=s["accept_real"], accept_null_instead=s["accept_null"])
            res[name] = r
        out[f"rho={rho}"] = res
        print(rho, json.dumps({n: {k: v for k, v in x.items() if k.startswith("false") or k == "margins"} for n, x in res.items()}))
    return out


# ---------------------------------------------------------------- Part B: G1 return-risk rule
def cagr(r):
    return float(np.prod(1 + r) ** (252 / len(r)) - 1)


def mdd(r):
    e = np.cumprod(1 + r)
    return float((e / np.maximum.accumulate(e) - 1).min())


def sharpe(r):
    return float(r.mean() / r.std(ddof=1) * ANN)


def g1_rules(rc, re, m=0.20):
    dsr = sharpe(rc) - sharpe(re)
    c_c, c_e, d_c, d_e = cagr(rc), cagr(re), mdd(rc), mdd(re)
    old = dsr >= m and c_c >= c_e - 0.02 and d_c >= d_e
    calmar_ok = (c_c / abs(d_c)) >= (c_e / abs(d_e))
    new = dsr >= m and c_c >= c_e - 0.02 and calmar_ok and d_c >= d_e - 0.05
    return dict(sharpe_only=dsr >= m, old=old, new=new, dd_worse=d_c < d_e, dd_much_worse=d_c < d_e - 0.10)


def part_b(rng, reps=1500):
    from C03_h012_power_study import regime_market
    long = regime_market(np.random.default_rng(1), 400_000, -0.30)
    mu_m, sd_m = long.mean(), long.std()
    sr_m = mu_m / sd_m
    out = dict(market_true_sharpe_annual=sr_m * ANN)
    n = 12 * 252
    for beta in (1.0, 0.7, 1.3):
        for d in (0.0, 0.2, 0.3, 0.5):
            a = beta * RHO
            sd_e = a * sd_m * math.sqrt(1 - RHO ** 2) / RHO
            sd_c = beta * sd_m
            mu_c = (sr_m + d / ANN) * sd_c
            tallies = dict(sharpe_only=0, old=0, new=0, dd_worse=0, dd_much_worse=0)
            for _ in range(reps):
                m = regime_market(rng, n, -0.30)
                rc = a * (m - mu_m) + sd_e * rng.standard_normal(n) + mu_c
                for k, v in g1_rules(rc, m).items():
                    tallies[k] += v
            out[f"beta={beta},delta={d}"] = {k: v / reps for k, v in tallies.items()}
            print(beta, d, out[f"beta={beta},delta={d}"])
    return out


def main():
    rng = np.random.default_rng(SEED)
    out = dict(assumptions=dict(rho_base=RHO, dev_years=DEV_Y, holdout_years=HOLD_Y, holdout_margin=M_HOLD, reps=REPS,
                                seed=SEED, process="sequential: first hypothesis to clear its margin consumes the Holdout",
                                note="development gates G2-G4 not modelled: false acceptance figures are upper bounds"),
               part_a_schedules=part_a(rng), part_b_g1=part_b(rng))
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
