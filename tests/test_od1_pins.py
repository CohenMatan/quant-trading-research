"""OD-1 (owner D308): pins of the frozen protocol, host, module, evaluation rule and SEC object; the run config; the
runner upload set; the compact statistics order shared by host and evaluation."""
import json
import sys

import pytest

from conftest import ROOT
from qresearch import experiment, od1 as P, run

sys.path.insert(0, str(ROOT / "research/od"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))


def test_pins_match_files():
    assert P.file_sha256(P.PROTOCOL) == P.PROTOCOL_SHA256
    for path, sha in P.CODE_SHA256.items():
        assert P.file_sha256(path) == sha, path
    assert json.loads((ROOT / P.OD1_MANIFEST).read_text())["sha256"] == P.OD1_REFERENCE_SHA256


def test_stat_keys_shared():
    import OD1_eval as EV
    import qr_od1 as O
    assert EV.STAT_KEYS == O.STAT_KEYS


def test_config_validates_and_refuses_changes():
    p = ROOT / "experiments" / P.RUN / "config.json"
    if not p.exists():
        pytest.skip("config not written yet")
    cfg = json.loads(p.read_text())
    experiment.validate(cfg)
    for bad in (dict(start="2009-06-01"), dict(experiment_id="E808-03"), dict(warmup_start="2009-07-01"),
                dict(params=dict(cfg["params"], od1_reference_sha256="0" * 64)), dict(kind="research")):
        with pytest.raises(experiment.ConfigError):
            experiment.validate(dict(cfg, **bad))


def test_upload_set():
    files = run.assemble_files(dict(strategy_dir="strategies/X808_od1_outcomes", experiment_id=P.RUN,
                                    start="2010-01-04", end="2021-12-31", cash=100000,
                                    universe=dict(min_market_cap=2e9), costs={}, portfolio={}, params={}),
                               None, False)
    assert {"main.py", "qr_od1.py", "qr_os1.py", "qr_ucr.py", "qr_harness.py"} <= set(files)
    assert len(files) <= 50
    bad = ("import zlib", "import lzma", "import base64", "b85decode")
    assert not any(b in files[f] for f in ("main.py", "qr_od1.py") for b in bad)
