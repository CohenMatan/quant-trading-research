# S007 — volatility contraction followed by expansion (H007). Variations differ only in params.
from AlgorithmImports import *
from collections import deque
from qr_harness import QRAlgorithm
from qr_indicators import bandwidth
from signals import bandwidth_series, contracted_atr, contracted_bw, expansion, exit_signal


class Squeeze(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 280
    USES_OHLC = True

    def qr_initialize(self):
        self.bw = {}            # symbol -> deque of daily bandwidth values (ends at T)
        self.bw_session = {}    # symbol -> harness session of the last value

    def _bandwidth_history(self, s):
        """Bandwidth series ending at T: extended by one value if it was current at the previous
        session, otherwise rebuilt from the close window (identical values either way)."""
        c, now = self.qr_close[s], self._qr_session
        last = self.bw_session.get(s)
        if last == now:
            return self.bw[s]
        if last == now - 1 and s in self.bw:
            self.bw[s].append(bandwidth(c, 20, 2.0))
        else:
            self.bw[s] = deque(bandwidth_series(c)[-252:], maxlen=252)
        self.bw_session[s] = now
        return self.bw[s]

    def qr_on_close(self, data):
        p = self.qr_params
        exits = []
        for kv in self.portfolio:
            s = kv.key
            if kv.value.invested and s in self.qr_close:
                if exit_signal(self.qr_close[s], self.qr_sessions_held(s), 5, int(p["time_stop"])):
                    exits.append(s)
        cands = {}
        for s in self.qr_eligible:
            if not data.bars.contains_key(s) or data.bars[s].is_fill_forward or s not in self.qr_high:
                continue
            h, l, c, v = self.qr_high[s], self.qr_low[s], self.qr_close[s], self.qr_volume[s]
            if p["setup"] == "bandwidth":
                score = contracted_bw(self._bandwidth_history(s), float(p["pct"]))
            else:
                score = contracted_atr(h, l, c, float(p["atr_ratio"]))
            if score is None:
                continue
            if expansion(h, l, c, v, use_trend=bool(p.get("use_trend", True))):
                cands[str(s.id)] = (score, s)
        ranked = [cands[k][1] for k in sorted(cands, key=lambda k: (cands[k][0], k))]   # tightest first
        self.qr_event_step(exits, ranked, int(p["slots"]), tag="s007")
        for s in list(self.bw):
            if s not in self.qr_close:
                self.bw.pop(s, None)
                self.bw_session.pop(s, None)
