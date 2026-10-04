# X985 — H019 cross-sectional technical signal validation host (research/phase4/P4_xs_spec.md v2). NON-TRADING: no
# orders are ever placed. The harness supplies the frozen universe of data infrastructure v1 (US common stock, point-in-
# time market cap >= $2B, price >= $5, ADV20 >= $5M, SEC correction layer), the sessions and the Holdout lock. The run
# ends on 2017-12-31; no 2018+ data is ever requested.
#
# During the run: at every official session the eligible set (as of the previous close, the harness convention) is
# remembered; the set of the LAST session of each month is that month-end's universe (with market cap and the point-
# in-time SEC SIC). At the end (2017-12-31): the daily panel of every stock eligible at any research month-end is
# assembled from history (qr_xs_panel: SCALED_RAW = total-return prices adjusted with corporate actions up to 2017
# only; RAW x split events up to 2017 = split-adjusted closes), then qr_xs.Features -> qr_xs.run_world, exactly the
# code of the synthetic studies. Only aggregates leave QuantConnect (summary statistics); no price is exported.
# Modes (params.mode):
#   canary : E985-01 plumbing / fidelity canary (spec section 10): universe and calendar facts, history coverage,
#            split alignment, independent slow recomputation, truncation invariance, S2 structure, placebo features,
#            planted response, null determinism and timing. Publishes NO real-signal statistic.
#   null   : null worlds params.seeds = [first, last] (full procedure per world); publishes per-world statistics.
#   real   : the real evaluation (identity world), once; needs the pinned threshold provenance in params.
from AlgorithmImports import *
from datetime import datetime
import hashlib
import json
import time
import numpy as np
from qr_harness import QRAlgorithm
import qr_xs as X
import qr_xs_diag as XD
import qr_xs_panel as XP

HIST_START = datetime(2005, 11, 1)      # >= 1,000 sessions before the first research month-end (2010-01-29)
HIST_END = datetime(2017, 12, 31)       # the last bar is the 2017-12-29 session
LAST_SESSION = np.datetime64("2017-12-29").astype(np.int64)
BATCH = 100
CANARY_MONTHS = ((2011, 1), (2012, 6), (2013, 12), (2015, 3), (2016, 8), (2017, 11))
TRUNC_DECISION = (2014, 6)              # truncation test: panel cut at the 2014-07 month-end close


def _sid(s):
    return str(s.id) if hasattr(s, "id") else str(s)


def _r(x, n=6):
    if isinstance(x, float):
        return float(f"{x:.{n}g}") if np.isfinite(x) else None
    if isinstance(x, (list, tuple)):
        return [_r(v, n) for v in x]
    if isinstance(x, dict):
        return {str(k): _r(v, n) for k, v in x.items()}
    if isinstance(x, (np.floating,)):
        return _r(float(x), n)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


class H019XS(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        p = self.qr_params
        self.xs_mode = p["mode"]
        if self.xs_mode not in ("canary", "null", "real"):
            raise Exception(f"X985: unknown mode {self.xs_mode!r}")
        if self.qr_sec is None or self.qr_sic is None:
            raise Exception("X985 needs universe.sec_corrections (frozen data infrastructure v1)")
        if self.qr["end"] > "2017-12-31":
            raise Exception("X985: H019 runs end on or before 2017-12-31")
        if self.xs_mode == "null":
            a, b = p["seeds"]
            if not (1 <= a <= b <= 5000):
                raise Exception("X985: null seeds must lie in 1..5000")
            self.xs_seeds = list(range(int(a), int(b) + 1))
        if self.xs_mode == "real":
            for k in ("threshold_c", "threshold_commit", "null_result_sha256", "spec_sha256"):
                if k not in p:
                    raise Exception(f"X985: real mode needs the pinned null provenance ({k})")
        self._qr_log_budget = 400000
        self.t0 = time.perf_counter()
        self.xs_sym = {}                 # sid -> Symbol
        self.xs_snap = None              # (date, eligible symbols, info) of the latest official session
        self.xs_me = {}                  # (y, m) -> (date, {sid: (market cap, sic)})
        self.xs_st = {"official_sessions": 0}

    def qr_select_universe(self, eligible):
        return []                        # nothing is traded or streamed; prices come from history at the end

    def qr_on_close(self, data):
        today = self.time.date()
        self.xs_st["official_sessions"] += 1
        if self.xs_snap is not None and (self.xs_snap[0].year, self.xs_snap[0].month) != (today.year, today.month):
            self._finalise_month(self.xs_snap)
        self.xs_snap = (today, self.qr_eligible, self.qr_eligible_info)

    def _finalise_month(self, snap):
        d, elig, info = snap
        rec = {}
        for sym in elig:
            sid = str(sym.id)
            self.xs_sym[sid] = sym
            rec[sid] = (float(info[sym][0]), self.qr_sic.sic_on(sid, d))
        self.xs_me[(d.year, d.month)] = (d, rec)

    # ---------------------------------------------------------------- panel
    def _cols(self, frame, col_of, cal_ix, D, N, fields):
        out = {f: np.full((D, N), np.nan) for f in fields}
        if frame is None or frame.empty:
            return out, 0, 0
        idx = frame.index
        lmap = np.array([col_of.get(_sid(s), -1) for s in idx.levels[0]], dtype=np.int64)
        cols = lmap[np.asarray(idx.codes[0])]
        days = XP.session_days(idx.get_level_values(-1).values)
        late = int((days > LAST_SESSION).sum())
        pos = np.searchsorted(cal_ix, days)
        pos_c = np.minimum(pos, cal_ix.size - 1)
        ok = (cols >= 0) & (cal_ix[pos_c] == days)
        unknown = int((~ok & (cols >= 0)).sum())
        if (cols < 0).all():
            raise Exception("X985: history symbols could not be mapped to columns")
        key = pos_c[ok] * (N + 1) + cols[ok]
        if np.unique(key).size != key.size:
            raise Exception("X985: two bars of one stock map to the same session")
        for f in fields:
            out[f][pos_c[ok], cols[ok]] = frame[f].to_numpy(dtype=float)[ok]
        return out, late, unknown

    def _build_panel(self):
        t0 = time.perf_counter()
        self._finalise_month(self.xs_snap)
        sids = sorted({sid for _, rec in self.xs_me.values() for sid in rec})
        col_of = {sid: j for j, sid in enumerate(sids)}
        N = len(sids)
        self.xs_sids = sids
        spy = self.history(self.spy, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        cal = np.unique(XP.session_days(spy.index.get_level_values(-1).values))
        if cal[-1] > LAST_SESSION:
            raise Exception("X985: calendar extends past 2017-12-29")
        D = cal.size
        Q = np.full((D, N), np.nan)
        P = np.full((D, N), np.nan)
        O = np.full((D, N), np.nan)
        st = dict(columns=N, rows=D, first_day=str(cal[0].astype("datetime64[D]")),
                  last_day=str(cal[-1].astype("datetime64[D]")), late_rows=0, unknown_day_rows=0, history_calls=0,
                  split_types={}, split=dict(n=0, aligned=0, realigned=0, unverified=0, outside=0),
                  jumps_hi=0, jumps_lo=0, stocks_with_jumps=0, last_scale_not_one=0)
        for i in range(0, N, BATCH):
            part = sids[i:i + BATCH]
            syms = [self.xs_sym[s] for s in part]
            hr = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.RAW)
            hs = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            sp = self.history(Split, syms, HIST_START, HIST_END)
            st["history_calls"] += 3
            loc = {s: j for j, s in enumerate(part)}
            a, l1, u1 = self._cols(hr, loc, cal, D, len(part), ("close",))
            b, l2, u2 = self._cols(hs, loc, cal, D, len(part), ("close", "open"))
            st["late_rows"] += l1 + l2
            st["unknown_day_rows"] += u1 + u2
            ev = {j: [] for j in range(len(part))}
            if sp is not None and not sp.empty:
                sidx = sp.index
                lmap = np.array([loc.get(_sid(s), -1) for s in sidx.levels[0]], dtype=np.int64)
                cols = lmap[np.asarray(sidx.codes[0])]
                eday = XP.event_days(sidx.get_level_values(-1).values)
                typ = [str(t) for t in sp["type"].tolist()]
                ref = sp["referenceprice"].to_numpy(dtype=float)
                fac = sp["splitfactor"].to_numpy(dtype=float)
                for r in range(len(typ)):
                    st["split_types"][typ[r]] = st["split_types"].get(typ[r], 0) + 1
                    if cols[r] < 0 or not ("OCCUR" in typ[r].upper() or ref[r] > 0):
                        continue
                    if eday[r] > LAST_SESSION:
                        st["late_rows"] += 1
                        continue
                    ev[int(cols[r])].append((int(np.searchsorted(cal, eday[r])), float(fac[r])))
            for j in range(len(part)):
                raw, sc = a["close"][:, j], b["close"][:, j]
                mult, s1 = XP.split_multiplier(raw, sc, ev[j])
                for k2, v in s1.items():
                    st["split"][k2] += v
                q = raw * mult
                hi, lo = XP.residual_jumps(q, sc)
                st["jumps_hi"] += hi
                st["jumps_lo"] += lo
                st["stocks_with_jumps"] += int(hi + lo > 0)
                v = np.flatnonzero(np.isfinite(raw) & np.isfinite(sc) & (raw > 0))
                if v.size and abs(sc[v[-1]] / raw[v[-1]] - 1.0) > 1e-6:
                    st["last_scale_not_one"] += 1
                Q[:, i + j] = q
                P[:, i + j] = sc
                O[:, i + j] = b["open"][:, j]
        if st["late_rows"]:
            raise Exception("X985: history returned data after 2017-12-29")
        months, me = XP.month_ends(cal)
        K = len(months)
        elig = np.zeros((K, N), bool)
        self.xs_mcap = np.full((K, N), np.nan)
        self.xs_sector = [["Unclassified"] * N for _ in range(K)]
        mism = []
        for k, m in enumerate(months):
            if m not in self.xs_me or m < X.FIRST_RESEARCH_MONTH:
                continue
            d, rec = self.xs_me[m]
            if np.datetime64(d).astype("datetime64[D]").astype(np.int64) != cal[me[k]]:
                mism.append("%04d-%02d" % m)
            for sid, (mc, sic) in rec.items():
                j = col_of[sid]
                elig[k, j] = True
                self.xs_mcap[k, j] = mc
                self.xs_sector[k][j] = XD.ff12(sic)
        st["month_end_date_mismatches"] = mism
        st["research_months_recorded"] = sorted("%04d-%02d" % m for m in self.xs_me)
        st["panel_s"] = round(time.perf_counter() - t0, 1)
        self.xs_cal, self.xs_me_rows, self.xs_months = cal, me, months
        self.xs_panel = X.Panel(Q, P, O, me, months, elig)
        t1 = time.perf_counter()
        self.xs_F = X.Features(self.xs_panel)
        st["features_s"] = round(time.perf_counter() - t1, 1)
        F = self.xs_F
        k0, kl = months.index(X.FIRST_RESEARCH_MONTH), months.index((2017, 12))
        st["features_sha256"] = XD.features_digest(F, range(k0, kl + 1))
        st["fwd_end_last_decision"] = str(cal[me[months.index(X.LAST_DECISION) + 1]].astype("datetime64[D]"))
        st["fwd3_end_last_diag"] = str(cal[me[months.index(X.LAST_DECISION_DIAG[3]) + 3]].astype("datetime64[D]"))
        self.xs_st["panel"] = st

    # ---------------------------------------------------------------- end
    def qr_on_end(self):
        self._build_panel()
        F = self.xs_F
        months = self.xs_months
        k0 = months.index(X.FIRST_RESEARCH_MONTH)
        kd0, kd1 = months.index(X.FIRST_DECISION), months.index(X.LAST_DECISION)
        nb = XD.bars_upto(self.xs_panel.Q, self.xs_me_rows)
        self.xs_st["universe"] = XD.universe_counts(F)
        self.xs_st["coverage"] = XD.coverage(F, nb, range(kd0, kd1 + 1), range(k0, kd1 + 1))
        if self.xs_mode == "canary":
            self._canary(F, nb)
        elif self.xs_mode == "null":
            self._null(F)
        else:
            self._real(F)
        self.xs_st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.xs_st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as e:
            self.xs_st["max_rss_mb"] = f"unavailable: {type(e).__name__}"
        self._qr_log("QRX985|summary|" + json.dumps(_r(self.xs_st), sort_keys=True, default=str))

    def _world_line(self, sm):
        o = {"F": X.family_stat(sm)}
        for s in X.SIGNALS:
            r = sm[s]
            o[s] = dict(t=r["t"], ic=r["ic_mean"], top=r["top_ann"], spr=r["spread_ann"], mono=r["mono"],
                        gap=r["q_gap"], sub=r["sub"], blk=r["block_max"])
            if s in X.INCREMENTAL:
                o[s].update(t_inc=r["t_inc"], inc=r["inc_mean"])
        return o

    def _null(self, F):
        t0 = time.perf_counter()
        for seed in self.xs_seeds:
            sm = X.run_world(F, seed=seed)
            self._qr_log(f"N|{seed}|" + json.dumps(_r(self._world_line(sm), 8), sort_keys=True))
        self.xs_st["null"] = dict(seeds=[self.xs_seeds[0], self.xs_seeds[-1]], worlds=len(self.xs_seeds),
                                  world_s=round(time.perf_counter() - t0, 1))

    def _real(self, F):
        p = self.qr_params
        self.xs_st["provenance"] = {k: p[k] for k in ("threshold_c", "threshold_commit", "null_result_sha256",
                                                      "spec_sha256")}
        t0 = time.perf_counter()
        sm = X.run_world(F, keep_series=True, keep_signals=True)          # the primary result first
        pub = {s: sm[s] for s in X.SIGNALS}
        self._qr_log("R|" + json.dumps(_r(pub, 10), sort_keys=True))
        self._qr_log("RS|" + json.dumps(_r(dict(years=sm["_years"], series=sm["_series"]), 8), sort_keys=True))
        months = self.xs_months
        r1m = np.full(F.pret.shape, np.nan)
        Pm = self.xs_panel.P[self.xs_me_rows]
        r1m[1:] = Pm[1:] / Pm[:-1] - 1.0
        diag = XD.real_diagnostics(F, sm, self.xs_mcap, self.xs_sector, r1m)
        self._qr_log("RD|" + json.dumps(_r(diag, 8), sort_keys=True))
        # NON-GATING DIAGNOSTIC: 3-month horizon, computed only after the primary result
        sm3 = X.run_world(F, h=3, lag=X.DIAG_NW_LAG[3], last_decision=X.LAST_DECISION_DIAG[3])
        self._qr_log("R3|" + json.dumps(_r({s: sm3[s] for s in X.SIGNALS}, 10), sort_keys=True))
        self.xs_st["real"] = dict(decisions=len(sm["_years"]), world_s=round(time.perf_counter() - t0, 1),
                                  first_last=["%04d-%02d" % months[sm["_signals"][i]["k"]] for i in (0, -1)])

    # ---------------------------------------------------------------- canary (no real-signal statistic)
    def _replace(self, F, rng, pret=None, idm=None, A=None, fwd=None):
        G = object.__new__(X.Features)
        G.__dict__.update(F.__dict__)
        G.fwd = dict(F.fwd)
        G.pret = F.pret.copy() if pret is None else pret
        G.idm = F.idm.copy() if idm is None else idm
        G.A = F.A if A is None else A
        if fwd is not None:
            G.fwd.update(fwd)
        return G

    def _canary(self, F, nb):
        ck = {}
        months, me = self.xs_months, self.xs_me_rows
        Pn, D = self.xs_panel, self.xs_cal.size
        rng = np.random.default_rng(20261004)
        kd0, kd1 = months.index(X.FIRST_DECISION), months.index(X.LAST_DECISION)
        ck["decisions"] = kd1 - kd0 + 1
        ck["decision_dates_first_last"] = [str(self.xs_cal[me[kd0]].astype("datetime64[D]")),
                                           str(self.xs_cal[me[kd1]].astype("datetime64[D]"))]
        # 1. independent slow recomputation of PRET / ID / A_L (panel columns, loops)
        dmax = dict(pret=0.0, idm=0.0, A=0.0, nan_mismatch=0, n=0)
        for m in CANARY_MONTHS:
            k = months.index(m)
            js = np.flatnonzero(F.dom[k])
            for j in rng.choice(js, size=min(25, js.size), replace=False):
                pret, idm, A = XD.slow_features(Pn.Q, Pn.P, me, k, int(j))
                dmax["n"] += 1
                for name, a, b in (("pret", pret, F.pret[k, j]), ("idm", idm, F.idm[k, j])):
                    if np.isfinite(a) != np.isfinite(b):
                        dmax["nan_mismatch"] += 1
                    elif np.isfinite(a):
                        dmax[name] = max(dmax[name], abs(a - b))
                dA = np.abs(np.asarray(A) - F.A[k, j])
                if np.isfinite(dA).any():
                    dmax["A"] = max(dmax["A"], float(np.nanmax(dA)))
                dmax["nan_mismatch"] += int((np.isfinite(A) != np.isfinite(F.A[k, j])).sum())
        ck["slow_features"] = dmax
        # 2. trend-factor regressions: qr_xs.ols_slopes vs independent normal equations (identity world sample)
        rd = dict(max_abs=0.0, months=0, rank_deficient=0)
        for s in range(months.index(X.FIRST_RESEARCH_MONTH), kd1 + 1, 7):
            j = np.flatnonzero(F.dom[s])
            Am, y = F.A[s, j], F.reg[s, j]
            b1 = X.ols_slopes(Am, y)
            try:
                b2 = XD.slow_ols(Am, y)
                rd["max_abs"] = max(rd["max_abs"], float(np.max(np.abs(b1 - b2))))
                rd["months"] += 1
            except np.linalg.LinAlgError:
                rd["rank_deficient"] += 1
        ck["regressions"] = rd
        # 3. signals-only runs: real features, PLACEBO responses (seeded noise) -> no real IC is computed anywhere
        noise = {h: np.where(np.isfinite(F.fwd[h]), rng.standard_normal(F.fwd[h].shape) * 0.08, np.nan) for h in F.fwd}
        G = self._replace(F, rng, fwd=noise)
        full = X.run_world(G, keep_signals=True)
        # 3a. S3 independently: slow regressions, 12-month mean, score; S2 structure
        s3d, s2bad, eb_bad = 0.0, 0, 0
        for rec in full["_signals"]:
            k = rec["k"]
            if months[k] not in CANARY_MONTHS:
                continue
            bs = []
            for s in range(k - 12, k):
                j = np.flatnonzero(F.dom[s])
                try:
                    bs.append(XD.slow_ols(F.A[s, j], F.reg[s, j]))
                except np.linalg.LinAlgError:
                    bs.append(full["_betas"][s])
                    eb_bad += 1
            s3 = F.A[k, rec["src"]] @ np.mean(bs, axis=0)
            s3d = max(s3d, float(np.max(np.abs(s3 - rec["S3"]))))
            s2bad += XD.s2_structure_violations(rec["pret"], X.fip_key(rec["idm"], rec["pret"]), rec["S2"])
        ck["s3_slow_max_abs"] = s3d
        ck["s3_slow_rank_deficient_months"] = eb_bad
        ck["s2_structure_violations"] = s2bad
        ck["id_range_ok"] = bool(all(np.all(np.abs(r["idm"]) <= 1.0 + 1e-12) for r in full["_signals"]))
        ck["betas_keys_ok"] = bool(min(full["_betas"]) == months.index(X.FIRST_RESEARCH_MONTH) and
                                   max(full["_betas"]) == kd1)
        # 3b. truncation invariance: the panel cut at the close after decision TRUNC_DECISION gives identical signals
        kt = months.index(TRUNC_DECISION)
        cut = me[kt + 1] + 1
        PT = X.Panel(Pn.Q[:cut], Pn.P[:cut], Pn.O[:cut], me[:kt + 2], months[:kt + 2], Pn.elig[:kt + 2])
        FT = X.Features(PT)
        GT = self._replace(FT, rng, fwd={h: noise[h][:kt + 2] for h in noise})
        tr = X.run_world(GT, keep_signals=True, last_decision=TRUNC_DECISION)
        fa = [r for r in full["_signals"] if r["k"] <= kt]
        td = dict(dates=len(tr["_signals"]), dates_full=len(fa), max_abs=0.0, id_mismatch=0)
        for a, b in zip(fa, tr["_signals"]):
            if a["k"] != b["k"] or not np.array_equal(a["rec"], b["rec"]):
                td["id_mismatch"] += 1
                continue
            for f in ("pret", "idm", "S2", "S3", "y"):
                td["max_abs"] = max(td["max_abs"], float(np.max(np.abs(a[f] - b[f]))))
        td["betas_max_abs"] = max(float(np.max(np.abs(full["_betas"][s] - tr["_betas"][s]))) for s in tr["_betas"])
        ck["truncation"] = td
        # 3c. evaluation-set facts per decision (counts only)
        ck["eval_counts"] = [int(r["rec"].size) for r in full["_signals"]]
        ck["eval_min_max"] = [min(ck["eval_counts"]), max(ck["eval_counts"])]
        # 4. placebo features (seeded random signals vs real responses): IC ~ 0 expected
        pp = np.where(np.isfinite(F.pret), rng.standard_normal(F.pret.shape), np.nan)
        pi = np.where(np.isfinite(F.idm), rng.uniform(-1, 1, F.idm.shape), np.nan)
        pa = np.where(np.isfinite(F.A), rng.uniform(0.5, 1.5, F.A.shape), np.nan)
        sp = X.run_world(self._replace(F, rng, pret=pp, idm=pi, A=pa))
        ck["placebo"] = {s: dict(t=sp[s]["t"], ic=sp[s]["ic_mean"], t_inc=sp[s].get("t_inc")) for s in X.SIGNALS}
        ck["placebo_F"] = X.family_stat(sp)
        # 5. planted response (alignment): S1 := the response itself -> IC exactly 1 at every date (h = 1 and h = 3)
        pl = {}
        for h, last, lag in ((1, X.LAST_DECISION, X.NW_LAG), (3, X.LAST_DECISION_DIAG[3], X.DIAG_NW_LAG[3])):
            plant = np.where(np.isfinite(F.pret) & np.isfinite(F.fwd[h]), F.fwd[h] + 1e-9 * rng.standard_normal(
                F.pret.shape), np.where(np.isfinite(F.pret), -1e3, np.nan))
            sm = X.run_world(self._replace(F, rng, pret=plant, idm=pi, A=pa), h=h, lag=lag, last_decision=last,
                             keep_series=True)
            ics = [d["S1"]["ic"] for d in sm["_series"]]
            pl[f"h{h}"] = dict(ic_min=min(ics), ic_mean=float(np.mean(ics)), dates=len(ics))
        ck["planted"] = pl
        # 6. null determinism and timing (seeds outside the official 1..5000; only digests and seconds are published)
        n = int(self.qr_params.get("timing_worlds", 10))
        t0 = time.perf_counter()
        dg = [XD.world_digest(X.run_world(F, seed=900001 + i)) for i in range(n)]
        ck["null_world_s"] = (time.perf_counter() - t0) / max(n, 1)
        ck["null_repeat_identical"] = XD.world_digest(X.run_world(F, seed=900001)) == dg[0]
        ck["null_digest_900001"] = dg[0]
        ck["null_world_s_1000"] = ck["null_world_s"] * 1000
        self._qr_log("K|" + json.dumps(_r(ck, 8), sort_keys=True, default=str))
