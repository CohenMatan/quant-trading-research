"""Phase 2 opportunity review support (2026-10-01): how large a TRUE Sharpe edge over EW any long-only stock-
selection strategy needs, at a given position count, to pass the fixed +0.25 development margin with 80% power
on 12 years. No market data and no backtest: inputs are the committed noise estimates in
research/phase2/P2_h015_feasibility.json (from already-observed 12-stock books).

Model: Sharpe-difference noise = population part (strategy-specific tracking vs EW, assumed equal to the
observed population part) + selection noise that scales with 1/sqrt(positions) (12-stock pooled seed sd).

    PYTHONPATH=src python research/phase2/P2_opportunity_power.py -> research/phase2/P2_opportunity_power.json
"""
import json
import math
from pathlib import Path

from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
MARGIN, POWER = 0.25, 0.80


def main():
    f = json.loads((ROOT / "research/phase2/P2_h015_feasibility.json").read_text())
    seed12 = f["seed_noise"]["pooled_sd_12_slots"]
    pop = f["tracking"]["se_sharpe_diff_population"]
    z = norm.ppf(POWER)
    out = dict(margin=MARGIN, power=POWER, seed_sd_12=seed12, population_se=pop, by_positions={})
    for n in (12, 15, 19, 30, 50):
        seed = seed12 * math.sqrt(12 / n)
        for label, p in (("population se as observed", pop), ("population se halved", pop / 2)):
            se = math.sqrt(p ** 2 + seed ** 2)
            out["by_positions"].setdefault(str(n), {})[label] = dict(
                selection_sd=seed, se_total=se, required_true_edge=MARGIN + z * se,
                false_pass_no_edge=float(1 - norm.cdf(MARGIN / se)))
    out["note"] = ("19 positions is the most the $5,000 minimum allows at $100K (98% invested); 30-50 positions "
                   "need >= $150K-$250K. 'Population se halved' illustrates a strategy that tracks EW more closely "
                   "than the observed random-uptrend books (e.g. a broad, diversified factor tilt).")
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    for n, v in out["by_positions"].items():
        print(n, {k: round(x["required_true_edge"], 2) for k, x in v.items()},
              {k: round(x["false_pass_no_edge"], 3) for k, x in v.items()})


if __name__ == "__main__":
    main()
