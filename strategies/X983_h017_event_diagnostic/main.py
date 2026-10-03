# X983 — H017 event-level diagnostic E983-01 (research/phase2/H017_spec.md §8). NON-TRADING, aggregated output only;
# never a gate, never a design input; used only within PbNQ rule 7. PREPARED 2026-10-03; it computes post-event
# returns and therefore runs ONLY after its separate owner approval (config owner_approval_required).
# For every universe event with a valid reaction (the same events, closes and point-in-time breakpoints as S017),
# decision session 2010-03-01 .. 2021-12-31 and exit session E+62 on or before the run end (no Holdout data):
#   group     top (AR >= p90 and AR > 0, = the candidate's signals) / mid (deciles 2-9) / bottom (decile 1) /
#             d10_nonpos (decile 10 with AR <= 0; reported separately)
#   excess    [Open(E+62)/Open(E+2) - 1] - [SPY Open(E+62)/SPY Open(E+2) - 1], adjusted (SCALED_RAW) prices; a real
#             open at E+2 is required; no real bar at E+62 -> the last real close before it (harness convention)
#   splits    timing class (BMO / DURING / AMC / other) and abnormal-volume tercile (mean volume of E and E+1 over the
#             mean volume of the 20 sessions ending at E-1; trailing 252-session terciles; 0 = not computable)
# Output (summary statistics): per (decision month, group, class, volume tercile) n, sum, sum of squares; medians and
# quartiles per group, per (group, two-year block), per (group, class), per (group, tercile); counts. No prices.
from AlgorithmImports import *
from collections import defaultdict
from datetime import date, datetime, timedelta
import json
from qr_harness import QRAlgorithm, in_warmup
from qr_h017 import (DECILE_QS, Breakpoints, bar_date, breakpoints_of, decile_of, qualifies, reaction, tercile_of)
from qr_h017_events import SHA256 as EVENTS_SHA256, load_events

VOL_BASE = 20
EXIT_OFFSET = 61          # E+62 = decision session (E+1) + 61 sessions
CLASS = {"B": "BMO", "D": "DURING", "A": "AMC", "N": "other", "U": "other"}


def _q(xs, p):
    x = sorted(xs)
    h = (len(x) - 1) * p
    lo = int(h)
    return x[lo] + (h - lo) * (x[min(lo + 1, len(x) - 1)] - x[lo])


class EventDiagnostic(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        if self.qr_sec is None:
            raise Exception("X983 needs universe.sec_corrections (frozen data infrastructure v1)")
        t = load_events()
        epoch = date.fromisoformat(t["epoch"])
        self.by_E = {}
        for i, d, c in t["events"]:
            self.by_E.setdefault(epoch + timedelta(days=d), []).append((t["sids"][i], c))
        self.bp_ar = Breakpoints()
        self.bp_av = Breakpoints()
        self.sess = []
        self.done = None
        self.pending = defaultdict(list)       # exit session index -> [(symbol, decision date, group, class, tercile)]
        self.agg = defaultdict(lambda: [0, 0.0, 0.0])
        self.vals = defaultdict(list)
        self.st = {"events_table_sha256": EVENTS_SHA256, "events_universe": 0, "events_valid": 0,
                   "events_scheduled": 0, "events_measured": 0, "no_entry_open": 0, "exit_from_last_close": 0,
                   "no_exit_price": 0, "no_breakpoints": 0, "av_missing": 0, "bars_after_today": 0}

    def qr_select_universe(self, eligible):
        return [f.symbol for f in eligible]

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count == 0 or self.time.hour < 9:
            return
        today = self.time.date()
        if self.done != today and in_warmup(today, self.qr_official_start):
            self._day(data, today, official=False)

    def qr_on_close(self, data):
        self._day(data, self.time.date(), official=True)

    def _hist(self, symbols, start, field, data=None):
        """{symbol: {session date: (field values)}} of real SCALED_RAW bars from `start` through today; today's bar
        from the current slice if history lacks it (as S017)."""
        out = {s: {} for s in symbols}
        h = self.history(symbols, datetime(start.year, start.month, start.day), self.time, Resolution.DAILY,
                         fill_forward=False, data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if h is not None and not h.empty:
            for (sym, tt), row in h[list(field)].iterrows():
                d = bar_date(tt)
                if d > self.time.date():
                    self.st["bars_after_today"] += 1
                    continue
                if sym in out:
                    out[sym][d] = tuple(float(row[f]) for f in field)
        today = self.time.date()
        if data is not None:
            for s in symbols:
                if today not in out[s] and data.bars.contains_key(s) and not data.bars[s].is_fill_forward:
                    b = data.bars[s]
                    out[s][today] = tuple(float(getattr(b, f)) for f in field)
        return out

    def _day(self, data, today, official):
        self.done = today
        if self._qr_session_day != today:
            return
        if not self.sess or self.sess[-1] != today:
            self.sess.append(today)
        t = len(self.sess) - 1
        if official:
            self._measure(t, today, data)
        if t < 2:
            return
        E = self.sess[t - 1]
        evs = self.by_E.get(E, [])
        elig = {str(s.id): s for s in self.qr_eligible}
        uni = [(sid, c) for sid, c in evs if sid in elig]
        self.st["events_universe"] += len(uni)
        valid = []
        if uni:
            syms = [elig[sid] for sid, _ in uni]
            h = self._hist(syms + [self.spy], self.sess[max(0, t - VOL_BASE - 2)], ("close", "volume"), data)
            d_m1, base = self.sess[t - 2], self.sess[max(0, t - VOL_BASE - 1):t - 1]   # 20 sessions ending at E-1
            spy = h.get(self.spy, {})
            for sid, c in uni:
                x = h.get(elig[sid], {})
                if not all(d in x and d in spy for d in (d_m1, E, today)):
                    continue
                ar = reaction(x[d_m1][0], x[today][0], spy[d_m1][0], spy[today][0])
                if ar is None:
                    continue
                vb = [x[d][1] for d in base if d in x]
                av = (x[E][1] + x[today][1]) / 2.0 / (sum(vb) / len(vb)) if len(vb) == VOL_BASE and sum(vb) > 0 else None
                valid.append((sid, ar, av, c))
        self.st["events_valid"] += len(valid)
        thr_s = self.bp_ar.sample(t)
        av_s = self.bp_av.sample(t)
        bps = breakpoints_of(thr_s, DECILE_QS) if len(thr_s) >= self.bp_ar.min_events else None
        avb = breakpoints_of(av_s, (1 / 3, 2 / 3)) if len(av_s) >= self.bp_av.min_events else None
        for sid, ar, av, c in valid:
            self.bp_ar.add(t, ar)
            if av is not None:
                self.bp_av.add(t, av)
        if not official or not valid:
            return
        if bps is None:
            self.st["no_breakpoints"] += len(valid)
            return
        for sid, ar, av, c in valid:
            d = decile_of(ar, bps)
            g = "top" if qualifies(ar, bps[-1]) else ("d10_nonpos" if d == 10 else ("bottom" if d == 1 else "mid"))
            if av is None or avb is None:
                self.st["av_missing"] += 1
                ter = 0
            else:
                ter = tercile_of(av, avb)
            self.pending[t + EXIT_OFFSET].append((elig[sid], str(today), g, CLASS[c], ter))
            self.st["events_scheduled"] += 1

    def _measure(self, t, today, data):
        due = self.pending.pop(t, [])
        if not due:
            return
        e2 = self.sess[t - EXIT_OFFSET + 1]
        syms = list({s for s, *_ in due})
        h = self._hist(syms + [self.spy], e2, ("open", "close"), data)
        spy = h.get(self.spy, {})
        if e2 not in spy or today not in spy:
            self.st["no_exit_price"] += len(due)
            return
        r_spy = spy[today][0] / spy[e2][0] - 1.0
        for sym, dec, g, cls, ter in due:
            x = h.get(sym, {})
            if e2 not in x or not x[e2][0] > 0:
                self.st["no_entry_open"] += 1
                continue
            if today in x and x[today][0] > 0:
                px = x[today][0]
            else:
                prior = [d for d in x if e2 <= d < today]
                if not prior:
                    self.st["no_exit_price"] += 1
                    continue
                px = x[max(prior)][1]
                self.st["exit_from_last_close"] += 1
            ex = (px / x[e2][0] - 1.0) - r_spy
            y = int(dec[:4])
            block = f"{y - (y - 2010) % 2}-{y - (y - 2010) % 2 + 1}"
            a = self.agg[(dec[:7], g, cls, ter)]
            a[0] += 1
            a[1] += ex
            a[2] += ex * ex
            for k in ((g,), (g, "block", block), (g, "class", cls), (g, "av", str(ter))):
                self.vals[k].append(ex)
            self.st["events_measured"] += 1

    def qr_on_end(self):
        self.st["events_beyond_end"] = sum(len(v) for v in self.pending.values())
        for (m, g, cls, ter), (n, s, ss) in sorted(self.agg.items()):
            self._qr_log(f"A|{m}|{g}|{cls}|{ter}|{n}|{s:.10g}|{ss:.10g}")
        for k, v in sorted(self.vals.items()):
            self._qr_log(f"M|{'/'.join(k)}|{len(v)}|{sum(v) / len(v):.10g}|{_q(v, 0.5):.10g}|{_q(v, 0.25):.10g}|"
                         f"{_q(v, 0.75):.10g}")
        self._qr_log("QRX983|summary|" + json.dumps(self.st, sort_keys=True))
