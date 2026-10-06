# X992 v1.1 (after E992-01): no VIX subscription (availability answered by E992-01; the custom-data subscription
# changed QuantConnect's tradeable-date count and tripped the runner's equity-dates integrity check); itemised
# lists of chart jumps > 50% and of missing sessions restricted to the days a security was ELIGIBLE (with spike-
# reversal, split and large-distribution flags); the average cross-sectional Spearman matrix of the candidate
# technical features (feature-feature overlap only; no return).
# X992 — Phase 7 (P7-CP1, D165) PRICE / TECHNICAL / BREADTH / CORPORATE-ACTION DATA AUDIT (infrastructure; NO
# orders, NO returns after any decision date, NO ranking, NO score). 2010-01-04 .. 2017-12-31 with the history-only
# warm-up from 2008-07-01; the frozen data-v1 universe (>= $2B, >= $5, ADV20 >= $5M, NYSE/Nasdaq, SEC correction
# layer). Nothing after 2017-12-31 is requested.
# During the run: the eligible set of every universe selection from 2010-02-01 (data through the previous close t) is
# recorded. At the end: the daily panel of every security eligible on any of those days is assembled from history
# 2007-01-01 .. 2017-12-31: RAW bars x QuantConnect's split feed = split-adjusted CHART bars (C, H, L, V); x the
# dividend feed as well = TOTAL-RETURN closes P (the H019 / D148 construction; SCALED_RAW verifies split boundaries,
# ADJUSTED cross-checks the distribution accounting). Then:
#   data-error hunt per security (duplicates, order, gaps, zero volume, OHLC consistency, stale runs, unexplained
#     jumps, split verification, factor steps, distributions vs ADJUSTED, spin-offs);
#   eligibility vs bars (stale / after-last-bar eligibility, delistings);
#   candidate technical features at every month-end for every eligible security (availability, history needs);
#   independent point-in-time recomputation of the features on a deterministic sample (fresh history ending at t);
#   daily breadth with point-in-time denominators vs a survivors-only denominator;
#   sector (FF12 from the SEC SIC at filing) group sizes; market-regime input availability (SPY, VIX).
# Outputs: counts, dates, ratios of availability and feature-agreement statistics only (no price, no return).
from AlgorithmImports import *
from datetime import date, datetime, timedelta
import hashlib
import json
import time
import numpy as np
from qr_harness import QRAlgorithm
import qr_p7 as P
import qr_xs_diag as XD
import qr_xs_panel as XP

HIST_START = datetime(2007, 1, 1)
HIST_END = datetime(2017, 12, 31)
LAST_SESSION = np.datetime64("2017-12-29").astype(np.int64)
RECORD_FROM = date(2010, 2, 1)          # first selection whose data reflect the 2010-01-29 close
BATCH = 100
SALT = "P7CP1-alignment"                # the same deterministic sample as X991's alignment lines
SAMPLE_PER_MONTH = 3
EXTRA_SALT = "P7CP1-technical"
EXTRA_PER_MONTH = 1


def _sid(s):
    return str(s.id) if hasattr(s, "id") else str(s)


def _ds(day):
    return str(np.datetime64(int(day), "D"))


def _day(d):
    return int(np.datetime64(d.strftime("%Y-%m-%d")).astype(np.int64))


def _r(x, n=6):
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


def add(h, k, n=1):
    h[k] = h.get(k, 0) + n


class P7PriceAudit(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        self._qr_log_budget = 400000
        if self.qr_sec is None or self.qr_sic is None:
            raise Exception("X992 needs universe.sec_corrections (frozen data infrastructure v1)")
        if self.qr["end"] > "2017-12-31":
            raise Exception("X992: P7-CP1 audits end on or before 2017-12-31")
        self.t0 = time.perf_counter()
        self.sel = {}                    # selection day number -> tuple of eligible sids
        self.sym = {}                    # sid -> Symbol
        self.ff12_m = {}                 # month-end selection day -> {sid: FF12}
        self.month = None
        self.st = {}
        self.vix = {}                    # v1.1: VIX availability was measured by E992-01 (index and CBOE from 2005)

    def _qr_select(self, fundamental):
        fl = list(fundamental)
        out = super()._qr_select(fl)
        today = self.time.date()
        if today >= RECORD_FROM:
            el = []
            for s in self.qr_eligible:
                sid = str(s.id)
                self.sym[sid] = s
                el.append(sid)
            self.sel[_day(today)] = tuple(sorted(el))
            if (today.year, today.month) != self.month:
                self.ff12_m[_day(today)] = {sid: XD.ff12(self.qr_sic.sic_on(sid, today)) for sid in el}
        self.month = (today.year, today.month)
        return out

    def qr_select_universe(self, eligible):
        return []

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
        # order and duplicates per security (the frame is grouped by symbol)
        for j in np.unique(cols[cols >= 0]):
            d = days[cols == j]
            if d.size > 1 and np.any(np.diff(d) < 0):
                st["out_of_order_securities"] += 1
        key = pc[ok] * (n + 1) + cols[ok]
        uk, cnt = np.unique(key, return_counts=True)
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

    def _build(self):
        t0 = time.perf_counter()
        spy = self.history(self.spy, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        cal = np.unique(XP.session_days(spy.index.get_level_values(-1).values))
        cal = cal[cal <= LAST_SESSION]
        D = cal.size
        sids = sorted({s for v in self.sel.values() for s in v})
        N = len(sids)
        st = dict(sessions=D, first_session=_ds(cal[0]), last_session=_ds(cal[-1]), securities=N, late_rows=0,
                  off_calendar_rows=0, out_of_order_securities=0, duplicate_bars=0, late_events=0, history_calls=0,
                  split_types={}, split=dict(n=0, aligned=0, realigned=0, unverified=0, outside=0),
                  dividend_events=0, large_distributions=0, factor_steps_small=0, factor_steps_big=0,
                  securities_with_factor_steps=0, residual_up=0, residual_down=0, last_scale_not_one=0,
                  zero_volume_bars=0, nonpositive_or_nan_ohlc=0, ohlc_inconsistent=0, stale_runs_ge5=0,
                  jumps_gt_50pct=0, jumps_gt_50pct_near_split=0, tr_jumps_gt_50pct=0, missing_inside_life=0,
                  securities_with_missing_inside_life=0, adj_steps=0, adj_dev_nonevent_gt_1e6=0,
                  adj_dev_event_beyond_cent=0, adj_max_dev_nonevent=0.0, securities_adjusted_missing=0)
        C, Hh, L, V, Pt = (np.full((D, N), np.nan) for _ in range(5))
        first, last = np.full(N, -1), np.full(N, -1)
        self.ev = {}
        examples = {}
        for i in range(0, N, BATCH):
            part = sids[i:i + BATCH]
            syms = [self.sym[s] for s in part]
            loc = {s: j for j, s in enumerate(part)}
            n = len(part)
            hr = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.RAW)
            hs = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            ha = self.history(syms, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.ADJUSTED)
            sp = self.history(Split, syms, HIST_START, HIST_END)
            dv = self.history(Dividend, syms, HIST_START, HIST_END)
            st["history_calls"] += 5
            a = self._cols(hr, loc, cal, D, n, ("open", "high", "low", "close", "volume"), st)
            b = self._cols(hs, loc, cal, D, n, ("close",), st)
            ad = self._cols(ha, loc, cal, D, n, ("close",), st)
            sev = self._events(sp, loc, cal, ("type", "referenceprice", "splitfactor"), st)
            dev = self._events(dv, loc, cal, ("distribution", "referenceprice"), st)
            for j in range(n):
                g = i + j
                raw, sc = a["close"][:, j], b["close"][:, j]
                o_, h_, l_, v_ = a["open"][:, j], a["high"][:, j], a["low"][:, j], a["volume"][:, j]
                v = np.flatnonzero(np.isfinite(raw) & (raw > 0))
                if v.size == 0:
                    continue
                first[g], last[g] = v[0], v[-1]
                inside = np.arange(v[0], v[-1] + 1)
                miss = int(np.sum(~(np.isfinite(raw[inside]) & (raw[inside] > 0))))
                st["missing_inside_life"] += miss
                st["securities_with_missing_inside_life"] += int(miss > 0)
                st["zero_volume_bars"] += int(np.sum(v_[v] == 0))
                bad = ~(np.isfinite(o_[v]) & np.isfinite(h_[v]) & np.isfinite(l_[v]) & (o_[v] > 0) & (h_[v] > 0)
                        & (l_[v] > 0))
                st["nonpositive_or_nan_ohlc"] += int(bad.sum())
                inc = (h_[v] < np.maximum(o_[v], raw[v]) * (1 - 1e-6)) | (l_[v] > np.minimum(o_[v], raw[v]) * (1 + 1e-6))
                st["ohlc_inconsistent"] += int(np.sum(inc & ~bad))
                same = (raw[v][1:] == raw[v][:-1]) & (v_[v][1:] == 0)
                run = 0
                for x in same:
                    run = run + 1 if x else 0
                    if run == 4:
                        st["stale_runs_ge5"] += 1
                vv = np.flatnonzero(np.isfinite(raw) & np.isfinite(sc) & (raw > 0) & (sc > 0))
                if vv.size and abs(sc[vv[-1]] / raw[vv[-1]] - 1.0) > 1e-6:
                    st["last_scale_not_one"] += 1
                    sc = sc / (sc[vv[-1]] / raw[vv[-1]])
                ev = []
                for r_, typ, ref, fac in sev[j]:
                    t_ = str(typ)
                    st["split_types"][t_] = st["split_types"].get(t_, 0) + 1
                    if "OCCUR" in t_.upper() or float(ref) > 0:
                        ev.append((r_, float(fac)))
                de = [(r_, float(amt), float(ref)) for r_, amt, ref in dev[j]]
                st["dividend_events"] += len(de)
                det = []
                mult, s1 = XP.split_multiplier(raw, sc, ev, detail=det)
                for k2, v2 in s1.items():
                    st["split"][k2] += v2
                if det and len(examples.setdefault("split_unverified", [])) < 15:
                    examples["split_unverified"].append([part[j]] + [[_ds(cal[min(d[0], D - 1)]), d[1], d[2]] for d in det[:2]])
                dm = XP.dividend_multiplier(D, de)
                Cj = raw * mult
                Pj = raw * mult * dm
                C[:, g], Hh[:, g], L[:, g] = Cj, h_ * mult, l_ * mult
                V[:, g], Pt[:, g] = v_ / mult, Pj
                up, dn = XP.residual_jumps(Cj, Pj)
                st["residual_up"] += up
                st["residual_down"] += dn
                sm, bg = XP.factor_steps(sc, Pj)
                st["factor_steps_small"] += sm
                st["factor_steps_big"] += bg
                st["securities_with_factor_steps"] += int(sm + bg > 0)
                st["large_distributions"] += sum(1 for _, amt, ref in de if ref > 0 and amt / ref > XP.LARGE_DISTRIBUTION)
                # unexplained jumps in the chart series (> 50% day move) and whether a split event is near
                lr = np.abs(np.log(Cj[v][1:] / Cj[v][:-1]))
                jr = v[1:][lr > np.log(1.5)]
                st["jumps_gt_50pct"] += int(jr.size)
                near = sum(1 for r_ in jr if any(abs(r_ - e[0]) <= 2 for e in ev))
                st["jumps_gt_50pct_near_split"] += near
                if jr.size - near and len(examples.setdefault("jumps", [])) < 25:
                    examples["jumps"].append([part[j], [_ds(cal[r_]) for r_ in jr[:3]]])
                ltr = np.abs(np.log(Pj[v][1:] / Pj[v][:-1]))
                st["tr_jumps_gt_50pct"] += int(np.sum(ltr > np.log(1.5)))
                # distributions vs QuantConnect's ADJUSTED series (cent-rounded feed amounts: tolerance per event)
                A = ad["close"][:, j]
                va = np.flatnonzero(np.isfinite(A) & (A > 0) & np.isfinite(Pj) & (Pj > 0))
                if va.size < 2:
                    st["securities_adjusted_missing"] += 1
                else:
                    e = Pj[va] / A[va]
                    dlt = np.abs(e[1:] / e[:-1] - 1)
                    evm = np.zeros(D + 1)
                    for r_ in [x[0] for x in de] + [x[0] for x in ev]:
                        evm[min(r_, D)] = 1.0
                    ce = np.cumsum(evm)
                    is_ev = (ce[va[1:]] - ce[va[:-1]]) > 0          # an event row in (previous valid row, row]
                    tol = 0.0051 / raw[va[:-1]] + 1e-6                # cent-rounded feed amounts (E990-02)
                    bad_ev = is_ev & (dlt > tol)
                    bad_ne = ~is_ev & (dlt > 1e-6)
                    st["adj_steps"] += int(dlt.size)
                    st["adj_dev_event_beyond_cent"] += int(bad_ev.sum())
                    st["adj_dev_nonevent_gt_1e6"] += int(bad_ne.sum())
                    if bad_ne.any():
                        st["adj_max_dev_nonevent"] = max(st["adj_max_dev_nonevent"], float(dlt[bad_ne].max()))
                    for nm, msk in (("adj_event", bad_ev), ("adj_nonevent", bad_ne)):
                        for k3 in np.flatnonzero(msk)[:2]:
                            if len(examples.setdefault(nm, [])) < 20:
                                examples[nm].append([part[j], _ds(cal[va[k3 + 1]]), float(dlt[k3])])
                self.ev[g] = (ev, de)
        if st["late_rows"]:
            raise Exception("X992: history returned data after 2017-12-29")
        st["build_s"] = round(time.perf_counter() - t0, 1)
        st["examples"] = examples
        self.cal, self.sids, self.first, self.last = cal, sids, first, last
        self.C, self.H, self.L, self.V, self.P = C, Hh, L, V, Pt
        self.col = {s: j for j, s in enumerate(sids)}
        self.st["panel"] = st

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        self._build()
        self._eligibility_and_features()
        self._breadth()
        self._fidelity()
        self._regime()
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as e:
            self.st["max_rss_mb"] = f"unavailable: {type(e).__name__}"
        text = json.dumps(_r(self.st), sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRP7P|{i // 9000}|{text[i:i + 9000]}")

    def _t_of(self, sel_day):
        """The session whose close a selection day's data reflect (the last session before it)."""
        k = int(np.searchsorted(self.cal, sel_day)) - 1
        return k

    def _eligibility_and_features(self):
        cal, D = self.cal, self.cal.size
        el = dict(selections=len(self.sel), stock_days=0, eligible_no_bar_at_t=0, eligible_after_last_bar=0,
                  eligible_stale_gt5=0, securities_last_bar_before_end=int(np.sum((self.last >= 0) & (self.last < D - 1))))
        months = {}
        for sd, lst in self.sel.items():
            k = self._t_of(sd)
            for s in lst:
                j = self.col[s]
                el["stock_days"] += 1
                if not (np.isfinite(self.C[k, j]) and self.C[k, j] > 0):
                    el["eligible_no_bar_at_t"] += 1
                    if self.last[j] < k:
                        el["eligible_after_last_bar"] += 1
                    lb = np.flatnonzero(np.isfinite(self.C[:k + 1, j]))
                    if lb.size and k - lb[-1] > P.MAX_LAST_BAR_AGE:
                        el["eligible_stale_gt5"] += 1
        self.st["eligibility"] = el
        # month-end decision rows: the first selection of each month
        msel = sorted(self.ff12_m)
        self.mrows = [(sd, self._t_of(sd)) for sd in msel]
        feat = {}
        sect = {}
        young = {}
        t1 = time.perf_counter()
        per_sec = {}
        for sd, k in self.mrows:
            for s in self.sel[sd]:
                per_sec.setdefault(self.col[s], []).append(k)
        self.featv = {}
        for j, rows in per_sec.items():
            rows = sorted(set(rows))
            F = P.features_at(self.C[:, j], self.H[:, j], self.L[:, j], self.V[:, j], self.P[:, j], rows)
            for i, k in enumerate(rows):
                self.featv[(j, k)] = {f: F[f][i] for f in P.FEATURES}
        for sd, k in self.mrows:
            y = _ds(self.cal[k])[:4]
            Y = feat.setdefault(y, {})
            add(Y, "decisions", 0)
            for s in self.sel[sd]:
                j = self.col[s]
                fv = self.featv[(j, k)]
                add(Y, "eligible")
                nb = int(np.sum(np.isfinite(self.C[:k + 1, j])))
                yc = young.setdefault(y, {})
                add(yc, "eligible")
                if nb < 252:
                    add(yc, "lt252_bars")
                if nb < 504:
                    add(yc, "lt504_bars")
                stale = fv["last_bar_age"] > P.MAX_LAST_BAR_AGE if np.isfinite(fv["last_bar_age"]) else True
                if stale:
                    add(Y, "stale_last_bar")
                for f in P.FEATURES:
                    if f != "last_bar_age" and np.isfinite(fv[f]):
                        add(Y, f"has|{f}")
                if all(np.isfinite(fv[f]) for f in P.FEATURES):
                    add(Y, "has_all_features")
            sc = sect.setdefault(y, {})
            cnt = {}
            for s, g in self.ff12_m[sd].items():
                add(cnt, g)
            for g, n in cnt.items():
                sc.setdefault(g, []).append(n)
        for y in feat:
            feat[y]["decisions"] = sum(1 for sd, k in self.mrows if _ds(self.cal[k])[:4] == y)
        self.st["features"] = feat
        self.st["young"] = young
        # v1.1: feature-feature overlap at month-ends (average cross-sectional Spearman over complete rows)
        names = [f for f in P.FEATURES if f != "last_bar_age"]
        csum, cn = None, 0
        for sd, k in self.mrows:
            X = []
            for s in self.sel[sd]:
                fv = self.featv[(self.col[s], k)]
                row = [fv[f] if f != "adv20_usd" else (np.log(fv[f]) if fv[f] > 0 else np.nan) for f in names]
                if all(np.isfinite(row)):
                    X.append(row)
            if len(X) >= 30:
                X = np.array(X)
                R = np.argsort(np.argsort(X, axis=0), axis=0).astype(float)
                cm = np.corrcoef(R, rowvar=False)
                csum = cm if csum is None else csum + cm
                cn += 1
        self.st["overlap"] = dict(names=names[:-1] + ["log adv20_usd"], dates=cn,
                                  mean_spearman=np.round(csum / cn, 3).tolist() if cn else None)
        # v1.1: itemised data-error lists on ELIGIBLE days only
        erow = {}
        for sd, lst in self.sel.items():
            k = self._t_of(sd)
            for s_ in lst:
                erow.setdefault(self.col[s_], set()).add(k)
        jumps, gaps = [], []
        for j, rws in erow.items():
            c = self.C[:, j]
            v = np.flatnonzero(np.isfinite(c) & (c > 0))
            if v.size < 3:
                continue
            ratio = c[v][1:] / c[v][:-1]
            evs, des = self.ev.get(j, ([], []))
            for i in np.flatnonzero(np.abs(np.log(ratio)) > np.log(1.5)):
                r_ = int(v[i + 1])
                if r_ not in rws and int(v[i]) not in rws:
                    continue
                nxt = ratio[i + 1] if i + 1 < ratio.size else np.nan
                rev = bool(np.isfinite(nxt) and abs(np.log(ratio[i]) + np.log(nxt)) < 0.2 * abs(np.log(ratio[i])))
                jumps.append([self.sids[j], _ds(self.cal[r_]), round(float(ratio[i]), 4), rev,
                              any(abs(r_ - e[0]) <= 2 for e in evs),
                              any(abs(r_ - e[0]) <= 2 and e[2] > 0 and e[1] / e[2] > 0.10 for e in des)])
            inside = np.arange(v[0], v[-1] + 1)
            miss = inside[~(np.isfinite(c[inside]) & (c[inside] > 0))]
            if miss.size:
                me = int(sum(1 for r_ in miss if r_ in rws))
                runs = np.split(miss, np.flatnonzero(np.diff(miss) > 1) + 1)
                gaps.append([self.sids[j], int(miss.size), me, int(max(len(x) for x in runs)), _ds(self.cal[v[0]]),
                             _ds(self.cal[v[-1]]), _ds(self.cal[miss[0]])])
        self.st["jumps_on_eligible_days"] = dict(n=len(jumps), reversed_spikes=sum(1 for x in jumps if x[3]),
                                                 near_split=sum(1 for x in jumps if x[4]),
                                                 near_large_distribution=sum(1 for x in jumps if x[5]),
                                                 items=jumps[:300])
        self.st["missing_sessions_detail"] = dict(securities=len(gaps), on_eligible_days=sum(g[2] for g in gaps),
                                                  items=sorted(gaps, key=lambda g: -g[1])[:120])
        self.st["sector_group_sizes"] = {y: {g: dict(min=min(v), median=float(np.median(v)), max=max(v))
                                             for g, v in sorted(d.items())} for y, d in sorted(sect.items())}
        self.st["features_s"] = round(time.perf_counter() - t1, 1)

    def _breadth(self):
        t1 = time.perf_counter()
        D, N = self.cal.size, len(self.sids)
        S = {k: np.full((D, N), np.nan, dtype=np.float32) for k in ("above50", "above200", "new_high", "new_low")}
        for j in range(N):
            cs = P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])
            for k in S:
                S[k][:, j] = cs[k]
        last_day_set = set(self.sel[max(self.sel)])
        surv = np.array([s in last_day_set for s in self.sids])
        dead = (self.last >= 0) & (self.last < D - 1)
        res = {k: {} for k in S}
        diffs = {k: [] for k in S}
        month_vals = {}
        dead_days = 0
        mset = {k for _, k in self.mrows}
        for sd in sorted(self.sel):
            k = self._t_of(sd)
            cols = np.array([self.col[s] for s in self.sel[sd]], dtype=int)
            if cols.size == 0:
                continue
            dead_days += int(dead[cols].sum())
            y = _ds(self.cal[k])[:4]
            for key, arr in S.items():
                x = arr[k, cols]
                ok = np.isfinite(x)
                val = float(x[ok].mean()) if ok.any() else float("nan")
                xs = x[ok & surv[cols]]
                sv = float(xs.mean()) if xs.size else float("nan")
                cell = res[key].setdefault(y, [0, 0.0, 1.0, 0.0, 0])   # days, sum, min, max, insufficient
                cell[0] += 1
                cell[1] += val
                cell[2] = min(cell[2], val)
                cell[3] = max(cell[3], val)
                cell[4] += int((~ok).sum())
                if np.isfinite(sv):
                    diffs[key].append(val - sv)
                if k in mset and key in ("above200", "above50"):
                    month_vals.setdefault(key, []).append([_ds(self.cal[k]), round(val, 4), int(ok.sum()), int(cols.size)])
        self.st["breadth"] = {key: {y: dict(days=c[0], mean=c[1] / c[0], min=c[2], max=c[3],
                                            insufficient_per_day=c[4] / c[0]) for y, c in v.items()}
                              for key, v in res.items()}
        self.st["breadth_survivor_bias"] = {key: dict(mean=float(np.mean(d)), mean_abs=float(np.mean(np.abs(d))),
                                                      max_abs=float(np.max(np.abs(d))), days=len(d))
                                            for key, d in diffs.items() if d}
        self.st["breadth_monthly"] = month_vals
        self.st["breadth_dead_stock_days_in_denominator"] = dead_days
        self.st["breadth_s"] = round(time.perf_counter() - t1, 1)

    def _fresh(self, sym, k):
        """Independent point-in-time path: a fresh RAW history request for one security ending at session k plus
        its split and dividend events up to that day; split / total-return adjustment applied directly per event
        (no SCALED_RAW verification, no multiplier arrays). Returns (bars [(c, h, l, v, p)], last bar day, events)."""
        t_day = int(self.cal[k])
        d1 = datetime.utcfromtimestamp(t_day * 86400) + timedelta(days=1)
        d0 = datetime.utcfromtimestamp(int(self.cal[max(0, k - 450)]) * 86400)
        h = self.history([sym], d0, d1, Resolution.DAILY, fill_forward=False,
                         data_normalization_mode=DataNormalizationMode.RAW)
        if h is None or h.empty:
            return None, None, 0
        days = XP.session_days(h.index.get_level_values(-1).values)
        keep = days <= t_day
        days = days[keep]
        o, hi, lo, c, vol = (h[x].to_numpy(dtype=float)[keep] for x in ("open", "high", "low", "close", "volume"))
        fac = np.ones(days.size)
        div = np.ones(days.size)
        nev = 0
        sp = self.history(Split, [sym], d0 - timedelta(days=5), d1)
        if sp is not None and not sp.empty and {"type", "referenceprice", "splitfactor"} <= set(sp.columns):
            ed = XP.event_days(sp.index.get_level_values(-1).values)
            for e, typ, ref, f in zip(ed, sp["type"].tolist(), sp["referenceprice"].tolist(), sp["splitfactor"].tolist()):
                if e <= t_day and ("OCCUR" in str(typ).upper() or float(ref) > 0):
                    fac[days < e] *= float(f)
                    nev += 1
        dv = self.history(Dividend, [sym], d0 - timedelta(days=5), d1)
        if dv is not None and not dv.empty and {"distribution", "referenceprice"} <= set(dv.columns):
            ed = XP.event_days(dv.index.get_level_values(-1).values)
            for e, amt, ref in zip(ed, dv["distribution"].tolist(), dv["referenceprice"].tolist()):
                if e <= t_day and float(ref) > 0 and 0 < float(amt) < float(ref):
                    div[days < e] *= 1.0 - float(amt) / float(ref)
                    nev += 1
        bars = [(c[i] * fac[i], hi[i] * fac[i], lo[i] * fac[i], vol[i] / fac[i], c[i] * fac[i] * div[i])
                for i in range(days.size)]
        return bars, (int(days[-1]) if days.size else None), nev

    def _fidelity(self):
        t1 = time.perf_counter()
        res = dict(pairs=0, agree=0, mismatch=0, missing=0, with_events=0, worst_rel=0.0, by_feature={},
                   last_bar_day_mismatch=0, examples=[])
        align = dict(pairs=0, violations=0)
        for sd, k in self.mrows:
            lst = list(self.sel[sd])
            # the same alignment sample as X991 (same eligible set, same salt and date label)
            t_label = date.fromisoformat(_ds(self.cal[k]))
            pick = P.pick(lst, SAMPLE_PER_MONTH, f"{SALT}|{t_label}") + \
                P.pick(lst, EXTRA_PER_MONTH, f"{EXTRA_SALT}|{t_label}")
            for s in dict.fromkeys(pick):
                j = self.col[s]
                bars, lastday, nev = self._fresh(self.sym[s], k)
                res["pairs"] += 1
                if bars is None:
                    res["missing"] += 1
                    continue
                res["with_events"] += int(nev > 0)
                a = self.featv[(j, k)]
                b = P.features_slow(bars)
                ok, w, bad = P.compare(a, b)
                res["worst_rel"] = max(res["worst_rel"], w)
                if ok:
                    res["agree"] += 1
                else:
                    res["mismatch"] += 1
                    for f in bad:
                        add(res["by_feature"], f)
                    if len(res["examples"]) < 20:
                        res["examples"].append([s, _ds(self.cal[k]), bad])
                lb = np.flatnonzero(np.isfinite(self.C[:k + 1, j]))
                pan_last = int(self.cal[lb[-1]]) if lb.size else None
                if pan_last != lastday:
                    res["last_bar_day_mismatch"] += 1
                # price side of the cross-domain snapshot (dates only)
                align["pairs"] += 1
                okA, late = P.alignment(_ds(self.cal[k]), price_last_bar=_ds(lastday) if lastday else None,
                                        features_through=_ds(self.cal[k]), breadth_day=_ds(self.cal[k]))
                if not okA:
                    align["violations"] += 1
                self._qr_log("AP|" + json.dumps(dict(t=_ds(self.cal[k]), sid=s, last_bar=_ds(lastday) if lastday else None,
                                                     ok=okA, late=late, bars=len(bars), events=nev,
                                                     nbars_panel=int(lb.size)), sort_keys=True))
        res["seconds"] = round(time.perf_counter() - t1, 1)
        self.st["fidelity"] = res
        self.st["alignment_price"] = align

    def _regime(self):
        out = {}
        try:
            h = self.history(self.spy, HIST_START, HIST_END, Resolution.DAILY, fill_forward=False,
                             data_normalization_mode=DataNormalizationMode.RAW)
            d = XP.session_days(h.index.get_level_values(-1).values)
            out["SPY"] = dict(bars=int(d.size), first=_ds(d.min()), last=_ds(d.max()))
        except Exception as e:
            out["SPY"] = dict(error=f"{type(e).__name__}: {str(e)[:150]}")
        for name, sym in self.vix.items():
            if isinstance(sym, str):
                out[name] = dict(error=sym)
                continue
            try:
                h = self.history(sym, datetime(2005, 1, 1), HIST_END, Resolution.DAILY)
                if h is None or h.empty:
                    out[name] = dict(bars=0)
                else:
                    tt = h.index.get_level_values(-1)
                    out[name] = dict(bars=int(len(h)), first=str(tt.min())[:10], last=str(tt.max())[:10],
                                     columns=sorted(map(str, h.columns))[:8])
            except Exception as e:
                out[name] = dict(error=f"{type(e).__name__}: {str(e)[:150]}")
        self.st["regime_inputs"] = out
