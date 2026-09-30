"""C03 PBO analysis (owner request 2026-09-30, before any C03 result).

Question: is the D073 cycle-level PBO (CSCV, 16 blocks, at-or-below-median = overfit, gate <= 0.30)
still meaningful when the C03 selection set has only 6 candidates in 2 correlated groups of 3
(H012 v1.0-1.2, H013 v1.0-1.2)? Compared with the alternative of pooling the same-harness C02
candidates (18) with C03's 6 (24 columns).

Part 1: purely synthetic (known Sharpe ratios and correlations).
Part 2: semi-real - the 18 REAL C02 IS return series (derived results, committed) plus 6 synthetic
C03 columns built from the real EW benchmark return plus noise at a chosen Sharpe. No C03 data.

    PYTHONPATH=src python research/cycles/C03_pbo_analysis.py   -> research/cycles/C03_pbo_analysis.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
sys.path.insert(0, str(Path(__file__).parent))
from C02_pbo_simulation import pbo_fast, simulate, summarise  # noqa: E402
from qresearch import cycle, metrics, results  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REPS = 200


def part1(rng):
    """6 candidates = 2 groups x 3. Within-group correlation 0.9 (near-identical variations),
    across 0.5. Group 0 (say H012) may be better by d; group 1 by e."""
    out = {}
    for label, sh in {
        "null: all 6 equal (0.5)": [0.5] * 6,
        "one hypothesis +0.25": [0.75] * 3 + [0.5] * 3,
        "one hypothesis +0.5": [1.0] * 3 + [0.5] * 3,
        "one hypothesis +1.0": [1.5] * 3 + [0.5] * 3,
        "both hypotheses good and similar (1.0, 1.0)": [1.0] * 6,
        "both good, one a bit better (1.2 vs 1.0)": [1.2] * 3 + [1.0] * 3,
        "one variation +0.5 inside a group": [1.0, 0.5, 0.5, 0.5, 0.5, 0.5],
    }.items():
        vals = [pbo_fast(simulate(rng, sh, [0, 0, 0, 1, 1, 1], 0.9, 0.5)) for _ in range(REPS)]
        out[label] = summarise(vals)
    return out


def part1_pooled(rng):
    """24 candidates: 6 synthetic 'C02-like' groups of 3 (within 0.8) with Sharpes spread 0.2..0.9 as
    observed, plus the 2 C03 groups (within 0.9); across 0.5."""
    c02 = [0.2, 0.5, 0.6, 0.7, 0.8, 0.9]
    base = [s for s in c02 for _ in range(3)]
    groups = [j // 3 for j in range(24)]
    out = {}
    for label, c03 in {
        "C03 null (both 0.5)": [0.5] * 6,
        "C03 one hypothesis at 1.0": [1.0] * 3 + [0.5] * 3,
        "C03 one hypothesis at 1.5": [1.5] * 3 + [0.5] * 3,
        "C03 both at 1.0": [1.0] * 6,
        "C03 both at 1.3": [1.3] * 6,
    }.items():
        vals = [pbo_fast(simulate(rng, base + c03, groups, 0.8, 0.5)) for _ in range(REPS)]
        out[label] = summarise(vals)
    return out


def part2(rng):
    """Semi-real: real C02 returns (18) + synthetic C03 columns = beta * EW + idiosyncratic noise,
    scaled to target Sharpe; 3 columns per hypothesis sharing most of their noise."""
    ids = cycle.cycle_experiments("C02")
    ser = {}
    for e in ids:
        eq = results.read_csv_gz(ROOT / "experiments" / e / "equity.csv.gz")
        ser[e] = metrics.returns_from_equity(pd.Series(eq["equity"].to_numpy(float), index=eq["date"].astype(str)))
    ew = results.read_csv_gz(ROOT / "experiments" / "E901-07" / "equity.csv.gz")
    rew = metrics.returns_from_equity(pd.Series(ew["equity"].to_numpy(float), index=ew["date"].astype(str)))
    real = pd.concat(ser, axis=1, join="inner").join(rew.rename("EW"), how="inner").dropna()
    R, ewr = real[ids].to_numpy(), real["EW"].to_numpy()
    T = len(real)
    ew_sd = ewr.std()

    def synth(target_sr, n=3, beta=0.8, idio=0.006, shared=0.85):
        """Expected (not forced) Sharpe: the real EW path times beta, plus random idiosyncratic noise,
        plus a constant drift chosen from the EXPECTED volatility. Forcing each column's realised
        full-sample Sharpe makes the IS and OOS halves mirror images (a winner in one half must lose
        in the other) - an artefact found in the first version of this script."""
        common = rng.standard_normal(T)
        sd_exp = math.sqrt((beta * ew_sd) ** 2 + idio ** 2)
        drift = target_sr / math.sqrt(252) * sd_exp - beta * ewr.mean()
        cols = []
        for _ in range(n):
            e = idio * (math.sqrt(shared) * common + math.sqrt(1 - shared) * rng.standard_normal(T))
            cols.append(beta * ewr + e + drift)
        return np.column_stack(cols)

    out = {"real_C02_columns": len(ids), "days": T,
           "C02_alone_pbo": pbo_fast(R)}
    for label, (sa, sb) in {"C03 null (both at 0.5)": (0.5, 0.5), "C03 both at EW-like 0.9": (0.9, 0.9),
                            "C03 one hypothesis at 1.3": (1.3, 0.5), "C03 one at 1.6": (1.6, 0.5),
                            "C03 both at 1.3": (1.3, 1.3)}.items():
        v6, v24 = [], []
        for _ in range(REPS // 2):
            c3 = np.column_stack([synth(sa), synth(sb)])
            v6.append(pbo_fast(c3))
            v24.append(pbo_fast(np.column_stack([R, c3])))
        out[label] = dict(six_only=summarise(v6), pooled_24=summarise(v24))
    return out


def main():
    rng = np.random.default_rng(20260930)
    res = dict(setup=dict(reps=REPS, blocks=16, rule="PBO = share of CSCV splits whose IS-best lands at or below the OOS median; gate <= 0.30"),
               part1_six_candidates=part1(rng), part1_pooled_24=part1_pooled(rng), part2_semi_real=part2(rng))
    p = Path(__file__).with_suffix(".json")
    p.write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
