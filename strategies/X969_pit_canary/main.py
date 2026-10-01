# X969 v1.0 — point-in-time fundamentals-layer canary (infrastructure; NO orders; no rankings, no returns; D108).
# Runs the real qr_fundamentals.PITStore over the eligible >= $2B universe, 2010-2021, every day, and verifies:
#  C1 no record is ever exposed before its availability date; C2 estimated filing dates respect period end + 90;
#  C3 amendments become visible only after their own filing date; C4 share counts / per-share / unapproved fields
#  fail hard; C5 Visa is eligible on the corrected dates (D108 override); C6 known acquired/delisted companies stay
#  eligible until their deal dates; C7 the PIT 'financial-format' classification vs the vendor sector label (which
#  is audited for point-in-time changes); C8 freshness: nothing older than the policy is exposed; quarantine counts.
# Monthly coverage: eligible, usable, missing by cause, financial-format exclusions, missingness concentration.
# Outputs: counts, dates, tickers and ratios only (no raw fundamental values; licence).
from AlgorithmImports import *
import json
from qr_harness import QRAlgorithm, _attr
from qr_fundamentals import (DEFAULT_MAX_AGE_DAYS, FundamentalFieldError, PITStore, WHITELIST, accession_year,
                             check_field, financial_format, read_values)

DEAL = {"MON": "2018-06-07", "DTV": "2015-07-24", "TWX": "2018-06-14"}     # last trading days (public record)
NAMED = ("V", "MA", "JPM", "BAC", "AIG", "GS", "BRK.B", "AAPL", "XOM", "MON", "DTV", "TWX")
USABLE = ("revenue_ttm", "net_income_ttm", "total_assets", "stockholders_equity")


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


def add(h, k, n=1):
    h[k] = h.get(k, 0) + n


class PITCanary(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS)
        self.month = None
        self.c = {"days": 0, "stock_days": 0, "exposed_before_available": 0, "exposed_before_filing": 0,
                  "estimated_exposed_before_pe90": 0, "stale_exposed": 0, "amendment_exposed_early": 0,
                  "vendor_new_reports": 0, "exposure_delay_days": {}, "field_guard": {}, "visa": {},
                  "named_eligible_months": {}, "deal_check": {}, "coverage": {}, "missing_concentration": {},
                  "classification_changes": {}, "fin_vs_sector": {}, "quarantine_by_year": {},
                  "quarantine_companies": 0, "survivorship_liquid_no_fundamentals": {}, "survivorship_top": [],
                  "store_stats": None}
        # C4: hard failures for unsafe / unapproved fields
        for name in ("shares_outstanding", "basic_eps", "roe", "accession_number", "morningstar_sector_code", "foo"):
            try:
                check_field(name)
                self.c["field_guard"][name] = "ACCEPTED (FAIL)"
            except FundamentalFieldError:
                self.c["field_guard"][name] = "rejected"
        bad = [n for n, (p, _) in WHITELIST.items() if any(x in p for x in ("shares", "eps", "per_share", "ratio"))]
        self.c["field_guard"]["whitelist_paths_with_share_or_ratio"] = bad
        self.first_seen = {}       # (sid, pe, fd) -> first vendor sighting date
        self.prev_cls = {}         # sid -> (sector, template)
        self.rows = []             # (ym, sid, usable, cause, tercile) for missingness concentration
        self.last_seen = {}
        self.q_companies = set()

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        super()._qr_select(fl)
        today = self.time.date()
        day = today.strftime("%Y-%m-%d")
        elig = set(self.qr_eligible)
        c = self.c
        c["days"] += 1
        monthly = (today.year, today.month) != self.month
        by = {}
        for f in fl:
            if f.symbol in elig:
                by[f.symbol] = f
        # ------------------------------------------------ daily: feed the layer and check exposure rules
        for sym, f in by.items():
            c["stock_days"] += 1
            sid = str(sym.id)
            try:
                er = f.earning_reports
                pe, fd = as_date(er.period_ending_date.three_months), as_date(er.file_date.three_months)
                ay = accession_year(er.accession_number.three_months)
            except Exception:
                continue
            key = (sid, pe, fd)
            if key not in self.first_seen:
                self.first_seen[key] = today
                c["vendor_new_reports"] += 1
                if ay is not None and ay > today.year:
                    add(c["quarantine_by_year"], str(today.year))
                    self.q_companies.add(sid)
            self.store.observe(sid, pe, fd, read_values(f, get), ay, today)
            r = self.store.record(sid, today)
            if r is None:
                continue
            if r.available > today:
                c["exposed_before_available"] += 1
            if r.file_date >= today:
                c["exposed_before_filing"] += 1
            if r.estimated and (today - r.period_end).days < 90:
                c["estimated_exposed_before_pe90"] += 1
            if (today - r.period_end).days > DEFAULT_MAX_AGE_DAYS:
                c["stale_exposed"] += 1
            k0 = (sid, r.period_end, r.file_date)
            if k0 in self.first_seen and self.first_seen[k0] == today and r.file_date >= today:
                c["amendment_exposed_early"] += 1
            if self.first_seen.get(k0) == today:
                pass
        if monthly:
            self.month = (today.year, today.month)
            self._monthly(fl, by, today, day)
        return []

    def qr_select_universe(self, eligible):
        return []

    def _monthly(self, fl, by, today, day):
        c = self.c
        y = str(today.year)
        ym = today.year * 100 + today.month
        cov = c["coverage"].setdefault(y, {})
        caps = {str(s.id): float(f.market_cap) for s, f in by.items()}
        order = sorted(caps, key=lambda k: (caps[k], k))
        terc = {k: ("T1" if i < len(order) / 3 else "T2" if i < 2 * len(order) / 3 else "T3") for i, k in enumerate(order)}
        for sym, f in by.items():
            sid = str(sym.id)
            self.last_seen[sid] = today
            add(cov, "eligible")
            r = self.store.record(sid, today)
            pend = self.store.pending.get(sid) or []
            cur = self.store.current.get(sid)
            if r is not None and all(r.values.get(k) is not None for k in USABLE):
                cause = "usable"
                ff = financial_format(r.values)
                add(cov, "financial_format" if ff else "non_financial_usable" if ff is False else "unclassifiable")
            elif r is not None:
                cause = "missing_fields_in_filing"
            elif pend or (sid in self.q_companies and cur is None):
                cause = "withheld_timing_rule"           # estimated date waiting for +90, or quarantined
            elif cur is not None:
                cause = "stale_beyond_policy"
            else:
                cause = "no_filing_data"
            add(cov, cause)
            # classification metadata: does it ever change for a company? (point-in-time test)
            sec = _attr(f.asset_classification, "morningstar_sector_code", None)
            tpl = _attr(f.company_reference, "industry_template_code", None)
            prev = self.prev_cls.get(sid)
            if prev is not None:
                if prev[0] != sec:
                    add(c["classification_changes"], "sector")
                if prev[1] != tpl:
                    add(c["classification_changes"], "template")
            else:
                add(c["classification_changes"], "companies")
            self.prev_cls[sid] = (sec, tpl)
            if r is not None:
                ff = financial_format(r.values)
                add(c["fin_vs_sector"], f"fin_format={ff}|sector103={str(sec) == '103'}|template={tpl}")
            sector = "103" if str(sec) == "103" else "other"
            self.rows.append((ym, sid, cause, terc.get(sid, "?"), sector))
        # C5/C6 named companies
        for f in fl:
            t = f.symbol.value
            if t in NAMED and today.day <= 7:
                add(c["named_eligible_months"], f"{t}|{int(f.symbol in by)}")
                if t == "V":
                    c["visa"][day] = dict(eligible=int(f.symbol in by), sid=str(f.symbol.id),
                                          vendor_exchange=str(f.security_reference.exchange_id))
                if t in DEAL:
                    d = c["deal_check"].setdefault(t, {"last_eligible": None})
                    if f.symbol in by:
                        d["last_eligible"] = day
        # survivorship gap (D043) in the fundamental context: liquid securities with no fundamentals at all
        dvs = sorted(float(f.dollar_volume) for f in by.values())
        thr = dvs[len(dvs) // 10] if dvs else 0.0
        nof = [(float(f.dollar_volume), f.symbol.value) for f in fl if not f.has_fundamental_data and f.dollar_volume >= thr]
        add(c["survivorship_liquid_no_fundamentals"], y, len(nof))
        if today.month == 1:
            nof.sort(reverse=True)
            c["survivorship_top"].append(f"{day}|" + ",".join(t for _, t in nof[:25]))

    def qr_on_end(self):
        c = self.c
        end = self.time.date()
        gone = {sid for sid, d in self.last_seen.items() if (end - d).days > 60}
        conc = {}
        for ym, sid, cause, terc, sector in self.rows:
            y = str(ym // 100)
            fails = sid in gone and (end.year * 100 + end.month) - ym <= 100 and \
                (self.last_seen[sid].year * 100 + self.last_seen[sid].month) - ym <= 100
            for dim, lab in (("year", y), ("size", terc), ("sector", sector),
                             ("delisted_within_12m", "yes" if fails else "no")):
                cell = conc.setdefault(f"{dim}={lab}", {})
                add(cell, "n")
                add(cell, cause)
        c["missing_concentration"] = conc
        c["quarantine_companies"] = len(self.q_companies)
        c["store_stats"] = dict(self.store.stats)
        text = json.dumps(c, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRC69|summary|{i // 9000}|{text[i:i + 9000]}")
