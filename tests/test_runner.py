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
