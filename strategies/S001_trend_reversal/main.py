# S001 — trend-filtered short-term reversal (H001). Variations differ only in params.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import entry_score, exit_signal, rank_entries, sma


class TrendReversal(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 210

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
            c = self.qr_close.get(s)
            if s not in pending and c is not None and exit_signal(c, self.age[s], p):
                targets[s] = 0.0
        for s in list(self.age):
            if s not in held and s not in pending:
                del self.age[s]
        regime_ok = True
        if p.get("regime_filter"):
            spy = self.qr_close.get(self.spy)
            m = sma(spy, 200) if spy is not None else None
            regime_ok = m is not None and spy[-1] > m
        if regime_ok:
            busy = set(held) | pending
            scores = {}
            for s in self.qr_eligible:
                if s in busy or not data.bars.contains_key(s):
                    continue
                c = self.qr_close.get(s)
                if c is None:
                    continue
                v = entry_score(c, p)
                if v is not None:
                    scores[str(s.id)] = (v, s)
            ordered = rank_entries({k: v for k, (v, _) in scores.items()}, int(p["slots"]))
            for k in ordered:
                s = scores[k][1]
                targets[s] = self.qr_slot_weight(int(p["slots"]))
                self.age[s] = 0
        if targets:
            self.qr_rebalance(targets, tag="s001")
