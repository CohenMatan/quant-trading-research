"""Phase 2 feasibility, before any Phase 2 backtest: costs vs holding period, DSR hurdles under the
trial-count options, and the statistical power of the key paired comparison (strategy vs trend-only
control). Analytic formulas plus one empirical cost anchor from an existing, committed pre-Phase-2 run
(E962-22: no-skill random portfolio, 15 slots, hold 60, $100K, IS 2010-2017). No market data is read
beyond that anchor; no Validation, Walk-Forward or Holdout data is used.

    PYTHONPATH=src python research/phase2/P2_feasibility.py -> research/phase2/P2_feasibility.json
"""
import json
import math
import sys
from pathlib import Path

from scipy.stats import norm

sys.path.insert(0, "src")
from qresearch import stats  # noqa: E402

COMMISSION, SLIP = 7.0, 0.0010          # $ per order; per side (D039, D024)
VAR_SR = 0.0009463432771146249          # programme-1 dispersion of daily Sharpe (40 candidates, frozen at CP3j)
T_IS_VAL = 3019                         # daily returns over IS + VAL


def annual_costs(slots, hold, equity=100_000, invested=0.85):
    """Round trips per year = slots x filled share x 252/hold; each round trip = 2 orders and 2 x position
    notional traded. Returns commission and slippage drag as fractions of equity."""
    rt = slots * invested * 252 / hold
    commission = 2 * rt * COMMISSION / equity
    slippage = SLIP * 2 * invested * 252 / hold
    return dict(round_trips=rt, orders=2 * rt, commission=commission, slippage=slippage, total=commission + slippage)


def dsr_hurdle(n):
    e = stats.expected_max_sharpe(n, VAR_SR)
    return dict(n=n, sr_star_annual=e * math.sqrt(252),
                observed_sharpe_needed_is_val=(e + norm.ppf(0.90) / math.sqrt(T_IS_VAL - 1)) * math.sqrt(252))


def paired_power(delta, rho, years, alpha=0.05):
    """Power of a one-sided test of Sharpe(A) - Sharpe(B) > 0 for two books with return correlation rho
    (Jobson-Korkie/Memmel approximation, equal volatility, small daily Sharpe): se ~ sqrt(2(1-rho)/years)."""
    se = math.sqrt(2 * (1 - rho) / years)
    return dict(delta=delta, rho=rho, years=years, se=se, power=float(1 - norm.cdf(norm.ppf(1 - alpha) - delta / se)))


def main():
    anchor = json.loads(Path("experiments/E962-22/result.json").read_text())
    out = dict(
        assumptions=dict(commission_per_order=COMMISSION, slippage_per_side=SLIP, equity=100_000,
                         invested_share=0.85, note="0.85 = the invested share measured for the hold-60 random null"),
        cost_model={f"slots={s},hold={h}": annual_costs(s, h) for s in (10, 12, 15) for h in (20, 40, 60, 80, 120)},
        cost_model_200k={f"slots={s},hold={h}": annual_costs(s, h, equity=200_000) for s in (12,) for h in (40, 60, 80)},
        empirical_anchor=dict(experiment="E962-22", description="random picks, 15 slots, hold 60, $100K, IS",
                              harness_orders=anchor["harness_summary"]["orders"], note="measured drag: see C03_results.json nulls"),
        dsr_hurdles=[dsr_hurdle(n) for n in (2, 4, 8, 14, 20, 42, 45, 60)],
        paired_power=[paired_power(d, r, y) for y in (8, 12) for r in (0.7, 0.8, 0.9) for d in (0.1, 0.2, 0.3)],
    )
    c03 = json.loads(Path("research/cycles/C03_results.json").read_text())["h013"]["nulls"]["1"]["costs"]
    out["empirical_anchor"].update(measured_commission_drag=c03["commission_drag_pa"], measured_slippage_drag=c03["slippage_drag_pa"],
                                   model_prediction=annual_costs(15, 60))
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    for k, v in out["cost_model"].items():
        print(k, {x: round(y, 4) for x, y in v.items()})
    print("anchor", out["empirical_anchor"])
    for d in out["dsr_hurdles"]:
        print(d)
    for p in out["paired_power"]:
        print({k: round(v, 3) for k, v in p.items()})


if __name__ == "__main__":
    main()
