"""H016 statistical and cost feasibility (P2-CP8), from stated ASSUMPTIONS only. This script reads no project returns,
prices or factor results; it makes the trade-offs in the proposal reproducible.

1. Precision of the gate statistic Sharpe(H) - Sharpe(EW) over T = 12 years (Jobson-Korkie / Memmel variance for
   the difference of two correlated Sharpe ratios, annual units):
       Var = [2(1 - rho) + 0.5 (S1^2 + S2^2 - 2 rho^2 S1 S2)] / T
   and the probability that the estimate clears the +0.25 margin for a given TRUE difference (normal approximation).
2. Idiosyncratic tracking of an N-stock equal-weight selection: sigma_idio / sqrt(N).
3. Costs at $100,000 with $7 per order and 10 bps slippage per side, for a quarterly replacement fraction q of the
   N names (continuing holdings are not resized): orders/year = 2 * N * q * 4; traded notional = 2 * q * 4 * equity.
Output: research/phase2/H016_feasibility.json"""
from __future__ import annotations

import json
import math
from pathlib import Path

T_YEARS = 12.0
MARGIN = 0.25
SR_EW = 0.80          # assumption: a large-cap EW Sharpe of this order (literature/typical; not our data)
SIGMA_IDIO = 0.28     # assumption: annual idiosyncratic volatility of a large-cap US stock
EQUITY, FEE, SLIP = 100_000.0, 7.0, 0.0010


def se_diff(s1, s2, rho, t=T_YEARS):
    return math.sqrt((2 * (1 - rho) + 0.5 * (s1 * s1 + s2 * s2 - 2 * rho * rho * s1 * s2)) / t)


def p_clear(true_diff, rho):
    se = se_diff(SR_EW + true_diff, SR_EW, rho)
    z = (true_diff - MARGIN) / se
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def costs(n, q, equity=EQUITY):
    orders = 2 * n * q * 4
    commission = orders * FEE / equity
    slippage = 2 * q * 4 * 0.98 * SLIP
    return {"orders_per_year": round(orders), "commission_pct": round(100 * commission, 2),
            "slippage_pct": round(100 * slippage, 2), "total_pct": round(100 * (commission + slippage), 2),
            "position_usd": round(0.98 * equity / n)}


def main():
    res = {"assumptions": {"years": T_YEARS, "margin": MARGIN, "sr_ew": SR_EW, "sigma_idio": SIGMA_IDIO,
                           "equity": EQUITY, "fee_per_order": FEE, "slippage_per_side": SLIP}}
    res["se_of_sharpe_difference"] = {f"rho={r}": round(se_diff(SR_EW + 0.25, SR_EW, r), 3) for r in (0.80, 0.85, 0.90, 0.95)}
    res["p_estimate_clears_margin"] = {f"true_diff={d}": {f"rho={r}": round(p_clear(d, r), 2) for r in (0.85, 0.90)}
                                       for d in (0.0, 0.10, 0.20, 0.25, 0.40)}
    res["idiosyncratic_tracking_by_n"] = {n: round(SIGMA_IDIO / math.sqrt(n), 3) for n in (12, 15, 20, 25, 30, 40)}
    res["costs_by_n_and_quarterly_replacement"] = {f"N={n}": {f"q={q}": costs(n, q) for q in (0.15, 0.25, 0.35)}
                                                   for n in (15, 20, 25, 30)}
    res["costs_200k_n20"] = {f"q={q}": costs(20, q, 200_000.0) for q in (0.15, 0.25, 0.35)}
    out = Path(__file__).with_suffix(".json")
    out.write_text(json.dumps(res, indent=1) + "\n")
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
