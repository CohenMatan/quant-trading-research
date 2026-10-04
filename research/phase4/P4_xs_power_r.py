"""P4-CP3R synthetic power study for the CORRECTED H019 design (1-month primary horizon, 82 monthly decisions
2011-02 .. 2017-11, Newey-West lag 2, the full promotion rule of qr_xs, family-wise alpha = 1%).
SYNTHETIC DATA ONLY: no market data, no real signal and no real forward return is used.

Same panel model as P4_xs_power.py (P4-CP3): N = 1,100 stocks, 12 sectors, 4 style factors, persistent latent
momentum information z (phi 0.90), a smoothness component w2 and a trend component w3. The three IC-noise scenarios
keep the P4-CP3 factor alignments (defined by a 3-month no-edge IC volatility of 0.06 / 0.10 / 0.15), so the 1-month
and 3-month figures describe the same synthetic world. Reported per scenario:
  - effective sample size of the primary IC series; naive-test over-rejection; null critical values;
  - false-pass rates under the null: the statistical gate alone and the complete promotion rule;
  - power and the minimum detectable effects (rank IC, top-decile excess, decile spread) at 50% and 80%;
  - the probability that a true effect passes the COMPLETE rule (economic floor included);
  - the incremental (smoothness beyond momentum) test;
  - the 3-month horizon (lag 6, 80 decisions) for comparison only.
Monotonicity (P2) is judged on quintiles (S2's decile zig-zag artefact, P4-CP3R §18).
Run: python research/phase4/P4_xs_power_r.py  ->  research/phase4/P4_xs_power_r.json
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
sys.path.insert(0, str(HERE))
import qr_xs as X  # noqa: E402
import P4_xs_power as B  # noqa: E402  (panel model of P4-CP3, unchanged)

T_PRIMARY = 82                      # 2011-02 .. 2017-11
T_DIAG3 = 80                        # 2011-02 .. 2017-09
SEED0 = 20261005
SCEN = {"low": 0.206, "mid": 0.367, "high": 0.564}   # P4-CP3 alignments (3-month IC sd 0.06 / 0.10 / 0.15)


def years_of(t_dec):
    return [2011 + (t + 1) // 12 for t in range(t_dec)]


def stats(z, w2, w3, r, h, t_dec):
    """Per-date ICs, decile means for S1-S3 and incremental statistics (vectorised over dates)."""
    n = z.shape[1]
    S1 = z[:t_dec]
    key = B.RHO_NUD * S1 + math.sqrt(1 - B.RHO_NUD ** 2) * w2[:t_dec]
    S3 = B.RHO_TS * S1 + math.sqrt(1 - B.RHO_TS ** 2) * w3[:t_dec]
    Y = B.forward(r, h, t_dec)
    Y = Y - Y.mean(axis=1, keepdims=True)
    q = n // X.N_MOM_Q
    o = np.argsort(S1, axis=1)
    take = lambda A: np.take_along_axis(A, o, axis=1).reshape(t_dec, X.N_MOM_Q, q)
    Yq, Mq, Kq, Tq = take(Y), take(S1), take(key), take(S3)
    rYq, rMq, rKq, rTq = B.ranks(Yq), B.ranks(Mq), B.ranks(Kq), B.ranks(Tq)
    Yo = Yq.reshape(t_dec, n)
    R2 = (rKq + (np.arange(X.N_MOM_Q) * q)[None, :, None]).reshape(t_dec, n)   # S2 rank (MOM-ordered coordinates)
    RYo = B.ranks(Yo)
    R1o = np.broadcast_to(np.arange(1, n + 1, dtype=float), (t_dec, n))      # S1 rank in its own order
    R3o = B.ranks(Tq.reshape(t_dec, n))

    def inc(rC):
        ryc, rym, rcm = B.rowcorr(rYq, rC), B.rowcorr(rYq, rMq), B.rowcorr(rC, rMq)
        return ((ryc - rym * rcm) / np.sqrt((1 - rym ** 2) * (1 - rcm ** 2))).mean(axis=1)

    def dec(R):
        d = ((R - 1) * X.N_DECILES // n).astype(int)
        return np.stack([(Yo * (d == k)).sum(1) / (d == k).sum(1) for k in range(X.N_DECILES)], axis=1)

    return dict(ic={"S1": B.rowcorr(R1o, RYo), "S2": B.rowcorr(R2, RYo), "S3": B.rowcorr(R3o, RYo)},
                dec={"S1": dec(R1o), "S2": dec(R2), "S3": dec(R3o)},
                inc={"S2": inc(rKq), "S3": inc(rTq)})


def summary(st, h, lag, years):
    yrs = np.asarray(years)
    out = {}
    for s in X.SIGNALS:
        ic, dec = st["ic"][s], st["dec"][s]
        m, se, t = X.nw_tstat(ic, lag)
        md = dec.mean(axis=0)
        q5 = np.array([(md[2 * k] + md[2 * k + 1]) / 2 for k in range(X.N_MONO_Q)])   # equal-count decile pairs
        out[s] = dict(ic_mean=m, t=t, top_ann=float(md[-1]) * 12 / h, spread_ann=float(md[-1] - md[0]) * 12 / h,
                      mono=X.spearman(np.arange(X.N_MONO_Q, dtype=float), q5),
                      q_gap=float(q5[-1] - q5[0]),
                      sub=[float(ic[:ic.size // 2].mean()), float(ic[ic.size // 2:].mean())],
                      block_max=X.block_share_max(ic, yrs))
        if s in X.INCREMENTAL:
            out[s]["inc_mean"], _, out[s]["t_inc"] = X.nw_tstat(st["inc"][s], lag)
    return out


def world(rng, a, k1=0.0, k2=0.0, h=1, t_dec=T_PRIMARY, lag=X.NW_LAG):
    z, w2, w3, r = B.simulate(rng, a, a / 2, k1=k1, k2=k2, periods=t_dec + h + 1)
    st = stats(z, w2, w3, r, h, t_dec)
    return st, summary(st, h, lag, years_of(t_dec))


def run_null(rng, a, R, h=1, t_dec=T_PRIMARY, lag=X.NW_LAG):
    fam, single, sums, acs = [], [], [], []
    for _ in range(R):
        st, sm = world(rng, a, h=h, t_dec=t_dec, lag=lag)
        fam.append(X.family_stat(sm))
        single.append(sm["S1"]["t"])
        sums.append(sm)
        ic = st["ic"]["S1"]
        acs.append([B.acf(ic, k) for k in range(1, 13)])
    c = X.critical_value(fam, X.ALPHA)
    ac = np.mean(acs, axis=0)
    w = np.array([1 - k / 13.0 for k in range(1, 13)])
    vif = 1 + 2 * float((w * ac).sum())
    single = np.array(single)
    stat_any = np.mean([any(sm[s]["t"] > c for s in X.SIGNALS) or any(sm[s]["t_inc"] > c for s in X.INCREMENTAL)
                        for sm in sums])
    full = [X.promotion(sm, c) for sm in sums]
    return dict(R=R, c_family_1pct=c, c_single_1pct=X.critical_value(single, 0.01),
                naive_reject_1pct=float((single > 2.326).mean()), null_t_sd=float(single.std()),
                ic_sd_no_edge=float(np.mean([np.std(s) for s in [world(rng, a, h=h, t_dec=t_dec, lag=lag)[0]["ic"]["S1"]
                                                                  for _ in range(20)]])),
                ic_acf_1_4=[round(float(v), 3) for v in ac[:4]], vif=vif, t_eff=t_dec / vif,
                false_pass_statistical_any=float(stat_any),
                false_pass_full_rule_S2_S3=float(np.mean([p["outcome"] == "candidate" for p in full])),
                false_pass_full_rule_S1=float(np.mean([p["S1"]["pass"] for p in full])))


def run_power(rng, a, kind, grid, c, R, h=1, t_dec=T_PRIMARY, lag=X.NW_LAG):
    res = []
    for k in grid:
        hit, full, ics, incs, top, spr, gain = 0, 0, [], [], [], [], []
        for _ in range(R):
            st, sm = world(rng, a, k1=(k if kind == "s1" else 0.002), k2=(k if kind == "inc2" else 0.0), h=h,
                           t_dec=t_dec, lag=lag)
            p = X.promotion(sm, c)
            if kind == "s1":
                hit += sm["S1"]["t"] > c
                full += p["S1"]["pass"]
            else:
                hit += sm["S2"]["t_inc"] > c
                full += p["S2"]["pass"]
            ics.append(sm["S1"]["ic_mean"])
            incs.append(sm["S2"]["inc_mean"])
            top.append(sm["S1"]["top_ann"])
            spr.append(sm["S1"]["spread_ann"])
            gain.append(sm["S2"]["top_ann"] - sm["S1"]["top_ann"])
        res.append(dict(kappa=k, power=hit / R, power_full_rule=full / R, ic=float(np.mean(ics)),
                        inc=float(np.mean(incs)), top_ann=float(np.mean(top)), spread_ann=float(np.mean(spr)),
                        s2_minus_s1_top_ann=float(np.mean(gain))))
    return res


def mde(res, p, key, pk="power"):
    pw = np.maximum.accumulate(np.array([r[pk] for r in res]))
    v = np.array([r[key] for r in res])
    return float(np.interp(p, pw, v)) if pw.max() >= p else None


def main(quick=False):
    t0 = time.time()
    rng = np.random.default_rng(SEED0)
    R_NULL, R_POW = (150, 40) if quick else (1000, 200)
    grid_s1 = [0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.0065, 0.008, 0.010]
    grid_inc = [0.0, 0.0005, 0.001, 0.0015, 0.002, 0.003, 0.004]
    out = dict(design=dict(primary_h=1, nw_lag=X.NW_LAG, decisions=T_PRIMARY, alpha=X.ALPHA, diag_h=3,
                           diag_nw_lag=6, diag_decisions=T_DIAG3, seed=SEED0, N=B.N, alignments=SCEN),
               scenarios={})
    for name, a in SCEN.items():
        nl = run_null(rng, a, R_NULL)
        c = nl["c_family_1pct"]
        p1 = run_power(rng, a, "s1", grid_s1, c, R_POW)
        p2 = run_power(rng, a, "inc2", grid_inc, c, R_POW)
        nl3 = run_null(rng, a, R_NULL // 2, h=3, t_dec=T_DIAG3, lag=6)
        p13 = run_power(rng, a, "s1", grid_s1, nl3["c_family_1pct"], R_POW // 2, h=3, t_dec=T_DIAG3, lag=6)
        sc = dict(null=nl, power_s1=p1, power_inc2=p2, diag3_null=nl3, diag3_power_s1=p13,
                  mde_s1={f"p{int(p * 100)}": {k: mde(p1, p, k) for k in ("kappa", "ic", "top_ann", "spread_ann")}
                          for p in (0.5, 0.8)},
                  mde_s1_full_rule={f"p{int(p * 100)}": {k: mde(p1, p, k, "power_full_rule")
                                                         for k in ("kappa", "ic", "top_ann")} for p in (0.5, 0.8)},
                  mde_inc2={f"p{int(p * 100)}": {k: mde(p2, p, k) for k in ("kappa", "inc", "s2_minus_s1_top_ann")}
                            for p in (0.5, 0.8)},
                  diag3_mde_s1={f"p{int(p * 100)}": {k: mde(p13, p, k) for k in ("kappa", "ic", "top_ann")}
                                for p in (0.5, 0.8)})
        out["scenarios"][name] = sc
        print(name, round(time.time() - t0), "s", json.dumps(sc["mde_s1"]), json.dumps(sc["diag3_mde_s1"]),
              flush=True)
    out["runtime_s"] = round(time.time() - t0, 1)
    return out


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    res = main(quick)
    path = HERE / ("P4_xs_power_r_quick.json" if quick else "P4_xs_power_r.json")
    path.write_text(json.dumps(res, indent=1, sort_keys=True))
    print("done", res["runtime_s"])
