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
