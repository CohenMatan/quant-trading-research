"""Phase 6 SYNTHETIC power / size / effective-sample study for the sector relative-momentum signal test (P6-CP1).
No market data: sector returns are generated from a market factor, a cyclical-vs-defensive style factor, sector noise
and (optionally) a persistent sector drift that creates momentum. Parameters are round, typical magnitudes (monthly
market sd 4.3%, betas 0.6-1.3, style factor sd 2%, sector noise 2.5-5%), not estimates from any real sector series.

  python research/phase6/p6_power.py [--quick]   -> research/phase6/p6_power_result.json
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p6_xs as P  # noqa: E402

QUICK = "--quick" in sys.argv


def make_panel(T, N, drift_sd=0.0, phi=0.95, seed=0):
    """(T, N) monthly total returns. drift_sd = stationary sd of the persistent sector drift (monthly)."""
    rng = np.random.default_rng(seed)
    beta = np.linspace(0.6, 1.3, N)
    load = np.linspace(-1.0, 1.0, N)
    idio = np.linspace(0.025, 0.05, N)
    f = rng.normal(0.007, 0.043, T)
    g = rng.normal(0.0, 0.02, T)
    mu = np.zeros((T, N))
    if drift_sd > 0:
        inn = drift_sd * np.sqrt(1 - phi ** 2)
        m = rng.normal(0, drift_sd, N)
        for t in range(T):
            m = phi * m + rng.normal(0, inn, N)
            mu[t] = m - m.mean()
    return np.outer(f, beta) + np.outer(g, load) + mu + rng.normal(0, 1, (T, N)) * idio


def first_decision(L):
    return L - 1


def nulls(R, lookbacks, first, worlds, seed0):
    return [P.run_world(R, lookbacks, first, seed=seed0 + w)["max_t_ic"] for w in range(worlds)]


def study(T, N, lookbacks, drifts, panels, null_panels, worlds, seed=1):
    first = first_decision(max(lookbacks))
    pool = []
    for i in range(null_panels):
        R = make_panel(T + first, N, seed=seed * 1000 + i)
        pool += nulls(R, lookbacks, first, worlds, 10_000 * (i + 1))
    pool = np.sort(np.array(pool))[::-1]
    c = float(np.quantile(pool, 0.99))
    res = dict(T_decisions=None, N=N, lookbacks=list(lookbacks), c_1pct=c, null_sd=float(pool.std()),
               null_mean=float(pool.mean()), rows=[])
    for d in drifts:
        stats, tops, ics, tmbs = [], [], [], []
        for i in range(panels):
            R = make_panel(T + first, N, drift_sd=d, seed=seed * 7919 + 31 * i + int(d * 1e5))
            w = P.run_world(R, lookbacks, first)
            res["T_decisions"] = w[lookbacks[0]]["dates"]
            stats.append(w["max_t_ic"])
            L0 = lookbacks[0]
            tops.append(w[L0]["top_ann"])
            ics.append(w[L0]["ic"])
            tmbs.append(w[L0]["tmb_ann"])
        stats = np.array(stats)
        res["rows"].append(dict(drift_sd=d, mean_ic=float(np.mean(ics)), mean_top3_vs_avg_ann=float(np.mean(tops)),
                                mean_top_minus_bottom_ann=float(np.mean(tmbs)),
                                power_1pct=float(np.mean(stats > c)), power_5pct_naive=float(np.mean(stats > 1.645))))
    return res


def turnover(N, L, k, drift_sd, T=600, seed=3):
    R = make_panel(T, N, drift_sd=drift_sd, seed=seed)
    S = P.signal(R, L)[L - 1:]
    top = [set(np.argsort(-s, kind="mergesort")[:k].tolist()) for s in S]
    ch = [len(a - b) for a, b in zip(top[1:], top[:-1])]
    return float(np.mean(ch))


def main():
    t0 = time.time()
    panels, null_panels, worlds = (40, 10, 100) if QUICK else (300, 40, 250)
    drifts = (0.0, 0.002, 0.004, 0.006, 0.008, 0.012)
    out = dict(model=dict(market_sd=0.043, market_mean=0.007, beta=[0.6, 1.3], style_sd=0.02, idio_sd=[0.025, 0.05],
                          drift_phi=0.95, note="synthetic; no real sector data"), cases={})
    cases = {
        "N9_2000_2017_L6": (215, 9, (6,)),
        "N9_2010_2017_L6": (89, 9, (6,)),
        "N9_2000_2017_L6_L12_maxstat": (215, 9, (6, 12)),
        "N11_2000_2017_L6": (215, 11, (6,)),
        "N9_2000_2017_L12": (215, 9, (12,)),
    }
    for name, (T, N, lbs) in cases.items():
        out["cases"][name] = study(T, N, lbs, drifts, panels, null_panels, worlds)
        print(name, json.dumps(out["cases"][name]["rows"])[:600], round(time.time() - t0), flush=True)
    # size: independent no-edge panels against c of the primary case
    c = out["cases"]["N9_2000_2017_L6"]["c_1pct"]
    st = [P.run_world(make_panel(215 + 5, 9, seed=900000 + i), (6,), 5)["max_t_ic"] for i in range(panels * 2)]
    out["size_primary"] = dict(panels=len(st), rate_1pct=float(np.mean(np.array(st) > c)),
                               rate_naive_2_33=float(np.mean(np.array(st) > 2.326)), sd=float(np.std(st)))
    out["turnover_top3_changes_per_month"] = {f"L{L}_drift{d}": turnover(9, L, 3, d) for L in (6, 12)
                                              for d in (0.0, 0.006)}
    out["seconds"] = round(time.time() - t0)
    if not QUICK:
        (HERE / "p6_power_result.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "cases"}, indent=1))


if __name__ == "__main__":
    main()
