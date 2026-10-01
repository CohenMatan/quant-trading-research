# X970 v1.0 — identifier export for the SEC verification and D043 survivorship repair (infrastructure; NO orders,
# no rankings, no returns, no fundamental VALUES; D111). 2010-2021.
# Exports (identifiers, dates and flags only; licence):
#  R  every new vendor report of an eligible company: sid, CIK, period end, file date, accession, first-seen date,
#     and the PIT-layer status (estimated / quarantined / amendment) -> SEC timing comparison at full scale
#  N  native companies: securities WITH fundamentals and PIT market cap >= $1B at a month start: sid, CIK, tickers,
#     first/last such month, months eligible -> which SEC filers QuantConnect already covers
#  M  liquid securities WITHOUT fundamentals (price >= $5, ADV20 >= $5M; the D043 population): sid, tickers by
#     month, liquid months, first/last date seen at all -> candidates for the dated SEC correction
#  F  financial-format vs vendor template disagreements (stock-months): sid, CIK, month, PIT rule result, template,
#     vendor sector/industry (current-status metadata: characterisation only, never used to classify), and which
#     income-statement lines are present (booleans)
from AlgorithmImports import *
import json
from collections import deque
from qr_harness import QRAlgorithm, _attr
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, accession_year, financial_format, read_values

MIN_PRICE, MIN_ADV, ADV_DAYS = 5.0, 5e6, 20


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


class SECLinkExport(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS)
        self._qr_log_budget = 400000     # one line per vendor report (~60k) plus the security lists
        self.month = None
        self.seen_reports = set()
        self.native = {}          # sid -> dict(cik, tickers, first, last, elig_months)
        self.nofund = {}          # sid -> dict(tickers{ticker: [first_ym, last_ym]}, months, first_liquid, last_seen)
        self.adv = {}             # sid -> deque of dollar volume (securities without fundamentals)
        self.counts = {"reports": 0, "quarantined": 0, "estimated": 0, "amendments": 0, "fin_disagree": 0,
                       "fin_checked": 0, "days": 0}
        self.by_period = {}       # (sid, period_end) -> first file date seen (amendment detection)

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        day = today.strftime("%Y-%m-%d")
        ym = today.year * 100 + today.month
        monthly = (today.year, today.month) != self.month
        self.month = (today.year, today.month)
        self.counts["days"] += 1
        elig = set(self.qr_eligible)
        for f in fl:
            sym = f.symbol
            sid = str(sym.id)
            if not f.has_fundamental_data:
                dq = self.adv.get(sid)
                if dq is None:
                    dq = self.adv[sid] = deque(maxlen=ADV_DAYS)
                dv = float(f.dollar_volume)
                if dv == dv:
                    dq.append(dv)
                rec = self.nofund.get(sid)
                if rec is not None:
                    rec["last_seen"] = day
                if monthly and float(f.price) >= MIN_PRICE and len(dq) == ADV_DAYS and sum(dq) / ADV_DAYS >= MIN_ADV:
                    if rec is None:
                        rec = self.nofund[sid] = {"tickers": {}, "months": [], "first_liquid": day, "last_seen": day}
                    t = rec["tickers"].setdefault(sym.value, [ym, ym])
                    t[1] = ym
                    rec["months"].append(ym)
                continue
            if monthly:
                mc = float(f.market_cap or 0)
                if mc >= 1e9 or sym in elig:
                    n = self.native.get(sid)
                    if n is None:
                        n = self.native[sid] = {"cik": str(_attr(f.company_reference, "cik", "") or ""),
                                                "tickers": [], "first": ym, "last": ym, "elig_months": 0,
                                                "elig_first": None, "elig_last": None}
                    if sym.value not in n["tickers"]:
                        n["tickers"].append(sym.value)
                    n["last"] = ym
                    if sym in elig:
                        n["elig_months"] += 1
                        n["elig_first"] = n["elig_first"] or ym
                        n["elig_last"] = ym
            if sym not in elig:
                continue
            # ---- R: every new vendor report of an eligible company (identifiers and dates only)
            try:
                er = f.earning_reports
                pe, fd = as_date(er.period_ending_date.three_months), as_date(er.file_date.three_months)
                acc = str(er.accession_number.three_months or "")
            except Exception:
                continue
            key = (sid, pe, fd)
            if key in self.seen_reports:
                vals = None
            else:
                self.seen_reports.add(key)
                vals = read_values(f, get)
                ay = accession_year(acc)
                est = pe is not None and fd is not None and (fd - pe).days == 45
                quar = ay is not None and ay > today.year
                prev = self.by_period.get((sid, pe))
                amend = prev is not None and fd is not None and prev < fd
                if prev is None and fd is not None:
                    self.by_period[(sid, pe)] = fd
                c = self.counts
                c["reports"] += 1
                c["quarantined"] += int(quar)
                c["estimated"] += int(est)
                c["amendments"] += int(amend)
                self._qr_log(f"R|{sid}|{sym.value}|{_attr(f.company_reference, 'cik', '')}|{pe}|{fd}|{acc}|{day}|"
                             f"{int(est)}{int(quar)}{int(amend)}")
                self.store.observe(sid, pe, fd, vals, ay, today)
            if monthly:
                r = self.store.record(sid, today)
                if r is not None and r.values.get("revenue_ttm") is not None:
                    ff = financial_format(r.values)
                    tpl = str(_attr(f.company_reference, "industry_template_code", ""))
                    self.counts["fin_checked"] += 1
                    if (tpl in ("B", "I")) != bool(ff):
                        self.counts["fin_disagree"] += 1
                        v = r.values
                        flags = "".join(str(int(v.get(k) is not None)) for k in
                                        ("revenue_ttm", "gross_profit_ttm", "cost_of_revenue_ttm", "operating_income_ttm"))
                        ac = f.asset_classification
                        self._qr_log(f"F|{sid}|{sym.value}|{_attr(f.company_reference, 'cik', '')}|{ym}|{int(bool(ff))}|"
                                     f"{tpl}|{_attr(ac, 'morningstar_sector_code', '')}|"
                                     f"{_attr(ac, 'morningstar_industry_code', '')}|{flags}|{r.period_end}")
        return []

    def qr_select_universe(self, eligible):
        return []

    def qr_on_end(self):
        for sid, n in sorted(self.native.items()):
            self._qr_log(f"N|{sid}|{n['cik']}|{','.join(n['tickers'])}|{n['first']}|{n['last']}|{n['elig_months']}|"
                         f"{n['elig_first']}|{n['elig_last']}")
        for sid, r in sorted(self.nofund.items()):
            tk = ";".join(f"{t}:{a}-{b}" for t, (a, b) in sorted(r["tickers"].items(), key=lambda kv: kv[1]))
            self._qr_log(f"M|{sid}|{tk}|{len(r['months'])}|{r['months'][0]}|{r['months'][-1]}|{r['first_liquid']}|"
                         f"{r['last_seen']}")
        self._qr_log("C|" + json.dumps(self.counts, sort_keys=True))
