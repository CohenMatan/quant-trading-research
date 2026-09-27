# B900 — SPY buy-and-hold benchmark, dividends reinvested (total return proxy).
# Buys SPY on the first close (MOO next open) and, on the first close of each month,
# reinvests accumulated cash (dividends) back up to the target weight.
from AlgorithmImports import *
from qr_harness import QRAlgorithm


class SpyBuyHold(QRAlgorithm):
    def qr_initialize(self):
        self.last_month = None

    def qr_on_close(self, data):
        m = (self.time.year, self.time.month)
        if m == self.last_month:
            return
        self.last_month = m
        w = float(self.qr_params.get("weight", 0.98))
        self.qr_rebalance({self.spy: w}, tag="spy_bh")
