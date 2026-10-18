"""P13-CP6 (owner D239 section 19): generic R3 (monthly factor-regression alpha) on FULLY SYNTHETIC panels — a
secondary diagnostic only (never R1 validation, never real data). Settings fixed in this file and committed before
it is run:

  * seeds 910001.. (200 panels per configuration; disjoint from the feasibility range 900001-900008);
  * 84 evaluation months, H028-style Top-15 portfolio (P1 / P2 selection), $7 + 10 bps costs;
  * premia (monthly return per 1 SD of the latent characteristic):
      R3-S1 none;  R3-S2 LV 0.0025;  R3-S3 LV 0.0025, BM -0.0030 (growth wins), PROF 0.0020;
      R3-S4 R3-S2 premia plus a planted stock-specific predictor Q 0.0040 (P2 selection, weight 1);
  * statistics: Newey-West (lag 2) t of the intercept in (portfolio - SPY) on [SPY, LVF] ("R3a") and on
    [SPY, LVF, BMF, PROFF, MOMF] ("R3b"); one-sided rejection at t > 2.326 (1%) and t > 1.645 (5%).

    PYTHONPATH=src python research/phase13/cp6/P13_CP6_r3_diagnostic.py
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from qresearch import r1synth as G  # noqa: E402
from qresearch import r1twin as T  # noqa: E402

N_PANELS = 200
CONFIGS = {
    "R3-S1_none_P1": (dict(), "P1", 910001),
    "R3-S2_lv_P1": (dict(prem=dict(LV=0.0025)), "P1", 911001),
    "R3-S3_lv_bm_prof_P1": (dict(prem=dict(LV=0.0025, BM=-0.0030, PROF=0.0020)), "P1", 912001),
    "R3-S4_strongQ_P2": (dict(prem=dict(LV=0.0025, Q=0.0040)), "P2", 913001),
}


def main():
    t0 = time.time()
    out = dict(checkpoint="P13-CP6", decision="D239", kind="R3 synthetic diagnostic (secondary; not R1 validation)",
               synthetic_only=True, n_panels=N_PANELS, results={})
    for name, (kw, proc, s0) in CONFIGS.items():
        ta, tb = [], []
        for seed in range(s0, s0 + N_PANELS):
            ms = G.panel(seed, G.config(**kw))
            real = T.real_sim(ms, T.scores(ms, proc))
            r = T.r3(real, ms)
            ta.append(r["t_alpha_lv"])
            tb.append(r["t_alpha_all"])
        ta, tb = np.array(ta), np.array(tb)

        def rate(x, c):
            k = int((x > c).sum())
            return dict(rate=k / x.size, k=k, n=int(x.size))
        out["results"][name] = dict(R3a_1pct=rate(ta, 2.326), R3a_5pct=rate(ta, 1.645), R3b_1pct=rate(tb, 2.326),
                                    R3b_5pct=rate(tb, 1.645), t_a_median=float(np.median(ta)),
                                    t_b_median=float(np.median(tb)), seeds=[s0, s0 + N_PANELS - 1])
        print(name, f"{time.time() - t0:.0f}s", flush=True)
    txt = json.dumps(out, indent=1, sort_keys=True)
    (HERE / "P13_CP6_r3_diagnostic.json").write_text(txt + "\n")
    print(hashlib.sha256(txt.encode()).hexdigest()[:16])


if __name__ == "__main__":
    main()
