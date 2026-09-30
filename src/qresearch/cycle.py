"""Research-cycle summary: gates, trial accounting, DSR and PBO for one cycle's IS experiments.

    python -m qresearch.cycle C01
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import config, gates, metrics, registry, results, stats


def _load(eid: str):
    d = config.EXPERIMENTS_DIR / eid
    cfg = json.loads((d / "config.json").read_text())
    if not (d / "result.json").exists():
        return cfg, dict(status="not run"), None, None, None
    r = json.loads((d / "result.json").read_text())
    if not r["status"].startswith("completed"):
        return cfg, r, None, None, None
    eq = results.read_csv_gz(d / "equity.csv.gz")
    tr = results.read_csv_gz(d / "trades.csv.gz")
    fi = results.read_csv_gz(d / "fills.csv.gz")
    return cfg, r, eq, tr, fi


RETIRED = ("superseded", "invalid", "bugged", "failed", "not_started")


def retired_ids() -> dict[str, str]:
    """Experiment id -> annotation status for runs retired by an annotation row (never deleted)."""
    return {r["experiment_id"]: r["status"] for r in registry.read()
            if r["run_type"] == "annotation" and r["status"] in RETIRED}


def dsr_inputs() -> dict:
    """D069 inputs for the Deflated Sharpe Ratio, frozen before any C02 result, extended by D082 (C03):
    n_trials = cumulative distinct selection candidates (registry.dsr_trial_count "official");
    var_sr   = variance of the per-day Sharpe across the latest valid (not retired) run of every
               selection candidate counted in n_trials (an H013 candidate: the mean over its seeds);
    n_conservative = selection + replicate + robustness + validation configurations."""
    from .c03stats import snapshot
    snap = snapshot(retired=set(retired_ids()))
    return dict(n_trials=snap["official"], n_conservative=snap["conservative"],
                var_sr=snap["var_sr"], n_sharpes=snap["n_sharpes"])


def cycle_experiments(cycle: str, final_only: bool = True) -> list[str]:
    """The cycle's research experiments. With final_only, only the comparable set: runs under the
    current execution model that no annotation has retired (superseded, invalid, bugged, failed)."""
    retired = retired_ids()
    out = []
    for p in sorted(config.EXPERIMENTS_DIR.glob("E*/config.json")):
        c = json.loads(p.read_text())
        if c.get("cycle") != cycle or c["kind"] != "research":
            continue
        if final_only and (c.get("execution_model", "d044") != config.CURRENT_EXECUTION_MODEL
                           or c["experiment_id"] in retired):
            continue
        out.append(c["experiment_id"])
    return out


PBO_GATE = 0.30   # D073: hard Validation gate on the CYCLE-level PBO (frozen before any C02 result)


def cycle_pbo(rets: dict, ids: list[str]) -> dict:
    """D073 (owner-approved 2026-09-29, frozen): the hard-gate PBO is computed across the cycle's
    full selection set (every pre-declared IS candidate at base costs), with the unchanged CSCV
    (16 blocks, at-or-below-median rule). `complete` is False if any candidate has no return
    series (then the gate cannot pass)."""
    have = [i for i in ids if i in rets]
    out = dict(candidates=list(ids), n_candidates=len(ids), n_with_returns=len(have),
               complete=len(have) == len(ids) and len(ids) >= 2, threshold=PBO_GATE)
    if len(have) >= 2:
        mat = pd.concat([rets[i] for i in have], axis=1, join="inner").dropna()
        out.update(stats.pbo_cscv(mat.to_numpy(), n_blocks=16), n_days=len(mat))
        out["gate_ok"] = bool(out["complete"] and out["pbo"] <= PBO_GATE)
    else:
        out["gate_ok"] = False
    return out


def summarise(cycle: str, bench_id: str | None = None, spy_id: str | None = None) -> dict:
    final = cycle_experiments(cycle)
    if bench_id is None or spy_id is None:   # the cycle's own benchmarks (config: [SPY, EW])
        b = json.loads((config.EXPERIMENTS_DIR / final[0] / "config.json").read_text()).get("benchmarks") \
            if final else None
        spy_id, bench_id = (b or ["E900-06", "E901-05"])[:2]
    _, _, beq, _, _ = _load(bench_id)
    _, _, seq, _, _ = _load(spy_id)
    rows, rets, checks_all = [], {}, {}
    d = dsr_inputs()   # D069: official N = cumulative selection candidates; conservative N reported beside it
    n_trials, n_cons, var_sr = d["n_trials"], d["n_conservative"], d["var_sr"]
    selection = []
    for eid in final:
        cfg, res, eq, tr, fi = _load(eid)
        if registry.trial_category(cfg) == registry.SELECTION:
            selection.append(eid)
        row = dict(experiment=eid, hypothesis=cfg["hypothesis_id"], strategy=cfg["strategy_id"],
                   version=cfg["strategy_version"], params=json.dumps(cfg["params"], sort_keys=True), status=res["status"])
        if eq is None:
            rows.append(row)
            continue
        a, z = eq["date"].iloc[0], eq["date"].iloc[-1]
        b = metrics.slice_equity(beq, a, z)
        m = metrics.compute_metrics(eq, tr, fi)
        chk = gates.is_screen(eq, tr, b)
        checks_all[eid] = chk
        e = pd.Series(eq["equity"].to_numpy(float), index=eq["date"])
        r_daily = metrics.returns_from_equity(e)
        rets[eid] = r_daily
        years = (pd.Timestamp(z) - pd.Timestamp(a)).days / 365.25
        fees = float(fi["fee"].sum())
        mb = metrics.compute_metrics(b)
        row.update(cagr=m["cagr"], sharpe=m["sharpe"], max_dd=m["max_drawdown"], ew_sharpe=mb["sharpe"],
                   ew_cagr=mb["cagr"], trades=m.get("n_trades"), win_rate=m.get("win_rate"),
                   expectancy=m.get("expectancy"), profit_factor=m.get("profit_factor"),
                   avg_hold_days=m.get("avg_holding_days"), exposure=m.get("exposure_mean"),
                   orders=int(fi["order_id"].nunique()), commissions=fees,
                   commission_drag_pa=fees / float(e.mean()) / years,
                   # 10 bps per side is already inside the fill prices; this is its estimated annual cost
                   slippage_drag_pa=float((fi["quantity"].abs() * fi["price"]).sum()) * cfg["costs"]["slippage_bps"] / 1e4
                   / float(e.mean()) / years,
                   turnover_pa=float((fi["quantity"].abs() * fi["price"]).sum()) / float(e.mean()) / years,
                   dsr=stats.deflated_sharpe(r_daily.to_numpy(), max(n_trials, 1), var_sr),
                   dsr_conservative=stats.deflated_sharpe(r_daily.to_numpy(), max(n_cons, 1), var_sr),
                   thirds=[round(x, 2) for x in gates.thirds_positive(eq)],
                   is_screen="PASS" if gates.passed(chk) else "fail",
                   failed_gates="; ".join(c["gate"] for c in chk if not c["ok"]))
        rows.append(row)
    table = pd.DataFrame(rows)
    pbo = {}   # per hypothesis (3 variations): DIAGNOSTIC only from C02 on (D073)
    for h, g in table.groupby("hypothesis"):
        ids = [i for i in g["experiment"] if i in rets]
        if len(ids) >= 2:
            mat = pd.concat([rets[i] for i in ids], axis=1, join="inner").dropna()
            pbo[h] = stats.pbo_cscv(mat.to_numpy(), n_blocks=16)
    bench = {}
    for name, df in ((f"EW >= $2B ({bench_id})", beq), (f"SPY ({spy_id})", seq)):
        sl = metrics.slice_equity(df, "2010-01-04", "2017-12-29")
        bm = metrics.compute_metrics(sl)
        bench[name] = dict(cagr=bm["cagr"], sharpe=bm["sharpe"], max_dd=bm["max_drawdown"])
    return dict(table=table, checks=checks_all, pbo=pbo, pbo_cycle=cycle_pbo(rets, selection),
                bench=bench, bench_ids=dict(ew=bench_id, spy=spy_id), n_trials=n_trials,
                n_trials_conservative=n_cons, counts=registry.counts(), var_sr=var_sr)


def main(argv=None) -> int:
    cycle = (argv or sys.argv[1:] or ["C01"])[0]
    s = summarise(cycle)
    out = config.REPO_ROOT / "research" / "cycles"
    s["table"].to_csv(out / f"{cycle}_is_results.csv", index=False)
    (out / f"{cycle}_is_gates.json").write_text(json.dumps(s["checks"], indent=1, default=str))
    (out / f"{cycle}_pbo.json").write_text(json.dumps(dict(per_hypothesis_diagnostic=s["pbo"],
                                                           cycle_gate=s["pbo_cycle"]), indent=1))
    print(s["table"].to_string(index=False))
    print(json.dumps(dict(pbo=s["pbo"], bench=s["bench"], n_trials=s["n_trials"], counts=s["counts"]), indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
