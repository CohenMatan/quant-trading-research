# S028 v1.0 — H026 LEARNED STOCK SCORE PORTFOLIO ON DATA v2.1 (owner D206; research/phase11/H026_spec.md, pinned by
# qresearch.p11h026). NO orders (the portfolio is simulated in-host from the frozen panel conventions); nothing after
# 2021-12-31 is requested (the last price row is the 2021-12-31 session): 2011-2021 is H026 DEVELOPMENT; the Holdout
# 2022-01-01 .. 2026-08-31 stays sealed. A subclass of the Data v2.1 host X801 (uploaded byte-identical as qr_x801; X801 =
# the frozen X998 extended through 2021): Data v2.1 universe, Score v1, the H022 population and the H024 features are
# the frozen rules; S028 only ADDS:
#   - the market cap of every reviewed security, the live total-assets ledger 2010-01 .. 2020-12 (as S024 / S026);
#   - the panel RAW open and split x dividend multiplier (S024 construction), SPY total-return arrays;
#   - the H026 months: population (H022 population with all 11 H024 features valid), centred-percentile features,
#     63-session SPY-relative labels, holding-period arrays (qr_h026.holding), SPY;
#   - modes: canary (reproduction digests, coverage, feature recomputation, label purge, SYNTHETIC planted / zero worlds;
#     NO real portfolio result), null (worlds params.seeds of the complete procedure on tether-permuted vectors; the
#     real assignment only hashed), real (the ONE outer walk-forward 2015-2021 with the pinned c_WEALTH + diagnostics).
# New attribute / method names carry the prefix w_ / _w_ (X801 / X998 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_x801, qr_h026, qr_h024,
# qr_h023, qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred, qr_p7_mech, qr_h020_stats, qr_xs, qr_xs_diag, qr_xs_panel,
# qr_v2, qr_data_v21, qr_sec_corrections, qr_industry, qr_fundamentals.
from AlgorithmImports import *
from datetime import date, datetime
import hashlib
import json
import math
import time
import numpy as np
import qr_x801 as X81
import qr_h026 as H
import qr_h024 as K
import qr_p7 as P
import qr_p7_score as S
import qr_p7_export as E
import qr_p7_pred as R
import qr_xs_diag as XD
import qr_xs_panel as XP

W_HIST_START = datetime(2007, 1, 1)
W_LAST = "2021-12-31"
W_REVIEW_FROM = date(2011, 1, 1)
W_LEDGER_FROM, W_LEDGER_TO = date(2010, 1, 1), date(2021, 1, 1)     # total assets 12 months back for reviews to 2021-12
W_H022_END = date(2017, 12, 31)                                      # the frozen H022 / H024 window (reproduction)
W_BATCH = 100
W_SAMPLE = 300
W_SALT = "P11CP1-S028"
W_SYNTH_SEEDS = (991101, 991102)


def _ds(day):
    return str(np.datetime64(int(day), "D"))


def _day(d):
    return int(np.datetime64(d.strftime("%Y-%m-%d")).astype(np.int64))


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


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


class H026Learned(X81.DataV2Export):

    def qr_initialize(self):
        p = self.qr_params
        mode = p.get("mode")
        if mode not in ("canary", "null", "real"):
            raise Exception(f"S028: unknown mode {mode!r}")
        for k in ("spec_sha256", "h026_code_sha256", "data_v21_manifest_sha256"):
            if not p.get(k):
                raise Exception(f"S028: params need {k}")
        if mode in ("null", "real"):
            for k in ("feature_panel_sha256",):
                if not p.get(k):
                    raise Exception(f"S028: {mode} runs need the pinned {k}")
        if mode == "null":
            a, b = (int(x) for x in p["seeds"])
            if not (1 <= a <= b <= H.R_NULL):
                raise Exception("S028: null seeds must lie in 1..5000")
            self.w_seeds = list(range(a, b + 1))
        if mode == "real":
            for k in ("c_wealth", "null_result_sha256", "threshold_commit", "response_panel_sha256"):
                if p.get(k) in (None, ""):
                    raise Exception(f"S028: real mode needs the pinned null provenance ({k})")
        if self.qr["end"] != W_LAST:
            raise Exception("S028: H026 runs end on 2021-12-31")
        self.qr_params = dict(p, mode="export")              # the X801 / X998 initialisation (export mode)
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.w_mode = mode
        self.w_mcap, self.w_ta = {}, {}

    def _month_end(self, t, today, elig, adv, fl):
        super()._month_end(t, today, elig, adv, fl)
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

    def _repair(self):
        super()._repair()
        for t, keep in self.repaired.items():
            for sid in keep:
                r = self.cand[t][sid]
                self.w_mcap.setdefault(t, {})[sid] = self._secmcap(sid, r["cik_sh"], self.mon_sel[t], r["px"])[0]

    def _build(self):
        """X801's panel (identical C / H / L / P / RAW / unverified splits / distributions) plus the RAW open (RO) and
        the split x dividend multiplier (M) (S024 construction), and SPY RAW open / close with its multiplier."""
        super()._build()
        D, N = self.cal.size, len(self.sids)
        RO, M = np.full((D, N), np.nan), np.full((D, N), np.nan)
        st = dict(late_rows=0)
        for i in range(0, N, W_BATCH):
            part = self.sids[i:i + W_BATCH]
            syms = [self.sym[s] for s in part]
            loc = {s: j for j, s in enumerate(part)}
            hr = self.history(syms, W_HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.RAW)
            hs = self.history(syms, W_HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                              data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            sp = self.history(Split, syms, W_HIST_START, self.hist_end)
            dv = self.history(Dividend, syms, W_HIST_START, self.hist_end)
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
        spy = self.history(self.spy, W_HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        O, C = np.full(D, np.nan), np.full(D, np.nan)
        d = XP.session_days(spy.index.get_level_values(-1).values)
        ok = d <= self.last_session
        r = np.searchsorted(self.cal, d[ok])
        O[r], C[r] = spy["open"].to_numpy(dtype=float)[ok], spy["close"].to_numpy(dtype=float)[ok]
        m = np.ones(D)
        key = {X81._sid(self.spy): 0}
        for r_, typ, ref, f in self._events(self.history(Split, [self.spy], W_HIST_START, self.hist_end), key,
                                            self.cal, ("type", "referenceprice", "splitfactor")).get(0, []):
            if "OCCUR" in str(typ).upper() or float(ref) > 0:
                m[:r_] *= float(f)
        de = [(r_, float(a_), float(rf)) for r_, a_, rf in self._events(
            self.history(Dividend, [self.spy], W_HIST_START, self.hist_end), key, self.cal,
            ("distribution", "referenceprice")).get(0, [])]
        self.w_spy = (O, C, m * XP.dividend_multiplier(D, de))
        self.st["w_spy"] = dict(dividends=len(de), missing_rows_from_2010=int(
            (~(np.isfinite(O) & np.isfinite(C)))[int(np.searchsorted(self.cal, _day(date(2010, 1, 4)))):].sum()))

    # ------------------------------------------------------------------------------------------------ scores / features
    def _w_scores(self, reviews, rows_k):
        """Frozen Score v1 per review (S024 code path) -> the H022 population per review (eligible_flag rows)."""
        need = sorted(set(rows_k.values()))
        self.a200 = {j: P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])["above200"][need]
                     for j in range(len(self.sids))}
        self.rix = {k: i for i, k in enumerate(need)}
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

    def _w_h022_reproduction(self, reviews, rows_k, pops, regimes, raw_by_t):
        """The frozen H022 panel digest (S024 _h_digest of S, sector, mom, size, y, y2, y3 over the 83 decisions
        2011-01 .. 2017-11, responses one / two / three reviews ahead within the 2017 window) and the frozen H024
        population digest (finite one-review response and all 11 features valid)."""
        rv = [t for t in reviews if t <= W_H022_END]
        hp, hpop = hashlib.sha256(), hashlib.sha256()
        npop = 0
        for i, t in enumerate(rv[:-1]):
            k = rows_k[t]
            ids = sorted(pops[t])
            ys = {}
            for h in (1, 2, 3):
                y = np.full(len(ids), np.nan)
                if i + h < len(rv):
                    kn = rows_k[rv[i + h]]
                    for n, s in enumerate(ids):
                        j = self.col[s]
                        y[n] = R.response(self.RO[:, j], self.RC[:, j], self.M[:, j], k, kn, self.unv.get(j, ()))[0]
                ys[h] = y
            rec = [str(t), ids, regimes[t]] + [np.asarray(v).tolist() for v in (
                [pops[t][s][0] for s in ids], [pops[t][s][1] for s in ids], [pops[t][s][2] for s in ids],
                [pops[t][s][3] for s in ids], ys[1], ys[2], ys[3])]
            hp.update(json.dumps(rec, separators=(",", ":")).encode())
            Xr = raw_by_t[t]
            okp = np.isfinite(ys[1]) & np.all(np.isfinite(Xr), axis=1)
            keep = [s for s, o in zip(ids, okp) if o]
            npop += len(keep)
            hpop.update(json.dumps([str(t), keep], separators=(",", ":")).encode())
        return dict(h022_panel_sha256=hp.hexdigest(), h024_population_sha256=hpop.hexdigest(), h024_population_rows=npop,
                    decisions=len(rv) - 1)

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

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        p = self.qr_params
        self.st = dict(self.st0, mode=self.w_mode, checks=self.c, store_stats=dict(self.store.stats),
                       spec_sha256=p["spec_sha256"])
        self._repair()
        self._build()
        t0 = time.perf_counter()
        reviews = sorted(self.mon)
        rows_k = {t: self._row(t) for t in reviews}
        # a run ending on a month-end never reaches that month's review (CLAUDE.md): the last review is 2021-11-30
        if str(reviews[-1]) != "2021-11-30" or str(reviews[0])[:7] != "2011-01" or len(reviews) != 131:
            raise Exception(f"S028: reviews {reviews[0]} .. {reviews[-1]} differ from 2011-01 .. 2021-11 (131)")
        pops, sdig, edig, regimes, tech_cache = self._w_scores(reviews, rows_k)
        raw_by_t = {t: self._w_features(t, rows_k[t], sorted(pops[t]), tech_cache) for t in reviews}
        self.st["scores_s"] = round(time.perf_counter() - t0, 1)
        months, cov = self._w_months(reviews, rows_k, pops, raw_by_t)
        self.st["coverage"] = dict(by_year={y: dict(h022_population=v[0], all_11_valid=v[1],
                                                    share=round(v[1] / v[0], 4) if v[0] else None)
                                            for y, v in sorted(cov.items())},
                                   decisions=len(months), first=months[0]["day"], last=months[-1]["day"])
        self.st["data_v21_digests"] = dict(review_scores=sdig, review_eligibility=edig)
        self.st["feature_panel_sha256"] = self._w_feature_digest(months)
        self.st["months_s"] = round(time.perf_counter() - t0, 1)
        if self.w_mode == "canary":
            self.st["reproduction"] = self._w_h022_reproduction(reviews, rows_k, pops, regimes, raw_by_t)
            self._w_canary(months, reviews, rows_k, pops, raw_by_t)
        else:
            if self.st["feature_panel_sha256"] != p["feature_panel_sha256"]:
                raise Exception("S028: the feature panel differs from the pinned digest; nothing computed")
            self.st["response_panel_sha256"] = self._w_response_digest(months)
            if p.get("response_panel_sha256") and self.st["response_panel_sha256"] != p["response_panel_sha256"]:
                raise Exception("S028: the response panel differs from the pinned digest; nothing computed")
            if self.w_mode == "null":
                self._w_null(months)
            else:
                self._w_real(months, regimes, reviews)
        self.st["pit_audit"] = dict(self.audit)
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        text = json.dumps(_plain(self.st), sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRW|{i // 9000}|{text[i:i + 9000]}")

    def _w_emit(self, tag, obj):
        blob = E.pack(json.dumps(_plain(obj), sort_keys=True, separators=(",", ":")))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"{tag}|{i // 9000}|{blob[i:i + 9000]}")
        return dict(blob_sha256=hashlib.sha256(blob.encode()).hexdigest(), blob_chars=len(blob))

    # ------------------------------------------------------------------------------------------------ canary
    def _w_canary(self, months, reviews, rows_k, pops, raw_by_t):
        ck = dict(real_portfolio_computed=False)
        # 1. universe / survivor share / population by year (no return)
        final = set(self.mon[reviews[-1]])
        uy = {}
        for t in reviews:
            u = uy.setdefault(str(t.year), dict(eligible=0, securities=set(), survivor=0, h022_population=0,
                                                repaired=0))
            u["eligible"] += len(self.mon[t])
            u["securities"] |= set(self.mon[t])
            u["survivor"] += sum(1 for s in self.mon[t] if s in final)
            u["h022_population"] += len(pops[t])
            u["repaired"] += len(self.repaired.get(t, ()))
        ck["universe_by_year"] = {y: dict(eligible=u["eligible"], securities=len(u["securities"]),
                                          survivor_share=round(u["survivor"] / u["eligible"], 4) if u["eligible"] else None,
                                          h022_population=u["h022_population"], repaired=u["repaired"])
                                  for y, u in sorted(uy.items())}
        # 2. feature recomputation on a deterministic sample (full histories, no slicing; S026 method)
        tags = sorted(f"{m['day']}|{s}" for m in months for s in m["ids"])
        rec = dict(checked=0, mismatch=0)
        rows = {str(t): t for t in reviews}
        for tag in P.pick(tags, W_SAMPLE, W_SALT):
            day, s = tag.split("|")
            t = rows[day]
            k = rows_k[t]
            j = self.col[s]
            full = S.technical_inputs(self.C[:k + 1, j], self.P[:k + 1, j], k)
            pf = K.price_features(self.C[:k + 1, j], self.P[:k + 1, j], k, self.unv.get(j, ()), self.dist.get(j, ()),
                                  span=10 ** 9)
            ff = K.fund_features(self.mon[t][s]["vals"], self.w_ta.get((t.year - 1, t.month), {}).get(s),
                                 self.w_mcap.get(t, {}).get(s))
            ref = np.array(K.feature_row(full, pf, ff), float)
            got = raw_by_t[t][sorted(pops[t]).index(s)]
            rec["checked"] += 1
            rec["mismatch"] += int(not np.array_equal(ref, got))
        ck["feature_recomputation"] = rec
        # 3. label purge over the real calendar (no label used before its exit)
        fit = H.Fitter(months, [m["X"] for m in months])
        lp = dict(checked=0, violations=0)
        for y in range(H.FIRST_INNER, H.OUTER_YEARS[-1] + 1):
            cut = next(m["cutoff_day"] for m in months if m["test_year"] == y)
            used = fit.months_used(cut)
            lp["checked"] += 1
            lp["violations"] += sum(1 for i in used if not months[i]["exit_day"] < cut)
            lp[str(y)] = dict(train_months=len(used), last_label_exit=_ds(max(months[i]["exit_day"] for i in used)),
                              cutoff=_ds(cut))
        ck["label_purge"] = lp
        # 4. 63-session timing: every label exit row = review row + 63; entries strictly after the review
        tm = dict(months=len(months), exit_row_mismatch=0, entry_not_after_review=0)
        for mo in months:
            if math.isfinite(mo["exit_day"]):
                tm["exit_row_mismatch"] += int(_ds(self.cal[mo["k"] + H.HORIZON]) != _ds(mo["exit_day"]))
            tm["entry_not_after_review"] += int(not mo["days"][0] > mo["cutoff_day"])
        ck["timing"] = tm
        # 5. SYNTHETIC worlds on the real structure: planted coefficients -> edge; zero -> none
        syn = {}
        for name, beta in (("planted", np.r_[0.02, 0, 0, 0, -0.015, 0, 0, 0, 0, 0, 0]), ("zero", np.zeros(11))):
            rng = np.random.default_rng(W_SYNTH_SEEDS[0])
            fake = []
            for mo in months:
                r = mo["X"] @ beta + rng.normal(0, 0.07, len(mo["ids"]))
                d = dict(mo, r_oo=r, r_oc=r, daily=np.outer(np.linspace(1.0 / len(mo["days"]), 1.0, len(mo["days"])), r))
                fake.append(d)
            for i, mo in enumerate(fake):
                fut = fake[i:i + 3]
                if len(fut) == 3 and math.isfinite(mo["exit_day"]):
                    common = set(mo["ids"])
                    acc = {}
                    for f in fut:
                        pos = {s: n for n, s in enumerate(f["ids"])}
                        for s in common:
                            acc[s] = acc.get(s, 1.0) * (1.0 + (f["r_oo"][pos[s]] if s in pos else 0.0))
                    mo["label"] = H.centred_percentile(np.array([acc[s] - 1.0 for s in mo["ids"]]))
            t1 = time.perf_counter()
            w = H.run_world(fake, None, full=True)
            syn[name] = dict(S_WEALTH=w["rec"]["S_WEALTH"], lam=w["rec"]["lam"], beta_2021=_plain(
                w["coef"][(2021, w["lam_y"][2021])][1]), world_s=round(time.perf_counter() - t1, 2))
            t2 = time.perf_counter()
            nul = [H.run_world(fake, sd)["S_WEALTH"] for sd in (1, 2)]
            syn[name]["null_S_WEALTH"] = nul
            syn[name]["null_world_s"] = round((time.perf_counter() - t2) / 2, 2)
            syn[name]["repeat_identical"] = H.run_world(fake, 1)["S_WEALTH"] == nul[0]
        ck["synthetic"] = syn
        ck["estimated_5000_world_minutes"] = round(syn["zero"]["null_world_s"] * 5000 / 60.0, 1)
        self.st["canary"] = ck

    # ------------------------------------------------------------------------------------------------ null / real
    def _w_null(self, months):
        t0 = time.perf_counter()
        rows = []
        for sd in self.w_seeds:
            r = H.run_world(months, sd)
            rows.append([r["seed"], r["S_WEALTH"], r["excess_cagr"], r["maxdd"], r["vol"], r["years_beating"]] + r["lam"])
        out = self._w_emit("QRWN", dict(fields=["seed", "S_WEALTH", "excess_cagr", "maxdd", "vol", "years_beating"]
                                       + [f"lam_{y}" for y in H.OUTER_YEARS], worlds=rows))
        self.st["null"] = dict(seeds=[self.w_seeds[0], self.w_seeds[-1]], worlds=len(rows),
                               nonfinite=sum(1 for r in rows if not math.isfinite(r[1])),
                               world_s=round((time.perf_counter() - t0) / max(1, len(rows)), 3), **out)

    def _w_real(self, months, regimes, reviews):
        p = self.qr_params
        c = float(p["c_wealth"])
        self.st["provenance"] = {k: p[k] for k in ("c_wealth", "null_result_sha256", "threshold_commit",
                                                   "response_panel_sha256", "feature_panel_sha256")}
        w = H.run_world(months, None, full=True)                      # the primary result first
        ms = [months[i] for i in w["idx"]]
        sc = w["scores"]
        stress = H.simulate(ms, sc, slip=H.STRESS_SLIPPAGE)["wealth"]
        stress_spy = H.spy_simulate(ms, slip=H.STRESS_SLIPPAGE)["wealth"]
        g = H.gates(w["hm"], w["sm"], w["yh"], w["ys"], stress, stress_spy, c)
        coef = {str(y): dict(lam=w["lam_y"][y], b0=w["coef"][(y, w["lam_y"][y])][0],
                             beta=w["coef"][(y, w["lam_y"][y])][1]) for y in H.OUTER_YEARS}
        h = w["h"]
        out = dict(c_wealth=c, gates=g, rec=w["rec"], h026=w["hm"], spy=w["sm"], years_h026=w["yh"], years_spy=w["ys"],
                   coefficients=coef, inner=[[y, lam, v] for (y, lam), v in sorted(w["inner"].items())],
                   selection={str(Y): w["sel"][Y] for Y in H.OUTER_YEARS},
                   ntrain={f"{y}|{lam}": n for (y, lam), n in sorted(w["ntrain"].items())},
                   trades=dict(buys=h["buys"], sells=h["sells"], trades=h["trades"], commissions=h["commissions"],
                               slippage=h["slippage"], turnover=h["turnover"], holdings=h["holdings"],
                               cash_share=h["cash_share"]),
                   stress=dict(h026=stress, spy=stress_spy), daily_h026=h["daily"], daily_spy=w["s"]["daily"],
                   days=w["days"], months=[m["day"] for m in ms])
        # sector concentration of the held portfolio (counts of FF12 at each rebalance)
        secs = {}
        for mo, pk in zip(ms, h["picks"]):
            pos = {s: n for n, s in enumerate(mo["ids"])}
            for s in pk:
                nm = XD.FF12_NAMES[int(mo["sector"][pos[s]])]
                secs[nm] = secs.get(nm, 0) + 1
        out["sector_counts"] = secs
        # NON-GATING diagnostics (same frozen yearly coefficients; no refit)
        diag = {}
        for name, kw in (("capital_200k", dict(capital=200_000.0)), ("top10", dict(k=10)), ("top20", dict(k=20))):
            hh = H.simulate(ms, sc, daily=True, **kw)
            ss = H.spy_simulate(ms, capital=kw.get("capital", H.CAPITAL), daily=True)
            hm = H.path_metrics(hh["daily"], w["days"], kw.get("capital", H.CAPITAL), hh["wealth"])
            sm = H.path_metrics(ss["daily"], w["days"], kw.get("capital", H.CAPITAL), ss["wealth"])
            diag[name] = dict(wealth=hh["wealth"], spy=ss["wealth"], S_WEALTH=math.log(hh["wealth"] / ss["wealth"]),
                              cagr=hm["cagr"], spy_cagr=sm["cagr"], maxdd=hm["maxdd"], vol=hm["vol"])
        # sector-neutral and regime (monthly)
        sn, reg = [], {}
        for i, (mo, pk) in enumerate(zip(ms, h["picks"])):
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
            key = str(regimes[t])
            reg.setdefault(key, []).append(port - mo["spy_oo"])
        diag["sector_neutral"] = dict(months=len(sn), mean_monthly=float(np.mean(sn)) if sn else None,
                                      t=float(np.mean(sn) / (np.std(sn, ddof=1) / math.sqrt(len(sn)))) if len(sn) > 2 else None)
        diag["regime"] = {k: dict(months=len(v), mean_monthly_relative=float(np.mean(v))) for k, v in sorted(reg.items())}
        out["diagnostics"] = diag
        # final model only if every gate passes (spec section 12)
        if g["all"]:
            Xs = [m["X"] for m in months]
            fit = H.Fitter(months, Xs)
            yrs = {y: [i for i, m in enumerate(months) if m["test_year"] == y] for y in range(H.FIRST_INNER, 2022)}
            inner21 = {}
            ms21 = [months[i] for i in yrs[2021]]
            spy21 = H.spy_simulate(ms21)["wealth"]
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
        res = self._w_emit("QRWR", out)
        self.st["real"] = dict(S_WEALTH=g["S_WEALTH"], gates={k: v for k, v in g.items() if k.startswith("D") or k == "all"},
                               wealth=w["hm"]["wealth"], spy=w["sm"]["wealth"], **res)
