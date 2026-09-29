"""C02 PBO calibration (owner request 2026-09-29, before any C02 result). Synthetic data only.

What does the CSCV PBO statistic (16 blocks, "at or below the OOS median counts as overfit", as in
qresearch.stats.pbo_cscv) do when the matrix has only 3 variations, and what does it do at the
cycle level (18 variations)? Monte Carlo over daily returns with known Sharpe ratios and
correlations; the IS period length (2,012 sessions) matches 2010-01-04..2017-12-29.

    PYTHONPATH=src python research/cycles/C02_pbo_simulation.py   -> research/cycles/C02_pbo_simulation.json
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np

T, BLOCKS, DAILY_VOL = 2012, 16, 0.01
_COMBOS = np.array(list(itertools.combinations(range(BLOCKS), BLOCKS // 2)))
_MASK = np.zeros((len(_COMBOS), BLOCKS), bool)
_MASK[np.arange(len(_COMBOS))[:, None], _COMBOS] = True


def pbo_fast(m: np.ndarray) -> float:
    """Same statistic as stats.pbo_cscv, vectorised over the 12,870 splits via block sums
    (a tested equivalence: tests/test_pbo_calibration.py)."""
    t, n = m.shape
    blocks = np.array_split(np.arange(t), BLOCKS)
    cnt = np.array([len(b) for b in blocks], float)
    s1 = np.array([m[b].sum(0) for b in blocks])
    s2 = np.array([(m[b] ** 2).sum(0) for b in blocks])

    def sharpe(mask):
        c = mask.astype(float) @ cnt
        a = mask.astype(float) @ s1
        b = mask.astype(float) @ s2
        mean = a / c[:, None]
        var = (b - c[:, None] * mean ** 2) / (c[:, None] - 1)
        return mean / np.sqrt(var)

    sr_is, sr_oos = sharpe(_MASK), sharpe(~_MASK)
    best = np.argmax(sr_is, axis=1)
    sb = sr_oos[np.arange(len(best)), best][:, None]
    rank = ((sr_oos < sb).sum(1) + 0.5 * ((sr_oos == sb).sum(1) - 1) + 1) / (n + 1)
    return float(np.mean(np.log(rank / (1 - rank)) <= 0))


def simulate(rng, sharpes, groups, rho_within, rho_across):
    """Daily returns: one market factor (rho_across) + one factor per group (extra within-group
    correlation) + idiosyncratic noise; annualised Sharpe ratios as given."""
    n = len(sharpes)
    mkt = rng.standard_normal(T)
    grp = {g: rng.standard_normal(T) for g in set(groups)}
    extra = max(rho_within - rho_across, 0.0)
    out = np.empty((T, n))
    for j in range(n):
        z = (math.sqrt(rho_across) * mkt + math.sqrt(extra) * grp[groups[j]]
             + math.sqrt(1 - rho_across - extra) * rng.standard_normal(T))
        out[:, j] = DAILY_VOL * z + sharpes[j] / math.sqrt(252) * DAILY_VOL
    return out


def summarise(vals):
    v = np.array(vals)
    return dict(mean=round(float(v.mean()), 3), p05=round(float(np.quantile(v, 0.05)), 3),
                p50=round(float(np.quantile(v, 0.5)), 3), p95=round(float(np.quantile(v, 0.95)), 3),
                share_pass_030=round(float(np.mean(v <= 0.30)), 3))


def main(reps: int = 200, seed: int = 20260929) -> dict:
    rng = np.random.default_rng(seed)
    out = {"setup": dict(T=T, blocks=BLOCKS, reps=reps, seed=seed, daily_vol=DAILY_VOL,
                         rule="PBO = share of 12,870 CSCV splits whose IS-best lands at or below the OOS median")}
    # A. three variations of one hypothesis: variation 0 better by d (annualised Sharpe), base 0.5
    a = {}
    for rho in (0.5, 0.8, 0.95):
        for d in (0.0, 0.25, 0.5, 1.0):
            vals = [pbo_fast(simulate(rng, [0.5 + d, 0.5, 0.5], [0, 0, 0], rho, rho)) for _ in range(reps)]
            a[f"rho={rho} dSR={d}"] = summarise(vals)
    out["A_three_variations"] = a
    # B. cycle level: 6 hypotheses x 3 variations (within 0.8, across 0.5); one hypothesis has an edge d
    b = {}
    for d in (0.0, 0.25, 0.5, 1.0):
        sh = [0.5 + (d if j < 3 else 0.0) for j in range(18)]
        vals = [pbo_fast(simulate(rng, sh, [j // 3 for j in range(18)], 0.8, 0.5)) for _ in range(reps)]
        b[f"one hypothesis +{d}"] = summarise(vals)
    # B2. cycle level with a spread of true Sharpes (no single winner): 0.0 .. 1.0 across hypotheses
    vals = [pbo_fast(simulate(rng, [0.2 * (j // 3) for j in range(18)], [j // 3 for j in range(18)], 0.8, 0.5))
            for _ in range(reps)]
    b["spread 0.0..1.0 by hypothesis"] = summarise(vals)
    out["B_cycle_18_variations"] = b
    return out


if __name__ == "__main__":
    res = main()
    p = Path(__file__).with_suffix(".json")
    p.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
