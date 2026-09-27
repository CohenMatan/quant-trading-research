import re

import pandas as pd

from qresearch import integrity
from conftest import ROOT, experiment_result

ORDER_APIS = ("market_order(", "limit_order(", "stop_market_order(", "set_holdings(", "liquidate(",
              "market_on_close_order(", "stop_limit_order(", "limit_if_touched_order(")


def _eq(n=3):
    d = pd.bdate_range("2001-01-01", periods=n).strftime("%Y-%m-%d")
    return pd.DataFrame(dict(date=d, equity=[100.0] * n, cash=[100.0] * n, npos=0, nelig=0))


def _fills(day, sig):
    return pd.DataFrame(dict(order_id=[1], symbol_id=["A"], symbol=["A"], date=[day], quantity=[1.0],
                             price=[1.0], fee=[1.0], tag=[f"x|sig={sig}"]))


SUMMARY = dict(days=3, timing_violations=0, negative_qty=0, invalid=0)


def _check(checks, name):
    return next(c for c in checks if c["check"] == name)


def test_fill_on_signal_day_is_flagged():
    c = integrity.check_all(_eq(), _fills("2001-01-02", "2001-01-02"), SUMMARY, "2001-01-01", "2001-01-03")
    assert not _check(c, "fills_after_signal_date")["ok"]
    assert integrity.status_from(c) == "integrity_failed"


def test_fill_next_day_passes():
    c = integrity.check_all(_eq(), _fills("2001-01-02", "2001-01-01"), SUMMARY, "2001-01-01", "2001-01-03")
    assert _check(c, "fills_after_signal_date")["ok"]
    assert integrity.status_from(c) == "completed"


def test_harness_places_only_market_on_open_orders():
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert src.count("self.market_on_open_order(") == 1
    for api in ORDER_APIS:
        assert f"self.{api}" not in src, api
    assert 'raise Exception("QR timing guard' in src


def test_strategies_never_place_orders_directly():
    for main in ROOT.glob("strategies/*/main.py"):
        src = main.read_text()
        for api in ORDER_APIS + ("market_on_open_order(",):
            assert not re.search(r"\bself\." + re.escape(api), src), f"{main}: {api}"


def test_canary_run_has_no_timing_violations():
    r = experiment_result("E950-01")
    assert r["status"] == "completed"
    s = r["harness_summary"]
    assert s["timing_violations"] == 0 and s["fills"] > 1000 and s["max_fill_dev"] < 1e-9
    line = next(m for m in r["harness_messages"] if m.startswith("QRCANARY|"))
    assert '"not_next_session": 0' in line and '"same_day": 0' in line
