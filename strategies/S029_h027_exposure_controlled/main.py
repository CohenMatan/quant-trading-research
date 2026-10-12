# S029 v1.0 — H027 EXPOSURE-CONTROLLED LEARNED STOCK SCORE ON DATA v2.1 (owner D213; research/phase12/H027_spec.md,
# pinned by qresearch.p12h027). NO orders (portfolios are simulated in-host); nothing after 2021-12-31 is requested:
# 2011-2021 is fully seen development data; the Holdout 2022-01-01 .. 2026-08-31 stays sealed. A subclass of the
# pinned H026 host S028 (uploaded byte-identical as qr_s028), itself a subclass of the Data v2.1 host X801 (qr_x801).
# The real H027 portfolio IS the frozen H026 procedure (qr_h026.run_world(months, None)); S029 only ADDS:
#   - memory reduction (spec section 9): the run-time fundamentals store / ledgers released before the matrix build;
#     the 200-day state computed right after X801's build and the high / low matrices freed before S028's open-price
#     and multiplier matrices; every price matrix freed after the months exist (null / real); stage memory reported;
#   - the LOWVOL-conditional null (qr_h027.conditional_permuted: LOWVOL stays, the ten other features move together
#     from a persistent tether donor; the complete pipeline rerun per world);
#   - LV15_CONTROL (Top-15 by LOWVOL alone), gates A1-A6, the LOWVOL-factor regression and the H026 diagnostics;
#   - modes: canary (equivalence gate vs H026 pins and committed E028-04 null rows, conditional-permutation checks,
#     LV15 pick check, synthetic worlds A / B; NO real H027 / LV15 / factor result), null (conditional worlds
#     params.seeds; the real assignment only hashed), real (the ONE run with the pinned c_WEALTH_CONDITIONAL).
# New attribute / method names carry the prefix g_ / _g_ (X801 / X998 / S028 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_s028, qr_h027, qr_x801,
# qr_h026, qr_h024, qr_h023, qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred, qr_p7_mech, qr_h020_stats, qr_xs,
# qr_xs_diag, qr_xs_panel, qr_v2, qr_data_v21, qr_sec_corrections, qr_industry, qr_fundamentals.
from AlgorithmImports import *
from datetime import date
import gc
import hashlib
import json
import math
import time
import numpy as np
import qr_s028 as S28
import qr_x801 as X81
import qr_h026 as H
import qr_h027 as G
import qr_p7 as P
import qr_p7_export as E
import qr_p7_score as S
import qr_xs_diag as XD
import qr_xs_panel as XP

G_SYNTH_A = (-0.03, 0.0)            # synthetic world A: LOWVOL only (raw volatility percentile coefficient), GPA 0
G_SYNTH_B = (-0.03, 0.03)           # synthetic world B: LOWVOL + GPA
G_SYNTH_SIGMA = 0.07
G_SYNTH_REPS_A, G_SYNTH_REPS_B, G_SYNTH_NULLS = 5, 3, 19
G_SYNTH_SEED = 270001
G_PERM_CHECK_SEEDS = (1, 2, 3)
_plain, _ds = S28._plain, S28._ds


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


class H027Conditional(S28.H026Learned):

    def qr_initialize(self):
        p = self.qr_params
        mode = p.get("mode")
        if mode not in ("canary", "null", "real"):
            raise Exception(f"S029: unknown mode {mode!r}")
        for k in ("spec_sha256", "h027_code_sha256", "data_v21_manifest_sha256", "h026_feature_panel_sha256",
                  "h026_response_panel_sha256"):
            if not p.get(k):
                raise Exception(f"S029: params need {k}")
        if mode == "canary" and not p.get("h026_null_rows_sha256"):
            raise Exception("S029: the canary needs the committed E028-04 null-row digest")
        if mode == "null":
            a, b = (int(x) for x in p["seeds"])
            if not (1 <= a <= b <= G.R_NULL):
                raise Exception("S029: null seeds must lie in 1..5000")
            self.g_seeds = list(range(a, b + 1))
        if mode == "real":
            for k in ("c_wealth_conditional", "null_result_sha256", "threshold_commit", "h026_real_wealth",
                      "h026_real_s_wealth"):
                if p.get(k) in (None, ""):
                    raise Exception(f"S029: real mode needs the pinned {k}")
        # S028's initialisation with S028-compatible parameters (canary mode: no S028-specific pins needed)
        self.qr_params = dict(spec_sha256=p["spec_sha256"], h026_code_sha256=p["h027_code_sha256"],
                              data_v21_manifest_sha256=p["data_v21_manifest_sha256"], mode="canary")
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.g_mode = self.w_mode = mode
        self.g_mem = []

    # ------------------------------------------------------------------------------------------------ memory
    def _g_stage(self, name):
        self.g_mem.append([name, round(time.perf_counter() - self.t0, 1), _mem_now()])

    def _g_release_run_state(self):
        """The run-time fundamentals store, revenue ledger, first-seen ledger, weekly checks and digest buffers are
        used only while the algorithm runs (month ends / weekly checks); nothing after the run reads them."""
        for a in ("store", "rev", "led", "wk", "dg"):
            if hasattr(self, a):
                setattr(self, a, None)
        _trim()

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

    def _g_free_panel(self):
        for a in ("C", "P", "RAW", "RO", "RC", "M", "a200", "mon", "cand", "val", "w_ta"):
            if hasattr(self, a):
                setattr(self, a, None)
        _trim()

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        p = self.qr_params
        self.st = dict(self.st0, mode=self.g_mode, hypothesis="H027", checks=self.c,
                       store_stats=dict(self.store.stats), spec_sha256=p["spec_sha256"])
        self._g_stage("on_end_start")
        self._g_release_run_state()
        self._g_stage("after_run_state_released")
        self._repair()
        self._g_stage("after_repair")
        self._build()
        self._g_stage("after_build")
        t0 = time.perf_counter()
        reviews = sorted(self.mon)
        rows_k = {t: self._row(t) for t in reviews}
        if str(reviews[-1]) != "2021-11-30" or str(reviews[0])[:7] != "2011-01" or len(reviews) != 131:
            raise Exception(f"S029: reviews {reviews[0]} .. {reviews[-1]} differ from 2011-01 .. 2021-11 (131)")
        pops, sdig, edig, regimes, tech_cache = self._w_scores(reviews, rows_k)
        self._g_stage("after_scores")
        raw_by_t = {t: self._w_features(t, rows_k[t], sorted(pops[t]), tech_cache) for t in reviews}
        months, cov = self._w_months(reviews, rows_k, pops, raw_by_t)
        self._g_stage("after_months")
        self.st["coverage"] = dict(by_year={y: dict(h022_population=v[0], all_11_valid=v[1],
                                                    share=round(v[1] / v[0], 4) if v[0] else None)
                                            for y, v in sorted(cov.items())},
                                   decisions=len(months), first=months[0]["day"], last=months[-1]["day"])
        self.st["data_v21_digests"] = dict(review_scores=sdig, review_eligibility=edig)
        self.st["feature_panel_sha256"] = self._w_feature_digest(months)
        self.st["response_panel_sha256"] = self._w_response_digest(months)
        self.st["months_s"] = round(time.perf_counter() - t0, 1)
        eq = dict(feature_panel=self.st["feature_panel_sha256"] == p["h026_feature_panel_sha256"],
                  response_panel=self.st["response_panel_sha256"] == p["h026_response_panel_sha256"])
        self.st["equivalence"] = eq
        if self.g_mode == "canary":
            self.st["reproduction"] = self._w_h022_reproduction(reviews, rows_k, pops, regimes, raw_by_t)
            del tech_cache, raw_by_t, pops
            self._g_free_panel()
            self._g_stage("after_panel_freed")
            self._g_canary(months)
        else:
            if not (eq["feature_panel"] and eq["response_panel"]):
                raise Exception("S029: the feature / response panel differs from the pinned H026 digests; nothing computed")
            del tech_cache, raw_by_t, pops
            self._g_free_panel()
            self._g_stage("after_panel_freed")
            if self.g_mode == "null":
                self._g_null(months)
            else:
                self._g_real(months, regimes, reviews)
        self._g_stage("end")
        self.st["pit_audit"] = dict(self.audit)
        self.st["memory"] = self.g_mem
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        self.st["max_rss_mb"] = _mem_now().get("ru_maxrss_mb")
        text = json.dumps(_plain(self.st), sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRG|{i // 9000}|{text[i:i + 9000]}")

    # ------------------------------------------------------------------------------------------------ canary
    def _g_canary(self, months):
        p = self.qr_params
        ck = dict(real_h027_result_computed=False)
        # 1. equivalence gate: H026's UNCONDITIONAL null worlds 1-25 through the frozen qr_h026.run_world (= E028-04)
        t1 = time.perf_counter()
        rows = []
        for sd in H.DETERMINISM_SEEDS:
            r = H.run_world(months, sd)
            rows.append([r["seed"], r["S_WEALTH"], r["excess_cagr"], r["maxdd"], r["vol"], r["years_beating"]] + r["lam"])
        text = json.dumps(_plain(rows), separators=(",", ":"))
        ck["h026_null_rows"] = dict(rows=_plain(rows), sha256=hashlib.sha256(text.encode()).hexdigest(),
                                    equal_to_e028_04=hashlib.sha256(text.encode()).hexdigest() == p["h026_null_rows_sha256"],
                                    world_s=round((time.perf_counter() - t1) / len(rows), 3))
        # 2. conditional permutation on the real months: LOWVOL kept, OTHER vector from one donor, persistence,
        #    no self-match, recipients' returns untouched
        before = self._w_response_digest(months)
        pc = dict(months=0, rows=0, lowvol_changed=0, other_not_donor_row=0, self_matches=0, persistence_checked=0,
                  persistence_broken=0, permutation_not_exact=0)
        other = list(G.OTHER)
        for sd in G_PERM_CHECK_SEEDS:
            Xs = G.conditional_permuted(months, sd)
            dn = G.donors(months, sd)
            prev = None
            for m, X, d in zip(months, Xs, dn):
                pc["months"] += 1
                pc["rows"] += len(m["ids"])
                pos = {s: i for i, s in enumerate(m["ids"])}
                pc["lowvol_changed"] += int(not np.array_equal(X[:, G.LOWVOL], m["X"][:, G.LOWVOL]))
                for i, s in enumerate(m["ids"]):
                    pc["self_matches"] += int(d[s] == s)
                    pc["other_not_donor_row"] += int(not np.array_equal(X[i, other], m["X"][pos[d[s]], other]))
                    if prev is not None and s in prev and prev[s] in pos:
                        pc["persistence_checked"] += 1
                        pc["persistence_broken"] += int(d[s] != prev[s])
                pc["permutation_not_exact"] += int(sorted(map(tuple, X[:, other])) != sorted(map(tuple, m["X"][:, other])))
                prev = d
        pc["responses_unchanged"] = self._w_response_digest(months) == before
        # the frozen tether keeps a pair while both stay, except its documented fixed-point splice (a lone free stock
        # matched to itself is spliced into one kept pair): at most one changed pair per month and seed
        pc["persistence_within_splice_bound"] = pc["persistence_broken"] <= pc["months"]
        pc["persistence_kept_share"] = (1.0 - pc["persistence_broken"] / pc["persistence_checked"]
                                        if pc["persistence_checked"] else None)
        ck["conditional_permutation"] = pc
        # 3. LV15 picks = an independent lowest-volatility walk (no return read)
        lc = dict(months=0, mismatch=0)
        for m in months:
            if m["test_year"] not in H.OUTER_YEARS:
                continue
            lc["months"] += 1
            got = sorted(H.pick(m, G.lv15_scores([m])[0]))
            order = sorted(range(len(m["ids"])), key=lambda i: (m["raw"][i, G.LOWVOL], m["ids"][i]))
            out, cnt = [], {}
            for i in order:
                if not m["open_ok"][i] or cnt.get(m["sector"][i], 0) >= H.SECTOR_CAP:
                    continue
                out.append(i)
                cnt[m["sector"][i]] = cnt.get(m["sector"][i], 0) + 1
                if len(out) == H.K:
                    break
            lc["mismatch"] += int(got != sorted(out))
        ck["lv15_picks"] = lc
        # 4. costs by hand on a toy month; S_WEALTH arithmetic; the c order statistic
        ck["costs_by_hand"] = self._g_costs_check()
        ck["critical_value_50th_of_5000"] = H.critical_value(list(range(5000))) == 4950.0
        # 5. synthetic worlds A (LOWVOL only) and B (LOWVOL + GPA) on the real month structure (SPY real)
        ck["synthetic"] = self._g_synthetic(months)
        ck["estimated_5000_world_minutes"] = round(ck["synthetic"]["world_s"] * 5000 / 60.0, 1)
        self.st["canary"] = ck

    @staticmethod
    def _g_costs_check():
        m = dict(ids=["A", "B"], sector=np.array([0, 1]), open_ok=np.array([True, True]), r_oo=np.array([0.1, -0.1]),
                 r_oc=np.array([0.1, -0.1]), alive_next=np.array([True, True]), alive_end=np.array([True, True]),
                 daily=np.array([[0.1, -0.1]]))
        w = H.simulate([m], [np.array([2.0, 1.0])], capital=1000.0, k=2, slip=0.001, comm=7.0)["wealth"]
        a = 500.0 if 2 * (500.0 * 1.001 + 7.0) <= 1000.0 else (1000.0 - 14.0) / (2 * 1.001)
        cash = 1000.0 - 2 * (a * 1.001 + 7.0)
        exp_ = cash + a * 1.1 * 0.999 - 7.0 + a * 0.9 * 0.999 - 7.0
        return dict(wealth=w, expected=exp_, ok=abs(w - exp_) < 1e-9)

    def _g_synthetic(self, months):
        """Returns = a . [x_LOWVOL, x_GPA] + noise on the real feature matrices; labels recomputed from three synthetic
        months ahead (as S028's canary); per replicate the real-assignment model vs G_SYNTH_NULLS conditional nulls."""
        gpa = H.FEATURES.index("GPA")
        out = {}
        t0 = time.perf_counter()
        nworld = 0
        for name, (bl, bg), reps in (("A", G_SYNTH_A, G_SYNTH_REPS_A), ("B", G_SYNTH_B, G_SYNTH_REPS_B)):
            pct, reals = [], []
            for rep in range(reps):
                rng = np.random.default_rng(G_SYNTH_SEED + 100 * (name == "B") + rep)
                fake = []
                for mo in months:
                    r = bl * mo["X"][:, G.LOWVOL] + bg * mo["X"][:, gpa] + rng.normal(0, G_SYNTH_SIGMA, len(mo["ids"]))
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
                real = G.run_conditional(fake, None)["S_WEALTH"]
                nul = [G.run_conditional(fake, sd)["S_WEALTH"] for sd in range(1, G_SYNTH_NULLS + 1)]
                nworld += 1 + len(nul)
                rep2 = G.run_conditional(fake, 1)["S_WEALTH"] == nul[0]
                reals.append(real)
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
        t0 = time.perf_counter()
        rows, coefs = [], {}
        for sd in self.g_seeds:
            r = G.run_conditional(months, sd)
            rows.append(G.row(r))
            if sd in G.DETERMINISM_SEEDS:
                coefs[str(sd)] = r["coef"]
        out = self._w_emit("QRGN", dict(fields=list(G.FIELDS), worlds=rows, coef=coefs))
        self.st["null"] = dict(seeds=[self.g_seeds[0], self.g_seeds[-1]], worlds=len(rows),
                               nonfinite=sum(1 for r in rows if not math.isfinite(r[1])),
                               world_s=round((time.perf_counter() - t0) / max(1, len(rows)), 3), **out)

    # ------------------------------------------------------------------------------------------------ real
    def _g_real(self, months, regimes, reviews):
        p = self.qr_params
        c = float(p["c_wealth_conditional"])
        self.st["provenance"] = {k: p[k] for k in ("c_wealth_conditional", "null_result_sha256", "threshold_commit",
                                                   "h026_feature_panel_sha256", "h026_response_panel_sha256")}
        w = H.run_world(months, None, full=True)                      # the frozen H026 procedure = the real H027
        ms = [months[i] for i in w["idx"]]
        days, cap = w["days"], H.CAPITAL
        repro = dict(wealth=w["hm"]["wealth"], expected_wealth=float(p["h026_real_wealth"]),
                     s_wealth=w["rec"]["S_WEALTH"], expected_s_wealth=float(p["h026_real_s_wealth"]))
        repro["ok"] = (abs(repro["wealth"] / repro["expected_wealth"] - 1.0) <= 1e-9
                       and abs(repro["s_wealth"] - repro["expected_s_wealth"]) <= 1e-9)
        lvr = G.lv15(ms)
        lvm = H.path_metrics(lvr["daily"], days, cap, lvr["wealth"])
        ylv = H.year_returns(lvr["daily"], days, cap)
        st_h = H.simulate(ms, w["scores"], slip=H.STRESS_SLIPPAGE)["wealth"]
        st_s = H.spy_simulate(ms, slip=H.STRESS_SLIPPAGE)["wealth"]
        st_lv = G.lv15(ms, slip=H.STRESS_SLIPPAGE, daily=False)["wealth"]
        g = G.gates(w["hm"], w["sm"], lvm, w["yh"], w["ys"], ylv, st_h, st_s, st_lv, c)
        rk_h = G.risk(w["h"]["daily"], w["s"]["daily"], days, cap)
        rk_lv = G.risk(lvr["daily"], w["s"]["daily"], days, cap)
        risk = {n: {k: v for k, v in r.items() if k not in ("rh", "rs")} for n, r in (("h027", rk_h), ("lv15", rk_lv))}
        risk["spy"] = dict(beta=1.0, up_capture=1.0, down_capture=1.0)
        h = w["h"]
        coef = {str(y): dict(lam=w["lam_y"][y], b0=w["coef"][(y, w["lam_y"][y])][0],
                             beta=w["coef"][(y, w["lam_y"][y])][1]) for y in H.OUTER_YEARS}
        out = dict(c_wealth_conditional=c, gates=g, reproduction=repro, rec=w["rec"], h027=w["hm"], spy=w["sm"],
                   lv15=lvm, years_h027=w["yh"], years_spy=w["ys"], years_lv15=ylv, risk=risk,
                   coefficients=coef, selection={str(Y): w["sel"][Y] for Y in H.OUTER_YEARS},
                   trades=dict(buys=h["buys"], sells=h["sells"], trades=h["trades"], commissions=h["commissions"],
                               slippage=h["slippage"], turnover=h["turnover"], holdings=h["holdings"],
                               cash_share=h["cash_share"]),
                   lv15_trades=dict(trades=lvr["trades"], commissions=lvr["commissions"], slippage=lvr["slippage"],
                                    turnover=lvr["turnover"], holdings=lvr["holdings"], cash_share=lvr["cash_share"]),
                   stress=dict(h027=st_h, spy=st_s, lv15=st_lv), daily_h027=h["daily"], daily_spy=w["s"]["daily"],
                   daily_lv15=lvr["daily"], days=days, months=[m["day"] for m in ms])
        # non-gating diagnostics (spec section 8; never rescue)
        diag = {}
        fac = G.lowvol_factor(ms)
        dep = G.period_returns(h["daily"], ms, cap) - G.period_returns(w["s"]["daily"], ms, cap)
        diag["lowvol_factor_regression"] = dict(G.nw_regression(dep, fac), factor_mean=float(np.nanmean(fac)),
                                                factor=_plain(fac), dependent=_plain(dep))
        for name, kw in (("capital_200k", dict(capital=200_000.0)), ("top10", dict(k=10)), ("top20", dict(k=20))):
            hh = H.simulate(ms, w["scores"], daily=True, **kw)
            ss = H.spy_simulate(ms, capital=kw.get("capital", cap), daily=True)
            hm = H.path_metrics(hh["daily"], days, kw.get("capital", cap), hh["wealth"])
            sm = H.path_metrics(ss["daily"], days, kw.get("capital", cap), ss["wealth"])
            diag[name] = dict(wealth=hh["wealth"], spy=ss["wealth"], S_WEALTH=math.log(hh["wealth"] / ss["wealth"]),
                              cagr=hm["cagr"], spy_cagr=sm["cagr"], maxdd=hm["maxdd"], vol=hm["vol"])
        picks = H.simulate(ms, w["scores"], keep_trades=True)["picks"]
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
        mark = {n: np.r_[cap, np.asarray(x, float)[ends]] for n, x in (("h027", h["daily"]), ("spy", w["s"]["daily"]),
                                                                        ("lv15", lvr["daily"]))}
        mar = {}
        for mon in ("2020-02", "2020-03", "2020-04"):
            i = lab.index(mon) + 1
            mar[mon] = {n: float(v[i] / v[i - 1] - 1.0) for n, v in mark.items()}
        diag["march_2020"] = mar
        out["diagnostics"] = diag
        if g["all"]:                                                   # final score (H026 spec section 12 code)
            Xs = [m["X"] for m in months]
            fit = H.Fitter(months, Xs)
            yrs = {y: [i for i, m in enumerate(months) if m["test_year"] == y] for y in range(H.FIRST_INNER, 2022)}
            ms21 = [months[i] for i in yrs[2021]]
            spy21 = H.spy_simulate(ms21)["wealth"]
            inner21 = {}
            for lam in H.LAMBDAS:
                b = w["coef"][(2021, lam)][1]
                inner21[lam] = math.log(H.simulate(ms21, [Xs[i] @ b for i in yrs[2021]])["wealth"] / spy21)
            cand = []
            for lam in H.LAMBDAS:
                ls = [w["inner"][(y, lam)] for y in range(H.FIRST_INNER, 2021)] + [inner21[lam]]
                cand.append((sum(ls), min(ls), lam))
            lam_f = max(cand, key=lambda c_: (c_[0], c_[1], c_[2]))[2]
            b0, b, n = fit.fit(float(self.cal[-1]), lam_f)
            out["final_model"] = dict(lam=lam_f, b0=b0, beta=dict(zip(H.FEATURES, b.tolist())), train_months=n,
                                      selection=cand)
        res = self._w_emit("QRGR", out)
        self.st["real"] = dict(S_WEALTH=g["S_WEALTH"], gates={k: v for k, v in g.items() if k.startswith("A") or k == "all"},
                               reproduction_ok=repro["ok"], wealth=w["hm"]["wealth"], spy=w["sm"]["wealth"],
                               lv15=lvm["wealth"], **res)
