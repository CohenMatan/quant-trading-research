import gzip

import pandas as pd
import pytest

from qresearch import integrity, results
from conftest import ROOT, latest_completed

# order payload in the format returned by backtests/orders/read (trimmed)
ORDER = {"id": 7, "symbol": {"value": "SPY", "id": "SPY R735QTJ8XC9X"}, "tag": "e|sig=1999-01-04",
         "events": [{"status": "submitted", "time": 915483600.0, "fillQuantity": 0.0},
                    {"status": "filled", "time": 915570000.0, "fillPrice": 122.94, "fillQuantity": 100.0,
                     "orderFeeAmount": 1.0}]}


def test_parse_fills_uses_new_york_dates():
    f = results.parse_fills([ORDER])
    assert f.to_dict("records") == [dict(order_id=7, symbol_id="SPY R735QTJ8XC9X", symbol="SPY",
                                         date="1999-01-05", quantity=100.0, price=122.94, fee=1.0,
                                         tag="e|sig=1999-01-04")]


def test_parse_equity_one_row_per_day():
    # 21:00Z = 16:00 New York (EST); 18:00Z = 13:00 early close
    series = {"equity": [[915483600, 100.0], [915570000, 101.0], [915570000, 101.5]],
              "cash": [[915483600, 100.0], [915570000, 0.0]], "npos": [[915570000, 1]], "nelig": []}
    df = results.parse_equity(series)
    assert list(df.date) == ["1999-01-04", "1999-01-05"]
    assert list(df.equity) == [100.0, 101.5] and list(df.npos) == [0, 1]


def test_parse_logs():
    lines = ["2005-02-28 00:00:00 QRSPLIT|AAPL R735QTJ8XC9X|2005-02-28|0.4999986000",
             '2005-03-01 16:00:00 QRSUMMARY|{"days": 3}', "2005-03-01 16:00:00 unrelated", "x QRCANARY|{}"]
    splits, summary, other = results.parse_logs(lines)
    assert splits.iloc[0].factor == pytest.approx(0.4999986) and summary == {"days": 3}
    assert other == ["QRCANARY|{}"]


def _eq(dates, equity, cash):
    return pd.DataFrame(dict(date=dates, equity=equity, cash=cash, npos=0, nelig=0))


@pytest.mark.parametrize("dates,equity,cash,bad", [
    (["2001-01-03", "2001-01-02"], [1.0, 1.0], [1.0, 1.0], "equity_dates_increasing"),
    (["2001-01-02", "2001-01-02"], [1.0, 1.0], [1.0, 1.0], "equity_dates_increasing"),
    (["2001-01-02", "2001-01-03"], [1.0, -1.0], [1.0, 1.0], "equity_positive"),
    (["2001-01-02", "2001-01-03"], [1.0, 1.0], [1.0, -0.5], "no_leverage"),
    (["2000-12-29", "2001-01-03"], [1.0, 1.0], [1.0, 1.0], "equity_within_dates"),
])
def test_integrity_detects_bad_equity(dates, equity, cash, bad):
    summary = dict(days=2, timing_violations=0, negative_qty=0, invalid=0)
    fills = results.parse_fills([])
    c = {x["check"]: x for x in integrity.check_all(_eq(dates, equity, cash), fills, summary, "2001-01-01", "2001-12-31")}
    assert not c[bad]["ok"]


def test_integrity_detects_incomplete_chart():
    summary = dict(days=5, timing_violations=0, negative_qty=0, invalid=0)
    c = {x["check"]: x for x in integrity.check_all(_eq(["2001-01-02"], [1.0], [1.0]), results.parse_fills([]),
                                                     summary, "2001-01-01", "2001-12-31")}
    assert not c["equity_complete"]["ok"]


def test_committed_results_are_self_consistent():
    """Every committed experiment: stored files hash to the recorded hashes and pass integrity."""
    found = 0
    for rp in ROOT.glob("experiments/E*/result.json"):
        import json
        r = json.loads(rp.read_text())
        if not r["status"].startswith("completed"):
            continue   # failed runs stay on record; they are not used
        found += 1
        for k in ("equity", "fills", "trades"):
            text = gzip.decompress((rp.parent / f"{k}.csv.gz").read_bytes()).decode()
            assert results.sha256_text(text) == r["hashes"][f"{k}_sha256"], (rp, k)
        assert all(c["ok"] or c["level"] == "warn" for c in r["integrity"]), rp
    if not found:
        pytest.skip("no experiments run yet")


def test_canary_fees_match_engine():
    eid, r = latest_completed("X950")
    f = results.read_csv_gz(ROOT / "experiments" / eid / "fills.csv.gz")
    qc_fees = float(r["qc_statistics"]["Total Fees"].replace("$", "").replace(",", ""))
    assert f["fee"].sum() == pytest.approx(qc_fees, abs=0.01)
