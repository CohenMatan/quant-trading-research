# S024 v1.0 — H022 ON FROZEN DATA INFRASTRUCTURE v2 (owner D194: canary + 5,000 null worlds + new c_IC only; the one
# real evaluation is NOT authorised). X999 = a byte copy run as the plumbing canary. NO orders, NO portfolio, NO
# performance; nothing after 2017-12-31 is requested (the last price row is the 2017-12-29 session).
# Data: the FROZEN Data Infrastructure v2 host X998 (manifest cf833f6f..., D192/D193) imported unchanged as qr_x998 (a
# byte copy of strategies/X998_data_v2_export/main.py; its imports qr_v2 / qr_data_v2 / qr_p7_mech / qr_sec_corrections
# / qr_industry / qr_fundamentals are uploaded by the runner): Data v2 universe (QuantConnect market cap if > 0, else the
# D111 SEC market cap), M2 timing, verified identity, restatement guard, store-wide revenue baseline, frozen Score v1.
# (H022's panel digest is _h_digest: X998's own _digest is its ledger digest.) This subclass only ADDS what H022 (research/phase7/P7_predictive_spec.md, frozen; qr_p7_pred unchanged) needs:
#   - the market cap of every reviewed security (QuantConnect's at the review; the SEC market cap for repaired ones);
#   - the panel's RAW open and the split x dividend multiplier (X998 panel construction, same arrays otherwise);
#   - the population, responses, canary, null and real steps, copied VERBATIM from S023 v1.1 (tests compare sources).
# The score side is checked against the frozen E998-01 export (per-review Score v1 / eligibility digests).
# Modes (params.mode): canary = plumbing / integrity only (no IC of the real assignment, no gate, no null statistic of
# real responses); null = worlds params.seeds of the frozen identity-tethered null (refused unless the prepared panel
# equals params.panel_sha256); real = refused unless the pinned Data v2 null provenance is given and the panel matches.
from AlgorithmImports import *
from datetime import date, datetime, timedelta
import hashlib
import json
import math
import time
import numpy as np
import qr_x998 as X98
import qr_p7 as P
import qr_p7_score as S
import qr_p7_export as E
import qr_p7_pred as R
import qr_xs_diag as XD
import qr_xs_panel as XP

HIST_START = datetime(2007, 1, 1)
HIST_END = datetime(2017, 12, 31)
LAST_SESSION = np.datetime64("2017-12-29").astype(np.int64)
REVIEW_FROM = date(2011, 1, 1)
BATCH = 100
SPOT_SALT = "P7CP3-slice-check"
SPOT_PER_REVIEW = 4
PROVENANCE = ("c_ic", "threshold_commit", "null_result_sha256", "spec_sha256", "panel_sha256")
DECISIONS = ("2011-01-31", "2017-11-30", 83)
HORIZONS = (1, 2, 3)                    # reviews ahead: primary 1, diagnostics 2 and 3
CANARY_SALT = "P7CP6-X999"
CANARY_FRESH = 30                       # fresh-history recomputations per event class (split / dividend / truncated / plain)
CANARY_PERTURB = 80                     # stock-dates for the response future / past / truncation invariance checks
CANARY_SCORE_REVIEWS = 6                # reviews re-scored on truncated and future-perturbed price histories
TIMING_WORLDS = 20                      # null machinery timing on SYNTHETIC responses (no real response used)
GATE_WORLDS = 10                        # the full G1-G4 null procedure exercised on SYNTHETIC responses
MODULES = ("qr_p7_pred.py", "qr_p7_score.py", "qr_p7_export.py", "qr_p7.py", "qr_h020_stats.py", "qr_xs.py",
           "qr_xs_panel.py", "qr_fundamentals.py", "qr_x998.py", "qr_v2.py", "qr_data_v2.py")


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


def _nw_t(x, lag):
    """Independent Newey-West (Bartlett) t-statistic: autocovariances from numpy.correlate (canary cross-check)."""
    x = np.asarray(x, float)
    n = x.size
    e = x - x.mean()
    ac = np.correlate(e, e, mode="full")[n - 1:] / n
    s = ac[0] + 2.0 * sum((1.0 - l / (lag + 1.0)) * ac[l] for l in range(1, min(lag, n - 1) + 1))
    return float(x.mean() / math.sqrt(s / n)) if s > 0 else 0.0


class H022DataV2(X98.DataV2Export):

    def qr_initialize(self):
        p = self.qr_params
        self.h_mode = p.get("mode")
        if self.h_mode not in ("canary", "null", "real"):
            raise Exception(f"S024: unknown mode {self.h_mode!r}")
        if "spec_sha256" not in p or "pred_code_sha256" not in p:
            raise Exception("S024: params need spec_sha256 and pred_code_sha256 (frozen fingerprints)")
        if self.h_mode == "null":
            a, b = (int(x) for x in p["seeds"])
            if not (1 <= a <= b <= R.R_NULL):
                raise Exception("S024: null seeds must lie in 1..5000")
            if not p.get("panel_sha256"):
                raise Exception("S024: null runs need the pinned Data v2 panel digest (panel_sha256)")
            self.h_seeds = list(range(a, b + 1))
        if self.h_mode == "real":
            for k in PROVENANCE:
                if p.get(k) in (None, ""):
                    raise Exception(f"S024: real mode needs the pinned null provenance ({k})")
        if self.qr["end"] != "2017-12-31":
            raise Exception("S024: H022 runs end on 2017-12-31")
        self.qr_params = dict(p, mode="export")         # the frozen X998 initialisation (its export mode)
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.h_mcap = {}

    def _month_end(self, t, today, elig, adv, fl):
        super()._month_end(t, today, elig, adv, fl)
        if t >= REVIEW_FROM:
            info = {str(s.id): v[0] for s, v in self.qr_eligible_info.items()}
            self.h_mcap[t] = {sid: info.get(sid) for sid in self.mon[t]}

    def _repair(self):
        super()._repair()
        for t, keep in self.repaired.items():
            for sid in keep:
                r = self.cand[t][sid]
                self.h_mcap[t][sid] = self._secmcap(sid, r["cik_sh"], self.mon_sel[t], r["px"])[0]

    def _build(self):
        """X998's panel (identical C / H / L / P / RAW / unverified splits / distributions) plus the RAW open (RO) and
        the split x dividend multiplier (M) of S023's response construction; RC = RAW close."""
        t0 = time.perf_counter()
        spy = self.history(self.spy, HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        cal = np.unique(XP.session_days(spy.index.get_level_values(-1).values))
        cal = cal[cal <= self.last_session]
        D = cal.size
        sids = sorted({s for rows in self.mon.values() for s in rows})
        N = len(sids)
        st = dict(sessions=D, securities=N, late_rows=0)
        C, Hh, L, Pt, Rw, RO, M = (np.full((D, N), np.nan) for _ in range(7))
        self.unv, self.dist, self.psplit = {}, {}, {}
        # column-keyed split rows (S023 canary classes) ADDED beside X998's security-keyed split history
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
            a = self._cols(hr, loc, cal, D, len(part), ("open", "high", "low", "close"), st)
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
                RO[:, g], M[:, g] = a["open"][:, j], mult * dm
                self.unv[g] = [int(d_[0]) for d_ in det]
                self.dist[g] = [(r_, amt / ref) for r_, amt, ref in de if ref > 0]
                self.psplit[g] = ev
                self.splits[g] = sorted({int(e[0]) for e in sev[j]})
        if st["late_rows"]:
            raise Exception("S024: history returned data after 2017-12-29")
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
        self.RO, self.RC, self.M = RO, Rw, M
        self.st["panel"] = st

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        self.st = dict(self.st0, mode=self.h_mode, checks=self.c, store_stats=dict(self.store.stats),
                       runtime_modules=_module_hashes(), spec_sha256=self.qr_params["spec_sha256"])
        self._repair()
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
        # ---- 1. every score first (frozen Score v1 on frozen Data v2; no response price exists yet)
        spot = dict(checked=0, mismatch=0, full_fallbacks=0, examples=[])
        regimes, pops, sdig, edig = {}, {}, {}, {}
        self.res_rows = {}
        cov = dict(mcap_missing=0, mom_missing=0, repaired_rows=0)
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
                spot["mismatch"] += int(not same)
            sdig[str(t)] = X98.sha(sorted(res["rows"].items()))          # = X998's review_scores digest
            edig[str(t)] = X98.sha(sorted(elig))                         # = X998's review_eligibility digest
            regimes[t] = S.regime(S.spy_trend(self.spy_c, k), res["breadth"][0])
            self.res_rows[t] = res["rows"]
            pop = {}
            for s, (bits, tot, pts) in res["rows"].items():
                if E.eligible_flag(bits, tot):
                    mom = tech(s)[0]["mom_12_1"]
                    mc = self.h_mcap.get(t, {}).get(s)
                    cov["mcap_missing"] += int(not (mc is not None and mc > 0))
                    cov["mom_missing"] += int(mom is None)
                    cov["repaired_rows"] += int(elig[s].get("rep", False))
                    pop[s] = (int(tot), XD.ff12(elig[s]["sic"]), float("nan") if mom is None else float(mom),
                              math.log(mc) if mc is not None and mc > 0 else float("nan"))
            pops[t] = pop
        self.st["score_s"] = round(time.perf_counter() - t2, 1)
        self.st["slice_spot_check"] = spot
        self.st["data_v2_digests"] = dict(review_scores=sdig, review_eligibility=edig)
        self.st["sids_sha256"] = _sha(json.dumps(self.sids, separators=(",", ":")))
        self.st["regimes"] = [[str(t), regimes[t]] for t in reviews]
        self.st["calendar_sha256"] = _sha(json.dumps([str(t) for t in reviews] + [_ds(x) for x in self.cal],
                                                     separators=(",", ":")))
        dec = reviews[:-1]
        self.st["decisions"] = dict(n=len(dec), first=str(dec[0]), last=str(dec[-1]), last_response_end=str(reviews[-1]))
        if (str(dec[0]), str(dec[-1]), len(dec)) != DECISIONS or int(self.cal[rows_k[reviews[-1]]]) != int(LAST_SESSION):
            raise Exception(f"S024: decisions {self.st['decisions']} differ from the frozen {DECISIONS}")
        # ---- 2. responses, only after every score is final
        t3 = time.perf_counter()
        dates, status = self._responses(reviews, rows_k, pops, regimes)
        self.st["responses_s"] = round(time.perf_counter() - t3, 1)
        cov.update(status=status, population=[[d["day"], len(d["ids"]), int((d["S"] >= R.ENTRY).sum())] for d in dates])
        self.st["coverage"] = cov
        self.st["score_side_sha256"] = self._h_digest(dates, ("S", "sector", "mom", "size"))
        self.st["response_side_sha256"] = self._h_digest(dates, ("y", "y2", "y3"))
        self.st["availability_sha256"] = _sha(json.dumps(
            [[d["day"], d["ids"]] + [np.isfinite(np.asarray(d[k])).astype(int).tolist() for k in ("y", "y2", "y3")]
             for d in dates], separators=(",", ":")))
        self.st["panel_sha256"] = self._h_digest(dates, ("S", "sector", "mom", "size", "y", "y2", "y3"))
        self.h_dates = dates
        if self.h_mode == "canary":
            self._canary(dates, reviews, rows_k)
            self._canary_v2(dates)
        elif self.h_mode == "null":
            if self.st["panel_sha256"] != self.qr_params["panel_sha256"]:
                raise Exception("S024: the prepared panel differs from the pinned Data v2 panel; no null world computed")
            self._null(dates)
        else:
            self._real(dates)
        self.st["pit_audit"] = dict(self.audit)          # X998's Data v2 PIT audit counters (all must be 0)
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        text = json.dumps(self.st, sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRP7V|{i // 9000}|{text[i:i + 9000]}")

    def _canary_v2(self, dates):
        """Added checks (SYNTHETIC responses only): an independent Newey-West computation, the complete G1-G4 null
        procedure exercised end to end, and the tether never reproducing the identity (real) assignment."""
        ck = self.st["canary"]
        rng = np.random.default_rng(990002)
        nw = dict(series=0, max_abs_diff=0.0)
        for _ in range(20):
            x = rng.standard_normal(83) * 0.05 + 0.002
            nw["series"] += 1
            nw["max_abs_diff"] = max(nw["max_abs_diff"], abs(R.X.nw_tstat(x, R.NW_LAG)[2] - _nw_t(x, R.NW_LAG)))
        ck["newey_west"] = nw
        synth = [dict(d, y=rng.standard_t(5, len(d["ids"])) * 0.07) for d in dates]
        prep = R.prepare(synth)
        gp = dict(worlds=0, complete=0, gates_evaluated=0, identity_dates=0, fields_finite=0)
        for i in range(GATE_WORLDS):
            seed = 950001 + i
            w = R.run_world(prep, seed=seed)
            g = R.promotion(w, R.CRIT_FLOOR)
            gp["worlds"] += 1
            gp["complete"] += int(w["n_dates"] == len(prep) and len(w["halves"]) == 2 and len(w["q_mean_ann"]) == R.N_Q)
            gp["gates_evaluated"] += int(set(g) == {"G1_significant", "G2_economic", "G3_monotonic", "G4_stable", "pass"})
            gp["fields_finite"] += int(all(np.isfinite(w[k]) for k in ("t_ic", "ic_mean", "mono", "q5_minus_q1_ann")))
            T = R.Tether(seed)
            for pp in prep:
                gp["identity_dates"] += int(list(T.step(pp["ids"])) == list(pp["ids"]))
        ck["gate_procedure"] = gp
        ck["real_ic_computed"] = False
        ck["gates_computed"] = False

    # ------------------------------------------------------------------------------------------------ verbatim S023 v1.1

    def _st200(self, elig, k, states=None):
        out = {}
        for s in elig:
            if states is not None:
                x = states(s)
            else:
                x = self.a200[self.col[s]][self.rix[k]] if s in self.col else np.nan
            out[s] = None if not np.isfinite(x) else bool(x)
        return out

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
    def _h_digest(dates, keys):
        h = hashlib.sha256()
        for d in dates:
            rec = [d["day"], d["ids"], d["regime"]] + [np.asarray(d[k]).tolist() for k in keys]
            h.update(json.dumps(rec, separators=(",", ":")).encode())
        return h.hexdigest()

    @staticmethod
    def _world_digest(w):
        return _sha(json.dumps({k: v for k, v in w.items() if not k.startswith("_")}, sort_keys=True, default=str))

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
