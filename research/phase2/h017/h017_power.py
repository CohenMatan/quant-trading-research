"""H017 proposal support (P2-CP13): operating characteristics of the frozen Amendment 3 gates and of the proposed
"Promising but Not Qualified" (PbNQ) rule for a 10-position book on 12 years. Inputs: ONLY the completed control books
(SPY, same-universe EW, five random 20-stock books, 2010-03 -> 2021-12), as in P2_amend3_calibration.py; the stock-
selection noise is scaled to 10 positions by sqrt(20/10). No candidate, event or factor returns.

PbNQ (proposed, P2-CP13 section 23), evaluated here on its return-based parts:
  W1 passes; excess CAGR >= +1.0 point a year; W2 statistic g/SE >= 1.0 (but W2 itself, 2.15, fails); W3 passes;
  R1, R2, R3 pass. (R4, the 2x-slippage check and the event-level condition are not modelled: upper bounds.)

    PYTHONPATH=src python research/phase2/h017/h017_power.py -> h017_power.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research/phase2/architecture"))
from qresearch import wealth  # noqa: E402
import P2_amend3_calibration as C  # noqa: E402

N_SIM, SEED = 2000, 20261005
EDGES = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10)
PBNQ_MIN_EXCESS, PBNQ_MIN_T = 0.01, 1.0


def pbnq(g):
    w2 = g["W2"]
    t = w2["g"] / w2["se"] if w2["se"] > 0 else float("nan")
    return bool(g["W1"]["ok"] and g["W1"]["excess"] >= PBNQ_MIN_EXCESS and t >= PBNQ_MIN_T and not w2["ok"]
                and g["W3"]["ok"] and g["R1"]["ok"] and g["R2"]["ok"] and g["R3"]["ok"])


def main():
    R = pd.concat({k: C.daily(v) for k, v in C.IDS.items()}, axis=1, join="inner").dropna()
    X = R.to_numpy(float)
    spy, ew, rnd = X[:, 0], X[:, 1], X[:, 2:]
    n = len(X)
    u = (ew - spy) - (ew - spy).mean()
    s = (rnd - ew[:, None]) - (rnd - ew[:, None]).mean(axis=0)
    rng = np.random.default_rng(SEED)
    out = {}
    for npos in (10, 20):
        sc = math.sqrt(20 / npos)
        idxs = [C.sb_index(rng, n, n, 126) for _ in range(N_SIM)]
        rows = {}
        for a in EDGES:
            q = p = 0
            for b, ix in enumerate(idxs):
                k = b % 5
                sp = spy[ix]
                e = sp + u[ix]
                h = e + s[ix, k] * sc + a / 252
                others = [s[ix][:, j] for j in range(5) if j != k] + [np.roll(s[:, k], n // 2)[ix]]
                ctl = e[:, None] + np.column_stack(others) * sc
                g = wealth.evaluate_gates(h, sp, e, list(ctl.T))
                q += g["core_ok"]
                p += pbnq(g)
            rows[f"{a:.2f}"] = dict(qualified=q / N_SIM, pbnq=p / N_SIM, qualified_or_pbnq=(q + p) / N_SIM)
        out[f"{npos} positions, 12y"] = rows
    Path(__file__).with_suffix(".json").write_text(json.dumps(dict(pbnq_rule=dict(min_excess=PBNQ_MIN_EXCESS,
                                                                                  min_t=PBNQ_MIN_T), results=out),
                                                             indent=1) + "\n")
    for k, rows in out.items():
        print(k)
        for a, v in rows.items():
            print("  ", a, {x: round(y, 3) for x, y in v.items()})


if __name__ == "__main__":
    main()
