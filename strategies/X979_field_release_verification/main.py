# X979 v1.0 — field-level SEC verification of the 135 quarantined 'mixed-period' vendor reports (D114; owner item 6)
# (infrastructure; NO orders, no rankings, no returns). For each target report (security, period end, vendor file
# date): when the vendor object first shows it, the ratio vendor value / SEC as-first-filed value for each field a
# field-level release may cover (approved flows: quarterly and fiscal-year revenue, gross profit, net income,
# operating cash flow), the accession year flag, and the observation date. Ratios, dates and identifiers only.
from AlgorithmImports import *
from datetime import date
from qr_harness import QRAlgorithm
from qr_fundamentals import accession_year, read_values
from ref import load_table

FIELDS = ("revenue_q", "gross_profit_q", "net_income_q", "operating_cash_flow_q",
          "revenue_ttm", "gross_profit_ttm", "net_income_ttm", "operating_cash_flow_ttm")


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


def fmt(x):
    return "na" if x is None else f"{x:.5f}"


class FieldReleaseVerification(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 20000
        self.targets = {}
        for sid, rows in load_table().items():
            for pe, fd, orig_filed, sec in rows:
                self.targets[(sid, pe, fd)] = (orig_filed, sec)
        self.sids = {k[0] for k in self.targets}
        self.done = set()

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        for f in fl:
            sid = str(f.symbol.id)
            if sid not in self.sids or not f.has_fundamental_data:
                continue
            try:
                er = f.earning_reports
                pe, fd = as_date(er.period_ending_date.three_months), as_date(er.file_date.three_months)
                k = (sid, str(pe), str(fd))
                if k not in self.targets or k in self.done:
                    continue
                self.done.add(k)
                ay = accession_year(er.accession_number.three_months)
                vals = read_values(f, get)
            except Exception as e:
                self._qr_log(f"ERR|{sid}|{today}|{type(e).__name__}")
                continue
            orig_filed, sec = self.targets[k]
            parts = []
            for fld in FIELDS:
                v, s = vals.get(fld), sec.get(fld)
                parts.append(f"{fld}={fmt(v / s) if (v is not None and s) else ('vendor_na' if v is None else 'sec_na')}")
            self._qr_log("R|" + "|".join((sid, str(pe), str(fd), str(today), str(int(ay is not None and ay > today.year)),
                                          orig_filed, ";".join(parts))))
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        self._qr_log(f"SUMMARY|targets={len(self.targets)}|seen={len(self.done)}")
