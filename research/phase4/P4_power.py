"""P4-CP1 design study: null precision, false-pass rate and POWER of the proposed Weekly search, for two validation
architectures. NO market data and NO strategy returns: synthetic monthly excess-return worlds calibrated on the
already-committed CONTROL-book statistics (research/phase3/P3_calibration.json: random books vs EW / SPY, 2010-2017 and
2018-2021), run through the FROZEN Phase 3 selection pipeline (qr_p3_pipeline: gates, fold-median score, plateau,
clusters, statistic T, one-standard-error rule, walk-forward) on the PROPOSED Weekly grammar graph (P4_search_space.py).

Model of configuration c, month m:  x_cm = common_m + drift + edge_c + sel_cm
  common  : EW minus SPY (Gaussian; train mean/TE and OOS mean/TE from the control books)
  drift   : mechanical no-skill drag of a slot book vs EW (cash, costs), per month
  sel     : selection noise with tracking error sigma(N) = sigma_10 sqrt(10 / N) (control-book scaling), AR(1) phi,
            correlated: a global part, a part shared by the same primary type, a part shared by the same primary
            variant (same exit rule), and an idiosyncratic part
  edge    : a true selection edge (a year) planted on one whole graph component (18 configurations)

Architecture A (Phase 3 pattern): search 2010-03..2017-12 (4 two-year folds); Q1 T > tau (null 95th percentile);
  Q2 walk-forward 2014-2017; Q4 one-shot internal OOS 2018-2021 for the rank-1 centre: W1 (g vs SPY > 0), W3 proxy (beats
  EW and the random-book drift), g / SE >= 1.
Architecture B (expanding walk-forward as the main evidence): search 2010-03..2021-12 (6 folds); Q1 on that window;
  Q2' walk-forward 2014-2021 (8 one-year tests, >= 6 picks, summed excess vs SPY > 0 and vs EW > 0, g / SE >= 1 of the
  8 yearly excesses); no internal OOS left (the Holdout is the next test).

    PYTHONPATH=src python research/phase4/P4_power.py -> P4_power.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import qr_p3_pipeline as P  # noqa: E402
import P4_search_space as S  # noqa: E402

N_SLOTS = 12
R_NULL, R_POWER, SEED = 1000, 300, 20261006
EDGES = (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12)
SCEN = {"base": dict(g=0.20, t=0.40, p=0.70, phi=0.2), "high_corr": dict(g=0.30, t=0.60, p=0.85, phi=0.3),
        "low_corr": dict(g=0.10, t=0.25, p=0.50, phi=0.0)}
TRAIN_MONTHS = 94                     # 2010-03 .. 2017-12
OOS_MONTHS = 48                       # 2018-01 .. 2021-12


def calib():
    cal = json.loads((ROOT / "research/phase3/P3_calibration.json").read_text())
    m, tr, oo = cal["model"], cal["measured"]["train_2010_2017"], cal["measured"]["oos_2018_2021"]
    k = math.sqrt(10 / N_SLOTS)
    return dict(sel_tr=m["selection_te_train"] * k, sel_oos=m["selection_te_oos"] * k,
                drift=m["null_selection_drift_vs_ew"],
                ew_tr=(tr["g_vs_spy"]["EW17"], tr["te_vs_spy"]["EW17"]),
                ew_oos=(oo["g_vs_spy"]["EW17"], oo["te_vs_spy"]["EW17"]))


class World:
    def __init__(self):
        C = S.enumerate_configs()
        self.C = C
        self.ids = [c["id"] for c in C]
        ix = {c["id"]: i for i, c in enumerate(C)}
        nb = S.neighbours(C)
        self.nbi = [np.array([ix[o] for o in nb[c["id"]]], dtype=int) for c in C]
        self.cpx = [S.complexity(c) for c in C]
        self.ptype = np.array([sorted(S.PRIMARY).index(c["primary"][0]) for c in C])
        pv = sorted({(c["primary"][0], c["primary"][2]) for c in C})
        self.pvar = np.array([pv.index((c["primary"][0], c["primary"][2])) for c in C])
        comp = {}
        for c in C:                                          # planted region: one 18-configuration component
            comp.setdefault((c["primary"][0], c["primary"][2][:0], None if c["confirm"] is None else c["confirm"][0]),
                            []).append(ix[c["id"]])
        self.planted = np.array(sorted(next(v for k, v in sorted(comp.items(), key=lambda kv: str(kv[0]))
                                            if k[0] == "WP1" and k[2] == "CRS")))
        self.n = len(C)


def sim_months(rng, W, months, sel_sd, ew, drift, edge, sc):
    n = W.n
    t = months
    a = np.zeros((n, t))
    g = rng.standard_normal(t)
    ty = rng.standard_normal((3, t))
    pv = rng.standard_normal((W.pvar.max() + 1, t))
    u = rng.standard_normal((n, t))
    e = (math.sqrt(sc["g"]) * g[None, :] + math.sqrt(sc["t"] - sc["g"]) * ty[W.ptype] +
         math.sqrt(sc["p"] - sc["t"]) * pv[W.pvar] + math.sqrt(1 - sc["p"]) * u)
    phi = sc["phi"]
    a[:, 0] = e[:, 0]
    for k in range(1, t):                                    # unit-variance AR(1)
        a[:, k] = phi * a[:, k - 1] + math.sqrt(1 - phi ** 2) * e[:, k]
    sel = a * sel_sd / math.sqrt(12)
    common = rng.normal(ew[0] / 12, ew[1] / math.sqrt(12), t)
    mu = np.full(n, drift / 12)
    mu[W.planted] += edge / 12
    return common[None, :] + mu[:, None] + sel, common


def yearly(x, first_months):
    """Monthly -> calendar-year sums; the first year has `first_months` months."""
    out, i = [], 0
    sizes = [first_months] + [12] * ((x.shape[1] - first_months) // 12)
    for s in sizes:
        out.append(x[:, i:i + s].sum(axis=1))
        i += s
    return np.stack(out, axis=1), np.array(sizes, float)


def inputs(W, logex_y, months_y, common_y, years):
    n, k = logex_y.shape
    sess = months_y * 21.0
    return P.Inputs(W.ids, logex_y, np.full((n, k), 500.0), np.full((n, k), 1e5) * sess, np.full((n, k), 3e5),
                    np.full((n, k), -0.10), sess, np.full(k, -0.20), common_y, years)


def one(rng, W, cal, sc, edge, arch):
    tr, ctr = sim_months(rng, W, TRAIN_MONTHS, cal["sel_tr"], cal["ew_tr"], cal["drift"], edge, sc)
    oo, coo = sim_months(rng, W, OOS_MONTHS, cal["sel_oos"], cal["ew_oos"], cal["drift"], edge, sc)
    if arch == "A":
        ly, my = yearly(tr, 10)
        cy, _ = yearly(ctr[None, :], 10)
        inp = inputs(W, ly, my, cy[0], list(range(2010, 2018)))
        full = P.select(inp, W.nbi, W.cpx, 2017, k=1)
        wf = P.walk_forward(inp, W.nbi, W.cpx, years=(2014, 2015, 2016, 2017))
        res = dict(T=full["T"], wf=bool(wf["passed"]))
        if full["ranked"]:
            c = full["ranked"][0]["centre"]
            o = oo[c]
            g = o.mean() * 12
            se = max(o.std(ddof=1) * math.sqrt(12) / math.sqrt(OOS_MONTHS / 12), 1e-9)
            res.update(pick_planted=bool(c in set(W.planted)),
                       q4=bool(g > 0 and (o - coo).mean() > 0 and (o - coo - cal["drift"] / 12).mean() > 0
                               and g / se >= 1.0))
        else:
            res.update(pick_planted=False, q4=False)
        return res
    x = np.concatenate([tr, oo], axis=1)
    cx = np.concatenate([ctr, coo])
    ly, my = yearly(x, 10)
    cy, _ = yearly(cx[None, :], 10)
    years = list(range(2010, 2022))
    inp = inputs(W, ly, my, cy[0], years)
    full = P.select(inp, W.nbi, W.cpx, 2021, k=1)
    wf = P.walk_forward(inp, W.nbi, W.cpx, years=tuple(range(2014, 2022)))
    ex = np.array([y["ex_spy"] for y in wf["years"]])
    se = ex.std(ddof=1) / math.sqrt(len(ex)) if len(ex) > 1 else 1e9
    q2 = bool(wf["picks"] >= 6 and wf["total_ex_spy"] > 0 and wf["total_ex_ew"] > 0 and ex.mean() / max(se, 1e-9) >= 1)
    c = full["ranked"][0]["centre"] if full["ranked"] else -1
    return dict(T=full["T"], wf=q2, pick_planted=bool(c in set(W.planted)), q4=True)


def tau_of(T, alpha=0.05):
    v = np.sort(np.asarray(T, float))[::-1]
    return float(v[int(math.floor(alpha * (len(v) + 1))) - 1])


def cp(k, n):
    lo = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))
    return lo, hi


def interp_edge(edges, p, target):
    for i in range(1, len(edges)):
        if p[i - 1] < target <= p[i]:
            return edges[i - 1] + (target - p[i - 1]) / (p[i] - p[i - 1]) * (edges[i] - edges[i - 1])
    return None if p[-1] < target else edges[0]


def main():
    cal = calib()
    W = World()
    out = dict(model=dict(cal, slots=N_SLOTS, configs=W.n, planted_region=len(W.planted), r_null=R_NULL,
                          r_power=R_POWER, edges=EDGES, scenarios=SCEN), results={})
    for sname, sc in SCEN.items():
        for arch in ("A", "B"):
            rng = np.random.default_rng([SEED, list(SCEN).index(sname), ord(arch)])
            null = [one(rng, W, cal, sc, 0.0, arch) for _ in range(R_NULL)]
            T = np.array([x["T"] for x in null])
            tau = tau_of(T)
            q1 = np.array([np.isfinite(T[i]) and T[i] > tau_of(np.delete(T, i)) for i in range(R_NULL)])
            wf = np.array([x["wf"] for x in null])
            q4 = np.array([x["q4"] for x in null])
            fp_search = int((q1 & wf).sum())
            fp_chain = int((q1 & wf & q4).sum())
            power = {}
            for e in EDGES[1:]:
                sims = [one(rng, W, cal, sc, e, arch) for _ in range(R_POWER)]
                det = np.array([x["T"] > tau and x["pick_planted"] for x in sims])
                s2 = det & np.array([x["wf"] for x in sims])
                s4 = s2 & np.array([x["q4"] for x in sims])
                power[f"{e:.2f}"] = dict(q1_detect_select=float(det.mean()), plus_walk_forward=float(s2.mean()),
                                         full_pre_holdout_chain=float(s4.mean()))
            ed = list(EDGES)
            curves = {k: [0.0] + [power[f"{e:.2f}"][k] for e in EDGES[1:]]
                      for k in ("q1_detect_select", "plus_walk_forward", "full_pre_holdout_chain")}
            res = dict(tau=tau, null_T_quantiles={q: float(np.percentile(T[np.isfinite(T)], q)) for q in (50, 95, 99)},
                       null_q1_rate=float(q1.mean()), null_wf_rate=float(wf.mean()),
                       false_pass_search_stage=dict(k=fp_search, rate=fp_search / R_NULL, ci95=cp(fp_search, R_NULL)),
                       false_pass_full_chain=dict(k=fp_chain, rate=fp_chain / R_NULL, ci95=cp(fp_chain, R_NULL)),
                       power=power,
                       edge_for_50pct={k: interp_edge(ed, v, 0.5) for k, v in curves.items()},
                       edge_for_80pct={k: interp_edge(ed, v, 0.8) for k, v in curves.items()})
            out["results"][f"{sname}_{arch}"] = res
            print(sname, arch, json.dumps({k: res[k] for k in ("tau", "false_pass_search_stage",
                                                                "false_pass_full_chain", "edge_for_50pct",
                                                                "edge_for_80pct")}, default=float))
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, default=float) + "\n")


if __name__ == "__main__":
    main()
