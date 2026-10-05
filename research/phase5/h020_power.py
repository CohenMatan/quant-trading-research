"""H020 SYNTHETIC null-calibration and power study (P5-CP2 section 30). Synthetic latent panels only
(h020_synth_panel): no market data, no chart of any real stock, no real return.

  python research/phase5/h020_power.py [--quick]     -> research/phase5/h020_power_result.json

1. Null size: c_ic / c_inc from R null worlds of one no-edge panel; the share of independent no-edge panels whose REAL
   statistic exceeds c (should be ~ ALPHA = 1%) and their full-promotion rate.
2. Momentum-only world (returns depend on momentum, chart score correlated with momentum, no chart information beyond
   it): real statistics against the panel's own null (per-panel R); share with p < 1% for t_ic, t_inc and promotion.
3. Power: planted chart edge (beyond momentum) at several sizes; the realised mean IC and High-group excess (%/yr), and
   the rates of G3, G5 and full promotion with c from a null on a panel of the same design.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "src" / "qresearch" / "lean")]
import h020_synth_panel as P  # noqa: E402
import qr_h020_stats as H  # noqa: E402

QUICK = "--quick" in sys.argv
N_DATES = 417                                    # weekly decisions 2010-01 .. 2017-12 (approx.)
N_STOCKS = 300 if QUICK else 1000
R_NULL = 200 if QUICK else 1000
N_PANELS_SIZE = 60 if QUICK else 300
N_PANELS_MOM, R_MOM = (5, 100) if QUICK else (8, 150)
N_PANELS_POW = 10 if QUICK else 30
EDGES = (0.02, 0.04, 0.06, 0.08)


def null_worlds(prep, R, seed0=10_000):
    return [H.null_stats(H.run_world(prep, seed=seed0 + k)) for k in range(R)]


def main():
    t0 = time.time()
    out = dict(design=dict(n_dates=N_DATES, n_stocks=N_STOCKS, r_null=R_NULL, alpha=H.ALPHA, sigma_weekly=0.045,
                           phi_z=0.85, phi_m=0.97, rho=0.5, churn=0.05, quick=QUICK))
    # 1. size
    base = H.prepare(P.make_dates(N_DATES, N_STOCKS, seed=1))
    nw = null_worlds(base, R_NULL)
    c = H.critical_values(nw)
    reals = [H.run_world(H.prepare(P.make_dates(N_DATES, N_STOCKS, seed=100 + i))) for i in range(N_PANELS_SIZE)]
    out["size"] = dict(c=c, panels=N_PANELS_SIZE,
                       rate_t_ic=float(np.mean([r["t_ic"] > c["t_ic"] for r in reals])),
                       rate_t_inc=float(np.mean([r["t_inc"] > c["t_inc"] for r in reals])),
                       rate_promotion=float(np.mean([H.promotion(r, c)["pass"] for r in reals])),
                       null_t_ic_mean=float(np.mean([w["t_ic"] for w in nw])),
                       null_t_ic_sd=float(np.std([w["t_ic"] for w in nw])),
                       null_t_inc_sd=float(np.std([w["t_inc"] for w in nw])))
    print("size", out["size"], round(time.time() - t0), flush=True)
    # 2. momentum-only world
    res = []
    for i in range(N_PANELS_MOM):
        pr = H.prepare(P.make_dates(N_DATES, N_STOCKS, mom_ic=0.05, rho=0.5, seed=200 + i))
        r = H.run_world(pr)
        w = null_worlds(pr, R_MOM, 20_000 + 1000 * i)
        cc = {k: H.X.critical_value([x[k] for x in w], 0.01) for k in H.STATS}
        res.append(dict(t_ic=r["t_ic"], t_inc=r["t_inc"], null_t_ic_mean=float(np.mean([x["t_ic"] for x in w])),
                        g3=r["t_ic"] > cc["t_ic"], g5=r["t_inc"] > cc["t_inc"], promoted=H.promotion(r, cc)["pass"]))
    out["momentum_only"] = dict(panels=N_PANELS_MOM, r=R_MOM, rate_g3=float(np.mean([x["g3"] for x in res])),
                                rate_g5=float(np.mean([x["g5"] for x in res])),
                                rate_promotion=float(np.mean([x["promoted"] for x in res])),
                                mean_real_t_ic=float(np.mean([x["t_ic"] for x in res])),
                                mean_null_t_ic=float(np.mean([x["null_t_ic_mean"] for x in res])))
    print("mom", out["momentum_only"], round(time.time() - t0), flush=True)
    # 3. power
    out["power"] = []
    for e in EDGES:
        pr0 = H.prepare(P.make_dates(N_DATES, N_STOCKS, edge_ic=e, seed=300))
        ce = H.critical_values(null_worlds(pr0, R_NULL // 2, 30_000))
        rs = [H.run_world(H.prepare(P.make_dates(N_DATES, N_STOCKS, edge_ic=e, seed=400 + i)))
              for i in range(N_PANELS_POW)]
        out["power"].append(dict(edge_param=e, c=ce, panels=N_PANELS_POW,
                                 mean_ic=float(np.mean([r["ic_mean"] for r in rs])),
                                 mean_high_ann=float(np.mean([r["high_ann"] for r in rs])),
                                 mean_high_minus_low_ann=float(np.mean([r["high_ann"] - r["low_ann"] for r in rs])),
                                 rate_g3=float(np.mean([r["t_ic"] > ce["t_ic"] for r in rs])),
                                 rate_g5=float(np.mean([r["t_inc"] > ce["t_inc"] for r in rs])),
                                 rate_g1=float(np.mean([H.promotion(r, ce)["G1_economic"] for r in rs])),
                                 rate_promotion=float(np.mean([H.promotion(r, ce)["pass"] for r in rs]))))
        print("power", out["power"][-1], round(time.time() - t0), flush=True)
    out["seconds"] = round(time.time() - t0)
    if not QUICK:
        (HERE / "h020_power_result.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
