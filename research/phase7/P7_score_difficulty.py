"""P7-CP2 design aid (SYNTHETIC; no market data, no returns): how rare is a high score under the frozen v1 point
rules? Latent features are drawn from a multivariate normal whose correlations are the feature-feature Spearman
averages measured in P7-CP1 (E991-02 fundamental, E992-03 technical; no return involved); cross-domain
(technical vs fundamental) correlations are unknown and set to 0 (independent) and to 0.2 (sensitivity). Trend state
from a latent correlated 0.60 with 12-1 momentum (CP1: SMA200 ratio vs momentum), split strong 45% / moderate 20% /
weak 35% (assumption, roughly the 2011-2017 breadth level); sector context drawn per FF12 group 30/40/30.
Output: research/phase7/P7_score_difficulty.json — the share of scorable names at or above candidate thresholds and
the implied count for 600 scorable names. The real distribution is measured only in P7-CP3 (availability study)."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import qr_p7_score as S  # noqa: E402

NAMES = ["trend_latent", "momentum", "neg_vol", "gpa", "cash_conversion", "eqa", "growth"]


def corr(cross=0.0):
    R = np.eye(7)
    pairs = {("trend_latent", "momentum"): 0.60, ("trend_latent", "neg_vol"): 0.02, ("momentum", "neg_vol"): 0.00,
             ("gpa", "cash_conversion"): 0.07, ("gpa", "eqa"): 0.23, ("gpa", "growth"): 0.17,
             ("cash_conversion", "eqa"): -0.01, ("cash_conversion", "growth"): -0.01, ("eqa", "growth"): 0.19}
    for (a, b), v in pairs.items():
        i, j = NAMES.index(a), NAMES.index(b)
        R[i, j] = R[j, i] = v
    for a in NAMES[:3]:
        for b in NAMES[3:]:
            i, j = NAMES.index(a), NAMES.index(b)
            R[i, j] = R[j, i] = cross
    return R


def simulate(cross, n=600, dates=200, seed=7):
    rng = np.random.default_rng(seed)
    L = np.linalg.cholesky(corr(cross))
    groups = ("BusEq", "Manuf", "Hlth", "Shops", "Other", "Enrgy", "NoDur", "Chems", "Utils", "Telcm", "Durbl")
    tot = []
    for _ in range(dates):
        Z = rng.standard_normal((n, 7)) @ L.T
        tl = Z[:, 0]
        cut_w, cut_m = np.quantile(tl, 0.35), np.quantile(tl, 0.55)
        ctx = {g: rng.choice(["supportive", "neutral", "weak"], p=[0.3, 0.4, 0.3]) for g in groups}
        st = {}
        for i in range(n):
            trend = "weak" if tl[i] < cut_w else ("moderate" if tl[i] < cut_m else "strong")
            st[f"s{i:04d}"] = dict(ff12=groups[i % len(groups)], sic=3000, contaminated=False,
                                   tech=dict(bars=400, age=0, trend_state=trend, broken_trend=False,
                                             mom_12_1=Z[i, 1], vol60=-Z[i, 2]),
                                   fund=(dict(gpa=Z[i, 3], cash_conversion=Z[i, 4], eqa=Z[i, 5], rev_growth=Z[i, 6],
                                              impaired=False), ""))
        tot += [r["total"] for r in S.score_date(st, ctx).values()]
    tot = np.array(tot)
    out = dict(cross_correlation=cross, scorable_per_date=n, dates=dates, median=float(np.median(tot)),
               p90=float(np.quantile(tot, 0.9)), p99=float(np.quantile(tot, 0.99)))
    for th in (60, 65, 70, 75, 80, 85, 90):
        sh = float((tot >= th).mean())
        out[f"share_ge_{th}"] = round(sh, 4)
        out[f"count_ge_{th}_per_{n}"] = round(sh * n, 1)
    return out


def main():
    res = [simulate(0.0), simulate(0.2)]
    (Path(__file__).parent / "P7_score_difficulty.json").write_text(json.dumps(res, indent=1) + "\n")
    for r in res:
        print(r)


if __name__ == "__main__":
    main()
