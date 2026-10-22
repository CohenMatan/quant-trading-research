# S033 v1.0 — H032 / OS-1 revised: R1 / R2 trading host (owner D282; frozen specification research/os/H032_spec.md
# section 9 and the implementation protocol research/os/H032_R_protocol.md, both SHA-256-pinned in qresearch.os1r).
# Modules (runner upload rules): qr_x807 (the pinned C-OS1 canary host X807, uploaded byte-identical), qr_os1, qr_ucr,
# qr_os1_books (a byte-identical copy of the LEAN-verified Phase 3 shadow-book engine, E984), qr_os1_trade.
# Plain-text source, no compression or encoding.
# The review pipeline is the canary's own code (this class subclasses it): universe repair, identity, SIC, the
# split-adjusted net share issuance, the fiscal-year filters, coverage and the mechanical start, betas and momentum.
# The history-only warm-up starts on 2009-05-01, so the stream the reviews see is the canary's; the official start is
# the frozen start review (2012-07-31).
# Books:
#   LEAN B1      the H032 strategy, traded in LEAN through the harness (D051 settled cash, 2% buffer, 15% gap reserve,
#                $5,000 minimum new position, 10% cap, at most 15 positions, $7 per order, slippage from the config).
#   shadow books the frozen controls (VB1, B0, MOM, B2 x 5, random x 5, beta-matched x 5) and a shadow replay of B1,
#                simulated with the same mechanics and costs in qr_os1_books.
#   indices      SPY total return (closes + dividends) and the frictionless equal-weight covered pools (all / vendor).
# Timing (protocol section 2): a review sees the stream of month-end session t, which reaches the algorithm in the
# selection stamped the next day; every book decides at the next harness close and its orders execute at the following
# open. Exits at review closes only; entries chosen at a review are retried at every close until the next review.
# Outputs: aggregate JSON lines 'OS1R|...' (daily equity of every book, review counts, costs, checks). No identifiers.
from AlgorithmImports import *
import json
import time
import numpy as np
import qr_os1 as O
import qr_os1_books as EN
import qr_os1_trade as T
import qr_x807 as X

MAXG = 20000
WARMUP_FROM = "2009-05-01"


class H032Trading(X.OS1Canary):
    USES_UNIVERSE = True

    def qr_initialize(self):
        e = self.qr
        p = self.qr_params
        if e.get("warmup_start") != WARMUP_FROM or e["end"] != "2021-12-31" or e["start"] != p["start_review"]:
            raise Exception("S033: warm-up from 2009-05-01, official start = the frozen start review, end 2021-12-31")
        # the pinned canary initialisation checks the canary's own window; LEAN starts on warmup_start = 2009-05-01, so
        # the stream observed by the reviews is the canary's
        self.qr = dict(e, start=WARMUP_FROM, warmup_start=None)
        try:
            super().qr_initialize()
        finally:
            self.qr = e
        self._qr_log_budget = 5000
        pf = self._qr_pf
        self.start_review = p["start_review"]
        self.EB = EN.Books(len(T.SHADOW), O.N, 10 ** 9, float(e["cash"]), slip=self._qr_slip,
                           fee=float(e["costs"]["commission_per_order"]), buffer=float(pf["cash_buffer"]),
                           gap=float(pf["gap_reserve"]), min_pos=float(pf["min_position_usd"]),
                           max_w=float(pf["max_position_weight"]))
        self.EB.fills = []
        self.EB.trace = {0}                              # the shadow replay of B1: fills kept for the P&L attribution
        self.g_of, self.key_of = {}, []
        self.open_px = np.full(MAXG, np.nan)
        self.last_close = np.full(MAXG, np.nan)
        self.has_bar = np.zeros(MAXG, dtype=bool)
        self.last_real = np.full(MAXG, -10 ** 6, dtype=np.int64)
        self.warned, self.dead = set(), set()
        self.symk = {}                                   # key -> Symbol of every name a book has targeted
        self.vendor_now = set()
        self.target = {b: [] for b in T.SHADOW}
        self.pend = {b: [] for b in T.SHADOW}
        self.lean_target, self.lean_pend = [], []
        self.pairs = {s: {} for s in O.SEEDS_BETA}
        self.decide = False
        self.review_t = None
        self.review_now = None
        self.ew_prev = None
        self.ew = []                                     # (period end, EW all, EW vendor, members, missing end)
        self.spy_prev, self.spy_div, self.spy_lvl = None, 0.0, 1.0
        self.dates, self.eq_lean, self.eq_spy = [], [], []
        self.eq_books = [[] for _ in T.SHADOW]
        self.npos_lean, self.maxw_lean = [], []
        self.costs = []                                  # (month, commission[], slippage[], notional[])
        self.rlog = []                                   # per-review trading records
        self.pnl = T.PnL()
        self.restored = {}                               # key -> restored (not vendor-eligible) at its latest review
        self.st = dict(decisions=0, lean_orders=0, lean_entries=0, lean_exits=0, lean_missing_symbol=0,
                       lean_vs_shadow_target_diff=0, first_target_diff=None, beta_attempted=0, beta_matched=0,
                       ew_missing_end=0, closes=0)
        self.t_trade = time.perf_counter()

    # ---------------------------------------------------------------- identifiers of the shadow engine
    def _g(self, key):
        g = self.g_of.get(key)
        if g is None:
            g = len(self.key_of)
            if g >= MAXG:
                raise Exception("S033: shadow stock index capacity exceeded")
            self.g_of[key] = g
            self.key_of.append(key)
        return g

    def _book_keys(self, b):
        """(held not exiting, busy = every occupied slot) of shadow book b, as keys."""
        st, sid, ps = self.EB.state[b], self.EB.sid[b], self.EB.psell[b]
        held = {self.key_of[int(sid[j])] for j in range(O.N) if st[j] == EN.HELD and not ps[j]}
        busy = {self.key_of[int(sid[j])] for j in range(O.N) if st[j] != EN.EMPTY}
        pend = {self.key_of[int(sid[j])] for j in range(O.N) if st[j] == EN.PENDING}
        return held, busy, pend

    def _lean_keys(self):
        """LEAN B1: (held not being sold, busy, pending buys, {key: Symbol} of holdings)."""
        hs = {}
        for kv in self.portfolio:
            if kv.value.invested:
                hs[str(kv.key.id)] = kv.key
        tk = list(self.transactions.get_open_order_tickets())
        pbuy = {str(t.symbol.id) for t in tk if float(t.quantity) > 0}
        psell = {str(t.symbol.id) for t in tk if float(t.quantity) < 0}
        held = {k for k in hs if k not in psell}
        return held, set(hs) | pbuy, pbuy, hs

    # ---------------------------------------------------------------- universe (the canary's review + subscriptions)
    def _category(self, f, px, adv):
        c = super()._category(f, px, adv)
        if c == "E":
            self.vendor_now.add(str(f.symbol.id))
        return c

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        self.vendor_now = set()
        self.review_now = None
        super()._qr_select(fl)
        if self.review_now is not None:
            need = self.review_now
            for f in fl:
                key = str(f.symbol.id)
                if key in need:
                    self.symk[key] = f.symbol
        return self._subscriptions()

    def _subscriptions(self):
        keys = set(self.lean_pend) | set(self.lean_target)
        for b in range(len(T.SHADOW)):
            keys |= self._book_keys(b)[1]
            keys |= set(self.pend[T.SHADOW[b]]) | set(self.target[T.SHADOW[b]])
        out = [self.symk[k] for k in sorted(keys) if k in self.symk]
        out += [kv.key for kv in self.portfolio if kv.value.invested]
        out += [t.symbol for t in self.transactions.get_open_order_tickets()]
        return list(dict.fromkeys(out))

    def _books(self, k, s_b1, s_vb1, s_b0, cov_pool, adv_of, c, Y, sic_of):
        """Review k (from the start review): the frozen inputs of every book, then each book's targets on its ACTUAL
        holdings (after the orders already placed). Execution waits for the next harness close."""
        t = c["t"]
        if self.review_t is None and t != self.start_review:
            raise Exception(f"S033: coverage start {t} differs from the frozen start review {self.start_review}")
        self.review_t = t
        mom = {}
        if k >= O.MOM_BACK:
            for key in cov_pool:
                r = self.row.get(key)
                if r is None:
                    continue
                v = O.momentum(float(self.mpx[r, k - O.MOM_BACK]), float(self.mpx[r, k - O.MOM_SKIP]))
                if v is not None:
                    mom[key] = (v, adv_of.get(key, 0.0))
        cov_sorted = sorted(cov_pool)
        bet = self._betas(cov_sorted)
        quint = O.quintiles(bet)
        rev = dict(s_b1=s_b1, s_vb1=s_vb1, s_b0=s_b0, mom=mom, pool_b2=sorted(s_b1), pool_cov=cov_sorted, quint=quint)
        held = {}
        for b, name in enumerate(T.SHADOW):
            h, busy, pend = self._book_keys(b)
            held[name] = h | pend
        lh, _, lpend, _ = self._lean_keys()
        lean_held = lh | lpend
        plans, n_new, self.pairs, att, mat = T.plans(rev, held, lean_held, self.pairs, k)
        self.st["beta_attempted"] += att
        self.st["beta_matched"] += mat
        self.lean_target = plans["LEAN"][0]
        self.lean_pend = T.pending_after(plans["LEAN"][1], lean_held)
        for name in T.SHADOW:
            self.target[name] = plans[name][0]
            self.pend[name] = T.pending_after(plans[name][1], held[name])
        if set(plans["LEAN"][0]) != set(plans["B1"][0]):
            self.st["lean_vs_shadow_target_diff"] += 1
            if self.st["first_target_diff"] is None:
                self.st["first_target_diff"] = t
        need = set()
        for name, (tg, _) in plans.items():
            need |= set(tg)
            for key in tg:
                self._g(key)
        self.review_now = need
        for key in s_b1:
            self.restored[key] = key not in self.vendor_now
        self.decide = True
        self._ew_step(k, cov_sorted, t)
        Y["b1_entries"] += n_new
        for key in self.lean_target:
            self._inc(Y["ff12_b1"], O.ff12(sic_of.get(key)))
        sizes = {name: len(plans[name][0]) for name in plans}
        self.rlog.append(dict(t=t, n_new=n_new, sizes=sizes, pool_b1=len(s_b1), pool_vb1=len(s_vb1), pool_b0=len(s_b0),
                              pool_cov=len(cov_pool), pool_mom=len(mom), beta_n=len(bet),
                              restored_in_target=sum(1 for x in self.lean_target if self.restored.get(x))))
        c.update(b1_new=n_new, pool_b1=len(s_b1), pool_vb1=len(s_vb1), pool_b0=len(s_b0), pool_cov=len(cov_pool),
                 pool_mom=len(mom), beta_n=len(bet), sizes=sizes)

    # ---------------------------------------------------------------- equal-weight covered pools (frictionless)
    def _end_prices(self, rows, s0, s1):
        """Adjusted close at session s1 for each row; a missing value falls back to the last close after s0."""
        out = np.full(len(rows), np.nan)
        for a, r in enumerate(rows):
            for s in range(s1, s0, -1):
                v = self.px[r, s % X.RING]
                if v == v and v > 0:
                    out[a] = v
                    break
        return out

    def _ew_step(self, k, cov_sorted, t):
        if self.ew_prev is not None:
            self._ew_close(t, self.sess_n)
        rows = [self.row[x] for x in cov_sorted if x in self.row]
        vrows = [self.row[x] for x in cov_sorted if x in self.row and x in self.vendor_now]
        p0 = self.px[rows, self.sess_n % X.RING] if rows else np.array([])
        v0 = self.px[vrows, self.sess_n % X.RING] if vrows else np.array([])
        self.ew_prev = dict(sess=self.sess_n, rows=rows, vrows=vrows, p0=p0.copy(), v0=v0.copy())

    def _ew_close(self, t, s1):
        e = self.ew_prev
        r_all, n_all, miss = T.ew_return(e["p0"], self._end_prices(e["rows"], e["sess"], s1))
        r_v, n_v, miss_v = T.ew_return(e["v0"], self._end_prices(e["vrows"], e["sess"], s1))
        self.st["ew_missing_end"] += miss
        self.ew.append((t, r_all, r_v, n_all, miss, n_v, miss_v))

    # ---------------------------------------------------------------- corporate actions (before the bars, as X984)
    def on_data(self, data):
        for sym, sp in data.splits.items():
            if sp.type != SplitType.SPLIT_OCCURRED:
                continue
            g = self.g_of.get(str(sym.id))
            if g is None:
                continue
            f = float(sp.split_factor)
            c0 = float(self.EB.cash[0])
            self.EB.split(g, f, float(sp.reference_price))
            self.pnl.add(g, float(self.EB.cash[0]) - c0)
            self.last_close[g] *= f
        for sym, dv in data.dividends.items():
            amt = float(dv.distribution)
            if sym == self.spy:
                self.spy_div += amt
                continue
            g = self.g_of.get(str(sym.id))
            if g is None:
                continue
            c0 = float(self.EB.cash[0])
            self.EB.dividend(g, amt)
            self.pnl.add(g, float(self.EB.cash[0]) - c0)
        for sym, dl in data.delistings.items():
            g = self.g_of.get(str(sym.id))
            if g is None:
                continue
            if dl.type == DelistingType.WARNING:
                self.warned.add(g)
            else:
                self.dead.add(g)
                self.EB.delist(g, float(self.last_close[g]))
                self._drain_fills()
        super().on_data(data)

    def _drain_fills(self):
        for b, kind, g, q, px, fee in self.EB.fills:
            self.pnl.fill(kind, g, q, px, fee)
        self.EB.fills = []

    # ---------------------------------------------------------------- one official close
    def qr_on_close(self, data):
        today = self.time.date()
        s = self._qr_session
        self.has_bar[:] = False
        spy_close = None
        for sym, bar in data.bars.items():
            if bar.is_fill_forward:
                continue
            if sym == self.spy:
                spy_close = float(bar.close)
                continue
            g = self.g_of.get(str(sym.id))
            if g is None:
                continue
            self.open_px[g], self.last_close[g] = float(bar.open), float(bar.close)
            self.has_bar[g] = True
            self.last_real[g] = s
        if spy_close is not None:
            if self.spy_prev:
                self.spy_lvl *= (spy_close + self.spy_div) / self.spy_prev
            self.spy_prev, self.spy_div = spy_close, 0.0
        EB = self.EB
        EB.open_fills(self.open_px, self.has_bar, s)
        EB.stale_exits(s, self.last_real, self.last_close)
        self._drain_fills()
        pv = EB.equity(self.last_close)
        decision = self.decide
        self.decide = False
        extra = np.zeros(EB.state.shape, dtype=bool)
        if decision:
            self.st["decisions"] += 1
            for b, name in enumerate(T.SHADOW):
                tgt = set(self.target[name])
                for j in range(O.N):
                    if EB.state[b, j] == EN.HELD and not EB.psell[b, j] and self.key_of[int(EB.sid[b, j])] not in tgt:
                        extra[b, j] = True
        due = EB.exits_due(s, extra)
        n_sells = due.sum(axis=1)
        for b, name in enumerate(T.SHADOW):
            _, busy, _ = self._book_keys(b)
            _, entries = T.exits_entries([], self.pend[name], set(), busy)
            if entries:
                EB.plan_entries(b, [self._g(x) for x in entries], self.last_close, float(pv[b]), int(n_sells[b]),
                                skip=self.warned)
        self._lean_step(decision)
        self._record(today)

    def _lean_step(self, decision):
        held, busy, _, hs = self._lean_keys()
        exits, entries = T.exits_entries(self.lean_target, self.lean_pend, held, busy, decision=decision)
        targets = {hs[x]: 0.0 for x in exits}
        w = self.qr_slot_weight(O.N)
        for x in entries:
            sym = self.symk.get(x)
            if sym is None:
                self.st["lean_missing_symbol"] += 1
                continue
            targets[sym] = w
        if targets:
            self.st["lean_orders"] += self.qr_rebalance(targets, tag="h032")
            self.st["lean_exits"] += len(exits)
            self.st["lean_entries"] += len(entries)

    def _record(self, today):
        self.st["closes"] += 1
        pv = float(self.portfolio.total_portfolio_value)
        self.dates.append(today.isoformat())
        self.eq_lean.append(round(pv, 2))
        self.eq_spy.append(round(self.spy_lvl, 8))
        eq = self.EB.equity(self.last_close)
        for b in range(len(T.SHADOW)):
            self.eq_books[b].append(round(float(eq[b]), 2))
        vals = [float(kv.value.holdings_value) for kv in self.portfolio if kv.value.invested]
        self.npos_lean.append(len(vals))
        self.maxw_lean.append(round(max(vals) / pv, 5) if vals and pv > 0 else 0.0)
        if self.qr_is_last_session_of_month():
            c, sl, nt = self.EB.reset_costs()
            self.costs.append((today.strftime("%Y-%m"), [round(float(x), 2) for x in c],
                               [round(float(x), 2) for x in sl], [round(float(x), 2) for x in nt]))

    # ---------------------------------------------------------------- end
    def qr_on_end(self):
        t1 = time.perf_counter()
        if self.ew_prev is not None:
            self._ew_close("end", self.sess_n)
        marks = {}
        EB = self.EB
        for j in range(O.N):
            if EB.state[0, j] == EN.HELD:
                g = int(EB.sid[0, j])
                marks[g] = marks.get(g, 0.0) + float(EB.qty[0, j]) * float(self.last_close[g])
        pnl = self.pnl.total(marks)
        attrib = dict(restored=0.0, vendor=0.0, unknown=0.0, n_restored=0, n_vendor=0)
        for g, v in pnl.items():
            fl = self.restored.get(self.key_of[g])
            grp = "unknown" if fl is None else ("restored" if fl else "vendor")
            attrib[grp] += v
            if fl is not None:
                attrib["n_" + grp] += 1
        meta = dict(protocol="H032 R", start_review=self.start_review, first_review_traded=self.rlog[0]["t"]
                    if self.rlog else None, reviews_traded=len(self.rlog), reviews_total=len(self.reviews),
                    checks=dict(self.checks, pit_violations_ext=self.ext.pit_violations), stats=self.st,
                    engine=EB.counts, warned=len(self.warned), dead=len(self.dead), stocks_indexed=len(self.key_of),
                    pnl_b1_shadow=attrib, books=list(T.SHADOW), slippage=self._qr_slip,
                    ucr_reference_sha256=self.sha["ucr"], os1_reference_sha256=self.sha["os1"],
                    collect_s=round(t1 - self.t0, 1), experiment_id=self.qr.get("experiment_id"))
        dump = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"))
        self._qr_log("OS1R|meta|" + dump(meta))
        self._qr_log("OS1R|reviews|" + dump([dict(c, t=c["t"]) for c in self.reviews]))
        self._qr_log("OS1R|rlog|" + dump(self.rlog))
        self._qr_log("OS1R|ew|" + dump(self.ew))
        self._qr_log("OS1R|costs|" + dump(self.costs))
        self._qr_log("OS1R|dates|" + ",".join(self.dates))
        self._qr_log("OS1R|eq|LEAN|" + ",".join(f"{v:.2f}" for v in self.eq_lean))
        self._qr_log("OS1R|eq|SPY|" + ",".join(f"{v:.8f}" for v in self.eq_spy))
        for b, name in enumerate(T.SHADOW):
            self._qr_log(f"OS1R|eq|{name}|" + ",".join(f"{v:.2f}" for v in self.eq_books[b]))
        self._qr_log("OS1R|npos|" + ",".join(str(v) for v in self.npos_lean))
        self._qr_log("OS1R|maxw|" + ",".join(f"{v:.5f}" for v in self.maxw_lean))
        self._qr_log("OS1R|years|" + dump({str(y): dict(ff12_b1=Y["ff12_b1"], b1_entries=Y["b1_entries"])
                                          for y, Y in sorted(self.years.items())}))
