# X952 v1.1 — corporate-action and delisting check (infrastructure, not research).
# Buys small positions in names with known events and verifies LEAN's handling:
#   splits:     AAPL 2:1 2005-02-28, AAPL 7:1 2014-06-09 → quantity × 1/factor, equity continuous
#   dividends:  KO, XOM quarterly → cash rises by quantity × distribution on the event
#   delistings: ENE (2001-02), WCOM (2002), BSC (acquired 2008), LEH (2008) → position liquidated
from AlgorithmImports import *
from qr_harness import QRAlgorithm
import json

BUYS = {  # ticker: first signal date (YYYY-MM-DD) on/after which a 4% position is bought
    "AAPL": "2004-06-01", "KO": "2004-06-01", "XOM": "2004-06-01",
    "ENE": "2001-06-01", "WCOM": "2002-01-02", "BSC": "2008-01-02", "LEH": "2008-06-02",
}


class CorporateActions(QRAlgorithm):
    FIXED_TICKERS = tuple(BUYS)

    def qr_initialize(self):
        self.bought = set()
        self.prev = None    # (cash, {symbol: qty}, total value) at last close
        self.checks = {"splits": [], "dividends_ok": 0, "dividends_bad": 0, "delist_fills": []}

    def on_data(self, data):
        if self.prev is not None and (data.splits.count or data.dividends.count):
            cash0, qty0, val0 = self.prev
            for sym, sp in data.splits.items():
                if sp.type == SplitType.SPLIT_OCCURRED and qty0.get(sym, 0):
                    q1 = float(self.portfolio[sym].quantity)
                    self.checks["splits"].append(dict(sym=sym.value, day=f"{self.time:%Y-%m-%d}",
                        factor=float(sp.split_factor), qty_before=qty0[sym], qty_after=q1,
                        value_before=val0, value_after=float(self.portfolio.total_portfolio_value)))
            # several dividends can arrive in the same slice: compare their total with the cash change
            expected = sum(qty0.get(sym, 0) * float(dv.distribution) for sym, dv in data.dividends.items())
            if expected:
                got = float(self.portfolio.cash) - cash0
                ok = abs(got - expected) <= 0.01 + 1e-6 * abs(expected)
                self.checks["dividends_ok" if ok else "dividends_bad"] += 1
                if not ok:
                    self._qr_log(f"QRCA_DIV_BAD|{self.time:%Y-%m-%d}|exp={expected:.4f}|got={got:.4f}")
        super().on_data(data)

    def qr_on_close(self, data):
        day = self.time.strftime("%Y-%m-%d")
        targets = {}
        for t, d in BUYS.items():
            sym = self.qr_fixed[t]
            if t not in self.bought and day >= d and data.bars.contains_key(sym):
                targets[sym] = 0.04
                self.bought.add(t)
        if targets:
            self.qr_rebalance(targets, tag="ca_buy")
        self.prev = (float(self.portfolio.cash),
                     {kv.key: float(kv.value.quantity) for kv in self.portfolio if kv.value.invested},
                     float(self.portfolio.total_portfolio_value))

    def qr_on_fill(self, ev):
        if self._qr_sig.get(ev.order_id) is None:
            self.checks["delist_fills"].append(dict(sym=ev.symbol.value, day=f"{self.time:%Y-%m-%d}",
                qty=float(ev.fill_quantity), price=float(ev.fill_price)))

    def qr_on_end(self):
        self.log("QRCA|" + json.dumps(self.checks, sort_keys=True))
