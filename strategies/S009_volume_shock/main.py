# S009 — high-volume return premium (H009). Variations differ only in params.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import exit_signal, volume_shock


class VolumeShock(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 120
    USES_OHLC = True

    def qr_on_close(self, data):
        p = self.qr_params
        exits = [kv.key for kv in self.portfolio
                 if kv.value.invested and exit_signal(self.qr_sessions_held(kv.key), int(p["hold"]))]
        cands = {}
        for s in self.qr_eligible:
            if not data.bars.contains_key(s) or data.bars[s].is_fill_forward or s not in self.qr_high:
                continue
            r = volume_shock(self.qr_high[s], self.qr_low[s], self.qr_close[s], self.qr_volume[s],
                             float(p["vol_mult"]), int(p["days"]))
            if r is not None:
                cands[str(s.id)] = (r, s)
        ranked = [cands[k][1] for k in sorted(cands, key=lambda k: (-cands[k][0], k))]
        self.qr_event_step(exits, ranked, int(p["slots"]), tag="s009")
