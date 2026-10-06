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
from qr_harness import QRAlgorithm
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
        self.mon = {}                    # t (date) -> {sid: dict(sic, cik, adv, fund, base_only, base_store)}
        self.ledger = {}                 # (y, m) of t -> {sid: revenue True TTM} (eligible at that review)
        self.shadow = {}                 # (y, m) -> {sid: revenue True TTM} (every company in the store; diagnostic)
        self.wk = {}                     # weekly t -> {sid: H1 / H2 / H7 bits}
        self.last_review = None          # (t, eligible sids) of the latest scored review
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
        watch = set(elig) | (set(self.last_review[1]) if self.last_review else set())
        for f in fl:
            sid = str(f.symbol.id)
            if not f.has_fundamental_data:
                if sid in watch and self.qr_sec.has(sid):
                    self.qr_sec.feed(sid, today, self.store)
                    self.c["sec_fed"] += 1
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
            self._month_end(t, today, elig, adv)
        elif week_end and self.last_review is not None:
            self._weekly(t, today)
        return out

    def qr_select_universe(self, eligible):
        return []

    # ------------------------------------------------------------------------------------------------ snapshots
    def _month_end(self, t, today, elig, adv):
        self.c["month_ends"] += 1
        ym = (t.year, t.month)
        prev = (t.year - 1, t.month)
        led, base, sh = {}, self.ledger.get(prev, {}), self.shadow.get(prev, {})
        rows = {}
        for sid, s in elig.items():
            self.sym[sid] = s
            vals = E.fund_values(self.store, sid, today)
            if vals[0] is not None:
                led[sid] = vals[0]
            if t < REVIEW_FROM:
                continue
            sic = self.qr_sic.sic_on(sid, today)
            fi, why, bo = E.fund_inputs(vals, base.get(sid))
            rows[sid] = dict(sic=sic, cik=self._cik_on(sid, today), adv=adv[sid], fund=(fi, why), base_only=bo,
                             base_store=bo and sid in sh)
        self.ledger[ym] = led
        if t < date(2017, 1, 1):          # the shadow ledger is only needed as a 12-month-earlier diagnostic
            sh_now = {}
            for sid in sorted(set(self.store.hist) | set(self.store.pending)):
                v = self.store.ttm(sid, "revenue", today)
                if v is not None:
                    sh_now[sid] = v
            self.shadow[ym] = sh_now
            self.c["store_sids_max"] = max(self.c["store_sids_max"], len(self.store.hist))
        self.ledger.pop((t.year - 2, t.month), None)
        self.shadow.pop((t.year - 2, t.month), None)
        if t >= REVIEW_FROM:
            self.mon[t] = rows
            self.last_review = (t, tuple(sorted(elig)))

    def _weekly(self, t, today):
        self.c["weekly"] += 1
        lt = self.last_review[0]
        base = self.ledger.get((lt.year - 1, lt.month), {})       # the baseline of the score in force
        out = {}
        for sid in self.last_review[1]:
            bits = E.sic_bits(self.qr_sic.sic_on(sid, today))
            fi, _, _ = E.fund_inputs(E.fund_values(self.store, sid, today), base.get(sid))
            if fi is None:
                bits |= E.BIT["H2"]
            elif fi["impaired"]:
                bits |= E.BIT["H7"]
            out[sid] = bits
        self.wk[t] = out

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
        sids = sorted({s for rows in self.mon.values() for s in rows} | {s for w in self.wk.values() for s in w})
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
            for s, bits in sorted(self.wk[t].items()):
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
            weekly.append([str(t), _ds(self.cal[k]), sorted(sid_index[s] for s in self.wk[t] if s in cand_ever),
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
        payload = dict(sids=self.sids, ff12_names=ff_names, bits=list(E.BITS), dims=list(E.DIMS), reviews=review_out,
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
