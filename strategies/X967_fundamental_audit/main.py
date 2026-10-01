# X967 v1.0 — Morningstar fundamental-data point-in-time AUDIT (infrastructure; NO orders; not a strategy, not a
# trial; owner request "Approve Fundamental-Data Scope Expansion and Run Data Audit Only", 2026-10-01).
# Data quality and coverage ONLY: it never ranks stocks, forms portfolios or measures any return.
# Every output is a count, a bucket, a date, an SEC accession year or a ratio - never a raw fundamental value.
#
# A. Timing, every day, every eligible stock (latest report = earning_reports.<field>.value):
#    file date <= today (else look-ahead); accession-number filing year <= today's year (else a later filing -
#    e.g. a restatement - leaked backward); accession year == file-date year; on each NEW period: days from
#    file date to first sight, days from period end to file date (exactly 45 = the documented approximation).
# B. Revisions of an already-delivered period: same period end with a new accession (amendment) or with changed
#    values under the same accession (silent overwrite), checked at period changes and monthly.
# C. Monthly coverage of the curated profitability/quality fields over the eligible universe, by year, and
#    missingness of the core set by market-cap tercile, sector, exchange, listing age and distress
#    (adjusted price down > 50% over 12 months).
# D. Monthly market cap vs raw price x shares (three share-count fields): ratio histogram (1.0 = point-in-time;
#    a ratio near 1/k = shares restated for a later k-for-1 split).
# E. Staleness of the latest report; fiscal-year-end changes; sample companies (normal filers, splits,
#    acquisitions, bankruptcies, restatements) logged with dates, accession numbers and ratios only.
from AlgorithmImports import *
import json
from qr_harness import QRAlgorithm
from audit_lib import (GAP_BUCKETS, LAG_BUCKETS, RATIO_BUCKETS, accession_year, add, age_bucket, bucket,
                       cap_tercile, days, fingerprint, present, rel_change)

IS_ = "financial_statements.income_statement."
BS_ = "financial_statements.balance_sheet."
CF_ = "financial_statements.cash_flow_statement."
FIELDS = {   # name -> (path, periods checked for coverage)
    "revenue": (IS_ + "total_revenue", ("three_months", "twelve_months")),
    "gross_profit": (IS_ + "gross_profit", ("three_months", "twelve_months")),
    "cost_of_revenue": (IS_ + "cost_of_revenue", ("three_months", "twelve_months")),
    "operating_income": (IS_ + "operating_income", ("three_months", "twelve_months")),
    "net_income": (IS_ + "net_income", ("three_months", "twelve_months")),
    "total_assets": (BS_ + "total_assets", ("three_months", "twelve_months")),
    "stockholders_equity": (BS_ + "stockholders_equity", ("three_months", "twelve_months")),
    "total_debt": (BS_ + "total_debt", ("three_months", "twelve_months")),
    "ordinary_shares_number": (BS_ + "ordinary_shares_number", ("three_months", "twelve_months")),
    "operating_cash_flow": (CF_ + "operating_cash_flow", ("three_months", "twelve_months")),
    "free_cash_flow": (CF_ + "free_cash_flow", ("three_months", "twelve_months")),
    "basic_average_shares": ("earning_reports.basic_average_shares", ("three_months", "twelve_months")),
    "roa": ("operation_ratios.roa", ("value",)),
    "roe": ("operation_ratios.roe", ("value",)),
    "gross_margin": ("operation_ratios.gross_margin", ("value",)),
}
CORE = (("revenue", "twelve_months"), ("gross_profit", "twelve_months"), ("operating_income", "twelve_months"),
        ("net_income", "twelve_months"), ("total_assets", "three_months"), ("stockholders_equity", "three_months"),
        ("operating_cash_flow", "twelve_months"))
FP_FIELDS = (("revenue", "three_months"), ("net_income", "three_months"), ("total_assets", "three_months"),
             ("stockholders_equity", "three_months"))
SAMPLE = {"AAPL": "normal+splits 2014/2020", "MSFT": "normal (June FY)", "JNJ": "normal", "XOM": "normal",
          "KO": "normal", "NVDA": "split 2021", "TSLA": "split 2020", "NFLX": "split 2015", "V": "split 2015",
          "GOOGL": "share-class 2014", "TWX": "acquired 2018", "MON": "acquired 2018", "DTV": "acquired 2015",
          "CHK": "bankruptcy 2020", "HTZ": "restatement 2014 / bankruptcy 2020", "KHC": "restatement 2019"}
MAX_EXAMPLES = 60


def get(obj, path):
    for p in path.split("."):
        obj = getattr(obj, p)
    return obj


def as_date(v):
    try:
        return v.date() if hasattr(v, "date") and callable(v.date) else v
    except Exception:
        return None


class FundamentalAudit(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self.state = {}            # sid -> dict(pe, acc, fp)
        self.month = None
        self.prev_adj = {}         # sid -> list of (yyyymm, adjusted price) for the distress proxy
        self.fye = {}              # sid -> fiscal year end month
        self.sample_seen = {}      # ticker -> dict(first, last, last_eligible)
        self.sample_ratio = {}
        self.a = {"days": 0, "stock_days": 0, "read_errors": 0,
                  "file_date_after_today": 0, "accession_year_after_today": 0, "accession_year_ne_file_year": 0,
                  "accession_unparsed": 0, "no_file_date": 0, "default_period_ne_quarter": 0,
                  "statements_period_ne_report_period": 0, "statement_file_date_after_today": 0, "new_periods": 0, "period_backwards": 0,
                  "lag_first_seen_minus_file": {}, "gap_file_minus_period_end": {}, "gap_exactly_45_by_year": {},
                  "new_periods_by_year": {}, "amended_same_period": 0, "amended_file_date_changed": 0,
                  "silent_value_change_same_period": 0, "silent_change_fields": {}, "period_types": {},
                  "examples": {"look_ahead": [], "accession_leak": [], "silent_change": [], "amended": [],
                               "fiscal_year_change": [], "accession_ne_file_year": [], "cap_ratio_far": []},
                  "coverage": {}, "missing_core": {}, "staleness_by_year": {}, "cap_ratio": {},
                  "fiscal_year_end_changes": 0, "eligible_by_year": {}, "eps_consistency": {}}
        self.last_seen = {}        # sid -> last month-start date seen eligible (survivorship check)

    # ------------------------------------------------------------------ universe hook (all fundamentals)
    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        elig = set(self.qr_eligible)
        by_sym = {}
        for f in fl:
            if f.symbol in elig:
                by_sym[f.symbol] = f
            t = f.symbol.value
            if t in SAMPLE:
                self._sample(t, f, today, f.symbol in elig)
        self._daily(by_sym, today)
        m = (today.year, today.month)
        if m != self.month and by_sym:
            self.month = m
            self._monthly(by_sym, today)
        return []

    def qr_select_universe(self, eligible):
        return []

    # ------------------------------------------------------------------ A/B timing and revisions (daily)
    def _daily(self, by_sym, today):
        a = self.a
        a["days"] += 1
        for sym, f in by_sym.items():
            a["stock_days"] += 1
            try:
                er = f.earning_reports
                pe, fd = as_date(er.period_ending_date.three_months), as_date(er.file_date.three_months)
                acc = er.accession_number.three_months
                fs = f.financial_statements
                fpe, ffd = as_date(fs.period_ending_date.three_months), as_date(fs.file_date.three_months)
                dpe = as_date(er.period_ending_date.value)
            except Exception:
                a["read_errors"] += 1
                continue
            if dpe != pe:
                a["default_period_ne_quarter"] += 1
            if fpe != pe:
                a["statements_period_ne_report_period"] += 1
            if ffd is not None and hasattr(ffd, "year") and ffd.year > 1990 and ffd > today:
                a["statement_file_date_after_today"] += 1
                self._ex("look_ahead", f"{today}|{sym.id}|statements|pe={fpe}|fd={ffd}")
            sid = str(sym.id)
            if fd is None or not hasattr(fd, "year") or fd.year < 1990:
                a["no_file_date"] += 1
                continue
            if fd > today:
                a["file_date_after_today"] += 1
                self._ex("look_ahead", f"{today}|{sid}|pe={pe}|fd={fd}")
            ay = accession_year(acc)
            if ay is None:
                a["accession_unparsed"] += 1
            else:
                if ay > today.year:
                    a["accession_year_after_today"] += 1
                    self._ex("accession_leak", f"{today}|{sid}|pe={pe}|fd={fd}|acc={acc}")
                if ay != fd.year:
                    a["accession_year_ne_file_year"] += 1
                    self._ex("accession_ne_file_year", f"{today}|{sid}|pe={pe}|fd={fd}|acc={acc}")
            st = self.state.get(sid)
            if st is None or st["pe"] != pe:
                if st is not None and pe is not None and st["pe"] is not None and pe < st["pe"]:
                    a["period_backwards"] += 1
                if st is not None:          # first sight of a new period (not the first day we see the stock)
                    a["new_periods"] += 1
                    add(a["new_periods_by_year"], str(today.year))
                    lag, gap = days(today, fd), days(fd, pe)
                    if lag is not None:
                        add(a["lag_first_seen_minus_file"], bucket(lag, LAG_BUCKETS))
                    if gap is not None:
                        add(a["gap_file_minus_period_end"], bucket(gap, GAP_BUCKETS))
                        if gap == 45:
                            add(a["gap_exactly_45_by_year"], str(today.year))
                    try:
                        add(a["period_types"], str(f.earning_reports.period_type.value))
                    except Exception:
                        pass
                self.state[sid] = dict(pe=pe, acc=acc, fd=fd, fpe=fpe, ffd=ffd, fp=self._fp(f))
            elif st["acc"] != acc:
                a["amended_same_period"] += 1
                if st["fd"] != fd:
                    a["amended_file_date_changed"] += 1
                self._ex("amended", f"{today}|{sid}|pe={pe}|old_acc={st['acc']}|new_acc={acc}|old_fd={st['fd']}|new_fd={fd}")
                st.update(acc=acc, fd=fd, fpe=fpe, ffd=ffd, fp=self._fp(f))
            if st is not None and (st.get("fpe") != fpe or st.get("ffd") != ffd):
                st.update(fpe=fpe, ffd=ffd, fp=self._fp(f))     # statements moved to a new period/filing

    def _fp(self, f):
        vals = []
        for name, per in FP_FIELDS:
            try:
                vals.append(getattr(get(f, FIELDS[name][0]), per))
            except Exception:
                vals.append(None)
        return fingerprint(vals)

    # ------------------------------------------------------------------ C/D/E monthly
    def _monthly(self, by_sym, today):
        a = self.a
        y = str(today.year)
        add(a["eligible_by_year"], y, len(by_sym))
        cov = a["coverage"].setdefault(y, {})
        caps = {}
        rows = []
        for sym, f in by_sym.items():
            sid = str(sym.id)
            pres = {}
            for name, (path, pers) in FIELDS.items():
                for per in pers:
                    try:
                        v = getattr(get(f, path), per)
                    except Exception:
                        v = None
                    ok = present(v)
                    pres[(name, per)] = ok
                    add(cov, f"{name}.{per}", int(ok))
            core = all(pres.get(k, False) for k in CORE)
            add(cov, "CORE_SET", int(core))
            # silent revision of the current period (same accession, values changed)
            st = self.state.get(sid)
            if st is not None:
                fp = self._fp(f)
                if fp != st["fp"]:
                    try:
                        fs = f.financial_statements
                        same = (as_date(fs.period_ending_date.three_months) == st["fpe"]
                                and as_date(fs.file_date.three_months) == st["ffd"])
                    except Exception:
                        same = False
                    if same:
                        a["silent_value_change_same_period"] += 1
                        changed = [FP_FIELDS[i][0] for i, (u, v) in enumerate(zip(st["fp"], fp)) if u != v]
                        for c in changed:
                            add(a["silent_change_fields"], c)
                        rc = [rel_change(v, u) for u, v in zip(st["fp"], fp)]
                        self._ex("silent_change", f"{today}|{sid}|statements_pe={st['fpe']}|fd={st['ffd']}|fields={changed}|"
                                                  f"rel={[None if r is None else round(r, 4) for r in rc]}")
                    st["fp"] = fp
            try:
                cap = float(f.market_cap)
            except Exception:
                cap = 0.0
            caps[sid] = cap
            rows.append((sid, f, core))
            # staleness of the latest report
            try:
                fd = as_date(f.earning_reports.file_date.value)
                age = days(today, fd)
                if age is not None:
                    add(a["staleness_by_year"].setdefault(y, {}), bucket(age, (100, 130, 200, 400, 10 ** 6)))
            except Exception:
                pass
            # market cap vs raw price x shares
            try:
                px = float(f.price)
                for lab, path in (("so", "company_profile.shares_outstanding"),
                                  ("scl", "company_profile.share_class_level_shares_outstanding"),
                                  ("bas3m", "earning_reports.basic_average_shares.three_months"),
                                  ("osn3m", BS_ + "ordinary_shares_number.three_months")):
                    sh = float(get(f, path))
                    if px > 0 and sh > 0 and cap > 0:
                        r = cap / (px * sh)
                        add(a["cap_ratio"].setdefault(lab, {}).setdefault(y, {}), bucket(r, RATIO_BUCKETS))
                        if lab == "so" and not 0.45 < r < 2.2:
                            self._ex("cap_ratio_far", f"{today}|{sid}|{f.symbol.value}|cap/(px*so)={r:.4f}")
            except Exception:
                pass
            # per-share consistency: net income TTM / (basic EPS TTM x basic average shares TTM) (1.0 = consistent)
            try:
                ni = float(get(f, IS_ + "net_income").twelve_months)
                eps = float(f.earning_reports.basic_eps.twelve_months)
                bas = float(f.earning_reports.basic_average_shares.twelve_months)
                if ni != 0 and eps != 0 and bas > 0:
                    add(a["eps_consistency"].setdefault(y, {}), bucket(ni / (eps * bas), RATIO_BUCKETS))
            except Exception:
                pass
            self.last_seen[sid] = today
            # fiscal-year-end changes
            try:
                fye = int(f.company_reference.fiscal_year_end)
                old = self.fye.get(sid)
                if old is not None and old != fye:
                    a["fiscal_year_end_changes"] += 1
                    self._ex("fiscal_year_change", f"{today}|{sid}|{old}->{fye}")
                self.fye[sid] = fye
            except Exception:
                pass
        terc = cap_tercile(caps)
        ym = today.year * 100 + today.month
        for sid, f, core in rows:
            dims = [("size", terc.get(sid, "?"))]
            try:
                dims.append(("sector", str(int(f.asset_classification.morningstar_sector_code))))
            except Exception:
                dims.append(("sector", "unknown"))
            try:
                dims.append(("exchange", str(f.security_reference.exchange_id)))
            except Exception:
                dims.append(("exchange", "unknown"))
            try:
                ipo = as_date(f.security_reference.ipo_date)
                dims.append(("age", age_bucket(ipo.year if ipo is not None else None, today.year)))
            except Exception:
                dims.append(("age", "unknown"))
            try:
                adj = float(f.adjusted_price)
                hist = self.prev_adj.setdefault(sid, [])
                hist.append((ym, adj))
                old = [p for m, p in hist if m <= ym - 100]
                if old:
                    dims.append(("distress", "down>50%" if adj < 0.5 * old[-1] else "not"))
                    self.prev_adj[sid] = [(m, p) for m, p in hist if m > ym - 100] + [max(((m, p) for m, p in hist if m <= ym - 100))]
                else:
                    dims.append(("distress", "no_history"))
            except Exception:
                dims.append(("distress", "unknown"))
            for d, lab in dims:
                cell = self.a["missing_core"].setdefault(f"{d}={lab}", [0, 0])
                cell[0] += 1
                cell[1] += int(not core)

    # ------------------------------------------------------------------ E sample companies
    def _sample(self, t, f, today, eligible):
        s = self.sample_seen.setdefault(t, {"first": str(today), "last": None, "last_eligible": None, "periods": 0})
        s["last"] = str(today)
        if eligible:
            s["last_eligible"] = str(today)
        try:
            er = f.earning_reports
            pe, fd, acc = as_date(er.period_ending_date.value), as_date(er.file_date.value), er.accession_number.value
        except Exception:
            return
        key = "s:" + t
        st = self.sample_ratio.get(key)
        try:
            cap, px, so = float(f.market_cap), float(f.price), float(f.company_profile.shares_outstanding)
            r = cap / (px * so) if px > 0 and so > 0 else None
        except Exception:
            r, so = None, None
        if st is None or st["pe"] != pe:
            s["periods"] += 1
            lag, gap = days(today, fd), days(fd, pe)
            self._qr_log(f"QRF67|sample|{t}|seen={today}|pe={pe}|fd={fd}|acc={acc}|acc_year={accession_year(acc)}"
                         f"|lag_days={lag}|gap_days={gap}|eligible={int(eligible)}")
        if r is not None and (st is None or st.get("r") is None or abs(r / st["r"] - 1) > 0.02
                              or (st.get("so") and so and abs(so / st["so"] - 1) > 0.02)):
            so_ratio = None if not (st and st.get("so") and so) else so / st["so"]
            self._qr_log(f"QRF67|shares|{t}|{today}|cap_over_px_x_so={r:.4f}|so_change_ratio="
                         f"{'' if so_ratio is None else f'{so_ratio:.4f}'}")
        self.sample_ratio[key] = dict(pe=pe, r=r, so=so)

    def _ex(self, kind, line):
        lst = self.a["examples"][kind]
        if len(lst) < MAX_EXAMPLES:
            lst.append(line)

    def qr_on_end(self):
        a = dict(self.a)
        end = self.time.date()
        gone = [d for d in self.last_seen.values() if days(end, d) is not None and days(end, d) > 60]
        a["ever_eligible"] = len(self.last_seen)
        a["eligible_then_disappeared_before_end"] = len(gone)
        a["disappeared_by_year"] = {}
        for d in gone:
            add(a["disappeared_by_year"], str(d.year))
        a["sample_seen"] = self.sample_seen
        text = json.dumps(a, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRF67|summary|{i // 9000}|{text[i:i + 9000]}")
