"""Research-programme review C01-C03 (owner request 2026-09-30): one consolidated, uniform table.

Uses only committed, derived IS results (2010-01-04..2017-12-29) of runs that already exist. No new
backtest; no Validation, Walk-Forward or Holdout data (the one C01 Validation outcome is quoted from its
published report, research/validation/E005-28_validation.json, unchanged). Official verdicts are taken
from each cycle's own records and are NOT recomputed or changed; metrics are recomputed uniformly with
the shared metrics module so that the cycles can be compared on one basis.

    PYTHONPATH=src python research/cycles/programme_review.py -> research/cycles/programme_review.json
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")
from qresearch import registry  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("c03_eval", ROOT / "research/cycles/C03_eval.py")
EV = importlib.util.module_from_spec(spec)
spec.loader.exec_module(EV)

NAMES = {
    "H001": "Short-term oversold reversal (RSI)", "H002": "Price momentum", "H003": "52-week-high proximity",
    "H004": "Momentum pullback", "H005": "Low volatility", "H006": "Breakout", "H007": "Volatility squeeze",
    "H008": "Residual relative strength", "H009": "Volume shock", "H010": "Gap and hold",
    "H011": "Seasonality", "H012": "Volatility-managed exposure", "H013": "Lottery-stock avoidance"}

# Official outcomes as recorded (not recomputed): the furthest stage each candidate reached.
OFFICIAL = {   # keyed by (hypothesis, version): candidate ids are the first-started run of each configuration
    ("H005", "v1.0"): "passed IS screen; not chosen for Validation (S005 v1.2 chosen, D056)",
    ("H005", "v1.1"): "passed IS screen; not chosen for Validation (S005 v1.2 chosen, D056)",
    ("H005", "v1.2"): "passed IS screen; FAILED Validation (DSR 0.68 < 0.90; PBO 0.71 > 0.30) - E005-28, D060",
    ("H007", "v1.1"): "passed IS screen; FAILED robustness (plateau 5/8 < 7/8) - D076",
}


def candidates():
    """The 40 official selection candidates, each with its latest valid run(s) (H013: its 3 seed books)."""
    from qresearch.cycle import retired_ids
    acc = registry.trial_accounting(retired=set(retired_ids()))
    out = []
    for cand, members in acc["selection_members"].items():
        cfg = json.loads((ROOT / "experiments" / cand / "config.json").read_text())
        out.append(dict(candidate=cand, hypothesis=cfg["hypothesis_id"], version=cfg["strategy_version"],
                        cycle=cfg.get("cycle") or "C01", runs=[m for m in members if m]))
    return out


IS_START, IS_END = "2010-01-04", "2017-12-29"


def bench_is(eid):
    """Benchmark metrics over IS only: the benchmark runs span 2010-2021, so they are cut to the IS dates
    before anything is computed (no Validation-period data is used)."""
    from qresearch import metrics, results
    eq = results.read_csv_gz(ROOT / "experiments" / eid / "equity.csv.gz")
    eq = eq[(eq["date"].astype(str) >= IS_START) & (eq["date"].astype(str) <= IS_END)].reset_index(drop=True)
    assert str(eq["date"].iloc[-1]) <= IS_END
    m = metrics.compute_metrics(eq)
    return dict(sharpe=m["sharpe"], cagr=m["cagr"], max_dd=m["max_drawdown"], last_date=str(eq["date"].iloc[-1]))


def main():
    ew = bench_is("E901-07")
    spy = bench_is("E900-07")
    null = [EV.book(e) for e in ("E962-22", "E962-23", "E962-24")]
    rows = []
    for c in candidates():
        books = [EV.book(r) for r in c["runs"]]
        books = [b for b in books if b.get("status") == "completed"]
        if not books:
            rows.append(dict(c, status="no valid run"))
            continue
        agg = {k: float(np.mean([b[k] for b in books])) for k in ("sharpe", "cagr", "max_dd", "exposure_mean")}
        agg["trades"] = float(np.mean([b["trades"] for b in books]))
        cost = {k: float(np.mean([b["costs"][k] for b in books])) for k in
                ("commission_drag_pa", "slippage_drag_pa", "turnover_pa")}
        official = OFFICIAL.get((c["hypothesis"], c["version"]), "failed IS screen")
        if c["hypothesis"] == "H013":
            official = "failed IS screen (all 3 seeds); effect refuted - D089"
        if agg["cagr"] <= 0:
            cls = "A lost money"
        elif agg["sharpe"] < ew["sharpe"]:
            cls = "B profitable, but below the passive equal-weight benchmark"
        else:
            cls = "C profitable and above EW Sharpe, but failed a requirement"
        rows.append(dict(c, name=NAMES[c["hypothesis"]], n_books=len(books), **agg, **cost,
                         approx_gross_cagr=agg["cagr"] + cost["commission_drag_pa"] + cost["slippage_drag_pa"],
                         official_outcome=official, category=cls))
    rows.sort(key=lambda r: (r["cycle"], r["candidate"]))
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(f'{r["candidate"]} {r["hypothesis"]} {r["version"]}')
    cnt = registry.counts()
    runtime_h = sum(float(r["runtime_s"] or 0) for r in registry.read() if r["run_type"] != "annotation") / 3600
    out = dict(
        note="IS 2010-2017 only; derived results; official verdicts unchanged; H012 not evaluated (D087)",
        benchmarks=dict(ew_is=ew, spy_is=spy,
                        no_skill_random_100k_15slots_hold60=[{k: n[k] for k in ("sharpe", "cagr", "max_dd")} for n in null]),
        candidates=rows, categories=by_cat,
        summary=dict(n_candidates=len(rows), median_sharpe=float(np.median([r["sharpe"] for r in rows if "sharpe" in r])),
                     median_cagr=float(np.median([r["cagr"] for r in rows if "cagr" in r])),
                     beat_ew_sharpe=sum(1 for r in rows if r.get("sharpe", -9) >= ew["sharpe"]),
                     beat_ew_cagr=sum(1 for r in rows if r.get("cagr", -9) >= ew["cagr"]),
                     lost_money=sum(1 for r in rows if r.get("cagr", 1) <= 0)),
        registry=dict(runs=cnt["runs"], experiment_ids=cnt["experiments"], hypotheses=cnt["hypotheses"],
                      research_strategies=cnt["strategies"], by_kind=cnt["by_kind"], by_status=cnt["by_status"],
                      total_backtest_runtime_hours=runtime_h),
        c01_validation_published=json.loads((ROOT / "research/validation/E005-28_validation.json").read_text())["s005"])
    (ROOT / "research/cycles/programme_review.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    for r in rows:
        print(f'{r["cycle"]} {r["candidate"]} {r["hypothesis"]} {r["version"]:5} SR {r.get("sharpe", float("nan")):5.2f} '
              f'CAGR {r.get("cagr", float("nan")):6.3f} DD {r.get("max_dd", float("nan")):6.3f} '
              f'costs {r.get("commission_drag_pa", 0) + r.get("slippage_drag_pa", 0):5.3f} turn {r.get("turnover_pa", 0):5.1f} '
              f'expo {r.get("exposure_mean", 0):4.2f} | {r.get("category", "")[:2]} | {r.get("official_outcome", r.get("status"))}')
    print(json.dumps(dict(summary=out["summary"], benchmarks=out["benchmarks"], registry=out["registry"]), indent=1, default=float))


if __name__ == "__main__":
    main()
