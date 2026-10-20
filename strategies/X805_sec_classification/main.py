# X805 v1.0 — SEC Classification Audit SCA-1 (owner D267, UR-1 option A; research/rr/sec_classification/
# SCA_protocol.md, frozen and SHA-256-pinned in qresearch.rr_sca with this host and qr_sca). Infrastructure only: NO
# orders, NO subscriptions besides the harness's SPY clock, NO returns. QuantConnect's DEFAULT build (recorded).
# Plain-text source, no compression or encoding. The only reference data is the public SEC JSON 'rr/sca_sec_v1.json'
# that the owner-approved upload put in the Object Store (D257: SEC EDGAR data as plain JSON); it carries no
# QuantConnect identifier and its SHA-256 must equal the pinned value. Every QuantConnect key and the universe
# categories are generated in this run and never leave it.
# Each selection day: every Fundamental object's appearance (last seen) and its daily dollar volume (ADV20, the
# harness rule). Each month-end session 2010-01 .. 2021-11: one row per security passed to selection (ticker, the
# category of protocol section 3, raw price, vendor market cap) goes to qr_sca, which matches SEC registrants by
# dated ticker evidence (fingerprint fallback) and classifies matched / confirmed missing / possible missing /
# unresolved. At the end qr_sca.summarize() returns aggregates only, published as plain JSON lines
# 'SCA|<section>|<json>' through the harness summary statistics.
from AlgorithmImports import *
from collections import deque
import hashlib
import json
import time
import qr_sca as A
from qr_harness import EXCHANGES, QRAlgorithm, is_us_common

ADV_DAYS = 20
MIN_PRICE, MIN_ADV = 5.0, 5e6
FIRST_POINT = (2010, 1)


class SecClassificationAudit(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 1000
        if self.qr["start"] != "2009-11-02" or self.qr["end"] != "2021-12-31" or self.qr.get("warmup_start"):
            raise Exception("X805: SCA-1 runs 2009-11-02 .. 2021-12-31 without warm-up")
        u = self._qr_u
        if u.get("sec_corrections") or (float(u.get("min_market_cap", 0)), float(u.get("min_price", 0)),
                                        float(u.get("min_avg_dollar_volume", 0)), int(u.get("adv_days", 0))) != \
                (A.MIN_CAP, MIN_PRICE, MIN_ADV, ADV_DAYS):
            raise Exception("X805: the approved universe filters without the SEC layer")
        p = self.qr["params"]
        key, want = p["sec_object_key"], p["sec_reference_sha256"]
        if not self.object_store.contains_key(key):
            raise Exception("X805: the SEC reference object is not in the Object Store")
        text = self.object_store.read(key)
        got = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if got != want:
            raise Exception(f"X805: SEC reference digest {got[:12]} differs from the pinned {want[:12]}")
        self.sec_sha = got
        self.sca = A.Audit(A.SecRef(json.loads(text)))
        text = None
        self.dv = {}
        self.prev_session = None
        self.done_t = None
        self.t0 = time.perf_counter()

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:
            self.prev_session = self.time.date()

    def _category(self, f, px, adv):
        if adv is None or not (px >= MIN_PRICE and adv >= MIN_ADV):
            return A.CAT_I
        if not f.has_fundamental_data:
            return A.CAT_N
        try:
            common = is_us_common(f, None)
            exch = str(f.security_reference.exchange_id or "").strip()
        except Exception:
            self.sca.c["struct_errors"] = self.sca.c.get("struct_errors", 0) + 1
            return A.CAT_B
        if not common or not exch:
            return A.CAT_B                      # non-structural, incl. blank classification / exchange fields
        if exch not in EXCHANGES:
            return A.CAT_X
        try:
            mc = float(f.market_cap)
        except Exception:
            mc = 0.0
        if not mc > 0:
            return A.CAT_M
        return A.CAT_E if mc >= A.MIN_CAP else A.CAT_ALT

    def _qr_select(self, fundamental):
        today = self.time.date()
        o = today.toordinal()
        t = self.prev_session
        audit = False
        if t is not None and t != self.done_t and (t.year, t.month) >= FIRST_POINT:
            nxt = self.securities[self.spy].exchange.hours.get_next_market_open(self.time, False).date()
            audit = nxt.month != t.month or nxt.year != t.year
        rows = []
        for f in fundamental:
            key = str(f.symbol.id)
            self.sca.observe(key, o)
            dq = self.dv.get(key)
            if dq is None:
                dq = self.dv[key] = deque(maxlen=ADV_DAYS)
            dv = float(f.dollar_volume)
            if dv == dv:                         # missing (NaN) volumes are skipped (D029)
                dq.append(dv)
            if not audit:
                continue
            px = float(f.price)
            adv = sum(dq) / ADV_DAYS if len(dq) == ADV_DAYS else None
            cat = self._category(f, px, adv)
            try:
                mc = float(f.market_cap) if f.has_fundamental_data else 0.0
            except Exception:
                mc = 0.0
            rows.append((key, f.symbol.value, cat, px, mc if mc > 0 else 0.0))
        if audit:
            self.done_t = t
            self.sca.audit_point(t.year, t.month, o, t.toordinal(), rows)
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        t1 = time.perf_counter()
        res = self.sca.summarize()
        res["sec_reference_sha256"] = self.sec_sha
        meta = {k: v for k, v in res.items() if k not in ("years", "windows")}
        meta.update(collect_s=round(t1 - self.t0, 1), summarize_s=round(time.perf_counter() - t1, 1),
                    experiment_id=self.qr.get("experiment_id"))
        dump = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"))
        self._qr_log("SCA|meta|" + dump(meta))
        for y, rec in sorted((res.get("years") or {}).items()):
            self._qr_log(f"SCA|year|{y}|" + dump(rec))
        self._qr_log("SCA|windows|" + dump(res.get("windows")))
