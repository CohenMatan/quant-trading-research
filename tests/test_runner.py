import hashlib
import json
import subprocess

import pytest
import requests

from qresearch import experiment, gitutil
from qresearch.qc_client import MissingCredentialsError, QCClient, QCError, auth_headers
from test_holdout_lock import _cfg


def test_auth_header_is_hashed_token():
    (user, digest), headers = auth_headers("123", "secret-token", now=lambda: 1700000000)
    assert user == "123" and headers == {"Timestamp": "1700000000"}
    assert digest == hashlib.sha256(b"secret-token:1700000000").hexdigest()
    assert "secret-token" not in digest


def test_missing_credentials(monkeypatch):
    monkeypatch.delenv("QC_USER_ID", raising=False)
    monkeypatch.delenv("QC_API_TOKEN", raising=False)
    with pytest.raises(MissingCredentialsError):
        QCClient()


class _Resp:
    def __init__(self, payload, status=200):
        self._p, self.status_code = payload, status

    def json(self):
        return self._p

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)


class _Session:
    def __init__(self, payload):
        self.payload, self.calls = payload, []

    def post(self, url, auth, headers, json, timeout):
        self.calls.append((url, auth, headers))
        return _Resp(self.payload)


def test_errors_never_contain_credentials():
    s = _Session({"success": False, "errors": ["bad token TOKEN-XYZ for user 999"]})
    c = QCClient(user_id="999", token="TOKEN-XYZ", session=s, max_retries=0)
    with pytest.raises(QCError) as e:
        c.call("authenticate")
    assert "TOKEN-XYZ" not in str(e.value) and "999" not in str(e.value)
    url, auth, _ = s.calls[0]
    assert "TOKEN-XYZ" not in url and auth[1] != "TOKEN-XYZ"


@pytest.mark.parametrize("change,msg", [
    (dict(experiment_id="E1-01"), "experiment_id"),
    (dict(strategy_id="S950"), "strategy_id"),
    (dict(kind="research", strategy_id="S001", experiment_id="E001-01"), "hypothesis"),
    (dict(experiment_id="E951-01"), "strategy's number"),
    (dict(split="IS"), "outside split"),
    (dict(universe={"min_market_cap": 1e9}), "below the approved"),
    (dict(kind="research", strategy_id="S001", experiment_id="E001-01", hypothesis_id="H001", split="FULL",
          start="1999-01-04"), "single split"),
])
def test_config_validation(change, msg):
    with pytest.raises(experiment.ConfigError, match=msg):
        experiment.validate(_cfg(**change))


def test_committed_configs_are_valid(root):
    ids = []
    for p in root.glob("experiments/E*/config.json"):
        c = json.loads(p.read_text())
        experiment.validate(c)
        assert p.parent.name == c["experiment_id"]
        assert (root / c["strategy_dir"] / "main.py").exists()
        ids.append(c["experiment_id"])
    assert len(ids) == len(set(ids))


def _repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(tmp_path), "config", k, v], check=True)
    (tmp_path / "f.txt").write_text("1")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "c"], check=True)
    return tmp_path


def test_clean_tree_check(tmp_path):
    r = _repo(tmp_path)
    head = gitutil.require_clean_tree(r)
    assert len(head) == 40
    (r / "f.txt").write_text("2")
    with pytest.raises(gitutil.DirtyTreeError):
        gitutil.require_clean_tree(r)
    (r / "f.txt").write_text("1")
    (r / "new.txt").write_text("untracked")
    with pytest.raises(gitutil.DirtyTreeError):
        gitutil.require_clean_tree(r)


def test_files_are_read_from_the_commit(tmp_path):
    r = _repo(tmp_path)
    head = gitutil.head_commit(r)
    (r / "f.txt").write_text("changed")
    assert gitutil.show_file(head, "f.txt", r) == "1"


def test_incomplete_order_detection():
    from qresearch.qc_client import incomplete_order
    filled_ev = {"status": "filled", "fillQuantity": 1}
    assert incomplete_order({"status": 3, "events": []})
    assert incomplete_order({"status": 3})
    assert not incomplete_order({"status": 3, "events": [{"status": "submitted"}, filled_ev]})
    assert not incomplete_order({"status": 5, "events": []})      # cancelled: no fill expected


# ---- E003-04/05/06 incidents (D053): transient orders API errors, stalled backtests, failure metadata

class _ScriptedClient(QCClient):
    """QCClient whose `call` replays scripted responses per endpoint (an Exception is raised)."""
    def __init__(self, script):
        super().__init__(user_id="u", token="t", session=object(), max_retries=0)
        self.script = {k: list(v) for k, v in script.items()}

    def call(self, endpoint, **payload):
        seq = self.script[endpoint]
        r = seq.pop(0) if len(seq) > 1 else seq[0]
        if isinstance(r, Exception):
            raise r
        return r


def _filled(i):
    return {"id": i, "status": 3, "events": [{"status": "filled"}]}


def test_orders_read_retries_transient_errors_and_loading(monkeypatch):
    from qresearch.qc_client import BacktestHandle
    monkeypatch.setattr("qresearch.qc_client.time.sleep", lambda s: None)
    c = _ScriptedClient({"backtests/orders/read": [
        QCError("backtests/orders/read failed: ['Error retrieving orders result, please try again later']"),
        {"success": True, "status": "loading", "progress": 0.0},
        QCError("backtests/orders/read: giving up after retries (HTTP 500)"),
        {"success": True, "orders": [_filled(1), _filled(2)], "length": 2},
    ]})
    out = c.read_orders(BacktestHandle(1, "b", "c"), expected=2)
    assert [o["id"] for o in out] == [1, 2]


def test_orders_loading_is_never_accepted_as_empty(monkeypatch):
    from qresearch.qc_client import BacktestHandle
    monkeypatch.setattr("qresearch.qc_client.time.sleep", lambda s: None)
    c = _ScriptedClient({"backtests/orders/read": [{"success": True, "status": "loading", "progress": 0.0}]})
    with pytest.raises(QCError, match="still loading"):
        c.read_orders(BacktestHandle(1, "b", "c"), expected=None, timeout_s=0)


def test_stalled_backtest_is_detected():
    from qresearch.qc_client import BacktestHandle
    t = [0.0]
    c = _ScriptedClient({"backtests/read": [
        {"success": True, "backtest": {"completed": False, "progress": 0.5}},
        {"success": True, "backtest": {"completed": False, "progress": 0.97, "status": "In Progress..."}}]})

    def sleep(s):
        t[0] += s
    with pytest.raises(QCError, match="stalled: progress 0.97"):
        c.wait_backtest(BacktestHandle(1, "b", "c"), poll_s=60, stall_s=45 * 60, clock=lambda: t[0], sleep=sleep)
    assert 45 * 60 < t[0] < 6 * 3600


def test_running_backtests_lists_incomplete_only():
    c = _ScriptedClient({"projects/read": [{"success": True, "projects": [{"projectId": 7, "name": "qr-S003"}]}],
                         "backtests/list": [{"success": True, "backtests": [
                             {"name": "E003-06", "completed": False}, {"name": "E003-05", "completed": True}]}]})
    assert c.running_backtests() == [("qr-S003", "E003-06")]


def test_failed_run_keeps_backtest_id_and_stage():
    from qresearch import run as runmod
    from qresearch.qc_client import BacktestHandle

    class C:
        def find_or_create_project(self, name): return 7
        def sync_files(self, p, f): pass
        def pin_lean_version(self, p, v): pass
        def compile(self, p): return "cid"
        def start_backtest(self, p, cid, name): return BacktestHandle(p, "bt123", cid)
        def wait_backtest(self, h): raise QCError("Backtest bt123 stalled")
    state = {}
    with pytest.raises(QCError):
        runmod.execute({"experiment_id": "E003-09", "strategy_id": "S003", "lean_version_id": 1}, {}, C(), state)
    assert state["backtest_id"] == "bt123" and state["project_id"] == 7 and state["stage"] == "backtest"
    assert state["backtest_started_utc"]
