import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# LEAN-side pure modules (qr_indicators) are imported by the harness and strategy signal files
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def root():
    return ROOT


def experiment_result(eid: str):
    p = ROOT / "experiments" / eid / "result.json"
    if not p.exists():
        pytest.skip(f"{eid} has not been run yet")
    return json.loads(p.read_text())


def latest_completed(strategy_id: str):
    """Result of the most recent completed original run of a strategy (skips if none yet)."""
    from qresearch import registry
    rows = [r for r in registry.read(ROOT / "experiments" / "INDEX.csv")
            if r["strategy_id"] == strategy_id and r["run_type"] == "original" and r["status"].startswith("completed")]
    if not rows:
        pytest.skip(f"no completed run of {strategy_id} yet")
    eid = rows[-1]["experiment_id"]
    return eid, json.loads((ROOT / "experiments" / eid / "result.json").read_text())
