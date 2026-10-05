"""H020 canary assessment (E987-01, check 13): SYNTHETIC check of the planted-signal null width. A score planted as the
rank of each stock's own response, permuted by the tethered null, has a null t_ic distribution of sd ~1 without common
return factors but ~5 with them (fixed partner pairs x squared factor returns), so one real null world at t = 4.47 is
expected; the 5,000-world null calibrates c on exactly this structure. Synthetic data only.

  python research/phase5/h020_planted_factor_check.py
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase5")]
import numpy as np, qr_h020_stats as H, qr_xs as X
rng=np.random.default_rng(1)
n, T = 800, 412
for nf, fvol in ((0, 0.0), (3, 0.03)):
    beta = rng.normal(size=(n, nf)) if nf else np.zeros((n,0))
    f = rng.normal(size=(T+5, nf)) * fvol
    r = (beta @ f.T).T + 0.045 * rng.normal(size=(T+5, n))
    cs = np.vstack([np.zeros(n), np.cumsum(r, axis=0)])
    dates=[]
    for w in range(T):
        y = cs[w+5]-cs[w+1]
        q = np.floor(21*(X.avg_rank(y)-0.5)/n).astype(int)
        G = np.where(q<=5,1,np.where(q<=10,2,np.where(q<=15,3,4)))
        dates.append(dict(ids=np.arange(n), Q=q, G=G, mom=rng.normal(size=n), trend=rng.random(n)>0.5, y=y, y13=y, year=2010+w//52))
    pr=H.prepare(dates)
    t=[H.run_world(pr, seed=s)["t_ic"] for s in range(1,41)]
    print("factors",nf,"planted null t_ic: mean %.2f sd %.2f max|t| %.2f"%(np.mean(t), np.std(t), np.max(np.abs(t))))
