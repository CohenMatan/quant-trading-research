# S008 — residual (market-adjusted) relative strength (H008). Variations differ only in params.
# Score: Blitz-Huij-Martens residuals, alpha/beta on SPY over 36 months (D074 option A); stocks
# without 36 months of history are unscorable. At the 2010 start the 36-month look-back reads
# 2007-2009 prices as signal warm-up only (owner approval 2026-09-29). Long-only, not beta-hedged.
# Monthly ranking at the first close of each month; free slots are refilled daily from the current
# month's ranking (C02 plan, approved). Orders execute at the next open.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import monthly_targets, residual_score


class ResidualRS(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 780           # >= 758 closes: 756 estimation returns + the return of T

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
