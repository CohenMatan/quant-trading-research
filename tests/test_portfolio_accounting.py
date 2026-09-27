import pandas as pd
import pytest

from qresearch.trades import FILL_COLUMNS, LongOnlyViolation, build_trades
from conftest import experiment_result


def fills(rows):
    return pd.DataFrame([dict(zip(FILL_COLUMNS, r)) for r in rows], columns=FILL_COLUMNS)


def test_simple_round_trip():
    f = fills([(1, "A1", "A", "2001-01-02", 100, 10.0, 1.0, "x|sig=2001-01-01"),
               (2, "A1", "A", "2001-01-09", -100, 11.0, 1.0, "exit|sig=2001-01-08")])
    t = build_trades(f)
    assert len(t) == 1
    r = t.iloc[0]
    assert r.pnl == pytest.approx(1100 - 1000 - 2) and r.ret == pytest.approx(98 / 1000)
    assert (r.entry_date, r.exit_date, r.exit_tag, r.status) == ("2001-01-02", "2001-01-09", "exit", "closed")


def test_scale_in_partial_exit_and_forced_close():
    f = fills([(1, "A1", "A", "2001-01-02", 100, 10.0, 1.0, "e|sig=2001-01-01"),
               (2, "A1", "A", "2001-01-03", 50, 12.0, 1.0, "e|sig=2001-01-02"),
               (3, "A1", "A", "2001-01-04", -100, 13.0, 1.0, "trim|sig=2001-01-03"),
               (4, "A1", "A", "2001-01-05", -50, 2.0, 0.0, "Liquidated due to delisting")])
    t = build_trades(f)
    assert len(t) == 1 and t.iloc[0].n_fills == 4 and t.iloc[0].exit_tag == "forced"
    assert t.iloc[0].pnl == pytest.approx(1300 + 100 - 1000 - 600 - 3)


def test_split_changes_quantity_not_dollar_pnl():
    f = fills([(1, "A1", "A", "2005-02-01", 100, 80.0, 1.0, "e|sig=2005-01-31"),
               (2, "A1", "A", "2005-03-01", -200, 42.0, 1.0, "x|sig=2005-02-28")])
    splits = pd.DataFrame([dict(symbol_id="A1", date="2005-02-28", factor=0.4999986)])
    t = build_trades(f, splits)
    assert len(t) == 1 and t.iloc[0].status == "closed"
    assert t.iloc[0].pnl == pytest.approx(8400 - 8000 - 2)


def test_split_without_event_would_look_short():
    f = fills([(1, "A1", "A", "2005-02-01", 100, 80.0, 1.0, "e|sig=2005-01-31"),
               (2, "A1", "A", "2005-03-01", -200, 42.0, 1.0, "x|sig=2005-02-28")])
    with pytest.raises(LongOnlyViolation):
        build_trades(f)


def test_reverse_split_and_open_trade():
    f = fills([(1, "G1", "GE", "2021-07-01", 800, 13.0, 4.0, "e|sig=2021-06-30"),
               (2, "B1", "B", "2021-07-01", 10, 50.0, 1.0, "e|sig=2021-06-30")])
    splits = pd.DataFrame([dict(symbol_id="G1", date="2021-08-02", factor=8.0)])
    t = build_trades(f, splits)
    assert set(t.status) == {"open"} and len(t) == 2


def test_sell_without_position_raises():
    with pytest.raises(LongOnlyViolation):
        build_trades(fills([(1, "A1", "A", "2001-01-02", -5, 10.0, 1.0, "x|sig=2001-01-01")]))


def test_canary_local_accounting_matches_engine():
    """Cross-check on a real run: local net profit and fees equal QuantConnect's own figures."""
    r = experiment_result("E950-01")
    qc = r["qc_statistics"]
    m = r["metrics"]
    net = float(qc["Net Profit"].rstrip("%")) / 100
    assert m["total_return"] == pytest.approx(net, abs=5e-5)
