# X960 v1.0 — month-end close store canary (infrastructure, not research; not a trial).
# Checks the MONTHLY_BARS store that S011 (H011) uses, on QuantConnect itself:
#  A. At the first session of every month, qr_month_close equals the month-end closes rebuilt from a
#     fresh point-in-time (SCALED_RAW) daily history, month by month (AAPL 7:1 split 2014, dividends).
#  B. No look-ahead: the store never holds the current month.
#  C. At the 2010 start there are >= 120 completed months (10-year look-back, owner approval
#     2026-09-29: pre-2010 prices as signal warm-up only).
# It places no orders.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
import json

FIXED = ("AAPL", "KO", "XOM", "JNJ", "WMT", "MSFT", "PG", "IBM")


class MonthEndCanary(QRAlgorithm):
    USES_UNIVERSE = False
    WINDOW_BARS = 0
    MONTHLY_BARS = 12 * 10 + 14
    FIXED_TICKERS = FIXED

    def qr_initialize(self):
        self.prev_month = None
        self.c = {"checks": 0, "months_compared": 0, "max_rel_dev": 0.0, "mismatches": 0, "month_key_mismatches": 0,
                  "current_month_in_store": 0, "months_at_start": {}, "min_months_at_start": None,
                  "first_check_date": None}

    def qr_on_close(self, data):
        today = self.time.date()
        ym = today.year * 100 + today.month
        syms = [self.qr_fixed[t] for t in FIXED]
        for s in syms:
            mc = self.qr_month_close.get(s)
            if mc and any(k >= ym for k, _ in mc):
                self.c["current_month_in_store"] += 1
        if self.prev_month == ym:
            return
        first = self.prev_month is None
        self.prev_month = ym
        if first:
            self.c["first_check_date"] = today.isoformat()
            n = {s.value: len(self.qr_month_close.get(s) or []) for s in syms}
            self.c["months_at_start"] = n
            self.c["min_months_at_start"] = min(n.values()) if n else 0
        self._compare(syms, today, ym)

    def _compare(self, syms, today, ym):
        bars = self.MONTHLY_BARS * 23 + 30
        hist = self.history(syms, bars, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if hist is None or hist.empty:
            return
        last = {}
        rebuilt = {}
        for (sym, t), c in hist["close"].items():
            # daily bars must be stamped at the session close (16:00), not midnight of the next day;
            # a midnight stamp would move each month's last bar into the following month
            self.c["midnight_stamps"] = self.c.get("midnight_stamps", 0) + int(t.hour == 0)
            k = t.year * 100 + t.month
            if t.date() >= today:
                continue                                   # only bars before today's close
            p = last.get(sym)
            if p is not None and p[0] != k:
                rebuilt.setdefault(sym, {})[p[0]] = p[1]
            last[sym] = (k, float(c))
        for sym, (k, c) in last.items():
            if k < ym:
                rebuilt.setdefault(sym, {})[k] = c          # the previous month is complete today
        for sym in syms:
            mc = list(self.qr_month_close.get(sym) or [])
            if not mc:
                continue
            ref = rebuilt.get(sym, {})
            self.c["checks"] += 1
            have = {k for k, _ in mc}
            miss = [k for k in ref if mc[0][0] <= k < ym and k not in have]
            self.c["store_missing_months"] = self.c.get("store_missing_months", 0) + len(miss)
            for k1, v1 in mc[1:]:                            # the oldest month may be cut by the history length
                self.c["months_compared"] += 1
                if k1 not in ref:
                    self.c["month_key_mismatches"] += 1
                    continue
                v2 = ref[k1]
                dev = abs(v1 - v2) / max(abs(v2), 1e-9)
                self.c["max_rel_dev"] = max(self.c["max_rel_dev"], dev)
                if dev > 1e-6:
                    self.c["mismatches"] += 1
                    if self.c["mismatches"] <= 20:
                        self._qr_log(f"QRC60|mismatch|{today}|{sym.value}|{k1}|{v1}|{v2}")

    def qr_on_end(self):
        self._qr_log("QRC60|summary|" + json.dumps(self.c, sort_keys=True))
