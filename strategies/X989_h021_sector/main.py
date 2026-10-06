# X989 — H021-A sector relative-momentum falsification host (research/phase6/H021A_spec.md v1; owner D160).
# NON-TRADING: no orders are ever placed and no universe is selected. At the end of a one-month run the daily panel of
# the nine original Select Sector SPDRs (+ SPY for the calendar and one NON-GATING diagnostic) is assembled from history
# 1998-12-01 .. 2017-12-31 (RAW bars x QuantConnect's split and dividend feeds = total-return closes / opens, the H019
# construction; SCALED_RAW verifies split boundaries, ADJUSTED is an independent cross-check), then only the frozen
# module qr_h021 is called. Only aggregates leave QuantConnect (summary statistics); no price is exported.
# Modes (params.mode):
#   canary : E989-01 fidelity canary. Publishes NO real IC and no other signal-response statistic.
#   null   : derangement worlds params.seeds = [first, last] (complete evaluation per world); per-world statistics.
#   real   : the one real evaluation (identity world); needs the pinned null provenance and refuses to compute anything
#            if the signal / response panel differs from the one the null was calibrated on.
from AlgorithmImports import *
from datetime import datetime, timedelta
import json
import time
import numpy as np
from qr_harness import QRAlgorithm
import qr_h021 as H
import qr_xs_panel as XP

HIST_START = datetime(1998, 12, 1)
HIST_END = datetime(2017, 12, 31)
LAST_SESSION = np.datetime64("2017-12-29").astype(np.int64)
TICKERS = H.UNIVERSE + ("SPY",)
PROVENANCE = ("threshold_c", "threshold_commit", "null_result_sha256", "spec_sha256", "panel_sha256", "diag_sha256")
TRUNC_SAMPLE = 12


def _r(x, n=8):
    if isinstance(x, (np.floating,)):
        x = float(x)
    if isinstance(x, float):
        return float(f"{x:.{n}g}") if np.isfinite(x) else None
    if isinstance(x, (list, tuple)):
        return [_r(v, n) for v in x]
    if isinstance(x, dict):
        return {str(k): _r(v, n) for k, v in x.items()}
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def _ds(day):
    return str(np.datetime64(int(day), "D"))


def _dt(day):
    return datetime.utcfromtimestamp(int(day) * 86400)


class H021Sector(QRAlgorithm):
    def qr_initialize(self):
        p = self.qr_params
        self.h_mode = p["mode"]
        if self.h_mode not in ("canary", "null", "real"):
            raise Exception(f"X989: unknown mode {self.h_mode!r}")
        if self.qr["end"] > "2017-12-31":
            raise Exception("X989: H021-A runs end on or before 2017-12-31")
        if self.h_mode == "null":
            a, b = p["seeds"]
            if not (1 <= a <= b <= H.R_NULL):
                raise Exception("X989: null seeds must lie in 1..5000")
            self.h_seeds = list(range(int(a), int(b) + 1))
        if self.h_mode == "real":
            for k in PROVENANCE:
                if k not in p:
                    raise Exception(f"X989: real mode needs the pinned null provenance ({k})")
        self._qr_log_budget = 5000
        self.t0 = time.perf_counter()
        self.h_st = {}

    def qr_select_universe(self, eligible):
        return []

    # ---------------------------------------------------------------- history helpers
    def _bars(self, sym, cal, mode, d0=HIST_START, d1=HIST_END):
        D = cal.size
        c, o = np.full(D, np.nan), np.full(D, np.nan)
        h = self.history([sym], d0, d1, Resolution.DAILY, fill_forward=False, data_normalization_mode=mode)
        if h is None or h.empty:
            return c, o, dict(bars=0, late=0, unknown=0)
        days = XP.session_days(h.index.get_level_values(-1).values)
        late = int((days > LAST_SESSION).sum())
        pos = np.searchsorted(cal, days)
        pc = np.minimum(pos, D - 1)
        ok = (cal[pc] == days) & (days <= LAST_SESSION)
        if np.unique(pc[ok]).size != int(ok.sum()):
            raise Exception("X989: two bars map to one session")
        c[pc[ok]] = h["close"].to_numpy(dtype=float)[ok]
        o[pc[ok]] = h["open"].to_numpy(dtype=float)[ok]
        return c, o, dict(bars=int(ok.sum()), late=late, unknown=int((~ok).sum()) - late,
                          first=_ds(days[ok][0]) if ok.any() else None)

    def _events(self, sym, cal, d0=HIST_START, d1=HIST_END, upto=LAST_SESSION):
        """Split events [(row, f)] and distributions {row: [(amount, reference)]} with event day <= upto."""
        splits, divs, late, types = [], {}, 0, {}
        sp = self.history(Split, [sym], d0, d1)
        if sp is not None and not sp.empty:
            ed = XP.event_days(sp.index.get_level_values(-1).values)
            for e, typ, ref, fac in zip(ed, sp["type"].tolist(), sp["referenceprice"].tolist(),
                                        sp["splitfactor"].tolist()):
                t = str(typ)
                types[t] = types.get(t, 0) + 1
                if e > upto:
                    late += 1
                    continue
                if "OCCUR" in t.upper() or float(ref) > 0:
                    splits.append((int(np.searchsorted(cal, e)), float(fac)))
        dv = self.history(Dividend, [sym], d0, d1)
        if dv is not None and not dv.empty:
            ed = XP.event_days(dv.index.get_level_values(-1).values)
            for e, amt, ref in zip(ed, dv["distribution"].tolist(), dv["referenceprice"].tolist()):
                if e > upto:
                    late += 1
                    continue
                divs.setdefault(int(np.searchsorted(cal, e)), []).append((float(amt), float(ref)))
        return splits, divs, late, types

    # ---------------------------------------------------------------- panel
    def _build(self):
        t0 = time.perf_counter()
        spy = Symbol.create("SPY", SecurityType.EQUITY, Market.USA)
        hs = self.history([spy], HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                          data_normalization_mode=DataNormalizationMode.RAW)
        cal = np.unique(XP.session_days(hs.index.get_level_values(-1).values))
        cal = cal[cal <= LAST_SESSION]
        D, N = cal.size, len(TICKERS)
        st = dict(sessions=D, first_session=_ds(cal[0]), last_session=_ds(cal[-1]), tickers={})
        RC, RO, P, O, A = (np.full((D, N), np.nan) for _ in range(5))
        self.h_ev = []
        self.h_sym = []
        self.h_first = []
        for j, tk in enumerate(TICKERS):
            sym = Symbol.create(tk, SecurityType.EQUITY, Market.USA)
            self.h_sym.append(sym)
            rc, ro, s1 = self._bars(sym, cal, DataNormalizationMode.RAW)
            sc, _, s2 = self._bars(sym, cal, DataNormalizationMode.SCALED_RAW)
            ad, _, s3 = self._bars(sym, cal, DataNormalizationMode.ADJUSTED)
            splits, divs, late_ev, types = self._events(sym, cal)
            v = np.flatnonzero(np.isfinite(rc) & np.isfinite(sc) & (rc > 0) & (sc > 0))
            if v.size and abs(sc[v[-1]] / rc[v[-1]] - 1.0) > 1e-6:
                sc = sc / (sc[v[-1]] / rc[v[-1]])
            mult, ss = XP.split_multiplier(rc, sc, splits)
            dm = XP.dividend_multiplier(D, [(b, a, r) for b, lst in divs.items() for a, r in lst])
            RC[:, j], RO[:, j], A[:, j] = rc, ro, ad
            P[:, j], O[:, j] = rc * mult * dm, ro * mult * dm
            self.h_ev.append(({b: f for b, f in splits}, divs))
            fb = np.flatnonzero(np.isfinite(rc) & (rc > 0))
            first = int(fb[0]) if fb.size else D
            miss = np.flatnonzero(~(np.isfinite(rc) & (rc > 0) & np.isfinite(ro) & (ro > 0)))
            miss = miss[miss > first]
            st["tickers"][tk] = dict(
                bars=s1["bars"], first_bar=s1["first"], last_bar=_ds(cal[fb[-1]]) if fb.size else None,
                late_rows=s1["late"] + s2["late"] + s3["late"] + late_ev, unknown_rows=s1["unknown"],
                missing_sessions_after_first=int(miss.size), missing_days=[_ds(cal[m]) for m in miss[:10]],
                adjusted_bars=s3["bars"], split_events=len(splits), split_check=ss, split_types=types,
                distributions=sum(len(x) for x in divs.values()),
                large_distributions=[[_ds(cal[b]), a / r] for b, lst in sorted(divs.items()) for a, r in lst
                                     if r > 0 and a / r > 0.05])
            self.h_first.append(first)
        if any(t["late_rows"] for t in st["tickers"].values()):
            raise Exception("X989: history returned data after 2017-12-29")
        months, me = H.month_end_rows(cal)
        ks = H.decision_index(months)
        years = np.array([months[k][0] for k in ks])
        self.h = dict(cal=cal, RC=RC, RO=RO, P=P, O=O, A=A, months=months, me=me, ks=ks, years=years)
        n9 = len(H.UNIVERSE)
        S = H.signal(P[:, :n9], me, ks)
        F1 = H.forward(P[:, :n9], O[:, :n9], me, ks, 1)
        Y1 = H.relative(F1)
        self.h.update(S=S, F1=F1, Y1=Y1)
        k3 = ks[ks + 3 <= len(months) - 1]
        k6 = ks[ks + 6 <= len(months) - 1]
        F3 = H.forward(P[:, :n9], O[:, :n9], me, k3, 3)
        F6 = H.forward(P[:, :n9], O[:, :n9], me, k6, 6)
        Fspy = H.forward(P[:, n9:], O[:, n9:], me, ks, 1)[:, 0]
        self.h.update(k3=k3, k6=k6, F3=F3, F6=F6, Fspy=Fspy)
        st["panel_sha256"] = H.digest(S, Y1)
        st["diag_sha256"] = H.digest(H.signal(P[:, :n9], me, k3), H.relative(F3), H.signal(P[:, :n9], me, k6),
                                     H.relative(F6), Fspy)
        st["decisions"] = int(ks.size)
        st["decision_first_last"] = [_ds(cal[me[ks[0]]]), _ds(cal[me[ks[-1]]])]
        st["signal_base_first"] = _ds(cal[me[ks[0] - H.LOOKBACK]])
        st["response_end_last"] = _ds(cal[me[ks[-1] + 1]])
        st["decisions_3m_6m"] = [int(k3.size), int(k6.size)]
        st["finite"] = bool(np.isfinite(S).all() and np.isfinite(Y1).all() and np.isfinite(F3).all()
                            and np.isfinite(F6).all() and np.isfinite(Fspy).all())
        st["build_s"] = round(time.perf_counter() - t0, 1)
        self.h_st["panel"] = st

    # ---------------------------------------------------------------- end
    def qr_on_end(self):
        self._build()
        if self.h_mode == "canary":
            self._canary()
        elif self.h_mode == "null":
            self._null()
        else:
            self._real()
        self.h_st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        self._qr_log("QRX989|summary|" + json.dumps(_r(self.h_st), sort_keys=True, default=str))

    @staticmethod
    def _line(s):
        return dict(t=s["t_ic"], ic=s["ic_mean"], top=s["top_ann"], mid=s["mid_ann"], bot=s["bot_ann"],
                    h=s["halves"], bs=max(s["block_share"].values()), sum=s["ic_sum"])

    def _null(self):
        h = self.h
        t0 = time.perf_counter()
        for seed in self.h_seeds:
            s = H.null_world(h["S"], h["Y1"], h["years"], seed)
            self._qr_log(f"N|{seed}|" + json.dumps(_r(self._line(s), 10), sort_keys=True))
        self.h_st["null"] = dict(seeds=[self.h_seeds[0], self.h_seeds[-1]], worlds=len(self.h_seeds),
                                 world_s=round(time.perf_counter() - t0, 2))

    def _real(self):
        p, h, st = self.qr_params, self.h, self.h_st["panel"]
        self.h_st["provenance"] = {k: p[k] for k in PROVENANCE}
        if st["panel_sha256"] != p["panel_sha256"] or st["diag_sha256"] != p["diag_sha256"]:
            raise Exception("X989: the panel differs from the one the null was calibrated on; nothing computed")
        c = float(p["threshold_c"])
        s, ic = H.evaluate(h["S"], h["Y1"], h["years"])                 # the primary result first
        g = H.gates(s, c)
        self._qr_log("R|" + json.dumps(_r(dict(summary=s, gates=g, c=c), 10), sort_keys=True))
        order = np.argsort(-h["S"], axis=1, kind="mergesort")
        Y = h["Y1"]
        ser = []
        for j, k in enumerate(h["ks"]):
            ser.append(dict(d=_ds(h["cal"][h["me"][k]]), ic=float(ic[j]),
                            top=float(Y[j, order[j, :3]].mean()), mid=float(Y[j, order[j, 3:6]].mean()),
                            bot=float(Y[j, order[j, 6:]].mean()),
                            top3=[H.UNIVERSE[i] for i in order[j, :3]]))
        self._qr_log("RS|" + json.dumps(_r(ser, 8), sort_keys=True))
        # NON-GATING DIAGNOSTICS (spec section 9), computed only after the primary result
        diag = {}
        months = h["months"]
        for name, (a, b) in zip(("D1_2010_2017", "D2_2005_2017"), H.DIAG_PERIODS):
            sel = np.array([a <= months[k] <= b for k in h["ks"]])
            diag[name] = H.evaluate(h["S"][sel], h["Y1"][sel], h["years"][sel])[0]
        for name, kk, F, hz in (("D3_3m", h["k3"], h["F3"], 3), ("D4_6m", h["k6"], h["F6"], 6)):
            yrs = np.array([months[k][0] for k in kk])
            diag[name] = H.evaluate(H.signal(h["P"][:, :9], h["me"], kk), H.relative(F), yrs, h=hz)[0]
        x = h["F1"].mean(axis=1) - h["Fspy"]
        m, se, t = H.nw_t(x, 0)
        diag["D5_sector_average_vs_spy"] = dict(mean_monthly=m, ann=12 * m, t=t, decisions=int(x.size))
        diag["label"] = "NON-GATING DIAGNOSTIC"
        self._qr_log("RD|" + json.dumps(_r(diag, 10), sort_keys=True))
        self.h_st["real"] = dict(decisions=int(h["ks"].size))

    # ---------------------------------------------------------------- canary (no real IC is published)
    def _canary(self):
        h, st = self.h, self.h_st["panel"]
        cal, me, ks, months = h["cal"], h["me"], h["ks"], h["months"]
        P, O, RC, RO, A = h["P"], h["O"], h["RC"], h["RO"], h["A"]
        n9 = len(H.UNIVERSE)
        ck = {}
        # 1. histories
        ck["all_histories_present"] = all(st["tickers"][t]["bars"] > 0 and st["tickers"][t]["first_bar"] is not None
                                          and st["tickers"][t]["last_bar"] == "2017-12-29" for t in TICKERS)
        ck["first_bars"] = {t: st["tickers"][t]["first_bar"] for t in TICKERS}
        ck["missing_sessions"] = {t: st["tickers"][t]["missing_sessions_after_first"] for t in TICKERS}
        # 2. no ETF before launch
        base = me[ks[0] - H.LOOKBACK]
        ck["earliest_row_used"] = _ds(cal[base])
        ck["no_use_before_launch"] = bool(all(self.h_first[j] <= base for j in range(n9 + 1)))
        rows_used = np.unique(np.r_[me[ks - H.LOOKBACK], me[ks], me[ks + 1], me[h["k3"] + 3], me[h["k6"] + 6]])
        carried = {TICKERS[j]: [_ds(cal[r]) for r in rows_used if not (np.isfinite(RC[r, j]) and RC[r, j] > 0)]
                   for j in range(n9 + 1)}
        ck["used_close_rows_carried_forward"] = {k: v for k, v in carried.items() if v}
        E = H.entry_rows(O, me, ks)
        late = [(TICKERS[j], _ds(cal[me[ks[i]]])) for i, j in zip(*np.nonzero(E != (me[ks] + 1)[:, None]))]
        ck["entries_not_next_session"] = late
        # 3. calendar
        mo = cal.astype("datetime64[D]").astype("datetime64[M]")
        ck["decisions"] = int(ks.size)
        ck["decision_first_last"] = st["decision_first_last"]
        ck["response_end_last"] = st["response_end_last"]
        ck["decisions_are_month_ends"] = bool(all(mo[me[k]] != mo[me[k] + 1] and
                                                  str(mo[me[k]]) == f"{months[k][0]:04d}-{months[k][1]:02d}"
                                                  for k in ks))
        allm = sorted({str(x) for x in mo})
        ck["no_missing_month"] = len(allm) == len(months) and allm[0] == "1998-12" and allm[-1] == "2017-12"
        ck["calendar_ok"] = bool(ks.size == 215 and st["decision_first_last"] == ["2000-01-31", "2017-11-30"]
                                 and st["response_end_last"] == "2017-12-29" and ck["decisions_are_month_ends"]
                                 and ck["no_missing_month"])
        # 4. independent day-by-day recomputation of every signal and response
        worst = dict(signal=0.0, f1=0.0, f3=0.0, f6=0.0, spy=0.0)
        k3, k6 = h["k3"], h["k6"]
        S3, S6 = h["F3"], h["F6"]
        E3, E6 = H.entry_rows(O, me, k3), H.entry_rows(O, me, k6)
        for j in range(n9 + 1):
            sp, dv = self.h_ev[j]
            for i, k in enumerate(ks):
                if j < n9:
                    s = H.slow_total_return(RC[:, j], RO[:, j], sp, dv, me[k - H.LOOKBACK], me[k])
                    worst["signal"] = max(worst["signal"], abs(s - h["S"][i, j]))
                    f = H.slow_total_return(RC[:, j], RO[:, j], sp, dv, E[i, j], me[k + 1], from_open=True)
                    worst["f1"] = max(worst["f1"], abs(f - h["F1"][i, j]))
                else:
                    e = H.entry_rows(O[:, n9:], me, ks[i:i + 1])[0, 0]
                    f = H.slow_total_return(RC[:, j], RO[:, j], sp, dv, e, me[k + 1], from_open=True)
                    worst["spy"] = max(worst["spy"], abs(f - h["Fspy"][i]))
            if j < n9:
                for i, k in enumerate(k3):
                    f = H.slow_total_return(RC[:, j], RO[:, j], sp, dv, E3[i, j], me[k + 3], from_open=True)
                    worst["f3"] = max(worst["f3"], abs(f - S3[i, j]))
                for i, k in enumerate(k6):
                    f = H.slow_total_return(RC[:, j], RO[:, j], sp, dv, E6[i, j], me[k + 6], from_open=True)
                    worst["f6"] = max(worst["f6"], abs(f - S6[i, j]))
        ck["slow_worst_abs"] = worst
        ck["slow_ok"] = bool(max(worst.values()) < 1e-9)
        # 5. distribution accounting vs QuantConnect's ADJUSTED series
        adj = {}
        for j in range(n9 + 1):
            dev, row, nv = H.step_consistency(P[:, j], A[:, j])
            adj[TICKERS[j]] = dict(max_step_dev=dev, at=_ds(cal[row]) if row >= 0 else None, rows=nv)
        Sa = H.signal(A[:, :n9], me, ks)
        sig_adj = float(np.nanmax(np.abs(Sa - h["S"])))
        ck["adjusted_cross_check"] = adj
        ck["signal_vs_adjusted_max_abs"] = sig_adj
        ck["adjusted_ok"] = bool(max(v["max_step_dev"] for v in adj.values()) < 1e-4)
        # 6. XLF 2016 XLRE distribution
        jx = H.UNIVERSE.index("XLF")
        big = [(b, a, r) for b, lst in sorted(self.h_ev[jx][1].items()) for a, r in lst if r > 0 and a / r > 0.10]
        xl = []
        for b, a, r in big:
            pv = b - 1
            while pv > 0 and not np.isfinite(RC[pv, jx]):
                pv -= 1
            xl.append(dict(day=_ds(cal[b]), ratio=a / r, raw_step=RC[b, jx] / RC[pv, jx] - 1.0,
                           tr_step=P[b, jx] / P[pv, jx] - 1.0, adjusted_step=A[b, jx] / A[pv, jx] - 1.0,
                           tr_minus_adjusted=abs(P[b, jx] / P[pv, jx] - A[b, jx] / A[pv, jx])))
        ck["xlf_large_distributions"] = xl
        ck["xlf_2016_ok"] = bool(len(xl) == 1 and xl[0]["day"] == "2016-09-19" and xl[0]["raw_step"] < -0.15
                                 and xl[0]["tr_minus_adjusted"] < 1e-4 and abs(xl[0]["tr_step"]) < 0.05)
        # 7. future perturbation: rows after the decision (signals) / after the window end (responses)
        rng = np.random.default_rng(20261006)
        pert_s = pert_f = 0
        picks = rng.choice(ks.size - 1, size=20, replace=False)
        for i in picks:
            P2, O2 = P[:, :n9].copy(), O[:, :n9].copy()
            cut = me[ks[i]]
            P2[cut + 1:] *= rng.uniform(0.5, 1.5, (P2.shape[0] - cut - 1, n9))
            O2[cut + 1:] *= rng.uniform(0.5, 1.5, (O2.shape[0] - cut - 1, n9))
            pert_s += int(not np.array_equal(H.signal(P2, me, ks[:i + 1]), h["S"][:i + 1]))
            P3, O3 = P[:, :n9].copy(), O[:, :n9].copy()
            cut = me[ks[i] + 1]
            P3[cut + 1:] *= rng.uniform(0.5, 1.5, (P3.shape[0] - cut - 1, n9))
            O3[cut + 1:] *= rng.uniform(0.5, 1.5, (O3.shape[0] - cut - 1, n9))
            pert_f += int(not np.array_equal(H.forward(P3, O3, me, ks[:i + 1], 1), h["F1"][:i + 1]))
        ck["future_perturbation_changed"] = dict(signals=pert_s, responses=pert_f, trials=int(picks.size))
        # 8. truncation: fresh RAW history + events ending at the decision session reproduce the panel signal
        xlf_k = [i for i, k in enumerate(ks) if months[k] == (2016, 9)]
        tr_pick = sorted(set([0, ks.size - 1] + xlf_k + rng.choice(ks.size, size=TRUNC_SAMPLE, replace=False).tolist()))
        tw = 0.0
        tn = after = 0
        for i in tr_pick:
            k = ks[i]
            t_day = int(cal[me[k]])
            d0 = _dt(int(cal[me[k - H.LOOKBACK]]) - 10)
            d1 = _dt(t_day) + timedelta(days=1)
            for j in range(n9):
                rc, ro, _ = self._bars(self.h_sym[j], cal, DataNormalizationMode.RAW, d0, d1)
                after += int(np.isfinite(rc[me[k] + 1:]).sum())
                rc[me[k] + 1:] = np.nan                     # nothing after the decision session is used
                ro[me[k] + 1:] = np.nan
                sp, dv, _, _ = self._events(self.h_sym[j], cal, d0 - timedelta(days=5), d1, upto=t_day)
                s = H.slow_total_return(rc, ro, {b: f for b, f in sp}, dv, me[k - H.LOOKBACK], me[k])
                tw = max(tw, abs(s - h["S"][i, j]))
                tn += 1
        ck["truncation"] = dict(decisions=[_ds(cal[me[ks[i]]]) for i in tr_pick], comparisons=tn, worst_abs=tw,
                                bars_after_decision_returned=after)
        ck["truncation_ok"] = bool(tw < 1e-9)
        # 9. placebo (seeded random signals on the real responses) and planted ranks
        Y = h["Y1"]
        pl = [H.evaluate(rng.normal(size=Y.shape), Y, h["years"])[0]["t_ic"] for _ in range(200)]
        ck["placebo"] = dict(first_t=pl[0], mean_t=float(np.mean(pl)), sd_t=float(np.std(pl)),
                             share_abs_t_gt_2576=float(np.mean(np.abs(pl) > 2.576)), max_abs_t=float(np.max(np.abs(pl))))
        ck["placebo_ok"] = bool(abs(pl[0]) < 4)
        sp_, ic_ = H.evaluate(Y.copy(), Y, h["years"])
        noisy = Y + rng.normal(size=Y.shape) * 3 * float(Y.std())
        ck["planted"] = dict(ic_min=float(ic_.min()), ic_mean=sp_["ic_mean"],
                             monotonic=bool(sp_["top_ann"] > sp_["mid_ann"] > sp_["bot_ann"]),
                             weak_t=H.evaluate(noisy, Y, h["years"])[0]["t_ic"])
        ck["planted_ok"] = bool(ic_.min() > 1 - 1e-12 and ck["planted"]["monotonic"])
        # 10. null determinism (seeds outside 1..5000; digests only)
        dets = []
        for sd in range(900001, 900011):
            p1, p2 = H.derangement(sd), H.derangement(sd)
            dets.append(bool(np.array_equal(p1, p2) and not np.any(p1 == np.arange(9))))
        t0 = time.perf_counter()
        dg = [H.digest(list(self._line(H.null_world(h["S"], Y, h["years"], sd)).values())[:5])
              for sd in range(900001, 900011)]
        ck["null_world_s"] = (time.perf_counter() - t0) / 10
        rep = H.digest(list(self._line(H.null_world(h["S"], Y, h["years"], 900001)).values())[:5])
        ck["null_ok"] = bool(all(dets) and rep == dg[0])
        ck["null_digest_900001"] = dg[0]
        ck["panel_repeat_identical"] = H.digest(H.signal(P[:, :n9], me, ks), H.relative(
            H.forward(P[:, :n9], O[:, :n9], me, ks, 1))) == st["panel_sha256"]
        ck["panel_sha256"], ck["diag_sha256"] = st["panel_sha256"], st["diag_sha256"]
        ck["all_ok"] = bool(ck["all_histories_present"] and ck["no_use_before_launch"] and ck["calendar_ok"]
                            and ck["slow_ok"] and ck["adjusted_ok"] and ck["xlf_2016_ok"]
                            and pert_s == 0 and pert_f == 0 and ck["truncation_ok"] and ck["placebo_ok"]
                            and ck["planted_ok"] and ck["null_ok"] and ck["panel_repeat_identical"]
                            and st["finite"])
        self._qr_log("K|" + json.dumps(_r(ck, 10), sort_keys=True, default=str))
