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
    """D069 inputs for the Deflated Sharpe Ratio, frozen before any C02 result.
    n_trials = cumulative distinct selection candidates (registry.dsr_trial_count "official");
    var_sr   = variance of the per-day Sharpe across the latest valid (not retired) run of every
               selection candidate counted in n_trials;
    n_conservative = selection + robustness + validation configurations, reported separately."""
    acc = registry.trial_accounting(retired=set(retired_ids()))
    sharpe = {r["experiment_id"]: r["sharpe"] for r in registry.read() if r["run_type"] == "original"}
    srs = [float(sharpe[e]) / math.sqrt(252) for e in acc["selection_latest"].values() if e and sharpe.get(e)]
    return dict(n_trials=acc["selection_trials"],
                n_conservative=acc["selection_trials"] + acc["robustness_runs"] + acc["validation_runs"],
                var_sr=float(np.var(srs, ddof=1)) if len(srs) > 1 else 0.0, n_sharpes=len(srs))


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


def summarise(cycle: str, bench_id: str = "E901-05", spy_id: str = "E900-06") -> dict:
    _, _, beq, _, _ = _load(bench_id)
    _, _, seq, _, _ = _load(spy_id)
    rows, rets, checks_all = [], {}, {}
    d = dsr_inputs()   # D069: official N = cumulative selection candidates; conservative N reported beside it
    n_trials, n_cons, var_sr = d["n_trials"], d["n_conservative"], d["var_sr"]
    final = cycle_experiments(cycle)
    for eid in final:
        cfg, res, eq, tr, fi = _load(eid)
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
    pbo = {}
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
    return dict(table=table, checks=checks_all, pbo=pbo, bench=bench, n_trials=n_trials,
                n_trials_conservative=n_cons, counts=registry.counts(), var_sr=var_sr)


def main(argv=None) -> int:
    cycle = (argv or sys.argv[1:] or ["C01"])[0]
    s = summarise(cycle)
    out = config.REPO_ROOT / "research" / "cycles"
    s["table"].to_csv(out / f"{cycle}_is_results.csv", index=False)
    (out / f"{cycle}_is_gates.json").write_text(json.dumps(s["checks"], indent=1, default=str))
    (out / f"{cycle}_pbo.json").write_text(json.dumps(s["pbo"], indent=1))
    print(s["table"].to_string(index=False))
    print(json.dumps(dict(pbo=s["pbo"], bench=s["bench"], n_trials=s["n_trials"], counts=s["counts"]), indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
