# X958 v1.0 — D063 end-to-end canary (infrastructure, not research; not a trial).
# Every CYCLE sessions: at the close, pick one eligible stock and queue a next-open buy; at the next
# universe selection (overnight) drop that stock from the universe, so LEAN removes it while the buy
# is pending. Requirements: the buy fills, the price window survives, and a time-exit rule that READS
# the window (as S001 does) sells after EXIT_AGE closes. Every SIM_EVERY-th cycle the window is also
# deleted after the fill to exercise the daily safety net (_qr_check_windows).
from AlgorithmImports import *
from qr_harness import QRAlgorithm
import json

CYCLE, EXIT_AGE, SIM_EVERY = 10, 3, 5


class WindowCanary(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 30

    def qr_initialize(self):
        self.session = 0
        self.drop = set()          # symbols kept out of the universe (picked, pending or held)
        self.age = {}
        self.cycle = 0
        self.sim = set()
        self.c = {"picks": 0, "removed_while_pending": 0, "window_kept_on_removal": 0, "filled": 0,
                  "window_at_fill": 0, "exits_submitted": 0, "exits_filled": 0, "exit_ages": [],
                  "no_window_at_close": 0, "simulated_window_loss": 0}

    def qr_select_universe(self, eligible):
        return [f.symbol for f in eligible if f.symbol not in self.drop]

    def on_securities_changed(self, changes):
        pending = {t.symbol for t in self.transactions.get_open_order_tickets()}
        for sec in changes.removed_securities:
            if sec.symbol in self.drop and sec.symbol in pending and not self.portfolio[sec.symbol].invested:
                self.c["removed_while_pending"] += 1
        super().on_securities_changed(changes)
        for sec in changes.removed_securities:
            if sec.symbol in self.drop and sec.symbol in pending and sec.symbol in self.qr_close:
                self.c["window_kept_on_removal"] += 1
                self._qr_log(f"QRC58|removed_pending_window_kept|{self.time:%Y-%m-%d}|{sec.symbol.value}")

    def qr_on_fill(self, ev):
        s = ev.symbol
        if s not in self.drop:
            return
        if float(ev.fill_quantity) > 0:
            self.c["filled"] += 1
            self.c["window_at_fill"] += int(s in self.qr_close)
            self.age[s] = 0
            if s in self.sim:                     # safety-net exercise: lose the window after the fill
                self.qr_close.pop(s, None)
                self.qr_volume.pop(s, None)
                self.c["simulated_window_loss"] += 1
        else:
            self.c["exits_filled"] += 1

    def qr_on_close(self, data):
        self.session += 1
        targets = {}
        for kv in self.portfolio:
            s = kv.key
            if not kv.value.invested or s not in self.age:
                continue
            self.age[s] += 1
            c = self.qr_close.get(s)
            if c is None:
                self.c["no_window_at_close"] += 1          # the D063 failure: exit rule blind
                continue
            if self.age[s] >= EXIT_AGE and len(c) > 0:
                targets[s] = 0.0
                self.c["exits_submitted"] += 1
                self.c["exit_ages"].append(self.age[s])
                del self.age[s]
        if self.session % CYCLE == 0:
            cands = [s for s in self.qr_eligible if s not in self.drop and data.bars.contains_key(s)
                     and s in self.qr_close and len(self.qr_close[s]) >= 5]
            if cands:
                pick = min(cands, key=lambda s: self.qr_eligible_info[s][0])   # smallest market cap
                targets[pick] = 0.05
                self.drop.add(pick)
                self.cycle += 1
                if self.cycle % SIM_EVERY == 0:
                    self.sim.add(pick)
                self.c["picks"] += 1
                self._qr_log(f"QRC58|pick|{self.time:%Y-%m-%d}|{pick.value}")
        if targets:
            self.qr_rebalance(targets, tag="c58")

    def qr_on_end(self):
        held = sorted(kv.key.value for kv in self.portfolio if kv.value.invested)
        self._qr_log("QRC58|summary|" + json.dumps(dict(self.c, held_at_end=held), sort_keys=True))
