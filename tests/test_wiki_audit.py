"""WIKI Prices audit (D298): protocol pin and the audit code, on small synthetic fixtures only (no WIKI data)."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research" / "tt" / "wiki_audit"
sys.path.insert(0, str(HERE))
import sec_reference as sr  # noqa: E402
import wiki_audit as wa  # noqa: E402


def test_protocol_frozen():
    pin = json.loads((HERE / "PROTOCOL_PIN.json").read_text())
    assert hashlib.sha256((ROOT / pin["protocol"]).read_bytes()).hexdigest() == pin["sha256"]


def bars(ticker, dates, close=10.0, **kw):
    rows = []
    for i, d in enumerate(dates):
        c = close if np.isscalar(close) else close[i]
        rows.append({"ticker": ticker, "date": d, "open": c, "high": c * 1.01, "low": c * 0.99, "close": c,
                     "volume": 1000.0, "ex-dividend": 0.0, "split_ratio": 1.0, "adj_open": c, "adj_high": c * 1.01,
                     "adj_low": c * 0.99, "adj_close": c, "adj_volume": 1000.0})
    df = pd.DataFrame(rows, columns=wa.COLUMNS)
    for k, v in kw.items():
        df[k] = v
    return df


DATES = [str(d.date()) for d in pd.bdate_range("2012-01-02", "2012-03-30")]


def test_load_wiki_window_and_schema(tmp_path):
    df = pd.concat([bars("OLD", ["2009-12-31", "2010-01-04"]), bars("new", ["2017-12-29", "2018-01-02"])])
    f = tmp_path / "w.csv"
    df.to_csv(f, index=False)
    out, total = wa.load_wiki(f)
    assert total == 4 and sorted(out["date"]) == ["2010-01-04", "2017-12-29"] and set(out["ticker"]) == {"OLD", "NEW"}
    bad = tmp_path / "b.csv"
    df.drop(columns=["adj_volume"]).to_csv(bad, index=False)
    with pytest.raises(SystemExit):
        wa.load_wiki(bad)


def test_reference_sessions_majority_rule():
    df = pd.concat([bars("A", DATES), bars("B", DATES), bars("C", DATES[:1] + ["2012-01-07"])])  # Saturday by one name
    s = wa.reference_sessions(df)
    assert "2012-01-07" not in s and len(s) == len(DATES)


def test_integrity_detects_spikes_invalid_and_adjustment():
    c = [10.0] * len(DATES)
    c[10], c[11] = 20.0, 10.0                                   # +69% then -69%: spike
    a = bars("A", DATES, close=c)
    b = bars("B", DATES)
    b.loc[5, "high"] = 5.0                                      # invalid OHLC
    d = bars("D", DATES)
    d.loc[20, "ex-dividend"] = 0.10                             # dividend 1% on day 20: earlier adj prices scaled
    for k in ("open", "high", "low", "close"):
        d.loc[:19, "adj_" + k] = d.loc[:19, k] * (1 - 0.10 / 10.0)
    e = bars("E", DATES)
    for k in ("open", "high", "low", "close"):
        e.loc[:29, "adj_" + k] = e.loc[:29, k] * 0.5           # unexplained ratio change at day 30
    df = pd.concat([a, b, d, e], ignore_index=True)
    out = wa.integrity(df, wa.reference_sessions(df))
    n = out["ticker_sessions"]
    assert out["spike_share"] == pytest.approx(1 / n)
    assert out["invalid_ohlc_share"] == pytest.approx(1 / n)
    assert out["ratio_changes"] == 2 and out["ratio_changes_explained_share"] == pytest.approx(0.5)
    assert out["dividend_events"] == 1 and out["dividend_factor_agree_share"] == 1.0
    assert out["missing_share"] == 0.0


def frame_row(cik, ym, prefix, **kw):
    r = {"cik": cik, "ym": ym, "float": 3e9, "prefix": prefix, "sic": 3570, "fin": False, "foreign_name": False,
         "left": False, "exit_ym": None, "exit_type": None, "leaver_month": False, "size_tercile": 1, "prefix_shared": False}
    r.update(kw)
    return r


def test_classify_identity_classes():
    df = pd.concat([bars("AAA", DATES), bars("BBB", DATES[:5]), bars("RRR", DATES)])
    s = wa.reference_sessions(df)
    b, per_m = wa.month_bars(df, s)
    rows = [frame_row(1, 201202, "AAA"), frame_row(2, 201202, "BBB"), frame_row(3, 201202, "ZZZ"),
            frame_row(4, 201202, "RRR"), frame_row(5, 201202, "SSS", prefix_shared=True), frame_row(6, 201201, "BBB")]
    cl = {r["cik"]: r["cls"] for r in wa.classify(rows, {"RRR": [4, 9]}, set(df["ticker"]), b, per_m)}
    assert cl == {1: "MATCHED", 2: "MISSING-OUT-OF-LIFE", 3: "UNRESOLVED-IDENTITY", 4: "AMBIGUOUS", 5: "AMBIGUOUS",
                  6: "MISSING-PARTIAL"}
    comp = wa.cov([dict(r, cls=cl[r["cik"]]) for r in rows])
    assert comp["strict"] == pytest.approx(1 / 4) and comp["resolved"] == pytest.approx(1 / 3)


def _comp(strict, leaver=None, types=None, strata=None, classes=None, n=1000):
    cv = lambda v, reg=100: {"strict": v, "resolved": v, "registrants": reg, "n": n, "classes": classes or {"MATCHED": n}}
    return {"overall": cv(strict), "by_year": {y: cv(strict) for y in range(2010, 2018)},
            "leavers": cv(leaver if leaver is not None else strict), "non_leavers": cv(strict),
            "leavers_by_exit_type": types if types is not None else {"ACQUIRED": cv(strict, 30)},
            "strata": strata or {"2012|size1": cv(strict)}}


GOOD_INT = {"missing_share": 0.001, "spike_share": 0.0, "invalid_ohlc_share": 0.0, "ratio_changes_explained_share": 1.0,
            "dividend_factor_agree_share": 1.0}


def _ready(n_per_cell=25, leavers=40):
    out, cik = [], 0
    for y in range(2011, 2018):
        for t in (1, 2, 3):
            for _ in range(n_per_cell):
                cik += 1
                out.append(frame_row(cik, y * 100 + 6, "X", size_tercile=t, leaver_month=cik <= leavers))
    return out


def test_gates_pass_fail_inconclusive():
    cal, sp = {"ok": True}, {"tested": 100, "agree_share": 0.97}
    g = wa.gates(_comp(0.95), GOOD_INT, cal, sp, _ready())
    assert g["overall"] == "SUFFICIENT FOR EXPLORATORY CHART RESEARCH"
    assert wa.gates(_comp(0.60), GOOD_INT, cal, sp, _ready())["A1"] == "FAIL"
    assert wa.gates(_comp(0.80), GOOD_INT, cal, sp, _ready())["overall"] == "INCONCLUSIVE"
    assert wa.gates(_comp(0.95, leaver=0.70), GOOD_INT, cal, sp, _ready())["A2"] == "FAIL"     # gap 25 points
    assert wa.gates(_comp(0.95, types={}), GOOD_INT, cal, sp, _ready())["A2"] == "INCONCLUSIVE"
    assert wa.gates(_comp(0.95), GOOD_INT, {"ok": False}, sp, _ready())["A5"] == "INCONCLUSIVE"
    assert wa.gates(_comp(0.95), dict(GOOD_INT, spike_share=0.01), cal, sp, _ready())["A5"] == "FAIL"
    assert wa.gates(_comp(0.95), GOOD_INT, cal, sp, _ready(n_per_cell=5))["A7"] == "FAIL"
    amb = _comp(0.95, classes={"MATCHED": 900, "AMBIGUOUS": 100})
    assert wa.gates(amb, GOOD_INT, cal, sp, _ready())["A4"] == "FAIL"


def test_calendar_check():
    s = [f"{y}-01-{d:02d}" for y, n in wa.NYSE_SESSIONS.items() for d in range(1, 1 + 1)]
    assert not wa.calendar_check(s)["ok"]


def test_sec_exit_type_rules():
    forms = [("2015-01-10", "8-K", "1.03,9.01"), ("2015-03-01", "15-12B", "")]
    assert sr.exit_type(forms, 201503) == "FAILED"
    assert sr.exit_type([("2015-01-10", "DEFM14A", "")], 201503) == "ACQUIRED"
    assert sr.exit_type([("2015-02-10", "25-NSE", "")], 201503) == "DELISTED-OTHER"
    assert sr.exit_type([("2010-02-10", "DEFM14A", "")], 201503) == "UNKNOWN"      # outside the 24-month window
    assert sr.exit_type(None, 201503) == "UNKNOWN"


def test_sec_frame_point_in_time_and_terciles():
    filings = [{"cik": 1, "accn": "a1", "form": "10-K", "filed": "2012-03-15", "sic": 3570, "name": "ALPHA INC", "prefix": "alp"},
               {"cik": 1, "accn": "q1", "form": "10-Q", "filed": "2019-05-01", "sic": 3570, "name": "ALPHA INC", "prefix": "alp"},
               {"cik": 2, "accn": "a2", "form": "10-K", "filed": "2012-02-20", "sic": 6726, "name": "BETA FUND", "prefix": "bet"},
               {"cik": 3, "accn": "a3", "form": "10-K", "filed": "2012-02-20", "sic": 2834, "name": "GAMMA CORP", "prefix": "gam"}]
    floats = {"a1": (1, "2011-06-30", 5e9), "a2": (2, "2011-06-30", 9e9), "a3": (3, "2011-06-30", 1e9)}
    rows = sr.build(floats, filings, forms_of=lambda c: None)
    months = sorted({r["ym"] for r in rows if r["cik"] == 1})
    assert months[0] == 201204                        # filed 2012-03-15: not usable for March 2012
    assert months[-1] == sr.ym_add(201203, 15)        # stale after 15 months
    assert {r["cik"] for r in rows} == {1}            # fund SIC excluded; float < $2B excluded
    assert all(r["prefix"] == "ALP" and r["size_tercile"] == 1 for r in rows)


def test_main_refuses_unverified_file(tmp_path, monkeypatch):
    f = tmp_path / "w.csv"
    bars("A", DATES[:3]).to_csv(f, index=False)
    man = tmp_path / "m.json"
    man.write_text(json.dumps({"sha256": "0" * 64}))
    monkeypatch.setattr(wa, "MANIFEST", man)
    with pytest.raises(SystemExit):
        wa.main(str(f))


def test_acquire_never_records_the_key(tmp_path):
    import acquire_wiki as aq

    class R:
        status_code = 200

        def __init__(self, status):
            self.status = status

        def json(self):
            return {"datatable_bulk_download": {"file": {"status": self.status, "link": "https://example/x.zip",
                                                         "data_snapshot_time": "2018-04-11"}}}

    class S:
        def __init__(self):
            self.calls = 0

        def get(self, url, params=None, timeout=None):
            self.calls += 1
            return R("creating" if self.calls == 1 else "fresh")

    link, snap = aq.export_link(S(), "SECRETKEY", wait=0)
    assert link == "https://example/x.zip" and snap == "2018-04-11"
    csv = aq.ROOT / "data" / "wiki_test_tmp.csv"
    csv.parent.mkdir(parents=True, exist_ok=True)
    csv.write_text("ticker,date\nA,2010-01-04\n")
    try:
        m = aq.write_manifest(csv, snap, out=tmp_path / "m.json")
    finally:
        csv.unlink()
    text = (tmp_path / "m.json").read_text()
    assert m["row_count"] == 1 and "SECRETKEY" not in text and "api_key=" not in text
