"""P7-CP4 (D175): the frozen predictive-test specification, the score / mechanics / null / power code and the tests it
names are hash-pinned, and the code carries exactly the pinned constants; c_IC is pinned from the committed null before the one real run (D179)."""
import qr_p7_mech as M
import qr_p7_pred as R
from qresearch import p7pred, p7score


def test_spec_and_code_hashes():
    assert p7pred.sha256(p7pred.SPEC) == p7pred.SPEC_SHA256
    for rel, h in p7pred.CODE_SHA256.items():
        assert p7pred.sha256(rel) == h, rel
    for rel, h in p7score.CODE_SHA256.items():              # Score v1 unchanged
        assert p7pred.CODE_SHA256[rel] == h


def test_constants_pinned():
    for k, v in p7pred.CONSTANTS.items():
        assert getattr(R, k) == v, k
    assert R.SEEDS == p7pred.NULL_SEEDS
    assert M.SECTOR_MAX == 3 and M.REGIME_POSITIONS == p7pred.MECHANICS["REGIME_POSITIONS"]
    assert (M.INITIAL_POSITION_CAP, M.GROWN_WINNER_CAP) == (0.10, 0.20)


def test_d177_wording_only_correction():
    # D177: the only change to spec v1 is the C3 wording; the original hash is kept for the record
    assert p7pred.SPEC_SHA256_V1_ORIGINAL == "389f9364541588f78f504843bdce32067dc3004a26a64eab5c91331b5ffc2bd9"
    from qresearch import config
    assert "maximises independent observations" not in (config.REPO_ROOT / p7pred.SPEC).read_text()


def test_null_threshold_pinned_before_the_real_run():
    """P7-CP5 (D179): c_IC = max(50th largest of the 5,000 committed null t_IC, 2.326), pinned with the null result hash
    and the prepared-panel digest BEFORE the one real evaluation E023-06."""
    import gzip
    import json

    from qresearch import config
    root = config.REPO_ROOT
    assert p7pred.sha256(p7pred.NULL_RESULT) == p7pred.NULL_RESULT_SHA256
    null = json.loads((root / p7pred.NULL_RESULT).read_text())
    worlds = json.loads(gzip.open(root / p7pred.NULL_WORLDS).read())
    assert len(worlds) == 5000 and [w["seed"] for w in worlds] == list(p7pred.NULL_SEEDS)
    assert R.critical_value(worlds) == p7pred.C_IC == null["c_ic"]
    assert null["integrity"]["identical_panel_all_batches"] and null["integrity"]["panel_equals_canary"]
    assert null["runs"][0]["panel_sha256"] == p7pred.PANEL_SHA256


def test_execution_host_pinned():
    assert p7pred.sha256(p7pred.HOST) == p7pred.HOST_SHA256
    assert p7pred.sha256("strategies/X994_h022_canary/main.py") == p7pred.HOST_SHA256


def test_spec_states_the_frozen_rules():
    from qresearch import config
    s = (config.REPO_ROOT / p7pred.SPEC).read_text()
    for frag in ("**83 dates:**", "**next session's open**", "**last real close**", "Newey-West standard error with **lag 2**", "+3.0% a year**",
                 "**≥ 0.90**", "**both halves**", "identity-tethered within-date permutation", "R = **5,000**",
                 "**one-sided 1%**", "**80 / 70 / 5**", "**STRONG 10, NORMAL 8, WEAK 5, RISK_OFF 2**",
                 "**3** holdings per PIT FF12", "**20%** of equity", "CIK Option A",
                 "maximises the number of non-overlapping monthly response periods"):
        assert frag in s, frag


def test_real_config_carries_exactly_the_pinned_provenance():
    import json
    import subprocess

    from qresearch import config, experiment
    cfg = json.loads((config.REPO_ROOT / "experiments/E023-07/config.json").read_text())
    experiment.validate(cfg)
    # D180: E023-07 = E023-06 (never started) with the identical configuration
    c6 = json.loads((config.REPO_ROOT / "experiments/E023-06/config.json").read_text())
    assert {k: v for k, v in c6.items() if k not in ("experiment_id", "description")} == \
        {k: v for k, v in cfg.items() if k not in ("experiment_id", "description")}
    p = cfg["params"]
    assert (p["mode"], p["c_ic"], p["threshold_commit"], p["null_result_sha256"], p["panel_sha256"]) == \
        ("real", p7pred.C_IC, p7pred.THRESHOLD_COMMIT, p7pred.NULL_RESULT_SHA256, p7pred.PANEL_SHA256)
    # the threshold commit already carried c_IC and the null hash (pinned before the real run)
    old = subprocess.run(["git", "show", f"{p7pred.THRESHOLD_COMMIT}:src/qresearch/p7pred.py"], capture_output=True,
                         text=True, cwd=config.REPO_ROOT)
    if old.returncode == 0:                         # shallow clones may lack the commit
        assert f"C_IC = {p7pred.C_IC!r}" in old.stdout and p7pred.NULL_RESULT_SHA256 in old.stdout
