"""Final Phase 2 slot review (P2-CP10, 2026-10-02): how much TRUE excess return a 20-stock, equal-weight, long-only
book needs to pass the development gates, with and without the proposed "beat SPY" amendment (G1.5).

No factor returns and no strategy returns are used. The inputs are only already-completed CONTROL books on the
common window 2010-03-01 -> 2021-12-31: SPY (E900-07), the same-universe equal-weight benchmark EW-H016 (E016-02) and
the five random 20-stock books (E016-03..07, seeds 1-5). They describe the NOISE of a 20-stock book around its
universe (tracking error, selection luck) and the universe's own position relative to SPY.

Model (stationary block bootstrap of the joint daily returns, mean block 63 days, seed 20261002):
  * the noise of a 20-stock book = (random seed k - EW), demeaned so that a random book has no edge;
  * candidate H = beta * EW + noise_k * risk_scale + alpha / 252 (alpha = TRUE annual excess over beta * EW; the
    "defensive" profile, beta 0.75, illustrates a low-risk book that can win on Sharpe while earning less than SPY);
  * random controls = EW + demeaned noise of the other four seeds (G2 uses their median: an approximation of the
    five-seed rule); SPY and EW are resampled jointly with them.
Gates evaluated: G1.1-G1.4, G2, G3 (frozen p2spec thresholds) and the proposed G1.5 (CAGR(H) > CAGR(SPY)).
G4 (perturbations, 2x slippage) is NOT modelled, so every pass probability here is an UPPER bound.

    PYTHONPATH=src python research/phase2/P2_final_slot_power.py -> research/phase2/P2_final_slot_power.json
"""
import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from qresearch import p2spec  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
START, END = "2010-03-01", "2021-12-31"
IDS = dict(SPY="E900-07", EW="E016-02", R1="E016-03", R2="E016-04", R3="E016-05", R4="E016-06", R5="E016-07")
N_BOOT, BLOCK, SEED = 2000, 63, 20261002
ALPHAS = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08)
RISK = {"random-like (tracking as a random 20-stock book)": (1.0, 1.0),
        "concentrated tilt (1.4x the random book's tracking)": (1.0, 1.4),
        "defensive (0.75x the universe's market moves, random-book tracking)": (0.75, 1.0)}


def daily(eid):
    df = pd.read_csv(gzip.open(ROOT / "experiments" / eid / "equity.csv.gz"))
    eq = pd.Series(df["equity"].to_numpy(float), index=df["date"].astype(str))
    eq = eq[(eq.index >= START) & (eq.index <= END)]
    return eq.pct_change().dropna()


def stats(r, years):
    """(Sharpe, CAGR, max drawdown, Calmar) of each column of the daily-return matrix r (T x k)."""
    sd = r.std(axis=0, ddof=1)
    sh = r.mean(axis=0) / sd * math.sqrt(252)
    eq = np.cumprod(1 + r, axis=0)
    cagr = eq[-1] ** (1 / years) - 1
    peak = np.maximum.accumulate(np.vstack([np.ones((1, r.shape[1])), eq]), axis=0)[1:]
    dd = (eq / peak - 1).min(axis=0)
    return sh, cagr, dd, cagr / np.abs(dd)


def main():
    R = pd.concat({k: daily(v) for k, v in IDS.items()}, axis=1, join="inner").dropna()
    dates = R.index.to_numpy()
    years = (pd.Timestamp(dates[-1]) - pd.Timestamp(START)).days / 365.25
    X = R.to_numpy(float)
    spy, ew, rnd = X[:, 0], X[:, 1], X[:, 2:]
    noise = rnd - ew[:, None]
    noise = noise - noise.mean(axis=0)                       # a random book has no edge over its universe
    obs = {}
    for j, k in enumerate(["R1", "R2", "R3", "R4", "R5"]):
        d_spy, d_ew = rnd[:, j] - spy, rnd[:, j] - ew
        obs[k] = dict(te_vs_spy=float(d_spy.std(ddof=1) * math.sqrt(252)), te_vs_ew=float(d_ew.std(ddof=1) * math.sqrt(252)),
                      corr_spy=float(np.corrcoef(rnd[:, j], spy)[0, 1]))
    s_obs = stats(X, years)
    observed = dict(
        books={k: dict(sharpe=float(s_obs[0][i]), cagr=float(s_obs[1][i]), max_dd=float(s_obs[2][i]))
               for i, k in enumerate(R.columns)},
        tracking=obs, ew_te_vs_spy=float((ew - spy).std(ddof=1) * math.sqrt(252)),
        random_cagr_sd=float(np.std(s_obs[1][2:], ddof=1)), random_sharpe_sd=float(np.std(s_obs[0][2:], ddof=1)),
        ew_minus_spy_cagr=float(s_obs[1][1] - s_obs[1][0]))
    blocks = [((dates >= a) & (dates <= z)) for a, z in p2spec.BLOCKS]
    rng = np.random.default_rng(SEED)
    T = len(X)
    out = dict(window=[START, END], years=years, n_boot=N_BOOT, mean_block=BLOCK, seed=SEED, inputs=IDS,
               observed=observed, results={})
    idxs = []
    for _ in range(N_BOOT):
        flags = rng.random(T) < 1.0 / BLOCK
        flags[0] = True
        pos = np.flatnonzero(flags)
        seg = np.cumsum(flags) - 1
        starts = rng.integers(T, size=len(pos))
        idxs.append((starts[seg] + np.arange(T) - pos[seg]) % T)
    for rname, (beta, scale) in RISK.items():
        res = {}
        for alpha in ALPHAS:
            cnt = dict(G1=0, G2=0, G3=0, G1_5=0, current_G1_G3=0, amended_G1_G3=0, cagr_gt_spy_only=0,
                       current_pass_but_cagr_below_spy=0)
            for b, ix in enumerate(idxs):
                k = b % 5
                others = [j for j in range(5) if j != k]
                e, s, nz = ew[ix], spy[ix], noise[ix]
                h = beta * e + nz[:, k] * scale + alpha / 252
                ctl = e[:, None] + nz[:, others]
                M = np.column_stack([h, e, s, ctl])
                sh, cg, dd, cal = stats(M, years)
                g11 = sh[0] - sh[1] >= p2spec.MARGIN_EW and sh[0] - sh[2] >= p2spec.MARGIN_SPY
                g1 = g11 and cg[0] >= cg[1] - p2spec.CAGR_TOL and cal[0] >= cal[1] and dd[0] >= dd[1] - p2spec.DD_TOL
                g2 = sh[0] > np.median(sh[3:])
                ex = h - e
                tot = ex.sum()
                bex = [ex[m].sum() for m in blocks]
                wins = 0
                for m in blocks:
                    hb, eb = h[m], e[m]
                    if hb.mean() / hb.std(ddof=1) > eb.mean() / eb.std(ddof=1):
                        wins += 1
                g3 = wins >= p2spec.G3_MIN_BLOCKS and tot > 0 and max(bex) / tot <= p2spec.G3_MAX_SHARE
                g15 = cg[0] > cg[2]
                cur = g1 and g2 and g3
                cnt["G1"] += g1
                cnt["G2"] += g2
                cnt["G3"] += g3
                cnt["G1_5"] += g15
                cnt["current_G1_G3"] += cur
                cnt["amended_G1_G3"] += cur and g15
                cnt["cagr_gt_spy_only"] += g15
                cnt["current_pass_but_cagr_below_spy"] += cur and not g15
            res[f"{alpha:.2f}"] = {k: v / N_BOOT for k, v in cnt.items()}
        out["results"][rname] = res
    out["notes"] = [
        "alpha = TRUE annual excess return over the same-universe equal-weight benchmark, added to a 20-stock book "
        "with the tracking noise of the observed random books; it is NOT an estimate for any factor.",
        "G4 is not modelled; pass probabilities are upper bounds. G2 uses the median of four control seeds.",
        "The bootstrap keeps the observed average gap between the universe (EW) and SPY in the window.",
    ]
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(observed, indent=1))
    for rname, res in out["results"].items():
        print(rname)
        for a, v in res.items():
            print(" ", a, {k: round(x, 3) for k, x in v.items()})


if __name__ == "__main__":
    main()
