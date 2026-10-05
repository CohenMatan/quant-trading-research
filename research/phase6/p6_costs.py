"""Phase 6 mechanical design arithmetic (P6-CP1): effective cross-sectional sample, per-date IC noise, tracking error
of a top-k sector book vs the equal-weight sector average, membership turnover and cost drag at $100K / $200K with
$7 per order and 10 bps slippage per side. SYNTHETIC model of p6_power.py only; no real sector data.

  python research/phase6/p6_costs.py   -> research/phase6/p6_costs_result.json
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p6_power as PW  # noqa: E402
import p6_xs as P  # noqa: E402

N = 9


def model_cov():
    beta = np.linspace(0.6, 1.3, N)
    load = np.linspace(-1.0, 1.0, N)
    idio = np.linspace(0.025, 0.05, N)
    return 0.043 ** 2 * np.outer(beta, beta) + 0.02 ** 2 * np.outer(load, load) + np.diag(idio ** 2)


def main():
    out = {}
    S = model_cov()
    M = np.eye(N) - np.ones((N, N)) / N                     # cross-sectional demeaning
    Sr = M @ S @ M
    ev = np.clip(np.linalg.eigvalsh(Sr), 0, None)
    out["effective_cross_sectional_n"] = float(ev.sum() ** 2 / (ev ** 2).sum())    # participation ratio
    out["n_minus_1"] = N - 1
    out["relative_return_sd_monthly"] = float(np.sqrt(np.diag(Sr)).mean())
    # per-date IC noise under the null (synthetic, no edge) and IC autocorrelation
    R = PW.make_panel(2000, N, seed=5)
    s6 = P.signal(R, 6)
    ts = np.arange(5, R.shape[0] - 1)
    Y = R[ts + 1] - R[ts + 1].mean(axis=1, keepdims=True)
    ic = P.spearman_rows(s6[ts], Y)
    out["null_ic_sd_per_date"] = float(ic.std())
    out["iid_ic_sd_theory_1_over_sqrt_n_minus_1"] = float(1 / np.sqrt(N - 1))
    out["null_ic_autocorr_lag1"] = float(np.corrcoef(ic[1:], ic[:-1])[0, 1])
    # tracking error of an EQUAL-WEIGHT top-k book vs the equal-weight 9-sector average (random membership bound)
    te = {}
    for k in (1, 2, 3, 4):
        sims = []
        rng = np.random.default_rng(k)
        for _ in range(4000):
            w = np.zeros(N)
            w[rng.choice(N, k, replace=False)] = 1.0 / k
            d = w - np.ones(N) / N
            sims.append(d @ S @ d)
        te[k] = float(np.sqrt(np.mean(sims)) * np.sqrt(12))
    out["tracking_error_vs_ew_sectors_ann"] = te
    # turnover and costs: replacements of top-k members per month (6-month signal, synthetic persistence)
    costs = {}
    for k in (1, 2, 3, 4):
        repl = PW.turnover(N, 6, k, 0.006, T=1200)
        for cap in (100_000, 200_000):
            pos = cap / k
            per_repl = 2 * 7.0 + 2 * pos * 0.001                  # one sell + one buy order; 10 bps each side
            yearly = repl * 12 * per_repl
            costs[f"k{k}_{cap // 1000}K"] = dict(replacements_per_month=round(repl, 3),
                                                 orders_per_year=round(repl * 24, 1),
                                                 cost_usd_per_year=round(yearly, 0),
                                                 cost_pct_per_year=round(100 * yearly / cap, 3))
    out["costs_6m_signal"] = costs
    out["note"] = ("Costs exclude rebalancing back to equal weight between replacements (optional; with k ETFs and "
                   "a 5% band it adds a few orders a year) and the SPY benchmark difference (cap-weighted vs equal-"
                   "weight sectors).")
    (HERE / "p6_costs_result.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
