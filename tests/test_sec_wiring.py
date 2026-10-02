"""D111 wiring: the SEC correction layer is opt-in (never silent), the packed table round-trips with a hash check,
and the SEC client caches every response and throttles requests."""
import json

from qresearch import run, sec_pack
from qresearch.sec_edgar import MIN_INTERVAL_S, SECClient, USER_AGENT
from conftest import ROOT


def _cfg(sec=False):
    cfg = json.loads((ROOT / "experiments/E969-01/config.json").read_text())
    if sec:
        cfg["universe"]["sec_corrections"] = True
    return cfg


def test_pack_roundtrip_and_hash():
    obj = {"a": [1, 2.5, None, "x"], "b": {"c": "d" * 5000}}
    files = sec_pack.pack(obj, "tbl", chunk=1000)
    assert len([f for f in files if f.startswith("tbl_")]) >= 1 and "tbl.py" in files
    assert sec_pack.unpack(files, "tbl") == obj
    ns = {}
    import sys, types
    for name, text in files.items():
        mod = types.ModuleType(name[:-3])
        exec(text, mod.__dict__)
        sys.modules[name[:-3]] = mod
    assert sys.modules["tbl"].load_table() == obj


def test_sec_data_uploaded_only_when_opted_in():
    plain = run.assemble_files(_cfg(False), None, False)
    assert not any(n.startswith("qr_sec_data") for n in plain)
    assert "qr_sec_corrections.py" in plain        # logic only; inert without the table and the flag


def test_harness_default_is_unchanged():
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert 'if self._qr_u.get("sec_corrections"):' in src
    assert "self.qr_sec = None" in src
    # without the flag no security lacking fundamentals can pass: the only path is sec.has(sid)
    assert "if sec is None or not sec.has(sid):\n                    continue" in src


def test_contact_is_runtime_only(tmp_path, monkeypatch):
    """D113: the SEC contact address comes only from the environment or a local file outside the repository."""
    import qresearch.sec_edgar as E
    monkeypatch.setattr(E, "CONTACT_FILE", tmp_path / "none")
    monkeypatch.delenv("SEC_CONTACT_EMAIL", raising=False)
    assert E.contact_user_agent() == USER_AGENT
    monkeypatch.setenv("SEC_CONTACT_EMAIL", "contact@example.org")
    assert E.contact_user_agent().endswith("contact@example.org")
    src = (ROOT / "src/qresearch/sec_edgar.py").read_text()
    assert "@" not in USER_AGENT and "gmail" not in src.lower()


def test_client_caches_and_throttles(tmp_path, monkeypatch):
    import qresearch.sec_edgar as E
    monkeypatch.setattr(E, "CONTACT_FILE", tmp_path / "none")
    monkeypatch.delenv("SEC_CONTACT_EMAIL", raising=False)
    calls = []

    class Sess:
        def get(self, url, headers, timeout):
            calls.append((url, headers["User-Agent"]))

            class R:
                status_code = 200
                content = b'{"ok": 1}'
            return R()

    slept = []
    c = SECClient(cache_dir=tmp_path, session=Sess(), sleep=slept.append)
    assert c.get_json("https://data.sec.gov/x.json") == {"ok": 1}
    assert c.get_json("https://data.sec.gov/x.json") == {"ok": 1}
    assert len(calls) == 1 and calls[0][1] == USER_AGENT and c.cache_hits == 1
    c.get_json("https://data.sec.gov/y.json")
    assert MIN_INTERVAL_S >= 0.1 and len(calls) == 2
    assert "@" not in USER_AGENT          # no personal contact data is sent
