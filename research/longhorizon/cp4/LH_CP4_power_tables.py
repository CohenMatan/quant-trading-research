"""LH-CP4 (owner D245): analytical power / MDE tables under EXPLICITLY ASSUMED parameter ranges. No data, no returns,
no simulation, no Monte Carlo. Structural counts come from LH_CP4_population.json (metadata aggregates); the only
other inputs are labelled assumptions and committed results of earlier synthetic studies used as cross-references
(P7-CP4 / P7-CP5f), never re-estimated here.

    PYTHONPATH=src python research/longhorizon/cp4/LH_CP4_power_tables.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import lh_cp4_power as P

HERE = Path(__file__).parent
OUT = HERE / "LH_CP4_power.json"

# ---------------------------------------------------------------- ASSUMPTIONS (labelled; none estimated from returns)
SIGMA_IC = {"optimistic": 0.06, "main": 0.09, "pessimistic": 0.12}   # P7-CP4 synthetic noise scenarios (assumed there)
RHO = (0.0, 0.1, 0.2, 0.3)                                            # AR(1) of the monthly statistic (assumed)
SIGMA_CS = (0.05, 0.065, 0.08)                                        # monthly cross-sectional return sd (assumed)
TESTS = [("5%, 1 hypothesis", 0.05, 1), ("5%, 2 hypotheses", 0.05, 2), ("1%, 1 hypothesis", 0.01, 1),
         ("1%, 2 hypotheses", 0.01, 2)]
EFFECTS = (0.02, 0.03, 0.05)                                          # illustrative top-quintile excess / yr
# committed cross-reference (P7-CP4 main scenario, 83 months, sigma_IC ~0.09, c_IC 2.50): 50% power at IC 0.033
P7_T, P7_SIGMA, P7_C, P7_IC50, P7_IC80 = 83, 0.09, 2.50, 0.033, 0.047


def main():
    pop = json.loads((HERE / "LH_CP4_population.json").read_text())
    T = pop["review_months"]
    N = pop["C1_per_month"]["mean"]
    f = pop["new_quarter_share_all_c1"]
    seasons = 4 * 7                                                    # Feb / May / Aug / Nov reviews 2015-2021
    out = dict(kind="LH-CP4 analytical power tables (assumption-driven; no data, no returns, no simulation)",
               decision="D245", T_monthly=T, N_mean_c1=N, fresh_share=f, earnings_season_months=seasons,
               assumptions=dict(sigma_ic=SIGMA_IC, rho=RHO, sigma_cs=SIGMA_CS,
                                note="ranges, not estimates; sigma_ic scenarios as assumed in P7-CP4"))
    # sampling-only floor of sigma_IC (independent returns): 1 / sqrt(N - 1)
    out["sigma_ic_sampling_floor"] = round(1 / math.sqrt(N - 1), 4)
    # realistic-structure inflation factor implied by the committed P7-CP4 synthetic result
    ic50_analytic = P7_C * P7_SIGMA / math.sqrt(P7_T)
    infl = P7_IC50 / ic50_analytic
    out["p7cp4_inflation_factor"] = dict(analytic_ic50=round(ic50_analytic, 4), synthetic_ic50=P7_IC50,
                                         factor=round(infl, 3),
                                         note="committed synthetic result / naive analytic at the same T, sigma, c")
    # ---- MDE (80% power) in IC units, designs x sigma x rho x test
    designs = {"D1 monthly full cross-section, 1-month horizon": lambda rho: P.t_eff_ar1(T, rho),
               "D2 monthly, 3-month overlapping horizon": lambda rho: P.t_eff_ar1(P.t_eff_overlap(T, 3), rho),
               "D3 earnings-season cross-sections only": lambda rho: P.t_eff_ar1(seasons, rho)}
    mdes = {}
    for dname, teff in designs.items():
        for sname, sig in SIGMA_IC.items():
            for rho in RHO:
                for tname, a, m in TESTS:
                    te = teff(rho)
                    mdes[f"{dname} | sigma_ic {sname} {sig} | rho {rho} | {tname}"] = dict(
                        T_eff=round(te, 1), mde_ic_80=round(P.mde(sig, te, a, 0.80, m), 4),
                        mde_ic_50=round(P.mde(sig, te, a, 0.50, m), 4))
    out["mde"] = mdes
    # ---- IC needed for illustrative economic effects, and power at that IC (design D1)
    conv = {}
    for eff in EFFECTS:
        for scs in SIGMA_CS:
            ic = P.ic_for_top_quintile_excess(eff, scs)
            row = dict(ic=round(ic, 4), ic_if_only_fresh_signals_inform=round(ic / f, 4))
            for sname, sig in SIGMA_IC.items():
                for rho in (0.0, 0.2):
                    for tname, a, m in TESTS:
                        te = P.t_eff_ar1(T, rho)
                        row[f"power | sigma_ic {sname} | rho {rho} | {tname}"] = round(P.power_at(ic, sig, te, a, m), 3)
                        row[f"power_inflated | sigma_ic {sname} | rho {rho} | {tname}"] = round(
                            P.power_at(ic / infl, sig, te, a, m), 3)
            conv[f"top-quintile excess {eff:.0%}/yr | sigma_cs {scs}"] = row
    out["effect_conversion_and_power"] = conv
    # ---- MDE in economic units (top-quintile excess / yr), D1, main sigma, rho 0.1
    econ = {}
    for tname, a, m in TESTS:
        ic80 = P.mde(SIGMA_IC["main"], P.t_eff_ar1(T, 0.1), a, 0.80, m)
        econ[tname] = {f"sigma_cs {s}": dict(naive=round(P.top_quintile_excess_annual(ic80, s), 4),
                                             inflated=round(P.top_quintile_excess_annual(ic80 * infl, s), 4))
                       for s in SIGMA_CS}
        econ[tname]["mde_ic_80"] = round(ic80, 4)
    out["mde_top_quintile_excess_main_rho0.1"] = econ
    # ---- controls: sampling part of sigma inflated by 1 / (1 - R2) (illustrative)
    ctrl = {}
    floor = 1 / math.sqrt(N - 1)
    for sname, sig in SIGMA_IC.items():
        fac2 = max(sig ** 2 - floor ** 2, 0.0)
        ctrl[sname] = {f"R2 {r2}": round(math.sqrt(fac2 + floor ** 2 / (1 - r2)), 4) for r2 in (0.0, 0.2, 0.4, 0.6)}
    out["sigma_with_controls"] = ctrl
    # ---- cost hurdles (frozen $7 / order, 0.10% / side; hypothetical books)
    costs = {}
    for cap in (100_000, 200_000):
        for k in (15, 20, 30, 165):
            for tau in (1, 2, 4):
                costs[f"capital {cap} | positions {k} | turnover {tau}x"] = dict(
                    trade_size=round(P.min_trade_size(cap, k)), annual_cost=round(P.annual_cost(cap, k, tau), 4))
    out["cost_hurdles"] = costs
    # ---- portfolio-level evidence: t of a net edge over 7 years at a given tracking error (illustrative)
    out["portfolio_t_7y"] = {f"edge {e:.1%} | TE {te:.0%}": round(e * math.sqrt(7) / te, 2)
                             for e in (0.01, 0.02, 0.03) for te in (0.04, 0.06, 0.08, 0.10)}
    out["terminal_wealth_ratio_30y"] = {f"{e:.1%}": round((1 + e) ** 30, 3) for e in (0.005, 0.01, 0.02, 0.03)}
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("sigma_ic_sampling_floor", "p7cp4_inflation_factor",
                                          "mde_top_quintile_excess_main_rho0.1")}, indent=1))


if __name__ == "__main__":
    main()
