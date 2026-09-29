# S004 — pullbacks in momentum leaders, time exit (H004). Variations differ only in params.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import leaders, pullback_entries, sma


class MomentumPullback(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 210            # >= 201 bars: the SPY 200-day regime filter needs them (E004-04 bug)

    def qr_initialize(self):
        self.p = self.qr_params
        self.age = {}

    def qr_on_close(self, data):
        p = self.p
        held = [kv.key for kv in self.portfolio if kv.value.invested]
        pending = {t.symbol for t in self.transactions.get_open_order_tickets()}
        targets = {}
        for s in held:
            self.age[s] = self.age.get(s, 0) + 1
            if s not in pending and self.age[s] >= int(p["hold_days"]):
                targets[s] = 0.0
        for s in list(self.age):
            if s not in held and s not in pending:
                del self.age[s]
        if p.get("regime_filter"):
            spy = self.qr_close.get(self.spy)
            m = sma(spy, 200) if spy is not None else None
            if m is None or spy[-1] <= m:
                if targets:
                    self.qr_rebalance(targets, tag="s004")
                return
        by_id, windows = {}, {}
        for s in self.qr_eligible:
            c = self.qr_close.get(s)
            if c is not None and data.bars.contains_key(s):
                by_id[str(s.id)] = s
                windows[str(s.id)] = c
        busy = {str(s.id) for s in set(held) | pending}
        for k in pullback_entries(windows, leaders(windows, float(p["leader_frac"])), float(p["drop"]),
                                  busy, int(p["slots"])):
            s = by_id[k]
            targets[s] = self.qr_slot_weight(int(p["slots"]))
            self.age[s] = 0
        if targets:
            self.qr_rebalance(targets, tag="s004")
