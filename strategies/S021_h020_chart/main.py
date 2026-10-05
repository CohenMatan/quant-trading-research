# X987 — H020 structured chart score validation host (research/phase5/H020_spec.md v1 + H020_spec_addendum_1.md).
# NON-TRADING: no orders are ever placed. The harness supplies the frozen universe of data infrastructure v1 (US common
# stock, point-in-time market cap >= $2B, price >= $5, ADV20 >= $5M, SEC correction layer), the sessions and the Holdout
# lock. The run ends on 2017-12-31; no 2018+ data is ever requested.
#
# During the run: at every official session the eligible set (as of the previous close, the harness convention) is
# remembered; the set of the LAST session of each ISO week is that week-end's universe (with market cap and the point-
# in-time FF12 industry from the SEC SIC at filing). At the end: the daily panel of every stock eligible at any research
# week-end is assembled from history (RAW bars x QuantConnect's split feed = split-adjusted chart bars, volume / the same
# factors; x the dividend feed as well = total-shareholder-return closes / opens; SCALED_RAW only as a cross-check), the
# frozen chart score qr_chart.snapshot is computed for every eligible stock at every decision (qr_h020_panel.ScoreTable),
# then qr_h020_stats.prepare / run_world, exactly the code of the synthetic studies. Only aggregates leave QuantConnect
# (summary statistics); no price and no chart image is exported or rendered.
# Modes (params.mode):
#   canary : E987-01 PIT plumbing / fidelity canary. Publishes NO response-linked statistic of a real score.
#   null   : null worlds params.seeds = [first, last] (full procedure per world); publishes per-world statistics.
#   real   : the real evaluation (identity world), once; needs the pinned null provenance in params and refuses to
#            compute anything if the chart panel differs from the one the null was calibrated on.
from AlgorithmImports import *
from datetime import datetime, timedelta
import hashlib
import json
import time
import numpy as np
from qr_harness import QRAlgorithm
import qr_chart as C
import qr_h020_diag as HD
import qr_h020_panel as HP
import qr_h020_stats as HS
import qr_xs_diag as XD
import qr_xs_panel as XP

HIST_START = datetime(2006, 11, 1)      # >= 756 sessions before the first decision (2010-01-08): full snapshot window
HIST_END = datetime(2017, 12, 31)       # the last bar is the 2017-12-29 session
LAST_SESSION = np.datetime64("2017-12-29").astype(np.int64)
BATCH = 100
SLOW_SAMPLE = 120                       # canary: (stock, decision) pairs recomputed independently
PROVENANCE = ("c_ic", "c_inc", "threshold_commit", "null_result_sha256", "spec_sha256", "addendum_sha256",
              "chart_panel_sha256")


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
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def _day(d):
    return np.datetime64(d.strftime("%Y-%m-%d")).astype(np.int64)


class H020Chart(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        p = self.qr_params
        self.h_mode = p["mode"]
        if self.h_mode not in ("canary", "null", "real"):
            raise Exception(f"X987: unknown mode {self.h_mode!r}")
        if self.qr_sec is None or self.qr_sic is None:
            raise Exception("X987 needs universe.sec_corrections (frozen data infrastructure v1)")
        if self.qr["end"] > "2017-12-31":
            raise Exception("X987: H020 runs end on or before 2017-12-31")
        if self.h_mode == "null":
            a, b = p["seeds"]
            if not (1 <= a <= b <= 5000):
                raise Exception("X987: null seeds must lie in 1..5000")
            self.h_seeds = list(range(int(a), int(b) + 1))
        if self.h_mode == "real":
            for k in PROVENANCE:
                if k not in p:
                    raise Exception(f"X987: real mode needs the pinned null provenance ({k})")
        self._qr_log_budget = 400000
        self.t0 = time.perf_counter()
        self.h_sym = {}                  # sid -> Symbol
        self.h_snap = None               # (date, eligible symbols, info) of the latest official session
        self.h_we = {}                   # week-end day number -> {sid: (market cap, FF12)}
        self.h_st = {"official_sessions": 0}

    def qr_select_universe(self, eligible):
        return []                        # nothing is traded or streamed; prices come from history at the end

    def qr_on_close(self, data):
        today = self.time.date()
        self.h_st["official_sessions"] += 1
        if self.h_snap is not None and self.h_snap[0].isocalendar()[:2] != today.isocalendar()[:2]:
            self._finalise_week(self.h_snap)
        self.h_snap = (today, self.qr_eligible, self.qr_eligible_info)

    def _finalise_week(self, snap):
        d, elig, info = snap
        rec = {}
        for sym in elig:
            sid = str(sym.id)
            self.h_sym[sid] = sym
            rec[sid] = (float(info[sym][0]), XD.ff12(self.qr_sic.sic_on(sid, d)))
        self.h_we[int(_day(d))] = rec

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
            raise Exception("X987: history symbols could not be mapped to columns")
        key = pos_c[ok] * (N + 1) + cols[ok]
        if np.unique(key).size != key.size:
            raise Exception("X987: two bars of one stock map to the same session")
        for f in fields:
            if f in frame.columns:
                out[f][pos_c[ok], cols[ok]] = frame[f].to_numpy(dtype=float)[ok]
        return out, late, unknown

    def _events(self, frame, loc, cal, fields, st):
        out = {j: [] for j in loc.values()}
        if frame is None or frame.empty:
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
                st["late_rows"] += 1
                continue
            out[int(cols[r])].append((int(np.searchsorted(cal, eday[r])),) + tuple(v[r] for v in vals))
        return out

    def _build_panel(self):
        t0 = time.perf_counter()
        self._finalise_week(self.h_snap)
        spy = self.history(self.spy, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        cal = np.unique(XP.session_days(spy.index.get_level_values(-1).values))
        if cal[-1] > LAST_SESSION:
            raise Exception("X987: calendar extends past 2017-12-29")
        D = cal.size
        rows = HP.decision_rows(cal, HP.H_PRIMARY)
        we_all = HP.week_end_rows(cal)
        we_res = we_all[cal[we_all] >= HP.FIRST_DECISION_DAY]
        st = dict(rows=D, first_day=str(cal[0].astype("datetime64[D]")), last_day=str(cal[-1].astype("datetime64[D]")),
                  late_rows=0, unknown_day_rows=0, history_calls=0, split_types={},
                  split=dict(n=0, aligned=0, realigned=0, unverified=0, outside=0), dividend_events=0,
                  factor_steps_small=0, factor_steps_big=0, stocks_with_factor_steps=0, last_scale_not_one=0,
                  large_distributions=0, volume_missing_rows=0)
        rec_days = sorted(self.h_we)
        st["week_ends_recorded"] = len(rec_days)
        st["week_ends_in_calendar"] = int(we_res.size)
        st["week_end_universe_missing"] = [str(np.datetime64(int(cal[r]), "D")) for r in we_res
                                           if int(cal[r]) not in self.h_we]
        st["week_end_universe_extra"] = [str(np.datetime64(d, "D")) for d in rec_days if d not in set(cal[we_res].tolist())]
        K = rows.size
        sids = sorted({sid for r in rows for sid in self.h_we.get(int(cal[r]), {})})
        dev = int(self.qr_params.get("dev_max_columns", 0))       # scratch development runs only (plumbing)
        if dev:
            sids = sids[:dev]
        col_of = {sid: j for j, sid in enumerate(sids)}
        N = len(sids)
        self.h_sids = sids
        st["columns"] = N
        elig = np.zeros((K, N), bool)
        mcap = np.full((K, N), np.nan)
        sector = [["Unclassified"] * N for _ in range(K)]
        for k, r in enumerate(rows):
            for sid, (mc, ff) in self.h_we.get(int(cal[r]), {}).items():
                j = col_of.get(sid)
                if j is None:
                    continue
                elig[k, j] = True
                mcap[k, j] = mc
                sector[k][j] = ff
        O, Hh, L, Cl, V, TRC, TRO = (np.full((D, N), np.nan) for _ in range(7))
        self.h_events = {}
        for i in range(0, N, BATCH):
            part = sids[i:i + BATCH]
            syms = [self.h_sym[s] for s in part]
            hr = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.RAW)
            hs = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            sp = self.history(Split, syms, HIST_START, HIST_END)
            dv = self.history(Dividend, syms, HIST_START, HIST_END)
            st["history_calls"] += 4
            loc = {s: j for j, s in enumerate(part)}
            a, l1, u1 = self._cols(hr, loc, cal, D, len(part), ("open", "high", "low", "close", "volume"))
            b, l2, u2 = self._cols(hs, loc, cal, D, len(part), ("close",))
            st["late_rows"] += l1 + l2
            st["unknown_day_rows"] += u1 + u2
            sev = self._events(sp, loc, cal, ("type", "referenceprice", "splitfactor"), st)
            dev = self._events(dv, loc, cal, ("distribution", "referenceprice"), st)
            for j in range(len(part)):
                raw, sc = a["close"][:, j], b["close"][:, j]
                v = np.flatnonzero(np.isfinite(raw) & np.isfinite(sc) & (raw > 0) & (sc > 0))
                if v.size and abs(sc[v[-1]] / raw[v[-1]] - 1.0) > 1e-6:
                    st["last_scale_not_one"] += 1           # cross-check series only (see X985)
                    sc = sc / (sc[v[-1]] / raw[v[-1]])
                ev = []
                for r_, typ, ref, fac in sev[j]:
                    t = str(typ)
                    st["split_types"][t] = st["split_types"].get(t, 0) + 1
                    if "OCCUR" in t.upper() or float(ref) > 0:
                        ev.append((r_, float(fac)))
                de = [(r_, float(amt), float(ref)) for r_, amt, ref in dev[j]]
                st["dividend_events"] += len(de)
                mult, s1 = XP.split_multiplier(raw, sc, ev)
                for k2, v2 in s1.items():
                    st["split"][k2] += v2
                dm = XP.dividend_multiplier(D, de)
                O[:, i + j] = a["open"][:, j] * mult
                Hh[:, i + j] = a["high"][:, j] * mult
                L[:, i + j] = a["low"][:, j] * mult
                Cl[:, i + j] = raw * mult
                vol = a["volume"][:, j]
                st["volume_missing_rows"] += int((np.isfinite(raw) & ~np.isfinite(vol)).sum())
                V[:, i + j] = vol / mult
                TRC[:, i + j] = raw * mult * dm
                TRO[:, i + j] = a["open"][:, j] * mult * dm
                sm, bg = XP.factor_steps(sc, raw * mult * dm)
                st["factor_steps_small"] += sm
                st["factor_steps_big"] += bg
                st["stocks_with_factor_steps"] += int(sm + bg > 0)
                st["large_distributions"] += sum(1 for _, amt, ref in de if ref > 0 and amt / ref > XP.LARGE_DISTRIBUTION)
                self.h_events[i + j] = (ev, de)
        if st["late_rows"]:
            raise Exception("X987: history returned data after 2017-12-29")
        st["panel_s"] = round(time.perf_counter() - t0, 1)
        t1 = time.perf_counter()
        T = HP.ScoreTable(cal, rows, elig, mcap, sector, O, Hh, L, Cl, V, TRC, TRO)
        st["score_table_s"] = round(time.perf_counter() - t1, 1)
        st["snapshots"] = int(T.scored.sum())
        self.h_cal, self.h_rows, self.h_T = cal, rows, T
        self.h_bars = (O, Hh, L, Cl, V, TRC, TRO)
        st["chart_panel_sha256"] = T.chart_digest()
        st["response_panel_sha256"] = T.response_digest()
        st["decisions"] = int(K)
        st["decision_first_last"] = [str(np.datetime64(int(cal[rows[0]]), "D")), str(np.datetime64(int(cal[rows[-1]]), "D"))]
        st["fwd_end_last_decision"] = str(np.datetime64(int(cal[rows[-1] + HP.H_PRIMARY]), "D"))
        r13 = rows[rows + HP.H_DIAG <= D - 1]
        st["decisions_13w"] = int(r13.size)
        st["fwd13_end_last_decision"] = str(np.datetime64(int(cal[r13[-1] + HP.H_DIAG]), "D"))
        st["eligible_per_decision"] = [int(x) for x in T.eligible]
        st["scored_per_decision"] = [int(x) for x in T.scored.sum(axis=1)]
        st["exclusions_total"] = {e: int(v.sum()) for e, v in T.excl.items()}
        self.h_st["panel"] = st

    # ---------------------------------------------------------------- end
    def qr_on_end(self):
        self._build_panel()
        T = self.h_T
        D = self.h_cal.size
        self.h_dates = T.dates("y")
        self.h_dates13 = T.dates("y13", max_row=D - 1 - HP.H_DIAG)
        if self.h_mode == "canary":
            self._canary(T)
        elif self.h_mode == "null":
            self._null()
        else:
            self._real(T)
        self.h_st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.h_st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as e:
            self.h_st["max_rss_mb"] = f"unavailable: {type(e).__name__}"
        self._qr_log("QRX987|summary|" + json.dumps(_r(self.h_st), sort_keys=True, default=str))

    @staticmethod
    def _world_line(s):
        return dict(t_ic=s["t_ic"], t_inc=s["t_inc"], ic=s["ic_mean"], inc=s["inc_mean"], high=s["high_ann"],
                    low=s["low_ann"], mono=s["mono"], halves=s["halves"], blk=s["block_max"])

    def _null(self):
        t0 = time.perf_counter()
        prep = HS.prepare(self.h_dates)
        for seed in self.h_seeds:
            s = HS.run_world(prep, seed=seed)
            self._qr_log(f"N|{seed}|" + json.dumps(_r(self._world_line(s), 10), sort_keys=True))
        self.h_st["null"] = dict(seeds=[self.h_seeds[0], self.h_seeds[-1]], worlds=len(self.h_seeds),
                                 world_s=round(time.perf_counter() - t0, 1), dates=len(prep))

    def _real(self, T):
        p = self.qr_params
        self.h_st["provenance"] = {k: p[k] for k in PROVENANCE}
        if self.h_st["panel"]["chart_panel_sha256"] != p["chart_panel_sha256"]:
            raise Exception("X987: the chart panel differs from the one the null was calibrated on; nothing computed")
        t0 = time.perf_counter()
        prep = HS.prepare(self.h_dates)
        s = HS.run_world(prep, keep_series=True)                       # the primary result first
        c = dict(t_ic=float(p["c_ic"]), t_inc=float(p["c_inc"]))
        gates = HS.promotion(s, c)
        pub = {k: v for k, v in s.items() if not k.startswith("_")}
        self._qr_log("R|" + json.dumps(_r(dict(summary=pub, gates=gates, c=c), 10), sort_keys=True))
        ser = [dict(day=d["day"], ic=x["ic"], inc=x["inc"], g=x["g"], n=x["n"], high=x["high"], low=x["low"])
               for d, x in zip([dd for dd in self.h_dates if np.isfinite(dd["y"]).sum() >= 20], s["_series"])]
        self._qr_log("RS|" + json.dumps(_r(ser, 8), sort_keys=True))
        diag = dict(score_distribution=HD.score_distribution(T, self.h_dates),
                    condition_frequencies=HD.condition_frequencies(T, self.h_dates),
                    relationships=HD.relationships(T, self.h_dates),
                    sector=HD.sector_diagnostic(T, prep, self.h_dates, None),
                    evaluation_counts=[int(np.isfinite(d["y"]).sum()) for d in self.h_dates])
        self._qr_log("RD|" + json.dumps(_r(diag, 8), sort_keys=True))
        # NON-GATING DIAGNOSTIC: 13-week horizon, computed only after the primary result
        s13 = HS.run_world(HS.prepare(self.h_dates13, "y13"), lag=HS.DIAG_NW_LAG, ann=HS.ANN_DIAG)
        self._qr_log("R13|" + json.dumps(_r({k: v for k, v in s13.items() if not k.startswith("_")}, 10),
                                          sort_keys=True))
        self.h_st["real"] = dict(decisions=len(s["_years"]), world_s=round(time.perf_counter() - t0, 1))

    # ---------------------------------------------------------------- canary (no response-linked real-score statistic)
    def _pit_bars(self, sym, t_day, start_day):
        """Independent point-in-time path: a fresh RAW history request for one stock ending at the decision day and the
        split events up to it (simple factor application, no SCALED_RAW verification); split-adjusted bars + volume."""
        d1 = datetime.utcfromtimestamp(int(t_day) * 86400) + timedelta(days=1)
        d0 = datetime.utcfromtimestamp(int(start_day) * 86400)
        h = self.history([sym], d0, d1, Resolution.DAILY, fill_forward=False,
                         data_normalization_mode=DataNormalizationMode.RAW)
        if h is None or h.empty:
            return None
        days = XP.session_days(h.index.get_level_values(-1).values)
        keep = days <= t_day
        days = days[keep]
        f = {k: h[k].to_numpy(dtype=float)[keep] for k in ("open", "high", "low", "close", "volume")}
        sp = self.history(Split, [sym], d0, d1)
        mult = np.ones(days.size)
        if sp is not None and not sp.empty:
            ed = XP.event_days(sp.index.get_level_values(-1).values)
            for e, typ, ref, fac in zip(ed, sp["type"].tolist(), sp["referenceprice"].tolist(), sp["splitfactor"].tolist()):
                if e <= t_day and ("OCCUR" in str(typ).upper() or float(ref) > 0):
                    mult[days < e] *= float(fac)
        wk = HP.iso_week_ids(days)
        return days, f["open"] * mult, f["high"] * mult, f["low"] * mult, f["close"] * mult, f["volume"] / mult, wk

    def _canary(self, T):
        ck = {}
        cal, rows = self.h_cal, self.h_rows
        D = cal.size
        rng = np.random.default_rng(20261005)
        st = self.h_st["panel"]
        # 1. calendar and decisions
        wk = HP.iso_week_ids(cal)
        ck["decisions_are_week_ends"] = bool(all(wk[r] != wk[r + 1] for r in rows))
        nxt = HP.week_end_rows(cal)
        later = nxt[nxt > rows[-1]]
        ck["last_decision_is_maximal"] = bool(later.size == 0 or later[0] + HP.H_PRIMARY > D - 1)
        ck["first_decision_is_first_week_end_2010"] = st["decision_first_last"][0] == "2010-01-08"
        ck["eligible_min_max_mean"] = [int(T.eligible.min()), int(T.eligible.max()), float(T.eligible.mean())]
        sc = T.scored.sum(axis=1)
        ck["scored_min_max_mean"] = [int(sc.min()), int(sc.max()), float(sc.mean())]
        ev = [int(np.isfinite(d["y"]).sum()) for d in self.h_dates]
        ck["evaluated_min_max_mean"] = [int(min(ev)), int(max(ev)), float(np.mean(ev))]
        yrs = {}
        for d, e in zip(self.h_dates, ev):
            yrs.setdefault(d["year"], []).append(e)
        ck["evaluated_mean_by_year"] = {str(y): float(np.mean(v)) for y, v in sorted(yrs.items())}
        # 2. history requirement and coverage
        nb = T.nbars[T.scored]
        ck["min_bars_scored"] = int(nb.min())
        ck["coverage"] = dict(eligible=int(T.eligible.sum()), scored=int(T.scored.sum()),
                              exclusions={e: int(v.sum()) for e, v in T.excl.items()})
        # 3. independent slow recomputation (fresh point-in-time history ending at t) + response accounting
        pairs = np.argwhere(T.scored)
        pick = pairs[rng.choice(len(pairs), size=min(SLOW_SAMPLE, len(pairs)), replace=False)]
        sl = dict(n=0, exact=0, max_rel=0.0, missing=0, digest_panel=hashlib.sha256(), digest_pit=hashlib.sha256())
        rs = dict(n=0, max_abs=0.0, nan_mismatch=0, with_dividend=0, with_split=0, delisted_in_window=0,
                  scaled_raw_max_abs=None)
        O, Hh, L, Cl, V, TRC, TRO = self.h_bars
        for k, j in sorted(map(tuple, pick)):
            t = int(rows[k])
            sym = self.h_sym[self.h_sids[j]]
            crows = HP.clean_rows(O[:, j], Hh[:, j], L[:, j], Cl[:, j])
            a, _ = HP.stock_snapshot(O[:, j], Hh[:, j], L[:, j], Cl[:, j], V[:, j], T.wk, crows, t)
            pb = self._pit_bars(sym, int(cal[t]), int(cal[max(0, t - 800)]) if t >= 800 else int(cal[0]))
            sl["n"] += 1
            if pb is None or a is None:
                sl["missing"] += 1
                continue
            days, o2, h2, l2, c2, v2, wk2 = pb
            ok = np.isfinite(o2) & np.isfinite(h2) & np.isfinite(l2) & np.isfinite(c2) & (c2 > 0) & (o2 > 0) & \
                (h2 > 0) & (l2 > 0)
            sel = np.flatnonzero(ok)[-C.HIST_SESSIONS:]
            try:
                b = C.snapshot(o2[sel], h2[sel], l2[sel], c2[sel], np.nan_to_num(v2[sel]), wk2[sel])
            except Exception:
                sl["missing"] += 1
                continue
            ex, rel = HP.compare_scale_free(HP.scale_free(a), HP.scale_free(b))
            sl["exact"] += int(ex)
            sl["max_rel"] = max(sl["max_rel"], rel)
            sl["digest_panel"].update(json.dumps(C.canonical(HP.scale_free(a))["conditions"], sort_keys=True).encode())
            sl["digest_pit"].update(json.dumps(C.canonical(HP.scale_free(b))["conditions"], sort_keys=True).encode())
            # response accounting: panel TSR vs an independent recomputation from RAW prices + event lists
            evs, des = self.h_events[j]
            trows = np.flatnonzero(np.isfinite(TRC[:, j]) & (TRC[:, j] > 0))
            for h, key in ((HP.H_PRIMARY, "y"), (HP.H_DIAG, "y13")):
                if t + h > D - 1:
                    continue
                y_panel = HP.response(TRC[:, j], TRO[:, j], trows, t, h)
                y_slow = self._slow_response(sym, cal, t, h)
                rs["n"] += 1
                if np.isfinite(y_panel) != np.isfinite(y_slow):
                    rs["nan_mismatch"] += 1
                elif np.isfinite(y_panel):
                    rs["max_abs"] = max(rs["max_abs"], abs(y_panel - y_slow))
                rs["with_dividend"] += int(any(t + 1 < b_ <= t + h for b_, _, _ in des))
                rs["with_split"] += int(any(t + 1 < b_ <= t + h for b_, _ in evs))
                rs["delisted_in_window"] += int(trows.size and trows[-1] < t + h)
        sl["digest_panel"], sl["digest_pit"] = sl["digest_panel"].hexdigest(), sl["digest_pit"].hexdigest()
        ck["slow_recomputation"] = sl
        ck["slow_response"] = rs
        # 4. response accounting over the whole panel (no score involved): dividends raise TSR above price return
        acc = dict(windows=0, with_dividend=0, tsr_ge_price=0, mean_tsr_minus_price=0.0, delisted_in_window=0)
        diffs = []
        for d in self.h_dates:
            k, t = d["k"], d["row"]
            for j in d["ids"][np.isfinite(d["y"])]:
                evs, des = self.h_events[int(j)]
                acc["windows"] += 1
                trows = np.flatnonzero(np.isfinite(TRC[:, j]) & (TRC[:, j] > 0))
                if trows[-1] < t + HP.H_PRIMARY:
                    acc["delisted_in_window"] += 1
                if any(t + 1 < b_ <= t + HP.H_PRIMARY for b_, _, _ in des):
                    acc["with_dividend"] += 1
                    e = trows[HP.last_valid(trows, t + HP.H_PRIMARY)]
                    pr = Cl[e, j] / O[t + 1, j] - 1.0
                    tsr = TRC[e, j] / TRO[t + 1, j] - 1.0
                    acc["tsr_ge_price"] += int(tsr >= pr - 1e-12)
                    diffs.append(tsr - pr)
        acc["mean_tsr_minus_price"] = float(np.mean(diffs)) if diffs else None
        acc["max_tsr_minus_price"] = float(np.max(diffs)) if diffs else None
        ck["response_accounting"] = acc
        # 5. sector availability (point-in-time SEC SIC -> FF12) over the evaluation observations
        cov = {}
        for d in self.h_dates:
            labs = [T.sector[d["k"]][int(j)] for j in d["ids"]]
            cov.setdefault(d["year"], []).append(1.0 - labs.count("Unclassified") / max(len(labs), 1))
        ck["sector_classified_share_by_year"] = {str(y): float(np.mean(v)) for y, v in sorted(cov.items())}
        # 6. placebo chart side (seeded, independent of everything) and planted response
        prep = HS.prepare(self.h_dates)
        pl = []
        for p_ in prep:
            q = rng.integers(-1, 21, p_["rq"].size)
            pl.append(q)
        placebo = []
        for p_, q in zip(prep, pl):
            p2 = dict(p_)
            p2["rq"] = HD.X.avg_rank(q.astype(float))
            p2["G"] = np.where(q < 0, 0, np.where(q <= 5, 1, np.where(q <= 10, 2, np.where(q <= 15, 3, 4))))
            placebo.append(p2)
        sp = HS.run_world(placebo)
        ck["placebo"] = dict(t_ic=sp["t_ic"], t_inc=sp["t_inc"], ic=sp["ic_mean"], mono=sp["mono"])
        planted = []
        for p_ in prep:
            p2 = dict(p_)
            p2["rq"] = p_["ry"].copy()                       # Q := the response's own rank
            q = np.floor(21 * (p_["ry"] - 0.5) / p_["ry"].size).astype(int)
            p2["G"] = np.where(q <= 5, 1, np.where(q <= 10, 2, np.where(q <= 15, 3, 4)))
            planted.append(p2)
        sm = HS.run_world(planted, keep_series=True)
        ics = [x["ic"] for x in sm["_series"]]
        sn = HS.run_world(planted, seed=900001)
        ck["planted"] = dict(ic_min=min(ics), ic_mean=float(np.mean(ics)), t_ic=sm["t_ic"], t_inc=sm["t_inc"],
                             mono=sm["mono"], null_t_ic=sn["t_ic"], null_t_inc=sn["t_inc"])
        # 7. null determinism and timing (seeds outside 1..5000; digests and seconds only)
        n = int(self.qr_params.get("timing_worlds", 10))
        t0 = time.perf_counter()
        dg = [self._digest(HS.run_world(prep, seed=900001 + i)) for i in range(n)]
        ck["null_world_s"] = (time.perf_counter() - t0) / max(n, 1)
        ck["null_repeat_identical"] = self._digest(HS.run_world(prep, seed=900001)) == dg[0]
        ck["null_digest_900001"] = dg[0]
        ck["null_world_s_1000"] = ck["null_world_s"] * 1000
        ck["chart_panel_repeat_identical"] = T.chart_digest() == st["chart_panel_sha256"]
        self._qr_log("K|" + json.dumps(_r(ck, 8), sort_keys=True, default=str))

    def _slow_response(self, sym, cal, t, h):
        """Fresh RAW history over the window plus the split and dividend events inside it (no panel arrays)."""
        d0 = datetime.utcfromtimestamp(int(cal[t + 1]) * 86400)
        d1 = datetime.utcfromtimestamp(int(cal[t + h]) * 86400) + timedelta(days=1)
        hh = self.history([sym], d0, d1, Resolution.DAILY, fill_forward=False,
                          data_normalization_mode=DataNormalizationMode.RAW)
        if hh is None or hh.empty:
            return float("nan")
        days = XP.session_days(hh.index.get_level_values(-1).values)
        pos = np.searchsorted(cal, days)
        ok = (pos < cal.size) & (cal[np.minimum(pos, cal.size - 1)] == days)
        D = cal.size
        rc, ro = np.full(D, np.nan), np.full(D, np.nan)
        rc[pos[ok]] = hh["close"].to_numpy(dtype=float)[ok]
        ro[pos[ok]] = hh["open"].to_numpy(dtype=float)[ok]
        rws = np.flatnonzero(np.isfinite(rc) & (rc > 0))
        splits, divs = [], []
        sp = self.history(Split, [sym], d0 - timedelta(days=5), d1)
        if sp is not None and not sp.empty:
            ed = XP.event_days(sp.index.get_level_values(-1).values)
            for e, typ, ref, fac in zip(ed, sp["type"].tolist(), sp["referenceprice"].tolist(), sp["splitfactor"].tolist()):
                if "OCCUR" in str(typ).upper() or float(ref) > 0:
                    splits.append((int(np.searchsorted(cal, e)), float(fac)))
        dv = self.history(Dividend, [sym], d0 - timedelta(days=5), d1)
        if dv is not None and not dv.empty:
            ed = XP.event_days(dv.index.get_level_values(-1).values)
            for e, amt, ref in zip(ed, dv["distribution"].tolist(), dv["referenceprice"].tolist()):
                divs.append((int(np.searchsorted(cal, e)), float(amt), float(ref)))
        return HP.response_slow(rc, ro, splits, divs, t, h, rws)

    @staticmethod
    def _digest(s):
        hh = hashlib.sha256()
        hh.update(np.asarray([s["t_ic"], s["t_inc"], s["ic_mean"], s["inc_mean"], s["mono"]], float).tobytes())
        return hh.hexdigest()
