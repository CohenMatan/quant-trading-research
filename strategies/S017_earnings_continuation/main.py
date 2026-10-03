# S017 — H017 earnings-event continuation (research/hypotheses/H017.md; frozen spec research/phase2/H017_spec.md) and
# its controls. ONE code path for every book; only params differ:
#   book "candidate" : the day's qualifying signals (AR >= trailing 90th percentile and AR > 0), ranked by AR
#   book "random"    : the same events, timing, sizing, holding, costs and cash; at most k_t entries (k_t = the day's
#                      candidate signal count) chosen among ALL universe events of the day by SHA-256("seed|sid|E")
#   book "ew"        : same-universe equal weight (eligible AND a verified domestic event filer with an event decided in
#                      the trailing 252 sessions), first session of each month, 25% band (B901 mechanics)
# Events: the frozen H017 event table v1 (Event Data v1; qr_h017_events, SHA-256 checked on load). Universe on the
# decision session: harness-eligible (US common, NYSE/Nasdaq/AMEX, PIT market cap >= $2B, price >= $5, ADV20 >= $5M,
# SEC correction layer); financials included.
# Timing: event session E from the SEC acceptance time; reaction from the adjusted closes of E-1 and E+1 (and SPY's),
# all three closes E-1, E, E+1 required (real bars); decision at the close of E+1; market-on-open entry at E+2 via the
# harness (D051 settled cash, 2% buffer, 15% gap reserve, $4,000 minimum, 10% cap). Exit order at the close of the 59th
# session after entry (executes at entry + 60 sessions). No top-up, no queue, no replacement; events of held or pending
# stocks are ignored. History-only warm-up (harness warmup_start): reactions of universe events feed the breakpoint
# history; no decision, order or equity before the official start. Outputs: counts, identifiers, the daily
# breakpoint and each entry's planned weight at placement (EP lines) only (no returns are logged).
from AlgorithmImports import *
from datetime import date, datetime, timedelta
import hashlib
import json
from qr_harness import QRAlgorithm, in_warmup
from qr_h017 import (HOLD_SESSIONS, SLOTS, TOP_QUANTILE, Breakpoints, bar_date, ew_member, exit_due, free_slots,
                     plan_entries, qualifies, rank_random, rank_signals, reaction)
from qr_h017_events import SHA256 as EVENTS_SHA256, load_events


class EarningsContinuation(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        p = self.qr_params
        self._qr_log_budget = 20000
        self.book = p["book"]
        if self.book not in ("candidate", "random", "ew"):
            raise Exception(f"S017: unknown book {self.book!r}")
        self.seed = int(p.get("seed", 0))
        self.slots = int(p.get("slots", SLOTS))
        self.hold = int(p.get("hold_sessions", HOLD_SESSIONS))
        self.lag = int(p.get("reaction_lag", 1))          # 1: two-session reaction (frozen); 0: perturbation P4
        self.canary = bool(p.get("canary", False))
        if self.qr_sec is None:
            raise Exception("S017 needs universe.sec_corrections (frozen data infrastructure v1)")
        t = load_events()                                 # raises on a hash mismatch
        epoch = date.fromisoformat(t["epoch"])
        sids = t["sids"]
        self.by_E = {}
        for i, d, c in t["events"]:
            self.by_E.setdefault(epoch + timedelta(days=d), []).append((sids[i], c))
        self.bp = Breakpoints(q=float(p.get("quantile", TOP_QUANTILE)))
        self.sess = []                                    # LEAN session dates (real SPY bars), from the LEAN start
        self.done = None
        self.last_dec = {}                                # sid -> latest decision-session index of a table event
        self.last_ew_month = None
        self.st = {"events_table_sha256": EVENTS_SHA256, "table_events": len(t["events"]), "decision_days": 0,
                   "warmup_decision_days": 0, "events_seen": 0, "events_universe": 0, "events_valid": 0,
                   "events_missing_close": 0, "signals": 0, "entries_planned": 0, "entry_orders": 0,
                   "exit_orders": 0, "held_events_ignored": 0, "entries_over_kt": 0, "entries_over_free": 0,
                   "threshold_future_violations": 0, "bars_after_today": 0, "today_close_from_slice": 0,
                   "first_trade_decision": None, "min_hist_official": None, "days_no_threshold_official": 0,
                   "max_holdings": 0, "non_session_close_days": 0, "ew_rebalances": 0, "universe_sum": 0,
                   "skipped_first_sessions": 0, "max_entry_rank_pos": 0}

    def qr_select_universe(self, eligible):
        return [f.symbol for f in eligible]               # every eligible name subscribed (prices at decision time)

    # ---------------------------------------------------------------- daily step (history in warm-up, trading after)
    def on_data(self, data):
        super().on_data(data)                             # harness: windows, sessions, and qr_on_close after warm-up
        if data.bars.count == 0 or self.time.hour < 9:
            return
        today = self.time.date()
        if self.done != today and in_warmup(today, self.qr_official_start):
            self._day(data, today, trade=False)

    def qr_on_close(self, data):
        self._day(data, self.time.date(), trade=True)

    def _day(self, data, today, trade):
        self.done = today
        if self._qr_session_day != today:                 # not a trading session (no real SPY bar today)
            self.st["non_session_close_days"] += 1
            return
        if not self.sess or self.sess[-1] != today:
            self.sess.append(today)
        t = len(self.sess) - 1
        exits = self._exits() if trade and self.book != "ew" else []
        if t - self.lag - 1 < 0:
            self.st["skipped_first_sessions"] += 1
            evs, E = [], None
        else:
            E = self.sess[t - self.lag]
            evs = self.by_E.get(E, [])
        valid, n_univ = self._reactions(data, today, t, E, evs) if evs else ([], 0)
        thr, n_hist, newest = self.bp.threshold(t)
        if newest is not None and newest >= t:
            self.st["threshold_future_violations"] += 1
        signals = [(sid, ar) for sid, ar, _c in valid if qualifies(ar, thr)]
        k = len(signals)
        for _sid, ar, _c in valid:                        # today's reactions enter the history AFTER today's breakpoint
            self.bp.add(t, ar)
        if trade:
            self.st["decision_days"] += 1
            if self.st["first_trade_decision"] is None:
                self.st["first_trade_decision"] = str(today)
            if evs:
                m = self.st["min_hist_official"]
                self.st["min_hist_official"] = n_hist if m is None else min(m, n_hist)
                if thr is None:
                    self.st["days_no_threshold_official"] += 1
            self.st["signals"] += k
        else:
            self.st["warmup_decision_days"] += 1
        entries, free = [], None
        if trade and self.book != "ew":
            entries, free = self._entries(today, E, valid, signals, k, exits)
        elif trade and self.book == "ew":
            self._ew(today, t)
        if evs or entries or exits:
            thr_s = "" if thr is None else f"{thr:.6f}"
            self._qr_log(f"{'EV' if trade else 'WEV'}|{today}|{len(evs)}|{n_univ}|{len(valid)}|{n_hist}|{thr_s}|{k}|"
                         f"{'' if free is None else free}|{len(entries)}|{len(exits)}")
        n = sum(1 for kv in self.portfolio if kv.value.invested)
        self.st["max_holdings"] = max(self.st["max_holdings"], n)

    def _reactions(self, data, today, t, E, evs):
        """[(sid, AR, class)] of today's universe events with all required closes, and the universe event count."""
        elig = {str(s.id): s for s in self.qr_eligible}
        uni = []
        for sid, cls in evs:
            self.st["events_seen"] += 1
            self.last_dec[sid] = t
            if sid in elig:
                uni.append((sid, cls))
        self.st["events_universe"] += len(uni)
        if not uni:
            return [], 0
        d_m1, d_e = self.sess[t - self.lag - 1], self.sess[t - self.lag]
        need = (d_m1, d_e, today)
        syms = [elig[sid] for sid, _ in uni]
        closes = self._closes(syms + [self.spy], d_m1, today, data)
        spy = closes.get(self.spy, {})
        out = []
        for sid, cls in uni:
            c = closes.get(elig[sid], {})
            if not all(d in c for d in need) or not all(d in spy for d in need):
                self.st["events_missing_close"] += 1
                continue
            ar = reaction(c[d_m1], c[today], spy[d_m1], spy[today])
            if ar is None:
                self.st["events_missing_close"] += 1
                continue
            out.append((sid, ar, cls))
        self.st["events_valid"] += len(out)
        return out, len(uni)

    def _closes(self, symbols, start, today, data):
        """{symbol: {session date: adjusted close}} of REAL bars from `start` through today (point in time: SCALED_RAW
        is adjusted only for actions up to now). Today's close comes from the current slice if history lacks it."""
        out = {s: {} for s in symbols}
        hist = self.history(symbols, datetime(start.year, start.month, start.day), self.time, Resolution.DAILY,
                            fill_forward=False, data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        if hist is not None and not hist.empty:
            for (sym, tt), c in hist["close"].items():
                d = bar_date(tt)
                if d > today:
                    self.st["bars_after_today"] += 1
                    continue
                if sym in out:
                    out[sym][d] = float(c)
        for s in symbols:
            if today not in out[s] and data.bars.contains_key(s) and not data.bars[s].is_fill_forward:
                out[s][today] = float(data.bars[s].close)
                self.st["today_close_from_slice"] += 1
        return out

    # ---------------------------------------------------------------- trading books
    def _held(self):
        return {str(kv.key.id): kv.key for kv in self.portfolio if kv.value.invested}

    def _exits(self):
        pending_sells = {t.symbol for t in self.transactions.get_open_order_tickets() if float(t.quantity) < 0}
        out = []
        for sid, s in sorted(self._held().items()):
            if s not in pending_sells and exit_due(self.qr_sessions_held(s), self.hold):
                out.append(s)
        return out

    def _entries(self, today, E, valid, signals, k, exits):
        held = self._held()
        pend = {str(t.symbol.id) for t in self.transactions.get_open_order_tickets() if float(t.quantity) > 0}
        free = free_slots(self.slots, len(held), len(pend - set(held)))
        blocked = set(held) | pend
        if self.book == "candidate":
            ranked = rank_signals(signals)
        else:
            ranked = rank_random([(sid, str(E)) for sid, _a, _c in valid], self.seed)
        entries = plan_entries(ranked, blocked, free, k)
        self.st["held_events_ignored"] += sum(1 for x in ranked[:k] if x in blocked)
        if len(entries) > k:
            self.st["entries_over_kt"] += 1
        if len(entries) > free:
            self.st["entries_over_free"] += 1
        elig = {str(s.id): s for s in self.qr_eligible}
        targets = {s: 0.0 for s in exits}
        w = self.qr_slot_weight(self.slots)
        for sid in entries:
            targets[elig[sid]] = w
        if targets:
            n0 = self._qr_stats["orders"]
            self.qr_rebalance(targets, tag="s017")
            placed = self._qr_stats["orders"] - n0
            self.st["exit_orders"] += len(exits)
            self.st["entry_orders"] += placed - len(exits)
            pv = float(self.portfolio.total_portfolio_value)
            want = {elig[sid]: sid for sid in entries}
            for tk in self.transactions.get_open_order_tickets():
                if tk.symbol in want and float(tk.quantity) > 0:
                    # planned weight at placement: quantity x decision-close price / equity (the 10% cap applies here)
                    w_pl = float(tk.quantity) * float(self.securities[tk.symbol].price) / pv
                    self.st["max_planned_entry_weight"] = max(self.st.get("max_planned_entry_weight", 0.0), w_pl)
                    self._qr_log(f"EP|{today}|{want[tk.symbol]}|{int(tk.quantity)}|{w_pl:.6f}")
        self.st["entries_planned"] += len(entries)
        for pos, sid in enumerate(entries):
            self.st["max_entry_rank_pos"] = max(self.st["max_entry_rank_pos"], ranked.index(sid))
            self._qr_log(f"EN|{today}|{sid}|{E}|{pos}")
        for s in exits:
            self._qr_log(f"XT|{today}|{s.id}|{self.qr_sessions_held(s)}")
        return entries, free

    def _ew(self, today, t):
        m = (today.year, today.month)
        if m == self.last_ew_month:
            return
        self.last_ew_month = m
        members = [s for s in self.qr_eligible if ew_member(self.last_dec.get(str(s.id)), t)
                   and self.securities.contains_key(s) and self.securities[s].price > 0]
        if not members:
            return
        self.st["ew_rebalances"] += 1
        self.st["universe_sum"] += len(members)
        w = (1.0 - float(self._qr_pf.get("cash_buffer", 0.02))) / len(members)
        self.qr_rebalance({s: w for s in members}, tag="ew_rebal", liquidate_others=True,
                          band=float(self.qr_params.get("band", 0.25)))
        h = hashlib.sha256("|".join(sorted(str(s.id) for s in members)).encode()).hexdigest()[:12]
        self._qr_log(f"EW|{today}|{len(members)}|{h}")

    def qr_on_end(self):
        lo, hi = (self.sess[0], self.sess[-1]) if self.sess else (None, None)
        ss = set(self.sess)
        self.st["table_E_not_lean_session"] = sum(len(v) for E, v in self.by_E.items()
                                                  if lo is not None and lo <= E <= hi and E not in ss)
        self.st["lean_sessions"] = len(self.sess)
        self.st["first_session"] = str(lo)
        self._qr_log("QRS017|summary|" + json.dumps(self.st, sort_keys=True))
