"""Phase 2 Amendment 3: terminal-wealth evaluation framework (owner 2026-10-02; frozen spec
research/phase2/P2_amendment3_spec.md, hash-pinned in AMENDMENT3_SHA256).

Objective: starting with the same capital on the same date, finish with more wealth than S&P 500 buy-and-hold
(SPY total return) after realistic costs, without leverage. The gates:
  W1  objective      CAGR(H) > CAGR(SPY)  (equivalently terminal wealth above SPY's over the same dates)
  W2  evidence       g >= W2_CRITICAL (2.15) * SE, where g = 252 * mean(log(1 + r_H) - log(1 + r_SPY)) is the annualised
                     growth of the log wealth ratio and SE = max(iid SE, exact stationary-bootstrap SE of that mean
                     (Politis & Romano 1994), mean block W2_MEAN_BLOCK sessions): serial-dependence aware, never
                     smaller than the iid SE, deterministic (no Monte Carlo noise)
  W3  attribution    CAGR(H) > CAGR(same-universe EW) and CAGR(H) > median CAGR of the five matched random books
  R1  drawdown       MaxDD(H) >= MaxDD(SPY) - R1_MAX_EXTRA_DD
  R2  risk-adjusted  Sharpe(H) >= Sharpe(SPY) - R2_TOLERANCE
  R3  no lucky period total log excess over SPY > 0 and no two-year block contributes more than half of it
  R4  implementation realised costs <= 1.5% a year; no leverage; account and concentration limits (inputs)
  G4' robustness     (conditional) >= 5 of 6 pre-declared perturbations keep W1; at 2x slippage W1 still holds
Rolling 1/3/5/10-year comparisons are REPORTED only (rolling_report), never gates.
The constants below were fixed from completed CONTROL books only (research/phase2/architecture/
P2_amend3_calibration.py) before any new hypothesis was chosen; nothing here may change after a candidate result."""
from __future__ import annotations

import hashlib
import math

import numpy as np

from . import config

SPEC = "research/phase2/P2_amendment3_spec.md"
AMENDMENT3_SHA256 = "10fe4cbe69c4bd9f3e8f2576f43ad03002f9b4c2ffd46cee5c143e048c9cb2ab"   # frozen 2026-10-03 (D121); tests/test_wealth.py
TRADING_DAYS = 252
W2_CRITICAL = 2.15                       # one-sided critical value, calibrated (P2_amend3_calibration.json) so the
                                         # false-pass rate is <= ~5% for relative-performance processes with one-year
                                         # variance ratio up to 1.25 and half-lives up to a year (controls: <= 1.08)
W2_METHOD = "max(iid, stationary_bootstrap)"   # the larger of the two standard errors (conservative)
W2_MEAN_BLOCK = 126                      # sessions (calibration: P2_amend3_calibration.json)
R1_MAX_EXTRA_DD = 0.10
R2_TOLERANCE = 0.15
R3_MAX_BLOCK_SHARE = 0.50
R4_MAX_COST = 0.015
G4_MIN_PERTURB_KEEP = 5
HORIZONS = {"1y": 252, "3y": 756, "5y": 1260, "10y": 2520}


def spec_hash() -> str:
    return hashlib.sha256((config.REPO_ROOT / SPEC).read_bytes()).hexdigest()


# ---------------------------------------------------------------- basic statistics on daily simple returns
def _a(x):
    return np.asarray(x, dtype=float)


def cagr(r, years=None):
    r = _a(r)
    years = len(r) / TRADING_DAYS if years is None else years
    return float(np.prod(1 + r) ** (1 / years) - 1)


def sharpe(r):
    r = _a(r)
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")


def max_drawdown(r):
    eq = np.cumprod(1 + _a(r))
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
    return float((eq / peak - 1).min())


def log_excess(r_h, r_b):
    return np.log1p(_a(r_h)) - np.log1p(_a(r_b))


# ---------------------------------------------------------------- W2 standard errors of the mean of d (annualised)
def se_iid(d):
    d = _a(d)
    return float(d.std(ddof=1) * TRADING_DAYS / math.sqrt(len(d)))


def _autocov(d):
    """Biased (1/n) autocovariances at lags 0..n-1."""
    x = _a(d) - np.mean(d)
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    return np.fft.irfft(f * np.conj(f))[:n] / n


def se_newey_west(d, lags):
    g = _autocov(d)
    n = len(g)
    L = min(int(lags), n - 1)
    k = np.arange(1, L + 1)
    v = g[0] + 2 * np.sum((1 - k / (L + 1)) * g[1:L + 1])
    return float(math.sqrt(max(v, 0.0) / n) * TRADING_DAYS)


def se_stationary_bootstrap(d, mean_block):
    """Exact standard error of the mean under the stationary bootstrap (Politis & Romano 1994, Lemma 1):
    Var* = (1/n) [C(0) + 2 sum_{k=1}^{n-1} b(k) C(k)], b(k) = (1 - k/n) q^k + (k/n) q^(n-k), q = 1 - 1/mean_block,
    with C the ordinary (1/n) sample autocovariances. Annualised (x 252)."""
    c = _autocov(d)
    n = len(c)
    q = 1.0 - 1.0 / float(mean_block)
    k = np.arange(1, n)
    b = (1 - k / n) * q ** k + (k / n) * q ** (n - k)
    v = c[0] + 2 * np.sum(b * c[1:])
    return float(math.sqrt(max(v, 0.0) / n) * TRADING_DAYS)


def se_w2(d, mean_block=None):
    """W2 standard error: max(iid, exact stationary bootstrap with mean block `mean_block`). The bootstrap term
    captures positive serial dependence (persistent relative performance, overlapping holdings); the iid floor
    prevents noisy NEGATIVE long-lag autocovariance estimates from shrinking the standard error."""
    return max(se_iid(d), se_stationary_bootstrap(d, W2_MEAN_BLOCK if mean_block is None else mean_block))


def w2_test(r_h, r_spy, mean_block=None, z=None):
    mean_block = W2_MEAN_BLOCK if mean_block is None else mean_block
    z = W2_CRITICAL if z is None else z
    d = log_excess(r_h, r_spy)
    g = TRADING_DAYS * float(d.mean())
    se = se_w2(d, mean_block)
    return dict(g=g, se=se, z=g / se if se > 0 else float("nan"), threshold=z * se, ok=bool(g >= z * se))


# ---------------------------------------------------------------- gates
def r1_ok(max_dd_h, max_dd_spy):
    return bool(max_dd_h >= max_dd_spy - R1_MAX_EXTRA_DD)


def r2_ok(sharpe_h, sharpe_spy):
    return bool(sharpe_h >= sharpe_spy - R2_TOLERANCE)


def _blocks(n, dates=None, block_days=504):
    if dates is None:
        idx = np.arange(n) // block_days
        return [idx == b for b in range(int(idx.max()) + 1)]
    yrs = np.array([int(str(d)[:4]) for d in dates])
    y0 = yrs.min()
    key = (yrs - y0) // 2
    return [key == b for b in range(int(key.max()) + 1)]


def evaluate_gates(r_h, r_spy, r_ew, r_randoms, years=None, dates=None, cost_pa=None, no_leverage=True,
                   limits_ok=True):
    """Amendment 3 development gates on aligned daily simple returns (common window). r_randoms: the five matched
    random books (W3 uses their median CAGR; fewer than five -> W3 fails). R4 inputs come from the run records."""
    r_h, r_spy, r_ew = _a(r_h), _a(r_spy), _a(r_ew)
    ch, cs, ce = cagr(r_h, years), cagr(r_spy, years), cagr(r_ew, years)
    cr = [cagr(x, years) for x in r_randoms]
    w1 = dict(cagr=ch, spy=cs, excess=ch - cs, ok=bool(ch > cs))
    w2 = w2_test(r_h, r_spy)
    med = float(np.median(cr)) if len(cr) == 5 else float("nan")
    w3 = dict(ew=ce, median_random=med, ok=bool(len(cr) == 5 and ch > ce and ch > med))
    dh, ds = max_drawdown(r_h), max_drawdown(r_spy)
    r1 = dict(max_dd=dh, spy=ds, ok=r1_ok(dh, ds))
    sh, ss = sharpe(r_h), sharpe(r_spy)
    r2 = dict(sharpe=sh, spy=ss, ok=r2_ok(sh, ss))
    d = log_excess(r_h, r_spy)
    tot = float(d.sum())
    shares = [float(d[m].sum()) for m in _blocks(len(d), dates)]
    share = max(shares) / tot if tot > 0 else float("nan")
    r3 = dict(total_log_excess=tot, block_excess=shares, max_block_share=share,
              ok=bool(tot > 0 and share <= R3_MAX_BLOCK_SHARE))
    r4 = dict(cost_pa=cost_pa, ok=bool((cost_pa is not None and cost_pa <= R4_MAX_COST) and no_leverage and limits_ok))
    core = w1["ok"] and w2["ok"] and w3["ok"] and r1["ok"] and r2["ok"] and r3["ok"]
    return dict(W1=w1, W2=w2, W3=w3, R1=r1, R2=r2, R3=r3, R4=r4, core_ok=bool(core),
                qualified=bool(core) if cost_pa is None else bool(core and r4["ok"]))


def g4_prime(perturbation_w1_ok: list[bool] | None, w1_ok_2x_slippage: bool | None) -> dict:
    a = None if perturbation_w1_ok is None else sum(bool(x) for x in perturbation_w1_ok)
    ok_a = bool(perturbation_w1_ok is not None and len(perturbation_w1_ok) == 6 and a >= G4_MIN_PERTURB_KEEP)
    ok_b = bool(w1_ok_2x_slippage)
    return dict(perturbations_keeping_w1=a, slippage_2x_keeps_w1=ok_b, ok=ok_a and ok_b)


# ---------------------------------------------------------------- reporting
def wealth_table(eq_h, eq_spy, years=None) -> dict:
    """The primary economic table: same capital, same dates."""
    eq_h, eq_spy = _a(eq_h), _a(eq_spy)
    years = (len(eq_h) - 1) / TRADING_DAYS if years is None else years
    c0 = float(eq_h[0])
    fs = float(eq_spy[-1] / eq_spy[0] * c0)
    fh = float(eq_h[-1])
    ch, cs = (fh / c0) ** (1 / years) - 1, (fs / c0) ** (1 / years) - 1
    return dict(starting_capital=c0, final_strategy=fh, final_spy=fs, strategy_total_return=fh / c0 - 1,
                spy_total_return=fs / c0 - 1, strategy_cagr=ch, spy_cagr=cs, excess_cagr=ch - cs,
                terminal_wealth_ratio=fh / fs)


def rolling_report(r_book, r_spy) -> dict:
    """Rolling 1/3/5/10-year comparison with SPY over every start date (reported, never a gate)."""
    lb, ls = np.log1p(_a(r_book)), np.log1p(_a(r_spy))
    cb, cs = np.concatenate([[0.0], np.cumsum(lb)]), np.concatenate([[0.0], np.cumsum(ls)])
    out = {}
    for h, n in HORIZONS.items():
        if len(lb) < n:
            out[h] = dict(windows=0)
            continue
        yrs = n / TRADING_DAYS
        xb, xs = cb[n:] - cb[:-n], cs[n:] - cs[:-n]
        ex = np.exp(xb / yrs) - np.exp(xs / yrs)
        out[h] = dict(windows=int(len(ex)), independent_windows=round(len(lb) / n, 2),
                      share_beats_spy=float((xb > xs).mean()), mean_excess_cagr=float(ex.mean()),
                      median_excess_cagr=float(np.median(ex)), p10=float(np.percentile(ex, 10)),
                      p90=float(np.percentile(ex, 90)), worst=float(ex.min()), best=float(ex.max()))
    return out
