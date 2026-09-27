"""Multiple-testing and robustness statistics.

* PSR / DSR: Bailey & López de Prado (2012, 2014). Sharpe ratios here are per-period (daily),
  not annualised, as the formulas require.
* PBO via CSCV: Bailey, Borwein, López de Prado & Zhu (2015).
* Trade-distribution helpers: profit concentration, best-trade removal, bootstrap CI.
"""
from __future__ import annotations

import itertools
import math

import numpy as np
import pandas as pd
from scipy.stats import norm

EULER_GAMMA = 0.5772156649015329


def sharpe_per_period(r: np.ndarray) -> float:
    r = np.asarray(r, dtype=float)
    sd = r.std(ddof=1)
    return float(r.mean() / sd) if sd > 0 else float("nan")


def probabilistic_sharpe(r: np.ndarray, sr_benchmark: float = 0.0) -> float:
    """P(true SR > sr_benchmark) given the observed per-period returns r."""
    r = np.asarray(r, dtype=float)
    n = len(r)
    sr = sharpe_per_period(r)
    if n < 3 or not np.isfinite(sr):
        return float("nan")
    s = pd.Series(r)
    skew, kurt = float(s.skew()), float(s.kurt() + 3.0)
    denom = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    if denom <= 0:
        return float("nan")
    return float(norm.cdf((sr - sr_benchmark) * math.sqrt(n - 1) / math.sqrt(denom)))


def expected_max_sharpe(n_trials: int, var_sr: float) -> float:
    """Expected maximum of n_trials per-period Sharpe estimates under the null of zero skill."""
    if n_trials <= 1 or var_sr <= 0:
        return 0.0
    z1 = norm.ppf(1.0 - 1.0 / n_trials)
    z2 = norm.ppf(1.0 - 1.0 / (n_trials * math.e))
    return float(math.sqrt(var_sr) * ((1.0 - EULER_GAMMA) * z1 + EULER_GAMMA * z2))


def deflated_sharpe(r: np.ndarray, n_trials: int, var_sr: float) -> float:
    """DSR = PSR against the expected maximum Sharpe of n_trials independent tries.

    n_trials comes from the experiment registry; var_sr is the variance of the per-period Sharpe
    ratios across those trials. With one trial DSR equals PSR(0).
    """
    return probabilistic_sharpe(r, expected_max_sharpe(n_trials, var_sr))


def pbo_cscv(returns: pd.DataFrame | np.ndarray, n_blocks: int = 16) -> dict:
    """Probability of Backtest Overfitting by combinatorially symmetric cross-validation.

    returns: T × N matrix (rows = periods, columns = strategy variations). Rows are cut into
    n_blocks contiguous blocks; for every choice of half the blocks as IS the best-IS variation's
    OOS rank is recorded. PBO = share of splits where that variation lands at or below the OOS median.
    """
    m = np.asarray(returns, dtype=float)
    t, n = m.shape
    if n < 2:
        raise ValueError("PBO needs at least two variations")
    if n_blocks % 2 or n_blocks < 2:
        raise ValueError("n_blocks must be even and >= 2")
    blocks = np.array_split(np.arange(t), n_blocks)
    logits = []
    for is_ids in itertools.combinations(range(n_blocks), n_blocks // 2):
        is_rows = np.concatenate([blocks[i] for i in is_ids])
        oos_rows = np.concatenate([blocks[i] for i in range(n_blocks) if i not in is_ids])
        sr_is = _col_sharpe(m[is_rows])
        sr_oos = _col_sharpe(m[oos_rows])
        best = int(np.nanargmax(sr_is))
        # relative rank of the IS winner among OOS results, in (0, 1)
        rank = (np.sum(sr_oos < sr_oos[best]) + 0.5 * (np.sum(sr_oos == sr_oos[best]) - 1) + 1) / (n + 1)
        logits.append(math.log(rank / (1.0 - rank)))
    logits_arr = np.array(logits)
    return dict(pbo=float(np.mean(logits_arr <= 0.0)), n_splits=len(logits),
                logit_median=float(np.median(logits_arr)))


def _col_sharpe(x: np.ndarray) -> np.ndarray:
    sd = x.std(axis=0, ddof=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(sd > 0, x.mean(axis=0) / sd, np.nan)


def profit_concentration(pnl: pd.Series, fractions=(0.01, 0.05, 0.10)) -> dict:
    """Share of total net profit contributed by the top x% of trades by PnL."""
    p = pnl.dropna().sort_values(ascending=False)
    total = p.sum()
    out = {}
    for f in fractions:
        k = max(1, int(math.ceil(f * len(p)))) if len(p) else 0
        out[f"top_{int(f * 100)}pct_share"] = float(p.iloc[:k].sum() / total) if total > 0 and k else float("nan")
    return out


def expectancy_without_best(ret: pd.Series, n_best: int) -> float:
    r = ret.dropna().sort_values(ascending=False)
    rest = r.iloc[n_best:]
    return float(rest.mean()) if len(rest) else float("nan")


def bootstrap_mean_ci(x: np.ndarray, n_boot: int = 10_000, alpha: float = 0.05, seed: int = 12345) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n_boot, len(x)), replace=True).mean(axis=1)
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))
