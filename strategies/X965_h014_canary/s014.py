# S014 — H014 trend + pullback + confirmed recovery (Phase 2; research/hypotheses/H014.md), and its
# controls (C1 trend-only, C2 pullback without recovery, R random uptrend), frozen by
# research/phase2/P2_spec.md (D094). One code path for every book: only params differ.
#   params: mode (h014 | c1 | c2 | rand), exit (A | B), limit (A: horizon 63; B: cap 126), slots 12,
#           rsi_pullback 40, window 5, rsi_recovery 45, seed (rand only).
# Every close: held stocks whose exit rule fires are sold; free slots are filled from today's entry
# candidates in the book's order. Orders are next-open orders via the harness (D051 cash rules, $7/order,
# 10 bps slippage); nothing can execute before T+1.
from AlgorithmImports import *
import json
import numpy as np
from qr_harness import QRAlgorithm
from nullorder import pick_order
from signals import MIN_BARS, entry_mask, exit_decision, features, momentum_order


class TrendPullback(QRAlgorithm):
    USES_UNIVERSE = True
    USES_OHLC = True
    WINDOW_BARS = MIN_BARS

    def qr_initialize(self):
        p = self.qr_params
        self.mode, self.variant, self.limit = p["mode"], p["exit"], int(p["limit"])
        self.slots = int(p["slots"])
        self.seed = int(p.get("seed", 0))
        self.rule = dict(rsi_pullback=float(p["rsi_pullback"]), window=int(p["window"]),
                         rsi_recovery=float(p["rsi_recovery"]))
        self.s14 = {"closes": 0, "candidates_sum": 0, "signals_sum": 0, "signal_days": 0, "exits_ma200": 0,
                    "exits_time": 0, "rolls": 0, "held_short_window": 0, "held_no_entry": 0, "entries_ordered": 0}

    def _matrix(self, syms):
        c = np.array([list(self.qr_close[s])[-MIN_BARS:] for s in syms], dtype=float).reshape(len(syms), MIN_BARS)
        h = np.array([self.qr_high[s][-2] for s in syms], dtype=float)
        return features(c, h)

    def qr_signals(self, data):
        """Today's entry candidates (eligible, real bar at T, >= MIN_BARS closes), their features and mask."""
        cands = [s for s in self.qr_eligible
                 if data.bars.contains_key(s) and not data.bars[s].is_fill_forward
                 and s in self.qr_close and len(self.qr_close[s]) >= MIN_BARS]
        if not cands:
            return cands, None, np.zeros(0, dtype=bool)
        f = self._matrix(cands)
        return cands, f, entry_mask(f, self.mode, **self.rule)

    def qr_on_close(self, data):
        st = self.s14
        st["closes"] += 1
        cands, f, mask = self.qr_signals(data)
        signal = {s for s, m in zip(cands, mask) if m}
        st["candidates_sum"] += len(cands)
        st["signals_sum"] += len(signal)
        st["signal_days"] += int(bool(signal))
        exits = []
        for kv in self.portfolio:
            sym = kv.key
            if not kv.value.invested:
                continue
            w = self.qr_close.get(sym)
            if w is None or len(w) < 200:
                st["held_short_window"] += 1
                continue
            close, ma200 = float(w[-1]), float(np.mean(list(w)[-200:]))
            held = self.qr_sessions_held(sym)
            if held is None:
                st["held_no_entry"] += 1
            d = exit_decision(held, close, ma200, self.variant, self.limit, sym in signal)
            if d == "ma200":
                exits.append(sym)
                st["exits_ma200"] += 1
            elif d == "time":
                exits.append(sym)
                st["exits_time"] += 1
            elif d == "roll":
                self._qr_entry[sym]["session"] = self._qr_session     # clock restarts: held = 0 today
                st["rolls"] += 1
        ids = {str(s.id): s for s in signal}
        if self.mode == "rand":
            order = pick_order(list(ids), self.seed, self._qr_session)
        else:
            mom = {str(s.id): float(m) for s, m in zip(cands, f["mom"])} if f is not None else {}
            order = momentum_order(list(ids), [mom[k] for k in ids])
        ranked = [ids[k] for k in order]
        st["entries_ordered"] += len(ranked)
        self.qr_event_step(exits, ranked, self.slots, tag="s014")
        return cands, f, mask, ranked, exits

    def qr_on_end(self):
        self._qr_log("QRS014|summary|" + json.dumps(self.s14, sort_keys=True))
