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
from .qc_client import BacktestHandle, QCClient, QCError
from .trades import build_trades



def _uses_sec(cfg: dict) -> bool:
    return bool(cfg.get("universe", {}).get("sec_corrections"))


def assemble_files(cfg: dict, commit: str | None, unlocked: bool) -> dict[str, str]:
    """Project files for QC: the strategy's .py files, the shared harness, generated params."""
    sdir = cfg["strategy_dir"].rstrip("/")
    files: dict[str, str] = {}
    if commit:
        paths = [p for p in gitutil.list_files(commit, sdir) if p.endswith(".py")]
        for p in paths:
            files[Path(p).name] = gitutil.show_file(commit, p)
        files["qr_harness.py"] = gitutil.show_file(commit, "src/qresearch/lean/qr_harness.py")
        try:   # shared pure indicators (C02); absent in commits before it existed
            files["qr_indicators.py"] = gitutil.show_file(commit, "src/qresearch/lean/qr_indicators.py")
        except Exception:
            pass
        try:   # point-in-time fundamentals layer (D108); absent in commits before it existed
            files["qr_fundamentals.py"] = gitutil.show_file(commit, "src/qresearch/lean/qr_fundamentals.py")
        except Exception:
            pass
        for extra in ("qr_sec_corrections.py", "qr_industry.py"):
            try:   # D111/D113 SEC layer logic; absent in commits before it existed
                files[extra] = gitutil.show_file(commit, f"src/qresearch/lean/{extra}")
            except Exception:
                pass
        if _uses_sec(cfg):   # the packed SEC correction table, only for opt-in configs
            data = [p for p in gitutil.list_files(commit, "src/qresearch/lean")
                    if Path(p).name.startswith("qr_sec_data") and p.endswith(".py")]
            if not data:
                raise experiment.ConfigError("universe.sec_corrections needs the packed table src/qresearch/lean/qr_sec_data*.py")
            for p in data:
                files[Path(p).name] = gitutil.show_file(commit, p)
    else:
        for p in sorted((config.REPO_ROOT / sdir).glob("*.py")):
            files[p.name] = p.read_text(encoding="utf-8")
        files["qr_harness.py"] = config.LEAN_HARNESS.read_text(encoding="utf-8")
        for extra in ("qr_indicators.py", "qr_fundamentals.py", "qr_sec_corrections.py", "qr_industry.py"):
            ind = config.LEAN_HARNESS.parent / extra
            if ind.exists():
                files[extra] = ind.read_text(encoding="utf-8")
        if _uses_sec(cfg):
            for p in sorted(config.LEAN_HARNESS.parent.glob("qr_sec_data*.py")):
                files[p.name] = p.read_text(encoding="utf-8")
    if "main.py" not in files:
        raise experiment.ConfigError(f"{sdir} has no main.py")
    if "qr_h016" in files["main.py"]:   # D116: H016 decision logic, only for strategies that import it (S016, X980)
        src = "src/qresearch/lean/qr_h016.py"
        files["qr_h016.py"] = gitutil.show_file(commit, src) if commit else (config.REPO_ROOT / src).read_text(
            encoding="utf-8")
    if "qr_h017" in files["main.py"]:   # H017 decision logic + packed event table v1, only for strategies importing it
        lean = "src/qresearch/lean"
        if commit:
            names = [p for p in gitutil.list_files(commit, lean) if Path(p).name.startswith("qr_h017") and p.endswith(".py")]
            for p in names:
                files[Path(p).name] = gitutil.show_file(commit, p)
        else:
            for p in sorted((config.REPO_ROOT / lean).glob("qr_h017*.py")):
                files[p.name] = p.read_text(encoding="utf-8")
        if "qr_h017.py" not in files or "qr_h017_events.py" not in files:
            raise experiment.ConfigError("S017 needs src/qresearch/lean/qr_h017.py and the packed event table qr_h017_events*.py")
    if "qr_p3" in files["main.py"]:   # Phase 3 engine modules (+ fidelity replay schedule), only for strategies importing them
        lean = "src/qresearch/lean"
        if commit:
            for p in gitutil.list_files(commit, lean):
                if Path(p).name.startswith("qr_p3") and p.endswith(".py"):
                    files[Path(p).name] = gitutil.show_file(commit, p)
        else:
            for p in sorted((config.REPO_ROOT / lean).glob("qr_p3*.py")):
                files[p.name] = p.read_text(encoding="utf-8")
        missing = {"qr_p3_engine.py", "qr_p3_features.py", "qr_p3_grammar.py", "qr_p3_pipeline.py"} - set(files)
        if missing:
            raise experiment.ConfigError(f"Phase 3 engine modules missing: {sorted(missing)}")
    if "qr_xs" in files["main.py"]:   # H019 cross-sectional modules (qr_xs, qr_xs_diag, qr_xs_panel), only when imported
        lean = "src/qresearch/lean"
        if commit:
            for p in gitutil.list_files(commit, lean):
                if Path(p).name.startswith("qr_xs") and p.endswith(".py"):
                    files[Path(p).name] = gitutil.show_file(commit, p)
        else:
            for p in sorted((config.REPO_ROOT / lean).glob("qr_xs*.py")):
                files[p.name] = p.read_text(encoding="utf-8")
        missing = {"qr_xs.py", "qr_xs_diag.py", "qr_xs_panel.py"} - set(files)
        if missing:
            raise experiment.ConfigError(f"H019 modules missing: {sorted(missing)}")
    if "qr_chart" in files["main.py"] or "qr_h020" in files["main.py"]:
        # H020 chart score + validation modules (frozen, hash-pinned in qresearch.p5h020); the renderer is never
        # uploaded (no chart image of QuantConnect data is ever made)
        names = ("qr_chart.py", "qr_h020_stats.py", "qr_h020_panel.py", "qr_h020_diag.py")
        for n in names:
            rel = f"src/qresearch/lean/{n}"
            files[n] = gitutil.show_file(commit, rel) if commit else (config.REPO_ROOT / rel).read_text(encoding="utf-8")
        if "qr_xs.py" not in files:
            raise experiment.ConfigError("H020 modules need qr_xs.py (imported by qr_h020_stats)")
    if "qr_p7" in files["main.py"]:
        # Phase 7 data / fidelity audit helpers (P7-CP1, D165)
        rel = "src/qresearch/lean/qr_p7.py"
        files["qr_p7.py"] = gitutil.show_file(commit, rel) if commit else (config.REPO_ROOT / rel).read_text(encoding="utf-8")
        # P7-CP3 (D171): the frozen score v1 (hash-pinned in qresearch.p7score) and its export helpers
        for n in ("qr_p7_score.py", "qr_p7_export.py", "qr_p7_pred.py"):
            if n[:-3] in files["main.py"]:
                rel = f"src/qresearch/lean/{n}"
                files[n] = gitutil.show_file(commit, rel) if commit else (config.REPO_ROOT / rel).read_text(encoding="utf-8")
        if "qr_p7_export.py" in files and "qr_p7_score.py" not in files:
            raise experiment.ConfigError("qr_p7_export needs qr_p7_score.py")
        if "qr_p7_pred.py" in files:      # P7-CP5 (D177): H022's frozen module imports the H020 tether and qr_xs
            rel = "src/qresearch/lean/qr_h020_stats.py"
            files["qr_h020_stats.py"] = gitutil.show_file(commit, rel) if commit else \
                (config.REPO_ROOT / rel).read_text(encoding="utf-8")
            if "qr_xs.py" not in files:
                raise experiment.ConfigError("qr_p7_pred needs qr_xs.py")
    if "qr_h021" in files["main.py"]:
        # H021-A sector relative-momentum module (frozen, hash-pinned in qresearch.p6h021); the panel helpers come
        # from qr_xs_panel (uploaded above with the qr_xs modules)
        rel = "src/qresearch/lean/qr_h021.py"
        files["qr_h021.py"] = gitutil.show_file(commit, rel) if commit else (config.REPO_ROOT / rel).read_text(encoding="utf-8")
        if "qr_xs_panel.py" not in files:
            raise experiment.ConfigError("H021-A needs qr_xs_panel.py")
    files["qr_params.py"] = experiment.lean_params(cfg, unlocked)
    return files


def code_hash(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name in sorted(files):
        h.update(name.encode() + b"\0" + files[name].encode() + b"\0")
    return h.hexdigest()


def execute(cfg: dict, files: dict[str, str], client: QCClient, state: dict | None = None) -> dict:
    """Upload, compile, backtest, download. Returns raw payloads plus timings.

    `state` is filled in as the run progresses (project, backtest id, stage), so a run that fails
    part-way still records which QuantConnect backtest it was (E003-06 incident)."""
    state = {} if state is None else state
    state["stage"] = "upload"
    project = client.find_or_create_project(f"qr-{cfg['strategy_id']}")
    state["project_id"] = project
    client.sync_files(project, files)
    if cfg.get("params", {}).get("pred_code_sha256"):           # D178: pinned modules checked on the stored copy
        verify_stored_modules(cfg, client.read_file_contents(project))
    if cfg.get("lean_version_policy") != DEFAULT_BUILD_POLICY:
        client.pin_lean_version(project, cfg["lean_version_id"])
    state["stage"] = "compile"
    compile_id = client.compile(project)
    state["stage"] = "start_backtest"
    t0 = time.time()
    name = f"{cfg['experiment_id']} {datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    try:
        handle = client.start_backtest(project, compile_id, name)
    except QCError as exc:          # E003-03: QC transiently rejected a fresh compile id; recompile once
        if "Compile id not found" not in str(exc):
            raise
        compile_id = client.compile(project)
        handle = client.start_backtest(project, compile_id, name)
    state.update(backtest_id=handle.backtest_id, backtest_name=name, stage="backtest",
                 backtest_started_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    # long end-of-run computations (H020: the chart score of every stock-week) keep the backtest's progress still;
    # such configs declare their own stall allowance
    stall = cfg.get("stall_minutes")
    bt = client.wait_backtest(handle, stall_s=float(stall) * 60) if stall else client.wait_backtest(handle)
    runtime = time.time() - t0
    state.update(stage="download_results", runtime_s=runtime)
    return download(cfg, client, handle, bt, runtime)


def download(cfg: dict, client: QCClient, handle, bt: dict, runtime: float) -> dict:
    """Everything after the backtest has completed: statistics, orders (verified complete), logs
    or summary statistics, and charts. Shared by normal runs and by --recover (D077)."""
    project = handle.project_id
    out = dict(project_id=project, backtest_id=handle.backtest_id, backtest=bt, runtime_s=runtime,
               lean_version=client.lean_version(bt))
    if cfg.get("lean_version_policy") == DEFAULT_BUILD_POLICY:
        # D182: QuantConnect runs its default build below the Trading Firm tier; the build actually used is recorded
        # (provenance lean_version) and the run's integrity rests on its prepared-input digest, not on the pin
        pass
    elif not out["lean_version"].endswith(f".{cfg['lean_version_id']}"):
        out["error"] = f"backtest ran on LEAN {out['lean_version']}, expected build {cfg['lean_version_id']}"
        out["logs"] = []
        return out
    if bt.get("error") or bt.get("stacktrace") or not bt.get("completed"):
        out["error"] = (bt.get("error") or "") + "\n" + (bt.get("stacktrace") or "")
        out["logs"] = []            # the error and stack trace come from backtests/read, not logs
        return out
    stats_ = client.read_statistics(handle, must_have="qr_summary")
    out["backtest"]["statistics"] = stats_
    # QuantConnect's own order count makes the orders download verifiably complete (E901-02 incident).
    out["expected_orders"] = qc_total_orders(stats_)
    out["orders"] = client.read_orders(handle, expected=out["expected_orders"])
    if "qr_summary" in stats_:
        out["logs"] = results.lines_from_statistics(stats_)      # D046: no QuantConnect logs needed
        out["result_channel"] = "summary_statistics"
    else:                            # harness older than D046 (reproductions of old runs only)
        out["logs"] = client.read_logs(handle, must_contain="QRSUMMARY|")
        out["result_channel"] = "logs (legacy harness)"
    s = datetime.fromisoformat(cfg["start"]).replace(tzinfo=timezone.utc)
    e = datetime.fromisoformat(cfg["end"]).replace(tzinfo=timezone.utc)
    _, summary, _ = results.parse_logs(out["logs"])
    out["chart"] = client.read_chart(handle, "QR", int(s.timestamp()) - 86400, int(e.timestamp()) + 3 * 86400,
                                     min_points=int(summary.get("days") or 1))
    out["extra_charts"] = {name: client.read_chart(handle, name, int(s.timestamp()) - 86400,
                                                   int(e.timestamp()) + 3 * 86400)
                           for name in cfg.get("extra_charts", [])}
    return out


def qc_total_orders(stats_: dict) -> int | None:
    """QuantConnect's "Total Orders" summary statistic as an int (None if absent)."""
    v = str(stats_.get("Total Orders", "")).replace(",", "").strip()
    return int(v) if v.isdigit() else None


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
    fills, _ = results.apply_forced_fees(fills, qr_lines)          # D049: mirror harness fee debits
    fills, _ = results.apply_stale_exits(fills, qr_lines)          # D059: mirror fallback exits
    trades = build_trades(fills, splits)
    checks = integrity.check_all(equity, fills, summary, cfg["start"], cfg["end"],
                                 commission_per_order=cfg["costs"].get("commission_per_order"),
                                 tradeable_dates=integrity.official_tradeable_dates(
                                     raw["backtest"].get("tradeableDates"), summary),
                                 expected_orders=raw.get("expected_orders"),
                                 downloaded_orders=len({o.get("id") for o in raw["orders"]}),
                                 late_open_orders=results.late_open_orders(raw["orders"], cfg["end"]),
                                 initial_cash=cfg.get("cash"))
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


def recover(exp_id: str, backtest_id: str, notes: str = "") -> dict:
    """D077: an official run whose local runner was lost (e.g. a container restart) while its
    QuantConnect backtest went on to complete. Downloads that SAME backtest through the normal
    download/verify/analyse path. The failed original record is kept untouched; the recovered result
    goes to experiments/<id>/recovery/<utc>/ with a registry row of run_type "recovery".
    Refused unless: the original row failed, its result.json names this backtest, the backtest
    completed on the pinned LEAN build, and the strategy/harness files built from the original
    commit are byte-identical to those at the current (clean) commit."""
    run_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    head = gitutil.require_clean_tree()
    exp_dir = config.EXPERIMENTS_DIR / exp_id
    orig = json.loads((exp_dir / "result.json").read_text())
    rows = [r for r in registry.read() if r["experiment_id"] == exp_id and r["run_type"] == "original"]
    # D077; H020 E021-01: also an original that failed integrity because the runner downloaded the results while
    # QuantConnect still reported "In Progress..." (completed = True before the end-of-run computation finished)
    bad = ("failed", "integrity_failed")
    if not rows or rows[-1]["status"] not in bad or orig.get("status") not in bad:
        raise SystemExit(f"{exp_id}: recovery only applies to a failed original run")
    if orig["provenance"].get("qc_backtest_id") != backtest_id:
        raise SystemExit(f"{exp_id}: backtest {backtest_id} is not the one recorded for this run")
    build_commit = orig["provenance"]["git_commit"]
    cfg_text = gitutil.show_file(build_commit, f"experiments/{exp_id}/config.json")
    cfg = experiment.parse(cfg_text)
    files = assemble_files(cfg, build_commit, holdout.holdout_unlocked())
    if code_hash(files) != code_hash(assemble_files(cfg, head, holdout.holdout_unlocked())):
        raise SystemExit(f"{exp_id}: code changed between {build_commit[:8]} and HEAD; cannot attribute the backtest")
    client = QCClient()
    handle = BacktestHandle(int(orig["provenance"]["qc_project_id"]), backtest_id, "")
    bt = client.read_backtest(handle)
    if (not bt.get("completed") or "in progress" in str(bt.get("status", "")).lower() or bt.get("error")
            or bt.get("stacktrace")):
        raise SystemExit(f"{exp_id}: backtest {backtest_id} did not complete cleanly on QuantConnect")
    prov = dict(git_commit=build_commit, run_utc=orig["provenance"].get("run_utc", ""), recovered_utc=run_utc,
                recovered_at_commit=head, config_sha256=results.sha256_text(cfg_text), code_sha256=code_hash(files),
                files=sorted(files), holdout_unlocked=holdout.holdout_unlocked(), build_commit=build_commit,
                datasets=["QC US Equities (AlgoSeek) daily", "QC US Equity Security Master",
                          "Morningstar US Fundamentals (QC)"])
    if orig["provenance"].get("owner_approved"):
        prov["owner_approved"] = orig["provenance"]["owner_approved"]
    try:
        raw = download(cfg, client, handle, bt, 0.0)
    except Exception as exc:
        raw = dict(project_id=handle.project_id, backtest_id=backtest_id, runtime_s=0.0, logs=[],
                   error=f"{type(exc).__name__}: {exc} [stage: recovery download]")
    prov.update(result_channel=raw.get("result_channel", ""), qc_project_id=raw.get("project_id", ""),
                qc_backtest_id=backtest_id, lean_version=raw.get("lean_version", ""), runtime_s=0.0,
                failure_stage="" if "error" not in raw else "recovery")
    an = None
    if "error" not in raw:
        try:
            an = analyse(cfg, raw)
        except Exception:
            raw["error"] = "analysis failed:\n" + traceback.format_exc()
    outdir = exp_dir / "recovery" / run_utc.replace(":", "")
    result = write_outputs(outdir, cfg, prov, raw, an)
    registry.append(registry_row(cfg, prov, result, "recovery",
                                 ((notes + " ") if notes else "") + f"recovered QC backtest {backtest_id} (D077)"))
    from .report import write_report
    write_report(outdir, cfg, result)
    return result


DEFAULT_BUILD_POLICY = "default_build_digest_verified"     # D182 (H022 family only; see experiment.validate)


def verify_stored_modules(cfg: dict, stored: dict[str, str]) -> None:
    """P7-CP5 (D178): configs that pin a module fingerprint (params.pred_code_sha256 = qr_p7_pred.py) are checked on the
    copy QuantConnect stores for the project, read back after the upload and before compiling (LEAN's runtime copy of a
    source file is not byte-identical to the stored one, so the check cannot live in the algorithm)."""
    want = cfg.get("params", {}).get("pred_code_sha256")
    if want is None:
        return
    got = hashlib.sha256(stored.get("qr_p7_pred.py", "").encode()).hexdigest()
    if got != want:
        raise experiment.ConfigError(f"{cfg['experiment_id']}: QuantConnect's stored qr_p7_pred.py ({got[:12]}...) "
                                     f"differs from the pinned module ({want[:12]}...); nothing compiled")


def approval_gate(cfg: dict, owner_approved: str | None) -> None:
    """Configs written ahead of an owner decision carry owner_approval_required (H017, 2026-10-03: E017-01 consumes
    Phase 2 slot 3). They run only with --owner-approved <decision id> naming the written approval."""
    if cfg.get("owner_approval_required") and not (owner_approved or "").strip():
        raise SystemExit(f"{cfg['experiment_id']} needs explicit owner approval before it may run "
                         f"({cfg['owner_approval_required']}); pass --owner-approved <decision id>")


def run(exp_id: str | None, reproduce: bool = False, dry_run: bool = False, scratch: str | None = None,
        notes: str = "", owner_approved: str | None = None) -> dict:
    run_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if exp_id and exp_id in experiment.withdrawn():      # D087: refused before anything else happens
        raise SystemExit(f"{exp_id} is withdrawn and may never run: {experiment.withdrawn()[exp_id]}")
    if scratch:
        cfg_text = Path(scratch).read_text(encoding="utf-8")
        cfg = experiment.parse(cfg_text)
        approval_gate(cfg, owner_approved)
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
        approval_gate(cfg, owner_approved)
        prior = [r for r in registry.read() if r["experiment_id"] == exp_id and r["run_type"] == "original"]
        if prior and not reproduce:
            raise SystemExit(f"{exp_id} already has an original run; use --reproduce or a new ID.")
        if not reproduce and cfg.get("split_scheme", "cp1") != config.CURRENT_SCHEME:
            raise SystemExit(f"{exp_id} uses split scheme {cfg.get('split_scheme', 'cp1')}; new runs must use "
                             f"{config.CURRENT_SCHEME} (D034). Old configs are history (reproduce only).")
        if (not reproduce and cfg["kind"] in ("research", "sizing", "stress")
                and cfg.get("execution_model", "d044") != config.CURRENT_EXECUTION_MODEL):
            raise SystemExit(f"{exp_id}: new research runs must use execution_model "
                             f"{config.CURRENT_EXECUTION_MODEL} (D051); older configs are history.")
        if reproduce and not prior:
            raise SystemExit(f"{exp_id} has no original run to reproduce.")
    if not cfg.get("lean_version_id"):
        raise SystemExit("config needs lean_version_id: every run is pinned to an explicit LEAN build (D021)")
    unlocked = holdout.holdout_unlocked()
    build_commit = commit
    if reproduce:
        orig = json.loads((config.EXPERIMENTS_DIR / cfg["experiment_id"] / "result.json").read_text())
        build_commit = orig["provenance"]["git_commit"]
        if "+uncommitted" in build_commit:
            raise SystemExit("cannot reproduce an uncommitted run")
    files = assemble_files(cfg, build_commit, unlocked)
    if not scratch and not reproduce:
        _check_freeze(cfg, commit, files)
    prov = dict(git_commit=head if commit else f"{head}+uncommitted", run_utc=run_utc,
                config_sha256=results.sha256_text(cfg_text), code_sha256=code_hash(files),
                files=sorted(files), holdout_unlocked=unlocked,
                datasets=["QC US Equities (AlgoSeek) daily", "QC US Equity Security Master",
                          "Morningstar US Fundamentals (QC)"])
    if owner_approved:
        prov["owner_approved"] = owner_approved
    if dry_run:
        print(json.dumps(prov, indent=1))
        return prov

    client = QCClient()
    busy = client.running_backtests()
    if busy:   # precondition, like the clean-tree check: nothing is started, nothing is registered
        raise SystemExit(f"backtest node busy ({busy}); {cfg['experiment_id']} not started")
    state: dict = {}
    try:
        raw = execute(cfg, files, client, state)
    except Exception as exc:  # the run still gets registered as failed, with how far it got
        raw = dict(project_id=state.get("project_id", ""), backtest_id=state.get("backtest_id", ""),
                   runtime_s=state.get("runtime_s", 0.0), logs=[],
                   error=f"{type(exc).__name__}: {exc} [stage: {state.get('stage', 'setup')}]")
    prov["failure_stage"] = state.get("stage", "") if "error" in raw else ""
    prov["backtest_started_utc"] = state.get("backtest_started_utc", "")
    prov["result_channel"] = raw.get("result_channel", "")
    prov["build_commit"] = build_commit if not scratch else prov["git_commit"]
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


def _check_freeze(cfg: dict, commit: str, files: dict[str, str]) -> None:
    """D042: VAL/WF/HOLDOUT research runs must match their promotion record exactly."""
    from . import freeze
    rec = None
    try:
        rec = json.loads(gitutil.show_file(commit, freeze.record_path(cfg["strategy_id"], cfg["strategy_version"])))
    except Exception:
        rec = None
    strategy_files = {k: v for k, v in files.items() if k not in ("qr_harness.py", "qr_params.py")}
    rows = registry.read()
    lineages = {}
    for r in rows:
        if r["split"] == "VAL" and r["kind"] == "research":
            try:
                c = json.loads(gitutil.show_file(commit, f"experiments/{r['experiment_id']}/config.json"))
                lineages[r["experiment_id"]] = freeze.lineage(c)
            except Exception:
                lineages[r["experiment_id"]] = {r["strategy_id"]}
    try:
        freeze.check(cfg, rec, strategy_files, files["qr_harness.py"], rows, lineages)
    except freeze.FreezeError as exc:
        raise SystemExit(f"Refused (D042): {exc}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m qresearch.run")
    ap.add_argument("experiment_id", nargs="?")
    ap.add_argument("--reproduce", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--scratch", metavar="CONFIG_JSON")
    ap.add_argument("--notes", default="")
    ap.add_argument("--recover", metavar="QC_BACKTEST_ID")
    ap.add_argument("--owner-approved", metavar="DECISION_ID", default=None)
    a = ap.parse_args(argv)
    if not a.scratch and not a.experiment_id:
        ap.error("experiment_id or --scratch is required")
    if a.recover:
        res = recover(a.experiment_id, a.recover, notes=a.notes)
    else:
        res = run(a.experiment_id, reproduce=a.reproduce, dry_run=a.dry_run, scratch=a.scratch, notes=a.notes,
                  owner_approved=a.owner_approved)
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
