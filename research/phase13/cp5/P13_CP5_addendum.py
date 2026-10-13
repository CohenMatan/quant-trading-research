"""P13-CP5 EXPLORATORY ADDENDUM, written AFTER the pre-registered audit result was read (owner sections 21-22, 25):
descriptive mechanism decomposition with the committed H028 coefficient vectors held fixed (no refit), on the same
synthetic panels -> P13_CP5_addendum.json. Non-gating: it cannot change the pre-registered classification.

  (a) churn dose-response without refit noise: S1 / S2 / S3, panels 1-3, 100 worlds;
  (b) sector-cap interaction: S2, cap 3 (frozen) vs cap 15 (no binding cap), panels 1-3, 100 worlds;
  (c) LOWVOL anchoring: S2, conditional null (LOWVOL attached) vs all eleven features moved, panels 1-3, 100 worlds;
  (d) cost amplification: extra null commissions / slippage under the frozen cost model, as a share of the real
      synthetic path's final wealth, and the implied log-wealth shift.

    PYTHONPATH=src python research/phase13/cp5/P13_CP5_addendum.py
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import P13_CP5_audit as A  # noqa: E402

H, G = A.H, A.G
PANELS, WORLDS = (1, 2, 3), tuple(range(1, 101))
KEYS = ("name_turnover", "new_names", "trades", "commissions", "slippage", "total_cost", "top15_survival",
        "rank_autocorr", "top15_rank_change", "wealth")


def committed():
    com = json.loads((A.ROOT / "research/phase13/cp1/P13_CP1_result.json").read_text())["coefficients"]
    return {Y: np.array(com[str(Y)]["beta"], float) for Y in H.OUTER_YEARS}


def fixed(months, Xs, B, cap=H.SECTOR_CAP):
    first = {Y: H.year_months(months, Y) for Y in H.OUTER_YEARS}
    idx = [i for Y in H.OUTER_YEARS for i in first[Y]]
    ms = [months[i] for i in idx]
    sc = [Xs[i] @ B[months[i]["test_year"]] for i in idx]
    return A.structure(ms, sc, H.simulate(ms, sc, cap=cap, keep_trades=True))


def summary(real, nulls):
    out = {}
    for k in KEYS:
        b = A.band(real[k], [n[k] for n in nulls])
        out[k] = {f: b[f] for f in ("real", "null_median", "null_q005", "null_q995", "gap_median", "real_pct",
                                    "real_below_all", "real_above_all", "position")}
    return out


def main():
    B = committed()
    res = dict(note="EXPLORATORY, post-result, descriptive, non-gating", panels=PANELS, worlds=len(WORLDS),
               coefficients="committed real H028 lambda-100 coefficients per outer year (structural field)", runs={})
    for rg in A.REGIMES:
        for scen in ("S1_no_churn", "S2_realistic_churn", "S3_double_churn"):
            for p in PANELS:
                ms = A.panel(p, rg, scen)
                Xr = [m["X"] for m in ms]
                real = fixed(ms, Xr, B)
                cond = [fixed(ms, G.conditional_permuted(ms, s), B) for s in WORLDS]
                key = f"{rg}|{scen}|{p}"
                res["runs"][key] = dict(conditional=summary(real, cond))
                if scen == "S2_realistic_churn":
                    real15 = fixed(ms, Xr, B, cap=15)
                    res["runs"][key]["cap15"] = summary(real15, [fixed(ms, G.conditional_permuted(ms, s), B, cap=15)
                                                                 for s in WORLDS])
                    res["runs"][key]["all_eleven_moved"] = summary(real, [fixed(ms, H.permuted(ms, s), B)
                                                                          for s in WORLDS])
                    extra = res["runs"][key]["conditional"]["total_cost"]["gap_median"]
                    w = real["wealth"]
                    res["runs"][key]["cost_amplification"] = dict(
                        extra_cost=extra, real_final_wealth=w, extra_share_of_wealth=extra / w,
                        log_wealth_shift=-math.log(1.0 - extra / w) if extra < w else None)
                print(key, flush=True)
    txt = json.dumps(res, indent=1, sort_keys=True, default=float)
    (HERE / "P13_CP5_addendum.json").write_text(txt + "\n")
    print(hashlib.sha256(txt.encode()).hexdigest()[:16])


if __name__ == "__main__":
    main()
