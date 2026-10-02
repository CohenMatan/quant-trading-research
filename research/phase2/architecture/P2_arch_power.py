"""Architecture review (P2-CP11): what a terminal-wealth framework can detect, on 12 versus 22 years of data.

Inputs: ONLY already-completed control books on 2010-03-01 -> 2021-12-31: SPY (E900-07, total return), the
same-universe equal-weight benchmark EW-H016 (E016-02) and five random 20-stock books (E016-03..07). No candidate
or factor returns. Everything below describes NOISE (what luck alone produces) and the operating characteristics of
gate designs; nothing estimates the return of any strategy.

Part A, rolling horizons (actual control data): for each random book and the EW universe versus SPY, over every
start date, the share of 1/3/5/10-year windows in which the book ended with more wealth than SPY, plus median, mean,
worst and best excess CAGR. This is what "no skill" looks like in the rolling-horizon report.

Part B, noise model (stationary block bootstrap, mean block 63 days, seed 20261003):
  book = SPY + u + s_k * sqrt(20 / n) + a / 252
    u   = (EW - SPY), demeaned: the universe's own tracking noise against SPY (no universe edge assumed);
    s_k = (random seed k - EW), demeaned: stock-selection noise of a 20-stock book, scaled for n positions;
    a   = TRUE annual excess return over SPY (and over the universe). Controls get the same u and other seeds' s_j.
  Histories of 12 years (the current window) and 22 years (resampled from the same 12-year pool: an approximation
  that assumes 2000-2009 noise resembled 2010-2021; the dot-com and 2008 periods were probably noisier).

Part C, operating characteristics (false-pass rate at a = 0 and pass probability for a > 0) of:
  * CURRENT: G1.1-G1.4 + G2 + G3 (frozen p2spec) + G1.5 (CAGR > SPY);
  * PROPOSED terminal-wealth framework (P2-CP11 §3-§6), with z = 1.28 or 1.645:
      W1 objective:   CAGR(H) > CAGR(SPY)
      W2 evidence:    CAGR(H) - CAGR(SPY) >= z * TE(H vs SPY) / sqrt(years)
      W3 attribution: CAGR(H) > CAGR(EW same universe) and CAGR(H) > median CAGR of the random books
      R1 drawdown:    MaxDD(H) >= MaxDD(SPY) - 0.10
      R2 risk-adjusted: Sharpe(H) >= Sharpe(SPY)
      R3 dispersion:  no two-year block contributes more than half of the total excess over SPY (total > 0)
  G4-type robustness (perturbations, 2x costs) is not modelled: pass probabilities are upper bounds.

    PYTHONPATH=src python research/phase2/architecture/P2_arch_power.py -> P2_arch_power.json
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

ROOT = Path(__file__).resolve().parents[3]
START, END = "2010-03-01", "2021-12-31"
IDS = dict(SPY="E900-07", EW="E016-02", R1="E016-03", R2="E016-04", R3="E016-05", R4="E016-06", R5="E016-07")
N_BOOT, BLOCK, SEED = 2000, 63, 20261003
EDGES = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05)
HORIZONS = {"1y": 252, "3y": 756, "5y": 1260, "10y": 2520}


def daily(eid):
    df = pd.read_csv(gzip.open(ROOT / "experiments" / eid / "equity.csv.gz"))
    eq = pd.Series(df["equity"].to_numpy(float), index=df["date"].astype(str))
    eq = eq[(eq.index >= START) & (eq.index <= END)]
    return eq.pct_change().dropna()


def rolling(book, spy):
    """Excess CAGR of `book` over SPY for every start date, per horizon (daily log-wealth windows)."""
    lb, ls = np.log1p(book), np.log1p(spy)
    cb, cs = np.concatenate([[0], np.cumsum(lb)]), np.concatenate([[0], np.cumsum(ls)])
    out = {}
    for h, n in HORIZONS.items():
        if len(book) < n:
            continue
        yrs = n / 252
        xb = (cb[n:] - cb[:-n])
        xs = (cs[n:] - cs[:-n])
        ex = np.exp(xb / yrs) - np.exp(xs / yrs)
        out[h] = dict(windows=int(len(ex)), share_book_wins=float((xb > xs).mean()), median_excess_cagr=float(np.median(ex)),
                      mean_excess_cagr=float(ex.mean()), p10=float(np.percentile(ex, 10)), p90=float(np.percentile(ex, 90)),
                      worst=float(ex.min()), best=float(ex.max()))
    return out


def stats(M, years):
    sd = M.std(axis=0, ddof=1)
    sh = M.mean(axis=0) / sd * math.sqrt(252)
    eq = np.cumprod(1 + M, axis=0)
    cagr = eq[-1] ** (1 / years) - 1
    peak = np.maximum.accumulate(np.vstack([np.ones((1, M.shape[1])), eq]), axis=0)[1:]
    dd = (eq / peak - 1).min(axis=0)
    return sh, cagr, dd, cagr / np.abs(dd)


def boot_index(rng, T_pool, T_out):
    flags = rng.random(T_out) < 1.0 / BLOCK
    flags[0] = True
    pos = np.flatnonzero(flags)
    seg = np.cumsum(flags) - 1
    starts = rng.integers(T_pool, size=len(pos))
    return (starts[seg] + np.arange(T_out) - pos[seg]) % T_pool


def evaluate(h, ew, spy, ctl, years, blocks):
    sh, cg, dd, cal = stats(np.column_stack([h, ew, spy, ctl]), years)
    ex = h - spy
    te = ex.std(ddof=1) * math.sqrt(252)
    # current framework (frozen thresholds) + G1.5
    g11 = sh[0] - sh[1] >= p2spec.MARGIN_EW and sh[0] - sh[2] >= p2spec.MARGIN_SPY
    g1 = g11 and cg[0] >= cg[1] - p2spec.CAGR_TOL and cal[0] >= cal[1] and dd[0] >= dd[1] - p2spec.DD_TOL
    g2 = sh[0] > np.median(sh[3:])
    exe = h - ew
    tot_e = exe.sum()
    wins = sum(1 for m in blocks if h[m].mean() / h[m].std(ddof=1) > ew[m].mean() / ew[m].std(ddof=1))
    g3 = wins >= p2spec.G3_MIN_BLOCKS and tot_e > 0 and max(exe[m].sum() for m in blocks) / tot_e <= p2spec.G3_MAX_SHARE
    w1 = cg[0] > cg[2]
    current = bool(g1 and g2 and g3 and w1)
    # proposed
    xc = cg[0] - cg[2]
    w3 = cg[0] > cg[1] and cg[0] > np.median(cg[3:])
    r1 = dd[0] >= dd[2] - 0.10
    r2 = sh[0] >= sh[2]
    tot = ex.sum()
    r3 = tot > 0 and max(ex[m].sum() for m in blocks) / tot <= 0.50
    base = bool(w1 and w3 and r1 and r2 and r3)
    return dict(current=current, w1=bool(w1), w3=bool(w3), r=bool(r1 and r2 and r3), xc=xc, te=te, years=years,
                base=base)


def main():
    R = pd.concat({k: daily(v) for k, v in IDS.items()}, axis=1, join="inner").dropna()
    X = R.to_numpy(float)
    spy, ew, rnd = X[:, 0], X[:, 1], X[:, 2:]
    out = dict(window=[START, END], inputs=IDS, n_boot=N_BOOT, mean_block=BLOCK, seed=SEED)
    # ---- Part A: rolling horizons on the actual control books
    out["rolling_vs_spy_actual"] = {"EW (same universe)": rolling(ew, spy)}
    for j in range(5):
        out["rolling_vs_spy_actual"][f"random seed {j + 1}"] = rolling(rnd[:, j], spy)
    # ---- noise decomposition
    u = (ew - spy) - (ew - spy).mean()
    s = (rnd - ew[:, None]) - (rnd - ew[:, None]).mean(axis=0)
    out["noise"] = dict(te_universe_vs_spy=float(u.std(ddof=1) * math.sqrt(252)),
                        te_selection_20=float(np.mean(s.std(axis=0, ddof=1)) * math.sqrt(252)),
                        te_random20_vs_spy=float(np.mean((rnd - spy[:, None]).std(axis=0, ddof=1)) * math.sqrt(252)))
    rng = np.random.default_rng(SEED)
    T = len(X)
    res = {}
    for years_lbl, years in (("12y (2010-2021)", 12), ("22y (~2000-2021, resampled)", 22)):
        T_out = int(round(years * 252))
        blocks = [np.arange(T_out) // 504 == b for b in range(T_out // 504)]
        idxs = [boot_index(rng, T, T_out) for _ in range(N_BOOT)]
        for n in (20, 40):
            sc = math.sqrt(20 / n)
            key = f"{years_lbl}, {n} positions"
            res[key] = {}
            for a in EDGES:
                acc = {"current (G1-G3 + G1.5)": 0, "W1 alone (CAGR > SPY)": 0}
                for z in (1.28, 1.645):
                    acc[f"proposed, z={z}"] = 0
                xcs, tes = [], []
                for b, ix in enumerate(idxs):
                    k = b % 5
                    sp = spy[ix]
                    e = sp + u[ix]
                    h = e + s[ix, k] * sc + a / 252
                    ctl = e[:, None] + s[ix][:, [j for j in range(5) if j != k]] * sc
                    r = evaluate(h, e, sp, ctl, T_out / 252, blocks)
                    acc["current (G1-G3 + G1.5)"] += r["current"]
                    acc["W1 alone (CAGR > SPY)"] += r["w1"]
                    for z in (1.28, 1.645):
                        w2 = r["xc"] >= z * r["te"] / math.sqrt(r["years"])
                        acc[f"proposed, z={z}"] += bool(r["base"] and w2)
                    xcs.append(r["xc"])
                    tes.append(r["te"])
                res[key][f"{a:.2f}"] = {k2: v / N_BOOT for k2, v in acc.items()}
                if a == 0.0:
                    res[key]["_noise"] = dict(sd_excess_cagr=float(np.std(xcs)), median_te_vs_spy=float(np.median(tes)))
    out["operating_characteristics"] = res
    out["notes"] = [
        "a = TRUE annual excess return over SPY (and the universe); 0.00 rows are FALSE-PASS rates.",
        "22-year rows resample the 2010-2021 noise; the 2000-2009 decade likely had larger dispersion, so they are "
        "optimistic about power.",
        "G4-type robustness is not modelled; all pass probabilities are upper bounds.",
    ]
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["noise"], indent=1))
    for k, v in out["rolling_vs_spy_actual"].items():
        print(k, {h: (round(x["share_book_wins"], 2), round(x["median_excess_cagr"], 4)) for h, x in v.items()})
    for key, rows in res.items():
        print(key, rows.get("_noise"))
        for a, v in rows.items():
            if a != "_noise":
                print("  ", a, {k2: round(x, 3) for k2, x in v.items()})


if __name__ == "__main__":
    main()
