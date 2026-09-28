import pytest

from qresearch import experiment
from test_holdout_lock import _cfg

FIXED = {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0}
PORTF = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 5000, "max_positions": 15,
         "buy_funding": "settled_cash_only", "gap_reserve": 0.15}


def research(**kw):
    c = dict(kind="research", strategy_id="S001", experiment_id="E001-01", hypothesis_id="H001",
             strategy_dir="strategies/S000_pipeline_demo", split_scheme="2010", split="IS",
             start="2010-01-04", end="2017-12-29", costs=FIXED, portfolio=PORTF, execution_model="d051")
    c.update(kw)
    return _cfg(**c)


def test_research_in_new_is_and_val_is_valid():
    experiment.validate(research())
    experiment.validate(research(split="VAL", start="2018-01-02", end="2021-12-31"))
    experiment.validate(research(split="WF", start="2010-01-04", end="2021-12-31"))


@pytest.mark.parametrize("change,msg", [
    (dict(start="2009-06-01"), "outside split"),                                      # before 2010 in IS
    (dict(split="STRESS", start="2000-01-03", end="2005-12-30"), "single split"),     # research on 1999-2009
    (dict(split="FULL", start="2010-01-04", end="2021-12-31"), "single split"),
    (dict(split="IS", start="2010-01-04", end="2018-06-29"), "outside split"),        # IS now ends 2017
    (dict(split_scheme="xyz"), "unknown split_scheme"),
])
def test_research_date_rules(change, msg):
    with pytest.raises(experiment.ConfigError, match=msg):
        experiment.validate(research(**change))


def test_benchmark_cannot_start_before_2010():
    c = _cfg(kind="benchmark", strategy_id="B900", experiment_id="E900-99", split_scheme="2010", split="FULL",
             start="2005-01-03", end="2021-12-31", strategy_dir="strategies/B900_spy_buyhold", costs=FIXED)
    with pytest.raises(experiment.ConfigError):
        experiment.validate(c)


def test_stress_window_is_reserved_and_needs_a_finalist():
    base = dict(kind="stress", strategy_id="S001", experiment_id="E001-09", split_scheme="2010", split="STRESS",
                start="1999-01-04", end="2009-12-31", strategy_dir="strategies/S000_pipeline_demo", costs=FIXED,
                portfolio=PORTF, execution_model="d051")
    with pytest.raises(experiment.ConfigError, match="finalist"):
        experiment.validate(_cfg(**base))
    experiment.validate(_cfg(**base, finalist_of="S001"))
    with pytest.raises(experiment.ConfigError, match="reserved"):
        experiment.validate(_cfg(**dict(base, kind="infrastructure", strategy_id="X950", experiment_id="E950-09",
                                        strategy_dir="strategies/X950_timing_canary")))


def test_stress_runs_are_not_trials(tmp_path):
    from qresearch import registry
    p = tmp_path / "INDEX.csv"
    registry.append(dict(experiment_id="E001-01", run_type="original", kind="research"), p)
    registry.append(dict(experiment_id="E001-09", run_type="original", kind="stress"), p)
    assert registry.trial_count(p) == 1


@pytest.mark.parametrize("change", [
    dict(portfolio=dict(PORTF, min_position_usd=2000)),
    dict(portfolio=dict(PORTF, max_positions=20)),
    dict(portfolio=dict(PORTF, max_position_weight=0.2)),
    dict(cash=50_000),
    dict(costs=dict(FIXED, slippage_bps=5)),
])
def test_research_uses_approved_rules(change):
    with pytest.raises(experiment.ConfigError):
        experiment.validate(research(**change))


def test_slippage_stress_multiple_is_allowed():
    experiment.validate(research(costs=dict(FIXED, slippage_stress_multiple=4)))


def test_sizing_kind_for_account_size_retests():
    experiment.validate(research(kind="sizing", cash=50_000, account_size_test_of="E001-01"))
    with pytest.raises(experiment.ConfigError, match="account_size_test_of"):
        experiment.validate(research(kind="sizing", cash=50_000))


def test_audit_window_only_for_infrastructure():
    base = dict(kind="infrastructure", strategy_id="X954", experiment_id="E954-09", split_scheme="2010", split="AUDIT",
                start="2009-09-01", end="2021-12-31", strategy_dir="strategies/X954_survivorship_gap", costs=FIXED)
    experiment.validate(_cfg(**base))
    with pytest.raises(experiment.ConfigError):
        experiment.validate(research(split="AUDIT", start="2009-09-01", end="2017-12-29"))


def test_execution_model_versioning():
    old_pf = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 5000, "max_positions": 15}
    experiment.validate(research(portfolio=old_pf, execution_model="d044"))   # history stays valid
    with pytest.raises(experiment.ConfigError):
        experiment.validate(research(portfolio=old_pf, execution_model="d051"))
    with pytest.raises(experiment.ConfigError):
        experiment.validate(research(execution_model="d044"))                 # d051 rules under d044 label


def test_runner_requires_current_execution_model(root):
    src = (root / "src/qresearch/run.py").read_text()
    assert 'cfg.get("execution_model", "d044") != config.CURRENT_EXECUTION_MODEL' in src
