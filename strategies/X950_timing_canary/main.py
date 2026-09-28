# X950 — execution-timing canary (infrastructure, not research).
# Every 10 trading days it rotates between two fixed baskets, so each rebalance has simultaneous
# sells and buys. The harness checks each fill (strictly after the signal date, price = next open
# ± slippage). This file additionally checks that every fill happens at the FIRST session after its
# signal: when a fill arrives, the last close the algorithm processed must be the signal date.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
import json

BASKET_A = ("AAPL", "XOM", "KO", "GE")      # AAPL splits 2000/2005/2014/2020; GE 1:8 reverse split 2021
BASKET_B = ("MSFT", "JPM", "PFE", "WMT")


class TimingCanary(QRAlgorithm):
    FIXED_TICKERS = BASKET_A + BASKET_B

    def qr_initialize(self):
        self.n_close = 0
        self.last_close_day = None
        self.cstats = {"fills": 0, "not_next_session": 0, "same_day": 0, "rebalances": 0}

    def qr_on_close(self, data):
        self.n_close += 1
        if self.n_close % 10 == 1:
            basket = BASKET_A if (self.n_close // 10) % 2 == 0 else BASKET_B
            w = float(self.qr_params.get("weight", 0.24))
            targets = {self.qr_fixed[t]: w for t in basket}
            self.qr_rebalance(targets, tag="canary", liquidate_others=True)
            self.cstats["rebalances"] += 1
        self.last_close_day = self.time.strftime("%Y-%m-%d")

    def qr_on_fill(self, ev):
        sig = self._qr_sig.get(ev.order_id)
        if sig is None:
            return
        self.cstats["fills"] += 1
        fill_day = self.time.strftime("%Y-%m-%d")
        if fill_day == sig:
            self.cstats["same_day"] += 1
        if self.last_close_day != sig:
            self.cstats["not_next_session"] += 1
            self._qr_log(f"QRCANARY_LATE|{ev.symbol.value}|sig={sig}|last_close={self.last_close_day}|fill={fill_day}")

    def qr_on_end(self):
        self._qr_log("QRCANARY|" + json.dumps(self.cstats, sort_keys=True))
