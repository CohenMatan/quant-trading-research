"""H020 null design check (P5-CP2 section 27). SYNTHETIC latent panels only (h020_synth_panel); no market data.

Compares the two tether designs on no-edge panels (417 weekly dates x 300 stocks):
  'stratified'  : partners within momentum-quintile x trend strata (REJECTED);
  'flat'        : one stratum (FROZEN).
Reports week-to-week partner persistence, the null sd of t_ic / t_inc versus the sd of the same statistics across
independent no-edge 'real' panels, and the size (share of no-edge panels above the null critical value).

  python research/phase5/h020_null_design_check.py   -> research/phase5/h020_null_design_check.json
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "src" / "qresearch" / "lean")]
import h020_synth_panel as P  # noqa: E402
import qr_h020_stats as H  # noqa: E402

N_DATES, N_STOCKS, R, PANELS = 417, 300, 300, 120


def check(stratified):
    prep = H.prepare(P.make_dates(N_DATES, N_STOCKS, seed=1), stratified=stratified)
    T = H.ChartTether(1)
    prev, kept, tot = None, 0, 0
    for p in prep:
        src = T.step(p["ids"], p["strata"])
        if prev is not None:
            kept += sum(1 for i, s in zip(p["ids"], src) if prev.get(i) == s)
            tot += len(src)
        prev = dict(zip(p["ids"], src))
    nw = [H.run_world(prep, seed=10 + k) for k in range(R)]
    reals = [H.run_world(H.prepare(P.make_dates(N_DATES, N_STOCKS, seed=100 + i), stratified=stratified))
             for i in range(PANELS)]
    out = dict(persistence=kept / tot,
               null_sd={k: float(np.std([w[k] for w in nw])) for k in H.STATS},
               real_sd={k: float(np.std([r[k] for r in reals])) for k in H.STATS})
    for a in (0.05, 0.01):
        c = {k: H.X.critical_value([w[k] for w in nw], a) for k in H.STATS}
        out["alpha_%g" % a] = dict(c=c, size={k: float(np.mean([r[k] > c[k] for r in reals])) for k in H.STATS})
    return out


if __name__ == "__main__":
    res = dict(design=dict(n_dates=N_DATES, n_stocks=N_STOCKS, r_null=R, panels=PANELS),
               stratified=check(True), flat=check(False))
    (HERE / "h020_null_design_check.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
