# S031 v1.1 — H029 STANDALONE BUSINESS IMPROVEMENT SCORE + H030 FIXED 50/50 COMBINATION WITH FROZEN H028 (owner D229;
# research/phase14/H029_H030_spec.md, pinned by qresearch.p14h029). NO orders (portfolios are simulated in-host);
# nothing after 2021-12-31 is requested; 2015-2021 = development evidence; the Holdout 2022-01-01 .. 2026-08-31 stays
# sealed. A STANDALONE subclass of the frozen Data v2.1 host X801 only (uploaded byte-identical as qr_x801; no
# S028 -> S029 -> S030 chain). Engineering consolidation only, every scientific calculation frozen:
#   - VERBATIM copies (tests/test_p14_s031_host.py compares the source text) of the frozen S028 / S029 methods that
#     build the H026 months (memory-reduced S029 build, Score v1 population, H024 features, 63-session labels, holding
#     arrays): _repair, _build, _w_scores, _w_features, _w_months, _w_feature_digest, _w_response_digest, _w_emit,
#     _g_free_panel, _g_release_run_state, _g_stage; the S028 month-end additions (market caps, total-assets ledger);
#   - Data v3 (frozen, P14-CP2): the guard-v3 hook on the v2.1 store, the v3 view and the six H029 signals live at each
#     review (the X803 construction), F7 at the end; the per-review H029 panel digests must equal the frozen ones;
#   - the H028 component: lambda-100 fits (qr_h029.fixed_fits = the frozen H028 module arithmetic), checked against the
#     committed coefficients and the committed H028 terminal wealth;
#   - modes: canary (spec 13; NO real H029 / H030 portfolio result), null (worlds params.seeds; real assignment only
#     used for the score-only selection structure), real (the ONE run with the pinned thresholds);
#   - v1.1 (Amendment 1, owner D233, research/phase14/H029_H030_amendment1_sector_null.md): the null tether is
#     stratified by FF12 sector (qr_h029); the canary adds the sector checks. Nothing else changed.
# New attribute / method names carry the prefix y_ / _y_ (X801 / X998 / S028 / S029 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_x801, qr_v3, qr_data_v3,
# qr_h029, qr_h026, qr_h024, qr_h023, qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred, qr_p7_mech, qr_xs, qr_xs_diag,
# qr_xs_panel, qr_v2, qr_data_v21, qr_sec_corrections, qr_industry, qr_fundamentals.
from AlgorithmImports import *
from datetime import date, datetime
import gc
import hashlib
import json
import math
import time
import numpy as np
import qr_x801 as X81
import qr_h026 as H
import qr_h024 as K
import qr_h029 as Q
import qr_v3 as V
import qr_p7 as P
import qr_p7_export as E
import qr_p7_score as S
import qr_xs_diag as XD
import qr_xs_panel as XP
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore
from qr_sec_corrections import SECFiling

Y_LAST = "2021-12-31"
Y_REVIEW_FROM = date(2011, 1, 1)
W_REVIEW_FROM = date(2011, 1, 1)
W_LEDGER_FROM, W_LEDGER_TO = date(2010, 1, 1), date(2021, 1, 1)     # S028: total assets 12 months back
Z = V.Z


def _ds(day):
    return str(np.datetime64(int(day), "D"))


def _day(d):
    return int(np.datetime64(d.strftime("%Y-%m-%d")).astype(np.int64))


class S28:
    """The frozen S028 constants read by the verbatim S029 build."""
    W_BATCH = 100
    W_HIST_START = datetime(2007, 1, 1)
    _day = staticmethod(_day)


def _plain(x):
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, np.ndarray):
        return _plain(x.tolist())
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, (float, np.floating)):
        x = float(x)
        return x if math.isfinite(x) else None
    return x


def _mem_now():
    out = {}
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith(("VmRSS:", "VmHWM:")):
                    k, v = line.split(":", 1)
                    out[k] = round(int(v.split()[0]) / 1024.0, 1)
    except Exception as ex:
        out["error"] = type(ex).__name__
    try:
        import resource
        out["ru_maxrss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    except Exception:
        pass
    return out


def _trim():
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


class _V3Store(PITStore):
    """The v2.1 store, unchanged, plus a notification of every version it queues (the guard-v3 hook; X803)."""

    def __init__(self, host):
        super().__init__(DEFAULT_MAX_AGE_DAYS)
        self.v_host = host

    def observe(self, key, period_end, file_date, values, accession_year_, today):
        pend = self.pending.get(key)
        n0 = len(pend) if pend else 0
        super().observe(key, period_end, file_date, values, accession_year_, today)
        pend = self.pending.get(key)
        if pend and len(pend) > n0:
            self.v_host._v_fed(key, pend[-1], values, today)


class H029H030(X81.DataV2Export):

    def qr_initialize(self):
        p = self.qr_params
        mode = p.get("mode")
        if mode not in ("canary", "null", "real"):
            raise Exception(f"S031: unknown mode {mode!r}")
        for k in ("spec_sha256", "h029_code_sha256", "data_v3_manifest_sha256", "guard_sha256",
                  "h029_panel_digests_sha256", "h026_feature_panel_sha256", "h026_response_panel_sha256",
                  "h028_real_wealth", "lv15_real_wealth", "h028_coefficients"):
            if p.get(k) in (None, ""):
                raise Exception(f"S031: params need {k}")
        if mode == "null":
            a, b = (int(x) for x in p["seeds"])
            if not (1 <= a <= b <= Q.R_NULL):
                raise Exception("S031: null seeds must lie in 1..5000")
            self.y_seeds = list(range(a, b + 1))
        if mode == "real":
            for k in ("c_up_h029", "c_incremental_h030", "null_result_sha256", "threshold_commit"):
                if p.get(k) in (None, ""):
                    raise Exception(f"S031: real mode needs the pinned {k}")
        if self.qr["end"] != Y_LAST:
            raise Exception("S031: runs end on 2021-12-31")
        self.qr_params = dict(p, mode="export")              # the X801 / X998 initialisation (export mode)
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.y_mode = mode
        self.w_mcap, self.w_ta = {}, {}
        self.g_mem = []
        C, self.y_gparts = V.load_parts(V.GUARD_PREFIX, p["guard_sha256"])
        self.g3 = V.Guard3(C)
        del C
        self.store = _V3Store(self)                  # replaces X801's (still empty) PITStore; same rules
        self.ov = V.V3Overlay()
        self.v_rows = {}
        self.v_check = dict(fed=0, fed_no_match=0, blocked=0, view_future_records=0)

    # ------------------------------------------------------------------------------------------------ Data v3 (X803)
    def _v_fed(self, sid, rec, vals, today):
        self.v_check["fed"] += 1
        cik, _src = self.ident.m2(sid, today, self.pres_start.get(sid), self.first_day)
        m = self.ref.match(cik, rec.period_end) if cik is not None else None
        if m is None:
            self.v_check["fed_no_match"] += 1
            self.ov.fed(sid, rec, False, False)
            return
        rows = self.g3.rows(cik, m[0])
        blocked, _cats = self.g3.check(cik, m[0], vals, today)
        self.v_check["blocked"] += int(blocked)
        self.ov.fed(sid, rec, rows is not None, blocked)

    def _month_end(self, t, today, elig, adv, fl):
        super()._month_end(t, today, elig, adv, fl)
        # ---- S028._month_end additions, verbatim ----
        if t >= W_REVIEW_FROM and t in self.mon:
            info = {str(s.id): v[0] for s, v in self.qr_eligible_info.items()}
            self.w_mcap[t] = {sid: info.get(sid) for sid in self.mon[t]}
        if W_LEDGER_FROM <= t < W_LEDGER_TO:
            d = {}
            for sid in sorted(set(self.store.hist) | set(self.store.pending)):
                r = self.store.record(sid, today)
                v = r.values.get("total_assets") if r is not None else None
                if v is not None and math.isfinite(v):
                    d[sid] = float(v)
            self.w_ta[(t.year, t.month)] = d
        # ---- X803 live H029 signals on the v3 view ----
        if t < Y_REVIEW_FROM or t not in self.mon:
            return
        members = sorted(set(self.mon[t]) | set(self.cand.get(t, {})))
        S5 = V.SEC_SIGNALS
        V3m = np.full((len(members), len(S5)), np.nan)
        for i, sid in enumerate(members):
            cur = self.store.record(sid, today)          # promotes reports visible today BEFORE any history is read
            hist = self.store.hist.get(sid, {})
            h3, c3 = self.ov.view(hist, cur, sid, today)
            w3 = Z.Window(h3, c3, today)
            self.v_check["view_future_records"] += w3.viol
            s3 = V.signals(w3)
            for j, f in enumerate(S5):
                a = s3[f][0]
                if a is not None and math.isfinite(a):
                    V3m[i, j] = a
        rc = [(self.mon[t].get(sid) or self.cand[t][sid]).get("cik") for sid in members]
        self.v_rows[t] = dict(pos={s: i for i, s in enumerate(members)}, V=V3m, cik=rc, today=today)

    def _y_f7(self, reviews):
        need = sorted({s for t in reviews for s in self.mon[t] if s not in self.splits})
        if need:
            self.splits.update(self._split_history(need))
        fil, out = {}, {}
        for t in reviews:
            zr = self.v_rows[t]
            today = zr["today"]
            for sid in self.mon[t]:
                i = zr["pos"].get(sid)
                if i is None:
                    continue
                cik = zr["cik"][i]
                if cik is None or cik not in self.ref.shrows:
                    continue
                if cik not in fil:
                    fil[cik] = sorted((SECFiling(x) for x in self.ref.shrows[cik]), key=lambda x: (x.filed, x.accn))
                out[(t, sid)] = V.f7(fil[cik], self.splits.get(sid, ()), today)[0]
        return out

    def _y_panels(self, reviews):
        """The U_H029 six-signal panel of every review (the X803 construction) and its digests (Data v3 spec 12)."""
        f7 = self._y_f7(reviews)
        S6, F7I = V.SIGNALS, V.SIGNALS.index("F7")
        pan, dig = {}, {}
        for t in reviews:
            zr = self.v_rows[t]
            ids = [sid for sid in sorted(self.mon[t]) if self.mon[t][sid].get("sic") is not None
                   and not 6000 <= int(self.mon[t][sid]["sic"]) <= 6999]
            M = np.full((len(ids), len(S6)), np.nan)
            for i, sid in enumerate(ids):
                k = zr["pos"].get(sid)
                if k is not None:
                    for j, f in enumerate(V.SEC_SIGNALS):
                        M[i, S6.index(f)] = zr["V"][k, j]
                v = f7.get((t, sid))
                M[i, F7I] = v if v is not None and math.isfinite(v) else np.nan
            dig[str(t)] = V.panel_digest(ids, M)
            sec = np.array([XD.FF12_NAMES.index(XD.ff12(self.mon[t][s]["sic"])) for s in ids], dtype=np.int64)
            pan[t] = (ids, M, sec)
        return pan, dig

    # ------------------------------------------------------------------------------------------------ frozen S028 / S029
    def _g_stage(self, name):
        self.g_mem.append([name, round(time.perf_counter() - self.t0, 1), _mem_now()])

    def _g_release_run_state(self):
        """The run-time fundamentals store, revenue ledger, first-seen ledger, weekly checks and digest buffers are
        used only while the algorithm runs (month ends / weekly checks); nothing after the run reads them."""
        for a in ("store", "rev", "led", "wk", "dg"):
            if hasattr(self, a):
                setattr(self, a, None)
        _trim()

    def _repair(self):
        super()._repair()
        for t, keep in self.repaired.items():
            for sid in keep:
                r = self.cand[t][sid]
                self.w_mcap.setdefault(t, {})[sid] = self._secmcap(sid, r["cik_sh"], self.mon_sel[t], r["px"])[0]

    def _build(self):
        """X801's panel, then the 200-day state for the review rows (the only use of the high / low matrices), then
        high / low freed BEFORE S028's RAW open (RO), split x dividend multiplier (M) and SPY arrays (S028 code)."""
        X81.DataV2Export._build(self)
        reviews = sorted(self.mon)
        need = sorted({self._row(t) for t in reviews})
        self.a200 = {j: P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])["above200"][need]
                     for j in range(len(self.sids))}
        self.rix = {k: i for i, k in enumerate(need)}
        self.H = self.L = None
        _trim()
        self._g_stage("after_x801_build_hl_freed")
        # ---- S028._build after super()._build(), verbatim ----
        D, N = self.cal.size, len(self.sids)
        RO, M = np.full((D, N), np.nan), np.full((D, N), np.nan)
        st = dict(late_rows=0)
        for i in range(0, N, S28.W_BATCH):
            part = self.sids[i:i + S28.W_BATCH]
            syms = [self.sym[s] for s in part]
            loc = {s: j for j, s in enumerate(part)}
            hr = self.history(syms, S28.W_HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.RAW)
            hs = self.history(syms, S28.W_HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            sp = self.history(Split, syms, S28.W_HIST_START, self.hist_end)
            dv = self.history(Dividend, syms, S28.W_HIST_START, self.hist_end)
            a = self._cols(hr, loc, self.cal, D, len(part), ("open", "close"), st)
            b = self._cols(hs, loc, self.cal, D, len(part), ("close",), st)
            sev = self._events(sp, loc, self.cal, ("type", "referenceprice", "splitfactor"))
            dev = self._events(dv, loc, self.cal, ("distribution", "referenceprice"))
            for j in range(len(part)):
                g, raw, sc = i + j, a["close"][:, j], b["close"][:, j]
                if not np.any(np.isfinite(raw) & (raw > 0)):
                    continue
                vv = np.flatnonzero(np.isfinite(raw) & np.isfinite(sc) & (raw > 0) & (sc > 0))
                if vv.size and abs(sc[vv[-1]] / raw[vv[-1]] - 1.0) > 1e-6:
                    sc = sc / (sc[vv[-1]] / raw[vv[-1]])
                ev = [(r_, float(fac)) for r_, typ, ref, fac in sev[j] if "OCCUR" in str(typ).upper() or float(ref) > 0]
                de = [(r_, float(amt), float(ref)) for r_, amt, ref in dev[j]]
                mult, _ = XP.split_multiplier(raw, sc, ev, detail=[])
                RO[:, g], M[:, g] = a["open"][:, j], mult * XP.dividend_multiplier(D, de)
        if st["late_rows"]:
            raise Exception("S028: history returned data after 2021-12-31")
        self.RO, self.RC, self.M = RO, self.RAW, M
        spy = self.history(self.spy, S28.W_HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        O, C = np.full(D, np.nan), np.full(D, np.nan)
        d = XP.session_days(spy.index.get_level_values(-1).values)
        ok = d <= self.last_session
        r = np.searchsorted(self.cal, d[ok])
        O[r], C[r] = spy["open"].to_numpy(dtype=float)[ok], spy["close"].to_numpy(dtype=float)[ok]
        m = np.ones(D)
        key = {X81._sid(self.spy): 0}
        for r_, typ, ref, f in self._events(self.history(Split, [self.spy], S28.W_HIST_START, self.hist_end), key,
                                            self.cal, ("type", "referenceprice", "splitfactor")).get(0, []):
            if "OCCUR" in str(typ).upper() or float(ref) > 0:
                m[:r_] *= float(f)
        de = [(r_, float(a_), float(rf)) for r_, a_, rf in self._events(
            self.history(Dividend, [self.spy], S28.W_HIST_START, self.hist_end), key, self.cal,
            ("distribution", "referenceprice")).get(0, [])]
        self.w_spy = (O, C, m * XP.dividend_multiplier(D, de))
        self.st["w_spy"] = dict(dividends=len(de), missing_rows_from_2010=int(
            (~(np.isfinite(O) & np.isfinite(C)))[int(np.searchsorted(self.cal, S28._day(date(2010, 1, 4)))):].sum()))

    def _w_scores(self, reviews, rows_k):
        """S028._w_scores verbatim, except that the 200-day state (self.a200 / self.rix, identical arrays) was computed
        in _build before the high / low matrices were freed."""
        self._baselines(reviews, rows_k)
        pops, sdig, edig, regimes, tech_cache = {}, {}, {}, {}, {}
        for t in reviews:
            k = rows_k[t]
            elig = self.mon[t]
            st200 = {}
            for s in elig:
                x = self.a200[self.col[s]][self.rix[k]] if s in self.col else np.nan
                st200[s] = None if not np.isfinite(x) else bool(x)
            cache = {}

            def tech(s, k=k, cache=cache):
                if s not in cache:
                    j = self.col[s]
                    cache[s] = E.tech_at(self.C[:, j], self.P[:, j], k, self.unv.get(j, ()), self.dist.get(j, ()))
                return cache[s]
            res = E.score_review(elig, st200, tech, XD.ff12)
            sdig[str(t)] = X81.sha(sorted(res["rows"].items()))
            edig[str(t)] = X81.sha(sorted(elig))
            regimes[t] = S.regime(S.spy_trend(self.spy_c, k), res["breadth"][0])
            pop = {}
            for s, (bits, tot, pts) in res["rows"].items():
                if E.eligible_flag(bits, tot):
                    mom = tech(s)[0]["mom_12_1"]
                    mc = self.w_mcap.get(t, {}).get(s)
                    pop[s] = (int(tot), XD.ff12(elig[s]["sic"]), float("nan") if mom is None else float(mom),
                              math.log(mc) if mc is not None and mc > 0 else float("nan"))
                    tech_cache[(t, s)] = tech(s)
            pops[t] = pop
        return pops, sdig, edig, regimes, tech_cache

    def _w_features(self, t, k, ids, tech_cache):
        ym = (t.year - 1, t.month)
        ta_prev = self.w_ta.get(ym, {})
        out = []
        for s in ids:
            j = self.col[s]
            ti = tech_cache[(t, s)][0]
            pf = K.price_features(self.C[:, j], self.P[:, j], k, self.unv.get(j, ()), self.dist.get(j, ()))
            ff = K.fund_features(self.mon[t][s]["vals"], ta_prev.get(s), self.w_mcap.get(t, {}).get(s))
            out.append(K.feature_row(ti, pf, ff))
        return np.array(out, float).reshape(-1, len(K.LIBRARY))

    def _w_months(self, reviews, rows_k, pops, raw_by_t):
        """The H026 decision months = every review 2011-01-31 .. 2021-11-30 (spec sections 3-4, 7)."""
        O, C, m = self.w_spy
        last_row = int(self.cal.size - 1)
        months, cov = [], {}
        for i, t in enumerate(reviews):
            k = rows_k[t]
            e = k + 1
            if i + 1 < len(reviews):                       # held to the next review's close, rebalanced at its next open
                end = rows_k[reviews[i + 1]]
                nxt = end + 1
            else:                                          # the 2021-11-30 decision: held to the 2021-12-31 close
                end, nxt = last_row, None
            ids_all = sorted(pops[t])
            Xr = raw_by_t[t]
            ok = np.all(np.isfinite(Xr), axis=1)
            c = cov.setdefault(str(t.year), [0, 0])
            c[0] += len(ids_all)
            c[1] += int(ok.sum())
            ids = [s for s, o in zip(ids_all, ok) if o]
            Xraw = Xr[ok]
            X = H.feature_matrix(Xraw) if len(ids) else np.zeros((0, len(H.FEATURES)))
            x0 = e + H.HORIZON - 1
            exc = np.full(len(ids), np.nan)
            if x0 <= last_row:
                for n, s in enumerate(ids):
                    j = self.col[s]
                    v, st_, ee, xx = H.tsr(self.RO[:, j], self.RC[:, j], self.M[:, j], e, x0, self.unv.get(j, ()))
                    if np.isfinite(v):
                        exc[n] = v - ((C[x0] * m[x0]) / (O[ee] * m[ee]) - 1.0)
            label = H.centred_percentile(exc)
            hold = [H.holding(self.RO[:, self.col[s]], self.RC[:, self.col[s]], self.M[:, self.col[s]], e, nxt, end,
                              self.unv.get(self.col[s], ())) for s in ids]
            nday = end - e + 1
            sb = O[e] * m[e]
            spy_tr = C[e:end + 1] * m[e:end + 1] / sb - 1.0
            months.append(dict(
                day=str(t), ids=ids, sector=np.array([XD.FF12_NAMES.index(pops[t][s][1]) for s in ids], dtype=np.int64),
                X=X, raw=Xraw, label=label, exc=exc,
                exit_day=float(self.cal[x0]) if x0 <= last_row else float("inf"), cutoff_day=float(self.cal[k]),
                test_year=int(_ds(self.cal[e])[:4]), open_ok=np.array([h[0] for h in hold], bool),
                r_oo=np.array([h[1] for h in hold], float), alive_next=np.array([h[2] for h in hold], bool),
                r_oc=np.array([h[3] for h in hold], float), alive_end=np.array([h[4] for h in hold], bool),
                daily=np.column_stack([h[5] for h in hold]) if hold else np.zeros((nday, 0)),
                spy_oo=float(O[nxt] * m[nxt] / sb - 1.0) if nxt is not None else float(spy_tr[-1]),
                spy_oc=float(spy_tr[-1]), spy_daily=spy_tr, days=self.cal[e:end + 1].astype(np.int64),
                k=k))
        return months, cov

    @staticmethod
    def _w_feature_digest(months):
        h = hashlib.sha256()
        for mo in months:
            h.update(json.dumps([mo["day"], mo["ids"], mo["sector"].tolist(), mo["X"].round(12).tolist()],
                                separators=(",", ":")).encode())
        return h.hexdigest()

    @staticmethod
    def _w_response_digest(months):
        h = hashlib.sha256()
        for mo in months:
            h.update(json.dumps([mo["day"], _plain(mo["label"]), _plain(mo["r_oo"]), _plain(mo["r_oc"]),
                                 mo["open_ok"].tolist(), mo["alive_next"].tolist(), mo["alive_end"].tolist(),
                                 _plain(np.round(mo["daily"], 12)), _plain(mo["spy_oo"]), _plain(mo["spy_oc"])],
                                separators=(",", ":")).encode())
        return h.hexdigest()

    def _w_emit(self, tag, obj):
        blob = E.pack(json.dumps(_plain(obj), sort_keys=True, separators=(",", ":")))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"{tag}|{i // 9000}|{blob[i:i + 9000]}")
        return dict(blob_sha256=hashlib.sha256(blob.encode()).hexdigest(), blob_chars=len(blob))

    def _g_free_panel(self):
        for a in ("C", "P", "RAW", "RO", "RC", "M", "a200", "mon", "cand", "val", "w_ta"):
            if hasattr(self, a):
                setattr(self, a, None)
        _trim()

    # ------------------------------------------------------------------------------------------------ H029 / H030 months
    def _y_h029_months(self, months, pan, rows_k, reviews):
        """The H029 evaluation months: E29(t) (H029 score, >= 5 of 6) with the frozen qr_h026.holding arrays on the same
        entry / exit rows as the H026 month of the same review; SPY / calendar fields copied from it."""
        idx = Q.outer_index(months)
        byday = {str(t): t for t in reviews}
        last_row = int(self.cal.size - 1)
        out, V29, miss = [], [], 0
        for i in idx:
            mo = months[i]
            t = byday[mo["day"]]
            j = reviews.index(t)
            k = rows_k[t]
            e = k + 1
            if j + 1 < len(reviews):
                end = rows_k[reviews[j + 1]]
                nxt = end + 1
            else:
                end, nxt = last_row, None
            ids, M, sec = pan[t]
            sc, cnt = V.h029_score(M)
            ok = np.isfinite(sc) & np.array([s in self.col for s in ids], bool)
            miss += int((np.isfinite(sc) & ~ok).sum())
            keep = np.flatnonzero(ok)
            kid = [ids[q] for q in keep]
            hold = [H.holding(self.RO[:, self.col[s]], self.RC[:, self.col[s]], self.M[:, self.col[s]], e, nxt, end,
                              self.unv.get(self.col[s], ())) for s in kid]
            nday = end - e + 1
            out.append(dict(day=mo["day"], ids=kid, sector=sec[keep], test_year=mo["test_year"],
                            cutoff_day=mo["cutoff_day"], k=k,
                            open_ok=np.array([h[0] for h in hold], bool), r_oo=np.array([h[1] for h in hold], float),
                            alive_next=np.array([h[2] for h in hold], bool), r_oc=np.array([h[3] for h in hold], float),
                            alive_end=np.array([h[4] for h in hold], bool),
                            daily=np.column_stack([h[5] for h in hold]) if hold else np.zeros((nday, 0)),
                            spy_oo=mo["spy_oo"], spy_oc=mo["spy_oc"], spy_daily=mo["spy_daily"], days=mo["days"]))
            V29.append(M[keep])
        self.st["h029_months"] = dict(months=len(out), scored_without_panel_column=miss,
                                      eligible=[len(m["ids"]) for m in out])
        return out, V29

    def _y_setup(self, months, m29):
        """H028 (frozen lambda-100 path), its reproduction checks, SPY, LV15 and the joint H030 months."""
        p = self.qr_params
        Xs = [m["X"] for m in months]
        fits = Q.fixed_fits(months, Xs)
        com = p["h028_coefficients"]
        dmax = 0.0
        for Y in Q.OUTER:
            c = com[str(Y)]
            dmax = max(dmax, abs(fits[Y][0] - float(c["b0"])),
                       float(np.max(np.abs(fits[Y][1] - np.asarray(c["beta"], float)))))
        idx = Q.outer_index(months)
        m28 = [months[i] for i in idx]
        sc28 = Q.h028_scores(months, Xs, fits)
        days = np.concatenate([m["days"] for m in m28])
        spy = Q.spy_path(m28, days)
        e28 = Q.evaluate(m28, sc28, spy, days)
        lv = Q.evaluate(m28, Q.lv15_scores(m28), spy, days)
        rep = dict(coef_max_abs_diff=dmax, h028_wealth=e28["wealth"], expected_h028=float(p["h028_real_wealth"]),
                   lv15_wealth=lv["wealth"], expected_lv15=float(p["lv15_real_wealth"]))
        rep["ok"] = bool(dmax <= 1e-12 and abs(rep["h028_wealth"] / rep["expected_h028"] - 1.0) <= 1e-9
                         and abs(rep["lv15_wealth"] / rep["expected_lv15"] - 1.0) <= 1e-9)
        if [m["day"] for m in m28] != [m["day"] for m in m29]:
            raise Exception("S031: the H029 and H028 evaluation months differ")
        m30, sc28j, j29 = [], [], []
        for a, b, s in zip(m28, m29, sc28):
            ids, p28, p29 = Q.joint(a["ids"], b["ids"])
            m30.append(Q.sub_month(a, p28, ids))
            sc28j.append(s[p28])
            j29.append(p29)
        return dict(fits=fits, m28=m28, sc28=sc28, days=days, spy=spy, e28=e28, lv=lv, m30=m30, sc28j=sc28j, j29=j29,
                    rep=rep)

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        p = self.qr_params
        self.st = dict(self.st0, mode=self.y_mode, hypothesis="H029 / H030", checks=self.c,
                       store_stats=dict(self.store.stats), spec_sha256=p["spec_sha256"])
        self.st["v3"] = dict(self.v_check, overlay=dict(self.ov.check), overlay_blocked=len(self.ov.blocked))
        self._g_stage("on_end_start")
        self._g_release_run_state()
        self.ov = None
        _trim()
        self._repair()
        reviews = sorted(self.mon)
        if str(reviews[-1]) != "2021-11-30" or str(reviews[0])[:7] != "2011-01" or len(reviews) != 131:
            raise Exception(f"S031: reviews {reviews[0]} .. {reviews[-1]} differ from 2011-01 .. 2021-11 (131)")
        pan, dig = self._y_panels(reviews)
        self.v_rows = None
        _trim()
        self.st["h029_panel_digests_sha256"] = hashlib.sha256(json.dumps(dig, sort_keys=True).encode()).hexdigest()
        panel_ok = self.st["h029_panel_digests_sha256"] == p["h029_panel_digests_sha256"]
        self.st["h029_panel_equal"] = panel_ok
        self._g_stage("after_h029_panels")
        self._build()
        self._g_stage("after_build")
        rows_k = {t: self._row(t) for t in reviews}
        pops, sdig, edig, regimes, tech_cache = self._w_scores(reviews, rows_k)
        raw_by_t = {t: self._w_features(t, rows_k[t], sorted(pops[t]), tech_cache) for t in reviews}
        months, cov = self._w_months(reviews, rows_k, pops, raw_by_t)
        self.st["data_v21_digests"] = dict(review_eligibility=edig)
        self.st["feature_panel_sha256"] = self._w_feature_digest(months)
        self.st["response_panel_sha256"] = self._w_response_digest(months)
        eq = dict(feature_panel=self.st["feature_panel_sha256"] == p["h026_feature_panel_sha256"],
                  response_panel=self.st["response_panel_sha256"] == p["h026_response_panel_sha256"],
                  h029_panel=panel_ok)
        self.st["equivalence"] = eq
        m29, V29 = self._y_h029_months(months, pan, rows_k, reviews)
        del tech_cache, raw_by_t, pops, pan
        self._g_free_panel()
        self._g_stage("after_months_panel_freed")
        if self.y_mode != "canary" and not all(eq.values()):
            raise Exception("S031: a panel differs from its pinned digest; nothing computed")
        su = self._y_setup(months, m29)
        self.st["h028_reproduction"] = su["rep"]
        if self.y_mode != "canary" and not su["rep"]["ok"]:
            raise Exception("S031: frozen H028 / LV15 not reproduced; nothing computed")
        self._g_stage("after_setup")
        if self.y_mode == "canary":
            self._y_canary(months, m29, V29, su)
        elif self.y_mode == "null":
            self._y_null(m29, V29, su)
        else:
            self._y_real(m29, V29, su)
        self._g_stage("end")
        self.st["pit_audit"] = dict(self.audit)
        self.st["memory"] = self.g_mem
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        self.st["max_rss_mb"] = _mem_now().get("ru_maxrss_mb")
        text = json.dumps(_plain(self.st), sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRY|{i // 9000}|{text[i:i + 9000]}")

    def _y_args(self, m29, V, su):
        return (m29, su["m30"], V, su["sc28j"], su["j29"], su["e28"]["wealth"], su["spy"], su["days"])

    # ------------------------------------------------------------------------------------------------ canary
    def _y_canary(self, months, m29, V29, su):
        ck = dict(real_h029_h030_result_computed=False)
        # 1. mechanics on the real structure: entries after the review, joint universe, 50/50 recomputation
        mech = dict(months=len(m29), entry_not_after_review=0, joint_not_subset=0, blend_mismatch=0, score_mismatch=0)
        for i, (a, b) in enumerate(zip(m29, su["m30"])):
            mech["entry_not_after_review"] += int(not a["days"][0] > a["cutoff_day"])
            mech["joint_not_subset"] += int(not set(b["ids"]) <= set(a["ids"]))
        for i in (0, 41, 83):
            M = V29[i]
            Pm = np.column_stack([H.centred_percentile(M[:, j]) for j in range(M.shape[1])])   # frozen H026 percentile
            man = np.array([np.nanmean(r) if np.isfinite(r).sum() >= 5 else np.nan for r in Pm])
            sc = V.h029_score(M)[0]
            mech["score_mismatch"] += int(not np.allclose(man, sc, equal_nan=True, rtol=0, atol=1e-15))
            b30 = Q.blend(su["sc28j"][i], sc[su["j29"][i]])
            man30 = 0.5 * V.centred(su["sc28j"][i]) + 0.5 * V.centred(sc[su["j29"][i]])
            mech["blend_mismatch"] += int(not np.array_equal(b30, man30))
        mech["min_valid_signals"] = int(min(int(np.isfinite(V29[i]).sum(1).min()) for i in range(len(V29)) if len(V29[i])))
        ck["mechanics"] = mech
        # 2. null (Amendment 1, owner D233): sector-stratified tether -- constructible (every FF12 sector of every
        #    review holds >= 2 H029-eligible stocks), donor sector == recipient sector, recipient sector / returns /
        #    eligibility / H028 unchanged, complete donor vectors, no self-match, persistent partners
        sizes = [np.unique(np.asarray(m["sector"]), return_counts=True)[1] for m in m29 if len(m["ids"])]
        nc = dict(seeds=[1, 2], min_sector_size=int(min(int(z.min()) for z in sizes)),
                  singleton_sector_reviews=sum(int((z == 1).any()) for z in sizes), constructible=True,
                  not_constructible=None, h028_changed=0, eligibility_changed=0, not_donor_vector=0, self_match=0,
                  donor_other_sector=0, recipient_sector_changed=0, recipient_data_changed=0, persist_kept=0,
                  persist_possible=0, mapped=0)
        keys = ("ids", "sector", "open_ok", "r_oo", "alive_next", "r_oc", "alive_end", "daily")
        snap = lambda ms: [_sha([(m[k].tolist() if hasattr(m[k], "tolist") else m[k]) for k in keys if k in m])
                           for m in ms]
        sec0 = [np.asarray(m["sector"]).copy() for m in m29]
        d29, d30 = snap(m29), snap(su["m30"])
        try:
            for sd in (1, 2):
                before = [s.copy() for s in su["sc28j"]]
                Vp = Q.tether_vectors(m29, V29, sd)
                dn = Q.donors(m29, sd)
                prev = None
                for m, Vr, Pp, d in zip(m29, V29, Vp, dn):
                    pos = {s: i for i, s in enumerate(m["ids"])}
                    sec = np.asarray(m["sector"])
                    nc["eligibility_changed"] += int(sorted(d) != m["ids"] or not np.all(np.isfinite(V.h029_score(Pp)[0])))
                    for s, src in d.items():
                        nc["mapped"] += 1
                        nc["self_match"] += int(s == src)
                        nc["donor_other_sector"] += int(sec[pos[s]] != sec[pos[src]])
                        nc["not_donor_vector"] += int(not np.array_equal(Pp[pos[s]], Vr[pos[src]], equal_nan=True))
                    if prev is not None:
                        for s in m["ids"]:
                            if s in prev and prev[s] in pos and sec[pos[s]] == sec[pos[prev[s]]]:
                                nc["persist_possible"] += 1
                                nc["persist_kept"] += int(d[s] == prev[s])
                    prev = d
                Q.world(*self._y_args(m29, V29, su), seed=sd)
                nc["h028_changed"] += sum(int(not np.array_equal(a, b)) for a, b in zip(su["sc28j"], before))
        except Q.NullNotConstructible as e:
            nc["constructible"], nc["not_constructible"] = False, str(e)
        nc["recipient_sector_changed"] = sum(int(not np.array_equal(a, np.asarray(m["sector"])))
                                             for a, m in zip(sec0, m29))
        nc["recipient_data_changed"] = (sum(int(a != b) for a, b in zip(d29, snap(m29))) +
                                        sum(int(a != b) for a, b in zip(d30, snap(su["m30"]))))
        nc["mechanics_constants"] = dict(K=H.K, SECTOR_CAP=H.SECTOR_CAP, CAPITAL=H.CAPITAL, COMMISSION=H.COMMISSION,
                                         SLIPPAGE=H.SLIPPAGE, STRESS_SLIPPAGE=H.STRESS_SLIPPAGE, LAMBDA=Q.LAMBDA)
        ck["null_checks"] = nc
        if not nc["constructible"]:
            self.st["canary"] = ck                       # STOP -- SECTOR-STRATIFIED NULL NOT CONSTRUCTIBLE
            return
        # 3. determinism of one world
        a = Q.world(*self._y_args(m29, V29, su), seed=3)
        b = Q.world(*self._y_args(m29, V29, su), seed=3)
        ck["world_repeat_identical"] = a == b
        # 4. synthetic A (no relation) and B (planted upside predictor), 50 null worlds each
        t0 = time.perf_counter()
        syn = dict(A=[], B=None)
        for sd in Q.SYNTH_A_SEEDS:
            VA = Q.synthetic_vectors(m29, "A", sd)
            r = Q.world(*self._y_args(m29, VA, su))
            nul = [Q.world(*self._y_args(m29, VA, su), seed=s) for s in range(1, Q.SYNTH_NULLS + 1)]
            syn["A"].append(dict(seed=sd, s_up=r[1], p_up=Q.empirical_p([x[1] for x in nul], r[1]),
                                 s_inc=r[10], p_inc=Q.empirical_p([x[10] for x in nul], r[10])))
        VB = Q.synthetic_vectors(m29, "B", Q.SYNTH_B_SEED)
        r = Q.world(*self._y_args(m29, VB, su))
        nul = [Q.world(*self._y_args(m29, VB, su), seed=s) for s in range(1, Q.SYNTH_NULLS + 1)]
        syn["B"] = dict(s_up=r[1], p_up=Q.empirical_p([x[1] for x in nul], r[1]), null_max=max(x[1] for x in nul),
                        s_inc=r[10], p_inc=Q.empirical_p([x[10] for x in nul], r[10]))
        nworld = 6 * (Q.SYNTH_NULLS + 1)
        syn["world_s"] = round((time.perf_counter() - t0) / nworld, 3)
        syn["A_pass"] = (sum(1 for x in syn["A"] if x["p_up"] <= 0.02) <= 1 and
                         sum(1 for x in syn["A"] if x["p_inc"] <= 0.02) <= 1)
        syn["B_pass"] = syn["B"]["p_up"] == 1.0 / (Q.SYNTH_NULLS + 1)
        ck["synthetic"] = syn
        ck["estimated_5000_world_minutes"] = round(syn["world_s"] * 5000 / 60.0, 1)
        self.st["canary"] = ck

    # ------------------------------------------------------------------------------------------------ null
    def _y_null(self, m29, V29, su):
        t0 = time.perf_counter()
        rows = [Q.world(*self._y_args(m29, V29, su), seed=sd) for sd in self.y_seeds]
        sc29 = Q.h029_scores(V29)
        sc30 = [Q.blend(a, s[j]) for a, s, j in zip(su["sc28j"], sc29, su["j29"])]
        t29, h29 = Q.selection_structure(m29, sc29)
        t30, h30 = Q.selection_structure(su["m30"], sc30)
        real = dict(turn29=t29, hhi29=h29, turn30=t30, hhi30=h30,
                    eligible29=[len(m["ids"]) for m in m29], joint30=[len(m["ids"]) for m in su["m30"]])
        out = self._w_emit("QRYN", dict(fields=list(Q.NULL_FIELDS), worlds=rows, real_selection_structure=real))
        self.st["null"] = dict(seeds=[self.y_seeds[0], self.y_seeds[-1]], worlds=len(rows),
                               nonfinite=sum(1 for r in rows if not all(math.isfinite(x) for x in r[1:])),
                               world_s=round((time.perf_counter() - t0) / max(1, len(rows)), 3), **out)

    # ------------------------------------------------------------------------------------------------ real
    def _y_real(self, m29, V29, su):
        p = self.qr_params
        c_up, c_inc = float(p["c_up_h029"]), float(p["c_incremental_h030"])
        self.st["provenance"] = {k: p[k] for k in ("c_up_h029", "c_incremental_h030", "null_result_sha256",
                                                   "threshold_commit")}
        r = Q.world(*self._y_args(m29, V29, su), keep=True)              # the ONE real H029 / H030 result
        e29, e30, spy, days = r["e29"], r["e30"], su["spy"], su["days"]
        sp_s = Q.spy_path(su["m28"], days, slip=H.STRESS_SLIPPAGE)
        e29s = Q.evaluate(m29, r["sc29"], sp_s, days, slip=H.STRESS_SLIPPAGE)
        w30s = H.simulate(su["m30"], r["sc30"], slip=H.STRESS_SLIPPAGE)["wealth"]
        w28s = H.simulate(su["m28"], su["sc28"], slip=H.STRESS_SLIPPAGE)["wealth"]
        stress = dict(w30=w30s, w28=w28s, spy=sp_s["wealth"], s_up29=e29s["rel"]["s_up"], w29=e29s["wealth"])
        g29 = Q.gates_h029(e29, spy, e29s["rel"]["s_up"], c_up, 0.0 if e29["rel"]["s_up"] > c_up else 1.0)
        g30 = Q.gates_h030(e30, su["e28"]["wealth"], spy, c_inc,
                           0.0 if math.log(e30["wealth"] / su["e28"]["wealth"]) > c_inc else 1.0, stress)

        def tr(h):
            return dict(buys=h["buys"], sells=h["sells"], trades=h["trades"], commissions=h["commissions"],
                        slippage=h["slippage"], turnover=h["turnover"], holdings=h["holdings"], cash_share=h["cash_share"])

        def secs(ms, picks):
            out = {}
            for mo, pk in zip(ms, picks):
                pos = {s: n for n, s in enumerate(mo["ids"])}
                for s in pk:
                    nm = XD.FF12_NAMES[int(mo["sector"][pos[s]])]
                    out[nm] = out.get(nm, 0) + 1
            return out
        e28k = H.simulate(su["m28"], su["sc28"], daily=True, keep_trades=True)
        out = dict(c_up_h029=c_up, c_incremental_h030=c_inc, gates_h029=g29, gates_h030=g30, row=r["row"],
                   wealth=dict(h028=su["e28"]["wealth"], h029=e29["wealth"], h030=e30["wealth"], lv15=su["lv"]["wealth"],
                               spy=spy["wealth"]),
                   stress=dict(stress, daily_h029=e29s["h"]["daily"], daily_spy=sp_s["daily"]),
                   metrics={n: e["pm"] for n, e in (("h028", su["e28"]), ("h029", e29), ("h030", e30), ("lv15", su["lv"]))},
                   spy_metrics=spy["pm"],
                   risk={n: e["risk"] for n, e in (("h028", su["e28"]), ("h029", e29), ("h030", e30), ("lv15", su["lv"]))},
                   trades={n: tr(e["h"]) for n, e in (("h028", su["e28"]), ("h029", e29), ("h030", e30), ("lv15", su["lv"]))},
                   sectors=dict(h028=secs(su["m28"], e28k["picks"]), h029=secs(m29, e29["h"]["picks"]),
                                h030=secs(su["m30"], e30["h"]["picks"])),
                   daily=dict(h028=su["e28"]["h"]["daily"], h029=e29["h"]["daily"], h030=e30["h"]["daily"],
                              lv15=su["lv"]["h"]["daily"], spy=spy["daily"]),
                   days=days, months=[m["day"] for m in m29],
                   eligible29=[len(m["ids"]) for m in m29], joint30=[len(m["ids"]) for m in su["m30"]])
        res = self._w_emit("QRYR", out)
        self.st["real"] = dict(h029=g29["verdict"], h030=g30["verdict"],
                               gates_h029={k: g29[k] for k in ("N1", "N2", "N3", "N4", "N5", "all")},
                               gates_h030={k: g30[k] for k in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "all")},
                               wealth=out["wealth"], **res)
