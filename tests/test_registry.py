import pytest

from qresearch import registry


def test_append_and_read(tmp_path):
    p = tmp_path / "INDEX.csv"
    registry.append(dict(experiment_id="E001-01", run_type="original", kind="research", hypothesis_id="H001",
                         strategy_id="S001", status="completed", sharpe=0.1234567, notes='a, "quoted" note'), p)
    registry.append(dict(experiment_id="E001-02", run_type="original", kind="research", hypothesis_id="H001",
                         strategy_id="S001", status="failed"), p)
    rows = registry.read(p)
    assert [r["experiment_id"] for r in rows] == ["E001-01", "E001-02"]
    assert rows[0]["notes"] == 'a, "quoted" note' and rows[0]["sharpe"] == "0.123457"
    assert registry.trial_count(p) == 2
    c = registry.counts(p)
    assert c["experiments"] == 2 and c["hypotheses"] == 1 and c["strategies"] == 1 and c["by_status"]["failed"] == 1


def test_append_never_rewrites_existing_rows(tmp_path):
    p = tmp_path / "INDEX.csv"
    registry.append(dict(experiment_id="E001-01", run_type="original", kind="research"), p)
    before = p.read_bytes()
    registry.append(dict(experiment_id="E001-01", run_type="annotation", kind="research", notes="bugged"), p)
    assert p.read_bytes().startswith(before)
    assert registry.trial_count(p) == 1          # annotations are not trials


def test_rejects_unknown_columns_and_missing_id(tmp_path):
    p = tmp_path / "INDEX.csv"
    with pytest.raises(registry.RegistryError):
        registry.append(dict(experiment_id="E001-01", bogus=1), p)
    with pytest.raises(registry.RegistryError):
        registry.append(dict(kind="research"), p)


def test_rejects_modified_header(tmp_path):
    p = tmp_path / "INDEX.csv"
    p.write_text("experiment_id,foo\n")
    with pytest.raises(registry.RegistryError):
        registry.read(p)


def test_infrastructure_and_benchmarks_are_not_trials(tmp_path):
    p = tmp_path / "INDEX.csv"
    for kind in ("infrastructure", "benchmark", "demo"):
        registry.append(dict(experiment_id="E950-01", run_type="original", kind=kind), p)
    assert registry.trial_count(p) == 1


def test_repo_registry_is_valid(root):
    rows = registry.read(root / "experiments" / "INDEX.csv")
    for r in rows:
        assert r["experiment_id"] and r["run_type"] in ("original", "reproduce", "annotation")


def test_not_started_runs_are_not_trials(tmp_path):
    p = tmp_path / "INDEX.csv"
    for eid in ("E004-05", "E004-06"):
        registry.append(dict(experiment_id=eid, run_type="original", kind="research", status="failed"), p)
    registry.append(dict(experiment_id="E004-05", run_type="annotation", kind="research",
                         status=registry.NOT_STARTED, notes="no spare nodes"), p)
    assert registry.trial_count(p) == 1                 # E004-06 (started, failed) still counts
    assert registry.not_started_ids(p) == {"E004-05"}
    assert len(registry.read(p)) == 3                   # nothing deleted


def test_cycle_final_set_excludes_retired_and_robustness_runs(root):
    from qresearch import cycle
    final = cycle.cycle_experiments("C01")
    retired = cycle.retired_ids()
    assert not (set(final) & set(retired))
    # 19 corrected C01 variations at CP3; D063 (2026-09-29) marks the 5 final H001 runs bugged
    assert len(final) == 14 and not any(e.startswith("E001") for e in final)
    assert all(json_cfg(root, e).get("execution_model") == "d051" for e in final)
    assert not any(json_cfg(root, e).get("robustness_of") for e in final)


def json_cfg(root, eid):
    import json
    return json.loads((root / "experiments" / eid / "config.json").read_text())


def test_trial_accounting_separates_technical_repeats(tmp_path):
    import json
    exp = tmp_path / "experiments"
    base = dict(hypothesis_id="H001", strategy_id="S001", strategy_version="v1.0", params={"a": 1}, split="IS",
                start="2010-01-04", end="2017-12-29", costs={"slippage_bps": 10})
    cfgs = {"E001-01": base, "E001-06": base, "E001-16": base,                    # same config: 1 trial + 2 repeats
            "E001-02": dict(base, strategy_version="v1.1", params={"a": 2}),      # another variation
            "E001-03": dict(base, costs={"slippage_bps": 10, "slippage_stress_multiple": 2})}   # cost stress: a trial
    p = tmp_path / "INDEX.csv"
    for eid, c in cfgs.items():
        (exp / eid).mkdir(parents=True)
        (exp / eid / "config.json").write_text(json.dumps(c))
        registry.append(dict(experiment_id=eid, run_type="original", kind="research", status="completed"), p)
    registry.append(dict(experiment_id="E958-01", run_type="original", kind="infrastructure"), p)
    a = registry.trial_accounting(p, exp)
    assert a["genuine_trials"] == 3 and a["technical_repeats"] == 2 and a["verification_and_benchmark_runs"] == 1
    assert a["all_started_research_runs"] == 5


def test_d069_dsr_trial_categories(tmp_path):
    """D069 (frozen before any C02 result): N for DSR = distinct IS selection candidates only."""
    import json
    exp = tmp_path / "experiments"
    base = dict(hypothesis_id="H001", strategy_id="S001", strategy_version="v1.0", params={"a": 1}, split="IS",
                start="2010-01-04", end="2017-12-29", costs={"slippage_bps": 10})
    cfgs = {"E001-01": base,
            "E001-02": dict(base, strategy_version="v1.1", params={"a": 2}),
            "E001-03": dict(base, costs={"slippage_bps": 10, "slippage_stress_multiple": 2}, robustness_of="E001-01"),
            "E001-04": dict(base, params={"a": 1.2}, robustness_of="E001-01"),              # plateau perturbation
            "E001-05": dict(base, split="VAL", start="2018-01-01", end="2021-12-31"),       # validation
            "E001-06": base,                                                                # technical repeat
            "E001-07": base}                                                                # repeat, retired
    p = tmp_path / "INDEX.csv"
    for eid, c in cfgs.items():
        (exp / eid).mkdir(parents=True)
        (exp / eid / "config.json").write_text(json.dumps(c))
        registry.append(dict(experiment_id=eid, run_type="original", kind="research", status="completed"), p)
    registry.append(dict(experiment_id="E959-01", run_type="original", kind="infrastructure"), p)
    a = registry.trial_accounting(p, exp, retired={"E001-07"})
    assert (a["selection_trials"], a["robustness_runs"], a["validation_runs"], a["technical_repeats"]) == (2, 2, 1, 2)
    assert a["selection_latest"] == {"E001-01": "E001-06", "E001-02": "E001-02"}   # latest valid run per candidate
    assert registry.dsr_trial_count(p, exp) == dict(official=2, conservative=5)


def test_d069_counts_on_the_real_registry():
    """Pins the frozen counts at the C02 prerequisite checkpoint (before any C02 strategy run)."""
    from qresearch import config
    a = registry.trial_accounting(config.INDEX_CSV, config.EXPERIMENTS_DIR)
    assert (a["selection_trials"], a["robustness_runs"], a["validation_runs"]) == (19, 15, 1)
    assert registry.dsr_trial_count() == dict(official=19, conservative=35)
