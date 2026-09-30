"""Phase 2 (programme P2) frozen development rules for H014: the only implementation of
research/phase2/P2_spec.md §7-§10 (D094, frozen 2026-09-30 before any H014 backtest).

Pure functions of equity curves, daily returns and fills; tests/test_p2_spec.py pins the spec hash and
the behaviour. Nothing here may change after an H014 result without an owner-approved amendment.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np
import pandas as pd

from . import config, metrics, stats

SPEC = "research/phase2/P2_spec.md"
SPEC_SHA256 = "220d2856b23e9263c839eee1f28bf3c9fd7aa1f2d0dcf999576085080df1776f"
PROGRAMME, CYCLE = "P2", "P2C1"
DEV = ("2010-01-04", "2021-12-31")
HALVES = (("2010-01-04", "2015-12-31"), ("2016-01-01", "2021-12-31"))
BLOCKS = tuple((f"{y}-01-01", f"{y + 1}-12-31") for y in range(2010, 2022, 2))
MARGIN_EW, MARGIN_SPY = 0.25, 0.10          # G1.1 (fixed budget margin, no escalation)
CAGR_TOL, DD_TOL = 0.02, 0.05               # G1.2, G1.4
G3_MIN_BLOCKS, G3_MAX_SHARE = 4, 0.50
G4_KEEP, G4_MIN_PERTURB, G4_MAX_COST = 0.10, 5, 0.015
DSR_THRESHOLD = 0.90                        # a warning level only (diagnostic)
VAR_SR_P1 = 0.0009463432771146249           # programme-1 frozen dispersion of daily Sharpe (40 candidates)
BOOTSTRAP_SEED, BOOTSTRAP_BLOCK = 20261004, 63
EW_ID, SPY_ID = "E901-07", "E900-07"


def spec_hash() -> str:
    return hashlib.sha256((config.REPO_ROOT / SPEC).read_bytes()).hexdigest()


def equity_series(df: pd.DataFrame) -> pd.Series:
    return pd.Series(df["equity"].to_numpy(float), index=df["date"].astype(str))


def returns(eq: pd.Series) -> pd.Series:
    """Daily simple returns, indexed by the date on which each return is earned."""
    return metrics.returns_from_equity(eq)


def window(r: pd.Series, a: str, z: str) -> pd.Series:
    return r[(r.index >= a) & (r.index <= z)]


def sharpe(r: pd.Series) -> float:
    """Annualised Sharpe: mean / std (ddof 1) of daily returns x sqrt(252); NaN if undefined."""
    return metrics.sharpe(r) if len(r) > 2 else float("nan")


def calmar(eq: pd.Series) -> float:
    dd = metrics.max_drawdown(eq)
    return metrics.cagr(eq) / abs(dd) if dd < 0 else float("nan")


def choose_candidate(r_a: pd.Series, r_b: pd.Series, r_ew: pd.Series) -> dict:
    """§7: B replaces A iff D_B > D_A in BOTH halves, D_X = Sharpe(X, half) - Sharpe(EW, half)."""
    rows = []
    for a, z in HALVES:
        ew = sharpe(window(r_ew, a, z))
        rows.append(dict(half=f"{a}..{z}", d_a=sharpe(window(r_a, a, z)) - ew, d_b=sharpe(window(r_b, a, z)) - ew))
    b_wins = all(np.isfinite(x["d_a"]) and np.isfinite(x["d_b"]) and x["d_b"] > x["d_a"] for x in rows)
    return dict(chosen="B" if b_wins else "A", halves=rows, rule="B replaces A iff D_B > D_A in both halves")


def g1(eq_h: pd.Series, eq_ew: pd.Series, eq_spy: pd.Series) -> dict:
    sh, se, ss = sharpe(returns(eq_h)), sharpe(returns(eq_ew)), sharpe(returns(eq_spy))
    ch, ce = metrics.cagr(eq_h), metrics.cagr(eq_ew)
    dh, de = metrics.max_drawdown(eq_h), metrics.max_drawdown(eq_ew)
    kh, ke = calmar(eq_h), calmar(eq_ew)
    items = {
        "G1.1": dict(value=dict(d_ew=sh - se, d_spy=sh - ss), ok=bool(sh - se >= MARGIN_EW and sh - ss >= MARGIN_SPY)),
        "G1.2": dict(value=dict(cagr=ch, ew=ce), ok=bool(ch >= ce - CAGR_TOL)),
        "G1.3": dict(value=dict(calmar=kh, ew=ke), ok=bool(np.isfinite(kh) and np.isfinite(ke) and kh >= ke)),
        "G1.4": dict(value=dict(max_dd=dh, ew=de), ok=bool(dh >= de - DD_TOL)),
    }
    return dict(items=items, ok=all(v["ok"] for v in items.values()),
                sharpe=sh, sharpe_ew=se, sharpe_spy=ss)


def g2(sharpe_h: float, sharpe_c1: float, sharpe_c2: float, sharpe_r: list[float]) -> dict:
    med = float(np.median(sharpe_r)) if len(sharpe_r) == 3 else float("nan")
    items = {"beats C1": bool(sharpe_h > sharpe_c1), "beats C2": bool(sharpe_h > sharpe_c2),
             "beats median R": bool(np.isfinite(med) and sharpe_h > med)}
    return dict(items=items, median_r=med, ok=all(items.values()))


def g3(r_h: pd.Series, r_ew: pd.Series) -> dict:
    j = pd.concat([r_h.rename("h"), r_ew.rename("ew")], axis=1, join="inner")
    ex = j["h"] - j["ew"]
    total = float(ex.sum())
    rows = []
    for a, z in BLOCKS:
        rows.append(dict(block=f"{a[:4]}-{z[:4]}", d_sharpe=sharpe(window(r_h, a, z)) - sharpe(window(r_ew, a, z)),
                     excess=float(window(ex, a, z).sum())))
    wins = sum(1 for x in rows if np.isfinite(x["d_sharpe"]) and x["d_sharpe"] > 0)
    share = max(x["excess"] for x in rows) / total if total > 0 else float("nan")
    ok = bool(wins >= G3_MIN_BLOCKS and total > 0 and share <= G3_MAX_SHARE)
    return dict(blocks=rows, blocks_beating_ew=wins, total_excess=total, max_block_share=share, ok=ok)


def cost_drag(fills: pd.DataFrame, eq: pd.Series, slippage_rate: float) -> dict:
    """Realised costs a year as a share of mean equity: commissions + traded notional x slippage rate."""
    years = (pd.Timestamp(eq.index[-1]) - pd.Timestamp(eq.index[0])).days / 365.25
    notional = float((fills["quantity"].abs() * fills["price"]).sum())
    comm = float(fills["fee"].sum())
    m = float(eq.mean())
    return dict(commission_pa=comm / m / years, slippage_pa=notional * slippage_rate / m / years,
                total_pa=(comm + notional * slippage_rate) / m / years, turnover_pa=notional / m / years,
                orders=int(fills["order_id"].nunique()) if len(fills) else 0)


def g4(perturbation_d_ew: list[float] | None, d_ew_2x: float | None, drag_pa: float) -> dict:
    """(a) >= 5 of 6 perturbations keep D_EW >= +0.10; (b) 2x slippage keeps D_EW >= +0.10; (c) drag <= 1.5%.
    Items not run (None) fail: a gate that could not be evaluated fails."""
    a = None if perturbation_d_ew is None else sum(1 for d in perturbation_d_ew if np.isfinite(d) and d >= G4_KEEP)
    items = {"G4a": dict(value=a, ok=bool(perturbation_d_ew is not None and len(perturbation_d_ew) == 6
                                          and a >= G4_MIN_PERTURB)),
             "G4b": dict(value=d_ew_2x, ok=bool(d_ew_2x is not None and np.isfinite(d_ew_2x) and d_ew_2x >= G4_KEEP)),
             "G4c": dict(value=drag_pa, ok=bool(np.isfinite(drag_pa) and drag_pa <= G4_MAX_COST))}
    return dict(items=items, ok=all(v["ok"] for v in items.values()))


def robustness_triggered(g1_ok: bool, g2_ok: bool, g3_ok: bool) -> bool:
    """§9: the conditional robustness runs are made iff the chosen candidate passes G1, G2 and G3."""
    return bool(g1_ok and g2_ok and g3_ok)


def dsr_views(r: np.ndarray, n_p2: int, n_p2_broad: int, n_cumulative: int) -> dict:
    out = {}
    for name, n in (("P2 candidates", n_p2), ("P2 broad", n_p2_broad), ("cumulative", n_cumulative)):
        d = stats.deflated_sharpe(r, max(int(n), 1), VAR_SR_P1)
        star = stats.expected_max_sharpe(int(n), VAR_SR_P1)
        out[name] = dict(n=int(n), dsr=d, sr_star_annual=star * math.sqrt(252),
                         warning=bool(not np.isfinite(d) or d < DSR_THRESHOLD))
    return out


def paired_bootstrap_sharpe_diff(r1: pd.Series, r2: pd.Series, n_boot: int = 2000,
                                 block: int = BOOTSTRAP_BLOCK, seed: int = BOOTSTRAP_SEED) -> dict:
    """Stationary block bootstrap (Politis-Romano, mean block `block`) of Sharpe(r1) - Sharpe(r2) on
    date-aligned pairs; 95% percentile interval and the share of draws <= 0. Diagnostic only."""
    j = pd.concat([r1.rename("a"), r2.rename("b")], axis=1, join="inner").to_numpy(float)
    n = len(j)
    rng = np.random.default_rng(seed)
    p = 1.0 / block
    out = np.empty(n_boot)
    t = np.arange(n)
    for k in range(n_boot):
        flags = rng.random(n) < p
        flags[0] = True
        pos = np.flatnonzero(flags)                 # positions where a new block starts
        seg = np.cumsum(flags) - 1
        starts = rng.integers(n, size=len(pos))     # a random start in the sample for each block
        idx = (starts[seg] + t - pos[seg]) % n      # blocks wrap around (circular)
        s = j[idx]
        sd = s.std(axis=0, ddof=1)
        out[k] = (s[:, 0].mean() / sd[0] - s[:, 1].mean() / sd[1]) * math.sqrt(252)
    a, b = j[:, 0], j[:, 1]
    point = (a.mean() / a.std(ddof=1) - b.mean() / b.std(ddof=1)) * math.sqrt(252)
    return dict(point=float(point), ci95=[float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))],
                share_le_0=float((out <= 0).mean()), n_boot=n_boot)


def classify(cagr: float, g1_ok: bool, g2_ok: bool, all_ok: bool) -> dict:
    return {"profitable": bool(np.isfinite(cagr) and cagr > 0), "benchmark-beating": bool(g1_ok),
            "control-beating": bool(g2_ok), "development-qualified": bool(all_ok)}
