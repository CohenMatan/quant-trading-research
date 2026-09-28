"""Validation discipline (D042): promotion records freeze a strategy before it sees VAL.

A promotion record research/promotions/S###_vX.Y.json holds the SHA-256 of the strategy's .py
files and of the harness, plus the exact params/universe/costs/portfolio. The runner refuses a
VAL, WF or HOLDOUT research run unless the committed files and settings match the record, and
allows at most one VAL run per strategy lineage (the strategy plus everything it derives from).
"""
from __future__ import annotations

import hashlib
import json

FROZEN_KEYS = ("params", "universe", "costs", "portfolio")
GATED_SPLITS = ("VAL", "WF", "HOLDOUT")


class FreezeError(RuntimeError):
    pass


def files_hash(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name in sorted(files):
        h.update(name.encode() + b"\0" + files[name].encode() + b"\0")
    return h.hexdigest()


def record_path(strategy_id: str, version: str) -> str:
    return f"research/promotions/{strategy_id}_{version}.json"


def make_record(cfg: dict, strategy_files: dict[str, str], harness: str, is_experiment: str,
                gates: dict, promoted_utc: str) -> dict:
    return dict(strategy_id=cfg["strategy_id"], strategy_version=cfg["strategy_version"],
                hypothesis_id=cfg.get("hypothesis_id"), derived_from=list(cfg.get("derived_from") or []),
                is_experiment=is_experiment, strategy_files_sha256=files_hash(strategy_files),
                harness_sha256=hashlib.sha256(harness.encode()).hexdigest(),
                frozen={k: cfg[k] for k in FROZEN_KEYS}, gates=gates, promoted_utc=promoted_utc)


def lineage(cfg: dict) -> set[str]:
    return {cfg["strategy_id"], *[str(x) for x in (cfg.get("derived_from") or [])]}


def check(cfg: dict, record: dict | None, strategy_files: dict[str, str], harness: str,
          registry_rows: list[dict], registry_lineages: dict[str, set[str]] | None = None) -> None:
    """Raise FreezeError unless this research run may use cfg['split']."""
    if cfg["kind"] != "research" or cfg["split"] not in GATED_SPLITS:
        return
    if record is None:
        raise FreezeError(f"{cfg['strategy_id']} {cfg['strategy_version']} has no promotion record; "
                          f"{cfg['split']} runs need promotion from IS first (D042)")
    if record["strategy_id"] != cfg["strategy_id"] or record["strategy_version"] != cfg["strategy_version"]:
        raise FreezeError("promotion record is for a different strategy/version")
    if files_hash(strategy_files) != record["strategy_files_sha256"]:
        raise FreezeError("strategy files changed since promotion: frozen logic may not change (D042)")
    if hashlib.sha256(harness.encode()).hexdigest() != record["harness_sha256"]:
        raise FreezeError("harness changed since promotion; re-promotion needs a documented owner-visible reason")
    for k in FROZEN_KEYS:
        if json.dumps(cfg[k], sort_keys=True) != json.dumps(record["frozen"][k], sort_keys=True):
            raise FreezeError(f"'{k}' differs from the promoted (frozen) values (D042)")
    if cfg["split"] == "VAL":
        mine = lineage(cfg)
        for r in registry_rows:
            if r["split"] != "VAL" or r["run_type"] != "original" or r["kind"] != "research":
                continue
            theirs = (registry_lineages or {}).get(r["experiment_id"], {r["strategy_id"]})
            if mine & theirs:
                raise FreezeError(f"lineage {sorted(mine)} already has a VAL run ({r['experiment_id']}); "
                                  "VAL is out-of-sample only once (D042)")
