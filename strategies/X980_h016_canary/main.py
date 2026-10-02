# S016 — H016 gross profitability (research/hypotheses/H016.md; frozen spec research/phase2/H016_spec.md) and its
# controls. ONE code path for every book; only params differ:
#   book "gpa"    : candidate — at each quarterly rebalance rank the H016 universe by GP/A, hold the top `slots`
#   book "random" : control — same universe, slots, schedule, costs and holding rules; ranking = fixed seeded random key
#   book "ew"     : same-universe equal-weight benchmark — every H016-universe member at (1 - buffer)/n, rebalanced on
#                   the first session of each month with a 25% band (approved B901 mechanics), large paper notional
# H016 universe on T (identical for every book): harness-eligible (US common, NYSE/Nasdaq/AMEX, PIT market cap >= $2B,
# price >= $5, ADV20 >= $5M, SEC correction layer) AND not financial/REIT (qr_industry, SEC SIC at filing) AND GP/A
# computable from historically available data (qr_h016.gpa). Data: frozen fundamental infrastructure v1; every company
# with fundamentals is observed daily from the harness's history-only warm-up (qr_fundamentals.observe_vendor).
# Orders: next-open orders via the harness only (D051 settled-cash funding, 2% buffer, 15% gap reserve; H016 portfolio
# rules: 20 slots, $4,000 minimum new position). Exits at a rebalance are the holdings outside the new selection;
# entries are bought (reserve-scaled by the order planner) and retried at each close until the next rebalance; each
# newly opened position gets AT MOST ONE top-up toward its original target, evaluated once at the first close after its
# initial fill (qr_h016.plan_topups, minimum $250); nothing else is ever resized. No other exit: delistings/untradeable
# holdings are handled by the harness. Outputs: counts and identifiers only (no returns are logged).
from AlgorithmImports import *
import hashlib
import json
from qr_harness import QRAlgorithm
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, financial_format, observe_vendor
from qr_industry import classify, excluded
from qr_h016 import MIN_TOPUP_USD, gpa, is_rebalance_day, plan_selection, plan_topups, rank_gpa, rank_random


def get(obj, path):
    for p in path.split("."):
        obj = getattr(obj, p)
    return obj


class GrossProfitability(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        p = self.qr_params
        self._qr_log_budget = 20000
        self.book = p["book"]
        self.slots = int(p.get("slots", 20))
        self.seed = int(p.get("seed", 0))
        self.months = tuple(int(m) for m in p.get("months", [3, 6, 9, 12]))
        self.max_age = p.get("max_age_days")
        self.canary = bool(p.get("canary", False))
        if self.qr_sec is None:
            raise Exception("S016 needs universe.sec_corrections (frozen data infrastructure v1)")
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS, holds=self.qr_timing_holds, releases=self.qr_quarantine_releases,
                              blocked=self.qr_restatement_blocks, field_releases=self.qr_field_releases)
        self.seen = set()
        self.prev_session = None
        self.last_ew_month = None
        self.pending = []                # entries chosen at the last rebalance not yet held
        self.target_value = {}           # key -> original equal-weight target value of a new position
        self.awaiting = set()            # new positions whose single top-up has not been evaluated yet
        self.st = {"rebalances": 0, "universe_sum": 0, "entries_decided": 0, "exits_decided": 0, "entry_orders": 0,
                   "topup_orders": 0, "pending_left_at_rebalance": 0, "max_holdings": 0, "pit_violations": 0, "topup_evaluations": 0,
                   "topups_below_threshold_or_unfunded": 0, "max_topups_per_position": 0, "min_entry_planned_usd": None,
                   "min_topup_planned_usd": None, "max_topup_over_target_usd": 0.0,
                   "financial_in_universe": 0, "ew_rebalances": 0}
        self.n_topups = {}               # key -> top-ups placed since the position's entry decision (canary check)

    # ---------------------------------------------------------------- data: observe every company daily
    def _qr_select(self, fundamental):
        fl = list(fundamental)
        out = super()._qr_select(fl)
        today = self.time.date()
        corr = {str(s.id) for s in self.qr_corrected}
        for f in fl:
            sid = str(f.symbol.id)
            if sid in corr or not f.has_fundamental_data:
                continue
            observe_vendor(self.store, sid, f, today, get, self.seen)
        for s in self.qr_corrected:
            self.qr_sec.feed(str(s.id), today, self.store)
        return out

    def qr_select_universe(self, eligible):
        return [f.symbol for f in eligible]          # every eligible name subscribed (prices at decision time)

    # ---------------------------------------------------------------- the H016 universe on T
    def universe(self, today):
        """[(symbol, key, GP/A)] of the H016 universe on `today` (identical for every book)."""
        out = []
        for s in self.qr_eligible:
            key = str(s.id)
            r = self.store.record(key, today)
            ff = financial_format(r.values) if r is not None else None
            sic = self.qr_sic.sic_on(key, today) if self.qr_sic is not None else None
            cat, _src = classify(sic, ff)
            if excluded(cat):
                continue
            v, det = gpa(self.store, key, today, self.max_age)
            if v is None:
                continue
            if self.canary:
                if any(fd >= str(today) for fd in det["filed"]) or det["assets_filed"] >= str(today):
                    self.st["pit_violations"] += 1
                if cat in ("financial", "REIT", "financial-format"):
                    self.st["financial_in_universe"] += 1
            out.append((s, key, v))
        return out

    # ---------------------------------------------------------------- decisions (close of T, executed T+1 open)
    def qr_on_close(self, data):
        today = self.time.date()
        prev, self.prev_session = self.prev_session, today
        if self.book == "ew":
            m = (today.year, today.month)
            if m != self.last_ew_month:
                self.last_ew_month = m
                self._ew(today)
            return
        if is_rebalance_day(today, prev, self.months):
            self._rebalance(today)
        else:
            self._fill(today)
        n = sum(1 for kv in self.portfolio if kv.value.invested)
        self.st["max_holdings"] = max(self.st["max_holdings"], n)

    def _held(self):
        return {str(kv.key.id): kv.key for kv in self.portfolio if kv.value.invested}

    def _rebalance(self, today):
        u = self.universe(today)
        sym = {k: s for s, k, _ in u}
        if self.book == "gpa":
            ranked = rank_gpa({k: v for _, k, v in u})
        else:
            ranked = rank_random(list(sym), self.seed)
        held = self._held()
        sel, exits, entries = plan_selection(ranked, held, self.slots)
        self.st["rebalances"] += 1
        self.st["universe_sum"] += len(u)
        self.st["exits_decided"] += len(exits)
        self.st["entries_decided"] += len(entries)
        self.st["pending_left_at_rebalance"] += len([s for s in self.pending if str(s.id) not in held])
        self.pending = [sym[k] for k in entries]
        w = self.qr_slot_weight(self.slots)
        pv = float(self.portfolio.total_portfolio_value)
        self.target_value = {k: v for k, v in self.target_value.items() if k in sel}
        self.awaiting = {k for k in self.awaiting if k in sel}
        for k in entries:
            self.target_value[k] = w * pv            # the ORIGINAL equal-weight target of the new position
            self.n_topups[k] = 0
            self.awaiting.add(k)                     # its single top-up is evaluated after the initial fill
        if exits:
            self._submit({held[k]: 0.0 for k in exits}, "s016_exit")
        self._entries(w)
        self._topups()
        h = hashlib.sha256("|".join(sel).encode()).hexdigest()[:12]
        self._qr_log(f"RB|{today}|{len(self.qr_eligible)}|{len(u)}|{len(exits)}|{len(entries)}|{h}")
        if self.canary and self.book != "gpa":
            self._shadow_gpa(today)

    def _fill(self, today):
        """Between rebalances: retry unfilled entries (D051: as settled cash allows), then evaluate the single top-up
        of every position whose initial fill has just completed. Nothing else is ever resized."""
        if self.pending:
            self._entries(self.qr_slot_weight(self.slots))
        self._topups()

    def _entries(self, w):
        held = self._held()
        self.pending = [s for s in self.pending if str(s.id) not in held]
        if self.pending:
            n0 = self._qr_stats["orders"]
            self._submit({s: w for s in self.pending}, "s016_entry")
            self.st["entry_orders"] += self._qr_stats["orders"] - n0
            want = set(self.pending)
            for t in self.transactions.get_open_order_tickets():
                if t.symbol in want and float(t.quantity) > 0:
                    v = float(t.quantity) * float(self.securities[t.symbol].price)
                    m = self.st["min_entry_planned_usd"]
                    self.st["min_entry_planned_usd"] = v if m is None else min(m, v)

    def _topups(self):
        """One-time top-up (qr_h016.plan_topups): each newly opened position is evaluated exactly once, at the first
        close after its initial fill, toward its original target, from settled cash net of orders placed this close."""
        pf = self._qr_pf
        pv = float(self.portfolio.total_portfolio_value)
        gap = float(pf.get("gap_reserve", 0.0))
        held = self._held()
        open_syms = {t.symbol for t in self.transactions.get_open_order_tickets()}
        cands = []
        for k in sorted(self.awaiting):
            s = held.get(k)
            if s is None or s in open_syms:
                continue                              # not yet filled (or its order still open)
            price = float(self.securities[s].price)
            cands.append((k, self.target_value[k], float(self.portfolio[s].holdings_value), price))
        if not cands:
            return
        reserved = 0.0
        for t in self.transactions.get_open_order_tickets():
            q = float(t.quantity)
            if q > 0:
                px = float(self.securities[t.symbol].price)
                reserved += q * px * (1 + self._qr_slip) * (1 + gap) + self._qr_fee_est(q)
        plan = plan_topups(cands, float(self.portfolio.cash), pv, float(pf.get("cash_buffer", 0.02)), gap,
                           self._qr_slip, self._qr_fee_est(1), reserved, MIN_TOPUP_USD)
        self.st["topup_evaluations"] += len(cands)
        for k, _t, _v, price in cands:
            self.awaiting.discard(k)                  # at most one top-up opportunity per new position
        targets = {}
        cur = {k: (v, price) for k, _t, v, price in cands}
        for k, qty in plan.items():
            s = held[k]
            v, price = cur[k]
            self.n_topups[k] = self.n_topups.get(k, 0) + 1
            self.st["max_topups_per_position"] = max(self.st["max_topups_per_position"], self.n_topups[k])
            m = self.st["min_topup_planned_usd"]
            self.st["min_topup_planned_usd"] = qty * price if m is None else min(m, qty * price)
            self.st["max_topup_over_target_usd"] = max(self.st["max_topup_over_target_usd"],
                                                       v + qty * price - self.target_value[k])
            have = float(self.portfolio[s].quantity)
            targets[s] = (have + qty + 0.5) * float(self.securities[s].price) / pv
        if targets:
            n0 = self._qr_stats["orders"]
            self._submit(targets, "s016_topup")
            self.st["topup_orders"] += self._qr_stats["orders"] - n0
        self.st["topups_below_threshold_or_unfunded"] += len(cands) - len(plan)

    def _submit(self, targets, tag):
        if not targets:
            return 0
        return self.qr_rebalance(targets, tag=tag)

    def _shadow_gpa(self, today):
        """Canary only: the GP/A ranking is computed (never traded, never valued) to verify its point-in-time
        inputs; only counts and a selection hash are logged."""
        u = self.universe(today)
        sel = rank_gpa({k: v for _, k, v in u})[:self.slots]
        self._qr_log(f"SH|{today}|{len(u)}|{hashlib.sha256('|'.join(sel).encode()).hexdigest()[:12]}")

    def _ew(self, today):
        u = self.universe(today)
        members = [s for s, _, _ in u if self.securities.contains_key(s) and self.securities[s].price > 0]
        if not members:
            return
        self.st["ew_rebalances"] += 1
        self.st["universe_sum"] += len(members)
        w = (1.0 - float(self._qr_pf.get("cash_buffer", 0.02))) / len(members)
        self.qr_rebalance({s: w for s in members}, tag="ew_rebal", liquidate_others=True,
                          band=float(self.qr_params.get("band", 0.25)))

    def qr_on_end(self):
        self._qr_log("QRS016|summary|" + json.dumps(self.st, sort_keys=True))
