"""OC-2 synthetic calibration v2 (owner D249 section 8): engineering validation record. DEV seeds only; structure
statistics only (dimensions, failures, IC / payoff dispersion, refresh shares, slope scale, runtime). No scenario
rejection rate or power is computed or used for any choice. Synthetic only.

    OMP_NUM_THREADS=1 PYTHONPATH=src python research/longhorizon/oc2/v2/OC2_V2_engineering.py

Section 'identification_projection' combines the audit's POPULATION bias (no returns) with the DEV slope scale to
project, analytically, whether the frozen size criterion can be met in the identification family. It is the basis
of the pre-run STOP (owner D249 sections 7 / 10), not a scenario result.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
sys.path[:0] = [str(ROOT / "src"), str(HERE)]
from qresearch import oc2synth_v2 as V  # noqa: E402
import OC2_V2_scenarios as S  # noqa: E402

OUT = HERE / "OC2_V2_engineering.json"
REPS = 12


def summary(w, reps=REPS):
    t0 = time.time()
    rows = [V.run_world(w, r, tag="DEV") for r in range(reps)]
    ok = [r for r in rows if "failed" not in r]
    sec = (time.time() - t0) / reps
    if not ok:
        return dict(failed=len(rows), reasons=sorted({r["failed"] for r in rows}))
    m = lambda k: float(np.mean([r[k] for r in ok]))  # noqa: E731
    return dict(failed=len(rows) - len(ok), pic_sd=m("pic_sd"), ic_sd=m("ic_sd"), rho1=m("rho1"),
                sd_slope=m("sd_slope"), sd_tq_annual_across_reps=float(np.std([r["tq_annual"] for r in ok])),
                mean_n=m("mean_n"), min_n=min(r["min_n"] for r in ok), ret_sd=m("ret_sd"),
                fresh_by_phase=np.mean([r["fresh_by_phase"] for r in ok], axis=0).round(3).tolist(),
                corr_signal_controls=np.mean([r["corr"] for r in ok], axis=0).round(3).tolist(),
                sec_per_rep=round(sec, 3))


def shifted_rejection(delta, alphas=(0.05, 0.01), draws=200_000, seed=7):
    """P(NW7 t > fixed-b cv) for iid Gaussian slopes whose mean is delta / sqrt(T) slope-sd units."""
    rng = np.random.default_rng(seed)
    b = rng.standard_normal((draws, V.T)) + delta / math.sqrt(V.T)
    m = b.mean(axis=1, keepdims=True)
    d = b - m
    v = (d * d).mean(axis=1)
    for l in range(1, V.NW_LAG + 1):
        v += 2 * (1 - l / (V.NW_LAG + 1)) * (d[:, l:] * d[:, :-l]).sum(axis=1) / V.T
    t = m[:, 0] / np.sqrt(v / V.T)
    return {str(a): float(np.mean(t > V.CV[a])) for a in alphas}


def main():
    res = dict(kind="OC-2 v2 engineering validation (DEV seeds; structure only)", decision="D249", reps=REPS)
    t0 = time.time()
    cv = V.fixed_b_cv()
    res["fixed_b_cv"] = dict(recomputed=cv, pinned={str(k): v for k, v in V.CV.items()},
                             identical=all(abs(cv[a] - V.CV[a]) < 1e-12 for a in V.CV),
                             normal_reference=dict(zip(("0.05", "0.01"), (1.6449, 2.3263))))
    cal = V.calibrate_payoff()
    res["payoff_calibration"] = dict(cal, identical_to_pinned=all(abs(cal["g_sd"][k] - V.G_SD[k]) < 1e-15
                                                                  for k in V.G_SD))
    res["regimes"] = {str(r): summary(V.World(f"ENG-N4@{r}", priced=V.CONTROLS, ic_sd=r), 48)
                      for r in (0.06, 0.09, 0.12)}
    # N7 budget guard: the v1 parameters must be refused, the v2 ones accepted
    try:
        V.variance_budget(V.World("v1-N7", sigma_sector=0.05, sigma_factor=0.02), V.G_SD[0.09])
        n7_v1 = "accepted"
    except ValueError as e:
        n7_v1 = f"refused: {e}"
    w7 = [w for w in S.NULLS[9] if w.name == "N7"][0]
    res["N7_budget"] = dict(v1_parameters=n7_v1,
                            v2_parameters_idio_sd=V.variance_budget(w7, V.G_SD[0.09]),
                            v2_systematic_share=1 - V.variance_budget(w7, V.G_SD[0.09]) ** 2 / V.SD_TOTAL ** 2)
    # N13 at small and realistic cross-sections, with and without churn
    res["N13"] = {nm: summary(w, 6) for nm, w in {
        "realistic_churn0": V.World("ENG-N13a", priced=V.CONTROLS, horizon=3, churn=0.0),
        "realistic_churn1": V.World("ENG-N13b", priced=V.CONTROLS, horizon=3),
        "small_n0.1_churn1": V.World("ENG-N13c", priced=V.CONTROLS, horizon=3, n_scale=0.1),
        "small_n0.1_churn2": V.World("ENG-N13d", priced=V.CONTROLS, horizon=3, n_scale=0.1, churn=2.0)}.items()}
    # every planned world runs (one DEV replication each); record failures, dimensions, seconds
    runs = {}
    for w in S.all_nulls() + [S.ORACLE] + S.POWER:
        t1 = time.time()
        o = V.run_world(w, 0, tag="DEV")
        runs[w.name] = dict(failed=o.get("failed"), mean_n=o.get("mean_n"), min_n=o.get("min_n"),
                            seconds=round(time.time() - t1, 2))
    res["all_worlds_run"] = dict(n=len(runs), failures=sorted(k for k, v in runs.items() if v["failed"]), runs=runs)
    # determinism: the same seed gives identical statistics; DEV and FINAL seeds differ
    a, b = V.run_world(S.N4, 3, tag="DEV"), V.run_world(S.N4, 3, tag="DEV")
    res["determinism"] = dict(identical=a == b, dev_final_seed_differ=V.seed_of("N4", 3, "DEV") != V.seed_of("N4", 3))
    # identification projection (analytic; population bias from the audit x DEV slope scale)
    aud = json.loads((HERE / "OC2_V2_audit.json").read_text())["B_C_population_bias"]
    keys = {"N5a": "N5a reliability 0.8", "N5b": "N5b reliability 0.6", "N2L1": "N2L latent growth +1%",
            "N2L": "N2L latent growth +3%", "N2L5": "N2L latent growth +5%", "N4": "N4 normal-linear premia",
            "N4q": "N4q tail (decile) premia"}
    proj = {}
    for nm, k in keys.items():
        bpop = aud[k]["rcs"]["b"]
        tq = aud[k]["rcs"]["annual_top_quintile"]
        proj[nm] = {}
        for r, s in res["regimes"].items():
            delta = bpop * math.sqrt(V.T) / s["sd_slope"]
            p_tq = 1 - 0.5 * math.erfc(-(0.03 - tq) / s["sd_tq_annual_across_reps"] / math.sqrt(2))
            proj[nm][r] = dict(population_tq_annual=tq, delta_t=delta, projected_rejection=shifted_rejection(delta),
                               projected_p_tq_ge_3pct_upper_bound_full_rule=p_tq)
    res["identification_projection"] = proj
    res["seconds"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("fixed_b_cv", "payoff_calibration", "N7_budget", "determinism")}, indent=1))
    for r, s in res["regimes"].items():
        print(r, {k: s[k] for k in ("pic_sd", "ic_sd", "rho1", "sd_slope", "sd_tq_annual_across_reps",
                                    "fresh_by_phase", "sec_per_rep")})
    print({k: (v.get("failed"), v.get("min_n")) for k, v in res["N13"].items()})
    print("worlds", res["all_worlds_run"]["n"], "failures", res["all_worlds_run"]["failures"])
    for nm, v in proj.items():
        print(nm, {r: (round(x["delta_t"], 2), x["projected_rejection"],
                       round(x["projected_p_tq_ge_3pct_upper_bound_full_rule"], 4)) for r, x in v.items()})


if __name__ == "__main__":
    main()
