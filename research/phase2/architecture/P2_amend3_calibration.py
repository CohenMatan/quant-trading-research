"""Amendment 3 calibration (P2-CP12, owner 2026-10-02 refinements 1 and 2). Uses ONLY already-completed control books
on 2010-03-01 -> 2021-12-31: SPY total return (E900-07), the same-universe equal-weight benchmark EW-H016 (E016-02)
and five random 20-stock books (E016-03..07). No candidate or factor returns.

Part 1, serial dependence of relative performance: for each control book's daily excess log return over SPY,
d_t = log(1 + r_book) - log(1 + r_SPY): autocorrelations and variance ratios VR(h) = Var(h-day sums) / (h Var(d)).

Part 2, W2 standard-error methods for g = 252 * mean(d) (annualised log-wealth-ratio growth; g > 0 <=> terminal
wealth above SPY), test "g >= 1.645 * SE":
  iid      SE = TE / sqrt(years)                                   (the P2-CP11 proposal)
  NW63     Newey-West / Bartlett HAC, 63 daily lags
  NW252    Newey-West / Bartlett HAC, 252 daily lags
  SB63     stationary bootstrap (Politis & Romano 1994), mean block 63 days: exact bootstrap variance of the mean
  SB126    the same, mean block 126 days
  SB252    the same, mean block 252 days
The stationary-bootstrap variance is computed exactly (Politis & Romano 1994, Lemma 1), so the test is deterministic
(no Monte Carlo noise). Calibration: null histories of 12 years are generated from the demeaned control excess
series with different dependence structures (iid; stationary-bootstrap DGPs with mean blocks 21, 63, 126, 252, 504
days), and the false-pass rate of each method is measured. A method qualifies if its false-pass rate stays at or
below about 5% across the DGPs with realistic persistence.

Part 3, R2 tolerance: sampling distribution of Sharpe(book) - Sharpe(SPY) for 20-stock books with no edge (joint
block bootstrap of the controls), and the implied probability of wrongly rejecting a candidate whose true Sharpe
equals SPY's, for tolerances 0, 0.05, 0.10, 0.15, 0.20.

Part 4, operating characteristics of the final Amendment 3 (W1, W2 = chosen method, W3, R1, R2 = chosen tolerance,
R3), on the currently feasible architecture (12 years, 20 positions) and, for reference, 40 positions.

    PYTHONPATH=src python research/phase2/architecture/P2_amend3_calibration.py -> P2_amend3_calibration.json
"""
import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import wealth  # noqa: E402

START, END = "2010-03-01", "2021-12-31"
IDS = dict(SPY="E900-07", EW="E016-02", R1="E016-03", R2="E016-04", R3="E016-05", R4="E016-06", R5="E016-07")
SEED = 20261004
N_NULL = 4000
N_OC = 2000
Z = 1.645
DGP_BLOCKS = (None, 21, 63, 126, 252, 504)       # None = iid
METHODS = ("iid", "NW63", "NW252", "SB63", "SB126", "SB252", "max(iid,SB126)", "max(iid,SB252)")
PERSIST = ((0.989, 1.25), (0.989, 1.5), (0.989, 2.0), (0.9973, 1.25), (0.9973, 1.5), (0.9973, 2.0))   # (daily AR(1) of a slow drift, target VR(252))
EDGES = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09)
TOLS = (0.0, 0.05, 0.10, 0.15, 0.20)


def daily(eid):
    df = pd.read_csv(gzip.open(ROOT / "experiments" / eid / "equity.csv.gz"))
    eq = pd.Series(df["equity"].to_numpy(float), index=df["date"].astype(str))
    eq = eq[(eq.index >= START) & (eq.index <= END)]
    return eq.pct_change().dropna()


def se_methods(d):
    n = len(d)
    out = {"iid": wealth.se_iid(d)}
    for L in (63, 252):
        out[f"NW{L}"] = wealth.se_newey_west(d, L)
    for b in (63, 126, 252):
        out[f"SB{b}"] = wealth.se_stationary_bootstrap(d, b)
    out["max(iid,SB126)"] = max(out["iid"], out["SB126"])
    out["max(iid,SB252)"] = max(out["iid"], out["SB252"])
    return out


def persistent_component(rng, n, phi, var_daily):
    """Zero-mean AR(1) drift m_t (stationary start) with daily variance var_daily."""
    e = rng.normal(0.0, math.sqrt(var_daily * (1 - phi ** 2)), n)
    m = np.empty(n)
    m[0] = rng.normal(0.0, math.sqrt(var_daily))
    for t in range(1, n):
        m[t] = phi * m[t - 1] + e[t]
    return m


def drift_scale(phi, base_var, target_vr, h=252):
    """Daily variance of an AR(1) drift that lifts VR(h) of (iid noise + drift) to target_vr."""
    k = np.arange(1, h)
    vr_ar = 1 + 2 * np.sum((1 - k / h) * phi ** k)       # VR(h) of a pure AR(1)
    # VR = (base_var + v * vr_ar) / (base_var + v)  ->  v = base_var (target - 1) / (vr_ar - target)
    return base_var * (target_vr - 1) / (vr_ar - target_vr)


def sb_index(rng, n_pool, n_out, block):
    if block is None:
        return rng.integers(n_pool, size=n_out)
    flags = rng.random(n_out) < 1.0 / block
    flags[0] = True
    pos = np.flatnonzero(flags)
    seg = np.cumsum(flags) - 1
    starts = rng.integers(n_pool, size=len(pos))
    return (starts[seg] + np.arange(n_out) - pos[seg]) % n_pool


def variance_ratio(d, h):
    """Overlapping h-day variance ratio."""
    c = np.concatenate([[0.0], np.cumsum(d - d.mean())])
    s = c[h:] - c[:-h]
    return float(s.var(ddof=1) / (h * d.var(ddof=1)))


def main():
    R = pd.concat({k: daily(v) for k, v in IDS.items()}, axis=1, join="inner").dropna()
    X = R.to_numpy(float)
    spy, ew, rnd = X[:, 0], X[:, 1], X[:, 2:]
    n = len(X)
    years = n / 252
    books = {"EW": ew, **{f"R{j + 1}": rnd[:, j] for j in range(5)}}
    out = dict(window=[START, END], days=n, inputs=IDS, seed=SEED, z=Z)
    # ---- Part 1: dependence
    dep = {}
    for k, b in books.items():
        d = np.log1p(b) - np.log1p(spy)
        dc = d - d.mean()
        ac = [float(np.dot(dc[:-L], dc[L:]) / np.dot(dc, dc)) for L in (1, 2, 5, 21, 63)]
        dep[k] = dict(te=float(d.std(ddof=1) * math.sqrt(252)), acf={L: a for L, a in zip((1, 2, 5, 21, 63), ac)},
                      vr={h: variance_ratio(d, h) for h in (5, 21, 63, 126, 252)},
                      se={m: float(v) for m, v in se_methods(d).items()},
                      g=float(252 * d.mean()))
    out["dependence"] = dep
    vr_mean = {h: float(np.mean([dep[k]["vr"][h] for k in dep])) for h in (5, 21, 63, 126, 252)}
    out["dependence_mean_vr"] = vr_mean
    # ---- Part 2: null calibration of W2 methods
    rng = np.random.default_rng(SEED)
    pool = np.column_stack([np.log1p(books[k]) - np.log1p(spy) for k in books])
    pool = pool - pool.mean(axis=0)
    cal = {}
    for blk in DGP_BLOCKS:
        hits = {m: 0 for m in METHODS}
        for i in range(N_NULL):
            col = pool[:, i % pool.shape[1]]
            d = col[sb_index(rng, n, n, blk)]
            g = 252 * d.mean()
            ses = se_methods(d)
            for m in METHODS:
                hits[m] += bool(g >= Z * ses[m])
            hits["FINAL"] = hits.get("FINAL", 0) + bool(g >= wealth.W2_CRITICAL * wealth.se_w2(d))
        cal["iid" if blk is None else f"SB-DGP mean block {blk}"] = {m: hits[m] / N_NULL for m in list(METHODS) + ["FINAL"]}
    # synthetic PERSISTENT relative performance (style regimes): iid-resampled control noise + a slow AR(1) drift
    for phi, target in PERSIST:
        hits = {m: 0 for m in METHODS}
        for i in range(N_NULL):
            col = pool[:, i % pool.shape[1]]
            base = col[sb_index(rng, n, n, None)]
            v = drift_scale(phi, float(base.var()), target)
            d = base + persistent_component(rng, n, phi, v)
            d = d - 0.0
            g = 252 * d.mean()
            ses = se_methods(d)
            for m in METHODS:
                hits[m] += bool(g >= Z * ses[m])
            hits["FINAL"] = hits.get("FINAL", 0) + bool(g >= wealth.W2_CRITICAL * wealth.se_w2(d))
        cal[f"persistent drift phi={phi}, VR252={target}"] = {m: hits[m] / N_NULL for m in list(METHODS) + ["FINAL"]}
    out["w2_null_false_pass"] = cal
    out["w2_note"] = ("Columns other than FINAL use z = 1.645. FINAL = the frozen rule: g >= W2_CRITICAL x "
                      "max(iid SE, stationary-bootstrap SE, mean block W2_MEAN_BLOCK).")
    # ---- Part 3: R2 tolerance (no-edge 20-stock books vs SPY; joint bootstrap of controls, mean block 63)
    u = (ew - spy) - (ew - spy).mean()
    s = (rnd - ew[:, None]) - (rnd - ew[:, None]).mean(axis=0)
    dsr = []
    for i in range(N_OC):
        ix = sb_index(rng, n, n, 63)
        sp = spy[ix]
        h = sp + u[ix] + s[ix, i % 5]
        dsr.append(wealth.sharpe(h) - wealth.sharpe(sp))
    dsr = np.array(dsr)
    sd = float(dsr.std(ddof=1))
    from math import erf
    phi = lambda x: 0.5 * (1 + erf(x / math.sqrt(2)))   # noqa: E731
    mu_s, sig_s = float(spy.mean() * 252), float(spy.std(ddof=1) * math.sqrt(252))
    r2 = {}
    for t in TOLS:
        # max volatility a candidate with +3%/yr arithmetic excess may carry while meeting R2 (in multiples of SPY vol)
        vmax = (mu_s + 0.03) / (mu_s / sig_s - t) / sig_s
        r2[f"{t:.2f}"] = dict(wrong_reject_equal_true_sharpe=phi(-t / sd), max_vol_multiple_at_plus3pct=vmax)
    out["r2"] = dict(sd_sharpe_diff_no_edge_book=sd, mean_sharpe_diff_no_edge_book=float(dsr.mean()),
                     spy_mean_arith=mu_s, spy_vol=sig_s, by_tolerance=r2)
    out["choice"] = dict(w2_method=wealth.W2_METHOD, w2_block=wealth.W2_MEAN_BLOCK, w2_critical=wealth.W2_CRITICAL,
                         r2_tolerance=wealth.R2_TOLERANCE, r1_max_extra_dd=wealth.R1_MAX_EXTRA_DD)
    # ---- Part 4: operating characteristics of the FINAL rule set (wealth.evaluate_gates) under a persistent DGP
    oc = {}
    z_frozen = wealth.W2_CRITICAL
    alt = {}
    for z_alt in (1.645, 1.96):                      # the same full rule set with a different W2 critical value
        wealth.W2_CRITICAL = z_alt
        rows = {}
        idxs = [sb_index(rng, n, n, 126) for _ in range(N_OC)]
        for a in EDGES:
            c = 0
            for b, ix in enumerate(idxs):
                k = b % 5
                sp = spy[ix]
                e = sp + u[ix]
                h = e + s[ix, k] + a / 252
                others = [s[ix][:, j] for j in range(5) if j != k] + [np.roll(s[:, k], n // 2)[ix]]
                c += wealth.evaluate_gates(h, sp, e, list((e[:, None] + np.column_stack(others)).T))["qualified"]
            rows[f"{a:.2f}"] = dict(all=c / N_OC)
        alt[f"z={z_alt}"] = rows
    wealth.W2_CRITICAL = z_frozen
    for npos in (20, 40):
        sc = math.sqrt(20 / npos)
        for dgp_blk in (126, 252):
            key = f"12y, {npos} positions, DGP mean block {dgp_blk}"
            oc[key] = {}
            idxs = [sb_index(rng, n, n, dgp_blk) for _ in range(N_OC)]
            for a in EDGES:
                cnt = dict(all=0, W1=0, W2=0, W3=0, R=0)
                for b, ix in enumerate(idxs):
                    k = b % 5
                    sp = spy[ix]
                    e = sp + u[ix]
                    h = e + s[ix, k] * sc + a / 252
                    others = [s[ix][:, j] for j in range(5) if j != k] + [np.roll(s[:, k], n // 2)[ix]]
                    ctl = e[:, None] + np.column_stack(others) * sc     # five matched random books
                    gt = wealth.evaluate_gates(h, sp, e, list(ctl.T))
                    cnt["all"] += gt["qualified"]
                    cnt["W1"] += gt["W1"]["ok"]
                    cnt["W2"] += gt["W2"]["ok"]
                    cnt["W3"] += gt["W3"]["ok"]
                    cnt["R"] += gt["R1"]["ok"] and gt["R2"]["ok"] and gt["R3"]["ok"]
                oc[key][f"{a:.2f}"] = {k2: v / N_OC for k2, v in cnt.items()}
    out["final_operating_characteristics"] = oc

    def edge_for(rows, p):
        xs = sorted(float(a) for a in rows)
        ys = [rows[f"{a:.2f}"]["all"] for a in xs]
        for i in range(1, len(xs)):
            if ys[i - 1] < p <= ys[i]:
                return xs[i - 1] + (p - ys[i - 1]) / (ys[i] - ys[i - 1]) * (xs[i] - xs[i - 1])
        return None if ys[-1] < p else xs[0]
    out["final_power_summary"] = {k: dict(false_pass=v["0.00"]["all"], **{f"pass_at_{e}%": v[f"0.0{e}"]["all"]
                                                                            for e in (1, 2, 3, 4)},
                                          edge_for_50pct=edge_for(v, 0.5), edge_for_80pct=edge_for(v, 0.8))
                                  for k, v in oc.items()}
    out["alternative_critical_values_12y_20pos_dgp126"] = {
        k: dict(false_pass=v["0.00"]["all"], **{f"pass_at_{e}%": v[f"0.0{e}"]["all"] for e in (1, 2, 3, 4)},
                edge_for_50pct=edge_for(v, 0.5), edge_for_80pct=edge_for(v, 0.8)) for k, v in alt.items()}
    out["notes"] = [
        "Edges are TRUE annual excess returns over SPY (and over the universe). 0.00 rows are false-pass rates.",
        "R4 (costs, concentration) and G4' robustness are not modelled: pass probabilities are upper bounds.",
        "DGPs resample the 2010-2021 control noise; longer mean blocks preserve more persistence in relative "
        "performance.",
    ]
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(dict(dependence_mean_vr=vr_mean, w2_null_false_pass=cal, r2=out["r2"]), indent=1))
    for key, rows in oc.items():
        print(key)
        for a, v in rows.items():
            print("  ", a, {k2: round(x, 3) for k2, x in v.items()})


if __name__ == "__main__":
    main()
