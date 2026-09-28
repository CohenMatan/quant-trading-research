# S005 — 15 lowest-volatility names, monthly (H005). Variations differ only in params.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import lowest_vol


class LowVol(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 260

    def qr_initialize(self):
        self.p = self.qr_params
        self.last_month = None

    def qr_on_close(self, data):
        p = self.p
        m = (self.time.year, self.time.month)
        if m == self.last_month:
            return
        self.last_month = m
        by_id, windows = {}, {}
        for s in self.qr_eligible:
            c = self.qr_close.get(s)
            if c is not None and data.bars.contains_key(s):
                by_id[str(s.id)] = s
                windows[str(s.id)] = c
        top = lowest_vol(windows, int(p["vol_days"]), int(p["slots"]), bool(p.get("require_positive_mom")))
        self.qr_rebalance({by_id[k]: self.qr_slot_weight(int(p["slots"])) for k in top}, tag="s005",
                          liquidate_others=True, band=float(p.get("band", 0.25)))
