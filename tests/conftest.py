import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


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
