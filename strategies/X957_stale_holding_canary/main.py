# X957 v1.0 — D059 stale-holding canary (infrastructure, not research).
# Buys securities that QuantConnect's data stops pricing without a delisting event (found stuck in
# the equal-weight benchmark E901-05) shortly before their acquisitions, plus controls: TIF (a
# normal LEAN delisting) and KO (live all period). Never sells, except one real-world stuck sell on
# OAK. With D059 every dead holding must be taken out at its last real close (QRSTALE), no order may
# stay open, TIF must be liquidated by LEAN and KO must still be held at the end.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
import json


class StaleHoldingCanary(QRAlgorithm):
    def qr_initialize(self):
        self.plan = self.qr_params["buys"]           # sid -> {ticker, buy_on}
        self.syms = {}
        for sid, b in self.plan.items():
            sym = Symbol(SecurityIdentifier.parse(sid), b["ticker"])
            self.add_security(sym, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.RAW)
            self.syms[sid] = sym
        self.done = set()
        self.sell_oak_on = self.qr_params["oak_sell_on"]
        self.sold_oak = False

    def qr_on_close(self, data):
        day = self.time.strftime("%Y-%m-%d")
        targets = {}
        for sid, b in self.plan.items():
            sym = self.syms[sid]
            if sid not in self.done and day >= b["buy_on"] and data.bars.contains_key(sym) \
                    and not data.bars[sym].is_fill_forward:
                targets[sym] = 0.04
                self.done.add(sid)
        if targets:
            self.qr_rebalance(targets, tag="canary_buy")
        oak = self.syms[self.qr_params["oak_sid"]]
        if not self.sold_oak and day >= self.sell_oak_on and self.portfolio[oak].invested:
            self.qr_rebalance({oak: 0.0}, tag="canary_sell")
            self.sold_oak = True

    def qr_on_end(self):
        held = sorted(kv.key.value for kv in self.portfolio if kv.value.invested)
        self._qr_log("QRCANARY57|" + json.dumps({"held_at_end": held, "bought": len(self.done)}, sort_keys=True))
