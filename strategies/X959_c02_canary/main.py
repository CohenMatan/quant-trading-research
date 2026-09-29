# X959 v1.0 — C02 infrastructure canary (infrastructure, not research; not a trial).
# Checks, on QuantConnect itself, the harness features C02 relies on:
#  A. OHLC + volume windows equal a fresh point-in-time (SCALED_RAW) history, including across the
#     AAPL 7:1 split (2014-06-09) and dividends; the last window bar is the raw bar of day T.
#  B. A toy gap signal that needs close_T is placed only at the T close and fills at the T+1 open
#     (the harness self-check and the runner's fills_after_signal_date check do the fill test).
#  C. Entry bookkeeping: qr_sessions_held is 0 at the close of the fill day and counts sessions;
#     the gap day's low read from the window at "held" sessions equals the low seen at the signal.
#  D. qr_is_last_session_of_month flags exactly the last session of each month.
from AlgorithmImports import *
from qr_harness import QRAlgorithm
import json

CHECK_EVERY, HOLD, SLOTS = 21, 3, 5
FIXED = ("AAPL", "KO", "XOM", "JNJ", "WMT", "MSFT")


class C02Canary(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 60
    USES_OHLC = True
    FIXED_TICKERS = FIXED

    def qr_initialize(self):
        self.n = 0
        self.prev_day = None
        self.prev_flag = None
        self.sig_low = {}           # symbol -> (signal date, low_T at the signal close)
        self.c = {"window_checks": 0, "window_bars_compared": 0, "window_max_rel_dev": 0.0,
                  "window_mismatches": 0, "window_alignment": {}, "last_bar_checks": 0, "last_bar_mismatches": 0,
                  "gap_signals": 0, "entries_checked": 0, "held0_on_fill_day": 0, "held_not0_on_fill_day": 0,
                  "gap_low_checks": 0, "gap_low_mismatches": 0, "month_flags": 0, "month_flag_errors": 0,
                  "month_ends_seen": 0, "aapl_split_seen": 0}

    def on_data(self, data):
        # the recorded signal-day low is kept on the same point-in-time basis as the windows
        for sym, sp in data.splits.items():
            if sp.type != SplitType.SPLIT_OCCURRED:
                continue
            if sym.value == "AAPL":
                self.c["aapl_split_seen"] += 1
            if sym in self.sig_low:
                d, low = self.sig_low[sym]
                self.sig_low[sym] = (d, low * float(sp.split_factor))
        for sym, dv in data.dividends.items():
            ref = float(dv.reference_price)
            if sym in self.sig_low and ref > 0:
                d, low = self.sig_low[sym]
                self.sig_low[sym] = (d, low * (1.0 - float(dv.distribution) / ref))
        super().on_data(data)

    # ---------------------------------------------------------------- A: windows vs fresh history
    def _check_windows(self, data, syms):
        hist = self.history(syms, self.WINDOW_BARS, Resolution.DAILY,
                            data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if hist is None or hist.empty:
            return
        today = self.time.date()
        stores = (("close", self.qr_close), ("open", self.qr_open), ("high", self.qr_high),
                  ("low", self.qr_low), ("volume", self.qr_volume))
        cols = [c for c, _ in stores]
        fresh = {}
        for (sym, t), row in hist[cols].iterrows():
            f = fresh.setdefault(sym, {"dates": [], **{c: [] for c in cols}})
            f["dates"].append(t.date())
            for c in cols:
                f[c].append(float(row[c]))
        for sym in syms:
            if sym not in self.qr_close or sym not in self.qr_open or sym not in fresh:
                continue
            h = fresh[sym]
            last_date = h["dates"][-1]
            # align by the last history date: history may or may not already include today's bar
            key = "includes_today" if last_date == today else "ends_before_today"
            self.c["window_alignment"][key] = self.c["window_alignment"].get(key, 0) + 1
            self.c["window_checks"] += 1
            for col, store in stores:
                w = list(store[sym])
                if key == "ends_before_today":
                    w = w[:-1]
                ref = h[col]
                k = min(len(w), len(ref))
                for a, b in zip(w[-k:], ref[-k:]):
                    dev = abs(a - b) / max(abs(b), 1e-9)
                    self.c["window_bars_compared"] += 1
                    self.c["window_max_rel_dev"] = max(self.c["window_max_rel_dev"], dev)
                    if dev > 1e-6:
                        self.c["window_mismatches"] += 1
                        if self.c["window_mismatches"] <= 20:
                            self._qr_log(f"QRC59|window_mismatch|{today}|{sym.value}|{col}|{a}|{b}")

    def qr_on_close(self, data):
        self.n += 1
        today = self.time.date()
        # D: the previous session was flagged iff this session is in a new month
        flag = self.qr_is_last_session_of_month()
        if self.prev_day is not None:
            new_month = today.month != self.prev_day.month
            self.c["month_ends_seen"] += int(new_month)
            if new_month != self.prev_flag:
                self.c["month_flag_errors"] += 1
                self._qr_log(f"QRC59|month_flag_error|{self.prev_day}|{today}|{self.prev_flag}")
        self.c["month_flags"] += int(flag)
        self.prev_day, self.prev_flag = today, flag

        # A: last window bar is the raw bar of T (no adjustment has happened after T yet)
        for sym in [self.qr_fixed[t] for t in FIXED]:
            if data.bars.contains_key(sym) and sym in self.qr_close and not data.bars[sym].is_fill_forward:
                b = data.bars[sym]
                self.c["last_bar_checks"] += 1
                if (abs(self.qr_close[sym][-1] - float(b.close)) > 1e-9 or abs(self.qr_open[sym][-1] - float(b.open)) > 1e-9
                        or abs(self.qr_low[sym][-1] - float(b.low)) > 1e-9):
                    self.c["last_bar_mismatches"] += 1
        if self.n % CHECK_EVERY == 0 or today.isoformat() in ("2014-06-06", "2014-06-09", "2014-06-10"):
            elig = sorted(self.qr_eligible, key=lambda s: str(s.id))[:6]
            self._check_windows(data, [self.qr_fixed[t] for t in FIXED] + elig)

        # C: entry bookkeeping and the gap-day low read back from the window
        exits = []
        for kv in self.portfolio:
            s = kv.key
            if not kv.value.invested:
                continue
            held = self.qr_sessions_held(s)
            e = self._qr_entry.get(s)
            if e is not None and e["date"] == today.isoformat():
                self.c["entries_checked"] += 1
                self.c["held0_on_fill_day" if held == 0 else "held_not0_on_fill_day"] += 1
            if s in self.sig_low and held is not None and s in self.qr_low:
                lows = list(self.qr_low[s])
                if len(lows) >= held + 2:
                    self.c["gap_low_checks"] += 1
                    if abs(lows[-(held + 2)] - self.sig_low[s][1]) > 1e-6 * max(1.0, self.sig_low[s][1]):
                        self.c["gap_low_mismatches"] += 1
                        self._qr_log(f"QRC59|gap_low_mismatch|{today}|{s.value}|held={held}")
            if held is not None and held >= HOLD:
                exits.append(s)
        # B: toy gap signal, known only after the T close (needs open_T, close_T and close_T-1)
        cands = {}
        for s in self.qr_eligible:
            if not data.bars.contains_key(s) or data.bars[s].is_fill_forward or s not in self.qr_open:
                continue
            o, c = list(self.qr_open[s]), list(self.qr_close[s])
            if len(c) < 2 or c[-2] <= 0:
                continue
            gap = o[-1] / c[-2] - 1.0
            if gap >= 0.03 and c[-1] >= o[-1]:
                cands[str(s.id)] = (gap, s)
        ranked = [cands[k][1] for k in sorted(cands, key=lambda k: (-cands[k][0], k))]
        self.c["gap_signals"] += len(ranked)
        placed = self.qr_event_step(exits, ranked, SLOTS, tag="c59")
        for s, w in placed.items():
            if w > 0:
                self.sig_low[s] = (today.isoformat(), float(self.qr_low[s][-1]))

    def qr_on_end(self):
        self._qr_log("QRC59|summary|" + json.dumps(self.c, sort_keys=True))
