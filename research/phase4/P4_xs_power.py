"""P4-CP3 design study for cross-sectional technical signal validation. SYNTHETIC DATA ONLY: no market data, no real
signal and no real forward return is used. Answers, before any real computation:

  1. effective sample size of a monthly rank-IC series with overlapping 3-month returns and persistent signals;
  2. the null distribution of the Newey-West t-statistics and the family-wise critical value (max of 5 statistics);
  3. power: the true IC / top-decile excess / decile spread detectable with 50% and 80% probability, for S1 (a signal
     on its own) and for the incremental statistic of S2 (information beyond momentum);
  4. Monthly vs Weekly decision frequency at the same horizon and the same per-year edge;
  5. 1- vs 3- vs 6-month horizons at the same per-month edge.

Panel model (monthly): N = 1,100 stocks; 12 sectors; 4 style factors; idiosyncratic noise. A persistent latent
'momentum information' z (AR(1), phi = 0.90 a month, close to the month-to-month rank persistence of 12-1 momentum).
The signal is aligned with style factor 1 (loading a·z): this is what makes a real signal's IC vary from month to
month even when it has no edge. Its strength a is chosen to give three no-edge IC volatilities (0.06 / 0.10 / 0.15 at
the 3-month horizon), because the real value is unknown before the data is seen and drives every power number.
Smoothness and trend components (w2, w3) have their own persistence and factor alignment; S2 is the sequential sort
of the draft specification; S3 = 0.75 z + 0.66 w3. Edges: monthly expected return kappa1·z + kappa2·w2.
Run: python research/phase4/P4_xs_power.py  ->  research/phase4/P4_xs_power.json
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import qr_xs as X  # noqa: E402

N, T, NSEC, NF = 1100, 92, 12, 4
SIG_SEC, SIG_F, SIG_E = 0.025, 0.030, 0.065
PHI, PHI_W2, PHI_W3 = 0.90, 0.90, 0.80
RHO_NUD, RHO_TS = 0.50, 0.75
HMAX = 6
SEED0 = 20261004


def ranks(A):
    """Row-wise ranks 1..n (synthetic data: no ties)."""
    return np.argsort(np.argsort(A, axis=-1), axis=-1).astype(float) + 1.0


def rowcorr(A, B):
    A = A - A.mean(axis=-1, keepdims=True)
    B = B - B.mean(axis=-1, keepdims=True)
    return (A * B).sum(-1) / np.sqrt((A * A).sum(-1) * (B * B).sum(-1))


def ar1(rng, shape_t, n, phi):
    z = np.empty((shape_t, n))
    z[0] = rng.normal(size=n)
    s = math.sqrt(1 - phi * phi)
    for t in range(1, shape_t):
        z[t] = phi * z[t - 1] + s * rng.normal(size=n)
    return z


def simulate(rng, a, a_w, k1=0.0, k2=0.0, n=N, periods=T + HMAX + 1, phi=PHI, phi2=PHI_W2, phi3=PHI_W3,
             sig_scale=1.0):
    """Latent signals z, w2, w3 at the end of each period 0..periods-1 and returns r[m] for period m = 1..periods-1
    (r[0] unused). Expected return in period m = k1 z[m-1] + k2 w2[m-1]."""
    z, w2, w3 = ar1(rng, periods, n, phi), ar1(rng, periods, n, phi2), ar1(rng, periods, n, phi3)
    sec = rng.integers(0, NSEC, n)
    u = rng.normal(size=(NF, n))
    r = np.zeros((periods, n))
    Fs = rng.normal(0, SIG_SEC * sig_scale, (periods, NSEC))
    Ff = rng.normal(0, SIG_F * sig_scale, (periods, NF))
    E = rng.normal(0, SIG_E * sig_scale, (periods, n))
    for m in range(1, periods):
        L = u.copy()
        L[0] = a * z[m - 1] + math.sqrt(1 - a * a) * u[0]
        L[1] = a_w * w2[m - 1] + math.sqrt(1 - a_w * a_w) * u[1]
        L[2] = a_w * w3[m - 1] + math.sqrt(1 - a_w * a_w) * u[2]
        r[m] = k1 * z[m - 1] + k2 * w2[m - 1] + Fs[m, sec] + Ff[m] @ L + E[m]
    return z, w2, w3, r


def forward(r, h, t_dec):
    """Forward h-period returns for decisions t = 0..t_dec-1 (sum of periods t+1..t+h)."""
    c = np.cumsum(r, axis=0)
    idx = np.arange(t_dec)
    return c[idx + h] - c[idx]


def full_stats(z, w2, w3, r, h=X.H_MONTHS, t_dec=T):
    """Primary-horizon statistics of the draft specification, vectorised over decision dates."""
    S1 = z[:t_dec]
    nud = RHO_NUD * S1 + math.sqrt(1 - RHO_NUD ** 2) * w2[:t_dec]
    S3 = RHO_TS * S1 + math.sqrt(1 - RHO_TS ** 2) * w3[:t_dec]
    Y = forward(r, h, t_dec)
    Y = Y - Y.mean(axis=1, keepdims=True)
    RY, R1, R3 = ranks(Y), ranks(S1), ranks(S3)
    n = S1.shape[1]
    q = n // X.N_MOM_Q
    o = np.argsort(S1, axis=1)                                          # MOM order -> contiguous quintile slices
    take = lambda A: np.take_along_axis(A, o, axis=1).reshape(t_dec, X.N_MOM_Q, q)
    Yq, Mq, Nq, Tq = take(Y), take(S1), take(nud), take(S3)
    rYq, rMq, rNq, rTq = ranks(Yq), ranks(Mq), ranks(Nq), ranks(Tq)
    # S2 rank = quintile block offset + within-quintile NUD rank
    R2q = rNq + (np.arange(X.N_MOM_Q) * q)[None, :, None]
    ic2 = rowcorr(R2q.reshape(t_dec, n), ranks(Yq.reshape(t_dec, n)))       # same (MOM-ordered) coordinates

    def inc(rC):
        ryc, rym, rcm = rowcorr(rYq, rC), rowcorr(rYq, rMq), rowcorr(rC, rMq)
        return ((ryc - rym * rcm) / np.sqrt((1 - rym ** 2) * (1 - rcm ** 2))).mean(axis=1)

    d = ((R1 - 1) * X.N_DECILES // n).astype(int)
    dec = np.stack([(Y * (d == k)).sum(1) / (d == k).sum(1) for k in range(X.N_DECILES)], axis=1)
    return dict(ic1=rowcorr(R1, RY), ic2=ic2, ic3=rowcorr(R3, RY), inc2=inc(rNq), inc3=inc(rTq), dec1=dec)


def tstats(st, lag=X.NW_LAG):
    return dict(t1=X.nw_tstat(st["ic1"], lag)[2], t2=X.nw_tstat(st["ic2"], lag)[2], t3=X.nw_tstat(st["ic3"], lag)[2],
                t2i=X.nw_tstat(st["inc2"], lag)[2], t3i=X.nw_tstat(st["inc3"], lag)[2])


def acf(x, k):
    x = x - x.mean()
    return float((x[k:] * x[:-k]).sum() / (x * x).sum())


# --------------------------------------------------------------------------------------------- 1. calibration
def calibrate(rng):
    out = {}
    for a in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        sd, ac = [], []
        for _ in range(12):
            z, w2, w3, r = simulate(rng, a, a / 2)
            ic = full_stats(z, w2, w3, r)["ic1"]
            sd.append(ic.std())
        out[a] = float(np.mean(sd))
    return out


def pick_a(cal, target):
    a = np.array(sorted(cal))
    v = np.array([cal[k] for k in a])
    return float(np.interp(target, v, a))


# --------------------------------------------------------------------------------------------- 2.-3. null and power
def run_null(rng, a, R):
    rows, ac, vif = [], [], []
    for _ in range(R):
        z, w2, w3, r = simulate(rng, a, a / 2)
        st = full_stats(z, w2, w3, r)
        ts = tstats(st)
        rows.append(ts)
        ic = st["ic1"]
        rho = [acf(ic, k) for k in range(1, 13)]
        ac.append(rho)
    fam = np.array([max(t.values()) for t in rows])
    single = np.array([t["t1"] for t in rows])
    ac = np.mean(ac, axis=0)
    w = np.array([1 - k / 13.0 for k in range(1, 13)])
    vif_bartlett = 1 + 2 * float((w * ac).sum())
    return dict(R=R, c_family_1pct=X.critical_value(fam, 0.01), c_family_5pct=X.critical_value(fam, 0.05),
                c_single_1pct=X.critical_value(single, 0.01), c_single_5pct=X.critical_value(single, 0.05),
                single_t_sd=float(single.std()), single_frac_gt_2_33=float((single > 2.326).mean()),
                ic_acf_1_6=[round(float(v), 3) for v in ac[:6]], vif=vif_bartlett, t_eff=T / vif_bartlett)


def run_power(rng, a, kind, grid, c, R):
    """kind 's1': edge on z (k1); kind 'inc2': edge on the smoothness component w2 (k2), with a fixed k1."""
    res = []
    for k in grid:
        hits, ics, incs, top, spr = 0, [], [], [], []
        for _ in range(R):
            if kind == "s1":
                z, w2, w3, r = simulate(rng, a, a / 2, k1=k)
            else:
                z, w2, w3, r = simulate(rng, a, a / 2, k1=0.002, k2=k)
            st = full_stats(z, w2, w3, r)
            ts = tstats(st)
            hits += (ts["t1"] > c) if kind == "s1" else (ts["t2i"] > c)
            ics.append(st["ic1"].mean())
            incs.append(st["inc2"].mean())
            dm = st["dec1"].mean(0)
            top.append(dm[-1] * 12 / X.H_MONTHS)
            spr.append((dm[-1] - dm[0]) * 12 / X.H_MONTHS)
        res.append(dict(kappa=k, power=hits / R, ic=float(np.mean(ics)), inc=float(np.mean(incs)),
                        top_ann=float(np.mean(top)), spread_ann=float(np.mean(spr))))
    return res


def mde(res, p, key):
    pw = np.array([r["power"] for r in res])
    v = np.array([r[key] for r in res])
    if pw.max() < p:
        return None
    return float(np.interp(p, np.maximum.accumulate(pw), v))


# --------------------------------------------------------------------------------------------- 4. weekly vs monthly
def weekly_vs_monthly(rng, a, kappa_month, R):
    """Weekly panel; 'monthly' design = decisions every 4 weeks; 'weekly' = every week; horizon 13 weeks."""
    wk = 52 / 12
    phi_w = PHI ** (1 / wk)
    k_w = kappa_month / wk
    weeks = 13 * 31 + 13 + 1                                             # ~ 7.75 years of decisions
    hw = 13
    designs = {"monthly(4w)": (4, 6), "weekly": (1, 26)}
    out = {}
    tsn = {d: [] for d in designs}
    tsa = {d: [] for d in designs}
    for mode, store in (("null", tsn), ("alt", tsa)):
        for _ in range(R):
            z, w2, w3, r = simulate(rng, a, a / 2, k1=(0.0 if mode == "null" else k_w), periods=weeks, phi=phi_w,
                                    phi2=PHI_W2 ** (1 / wk), phi3=PHI_W3 ** (1 / wk), sig_scale=1 / math.sqrt(wk))
            tdec = weeks - hw - 1
            Y = forward(r, hw, tdec)
            ic = rowcorr(ranks(z[:tdec]), ranks(Y))
            for d, (step, lag) in designs.items():
                store[d].append(X.nw_tstat(ic[::step], lag)[2])
    for d in designs:
        c = X.critical_value(tsn[d], 0.01)
        out[d] = dict(decisions=len(range(0, weeks - hw - 1, designs[d][0])), nw_lag=designs[d][1],
                      c_1pct=c, null_sd=float(np.std(tsn[d])), power_at_edge=float(np.mean(np.array(tsa[d]) > c)))
    out["edge_kappa_per_month"] = kappa_month
    return out


# --------------------------------------------------------------------------------------------- 5. horizons
def horizons(rng, a, kappa, R):
    out = {}
    for h in (1, 3, 6):
        lag = 2 * h
        tn, ta = [], []
        for mode, store in (("null", tn), ("alt", ta)):
            for _ in range(R):
                z, w2, w3, r = simulate(rng, a, a / 2, k1=(0.0 if mode == "null" else kappa))
                tdec = T + 3 - h                                         # decisions end when returns reach Dec-2017
                Y = forward(r, h, tdec)
                ic = rowcorr(ranks(z[:tdec]), ranks(Y))
                store.append(X.nw_tstat(ic, lag)[2])
        c = X.critical_value(tn, 0.01)
        out[f"{h}m"] = dict(decisions=T + 3 - h, overlap_months=h - 1, nw_lag=lag, c_1pct=c,
                            null_sd=float(np.std(tn)), power_at_edge=float(np.mean(np.array(ta) > c)))
    out["edge_kappa_per_month"] = kappa
    return out


def main(quick=False):
    t0 = time.time()
    rng = np.random.default_rng(SEED0)
    R_NULL, R_POW, R_CMP = (200, 60, 120) if quick else (1000, 200, 400)
    cal = calibrate(rng)
    targets = {"low": 0.06, "mid": 0.10, "high": 0.15}
    scen = {k: pick_a(cal, v) for k, v in targets.items()}
    res = dict(model=dict(N=N, T_decisions=T, sectors=NSEC, style_factors=NF, sig_sector=SIG_SEC, sig_style=SIG_F,
                          sig_idio=SIG_E, phi=PHI, phi_w2=PHI_W2, phi_w3=PHI_W3, rho_nud=RHO_NUD, rho_ts=RHO_TS,
                          horizon_months=X.H_MONTHS, nw_lag=X.NW_LAG, seed=SEED0),
               calibration_ic_sd_by_alignment={str(k): v for k, v in cal.items()},
               scenarios={k: dict(target_ic_sd=targets[k], alignment=scen[k]) for k in targets})
    grid_s1 = [0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.0065, 0.008]
    grid_inc = [0.0, 0.0005, 0.001, 0.0015, 0.002, 0.003, 0.004]
    for name, a in scen.items():
        nl = run_null(rng, a, R_NULL)
        c = nl["c_family_1pct"]
        p1 = run_power(rng, a, "s1", grid_s1, c, R_POW)
        p2 = run_power(rng, a, "inc2", grid_inc, c, R_POW)
        res["scenarios"][name].update(
            null=nl, power_s1=p1, power_inc2=p2,
            mde_s1={f"p{int(p * 100)}": {k: mde(p1, p, k) for k in ("ic", "top_ann", "spread_ann")} for p in (0.5, 0.8)},
            mde_inc2={f"p{int(p * 100)}": {k: mde(p2, p, k) for k in ("inc", "top_ann")} for p in (0.5, 0.8)})
        print(name, round(time.time() - t0), "s", json.dumps(res["scenarios"][name]["mde_s1"]), flush=True)
    a_mid = scen["mid"]
    res["weekly_vs_monthly"] = weekly_vs_monthly(rng, a_mid, 0.004, R_CMP)
    res["horizons"] = horizons(rng, a_mid, 0.004, R_CMP)
    res["runtime_s"] = round(time.time() - t0, 1)
    return res


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    out = main(quick)
    path = ROOT / "research" / "phase4" / ("P4_xs_power_quick.json" if quick else "P4_xs_power.json")
    path.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: out[k] for k in ("weekly_vs_monthly", "horizons", "runtime_s")}, indent=1))
