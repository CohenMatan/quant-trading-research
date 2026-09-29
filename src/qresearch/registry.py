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
