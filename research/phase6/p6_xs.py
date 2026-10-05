"""Phase 6 sector-level cross-sectional signal-test DESIGN REFERENCE (P6-CP1). Pure numpy; SYNTHETIC data only in
P6-CP1 (no real sector return, ranking or IC is computed anywhere in this checkpoint).

Panel: R[t, i] = total return of sector i over month t (t = 0..T-1), N sectors (fixed universe, no missing).
Signal at decision month-end t: S[t, i] = cumulative total return of sector i over months t-L+1 .. t (L = lookback; no
skip). Response: Y[t, i] = R[t+1, i] - mean_i R[t+1, i] (next-month sector-relative total return; monthly decisions,
non-overlapping responses).

Statistics per decision: rank IC = Spearman(S[t], Y[t]); top-k minus average = mean Y over the k highest-signal
sectors. Time series: mean, Newey-West t (lag 0 for non-overlapping monthly responses; lag h-1 for h-month horizons).

Null (primary): IDENTITY-TETHERED DERANGEMENT. A null world draws one fixed permutation pi of the N sector labels with
no fixed point and gives sector i the ENTIRE signal history of sector pi(i). Every return, the common market and
sector co-movement, each signal's persistence and distribution, and the dates are preserved; only the link between a
sector's own signal and its own future relative return is broken. The complete procedure (all pre-declared
lookbacks, the selection rule, all gates) is re-run in every world.
"""
import math

import numpy as np


def avg_rank(x):
    o = np.argsort(x, kind="mergesort")
    r = np.empty(x.size)
    xs = x[o]
    i = 0
    while i < x.size:
        j = i
        while j + 1 < x.size and xs[j + 1] == xs[i]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman_rows(A, B):
    """Row-wise Spearman correlation of two (T, N) arrays (ties averaged)."""
    ra = np.apply_along_axis(avg_rank, 1, A)
    rb = np.apply_along_axis(avg_rank, 1, B)
    ra -= ra.mean(axis=1, keepdims=True)
    rb -= rb.mean(axis=1, keepdims=True)
    den = np.sqrt((ra * ra).sum(axis=1) * (rb * rb).sum(axis=1))
    return np.where(den > 0, (ra * rb).sum(axis=1) / np.where(den > 0, den, 1.0), 0.0)


def nw_t(x, lag):
    x = np.asarray(x, float)
    T = x.size
    e = x - x.mean()
    v = e @ e / T
    for l in range(1, min(lag, T - 1) + 1):
        v += 2 * (1 - l / (lag + 1)) * (e[l:] @ e[:-l]) / T
    se = math.sqrt(max(v, 0.0) / T)
    return float(x.mean()), se, (float(x.mean()) / se if se > 0 else 0.0)


def signal(R, L):
    """S[t] = prod(1 + R[t-L+1..t]) - 1 (NaN for t < L-1)."""
    lg = np.log1p(R)
    cs = np.vstack([np.zeros(R.shape[1]), np.cumsum(lg, axis=0)])
    S = np.full(R.shape, np.nan)
    S[L - 1:] = np.expm1(cs[L:] - cs[:-L])
    return S


def evaluate(S, R, first, k=3, h=1):
    """Decisions t = first .. T-1-h. Y = h-month sector-relative return after t. Returns summary dict."""
    T = R.shape[0]
    ts = np.arange(first, T - h)
    lg = np.log1p(R)
    cs = np.vstack([np.zeros(R.shape[1]), np.cumsum(lg, axis=0)])
    fut = np.expm1(cs[ts + 1 + h] - cs[ts + 1])                       # months t+1 .. t+h
    Y = fut - fut.mean(axis=1, keepdims=True)
    Sd = S[ts]
    ic = spearman_rows(Sd, Y)
    top = np.argsort(-Sd, axis=1, kind="mergesort")[:, :k]
    bot = np.argsort(Sd, axis=1, kind="mergesort")[:, :k]
    tk = np.take_along_axis(Y, top, 1).mean(axis=1)
    bk = np.take_along_axis(Y, bot, 1).mean(axis=1)
    m_ic, se_ic, t_ic = nw_t(ic, h - 1)
    m_tk, _, t_tk = nw_t(tk, h - 1)
    half = ic.size // 2
    return dict(dates=int(ts.size), ic=m_ic, t_ic=t_ic, top_ann=m_tk * 12 / h, t_top=t_tk,
                tmb_ann=float((tk - bk).mean()) * 12 / h, halves=[float(ic[:half].mean()), float(ic[half:].mean())])


def derangement(rng, n):
    while True:
        p = rng.permutation(n)
        if not np.any(p == np.arange(n)):
            return p


def run_world(R, lookbacks, first, seed=None, k=3, h=1):
    """Complete procedure for one world: every pre-declared lookback evaluated; the world statistic is the max t_ic
    over lookbacks (a single-lookback design reduces to its own t_ic)."""
    p = None if seed is None else derangement(np.random.default_rng(seed), R.shape[1])
    out = {}
    for L in lookbacks:
        S = signal(R, L)
        if p is not None:
            S = S[:, p]
        out[L] = evaluate(S, R, first, k, h)
    out["max_t_ic"] = max(out[L]["t_ic"] for L in lookbacks)
    return out
