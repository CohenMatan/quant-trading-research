# S010 — gap-and-hold (H010). Variations differ only in params.
# Timing: the gap day T is only evaluated at T's close (it needs T's close, low and volume); the
# order is a market-on-open order for T+1 (qr_event_step -> qr_rebalance). Nothing executes on T.
# The gap day is therefore always the session before the entry session, so its low is read from the
# adjusted low window (which splits and dividends rescale), never stored as a raw number.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import exit_signal, gap_day_low, gap_hold


class GapHold(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 210
    USES_OHLC = True

    def qr_on_close(self, data):
        p = self.qr_params
        exits = []
        for kv in self.portfolio:
            s = kv.key
            if kv.value.invested and s in self.qr_close and s in self.qr_low:
                held = self.qr_sessions_held(s)
                if exit_signal(self.qr_close[s], held, gap_day_low(self.qr_low[s], held), int(p["hold"])):
                    exits.append(s)
        cands = {}
        for s in self.qr_eligible:
            if not data.bars.contains_key(s) or data.bars[s].is_fill_forward or s not in self.qr_open:
                continue
            r = gap_hold(self.qr_open[s], self.qr_high[s], self.qr_low[s], self.qr_close[s], self.qr_volume[s],
                         float(p["min_gap"]), float(p["gap_atr"]), bool(p["require_hold"]), float(p["vol_mult"]))
            if r is not None:
                cands[str(s.id)] = (r[0], s)
        ranked = [cands[k][1] for k in sorted(cands, key=lambda k: (-cands[k][0], k))]
        self.qr_event_step(exits, ranked, int(p["slots"]), tag="s010")
