import json
import re
from datetime import date

import pytest

from qresearch import config, experiment
from qresearch.holdout import HoldoutLockedError, check_dates


def test_dates_in_validation_pass(tmp_path):
    check_dates(date(2015, 1, 2), date(2021, 12, 31), unlock_file=tmp_path / "HOLDOUT_UNLOCK.md")


@pytest.mark.parametrize("end", [date(2022, 1, 1), date(2022, 1, 3), date(2026, 8, 31)])
def test_holdout_dates_rejected_while_locked(tmp_path, end):
    with pytest.raises(HoldoutLockedError):
        check_dates(date(2015, 1, 2), end, unlock_file=tmp_path / "HOLDOUT_UNLOCK.md")


def test_unlock_file_opens_the_lock(tmp_path):
    f = tmp_path / "HOLDOUT_UNLOCK.md"
    f.write_text("approved")
    check_dates(date(2022, 1, 3), date(2026, 8, 31), unlock_file=f)


def test_repo_holdout_is_locked():
    assert not config.HOLDOUT_UNLOCK_FILE.exists(), "HOLDOUT_UNLOCK.md must not exist before CP5 approval"


def test_config_split_boundaries():
    assert config.LAST_UNLOCKED_DATE == date(2021, 12, 31)
    assert config.SPLITS["HOLDOUT"] == (date(2022, 1, 1), date(2026, 8, 31))


def _cfg(**kw):
    c = dict(experiment_id="E950-99", kind="infrastructure", strategy_id="X950", strategy_version="v1.0",
             strategy_dir="strategies/X950_timing_canary", split="VAL", start="2015-01-02", end="2021-12-31",
             cash=100000, universe={"min_market_cap": 2e9}, costs={"slippage_bps": 10}, portfolio={}, params={},
        lean_version_id=18131)
    c.update(kw)
    return c


def test_experiment_config_cannot_reach_holdout(tmp_path):
    with pytest.raises(HoldoutLockedError):
        experiment.validate(_cfg(split="HOLDOUT", start="2022-01-03", end="2022-06-30"),
                            unlock_file=tmp_path / "none.md")


def test_lean_harness_enforces_same_lock(root):
    src = (root / "src/qresearch/lean/qr_harness.py").read_text()
    assert "LAST_UNLOCKED = datetime(2021, 12, 31)" in src
    assert re.search(r"if end > LAST_UNLOCKED and not e\.get\(\"holdout_unlocked\", False\):\s*\n\s*raise", src)


def test_generated_params_carry_lock_flag():
    ns = {}
    exec(experiment.lean_params(_cfg(), holdout_unlocked=False), ns)
    assert ns["EXPERIMENT"]["holdout_unlocked"] is False
    assert ns["EXPERIMENT"]["end"] == "2021-12-31"


def test_no_committed_config_touches_holdout(root):
    for p in (root / "experiments").glob("E*/config.json"):
        c = json.loads(p.read_text())
        assert c["end"] <= "2021-12-31", p
