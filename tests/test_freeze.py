"""D042: validation is out-of-sample exactly once; promoted strategies are frozen."""
import pytest

from qresearch import freeze

FILES = {"main.py": "logic v1", "signals.py": "def f(): pass"}
HARNESS = "harness"
PF = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 5000, "max_positions": 15}


def cfg(**kw):
    c = dict(experiment_id="E001-05", kind="research", strategy_id="S001", strategy_version="v1.0",
             split="VAL", params={"lookback": 20}, universe={"min_market_cap": 2e9}, costs={"slippage_bps": 10},
             portfolio=PF)
    c.update(kw)
    return c


def rec(c=None):
    return freeze.make_record(c or cfg(split="IS"), FILES, HARNESS, "E001-03", {"is_screen": "pass"}, "t")


def test_is_runs_need_no_record():
    freeze.check(cfg(split="IS"), None, FILES, HARNESS, [])


def test_val_without_promotion_refused():
    with pytest.raises(freeze.FreezeError, match="no promotion record"):
        freeze.check(cfg(), None, FILES, HARNESS, [])


def test_val_with_matching_record_allowed():
    freeze.check(cfg(), rec(), FILES, HARNESS, [])


@pytest.mark.parametrize("change", [
    dict(files={"main.py": "logic v2", "signals.py": "def f(): pass"}),
    dict(harness="harness v2"),
    dict(cfg=dict(params={"lookback": 25})),
    dict(cfg=dict(portfolio=dict(PF, max_positions=10))),
    dict(cfg=dict(costs={"slippage_bps": 5})),
])
def test_any_change_after_promotion_refused(change):
    c = cfg(**change.get("cfg", {}))
    with pytest.raises(freeze.FreezeError):
        freeze.check(c, rec(), change.get("files", FILES), change.get("harness", HARNESS), [])


def test_second_val_run_in_same_lineage_refused():
    rows = [dict(experiment_id="E001-05", split="VAL", run_type="original", kind="research", strategy_id="S001")]
    with pytest.raises(freeze.FreezeError, match="already has a VAL run"):
        freeze.check(cfg(experiment_id="E001-06"), rec(), FILES, HARNESS, rows)
    # a "new" strategy derived from S001 is the same lineage
    c = cfg(strategy_id="S002", experiment_id="E002-04", derived_from=["S001"])
    r = freeze.make_record(dict(c, split="IS"), FILES, HARNESS, "E002-02", {}, "t")
    with pytest.raises(freeze.FreezeError):
        freeze.check(c, r, FILES, HARNESS, rows)


def test_unrelated_strategy_may_use_val():
    rows = [dict(experiment_id="E001-05", split="VAL", run_type="original", kind="research", strategy_id="S001")]
    c = cfg(strategy_id="S003", experiment_id="E003-04")
    freeze.check(c, freeze.make_record(dict(c, split="IS"), FILES, HARNESS, "E003-02", {}, "t"), FILES, HARNESS, rows)


def test_runner_calls_the_freeze_check(root):
    src = (root / "src/qresearch/run.py").read_text()
    assert "_check_freeze(cfg, commit, files)" in src and "if not scratch and not reproduce:" in src
