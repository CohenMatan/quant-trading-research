# X808 v1.0 — OD-1 outcome-driven discovery study (owner D308; research/od/OD1_protocol.md, frozen and SHA-256-pinned
# in qresearch.od1 with this host, qr_od1 and the three public SEC objects). EXPLORATORY, aggregates only: NO orders,
# NO subscriptions besides the harness's SPY clock, NO identifiers, prices or per-security rows leave the cloud.
# QuantConnect's DEFAULT build (recorded). Plain-text source, no compression or encoding.
# The run starts 2010-01-04 WITHOUT warm-up (no market datum before 2010 is read) and SEC filings filed before
# 2010-01-01 are discarded on load. Each session: every Fundamental object's adjusted price and dollar volume (ring of
# the last 253 sessions), split factor and last appearance; the SPY total-return index. Each month-end session
# 2011-01 .. 2021-11: the UCR-1 repaired universe (frozen qr_ucr), point-in-time identity / SIC / share issuance
# (frozen qr_os1), the OD-1 technical and fundamental features (qr_od1) and the review-day adjusted price of every
# security. At the end: forward outcomes (3 / 6 / 12 / 24 months, never past the 2021-11 review) joined to the
# features and summarised (qr_od1.summarize), published as plain JSON lines 'OD1|<section>|<key>|<json>'.
from AlgorithmImports import *
from collections import deque
from datetime import date
import hashlib
import json
import math
import time
import numpy as np
import qr_od1 as D
import qr_os1 as O
import qr_ucr as R
from qr_harness import COMMON_STOCK, EXCHANGES, QRAlgorithm, is_us_common, non_common_reason

ADV_DAYS = 20
MIN_PRICE, MIN_ADV = 5.0, 5e6
FIRST_POINT = (2011, 1)
LAST_POINT = (2021, 11)
RING = D.L
FILED_FROM = "2010-01-01"
SECTOR = {name: j for j, name in enumerate(D.FF12_NAMES)}


def filter_filed(ucr, os1):
    """Discard SEC filings filed before 2010-01-01 (owner D308) from both pinned objects, keeping the os1 SIC list
    parallel to the UCR-1 filing list."""
    for c, rec in ucr["r"].items():
        p = rec["p"]
        keep = [j for j, x in enumerate(p) if x[0] >= FILED_FROM]
        e = os1["r"][c]
        if len(e["s"]) != len(p):
            raise Exception(f"X808: os1 SIC list not parallel to the UCR-1 filings of CIK {c}")
        rec["p"] = [p[j] for j in keep]
        e["s"] = [e["s"][j] for j in keep]
        rec["f"] = [x for x in rec["f"] if x[0] >= FILED_FROM]
        e["k"] = [x for x in e["k"] if x[0] >= FILED_FROM]


class OutcomeStudy(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 100000
        if self.qr["start"] != "2010-01-04" or self.qr["end"] != "2021-12-31" or self.qr.get("warmup_start"):
            raise Exception("X808: OD-1 runs 2010-01-04 .. 2021-12-31 without warm-up")
        u = self._qr_u
        if u.get("sec_corrections") or (float(u.get("min_market_cap", 0)), float(u.get("min_price", 0)),
                                        float(u.get("min_avg_dollar_volume", 0)), int(u.get("adv_days", 0))) != \
                (R.MIN_CAP, MIN_PRICE, MIN_ADV, ADV_DAYS):
            raise Exception("X808: the approved universe filters without the SEC layer")
        p = self.qr["params"]
        docs = {}
        for name in ("ucr", "os1", "od1"):
            key, want = p[name + "_object_key"], p[name + "_reference_sha256"]
            if not self.object_store.contains_key(key):
                raise Exception(f"X808: the {name} SEC object is not in the Object Store")
            text = self.object_store.read(key)
            got = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if got != want:
                raise Exception(f"X808: {name} SEC object digest {got[:12]} differs from the pinned {want[:12]}")
            docs[name] = (got, json.loads(text))
            text = None
        self.sha = {k: v[0] for k, v in docs.items()}
        filter_filed(docs["ucr"][1], docs["os1"][1])
        self.ref = R.RepairRef(docs["ucr"][1])
        self.ext = O.Ext(docs["os1"][1], self.ref)
        self.rep = R.Repair(self.ref)
        self.fund = D.Fund(docs["od1"][1], self.ref.ciks)
        docs = None
        self.splits = O.Splits()
        self.dv, self.sf, self.sf_change = {}, {}, {}
        self.row = {}
        self.px = np.full((8192, RING), np.nan)
        self.dvx = np.full((8192, RING), np.nan, dtype=np.float32)
        self.mpx = np.full((8192, 140), np.nan, dtype=np.float32)
        self.last_px = np.full(8192, np.nan)
        self.last_day = np.zeros(8192, dtype=np.int64)
        self.spy_px = np.full(RING, np.nan)
        self.spy_tr, self.spy_last = 1.0, None
        self.sess_n, self.ring_sess = -1, -1
        self.prev_session = None
        self.done_t = None
        self.k = -1
        self.T, self.years, self.spy_rev, self.reviews = [], [], [], []
        self.ok, self.orow, self.ofirm, self.osec, self.ofin, self.ocap, self.oX = [], [], [], [], [], [], []
        self.checks = dict(struct_errors=0, identity_duplicates=0, repaired_rows=0, short_ring=0,
                           rows_grown=0)
        self.t0 = time.perf_counter()

    # ---------------------------------------------------------------- daily
    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:
            d = self.time.date()
            if d != self.prev_session and data.bars.contains_key(self.spy) \
                    and not data.bars[self.spy].is_fill_forward:
                c = float(data.bars[self.spy].close)
                div = float(data.dividends[self.spy].distribution) if data.dividends.contains_key(self.spy) else 0.0
                if self.spy_last is not None and self.spy_last > 0:
                    self.spy_tr *= (c + div) / self.spy_last
                self.spy_last = c
                self.prev_session = d
                self.sess_n += 1
                self.spy_px[self.sess_n % RING] = self.spy_tr

    def _row(self, key):
        r = self.row.get(key)
        if r is None:
            r = self.row[key] = len(self.row)
            if r >= self.px.shape[0]:
                n = self.px.shape[0]
                self.px = np.vstack([self.px, np.full((n, RING), np.nan)])
                self.dvx = np.vstack([self.dvx, np.full((n, RING), np.nan, dtype=np.float32)])
                self.mpx = np.vstack([self.mpx, np.full((n, self.mpx.shape[1]), np.nan, dtype=np.float32)])
                self.last_px = np.concatenate([self.last_px, np.full(n, np.nan)])
                self.last_day = np.concatenate([self.last_day, np.zeros(n, dtype=np.int64)])
                self.checks["rows_grown"] += 1
        return r

    def _category(self, f, px, adv):
        """Point-in-time category: E / A_lt / M / X / B_blank / B_explicit / N / I (as X806 / X807)."""
        if adv is None or not (px >= MIN_PRICE and adv >= MIN_ADV):
            return "I"
        if not f.has_fundamental_data:
            return "N"
        try:
            sr = f.security_reference
            exch = str(sr.exchange_id or "").strip()
            st = str(sr.security_type or "").strip()
            dep = bool(sr.is_depositary_receipt)
            common = is_us_common(f, None)
            ncr = non_common_reason(f, None)
        except Exception:
            self.checks["struct_errors"] += 1
            return "B_explicit"
        if common and exch:
            if exch not in EXCHANGES:
                return "X"
            try:
                mc = float(f.market_cap)
            except Exception:
                mc = 0.0
            if not mc > 0:
                return "M"
            return "E" if mc >= R.MIN_CAP else "A_lt"
        blank = (not st or not exch) and not dep and st in ("", COMMON_STOCK) and ncr is None \
            and (not exch or exch in EXCHANGES)
        return "B_blank" if blank else "B_explicit"

    def _qr_select(self, fundamental):
        today = self.time.date()
        t = self.prev_session
        if t is None:
            return []
        to = t.toordinal()
        so = to + 1                                      # split-factor stamp: the day after the session it reflects
        if self.ring_sess != self.sess_n:
            self.px[:, self.sess_n % RING] = np.nan
            self.dvx[:, self.sess_n % RING] = np.nan
            self.ring_sess = self.sess_n
        col = self.sess_n % RING
        review = False
        if t != self.done_t and FIRST_POINT <= (t.year, t.month) <= LAST_POINT:
            nxt = self.securities[self.spy].exchange.hours.get_next_market_open(self.time, False).date()
            review = nxt.month != t.month or nxt.year != t.year
        rows, rrows, advs, mcs, fs = [], [], [], [], []
        for f in fundamental:
            key = str(f.symbol.id)
            dq = self.dv.get(key)
            if dq is None:
                dq = self.dv[key] = deque(maxlen=ADV_DAYS)
            dv = float(f.dollar_volume)
            if dv == dv:
                dq.append(dv)
            try:
                sf = float(f.split_factor)
            except Exception:
                sf = float("nan")
            if sf == sf and sf > 0:
                last = self.sf.get(key)
                if last is not None and abs(sf / last - 1) > 1e-9:
                    self.sf_change[key] = so
                self.sf[key] = sf
                self.splits.observe(key, so, sf)
            try:
                ap = float(f.adjusted_price)
            except Exception:
                ap = float("nan")
            if ap == ap and ap > 0:
                r = self._row(key)
                self.px[r, col] = ap
                if dv == dv:
                    self.dvx[r, col] = dv
                self.last_px[r] = ap
                self.last_day[r] = to
            if not review:
                continue
            px = float(f.price)
            adv = sum(dq) / ADV_DAYS if len(dq) == ADV_DAYS else None
            cat = self._category(f, px, adv)
            try:
                mc = float(f.market_cap) if f.has_fundamental_data else 0.0
            except Exception:
                mc = 0.0
            tick = f.symbol.value
            rows.append((key, tick, cat))
            rrows.append((key, tick, cat, px, mc if mc > 0 else 0.0, self.sf_change.get(key), sf == sf and sf > 0))
            mcs.append(mc if mc > 0 else 0.0)
        if review:
            self.done_t = t
            self._review(t, rows, rrows, mcs)
        return []

    def qr_select_universe(self, eligible):
        return []

    # ---------------------------------------------------------------- monthly review
    def _review(self, t, rows, rrows, mcs):
        self.k += 1
        k = self.k
        to = t.toordinal()
        fixed = self.rep.repair(t.year, to, rrows)
        self.checks["repaired_rows"] += len(fixed)
        idmap, why = O.identity(self.ref, to, [(r[0], r[1]) for r in rows])
        if len(set(idmap.values())) != len(idmap):
            self.checks["identity_duplicates"] += 1
        elig = [j for j, (key, tick, cat) in enumerate(rows) if cat == "E" or j in fixed]
        n = len(elig)
        if self.sess_n < RING - 1:
            self.checks["short_ring"] += 1
        order = [(self.sess_n - RING + 1 + j) % RING for j in range(RING)]
        rr = np.array([self.row.get(rows[j][0], -1) for j in elig], dtype=np.int64)
        C = np.full((n, RING), np.nan)
        V = np.full((n, RING), np.nan)
        has = rr >= 0
        if has.any():
            C[has] = self.px[rr[has]][:, order]
            V[has] = self.dvx[rr[has]][:, order].astype(float)
        S = self.spy_px[order].copy()
        tf = D.tech_features(C, V, S)
        caps = np.array([mcs[j] if rows[j][2] == "E" else fixed[j] for j in elig], float)
        tf["SIZE"] = np.where(caps > 0, np.log(np.where(caps > 0, caps, 1.0)), np.nan)
        sec = np.full(n, -1, dtype=np.int64)
        fin = np.zeros(n, bool)
        firm = np.zeros(n, dtype=np.int64)
        F = np.full((n, len(D.FUND)), np.nan)
        c = dict(t=t.isoformat(), elig=n, vendor=0, restored=0, ident=0, fin=0, tech_ok=0, fund_ok=0)
        for a, j in enumerate(elig):
            key, tick, cat = rows[j]
            c["vendor" if cat == "E" else "restored"] += 1
            i = idmap.get(j)
            sic, finf, os_, nr, adj, ocf, g, ro, rr_, covered, passed = \
                O.classify(self.ref, self.ext, self.splits, to, key, i)
            if i is not None:
                c["ident"] += 1
                firm[a] = i
                s_ = SECTOR.get(O.ff12(sic), -1)
                sec[a] = s_
            else:
                firm[a] = 1000000 + max(int(rr[a]), 0)
            if finf is True:
                fin[a] = True
                c["fin"] += 1
            fv = self.fund.features(i, to, caps[a])
            fv["REPURCH"] = os_
            for b, name in enumerate(D.FUND):
                v = fv.get(name)
                if v is not None:
                    F[a, b] = float(v)
            if np.isfinite(F[a]).sum() >= 8 and not fin[a]:
                c["fund_ok"] += 1
        m6 = tf["MOM6_1"]
        rel = np.full(n, np.nan)
        for s_ in np.unique(sec):
            if s_ < 0:
                continue
            ms = (sec == s_) & np.isfinite(m6)
            if ms.sum() >= 5:
                rel[ms] = m6[ms] - np.median(m6[ms])
        tf["SECREL6"] = rel
        T = np.column_stack([tf[name] for name in D.TECH])
        c["tech_ok"] = int(np.isfinite(T[:, D.TECH.index("MOM12_1")]).sum())
        X = np.concatenate([T, F], axis=1).astype(np.float32)
        self.ok.append(np.full(n, k, dtype=np.int32))
        self.orow.append(rr.astype(np.int32))
        self.ofirm.append(firm)
        self.osec.append(sec.astype(np.int16))
        self.ofin.append(fin)
        self.ocap.append(caps.astype(np.float32))
        self.oX.append(X)
        rcol = self.px[:, self.sess_n % RING]
        if k >= self.mpx.shape[1]:
            self.mpx = np.hstack([self.mpx, np.full((self.mpx.shape[0], 20), np.nan, dtype=np.float32)])
        self.mpx[:len(self.row), k] = rcol[:len(self.row)].astype(np.float32)
        self.T.append(to)
        self.years.append(t.year)
        self.spy_rev.append(self.spy_tr)
        c["why"] = why
        self.reviews.append(c)

    # ---------------------------------------------------------------- end
    def qr_on_end(self):
        t1 = time.perf_counter()
        K = len(self.T)
        k = np.concatenate(self.ok).astype(np.int64)
        r = np.concatenate(self.orow).astype(np.int64)
        keep = r >= 0                                    # every eligible security has a price row (checked below)
        self.checks["obs_without_price_row"] = int((~keep).sum())
        T = self.T
        k1712 = max((j for j, x in enumerate(T) if date.fromordinal(x) <= date(2017, 12, 31)), default=-1)
        k1801 = min((j for j, x in enumerate(T) if date.fromordinal(x) >= date(2018, 1, 1)), default=K)
        nrow = len(self.row)
        P = dict(T=T, years=self.years, spy=np.array(self.spy_rev), MP=self.mpx[:nrow, :K],
                 last_day=self.last_day[:nrow], last_px=self.last_px[:nrow], k=k[keep], r=r[keep],
                 firm=np.concatenate(self.ofirm)[keep], X=np.concatenate(self.oX)[keep].astype(float),
                 sec=np.concatenate(self.osec).astype(np.int64)[keep], fin=np.concatenate(self.ofin)[keep],
                 cap=np.concatenate(self.ocap)[keep], K1712=k1712, K1801=k1801)
        out = D.summarize(P)
        dump = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)
        meta = dict(protocol="OD-1", reviews=K, first=date.fromordinal(T[0]).isoformat(),
                    last=date.fromordinal(T[-1]).isoformat(), K1712=k1712, K1801=k1801,
                    observations=int(P["k"].size), firms=int(np.unique(P["firm"]).size),
                    stream_rows=nrow, sha=self.sha,
                    checks=dict(self.checks, pit_violations_ext=self.ext.pit_violations,
                                pit_violations_fund=self.fund.pit_violations),
                    collect_s=round(t1 - self.t0, 1), summarize_s=round(time.perf_counter() - t1, 1),
                    experiment_id=self.qr.get("experiment_id"))
        self._qr_log("OD1|meta|all|" + dump(meta))
        self._qr_log("OD1|reviews|all|" + dump(self.reviews))
        for sec_, key, payload in out:
            self._qr_log(f"OD1|{sec_}|{key}|" + dump(payload))
