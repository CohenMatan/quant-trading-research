# S006 — breakout to a new N-day high on confirming volume (H006). Variations differ only in params.
# D304: params.time_stop null = no time stop (H006X Experiment B); beyond the 260-bar window the highest close since
# entry is carried as a ratio to the close it was stored at (and that bar's date), so window re-adjustments (splits,
# dividends) carry over exactly.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
from signals import breakout_strength, carried_peak, exit_signal, peak_since_entry


class Breakout(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 260
    USES_OHLC = True

    def qr_on_close(self, data):
        p = self.qr_params
        ts = p.get("time_stop")
        ts = None if ts is None else int(ts)
        peaks = getattr(self, "_s006_peak", None)       # symbol -> (peak / close then, that bar's date)
        if peaks is None:
            peaks = self._s006_peak = {}
        exits = []
        for kv in self.portfolio:
            s = kv.key
            if not kv.value.invested:
                peaks.pop(s, None)
                continue
            if s in self.qr_close and s in self.qr_high:
                c = self.qr_close[s]
                held = self.qr_sessions_held(s)
                last = self._qr_last_bar.get(s)
                carried = carried_peak(peaks.get(s), c, last, len(c) == self.WINDOW_BARS)
                if held is not None:
                    peaks[s] = (peak_since_entry(c, held, carried) / c[-1], last)
                if exit_signal(self.qr_high[s], self.qr_low[s], c, held, float(p["k"]), ts, carried):
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
