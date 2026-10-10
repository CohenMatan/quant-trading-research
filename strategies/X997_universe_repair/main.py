# X997 v1.1 (P7-CP5e): adds distinct-security counts of the frozen targets (recovered / still lost by reason; later-
# disappearing split) to the aggregates; nothing else changes (rules, universe, scores identical to v1.0).
# X997 v1.0 — P7-CP5e (owner D188) UNIVERSE REPAIR FEASIBILITY (infrastructure; NO orders, NO returns, NO performance;
# QuantConnect's DEFAULT build, recorded). The X996 M2 pipeline (frozen Score v1 / X993 v1.1; a report is usable from
# max(first seen in the stream, SEC original periodic filing + 1 day)) with two infrastructure changes under test:
#  1. SHADOW REPAIRED UNIVERSE: a security that passes every universe filter except that QuantConnect gives it no
#     market cap gets the D111 SEC market cap instead (qr_sec_corrections, unchanged: latest cover-page share count
#     usable on the day (filing + 1), cover date <= 135 days old, x split multiplier for splits after the cover date
#     and on/before the day, x raw price); eligible only if that is >= $2B. Securities with a QuantConnect market cap
#     keep it. Registrant = identity-v2 dated rows only. The repair is decided at the END of the run from values
#     recorded at each review (splits filtered to ex-date <= the review day), so nothing after a review is used.
#  2. EARLIER SEC IDENTITY (params identity = "extended"): for the M2 gate only, a report first seen before a
#     security's first identity-v2 row is mapped through the verified extension row (public EDGAR evidence, SAFE /
#     BOUNDED; research/phase7/cp5e/identity_extension.py) while the security's feed presence has been continuous
#     (no absence > 60 days) since the row start. identity = "v2" switches the extension off (baseline).
# The SEC original filing date now comes from EDGAR submissions (pre-XBRL filings included); the M2 rule is unchanged.
# Outputs (aggregates and SHA-256 digests only; no vendor value, no per-security row): target-population check,
# loss reasons, SEC-vs-QuantConnect market-cap classification agreement, threshold bands, split continuity of the SEC
# market cap, recovery and survivorship by year, identity mapping counts and value continuity, M2 coverage and
# Score v1 distributions. Window 2011-01-03 .. 2017-12-31, warm-up from 2008-07-01.
from AlgorithmImports import *
from datetime import date, datetime, timedelta
import hashlib
import json
import time
import numpy as np
import qr_fundamentals as F
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, WHITELIST, accession_year, as_date, read_values
from qr_harness import COMMON_STOCK, EXCHANGES, QRAlgorithm, exchange_of, is_us_common, non_common_reason
from qr_sec_corrections import SECCorrections, SECFiling
import qr_p7 as P
import qr_p7_score as S
import qr_p7_export as E
import qr_xs_diag as XD
import qr_xs_panel as XP
from p5e_ref import load_table

HIST_START = datetime(2007, 1, 1)
LEDGER_FROM = date(2010, 1, 1)
REVIEW_FROM = date(2011, 1, 1)
EPOCH = date(2000, 1, 1)
BATCH = 100
TOL = 0.005
PE_MATCH = 6
PRESENCE_GAP = 60
MIN_CAP = 2e9
BANDS = (1.5e9, 1.8e9, 2.0e9, 2.2e9, 2.5e9)
BAND_NAMES = ("lt1.5B", "1.5-1.8B", "1.8-2.0B", "2.0-2.2B", "2.2-2.5B", "gt2.5B")
SPOT_SALT = "P7CP5e-slice-check"
FP_KEYS = ("revenue_q", "revenue_ttm", "gross_profit_q", "gross_profit_ttm", "net_income_q", "net_income_ttm",
           "operating_cash_flow_q", "operating_cash_flow_ttm", "total_assets", "stockholders_equity")
HBITS = ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5", "H6", "H7", "duplicate_class")


def _first_seen_available(period_end, file_date):
    """P7-CP5d/e data-delivery rule (M2): the store receives as 'file date' the day BEFORE the usable day."""
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


def dd(n):
    return EPOCH + timedelta(days=int(n))


def add(h, k, n=1):
    h[k] = h.get(k, 0) + n


def g4(c):
    if c is None:
        return None
    a = abs(int(c))
    return (-1 if c < 0 else 1) * (a // 100) * 10.0 ** (a % 100 - 3)


def near(x, ref):
    return x is not None and ref is not None and ref != 0 and abs(x / ref - 1.0) <= TOL


def band(x):
    for b, n in zip(BANDS, BAND_NAMES):
        if x < b:
            return n
    return BAND_NAMES[-1]


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


class UniverseRepair(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        if self.qr_sec is None or self.qr_sic is None:
            raise Exception("X997 needs universe.sec_corrections (SEC identity / SIC layer)")
        if self.qr["end"] != "2017-12-31":
            raise Exception("X997: P7-CP5e ends on 2017-12-31")
        self.ident = str(self.qr_params.get("identity"))
        if self.ident not in ("extended", "v2"):
            raise Exception("X997: identity must be 'extended' or 'v2'")
        self.end = date(2017, 12, 31)
        self.hist_end = datetime(2017, 12, 31)
        self.last_session = np.datetime64("2017-12-29").astype(np.int64)
        self.t0 = time.perf_counter()
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS)
        ref = load_table()
        self.forms, self.pes, self.shrows = {}, {}, {}
        for cik, flat in ref["f"].items():
            d, pe, sh = {}, 0, []
            for i, r in enumerate(flat):
                pe += r[0]
                fd = pe + r[1]
                d.setdefault(pe, []).append((fd, r[2]))
                if len(r) >= 5 and r[4]:
                    cd = fd - r[3]
                    sh.append([f"{cik}-{i:05d}", "10-K" if r[2] == 2 else "10-Q", str(dd(fd)), str(dd(pe)),
                               str(dd(cd)), g4(r[4]), {}])
            out = {}
            for pe_, rows in d.items():
                orig = [x for x in rows if x[1] in (1, 2)]
                fd, fm = min(orig or rows)
                out[pe_] = (fd, "Q" if fm in (1, 3) else "K", not orig)
            self.forms[cik], self.pes[cik] = out, sorted(out)
            if sh:
                self.shrows[cik] = sh
        self.ext = {s: (dd(v[0]), str(v[1])) for s, v in ref["ext"].items()}
        self.v = ref["v"]
        osids = ref["old"]["sids"]
        self.old = {t: {osids[i] for i in ix} for t, ix in ref["old"]["reviews"].items()}
        self.old_last = self.old[max(self.old)]
        self.tgt_sha = ref["tgt_sha256"]
        self.cik = {}
        for sid, rows in (self.qr_sec.sic_history or {}).items():
            self.cik[sid] = [(date.fromisoformat(e), str(c) if c not in (None, "") else None) for e, _s, c in rows]
        self.prev_session = None
        self.done_t = None
        self.sym, self.mon, self.mon_sel = {}, {}, {}
        self.rev = E.RevenueLedger()
        self.sec_next = {}
        self.led = {}
        self.week = None
        self.first_day = None
        self.pres_start, self.pres_last = {}, {}
        self.cand = {}                   # review -> {sid: row dict + cik, px} (no QuantConnect market cap)
        self.val = []                    # (review, sid, cik, QuantConnect market cap, raw price) for the comparison
        self.tgt_per, self.tgt_reason, self.cstat = {}, {}, {}
        self.idc, self.id2 = {}, {}
        self.c = dict(selections=0, month_ends=0, sec_fed=0, reports_new=0, revisions=0, no_period_end=0,
                      pe_after_seen=0, fed=0, m2_not_fed=0, m2_delayed=0, m2_revision_unfed=0, ext_presence_break=0,
                      weekly_scans=0, cand_no_cik=0, cand_no_shares_table=0)
        u = self._qr_u
        self.filt = (float(u.get("min_market_cap", 2e9)), float(u.get("min_price", 0.0)),
                     float(u.get("min_avg_dollar_volume", 0.0)), int(u.get("adv_days", 20)))

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:
            self.prev_session = self.time.date()

    def _cik_v2(self, sid, today):
        out = None
        for eff, c in self.cik.get(sid, ()):
            if eff <= today:
                out = c
            else:
                break
        return out

    def _cik_m2(self, sid, today):
        c = self._cik_v2(sid, today)
        if c is not None:
            return c, "v2"
        if self.ident == "extended" and sid in self.ext:
            start, x = self.ext[sid]
            if today >= start:
                ps = self.pres_start.get(sid)
                if ps is not None and ps <= max(start, self.first_day):
                    return x, "ext"
                self.c["ext_presence_break"] += 1
        return None, None

    # ------------------------------------------------------------------------------------------------ ledger (M2)
    def _sec(self, cik, pe):
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
        led = self.led.setdefault(sid, {})
        pk = pe.toordinal()
        e = led.get(pk)
        if e is not None:
            if not scan:
                return
            fp = tuple(self._read1(f, k) for k in FP_KEYS)
            if fp == e[0]:
                return
            kind = "revision"
            self.c["revisions"] += 1
            e[0] = fp
        else:
            kind = "new"
            self.c["reports_new"] += 1
        vals = read_values(f, get)
        if kind == "new":
            led[pk] = [tuple(vals[k] for k in FP_KEYS)]
        try:
            ay = accession_year(er.accession_number.three_months)
        except Exception:
            ay = None
        if pe > today:
            self.c["pe_after_seen"] += 1
            return
        cik, src = self._cik_m2(sid, today)
        m = self._sec(cik, pe) if cik is not None else None
        y = str(today.year)
        if kind == "new":
            if m is None:
                add(self.idc, f"unmapped|{'no_cik' if cik is None else 'no_period'}|{y}")
            else:
                add(self.idc, f"mapped|{src}|{y}")
                row = self.v.get(cik, {}).get(str(m[0]))
                for i, fld in enumerate(("revenue_q", "total_assets")):
                    ref = g4(row[i]) if row and i < len(row) and row[i] is not None else None
                    k = "no_ref" if ref is None else ("vendor_missing" if vals.get(fld) is None else
                                                      ("match" if near(vals[fld], ref) else "differ"))
                    add(self.id2, f"{src}|{fld}|{k}")
        if m is None:
            self.c["m2_not_fed"] += 1
            return
        use = max(today, dd(m[1] + 1))
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
            last = self.pres_last.get(sid)
            if last is None or (today - last).days > PRESENCE_GAP:
                self.pres_start[sid] = today
            self.pres_last[sid] = today
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
        if px < min_price:
            return "price"
        dq = self._qr_dv.get(f.symbol)
        if dq is None or len(dq) < adv_days or not sum(dq) / len(dq) >= min_adv:
            return "adv"
        if not mc > 0:
            return "mcap_missing"
        if mc < min_cap:
            return "mcap_lt_2B"
        return "other"

    def _row_for(self, sid, today, advv):
        v, det, bday = self.rev.baseline((self._ym[0], self._ym[1]), sid)
        return dict(sic=self.qr_sic.sic_on(sid, today), cik=self._cik_v2(sid, today), adv=advv,
                    vals=E.fund_values(self.store, sid, today), base=v, base_det=det, base_day=bday)

    def _month_end(self, t, today, elig, adv, fl):
        self.c["month_ends"] += 1
        ym = (t.year, t.month)
        self._ym = ym
        store_sids = sorted(set(self.store.hist) | set(self.store.pending))
        if t < date(2017, 1, 1):
            self.rev.record(ym, t, today, self.store, store_sids)
        if t >= REVIEW_FROM:
            rows = {}
            for sid, s in elig.items():
                self.sym[sid] = s
                rows[sid] = dict(self._row_for(sid, today, adv[sid]), rep=False)
            self.mon[t] = rows
            self.mon_sel[t] = today
            min_cap, min_price, min_adv, adv_days = self.filt
            day = str(today)
            cand = {}
            for f in fl:
                if not f.has_fundamental_data:
                    continue
                sid = str(f.symbol.id)
                try:
                    if not is_us_common(f, day) or exchange_of(f, day) not in EXCHANGES:
                        continue
                    px, mc = float(f.price), float(f.market_cap)
                except Exception:
                    continue
                dq = self._qr_dv.get(f.symbol)
                if not px >= min_price or dq is None or len(dq) < adv_days or not sum(dq) / len(dq) >= min_adv:
                    continue
                cik = self._cik_v2(sid, today)
                has = cik is not None and cik in self.shrows
                if mc > 0:
                    if has:
                        self.val.append((t, sid, cik, mc, px))
                        self.sym[sid] = f.symbol
                    continue
                if sid in elig:
                    continue
                if cik is None or not has:
                    self.c["cand_no_cik" if cik is None else "cand_no_shares_table"] += 1
                    self.cstat[(str(t), sid)] = "no_cik" if cik is None else "no_shares_table"
                    continue
                self.sym[sid] = f.symbol
                cand[sid] = dict(self._row_for(sid, today, sum(dq) / len(dq)), rep=True, px=px, cik_sh=cik)
            self.cand[t] = cand
            old = self.old.get(str(t))
            if old is not None:
                byf = {str(f.symbol.id): f for f in fl}
                lost = sorted(old - set(elig))
                self.tgt_per[str(t)] = lost
                for sid in lost:
                    self.tgt_reason[(str(t), sid)] = self._why_old(byf.get(sid), sid, today)
        for k in [k for k in self.rev.v if k < (t.year - 1, t.month)]:
            self.rev.drop(k)

    # ------------------------------------------------------------------------------------------------ SEC market cap
    def _split_history(self, sids):
        out = {s: [] for s in sids}
        for i in range(0, len(sids), BATCH):
            part = sids[i:i + BATCH]
            fr = self.history(Split, [self.sym[s] for s in part], HIST_START, self.hist_end)
            if fr is None or fr.empty or not {"type", "referenceprice", "splitfactor"} <= set(fr.columns):
                continue
            idx = fr.index
            sid_of = [_sid(x) for x in idx.get_level_values(0)]
            days = XP.event_days(idx.get_level_values(-1).values)
            for s, d_, typ, ref, fac in zip(sid_of, days, fr["type"].tolist(), fr["referenceprice"].tolist(),
                                            fr["splitfactor"].tolist()):
                if s in out and ("OCCUR" in str(typ).upper() or float(ref) > 0) and float(fac) > 0:
                    out[s].append((date.fromisoformat(_ds(d_)), float(fac)))
        return out

    def _secmcap(self, sid, cik, today, px):
        """(market cap or None, cover-count age in days or None) on `today` by the unchanged D111 method."""
        key = f"{sid}|{cik}"
        if key not in self.secm.filings:
            self.secm.filings[key] = sorted((SECFiling(r) for r in self.shrows.get(cik, ())),
                                            key=lambda x: (x.filed, x.accn))
            self.secm.splits[key] = sorted(set(self.splits.get(sid, ())))
        f, sh = self.secm.shares_on(key, today)
        if sh is None or not px or px <= 0:
            return None, None if f is None else (today - f.cover_date).days
        return sh * float(px), (today - f.cover_date).days

    def _repair(self):
        t0 = time.perf_counter()
        need = sorted({s for c in self.cand.values() for s in c} | {x[1] for x in self.val})
        self.splits = self._split_history(need)
        self.secm = SECCorrections({})
        rep = dict(candidate_stock_months=0, repaired=0, no_fresh_shares=0, below_2B=0, bands={}, stale_near=0,
                   share_age=[])
        self.repaired = {}
        for t, cand in sorted(self.cand.items()):
            today = self.mon_sel[t]
            keep = set()
            for sid, r in cand.items():
                rep["candidate_stock_months"] += 1
                m, age = self._secmcap(sid, r["cik_sh"], today, r["px"])
                if m is None:
                    rep["no_fresh_shares"] += 1
                    self.cstat[(str(t), sid)] = "no_fresh_shares"
                    continue
                add(rep["bands"], band(m))
                rep["share_age"].append(age)
                if 1.8e9 <= m <= 2.2e9 and age > 90:
                    rep["stale_near"] += 1
                self.cstat[(str(t), sid)] = "repaired" if m >= MIN_CAP else "below_2B"
                if m >= MIN_CAP:
                    rep["repaired"] += 1
                    keep.add(sid)
                    self.mon[t][sid] = {k: v for k, v in r.items() if k not in ("px", "cik_sh")}
                else:
                    rep["below_2B"] += 1
            self.repaired[t] = keep
        rep["share_age"] = stats(rep["share_age"])
        cmp_ = dict(records=len(self.val), no_sec=0, agree_away=0, n_away=0, agree_near=0, n_near=0, rel={},
                    abs_rel=[], disagree_kind={})
        for t, sid, cik, mv, px in self.val:
            m, _ = self._secmcap(sid, cik, self.mon_sel[t], px)
            if m is None:
                cmp_["no_sec"] += 1
                continue
            r = m / mv - 1.0
            cmp_["abs_rel"].append(abs(r))
            add(cmp_["rel"], "le2pct" if abs(r) <= 0.02 else ("le5pct" if abs(r) <= 0.05 else
                                                                ("le10pct" if abs(r) <= 0.10 else "gt10pct")))
            same = (m >= MIN_CAP) == (mv >= MIN_CAP)
            nearb = 1.8e9 <= mv <= 2.2e9
            cmp_["n_near" if nearb else "n_away"] += 1
            cmp_["agree_near" if nearb else "agree_away"] += int(same)
            if not same:
                add(cmp_["disagree_kind"], ("near|" if nearb else "away|") +
                    ("sec_above" if m >= MIN_CAP else "sec_below") + "|" +
                    ("rel_le10pct" if abs(r) <= 0.10 else "rel_gt10pct"))
        a = np.asarray(cmp_.pop("abs_rel") or [np.nan])
        cmp_["abs_rel_median"] = round(float(np.nanmedian(a)), 5)
        cmp_["abs_rel_p90"] = round(float(np.nanpercentile(a, 90)), 5)
        rep["repair_s"] = round(time.perf_counter() - t0, 1)
        self.st["repair"], self.st["mcap_comparison"] = rep, cmp_

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
        for f in fields:
            if f in frame.columns:
                out[f][pc[ok], cols[ok]] = frame[f].to_numpy(dtype=float)[ok]
        return out

    def _events(self, frame, loc, cal, fields):
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

    def _build(self):
        t0 = time.perf_counter()
        spy = self.history(self.spy, HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        cal = np.unique(XP.session_days(spy.index.get_level_values(-1).values))
        cal = cal[cal <= self.last_session]
        D = cal.size
        sids = sorted({s for rows in self.mon.values() for s in rows})
        N = len(sids)
        st = dict(sessions=D, securities=N, late_rows=0)
        C, Hh, L, Pt, Rw = (np.full((D, N), np.nan) for _ in range(5))
        self.unv, self.dist, self.psplit = {}, {}, {}
        for i in range(0, N, BATCH):
            part = sids[i:i + BATCH]
            syms = [self.sym[s] for s in part]
            loc = {s: j for j, s in enumerate(part)}
            hr = self.history(syms, HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.RAW)
            hs = self.history(syms, HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            sp = self.history(Split, syms, HIST_START, self.hist_end)
            dv = self.history(Dividend, syms, HIST_START, self.hist_end)
            a = self._cols(hr, loc, cal, D, len(part), ("high", "low", "close"), st)
            b = self._cols(hs, loc, cal, D, len(part), ("close",), st)
            sev = self._events(sp, loc, cal, ("type", "referenceprice", "splitfactor"))
            dev = self._events(dv, loc, cal, ("distribution", "referenceprice"))
            for j in range(len(part)):
                g = i + j
                raw = a["close"][:, j]
                if not np.any(np.isfinite(raw) & (raw > 0)):
                    continue
                sc = b["close"][:, j]
                vv = np.flatnonzero(np.isfinite(raw) & np.isfinite(sc) & (raw > 0) & (sc > 0))
                if vv.size and abs(sc[vv[-1]] / raw[vv[-1]] - 1.0) > 1e-6:
                    sc = sc / (sc[vv[-1]] / raw[vv[-1]])
                ev = [(r_, float(fac)) for r_, typ, ref, fac in sev[j] if "OCCUR" in str(typ).upper() or float(ref) > 0]
                de = [(r_, float(amt), float(ref)) for r_, amt, ref in dev[j]]
                det = []
                mult, _ = XP.split_multiplier(raw, sc, ev, detail=det)
                dm = XP.dividend_multiplier(D, de)
                C[:, g], Hh[:, g], L[:, g], Pt[:, g] = raw * mult, a["high"][:, j] * mult, a["low"][:, j] * mult, \
                    raw * mult * dm
                Rw[:, g] = raw
                self.unv[g] = [int(d_[0]) for d_ in det]
                self.dist[g] = [(r_, amt / ref) for r_, amt, ref in de if ref > 0]
                self.psplit[g] = ev
        if st["late_rows"]:
            raise Exception("X997: history returned data after the end date")
        spy_raw = np.full(D, np.nan)
        d_spy = XP.session_days(spy.index.get_level_values(-1).values)
        ok = d_spy <= self.last_session
        spy_raw[np.searchsorted(cal, d_spy[ok])] = spy["close"].to_numpy(dtype=float)[ok]
        ssp = self.history(Split, [self.spy], HIST_START, self.hist_end)
        m = np.ones(D)
        for r_, typ, ref, f in self._events(ssp, {_sid(self.spy): 0}, cal, ("type", "referenceprice",
                                                                            "splitfactor")).get(0, []):
            if "OCCUR" in str(typ).upper() or float(ref) > 0:
                m[:r_] *= float(f)
        self.spy_c = spy_raw * m
        st["build_s"] = round(time.perf_counter() - t0, 1)
        self.cal, self.sids, self.col = cal, sids, {s: j for j, s in enumerate(sids)}
        self.C, self.H, self.L, self.P, self.RAW = C, Hh, L, Pt, Rw
        self.st["panel"] = st

    def _row(self, t):
        k = int(np.searchsorted(self.cal, _day(t)))
        if k >= self.cal.size or self.cal[k] != _day(t):
            raise Exception(f"X997: review session {t} not on the SPY calendar")
        return k

    def _life_start_row(self, j, k):
        if j not in self._life:
            v = P.valid_rows(self.C[:, j], self.P[:, j])
            self._life[j] = (v, P.life_starts(v))
        v, ls = self._life[j]
        b = int(np.searchsorted(v, k, side="right")) - 1
        return None if b < 0 else int(v[ls[b]])

    def _baselines(self, reviews, rows_k):
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
                    ok, why = E.baseline_check(ls, self._row(bsess), self._cik_v2(sid, bsel), self._cik_v2(sid, today))
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
        """SEC market cap across each split (ex-date 2011-2017, factor at least 1.4x) of a panel security with SEC
        cover counts: continuous (shares x raw price unchanged up to the day's return) vs jumping with the price."""
        out = {}
        lo = _day(date(2011, 1, 1))
        for sid, j in self.col.items():
            for row, fac in self.psplit.get(j, ()):
                if row < 1 or self.cal[row] < lo or abs(np.log(fac)) < np.log(1.4):
                    continue
                db, da = date.fromisoformat(_ds(self.cal[row - 1])), date.fromisoformat(_ds(self.cal[row]))
                cik = self._cik_v2(sid, da)
                if cik is None or cik not in self.shrows:
                    add(out, "no_sec_identity")
                    continue
                if sid not in self.splits:
                    self.splits[sid] = self._split_history([sid])[sid]
                pb, pa = self.RAW[row - 1, j], self.RAW[row, j]
                mb, _ = self._secmcap(sid, cik, db, pb)
                ma, _ = self._secmcap(sid, cik, da, pa)
                if mb is None or ma is None or not (np.isfinite(pb) and np.isfinite(pa)):
                    add(out, "no_sec_mcap")
                    continue
                lm, lp, lf = np.log(ma / mb), np.log(pa / pb), np.log(fac)
                d_pit, d_non = abs(lm - (lp - lf)), abs(lm - lp)
                add(out, "continuous" if d_pit < d_non and d_pit < abs(lf) / 2 else
                    ("jumps_with_price" if d_non < abs(lf) / 2 else "ambiguous"))
        return out

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        self.st = dict(identity=self.ident, checks=self.c, store_stats=dict(self.store.stats))
        sids_t = sorted({s for v in self.tgt_per.values() for s in v})
        per = {t: self.tgt_per.get(t, []) for t in sorted(self.old)}
        self.st["target_check"] = dict(
            securities=len(sids_t), stock_months=sum(len(v) for v in per.values()),
            sha256_match=hashlib.sha256(json.dumps([sids_t, per], sort_keys=True).encode()).hexdigest() == self.tgt_sha)
        self._repair()
        self._build()
        t1 = time.perf_counter()
        reviews = sorted(self.mon)
        rows_k = {t: self._row(t) for t in reviews}
        need = sorted(set(rows_k.values()))
        a200 = {j: P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])["above200"][need]
                for j in range(len(self.sids))}
        rix = {k: i for i, k in enumerate(need)}
        self._baselines(reviews, rows_k)
        spot = dict(checked=0, mismatch=0)
        per_review, sdig, yr = [], {}, {}
        tot_c, tot_p, lay = [], [], {"T": [], "F": [], "S": []}
        surv, rec, mc2 = {}, {}, {}
        sec_rec, sec_lost, sec_mm = set(), {}, set()
        for t in reviews:
            k = rows_k[t]
            elig = self.mon[t]
            today = self.mon_sel[t]
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
            for s in P.pick(sorted(res["kept"]), 2, f"{SPOT_SALT}|{t}"):
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
            a = yr.setdefault(y, dict(reviews=0, eligible=0, repaired=0, nonfin=0, h2_nonfin=0, scored=0,
                                      scored_repaired=0, candidates=0, ge75=0, ge80=0, ge85=0, ge90=0,
                                      field_present=[0] * 7, bits={b: 0 for b in HBITS}, mappable_v2=0,
                                      mappable_ext=0, h2_repaired_nonfin=0, nonfin_repaired=0))
            a["reviews"] += 1
            n_nf = n_h2 = n_sc = n_c = 0
            cnt = [0, 0, 0, 0]
            for s, (bits, tot, pts) in rows.items():
                e = elig[s]
                nonfin = e["sic"] is not None and not 6000 <= int(e["sic"]) <= 6999
                h2 = bool(bits & E.BIT["H2"])
                for b in HBITS:
                    a["bits"][b] += int(bool(bits & E.BIT[b]))
                c_, src = self._cik_m2(s, today)
                a["mappable_v2"] += int(src == "v2")
                a["mappable_ext"] += int(src == "ext")
                a["repaired"] += int(e["rep"])
                if nonfin:
                    n_nf += 1
                    n_h2 += int(h2)
                    a["nonfin_repaired"] += int(e["rep"])
                    a["h2_repaired_nonfin"] += int(e["rep"] and h2)
                    for i, v in enumerate(e["vals"] + [e["base"] if e.get("base_ok") else None]):
                        a["field_present"][i] += int(v is not None)
                if tot is not None and not bits & E.BIT["duplicate_class"]:
                    n_sc += 1
                    a["scored_repaired"] += int(e["rep"])
                    tot_p.append(tot)
                    lay["T"].append(sum(pts[0:3]))
                    lay["F"].append(sum(pts[3:7]))
                    lay["S"].append(pts[7])
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
            per_review.append([str(t), len(rows), len(self.repaired.get(t, ())), n_nf, n_h2, n_sc, n_c] + cnt +
                              [S.regime(trend, res["breadth"][0])])
            # survivorship: data v1 (old), delivered, repaired universe; recovery of the frozen targets
            old = self.old.get(str(t), set())
            dlv = {s for s, e in elig.items() if not e["rep"]}
            uni = set(elig)
            sv = surv.setdefault(y, {})
            for name, grp in (("data_v1", old), ("delivered", dlv), ("repaired_universe", uni),
                              ("lost", old - dlv), ("recovered", (old - dlv) & uni), ("still_lost", old - uni),
                              ("added_not_v1", uni - old - dlv)):
                z = sv.setdefault(name, [0, 0])
                z[0] += len(grp)
                z[1] += sum(1 for s in grp if s in self.old_last)
            for s in old - dlv:
                rs = self.tgt_reason.get((str(t), s), "unknown")
                sec_lost[s] = rs if s not in uni else sec_lost.get(s, "recovered_at_least_once")
                if s in uni:
                    sec_rec.add(s)
                if rs == "mcap_missing":
                    sec_mm.add(s)
                if rs == "mcap_missing":
                    z = mc2.setdefault(self.cstat.get((str(t), s), "not_a_candidate"), [0, 0])
                    z[0] += 1
                    z[1] += int(s not in self.old_last)
                z = rec.setdefault(rs, [0, 0, 0])
                z[0] += 1
                z[1] += int(s in uni)
                z[2] += int(s in uni and s not in self.old_last)
        self.st["slice_spot_check"] = spot
        never = {s: r for s, r in sec_lost.items() if s not in sec_rec}
        cnt = {}
        for s, r in never.items():
            add(cnt, r + ("|later_disappearing" if s not in self.old_last else "|in_universe_end_2017"))
        self.st["target_securities"] = dict(
            targets=len(sec_lost), with_mcap_missing_month=len(sec_mm), recovered_at_least_once=len(sec_rec),
            recovered_later_disappearing=sum(1 for s in sec_rec if s not in self.old_last),
            targets_later_disappearing=sum(1 for s in sec_lost if s not in self.old_last),
            never_recovered_by_last_reason=cnt)
        self.st["score_s"] = round(time.perf_counter() - t1, 1)
        L3 = {k: np.asarray(v, dtype=float) for k, v in lay.items()}
        corr = None
        if L3["T"].size > 2:
            cm = np.corrcoef(np.vstack([L3["T"], L3["F"], L3["S"]]))
            corr = {k: (round(float(v), 4) if np.isfinite(v) else None)
                    for k, v in (("T_F", cm[0, 1]), ("T_S", cm[0, 2]), ("F_S", cm[1, 2]))}
        rdig = {}
        for t in reviews:
            h = rdig.setdefault(str(t.year), hashlib.sha256())
            h.update((str(t) + "|" + ",".join(sorted(self.mon[t])) + "\n").encode())
        self.st.update(
            per_review_cols=["review", "eligible", "repaired", "nonfin", "h2_nonfin", "scored", "candidates", "ge75",
                             "ge80", "ge85", "ge90", "regime"],
            per_review=per_review, per_year=yr, totals_hist5_candidates=hist5(tot_c), totals_candidates=stats(tot_c),
            totals_scored=stats(tot_p), layers={k: dict(stats=stats(v), hist5=hist5(v)) for k, v in lay.items()},
            layer_corr=corr, field_order=["revenue_ttm4q", "gross_profit_ttm4q", "net_income_ttm4q",
                                          "operating_cash_flow_ttm4q", "total_assets", "stockholders_equity",
                                          "revenue_baseline_valid"],
            survivorship=surv, target_recovery_by_reason=rec, target_mcap_missing_status=mc2, identity_mapping=self.idc, identity_value_check=self.id2,
            sec_split_check=self._split_check(),
            digests=dict(universe_by_year={y: h.hexdigest() for y, h in sorted(rdig.items())}, review_scores=sdig))
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        text = json.dumps(self.st, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRP5E|{i // 9000}|{text[i:i + 9000]}")
