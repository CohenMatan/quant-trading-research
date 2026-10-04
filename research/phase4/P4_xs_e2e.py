"""P4-CP3R2 end-to-end synthetic study of the H019 procedure. SYNTHETIC ONLY: no market data.

Unlike P4_xs_power(_r).py (a monthly signal model), this runs the ACTUAL pipeline of src/qresearch/lean/qr_xs.py on
synthetic DAILY price panels shaped like the H019 setting: ~1,100 stocks, IPOs and delistings, 48 history months
(2006-2009, look-back inputs only) + research months 2010-01 .. 2017-12; features from daily prices (PRET, ID,
11 split-adjusted moving-average ratios); the fitted Han-Zhou-Zhu trend factor from monthly regressions; 83 decisions
2011-01 .. 2017-11; next-month returns from the next open.

Per IC-noise scenario (style-factor volatility):
  1. tethered null: R worlds of ONE no-edge panel, every world re-running the whole procedure (regressions, rolling
     coefficients, S2 two-stage sort, S3, statistics) -> c = the 1% family critical value; false rates inside;
  2. independent no-edge panels (the data-generating null): the real (identity) world of each, judged with c ->
     the procedure's false-promotion rate; effective sample size of the monthly IC series;
  3. planted edges (each signal's own information, monthly drift kappa x rank-normal score known at the month-end):
     power of the statistical gate and of the complete rule; minimum detectable effects.
Run: python research/phase4/P4_xs_e2e.py <scenario> [--quick]  ->  research/phase4/P4_xs_e2e_<scenario>.json
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats as sps

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src" / "qresearch" / "lean"))
sys.path.insert(0, str(HERE))
import qr_xs as X  # noqa: E402
import P4_xs_synth as SY  # noqa: E402

SCEN = {"low": 0.0025, "mid": 0.0045, "high": 0.006}
N, MONTHS, FRK, SPM = 1100, 144, 48, 21
WIN = dict(first_research=(2010, 1), first_decision=(2011, 1), last_decision=(2017, 11))
ME = [SPM * (k + 1) - 1 for k in range(MONTHS)]


def rank_normal(x, alive):
    z = np.zeros(x.size)
    ok = alive & np.isfinite(x)
    if ok.sum() > 2:
        z[ok] = sps.norm.ppf((sps.rankdata(x[ok]) - 0.5) / ok.sum())
    return z


def info_at(k, P):
    """Point-in-time information at month-end k from total-return closes P (rows <= me[k])."""
    r1, r12, d = ME[k - 1], ME[k - 12], ME[k]
    pret = P[r1] / P[r12] - 1
    w = P[r12:r1 + 1]
    dr = w[1:] / w[:-1] - 1
    n = np.isfinite(dr).sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        idm = np.sign(pret) * ((dr < 0).sum(0) - (dr > 0).sum(0)) / n
        ma200 = np.nanmean(P[d - 199:d + 1], axis=0)
        trend = np.log(P[d] / ma200)
    return pret, -np.sign(pret) * idm, trend


def make_edge(kind, kappa, kappa_backbone=0.0):
    def edge(k, P, _Q, alive):
        if k < 12 or kappa == 0 and kappa_backbone == 0:
            return np.zeros(P.shape[1])
        pret, key, trend = info_at(k, P)
        if kind == "S1":
            return kappa * rank_normal(pret, alive)
        if kind == "S3":
            return kappa * rank_normal(trend, alive)
        z = np.zeros(P.shape[1])                                   # S2: smoothness within PRET quintiles
        ok = alive & np.isfinite(pret) & np.isfinite(key)
        idx = np.flatnonzero(ok)
        qb = X.buckets(pret[idx], X.N_MOM_Q)
        for b in range(X.N_MOM_Q):
            ii = idx[qb == b]
            if ii.size > 2:
                z[ii] = sps.norm.ppf((sps.rankdata(key[ii]) - 0.5) / ii.size)
        return kappa * z + kappa_backbone * rank_normal(pret, alive)
    return edge


def panel(seed, sig_style, edge=None):
    kw, _ = SY.make_panel(N=N, months=MONTHS, seed=seed, first_research_k=FRK, start=(2006, 1), edge=edge,
                          sig_style=sig_style)
    return X.Features(X.Panel(**kw), horizons=(1,))


def acf(x, k):
    x = np.asarray(x) - np.mean(x)
    return float((x[k:] * x[:-k]).sum() / (x * x).sum())


def mde(rows, p, key, pk):
    pw = np.maximum.accumulate(np.array([r[pk] for r in rows]))
    v = np.array([r[key] for r in rows])
    return float(np.interp(p, pw, v)) if pw.max() >= p else None


def main(name, quick=False):
    t0 = time.time()
    st = SCEN[name]
    R, NP, PP = (60, 15, 6) if quick else (1000, 100, 25)
    out = dict(scenario=name, sig_style=st, N=N, decisions=83, R_null=R, independent_null_panels=NP,
               power_panels_per_point=PP, window=WIN)
    # 1. tethered null on one no-edge panel (full re-estimation in every world)
    F0 = panel(10_000, st)
    fam, nulls = [], []
    for r in range(1, R + 1):
        sm = X.run_world(F0, seed=r, **WIN)
        fam.append(X.family_stat(sm))
        nulls.append(sm)
    c = X.critical_value(fam, X.ALPHA)
    pr = [X.promotion(sm, c) for sm in nulls]
    out["tethered_null"] = dict(c_family_1pct=c,
                                any_stat_above_c=float(np.mean([f > c for f in fam])),
                                full_rule_promotes_S2_S3=float(np.mean([p["outcome"] == "candidate" for p in pr])),
                                full_rule_passes_S1=float(np.mean([p["S1"]["pass"] for p in pr])),
                                t_sd={s: float(np.std([sm[s]["t"] for sm in nulls])) for s in X.SIGNALS})
    print(name, "null done", round(time.time() - t0), "s c =", round(c, 3), flush=True)
    # 2. independent no-edge panels judged with c (data-generating null) + effective sample size
    real, acs, icsd = [], [], {s: [] for s in X.SIGNALS}
    for i in range(NP):
        F = panel(20_000 + i, st)
        sm = X.run_world(F, keep_series=True, **WIN)
        real.append(sm)
        for s in X.SIGNALS:
            ic = [d[s]["ic"] for d in sm["_series"]]
            icsd[s].append(np.std(ic))
            if s == "S1":
                acs.append([acf(ic, k) for k in range(1, 13)])
    pr = [X.promotion(sm, c) for sm in real]
    ac = np.mean(acs, axis=0)
    w = np.array([1 - k / 13.0 for k in range(1, 13)])
    vif = 1 + 2 * float((w * ac).sum())
    out["independent_null"] = dict(
        any_stat_above_c=float(np.mean([X.family_stat(sm) > c for sm in real])),
        full_rule_promotes_S2_S3=float(np.mean([p["outcome"] == "candidate" for p in pr])),
        full_rule_passes_S1=float(np.mean([p["S1"]["pass"] for p in pr])),
        ic_sd_no_edge={s: float(np.mean(v)) for s, v in icsd.items()},
        ic_acf_1_4=[round(float(v), 3) for v in ac[:4]], vif=vif, effective_sample=83 / vif)
    print(name, "independent null done", round(time.time() - t0), "s", json.dumps(out["independent_null"]), flush=True)
    # 3. planted edges
    grids = {"S1": [0.0, 0.002, 0.004, 0.006, 0.009, 0.013], "S2": [0.0, 0.002, 0.004, 0.006, 0.009, 0.013],
             "S3": [0.0, 0.002, 0.004, 0.006, 0.009, 0.013]}
    backbone = 0.006
    out["power"], out["mde"] = {}, {}
    for s, grid in grids.items():
        rows = []
        for kap in grid:
            stat, full, inc, ic, top, gain = 0, 0, 0, [], [], []
            for i in range(PP):
                e = make_edge(s, kap, backbone if s == "S2" else 0.0)
                sm = X.run_world(panel(30_000 + 1000 * grid.index(kap) + i + {"S1": 0, "S2": 100, "S3": 200}[s],
                                       st, e), **WIN)
                p = X.promotion(sm, c)
                stat += sm[s]["t"] > c
                full += p[s]["pass"]
                if s != "S1":
                    inc += sm[s]["t_inc"] > c
                ic.append(sm[s]["ic_mean"])
                top.append(sm[s]["top_ann"])
            rows.append(dict(kappa=kap, power_stat=stat / PP, power_full=full / PP,
                             power_incremental=(inc / PP if s != "S1" else None),
                             ic=float(np.mean(ic)), top_ann=float(np.mean(top))))
            print(name, s, kap, rows[-1], round(time.time() - t0), "s", flush=True)
        out["power"][s] = rows
        out["mde"][s] = {f"p{int(p * 100)}": {f"{m}_{k}": mde(rows, p, k, f"power_{m}")
                                              for m in ("stat", "full") for k in ("ic", "top_ann")}
                         for p in (0.5, 0.8)}
        if s != "S1":
            for p in (0.5, 0.8):
                out["mde"][s][f"p{int(p * 100)}"].update({f"incremental_{k}": mde(rows, p, k, "power_incremental")
                                                          for k in ("ic", "top_ann")})
    out["runtime_s"] = round(time.time() - t0, 1)
    return out


if __name__ == "__main__":
    name = sys.argv[1]
    quick = "--quick" in sys.argv
    res = main(name, quick)
    (HERE / f"P4_xs_e2e_{name}{'_quick' if quick else ''}.json").write_text(json.dumps(res, indent=1, sort_keys=True))
    print("done", res["runtime_s"])
