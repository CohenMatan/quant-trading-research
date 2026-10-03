# X981 v1.0 — universe identifier export for the SEC earnings-event audit (P2-CP12; infrastructure, NOT a trial).
# NO orders, no rankings, no prices or returns exported, no fundamental values. 2010-2021, frozen data v1 universe
# (harness eligibility incl. the SEC correction layer, universe.sec_corrections).
# Exports one line per security that was ever eligible on the first session of a month:
#   U|sid|vendor CIK (current-status, natives only)|SEC-correction CIK (repaired only)|corrected 0/1|
#     dated tickers 'TICKER:yyyymm-yyyymm;...' (as carried on eligible month starts)|eligible-month bitmask (hex, bit i
#     = month i from 2010-01)|first eligible month|last eligible month|last date the security was seen at all
#   C|counts (json)
from AlgorithmImports import *
import json
from qr_harness import QRAlgorithm, _attr

M0 = 2010 * 12


class UniverseExport(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        self.month = None
        self.recs = {}             # sid -> dict
        self.counts = {"month_starts": 0, "eligible_stock_months": 0, "days": 0}

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        day = today.strftime("%Y-%m-%d")
        self.counts["days"] += 1
        recs = self.recs
        for f in fl:
            r = recs.get(str(f.symbol.id))
            if r is not None:
                r["last_seen"] = day
        if (today.year, today.month) == self.month:
            return []
        self.month = (today.year, today.month)
        ym = today.year * 100 + today.month
        mi = today.year * 12 + today.month - 1 - M0
        self.counts["month_starts"] += 1
        by = {f.symbol: f for f in fl}
        corr = {str(s.id) for s in self.qr_corrected}
        for sym in self.qr_eligible:
            sid = str(sym.id)
            r = recs.get(sid)
            if r is None:
                f = by.get(sym)
                vcik = ""
                if f is not None and f.has_fundamental_data:
                    vcik = str(_attr(f.company_reference, "cik", "") or "")
                ccik = ""
                if sid in corr and self.qr_sec is not None:
                    c = self.qr_sec.meta.get(sid, {}).get("cik", [])
                    ccik = ",".join(str(x) for x in (c if isinstance(c, list) else [c]) if x)
                r = recs[sid] = {"vcik": vcik, "ccik": ccik, "corr": int(sid in corr), "tickers": {}, "mask": 0,
                                 "first": ym, "last": ym, "last_seen": day}
            t = r["tickers"].setdefault(sym.value, [ym, ym])
            t[1] = ym
            r["mask"] |= 1 << mi
            r["last"] = ym
            if sid in corr:
                r["corr"] = 1
            self.counts["eligible_stock_months"] += 1
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        for sid, r in sorted(self.recs.items()):
            tk = ";".join(f"{t}:{a}-{b}" for t, (a, b) in sorted(r["tickers"].items(), key=lambda kv: kv[1]))
            self._qr_log(f"U|{sid}|{r['vcik']}|{r['ccik']}|{r['corr']}|{tk}|{r['mask']:x}|{r['first']}|{r['last']}|"
                         f"{r['last_seen']}")
        self.counts["securities"] = len(self.recs)
        self._qr_log("C|" + json.dumps(self.counts, sort_keys=True))
