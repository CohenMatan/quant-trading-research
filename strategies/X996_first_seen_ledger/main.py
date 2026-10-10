# X996 v1.0 — P7-CP5d (owner D186) SCORE V1 MIGRATION FEASIBILITY on QuantConnect's new default dataset
# (infrastructure; NO orders, NO returns, NO performance; QuantConnect's DEFAULT build, recorded). It is the X993 v1.1
# score export (frozen Score v1, frozen mechanics inputs, store-wide revenue baseline) with ONE change in the data-
# delivery layer: a report's availability is no longer the vendor file date but the day the report is FIRST SEEN in
# the historical Fundamental stream ("first seen in backtest time"):
#   M1  usable from the first selection day on which the report (company, period end) appears in the stream;
#   M2  usable from max(first seen, SEC original periodic filing date + 1 day) (no SEC filing matched -> never used).
# Revisions (same period, changed values; checked weekly on the score's ten report fields) enter the store as
# amendments from their own first-seen day (M2: also not before the SEC original filing + 1 day). No vendor file date,
# no +90-day estimate rule, no data-v1 holds / blocks / releases (they are keyed to the old vendor reports); the
# accession-year quarantine, the 200-day freshness, True TTM and every Score v1 rule are unchanged. SEC-repaired
# securities are fed from the SEC table exactly as in data v1.
# In-cloud validation (vendor values never leave QuantConnect; only counts, distributions and SHA-256 digests do):
#  - timing: first seen minus the SEC original filing date, by form and era; early cases vs 8-K earnings releases;
#  - vintage: the first-seen (and each revised) quarterly revenue and total assets vs the SEC value as first filed /
#    as later restated (and whether that later filing was already public on the day seen);
#  - truncation / determinism: SHA-256 digests of the ledger events, the eligible set and every review's score rows;
#  - universe migration: why each E993-02 (data v1) member is not eligible now; market-cap continuity across splits;
#  - coverage and Score v1 distributions (counts, histograms, layer statistics; no return of any kind).
# Window: official 2011-01-03 .. 2017-12-31 (or truncated at 2013-12-31), history-only warm-up from 2008-07-01.
from AlgorithmImports import *
from array import array
from datetime import date, datetime, timedelta
import hashlib
import json
import time
import numpy as np
import qr_fundamentals as F
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, WHITELIST, accession_year, as_date, read_values
from qr_harness import COMMON_STOCK, EXCHANGES, QRAlgorithm, exchange_of, non_common_reason
import qr_p7 as P
import qr_p7_score as S
import qr_p7_export as E
import qr_xs_diag as XD
import qr_xs_panel as XP
from p5d_ref import load_table

HIST_START = datetime(2007, 1, 1)
LEDGER_FROM = date(2010, 1, 1)
REVIEW_FROM = date(2011, 1, 1)
DIGEST_CUT = date(2013, 12, 31)          # truncation comparison boundary (E996-02 ends here)
EPOCH = date(2000, 1, 1)
BATCH = 100
TOL = 0.005                              # value match tolerance (SEC reference rounded to 4 significant digits)
PE_MATCH = 6                             # vendor / SEC period ends within 6 days are the same fiscal period
SPOT_SALT = "P7CP5d-slice-check"
SPOT_PER_REVIEW = 2
SPLIT_FROM = date(2010, 12, 1)
# the ten report fields Score v1 reads (True TTM quarters + fiscal-year totals of the four flows; two snapshots)
FP_KEYS = ("revenue_q", "revenue_ttm", "gross_profit_q", "gross_profit_ttm", "net_income_q", "net_income_ttm",
           "operating_cash_flow_q", "operating_cash_flow_ttm", "total_assets", "stockholders_equity")
VKEYS = ("revenue_q", "total_assets")     # the SEC vintage reference fields (p5d_ref 'vfields')
HBITS = ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5", "H6", "H7", "duplicate_class")


def _first_seen_available(period_end, file_date):
    """D186 data-delivery rule for this host: the store receives as 'file date' the day BEFORE the usable day, so a
    report is usable on (file date + 1); no estimated-date rule (first-seen days are observations, not estimates).
    SEC-repaired filings keep filing date + 1. Impossible timing (before the period end) stays never-usable."""
    if period_end is None or file_date is None or file_date < period_end:
        return None
    return file_date + timedelta(days=1)


F.available_from = _first_seen_available
F.is_estimated_file_date = lambda period_end, file_date: False


def get(obj, path):
    for p in path.split("."):
        obj = getattr(obj, p)
    return obj


def _sid(s):
    return str(s.id) if hasattr(s, "id") else str(s)


def _day(d):
    return int(np.datetime64(d.strftime("%Y-%m-%d")).astype(np.int64))


def _ds(day):
    return str(np.datetime64(int(day), "D"))


def dn(d):
    return (d - EPOCH).days


def add(h, k, n=1):
    h[k] = h.get(k, 0) + n


def g4(c):
    if c is None:
        return None
    a = abs(int(c))
    return (-1 if c < 0 else 1) * (a // 100) * 10.0 ** (a % 100 - 3)


def near(x, ref):
    return x is not None and ref is not None and ref != 0 and abs(x / ref - 1.0) <= TOL


def bucket(d):
    if d <= 0:
        return "le0"
    if d == 1:
        return "1"
    if d <= 5:
        return "2-5"
    if d <= 30:
        return "6-30"
    if d <= 90:
        return "31-90"
    return "gt90"


def hist5(xs):
    h = [0] * 21
    for x in xs:
        h[min(20, max(0, int(x) // 5))] += 1
    return h


def stats(xs):
    if not xs:
        return None
    a = np.asarray(xs, dtype=float)
    return dict(n=int(a.size), mean=round(float(a.mean()), 3), sd=round(float(a.std()), 3), min=float(a.min()),
                p10=float(np.percentile(a, 10)), median=float(np.median(a)), p90=float(np.percentile(a, 90)),
                max=float(a.max()))


class FirstSeenLedger(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        if self.qr_sec is None or self.qr_sic is None:
            raise Exception("X996 needs universe.sec_corrections (SEC identity / SIC layer)")
        if self.qr["end"] not in ("2013-12-31", "2017-12-31"):
            raise Exception("X996: P7-CP5d ends on 2013-12-31 (truncation run) or 2017-12-31")
        self.mode = str(self.qr_params.get("mode"))
        if self.mode not in ("M1", "M2"):
            raise Exception("X996: mode must be M1 or M2")
        self.end = date.fromisoformat(self.qr["end"])
        self.hist_end = datetime(self.end.year, self.end.month, self.end.day)
        self.last_session = np.datetime64(min(self.qr["end"], "2017-12-29")).astype(np.int64)
        self.t0 = time.perf_counter()
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS)
        ref = load_table()
        self.forms = {}                  # cik -> {sec pe day: (original filing day, 'Q'/'K', amendment-only)}
        self.pes = {}                    # cik -> sorted SEC period-end days
        for cik, flat in ref["filings"].items():
            d, pe = {}, 0
            for i in range(0, len(flat), 3):
                pe += flat[i]
                fd, fm = pe + flat[i + 1], flat[i + 2]
                d.setdefault(pe, []).append((fd, fm))
            out = {}
            for pe_, rows in d.items():
                orig = [r for r in rows if r[1] in (1, 2)]
                use = orig or rows
                fd, fm = min(use)
                out[pe_] = (fd, "Q" if fm in (1, 3) else "K", not orig)
            self.forms[cik] = out
            self.pes[cik] = sorted(out)
        self.vint = ref["vint"]
        self.events = {}
        for cik, deltas in ref["events"].items():
            s, acc = 0, []
            for x in deltas:
                s += x
                acc.append(s)
            self.events[cik] = acc
        osids = ref["old"]["sids"]
        self.old = {t: {osids[i] for i in ix} for t, ix in ref["old"]["reviews"].items()}
        self.cik = {}
        for sid, rows in (self.qr_sec.sic_history or {}).items():
            self.cik[sid] = [(date.fromisoformat(e), str(c) if c not in (None, "") else None) for e, _s, c in rows]
        self.prev_session = None
        self.done_t = None
        self.sym = {}
        self.mon = {}
        self.mon_sel = {}
        self.rev = E.RevenueLedger()
        self.first_seen = {}
        self.sec_next = {}
        self.led = {}                    # sid -> {pe ordinal: [first-seen day, fingerprint, revisions]}
        self.first_feed = {}             # sid -> first day with vendor fundamentals in the stream
        self.first_day = None
        self.week = None
        self.dg = {}                     # year -> sha256 of ledger events
        self.dg_cut = hashlib.sha256()
        self.eg = {}                     # year -> sha256 of the daily eligible set with market caps
        self.eg_cut = hashlib.sha256()
        self.mc = {}                     # sid -> (days, market caps, prices) while eligible, from SPLIT_FROM
        self.tm, self.vt, self.fdq, self.um = {}, {}, {}, {}
        self.c = dict(selections=0, month_ends=0, sec_fed=0, store_sids_max=0, reports_new=0, revisions=0,
                      no_period_end=0, pe_after_seen=0, pe_regress=0, weekly_scans=0, censored=0, unmapped_cik=0,
                      unmapped_period=0, m2_not_fed=0, m2_delayed=0, m2_revision_unfed=0, fed=0, quarantined_seen=0,
                      revision_to_missing=0, revision_from_missing=0)
        u = self._qr_u
        self.filt = (float(u.get("min_market_cap", 2e9)), float(u.get("min_price", 0.0)),
                     float(u.get("min_avg_dollar_volume", 0.0)), int(u.get("adv_days", 20)))

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:
            self.prev_session = self.time.date()

    def _cik_on(self, sid, today):
        out = None
        for eff, c in self.cik.get(sid, ()):
            if eff <= today:
                out = c
            else:
                break
        return out

    # ------------------------------------------------------------------------------------------------ ledger
    def _sec(self, cik, pe):
        """(SEC period-end day, original filing day, 'Q'/'K', amendment-only) of the matched fiscal period, or None."""
        ps = self.pes.get(cik)
        if not ps:
            return None
        x = dn(pe)
        i = int(np.searchsorted(ps, x))
        best = None
        for j in (i - 1, i):
            if 0 <= j < len(ps) and abs(ps[j] - x) <= PE_MATCH and (best is None or abs(ps[j] - x) < abs(best - x)):
                best = ps[j]
        if best is None:
            return None
        fd, fm, am = self.forms[cik][best]
        return best, fd, fm, am

    def _digest(self, today, line):
        y = today.year
        if y not in self.dg:
            self.dg[y] = hashlib.sha256()
        b = (line + "\n").encode()
        self.dg[y].update(b)
        if today <= DIGEST_CUT:
            self.dg_cut.update(b)

    def _vintage(self, kind, cik, m, vals, today):
        """Aggregate match category of the vendor value (as seen today) against the SEC value as first filed and the
        first later differing value, for quarterly revenue and total assets."""
        row = self.vint.get(cik, {}).get(str(m[0]))
        td = dn(today)
        for i, f in enumerate(VKEYS):
            r = (row or [])[4 * i:4 * i + 4] + [None] * 4
            first, foff, later, loff = r[0], r[1], r[2], r[3]
            v = vals.get(f)
            if first is None:
                cat, restated = "no_ref", False
            else:
                fv, ffd = g4(first), m[0] + foff
                lv = g4(later) if later is not None else None
                lfd = ffd + loff if later is not None else None
                restated = lv is not None and lfd + 1 > td          # the restatement was still in the future
                if v is None:
                    cat = "vendor_missing"
                else:
                    a, b = near(v, fv), near(v, lv)
                    if a and b:
                        cat = "both"
                    elif a:
                        cat = "first" if ffd + 1 <= td else "first_before_sec"
                    elif b:
                        cat = "later_public" if lfd + 1 <= td else "later_FUTURE"
                    else:
                        cat = "neither"
            add(self.vt, f"{kind}|{f}|{cat}")
            if restated:
                add(self.vt, f"{kind}|{f}|restated_pending|{cat}")

    def _timing(self, sid, cik, pe, m, fd, today):
        era = "2008" if m[1] < dn(date(2009, 1, 1)) else ("2009-2012" if m[1] < dn(date(2013, 1, 1)) else "2013-2017")
        d = dn(today) - m[1]
        b = bucket(d)
        yr = str((EPOCH + timedelta(days=m[1])).year)
        add(self.tm, f"{m[2]}|{era}|{b}")
        add(self.tm, f"{m[2]}|{yr}|{b}")
        if m[3]:
            add(self.tm, f"{m[2]}|amendment_only")
        if d <= 0:
            ev = self.events.get(cik, ())
            lo, hi = dn(pe), dn(today) - 1
            j = int(np.searchsorted(ev, lo))
            why = "earnings_8k" if j < len(ev) and ev[j] <= hi else "unexplained"
            add(self.tm, f"early|{m[2]}|{era}|{why}|{bucket(1 - d)}")     # bucket of (SEC filing - first seen + 1)
        # the vendor's own file date (diagnostic only; never used)
        if fd is None:
            add(self.fdq, "missing")
        elif fd < pe:
            add(self.fdq, "before_period_end")
        else:
            if (fd - pe).days == F.APPROX_GAP_DAYS:
                add(self.fdq, "pe_plus_45")
            k = dn(fd) - m[1]
            add(self.fdq, "eq_sec" if k == 0 else ("before_sec" if k < 0 else "after_sec"))
            add(self.fdq, "seen_minus_fd|" + bucket((today - fd).days))

    def _usable(self, today, m):
        if self.mode == "M1":
            return today
        if m is None:
            return None
        return max(today, EPOCH + timedelta(days=m[1] + 1))

    @staticmethod
    def _read1(f, k):
        try:
            return F.clean(getattr(get(f, WHITELIST[k][0]), WHITELIST[k][1]))
        except Exception:
            return None

    def _ledger(self, f, sid, today, scan):
        try:
            er = f.earning_reports
            pe = as_date(er.period_ending_date.three_months)
        except Exception:
            pe = None
        if pe is None:
            self.c["no_period_end"] += 1
            return
        self.first_feed.setdefault(sid, today)
        led = self.led.setdefault(sid, {})
        pk = pe.toordinal()
        e = led.get(pk)
        if e is not None:
            if not scan:
                return
            fp = tuple(self._read1(f, k) for k in FP_KEYS)
            if fp == e[1]:
                return
            kind = "revision"
            self.c["revisions"] += 1
            if any(a is None and b is not None for a, b in zip(fp, e[1])):
                self.c["revision_to_missing"] += 1
            if any(a is not None and b is None for a, b in zip(fp, e[1])):
                self.c["revision_from_missing"] += 1
            e[1] = fp
            e[2] += 1
        else:
            kind = "new"
            self.c["reports_new"] += 1
            if led and pk < max(led):
                self.c["pe_regress"] += 1
            fp = None
        vals = read_values(f, get)
        if fp is None:
            fp = tuple(vals[k] for k in FP_KEYS)
            led[pk] = [today, fp, 0]
        try:
            ay = accession_year(er.accession_number.three_months)
        except Exception:
            ay = None
        try:
            fd = as_date(er.file_date.three_months)
        except Exception:
            fd = None
        self._digest(today, f"{today}|{sid}|{pk}|{kind}|{fp!r}")
        if pe > today:
            self.c["pe_after_seen"] += 1
            return
        if ay is not None and ay > today.year:
            self.c["quarantined_seen"] += 1
        cik = self._cik_on(sid, today)
        m = self._sec(cik, pe) if cik is not None else None
        censored = kind == "new" and (today == self.first_feed[sid] or today == self.first_day)
        if kind == "new":
            if censored:
                self.c["censored"] += 1
            elif cik is None:
                self.c["unmapped_cik"] += 1
            elif m is None:
                self.c["unmapped_period"] += int(pe >= date(2008, 6, 30))
            else:
                self._timing(sid, cik, pe, m, fd, today)
        if m is not None:
            self._vintage(kind + ("_censored" if censored else ""), cik, m, vals, today)
        use = self._usable(today, m)
        if use is None:
            self.c["m2_not_fed"] += 1
            return
        if use > today:
            self.c["m2_delayed"] += 1
        fd_syn = use - timedelta(days=1)
        if (sid, pe, fd_syn) in self.store.seen:
            self.c["m2_revision_unfed"] += 1
            return
        self.store.observe(sid, pe, fd_syn, vals, ay, today)
        self.c["fed"] += 1

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        out = super()._qr_select(fl)
        today = self.time.date()
        if self.first_day is None:
            self.first_day = today
        self.c["selections"] += 1
        wk = today.isocalendar()[:2]
        scan = wk != self.week
        if scan:
            self.week = wk
            self.c["weekly_scans"] += 1
        elig = {str(s.id): s for s in self.qr_eligible}
        adv = {str(s.id): v[1] for s, v in self.qr_eligible_info.items()}
        for f in fl:
            sid = str(f.symbol.id)
            self.first_seen.setdefault(sid, today)
            if not f.has_fundamental_data:
                if self.qr_sec.has(sid):
                    nxt = self.sec_next.get(sid)
                    if nxt is None or nxt <= today:
                        self.qr_sec.feed(sid, today, self.store)
                        self.c["sec_fed"] += 1
                        fut = [x.available for x in self.qr_sec.filings[sid] if x.available > today]
                        self.sec_next[sid] = min(fut) if fut else date.max
                continue
            self._ledger(f, sid, today, scan)
        # eligible-set digest (truncation / determinism) and market caps for the split-continuity check
        h = self.eg.setdefault(today.year, hashlib.sha256())
        line = (str(today) + "|" + ";".join(f"{str(s.id)}:{round(v[0] / 1e6)}" for s, v in
                                            sorted(self.qr_eligible_info.items(), key=lambda kv: str(kv[0].id)))
                + "\n").encode()
        h.update(line)
        if today <= DIGEST_CUT:
            self.eg_cut.update(line)
        if today >= SPLIT_FROM:
            byf = {str(f.symbol.id): f for f in fl}
            for s, v in self.qr_eligible_info.items():
                sid = str(s.id)
                r = self.mc.get(sid)
                if r is None:
                    r = self.mc[sid] = (array("i"), array("d"), array("d"))
                r[0].append(dn(today))
                r[1].append(float(v[0]))
                r[2].append(float(byf[sid].price) if sid in byf else float("nan"))
        t = self.prev_session
        if t is None or t == self.done_t or t > self.end:
            return out
        self.done_t = t
        nxt = self.securities[self.spy].exchange.hours.get_next_market_open(self.time, False).date()
        if (nxt.month != t.month or nxt.year != t.year) and t >= LEDGER_FROM:
            self._month_end(t, today, elig, adv, fl)
        return out

    def qr_select_universe(self, eligible):
        return []

    def _why_old(self, f, sid, today):
        """Why an E993-02 (data v1) member is not eligible in this run on the same review."""
        if f is None:
            return "not_in_feed"
        fix = not f.has_fundamental_data
        if fix and not self.qr_sec.has(sid):
            return "no_fundamentals"
        day = str(today)
        if not fix:
            try:
                sr = f.security_reference
                if sr.security_type != COMMON_STOCK:
                    return "not_common_type"
                if sr.is_depositary_receipt:
                    return "depositary"
                if not (bool(sr.is_primary_share) or str(f.company_reference.country_id) == "USA"):
                    return "not_primary_non_us"
                if non_common_reason(f, day) is not None:
                    return "fund_lp_other_non_common"
                if exchange_of(f, day) not in EXCHANGES:
                    return "exchange"
            except Exception:
                return "reference_error"
        min_cap, min_price, min_adv, adv_days = self.filt
        try:
            px = float(f.price)
            mc = float(f.market_cap) if not fix else (self.qr_sec.market_cap(sid, today, px) or 0.0)
        except Exception:
            return "value_error"
        if not mc > 0:
            return "mcap_missing"
        if mc < min_cap:
            return "mcap_1.5-2B" if mc >= 1.5e9 else "mcap_lt_1.5B"
        if px < min_price:
            return "price"
        dq = self._qr_dv.get(f.symbol)
        if dq is None or len(dq) < adv_days or not sum(dq) / len(dq) >= min_adv:
            return "adv"
        return "other"

    def _month_end(self, t, today, elig, adv, fl):
        self.c["month_ends"] += 1
        ym = (t.year, t.month)
        store_sids = sorted(set(self.store.hist) | set(self.store.pending))
        self.c["store_sids_max"] = max(self.c["store_sids_max"], len(store_sids))
        if t < date(2017, 1, 1):
            self.rev.record(ym, t, today, self.store, store_sids)
        if t >= REVIEW_FROM:
            rows = {}
            for sid, s in elig.items():
                self.sym[sid] = s
                v, det, bday = self.rev.baseline(ym, sid)
                rows[sid] = dict(sic=self.qr_sic.sic_on(sid, today), cik=self._cik_on(sid, today), adv=adv[sid],
                                 vals=E.fund_values(self.store, sid, today), base=v, base_det=det, base_day=bday)
            self.mon[t] = rows
            self.mon_sel[t] = today
            old = self.old.get(str(t))
            if old is not None:
                byf = {str(f.symbol.id): f for f in fl}
                y = str(t.year)
                for sid in old - set(elig):
                    add(self.um, f"{y}|old_only|{self._why_old(byf.get(sid), sid, today)}")
                for sid in set(elig) - old:
                    add(self.um, f"{y}|new_only|{'sec_repaired' if self.qr_sec.has(sid) else 'vendor'}")
                add(self.um, f"{y}|both", len(old & set(elig)))
        for k in [k for k in self.rev.v if k < (t.year - 1, t.month)]:
            self.rev.drop(k)

    # ------------------------------------------------------------------------------------------------ panel
    def _cols(self, frame, loc, cal, D, n, fields, st):
        out = {f: np.full((D, n), np.nan) for f in fields}
        if frame is None or frame.empty:
            return out
        idx = frame.index
        lmap = np.array([loc.get(_sid(s), -1) for s in idx.levels[0]], dtype=np.int64)
        cols = lmap[np.asarray(idx.codes[0])]
        days = XP.session_days(idx.get_level_values(-1).values)
        st["late_rows"] += int((days > self.last_session).sum())
        pos = np.searchsorted(cal, days)
        pc = np.minimum(pos, cal.size - 1)
        ok = (cols >= 0) & (cal[pc] == days) & (days <= self.last_session)
        key = pc[ok] * (n + 1) + cols[ok]
        _, cnt = np.unique(key, return_counts=True)
        st["duplicate_bars"] += int((cnt > 1).sum())
        for f in fields:
            if f in frame.columns:
                out[f][pc[ok], cols[ok]] = frame[f].to_numpy(dtype=float)[ok]
        return out

    def _events(self, frame, loc, cal, fields, st):
        out = {j: [] for j in loc.values()}
        if frame is None or frame.empty or not set(fields) <= set(frame.columns):
            return out
        idx = frame.index
        lmap = np.array([loc.get(_sid(s), -1) for s in idx.levels[0]], dtype=np.int64)
        cols = lmap[np.asarray(idx.codes[0])]
        eday = XP.event_days(idx.get_level_values(-1).values)
        vals = [frame[f].tolist() for f in fields]
        for r in range(len(cols)):
            if cols[r] < 0 or eday[r] > self.last_session:
                continue
            out[int(cols[r])].append((int(np.searchsorted(cal, eday[r])),) + tuple(v[r] for v in vals))
        return out

    def _adjust(self, raw, sc, sev, dev, st, D):
        vv = np.flatnonzero(np.isfinite(raw) & np.isfinite(sc) & (raw > 0) & (sc > 0))
        if vv.size and abs(sc[vv[-1]] / raw[vv[-1]] - 1.0) > 1e-6:
            sc = sc / (sc[vv[-1]] / raw[vv[-1]])
        ev = [(r_, float(fac)) for r_, typ, ref, fac in sev if "OCCUR" in str(typ).upper() or float(ref) > 0]
        de = [(r_, float(amt), float(ref)) for r_, amt, ref in dev]
        det = []
        mult, _ = XP.split_multiplier(raw, sc, ev, detail=det)
        dm = XP.dividend_multiplier(D, de)
        return mult, dm, [int(d[0]) for d in det], [(r_, amt / ref) for r_, amt, ref in de if ref > 0], ev

    def _build(self):
        t0 = time.perf_counter()
        spy = self.history(self.spy, HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        cal = np.unique(XP.session_days(spy.index.get_level_values(-1).values))
        cal = cal[cal <= self.last_session]
        D = cal.size
        sids = sorted({s for rows in self.mon.values() for s in rows})
        N = len(sids)
        st = dict(sessions=D, last_session=_ds(cal[-1]), securities=N, late_rows=0, duplicate_bars=0)
        C, Hh, L, Pt = (np.full((D, N), np.nan) for _ in range(4))
        self.unv, self.dist, self.splits = {}, {}, {}
        for i in range(0, N, BATCH):
            part = sids[i:i + BATCH]
            syms = [self.sym[s] for s in part]
            loc = {s: j for j, s in enumerate(part)}
            n = len(part)
            hr = self.history(syms, HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.RAW)
            hs = self.history(syms, HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            sp = self.history(Split, syms, HIST_START, self.hist_end)
            dv = self.history(Dividend, syms, HIST_START, self.hist_end)
            a = self._cols(hr, loc, cal, D, n, ("high", "low", "close"), st)
            b = self._cols(hs, loc, cal, D, n, ("close",), st)
            sev = self._events(sp, loc, cal, ("type", "referenceprice", "splitfactor"), st)
            dev = self._events(dv, loc, cal, ("distribution", "referenceprice"), st)
            for j in range(n):
                g = i + j
                raw = a["close"][:, j]
                if not np.any(np.isfinite(raw) & (raw > 0)):
                    continue
                mult, dm, unv, dist, ev = self._adjust(raw, b["close"][:, j], sev[j], dev[j], st, D)
                C[:, g], Hh[:, g], L[:, g], Pt[:, g] = raw * mult, a["high"][:, j] * mult, a["low"][:, j] * mult, \
                    raw * mult * dm
                self.unv[g], self.dist[g], self.splits[part[j]] = unv, dist, ev
        if st["late_rows"]:
            raise Exception("X996: history returned data after the end date")
        spy_raw = np.full(D, np.nan)
        d_spy = XP.session_days(spy.index.get_level_values(-1).values)
        ok = d_spy <= self.last_session
        spy_raw[np.searchsorted(cal, d_spy[ok])] = spy["close"].to_numpy(dtype=float)[ok]
        ssp = self.history(Split, [self.spy], HIST_START, self.hist_end)
        sev = self._events(ssp, {_sid(self.spy): 0}, cal, ("type", "referenceprice", "splitfactor"), st).get(0, [])
        m = np.ones(D)
        for r_, typ, ref, f in sev:
            if "OCCUR" in str(typ).upper() or float(ref) > 0:
                m[:r_] *= float(f)
        self.spy_c = spy_raw * m
        st["build_s"] = round(time.perf_counter() - t0, 1)
        self.cal, self.sids, self.col = cal, sids, {s: j for j, s in enumerate(sids)}
        self.C, self.H, self.L, self.P = C, Hh, L, Pt
        self.st["panel"] = st

    def _row(self, t):
        k = int(np.searchsorted(self.cal, _day(t)))
        if k >= self.cal.size or self.cal[k] != _day(t):
            raise Exception(f"X996: review session {t} not on the SPY calendar")
        return k

    def _life_start_row(self, j, k):
        if j not in self._life:
            v = P.valid_rows(self.C[:, j], self.P[:, j])
            self._life[j] = (v, P.life_starts(v))
        v, ls = self._life[j]
        b = int(np.searchsorted(v, k, side="right")) - 1
        return None if b < 0 else int(v[ls[b]])

    def _baselines(self, reviews, rows_k):
        """The X993 v1.1 baseline validity rule (same security life, same SEC registrant, every component quarter
        usable on or before the baseline selection day), unchanged."""
        self._life = {}
        st = dict(store_baseline=0, life_reject=0, cik_reject=0, pit_violations=0)
        for t in reviews:
            k, today = rows_k[t], self.mon_sel[t]
            for sid, e in self.mon[t].items():
                ok = False
                if e["base"] is not None:
                    st["store_baseline"] += 1
                    bsess, bsel = e["base_day"]
                    j = self.col.get(sid)
                    ls = self._life_start_row(j, k) if j is not None else None
                    ok, why = E.baseline_check(ls, self._row(bsess), self._cik_on(sid, bsel), self._cik_on(sid, today))
                    st["life_reject"] += int(why == "life")
                    st["cik_reject"] += int(why == "cik")
                    _, pe, fd = e["base_det"]
                    if any(x >= bsel.toordinal() for x in fd) or any(x > bsess.toordinal() for x in pe):
                        st["pit_violations"] += 1
                        ok = False
                e["base_ok"] = ok
                fi, why2, bo = E.fund_inputs(e["vals"], e["base"] if ok else None)
                e["fund"] = (fi, why2)
                e["base_only"] = bo
        self.st["baseline"] = st

    def _split_check(self):
        """Market-cap point-in-time check: across each split of an eligible security (2011+), a point-in-time market
        cap is continuous while the raw price jumps by the split factor; a market cap built from today's
        split-adjusted share count would jump with the price."""
        out = {}
        for sid, ev in self.splits.items():
            r = self.mc.get(sid)
            if r is None:
                continue
            days = np.frombuffer(r[0], dtype=np.int32) if len(r[0]) else np.zeros(0, dtype=np.int32)
            for row, fac in ev:
                if not fac > 0 or abs(np.log(fac)) < np.log(1.4):
                    continue
                e_ = dn(date.fromisoformat(_ds(self.cal[row])))
                i = int(np.searchsorted(days, e_ - 2, side="right")) - 1
                j = int(np.searchsorted(days, e_ + 3))
                if i < 0 or j >= days.size or e_ - days[i] > 10 or days[j] - e_ > 10:
                    add(out, "no_window")
                    continue
                lm, lp, lf = np.log(r[1][j] / r[1][i]), np.log(r[2][j] / r[2][i]), np.log(fac)
                if not (np.isfinite(lm) and np.isfinite(lp)):
                    add(out, "missing")
                    continue
                d_pit, d_non = abs(lm - (lp - lf)), abs(lm - lp)
                add(out, "mcap_pit_continuous" if d_pit < d_non and d_pit < abs(lf) / 2 else
                    ("mcap_jumps_with_price" if d_non < abs(lf) / 2 else "ambiguous"))
                add(out, "price_raw_jump" if abs(lp - lf) < abs(lf) / 2 else
                    ("price_adjusted" if abs(lp) < abs(lf) / 2 else "price_ambiguous"))
        return out

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        self.st = dict(mode=self.mode, end=str(self.end), checks=self.c, store_stats=dict(self.store.stats))
        self._build()
        t1 = time.perf_counter()
        reviews = sorted(self.mon)
        rows_k = {t: self._row(t) for t in reviews}
        need = sorted(set(rows_k.values()))
        a200 = {j: P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])["above200"][need]
                for j in range(len(self.sids))}
        rix = {k: i for i, k in enumerate(need)}
        days = self.cal.astype("datetime64[D]")
        lo_r = int(np.searchsorted(self.cal, _day(REVIEW_FROM)))
        exp_m = []
        for r in range(lo_r, self.cal.size):
            d0 = date.fromisoformat(str(days[r]))
            d1 = date.fromisoformat(str(days[r + 1])) if r + 1 < days.size else d0 + timedelta(days=40)
            if (d1.year, d1.month) != (d0.year, d0.month) and d0 + timedelta(days=1) <= self.end:
                exp_m.append(str(d0))
        self.st["calendar_check"] = dict(reviews=len(reviews), expected=len(exp_m),
                                         match=exp_m == [str(x) for x in reviews])
        self._baselines(reviews, rows_k)
        spot = dict(checked=0, mismatch=0)
        per_review, sdig = [], {}
        yr = {}
        tot_c, tot_p, lay, corr = [], [], {"T": [], "F": [], "S": []}, []
        for t in reviews:
            k = rows_k[t]
            elig = self.mon[t]
            st200 = {}
            for s in elig:
                x = a200[self.col[s]][rix[k]] if s in self.col else np.nan
                st200[s] = None if not np.isfinite(x) else bool(x)
            cache = {}

            def tech(s, k=k, cache=cache):
                if s not in cache:
                    j = self.col[s]
                    cache[s] = E.tech_at(self.C[:, j], self.P[:, j], k, self.unv.get(j, ()), self.dist.get(j, ()))
                return cache[s]
            res = E.score_review(elig, st200, tech, XD.ff12)
            for s in P.pick(sorted(res["kept"]), SPOT_PER_REVIEW, f"{SPOT_SALT}|{t}"):
                j = self.col[s]
                full = S.technical_inputs(self.C[:k + 1, j], self.P[:k + 1, j], k)
                sl = tech(s)[0]
                spot["checked"] += 1
                spot["mismatch"] += int(any(sl[f] != full[f] for f in ("close", "sma200", "mom_12_1", "vol60",
                                                                       "trend_state", "broken_trend", "age")))
            rows = res["rows"]
            sdig[str(t)] = hashlib.sha256(";".join(
                f"{s},{b},{tt},{p}" for s, (b, tt, p) in sorted(rows.items())).encode()).hexdigest()
            y = str(t.year)
            a = yr.setdefault(y, dict(reviews=0, eligible=0, nonfin=0, h2_nonfin=0, scored=0, candidates=0,
                                      ge75=0, ge80=0, ge85=0, ge90=0, field_present=[0] * 7,
                                      bits={b: 0 for b in HBITS}, old_overlap=0, old_overlap_nonfin=0,
                                      old_overlap_h2=0))
            a["reviews"] += 1
            old = self.old.get(str(t), set())
            n_nf = n_h2 = n_sc = n_c = 0
            cnt = [0, 0, 0, 0]
            for s, (bits, tot, pts) in rows.items():
                e = elig[s]
                nonfin = e["sic"] is not None and not 6000 <= int(e["sic"]) <= 6999
                h2 = bool(bits & E.BIT["H2"])
                for b in HBITS:
                    a["bits"][b] += int(bool(bits & E.BIT[b]))
                if nonfin:
                    n_nf += 1
                    n_h2 += int(h2)
                    for i, v in enumerate(e["vals"] + [e["base"] if e.get("base_ok") else None]):
                        a["field_present"][i] += int(v is not None)
                if s in old:
                    a["old_overlap"] += 1
                    a["old_overlap_nonfin"] += int(nonfin)
                    a["old_overlap_h2"] += int(nonfin and h2)
                if tot is not None and not bits & E.BIT["duplicate_class"]:
                    n_sc += 1
                    tot_p.append(tot)
                    T_, F_, S_ = sum(pts[0:3]), sum(pts[3:7]), pts[7]
                    lay["T"].append(T_)
                    lay["F"].append(F_)
                    lay["S"].append(S_)
                if E.eligible_flag(bits, tot):
                    n_c += 1
                    tot_c.append(tot)
                    for i, th in enumerate((75, 80, 85, 90)):
                        cnt[i] += int(tot >= th)
            for key, v in (("eligible", len(rows)), ("nonfin", n_nf), ("h2_nonfin", n_h2), ("scored", n_sc),
                           ("candidates", n_c), ("ge75", cnt[0]), ("ge80", cnt[1]), ("ge85", cnt[2]),
                           ("ge90", cnt[3])):
                a[key] += v
            trend = S.spy_trend(self.spy_c, k)
            mb = res["breadth"][0]
            per_review.append([str(t), len(rows), n_nf, n_h2, n_sc, n_c] + cnt + [len(old), len(old & set(rows)),
                                                                                  S.regime(trend, mb)])
        self.st["slice_spot_check"] = spot
        self.st["score_s"] = round(time.perf_counter() - t1, 1)
        L3 = {k: np.asarray(v, dtype=float) for k, v in lay.items()}
        if L3["T"].size > 2:
            cm = np.corrcoef(np.vstack([L3["T"], L3["F"], L3["S"]]))
            corr = {k: (round(float(v), 4) if np.isfinite(v) else None)
                    for k, v in (("T_F", cm[0, 1]), ("T_S", cm[0, 2]), ("F_S", cm[1, 2]))}
        # synthetic export-shape check (no market data): a seeded synthetic score / response panel and the H022-style
        # summary statistic shape, to test whether such an aggregate can leave QuantConnect at all
        rng = np.random.default_rng(20261010)
        ic = []
        for _ in range(83):
            x = rng.normal(size=300)
            y = 0.03 * x + rng.normal(size=300)
            rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
            ic.append(float(np.corrcoef(rx, ry)[0, 1]))
        ic = np.asarray(ic)
        self.st["synthetic_export_check"] = dict(label="SYNTHETIC seeded numbers, no market data", n=83,
                                                 mean_ic=round(float(ic.mean()), 6),
                                                 t=round(float(ic.mean() / (ic.std(ddof=1) / np.sqrt(ic.size))), 4))
        self.st.update(
            per_review_cols=["review", "eligible", "nonfin", "h2_nonfin", "scored", "candidates", "ge75", "ge80",
                             "ge85", "ge90", "old_members", "old_still_eligible", "regime"],
            per_review=per_review, per_year=yr, totals_hist5_candidates=hist5(tot_c), totals_hist5_scored=hist5(tot_p),
            totals_candidates=stats(tot_c), totals_scored=stats(tot_p),
            layers={k: dict(stats=stats(v), hist5=hist5(v)) for k, v in lay.items()}, layer_corr=corr,
            field_order=["revenue_ttm4q", "gross_profit_ttm4q", "net_income_ttm4q", "operating_cash_flow_ttm4q",
                         "total_assets", "stockholders_equity", "revenue_baseline_valid"],
            timing=self.tm, vintage=self.vt, vendor_file_date=self.fdq, universe_migration=self.um,
            mcap_split_check=self._split_check(),
            digests=dict(ledger_by_year={str(y): h.hexdigest() for y, h in sorted(self.dg.items())},
                         ledger_to_2013=self.dg_cut.hexdigest(),
                         eligible_by_year={str(y): h.hexdigest() for y, h in sorted(self.eg.items())},
                         eligible_to_2013=self.eg_cut.hexdigest(), review_scores=sdig),
            ledger_reports=sum(len(v) for v in self.led.values()), ledger_sids=len(self.led))
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        text = json.dumps(self.st, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRP5D|{i // 9000}|{text[i:i + 9000]}")
