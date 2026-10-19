"""SYS-1 pins (owner D252): protocol, engine, host and offline-rule hashes exactly as pinned; the frozen H026 / H027 /
H028 pins unchanged; the frozen references equal the committed E030-05 result; the run parameters are the E030-05
real-mode parameters plus the SYS-1 pins; the canary config validates and the evaluation is refused until the canary
digest is pinned."""
import hashlib
import json
import sys

import pytest

from qresearch import config, experiment, p11h026, p12h027, p13h028, sys1 as P


def test_protocol_and_code_hashes():
    assert P.PROTOCOL_SHA256 is not None and P.file_sha256(P.PROTOCOL) == P.PROTOCOL_SHA256
    changed = [f for f, h in P.CODE_SHA256.items() if h is None or P.file_sha256(f) != h]
    assert not changed, f"pinned SYS-1 files changed: {changed}"
    for mod in (p11h026, p12h027, p13h028):              # the frozen chain under the SYS-1 host is untouched
        assert all(mod.file_sha256(f) == h for f, h in mod.CODE_SHA256.items())
    assert P.PARENT_HOST == p13h028.HOST


def test_frozen_references_equal_the_committed_h028_result():
    r = json.loads((config.REPO_ROOT / P.FROZEN_RESULT).read_text())
    po = r["portfolio"]
    assert P.FROZEN_H028 == dict(wealth=po["h028"]["wealth"], commissions=po["trades"]["commissions"],
                                 buys=po["trades"]["buys"], sells=po["trades"]["sells"],
                                 slippage=po["trades"]["slippage"])
    assert P.FROZEN_SPY_WEALTH == po["spy"]["wealth"] and P.FROZEN_LV15_WEALTH == po["lv15"]["wealth"]
    assert P.FROZEN_SPY_WEALTH_200K == r["diagnostics"]["capital_200k"]["spy"]
    assert r["status"].startswith("H028 REJECTED")
    assert p13h028.C_WEALTH_H028 == 0.056125732120069 and p13h028.CANDIDATE is None             # H028 untouched


def test_engine_constants_match_the_protocol():
    import qr_sys1 as Y
    import qr_h026 as H
    assert (Y.CAPITAL, Y.SLEEVE, Y.MIN_TICKET, Y.MAX_INIT_W) == (P.CAPITAL, P.SLEEVE, P.MIN_TICKET, 0.10)
    assert (Y.ETF_MIN_TRADE, Y.BETA_WIN, Y.BETA_MIN_OBS, Y.BLUME) == (1000.0, 252, 189, (0.67, 0.33))
    assert Y.SLIPS == (0.001, 0.002) and (H.K, H.SECTOR_CAP, H.COMMISSION) == (15, 3, 7.0)
    text = (config.REPO_ROOT / P.PROTOCOL).read_text()
    for s in ("$200,000", "0.5 × E / 15", "$5,000", "$1,000", "189", "0.67 β + 0.33", "E032-03", "E032-04",
              "NOT FALSIFIED — DEVELOPMENT-CONSISTENT", "max_y LR_y ≤ 0.50 × Σ LR"):
        assert s in text, s


def test_run_params_are_the_e030_05_params_plus_sys1_pins():
    base = json.loads((config.REPO_ROOT / "experiments" / p13h028.REAL / "config.json").read_text())["params"]
    for mode in ("canary", "eval"):
        p = P.run_params(mode)
        assert {k: p[k] for k in base} == base and p["mode"] == "real" and p["sys1_mode"] == mode
        assert p["sys1_protocol_sha256"] == P.PROTOCOL_SHA256 and p["sys1_code_sha256"] == P.CODE_SHA256[P.ENGINE]
    assert "canary_result_sha256" not in P.run_params("canary")


def _cfg_module():
    sys.path.insert(0, str(config.REPO_ROOT / "research/longhorizon/sys1"))
    import SYS1_configs as C
    return C


def test_canary_config_validates_and_evaluation_refused_until_pinned():
    C = _cfg_module()
    path = config.EXPERIMENTS_DIR / P.CANARY / "config.json"
    assert path.exists()
    cfg = json.loads(path.read_text())
    experiment.validate(cfg)
    assert cfg == C.build("canary", P.CANARY)
    assert cfg["strategy_id"] == "S032" and cfg["kind"] == "infrastructure" and cfg["split"] == "AUDIT"
    assert cfg["owner_approval_required"] and "D252" in cfg["owner_approval_required"]
    with pytest.raises(experiment.ConfigError):
        experiment.validate(dict(cfg, experiment_id="E032-05"))
    with pytest.raises(experiment.ConfigError):
        experiment.validate(dict(cfg, params=dict(cfg["params"], sys1_mode="null")))
    with pytest.raises(experiment.ConfigError):
        experiment.validate(dict(cfg, params=dict(cfg["params"], c_wealth_h028=0.0)))
    if P.CANARY_RESULT_SHA256 is None:
        with pytest.raises(experiment.ConfigError):
            C.build("eval", P.EVAL)
    else:
        c = config.REPO_ROOT / P.CANARY_RESULT
        assert hashlib.sha256(c.read_bytes()).hexdigest() == P.CANARY_RESULT_SHA256
        assert json.loads(c.read_text())["all_pass"] is True
        ev = C.build("eval", P.EVAL)
        assert ev["kind"] == "research" and ev["split"] == "DEV" and ev["programme"] == "LH"
        e = config.EXPERIMENTS_DIR / P.EVAL / "config.json"
        if e.exists():
            assert json.loads(e.read_text()) == ev


def test_holdout_sealed_and_window():
    cfg = json.loads((config.EXPERIMENTS_DIR / P.CANARY / "config.json").read_text())
    assert cfg["end"] == "2021-12-31" and cfg["start"] == "2011-01-03"
    assert not (config.REPO_ROOT / "HOLDOUT_UNLOCK.md").exists() or "SYS-1" not in (
        config.REPO_ROOT / "HOLDOUT_UNLOCK.md").read_text()
