"""H006X (owner D304): the frozen spec, S006 code and evaluation rule match their pins; configs validate."""
import json

import pytest

from conftest import ROOT
from qresearch import experiment, h006x as H


def test_pins_match_files():
    assert H.file_sha256(H.SPEC) == H.SPEC_SHA256
    for path, sha in H.CODE_SHA256.items():
        assert H.file_sha256(path) == sha, path


@pytest.mark.parametrize("eid", [H.A, H.B, H.SPY])
def test_committed_configs_validate(eid):
    p = ROOT / "experiments" / eid / "config.json"
    if not p.exists():
        pytest.skip("config not written yet")
    cfg = json.loads(p.read_text())
    experiment.validate(cfg)
    assert cfg["params"] == H.run_params(eid)


def test_arms_differ_only_in_time_stop():
    a, b = H.run_params(H.A), H.run_params(H.B)
    assert a.pop("time_stop") == 60 and b.pop("time_stop") is None and a == b


def test_policy_refused_outside_h006x():
    import sys
    sys.path.insert(0, str(ROOT / "research" / "tt" / "h006_exit"))
    import H006X_configs as C
    cfg = C.build(H.B)
    for bad in (dict(experiment_id="E006-09"), dict(end="2020-12-31"), dict(params=dict(cfg["params"], k=2.5)),
                dict(universe=dict(cfg["universe"], sec_corrections=True)), dict(owner_approval_required="none")):
        with pytest.raises(experiment.ConfigError):
            experiment.validate(dict(cfg, **bad))
