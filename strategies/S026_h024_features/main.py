# S026 v1.0 — H024 FEATURE REDESIGN AND SELECTION ON FROZEN DATA v2 (owner D201; research/phase9/H024_spec.md,
# pinned by qresearch.p9h024). NO orders, NO portfolio, NO performance; nothing after 2017-12-31 is requested (the last
# price row is the 2017-12-29 session): 2011-2017 is H024's DEVELOPMENT / TRAINING period; 2018-2021 and the Holdout
# stay sealed. A subclass of the pinned H022 / Data v2 host S024 (uploaded byte-identical as qr_s024; S024 subclasses
# the frozen Data v2 host X998, uploaded byte-identical as qr_x998): Data v2 universe, Score v1, the H022 population,
# responses, panel digest and the H022 canary checks are reused unchanged. S026 only ADDS:
#   - a store-wide total-assets ledger recorded LIVE at every month-end 2010-01 .. 2016-12 (as the frozen revenue
#     baseline ledger) for the asset-growth feature;
#   - the raw values of the 11 library features for every H022 population row (qr_h024), the layer subtotals (controls);
#   - canary (coverage, independent recomputation, redundancy correlations, components, model library: NO response),
#     optimiser-null worlds (features and models), and the ONE real development search with the pinned thresholds.
# New attribute / method names carry the prefix k_ / _k_ (S024 and X998 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_s024, qr_x998, qr_h024,
# qr_h023, qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred, qr_p7_mech, qr_h020_stats, qr_xs, qr_xs_diag, qr_xs_panel,
# qr_v2, qr_data_v2, qr_sec_corrections, qr_industry, qr_fundamentals.
from AlgorithmImports import *
from datetime import date
import hashlib
import json
import math
import os
import time
import numpy as np
import qr_x998  # noqa: F401  (the frozen Data v2 host, imported by qr_s024)
import qr_s024 as S24
import qr_h023 as G
import qr_h024 as K
import qr_p7 as P7
import qr_p7_pred as R
import qr_p7_score as S
import qr_p7_export as E
import qr_xs as X

K_LEDGER_FROM = date(2010, 1, 1)
K_LEDGER_TO = date(2017, 1, 1)             # exclusive: baselines for reviews up to 2017-12 (as the revenue ledger)
K_PROVENANCE = ("c_model", "c_feature", "c_fold", "null_result_sha256", "threshold_commit", "panel_sha256",
                "population_sha256", "library_sha256", "spec_sha256")
K_MODULES = ("qr_h024.py", "qr_h023.py", "qr_s024.py", "qr_x998.py", "qr_p7_pred.py")
K_SAMPLE_SALT = "P9CP1-S026"
K_SAMPLE = 400                              # stock-dates recomputed independently in the canary
K_CANARY_SEEDS = (950001, 950002)
K_TIMING_WORLDS = 6
K_SUMMARY_KEYS = ("t_ic", "ic_mean", "ic_se", "hi_ann", "hi_monthly", "mono", "q5_minus_q1_ann", "block_max",
                  "hi_n_mean", "hi_months", "hi_stock_months", "half1", "half2", "positive_months", "ic_sum")


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _plain(x):
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, np.ndarray):
        return _plain(x.tolist())
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    return x


class H024Features(S24.H022DataV2):

    def qr_initialize(self):
        p = self.qr_params
        mode = p.get("mode")
        if mode not in ("canary", "null", "real"):
            raise Exception(f"S026: unknown mode {mode!r}")
        if not p.get("feature_code_sha256"):
            raise Exception("S026: params need feature_code_sha256 (frozen qr_h024 fingerprint)")
        if mode in ("null", "real"):
            for k in ("population_sha256", "library_sha256", "features", "links"):
                if p.get(k) is None:
                    raise Exception(f"S026: {mode} runs need the pinned {k}")
        if mode == "real":
            for k in K_PROVENANCE:
                if p.get(k) in (None, ""):
                    raise Exception(f"S026: real mode needs the pinned null provenance ({k})")
            if sorted(p["c_fold"]) != [str(y) for y in K.FOLD_YEARS]:
                raise Exception("S026: c_fold needs the four walk-forward fold thresholds")
        self.qr_params = dict(p, mode="canary" if mode == "real" else mode)
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.h_mode = mode
        self.k_ta = {}

    def _month_end(self, t, today, elig, adv, fl):
        super()._month_end(t, today, elig, adv, fl)
        if K_LEDGER_FROM <= t < K_LEDGER_TO:
            d = {}
            for sid in sorted(set(self.store.hist) | set(self.store.pending)):
                r = self.store.record(sid, today)
                v = r.values.get("total_assets") if r is not None else None
                if v is not None and math.isfinite(v):
                    d[sid] = float(v)
            self.k_ta[(t.year, t.month)] = d            # kept for the whole run (read at the end); never revised

    # ------------------------------------------------------------------------------------------------ features
    def _k_attach(self, dates, features=K.LIBRARY):
        """d['X'] = (n, F) raw library values (NaN = invalid) and d['C'] = layer subtotals for every H022 population
        row; coverage by feature; digests. No response is read."""
        rows = {str(t): t for t in self.mon}
        cov = {f: 0 for f in features}
        cov_year = {}
        n_rows = 0
        self.k_cache = {}
        for d in dates:
            t = rows[d["day"]]
            k = self._row(t)
            ym = (t.year - 1, t.month)
            ta_prev = self.k_ta.get(ym, {})
            Xr, C = [], []
            for s_, tot in zip(d["ids"], d["S"]):
                j = self.col[s_]
                u, di = self.unv.get(j, ()), self.dist.get(j, ())
                ti = E.tech_at(self.C[:, j], self.P[:, j], k, u, di)[0]
                pf = K.price_features(self.C[:, j], self.P[:, j], k, u, di)
                row = self.mon[t][s_]
                ff = K.fund_features(row["vals"], ta_prev.get(s_), self.h_mcap.get(t, {}).get(s_))
                Xr.append(K.feature_row(ti, pf, ff, features))
                bits, total, pts = self.res_rows[t][s_]
                c = G.layer_split(pts)
                if sum(c) != int(total) or int(total) != int(tot):
                    raise Exception("S026: layer subtotals inconsistent with Score v1; nothing computed")
                C.append(c)
                self.k_cache[(d["day"], s_)] = (ti, pf, ff)
            d["X"] = np.array(Xr, float).reshape(-1, len(features))
            d["C"] = np.array(C, dtype=np.int64).reshape(-1, 3)
            yv = cov_year.setdefault(str(t.year), dict(rows=0, **{f: 0 for f in features}))
            for jf, f in enumerate(features):
                ok = int(np.isfinite(d["X"][:, jf]).sum())
                cov[f] += ok
                yv[f] += ok
            n_rows += len(d["ids"])
            yv["rows"] += len(d["ids"])
        h = hashlib.sha256()
        for d in dates:
            h.update(json.dumps([d["day"], d["ids"], [[None if not math.isfinite(v) else v for v in r]
                                                      for r in d["X"].tolist()]], separators=(",", ":")).encode())
        self.st["features_sha256"] = h.hexdigest()
        self.st["feature_coverage"] = dict(rows=n_rows, valid={f: cov[f] for f in features},
                                           share={f: cov[f] / n_rows for f in features}, by_year=cov_year)
        base = os.path.dirname(os.path.abspath(K.__file__))
        mods = {}
        for n in K_MODULES:
            try:
                mods[n] = hashlib.sha256(open(os.path.join(base, n), "rb").read()).hexdigest()
            except Exception as ex:
                mods[n] = f"unavailable: {type(ex).__name__}"
        self.st["k_runtime_modules"] = mods
        return dates

    def _k_library(self, features, links):
        lib = K.Library(K.model_library(tuple(features), K.FAMILY, [tuple(x) for x in links]), tuple(features))
        return lib

    def _k_population_digest(self, dates, features):
        h = hashlib.sha256()
        n = 0
        for d in dates:
            ok = K.population(d, features)
            ids = [s_ for s_, o in zip(d["ids"], ok) if o]
            n += len(ids)
            h.update(json.dumps([d["day"], ids], separators=(",", ":")).encode())
        return h.hexdigest(), n

    def _k_emit(self, tag, obj):
        blob = E.pack(json.dumps(_plain(obj), sort_keys=True, separators=(",", ":")))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"{tag}|{i // 9000}|{blob[i:i + 9000]}")
        return dict(blob_sha256=_sha(blob), blob_chars=len(blob))

    def _k_prepare_inputs(self, dates, features):
        """Coverage rule (spec section 5), population digest, and the panel for qr_h024.prepare."""
        self._k_attach(dates)
        keep = [j for j, f in enumerate(K.LIBRARY) if f in features]
        for d in dates:
            d["X"] = d["X"][:, keep]
        dg, n = self._k_population_digest(dates, features)
        self.st["population_sha256"], self.st["population_rows"] = dg, n
        return dates

    # ------------------------------------------------------------------------------------------------ canary
    def _canary_v2(self, dates):
        """H022's added canary checks (inherited), then H024's: feature coverage and the coverage rule, independent
        recomputation of every feature on a deterministic sample, the PIT checks of the asset ledger, the redundancy
        correlations (feature values only, NO response), components and the model library, and the grid / engine
        against the frozen procedure on SYNTHETIC responses only."""
        super()._canary_v2(dates)
        self._k_attach(dates)
        ck = self.st["canary"]
        cov = self.st["feature_coverage"]["share"]
        features = tuple(f for f in K.LIBRARY if cov[f] >= K.COVERAGE_MIN)
        g = dict(library=list(K.LIBRARY), coverage=cov, retained=list(features),
                 dropped=[f for f in K.LIBRARY if f not in features])
        # independent recomputation on a sample of stock-dates (full histories, no slicing)
        tags = sorted(self.k_cache)
        pick = P7.pick([f"{a}|{b}" for a, b in tags], K_SAMPLE, K_SAMPLE_SALT)
        rec = dict(checked=0, mismatch=0, ledger_checked=0, ledger_mismatch=0, examples=[])
        rows = {str(t): t for t in self.mon}
        for tag in pick:
            day, s_ = tag.split("|")
            t = rows[day]
            k = self._row(t)
            j = self.col[s_]
            ti, pf, ff = self.k_cache[(day, s_)]
            full = S.technical_inputs(self.C[:k + 1, j], self.P[:k + 1, j], k)
            pf2 = K.price_features(self.C[:k + 1, j], self.P[:k + 1, j], k, self.unv.get(j, ()), self.dist.get(j, ()),
                                   span=10 ** 9)
            c, p = self.C[:k + 1, j], self.P[:k + 1, j]
            v = P7.valid_rows(c, p)
            b = v.size - 1
            ok = full["mom_12_1"] == ti["mom_12_1"] and full["vol60"] == ti["vol60"] and pf2 == pf
            if pf["REV1M"] is not None:
                ok &= pf["REV1M"] == float(p[v][b] / p[v][b - 21] - 1.0)
            if pf["HI52"] is not None:
                ok &= pf["HI52"] == float(c[v][b] / c[v][b - 251:b + 1].max())
            vals = self.mon[t][s_]["vals"]
            fi, _ = S.fundamental_inputs(*vals, 1.0) if all(x is not None for x in vals) else (None, "")
            if fi is not None and ff["GPA"] is not None:
                ok &= ff["GPA"] == fi["gpa"] and ff["ACC"] == fi["cash_conversion"] and ff["EQA"] == fi["eqa"]
            rec["checked"] += 1
            rec["mismatch"] += int(not ok)
            if not ok and len(rec["examples"]) < 10:
                rec["examples"].append(tag)
            if ff["AG"] is not None:
                rec["ledger_checked"] += 1
                prev = self.k_ta.get((t.year - 1, t.month), {}).get(s_)
                rec["ledger_mismatch"] += int(prev is None or ff["AG"] != vals[4] / prev - 1.0)
        g["recomputation"] = rec
        kt = self.k_ta
        g["ledger"] = dict(months=len(kt), first=list(min(kt)) if kt else None, last=list(max(kt)) if kt else None,
                           companies_mean=float(np.mean([len(v) for v in kt.values()])) if kt else 0.0)
        # redundancy correlations over the H024 population (all retained features valid); NO response read
        keep = [K.LIBRARY.index(f) for f in features]
        F = len(features)
        rho = []
        for d in dates:
            Xr = d["X"][:, keep]
            ok = np.all(np.isfinite(Xr), axis=1)
            if ok.sum() < R.MIN_STOCKS:
                continue
            Rk = np.column_stack([X.avg_rank(Xr[ok, i]) for i in range(F)])
            rho.append(np.corrcoef(Rk, rowvar=False))
        rho = np.array(rho)
        med_abs = np.median(np.abs(rho), axis=0)
        links = K.redundancy_links(med_abs.tolist(), features)
        lib = self._k_library(features, links)
        g["correlation"] = dict(dates=int(rho.shape[0]), median=np.median(rho, axis=0).round(6).tolist(),
                                median_abs=med_abs.round(6).tolist(), p10=np.percentile(rho, 10, axis=0).round(6).tolist(),
                                p90=np.percentile(rho, 90, axis=0).round(6).tolist())
        g["links"] = [list(x) for x in links]
        g["components"] = K.components_of(features, K.FAMILY, links)
        g["models"] = lib.M
        g["models_by_size"] = {str(k): int((lib.k == k).sum()) for k in K.SIZES}
        g["library_sha256"] = lib.sha
        for dd in dates:
            dd["X"] = dd["X"][:, keep]
        dg, n = self._k_population_digest(dates, features)
        g["population_sha256"], g["population_rows"] = dg, n
        g["population_share_of_h022"] = n / max(1, self.st["feature_coverage"]["rows"])
        # engine against the frozen procedure on SYNTHETIC responses only
        rng = np.random.default_rng(990026)
        synth = [dict(dd, y=rng.standard_t(5, len(dd["ids"])) * 0.07) for dd in dates]
        prep = K.prepare(synth, lib)
        worst, compared = 0.0, 0
        for seed in (None,) + K_CANARY_SEEDS:
            s = G.summarise(G.world(prep, seed))
            for c in (0, F - 1, F, F + lib.M // 2, F + lib.M - 1, lib.ctrl_cols[0]):
                dd2 = []
                for dd in synth:
                    ok = K.population(dd, features)
                    if ok.sum() < R.MIN_STOCKS:
                        continue
                    Pm = K.percentiles(dd["X"][ok], np.asarray(dd["sector"])[ok], features)
                    Sc = K.score_matrix(Pm, lib, dd["C"][ok])[:, c]
                    dd2.append(dict(ids=np.asarray(dd["ids"])[ok], S=Sc, sector=np.asarray(dd["sector"])[ok],
                                    mom=np.asarray(dd["mom"])[ok], size=np.asarray(dd["size"])[ok],
                                    y=np.asarray(dd["y"])[ok], year=dd["year"], regime=dd["regime"]))
                rw = R.run_world(R.prepare(dd2), seed=seed)
                for key in ("t_ic", "ic_mean", "hi_ann", "mono", "q5_minus_q1_ann", "block_max"):
                    a, b = float(rw[key]), float(s[key][c])
                    if a != b and not (np.isnan(a) and np.isnan(b)):
                        worst = max(worst, abs(a - b))
                compared += 1
        g["vs_h022_procedure"] = dict(compared=compared, max_abs_diff=worst)
        worst_ctrl = 0.0
        for dd in dates:
            ok = K.population(dd, features)
            if ok.sum() < R.MIN_STOCKS:
                continue
            Sc = K.score_matrix(K.percentiles(dd["X"][ok], np.asarray(dd["sector"])[ok], features), lib, dd["C"][ok])
            worst_ctrl = max(worst_ctrl, float(np.max(np.abs(Sc[:, lib.ctrl_cols[0]] - np.asarray(dd["S"])[ok]))))
        g["control_equals_score_v1"] = worst_ctrl == 0.0
        t0 = time.perf_counter()
        recs = [K.null_record(prep, lib, 900001 + i) for i in range(K_TIMING_WORLDS)]
        ws = (time.perf_counter() - t0) / K_TIMING_WORLDS
        g["null_record"] = dict(world_s=round(ws, 4), world_s_1000=round(ws * 1000, 1),
                                repeat_identical=K.null_record(prep, lib, 900001) == recs[0],
                                distinct=len({json.dumps(r) for r in recs}), fields=len(K.NULL_FIELDS))
        ev = K.evaluate(prep, lib, K.CRIT_FLOOR, [K.CRIT_FLOOR] * 4)
        g["machinery"] = dict(dates=len(prep), folds=len(ev["walk_forward"]["folds"]),
                              pseudo_oos_months=ev["walk_forward"]["pseudo_oos"]["months"], synthetic_responses=True)
        ck["h024"] = g
        ck["real_ic_computed"] = False
        ck["gates_computed"] = False

    # ------------------------------------------------------------------------------------------------ null / real
    def _k_ready(self, dates):
        p = self.qr_params
        features = tuple(p["features"])
        self._k_prepare_inputs(dates, features)
        if self.st["population_sha256"] != p["population_sha256"]:
            raise Exception("S026: the H024 population differs from the pinned digest; nothing computed")
        lib = self._k_library(features, p["links"])
        if lib.sha != p["library_sha256"]:
            raise Exception("S026: the model library differs from the pinned hash; nothing computed")
        return lib

    def _null(self, dates):
        lib = self._k_ready(dates)
        t0 = time.perf_counter()
        prep = K.prepare(dates, lib)
        rows = [K.null_record(prep, lib, seed) for seed in self.h_seeds]
        out = self._k_emit("QRK", dict(fields=list(K.NULL_FIELDS), worlds=rows))
        self.st["null"] = dict(seeds=[self.h_seeds[0], self.h_seeds[-1]], worlds=len(rows), dates=len(prep),
                               models=lib.M, features=lib.F, world_s=round(time.perf_counter() - t0, 1), **out)

    def _real(self, dates):
        p = self.qr_params
        self.st["provenance"] = {k: p[k] for k in K_PROVENANCE}
        if self.st["panel_sha256"] != p["panel_sha256"]:
            raise Exception("S026: the prepared panel differs from the pinned H022 / Data v2 panel; nothing computed")
        lib = self._k_ready(dates)
        t0 = time.perf_counter()
        c_model = float(p["c_model"])
        c_fold = [float(p["c_fold"][str(y)]) for y in K.FOLD_YEARS]
        prep = K.prepare(dates, lib)
        ev = K.evaluate(prep, lib, c_model, c_fold)               # the primary search first
        w, s, gt = ev["world"], ev["summary"], ev["gates"]
        yrs = w["years"]
        ys = sorted(set(yrs.tolist()))
        qsum = [[np.nansum(w["QM"][yrs == y], axis=0) for y in ys], [np.isfinite(w["QM"][yrs == y]).sum(axis=0)
                                                                      for y in ys]]
        out = dict(features=list(lib.features), models=[list(m) for m in lib.models], controls=[list(c) for c in K.CONTROLS],
                   days=[pp["day"] for pp in prep], years=yrs, n=[pp["n"] for pp in prep], IC=w["IC"], HI=w["HI"],
                   NH=w["NH"], QM_year_sum=qsum[0], QM_year_count=qsum[1], qyears=ys,
                   summary={k: s[k] for k in K_SUMMARY_KEYS}, q_mean=s["q_mean"], block_sum=s["block_sum"],
                   ic_years={str(y): v for y, v in s["years"].items()},
                   gates={k: v for k, v in gt.items() if k != "robust_nbrs"}, robust_nbrs=gt["robust_nbrs"],
                   pick=ev["pick"], ranked=ev["ranked"], argmax_model=ev["argmax_model"], cstar=ev["cstar"],
                   walk_forward=ev["walk_forward"], stability=ev["stability"], top10=[list(m) for m in ev["top10"]],
                   c_model=c_model, c_feature=float(p["c_feature"]), c_fold=c_fold)
        for h, key in G.DIAG_HORIZONS:                               # NON-GATING diagnostics, after the primary
            sh = G.summarise(G.world(K.prepare(dates, lib, key)), lag=h)
            out[f"h{h}"] = {k: sh[k] for k in ("t_ic", "ic_mean", "hi_ann", "mono", "q5_minus_q1_ann")}
        res = self._k_emit("QRK", out)
        self.st["real"] = dict(decisions=len(prep), models=lib.M, world_s=round(time.perf_counter() - t0, 1),
                               candidate=None if ev["pick"] is None else list(lib.models[ev["pick"]]), **res)
