"""Phase 3 null-calibration precision (P3-CP2; owner instruction 4). NO market data, NO strategy returns.
1. Exact binomial (Clopper-Pearson) 95% intervals for a false-pass rate estimated from R complete null searches, for
   R in {39, 100, 200, 500, 1000} and true rates {0.5%, 1%, 2%, 5%}: expected interval and the probability that the
   interval's upper bound stays below 5% / 10%.
2. Precision of the null threshold tau = the 95th percentile of the best plateau score: the order-statistic 95%
   interval (in quantile terms) for R = 39 .. 1000.
3. An end-to-end exercise of the FROZEN selection pipeline (qr_p3_pipeline, the real 1,533-configuration grammar and
   neighbourhood graph) on R = 500 synthetic null worlds (no edge; correlated configuration noise calibrated on the
   completed control books, P3_calibration.json), to show the machinery and the reporting format. The real null
   distribution comes only from the QuantConnect null runs after owner approval.

    PYTHONPATH=src python research/phase3/P3_null_precision.py -> P3_null_precision.json
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_p3_grammar as G  # noqa: E402
import qr_p3_pipeline as P  # noqa: E402

RS = (39, 100, 200, 500, 1000)
PS_TRUE = (0.005, 0.01, 0.02, 0.05)
SEED = 20261004


def tau_of(null_T, alpha=0.05):
    """Frozen null threshold: the m-th largest null statistic, m = floor(alpha (R + 1)) (R = 500 -> the 25th largest).
    Q1 (T_real > tau) <=> p = (1 + #{null >= T_real}) / (R + 1) <= alpha."""
    v = np.sort(np.asarray(null_T, float))[::-1]
    m = int(np.floor(alpha * (len(v) + 1)))
    return float(v[m - 1]) if m >= 1 else float("inf")


def clopper_pearson(k, n, a=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)


def binomial_table():
    out = {}
    for R in RS:
        row = {}
        for p in PS_TRUE:
            ks = np.arange(0, R + 1)
            pmf = stats.binom.pmf(ks, R, p)
            his = np.array([clopper_pearson(int(k), R)[1] for k in ks])
            k_med = int(stats.binom.median(R, p))
            row[f"{p:.3f}"] = dict(expected_passes=R * p, typical_interval=clopper_pearson(k_med, R),
                                   p_upper_below_5pct=float(pmf[his < 0.05].sum()),
                                   p_upper_below_10pct=float(pmf[his < 0.10].sum()))
        row["zero_passes_interval"] = clopper_pearson(0, R)
        out[str(R)] = row
    return out


def tau_precision():
    """95% distribution-free interval for the 95th percentile from R draws: order statistics (j, k) with
    P(X_(j) <= q95 <= X_(k)) >= 0.95, expressed as the quantile levels j/R, k/R."""
    out = {}
    for R in RS:
        best = None
        for j in range(1, R + 1):
            for k in range(j + 1, R + 1):
                cov = stats.binom.cdf(k - 1, R, 0.95) - stats.binom.cdf(j - 1, R, 0.95)
                if cov >= 0.95 and (best is None or k - j < best[1] - best[0]):
                    best = (j, k)
        out[str(R)] = dict(order_statistics=best, quantile_range=[best[0] / R, best[1] / R]) if best else \
            dict(order_statistics=None, note="95th percentile not bracketed at 95% confidence")
    return out


def synthetic_null(R=500):
    cal = json.loads((ROOT / "research/phase3/P3_calibration.json").read_text())["model"]
    sig, mu = cal["selection_te_train"], cal["null_selection_drift_vs_ew"]
    C = G.enumerate_configs()
    ids = [c["id"] for c in C]
    ix = {c: i for i, c in enumerate(ids)}
    nb = G.neighbours(C)
    nbi = [np.array([ix[o] for o in nb[c]], dtype=int) for c in ids]
    cpx = [G.complexity(c) for c in C]
    years = list(range(2010, 2018))
    sess = np.array([210] + [252] * 7, float)
    # correlated configuration noise: shared component per primary variant (neighbours share it) + idiosyncratic
    pkey = {}
    for i, c in enumerate(C):
        pkey.setdefault((c["primary"][0], c["primary"][2]), []).append(i)
    rng = np.random.default_rng(SEED)
    res = []
    n = len(C)
    for r in range(R):
        common = rng.normal(0, 0.03, 8)                               # EW-vs-SPY-like common component per year
        g = np.zeros((n, 8))
        for members in pkey.values():
            g[members] += rng.normal(0, sig * np.sqrt(0.6), 8)        # shared within a primary variant
        g += rng.normal(0, sig * np.sqrt(0.4), (n, 8))
        logex = (mu + common[None, :] + g) * sess / 252
        inp = P.Inputs(ids, logex, np.full((n, 8), 1000.0), np.full((n, 8), 1e5) * sess, np.full((n, 8), 4e5),
                       np.full((n, 8), -0.25), sess, np.full(8, -0.25), common * sess / 252, years)
        s = P.world_summary(inp, nbi, cpx)
        res.append(dict(T=s["T"], best_ps=s["best_ps"], wf_pass=s["wf"]["passed"], wf_total=s["wf"]["total_ex_spy"],
                        n_clusters=s["n_clusters"]))
    T = np.array([x["T"] for x in res])
    tau = tau_of(T)
    # leave-one-out: world r passes Q1 if T_r > tau estimated from the other R - 1 worlds; the full search-stage
    # pipeline (Q1 + Q2 walk-forward) passes if, in addition, its walk-forward passes
    q1 = np.array([T[i] > tau_of(np.delete(T, i)) for i in range(R)])
    wf = np.array([x["wf_pass"] for x in res])
    fp = int((q1 & wf).sum())
    fin = T[np.isfinite(T)]
    return dict(worlds=R, tau=tau, worlds_without_cluster=int((~np.isfinite(T)).sum()), wf_pass_rate=float(wf.mean()),
                q1_passes_loo=int(q1.sum()), q1_rate_loo=float(q1.mean()), q1_ci95=clopper_pearson(int(q1.sum()), R),
                full_pipeline_false_passes=fp, false_pass_rate=fp / R, ci95=clopper_pearson(fp, R),
                wf_pass_rate_given_q1=float(wf[q1].mean()) if q1.any() else None,
                T_quantiles={q: float(np.percentile(fin, q)) for q in (5, 50, 95, 99)} if len(fin) else {},
                note="synthetic worlds only (no market data): demonstrates the pipeline and reporting; the real null "
                     "comes from the QuantConnect null runs")


def main():
    out = dict(binomial=binomial_table(), tau=tau_precision(), synthetic_null=synthetic_null())
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(out["synthetic_null"], indent=1, default=float))
    for R in ("39", "200", "500"):
        print(R, out["binomial"][R]["0.010"], out["tau"][R])


if __name__ == "__main__":
    main()
