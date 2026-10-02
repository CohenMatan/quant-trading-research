# X975 v1.0 — True TTM validation (infrastructure; NO orders, no rankings, no returns; D113). 2009-06..2021-12.
# For the E971 sample (403 companies with SEC data): vendor quarterly reports go through the real PIT layer
# (qr_fundamentals.PITStore with SEC timing holds, verified quarantine releases and restatement blocks); each time a
# company's newest visible quarter changes, the True TTM of every additive field (PITStore.ttm_detail: four newest
# visible consecutive quarters, fiscal-year reconciliation gate) is compared with the authoritative SEC TTM for the
# same four quarters (ttm_ref, built offline from SEC filings as first filed). Output per company-quarter-field:
# ratio vendor/SEC, PIT availability vs the SEC availability date, or the reason no TTM exists. Ratios/dates only.
from AlgorithmImports import *
import json
from datetime import date, timedelta
from qr_harness import QRAlgorithm
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, TTM_BASES, accession_year, read_values
from ttm_ref import load_table


def get(obj, path):
    for p in path.split("."):
        obj = getattr(obj, p)
    return obj


def as_date(v):
    try:
        d = v.date() if callable(getattr(v, "date", None)) else v
        return d if d is not None and d.year > 1900 else None
    except Exception:
        return None


class TrueTTMValidation(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        self.ref = load_table()
        self.sid_cik = {sid: cik for cik, c in self.ref.items() for sid in c["sids"]}
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS, holds=self.qr_timing_holds, releases=self.qr_quarantine_releases,
                              blocked=self.qr_restatement_blocks)
        self.seen = set()
        self.done = set()
        self.c = {"lines": 0, "reports": 0}

    def _sec(self, cik, pe):
        t = self.ref[cik]["ttm"]
        for i in range(-6, 7):
            k = str(pe + timedelta(days=i))
            if k in t:
                return t[k]
        return None

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        for f in fl:
            sid = str(f.symbol.id)
            cik = self.sid_cik.get(sid)
            if cik is None or not f.has_fundamental_data:
                continue
            try:
                er = f.earning_reports
                pe, fd = as_date(er.period_ending_date.three_months), as_date(er.file_date.three_months)
                ay = accession_year(er.accession_number.three_months)
            except Exception:
                continue
            if (sid, pe, fd) not in self.seen:
                self.seen.add((sid, pe, fd))
                self.store.observe(sid, pe, fd, read_values(f, get), ay, today)
                self.c["reports"] += 1
            r = self.store.record(sid, today)
            if r is None:
                continue
            for b in TTM_BASES:
                key = (sid, b, r.period_end)
                if key in self.done:
                    continue
                v, det = self.store.ttm_detail(sid, b, today)
                if v is None and det == "fewer than four visible quarters":
                    continue                       # history still building (start of data)
                self.done.add(key)
                sec = self._sec(cik, r.period_end)
                s = sec.get(b) if sec else None
                if v is None:
                    self._qr_log(f"N|{cik}|{sid}|{b}|{today}|{r.period_end}|{det}|{int(s is not None)}")
                elif s is None or not s[0]:
                    self._qr_log(f"U|{cik}|{sid}|{b}|{today}|{r.period_end}|{det['fy_check_period']}")
                else:
                    fy = s[3]
                    fyr = f"{v / fy:.4f}" if fy else "na"
                    self._qr_log(f"T|{cik}|{sid}|{b}|{today}|{r.period_end}|{v / s[0]:.4f}|{s[1]}|{fyr}|"
                                 f"{','.join(det['quarters'])}|{','.join(det['filed'])}")
                self.c["lines"] += 1
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        self.c["store_stats"] = dict(self.store.stats)
        self._qr_log("C|" + json.dumps(self.c, sort_keys=True, default=str))
