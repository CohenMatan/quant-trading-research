"""Phase 3 (programme P3, H018) frozen search rules: the local implementation of research/phase3/P3_spec.md §9, §12
(null threshold, Q1, the search-stage false-pass rate) and the pins of the specification and of the configuration list.
The selection procedure itself (score, plateau, clusters, simplicity, walk-forward) lives in
src/qresearch/lean/qr_p3_pipeline.py and runs identically inside LEAN and locally.

tests/test_p3_spec.py pins the spec hash, the configuration-list hash and the behaviour. Nothing here may change after
any search or null result is seen.
"""
from __future__ import annotations

import hashlib
import math
import sys

import numpy as np
from scipy import stats

from . import config

SPEC = "research/phase3/P3_spec.md"
SPEC_SHA256 = "d7fa11235e6bd8d7183f6bc78e1f0b78b847cd41fb94d1898efaae98ceb6ea81"
CONFIG_LIST_SHA256 = "76b3dd3866bc1d0152426d68d1d17d88fce2a13c8f1c98189fb5817b6cba7016"
N_CONFIGS = 1533
PROGRAMME, CYCLE, HYPOTHESIS = "P3", "P3C1", "H018"
SEARCH = ("2010-03-01", "2017-12-31")
WARMUP_START = "2009-07-01"
INTERNAL_OOS = ("2018-01-01", "2021-12-31")
HOLD, SLOTS, CASH = 63, 10, 100000
ALPHA = 0.05
NULL_SEEDS = tuple(range(1, 501))                 # primary: within-date permutation (R = 500)
BLOCK_SEEDS = tuple(range(1001, 1101))            # secondary diagnostic: 63-session block permutation (R = 100)
BLOCK = 63
OOS_G_SE_MIN = 1.0


def spec_hash() -> str:
    return hashlib.sha256((config.REPO_ROOT / SPEC).read_bytes()).hexdigest()


def _grammar():
    p = str(config.REPO_ROOT / "src/qresearch/lean")
    if p not in sys.path:
        sys.path.insert(0, p)
    import qr_p3_grammar
    return qr_p3_grammar


def config_list_hash() -> str:
    """SHA-256 of the canonical configuration list, one line 'id|key' per configuration."""
    G = _grammar()
    return hashlib.sha256("".join(f"{c['id']}|{c['key']}\n" for c in G.enumerate_configs()).encode()).hexdigest()


def tau_of(null_T, alpha=ALPHA) -> float:
    """Null threshold: the m-th largest null statistic, m = floor(alpha (R + 1)); R = 500 -> the 25th largest.
    T_real > tau  <=>  p = (1 + #{null >= T_real}) / (R + 1) <= alpha. Worlds without a cluster count as -inf."""
    v = np.sort(np.asarray(null_T, float))[::-1]
    m = int(math.floor(alpha * (len(v) + 1) + 1e-12))
    return float(v[m - 1]) if m >= 1 else float("inf")


def p_value(T_real, null_T) -> float:
    v = np.asarray(null_T, float)
    return float((1 + np.sum(v >= T_real)) / (len(v) + 1))


def q1(T_real, null_T, alpha=ALPHA) -> bool:
    return bool(np.isfinite(T_real) and T_real > tau_of(null_T, alpha))


def clopper_pearson(k, n, a=0.05):
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


def false_pass(null_T, null_wf_pass, alpha=ALPHA) -> dict:
    """Search-stage false-pass rate of the null worlds: world r passes if T_r > tau estimated from the OTHER worlds
    (leave-one-out) and its walk-forward (Q2) passes. Count, rate and Clopper-Pearson 95% interval."""
    T = np.asarray(null_T, float)
    wf = np.asarray(null_wf_pass, bool)
    R = len(T)
    q = np.array([np.isfinite(T[i]) and T[i] > tau_of(np.delete(T, i), alpha) for i in range(R)])
    k = int((q & wf).sum())
    return dict(repetitions=R, q1_passes=int(q.sum()), q1_rate=float(q.mean()), q1_ci95=clopper_pearson(int(q.sum()), R),
                wf_passes=int(wf.sum()), wf_rate=float(wf.mean()), full_pipeline_passes=k, false_pass_rate=k / R,
                ci95=clopper_pearson(k, R), worlds_without_cluster=int((~np.isfinite(T)).sum()))
