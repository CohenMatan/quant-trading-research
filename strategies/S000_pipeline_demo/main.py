# S000 — PIPELINE DEMONSTRATION ONLY (not a research strategy; no hypothesis).
# Each close: among the 300 most liquid eligible stocks, buy the ones with the lowest 5-day
# return until 10 slots are filled (weight ~9.8% each); sell each position after it has been
# held for 5 closes. Exercises the universe, adjusted windows, signals module, MOO execution,
# position sizing, exits and delistings end to end.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import select_entries


class PipelineDemo(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 6

    def qr_initialize(self):
        p = self.qr_params
        self.lookback = int(p.get("lookback", 5))
        self.hold = int(p.get("hold_days", 5))
        self.slots = int(p.get("slots", 10))
        self.pool = int(p.get("pool", 300))
        self.weight = float(p.get("weight", 0.098))
        self.age = {}

    def qr_on_close(self, data):
        held = [kv.key for kv in self.portfolio if kv.value.invested]
        pending = {t.symbol for t in self.transactions.get_open_order_tickets()}
        targets = {}
        for s in held:
            self.age[s] = self.age.get(s, 0) + 1
            if self.age[s] >= self.hold and s not in pending:
                targets[s] = 0.0
        for s in list(self.age):
            if s not in held and s not in pending:
                del self.age[s]
        n_free = self.slots - (len(held) - len(targets)) - len([s for s in pending if s not in held])
        eligible = set(self.qr_eligible)
        windows = {str(s.id): self.qr_close[s] for s in eligible
                   if s in self.qr_close and data.bars.contains_key(s)}
        liquidity = {str(s.id): self.qr_eligible_info[s][1] for s in eligible if s in self.qr_eligible_info}
        by_id = {str(s.id): s for s in eligible}
        exclude = {str(s.id) for s in held} | {str(s.id) for s in pending}
        for k in select_entries(windows, liquidity, exclude, n_free, self.lookback, self.pool):
            targets[by_id[k]] = self.weight
            self.age[by_id[k]] = 0
        if targets:
            self.qr_rebalance(targets, tag="demo")
