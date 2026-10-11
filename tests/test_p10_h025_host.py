"""H025 host S027 (owner D204) on the fake QuantConnect environment of the H022 / Data v2 tests (SYNTHETIC prices,
fundamentals, SEC reference and a SYNTHETIC SEC event ledger):
- audit mode maps every ledger event (review strictly before the trigger, verified identity, multi-class rule, window
  status) and reads no response;
- canary checks pass on synthetic data; null worlds equal qr_h025.null_world on the host's own pools and need the
  pinned in-host ledger digest; real mode output equals qr_h025.summary / gates; config rules and runner wiring."""
import ast
import importlib.util
import json
import shutil
import sys
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

import qr_h025 as H
from conftest import ROOT
from qresearch import p10h025, p7pred_v2
from test_p7_export import _host
from test_p7_h022_host import _mk
from test_p7_h022_v2 import _chunks, _env, _mutate

S027 = "strategies/S027_h025_insider/main.py"
S024 = "strategies/S024_h022_data_v2/main.py"
spec = importlib.util.spec_from_file_location("h025_ledger", ROOT / "research" / "phase10" / "h025_ledger.py")
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)

CAL = [d for d in (date(2007, 1, 1) + timedelta(days=i) for i in range(4100)) if d.weekday() < 5
       and d <= date(2017, 12, 29)]
IDX = {d: i for i, d in enumerate(CAL)}


def _row(eid, kind, cik, trig, ws=None, n=2, value=150000.0, near=0, sym="T0"):
    i = IDX.get(trig.date())
    e = i if i is not None and trig.hour < 9 else next(k for k, d in enumerate(CAL) if d > trig.date())
    x = e + 19
    ex = CAL[x] if x < len(CAL) else None
    if ws is None:
        ws = "before_window" if trig.date() < date(2011, 2, 1) else ("exit_after_2017" if ex is None else "in_window")
    return dict(event_id=eid, kind=kind, issuer_cik=cik, symbol_as_filed=sym, trigger_et=trig.isoformat(sep=" "),
                trigger_date=str(trig.date()), entry_session=str(CAL[e]), exit_session=str(ex or ""),
                window_status=ws, n_insiders=n, cluster_value=f"{value:.2f}", ceo_cfo=1, director_only=0,
                n_qualifying_filings=n, median_delay_days=2.0, near_cluster=near)


def _ledger():
    rows = [_row("C-early", "cluster", "c3", datetime(2010, 12, 15, 17)),           # before the window (cooldown only)
            _row("C-multi", "cluster", "c7", datetime(2012, 3, 14, 18)),            # two classes share CIK c7
            _row("C-none", "cluster", "999999", datetime(2012, 5, 2, 16)),          # issuer outside the universe
            _row("C-late", "cluster", "c4", datetime(2017, 12, 20, 18))]            # exit after 2017
    k = 0
    for y in range(2011, 2018):
        for m in (2, 5, 8, 11):
            for j in (3, 12, 15):
                if y == 2017 and m == 11:
                    continue
                rows.append(_row(f"C{k:03d}", "cluster", f"c{j}", datetime(y, m, 3 + j, 8 if j == 12 else 17),
                                 n=2 + (k % 3), value=1e5 * (1 + k % 7)))
                k += 1
    rows.append(_row("S-one", "single", "c16", datetime(2013, 6, 12, 19), n=1))
    rows.append(_row("S-near", "single", "c3", datetime(2013, 2, 7, 19), n=1, near=1))
    rows.sort(key=lambda r: (r["trigger_et"], r["issuer_cik"], r["kind"]))
    return rows


def _events_module(tmp_path, rows):
    payload = L.csv_bytes(rows, L.LEAN_FIELDS)
    for name, text in L.pack(payload).items():
        (tmp_path / "lean" / name).write_text(text)
    for k in [k for k in sys.modules if k.startswith("qr_h025_events")]:
        del sys.modules[k]
    return L._sha(payload)


def _cal_sha():
    return H.sha([str(d) for d in CAL if str(d) >= "2010-10-01"])


_CACHE = {}


def _run(monkeypatch, tmp_path, mode, **params):
    key = (mode, json.dumps(params, sort_keys=True))
    if key not in _CACHE:
        _env(monkeypatch, tmp_path)
        shutil.copy(ROOT / S024, tmp_path / "lean" / "qr_s024.py")
        monkeypatch.delitem(sys.modules, "qr_s024", raising=False)
        psha = _events_module(tmp_path, _ledger())
        base = dict(spec_sha256="spec", pred_code_sha256=p7pred_v2.PRED_CODE_SHA256, h025_code_sha256="code",
                    payload_sha256=psha, calendar_sha256=_cal_sha())
        a = _host(monkeypatch, _mk(), path=S027, cls="H025Insider", params=dict(base, mode=mode, **params),
                  mutate=_mutate, sec_off=True)
        hist = a.history

        def history(what, *x, **kw):                 # the fake market gives SPY no open: add one (close x 0.998)
            spy = a.spy
            if what is spy or (isinstance(what, list) and what == [spy] and kw.get("data_normalization_mode")):
                df = hist(spy, *x, **kw)
                return df.assign(open=df["close"] * 0.998)     # the host selects its own window by session day
            return hist(what, *x, **kw)
        a.history = history
        a.qr_on_end()
        out = json.loads(_chunks(a.msgs, "QRP7V"))
        blob = _chunks(a.msgs, "QRH")
        _CACHE[key] = (a, out, json.loads(L.zlib.decompress(L.base64.b64decode(blob)).decode()) if blob else None)
    return _CACHE[key]


def test_audit_maps_events_and_reads_no_response(monkeypatch, tmp_path):
    a, st, blob = _run(monkeypatch, tmp_path, "audit")
    rows = {r[0]: r for r in blob["rows"]}
    assert H.sha(blob["rows"]) == st["in_host_ledger_sha256"]
    assert rows["C-early"][1] == "NO_REVIEW"                       # no review before 2011-01-31
    assert rows["C-multi"][1] == "ELIGIBLE_MULTICLASS" and rows["C-multi"][3] in ("S07", "S08")
    assert rows["C-none"][1] == "NOT_ELIGIBLE" and rows["C-none"][3] is None
    for eid, r in rows.items():
        if r[2] is not None:
            assert r[2] < next(x for x in _ledger() if x["event_id"] == eid)["trigger_date"]
    c = st["counts"]
    assert c["primary"] >= 60 and c["single_controls"] == 1 and c["multiclass"] == 1
    assert "C-late" in rows and c["by_kind_window_status"]["cluster|exit_after_2017|ELIGIBLE"] == 1
    assert "q_panel" not in st and "null" not in st and "real" not in st
    assert st["pit_audit"] and all(v == 0 for v in st["pit_audit"].values())


def test_canary_passes_on_synthetic_data(monkeypatch, tmp_path):
    _, st0, _ = _run(monkeypatch, tmp_path, "audit")
    a, st, blob = _run(monkeypatch, tmp_path, "canary", in_host_ledger_sha256=st0["in_host_ledger_sha256"])
    ck = st["canary"]
    g = ck["ledger"]
    assert all(g[k] == 0 for k in ("review_not_before_trigger", "review_not_latest", "sid_not_eligible",
                                   "cik_mismatch", "entry_mismatch", "exit_mismatch", "cooldown_violations"))
    assert g["mapped"] >= 60
    assert ck["spy_total_return"]["checked"] > 0 and ck["spy_total_return"]["worst_rel"] < 1e-9
    fr = ck["corporate_actions"]
    assert fr["frozen_fn_mismatch"] == 0
    assert fr["by_class"]["split"]["n"] > 0 and fr["by_class"]["dividend"]["n"] > 0
    for c in fr["by_class"].values():
        assert c["agree_1e9"] == c["n"] and c["status_agree"] == c["n"]
    assert ck["synthetic_timing"]["ok"]
    sy = ck["synthetic_statistics"]
    assert sy["repeat_identical"] and sy["planted"]["0.04"]["t"] > sy["planted"]["0.0"]["t"]
    assert ck["real_responses_computed"] is False and blob is None and "q_panel" not in st


def test_null_worlds_and_real_mode(monkeypatch, tmp_path):
    _, st0, _ = _run(monkeypatch, tmp_path, "audit")
    pin = st0["in_host_ledger_sha256"]
    a, st, blob = _run(monkeypatch, tmp_path, "null", in_host_ledger_sha256=pin, seeds=[1, 300])
    assert st["null"]["worlds"] == 300 and st["null"]["nonfinite"] == 0
    assert [w[0] for w in blob["worlds"]] == list(range(1, 301))
    # the worlds are qr_h025.null_world on the host's own pools
    a2, st2, blob2 = _run(monkeypatch, tmp_path, "null", in_host_ledger_sha256=pin, seeds=[1, 300],
                          response_panel_sha256=st["response_panel_sha256"])
    assert blob2 == blob and st2["response_panel_sha256"] == st["response_panel_sha256"]
    c, raw = H.critical_value([w[1] for w in blob["worlds"]])
    real = dict(in_host_ledger_sha256=pin, c_event=c, null_result_sha256="n", threshold_commit="t",
                response_panel_sha256=st["response_panel_sha256"], event_ledger_sha256="e")
    a3, st3, out = _run(monkeypatch, tmp_path, "real", **real)
    f = out["fields"]
    ev = [dict(zip(f, r)) for r in out["events"]]
    s = H.summary(np.array([e["y"] for e in ev]), [e["month"] for e in ev], [e["year"] for e in ev])
    assert json.loads(json.dumps(s)) == out["summary"]
    assert out["gates"] == H.gates(out["summary"], c)
    assert st3["real"]["evaluable"] == len(ev) == st["null"]["evaluable"]
    assert {e["level"] for e in ev} <= {"L1", "L2", "L3", "L4"}
    assert len(out["controls"]) == 1
    with pytest.raises(Exception, match="response panel differs"):
        _CACHE.pop(("real", json.dumps(dict(real, response_panel_sha256="x"), sort_keys=True)), None)
        _run(monkeypatch, tmp_path, "real", **dict(real, response_panel_sha256="x"))


def test_refuses_unpinned_or_different_ledger(monkeypatch, tmp_path):
    with pytest.raises(Exception, match="in-host ledger"):
        _run(monkeypatch, tmp_path, "canary", in_host_ledger_sha256="0" * 64)
    with pytest.raises(Exception, match="need the pinned in-host ledger"):
        _run(monkeypatch, tmp_path, "null", seeds=[1, 2])


def test_host_structure_and_names():
    src = (ROOT / S027).read_text()
    tree = ast.parse(src)
    cls = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "H025Insider"][0]
    own = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
    allowed = {"qr_initialize", "_month_end", "qr_on_end"}
    assert all(n in allowed or n.startswith("_q_") for n in own)
    x998 = (ROOT / "strategies/X998_data_v2_export/main.py").read_text() + (ROOT / S024).read_text()
    for n in own - allowed:
        assert f"def {n}(" not in x998
    head = src.split("from AlgorithmImports")[0]
    for m in ("qr_s024", "qr_x998", "qr_h025", "qr_h025_events"):
        assert m in head
    code = "\n".join(l.split("#")[0] for l in src.splitlines())
    assert "2018" not in code and "2019" not in code and "202" not in code.replace("2026", "")


def test_runner_uploads_h025_modules(tmp_path):
    from qresearch import run
    cfg = json.loads((ROOT / "experiments" / "E027-01" / "config.json").read_text()) \
        if (ROOT / "experiments" / "E027-01" / "config.json").exists() else None
    if cfg is None:
        pytest.skip("E027-01 config not written yet")
    files = run.collect_files(cfg, None, False) if hasattr(run, "collect_files") else None
    if files is None:
        pytest.skip("runner exposes no collect_files")
    assert "qr_h025.py" in files and "qr_h025_events.py" in files and "qr_s024.py" in files
    assert len(files) <= 50 and all(len(v) <= 64000 for v in files.values())
