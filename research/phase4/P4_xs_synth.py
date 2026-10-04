"""Synthetic daily price panels for the H019 pipeline (P4-CP3R2): leakage canaries (tests/test_xs_pipeline.py) and the
end-to-end synthetic study (P4_xs_e2e.py). SYNTHETIC ONLY: no market data.

Daily log returns = beta x market + sector + style loadings x style factors + idiosyncratic (+ an optional planted
monthly drift that depends only on information available at the previous month-end). Stocks list late (IPOs) and
delist early. Split-adjusted closes differ from total-return closes by a dividend drift; opens carry part of the
daily move. Month = `spm` sessions; months are labelled consecutively from `start`.
"""
import math

import numpy as np

NSEC, NSTYLE = 12, 4


def make_panel(N=60, months=40, spm=21, seed=0, first_research_k=14, start=(2009, 1), edge=None,
               sig_mkt=0.010, sig_sec=0.006, sig_style=0.004, sig_idio=0.016, ipo_share=0.15, delist_share=0.10,
               style_persist=True):
    """Returns (panel_kwargs, info). edge(k, P_hist, Q_hist, alive) -> per-stock expected log return for month k+1
    (P_hist / Q_hist: rows <= the month-k close)."""
    rng = np.random.default_rng(seed)
    D = months * spm + 1                                       # one extra session after the last month-end
    me = [spm * (k + 1) - 1 for k in range(months)]
    labels, (y, m) = [], start
    for _ in range(months):
        labels.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    beta = rng.normal(1.0, 0.3, N)
    sec = rng.integers(0, NSEC, N)
    load = rng.normal(size=(N, NSTYLE))
    born = np.zeros(N, int)
    died = np.full(N, D)
    ipo = rng.random(N) < ipo_share
    born[ipo] = rng.integers(spm * 6, D - spm * 6, ipo.sum())
    dl = rng.random(N) < delist_share
    died[dl] = rng.integers(spm * 6, D - spm, dl.sum())
    lr = np.zeros((D, N))
    mkt = rng.normal(0.0003, sig_mkt, D)
    fs = rng.normal(0, sig_sec, (D, NSEC))
    fst = rng.normal(0, sig_style, (D, NSTYLE))
    if style_persist:                                          # mildly persistent style returns (momentum-like)
        for t in range(1, D):
            fst[t] += 0.05 * fst[t - 1]
    eps = rng.normal(0, sig_idio, (D, N))
    base = beta[None, :] * mkt[:, None] + fs[:, sec] + fst @ load.T + eps
    drift = np.zeros(N)
    P = np.full((D, N), np.nan)
    logp = np.zeros(N)
    alive = lambda t: (t >= born) & (t < died)
    for t in range(D):
        if edge is not None and t > 0 and (t - 1) in me and t - 1 < me[-1]:
            k = me.index(t - 1)
            drift = edge(k, P[:t], None, alive(t - 1)) / spm
        lr[t] = base[t] + drift
        logp = np.where(t == born, 0.0, logp + lr[t])
        P[t] = np.where(alive(t), 100.0 * np.exp(logp), np.nan)
    div = np.exp(-0.00008 * np.arange(D))[:, None]
    Q = P * div                                                 # split-adjusted, not dividend-adjusted
    O = np.full_like(P, np.nan)
    O[1:] = P[:-1] * np.exp(0.3 * lr[1:])
    O[~np.isfinite(P)] = np.nan
    elig = np.zeros((months, N), bool)
    for k in range(first_research_k, months):
        elig[k] = np.isfinite(P[me[k]]) & (me[k] - born >= 20)
    return dict(split_close=Q, tr_close=P, tr_open=O, month_end=me, months=labels, elig=elig), \
        dict(first_research=labels[first_research_k], labels=labels, born=born, died=died)
