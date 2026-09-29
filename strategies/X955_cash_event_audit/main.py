# X955 v1.0 — cash-event audit of a completed run (infrastructure, not research; places no orders).
# For every security the audited run held, record each corporate-action event LEAN delivers while the
# run held it, and the cash the run's holdings should have received. Output is derived portfolio
# amounts only (no per-share data series): QRCE|kind|date|sid|ticker|held_qty|cash|dist/ref|dist/median.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
import bisect
import statistics


class CashEventAudit(QRAlgorithm):
    def qr_initialize(self):
        self.held = {}      # sid -> (sorted fill dates, cumulative qty after each date)
        self.syms = {}
        for sid, info in self.qr_params["holdings"].items():
            sym = Symbol(SecurityIdentifier.parse(sid), info["ticker"])
            self.add_security(sym, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.RAW)
            self.syms[str(sym.id)] = sym
            self.held[str(sym.id)] = (info["dates"], info["qty_after"])
        self.divs = []      # collected, emitted at the end with the per-security median

    def qty_before(self, sid, day):
        dates, qty = self.held.get(sid, ([], []))
        i = bisect.bisect_left(dates, day)      # fills dated strictly before the event day
        return qty[i - 1] if i else 0.0

    def on_data(self, data):
        day = f"{self.time:%Y-%m-%d}"
        for sym, dv in data.dividends.items():
            sid = str(sym.id)
            q = self.qty_before(sid, day)
            ref = float(dv.reference_price) or float("nan")
            self.divs.append((day, sid, sym.value, q, float(dv.distribution), ref))
        for sym, sp in data.splits.items():
            if sp.type == SplitType.SPLIT_OCCURRED and self.qty_before(str(sym.id), day):
                self._qr_log(f"QRCE|split|{day}|{sym.id}|{sym.value}|{self.qty_before(str(sym.id), day)}|0|{float(sp.split_factor):.8f}|")
        for sym, ch in data.symbol_changed_events.items():
            if self.qty_before(str(sym.id), day):
                self._qr_log(f"QRCE|symbol_change|{day}|{sym.id}|{ch.old_symbol}>{ch.new_symbol}|{self.qty_before(str(sym.id), day)}|0||")
        for sym, dl in data.delistings.items():
            if dl.type == DelistingType.DELISTED and self.qty_before(str(sym.id), day):
                self._qr_log(f"QRCE|delisted|{day}|{sym.id}|{sym.value}|{self.qty_before(str(sym.id), day)}|0||")
        super().on_data(data)

    def qr_on_close(self, data):
        pass

    def qr_on_end(self):
        by = {}
        for d in self.divs:
            by.setdefault(d[1], []).append(d[4])
        for day, sid, tic, q, dist, ref in self.divs:
            if q <= 0:
                continue
            med = statistics.median(by[sid])
            self._qr_log(f"QRCE|dividend|{day}|{sid}|{tic}|{q}|{q * dist:.4f}|{dist / ref:.6f}|{dist / med:.4f}")
