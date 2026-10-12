# S030 v1.0 — H028 FIXED STRONG SHRINKAGE LEARNED STOCK SCORE ON DATA v2.1 (owner D217; research/phase13/H028_spec.md,
# pinned by qresearch.p13h028). NO orders (portfolios are simulated in-host); nothing after 2021-12-31 is requested:
# 2011-2021 is fully seen development data (H028 is explicitly post-hoc); the Holdout 2022-01-01 .. 2026-08-31 stays
# sealed. A subclass of the pinned H027 host S029 (uploaded byte-identical as qr_s029; memory-reduced build, panels,
# months), itself a subclass of the pinned H026 host S028 (qr_s028) and the Data v2.1 host X801 (qr_x801).
# The ONLY scientific change from H027: every outer-year Ridge fit uses lambda = 100 (qr_h028.run_world_fixed); no inner
# lambda selection exists in this code path. S030 only replaces S029's three mode handlers:
#   - canary: lambda-100 fit log + call counts, the real H027 reproduced through the fixed path, H027 conditional rows
#     1-25 (= committed E029-02) reproduced through the fixed path with their own schedules, permutation / LV15 / costs
#     checks, the 2016-2021 tolerance calibration (spec 6.2) and synthetic worlds A / B (lambda = 100). NO real H028.
#   - null: LOWVOL-conditional worlds params.seeds at lambda = 100 (the real assignment only hashed).
#   - real: the ONE run with the pinned c_WEALTH_H028 and tolerance table: H027 reproduction, 2016-2021 equality,
#     LV15, gates B1-B6, diagnostics; the final lambda-100 model only if every gate passes.
# New attribute / method names carry the prefix h_ / _h_ (X801 / X998 / S028 / S029 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_s029, qr_h028, qr_s028,
# qr_h027, qr_x801, qr_h026, qr_h024, qr_h023, qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred, qr_p7_mech,
# qr_h020_stats, qr_xs, qr_xs_diag, qr_xs_panel, qr_v2, qr_data_v21, qr_sec_corrections, qr_industry, qr_fundamentals.
from AlgorithmImports import *
import hashlib
import json
import math
import time
import numpy as np
import qr_s029 as S29
import qr_s028 as S28
import qr_h026 as H
import qr_h027 as G
import qr_h028 as F
import qr_p7_export as E

H_SYNTH_A, H_SYNTH_B = S29.G_SYNTH_A, S29.G_SYNTH_B       # the H027 synthetic generator, unchanged
H_SYNTH_SIGMA, H_SYNTH_NULLS = S29.G_SYNTH_SIGMA, S29.G_SYNTH_NULLS
H_SYNTH_REPS_A, H_SYNTH_REPS_B, H_SYNTH_SEED = S29.G_SYNTH_REPS_A, S29.G_SYNTH_REPS_B, S29.G_SYNTH_SEED
H_PERM_SEEDS = (1, 2)
_plain, _ds = S28._plain, S28._ds


def _rank(x):
    return H.avg_rank(np.asarray(x, float))


def _spearman(a, b):
    ra, rb = _rank(a), _rank(b)
    ra, rb = ra - ra.mean(), rb - rb.mean()
    d = math.sqrt(float((ra @ ra) * (rb @ rb)))
    return float(ra @ rb / d) if d > 0 else float("nan")


class H028Fixed(S29.H027Conditional):

    def qr_initialize(self):
        p = self.qr_params
        mode = p.get("mode")
        if mode not in ("canary", "null", "real"):
            raise Exception(f"S030: unknown mode {mode!r}")
        for k in ("spec_sha256", "h028_code_sha256", "data_v21_manifest_sha256", "h026_feature_panel_sha256",
                  "h026_response_panel_sha256", "h027_real_wealth", "h027_real_s_wealth", "h027_lambda_schedule"):
            if p.get(k) in (None, ""):
                raise Exception(f"S030: params need {k}")
        if [float(x) for x in p["h027_lambda_schedule"]][1:] != [F.LAMBDA] * 6:
            raise Exception("S030: the H027 schedule must be lambda = 100 for 2016-2021")
        if mode == "canary" and not p.get("h027_null_rows_sha256"):
            raise Exception("S030: the canary needs the committed E029-02 rows 1-25 digest")
        if mode == "null":
            a, b = (int(x) for x in p["seeds"])
            if not (1 <= a <= b <= G.R_NULL):
                raise Exception("S030: null seeds must lie in 1..5000")
        if mode == "real":
            for k in ("c_wealth_h028", "null_result_sha256", "threshold_commit", "tolerance", "tolerance_sha256"):
                if p.get(k) in (None, ""):
                    raise Exception(f"S030: real mode needs the pinned {k}")
            tol = {str(y): {q: float(v) for q, v in d.items()} for y, d in p["tolerance"].items()}
            if F.tol_sha(tol) != p["tolerance_sha256"]:
                raise Exception("S030: the tolerance table differs from its pinned digest")
        # S029's initialisation with S029-compatible parameters (null mode: no S029-specific pins needed)
        self.qr_params = dict(spec_sha256=p["spec_sha256"], h027_code_sha256=p["h028_code_sha256"],
                              data_v21_manifest_sha256=p["data_v21_manifest_sha256"],
                              h026_feature_panel_sha256=p["h026_feature_panel_sha256"],
                              h026_response_panel_sha256=p["h026_response_panel_sha256"], mode="null", seeds=[1, 1])
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.g_mode = self.w_mode = mode
        if mode == "null":
            a, b = (int(x) for x in p["seeds"])
            self.h_seeds = list(range(a, b + 1))

    def _h_schedule27(self):
        return F.schedule_h027(self.qr_params["h027_lambda_schedule"])

    # ------------------------------------------------------------------------------------------------ canary
    def _g_canary(self, months):
        p = self.qr_params
        self.st["hypothesis"] = "H028"
        ck = dict(real_h028_result_computed=False)
        # 1. lambda = 100 in every fit; no inner selection (instrumented call counts on one conditional world)
        calls = dict(fit=[], simulate=0)
        fit0, sim0 = H.Fitter.fit, H.simulate

        def fit_c(obj, cut, lam):
            calls["fit"].append(float(lam))
            return fit0(obj, cut, lam)

        def sim_c(*a, **kw):
            calls["simulate"] += 1
            return sim0(*a, **kw)
        H.Fitter.fit, H.simulate = fit_c, sim_c
        try:
            w1 = F.run_fixed_conditional(months, 1, full=True)
        finally:
            H.Fitter.fit, H.simulate = fit0, sim0
        w1b = F.run_fixed_conditional(months, 1)
        ck["fixed_lambda"] = dict(fit_lambdas=calls["fit"], fit_calls=len(calls["fit"]), simulate_calls=calls["simulate"],
                                  fits_logged=[[y, l] for y, l in w1["fits"]], world_lambdas=w1["rec"]["lam"],
                                  repeat_identical=w1b == w1["rec"])
        ck["fixed_lambda"]["ok"] = (calls["fit"] == [F.LAMBDA] * 7 and calls["simulate"] == 1
                                    and all(l == F.LAMBDA for l in w1["rec"]["lam"]) and w1b == w1["rec"])
        # 2. the real H027 through the frozen qr_h026.run_world AND through the fixed path with H027's schedule
        w7 = H.run_world(months, None, full=True)
        w7f = F.run_world_fixed(months, [m["X"] for m in months], schedule=w7["lam_y"], full=True)
        same = (w7["h"]["wealth"] == w7f["h"]["wealth"] and w7["yh"] == w7f["yh"]
                and all(w7["coef"][(Y, w7["lam_y"][Y])][0] == w7f["coef"][(Y, w7f["lam_y"][Y])][0]
                        and np.array_equal(w7["coef"][(Y, w7["lam_y"][Y])][1], w7f["coef"][(Y, w7f["lam_y"][Y])][1])
                        for Y in H.OUTER_YEARS))
        ck["h027_real_reproduction"] = dict(
            fixed_path_equals_run_world=bool(same), lam_y=[w7["lam_y"][Y] for Y in H.OUTER_YEARS],
            wealth=w7["h"]["wealth"], expected_wealth=float(p["h027_real_wealth"]), s_wealth=w7["rec"]["S_WEALTH"],
            expected_s_wealth=float(p["h027_real_s_wealth"]),
            ok=bool(same and w7["h"]["wealth"] == float(p["h027_real_wealth"])
                    and w7["rec"]["S_WEALTH"] == float(p["h027_real_s_wealth"])
                    and [w7["lam_y"][Y] for Y in H.OUTER_YEARS] == [float(x) for x in p["h027_lambda_schedule"]]))
        del w7, w7f
        # 3. H027 conditional rows 1-25 (= committed E029-02) and the same worlds through the fixed path
        rows, mism = [], 0
        for sd in G.DETERMINISM_SEEDS:
            r = G.run_conditional(months, sd)
            rows.append(G.row(r))
            rf = F.run_world_fixed(months, G.conditional_permuted(months, sd), seed=sd,
                                   schedule=F.schedule_h027(r["lam"]))
            mism += int(G.row(rf) != G.row(r))
        text = json.dumps(_plain(rows), separators=(",", ":"))
        dg = hashlib.sha256(text.encode()).hexdigest()
        ck["h027_conditional_rows"] = dict(sha256=dg, equal_to_e029_02=dg == p["h027_null_rows_sha256"],
                                           fixed_path_mismatches=mism)
        # 4. conditional permutation: LOWVOL kept, the OTHER vector from one donor, no self-match, returns untouched
        before = self._w_response_digest(months)
        pc = dict(months=0, lowvol_changed=0, other_not_donor_row=0, self_matches=0)
        other = list(G.OTHER)
        for sd in H_PERM_SEEDS:
            for m, X, d in zip(months, G.conditional_permuted(months, sd), G.donors(months, sd)):
                pc["months"] += 1
                pos = {s: i for i, s in enumerate(m["ids"])}
                pc["lowvol_changed"] += int(not np.array_equal(X[:, G.LOWVOL], m["X"][:, G.LOWVOL]))
                for i, s in enumerate(m["ids"]):
                    pc["self_matches"] += int(d[s] == s)
                    pc["other_not_donor_row"] += int(not np.array_equal(X[i, other], m["X"][pos[d[s]], other]))
        pc["responses_unchanged"] = self._w_response_digest(months) == before
        ck["conditional_permutation"] = pc
        # 5. LV15 picks = an independent lowest-volatility walk; costs by hand; the c order statistic
        lc = dict(months=0, mismatch=0)
        for m in months:
            if m["test_year"] not in H.OUTER_YEARS:
                continue
            lc["months"] += 1
            order = sorted(range(len(m["ids"])), key=lambda i: (m["raw"][i, G.LOWVOL], m["ids"][i]))
            out, cnt = [], {}
            for i in order:
                if not m["open_ok"][i] or cnt.get(m["sector"][i], 0) >= H.SECTOR_CAP:
                    continue
                out.append(i)
                cnt[m["sector"][i]] = cnt.get(m["sector"][i], 0) + 1
                if len(out) == H.K:
                    break
            lc["mismatch"] += int(sorted(H.pick(m, G.lv15_scores([m])[0])) != sorted(out))
        ck["lv15_picks"] = lc
        ck["costs_by_hand"] = self._g_costs_check()
        ck["critical_value_50th_of_5000"] = H.critical_value(list(range(5000))) == 4950.0
        # 6. the 2016-2021 tolerance calibration (spec 6.2): lambda 100 everywhere vs H027's schedule, worlds 1-100
        t1 = time.perf_counter()
        sch, eqs, bad, summ = self._h_schedule27(), [], [], []
        for sd in F.CAL_SEEDS:
            Xs = G.conditional_permuted(months, sd)
            wa = F.run_world_fixed(months, Xs, schedule=sch, full=True)
            wb = F.run_world_fixed(months, Xs, full=True)
            e = F.equality(wb, wa, months)
            if not e["exact_ok"]:
                bad.append(sd)
            eqs.append(dict(per_year=e["per_year"]))
            summ.append([sd] + [e["per_year"][Y]["ret_diff"] for Y in F.EQUAL_YEARS]
                        + [e["per_year"][Y]["turnover_diff"] for Y in F.EQUAL_YEARS])
            del wa, wb, Xs
        cal = F.max_abs_diffs(eqs)
        tol = F.tolerance(cal)
        ck["calibration"] = dict(worlds=len(F.CAL_SEEDS), exact_failures=bad, max_abs=cal, tolerance=tol,
                                 tolerance_sha256=F.tol_sha(tol), rows=summ,
                                 pair_s=round((time.perf_counter() - t1) / len(F.CAL_SEEDS), 3))
        # 7. synthetic worlds A (LOWVOL only) / B (LOWVOL + GPA), lambda = 100
        ck["synthetic"] = self._h_synthetic(months)
        ck["null_world_s"] = ck["synthetic"]["world_s"]
        ck["estimated_5000_world_minutes"] = round(ck["synthetic"]["world_s"] * 5000 / 60.0, 1)
        self.st["canary"] = ck

    def _h_synthetic(self, months):
        """S029's synthetic generator verbatim (returns = a . [x_LOWVOL, x_GPA] + noise; labels from three synthetic
        months ahead); per replicate the real-assignment lambda-100 model vs H_SYNTH_NULLS lambda-100 conditional nulls."""
        gpa = H.FEATURES.index("GPA")
        out = {}
        t0 = time.perf_counter()
        nworld = 0
        for name, (bl, bg), reps in (("A", H_SYNTH_A, H_SYNTH_REPS_A), ("B", H_SYNTH_B, H_SYNTH_REPS_B)):
            pct = []
            for rep in range(reps):
                rng = np.random.default_rng(H_SYNTH_SEED + 100 * (name == "B") + rep)
                fake = []
                for mo in months:
                    r = bl * mo["X"][:, G.LOWVOL] + bg * mo["X"][:, gpa] + rng.normal(0, H_SYNTH_SIGMA, len(mo["ids"]))
                    fake.append(dict(mo, r_oo=r, r_oc=r, daily=np.outer(np.linspace(1.0 / len(mo["days"]), 1.0,
                                                                                    len(mo["days"])), r)))
                for i, mo in enumerate(fake):
                    fut = fake[i:i + 3]
                    if len(fut) == 3 and math.isfinite(mo["exit_day"]):
                        acc = {}
                        for f in fut:
                            pos = {s: n for n, s in enumerate(f["ids"])}
                            for s in mo["ids"]:
                                acc[s] = acc.get(s, 1.0) * (1.0 + (f["r_oo"][pos[s]] if s in pos else 0.0))
                        mo["label"] = H.centred_percentile(np.array([acc[s] - 1.0 for s in mo["ids"]]))
                real = F.run_fixed_conditional(fake, None)["S_WEALTH"]
                nul = [F.run_fixed_conditional(fake, sd)["S_WEALTH"] for sd in range(1, H_SYNTH_NULLS + 1)]
                nworld += 1 + len(nul)
                rep2 = F.run_fixed_conditional(fake, 1)["S_WEALTH"] == nul[0]
                pct.append(dict(real=real, percentile=float(np.mean(np.array(nul) < real)), null_median=float(
                    np.median(nul)), repeat_identical=rep2))
            out[name] = dict(replicates=pct, median_percentile=float(np.median([x["percentile"] for x in pct])),
                             min_percentile=float(min(x["percentile"] for x in pct)))
        out["A"]["pass"] = out["A"]["median_percentile"] < 0.90
        out["B"]["pass"] = out["B"]["min_percentile"] >= 0.90
        out["world_s"] = round((time.perf_counter() - t0) / max(1, nworld), 3)
        return out

    # ------------------------------------------------------------------------------------------------ null
    def _g_null(self, months):
        self.st["hypothesis"] = "H028"
        t0 = time.perf_counter()
        rows, coefs = [], {}
        for sd in self.h_seeds:
            r = F.run_fixed_conditional(months, sd)
            rows.append(F.row(r))
            if sd in F.DETERMINISM_SEEDS:
                coefs[str(sd)] = r["coef"]
        out = self._w_emit("QRHN", dict(fields=list(F.FIELDS), worlds=rows, coef=coefs))
        self.st["null"] = dict(seeds=[self.h_seeds[0], self.h_seeds[-1]], worlds=len(rows),
                               nonfinite=sum(1 for r in rows if not math.isfinite(r[1])),
                               world_s=round((time.perf_counter() - t0) / max(1, len(rows)), 3), **out)

    # ------------------------------------------------------------------------------------------------ real
    def _g_real(self, months, regimes, reviews):
        p = self.qr_params
        self.st["hypothesis"] = "H028"
        c = float(p["c_wealth_h028"])
        tol = {str(y): {q: float(v) for q, v in d.items()} for y, d in p["tolerance"].items()}
        self.st["provenance"] = {k: p[k] for k in ("c_wealth_h028", "null_result_sha256", "threshold_commit",
                                                   "tolerance_sha256", "h026_feature_panel_sha256",
                                                   "h026_response_panel_sha256")}
        Xr = [m["X"] for m in months]
        w8 = F.run_world_fixed(months, Xr, full=True)                    # the real H028
        w7 = H.run_world(months, None, full=True)                         # the real H027 (= H026), recomputed
        w7f = F.run_world_fixed(months, Xr, schedule=w7["lam_y"], full=True)
        repro = dict(wealth=w7["h"]["wealth"], expected_wealth=float(p["h027_real_wealth"]),
                     s_wealth=w7["rec"]["S_WEALTH"], expected_s_wealth=float(p["h027_real_s_wealth"]),
                     lam_y=[w7["lam_y"][Y] for Y in H.OUTER_YEARS],
                     fixed_path_equals_run_world=bool(w7f["h"]["wealth"] == w7["h"]["wealth"] and w7f["yh"] == w7["yh"]))
        repro["ok"] = (abs(repro["wealth"] / repro["expected_wealth"] - 1.0) <= 1e-9
                       and abs(repro["s_wealth"] - repro["expected_s_wealth"]) <= 1e-9
                       and repro["lam_y"] == [float(x) for x in p["h027_lambda_schedule"]]
                       and repro["fixed_path_equals_run_world"])
        eqr = F.equality(w8, w7, months)
        eqr["tolerance_check"] = F.within_tolerance(eqr, tol)
        ms = [months[i] for i in w8["idx"]]
        days, cap = w8["days"], H.CAPITAL
        lvr = G.lv15(ms)
        lvm = H.path_metrics(lvr["daily"], days, cap, lvr["wealth"])
        ylv = H.year_returns(lvr["daily"], days, cap)
        st_h = H.simulate(ms, w8["scores"], slip=H.STRESS_SLIPPAGE)["wealth"]
        st_s = H.spy_simulate(ms, slip=H.STRESS_SLIPPAGE)["wealth"]
        st_lv = G.lv15(ms, slip=H.STRESS_SLIPPAGE, daily=False)["wealth"]
        g = G.gates(w8["hm"], w8["sm"], lvm, w8["yh"], w8["ys"], ylv, st_h, st_s, st_lv, c)
        risk = {}
        for n, d in (("h028", w8["h"]["daily"]), ("h027", w7["h"]["daily"]), ("lv15", lvr["daily"])):
            risk[n] = {k: v for k, v in G.risk(d, w8["s"]["daily"], days, cap).items() if k not in ("rh", "rs")}
        h = w8["h"]
        coef = {str(Y): dict(lam=w8["lam_y"][Y], b0=w8["coef"][(Y, w8["lam_y"][Y])][0],
                             beta=w8["coef"][(Y, w8["lam_y"][Y])][1], ntrain=w8["ntrain"][(Y, w8["lam_y"][Y])])
                for Y in H.OUTER_YEARS}
        coef27 = {str(Y): dict(lam=w7["lam_y"][Y], b0=w7["coef"][(Y, w7["lam_y"][Y])][0],
                               beta=w7["coef"][(Y, w7["lam_y"][Y])][1]) for Y in H.OUTER_YEARS}
        rp8, rp7 = F.replay(ms, w8["scores"]), F.replay(ms, w7["scores"])
        out = dict(c_wealth_h028=c, gates=g, reproduction_h027=repro, equality=eqr, rec=w8["rec"], h028=w8["hm"],
                   h027=w7["hm"], spy=w8["sm"], lv15=lvm, years_h028=w8["yh"], years_h027=w7["yh"],
                   years_spy=w8["ys"], years_lv15=ylv, risk=risk, coefficients=coef, coefficients_h027=coef27,
                   trades=dict(buys=h["buys"], sells=h["sells"], trades=h["trades"], commissions=h["commissions"],
                               slippage=h["slippage"], turnover=h["turnover"], holdings=h["holdings"],
                               cash_share=h["cash_share"]),
                   trades_h027=dict(trades=w7["h"]["trades"], commissions=w7["h"]["commissions"],
                                    slippage=w7["h"]["slippage"], turnover=w7["h"]["turnover"]),
                   lv15_trades=dict(trades=lvr["trades"], commissions=lvr["commissions"], slippage=lvr["slippage"],
                                    turnover=lvr["turnover"], holdings=lvr["holdings"], cash_share=lvr["cash_share"]),
                   stress=dict(h028=st_h, spy=st_s, lv15=st_lv), daily_h028=h["daily"], daily_h027=w7["h"]["daily"],
                   daily_spy=w8["s"]["daily"], daily_lv15=lvr["daily"], days=days, months=[m["day"] for m in ms],
                   replay_months=dict(h028=[[x["day"], x["turnover"], x["orders"], x["commission"], x["slippage"]]
                                            for x in rp8["months"]],
                                      h027=[[x["day"], x["turnover"], x["orders"], x["commission"], x["slippage"]]
                                            for x in rp7["months"]]))
        # 2015 comparison (spec 9.1): score rank correlation and Top-15 overlap per 2015 decision month
        y15 = [n for n, m in enumerate(ms) if m["test_year"] == H.OUTER_YEARS[0]]
        out["y2015"] = dict(months=[ms[n]["day"] for n in y15],
                            score_spearman=[_spearman(w8["scores"][n], w7["scores"][n]) for n in y15],
                            held_overlap=[len(set(w8["h"]["picks"][n]) & set(w7["h"]["picks"][n])) for n in y15])
        # non-gating diagnostics (spec section 9; never rescue)
        diag = {}
        fac = G.lowvol_factor(ms)
        dep = G.period_returns(h["daily"], ms, cap) - G.period_returns(w8["s"]["daily"], ms, cap)
        diag["lowvol_factor_regression"] = dict(G.nw_regression(dep, fac), factor_mean=float(np.nanmean(fac)),
                                                factor=_plain(fac), dependent=_plain(dep))
        for name, kw in (("capital_200k", dict(capital=200_000.0)), ("top10", dict(k=10)), ("top20", dict(k=20))):
            hh = H.simulate(ms, w8["scores"], daily=True, **kw)
            ss = H.spy_simulate(ms, capital=kw.get("capital", cap), daily=True)
            hm = H.path_metrics(hh["daily"], days, kw.get("capital", cap), hh["wealth"])
            sm = H.path_metrics(ss["daily"], days, kw.get("capital", cap), ss["wealth"])
            diag[name] = dict(wealth=hh["wealth"], spy=ss["wealth"], S_WEALTH=math.log(hh["wealth"] / ss["wealth"]),
                              cagr=hm["cagr"], spy_cagr=sm["cagr"], maxdd=hm["maxdd"], vol=hm["vol"])
        picks = h["picks"]
        sn, reg = [], {}
        for mo, pk in zip(ms, picks):
            pos = {s: n for n, s in enumerate(mo["ids"])}
            if not pk:
                continue
            ex = []
            for s in pk:
                n = pos[s]
                peers = (mo["sector"] == mo["sector"][n]) & mo["open_ok"]
                ex.append(mo["r_oo"][n] - float(mo["r_oo"][peers].mean()))
            sn.append(float(np.mean(ex)))
            port = float(np.mean([mo["r_oo"][pos[s]] for s in pk]))
            t = next(x for x in reviews if str(x) == mo["day"])
            reg.setdefault(str(regimes[t]), []).append(port - mo["spy_oo"])
        diag["sector_neutral"] = dict(months=len(sn), mean_monthly=float(np.mean(sn)) if sn else None,
                                      t=float(np.mean(sn) / (np.std(sn, ddof=1) / math.sqrt(len(sn)))) if len(sn) > 2 else None)
        diag["regime"] = {k: dict(months=len(v), mean_monthly_relative=float(np.mean(v))) for k, v in sorted(reg.items())}
        ends = G.month_ends(days)
        lab = [_ds(days[i])[:7] for i in ends]
        mark = {n: np.r_[cap, np.asarray(x, float)[ends]] for n, x in (("h028", h["daily"]), ("h027", w7["h"]["daily"]),
                                                                        ("spy", w8["s"]["daily"]), ("lv15", lvr["daily"]))}
        mar = {}
        for mon in ("2020-02", "2020-03", "2020-04"):
            i = lab.index(mon) + 1
            mar[mon] = {n: float(v[i] / v[i - 1] - 1.0) for n, v in mark.items()}
        diag["march_2020"] = mar
        out["diagnostics"] = diag
        ok_all = g["all"] and repro["ok"] and eqr["exact_ok"] and eqr["tolerance_check"]["ok"]
        if ok_all:                                                     # final lambda-100 model (spec section 8)
            fit = H.Fitter(months, Xr)
            b0, b, n = fit.fit(float(self.cal[-1]), F.LAMBDA)
            out["final_model"] = dict(lam=F.LAMBDA, b0=b0, beta=dict(zip(H.FEATURES, b.tolist())), train_months=n)
        res = self._w_emit("QRHR", out)
        self.st["real"] = dict(S_WEALTH=g["S_WEALTH"], gates={k: v for k, v in g.items() if k.startswith("A") or k == "all"},
                               reproduction_ok=repro["ok"], equality_exact=eqr["exact_ok"],
                               equality_tolerance=eqr["tolerance_check"]["ok"], wealth=w8["hm"]["wealth"],
                               spy=w8["sm"]["wealth"], lv15=lvm["wealth"], **res)
