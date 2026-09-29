"""D059: holdings that stop receiving real price data (acquired without a delisting event in the
data, e.g. OAK 2019-09-30 and BPL 2019-11-01) are detected, taken out at their last real close,
mirrored locally, and runs with orders that can never fill fail loudly."""
import types
from datetime import date, timedelta

import pandas as pd
import pytest

from qresearch import integrity, results
from qresearch.trades import FILL_COLUMNS, build_trades


class Sym:
    def __init__(self, value, sid):
        self.value, self.id = value, sid

    def __repr__(self):
        return self.value


class Bars(dict):
    def contains_key(self, k):
        return k in self


class Holding:
    def __init__(self, q):
        self.quantity = q

    @property
    def invested(self):
        return self.quantity != 0

    def set_holdings(self, price, qty):
        self.quantity = qty


class Portfolio(dict):
    def __init__(self, cash):
        super().__init__()
        self.cash = cash
        book = self

        class CashBook:
            def add_amount(self, x):
                book.cash += x
        self.cash_book = {"USD": CashBook()}

    def __iter__(self):
        return iter([types.SimpleNamespace(key=k, value=v) for k, v in self.items()])


@pytest.fixture
def algo(monkeypatch):
    from test_commission import _load_harness
    h = _load_harness(monkeypatch)
    a = object.__new__(h.QRAlgorithm)
    a.spy = Sym("SPY", "SPY R735QTJ8XC9X")
    a.portfolio = Portfolio(cash=1000.0)
    a.cancelled = []
    a.transactions = types.SimpleNamespace(cancel_open_orders=lambda s: a.cancelled.append(s.value))
    a.logged = []
    a._qr_log = a.logged.append
    a._qr_forced_fee = 7.0
    a._qr_resubmit = {}
    a._qr_stats = {k: 0 for k in ("stale_exits", "stale_unresolved")}
    a._qr_session, a._qr_session_day = 0, None
    a._qr_real_session, a._qr_real_close, a._qr_real_date = {}, {}, {}
    a._qr_terminated = set()
    a._qr_entry = {}
    a.h = h
    return a


def _days(start, n):
    d, out = date.fromisoformat(start), []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def _run(algo, days, bars_for):
    """Feed one trading-day slice per day, then run the stale check, as on_data does."""
    for d in days:
        bars = Bars({algo.spy: types.SimpleNamespace(is_fill_forward=False, close=300.0)})
        bars.update(bars_for(d))
        algo._qr_track_real_bars(types.SimpleNamespace(bars=bars), d)
        algo._qr_check_stale(d)


def test_oak_filled_forward_after_acquisition_is_taken_out_at_last_real_close(algo):
    oak = Sym("OAK", "OAK V5P2MATBV339")
    algo.portfolio[oak] = Holding(125.0)
    last_real = date(2019, 9, 30)
    days = _days("2019-09-23", 30)

    def bars(d):   # real bars until the acquisition closes, filled-forward bars afterwards
        return {oak: types.SimpleNamespace(is_fill_forward=d > last_real, close=49.2 if d <= last_real else 49.2)}
    _run(algo, days, bars)
    line = [x for x in algo.logged if x.startswith("QRSTALE|")]
    assert len(line) == 1 and algo.cancelled == ["OAK"]
    _, sid, tic, lr, exit_day, qty, price, fee = line[0].split("|")
    assert (sid, tic, lr, float(qty), float(price), float(fee)) == ("OAK V5P2MATBV339", "OAK", "2019-09-30", 125.0, 49.2, 7.0)
    sessions_after = [d for d in days if d > last_real]
    assert exit_day == str(sessions_after[10])            # 11th session without a real bar
    assert algo.portfolio[oak].quantity == 0
    assert algo.portfolio.cash == pytest.approx(1000.0 + 125 * 49.2 - 7.0)
    assert algo._qr_stats["stale_exits"] == 1


def test_bpl_with_no_bars_at_all_is_detected(algo):
    bpl = Sym("BPL", "BPL R735QTJ8XC9X")
    algo.portfolio[bpl] = Holding(171.0)
    _run(algo, _days("2019-10-21", 30),
         lambda d: {bpl: types.SimpleNamespace(is_fill_forward=False, close=41.4)} if d <= date(2019, 11, 1) else {})
    assert algo._qr_stats["stale_exits"] == 1 and algo.portfolio[bpl].quantity == 0
    assert "|2019-11-01|" in [x for x in algo.logged if x.startswith("QRSTALE|")][0]


def test_live_holding_and_short_gaps_are_not_terminated(algo):
    ko = Sym("KO", "KO R735QTJ8XC9X")
    halt = Sym("HALT", "HALT X")
    algo.portfolio[ko] = Holding(10.0)
    algo.portfolio[halt] = Holding(10.0)
    days = _days("2020-01-02", 40)
    gap = set(days[5:15])                                  # 10 sessions without data: not yet stale
    _run(algo, days, lambda d: {ko: types.SimpleNamespace(is_fill_forward=False, close=50.0),
                                **({} if d in gap else {halt: types.SimpleNamespace(is_fill_forward=False, close=20.0)})})
    assert algo._qr_stats["stale_exits"] == 0 and not algo.cancelled


def test_unknown_last_price_is_unresolved_not_invented(algo):
    x = Sym("X", "X 1")
    algo.portfolio[x] = Holding(5.0)
    algo._qr_real_session[x] = -20                         # stale, but no real close ever seen
    algo._qr_terminate(x, date(2020, 1, 2))
    assert algo._qr_stats["stale_unresolved"] == 1 and algo.portfolio[x].quantity == 5.0
    assert algo.portfolio.cash == 1000.0


def test_mirror_closes_the_trade_and_reconciles_cash():
    fills = pd.DataFrame([dict(order_id=1, symbol_id="OAK V5P2MATBV339", symbol="OAK", date="2019-07-02",
                               quantity=125.0, price=49.78, fee=7.0, tag="s005|sig=2019-07-01")], columns=FILL_COLUMNS)
    lines = ["QRSTALE|OAK V5P2MATBV339|OAK|2019-09-30|2019-10-15|125.0|49.200000|7.00"]
    out, n = results.apply_stale_exits(fills, lines)
    assert n == 1 and out.iloc[-1]["order_id"] < 0 and out.iloc[-1]["tag"].startswith("stale_exit")
    t = build_trades(out)
    assert (t["status"] == "closed").all()
    assert t["pnl"].iloc[0] == pytest.approx(125 * (49.2 - 49.78) - 14.0)


def test_orders_that_can_never_fill_fail_the_run():
    orders = [dict(id=162, status=1, time="2019-10-01T13:30:00Z", quantity=-125, symbol={"value": "OAK"}),
              dict(id=900, status=1, time="2021-12-30T21:00:00Z", quantity=-10, symbol={"value": "KO"}),   # final day: normal
              dict(id=5, status=3, time="2019-01-02T14:30:00Z", quantity=10, symbol={"value": "PG"})]
    late = results.late_open_orders(orders, "2021-12-31")
    assert [x[0] for x in late] == [162]
    eq = pd.DataFrame({"date": ["2021-12-30", "2021-12-31"], "equity": [1.0, 1.0], "cash": [1.0, 1.0]})
    empty = pd.DataFrame(columns=FILL_COLUMNS)
    chk = {c["check"]: c for c in integrity.check_all(eq, empty, {"days": 2, "fills": 0, "stale_exits": 1,
                                                                  "stale_unresolved": 0, "stale_open_orders": 0},
                                                      "2021-01-01", "2021-12-31", late_open_orders=late)}
    assert not chk["no_stale_open_orders"]["ok"] and chk["no_stale_open_orders"]["level"] == "fail"
    assert not chk["stale_exits"]["ok"] and chk["stale_exits"]["level"] == "warn"   # loud, visible
    chk2 = {c["check"]: c for c in integrity.check_all(eq, empty, {"days": 2, "stale_unresolved": 1},
                                                       "2021-01-01", "2021-12-31")}
    assert not chk2["no_unresolved_stale_holdings"]["ok"]
    assert integrity.status_from(list(chk2.values())) == "integrity_failed"


def test_harness_wiring():
    from conftest import ROOT
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert "self._qr_check_stale(today)\n            self._qr_check_windows()\n            self._qr_resubmit_cancelled()" in src
    assert "STALE_SESSIONS = 10" in src and "ev.symbol in self._qr_terminated" in src
