"""D063: a symbol picked at the close and dropped from the universe overnight kept no price window,
so once its buy filled no exit rule could see it (S001: 7-15 of 15 slots stranded for years)."""
import types
from collections import deque

import pandas as pd
import pytest

from test_stale_holdings import Holding, Portfolio, Sym


@pytest.fixture
def algo(monkeypatch):
    from test_commission import _load_harness
    h = _load_harness(monkeypatch)
    for name in ("Resolution", "DataNormalizationMode"):
        setattr(h, name, types.SimpleNamespace(DAILY="d", SCALED_RAW="s"))
    a = object.__new__(h.QRAlgorithm)
    a.WINDOW_BARS = 3
    a.qr_close, a.qr_volume, a._qr_last_bar = {}, {}, {}
    a.portfolio = Portfolio(1000.0)
    a.open_orders = {}
    a.transactions = types.SimpleNamespace(get_open_order_tickets=lambda s: a.open_orders.get(s, []))
    a._qr_stats = {"max_subscribed": 0, "windows_restored": 0}
    a.securities = []
    a.logged = []
    a._qr_log = a.logged.append
    a.time = pd.Timestamp("2010-06-01")

    def history(symbols, n, res, data_normalization_mode=None):
        idx = pd.MultiIndex.from_tuples([(s, pd.Timestamp("2010-05-27") + pd.Timedelta(days=i))
                                         for s in symbols for i in range(n)])
        return pd.DataFrame({"close": [10.0 + i for _ in symbols for i in range(n)],
                             "volume": [1e6] * (n * len(symbols))}, index=idx)
    a.history = history
    return a


def _changes(added=(), removed=()):
    return types.SimpleNamespace(added_securities=[types.SimpleNamespace(symbol=s) for s in added],
                                 removed_securities=[types.SimpleNamespace(symbol=s) for s in removed])


def test_window_kept_while_a_buy_is_pending(algo):
    ptc = Sym("PMTC", "PMTC R735QTJ8XC9X")
    algo.portfolio[ptc] = Holding(0.0)
    algo.qr_close[ptc] = deque([1.0, 2.0, 3.0], maxlen=3)
    algo.qr_volume[ptc] = deque([1.0] * 3, maxlen=3)
    algo.open_orders[ptc] = ["buy 367 at the next open"]
    algo.on_securities_changed(_changes(removed=[ptc]))
    assert ptc in algo.qr_close                                   # kept: the buy is still pending
    algo.open_orders[ptc] = []
    algo.on_securities_changed(_changes(removed=[ptc]))
    assert ptc not in algo.qr_close                               # no order, not held: dropped as before


def test_held_symbol_without_window_is_restored_loudly(algo):
    dar = Sym("DAR", "DAR R735QTJ8XC9X")
    algo.portfolio[dar] = Holding(337.0)
    algo._qr_check_windows()
    assert list(algo.qr_close[dar]) == [10.0, 11.0, 12.0]
    assert algo._qr_stats["windows_restored"] == 1 and algo.logged[0].startswith("QRWINDOW|DAR")
    algo._qr_check_windows()
    assert algo._qr_stats["windows_restored"] == 1                # nothing missing any more


def test_daily_order_of_checks():
    from conftest import ROOT
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert "self._qr_check_stale(today)\n            self._qr_check_windows()\n            self._qr_resubmit_cancelled()" in src
