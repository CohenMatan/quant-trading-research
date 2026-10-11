"""H026 pins (owner D206): the frozen spec and code hash exactly as pinned in qresearch.p11h026; Data v2.1 is the
pinned manifest; the run plan and gates restate the D206 parameters; configs refuse unpinned runs."""
import json

import pytest

from qresearch import config, datafreeze_v21, experiment, p11h026 as P
import qr_h026 as H


def test_spec_and_code_hashes():
    assert P.file_sha256(P.SPEC) == P.SPEC_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if P.file_sha256(f) != h]
    assert not changed, f"pinned H026 code changed: {changed}"
    assert P.DATA_V21_MANIFEST_SHA256 == datafreeze_v21.MANIFEST_SHA256 == datafreeze_v21.manifest_sha()


def test_d206_parameters():
    assert H.LAMBDAS == (0.01, 0.1, 1.0, 10.0, 100.0) and H.HORIZON == 63 and H.K == 15 and H.SECTOR_CAP == 3
    assert tuple(H.OUTER_YEARS) == tuple(range(2015, 2022)) and H.R_NULL == 5000 and H.ALPHA == 0.01
    assert (H.COMMISSION, H.SLIPPAGE, H.STRESS_SLIPPAGE, H.CAPITAL) == (7.0, 0.001, 0.002, 100000)
    assert len(H.FEATURES) == 11
    assert P.NULL_BATCHES == ((1, 2500), (2501, 5000)) and P.RERUN_SEEDS == (1, 25)


def test_canary_config_validates_and_real_is_refused_until_pinned():
    cfg = json.loads((config.EXPERIMENTS_DIR / P.CANARY / "config.json").read_text())
    experiment.validate(cfg)
    if P.C_WEALTH is None:
        bad = dict(cfg, kind="research", split="DEV", experiment_id=P.REAL,
                   params=dict(cfg["params"], mode="real"))
        with pytest.raises(experiment.ConfigError):
            experiment.validate(bad)
