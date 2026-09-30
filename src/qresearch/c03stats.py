"""C03 multiple-testing statistics, frozen by D082 (owner-approved 2026-09-30, before any C03 result).

The specification in words is research/cycles/C03_statistical_spec.md; this module is its only
implementation, and tests/test_c03_stats.py pins it. Nothing here may change after a C03 result.

Trial counts (Clarification A), from the append-only registry at the evaluation commit:
    official     N = S                      (cumulative distinct selection candidates; 43 in C03)
    conservative N = S + P + R + V          (P = H013 replicate seeds, R = robustness, V = Validation)
Sharpe dispersion: ddof-1 variance of the daily Sharpe over the selection candidates' latest valid
IS runs (an H013 candidate's value is the mean of its seeds' daily Sharpes); one value for both N.

Deflated Sharpe (Clarification B), per deployable book (an H012 variation run; each H013 seed run):
    r   = daily simple returns of the net IS equity curve, then of the net VAL equity curve,
          concatenated (two separate backtests; no return bridges the IS end and the VAL start)
    n   = len(r); SR = mean(r) / std(r, ddof=1) (per day, not annualised)
    skew = pandas skew (adjusted Fisher-Pearson); kurtosis = pandas kurt (excess, adjusted) + 3
    SR* = expected maximum daily Sharpe of N skill-less tries = sqrt(V)[(1-g) z(1-1/N) + g z(1-1/(N e))]
    DSR = Phi[(SR - SR*) sqrt(n - 1) / sqrt(1 - skew SR + (kurt - 1)/4 SR^2)]
    pass = DSR >= 0.90 at the official N AND at the conservative N (not rounded; NaN fails).
IS-only and VAL-only figures are reported as diagnostics and never gate.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from . import config, metrics, registry, stats

THRESHOLD = 0.90
OFFICIAL_N_C03 = 40          # Amendment 1 (D087): 37 before C03 + the 3 H013 variations (H012 removed, never run)
SENSITIVITY_N_C03 = 43       # Amendment 1: the originally planned count, a reported sensitivity, never a gate
PRE_C03 = dict(official=37, conservative=64)
SPEC = "research/cycles/C03_statistical_spec.md"
SPEC_SHA256 = "74ce5351fe3c4915a61b8e63bf0ffea0741ac8bb28d81efeb59dd33fedcea66e"   # D082: the frozen text
AMENDMENTS = {"research/cycles/C03_statistical_spec_amendment_1.md": "d6634b710cc02e4623d570eec517c752e38bc240144e798b4b0d272ad2528141"}   # D087, owner-approved


class SpecError(RuntimeError):
    pass


def snapshot(path: Path | None = None, experiments_dir: Path | None = None,
             retired: set[str] | None = None, expect_official: int | None = None) -> dict:
    """Trial counts and Sharpe dispersion from the registry as it stands (Clarification A).
    `expect_official` (40 for the C03 evaluation, Amendment 1) makes a different official N an error to
    investigate, never a silent change."""
    p = path or config.INDEX_CSV
    if retired is None:
        from .cycle import retired_ids
        retired = set(retired_ids())
    acc = registry.trial_accounting(p, experiments_dir, retired=retired)
    sharpe = {r["experiment_id"]: r["sharpe"] for r in registry.read(p) if r["run_type"] == "original"}
    values = {}
    for cand, members in acc["selection_members"].items():
        srs = [float(sharpe[e]) / math.sqrt(252) for e in members if e and sharpe.get(e)]
        if srs:
            values[cand] = float(np.mean(srs))
    v = list(values.values())
    official = acc["selection_trials"]
    conservative = official + acc["replicate_runs"] + acc["robustness_runs"] + acc["validation_runs"]
    if expect_official is not None and official != expect_official:
        raise SpecError(f"official N is {official}, the frozen C03 value is {expect_official}: investigate "
                        "the registry before any DSR is computed")
    return dict(official=official, conservative=conservative,
                components=dict(selection=official, replicate=acc["replicate_runs"],
                                robustness=acc["robustness_runs"], validation=acc["validation_runs"]),
                excluded=dict(technical_repeats=acc["technical_repeats"], not_started=acc["not_started"],
                              verification_benchmark_sizing_stress=acc["verification_and_benchmark_runs"]),
                var_sr=float(np.var(v, ddof=1)) if len(v) > 1 else 0.0, n_sharpes=len(v),
                registry_sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest(),
                registry_rows=len(registry.read(p)))


def book_returns(is_equity: pd.Series, val_equity: pd.Series | None = None) -> np.ndarray:
    """Daily simple returns of the IS equity curve followed by those of the VAL curve. Each curve is a
    separate backtest starting from cash, so there is no return from the IS end to the VAL start."""
    r = [metrics.returns_from_equity(is_equity).to_numpy(float)]
    if val_equity is not None:
        if str(val_equity.index[0]) <= str(is_equity.index[-1]):
            raise SpecError("the VAL curve must start after the IS curve ends")
        r.append(metrics.returns_from_equity(val_equity).to_numpy(float))
    out = np.concatenate(r)
    if not np.all(np.isfinite(out)):
        raise SpecError("non-finite daily return in the equity curve")
    return out


def dsr_at(r: np.ndarray, n_trials: int, var_sr: float) -> dict:
    sr_star = stats.expected_max_sharpe(n_trials, var_sr)
    d = stats.deflated_sharpe(r, max(int(n_trials), 1), var_sr)
    return dict(n_trials=int(n_trials), sr_star_daily=sr_star, sr_star_annual=sr_star * math.sqrt(252),
                dsr=d, ok=bool(np.isfinite(d) and d >= THRESHOLD))


def describe(r: np.ndarray) -> dict:
    s = pd.Series(r)
    sr = stats.sharpe_per_period(r)
    return dict(n_obs=len(r), sharpe_daily=sr, sharpe_annual=sr * math.sqrt(252),
                skew=float(s.skew()), kurtosis=float(s.kurt() + 3.0))


def evaluate_book(name: str, is_equity: pd.Series, val_equity: pd.Series, snap: dict) -> dict:
    """The D082 DSR gate for one deployable book, plus the IS-only and VAL-only diagnostics."""
    r = book_returns(is_equity, val_equity)
    off = dsr_at(r, snap["official"], snap["var_sr"])
    con = dsr_at(r, snap["conservative"], snap["var_sr"])
    r_is, r_val = book_returns(is_equity), book_returns(val_equity)
    diag = dict(is_only=dict(describe(r_is), dsr_official=dsr_at(r_is, snap["official"], snap["var_sr"])["dsr"],
                             dsr_conservative=dsr_at(r_is, snap["conservative"], snap["var_sr"])["dsr"]),
                val_only=dict(describe(r_val), psr_0=stats.probabilistic_sharpe(r_val, 0.0),
                              dsr_official=dsr_at(r_val, snap["official"], snap["var_sr"])["dsr"],
                              dsr_conservative=dsr_at(r_val, snap["conservative"], snap["var_sr"])["dsr"]))
    diag["sensitivity_n43"] = dsr_at(r, SENSITIVITY_N_C03, snap["var_sr"])      # Amendment 1: reported only
    return dict(book=name, combined=describe(r), official=off, conservative=con, ok=off["ok"] and con["ok"],
                diagnostics_not_gates=diag)


def hypothesis_passes(books: list[dict]) -> bool:
    """Every seed's book of an H013 variation must pass; a missing or failed seed fails the variation."""
    return bool(books) and all(b["ok"] for b in books)


def amendment_hashes() -> dict:
    import hashlib as _h
    return {p: _h.sha256((config.REPO_ROOT / p).read_bytes()).hexdigest() for p in AMENDMENTS}


def spec_hash() -> str:
    return hashlib.sha256((config.REPO_ROOT / SPEC).read_bytes()).hexdigest()


def main() -> int:
    print(json.dumps(snapshot(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
