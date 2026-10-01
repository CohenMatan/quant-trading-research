# X973 v1.0 — universe-wide restatement guard (infrastructure; NO orders, no rankings, no returns; D111). 2010-2021.
# For every vendor report of an eligible company, compare each guarded field with the SEC filings that reported
# the same period (only periods where SEC filings disagree are in guard_ref): if the vendor value equals ONLY a
# value first filed AFTER the vendor's file date (and not any value public by then), the report carries later
# (restated) information -> exported for quarantine (the PIT layer then keeps the previous clean report).
# Interim '*_ttm' fields hold the latest completed fiscal year's total (vendor semantics, E971-02) and are checked
# against that fiscal year's filings. Outputs identifiers, dates and field names only (no values).
from AlgorithmImports import *
import json
from datetime import date
from qr_harness import QRAlgorithm, _attr
from qr_fundamentals import read_values
from guard_ref import load_table

TOL = 0.005
DIRECT = {"total_assets": "total_assets", "stockholders_equity": "stockholders_equity", "revenue_q": "revenue_q",
          "net_income_q": "net_income_q"}
FY = {"revenue_ttm": "revenue_fy", "net_income_ttm": "net_income_fy", "operating_cash_flow_ttm": "operating_cash_flow_fy"}


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


def near_key(dct, pe, tol=6):
    for i in range(-tol, tol + 1):
        k = str(date.fromordinal(pe.toordinal() + i))
        if k in dct:
            return k
    return None


class RestatementGuard(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 200000
        t = load_table()
        self.vers = t["versions"]
        self.fy = {k: [date.fromisoformat(x) for x in v] for k, v in t["fy_ends"].items()}
        self.seen = set()
        self.c = {"reports": 0, "with_sec_versions": 0, "checked_fields": 0, "flagged_reports": 0,
                  "flagged_fields": 0, "matches_original": 0, "matches_none": 0}

    def _check(self, rows, v, fd):
        """'orig' if v equals the first-filed value; 'future' if it equals only values filed after fd; 'public'
        if it equals a later value already public by fd; 'none' otherwise."""
        hits = [(filed, x) for filed, x, form in rows if x and abs(v / x - 1) <= TOL]
        if not hits:
            return "none"
        if abs(v / rows[0][1] - 1) <= TOL if rows[0][1] else False:
            return "orig"
        return "public" if any(filed <= str(fd) for filed, _ in hits) else "future"

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        elig = set(self.qr_eligible)
        for f in fl:
            if f.symbol not in elig:
                continue
            try:
                er = f.earning_reports
                pe, fd = as_date(er.period_ending_date.three_months), as_date(er.file_date.three_months)
            except Exception:
                continue
            sid = str(f.symbol.id)
            key = (sid, pe, fd)
            if key in self.seen or pe is None or fd is None:
                continue
            self.seen.add(key)
            self.c["reports"] += 1
            cik = str(_attr(f.company_reference, "cik", "") or "").lstrip("0")
            vp = self.vers.get(cik)
            if not vp:
                continue
            vals = read_values(f, get)
            flagged = []
            k = near_key(vp, pe)
            fys = [e for e in self.fy.get(cik, ()) if e <= pe]
            kf = near_key(vp, max(fys)) if fys else None
            if k is not None or kf is not None:
                self.c["with_sec_versions"] += 1
            for vf, sf in DIRECT.items():
                rows = vp.get(k, {}).get(sf) if k else None
                if rows and vals.get(vf):
                    self.c["checked_fields"] += 1
                    r = self._check(rows, vals[vf], fd)
                    if r == "future":
                        flagged.append(vf)
                    elif r == "orig":
                        self.c["matches_original"] += 1
                    elif r == "none":
                        self.c["matches_none"] += 1
            for vf, sf in FY.items():
                rows = vp.get(kf, {}).get(sf) if kf else None
                if rows and vals.get(vf):
                    self.c["checked_fields"] += 1
                    r = self._check(rows, vals[vf], fd)
                    if r == "future":
                        flagged.append(vf)
                    elif r == "orig":
                        self.c["matches_original"] += 1
                    elif r == "none":
                        self.c["matches_none"] += 1
            if flagged:
                self.c["flagged_reports"] += 1
                self.c["flagged_fields"] += len(flagged)
                self._qr_log(f"G|{sid}|{f.symbol.value}|{cik}|{pe}|{fd}|{today}|{','.join(flagged)}")
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        self._qr_log("C|" + json.dumps(self.c, sort_keys=True))
