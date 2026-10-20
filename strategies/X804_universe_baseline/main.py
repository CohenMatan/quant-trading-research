# X804 v1.0 — Universe Baseline Audit UB-1 (owner D263; research/rr/universe_baseline/UB_protocol.md, frozen and
# SHA-256-pinned in qresearch.rr_ub with this host and qr_ub). Infrastructure only: NO orders, NO subscriptions besides
# the harness's SPY clock, NO returns. QuantConnect's DEFAULT build (recorded). Plain-text source, no compression or
# encoding, no reference data uploaded, no identifier reused from earlier extractions (D257): every security key is
# generated in this run and never leaves it.
# Each selection day: every Fundamental object's appearance (last seen) and its daily dollar volume (ADV20, the
# harness rule). Each month-end session 1999-02 .. 2021-11: the liquid set L (raw price >= $5, ADV20 >= $5M) split
# into vendor market cap present (A) / missing (M) among structural US common stocks (harness is_us_common with NO
# dated overrides, vendor exchange code) and no-fundamentals names (N); for A / M the vendor company shares
# outstanding and the day's split factor (U-B cap = shares x raw price x split factor). At the end qr_ub.summarize()
# returns aggregates only (counts, rates, quantiles, bootstrap intervals, digests), published as plain JSON lines
# 'UB|<section>|<json>' through the harness summary statistics.
from AlgorithmImports import *
from collections import deque
from datetime import date
import json
import time
import qr_ub as U
from qr_harness import EXCHANGES, QRAlgorithm, is_us_common

ADV_DAYS = 20
FIRST_POINT = (1999, 2)


class UniverseBaseline(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 1000
        if self.qr["start"] != "1999-01-04" or self.qr["end"] != "2021-12-31" or self.qr.get("warmup_start"):
            raise Exception("X804: UB-1 runs 1999-01-04 .. 2021-12-31 without warm-up")
        u = self._qr_u
        if u.get("sec_corrections") or (float(u.get("min_market_cap", 0)), float(u.get("min_price", 0)),
                                        float(u.get("min_avg_dollar_volume", 0)), int(u.get("adv_days", 0))) != \
                (U.MIN_CAP, U.MIN_PRICE, U.MIN_ADV, ADV_DAYS):
            raise Exception("X804: the approved universe filters without the SEC layer")
        self.ub = U.Audit()
        self.dv = {}
        self.prev_session = None
        self.done_t = None
        self.t0 = time.perf_counter()

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:
            self.prev_session = self.time.date()

    def _qr_select(self, fundamental):
        today = self.time.date()
        o = today.toordinal()
        t = self.prev_session
        audit = False
        if t is not None and t != self.done_t and (t.year, t.month) >= FIRST_POINT:
            nxt = self.securities[self.spy].exchange.hours.get_next_market_open(self.time, False).date()
            audit = nxt.month != t.month or nxt.year != t.year
        rows = []
        c = self.ub.c
        for f in fundamental:
            key = str(f.symbol.id)
            self.ub.observe(key, o)
            dq = self.dv.get(key)
            if dq is None:
                dq = self.dv[key] = deque(maxlen=ADV_DAYS)
            dv = float(f.dollar_volume)
            if dv == dv:                         # missing (NaN) volumes are skipped (D029)
                dq.append(dv)
            if not audit or len(dq) < ADV_DAYS:
                continue
            px = float(f.price)
            adv = sum(dq) / ADV_DAYS
            if not (px >= U.MIN_PRICE and adv >= U.MIN_ADV):
                continue
            c["liquid"] += 1
            if not f.has_fundamental_data:
                c["liquid_no_fund"] += 1
                rows.append((key, U.CAT_N, 0.0, None, None, px, adv, False))
                continue
            try:
                common = is_us_common(f, None) and str(f.security_reference.exchange_id) in EXCHANGES
            except Exception:
                c["struct_errors"] += 1
                continue
            if not common:
                c["noncommon"] += 1
                continue
            try:
                mc = float(f.market_cap)
                if not mc > 0:
                    mc = 0.0
            except Exception:
                mc = 0.0
                c["cap_errors"] += 1
            try:
                S = float(f.company_profile.shares_outstanding)
            except Exception:
                S = None
                c["shares_errors"] += 1
            try:
                SF = float(f.split_factor)
            except Exception:
                SF = None
                c["sf_errors"] += 1
            try:
                scmc = float(f.company_profile.share_class_market_cap) > 0
            except Exception:
                scmc = False
            rows.append((key, U.CAT_A if mc > 0 else U.CAT_M, mc, S, SF, px, adv, scmc))
        if audit:
            self.done_t = t
            self.ub.audit_point(t.year, t.month, o, rows)
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        t1 = time.perf_counter()
        res = self.ub.summarize()
        meta = {k: v for k, v in res.items() if k not in ("years", "validity", "pre2010")}
        meta.update(collect_s=round(t1 - self.t0, 1), summarize_s=round(time.perf_counter() - t1, 1),
                    experiment_id=self.qr.get("experiment_id"))
        dump = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"))
        self._qr_log("UB|meta|" + dump(meta))
        for y, rec in sorted((res.get("years") or {}).items()):
            self._qr_log(f"UB|year|{y}|" + dump(rec))
        self._qr_log("UB|validity|" + dump(res.get("validity")))
        self._qr_log("UB|pre2010|" + dump(res.get("pre2010")))
