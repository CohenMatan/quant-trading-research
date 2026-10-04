"""P3-CP1 support: calibration of the Phase 3 selection procedure on COMPLETED CONTROL BOOKS ONLY (owner 2026-10-04:
"use already-completed controls for methodological calibration"). Inputs: SPY (E900-07), EW-H017 (E017-02) and the
five 10-slot random-event books (E017-03..07); for comparison the 20-slot random books (E016-03..07) and EW-H016.
No candidate book (E017-01/08, E016-01/08, ...) and no technical-indicator return is used.

1. Measured no-skill characteristics (2010-03 -> 2017-12 = proposed search window; 2018 -> 2021 = internal OOS):
   tracking error vs SPY, mean log excess vs SPY and vs EW, cross-book correlation.
2. Search-null simulation of the proposed procedure (fold-median score over the four two-year training folds, the
   3-of-4 fold-consistency filter, the plateau score = 25th percentile of the neighbourhood, max over ~1,536 configs in
   neighbourhoods of 8), with the ACTUAL monthly EW-H017-minus-SPY path as the common component and Gaussian
   stock-selection noise scaled to the measured random-book tracking error vs EW. Correlation of selection noise inside a
   neighbourhood (rho_n) and across neighbourhoods (rho_b) are scenarios (they are unknown before the search).
   Output: how often the optimizer finds a "winner" by chance, and the null 95th percentile of the best plateau score.
3. Power: a true selection edge mu (a year, over a random book) planted in one neighbourhood; probability that the
   procedure detects it (plateau score above the null 95th percentile and selected) and that the selected candidate
   then passes the proposed internal-OOS checks (W1, W3 proxy, g/SE >= 1) on 2018-2021.

    PYTHONPATH=src python research/phase3/P3_calibration.py -> P3_calibration.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p2spec, results  # noqa: E402

TRAIN = ("2010-03-01", "2017-12-31")
OOS = ("2018-01-01", "2021-12-31")
FOLDS = (("2010-03", "2011-12"), ("2012-01", "2013-12"), ("2014-01", "2015-12"), ("2016-01", "2017-12"))
IDS = {"SPY": "E900-07", "EW17": "E017-02", **{f"R17_{i}": f"E017-0{i + 2}" for i in range(1, 6)},
       "EW16": "E016-02", **{f"R16_{i}": f"E016-0{i + 2}" for i in range(1, 6)}}
N_CFG, NB = 1536, 8                     # configs, neighbourhood size
SIMS, SEED = 2000, 20261004
EDGES = (0.0, 0.02, 0.04, 0.06, 0.08)
SCEN = [dict(rho_n=0.8, rho_b=0.2), dict(rho_n=0.9, rho_b=0.3), dict(rho_n=0.6, rho_b=0.1)]


def eq(e):
    return p2spec.equity_series(results.read_csv_gz(ROOT / f"experiments/{e}/equity.csv.gz"))


def measured():
    E = {k: eq(v) for k, v in IDS.items()}
    R = pd.concat({k: p2spec.returns(v[(v.index >= TRAIN[0]) & (v.index <= OOS[1])]) for k, v in E.items()},
                  axis=1, join="inner").dropna()
    L = np.log1p(R)
    out = {}
    for lab, (a, b) in (("train_2010_2017", TRAIN), ("oos_2018_2021", OOS)):
        x = L[(L.index >= a) & (L.index <= b)]
        d = x.sub(x["SPY"], axis=0).drop(columns="SPY")
        s = x[[c for c in x if c.startswith("R17")]].sub(x["EW17"], axis=0)
        out[lab] = dict(
            g_vs_spy={k: float(v) for k, v in (d.mean() * 252).items()},
            te_vs_spy={k: float(v) for k, v in (d.std() * np.sqrt(252)).items()},
            r17_g_vs_ew={k: float(v) for k, v in (s.mean() * 252).items()},
            r17_te_vs_ew={k: float(v) for k, v in (s.std() * np.sqrt(252)).items()},
            r17_corr_vs_spy=float((d[[c for c in d if c.startswith("R17")]].corr().values.sum() - 5) / 20),
            r17_corr_vs_ew=float((s.corr().values.sum() - 5) / 20))
    mon = L.groupby(L.index.str[:7]).sum()
    return out, mon


def fold_scores(m, months):
    """m: (configs, months) monthly log excess; returns annualised fold g (configs, 4)."""
    out = []
    for a, b in FOLDS:
        idx = [i for i, x in enumerate(months) if a <= x <= b]
        out.append(m[:, idx].mean(axis=1) * 12)
    return np.stack(out, axis=1)


def simulate(rng, common_tr, common_oos, mtr, sig_tr, sig_oos, mu_null, rho_n, rho_b, edge=0.0):
    nt, no = len(common_tr), len(common_oos)
    C = N_CFG // NB

    def noise(n, sig):
        g = rng.standard_normal(n)
        k = rng.standard_normal((C, n))
        u = rng.standard_normal((N_CFG, n))
        e = np.sqrt(rho_b) * g[None, :] + np.sqrt(rho_n - rho_b) * np.repeat(k, NB, axis=0) + np.sqrt(1 - rho_n) * u
        return e * sig / np.sqrt(12)
    mu = np.full(N_CFG, mu_null / 12)
    mu[:NB] += edge / 12                                   # the planted neighbourhood (cluster 0)
    tr = common_tr[None, :] + mu[:, None] + noise(nt, sig_tr)
    F = fold_scores(tr, mtr)
    s = np.median(F, axis=1)
    fc = (F > 0).sum(axis=1)
    S = s.reshape(C, NB)
    ps = np.repeat(np.percentile(S, 25, axis=1), NB)       # plateau score (neighbourhood = cluster)
    ok = fc >= 3
    best_raw = float(s.max())
    psm = np.where(ok, ps, -np.inf)
    j = int(np.argmax(psm))
    oos = common_oos[None, :] + mu[:, None] + noise(no, sig_oos)
    o = oos[j]
    g = o.mean() * 12
    se = o.std(ddof=1) * np.sqrt(12) / np.sqrt(no / 12)
    sel_vs_ew = (o - common_oos).mean() * 12            # W3 proxy: beats EW / the random median (selection > 0)
    return dict(best_raw=best_raw, best_ps=float(psm[j]), sel=j, planted=j < NB, oos_g=float(g),
                oos_ratio=float(g / se), oos_sel=float(sel_vs_ew), best_raw_fc=int(fc[int(np.argmax(s))]))


def main():
    meas, mon = measured()
    mtr = [m for m in mon.index if "2010-03" <= m <= "2017-12"]
    moo = [m for m in mon.index if "2018-01" <= m <= "2021-12"]
    common_tr = (mon.loc[mtr, "EW17"] - mon.loc[mtr, "SPY"]).to_numpy()
    common_oos = (mon.loc[moo, "EW17"] - mon.loc[moo, "SPY"]).to_numpy()
    t = meas["train_2010_2017"]
    sig_tr = float(np.mean(list(t["r17_te_vs_ew"].values())))
    sig_oos = float(np.mean(list(meas["oos_2018_2021"]["r17_te_vs_ew"].values())))
    mu_null = float(np.mean(list(t["r17_g_vs_ew"].values())))
    out = dict(measured=meas, model=dict(selection_te_train=sig_tr, selection_te_oos=sig_oos,
                                         null_selection_drift_vs_ew=mu_null, configs=N_CFG, neighbourhood=NB,
                                         sims=SIMS, folds=FOLDS), scenarios=[])
    rng = np.random.default_rng(SEED)
    for sc in SCEN:
        null = [simulate(rng, common_tr, common_oos, mtr, sig_tr, sig_oos, mu_null, **sc) for _ in range(SIMS)]
        tau = float(np.percentile([x["best_ps"] for x in null], 95))
        res = dict(scenario=sc,
                   null=dict(p_best_raw_beats_spy_in_training=float(np.mean([x["best_raw"] > 0 for x in null])),
                             median_best_raw_training_excess=float(np.median([x["best_raw"] for x in null])),
                             p95_best_raw=float(np.percentile([x["best_raw"] for x in null], 95)),
                             p_best_plateau_beats_spy=float(np.mean([x["best_ps"] > 0 for x in null])),
                             median_best_plateau=float(np.median([x["best_ps"] for x in null])),
                             tau95_best_plateau=tau,
                             selected_oos_mean_excess=float(np.mean([x["oos_g"] for x in null])),
                             p_selected_oos_w1=float(np.mean([x["oos_g"] > 0 for x in null])),
                             p_selected_oos_w1_ratio1_w3=float(np.mean([x["oos_g"] > 0 and x["oos_ratio"] >= 1
                                                                         and x["oos_sel"] > 0 for x in null]))),
                   power={})
        for e in EDGES:
            sims = [simulate(rng, common_tr, common_oos, mtr, sig_tr, sig_oos, mu_null, edge=e, **sc)
                    for _ in range(SIMS // 4)]
            det = [x["planted"] and x["best_ps"] > tau for x in sims]
            chain = [d and x["oos_g"] > 0 and x["oos_ratio"] >= 1 and x["oos_sel"] > 0 for d, x in zip(det, sims)]
            res["power"][f"{e:.2f}"] = dict(detected_and_selected=float(np.mean(det)), full_chain=float(np.mean(chain)),
                                            any_false_selection_passing_chain=float(np.mean(
                                                [(not x["planted"]) and x["best_ps"] > tau and x["oos_g"] > 0 and
                                                 x["oos_ratio"] >= 1 and x["oos_sel"] > 0 for x in sims])))
        out["scenarios"].append(res)
        print(json.dumps(res, indent=0)[:1500])
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
