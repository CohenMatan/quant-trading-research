"""D077: --recover only adopts the recorded backtest of a failed original run, with unchanged code."""
import pytest

from qresearch import gitutil, run


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    monkeypatch.setattr(gitutil, "require_clean_tree", lambda: gitutil.head_commit())


def test_refuses_a_completed_run():
    with pytest.raises(SystemExit, match="failed original"):
        run.recover("E007-02", "anything")


def test_refuses_a_different_backtest_than_recorded():
    with pytest.raises(SystemExit, match="not the one recorded"):
        run.recover("E007-12", "0" * 32)


def test_download_is_shared_by_normal_runs_and_recovery():
    import inspect
    assert "download(cfg, client, handle, bt, runtime)" in inspect.getsource(run.execute)
    assert "download(cfg, client, handle, bt, 0.0)" in inspect.getsource(run.recover)
