# S003 — nearest to 52-week high, top 15 (H003). Variations differ only in params.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import top_by_proximity


class High52(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 260

    def qr_initialize(self):
        self.p = self.qr_params
        self.last_month = None
        self.days_since = 10 ** 6

    def qr_on_close(self, data):
        p = self.p
        self.days_since += 1
        if p.get("rebalance") == "days":
            if self.days_since < int(p["every_days"]):
                return
        else:
            m = (self.time.year, self.time.month)
            if m == self.last_month:
                return
            self.last_month = m
        self.days_since = 0
        by_id, windows = {}, {}
        for s in self.qr_eligible:
            c = self.qr_close.get(s)
            if c is not None and data.bars.contains_key(s):
                by_id[str(s.id)] = s
                windows[str(s.id)] = c
        top = top_by_proximity(windows, int(p["slots"]), bool(p.get("require_positive_mom")))
        self.qr_rebalance({by_id[k]: self.qr_slot_weight(int(p["slots"])) for k in top}, tag="s003",
                          liquidate_others=True, band=float(p.get("band", 0.25)))
