"""P7-CP5c (D184): the X995 timing probe on a fake QuantConnect environment (SYNTHETIC fundamentals objects): the
schema scan, the packed per-security timing records, V lines in the X971 format, no vendor value in any output,
the 2017-12-31 guard and the config rule."""
import base64
import copy
import json
import sys
import types
import zlib
from datetime import date, datetime

import pytest

from conftest import ROOT, load_module


class Obj:
    """A fake vendor object: unknown members are None; windows carry values."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __getattr__(self, n):
        if n.startswith("__"):
            raise AttributeError(n)
        return None


def win(**kw):
    return Obj(**kw)


def fund(sid, pe, fd, rev):
    er = Obj(period_ending_date=win(three_months=datetime(*pe), twelve_months=datetime(*pe)),
             file_date=win(three_months=datetime(*fd) if fd else None, twelve_months=None),
             accession_number=win(three_months="0000000000-11-000001"), form_type=win(three_months="10-Q"),
             period_type=win(three_months="3M"))
    inc = Obj(total_revenue=win(three_months=rev, twelve_months=4 * rev, value=rev))
    fs = Obj(period_ending_date=win(three_months=datetime(*pe)), file_date=win(three_months=None),
             income_statement=inc, balance_sheet=Obj(total_assets=win(three_months=10 * rev, value=10 * rev)),
             cash_flow_statement=Obj())
    return Obj(symbol=types.SimpleNamespace(id=sid, value=sid.split()[0]), has_fundamental_data=True,
               earning_reports=er, financial_statements=fs, company_reference=Obj(cik="123"), market_cap=0.0,
               price=10.0, split_factor=1.0)


def _host(monkeypatch, end="2017-12-31"):
    ai = types.ModuleType("AlgorithmImports")
    ai.SplitType = types.SimpleNamespace(SPLIT_OCCURRED=1)
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    hm = types.ModuleType("qr_harness")

    class QRAlgorithm:
        def __init__(self):
            self.qr = {"end": end}
            self.qr_params = {}
            self.msgs = []

        def _qr_log(self, line):
            self.msgs.append(line)

        def _qr_select(self, fl):
            return []

        def on_data(self, data):
            pass
    hm.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", hm)
    monkeypatch.syspath_prepend(str(ROOT / "strategies/X995_timing_probe"))
    mod = load_module(ROOT / "strategies/X995_timing_probe/main.py", "x995_test")
    a = mod.SECVerification()
    a.qr_initialize()
    return a


def test_x995_probe_outputs(monkeypatch):
    a = _host(monkeypatch)
    sid = sorted(a.sid_cik)[0]
    for d, pe, fd in ((date(2010, 3, 31), (2009, 12, 31), (2010, 2, 20)), (date(2010, 5, 3), (2010, 3, 31), None),
                      (date(2010, 5, 20), (2010, 3, 31), (2010, 5, 5))):
        a.time = datetime(d.year, d.month, d.day, 0, 0)
        a._qr_select([fund(sid, pe, fd, 1000.0 + d.day)])
    a.qr_on_end()
    tags = {m.split("|")[0] for m in a.msgs}
    assert {"SCH", "SCHN", "V", "TH", "TB", "KA", "C"} <= tags, tags
    th = next(m for m in a.msgs if m.startswith("TH|")).split("|")
    blob = "".join(m.split("|", 2)[2] for m in sorted((m for m in a.msgs if m.startswith("TB|")),
                                                       key=lambda m: int(m.split("|")[1])))
    raw = zlib.decompress(base64.b64decode(blob)).decode().split("\n")
    assert int(th[2]) == len(raw) - 1 == 3                      # three distinct timing tuples
    head = raw[0][1:].split(",")
    row = dict(zip(head, raw[2].split("|", 2)[2].split(",")))
    assert row["earning_reports.file_date.three_months"] == "-" and row["earning_reports.period_ending_date.three_months"] == "2010-03-31"
    sch = [m for m in a.msgs if m.startswith("SCH|") and "|earning_reports|file_date|three_months|" in m]
    assert sch and '"date"' in sch[0]
    text = "\n".join(a.msgs)
    for v in ("1031.0", "4124.0", "10310.0", "1003.0"):         # no vendor value anywhere (licence)
        assert v not in text
    with pytest.raises(Exception):
        _host(monkeypatch, end="2018-01-31")


def test_x995_config_rule():
    from qresearch import experiment
    for e in ("E995-02", "E995-03"):
        c = json.loads((ROOT / f"experiments/{e}/config.json").read_text())
        experiment.validate(c)
    bad = copy.deepcopy(c)
    bad["end"] = "2018-06-30"
    with pytest.raises(experiment.ConfigError):
        experiment.validate(bad)
    bad = copy.deepcopy(c)
    bad.pop("lean_version_policy")
    with pytest.raises(experiment.ConfigError):
        experiment.validate(bad)


def test_x995_fits_the_project_file_limit():
    """QuantConnect (2026-10-10): researcher projects hold at most 50 files (E995-01 failed at upload)."""
    from qresearch import run
    c = json.loads((ROOT / "experiments/E995-03/config.json").read_text())
    files = run.assemble_files(c, None, False)
    assert len(files) <= 50 and all(len(v) <= 64_000 for v in files.values())
