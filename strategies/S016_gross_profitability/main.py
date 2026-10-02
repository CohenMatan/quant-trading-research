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
# Orders: next-open orders via the harness only (D051 settled-cash funding); exits at a rebalance are the holdings
# outside the new selection; entries are bought in rank order as settled cash allows and retried at each close until
# the next rebalance; continuing holdings are not resized (optionally, 'build_positions': a new position is topped up
# to its slot value while below `build_floor` of it, from settled cash only). No other exit: delistings/untradeable
# holdings are handled by the harness. Outputs: counts and identifiers only (no returns are logged).
from AlgorithmImports import *
import hashlib
import json
from qr_harness import QRAlgorithm
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, financial_format, observe_vendor
from qr_industry import classify, excluded
from qr_h016 import gpa, is_rebalance_day, plan_selection, rank_gpa, rank_random


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
        self.build = bool(p.get("build_positions", False))
        self.build_floor = float(p.get("build_floor", 0.90))
        self.canary = bool(p.get("canary", False))
        # "scaled": entries submitted together, the harness scales them to settled cash (D051);
        # "affordable": only as many entries as settled cash funds at full slot size are submitted, in rank order
        self.entry_funding = p.get("entry_funding", "scaled")
        if self.qr_sec is None:
            raise Exception("S016 needs universe.sec_corrections (frozen data infrastructure v1)")
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS, holds=self.qr_timing_holds, releases=self.qr_quarantine_releases,
                              blocked=self.qr_restatement_blocks, field_releases=self.qr_field_releases)
        self.seen = set()
        self.prev_session = None
        self.last_ew_month = None
        self.pending = []                # entries chosen at the last rebalance not yet held
        self.slot_value = {}             # key -> slot value at its entry decision (build_positions)
        self.built = set()
        self.st = {"rebalances": 0, "universe_sum": 0, "entries_decided": 0, "exits_decided": 0, "entry_orders": 0,
                   "topup_orders": 0, "pending_left_at_rebalance": 0, "max_holdings": 0, "pit_violations": 0,
                   "financial_in_universe": 0, "ew_rebalances": 0}

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
        self.st["pending_left_at_rebalance"] += len([k for k in self.pending if k not in held])
        self.pending = [sym[k] for k in entries]
        self.slot_value = {k: v for k, v in self.slot_value.items() if k in sel and k in held}
        self.built = {k for k in self.built if k in sel}
        w = self.qr_slot_weight(self.slots)
        pv = float(self.portfolio.total_portfolio_value)
        for k in entries:
            self.slot_value[k] = w * pv
        targets = {held[k]: 0.0 for k in exits}
        targets.update({s: w for s in self._fundable(self.pending, w)})
        self.st["entry_orders"] += self._submit(targets, "s016_rebal")
        h = hashlib.sha256("|".join(sel).encode()).hexdigest()[:12]
        self._qr_log(f"RB|{today}|{len(self.qr_eligible)}|{len(u)}|{len(exits)}|{len(entries)}|{h}")

    def _fill(self, today):
        """Retry pending entries (bought in rank order as settled cash allows); optional position building."""
        held = self._held()
        self.pending = [s for s in self.pending if str(s.id) not in held]
        targets = {}
        if self.pending:
            w = self.qr_slot_weight(self.slots)
            targets.update({s: w for s in self._fundable(self.pending, w)})
        if self.build:
            for k, s in held.items():
                if k in self.built or k not in self.slot_value:
                    continue
                val = float(self.portfolio[s].holdings_value)
                if val >= self.build_floor * self.slot_value[k]:
                    self.built.add(k)
                    continue
                targets[s] = self.slot_value[k] / float(self.portfolio.total_portfolio_value)
        if targets:
            n_before = self._qr_stats["orders"]
            self._submit(targets, "s016_fill")
            self.st["topup_orders"] += self._qr_stats["orders"] - n_before

    def _fundable(self, entries, w):
        if self.entry_funding != "affordable":
            return list(entries)
        pv = float(self.portfolio.total_portfolio_value)
        pf = self._qr_pf
        per = w * pv * (1 + self._qr_slip) * (1 + float(pf.get("gap_reserve", 0.0))) + self._qr_fee_est(1)
        k = int(max(0.0, float(self.portfolio.cash) - float(pf.get("cash_buffer", 0.02)) * pv) // per)
        return list(entries)[:k]

    def _submit(self, targets, tag):
        if not targets:
            return 0
        return self.qr_rebalance(targets, tag=tag)

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
