# X972 v1.0 — post-remediation PIT canary and coverage/bias re-audit (infrastructure; NO orders, no rankings,
# no factor returns; D111). Universe = harness universe WITH the opt-in dated SEC correction layer
# (universe.sec_corrections). 2010-2021.
# Checks (counts of violations; all must be 0):
#  C1 an SEC filing is never visible before the day after its filing date (corrected companies)
#  C2 SEC amendments are visible only after their own filing date
#  C3 quarantined vendor values stay hidden unless on the SEC-verified release list; timing holds respected
#  C4 a corrected company is eligible only with a usable cover count (filed before today, cover <= 135 days old,
#     status 'repaired') and a reconstructed market cap >= $2B
#  C5 no future share information: the count used was filed before today; split adjustments only for splits
#     already observed (ex-date <= today)
#  C6 split handling: reconstructed market cap continuity across split dates of corrected companies
#  C7 acquisitions/delistings: a corrected company is never eligible after its last trading day
#  C8 Visa correction (dated exchange override) still eligible on the corrected dates
#  C9 financial-format classification stability (flips per company)
# Coverage by year and size; corrected vs native; quarantine coverage loss; universe composition returns
# (equal-weight month returns of native vs corrected eligible names: the D043 bias measure, not a factor).
# Outputs: counts, dates, identifiers and ratios only (no vendor values).
from AlgorithmImports import *
import json
from datetime import timedelta
from qr_harness import QRAlgorithm, _attr
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, accession_year, financial_format, read_values
from qr_sec_corrections import MAX_SHARE_AGE_DAYS

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


class RemediationCanary(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        if self.qr_sec is None:
            raise Exception("X972 needs universe.sec_corrections")
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS, holds=self.qr_timing_holds, releases=self.qr_quarantine_releases)
        self.c = {k: 0 for k in ("C1_sec_visible_before_filing", "C2_amendment_early", "C3_quarantine_exposed",
                                 "C3_hold_violated", "C4_unjustified_entry", "C5_future_share_info",
                                 "C6_split_jumps", "C7_eligible_after_last_trade", "stock_days", "corrected_days")}
        self.c.update(coverage={}, fin_flips={}, visa={}, exchange={}, split_checks=[], ret={}, size={},
                      corrected_first={}, corrected_last={}, quarantine_lost={})
        self.month = None
        self.prev_cls = {}
        self.prev_mc = {}
        self.last_px = {}            # sid -> (adjusted price, month) for month returns
        self.month_members = {}      # previous month's eligible: sid -> group
        self.delisted = {}
        self.seen_q = set()
        self.q_keys = set()          # vendor reports observed while quarantined (and not on the release list)
        self.q_latest = {}           # sid -> newest vendor report is quarantined
        self.member_px = {}          # sid -> last adjusted price seen this month (members of last month)

    def on_data(self, data):
        super().on_data(data)
        for sym, dl in data.delistings.items():
            if dl.type == DelistingType.DELISTED:
                self.delisted[str(sym.id)] = self.time.date()
        for sym, sp in data.splits.items():
            if sp.type == SplitType.SPLIT_OCCURRED and self.qr_sec.has(str(sym.id)):
                self.c["split_checks"].append([str(sym.id), str(self.time.date()), float(sp.split_factor)])

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        out = super()._qr_select(fl)
        today = self.time.date()
        day = str(today)
        sec = self.qr_sec
        elig = set(self.qr_eligible)
        corr = self.qr_corrected
        c = self.c
        monthly = (today.year, today.month) != self.month
        self.month = (today.year, today.month)
        by = {}
        for f in fl:
            if f.symbol in elig:
                by[str(f.symbol.id)] = f
        for sid, f in by.items():
            c["stock_days"] += 1
            fix = f.symbol in corr
            if fix:
                c["corrected_days"] += 1
                c["corrected_first"].setdefault(sid, day)
                c["corrected_last"][sid] = day
                fil, sh = sec.shares_on(sid, today)
                # C4 / C5: recompute the justification from first principles
                if (fil is None or sh is None or fil.available > today or fil.filed >= today
                        or (today - fil.cover_date).days > MAX_SHARE_AGE_DAYS
                        or sec.meta.get(sid, {}).get("status") != "repaired"
                        or sh * float(f.price) < 2e9):
                    c["C4_unjustified_entry"] += 1
                if fil is not None and any(ex > today for ex, _ in sec.splits.get(sid, ())):
                    c["C5_future_share_info"] += 1
                if sid in self.delisted and self.delisted[sid] < today:
                    c["C7_eligible_after_last_trade"] += 1
                # C6: market-cap continuity around split events
                mc = self.qr_eligible_info[f.symbol][0]
                pm = self.prev_mc.get(sid)
                if pm is not None and any(pm[0] < ex <= today for ex, _ in sec.splits.get(sid, ())):
                    if abs(mc / pm[1] - 1) > 0.35:
                        c["C6_split_jumps"] += 1
                    c["split_checks"].append([sid, day, round(mc / pm[1], 4)])
                self.prev_mc[sid] = (today, mc)
                sec.feed(sid, today, self.store)
                r = self.store.record(sid, today)
                if r is not None and r.file_date >= today:
                    c["C1_sec_visible_before_filing"] += 1
                if r is not None:
                    for fi in sec.filings.get(sid, ()):
                        if fi.form.endswith("/A") and fi.period_end == r.period_end and fi.filed == r.file_date \
                                and fi.filed >= today:
                            c["C2_amendment_early"] += 1
            else:
                try:
                    er = f.earning_reports
                    pe, fd = as_date(er.period_ending_date.three_months), as_date(er.file_date.three_months)
                    ay = accession_year(er.accession_number.three_months)
                except Exception:
                    continue
                k = (sid, pe, fd)
                if k not in self.seen_q:
                    self.seen_q.add(k)
                    q = ay is not None and ay > today.year and \
                        (str(pe), str(fd)) not in self.store.releases.get(sid, ())
                    if q:
                        self.q_keys.add(k)
                    self.q_latest[sid] = q
                    self.store.observe(sid, pe, fd, read_values(f, get), ay, today)
                r = self.store.record(sid, today)
                if r is not None:
                    if (sid, r.period_end, r.file_date) in self.q_keys:
                        c["C3_quarantine_exposed"] += 1
                    h = self.store.holds.get(sid, {}).get(str(r.period_end))
                    if h is not None and str(today) < h:
                        c["C3_hold_violated"] += 1
        if self.month_members:
            for f in fl:
                sid = str(f.symbol.id)
                if sid in self.month_members and float(f.adjusted_price or 0) > 0:
                    self.member_px[sid] = float(f.adjusted_price)
        if monthly:
            self._monthly(fl, by, today)
        return out

    def qr_select_universe(self, eligible):
        return []

    def _monthly(self, fl, by, today):
        c = self.c
        y = str(today.year)
        ym = today.year * 100 + today.month
        cov = c["coverage"].setdefault(y, {})
        corr = {str(s.id) for s in self.qr_corrected}
        caps = {str(s.id): v[0] for s, v in self.qr_eligible_info.items()}
        order = sorted(caps, key=lambda k: (caps[k], k))
        terc = {k: ("T1" if i < len(order) / 3 else "T2" if i < 2 * len(order) / 3 else "T3") for i, k in enumerate(order)}
        # universe-composition returns: previous month's members, equal weight, adjusted prices (characterisation)
        # (a member that stopped trading during the month counts at its last traded price)
        px = {str(f.symbol.id): float(f.adjusted_price) for f in fl if float(f.adjusted_price or 0) > 0}
        for sid, grp in self.month_members.items():
            p0 = self.last_px.get(sid)
            p1 = px.get(sid, self.member_px.get(sid))
            if p0 is None or p1 is None:
                add(c["ret"], f"{grp}|missing_price")
                continue
            if sid not in px:
                add(c["ret"], f"{grp}|ended_in_month")
            cell = c["ret"].setdefault(f"{grp}|{y}", [0, 0.0])
            cell[0] += 1
            cell[1] += p1 / p0 - 1
        self.month_members = {sid: ("corrected" if sid in corr else "native") for sid in by}
        self.last_px = {sid: px[sid] for sid in by if sid in px}
        self.member_px = {}
        for sid, f in by.items():
            grp = "corrected" if sid in corr else "native"
            add(cov, f"eligible_{grp}")
            add(c["size"], f"{y}|{terc.get(sid, '?')}|{grp}")
            r = self.store.record(sid, today)
            if r is not None and all(r.values.get(k) is not None for k in USABLE):
                add(cov, f"usable_{grp}")
                ff = financial_format(r.values)
                add(cov, f"financial_format_{grp}" if ff else f"operating_format_{grp}" if ff is False
                    else f"unclassifiable_{grp}")
                prev = self.prev_cls.get(sid)
                if prev is not None and prev != ff:
                    add(c["fin_flips"], sid)
                self.prev_cls[sid] = ff
            elif r is None and grp == "native":
                cur = self.store.current.get(sid)
                if cur is None and any(p for p in self.store.pending.get(sid, []) or []):
                    add(cov, "withheld_timing_native")
                else:
                    add(cov, f"no_usable_record_{grp}")
            else:
                add(cov, f"no_usable_record_{grp}")
            if grp == "corrected" and today.day <= 7:
                try:
                    ex = str(self.securities[f.symbol].primary_exchange)
                except Exception:
                    ex = "unsubscribed"
                add(c["exchange"], ex)
                if ex not in ("NYSE", "NASDAQ", "AMEX", "ARCA", "BATS"):
                    self._qr_log(f"EXCH|{sid}|{today}|{ex}")
        # quarantine coverage loss: native eligible names whose newest vendor report is quarantined and no usable
        # earlier record remains (counted from the store's statistics per month)
        add(c["quarantine_lost"], y, sum(1 for sid in by if sid not in corr and self.store.record(sid, today) is None
                                        and self.q_latest.get(sid)))
        for f in fl:
            if f.symbol.value == "V" and today.day <= 7:
                c["visa"][str(today)] = int(str(f.symbol.id) in by)
        for sid in corr:
            self._qr_log(f"M|{ym}|{sid}|{int(caps.get(sid, 0) / 1e6)}|{terc.get(sid, '?')}")

    def qr_on_end(self):
        c = self.c
        c["store_stats"] = dict(self.store.stats)
        c["fin_flips_summary"] = {"companies_with_flips": len(c["fin_flips"]),
                                  "flips": sum(c["fin_flips"].values())}
        c["delisted_corrected"] = {sid: str(d) for sid, d in self.delisted.items() if self.qr_sec.has(sid)}
        text = json.dumps(c, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRC72|{i // 9000}|{text[i:i + 9000]}")
