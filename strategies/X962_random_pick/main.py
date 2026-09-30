# X962 v1.0 — no-skill random-pick portfolio (portfolio-structure diagnostic; NOT research, NOT a
# trial; owner instruction 2026-09-30, pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md).
# Every close: sell holdings held `hold` sessions; fill free slots from ALL eligible stocks (the
# approved >= $2B US-common universe) in a seeded random order. Orders are next-open orders through
# the harness (D051 cash rules, $7/order, 10 bps slippage), exactly as for the C02 strategies.
# Selection uses no price information, so results measure portfolio structure, costs and the market.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import pick_order


class RandomPick(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 0

    def qr_on_close(self, data):
        p = self.qr_params
        hold, slots, seed = int(p["hold"]), int(p["slots"]), int(p["seed"])
        exits = [kv.key for kv in self.portfolio if kv.value.invested
                 and (self.qr_sessions_held(kv.key) or 0) >= hold]
        cands = {str(s.id): s for s in self.qr_eligible
                 if data.bars.contains_key(s) and not data.bars[s].is_fill_forward}
        ranked = [cands[k] for k in pick_order(list(cands), seed, self._qr_session)]
        self.qr_event_step(exits, ranked, slots, tag="x962")
