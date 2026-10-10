# X998 v1.0 — DATA INFRASTRUCTURE v2 score / mechanics export (P7-CP5f, owner D190; the X993-v2 equivalent).
# Infrastructure only: NO orders, NO returns, NO predictive statistic; QuantConnect's DEFAULT build (recorded);
# outputs are aggregates and SHA-256 digests only (no vendor value, no per-security row). Approved v2 rules (qr_v2):
#  * universe: US common, NYSE/Nasdaq, PIT market cap >= $2B, price >= $5, ADV20 >= $5M; market cap = QuantConnect's
#    if > 0, else the D111 SEC market cap (single unambiguous cover-page count usable from filing + 1, <= 135 days old,
#    x splits after the cover date and on/before the day, x raw price), else ineligible; the data-v1 SEC correction
#    layer (securities without vendor fundamentals) unchanged, installed here from the consolidated v2 table;
#  * timing (M2): a report is usable from max(first seen in the historical stream, SEC original periodic filing + 1);
#    first-seen snapshots are never rewritten, a revision enters from its own first-seen day; no vendor file date,
#    no +90-day rule;
#  * identity: identity-v2 dated rows + verified extension rows (SAFE / BOUNDED) while feed presence is continuous;
#  * restatement guard: a report version whose quarterly revenue or total assets equals only a later SEC value not
#    yet filed on the day seen is never fed;
#  * Score v1, its mechanics and the research window (reviews 2011-01 .. 2017-12) unchanged.
# The SEC-repaired membership is decided at the end of the run from values recorded at each review (splits filtered
# to ex-date <= the review day), so nothing after a review enters it. Mode 'export' (E998-01/02, truncated E998-03)
# reports universe, coverage, Score v1 distributions, mechanics, PIT audit and digests; mode 'power' adds the P7-CP4
# synthetic power study (synthetic returns only) on the Data v2 score tables.
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
from qr_industry import SICHistory
import qr_p7 as P
import qr_p7_score as S
import qr_p7_export as E
import qr_p7_mech as M
import qr_xs_diag as XD
import qr_xs_panel as XP
import qr_v2 as V
from qr_data_v2 import load_table

HIST_START = datetime(2007, 1, 1)
LEDGER_FROM = date(2010, 1, 1)
REVIEW_FROM = date(2011, 1, 1)
DIGEST_CUT = date(2013, 12, 31)
BATCH = 100
MIN_CAP = 2e9
MAX_SHARE_AGE = 135
BANDS = (1.5e9, 1.8e9, 2.0e9, 2.2e9, 2.5e9)
BAND_NAMES = ("lt1.5B", "1.5-1.8B", "1.8-2.0B", "2.0-2.2B", "2.2-2.5B", "gt2.5B")
SPOT_SALT = "P7CP5f-slice-check"
WEEKLY_FROM_SCORE = 75
FP_KEYS = ("revenue_q", "revenue_ttm", "gross_profit_q", "gross_profit_ttm", "net_income_q", "net_income_ttm",
           "operating_cash_flow_q", "operating_cash_flow_ttm", "total_assets", "stockholders_equity")
HBITS = ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5", "H6", "H7", "duplicate_class")


def _m2_available(period_end, file_date):
    """M2 data-delivery rule: the store receives as 'file date' the day BEFORE the usable day."""
    if period_end is None or file_date is None or file_date < period_end:
        return None
    return file_date + timedelta(days=1)


F.available_from = _m2_available
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


def add(h, k, n=1):
    h[k] = h.get(k, 0) + n


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


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


class DataV2Export(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        if self.qr_sec is not None:
            raise Exception("X998: data v2 installs its own SEC layer; universe.sec_corrections must be off")
        self.end = date.fromisoformat(self.qr["end"])
        if self.qr["end"] not in ("2013-12-31", "2017-12-31"):
            raise Exception("X998: ends on 2017-12-31 (or 2013-12-31 for the truncation test)")
        self.mode = str(self.qr_params.get("mode"))
        if self.mode not in ("export", "power") or (self.mode == "power" and self.qr["end"] != "2017-12-31"):
            raise Exception("X998: mode export / power (power on the full window only)")
        self.hist_end = datetime(self.end.year, self.end.month, self.end.day)
        self.last_session = np.datetime64(min(self.qr["end"], "2017-12-29")).astype(np.int64)
        self.t0 = time.perf_counter()
        t = load_table()
        self.st0 = dict(table_version=t["version"], table_end=t["end"])
        self.qr_sec = SECCorrections(V.sec_v1_table(t["sec_v1"]))
        self.qr_sic = SICHistory(self.qr_sec.sic_history)
        self.ref = V.Reference(t)
        rows = {sid: [(date.fromisoformat(e), str(c) if c not in (None, "") else None) for e, _s, c in r]
                for sid, r in self.qr_sec.sic_history.items()}
        self.ident = V.Identity(rows, self.ref.ext)
        dg = t["diag"]
        self.old = V.old_membership(dg["old"])
        self.old_last = self.old[max(self.old)]
        self.tgt_sha = dg["tgt_sha256"]
        self.id_reject, self.id_none = set(dg["id_reject"]), set(dg["id_none"])
        del t
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS)
        self.prev_session = self.done_t = self.week = self.first_day = None
        self.sym, self.mon, self.mon_sel, self.cand, self.val = {}, {}, {}, {}, []
        self.rev = E.RevenueLedger()
        self.sec_next, self.led, self.pres_start, self.pres_last = {}, {}, {}, {}
        self.tgt_per, self.tgt_reason, self.cstat, self.wk = {}, {}, {}, {}
        self.last_review = None
        self.idc, self.idv, self.guard = {}, {}, {}
        self.dg, self.dg_cut = {}, hashlib.sha256()
        self.audit = dict(fed_before_sec_filing=0, fed_before_first_seen=0, future_identity_row=0,
                          fed_after_guard_trigger=0, stale_share_count_used=0, share_filing_not_yet_public=0,
                          repaired_with_vendor_cap=0, repaired_below_2B=0, record_older_than_200d=0,
                          baseline_pit_violations=0, baseline_used_despite_reject=0)
        self.c = dict(selections=0, month_ends=0, weekly=0, sec_fed=0, reports_new=0, revisions=0, no_period_end=0,
                      pe_after_seen=0, fed=0, m2_not_fed=0, m2_delayed=0, m2_revision_unfed=0, presence_break=0,
                      guard_blocked=0, cand_no_cik=0, cand_no_shares_table=0)
        u = self._qr_u
        self.filt = (float(u.get("min_market_cap", 2e9)), float(u.get("min_price", 0.0)),
                     float(u.get("min_avg_dollar_volume", 0.0)), int(u.get("adv_days", 20)))

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:
            self.prev_session = self.time.date()

    # ------------------------------------------------------------------------------------------------ ledger (M2)
    @staticmethod
    def _read1(f, k):
        try:
            return F.clean(getattr(get(f, WHITELIST[k][0]), WHITELIST[k][1]))
        except Exception:
            return None

    def _digest(self, today, line):
        h = self.dg.setdefault(today.year, hashlib.sha256())
        b = (line + "\n").encode()
        h.update(b)
        if today <= DIGEST_CUT:
            self.dg_cut.update(b)

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
        fp = tuple(vals[k] for k in FP_KEYS)
        if kind == "new":
            led[pk] = [fp]
        self._digest(today, f"{today}|{sid}|{pk}|{kind}|{fp!r}")
        try:
            ay = accession_year(er.accession_number.three_months)
        except Exception:
            ay = None
        if pe > today:
            self.c["pe_after_seen"] += 1
            return
        cik, src = self.ident.m2(sid, today, self.pres_start.get(sid), self.first_day)
        if src == "presence_break":
            self.c["presence_break"] += 1
        if src == "ext" and today < self.ref.ext[sid][0]:
            self.audit["future_identity_row"] += 1
        m = self.ref.match(cik, pe) if cik is not None else None
        y = str(today.year)
        if kind == "new":
            add(self.idc, f"mapped|{src}|{y}" if m is not None else f"unmapped|{'no_cik' if cik is None else 'no_period'}|{y}")
            if m is not None and src in ("v2", "ext"):
                for fld, k in self.ref.identity_value(cik, m[0], vals).items():
                    add(self.idv, f"{src}|{fld}|{k}")
        if m is None:
            self.c["m2_not_fed"] += 1
            return
        blocked, cats = self.ref.guard(cik, m[0], vals, today)
        for fld, k in cats.items():
            add(self.guard, f"{kind}|{fld}|{k}")
        if blocked:
            self.c["guard_blocked"] += 1
            add(self.guard, f"blocked|{kind}|{y}")
            return
        use = max(today, V.dd(m[1] + 1))
        if use > today:
            self.c["m2_delayed"] += 1
        fd_syn = use - timedelta(days=1)
        if (sid, pe, fd_syn) in self.store.seen:
            self.c["m2_revision_unfed"] += 1
            return
        self.audit["fed_before_sec_filing"] += int(use < V.dd(m[1] + 1))
        self.audit["fed_before_first_seen"] += int(use < today)
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
        elig = {str(s.id): s for s in self.qr_eligible}
        adv = {str(s.id): v[1] for s, v in self.qr_eligible_info.items()}
        for f in fl:
            sid = str(f.symbol.id)
            last = self.pres_last.get(sid)
            if last is None or (today - last).days > V.PRESENCE_GAP:
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
        elif nxt.isocalendar()[:2] != t.isocalendar()[:2] and self.last_review is not None:
            self._weekly(t, today)
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
                if sr.security_type != COMMON_STOCK or sr.is_depositary_receipt or not (
                        bool(sr.is_primary_share) or str(f.company_reference.country_id) == "USA") \
                        or non_common_reason(f, day) is not None or exchange_of(f, day) not in EXCHANGES:
                    return "reference_or_security_type"
            except Exception:
                return "reference_or_security_type"
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
        return "mcap_lt_2B" if mc < min_cap else "other"

    def _row_for(self, sid, today, advv, ym):
        v, det, bday = self.rev.baseline(ym, sid)
        return dict(sic=self.qr_sic.sic_on(sid, today), cik=self.ident.v2(sid, today), adv=advv,
                    vals=E.fund_values(self.store, sid, today), base=v, base_det=det, base_day=bday)

    def _month_end(self, t, today, elig, adv, fl):
        self.c["month_ends"] += 1
        ym = (t.year, t.month)
        store_sids = sorted(set(self.store.hist) | set(self.store.pending))
        if t < date(2017, 1, 1):
            self.rev.record(ym, t, today, self.store, store_sids)
        if t >= REVIEW_FROM:
            rows = {sid: dict(self._row_for(sid, today, adv[sid], ym), rep=False) for sid in elig}
            for sid, s in elig.items():
                self.sym[sid] = s
                r = self.store.record(sid, today)
                if r is not None and (today - r.period_end).days > DEFAULT_MAX_AGE_DAYS:
                    self.audit["record_older_than_200d"] += 1
            self.mon[t], self.mon_sel[t] = rows, today
            min_cap, min_price, min_adv, adv_days = self.filt
            day, cand = str(today), {}
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
                cik = self.ident.v2(sid, today)
                has = cik is not None and cik in self.ref.shrows
                if mc > 0:
                    if has:
                        self.val.append((t, sid, cik, mc, px))
                        self.sym[sid] = f.symbol
                    continue
                if sid in elig:
                    continue
                if not has:
                    k = "no_cik" if cik is None else "no_shares_table"
                    self.c["cand_" + k] += 1
                    self.cstat[(str(t), sid)] = k
                    continue
                self.sym[sid] = f.symbol
                cand[sid] = dict(self._row_for(sid, today, sum(dq) / len(dq), ym), rep=True, px=px, cik_sh=cik)
            self.cand[t] = cand
            self.last_review = (t, tuple(sorted(set(elig) | set(cand))))
            old = self.old.get(str(t))
            if old is not None:
                byf = {str(f.symbol.id): f for f in fl}
                lost = sorted(old - set(elig))
                self.tgt_per[str(t)] = lost
                for sid in lost:
                    self.tgt_reason[(str(t), sid)] = self._why_old(byf.get(sid), sid, today)
        for k in [k for k in self.rev.v if k < (t.year - 1, t.month)]:
            self.rev.drop(k)

    def _weekly(self, t, today):
        """H1 / H2 / H7 of the possible holdings (members of the latest review, repaired candidates included) with
        the baseline of the score in force; H3-H6 are added at the end from the panel (X993 v1.1 logic)."""
        self.c["weekly"] += 1
        lt = self.last_review[0]
        out = {}
        for sid in self.last_review[1]:
            e = self.mon[lt].get(sid) or self.cand[lt].get(sid)
            bits = E.sic_bits(self.qr_sic.sic_on(sid, today))
            fi, _, _ = E.fund_inputs(E.fund_values(self.store, sid, today), e["base"])
            bits |= E.BIT["H2"] if fi is None else (E.BIT["H7"] if fi["impaired"] else 0)
            out[sid] = bits
        self.wk[t] = (lt, out)

    # ------------------------------------------------------------------------------------------------ SEC market cap
    def _split_history(self, sids):
        out = {s: [] for s in sids}
        for i in range(0, len(sids), BATCH):
            part = sids[i:i + BATCH]
            fr = self.history(Split, [self.sym[s] for s in part], HIST_START, self.hist_end)
            if fr is None or fr.empty or not {"type", "referenceprice", "splitfactor"} <= set(fr.columns):
                continue
            idx = fr.index
            days = XP.event_days(idx.get_level_values(-1).values)
            for s, d_, typ, ref, fac in zip([_sid(x) for x in idx.get_level_values(0)], days, fr["type"].tolist(),
                                            fr["referenceprice"].tolist(), fr["splitfactor"].tolist()):
                if s in out and ("OCCUR" in str(typ).upper() or float(ref) > 0) and float(fac) > 0:
                    out[s].append((date.fromisoformat(_ds(d_)), float(fac)))
        return out

    def _secmcap(self, sid, cik, today, px):
        key = f"{sid}|{cik}"
        if key not in self.secm.filings:
            self.secm.filings[key] = sorted((SECFiling(r) for r in self.ref.shrows.get(cik, ())),
                                            key=lambda x: (x.filed, x.accn))
            self.secm.splits[key] = sorted(set(self.splits.get(sid, ())))
        f, sh = self.secm.shares_on(key, today)
        if f is not None and f.available > today:
            self.audit["share_filing_not_yet_public"] += 1
        if sh is None or not px or px <= 0:
            return None, None if f is None else (today - f.cover_date).days
        age = (today - f.cover_date).days
        self.audit["stale_share_count_used"] += int(age > MAX_SHARE_AGE)
        return sh * float(px), age

    def _repair(self):
        need = sorted({s for c in self.cand.values() for s in c} | {x[1] for x in self.val})
        self.splits = self._split_history(need)
        self.secm = SECCorrections({})
        rep = dict(candidate_stock_months=0, repaired=0, no_fresh_shares=0, below_2B=0, bands={}, stale_near=0,
                   share_age=[], repaired_near_2_0_to_2_2B=0)
        self.repaired, self.rep_cap = {}, {}
        for t, cand in sorted(self.cand.items()):
            today, keep = self.mon_sel[t], set()
            for sid, r in cand.items():
                rep["candidate_stock_months"] += 1
                m, age = self._secmcap(sid, r["cik_sh"], today, r["px"])
                if m is None:
                    rep["no_fresh_shares"] += 1
                    self.cstat[(str(t), sid)] = "no_fresh_shares"
                    continue
                add(rep["bands"], band(m))
                rep["share_age"].append(age)
                rep["stale_near"] += int(1.8e9 <= m <= 2.2e9 and age > 90)
                self.cstat[(str(t), sid)] = "repaired" if m >= MIN_CAP else "below_2B"
                if m >= MIN_CAP:
                    rep["repaired"] += 1
                    rep["repaired_near_2_0_to_2_2B"] += int(m < 2.2e9)
                    keep.add(sid)
                    self.mon[t][sid] = {k: v for k, v in r.items() if k not in ("px", "cik_sh")}
                    self.audit["repaired_below_2B"] += int(m < MIN_CAP)
                else:
                    rep["below_2B"] += 1
            self.repaired[t] = keep
        rep["share_age"] = stats(rep["share_age"])
        cmp_ = dict(records=len(self.val), no_sec=0, agree_away=0, n_away=0, agree_near=0, n_near=0, rel={},
                    disagree_kind={})
        absr = []
        for t, sid, cik, mv, px in self.val:
            m, _ = self._secmcap(sid, cik, self.mon_sel[t], px)
            if m is None:
                cmp_["no_sec"] += 1
                continue
            r = m / mv - 1.0
            absr.append(abs(r))
            add(cmp_["rel"], "le2pct" if abs(r) <= 0.02 else ("le5pct" if abs(r) <= 0.05 else
                                                                ("le10pct" if abs(r) <= 0.10 else "gt10pct")))
            same, nearb = (m >= MIN_CAP) == (mv >= MIN_CAP), 1.8e9 <= mv <= 2.2e9
            cmp_["n_near" if nearb else "n_away"] += 1
            cmp_["agree_near" if nearb else "agree_away"] += int(same)
            if not same:
                add(cmp_["disagree_kind"], ("near|" if nearb else "away|") + ("sec_above" if m >= MIN_CAP else
                                                                               "sec_below"))
        a = np.asarray(absr or [np.nan])
        cmp_["abs_rel_median"] = round(float(np.nanmedian(a)), 5)
        cmp_["abs_rel_p90"] = round(float(np.nanpercentile(a, 90)), 5)
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
        pc = np.minimum(np.searchsorted(cal, days), cal.size - 1)
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
            if cols[r] >= 0 and eday[r] <= self.last_session:
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
                g, raw, sc = i + j, a["close"][:, j], b["close"][:, j]
                if not np.any(np.isfinite(raw) & (raw > 0)):
                    continue
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
            raise Exception("X998: history returned data after the end date")
        spy_raw = np.full(D, np.nan)
        d_spy = XP.session_days(spy.index.get_level_values(-1).values)
        ok = d_spy <= self.last_session
        spy_raw[np.searchsorted(cal, d_spy[ok])] = spy["close"].to_numpy(dtype=float)[ok]
        m = np.ones(D)
        for r_, typ, ref, f in self._events(self.history(Split, [self.spy], HIST_START, self.hist_end),
                                            {_sid(self.spy): 0}, cal, ("type", "referenceprice", "splitfactor")).get(0, []):
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
            raise Exception(f"X998: session {t} not on the SPY calendar")
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
        st = dict(store_baseline=0, life_reject=0, cik_reject=0)
        for t in reviews:
            k, today = rows_k[t], self.mon_sel[t]
            for sid, e in self.mon[t].items():
                ok = False
                if e["base"] is not None:
                    st["store_baseline"] += 1
                    bsess, bsel = e["base_day"]
                    j = self.col.get(sid)
                    ls = self._life_start_row(j, k) if j is not None else None
                    ok, why = E.baseline_check(ls, self._row(bsess), self.ident.v2(sid, bsel), self.ident.v2(sid, today))
                    st["life_reject"] += int(why == "life")
                    st["cik_reject"] += int(why == "cik")
                    _, pe, fd = e["base_det"]
                    if any(x >= bsel.toordinal() for x in fd) or any(x > bsess.toordinal() for x in pe):
                        self.audit["baseline_pit_violations"] += 1
                        ok = False
                e["base_ok"] = ok
                fi, why2, bo = E.fund_inputs(e["vals"], e["base"] if ok else None)
                e["fund"], e["base_only"] = (fi, why2), bo
                self.audit["baseline_used_despite_reject"] += int(not ok and fi is not None)
        self.st["baseline"] = st

    def _split_check(self):
        out, lo = {}, _day(date(2011, 1, 1))
        for sid, j in self.col.items():
            for row, fac in self.psplit.get(j, ()):
                if row < 1 or self.cal[row] < lo or abs(np.log(fac)) < np.log(1.4):
                    continue
                db, da = date.fromisoformat(_ds(self.cal[row - 1])), date.fromisoformat(_ds(self.cal[row]))
                cik = self.ident.v2(sid, da)
                if cik is None or cik not in self.ref.shrows:
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
        self.st = dict(self.st0, mode=self.mode, end=str(self.end), checks=self.c, store_stats=dict(self.store.stats))
        sids_t = sorted({s for v in self.tgt_per.values() for s in v})
        per = {t: self.tgt_per.get(t, []) for t in sorted(self.old) if t <= str(self.end)}
        self.st["target_check"] = dict(securities=len(sids_t), stock_months=sum(len(v) for v in per.values()),
                                       sha256_match=(self.end.year < 2017 or hashlib.sha256(
                                           json.dumps([sids_t, per], sort_keys=True).encode()).hexdigest() == self.tgt_sha))
        self._repair()
        self._build()
        t1 = time.perf_counter()
        reviews = sorted(self.mon)
        rows_k = {t: self._row(t) for t in reviews}
        wk_rows = {t: self._row(t) for t in sorted(self.wk)}
        need = sorted(set(rows_k.values()) | set(wk_rows.values()))
        a200 = {j: P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])["above200"][need]
                for j in range(len(self.sids))}
        rix = {k: i for i, k in enumerate(need)}
        self._baselines(reviews, rows_k)
        ff_names = list(XD.FF12_NAMES)
        spot = dict(checked=0, mismatch=0)
        per_review, sdig, edig, yr, surv, rec, mc2, ident = [], {}, {}, {}, {}, {}, {}, {}
        tot_c, tot_p, lay, regimes, sectors = [], [], {"T": [], "F": [], "S": []}, {}, {}
        mech_reviews, cand_ever, power_tables = [], set(), []
        sec_rec, sec_lost, aff_sm, ret_sm = set(), {}, [], []
        final_last = None
        for idx, t in enumerate(reviews):
            k, elig, today = rows_k[t], self.mon[t], self.mon_sel[t]
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
            sdig[str(t)] = sha(sorted(rows.items()))
            edig[str(t)] = sha(sorted(elig))
            y = str(t.year)
            a = yr.setdefault(y, dict(reviews=0, eligible=0, from_qc_cap=0, from_sec_repair=0, from_v1_sec_layer=0,
                                      nonfin=0, h2_nonfin=0, scored=0, candidates=0, ge75=0, ge80=0, ge85=0, ge90=0,
                                      field_present=[0] * 7, bits={b: 0 for b in HBITS}, mappable_v2=0,
                                      mappable_ext=0))
            a["reviews"] += 1
            n_nf = n_h2 = n_sc = n_c = 0
            cnt = [0, 0, 0, 0]
            trend = S.spy_trend(self.spy_c, k)
            regime = S.regime(trend, res["breadth"][0])
            add(regimes, str(regime))
            company = {s: (e["cik"] or s) for s, e in elig.items()}
            adv = {s: e["adv"] for s, e in elig.items()}
            ffi = {s: ff_names.index(XD.ff12(e["sic"])) for s, e in elig.items()}
            ptab = []
            for s, (bits, tot, pts) in rows.items():
                e = elig[s]
                nonfin = e["sic"] is not None and not 6000 <= int(e["sic"]) <= 6999
                h2 = bool(bits & E.BIT["H2"])
                for b in HBITS:
                    a["bits"][b] += int(bool(bits & E.BIT[b]))
                src = self.ident.m2(s, today, self.pres_start.get(s), self.first_day)[1]
                a["mappable_v2"] += int(src == "v2")
                a["mappable_ext"] += int(src == "ext")
                a["from_sec_repair"] += int(e["rep"])
                a["from_v1_sec_layer"] += int(not e["rep"] and self.qr_sec.has(s))
                a["from_qc_cap"] += int(not e["rep"] and not self.qr_sec.has(s))
                if nonfin:
                    n_nf += 1
                    n_h2 += int(h2)
                    for i, v in enumerate(e["vals"] + [e["base"] if e.get("base_ok") else None]):
                        a["field_present"][i] += int(v is not None)
                if tot is not None and not bits & E.BIT["duplicate_class"]:
                    n_sc += 1
                    tot_p.append(tot)
                    lay["T"].append(sum(pts[0:3]))
                    lay["F"].append(sum(pts[3:7]))
                    lay["S"].append(pts[7])
                if E.eligible_flag(bits, tot):
                    n_c += 1
                    tot_c.append(tot)
                    for i, th in enumerate((75, 80, 85, 90)):
                        cnt[i] += int(tot >= th)
                    if tot >= WEEKLY_FROM_SCORE:
                        cand_ever.add(s)
                    if tot >= 80:
                        add(sectors, ff_names[ffi[s]])
                    ptab.append((s, tot, ffi[s], pts[2], pts[1], sum(pts[3:7]), max(round(adv[s] / 1000.0), 1)))
                g = ident.setdefault(y, dict(affected_eligible=0, affected_scored=0, affected_h2=0, retained_scored=0))
                if s in self.id_reject or s in self.id_none:
                    g["affected_eligible"] += 1
                    g["affected_h2"] += int(h2)
                    g["affected_scored"] += int(tot is not None)
                    aff_sm.append(s)
                elif tot is not None and not bits & E.BIT["duplicate_class"]:
                    g["retained_scored"] += 1
                    ret_sm.append(s)
            for key, v in (("eligible", len(rows)), ("nonfin", n_nf), ("h2_nonfin", n_h2), ("scored", n_sc),
                           ("candidates", n_c), ("ge75", cnt[0]), ("ge80", cnt[1]), ("ge85", cnt[2]), ("ge90", cnt[3])):
                a[key] += v
            per_review.append([str(t), len(rows), len(self.repaired.get(t, ())), n_nf, n_h2, n_sc, n_c] + cnt +
                              [str(regime)])
            mech_reviews.append(dict(t=t, year=t.year, rows=rows, adv=adv, ff=ffi, company=company, regime=regime))
            if idx < len(reviews) - 1 or self.end.year < 2017:
                ptab.sort()
                power_tables.append(dict(ids=np.array([x[0] for x in ptab]), S=np.array([x[1] for x in ptab]),
                                         sector=np.array([x[2] for x in ptab]), risk=np.array([x[3] for x in ptab]),
                                         mom_pts=np.array([x[4] for x in ptab], float),
                                         fund=np.array([x[5] for x in ptab], float),
                                         size=np.log(np.array([x[6] for x in ptab], float)), year=t.year,
                                         regime=regime, tk=_ds(self.cal[k])))
            old = self.old.get(str(t), set())
            dlv = {s for s, e in elig.items() if not e["rep"]}
            uni = set(elig)
            final_last = uni
            sv = surv.setdefault(y, {})
            for name, grp in (("data_v1", old), ("delivered", dlv), ("v2_universe", uni), ("lost", old - dlv),
                              ("recovered", (old - dlv) & uni), ("still_lost", old - uni),
                              ("added_not_v1", uni - old - dlv)):
                z = sv.setdefault(name, [0, 0])
                z[0] += len(grp)
                z[1] += sum(1 for s in grp if s in self.old_last)
            for s in old - dlv:
                rs = self.tgt_reason.get((str(t), s), "unknown")
                z = rec.setdefault(rs, [0, 0, 0])
                z[0] += 1
                z[1] += int(s in uni)
                z[2] += int(s in uni and s not in self.old_last)
                sec_lost[s] = rs if s not in uni else sec_lost.get(s, "recovered")
                if s in uni:
                    sec_rec.add(s)
                if rs == "mcap_missing":
                    z = mc2.setdefault(self.cstat.get((str(t), s), "not_a_candidate"), [0, 0])
                    z[0] += 1
                    z[1] += int(s not in self.old_last)
        self.st["slice_spot_check"] = spot
        # identity sanity (owner item 7): survival = in the Data v2 universe at the run's last review
        isurv = dict(affected_securities=len(self.id_reject | self.id_none), by_year=ident)
        aff_ev = [len(aff_sm), sum(1 for s in aff_sm if s in final_last)]
        ret_ev = [len(ret_sm), sum(1 for s in ret_sm if s in final_last)]
        isurv.update(affected_stock_months=aff_ev[0], affected_survival=round(aff_ev[1] / aff_ev[0], 4) if aff_ev[0] else None,
                     retained_fully_scorable_stock_months=ret_ev[0],
                     retained_survival=round(ret_ev[1] / ret_ev[0], 4) if ret_ev[0] else None)
        # weekly H3 / H4 / H5 / H6 (X993 v1.1) restricted to the final universe of the review in force
        weekly = []
        sid_rev = {t: i for i, t in enumerate(reviews)}
        for t in sorted(self.wk):
            lt, wbits = self.wk[t]
            if lt not in self.mon:
                continue
            k = wk_rows[t]
            bits_out, members = {}, []
            for s, bits in wbits.items():
                if s not in self.mon[lt]:
                    continue
                members.append(s)
                if not self.mon[lt][s].get("base_ok"):
                    bits = (bits & ~(E.BIT["H2"] | E.BIT["H7"])) | E.BIT["H2"]
                if s in cand_ever and s in self.col:
                    j = self.col[s]
                    ti, cont = E.tech_at(self.C[:, j], self.P[:, j], k, self.unv.get(j, ()), self.dist.get(j, ()))[:2]
                    if ti["bars"] < S.MIN_HISTORY or ti["mom_12_1"] is None or ti["vol60"] is None or ti["trend_state"] is None:
                        bits |= E.BIT["H3"]
                    bits |= (E.BIT["H4"] if cont else 0) | (E.BIT["H5"] if ti["age"] is None or ti["age"] > S.STALE_PRICE_SESSIONS else 0) \
                        | (E.BIT["H6"] if ti["broken_trend"] else 0)
                bits_out[s] = bits
            weekly.append(dict(t=t, review_index=sid_rev[lt], bits=bits_out, members=members))
        mech = V.simulate(mech_reviews, weekly, E.BIT, E.eligible_flag, M.plan, S.weekly_check, M.REGIME_POSITIONS)
        mech["frozen_constants"] = dict(entry=80, exit=70, buffer=5, K=10, initial_cap=M.INITIAL_POSITION_CAP,
                                        regime_positions=M.REGIME_POSITIONS, sector_max=M.SECTOR_MAX,
                                        grown_winner_cap=M.GROWN_WINNER_CAP)
        L3 = {k: np.asarray(v, dtype=float) for k, v in lay.items()}
        corr = None
        if L3["T"].size > 2:
            cm = np.corrcoef(np.vstack([L3["T"], L3["F"], L3["S"]]))
            corr = {k: (round(float(v), 4) if np.isfinite(v) else None)
                    for k, v in (("T_F", cm[0, 1]), ("T_S", cm[0, 2]), ("F_S", cm[1, 2]))}
        never = {s: r for s, r in sec_lost.items() if s not in sec_rec}
        nr = {}
        for s, r in never.items():
            add(nr, r + ("|later_disappearing" if s not in self.old_last else "|in_v1_universe_end_2017"))
        udig = {}
        for t in reviews:
            udig.setdefault(str(t.year), hashlib.sha256()).update((str(t) + "|" + ",".join(sorted(self.mon[t])) + "\n").encode())
        self.st.update(
            per_review_cols=["review", "eligible", "repaired", "nonfin", "h2_nonfin", "scored", "candidates", "ge75",
                             "ge80", "ge85", "ge90", "regime"],
            per_review=per_review, per_year=yr, regimes=regimes, sectors_80plus=sectors,
            totals_hist5_candidates=hist5(tot_c), totals_candidates=stats(tot_c), totals_scored=stats(tot_p),
            totals_hist5_scored=hist5(tot_p), layers={k: dict(stats=stats(v), hist5=hist5(v)) for k, v in lay.items()},
            layer_corr=corr, field_order=["revenue_ttm4q", "gross_profit_ttm4q", "net_income_ttm4q",
                                          "operating_cash_flow_ttm4q", "total_assets", "stockholders_equity",
                                          "revenue_baseline_valid"],
            survivorship=surv, target_recovery_by_reason=rec, target_mcap_missing_status=mc2,
            target_securities=dict(targets=len(sec_lost), recovered_at_least_once=len(sec_rec),
                                   recovered_later_disappearing=sum(1 for s in sec_rec if s not in self.old_last),
                                   never_recovered_by_last_reason=nr),
            identity_mapping=self.idc, identity_value_check=self.idv, restatement_guard=self.guard,
            identity_sanity=isurv, sec_split_check=self._split_check(), mechanics=mech, pit_audit=self.audit,
            weekly_checks=len(weekly))
        h_counts = {y: a["bits"] for y, a in yr.items()}
        self.st["digests"] = dict(
            ledger_by_year={str(y): h.hexdigest() for y, h in sorted(self.dg.items())}, ledger_to_2013=self.dg_cut.hexdigest(),
            universe_by_year={y: h.hexdigest() for y, h in sorted(udig.items())}, review_eligibility=edig,
            review_scores=sdig, h_counts=sha(h_counts), score_distribution=sha([hist5(tot_c), hist5(tot_p)]),
            mechanics=sha(mech))
        self.st["score_s"] = round(time.perf_counter() - t1, 1)
        if self.mode == "power":
            import qr_p7_pred as R
            t2 = time.perf_counter()
            self.st["power"] = {name: V.power_scenario(R, power_tables, sd) for name, sd in V.SCENARIOS.items()}
            self.st["power_s"] = round(time.perf_counter() - t2, 1)
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        text = json.dumps(self.st, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRV2|{i // 9000}|{text[i:i + 9000]}")
