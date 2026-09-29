# S006 — breakout to a new N-day high on confirming volume (H006). Variations differ only in params.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import breakout_strength, exit_signal


class Breakout(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 260
    USES_OHLC = True

    def qr_on_close(self, data):
        p = self.qr_params
        exits = []
        for kv in self.portfolio:
            s = kv.key
            if kv.value.invested and s in self.qr_close and s in self.qr_high:
                if exit_signal(self.qr_high[s], self.qr_low[s], self.qr_close[s], self.qr_sessions_held(s),
                               float(p["k"]), int(p["time_stop"])):
                    exits.append(s)
        cands = {}
        for s in self.qr_eligible:
            if not data.bars.contains_key(s) or data.bars[s].is_fill_forward or s not in self.qr_high:
                continue
            v = breakout_strength(self.qr_high[s], self.qr_low[s], self.qr_close[s], self.qr_volume[s],
                                  int(p["n"]), float(p["vol_mult"]), bool(p.get("use_volume", True)))
            if v is not None:
                cands[str(s.id)] = (v, s)
        ranked = [cands[k][1] for k in sorted(cands, key=lambda k: (-cands[k][0], k))]
        self.qr_event_step(exits, ranked, int(p["slots"]), tag="s006")
