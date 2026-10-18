"""OC-CP2 (owner D247): analytical power / MDE / cost tables for the proposed business-improvement signal test (OC-2,
F5-A return-on-assets improvement). Uses only the LH-CP4 equations (`lh_cp4_power.py`), labelled assumptions and
committed NON-RETURN coverage aggregates (P14-CP1 F5-A monthly coverage). No data access, no returns, no signals, no
simulation, no Monte Carlo.

    PYTHONPATH=src python research/longhorizon/oc_cp2/OC_CP2_power.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/longhorizon/cp4"))
import lh_cp4_power as P  # noqa: E402

OUT = HERE / "OC_CP2_power.json"
P14_CP1 = ROOT / "research/phase14/cp1/P14_CP1_audit.json"

# ---------------------------------------------------------------- ASSUMPTIONS (labelled; none estimated from returns)
SIGMA_IC = {"optimistic": 0.06, "main": 0.09, "pessimistic": 0.12}   # as LH-CP4 / P7-CP4 (assumed there)
RHO = (0.1, 0.2)                                                      # AR(1) of the monthly slope (assumed)
SIGMA_CS = 0.065                                                      # monthly cross-sectional return sd (assumed)
STRUCTURE_FACTOR = 1.336                                              # LH-CP4: committed P7-CP4 synthetic / analytic
TESTS = [("two-sided 5% (one-sided 2.5%)", 0.05), ("two-sided 2% (one-sided 1%)", 0.02)]
EFFECTS = (0.02, 0.03, 0.04)                                          # top-quintile excess / yr, before costs
FRESH_SHARE = 0.337                                                   # LH-CP4 fresh-signal share (2015-2021)
COVERAGE_FLOOR = 0.60                                                 # window rule (OC-CP2 §11 item 5)


def window_from_coverage():
    """First review from which committed P14-CP1 F5-A coverage (share of U_NF, Data v2.1 basis) stays >= the floor."""
    m = json.loads(P14_CP1.read_text())["coverage"]["F5A"]["monthly"]
    for i in range(len(m)):
        if all(v >= COVERAGE_FLOOR for v in m[i:]):
            y, mo = 2011 + i // 12, i % 12 + 1
            yearly = {}
            for j, v in enumerate(m):
                yearly.setdefault(2011 + j // 12, []).append(v)
            return dict(first_review=f"{y}-{mo:02d}", reviews=len(m) - i, all_reviews=len(m),
                        min_from_start=round(min(m[i:]), 3),
                        yearly_mean={y: round(sum(v) / len(v), 3) for y, v in yearly.items()},
                        source="P14_CP1_audit.json coverage.F5A.monthly (non-return aggregate)")
    raise SystemExit("no window")


def main():
    win = window_from_coverage()
    T_main = win["reviews"]
    windows = {f"main {win['first_review']} -> 2021-11 ({T_main})": T_main,
               "sub-window 2015-01 -> 2021-11 (83)": 83, "reference 2011-01 -> 2021-11 (131)": 131}
    out = dict(kind="OC-CP2 analytical power tables (assumption-driven; no data, no returns, no simulation)",
               decision="D247", window=win,
               assumptions=dict(sigma_ic=SIGMA_IC, rho=RHO, sigma_cs=SIGMA_CS, structure_factor=STRUCTURE_FACTOR,
                                fresh_share=FRESH_SHARE,
                                note="ranges, not estimates; same conventions as LH-CP4 (crit() is two-sided)"))
    mde_rows, power_rows = {}, {}
    for wname, T in windows.items():
        for sname, sig in SIGMA_IC.items():
            for rho in RHO:
                te = P.t_eff_ar1(T, rho)
                for tname, a in TESTS:
                    ic80 = P.mde(sig, te, a, 0.80)
                    key = f"{wname} | sigma_ic {sname} {sig} | rho {rho} | {tname}"
                    mde_rows[key] = dict(
                        T_eff=round(te, 1), mde_ic_80=round(ic80, 4),
                        top_quintile_80_naive=round(P.top_quintile_excess_annual(ic80, SIGMA_CS), 4),
                        top_quintile_80_structure=round(P.top_quintile_excess_annual(ic80, SIGMA_CS)
                                                        * STRUCTURE_FACTOR, 4))
                    pw = {}
                    for e in EFFECTS:
                        ic = P.ic_for_top_quintile_excess(e, SIGMA_CS)
                        pw[f"{e:.0%}"] = dict(naive=round(P.power_at(ic, sig, te, a), 3),
                                              structure=round(P.power_at(ic / STRUCTURE_FACTOR, sig, te, a), 3),
                                              fresh_only=round(P.power_at(P.fresh_dilution(ic, FRESH_SHARE),
                                                                          sig, te, a), 3))
                    power_rows[key] = pw
    out["mde_80"] = mde_rows
    out["power"] = power_rows
    # ---- costs of an investable book (assumed turnover; $7 / order, 0.1% slippage per side as LH-CP4)
    costs = {}
    for cap in (100_000, 200_000):
        for k in (15, 20, 25):
            for tau in (1.5, 2.5, 3.5):
                costs[f"${cap // 1000}K | K {k} | one-way turnover {tau}/yr"] = dict(
                    annual_cost=round(P.annual_cost(cap, k, tau), 4),
                    position=round(P.min_trade_size(cap, k)))
    out["costs"] = costs
    # ---- portfolio-level detectability (t ~ e * sqrt(years) / TE), for the later standalone / combined stages
    out["portfolio_t"] = {f"years {y} | e {e:.1%} | TE {te:.0%}": round(e * math.sqrt(y) / te, 2)
                          for y in (7, 9.8) for e in (0.01, 0.02, 0.03) for te in (0.04, 0.06, 0.08)}
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    k = f"main {win['first_review']} -> 2021-11 ({T_main}) | sigma_ic main 0.09 | rho 0.1 | "
    for tname, _ in TESTS:
        print(tname, mde_rows[k + tname], power_rows[k + tname])
    print(win)


if __name__ == "__main__":
    main()
