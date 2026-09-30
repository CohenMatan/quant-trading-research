# X961 v1.1 — C02 signal-equivalence canary (verification, not research; not a trial; no orders).
# v1.1: corrected H008 score (D074 option A, 780-bar windows); params {"only": "H008"} runs the
# H008 check alone, with score-dispersion statistics per ranking date.
# Owner request 2026-09-29. The harness adjusts past prices for dividends with the standard factor
# (1 - dividend / reference price), which differs from QuantConnect's own factor in the 5th decimal
# (<= 0.06% after 5 years, E960-01). Question: do the ACTUAL C02 decisions change?
#
# The canary keeps a REFERENCE copy of every window and month-end store. It is identical to the
# harness's, except that at each dividend or split the reference is rescaled with QuantConnect's
# exact factor, measured at that close as fresh_history_close(T-1) / unadjusted_close(T-1). The
# reference is checked against fresh QuantConnect history periodically (ref_check_*).
#
# On every CHECK_EVERY-th session (event strategies; a sample, for runtime) and on every monthly ranking date (H008, H011)
# the unchanged C02 signal functions (sig006..sig011 = byte copies of the strategies' signals.py,
# enforced by tests/test_signal_equivalence_canary.py) are run on the harness inputs (H) and on the
# reference inputs (R), for every eligible stock, with the main.py filters and ranking rules. Every
# decision that differs is counted, with its direction, and examples are kept.
from AlgorithmImports import *
from collections import deque
from qr_harness import QRAlgorithm
from qr_indicators import sma
import json
import sig006, sig007, sig008, sig009, sig010, sig011

CHECK_EVERY = 10
FIXED = ("AAPL", "KO", "XOM", "JNJ", "WMT", "MSFT", "PG", "IBM")
N_EX = 15


def _ranked(d, ascending=False):
    """d: sid -> score. Ranking as in the strategies: score (desc unless ascending), ties by id."""
    return sorted(d, key=lambda k: ((d[k] if ascending else -d[k]), k))


class SignalEquivalence(QRAlgorithm):
    USES_UNIVERSE = True
    WINDOW_BARS = 780            # >= every C02 window (S008 780, S007 280, S006 260)
    USES_OHLC = True
    MONTHLY_BARS = 12 * 10 + 14  # as S011
    FIXED_TICKERS = FIXED

    def qr_initialize(self):
        self.n = 0
        self.rc, self.ro, self.rh, self.rl, self.rv = {}, {}, {}, {}, {}
        self.rmc, self.rml, self.rlast = {}, {}, {}
        self.events = set()
        self.last_month = None
        self.c = {"sessions": 0, "event_days_checked": 0, "rank_dates_h008": 0, "rank_dates_h011": 0,
                  "ca_events": 0, "ca_factor_diff_max": 0.0, "ca_no_prev": 0,
                  "ref_check_bars": 0, "ref_check_max_dev": 0.0, "ref_month_checks": 0, "ref_month_max_dev": 0.0,
                  "window_max_dev_H_vs_R": 0.0, "month_max_dev_H_vs_R": 0.0, "strategies": {}}

    # ------------------------------------------------------------ reference windows
    def on_securities_changed(self, changes):
        super().on_securities_changed(changes)
        for sec in changes.added_securities:
            s = sec.symbol
            if s in self.qr_close and s not in self.rc:
                self.rc[s], self.rv[s] = deque(self.qr_close[s], maxlen=self.WINDOW_BARS), deque(self.qr_volume[s], maxlen=self.WINDOW_BARS)
                self.ro[s], self.rh[s] = deque(self.qr_open[s], maxlen=self.WINDOW_BARS), deque(self.qr_high[s], maxlen=self.WINDOW_BARS)
                self.rl[s] = deque(self.qr_low[s], maxlen=self.WINDOW_BARS)
                self.rlast[s] = self._qr_last_bar.get(s)
            if s in self.qr_month_close and s not in self.rmc:
                self.rmc[s] = deque([list(x) for x in self.qr_month_close[s]], maxlen=self.MONTHLY_BARS)
                if s in self._qr_month_last:
                    self.rml[s] = list(self._qr_month_last[s])
        for s in list(self.rc):
            if s not in self.qr_close:
                for d in (self.rc, self.ro, self.rh, self.rl, self.rv, self.rlast):
                    d.pop(s, None)
        for s in list(self.rmc):
            if s not in self.qr_month_close:
                self.rmc.pop(s, None)
                self.rml.pop(s, None)

    def on_data(self, data):
        for s, sp in data.splits.items():
            if sp.type == SplitType.SPLIT_OCCURRED:
                self.events.add(s)
        for s, dv in data.dividends.items():
            self.events.add(s)
        super().on_data(data)

    def _apply_events(self, today):
        syms = [s for s in self.events if s in self.rc or s in self.rmc]
        self.events = set()
        if not syms:
            return
        hist = self.history(syms, 3, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        prev = {}
        if hist is not None and not hist.empty:
            for (s, t), c in hist["close"].items():
                if t.date() < today:
                    prev[s] = float(c)          # last bar before today, in today's QC adjustment
        for s in syms:
            base = self.rc[s][-1] if s in self.rc and len(self.rc[s]) else None
            if s not in prev or not base:
                self.c["ca_no_prev"] += 1
                continue
            f = prev[s] / base                   # QuantConnect's exact factor for this event
            self.c["ca_events"] += 1
            hf = self.qr_close[s][-2] / base if s in self.qr_close and len(self.qr_close[s]) > 1 else None
            if hf:
                self.c["ca_factor_diff_max"] = max(self.c["ca_factor_diff_max"], abs(hf / f - 1))
            for d in (self.rc, self.ro, self.rh, self.rl):
                if s in d:
                    d[s] = deque((x * f for x in d[s]), maxlen=d[s].maxlen)
            if s in self.rv:
                self.rv[s] = deque((x / f for x in self.rv[s]), maxlen=self.rv[s].maxlen)
            if s in self.rmc:
                self.rmc[s] = deque(([k, x * f] for k, x in self.rmc[s]), maxlen=self.rmc[s].maxlen)
            if s in self.rml:
                self.rml[s][1] *= f

    def _append_today(self, data, today):
        ym = today.year * 100 + today.month
        for s, b in data.bars.items():
            if s in self.rc and self.rlast.get(s) != today:
                self.rc[s].append(float(b.close)); self.rv[s].append(float(b.volume))
                self.ro[s].append(float(b.open)); self.rh[s].append(float(b.high)); self.rl[s].append(float(b.low))
                self.rlast[s] = today
            if s in self.rmc:
                last = self.rml.get(s)
                if last is not None and last[0] != ym:
                    self.rmc[s].append(list(last))
                self.rml[s] = [ym, float(b.close)]

    # ------------------------------------------------------------ bookkeeping of differences
    def _st(self, name):
        return self.c["strategies"].setdefault(name, {
            "evaluations": 0, "signals_H": 0, "signals_R": 0, "only_H": 0, "only_R": 0, "days": 0,
            "days_with_signal": 0, "days_top10_list_differs": 0, "top10_member_changes": 0,
            "max_rel_score_diff": 0.0, "examples": []})

    def _compare(self, name, sh, sr, today, n_eval, ascending=False, top=(10,)):
        st = self._st(name)
        st["days"] += 1
        st["evaluations"] += n_eval
        st["signals_H"] += len(sh); st["signals_R"] += len(sr)
        st["days_with_signal"] += int(bool(sh or sr))
        oh, orr = set(sh) - set(sr), set(sr) - set(sh)
        st["only_H"] += len(oh); st["only_R"] += len(orr)
        for k in sorted(oh | orr)[: max(0, N_EX - len(st["examples"]))]:
            st["examples"].append([str(today), self._sym_value.get(k, k), sh.get(k), sr.get(k)])
        for k in set(sh) & set(sr):
            d = abs(sh[k] - sr[k]) / max(abs(sr[k]), 1e-12)
            st["max_rel_score_diff"] = max(st["max_rel_score_diff"], d)
        rh, rr = _ranked(sh, ascending), _ranked(sr, ascending)
        for n in top:
            if rh[:n] != rr[:n]:
                st[f"days_top{n}_list_differs"] = st.get(f"days_top{n}_list_differs", 0) + 1
            a, b = set(rh[:n]), set(rr[:n])
            ch = max(len(a - b), len(b - a))       # names that would be bought/held under one input only
            st[f"top{n}_member_changes"] = st.get(f"top{n}_member_changes", 0) + ch
            if ch and len(st["examples"]) < N_EX:
                st["examples"].append([str(today), f"top{n}", [self._sym_value.get(k, k) for k in rh[:n]],
                                       [self._sym_value.get(k, k) for k in rr[:n]]])
        if top and len(sh) > 1 and len(sr) > 1 and set(sh) == set(sr):
            pos_r = {k: i for i, k in enumerate(rr)}
            st["max_rank_shift"] = max(st.get("max_rank_shift", 0), max(abs(i - pos_r[k]) for i, k in enumerate(rh)))
        return st

    def _flip(self, name, a, b, today, sym):
        st = self._st(name)
        st["evaluations"] += 1
        st["signals_H"] += int(a); st["signals_R"] += int(b)
        if a != b:
            st["only_H" if a else "only_R"] += 1
            if len(st["examples"]) < N_EX:
                st["examples"].append([str(today), sym.value])

    # ------------------------------------------------------------ daily
    def qr_on_close(self, data):
        today = self.time.date()
        self.n += 1
        self.c["sessions"] += 1
        self._apply_events(today)
        self._append_today(data, today)
        self._sym_value = {}
        elig = [s for s in self.qr_eligible if data.bars.contains_key(s) and not data.bars[s].is_fill_forward
                and s in self.qr_high and s in self.rh]
        for s in elig:
            self._sym_value[str(s.id)] = s.value
        if self.n % 21 == 0:
            self._check_reference(today)
            self._max_dev_windows()
        only = self.qr_params.get("only")
        if self.n % CHECK_EVERY == 0 and only is None:
            self.c["event_days_checked"] += 1
            self._event_strategies(elig, today)
        m = (today.year, today.month)
        if m != self.last_month:           # H008 ranks at the first close of each month
            self.last_month = m
            self.c["rank_dates_h008"] += 1
            self._h008(data, today)
            self._check_reference_months(today)
        if self.qr_is_last_session_of_month() and only is None:
            self.c["rank_dates_h011"] += 1
            self._h011(data, today)

    def _inputs(self, s, which):
        if which == "H":
            return self.qr_open[s], self.qr_high[s], self.qr_low[s], self.qr_close[s], self.qr_volume[s]
        return self.ro[s], self.rh[s], self.rl[s], self.rc[s], self.rv[s]

    EVENT_NAMES = ("H006 v1.0", "H006 v1.1", "H006 v1.2", "H007 v1.0", "H007 v1.1", "H007 v1.2",
                   "H009 v1.0/v1.1", "H009 v1.2", "H010 v1.0/v1.1", "H010 v1.2")
    EXIT_NAMES = ("exit H006 chandelier (held 20)", "exit H007 SMA20 (held 10)", "exit H010 gap-low (held 5)")

    @staticmethod
    def _event_decisions(ol, hl, ll, cl, vl):
        """Every event-strategy entry score (None = no signal) and exit decision for one stock, with
        the unchanged signal functions and each main.py's parameters (base variations)."""
        out = {}
        for name, n, use_v in (("H006 v1.0", 55, True), ("H006 v1.1", 252, True), ("H006 v1.2", 55, False)):
            out[name] = sig006.breakout_strength(hl, ll, cl, vl, n, 1.5, use_v)
        # S007 keeps the bandwidth of each of the last 252 bars (bandwidth_series(c)[-252:])
        bws = [sig007.bandwidth(cl[i - 19:i + 1]) for i in range(len(cl) - 252, len(cl))] if len(cl) >= 271 else []
        bw = sig007.contracted_bw(bws, 0.10)
        at = sig007.contracted_atr(hl, ll, cl, 0.6)
        e_tr = e_nt = False
        if bw is not None or at is not None:
            e_tr = sig007.expansion(hl, ll, cl, vl, use_trend=True)
            e_nt = e_tr or sig007.expansion(hl, ll, cl, vl, use_trend=False)
        out["H007 v1.0"] = bw if (bw is not None and e_tr) else None
        out["H007 v1.1"] = at if (at is not None and e_tr) else None
        out["H007 v1.2"] = bw if (bw is not None and e_nt) else None
        out["H009 v1.0/v1.1"] = sig009.volume_shock(hl, ll, cl, vl, 2.5, 1)
        out["H009 v1.2"] = sig009.volume_shock(hl, ll, cl, vl, 2.5, 5)
        for name, rh in (("H010 v1.0/v1.1", True), ("H010 v1.2", False)):
            r = sig010.gap_hold(ol, hl, ll, cl, vl, 0.02, 1.5, rh, 2.0)
            out[name] = None if r is None else r[0]
        exits = (sig006.exit_signal(hl, ll, cl, 20, 3.0, 60), sig007.exit_signal(cl, 10, 5, 40),
                 sig010.exit_signal(cl, 5, sig010.gap_day_low(ll, 5), 40))
        return out, exits

    def _event_strategies(self, elig, today):
        res = {k: ({}, {}) for k in self.EVENT_NAMES}
        same = 0
        for s in elig:
            sid = str(s.id)
            H = [list(x)[-280:] for x in self._inputs(s, "H")]
            R = [list(x)[-280:] for x in self._inputs(s, "R")]
            dh, eh = self._event_decisions(*H)
            if H == R:
                same += 1                       # identical inputs: identical decisions
                dr, er = dh, eh
            else:
                dr, er = self._event_decisions(*R)
            for name in self.EVENT_NAMES:
                if dh[name] is not None: res[name][0][sid] = dh[name]
                if dr[name] is not None: res[name][1][sid] = dr[name]
            for name, a, b in zip(self.EXIT_NAMES, eh, er):
                self._flip(name, a, b, today, s)
        self.c["event_stock_days"] = self.c.get("event_stock_days", 0) + len(elig)
        self.c["event_stock_days_identical_inputs"] = self.c.get("event_stock_days_identical_inputs", 0) + same
        for name, (sh, sr) in res.items():
            self._compare(name, sh, sr, today, len(elig), ascending=name.startswith("H007"))

    def _h008(self, data, today):
        spy_h, spy_r = self.qr_close.get(self.spy), self.rc.get(self.spy)
        if spy_h is None or spy_r is None:
            return
        res = {k: ({}, {}) for k in ("H008 v1.0", "H008 v1.1", "H008 v1.2")}
        n = 0
        for s in self.qr_eligible:
            if s not in self.qr_close or s not in self.rc or not data.bars.contains_key(s):
                continue
            n += 1
            self._sym_value[str(s.id)] = s.value
            for j, (c, m) in enumerate(((self.qr_close[s], spy_h), (self.rc[s], spy_r))):
                cl, ml = list(c), list(m)
                for name, win, scaled in (("H008 v1.0", 252, True), ("H008 v1.1", 126, True), ("H008 v1.2", 252, False)):
                    x = sig008.residual_score(cl, ml, win, 21, scaled)
                    if x is not None:
                        res[name][j][str(s.id)] = x
        for name, (sh, sr) in res.items():
            self._compare(name, sh, sr, today, n, top=(10, 20))
            self._dispersion(name, sh, n)

    def _dispersion(self, name, scores, n_eligible):
        """H008 non-degeneracy: how many stocks are scorable and how spread their scores are."""
        v = list(scores.values())
        d = self.c.setdefault("h008_dispersion", {}).setdefault(name, {
            "dates": 0, "eligible": 0, "scored": 0, "abs_below_1e-6": 0, "min_sd": None, "sd_sum": 0.0,
            "min_top_minus_median": None, "first": None})
        d["dates"] += 1
        d["eligible"] += n_eligible
        d["scored"] += len(v)
        d["abs_below_1e-6"] += sum(1 for x in v if abs(x) < 1e-6)
        if len(v) > 1:
            mu = sum(v) / len(v)
            sd = (sum((x - mu) ** 2 for x in v) / (len(v) - 1)) ** 0.5
            d["sd_sum"] += sd
            d["min_sd"] = sd if d["min_sd"] is None else min(d["min_sd"], sd)
            w = sorted(v)
            gap = w[-10] - w[len(w) // 2] if len(w) >= 10 else None
            if gap is not None:
                d["min_top_minus_median"] = gap if d["min_top_minus_median"] is None else min(d["min_top_minus_median"], gap)
        if d["first"] is None and v:
            d["first"] = [str(self.time.date()), len(v)]

    def _h011(self, data, today):
        y, mth = sig011.next_month(today.year, today.month)
        res = {k: ({}, {}) for k in ("H011 v1.0", "H011 v1.1", "H011 v1.2")}
        n = 0
        for s in self.qr_eligible:
            if s not in self.qr_month_close or s not in self.rmc or not data.bars.contains_key(s):
                continue
            n += 1
            self._sym_value[str(s.id)] = s.value
            for j, (mc, c) in enumerate(((self.qr_month_close[s], self.qr_close.get(s)), (self.rmc[s], self.rc.get(s)))):
                for name, lags, trend in (("H011 v1.0", 5, False), ("H011 v1.1", 10, False), ("H011 v1.2", 5, True)):
                    if trend:
                        t = sma(c, 200) if c is not None else None
                        if t is None or not list(c)[-1] > t:
                            continue
                    x = sig011.seasonal_score(mc, y, mth, lags)
                    if x is not None:
                        res[name][j][str(s.id)] = x
        for name, (sh, sr) in res.items():
            self._compare(name, sh, sr, today, n)

    # ------------------------------------------------------------ reference validity and H-vs-R size
    def _check_reference(self, today):
        syms = [self.qr_fixed[t] for t in FIXED if self.qr_fixed[t] in self.rc]
        hist = self.history(syms, self.WINDOW_BARS, Resolution.DAILY,
                            data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if hist is None or hist.empty:
            return
        fresh = {}
        for (s, t), row in hist[["open", "high", "low", "close", "volume"]].iterrows():
            fresh.setdefault(s, []).append([float(row[k]) for k in ("open", "high", "low", "close", "volume")])
        for s in syms:
            f = fresh.get(s, [])
            w = list(zip(self.ro[s], self.rh[s], self.rl[s], self.rc[s], self.rv[s]))
            k = min(len(f), len(w))
            for a, b in zip(w[-k:], f[-k:]):
                for x, y in zip(a, b):
                    self.c["ref_check_bars"] += 1
                    self.c["ref_check_max_dev"] = max(self.c["ref_check_max_dev"], abs(x - y) / max(abs(y), 1e-9))

    def _check_reference_months(self, today):
        syms = [self.qr_fixed[t] for t in FIXED if self.qr_fixed[t] in self.rmc]
        if today.month not in (1, 7):
            return
        hist = self.history(syms, self.MONTHLY_BARS * 23 + 30, Resolution.DAILY,
                            data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if hist is None or hist.empty:
            return
        last, reb = {}, {}
        for (s, t), c in hist["close"].items():
            if t.date() >= today:
                continue
            k = t.year * 100 + t.month
            p = last.get(s)
            if p is not None and p[0] != k:
                reb.setdefault(s, {})[p[0]] = p[1]
            last[s] = (k, float(c))
        for s, (k, c) in last.items():
            reb.setdefault(s, {})[k] = c
        for s in syms:
            for k, x in list(self.rmc[s])[1:]:
                y = reb.get(s, {}).get(k)
                if y:
                    self.c["ref_month_checks"] += 1
                    self.c["ref_month_max_dev"] = max(self.c["ref_month_max_dev"], abs(x - y) / abs(y))

    def _max_dev_windows(self):
        for s in list(self.rc)[:300]:
            for a, b in zip(self.qr_close[s], self.rc[s]):
                self.c["window_max_dev_H_vs_R"] = max(self.c["window_max_dev_H_vs_R"], abs(a - b) / max(abs(b), 1e-9))
        for s in list(self.rmc)[:300]:
            for (k1, a), (k2, b) in zip(self.qr_month_close[s], self.rmc[s]):
                self.c["month_max_dev_H_vs_R"] = max(self.c["month_max_dev_H_vs_R"], abs(a - b) / max(abs(b), 1e-9))

    def qr_on_end(self):
        self._qr_log("QRC61|summary|" + json.dumps(self.c, sort_keys=True, default=str))
