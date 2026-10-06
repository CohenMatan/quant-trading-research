# S023 v1.1 — H022 PREDICTIVE VALIDATION HOST (research/phase7/P7_predictive_spec.md v1 as corrected by D177; owner
# authorisation 2026-10-06, D177). X994 = a byte copy run as the plumbing canary. NO orders, NO portfolio, NO
# performance; nothing after 2017-12-31 is requested (the last price row is the 2017-12-29 session).
# The score pipeline is the X993 v1.1 export (E993-02, P7-CP3R) unchanged: PIT store + observe_vendor daily, SEC feed of
# repaired securities, store-wide live revenue ledger, month-end reviews from the session calendar, end-of-run panel
# (RAW x split feed verified by SCALED_RAW = C; x dividend feed = P), frozen technical inputs (exact sliced tech_at,
# spot-checked), frozen score_review / Score v1 and regime. Added for H022 (P7_predictive_spec.md Part C):
#   - the RAW OPEN of every bar and the market cap of every eligible security at each review;
#   - the population of each decision t (83 month-end reviews 2011-01-31 .. 2017-11-30): eligible, kept class, fully
#     scorable, no hard disqualifier H1-H7 (qr_p7_export.eligible_flag), with score, FF12 sector, 12-1 momentum, log
#     market cap and the frozen regime;
#   - the responses, computed only AFTER every score is final: qr_p7_pred.response (next valid open after t -> close
#     of the next review session; last real close on delisting; 0 with no bar; NaN on an unverified split) on RAW
#     prices x the panel's split x dividend multiplier; horizons 1 (primary), 2 and 3 reviews (diagnostics).
# Modes (params.mode): canary = plumbing / integrity checks only (no IC of the real assignment, no gate, no null
# statistic); null = worlds params.seeds [first, last] of the frozen identity-tethered null, the full procedure per
# world, per-world statistics only; real = the ONE real evaluation, refused unless the pinned null provenance is given
# and the prepared panel equals the one the null was calibrated on.
from AlgorithmImports import *
from datetime import date, datetime, timedelta
import hashlib
import json
import math
import time
import numpy as np
from qr_harness import EXCHANGES, QRAlgorithm, exchange_of, is_us_common
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore, observe_vendor
import qr_p7 as P
import qr_p7_score as S
import qr_p7_export as E
import qr_p7_pred as R
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
PROVENANCE = ("c_ic", "threshold_commit", "null_result_sha256", "spec_sha256", "panel_sha256")
DECISIONS = ("2011-01-31", "2017-11-30", 83)
HORIZONS = (1, 2, 3)                    # reviews ahead: primary 1, diagnostics 2 and 3
CANARY_SALT = "P7CP5-X994"
CANARY_FRESH = 30                       # fresh-history recomputations per event class (split / dividend / truncated / plain)
CANARY_PERTURB = 80                     # stock-dates for the response future / past / truncation invariance checks
CANARY_SCORE_REVIEWS = 6                # reviews re-scored on truncated and future-perturbed price histories
TIMING_WORLDS = 20                      # null machinery timing on SYNTHETIC responses (no real response used)
MODULES = ("qr_p7_pred.py", "qr_p7_score.py", "qr_p7_export.py", "qr_p7.py", "qr_h020_stats.py", "qr_xs.py",
           "qr_xs_panel.py", "qr_fundamentals.py")


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


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _module_hashes():
    import os
    out = {}
    base = os.path.dirname(os.path.abspath(R.__file__))
    for n in MODULES:
        try:
            out[n] = hashlib.sha256(open(os.path.join(base, n), "rb").read()).hexdigest()
        except Exception as ex:
            out[n] = f"unavailable: {type(ex).__name__}"
    return out


class H022Predictive(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        p = self.qr_params
        self.h_mode = p.get("mode")
        if self.h_mode not in ("canary", "null", "real"):
            raise Exception(f"S023: unknown mode {self.h_mode!r}")
        if "spec_sha256" not in p or "pred_code_sha256" not in p:
            raise Exception("S023: params need spec_sha256 and pred_code_sha256 (frozen fingerprints)")
        # D178: the pinned module fingerprints are verified by the runner on QuantConnect's stored project files before
        # compiling; LEAN's runtime copy of a source file is not byte-identical, so in-host hashes are informational
        if self.h_mode == "null":
            a, b = (int(x) for x in p["seeds"])
            if not (1 <= a <= b <= R.R_NULL):
                raise Exception("S023: null seeds must lie in 1..5000")
            self.h_seeds = list(range(a, b + 1))
        if self.h_mode == "real":
            for k in PROVENANCE:
                if p.get(k) in (None, ""):
                    raise Exception(f"S023: real mode needs the pinned null provenance ({k})")
        if self.qr_sec is None or self.qr_sic is None:
            raise Exception("S023 needs universe.sec_corrections (frozen data infrastructure v1)")
        if self.qr["end"] > "2017-12-31":
            raise Exception("S023: H022 runs end on or before 2017-12-31")
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
        mcap = {str(s.id): v[0] for s, v in self.qr_eligible_info.items()}
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
            self._month_end(t, today, elig, adv, fl, mcap)
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
    def _month_end(self, t, today, elig, adv, fl, mcap):
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
                                 mcap=mcap.get(sid),
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
        RO, RC, M = (np.full((D, N), np.nan) for _ in range(3))
        self.unv, self.dist, self.splits = {}, {}, {}
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
            a = self._cols(hr, loc, cal, D, n, ("open", "high", "low", "close"), st)
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
                RO[:, g], RC[:, g], M[:, g] = a["open"][:, j], raw, mult * dm
                self.splits[g] = sorted({int(e[0]) for e in sev[j]})
        if st["late_rows"]:
            raise Exception("S023: history returned data after 2017-12-29")
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
        self.RO, self.RC, self.M = RO, RC, M
        self.st["panel"] = st

    def _row(self, t):
        k = int(np.searchsorted(self.cal, _day(t)))
        if k >= self.cal.size or self.cal[k] != _day(t):
            raise Exception(f"S023: review session {t} not on the SPY calendar")
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
    def _st200(self, elig, k, states=None):
        out = {}
        for s in elig:
            if states is not None:
                x = states(s)
            else:
                x = self.a200[self.col[s]][self.rix[k]] if s in self.col else np.nan
            out[s] = None if not np.isfinite(x) else bool(x)
        return out

    def qr_on_end(self):
        self.st = dict(mode=self.h_mode, checks=self.c, store_stats=dict(self.store.stats), runtime_modules=_module_hashes(),
                       spec_sha256=self.qr_params["spec_sha256"])
        self._build()
        t1 = time.perf_counter()
        reviews = sorted(self.mon)
        rows_k = {t: self._row(t) for t in reviews}
        need = sorted(set(rows_k.values()))
        self.a200 = {}
        for j in range(len(self.sids)):
            cs = P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])["above200"]
            self.a200[j] = cs[need]
        self.rix = {k: i for i, k in enumerate(need)}
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
        # ---- 1. every score first (frozen Score v1; no response price exists yet)
        sid_index = {s: i for i, s in enumerate(self.sids)}
        ff_names = list(XD.FF12_NAMES)
        spot = dict(checked=0, mismatch=0, full_fallbacks=0, examples=[])
        review_out, regimes, pops = [], {}, {}
        self.res_rows = {}
        cov = dict(mcap_missing=0, mom_missing=0)
        t2 = time.perf_counter()
        for t in reviews:
            k = rows_k[t]
            elig = self.mon[t]
            st200 = self._st200(elig, k)
            cache = {}

            def tech(s, k=k, cache=cache):
                if s not in cache:
                    j = self.col[s]
                    cache[s] = E.tech_at(self.C[:, j], self.P[:, j], k, self.unv.get(j, ()), self.dist.get(j, ()))
                    spot["full_fallbacks"] += int(cache[s][4])
                return cache[s]
            res = E.score_review(elig, st200, tech, XD.ff12)
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
            review_out.append([str(t), _ds(self.cal[k]), E.encode_rows(res["rows"], sid_index, adv, ffo, ff_names)])
            regimes[t] = S.regime(S.spy_trend(self.spy_c, k), res["breadth"][0])
            self.res_rows[t] = res["rows"]
            pop = {}
            for s, (bits, tot, pts) in res["rows"].items():
                if E.eligible_flag(bits, tot):
                    mom = tech(s)[0]["mom_12_1"]
                    mc = elig[s].get("mcap")
                    cov["mcap_missing"] += int(not (mc is not None and mc > 0))
                    cov["mom_missing"] += int(mom is None)
                    pop[s] = (int(tot), ffo[s], float("nan") if mom is None else float(mom),
                              math.log(mc) if mc is not None and mc > 0 else float("nan"))
            pops[t] = pop
        self.st["score_s"] = round(time.perf_counter() - t2, 1)
        self.st["slice_spot_check"] = spot
        self.st["score_tables_sha256"] = _sha(json.dumps(review_out, sort_keys=True, separators=(",", ":")))
        self.st["review_sha256"] = [[x[0], _sha(x[2])] for x in review_out]
        self.st["sids_sha256"] = _sha(json.dumps(self.sids, separators=(",", ":")))
        self.st["regimes"] = [[str(t), regimes[t]] for t in reviews]
        dec = reviews[:-1]
        self.st["decisions"] = dict(n=len(dec), first=str(dec[0]), last=str(dec[-1]), last_response_end=str(reviews[-1]))
        if (str(dec[0]), str(dec[-1]), len(dec)) != DECISIONS or int(self.cal[rows_k[reviews[-1]]]) != int(LAST_SESSION):
            raise Exception(f"S023: decisions {self.st['decisions']} differ from the frozen {DECISIONS}")
        # ---- 2. responses, only after every score is final
        t3 = time.perf_counter()
        dates, status = self._responses(reviews, rows_k, pops, regimes)
        self.st["responses_s"] = round(time.perf_counter() - t3, 1)
        cov.update(status=status, population=[[d["day"], len(d["ids"]), int((d["S"] >= R.ENTRY).sum())] for d in dates])
        self.st["coverage"] = cov
        self.st["score_side_sha256"] = self._digest(dates, ("S", "sector", "mom", "size"))
        self.st["response_side_sha256"] = self._digest(dates, ("y", "y2", "y3"))
        self.st["panel_sha256"] = self._digest(dates, ("S", "sector", "mom", "size", "y", "y2", "y3"))
        self.h_dates = dates
        if self.h_mode == "canary":
            self._canary(dates, reviews, rows_k)
        elif self.h_mode == "null":
            self._null(dates)
        else:
            self._real(dates)
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        text = json.dumps(self.st, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRP7S|{i // 9000}|{text[i:i + 9000]}")

    def _responses(self, reviews, rows_k, pops, regimes):
        """Population of each decision (sorted ids) with the responses for 1 (primary), 2 and 3 reviews ahead
        (qr_p7_pred.response on RAW open / close x the panel multiplier); status counts of the primary horizon by year
        and population score quintile."""
        dates, status = [], {}
        nrev = len(reviews)
        for i, t in enumerate(reviews[:-1]):
            k = rows_k[t]
            ids = sorted(pops[t])
            Sv = np.array([pops[t][s][0] for s in ids], float)
            Q = R.quintile_labels(Sv) if ids else np.zeros(0, int)
            ys = {}
            for h in HORIZONS:
                y = np.full(len(ids), np.nan)
                if i + h < nrev:
                    kn = rows_k[reviews[i + h]]
                    for n, s in enumerate(ids):
                        j = self.col[s]
                        v, stt = R.response(self.RO[:, j], self.RC[:, j], self.M[:, j], k, kn, self.unv.get(j, ()))
                        y[n] = v
                        if h == 1:
                            add(status, f"{t.year}|{int(Q[n])}|{stt}")
                ys[h] = y
            dates.append(dict(ids=ids, S=Sv, sector=np.array([pops[t][s][1] for s in ids]),
                              mom=np.array([pops[t][s][2] for s in ids], float),
                              size=np.array([pops[t][s][3] for s in ids], float),
                              y=ys[1], y2=ys[2], y3=ys[3], year=t.year, regime=regimes[t], day=str(t)))
        return dates, status

    @staticmethod
    def _digest(dates, keys):
        h = hashlib.sha256()
        for d in dates:
            rec = [d["day"], d["ids"], d["regime"]] + [np.asarray(d[k]).tolist() for k in keys]
            h.update(json.dumps(rec, separators=(",", ":")).encode())
        return h.hexdigest()

    @staticmethod
    def _world_digest(w):
        return _sha(json.dumps({k: v for k, v in w.items() if not k.startswith("_")}, sort_keys=True, default=str))

    # ------------------------------------------------------------------------------------------------ null / real
    NULL_FIELDS = ("seed", "t_ic", "ic_mean", "ic_se", "hi_ann", "hi_months", "hi_n_mean", "mono", "q5_minus_q1_ann",
                   "half1", "half2", "block_max", "t_inc", "inc_mean", "t_ic_sector")

    def _null(self, dates):
        t0 = time.perf_counter()
        prep = R.prepare(dates)
        rows = []
        for seed in self.h_seeds:
            w = R.run_world(prep, seed=seed)
            rows.append([seed, w["t_ic"], w["ic_mean"], w["ic_se"], w["hi_ann"], w["hi_months"], w["hi_n_mean"],
                         w["mono"], w["q5_minus_q1_ann"], w["halves"][0], w["halves"][1], w["block_max"], w["t_inc"],
                         w["inc_mean"], w["t_ic_sector"]])
        blob = E.pack(json.dumps(dict(fields=list(self.NULL_FIELDS), worlds=rows), separators=(",", ":")))
        self.st["null"] = dict(seeds=[self.h_seeds[0], self.h_seeds[-1]], worlds=len(rows), dates=len(prep),
                               world_s=round(time.perf_counter() - t0, 1), blob_sha256=_sha(blob), blob_chars=len(blob))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"QRN|{i // 9000}|{blob[i:i + 9000]}")

    def _real(self, dates):
        p = self.qr_params
        self.st["provenance"] = {k: p[k] for k in PROVENANCE}
        if self.st["panel_sha256"] != p["panel_sha256"]:
            raise Exception("S023: the prepared panel differs from the one the null was calibrated on; nothing computed")
        t0 = time.perf_counter()
        c_ic = float(p["c_ic"])
        prep = R.prepare(dates)
        days = [d["day"] for d in dates if np.isfinite(d["y"]).sum() >= R.MIN_STOCKS]
        s = R.run_world(prep, keep_series=True)                         # the primary result first
        gates = R.promotion(s, c_ic)
        flags = R.diagnostics_flags(s)
        series = [dict(day=dy, n=len(pp["ids"]), ic=x["ic"], ic_sector=x["ic_sector"], inc=x["inc"], q=x["q"],
                       n_hi=x["n_hi"], hi=x["hi"], regime=pp["regime"])
                  for dy, pp, x in zip(days, prep, s["_series"])]
        out = dict(summary={k: v for k, v in s.items() if not k.startswith("_")}, gates=gates, flags=flags, c_ic=c_ic,
                   series=series)
        # NON-GATING diagnostic horizons (2 and 3 reviews ahead; overlapping; Newey-West lag h), after the primary
        for h, key in ((2, "y2"), (3, "y3")):
            sh = R.run_world(R.prepare(dates, key), lag=h)
            out[f"h{h}"] = {k: v for k, v in sh.items() if not k.startswith("_")}
        blob = E.pack(json.dumps(out, sort_keys=True, separators=(",", ":")))
        self.st["real"] = dict(decisions=len(prep), world_s=round(time.perf_counter() - t0, 1), blob_sha256=_sha(blob),
                               blob_chars=len(blob))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"QRR|{i // 9000}|{blob[i:i + 9000]}")

    # ------------------------------------------------------------------------------------------------ canary
    # Plumbing and integrity only: NO IC of the real assignment, NO gate, NO null statistic of real responses.
    def _fresh_response(self, sym, k, kn):
        """Independent path: a fresh RAW history request for ONE security over (t, t'] and its split / dividend events,
        applied directly as share counts (no multiplier arrays, no SCALED_RAW verification). (value, status)."""
        d0 = datetime.utcfromtimestamp(int(self.cal[k]) * 86400)
        d1 = datetime.utcfromtimestamp(int(self.cal[kn]) * 86400) + timedelta(days=1)
        h = self.history([sym], d0, d1, Resolution.DAILY, fill_forward=False,
                         data_normalization_mode=DataNormalizationMode.RAW)
        if h is None or h.empty:
            return 0.0, "no_bar_after_t"
        dd = XP.session_days(h.index.get_level_values(-1).values)
        keep = (dd > int(self.cal[k])) & (dd <= int(self.cal[kn]))
        dd = dd[keep]
        o, c = (h[x].to_numpy(dtype=float)[keep] for x in ("open", "close"))
        ok = np.isfinite(o) & (o > 0) & np.isfinite(c) & (c > 0)
        if not ok.any():
            return 0.0, "no_bar_after_t"
        e = int(np.argmax(ok))
        x = e + int(np.flatnonzero(np.isfinite(c[e:]) & (c[e:] > 0))[-1])
        de, dx = int(dd[e]), int(dd[x])
        shares = 1.0
        sp = self.history(Split, [sym], d0, d1)
        if sp is not None and not sp.empty and {"type", "referenceprice", "splitfactor"} <= set(sp.columns):
            ed = XP.event_days(sp.index.get_level_values(-1).values)
            for ev, typ, ref, f in zip(ed, sp["type"].tolist(), sp["referenceprice"].tolist(), sp["splitfactor"].tolist()):
                if de < ev <= dx and ("OCCUR" in str(typ).upper() or float(ref) > 0):
                    shares /= float(f)
        dv = self.history(Dividend, [sym], d0, d1)
        if dv is not None and not dv.empty and {"distribution", "referenceprice"} <= set(dv.columns):
            ed = XP.event_days(dv.index.get_level_values(-1).values)
            for ev, amt, ref in zip(ed, dv["distribution"].tolist(), dv["referenceprice"].tolist()):
                if de < ev <= dx and float(ref) > 0 and 0 < float(amt) < float(ref):
                    shares /= 1.0 - float(amt) / float(ref)
        return shares * c[x] / o[e] - 1.0, ("ok" if dx == int(self.cal[kn]) else "truncated")

    def _canary(self, dates, reviews, rows_k):
        ck = dict(real_ic_computed=False, gates_computed=False)
        t0 = time.perf_counter()
        nrev = len(reviews)
        # 1. response timing + independent recomputation of EVERY response (all horizons) from the panel rows
        tm = dict(rows=0, entry_not_after_t=0, entry_on_or_before_t_day=0, exit_outside=0, value_mismatch=0,
                  status_mismatch=0, unverified=0, no_bar=0, truncated=0, response_end_after_last_session=0)
        cls = dict(split=[], dividend=[], truncated=[], plain=[])
        for i, d in enumerate(dates):
            k = rows_k[reviews[i]]
            for h, key in zip(HORIZONS, ("y", "y2", "y3")):
                if i + h >= nrev:
                    continue
                kn = rows_k[reviews[i + h]]
                tm["response_end_after_last_session"] += int(int(self.cal[kn]) > int(LAST_SESSION))
                for n, s in enumerate(d["ids"]):
                    j = self.col[s]
                    tm["rows"] += 1
                    v = d[key][n]
                    O, Cc, m = self.RO[:, j], self.RC[:, j], self.M[:, j]
                    if any(k < u <= kn for u in self.unv.get(j, ())):
                        tm["unverified"] += 1
                        tm["value_mismatch"] += int(not np.isnan(v))
                        continue
                    okb = [r for r in range(k + 1, kn + 1) if np.isfinite(O[r]) and O[r] > 0
                           and np.isfinite(Cc[r]) and Cc[r] > 0]
                    if not okb:
                        tm["no_bar"] += 1
                        tm["value_mismatch"] += int(v != 0.0)
                        continue
                    e = okb[0]
                    x = [r for r in range(e, kn + 1) if np.isfinite(Cc[r]) and Cc[r] > 0][-1]
                    tm["entry_not_after_t"] += int(not k < e <= kn)
                    tm["entry_on_or_before_t_day"] += int(int(self.cal[e]) <= int(self.cal[k]))
                    tm["exit_outside"] += int(not e <= x <= kn)
                    tm["value_mismatch"] += int(v != (Cc[x] * m[x]) / (O[e] * m[e]) - 1.0)
                    stt = "ok" if x == kn else "truncated"
                    tm["truncated"] += int(stt == "truncated")
                    if h == 1:
                        tm["status_mismatch"] += int(R.response(O, Cc, m, k, kn, self.unv.get(j, ()))[1] != stt)
                        tag = f"{s}|{d['day']}"
                        if any(k < r <= kn for r in self.splits.get(j, ())):
                            cls["split"].append(tag)
                        elif any(k < r <= kn for r, _ in self.dist.get(j, ())):
                            cls["dividend"].append(tag)
                        elif stt == "truncated":
                            cls["truncated"].append(tag)
                        else:
                            cls["plain"].append(tag)
        ck["timing"] = tm
        ck["event_classes"] = {c_: len(v) for c_, v in cls.items()}
        # 2. corporate-action accounting: fresh single-security history on a deterministic sample per class
        day_i = {d["day"]: i for i, d in enumerate(dates)}
        fr = dict(checked=0, agree_1e9=0, agree_1e6=0, status_agree=0, worst_rel=0.0, by_class={}, examples=[])
        for c_, tags in cls.items():
            got = dict(n=0, agree_1e9=0, worst_rel=0.0)
            for tag in P.pick(sorted(tags), CANARY_FRESH, f"{CANARY_SALT}|fresh|{c_}"):
                s, dy = tag.split("|")
                i = day_i[dy]
                k, kn = rows_k[reviews[i]], rows_k[reviews[i + 1]]
                v = dates[i]["y"][dates[i]["ids"].index(s)]
                vf, sf = self._fresh_response(self.sym[s], k, kn)
                j = self.col[s]
                st_panel = R.response(self.RO[:, j], self.RC[:, j], self.M[:, j], k, kn, self.unv.get(j, ()))[1]
                rel = abs((1.0 + vf) / (1.0 + v) - 1.0) if (1.0 + v) > 0 else float("inf")
                fr["checked"] += 1
                got["n"] += 1
                fr["agree_1e9"] += int(rel <= 1e-9)
                got["agree_1e9"] += int(rel <= 1e-9)
                fr["agree_1e6"] += int(rel <= 1e-6)
                fr["status_agree"] += int(sf == st_panel)
                fr["worst_rel"] = max(fr["worst_rel"], rel)
                got["worst_rel"] = max(got["worst_rel"], rel)
                if (rel > 1e-9 or sf != st_panel) and len(fr["examples"]) < 15:
                    fr["examples"].append([c_, s, dy, float(f"{rel:.3g}"), sf, st_panel,
                                           [_ds(self.cal[r]) for r in self.splits.get(j, ()) if k < r <= kn]])
            fr["by_class"][c_] = got
        ck["fresh_recomputation"] = fr
        # 3. response invariance: prices after t' (future), at or before t (incl. the close of t), truncation at t'
        inv = dict(checked=0, future_changed=0, past_changed=0, truncation_changed=0)
        allt = sorted(f"{s}|{d['day']}" for d in dates for s, v in zip(d["ids"], d["y"]) if np.isfinite(v))
        for tag in P.pick(allt, CANARY_PERTURB, f"{CANARY_SALT}|invariance"):
            s, dy = tag.split("|")
            i = day_i[dy]
            k, kn = rows_k[reviews[i]], rows_k[reviews[i + 1]]
            j = self.col[s]
            O, Cc, m, u = self.RO[:, j].copy(), self.RC[:, j].copy(), self.M[:, j].copy(), self.unv.get(j, ())
            base = R.response(O, Cc, m, k, kn, u)
            O2, C2, m2 = O.copy(), Cc.copy(), m.copy()
            O2[kn + 1:] *= 3.0
            C2[kn + 1:] = np.nan
            m2[kn + 1:] *= 0.5
            O3, C3, m3 = O.copy(), Cc.copy(), m.copy()
            O3[:k + 1] *= 0.3
            C3[:k + 1] *= 7.0
            m3[:k + 1] *= 0.5
            inv["checked"] += 1
            inv["future_changed"] += int(R.response(O2, C2, m2, k, kn, u) != base)
            inv["past_changed"] += int(R.response(O3, C3, m3, k, kn, u) != base)
            inv["truncation_changed"] += int(R.response(O[:kn + 1], Cc[:kn + 1], m[:kn + 1], k, kn, u) != base)
        ck["response_invariance"] = inv
        # 4. score truncation / future invariance: whole reviews re-scored from price histories cut at t, and with every
        #    price after t perturbed (breadth states, technical inputs, contamination, regime) -> identical score rows
        sc = dict(reviews=[], rows=0, truncated_mismatch=0, future_mismatch=0, regime_mismatch=0)
        for t in P.pick([str(x) for x in reviews[:-1]], CANARY_SCORE_REVIEWS, f"{CANARY_SALT}|score"):
            t = date.fromisoformat(t)
            k = rows_k[t]
            elig = self.mon[t]
            sc["reviews"].append(str(t))
            for variant in ("truncated", "future"):
                cols = {}

                def col(s, k=k, variant=variant, cols=cols):
                    if s not in cols:
                        j = self.col[s]
                        a = [self.C[:, j].copy(), self.P[:, j].copy(), self.H[:, j].copy(), self.L[:, j].copy()]
                        if variant == "truncated":
                            a = [x[:k + 1] for x in a]
                            ev = ([u for u in self.unv.get(j, ()) if u <= k], [x for x in self.dist.get(j, ()) if x[0] <= k])
                        else:
                            a[0][k + 1:] *= 5.0
                            a[1][k + 1:] *= 0.2
                            a[2][k + 1:] *= 5.0
                            a[3][k + 1:] *= 5.0
                            ev = (self.unv.get(j, ()), self.dist.get(j, ()))
                        cols[s] = (a, ev)
                    return cols[s]

                def states(s, k=k, col=col):
                    if s not in self.col:
                        return np.nan
                    a, _ = col(s)
                    return P.calendar_states(a[0], a[2], a[3])["above200"][k]

                def tech2(s, k=k, col=col):
                    a, ev = col(s)
                    return E.tech_at(a[0], a[1], k, ev[0], ev[1])
                res2 = E.score_review(elig, self._st200(elig, k, states), tech2, XD.ff12)
                same = res2["rows"] == self.res_rows[t]
                sc["rows"] += len(res2["rows"]) if variant == "truncated" else 0
                sc[f"{variant}_mismatch"] += int(not same)
                spy = self.spy_c[:k + 1] if variant == "truncated" else np.r_[self.spy_c[:k + 1], self.spy_c[k + 1:] * 3.0]
                sc["regime_mismatch"] += int(S.regime(S.spy_trend(spy, k), res2["breadth"][0]) != self.st_regime(t))
        ck["score_invariance"] = sc
        # 5. determinism: every response recomputed -> identical response-side digest
        again, _ = self._responses(reviews, rows_k, {t: {s: (0, "", 0.0, 0.0) for s in d["ids"]}
                                                     for t, d in zip(reviews, dates)}, {t: d["regime"] for t, d in zip(reviews, dates)})
        ck["responses_repeat_identical"] = all(
            np.array_equal(a[key], b[key], equal_nan=True) for a, b in zip(dates, again) for key in ("y", "y2", "y3"))
        # 6. null machinery on SYNTHETIC responses only (timing, determinism, permutation structure; no statistic exported)
        rng = np.random.default_rng(990001)
        synth = [dict(d, y=rng.standard_t(5, len(d["ids"])) * 0.07) for d in dates]
        prep = R.prepare(synth)
        t1 = time.perf_counter()
        dg = [self._world_digest(R.run_world(prep, seed=900001 + i)) for i in range(TIMING_WORLDS)]
        ws = (time.perf_counter() - t1) / TIMING_WORLDS
        T = R.Tether(900001)
        perm = dict(dates=0, not_permutation=0, self_matches=0, kept=0, receivers=0)
        prev = None
        for pp in prep:
            part = T.step(pp["ids"])
            perm["dates"] += 1
            perm["not_permutation"] += int(sorted(part) != sorted(pp["ids"]))
            perm["self_matches"] += sum(1 for a, b in zip(pp["ids"], part) if a == b)
            if prev is not None:
                perm["kept"] += sum(1 for a, b in zip(pp["ids"], part) if prev.get(a) == b)
                perm["receivers"] += len(part)
            prev = dict(zip(pp["ids"], part))
        ck["null_machinery"] = dict(world_s=round(ws, 4), world_s_1000=round(ws * 1000, 1),
                                    repeat_identical=self._world_digest(R.run_world(prep, seed=900001)) == dg[0],
                                    distinct_worlds=len(set(dg)), tether=perm, synthetic_responses=True)
        ck["canary_s"] = round(time.perf_counter() - t0, 1)
        self.st["canary"] = ck

    def st_regime(self, t):
        return dict(self.st["regimes"])[str(t)]
