# S013 — H013 lottery-stock avoidance (C03; research/hypotheses/H013.md, frozen before any C03 result).
# Identical to the no-skill null X962 (every close: sell holdings held `hold` sessions; fill free slots
# in the null's seeded random order over ALL eligible stocks with a real bar today) except that names in
# the top fraction q of MAX (or MAX5) over the last 21 daily returns, among all eligible stocks with at
# least 21 returns, are skipped. nullorder.py is a byte copy of X962's signals.py (tested), so wherever
# the null would buy a non-excluded name, S013 buys the same name at the same place in the order.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from nullorder import pick_order
from signals import WINDOW, allowed_order, excluded_ids


class LotteryAvoid(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = WINDOW + 1

    def qr_initialize(self):
        self.s13 = {"closes": 0, "excluded_sum": 0, "ranked_sum": 0, "windows_sum": 0}

    def qr_on_close(self, data):
        p = self.qr_params
        hold, slots, seed = int(p["hold"]), int(p["slots"]), int(p["seed"])
        q, stat = float(p["q"]), p["stat"]
        exits = [kv.key for kv in self.portfolio if kv.value.invested
                 and (self.qr_sessions_held(kv.key) or 0) >= hold]
        cands = {str(s.id): s for s in self.qr_eligible
                 if data.bars.contains_key(s) and not data.bars[s].is_fill_forward}
        windows = {str(s.id): self.qr_close[s] for s in self.qr_eligible if s in self.qr_close}
        excluded = excluded_ids(windows, q, stat) if q > 0 else set()
        ranked = [cands[k] for k in allowed_order(pick_order(list(cands), seed, self._qr_session), excluded)]
        st = self.s13
        st["closes"] += 1
        st["excluded_sum"] += len(excluded)
        st["ranked_sum"] += len(ranked)
        st["windows_sum"] += len(windows)
        self.qr_event_step(exits, ranked, slots, tag="s013")

    def qr_on_end(self):
        import json
        self._qr_log("QRS013|summary|" + json.dumps(self.s13, sort_keys=True))
