# X993 v1.1 (P7-CP3R, owner D173): the YoY revenue baseline is the company's PIT revenue True TTM recorded LIVE at
# the review 12 months earlier for EVERY company in the PIT store (qr_p7_export.RevenueLedger), not only for securities
# then eligible; valid only within the same security life and SEC registrant and with every component quarter usable on
# or before that day (otherwise H2). SEC-repaired securities are fed whenever a further filing becomes usable. The CP3
# eligible-only rule is evaluated alongside for the audit (bit H2_old_rule), with the reason each rescued company was
# outside the universe a year earlier; non-chosen share classes are also scored (class substituted) so a held class can
# be kept. Score v1 is unchanged.
# X993 — Phase 7 (P7-CP3, owner D171) SCORE AVAILABILITY / MECHANICS EXPORT (infrastructure; NO orders, NO returns,
# NO performance of any kind). Runs the FROZEN conviction score v1 (qr_p7_score, hash-pinned in qresearch.p7score) at
# the 84 month-end reviews 2011-01 .. 2017-12 and exports the score tables, disqualifier flags, share-class choices,
# breadth / regime states and the weekly hard-disqualifier states the mechanics study needs. Nothing after
# 2017-12-31 is requested; official start 2011-01-03 with the history-only warm-up from 2008-07-01 (2010 month-ends
# exist only as the revenue-baseline ledger).
# During the run (the X991 pipeline): every company with vendor fundamentals is observed daily (frozen observe_vendor;
# SEC-repaired securities fed from the SEC table). Reviews come from the session calendar (D171): the universe
# selection stamped the day after a session t reflects t; t is a month-end review if the next market open is in
# another month, a weekly check if it is in another ISO week. At each month-end: the eligible set with SIC, CIK,
# ADV20 and the fundamental inputs (revenue baseline = the True TTM recorded at the month-end review 12 months
# earlier for the securities eligible then; the X991 v1.1 ledger). At each weekly check: H1 / H2 / H7 states of the
# securities eligible at the latest review (the only possible holdings).
# At the end (the X992 pipeline): RAW x split feed = split-adjusted closes C (SCALED_RAW verifies split boundaries),
# x dividend feed = total-return closes P; per review: breadth states, sector contexts, one class per company, the
# frozen technical inputs / contamination (exact sliced computation, qr_p7_export.tech_at, spot-checked against the
# full computation in-host), the frozen score_date, SPY trend and regime; weekly H3 / H4 / H5 / H6 states.
# Outputs: integer points, disqualifier bits, ADV20 ($K), FF12 codes, breadth shares and states (no price, no return).
from AlgorithmImports import *
from datetime import date, datetime, timedelta
import hashlib
import json
import time
import numpy as np
from qr_harness import EXCHANGES, QRAlgorithm, exchange_of, is_us_common
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, observe_vendor
import qr_p7 as P
import qr_p7_score as S
import qr_p7_export as E
import qr_xs_diag as XD
import qr_xs_panel as XP

HIST_START = datetime(2007, 1, 1)
HIST_END = datetime(2017, 12, 31)
LAST_SESSION = np.datetime64("2017-12-29").astype(np.int64)
LEDGER_FROM = date(2010, 1, 1)          # month-end sessions from 2010-01 record the revenue baseline ledger
REVIEW_FROM = date(2011, 1, 1)          # first scored review: the last session of 2011-01
REVIEW_TO = date(2017, 12, 31)
BATCH = 100
SPOT_SALT = "P7CP3-slice-check"
SPOT_PER_REVIEW = 4
WEEKLY_FROM_SCORE = 75                  # weekly states exported for every security that was ever a candidate >= 75
RESCUE_SAMPLE = 40                      # v1.1: deterministic sample of rescued baselines (dates only) for SEC checks
RESCUE_SALT = "P7CP3R-rescued"


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


class P7ScoreExport(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        if self.qr_sec is None or self.qr_sic is None:
            raise Exception("X993 needs universe.sec_corrections (frozen data infrastructure v1)")
        if self.qr["end"] > "2017-12-31":
            raise Exception("X993: P7-CP3 ends on or before 2017-12-31")
        self.t0 = time.perf_counter()
        self.store = PITStore(DEFAULT_MAX_AGE_DAYS, holds=self.qr_timing_holds, releases=self.qr_quarantine_releases,
                              blocked=self.qr_restatement_blocks, field_releases=self.qr_field_releases)
        self.seen_q = set()
        self.prev_session = None
        self.done_t = None
        self.cik = {}                    # sid -> [(effective date, CIK)] (the PIT SIC rows, D113)
        for sid, rows in (self.qr_sec.sic_history or {}).items():
            self.cik[sid] = [(date.fromisoformat(e), str(c) if c not in (None, "") else None) for e, _s, c in rows]
        self.sym = {}
        self.mon = {}                    # review t -> {sid: dict(sic, cik, adv, vals, base, old_base, reason, ...)}
        self.mon_sel = {}                # review t -> selection day
        self.rev = E.RevenueLedger()     # v1.1 (D173): store-wide company revenue True TTM at every month-end
        self.elig_at = {}                # (y, m) -> eligible sids at that review (the CP3 eligible-only ledger rule)
        self.why = {}                    # (y, m) -> {sid: reason code} for store companies outside the universe
        self.first_seen = {}             # sid -> first day in QuantConnect's universe list
        self.sec_next = {}               # sid -> next day a further SEC filing of a repaired security becomes usable
        self.wk = {}                     # weekly t -> (review in force, {sid: H1 / H2 / H7 bits})
        self.last_review = None          # (t, eligible sids) of the latest scored review
        u = self._qr_u
        self.filt = (float(u.get("min_market_cap", 2e9)), float(u.get("min_price", 0.0)),
                     float(u.get("min_avg_dollar_volume", 0.0)), int(u.get("adv_days", 20)))
        self.c = dict(selections=0, month_ends=0, weekly=0, sec_fed=0, store_sids_max=0)

    def on_data(self, data):
        super().on_data(data)
        if data.bars.count > 0 and self.time.hour >= 9:      # a real session (not a midnight corporate-action slice)
            self.prev_session = self.time.date()

    def _cik_on(self, sid, today):
        out = None
        for eff, c in self.cik.get(sid, ()):
            if eff <= today:
                out = c
            else:
                break
        return out

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        out = super()._qr_select(fl)
        today = self.time.date()
        self.c["selections"] += 1
        elig = {str(s.id): s for s in self.qr_eligible}
        adv = {str(s.id): v[1] for s, v in self.qr_eligible_info.items()}
        for f in fl:
            sid = str(f.symbol.id)
            self.first_seen.setdefault(sid, today)
            if not f.has_fundamental_data:
                # v1.1 (D173): every SEC-repaired security is fed on each day a further filing becomes usable (not only
                # while eligible): the same filings with the same availability dates (idempotent), complete history
                if self.qr_sec.has(sid):
                    nxt = self.sec_next.get(sid)
                    if nxt is None or nxt <= today:
                        self.qr_sec.feed(sid, today, self.store)
                        self.c["sec_fed"] += 1
                        fut = [x.available for x in self.qr_sec.filings[sid] if x.available > today]
                        self.sec_next[sid] = min(fut) if fut else date.max
                continue
            observe_vendor(self.store, sid, f, today, get, self.seen_q)
        t = self.prev_session
        if t is None or t == self.done_t or t > REVIEW_TO:
            return out
        self.done_t = t
        nxt = self.securities[self.spy].exchange.hours.get_next_market_open(self.time, False).date()
        month_end = nxt.month != t.month or nxt.year != t.year
        week_end = nxt.isocalendar()[:2] != t.isocalendar()[:2]
        if month_end and t >= LEDGER_FROM:
            self._month_end(t, today, elig, adv, fl)
        elif week_end and self.last_review is not None:
            self._weekly(t, today)
        return out

    def qr_select_universe(self, eligible):
        return []

    def _why_not(self, f, sid, today):
        """Why a company in the store is outside the eligible universe today (P7-CP3R audit only)."""
        min_cap, min_price, min_adv, adv_days = self.filt
        fix = not f.has_fundamental_data
        day = str(today)
        if not fix:
            try:
                if not is_us_common(f, day) or exchange_of(f, day) not in EXCHANGES:
                    return 5
            except Exception:
                return 6
        try:
            px = float(f.price)
            mc = float(f.market_cap) if not fix else (self.qr_sec.market_cap(sid, today, px) or 0.0)
        except Exception:
            return 6
        if not mc >= min_cap:
            return 2
        if px < min_price:
            return 3
        dq = self._qr_dv.get(f.symbol)
        if dq is None or len(dq) < adv_days or not sum(dq) / len(dq) >= min_adv:
            return 4
        return 6

    # ------------------------------------------------------------------------------------------------ snapshots
    def _month_end(self, t, today, elig, adv, fl):
        self.c["month_ends"] += 1
        ym = (t.year, t.month)
        store_sids = sorted(set(self.store.hist) | set(self.store.pending))
        self.c["store_sids_max"] = max(self.c["store_sids_max"], len(store_sids))
        if t < date(2017, 1, 1):                       # baselines are needed up to the 2017-12 review
            self.rev.record(ym, t, today, self.store, store_sids)
            self.elig_at[ym] = set(elig)
            byf = {str(f.symbol.id): f for f in fl}
            self.why[ym] = {sid: (0 if sid in elig else (self._why_not(byf[sid], sid, today) if sid in byf else 1))
                            for sid in self.rev.v[ym]}
        rows = {}
        if t >= REVIEW_FROM:
            prev = self.rev.prior(ym)
            for sid, s in elig.items():
                self.sym[sid] = s
                v, det, bday = self.rev.baseline(ym, sid)
                rows[sid] = dict(sic=self.qr_sic.sic_on(sid, today), cik=self._cik_on(sid, today), adv=adv[sid],
                                 vals=E.fund_values(self.store, sid, today), base=v, base_det=det, base_day=bday,
                                 old_base=v if sid in self.elig_at.get(prev, ()) else None,
                                 prior_reason=self.why.get(prev, {}).get(sid))
            self.mon[t] = rows
            self.mon_sel[t] = today
            self.last_review = (t, tuple(sorted(elig)))
        for old in [k for k in self.rev.v if k < (t.year - 1, t.month)]:
            self.rev.drop(old)
            self.why.pop(old, None)
            self.elig_at.pop(old, None)

    def _weekly(self, t, today):
        """H1 / H2 / H7 of the possible holdings with the baseline of the score in force (validated at the end)."""
        self.c["weekly"] += 1
        lt = self.last_review[0]
        out = {}
        for sid in self.last_review[1]:
            bits = E.sic_bits(self.qr_sic.sic_on(sid, today))
            fi, _, _ = E.fund_inputs(E.fund_values(self.store, sid, today), self.mon[lt][sid]["base"])
            if fi is None:
                bits |= E.BIT["H2"]
            elif fi["impaired"]:
                bits |= E.BIT["H7"]
            out[sid] = bits
        self.wk[t] = (lt, out)

    # ------------------------------------------------------------------------------------------------ panel
    def _cols(self, frame, loc, cal, D, n, fields, st):
        out = {f: np.full((D, n), np.nan) for f in fields}
        if frame is None or frame.empty:
            return out
        idx = frame.index
        lmap = np.array([loc.get(_sid(s), -1) for s in idx.levels[0]], dtype=np.int64)
        cols = lmap[np.asarray(idx.codes[0])]
        days = XP.session_days(idx.get_level_values(-1).values)
        st["late_rows"] += int((days > LAST_SESSION).sum())
        pos = np.searchsorted(cal, days)
        pc = np.minimum(pos, cal.size - 1)
        ok = (cols >= 0) & (cal[pc] == days) & (days <= LAST_SESSION)
        st["off_calendar_rows"] += int(((cols >= 0) & ~(cal[pc] == days) & (days <= LAST_SESSION)).sum())
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
            if cols[r] < 0:
                continue
            if eday[r] > LAST_SESSION:
                st["late_events"] += 1
                continue
            out[int(cols[r])].append((int(np.searchsorted(cal, eday[r])),) + tuple(v[r] for v in vals))
        return out

    def _adjust(self, raw, sc, sev, dev, st, D):
        """X992 construction: split multiplier verified by SCALED_RAW; dividend-feed factors. Returns (mult, dm,
        unverified split rows, [(ex-row, distribution / reference)])."""
        vv = np.flatnonzero(np.isfinite(raw) & np.isfinite(sc) & (raw > 0) & (sc > 0))
        if vv.size and abs(sc[vv[-1]] / raw[vv[-1]] - 1.0) > 1e-6:
            sc = sc / (sc[vv[-1]] / raw[vv[-1]])
        ev = []
        for r_, typ, ref, fac in sev:
            if "OCCUR" in str(typ).upper() or float(ref) > 0:
                ev.append((r_, float(fac)))
        de = [(r_, float(amt), float(ref)) for r_, amt, ref in dev]
        det = []
        mult, s1 = XP.split_multiplier(raw, sc, ev, detail=det)
        for k2, v2 in s1.items():
            st["split"][k2] += v2
        dm = XP.dividend_multiplier(D, de)
        unv = [int(d[0]) for d in det]
        dist = [(r_, amt / ref) for r_, amt, ref in de if ref > 0]
        st["dividend_events"] += len(de)
        st["large_distributions_10pct"] += sum(1 for _, f in dist if f >= S.LARGE_DISTRIBUTION)
        return mult, dm, unv, dist

    def _build(self):
        t0 = time.perf_counter()
        spy = self.history(self.spy, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        cal = np.unique(XP.session_days(spy.index.get_level_values(-1).values))
        cal = cal[cal <= LAST_SESSION]
        D = cal.size
        sids = sorted({s for rows in self.mon.values() for s in rows} | {s for w in self.wk.values() for s in w[1]})
        N = len(sids)
        st = dict(sessions=D, first_session=_ds(cal[0]), last_session=_ds(cal[-1]), securities=N, late_rows=0,
                  off_calendar_rows=0, duplicate_bars=0, late_events=0, history_calls=0,
                  split=dict(n=0, aligned=0, realigned=0, unverified=0, outside=0), dividend_events=0,
                  large_distributions_10pct=0)
        C, Hh, L, Pt = (np.full((D, N), np.nan) for _ in range(4))
        self.unv, self.dist = {}, {}
        for i in range(0, N, BATCH):
            part = sids[i:i + BATCH]
            syms = [self.sym[s] for s in part]
            loc = {s: j for j, s in enumerate(part)}
            n = len(part)
            hr = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.RAW)
            hs = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            sp = self.history(Split, syms, HIST_START, HIST_END)
            dv = self.history(Dividend, syms, HIST_START, HIST_END)
            st["history_calls"] += 4
            a = self._cols(hr, loc, cal, D, n, ("high", "low", "close"), st)
            b = self._cols(hs, loc, cal, D, n, ("close",), st)
            sev = self._events(sp, loc, cal, ("type", "referenceprice", "splitfactor"), st)
            dev = self._events(dv, loc, cal, ("distribution", "referenceprice"), st)
            for j in range(n):
                g = i + j
                raw = a["close"][:, j]
                if not np.any(np.isfinite(raw) & (raw > 0)):
                    continue
                mult, dm, unv, dist = self._adjust(raw, b["close"][:, j], sev[j], dev[j], st, D)
                C[:, g], Hh[:, g], L[:, g], Pt[:, g] = raw * mult, a["high"][:, j] * mult, a["low"][:, j] * mult, \
                    raw * mult * dm
                self.unv[g], self.dist[g] = unv, dist
        if st["late_rows"]:
            raise Exception("X993: history returned data after 2017-12-29")
        # SPY split-adjusted closes (regime input)
        spy_raw = np.full(D, np.nan)
        d_spy = XP.session_days(spy.index.get_level_values(-1).values)
        ok = d_spy <= LAST_SESSION
        spy_raw[np.searchsorted(cal, d_spy[ok])] = spy["close"].to_numpy(dtype=float)[ok]
        ssp = self.history(Split, [self.spy], HIST_START, HIST_END)
        sev = self._events(ssp, {_sid(self.spy): 0}, cal, ("type", "referenceprice", "splitfactor"), st).get(0, [])
        evs = [(r_, float(f)) for r_, typ, ref, f in sev if "OCCUR" in str(typ).upper() or float(ref) > 0]
        m = np.ones(D)
        for r_, f in evs:
            m[:r_] *= f
        self.spy_c = spy_raw * m
        st["spy_splits"] = len(evs)
        st["build_s"] = round(time.perf_counter() - t0, 1)
        self.cal, self.sids, self.col = cal, sids, {s: j for j, s in enumerate(sids)}
        self.C, self.H, self.L, self.P = C, Hh, L, Pt
        self.st["panel"] = st

    def _row(self, t):
        k = int(np.searchsorted(self.cal, _day(t)))
        if k >= self.cal.size or self.cal[k] != _day(t):
            raise Exception(f"X993: review session {t} not on the SPY calendar")
        return k

    # ------------------------------------------------------------------------------------------------ baselines
    def _life_start_row(self, j, k):
        if j not in self._life:
            v = P.valid_rows(self.C[:, j], self.P[:, j])
            self._life[j] = (v, P.life_starts(v))
        v, ls = self._life[j]
        b = int(np.searchsorted(v, k, side="right")) - 1
        return None if b < 0 else int(v[ls[b]])

    def _baselines(self, reviews, rows_k):
        """v1.1 (D173): validate every store-wide revenue baseline (same security life, same SEC registrant, every
        component quarter usable on or before the baseline selection day), then compute the fundamental inputs under
        the corrected rule and, for the audit, under the CP3 eligible-only rule."""
        self._life = {}
        st = dict(rows=0, nonfin_rows=0, store_baseline=0, life_reject=0, cik_reject=0, rescued=0, lost=0,
                  pit_violations=0, h2_new=0, h2_old=0, reasons={}, listed_lt_1y=0)
        resc = []
        for t in reviews:
            k = rows_k[t]
            today = self.mon_sel[t]
            for sid, e in self.mon[t].items():
                st["rows"] += 1
                ok, why = False, "none"
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
                fi_old = E.fund_inputs(e["vals"], e["old_base"])[0]
                e["fund"] = (fi, why2)
                e["base_only"] = bo
                e["H2_old_rule"] = fi_old is None
                e["baseline_life_reject"] = why == "life"
                e["baseline_cik_reject"] = why == "cik"
                nonfin = e["sic"] is not None and not 6000 <= int(e["sic"]) <= 6999
                st["nonfin_rows"] += int(nonfin)
                st["h2_new"] += int(fi is None and nonfin)
                st["h2_old"] += int(fi_old is None and nonfin)
                if fi is not None and fi_old is None:
                    st["rescued"] += 1
                    e["rescued"] = True
                    e["reason"] = e["prior_reason"] if e["prior_reason"] is not None else 6
                    add(st["reasons"], str(e["reason"]))
                    fs = self.first_seen.get(sid)
                    e["listed_lt_1y_at_baseline"] = fs is not None and (e["base_day"][1] - fs).days < 365 \
                        and fs > date(2008, 7, 15)
                    st["listed_lt_1y"] += int(e["listed_lt_1y_at_baseline"])
                    resc.append((sid, t))
                elif fi is None and fi_old is not None:
                    st["lost"] += 1
        self.st["baseline"] = st
        pick = set(P.pick([f"{s}|{t}" for s, t in resc], RESCUE_SAMPLE, RESCUE_SALT))
        self.rescued_sample = []
        for s_, t in resc:
            if f"{s_}|{t}" not in pick:
                continue
            e = self.mon[t][s_]
            _, pe, fd = e["base_det"]
            self.rescued_sample.append(dict(
                sid=s_, review=str(t), baseline_session=str(e["base_day"][0]), baseline_selection=str(e["base_day"][1]),
                quarters=[str(date.fromordinal(x)) for x in pe], filed=[str(date.fromordinal(x)) for x in fd],
                reason=E.REASONS.get(e["reason"]), cik=self._cik_on(s_, self.mon_sel[t]),
                first_seen=str(self.first_seen.get(s_))))

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        self.st = dict(checks=self.c, store_stats=dict(self.store.stats))
        self._build()
        t1 = time.perf_counter()
        reviews = sorted(self.mon)
        rows_k = {t: self._row(t) for t in reviews}
        wk_rows = {t: self._row(t) for t in sorted(self.wk)}
        need = sorted(set(rows_k.values()) | set(wk_rows.values()))
        a200 = {}
        for j in range(len(self.sids)):
            cs = P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])["above200"]
            a200[j] = cs[need]
        rix = {k: i for i, k in enumerate(need)}
        self.st["states_s"] = round(time.perf_counter() - t1, 1)
        # every month-end / ISO-week-end session of the SPY calendar 2011-01 .. 2017-12 must have been processed
        days = self.cal.astype("datetime64[D]")
        lo_r, hi_r = int(np.searchsorted(self.cal, _day(REVIEW_FROM))), int(np.searchsorted(self.cal, LAST_SESSION))
        exp_m, exp_w = [], []
        for r in range(lo_r, hi_r + 1):
            d0 = date.fromisoformat(str(days[r]))
            d1 = date.fromisoformat(str(days[r + 1])) if r + 1 < days.size else date(2018, 1, 2)
            if (d1.year, d1.month) != (d0.year, d0.month):
                exp_m.append(d0)
            elif d1.isocalendar()[:2] != d0.isocalendar()[:2] and d0 > reviews[0]:
                exp_w.append(d0)
        self.st["calendar_check"] = dict(reviews=len(reviews), expected_reviews=len(exp_m),
                                         reviews_match=[str(x) for x in exp_m] == [str(x) for x in reviews],
                                         weekly=len(self.wk), expected_weekly=len(exp_w),
                                         weekly_match=[str(x) for x in exp_w] == [str(x) for x in sorted(self.wk)],
                                         first_review=str(reviews[0]), last_review=str(reviews[-1]))
        self._baselines(reviews, rows_k)
        sid_index = {s: i for i, s in enumerate(self.sids)}
        ff_names = list(XD.FF12_NAMES)
        spot = dict(checked=0, mismatch=0, full_fallbacks=0, examples=[])
        cand_ever = set()
        review_out, regimes, sectors = [], [], []
        dq_dup = []
        t2 = time.perf_counter()
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
                    spot["full_fallbacks"] += int(cache[s][4])
                return cache[s]
            res = E.score_review(elig, st200, tech, XD.ff12)
            # in-host exactness spot check of the sliced technical computation against the full history
            for s in P.pick(sorted(res["kept"]), SPOT_PER_REVIEW, f"{SPOT_SALT}|{t}"):
                j = self.col[s]
                full = S.technical_inputs(self.C[:k + 1, j], self.P[:k + 1, j], k)
                cf = S.contamination(full, self.unv.get(j, ()), self.dist.get(j, ()))
                sl = tech(s)
                spot["checked"] += 1
                same = all(sl[0][f] == full[f] for f in ("close", "sma50", "sma200", "sma200_lag", "mom_12_1",
                                                          "vol60", "trend_state", "broken_trend", "age")) and \
                    (sl[0]["bars"] >= S.MIN_HISTORY) == (full["bars"] >= S.MIN_HISTORY) and \
                    sl[1] == cf[0] and sl[3] == cf[2]
                if not same:
                    spot["mismatch"] += 1
                    if len(spot["examples"]) < 10:
                        spot["examples"].append([s, str(t)])
            adv = {s: e["adv"] for s, e in elig.items()}
            ffo = {s: XD.ff12(e["sic"]) for s, e in elig.items()}
            for s, (bits, tot, pts) in res["rows"].items():
                if E.eligible_flag(bits, tot) and tot >= WEEKLY_FROM_SCORE:
                    cand_ever.add(s)
            review_out.append([str(t), _ds(self.cal[k]), E.encode_rows(res["rows"], sid_index, adv, ffo, ff_names)])
            trend = S.spy_trend(self.spy_c, k)
            mb, up, known, n_el = res["breadth"]
            regimes.append([str(t), trend, None if mb is None else round(mb, 6), up, known, n_el,
                            S.breadth_level(mb), S.regime(trend, mb)])
            sectors.append([str(t), {g: [None if v[0] is None else round(v[0], 6), v[1], v[2], res["context"][g]]
                                     for g, v in res["sectors"].items()}])
            cik_groups = {}
            for s, e in elig.items():
                if e["cik"] is not None:
                    cik_groups.setdefault(e["cik"], []).append(s)
            dups = [[c, sorted(v), sorted(set(v) & res["kept"])] for c, v in cik_groups.items() if len(v) > 1]
            dq_dup.append([str(t), dups])
        self.st["score_s"] = round(time.perf_counter() - t2, 1)
        self.st["slice_spot_check"] = spot
        # weekly technical states (H3 / H4 / H5 / H6) for every security that was ever an eligible candidate >= 75
        t3 = time.perf_counter()
        weekly = []
        for t in sorted(self.wk):
            k = wk_rows[t]
            parts = []
            lt, wbits = self.wk[t]
            for s, bits in sorted(wbits.items()):
                if not self.mon[lt][s]["base_ok"]:          # baseline of the score in force rejected / absent
                    bits = (bits & ~(E.BIT["H2"] | E.BIT["H7"])) | E.BIT["H2"]
                if s not in cand_ever:
                    continue
                j = self.col[s]
                ti, cont = E.tech_at(self.C[:, j], self.P[:, j], k, self.unv.get(j, ()), self.dist.get(j, ()))[:2]
                if ti["bars"] < S.MIN_HISTORY or ti["mom_12_1"] is None or ti["vol60"] is None or ti["trend_state"] is None:
                    bits |= E.BIT["H3"]
                if cont:
                    bits |= E.BIT["H4"]
                if ti["age"] is None or ti["age"] > S.STALE_PRICE_SESSIONS:
                    bits |= E.BIT["H5"]
                if ti["broken_trend"]:
                    bits |= E.BIT["H6"]
                if bits:
                    parts.append(f"{sid_index[s]}:{bits}")
            weekly.append([str(t), _ds(self.cal[k]), sorted(sid_index[s] for s in wbits if s in cand_ever),
                           ",".join(parts)])
        self.st["weekly_s"] = round(time.perf_counter() - t3, 1)
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        try:
            import qr_p7_score as _m
            self.st["score_code_sha256"] = hashlib.sha256(open(_m.__file__, "rb").read()).hexdigest()
        except Exception as ex:
            self.st["score_code_sha256"] = f"unavailable: {type(ex).__name__}"
        payload = dict(rescued_sample=self.rescued_sample, sids=self.sids, ff12_names=ff_names, bits=list(E.BITS), dims=list(E.DIMS), reviews=review_out,
                       regimes=regimes, sectors=sectors, weekly=weekly, duplicates=dq_dup,
                       candidates_ever_75=len(cand_ever))
        blob = E.pack(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        self.st["payload_sha256"] = hashlib.sha256(blob.encode()).hexdigest()
        self.st["payload_chars"] = len(blob)
        text = json.dumps(self.st, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRP7S|{i // 9000}|{text[i:i + 9000]}")
        for i in range(0, len(blob), 9000):
            self._qr_log(f"QRP7X|{i // 9000}|{blob[i:i + 9000]}")
