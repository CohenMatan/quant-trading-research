# X806 v1.0 — narrow SEC-based universe repair + re-audit UCR-1 (owner D269, UR-2 option A;
# research/rr/universe_repair/UCR_protocol.md, frozen and SHA-256-pinned in qresearch.rr_ucr with this host, qr_ucr and
# the two public SEC objects). Infrastructure only: NO orders, NO subscriptions besides the harness's SPY clock, NO
# returns. QuantConnect's DEFAULT build (recorded). Plain-text source, no compression or encoding.
# Reference data: two public SEC JSON objects in the Object Store (D257), each checked against its pinned SHA-256:
#   rr/ucr_sec_v1.json — the point-in-time per-filing object that drives the REPAIR (qr_ucr);
#   rr/sca_sec_v1.json — the frozen SCA-1 measurement object (retrospective; used ONLY to MEASURE, never to select).
# Each selection day: every Fundamental object's appearance (last seen), daily dollar volume (ADV20, the harness rule)
# and split factor (the day of its last change). Each month-end session 2010-01 .. 2021-11: one row per security
# passed to selection; qr_ucr repairs liquid securities without a usable vendor market cap from SEC filings filed
# BEFORE that session; the frozen SCA-1 audit (qr_sca) is run twice — on the original vendor universe (A0) and on the
# repaired universe (A1). Aggregates only, published as plain JSON lines 'UCR|<section>|<json>'.
from AlgorithmImports import *
from collections import deque
import hashlib
import json
import time
import numpy as np
import qr_sca as A
import qr_ucr as R
from qr_harness import COMMON_STOCK, EXCHANGES, QRAlgorithm, is_us_common, non_common_reason

ADV_DAYS = 20
MIN_PRICE, MIN_ADV = 5.0, 5e6
FIRST_POINT = (2010, 1)
SCA_CODE = {"E": A.CAT_E, "A_lt": A.CAT_ALT, "M": A.CAT_M, "X": A.CAT_X, "B_blank": A.CAT_B, "B_explicit": A.CAT_B,
            "N": A.CAT_N, "I": A.CAT_I}


class UniverseRepairReaudit(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 1000
        if self.qr["start"] != "2009-05-01" or self.qr["end"] != "2021-12-31" or self.qr.get("warmup_start"):
            raise Exception("X806: UCR-1 runs 2009-05-01 .. 2021-12-31 without warm-up")
        u = self._qr_u
        if u.get("sec_corrections") or (float(u.get("min_market_cap", 0)), float(u.get("min_price", 0)),
                                        float(u.get("min_avg_dollar_volume", 0)), int(u.get("adv_days", 0))) != \
                (A.MIN_CAP, MIN_PRICE, MIN_ADV, ADV_DAYS):
            raise Exception("X806: the approved universe filters without the SEC layer")
        p = self.qr["params"]
        docs = {}
        for name in ("sca", "ucr"):
            key, want = p[name + "_object_key"], p[name + "_reference_sha256"]
            if not self.object_store.contains_key(key):
                raise Exception(f"X806: the {name} SEC object is not in the Object Store")
            text = self.object_store.read(key)
            got = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if got != want:
                raise Exception(f"X806: {name} SEC object digest {got[:12]} differs from the pinned {want[:12]}")
            docs[name] = (got, json.loads(text))
            text = None
        self.sha = {k: v[0] for k, v in docs.items()}
        sca_ref = A.SecRef(docs["sca"][1])
        self.a0, self.a1 = A.Audit(sca_ref), A.Audit(sca_ref)
        self.rep = R.Repair(R.RepairRef(docs["ucr"][1]))
        docs = None
        self.dv, self.sf, self.sf_change = {}, {}, {}
        self.prev_session = None
        self.done_t = None
        self.t0 = time.perf_counter()

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:
            self.prev_session = self.time.date()

    def _category(self, f, px, adv):
        """Point-in-time category: E / A_lt / M / X / B_blank / B_explicit / N / I (protocol section 3.1)."""
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
            self.rep._cnt(self.time.year, "struct_errors")
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
            return "E" if mc >= A.MIN_CAP else "A_lt"
        blank = (not st or not exch) and not dep and st in ("", COMMON_STOCK) and ncr is None \
            and (not exch or exch in EXCHANGES)
        return "B_blank" if blank else "B_explicit"

    def _qr_select(self, fundamental):
        today = self.time.date()
        o = today.toordinal()
        t = self.prev_session
        audit = False
        if t is not None and t != self.done_t and (t.year, t.month) >= FIRST_POINT:
            nxt = self.securities[self.spy].exchange.hours.get_next_market_open(self.time, False).date()
            audit = nxt.month != t.month or nxt.year != t.year
        base, rrows = [], []
        for f in fundamental:
            key = str(f.symbol.id)
            self.a0.observe(key, o)
            self.a1.observe(key, o)
            dq = self.dv.get(key)
            if dq is None:
                dq = self.dv[key] = deque(maxlen=ADV_DAYS)
            dv = float(f.dollar_volume)
            if dv == dv:                         # missing (NaN) volumes are skipped (D029)
                dq.append(dv)
            try:
                sf = float(f.split_factor)
            except Exception:
                sf = float("nan")
            if sf == sf and sf > 0:
                last = self.sf.get(key)
                if last is not None and abs(sf / last - 1) > 1e-9:
                    self.sf_change[key] = o
                self.sf[key] = sf
            if not audit:
                continue
            px = float(f.price)
            adv = sum(dq) / ADV_DAYS if len(dq) == ADV_DAYS else None
            cat = self._category(f, px, adv)
            try:
                mc = float(f.market_cap) if f.has_fundamental_data else 0.0
            except Exception:
                mc = 0.0
            mc = mc if mc > 0 else 0.0
            tick = f.symbol.value
            base.append((key, tick, SCA_CODE[cat], px, mc))
            rrows.append((key, tick, cat, px, mc, self.sf_change.get(key), sf == sf and sf > 0))
        if audit:
            self.done_t = t
            fixed = self.rep.repair(t.year, t.toordinal(), rrows)
            rep = [(r[0], r[1], A.CAT_E, r[3], fixed[j]) if j in fixed else r for j, r in enumerate(base)]
            self.a0.audit_point(t.year, t.month, o, t.toordinal(), base)
            self.a1.audit_point(t.year, t.month, o, t.toordinal(), rep)
        return []

    def qr_select_universe(self, eligible):
        return []

    def _repaired_exits(self, res0):
        """Exits of repaired stock-months vs the original E (24 / 12-month horizon as SCA-1), per year."""
        a0 = self.a0
        P = a0.points
        CALL = np.array([p[2] for p in P], dtype=np.int64)
        Y = np.array([p[0] for p in P])
        final_call = int(CALL.max())
        last = np.array(a0.last_seen, dtype=np.int64)
        sr = np.array(a0.sec_rows, dtype=np.int64).reshape(-1, 3)
        rr = np.array([(k, a0.ids[key]) for k, key in self.rep.rep_rows], dtype=np.int64).reshape(-1, 2)
        k_all = np.concatenate([sr[:, 0], rr[:, 0]])
        sec = np.concatenate([sr[:, 1], rr[:, 1]])
        inc = np.concatenate([(sr[:, 2] == 0) | (sr[:, 2] == 3), np.zeros(len(rr), bool)])
        unr = np.concatenate([np.zeros(len(sr), bool), np.ones(len(rr), bool)])
        rng = np.random.default_rng(A.BOOT_SEED)
        out = {}
        for y in sorted(set(Y.tolist())):
            ky = np.where(Y == y)[0]
            m = np.isin(k_all, ky)
            h = next((hh for hh in (A.H_PRIMARY, A.H_SECONDARY)
                      if (np.array([A.add_months(c, hh) for c in CALL])[ky] <= final_call).any()), None)
            if h is None:
                out[str(y)] = dict(horizon=None, repaired_stock_months=int((m & unr).sum()),
                                   repaired_securities=int(np.unique(sec[m & unr]).size))
                continue
            hz = np.array([A.add_months(c, h) for c in CALL], dtype=np.int64)
            ass = (hz <= final_call)[k_all]
            ex = last[sec] < hz[k_all]
            b = A._boot(rng, sec, m & inc & ass, m & unr & ass, ex)
            out[str(y)] = dict(horizon=h, repaired_stock_months=int((m & unr).sum()),
                               repaired_securities=int(np.unique(sec[m & unr]).size), b_R=b)
        return out

    def qr_on_end(self):
        t1 = time.perf_counter()
        res0, res1 = self.a0.summarize(), self.a1.summarize()
        exits = self._repaired_exits(res0)
        years = {}
        for y in sorted(res1.get("years", {})):
            ry = self.rep.year.get(int(y), {})
            v = R.reaudit_verdict(res1["years"][y], res0["years"][y], ry, A.year_verdict)
            years[y] = dict(original=res0["years"][y], repaired=res1["years"][y], repair=ry, repaired_exits=exits[y],
                            verdict=v)
        windows = {w: A.window_verdict({y: dict(verdict=years[y]["verdict"]) for y in years}, a, b)
                   for w, (a, b) in A.WINDOWS.items()}
        meta = dict(protocol="UCR-1", sca_reference_sha256=self.sha["sca"], ucr_reference_sha256=self.sha["ucr"],
                    original={k: v for k, v in res0.items() if k not in ("years", "windows")},
                    repaired={k: v for k, v in res1.items() if k not in ("years", "windows")},
                    collect_s=round(t1 - self.t0, 1), summarize_s=round(time.perf_counter() - t1, 1),
                    experiment_id=self.qr.get("experiment_id"))
        dump = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"))
        self._qr_log("UCR|meta|" + dump(meta))
        for y, rec in years.items():
            self._qr_log(f"UCR|year|{y}|" + dump(rec))
        self._qr_log("UCR|windows|" + dump(windows))
