"""Run one registered experiment on QuantConnect Cloud.

    python -m qresearch.run E000-01              official run (clean committed tree required)
    python -m qresearch.run E000-01 --reproduce  re-run a recorded experiment, compare result hashes
    python -m qresearch.run E000-01 --dry-run    validate and assemble project files only
    python -m qresearch.run --scratch cfg.json   development run of infrastructure code (never
                                                 research), uncommitted, not registered

Every official run — including failed ones — is appended to experiments/INDEX.csv.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import config, experiment, gitutil, holdout, integrity, metrics, registry, results, stats
from .qc_client import QCClient
from .trades import build_trades

MIN_LOG_ALLOWANCE = 300_000   # bytes of QC daily log allowance required before starting a run


def assemble_files(cfg: dict, commit: str | None, unlocked: bool) -> dict[str, str]:
    """Project files for QC: the strategy's .py files, the shared harness, generated params."""
    sdir = cfg["strategy_dir"].rstrip("/")
    files: dict[str, str] = {}
    if commit:
        paths = [p for p in gitutil.list_files(commit, sdir) if p.endswith(".py")]
        for p in paths:
            files[Path(p).name] = gitutil.show_file(commit, p)
        files["qr_harness.py"] = gitutil.show_file(commit, "src/qresearch/lean/qr_harness.py")
    else:
        for p in sorted((config.REPO_ROOT / sdir).glob("*.py")):
            files[p.name] = p.read_text(encoding="utf-8")
        files["qr_harness.py"] = config.LEAN_HARNESS.read_text(encoding="utf-8")
    if "main.py" not in files:
        raise experiment.ConfigError(f"{sdir} has no main.py")
    files["qr_params.py"] = experiment.lean_params(cfg, unlocked)
    return files


def code_hash(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name in sorted(files):
        h.update(name.encode() + b"\0" + files[name].encode() + b"\0")
    return h.hexdigest()


def execute(cfg: dict, files: dict[str, str], client: QCClient) -> dict:
    """Upload, compile, backtest, download. Returns raw payloads plus timings."""
    project = client.find_or_create_project(f"qr-{cfg['strategy_id']}")
    client.sync_files(project, files)
    client.pin_lean_version(project, cfg["lean_version_id"])
    compile_id = client.compile(project)
    t0 = time.time()
    handle = client.start_backtest(project, compile_id, f"{cfg['experiment_id']} {datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    bt = client.wait_backtest(handle)
    runtime = time.time() - t0
    out = dict(project_id=project, backtest_id=handle.backtest_id, backtest=bt, runtime_s=runtime,
               lean_version=client.lean_version(bt))
    if not out["lean_version"].endswith(f".{cfg['lean_version_id']}"):
        out["error"] = f"backtest ran on LEAN {out['lean_version']}, expected build {cfg['lean_version_id']}"
        out["logs"] = []
        return out
    if bt.get("error") or bt.get("stacktrace") or not bt.get("completed"):
        out["error"] = (bt.get("error") or "") + "\n" + (bt.get("stacktrace") or "")
        out["logs"] = client.read_logs(handle)
        return out
    out["orders"] = client.read_orders(handle)
    out["logs"] = client.read_logs(handle, must_contain="QRSUMMARY|")
    s = datetime.fromisoformat(cfg["start"]).replace(tzinfo=timezone.utc)
    e = datetime.fromisoformat(cfg["end"]).replace(tzinfo=timezone.utc)
    _, summary, _ = results.parse_logs(out["logs"])
    out["chart"] = client.read_chart(handle, "QR", int(s.timestamp()) - 86400, int(e.timestamp()) + 3 * 86400,
                                     min_points=int(summary.get("days") or 1))
    out["extra_charts"] = {name: client.read_chart(handle, name, int(s.timestamp()) - 86400,
                                                   int(e.timestamp()) + 3 * 86400)
                           for name in cfg.get("extra_charts", [])}
    return out


def load_benchmarks(cfg: dict) -> dict[str, pd.Series]:
    out = {}
    for eid in cfg.get("benchmarks", []):
        p = config.EXPERIMENTS_DIR / eid / "equity.csv.gz"
        if p.exists():
            df = results.read_csv_gz(p)
            out[eid] = pd.Series(df["equity"].to_numpy(float), index=df["date"].astype(str))
    return out


def analyse(cfg: dict, raw: dict) -> dict:
    """Parse payloads, run integrity checks, compute metrics. Returns tables, texts and a result dict."""
    equity = results.parse_equity(raw["chart"])
    fills = results.parse_fills(raw["orders"])
    splits, summary, qr_lines = results.parse_logs(raw["logs"])
    trades = build_trades(fills, splits)
    checks = integrity.check_all(equity, fills, summary, cfg["start"], cfg["end"],
                                 commission_per_order=cfg["costs"].get("commission_per_order"))
    texts = {
        "equity": results.canonical_csv(equity),
        "fills": results.canonical_csv(fills),
        "trades": results.canonical_csv(trades),
    }
    benches = load_benchmarks(cfg)
    if len(equity) < 3:   # e.g. the QR chart was not delivered; integrity checks already fail
        return dict(equity=equity, fills=fills, trades=trades, splits=splits, texts=texts,
                    summary=summary, qr_lines=qr_lines, checks=checks,
                    status=integrity.status_from(checks), metrics={}, relative={}, segments={},
                    trade_distribution={})
    m_all = metrics.compute_metrics(equity, trades, fills)
    rel = {}
    eq_s = pd.Series(equity["equity"].to_numpy(float), index=equity["date"].astype(str))
    r = metrics.returns_from_equity(eq_s)
    for eid, b in benches.items():
        rel[eid] = metrics.benchmark_relative(r, metrics.returns_from_equity(b), eq_s, b)
    segments = {}
    if cfg["split"] == "FULL":
        for lab in ("IS", "VAL"):
            a, z = config.SPLITS[lab]
            sl = metrics.slice_equity(equity, a.isoformat(), z.isoformat())
            if len(sl) > 2:
                segments[lab] = metrics.compute_metrics(sl)
    closed = trades[trades["status"] == "closed"]
    tstats = {}
    if len(closed):
        tstats = stats.profit_concentration(closed["pnl"])
        tstats["expectancy_ci95"] = stats.bootstrap_mean_ci(closed["ret"].to_numpy(float))
        tstats["expectancy_without_best10"] = stats.expectancy_without_best(closed["ret"], 10)
    tstats["psr_0"] = stats.probabilistic_sharpe(r.to_numpy())
    return dict(equity=equity, fills=fills, trades=trades, splits=splits, texts=texts,
                summary=summary, qr_lines=qr_lines, checks=checks,
                status=integrity.status_from(checks), metrics=m_all, relative=rel,
                segments=segments, trade_distribution=tstats)


def write_outputs(outdir: Path, cfg: dict, prov: dict, raw: dict, an: dict | None) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    result = dict(experiment_id=cfg["experiment_id"], provenance=prov)
    if an is None:
        result.update(status="failed", error=raw.get("error", "unknown"),
                      log_tail=[ln for ln in raw.get("logs", [])][-40:])
    else:
        hashes = {f"{k}_sha256": results.sha256_text(v) for k, v in an["texts"].items()}
        for k, v in an["texts"].items():
            results.write_gz(outdir / f"{k}.csv.gz", v)
        for name, series in (raw.get("extra_charts") or {}).items():
            (outdir / f"chart_{name}.csv").write_text(results.canonical_csv(results.chart_table(series)))
        (outdir / "messages.txt").write_text("\n".join(an["qr_lines"]) + "\n")
        result.update(status=an["status"], hashes=hashes, metrics=an["metrics"],
                      segments=an["segments"], relative=an["relative"],
                      trade_distribution=an["trade_distribution"], harness_summary=an["summary"],
                      integrity=an["checks"], harness_messages=an["qr_lines"][:100],
                      qc_statistics=raw["backtest"].get("statistics"))
    (outdir / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True, default=_json_default) + "\n")
    return result


def _json_default(o):
    if isinstance(o, float) and o != o:
        return None
    if hasattr(o, "item"):
        return o.item()
    return str(o)


def registry_row(cfg: dict, prov: dict, result: dict, run_type: str, notes: str = "") -> dict:
    m = result.get("metrics", {})
    h = result.get("hashes", {})
    return dict(
        experiment_id=cfg["experiment_id"], run_type=run_type, kind=cfg["kind"],
        hypothesis_id=cfg.get("hypothesis_id") or "", strategy_id=cfg["strategy_id"],
        strategy_version=cfg["strategy_version"], split=cfg["split"], start=cfg["start"], end=cfg["end"],
        git_commit=prov["git_commit"], qc_project_id=prov.get("qc_project_id", ""),
        qc_backtest_id=prov.get("qc_backtest_id", ""), lean_version=prov.get("lean_version", ""),
        run_utc=prov["run_utc"], runtime_s=round(prov.get("runtime_s", 0.0), 1), status=result["status"],
        n_trades=m.get("n_trades", ""), cagr=m.get("cagr", ""), sharpe=m.get("sharpe", ""),
        max_drawdown=m.get("max_drawdown", ""), equity_sha256=h.get("equity_sha256", ""),
        fills_sha256=h.get("fills_sha256", ""), trades_sha256=h.get("trades_sha256", ""),
        config_sha256=prov["config_sha256"], notes=notes,
    )


def run(exp_id: str | None, reproduce: bool = False, dry_run: bool = False, scratch: str | None = None,
        notes: str = "") -> dict:
    run_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if scratch:
        cfg_text = Path(scratch).read_text(encoding="utf-8")
        cfg = experiment.parse(cfg_text)
        if cfg["kind"] == "research":
            raise SystemExit("Scratch runs are not allowed for research experiments.")
        commit = None
        head = gitutil.head_commit()
    else:
        commit = gitutil.require_clean_tree()
        head = commit
        cfg_text = gitutil.show_file(commit, f"experiments/{exp_id}/config.json")
        cfg = experiment.parse(cfg_text)
        if cfg["experiment_id"] != exp_id:
            raise SystemExit(f"config experiment_id {cfg['experiment_id']} != {exp_id}")
        prior = [r for r in registry.read() if r["experiment_id"] == exp_id and r["run_type"] == "original"]
        if prior and not reproduce:
            raise SystemExit(f"{exp_id} already has an original run; use --reproduce or a new ID.")
        if not reproduce and cfg.get("split_scheme", "cp1") != config.CURRENT_SCHEME:
            raise SystemExit(f"{exp_id} uses split scheme {cfg.get('split_scheme', 'cp1')}; new runs must use "
                             f"{config.CURRENT_SCHEME} (D034). Old configs are history (reproduce only).")
        if reproduce and not prior:
            raise SystemExit(f"{exp_id} has no original run to reproduce.")
    if not cfg.get("lean_version_id"):
        raise SystemExit("config needs lean_version_id: every run is pinned to an explicit LEAN build (D021)")
    unlocked = holdout.holdout_unlocked()
    files = assemble_files(cfg, commit, unlocked)
    prov = dict(git_commit=head if commit else f"{head}+uncommitted", run_utc=run_utc,
                config_sha256=results.sha256_text(cfg_text), code_sha256=code_hash(files),
                files=sorted(files), holdout_unlocked=unlocked,
                datasets=["QC US Equities (AlgoSeek) daily", "QC US Equity Security Master",
                          "Morningstar US Fundamentals (QC)"])
    if dry_run:
        print(json.dumps(prov, indent=1))
        return prov

    client = QCClient()
    remaining = int((client.organization().get("logs") or {}).get("dailyRemaining", 0))
    if remaining < MIN_LOG_ALLOWANCE:
        raise SystemExit(f"QuantConnect daily log allowance too low ({remaining} bytes < {MIN_LOG_ALLOWANCE}); "
                         "not starting, so the run is not lost (see E953-03). Try again later.")
    try:
        raw = execute(cfg, files, client)
    except Exception as exc:  # the run still gets registered as failed
        raw = dict(error=f"{type(exc).__name__}: {exc}", logs=[])
    prov.update(qc_project_id=raw.get("project_id", ""), qc_backtest_id=raw.get("backtest_id", ""),
                lean_version=raw.get("lean_version", ""), runtime_s=raw.get("runtime_s", 0.0))
    an = None
    if "error" not in raw:
        try:
            an = analyse(cfg, raw)
        except Exception:
            raw["error"] = "analysis failed:\n" + traceback.format_exc()
    exp_dir = config.EXPERIMENTS_DIR / cfg["experiment_id"]
    if scratch:
        outdir = config.REPO_ROOT / "scratch" / f"{cfg['experiment_id']}_{run_utc.replace(':', '')}"
    elif reproduce:
        outdir = exp_dir / "reproductions" / run_utc.replace(":", "")
    else:
        outdir = exp_dir
    result = write_outputs(outdir, cfg, prov, raw, an)
    if reproduce and an is not None:
        orig = json.loads((exp_dir / "result.json").read_text())
        same = {k: orig.get("hashes", {}).get(k) == v for k, v in result["hashes"].items()}
        result["reproduction"] = dict(original_backtest=orig["provenance"].get("qc_backtest_id"),
                                      hashes_match=same, identical=all(same.values()))
        (outdir / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True, default=_json_default) + "\n")
        notes = (notes + " " if notes else "") + ("reproduced: identical" if all(same.values())
                                                  else f"reproduced: MISMATCH {same}")
    if not scratch:
        registry.append(registry_row(cfg, prov, result, "reproduce" if reproduce else "original", notes))
        from .report import write_report
        write_report(outdir, cfg, result)
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m qresearch.run")
    ap.add_argument("experiment_id", nargs="?")
    ap.add_argument("--reproduce", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--scratch", metavar="CONFIG_JSON")
    ap.add_argument("--notes", default="")
    a = ap.parse_args(argv)
    if not a.scratch and not a.experiment_id:
        ap.error("experiment_id or --scratch is required")
    res = run(a.experiment_id, reproduce=a.reproduce, dry_run=a.dry_run, scratch=a.scratch, notes=a.notes)
    if a.dry_run:
        return 0
    m = res.get("metrics", {})
    print(json.dumps(dict(status=res.get("status"), error=(res.get("error") or "")[:2000],
                          runtime_s=res["provenance"].get("runtime_s"),
                          backtest=res["provenance"].get("qc_backtest_id"),
                          lean=res["provenance"].get("lean_version"),
                          cagr=m.get("cagr"), sharpe=m.get("sharpe"), max_dd=m.get("max_drawdown"),
                          n_trades=m.get("n_trades"), hashes=res.get("hashes"),
                          reproduction=res.get("reproduction"),
                          failed_checks=[c for c in res.get("integrity", []) if not c["ok"]],
                          harness=res.get("harness_summary")), indent=1, default=_json_default))
    return 0 if res.get("status", "").startswith("completed") else 1


if __name__ == "__main__":
    sys.exit(main())
