# S008 — residual (idiosyncratic) relative strength (H008). Variations differ only in params.
# Monthly ranking at the first close of each month; free slots are refilled daily from the current
# month's ranking (C02 plan, approved). Orders execute at the next open.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import monthly_targets, residual_score


class ResidualRS(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 400

    def qr_initialize(self):
        self.last_month = None
        self.ranked = []

    def qr_on_close(self, data):
        p = self.qr_params
        m = (self.time.year, self.time.month)
        held = [kv.key for kv in self.portfolio if kv.value.invested]
        if m != self.last_month:
            self.last_month = m
            spy = self.qr_close.get(self.spy)
            scores = {}
            if spy is not None:
                for s in self.qr_eligible:
                    c = self.qr_close.get(s)
                    if c is None or not data.bars.contains_key(s):
                        continue
                    v = residual_score(c, spy, int(p["window"]), int(p["skip"]), bool(p["scaled"]))
                    if v is not None:
                        scores[str(s.id)] = (v, s)
            self.ranked = [scores[k][1] for k in sorted(scores, key=lambda k: (-scores[k][0], k))]
            exits, cands = monthly_targets(self.ranked, held, int(p["slots"]), int(p["keep"]))
        else:
            exits, cands = [], self.ranked          # daily refill from the current month's ranking
        cands = [s for s in cands if s in self.qr_close]     # highest-ranked not held first
        self.qr_event_step(exits, cands, int(p["slots"]), tag="s008")
