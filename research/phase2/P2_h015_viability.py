"""H015 viability review (owner request "Reassess H015 Before Spending Hypothesis Slot 2", 2026-10-01).
No backtest. Inputs: committed, already-observed 2010-2021 outputs (EW/SPY benchmarks, H014 control books via
P2_h015_feasibility.json) and simulations. Nothing here chooses an H015 rule.

1. Predictability of H015's development result from what is already observed: H015 and H014's random-uptrend
   books share the same 2010-2021 path; they differ by a design shift (monthly SMA200-only vs daily
   MA200+MA50 with roll/cap; 15 vs 12 slots) and by independent seed draws.
2. P(H015 passes the +0.25 margin) under each seed methodology, conditional on the observed books.
3. Diversification: tracking error and EW-explained variance of the observed 12-stock random-uptrend books.

    PYTHONPATH=src python research/phase2/P2_h015_viability.py -> research/phase2/P2_h015_viability.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from qresearch import p2spec, results  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
MARGIN = 0.25
SEED = 20261002
N = 400_000
R_BOOKS = ["E014-05", "E014-06", "E014-07", "E014-10", "E014-11", "E014-12"]


def ret(eid):
    return p2spec.returns(p2spec.equity_series(results.read_csv_gz(EXP / eid / "equity.csv.gz")))


def main():
    feas = json.loads((ROOT / "research/phase2/P2_h015_feasibility.json").read_text())
    seed12 = feas["seed_noise"]["pooled_sd_12_slots"]
    seed15 = feas["seed_noise"]["approx_sd_15_slots"]
    pop = feas["tracking"]["se_sharpe_diff_population"]
    d_obs = [feas["books"][f"R exit {x} seed {s}"]["d_ew"] for x in "AB" for s in (1, 2, 3)]
    mean_obs = float(np.mean(d_obs))
    out = dict(observed_random_uptrend_d_ew=d_obs, observed_mean=mean_obs, observed_median=float(np.median(d_obs)),
               seed_sd_12=seed12, seed_sd_15=seed15, population_noise_sd=pop)

    # ---- 3. diversification of the observed 12-stock books
    r_ew = ret("E901-07")
    div = {}
    for eid in R_BOOKS:
        j = pd.concat([ret(eid), r_ew], axis=1, join="inner").to_numpy()
        te = float(np.std(j[:, 0] - j[:, 1], ddof=1) * math.sqrt(252))
        rho = float(np.corrcoef(j[:, 0], j[:, 1])[0, 1])
        div[eid] = dict(tracking_error_pa=te, corr_with_ew=rho, ew_explained_variance=rho ** 2,
                        vol_pa=float(np.std(j[:, 0], ddof=1) * math.sqrt(252)))
    out["diversification_12_stock_books"] = div
    out["diversification_summary"] = {k: float(np.mean([v[k] for v in div.values()]))
                                      for k in ("tracking_error_pa", "corr_with_ew", "ew_explained_variance", "vol_pa")}

    # ---- 1-2. conditional prediction of H015's development result
    # Shared 2010-2021 path => H015's population component = R's realised population component + design shift.
    # Estimate of R's realised population component: mean of the 6 observed books (seed noise sd seed12/sqrt(6)).
    # H015 result for seed k = mean_obs - e_R + delta + s_k, e_R ~ N(0, seed12^2/6), delta ~ N(0, sd_delta^2),
    # s_k ~ N(0, seed15^2) independent across H015 seeds.
    rng = np.random.default_rng(SEED)
    scen = {}
    for sd_delta in (0.05, 0.10, 0.15, 0.20):
        center = mean_obs - rng.normal(0, seed12 / math.sqrt(6), N) + rng.normal(0, sd_delta, N)
        s = rng.normal(0, seed15, (N, 5))
        books = center[:, None] + s                       # per-seed Sharpe difference vs EW (15-stock books)
        # composite of averaged returns: its Sharpe exceeds the mean of per-seed Sharpes by a diversification
        # gain; approximated here as the population component plus residual seed noise / sqrt(5)
        composite = center + rng.normal(0, seed15 / math.sqrt(5), N)
        scen[f"sd_delta={sd_delta}"] = dict(
            predicted_mean=float(center.mean()), predicted_sd_single_book=float(books[:, 0].std()),
            p_pass_one_frozen_seed=float((books[:, 0] >= MARGIN).mean()),
            p_pass_mean_of_per_seed_sharpes=float((books.mean(axis=1) >= MARGIN).mean()),
            p_pass_composite_returns=float((composite >= MARGIN).mean()),
            p_pass_at_least_4_of_5=float(((books >= MARGIN).sum(axis=1) >= 4).mean()),
            p_pass_all_5=float((books >= MARGIN).all(axis=1).mean()),
            # variance of a fresh single-book result: pop^2 + delta^2 + seed15^2; given the observed books only
            # seed12^2/6 + delta^2 + seed15^2 remains. Seed noise is luck, not information, so the second share
            # excludes it: how much of the systematic (population + design) uncertainty is already resolved.
            share_of_single_book_variance_already_known=float(
                1 - (sd_delta ** 2 + seed12 ** 2 / 6 + seed15 ** 2) / (pop ** 2 + sd_delta ** 2 + seed15 ** 2)),
            share_of_systematic_variance_already_known=float(
                1 - (sd_delta ** 2 + seed12 ** 2 / 6) / (pop ** 2 + sd_delta ** 2)))
    out["conditional_prediction"] = scen
    out["design_shift_yardsticks"] = dict(
        note="How much mechanics changes moved the Sharpe difference vs EW in observed books (same period)",
        R_exitB_minus_exitA_mean_of_seeds=float(np.mean(d_obs[3:]) - np.mean(d_obs[:3])),
        H014_B_minus_A=0.721385 - 0.642167,
        C2_B_minus_A=0.619360 - 0.605775,
        C1_B_minus_A=0.380459 - 0.589210)
    # unconditional (ignoring observed books): what a fresh test would look like with prior true edge unknown
    out["unconditional_power_reference"] = feas["power_g1_margin_0.25"]["decision_rules_5_seeds_simulated"]
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(dict(observed_mean=mean_obs, diversification=out["diversification_summary"],
                          yardsticks=out["design_shift_yardsticks"], prediction=scen), indent=1))


if __name__ == "__main__":
    main()
