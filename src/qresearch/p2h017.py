"""H017 development evaluation (research/phase2/H017_spec.md, frozen 2026-10-03): the only implementation of the
spec's gates (Amendment 3 via qresearch.wealth, unchanged), the "Promising but Not Qualified" (PbNQ) rule, the
pre-registered decision tree and the run gating. Written before any H017 candidate, control or diagnostic run.
Nothing here may change after an H017 result."""
from __future__ import annotations

import hashlib
import json
import math

import numpy as np
import pandas as pd

from . import config, p2spec, wealth

SPEC = "research/phase2/H017_spec.md"
SPEC_SHA256 = "975baacb935fd2f06b6dca0f4cf2e17c7a5efd2b35caa6d3783edcd6f7e7efd1"   # frozen 2026-10-03, before the canary; tests/test_p2h017.py
EVENT_MANIFEST = "research/phase2/h017/event_table_v1.json"
EVENT_TABLE_SHA256 = "ebb287536bca42874d36b73443dc0e0c5e02fc78245351e36d7b1c37334a5c70"   # payload, frozen 2026-10-03
COMMON_START, END = "2010-03-01", "2021-12-31"
WARMUP_START = "2009-07-01"
SPY_ID = p2spec.SPY_ID                                                      # E900-07
CANARY = "E982-01"
CANDIDATE, EW_H017, SIZING_200K = "E017-01", "E017-02", "E017-08"
RANDOM = ("E017-03", "E017-04", "E017-05", "E017-06", "E017-07")          # seeds 1..5, frozen
SEEDS = dict(zip(RANDOM, (1, 2, 3, 4, 5)))
SLIP_2X, SLIP_4X, SLIP_6X = "E017-09", "E017-10", "E017-11"
PERTURBATIONS = ("E017-12", "E017-13", "E017-14", "E017-15", "E017-16", "E017-17")   # P1..P6
EVENT_DIAG = "E983-01"
# Runs that need an explicit owner approval before they may execute (owner 2026-10-03): E017-01 consumes slot 3.
APPROVAL_REQUIRED = (CANDIDATE, EW_H017, *RANDOM, SIZING_200K, SLIP_2X, SLIP_4X, SLIP_6X, *PERTURBATIONS, EVENT_DIAG)
PBNQ_MIN_EXCESS = 0.01             # rule 2: +1.0 point a year
PBNQ_MIN_W2_RATIO = 1.0            # rule 3: g / SE >= 1.0 (while W2 at 2.15 fails)
EVENT_MIN_T = 2.0                  # rule 7: month-clustered t of the top-decile mean


def spec_hash() -> str:
    return hashlib.sha256((config.REPO_ROOT / SPEC).read_bytes()).hexdigest()


def event_manifest() -> dict:
    return json.loads((config.REPO_ROOT / EVENT_MANIFEST).read_text())


def window_eq(eq: pd.Series, a: str = COMMON_START, z: str = END) -> pd.Series:
    return eq[(eq.index >= a) & (eq.index <= z)]


def aligned_returns(eqs: dict[str, pd.Series]) -> pd.DataFrame:
    """Daily simple returns of every book on the common window, inner-joined on dates (identical for every book)."""
    return pd.concat({k: p2spec.returns(window_eq(v)) for k, v in eqs.items()}, axis=1, join="inner").dropna()


def gates(R: pd.DataFrame, h: str, spy: str, ew: str, randoms: list[str], cost_pa: float | None,
          no_leverage: bool, limits_ok: bool) -> dict:
    """Amendment 3 W1-W3, R1-R4 on aligned returns (wealth.evaluate_gates, unchanged)."""
    return wealth.evaluate_gates(R[h].to_numpy(), R[spy].to_numpy(), R[ew].to_numpy(),
                                 [R[x].to_numpy() for x in randoms], dates=list(R.index), cost_pa=cost_pa,
                                 no_leverage=no_leverage, limits_ok=limits_ok)


def clustered_t(x, clusters) -> dict:
    """Mean with a month-clustered standard error: SE = sqrt(M/(M-1) * sum_m (sum_{i in m} (x_i - mean))^2) / n."""
    x = np.asarray(x, dtype=float)
    c = np.asarray(clusters)
    n = len(x)
    if n < 2:
        return dict(n=n, months=0, mean=float(x.mean()) if n else float("nan"), se=float("nan"), t=float("nan"))
    mu = float(x.mean())
    s = pd.Series(x - mu).groupby(c).sum().to_numpy()
    m = len(s)
    se = math.sqrt(m / (m - 1) * float((s ** 2).sum())) / n if m > 1 else float("nan")
    return dict(n=n, months=m, mean=mu, median=float(np.median(x)), se=se, t=mu / se if se and se > 0 else float("nan"))


def clustered_from_sums(n_by_month: dict, sum_by_month: dict) -> dict:
    """clustered_t from per-month counts and sums (E983-01 aggregates): residual sum of month m = S_m - n_m * mean."""
    months = [m for m in n_by_month if n_by_month[m] > 0]
    n = int(sum(n_by_month[m] for m in months))
    if n < 2 or len(months) < 2:
        return dict(n=n, months=len(months), mean=float("nan"), se=float("nan"), t=float("nan"))
    mu = sum(sum_by_month[m] for m in months) / n
    r = np.array([sum_by_month[m] - n_by_month[m] * mu for m in months])
    m = len(months)
    se = math.sqrt(m / (m - 1) * float((r ** 2).sum())) / n
    return dict(n=n, months=m, mean=float(mu), se=se, t=mu / se if se > 0 else float("nan"))


def event_rule(top: dict, mid: dict) -> dict:
    """PbNQ rule 7 from the E983-01 groups (dicts from clustered_t): top-decile mean > 0, t >= 2.0, and above the mean
    of deciles 2-9."""
    ok = bool(np.isfinite(top.get("mean", np.nan)) and top["mean"] > 0 and np.isfinite(top.get("t", np.nan))
              and top["t"] >= EVENT_MIN_T and np.isfinite(mid.get("mean", np.nan)) and top["mean"] > mid["mean"])
    return dict(top_mean=top.get("mean"), top_t=top.get("t"), mid_mean=mid.get("mean"), ok=ok)


def pbnq(g: dict, w1_2x_ok: bool | None, event: dict | None) -> dict:
    """The frozen PbNQ rule (spec §7), evaluated in order; an item that could not be evaluated fails."""
    w2 = g["W2"]
    ratio = w2["g"] / w2["se"] if w2["se"] > 0 else float("nan")
    rules = {
        "1_W1": bool(g["W1"]["ok"]),
        "2_excess_ge_1pp": bool(g["W1"]["excess"] >= PBNQ_MIN_EXCESS),
        "3_w2_ratio_ge_1_and_W2_fails": bool(np.isfinite(ratio) and ratio >= PBNQ_MIN_W2_RATIO and not w2["ok"]),
        "4_W3": bool(g["W3"]["ok"]),
        "5_R1_R4": bool(g["R1"]["ok"] and g["R2"]["ok"] and g["R3"]["ok"] and g["R4"]["ok"]),
        "6_W1_at_2x_slippage": bool(w1_2x_ok),
        "7_event_level": bool(event is not None and event.get("ok")),
    }
    return dict(rules=rules, w2_ratio=ratio, ok=all(rules.values()))


def conditional_runs(g: dict) -> dict:
    """Which conditional runs the pre-registered rules allow after the base runs (spec §7)."""
    pb15 = (g["W1"]["ok"] and g["W1"]["excess"] >= PBNQ_MIN_EXCESS and g["W2"]["se"] > 0
            and g["W2"]["g"] / g["W2"]["se"] >= PBNQ_MIN_W2_RATIO and not g["W2"]["ok"] and g["W3"]["ok"]
            and g["R1"]["ok"] and g["R2"]["ok"] and g["R3"]["ok"] and g["R4"]["ok"])
    full = bool(g["core_ok"] and g["R4"]["ok"])
    return {SLIP_2X: bool(pb15 or full), "E017-10..17": full}


def decide(g: dict, g4: dict | None, pb: dict) -> dict:
    """Pre-registered decision tree: C (development-qualified), B (PbNQ) or A (failure)."""
    if g["core_ok"] and g["R4"]["ok"] and g4 is not None and g4["ok"]:
        return dict(case="C", label="development-qualified", consequence="freeze everything; STOP; request Holdout approval")
    if pb["ok"]:
        return dict(case="B", label="Promising but Not Qualified",
                    consequence="H017 frozen; Holdout locked; STOP; owner may consider a data purchase only to re-test "
                                "the same frozen H017. No Holdout, no production, no declaration of success")
    return dict(case="A", label="failure", consequence="H017 rejected; no tuning; no data purchase")
