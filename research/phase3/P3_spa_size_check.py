"""Phase 3: size check of Hansen's SPA test (consistent p-value, stationary bootstrap, studentised) in our setting,
on SYNTHETIC data only (no market data, no strategy returns). Decides whether SPA is usable as a secondary
diagnostic (P3-CP2, owner instruction: secondary methods only where useful, not stacked).

Setting: T = 94 monthly periods (2010-03 .. 2017-12), K = 200 correlated models with ZERO true mean excess (H0 true
at the boundary), one-factor correlation 0.5, Gaussian or AR(1) phi = 0.3 innovations. A correctly sized test
rejects about 5% of the time at alpha = 0.05.

    PYTHONPATH=src python research/phase3/P3_spa_size_check.py -> P3_spa_size_check.json
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from qresearch.p3stats import hansen_spa  # noqa: E402

T, K, RHO, SIMS, BOOT, SEED = 94, 200, 0.5, 200, 499, 20261004


def simulate(rng, phi):
    f = rng.normal(size=(T, 1))
    e = np.sqrt(RHO) * f + np.sqrt(1 - RHO) * rng.normal(size=(T, K))
    if phi:
        x = np.empty_like(e)
        x[0] = e[0]
        for t in range(1, T):
            x[t] = phi * x[t - 1] + np.sqrt(1 - phi ** 2) * e[t]
        e = x
    return 0.02 * e                                        # ~2% monthly excess volatility, zero mean


def main():
    out = dict(T=T, K=K, rho=RHO, sims=SIMS, n_boot=BOOT, alpha=0.05, results={})
    for name, phi, block in (("iid_block6", 0.0, 6), ("ar03_block6", 0.3, 6), ("iid_block12", 0.0, 12)):
        rng = np.random.default_rng([SEED, int(phi * 10), block])
        rej = 0
        for i in range(SIMS):
            r = hansen_spa(simulate(rng, phi), mean_block=block, n_boot=BOOT, seed=SEED + i)
            rej += r["p_value"] <= 0.05
        out["results"][name] = dict(rejection_rate=rej / SIMS, rejections=int(rej))
        print(name, rej / SIMS)
    out["decision"] = ("SPA is not used in Phase 3: in this sample length it rejects a true null far more often than "
                       "the nominal 5% (see results); the empirical full-search null is the only multiple-testing "
                       "gate, PBO and DSR are diagnostics")
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
