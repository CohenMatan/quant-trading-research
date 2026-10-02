"""D114 history-only warm-up (owner 2026-10-02): data seen between warmup_start (>= 2008-07-01) and the official
start may initialise state only. Proven here: no close hook (no decisions), no orders and no equity record before
the official start; the reported equity therefore starts at the official start with the initial cash; integrity
checks fail any run whose equity or fills precede the start; config validation and generated parameters."""
import sys
import types
from datetime import date, datetime

import pandas as pd
import pytest

from qresearch import experiment, integrity
from conftest import ROOT
from test_commission import _load_harness


# ---------------------------------------------------------------- date logic (pure)
def test_warmup_bounds(monkeypatch):
    h = _load_harness(monkeypatch)
    assert h.warmup_bounds({"start": "2010-01-04"}) == (datetime(2010, 1, 4), datetime(2010, 1, 4))
    assert h.warmup_bounds({"start": "2010-01-04", "warmup_start": "2008-07-01"}) == \
        (datetime(2008, 7, 1), datetime(2010, 1, 4))
    for bad in ("2008-06-30", "2010-01-04", "2011-01-03"):
        with pytest.raises(Exception, match="warm-up"):
            h.warmup_bounds({"start": "2010-01-04", "warmup_start": bad})
    off = datetime(2010, 1, 4)
    assert h.in_warmup(date(2010, 1, 1), off) and not h.in_warmup(date(2010, 1, 4), off)


# ---------------------------------------------------------------- harness behaviour across the official start
class _Coll(dict):
    def items(self):
        return list(super().items())


def _data():
    bars = types.SimpleNamespace(count=1, items=lambda: [], contains_key=lambda s: False)
    return types.SimpleNamespace(splits=_Coll(), dividends=_Coll(), delistings=_Coll(), bars=bars)


def _algo(h, official):
    a = object.__new__(h.QRAlgorithm)
    a.qr_official_start = official
    a.qr_sec = None
    a._qr_last_plot = None
    a._qr_stats = {}
    a._qr_in_close = False
    calls = {"close": [], "record": [], "submit": []}
    a._qr_track_real_bars = lambda data, today: None
    a._qr_check_stale = lambda today: None
    a._qr_check_windows = lambda: None
    a._qr_resubmit_cancelled = lambda: None
    a.qr_on_close = lambda data: calls["close"].append(a.time.date())
    a._qr_record = lambda today: calls["record"].append(today)
    a.market_on_open_order = lambda *x, **k: calls["submit"].append(a.time.date())
    return a, calls


def test_no_decision_no_record_before_official_start(monkeypatch):
    h = _load_harness(monkeypatch)
    a, calls = _algo(h, datetime(2010, 1, 4))
    days = [datetime(2008, 7, 1, 16), datetime(2009, 12, 31, 16), datetime(2010, 1, 4, 16), datetime(2010, 1, 5, 16)]
    for t in days:
        a.time = t
        h.QRAlgorithm.on_data(a, _data())
    assert calls["close"] == [date(2010, 1, 4), date(2010, 1, 5)]       # strategy decisions only from the start
    assert calls["record"] == [date(2010, 1, 4), date(2010, 1, 5)]      # equity/cash rows only from the start
    assert a._qr_stats["warmup_days"] == 2


def test_orders_are_impossible_during_warmup(monkeypatch):
    h = _load_harness(monkeypatch)
    a, calls = _algo(h, datetime(2010, 1, 4))
    a.time = datetime(2009, 6, 1, 16)
    a._qr_in_close = True                       # even if a strategy reached the order path during warm-up
    with pytest.raises(Exception, match="warm-up guard"):
        h.QRAlgorithm.qr_rebalance(a, {})
    with pytest.raises(Exception, match="warm-up guard"):
        h.QRAlgorithm._qr_submit(a, "SYM", 10, "x|sig=2009-06-01")
    assert calls["submit"] == []


def test_harness_source_orders_the_guards():
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    body = src[src.index("    def on_data(self, data):"):src.index("    # ================================================================ D059")]
    guard = body.index("if in_warmup(today, self.qr_official_start):")
    assert guard < body.index("self.qr_on_close(data)") and guard < body.index("self._qr_record(today)")
    assert src.count('raise Exception("QR warm-up guard') == 2                # qr_rebalance and _qr_submit
    sel = src[src.index("    def _qr_select(self, fundamental):"):src.index("    def on_securities_changed")]
    assert sel.index("if in_warmup(today, self.qr_official_start):") < sel.index('s["elig_min"]')


# ---------------------------------------------------------------- reported performance starts at the official start
def _eq(start, n, first=100000.0):
    d = pd.bdate_range(start, periods=n).strftime("%Y-%m-%d")
    return pd.DataFrame(dict(date=d, equity=[first] + [first * 1.01] * (n - 1), cash=[first] * n, npos=0, nelig=0))


def _chk(c, name):
    return next(x for x in c if x["check"] == name)


EMPTY = pd.DataFrame(columns=["order_id", "symbol_id", "symbol", "date", "quantity", "price", "fee", "tag"])


def test_integrity_rejects_equity_or_fills_before_the_official_start():
    s = dict(days=5, timing_violations=0, negative_qty=0, invalid=0, warmup_days=380)
    c = integrity.check_all(_eq("2009-12-28", 5), EMPTY, s, "2010-01-04", "2021-12-31", initial_cash=100000.0)
    assert not _chk(c, "equity_within_dates")["ok"]
    fills = pd.DataFrame(dict(order_id=[1], symbol_id=["A"], symbol=["A"], date=["2009-11-02"], quantity=[1.0],
                              price=[1.0], fee=[7.0], tag=["x|sig=2009-10-30"]))
    c = integrity.check_all(_eq("2010-01-04", 5), fills, s, "2010-01-04", "2021-12-31", initial_cash=100000.0)
    assert not _chk(c, "fills_within_dates")["ok"]


def test_integrity_requires_untouched_account_at_the_start():
    s = dict(days=5, timing_violations=0, negative_qty=0, invalid=0, warmup_days=380)
    ok = integrity.check_all(_eq("2010-01-04", 5), EMPTY, s, "2010-01-04", "2021-12-31", initial_cash=100000.0)
    assert _chk(ok, "warmup_left_account_untouched")["ok"]
    bad = integrity.check_all(_eq("2010-01-04", 5, first=101234.0), EMPTY, s, "2010-01-04", "2021-12-31",
                              initial_cash=100000.0)
    assert not _chk(bad, "warmup_left_account_untouched")["ok"]
    assert integrity.status_from(bad) == "integrity_failed"


def test_tradeable_dates_exclude_warmup_sessions():
    assert integrity.official_tradeable_dates(3400, {"warmup_days": 380}) == 3020
    assert integrity.official_tradeable_dates(3020, {}) == 3020
    assert integrity.official_tradeable_dates(None, {"warmup_days": 1}) is None


# ---------------------------------------------------------------- configs and generated parameters
def _cfg(**k):
    import json
    c = json.loads((ROOT / "experiments/E976-04/config.json").read_text())
    c.update(start="2010-01-04", **k)
    c.pop("warmup_start", None) if "warmup_start" not in k else None
    return c


def test_config_validation():
    experiment.validate(_cfg(warmup_start="2008-07-01"))
    for bad in ("2008-06-30", "2010-01-04", "not-a-date"):
        with pytest.raises(experiment.ConfigError):
            experiment.validate(_cfg(warmup_start=bad))


def test_generated_params_carry_warmup_only_when_set():
    assert "warmup_start" in experiment.lean_params(_cfg(warmup_start="2008-07-01"), False)
    assert "warmup_start" not in experiment.lean_params(_cfg(), False)
