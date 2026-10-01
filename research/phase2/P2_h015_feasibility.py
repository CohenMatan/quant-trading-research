"""H015 statistical feasibility, BEFORE any H015 backtest (owner request "Close H014 and Design H015",
2026-10-01). Reads only committed 2010-2021 development outputs that already exist and were already seen:
the EW and SPY benchmarks (E901-07, E900-07) and the H014 control books (E014-03..12). No new backtest, no
Validation/Holdout data. These books are NOT used to choose any H015 rule; they are used to (1) disclose how
much of a candidate H015 design is already observed, and (2) estimate turnover, costs, tracking correlation
with EW and seed (selection) noise, which determine statistical power.

    PYTHONPATH=src python research/phase2/P2_h015_feasibility.py -> research/phase2/P2_h015_feasibility.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, "src")
sys.path.insert(0, "research/phase2")
from qresearch import metrics, p2spec, results  # noqa: E402
from P2_feasibility import annual_costs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
YEARS = 12.0
MARGIN = 0.25
BOOKS = {"R exit A seed 1": "E014-05", "R exit A seed 2": "E014-06", "R exit A seed 3": "E014-07",
         "R exit B seed 1": "E014-10", "R exit B seed 2": "E014-11", "R exit B seed 3": "E014-12",
         "C1 exit A (momentum-ranked)": "E014-03", "C1 exit B (momentum-ranked)": "E014-08"}


def eq(eid):
    return p2spec.equity_series(results.read_csv_gz(EXP / eid / "equity.csv.gz"))


def main():
    ew, spy = eq("E901-07"), eq("E900-07")
    r_ew, r_spy = p2spec.returns(ew), p2spec.returns(spy)
    s_ew, s_spy = p2spec.sharpe(r_ew), p2spec.sharpe(r_spy)
    p2 = json.loads((ROOT / "research/phase2/P2_results.json").read_text())["books"]
    out = dict(note="Already-observed H014 control books (2010-2021, 12 slots, $100K). Disclosure and noise "
                    "estimates only; not used to choose H015 rules.",
               ew_sharpe=s_ew, spy_sharpe=s_spy, books={})
    for name, eid in BOOKS.items():
        e = eq(eid)
        r = p2spec.returns(e)
        m = pd.concat([r, r_ew], axis=1, join="inner").to_numpy()
        j = np.corrcoef(m[:, 0], m[:, 1])[0, 1]
        b = p2[eid]
        out["books"][name] = dict(exp=eid, sharpe=p2spec.sharpe(r), d_ew=p2spec.sharpe(r) - s_ew,
                                  d_spy=p2spec.sharpe(r) - s_spy, cagr=metrics.cagr(e), max_dd=metrics.max_drawdown(e),
                                  corr_with_ew=float(j), cost_pa=b["costs"]["total_pa"], turnover_pa=b["costs"]["turnover_pa"],
                                  mean_hold_sessions=b["holding_sessions"]["mean"], trades=b["trades"]["n_trades"])
    # seed (selection) noise: dispersion of Sharpe across the 3 seeds of the same mechanics
    seed_sd = {}
    for ex in ("A", "B"):
        v = [out["books"][f"R exit {ex} seed {s}"]["sharpe"] for s in (1, 2, 3)]
        seed_sd[ex] = float(np.std(v, ddof=1))
    pooled_12 = math.sqrt(np.mean([x ** 2 for x in seed_sd.values()]))
    seed_15 = pooled_12 * math.sqrt(12 / 15)          # idiosyncratic noise ~ 1/sqrt(positions)
    out["seed_noise"] = dict(sd_by_exit_12_slots=seed_sd, pooled_sd_12_slots=pooled_12, approx_sd_15_slots=seed_15,
                             note="3 seeds per exit: a rough estimate (sd of 3 values is itself very uncertain)")
    # market (sampling) noise of the Sharpe difference vs EW over 12 years, from the tracking correlation
    rho = float(np.mean([out["books"][f"R exit {x} seed {s}"]["corr_with_ew"] for x in "AB" for s in (1, 2, 3)]))
    se_single_12 = math.sqrt(2 * (1 - rho) / YEARS)       # a 12-slot book vs EW: includes its own seed noise
    se_market = math.sqrt(max(se_single_12 ** 2 - pooled_12 ** 2, 0.0))   # population-level part (no seed noise)
    out["tracking"] = dict(mean_corr_random_uptrend_vs_ew=rho, se_sharpe_diff_single_12_slot_book=se_single_12,
                           se_sharpe_diff_population=se_market,
                           note="se of a single book from its tracking correlation already contains seed noise; "
                                "the population part is what remains after removing the seed variance")
    # power: P(observed difference >= +0.25) for a single seed and for a seed-averaged decision
    power = {}
    for label, sd_seed in (("single 15-slot book", seed_15), ("mean of 5 seeds", seed_15 / math.sqrt(5)),
                           ("full trend population (no seed noise)", 0.0)):
        se = math.sqrt(se_market ** 2 + sd_seed ** 2)
        power[label] = dict(se_total=se, **{f"true_edge_{d:+.2f}": float(1 - norm.cdf((MARGIN - d) / se))
                                            for d in (0.0, 0.10, 0.25, 0.40, 0.50)})
    # decision rules across 5 seeds: shared market noise m, independent seed noise s_k (simulation, fixed seed)
    rng = np.random.default_rng(20261001)
    m = rng.normal(0, se_market, 200_000)[:, None]
    sk = rng.normal(0, seed_15, (200_000, 5))
    rules = {}
    for d in (0.0, 0.10, 0.25, 0.40, 0.50):
        obs = d + m + sk
        rules[f"true_edge_{d:+.2f}"] = dict(composite_mean=float((obs.mean(axis=1) >= MARGIN).mean()),
                                            all_5_seeds=float((obs >= MARGIN).all(axis=1).mean()),
                                            at_least_4_of_5=float(((obs >= MARGIN).sum(axis=1) >= 4).mean()))
    power["decision_rules_5_seeds_simulated"] = rules
    out["power_g1_margin_0.25"] = power
    # costs for 15 slots at plausible average holds (analytic model, P2_feasibility.py; conservative vs measured)
    out["cost_model_15_slots"] = {f"hold_{h}": {k: v for k, v in annual_costs(15, h, invested=0.93).items()}
                                  for h in (60, 100, 150, 200, 250)}
    out["cost_model_check"] = dict(model_12_slots_hold_103=annual_costs(12, 103, invested=0.94)["total"],
                                   measured_R_exit_A_mean=float(np.mean([out["books"][f"R exit A seed {s}"]["cost_pa"]
                                                                         for s in (1, 2, 3)])))
    # independent decisions
    out["decisions"] = {f"hold_{h}": dict(entries_per_year=15 * 0.93 * 252 / h, entries_12y=15 * 0.93 * 252 / h * YEARS)
                        for h in (100, 150, 200)}
    out["decisions"]["monthly_review_dates_12y"] = 144
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("seed_noise", "tracking", "power_g1_margin_0.25", "cost_model_check")}, indent=1))
    for k, v in out["books"].items():
        print(k, {a: round(b, 3) if isinstance(b, float) else b for a, b in v.items()})


if __name__ == "__main__":
    main()
