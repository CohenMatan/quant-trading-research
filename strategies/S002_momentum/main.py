# S002 — 12-1 / 6-1 momentum, top 15 (H002). Variations differ only in params.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import is_rebalance_month, sma, top_by_momentum


class Momentum(QRAlgorithm):
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
        if not is_rebalance_month(m[0], m[1], int(p.get("every_months", 1))):
            return
        if p.get("regime_filter"):
            spy = self.qr_close.get(self.spy)
            s = sma(spy, 200) if spy is not None else None
            if s is None or spy[-1] <= s:
                self.qr_rebalance({}, tag="s002_regime_off", liquidate_others=True)
                return
        by_id, windows = {}, {}
        for s in self.qr_eligible:
            c = self.qr_close.get(s)
            if c is not None and data.bars.contains_key(s):
                by_id[str(s.id)] = s
                windows[str(s.id)] = c
        top = top_by_momentum(windows, int(p["lookback"]), int(p["skip"]), int(p["slots"]))
        self.qr_rebalance({by_id[k]: self.qr_slot_weight(int(p["slots"])) for k in top}, tag="s002",
                          liquidate_others=True, band=float(p.get("band", 0.25)))
