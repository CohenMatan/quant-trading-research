"""Phase 3 secondary statistical diagnostics (research/phase3/P3_spec.md §12). NOT gates; the primary multiple-testing
control is the empirical full-search null. Hansen (2005) Superior Predictive Ability test, consistent version (SPA_c),
with the Politis-Romano stationary bootstrap, on the monthly log excess returns of all Stage-1 configurations over SPY.
PBO (CSCV) and DSR reuse the existing qresearch.stats implementations."""
from __future__ import annotations

import math

import numpy as np


def stationary_bootstrap_indices(rng, n, mean_block):
    """One stationary-bootstrap resample of 0..n-1 (geometric blocks, mean length mean_block, circular)."""
    idx = np.empty(n, dtype=np.int64)
    p = 1.0 / mean_block
    i = int(rng.integers(n))
    for t in range(n):
        if t > 0 and rng.random() < p:
            i = int(rng.integers(n))
        idx[t] = i
        i = (i + 1) % n
    return idx


def sb_variance_of_mean(d, mean_block):
    """Exact stationary-bootstrap variance of the sample mean of each column (Politis & Romano 1994, Lemma 1; the
    frozen W2 formula, not annualised): [C(0) + 2 sum_k b(k) C(k)] / T, b(k) = (1-k/T) q^k + (k/T) q^(T-k)."""
    d = np.asarray(d, float)
    T = d.shape[0]
    x = d - d.mean(axis=0)
    f = np.fft.rfft(x, 2 * T, axis=0)
    c = np.fft.irfft(f * np.conj(f), axis=0)[:T] / T
    q = 1.0 - 1.0 / float(mean_block)
    k = np.arange(1, T)
    b = (1 - k / T) * q ** k + (k / T) * q ** (T - k)
    return np.maximum((c[0] + 2 * (b[:, None] * c[1:]).sum(axis=0)) / T, 0.0)


def hansen_spa(d, mean_block=6, n_boot=2000, seed=20261004):
    """d: (T, K) array of the K models' period excess over the benchmark (e.g. monthly log excess vs SPY).
    H0: no model beats the benchmark (all mean excess <= 0). Returns the studentised statistic and the consistent
    p-value (SPA_c)."""
    d = np.asarray(d, float)
    T, K = d.shape
    rng = np.random.default_rng(seed)
    dbar = d.mean(axis=0)
    boots = np.empty((n_boot, K))
    for b in range(n_boot):
        boots[b] = d[stationary_bootstrap_indices(rng, T, mean_block)].mean(axis=0)
    # studentisation as frozen W2: max(iid, exact stationary-bootstrap) standard error (the SB variance alone is biased
    # low in short samples); bootstrap draws are scaled by their own bootstrap standard deviation
    omega = np.sqrt(T * np.maximum(sb_variance_of_mean(d, mean_block), d.var(axis=0, ddof=1) / T))
    omega = np.where(omega > 0, omega, np.inf)
    omega_b = np.sqrt(T) * boots.std(axis=0, ddof=1)
    omega_b = np.where(omega_b > 0, omega_b, np.inf)
    stat = max(float(np.max(np.sqrt(T) * dbar / omega)), 0.0)
    thresh = -math.sqrt(2 * math.log(math.log(T)))
    mu_c = np.where(np.sqrt(T) * dbar / omega <= thresh, dbar, 0.0)      # Hansen: recentre only clearly poor models
    # T* = max_k sqrt(T) (dbar*_k - dbar_k + mu_c_k) / omega_k, floored at 0
    tb = np.maximum(np.max(np.sqrt(T) * (boots - dbar[None, :]) / omega_b + np.sqrt(T) * mu_c[None, :] / omega,
                           axis=1), 0.0)
    p = float(np.mean(tb >= stat))
    best = int(np.argmax(dbar / np.where(np.isfinite(omega), omega, np.inf)))
    return dict(statistic=stat, p_value=p, best_model=best, best_mean=float(dbar[best]), models=K, periods=T,
                mean_block=mean_block, n_boot=n_boot)
