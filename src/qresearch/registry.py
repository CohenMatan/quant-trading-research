"""experiments/INDEX.csv — append-only registry of every run, including failed and bugged ones.

Rows are never edited or deleted. A later finding about a run (e.g. "bugged") is recorded by
appending an annotation row (run_type = "annotation") that references the same experiment_id.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

from . import config

COLUMNS = [
    "experiment_id", "run_type", "kind", "hypothesis_id", "strategy_id", "strategy_version", "split",
    "start", "end", "git_commit", "qc_project_id", "qc_backtest_id", "lean_version", "run_utc",
    "runtime_s", "status", "n_trades", "cagr", "sharpe", "max_drawdown", "equity_sha256",
    "fills_sha256", "trades_sha256", "config_sha256", "notes",
]


class RegistryError(RuntimeError):
    pass


def _path(path: Path | None) -> Path:
    return path or config.INDEX_CSV


def ensure(path: Path | None = None) -> None:
    p = _path(path)
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(",".join(COLUMNS) + "\n", encoding="utf-8")


def read(path: Path | None = None) -> list[dict]:
    p = _path(path)
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            raise RegistryError(f"{p} header does not match the registry schema")
        return list(reader)


def append(row: dict, path: Path | None = None) -> None:
    """Append one row. The existing file content is verified to be an unmodified prefix."""
    p = _path(path)
    ensure(p)
    unknown = set(row) - set(COLUMNS)
    if unknown:
        raise RegistryError(f"unknown registry columns: {sorted(unknown)}")
    if not str(row.get("experiment_id", "")).strip():
        raise RegistryError("experiment_id is required")
    before = p.read_bytes()
    if not before.endswith(b"\n"):
        raise RegistryError(f"{p} does not end with a newline; refusing to append")
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow([_fmt(row.get(c, "")) for c in COLUMNS])
    with open(p, "ab") as fh:
        fh.write(buf.getvalue().encode("utf-8"))
    after = p.read_bytes()
    if not after.startswith(before):
        raise RegistryError("registry prefix changed during append")


def _fmt(v) -> str:
    if isinstance(v, float):
        return "" if v != v else f"{v:.6g}"
    return "" if v is None else str(v)


def counts(path: Path | None = None) -> dict:
    """Totals for reports: distinct hypotheses, strategies and experiments by kind and status."""
    rows = [r for r in read(path) if r["run_type"] != "annotation"]
    out = {
        "runs": len(rows),
        "experiments": len({r["experiment_id"] for r in rows}),
        "hypotheses": len({r["hypothesis_id"] for r in rows if r["hypothesis_id"]}),
        "strategies": len({r["strategy_id"] for r in rows if r["kind"] == "research"}),
        "by_kind": {},
        "by_status": {},
    }
    for r in rows:
        out["by_kind"][r["kind"]] = out["by_kind"].get(r["kind"], 0) + 1
        out["by_status"][r["status"]] = out["by_status"].get(r["status"], 0) + 1
    return out


NOT_STARTED = "not_started"


def not_started_ids(path: Path | None = None) -> set[str]:
    """Runs annotated as operational failures in which no backtest ever ran (e.g. "no spare nodes",
    compile rejected): no strategy result existed, so they are not trials (owner, 2026-09-29)."""
    return {r["experiment_id"] for r in read(path) if r["run_type"] == "annotation" and r["status"] == NOT_STARTED}


def trial_count(path: Path | None = None) -> int:
    """Number of trials for the Deflated Sharpe Ratio: every original run of a research or demo
    strategy, whatever its outcome (failed runs count: they were attempts), except runs annotated
    `not_started`, in which no backtest ran and no strategy result was produced."""
    rows = read(path)
    skip = {r["experiment_id"] for r in rows if r["run_type"] == "annotation" and r["status"] == NOT_STARTED}
    return sum(1 for r in rows
               if r["run_type"] == "original" and r["kind"] in ("research", "demo") and r["experiment_id"] not in skip)


SELECTION, ROBUSTNESS, VALIDATION = "selection", "robustness", "validation"


def trial_category(cfg: dict) -> str:
    """D069 category of a research configuration (frozen 2026-09-29, before any C02 result).
    selection  = an IS candidate at base costs that could be chosen (a pre-declared variation);
    robustness = cost-stress or plateau run of an already-chosen variation (never selects);
    validation = any out-of-sample evaluation of a frozen candidate."""
    if cfg.get("robustness_of") or cfg.get("costs", {}).get("slippage_stress_multiple", 1) != 1:
        return ROBUSTNESS
    if cfg["split"] != "IS":
        return VALIDATION
    return SELECTION


REPLICATE = "replicate"


def _trial_key(cfg: dict, drop_param: str | None = None) -> str:
    """Configuration identity (D066/D069): hypothesis, strategy, version, parameters, split, dates and
    cost-stress multiple. `drop_param` removes one parameter (the replicate seed, D082)."""
    import json as _json
    params = {k: v for k, v in cfg["params"].items() if k != drop_param}
    return _json.dumps([cfg.get("hypothesis_id"), cfg["strategy_id"], cfg["strategy_version"], params,
                        cfg["split"], cfg["start"], cfg["end"],
                        cfg["costs"].get("slippage_stress_multiple", 1)], sort_keys=True)


def trial_accounting(path: Path | None = None, experiments_dir: Path | None = None,
                     retired: set[str] | None = None) -> dict:
    """D066: separate genuine strategy trials from technical repeats. A genuine trial is a distinct
    research configuration — (hypothesis, strategy, version, parameters, split, dates, cost-stress
    multiple) — whose backtest started. Further runs of an identical configuration (re-runs after
    infrastructure fixes, operational retries, remedial re-tests) are technical. Infrastructure,
    benchmark, sizing, stress and demo runs (verification, canaries, probes, controls, nulls, capital
    sensitivity) are never trials. Recovery and annotation rows are not runs.

    D069 splits the genuine configurations by `trial_category`. D082 (C03, frozen 2026-09-30): a
    SELECTION configuration whose config names `replicate_param` (H013: "seed") is grouped with the
    other values of that parameter: the first started one is the selection candidate; every further
    distinct value is a REPLICATE (in the conservative count only). Robustness and Validation
    configurations are never grouped: each seed counts separately there.

    `selection_latest` maps each selection candidate to its latest started run not in `retired` (None
    if every run is); `selection_members` maps it to that run for itself and for each replicate."""
    import json as _json
    exp_dir = experiments_dir or config.EXPERIMENTS_DIR
    retired = retired or set()
    rows = read(path)
    skip = {r["experiment_id"] for r in rows if r["run_type"] == "annotation" and r["status"] == NOT_STARTED}
    seen: dict[str, str] = {}          # full key -> first experiment id (genuine or replicate)
    group_head: dict[str, str] = {}    # replicate-group key -> the selection candidate's experiment id
    genuine, technical, not_started, verification = [], [], [], []
    category: dict[str, str] = {}
    head_of: dict[str, str] = {}       # replicate id -> candidate id
    latest: dict[str, str | None] = {}
    for r in rows:
        if r["run_type"] != "original":
            continue
        if r["kind"] != "research":
            verification.append(r["experiment_id"])
            continue
        if r["experiment_id"] in skip:
            not_started.append(r["experiment_id"])
            continue
        cfg = _json.loads((exp_dir / r["experiment_id"] / "config.json").read_text())
        key = _trial_key(cfg)
        if key in seen:
            technical.append((r["experiment_id"], seen[key]))
        else:
            seen[key] = r["experiment_id"]
            genuine.append(r["experiment_id"])
            cat = trial_category(cfg)
            rp = cfg.get("replicate_param")
            if cat == SELECTION and rp:
                if rp not in cfg["params"]:
                    raise RegistryError(f"{r['experiment_id']}: replicate_param {rp!r} is not a parameter")
                gkey = _trial_key(cfg, drop_param=rp)
                if gkey in group_head:
                    cat = REPLICATE
                    head_of[r["experiment_id"]] = group_head[gkey]
                else:
                    group_head[gkey] = r["experiment_id"]
            category[r["experiment_id"]] = cat
            latest[seen[key]] = None
        if r["experiment_id"] not in retired:
            latest[seen[key]] = r["experiment_id"]
    by_cat = {c: [e for e in genuine if category[e] == c] for c in (SELECTION, REPLICATE, ROBUSTNESS, VALIDATION)}
    members = {e: [latest[e]] for e in by_cat[SELECTION]}
    for rep in by_cat[REPLICATE]:
        members[head_of[rep]].append(latest[rep])
    return dict(genuine_trials=len(genuine), technical_repeats=len(technical), not_started=len(not_started),
                verification_and_benchmark_runs=len(verification), all_started_research_runs=len(genuine) + len(technical),
                selection_trials=len(by_cat[SELECTION]), replicate_runs=len(by_cat[REPLICATE]),
                robustness_runs=len(by_cat[ROBUSTNESS]), validation_runs=len(by_cat[VALIDATION]),
                genuine=genuine, technical=technical, by_category=by_cat,
                selection_latest={e: latest[e] for e in by_cat[SELECTION]},
                selection_members=members, replicate_of=head_of)


def dsr_trial_count(path: Path | None = None, experiments_dir: Path | None = None) -> dict:
    """D069 (owner clarification 1, 2026-09-29), extended by D082 (C03, frozen 2026-09-30).
    official     = N for the Deflated Sharpe Ratio: cumulative distinct selection candidates
                   (all cycles). DSR corrects for picking the best of the candidates that were
                   compared; only selection candidates are compared (an H013 variation is one
                   candidate whatever its number of seeds).
    conservative = selection + replicate + robustness + validation configurations (D082: a
                   second DSR requirement for C03, frozen in research/cycles/C03_statistical_spec.md).
    Technical repeats, not-started runs, recovery rows and verification/canary/benchmark/control/
    null/sizing/stress runs are in neither."""
    a = trial_accounting(path, experiments_dir)
    return dict(official=a["selection_trials"],
                conservative=a["selection_trials"] + a["replicate_runs"] + a["robustness_runs"] + a["validation_runs"])
