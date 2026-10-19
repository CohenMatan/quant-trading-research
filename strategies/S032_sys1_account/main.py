# S032 v1.0 — SYS-1 SINGLE-ACCOUNT DEFENSIVE SLEEVE + SPY TEST (owner D251 / D252; research/longhorizon/sys1/
# SYS1_protocol.md, pinned by qresearch.sys1). NO orders (every account is simulated in-host by qr_sys1); nothing after
# 2021-12-31 is requested; the Holdout 2022-01-01 .. 2026-08-31 stays sealed. H028 stays REJECTED; nothing about H028
# (score, lambda, Top-15, sector cap, costs, frozen results) is changed: the stock sleeve uses the frozen H028 / LV15
# scores computed by the pinned H028 host S030 (uploaded byte-identical as qr_s030), itself a subclass of S029 / S028 /
# X801 (Data v2.1). S032 only ADDS:
#   - SPLV / USMV RAW open / close and their split x dividend multipliers (the SPY construction of S028, verbatim), read
#     through history requests WITHOUT a subscription (D166);
#   - per decision month: ETF holding-period arrays, Blume-adjusted trailing-252-session betas (rows <= the review row)
#     of every population stock and of SPLV / USMV, and point-in-time market-cap shares (overlap proxy);
#   - modes (params.sys1_mode): canary (C1-C7 checks; NO SYS-1 arm result) and eval (the ONE evaluation: arms A0-A3,
#     BM-X, D1-D3 at 0.10% and 0.20% slippage; STOP if the frozen reproduction or SPLV fails).
# The panel equivalence gate of S029 runs first in both modes (params.mode = "real"): a panel that differs from the
# pinned H026 digests stops the run before anything is computed.
# New attribute / method names carry the prefix y_ / _y_ (X801 / X998 / S028 / S029 / S030 names keep their meanings).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_s030, qr_sys1, qr_s029,
# qr_h028, qr_s028, qr_h027, qr_x801, qr_h026, qr_h024, qr_h023, qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred,
# qr_p7_mech, qr_xs, qr_xs_diag, qr_xs_panel, qr_v2, qr_data_v21, qr_sec_corrections, qr_industry, qr_fundamentals
# (the H020 tether module imported by qr_p7_pred is uploaded by the qr_p7_pred rule; the chart modules are not needed).
from AlgorithmImports import *
from datetime import date, datetime, timedelta
import math
import time
import numpy as np
import qr_s030 as S30
import qr_s028 as S28
import qr_x801 as X81
import qr_h026 as H
import qr_h027 as G
import qr_h028 as F
import qr_sys1 as Y
import qr_xs_panel as XP

Y_ETFS = (("splv", "SPLV"), ("usmv", "USMV"))
Y_GATING = "splv"                       # owner OD-4: SPLV gating, USMV diagnostic only
Y_BIG_MOVE = 0.20                       # |daily total return| above this is counted (data sanity, counts only)
Y_C5_SEEDS = (1, 2, 3)                  # canary C5: seeded random scores (never an evaluation arm)
Y_C7_REVIEWS = 3                        # canary C7: reviews x stocks re-estimated from data truncated at the review
Y_C7_STOCKS = 8
_plain, _ds, _day = S28._plain, S28._ds, S28._day


class SYS1Account(S30.H028Fixed):

    def qr_initialize(self):
        p = self.qr_params
        mode = p.get("sys1_mode")
        if mode not in ("canary", "eval"):
            raise Exception(f"S032: unknown sys1_mode {mode!r}")
        if p.get("mode") != "real":
            raise Exception("S032: the S030 initialisation runs in real mode (panel equivalence gate)")
        for k in ("sys1_protocol_sha256", "sys1_code_sha256", "frozen_h028", "frozen_spy_wealth", "frozen_lv15_wealth",
                  "frozen_spy_wealth_200k"):
            if p.get(k) in (None, ""):
                raise Exception(f"S032: params need {k}")
        if mode == "eval" and not p.get("canary_result_sha256"):
            raise Exception("S032: the evaluation needs the committed E032-01 canary result digest")
        super().qr_initialize()
        self.y_mode = mode

    # ------------------------------------------------------------------------------------------------ ETF data
    def _build(self):
        super()._build()
        self._y_etfs()

    def _y_etf_arrays(self, sym, end):
        """RAW open / close and the split x dividend multiplier of one ETF: the S028 SPY construction verbatim, rows on
        the session calendar only, events on or before the last session (or `end`, a calendar row)."""
        D = self.cal.size
        O, C = np.full(D, np.nan), np.full(D, np.nan)
        info = dict(bars=0, late_rows=0, unknown_rows=0)
        h = self.history([sym], S28.W_HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                         data_normalization_mode=DataNormalizationMode.RAW)
        if h is not None and not h.empty:
            d = XP.session_days(h.index.get_level_values(-1).values)
            info["late_rows"] = int((d > self.last_session).sum())
            pc = np.minimum(np.searchsorted(self.cal, d), D - 1)
            ok = (self.cal[pc] == d) & (d <= self.last_session) & (pc <= end)
            if np.unique(pc[ok]).size != int(ok.sum()):
                raise Exception("S032: two ETF bars map to one session")
            O[pc[ok]] = h["open"].to_numpy(dtype=float)[ok]
            C[pc[ok]] = h["close"].to_numpy(dtype=float)[ok]
            info["bars"] = int(ok.sum())
            info["unknown_rows"] = int(((self.cal[pc] != d) & (d >= self.cal[0]) & (d <= self.last_session)).sum())
        m = np.ones(D)
        key = {X81._sid(sym): 0}
        splits = 0
        for r_, typ, ref, f in self._events(self.history(Split, [sym], S28.W_HIST_START, self.hist_end), key,
                                            self.cal, ("type", "referenceprice", "splitfactor")).get(0, []):
            if ("OCCUR" in str(typ).upper() or float(ref) > 0) and r_ <= end:
                m[:r_] *= float(f)
                splits += 1
        de = [(r_, float(a_), float(rf)) for r_, a_, rf in self._events(
            self.history(Dividend, [sym], S28.W_HIST_START, self.hist_end), key, self.cal,
            ("distribution", "referenceprice")).get(0, []) if r_ <= end]
        info.update(split_events=splits, distributions=len(de))
        return O, C, m * XP.dividend_multiplier(D, de), info

    def _y_etfs(self):
        self.y_etf, self.y_sym, st = {}, {}, {}
        last = int(self.cal.size - 1)
        for name, tk in Y_ETFS:
            sym = Symbol.create(tk, SecurityType.EQUITY, Market.USA)
            O, C, m, info = self._y_etf_arrays(sym, last)
            fb = np.flatnonzero(np.isfinite(C) & (C > 0))
            info.update(symbol=str(sym.id), first_bar=_ds(self.cal[fb[0]]) if fb.size else None,
                        last_bar=_ds(self.cal[fb[-1]]) if fb.size else None)
            self.y_etf[name], self.y_sym[name] = (O, C, m), sym
            st[name] = info
        self.st["y_etf"] = st

    # ------------------------------------------------------------------------------------------------ months
    def _w_months(self, reviews, rows_k, pops, raw_by_t):
        months, cov = super()._w_months(reviews, rows_k, pops, raw_by_t)
        self._y_augment(months, reviews)
        return months, cov

    def _y_tr(self, j, lo, hi):
        """Total-return index of panel column j over rows lo..hi (RAW close x split x dividend multiplier, the frozen
        holding-period construction); rows with an unverified split are blanked."""
        tr = self.RC[lo:hi + 1, j] * self.M[lo:hi + 1, j]
        for u in self.unv.get(j, ()):
            if lo <= int(u) <= hi:
                tr[int(u) - lo] = np.nan
        return tr

    def _y_augment(self, months, reviews):
        """ETF holding-period arrays (the S028 SPY formulas), Blume-adjusted trailing betas at the review row k (data at
        or before k only) and PIT market-cap shares, for every decision month (betas / shares: outer years only)."""
        t0 = time.perf_counter()
        last_row = int(self.cal.size - 1)
        Os, Cs, ms_ = self.w_spy
        spy_tr = Cs * ms_
        etf_tr = {n: C * m for n, (O, C, m) in self.y_etf.items()}
        bst = dict(stock_betas=0, insufficient=0, raw_below_0=0, raw_above_1=0, blume_below_0=0, blume_above_1=0)
        for i, mo in enumerate(months):
            t = reviews[i]
            if mo["day"] != str(t):
                raise Exception("S032: decision months and reviews are misaligned")
            k = mo["k"]
            e = k + 1
            end = e + len(mo["days"]) - 1
            nxt = end + 1 if i + 1 < len(months) else None
            if end > last_row or (nxt is not None and nxt != months[i + 1]["k"] + 1):
                raise Exception("S032: holding-period rows differ from the month construction")
            for name, (O, C, m) in self.y_etf.items():
                sb = O[e] * m[e]
                tr = C[e:end + 1] * m[e:end + 1] / sb - 1.0
                mo[f"{name}_daily"] = tr
                mo[f"{name}_oc"] = float(tr[-1])
                mo[f"{name}_oo"] = float(O[nxt] * m[nxt] / sb - 1.0) if nxt is not None else float(tr[-1])
            if mo["test_year"] not in H.OUTER_YEARS:
                continue
            lo = k - Y.BETA_WIN
            mk = spy_tr[lo:k + 1]
            raw = np.array([Y.beta_at(self._y_tr(self.col[s], lo, k), mk, Y.BETA_WIN)[0] for s in mo["ids"]])
            mo["beta_raw"] = raw
            mo["beta"] = np.array([Y.blume(b) for b in raw])
            fin = np.isfinite(raw)
            bst["stock_betas"] += int(raw.size)
            bst["insufficient"] += int((~fin).sum())
            bst["raw_below_0"] += int((raw[fin] < 0).sum())
            bst["raw_above_1"] += int((raw[fin] > 1).sum())
            bst["blume_below_0"] += int((mo["beta"] < 0).sum())
            bst["blume_above_1"] += int((mo["beta"] > 1).sum())
            for name in etf_tr:
                b, n = Y.beta_at(etf_tr[name][lo:k + 1], mk, Y.BETA_WIN)
                mo[f"beta_{name}_raw"], mo[f"beta_{name}"] = b, Y.blume(b)
            mc = self.w_mcap.get(t, {})
            ok = {s: float(v) for s, v in mc.items() if v is not None and math.isfinite(v) and v > 0}
            tot = sum(ok.values())
            mo["mcap_share"] = np.array([ok.get(s, 0.0) / tot if tot > 0 else 0.0 for s in mo["ids"]])
        bst["seconds"] = round(time.perf_counter() - t0, 1)
        self.st["y_betas"] = bst
        if self.y_mode == "canary":
            self.st["y_c7_panel"] = self._y_c7(months, reviews, spy_tr)

    def _y_c7(self, months, reviews, spy_tr):
        """C7: betas re-estimated from history requested only up to the review session (prices, splits, dividends;
        S028 per-security construction) equal the stored betas (stocks) and from events at or before the review row
        (SPY / ETFs)."""
        outer = [i for i, mo in enumerate(months) if mo["test_year"] in H.OUTER_YEARS]
        pick = [outer[0], outer[len(outer) // 2], outer[-1]][:Y_C7_REVIEWS]
        worst, cmp_n, nan_n = 0.0, 0, 0
        for i in pick:
            mo = months[i]
            k = mo["k"]
            day = datetime.strptime(_ds(self.cal[k]), "%Y-%m-%d") + timedelta(days=1)
            lo = k - Y.BETA_WIN
            spy_t = self._y_upto_tr(self.spy, day, k, split_only=True)
            ids = mo["ids"]
            step = max(1, len(ids) // Y_C7_STOCKS)
            for n in list(range(0, len(ids), step))[:Y_C7_STOCKS]:
                s = ids[n]
                tr_t = self._y_upto_tr(self.sym[s], day, k, j=self.col[s])
                b_t, _ = Y.beta_at(tr_t[lo:k + 1], spy_t[lo:k + 1], Y.BETA_WIN)
                b0 = mo["beta_raw"][n]
                same_nan = math.isnan(b0) and math.isnan(b_t)
                d = 0.0 if same_nan else abs(b_t - b0)
                worst = max(worst, d if math.isfinite(d) else float("inf"))
                cmp_n += 1
                nan_n += int(same_nan)
            for name in self.y_etf:
                tr_t = self._y_upto_tr(self.y_sym[name], day, k, split_only=True)
                b_t, _ = Y.beta_at(tr_t[lo:k + 1], spy_t[lo:k + 1], Y.BETA_WIN)
                b0 = mo[f"beta_{name}_raw"]
                d = 0.0 if (math.isnan(b0) and math.isnan(b_t)) else abs(b_t - b0)
                worst = max(worst, d if math.isfinite(d) else float("inf"))
                cmp_n += 1
                nan_n += int(math.isnan(b0) and math.isnan(b_t))
        return dict(compared=cmp_n, both_insufficient=nan_n, max_abs_diff=worst, reviews=[months[i]["day"] for i in pick],
                    ok=bool(cmp_n > 0 and worst <= 1e-9))

    def _y_upto_tr(self, sym, day, k, j=None, split_only=False):
        """Total-return index rebuilt from history requested only up to `day` (the session after review row k is never
        included: rows > k blanked, events on rows > k ignored). split_only: the SPY / ETF construction (split events);
        otherwise the S028 per-security construction (RAW + SCALED_RAW split multiplier)."""
        D = self.cal.size
        if split_only:
            O, C, m, _ = self._y_etf_arrays_upto(sym, day, k)
            return C * m
        loc = {X81._sid(sym): 0}
        st = dict(late_rows=0)
        hr = self.history([sym], S28.W_HIST_START, day, Resolution.DAILY, fill_forward=False,
                          data_normalization_mode=DataNormalizationMode.RAW)
        hs = self.history([sym], S28.W_HIST_START, day, Resolution.DAILY, fill_forward=False,
                          data_normalization_mode=DataNormalizationMode.SCALED_RAW)
        a = self._cols(hr, loc, self.cal, D, 1, ("open", "close"), st)
        b = self._cols(hs, loc, self.cal, D, 1, ("close",), st)
        raw, sc = a["close"][:, 0], b["close"][:, 0]
        raw[k + 1:], sc[k + 1:] = np.nan, np.nan
        sev = self._events(self.history(Split, [sym], S28.W_HIST_START, day), loc, self.cal,
                           ("type", "referenceprice", "splitfactor"))
        dev = self._events(self.history(Dividend, [sym], S28.W_HIST_START, day), loc, self.cal,
                           ("distribution", "referenceprice"))
        vv = np.flatnonzero(np.isfinite(raw) & np.isfinite(sc) & (raw > 0) & (sc > 0))
        if vv.size and abs(sc[vv[-1]] / raw[vv[-1]] - 1.0) > 1e-6:
            sc = sc / (sc[vv[-1]] / raw[vv[-1]])
        ev = [(r_, float(fac)) for r_, typ, ref, fac in sev[0] if ("OCCUR" in str(typ).upper() or float(ref) > 0)
              and r_ <= k]
        de = [(r_, float(amt), float(ref)) for r_, amt, ref in dev[0] if r_ <= k]
        mult, _ = XP.split_multiplier(raw, sc, ev, detail=[])
        tr = raw * mult * XP.dividend_multiplier(D, de)
        for u in self.unv.get(j, ()):
            if int(u) <= k:
                tr[int(u)] = np.nan
        return tr

    def _y_etf_arrays_upto(self, sym, day, k):
        hist_end = self.hist_end
        self.hist_end = day
        try:
            O, C, m, info = self._y_etf_arrays(sym, k)
        finally:
            self.hist_end = hist_end
        C = C.copy()
        C[k + 1:] = np.nan
        return O, C, m, info

    # ------------------------------------------------------------------------------------------------ ETF checks
    def _y_c4(self, ms):
        """C4: every calendar row from 252 sessions before the first outer review through 2021-12-31 has a valid RAW
        open and close; no late or off-calendar rows; no |daily total return| > 20%; at least one distribution (SPLV /
        USMV; SPY's total-return series is verified exactly by C2); split counts (all counts only)."""
        last_row = int(self.cal.size - 1)
        r0 = ms[0]["k"] - Y.BETA_WIN
        out = {}
        for name, (O, C, m) in list(self.y_etf.items()) + [("spy", self.w_spy)]:
            w = slice(r0, last_row + 1)
            okb = np.isfinite(O[w]) & (O[w] > 0) & np.isfinite(C[w]) & (C[w] > 0)
            tr = (C * m)[w]
            with np.errstate(divide="ignore", invalid="ignore"):
                r = tr[1:] / tr[:-1] - 1.0
            info = self.st["y_etf"].get(name, {})
            d = dict(window=[_ds(self.cal[r0]), _ds(self.cal[last_row])], rows=int(okb.size),
                     missing_rows=int((~okb).sum()), big_moves=int((np.abs(r[np.isfinite(r)]) > Y_BIG_MOVE).sum()),
                     late_rows=info.get("late_rows", 0), unknown_rows=info.get("unknown_rows", 0),
                     distributions=info.get("distributions", self.st.get("w_spy", {}).get("dividends")),
                     split_events=info.get("split_events"), first_bar=info.get("first_bar"))
            d["ok"] = bool(d["missing_rows"] == 0 and d["late_rows"] == 0 and d["unknown_rows"] == 0
                           and d["big_moves"] == 0 and (name == "spy" or (d["distributions"] or 0) > 0))
            out[name] = d
        return out

    # ------------------------------------------------------------------------------------------------ frozen replay
    def _y_frozen(self, months):
        """The real H028 (frozen S030 real path) and LV15 scores, and the C1-C3 reproduction checks."""
        p = self.qr_params
        fz = p["frozen_h028"]
        w8 = F.run_world_fixed(months, [m["X"] for m in months], full=True)
        ms = [months[i] for i in w8["idx"]]
        sc8, sclv = w8["scores"], G.lv15_scores(ms)
        h = w8["h"]
        a1 = Y.account(ms, sc8, capital=H.CAPITAL, sleeve=1.0, absorber=None, min_ticket=0.0)
        c1 = dict(wealth=a1["wealth"], frozen_wealth=float(fz["wealth"]), commissions=a1["commissions"],
                  buys=a1["buys"], sells=a1["sells"], slippage=a1["slippage"],
                  engine_equals_frozen_simulate=bool(a1["wealth"] == h["wealth"] and a1["picks"] == h["picks"]
                                                     and np.array_equal(a1["daily"], h["daily"])),
                  decision_months=len(ms), pick_lists=len(a1["picks"]))
        c1["ok"] = bool(c1["engine_equals_frozen_simulate"] and a1["wealth"] == float(fz["wealth"])
                        and a1["commissions"] == float(fz["commissions"]) and a1["buys"] == int(fz["buys"])
                        and a1["sells"] == int(fz["sells"]) and a1["slippage"] == float(fz["slippage"])
                        and len(ms) == 84)
        s1 = Y.account(ms, None, capital=H.CAPITAL)
        s2 = Y.account(ms, None, capital=Y.CAPITAL)
        f1, f2 = H.spy_simulate(ms, daily=True), H.spy_simulate(ms, capital=Y.CAPITAL, daily=True)
        c2 = dict(wealth_100k=s1["wealth"], frozen_100k=float(p["frozen_spy_wealth"]), wealth_200k=s2["wealth"],
                  equals_spy_simulate_100k=bool(s1["wealth"] == f1["wealth"] and np.array_equal(s1["daily"], f1["daily"])),
                  equals_spy_simulate_200k=bool(s2["wealth"] == f2["wealth"] and np.array_equal(s2["daily"], f2["daily"])),
                  equals_frozen_200k_diagnostic=bool(s2["wealth"] == float(p["frozen_spy_wealth_200k"])))
        c2["ok"] = bool(c2["equals_spy_simulate_100k"] and c2["equals_spy_simulate_200k"]
                        and s1["wealth"] == float(p["frozen_spy_wealth"]) and c2["equals_frozen_200k_diagnostic"])
        lv = G.lv15(ms)
        a3 = Y.account(ms, sclv, capital=H.CAPITAL, sleeve=1.0, absorber=None, min_ticket=0.0)
        c3 = dict(wealth=a3["wealth"], frozen=float(p["frozen_lv15_wealth"]),
                  engine_equals_frozen_lv15=bool(a3["wealth"] == lv["wealth"] and np.array_equal(a3["daily"], lv["daily"])))
        c3["ok"] = bool(c3["engine_equals_frozen_lv15"] and a3["wealth"] == float(p["frozen_lv15_wealth"]))
        return w8, ms, sc8, sclv, dict(C1=c1, C2=c2, C3=c3)

    # ------------------------------------------------------------------------------------------------ dispatch
    def _g_real(self, months, regimes, reviews):
        self.st["hypothesis"] = "SYS-1 (H028 sleeve; H028 REJECTED)"
        self.st["sys1_mode"] = self.y_mode
        self.st["provenance_sys1"] = {k: self.qr_params.get(k) for k in (
            "sys1_protocol_sha256", "sys1_code_sha256", "canary_result_sha256")}
        if self.y_mode == "canary":
            self._y_canary(months)
        else:
            self._y_eval(months)

    # ------------------------------------------------------------------------------------------------ canary
    def _y_canary(self, months):
        w8, ms, sc8, sclv, ck = self._y_frozen(months)
        ck["C4"] = self._y_c4(ms)
        # C5: account-rule counts on SEEDED RANDOM scores (never an evaluation arm) and on an SPLV 0.3 + SPY account;
        # a zero-return copy of the real month structure (no hidden financing: wealth = capital - costs)
        c5 = dict(random=[], etf=[], zero=[])
        for sd in Y_C5_SEEDS:
            rng = np.random.default_rng(sd)
            rs = [rng.normal(size=len(m["ids"])) for m in ms]
            for slip in Y.SLIPS:
                rec = Y.account(ms, rs, slip=slip)
                c5["random"].append(self._y_rules(rec, sd, slip))
        if ck["C4"][Y_GATING]["ok"]:
            for slip in Y.SLIPS:
                c5["etf"].append(self._y_rules(Y.account(ms, None, slip=slip, targets={Y_GATING: 0.3}), 0, slip))
        zms = []
        for m in ms:
            z = dict(m, r_oo=np.zeros(len(m["ids"])), r_oc=np.zeros(len(m["ids"])), daily=np.zeros_like(m["daily"]))
            for name in Y.ETFS:
                z[f"{name}_oo"] = z[f"{name}_oc"] = 0.0
                z[f"{name}_daily"] = np.zeros(len(m["days"]))
            zms.append(z)
        rng = np.random.default_rng(Y_C5_SEEDS[0])
        rz = [rng.normal(size=len(m["ids"])) for m in zms]
        for kw in (dict(scores=rz), dict(scores=rz, targets={"splv": 0.3}), dict(scores=None, targets={"spy": 0.9},
                                                                                  absorber=None)):
            rec = Y.account(zms, kw.pop("scores"), **kw)
            c5["zero"].append(dict(wealth_minus_capital_plus_costs=rec["wealth"] - (Y.CAPITAL - rec["commissions"]
                                                                                   - rec["slippage"]),
                                   negative_cash=rec["violations"]["negative_cash"]))
        okr = all(r["ok"] for r in c5["random"] + c5["etf"])
        okz = all(abs(z["wealth_minus_capital_plus_costs"]) < 1e-6 and z["negative_cash"] == 0 for z in c5["zero"])
        c5["ok"] = bool(okr and okz and len(c5["etf"]) == len(Y.SLIPS))
        ck["C5"] = c5
        c6 = Y.costs_check()
        ck["C6"] = dict(c6, ok=bool(c6["ok"]))
        c7 = dict(self.st.pop("y_c7_panel"))
        ck["C7"] = c7
        ck["betas"] = self.st.get("y_betas")
        ck["all_in_host"] = bool(all(ck[c]["ok"] for c in ("C1", "C2", "C3", "C5", "C6", "C7"))
                                 and ck["C4"][Y_GATING]["ok"] and ck["C4"]["spy"]["ok"])
        ck["sys1_arm_result_computed"] = False
        self.st["canary"] = ck

    @staticmethod
    def _y_rules(rec, seed, slip):
        al = rec["alloc"]
        err = max(abs(sum(a[x] for x in ("stock", "cash") + Y.ETFS) - 1.0) for a in al)
        r = dict(seed=seed, slip=slip, violations=dict(rec["violations"]), min_cash=rec["min_cash"],
                 stock_positions_max=max(rec["holdings"]), skipped_min=rec["skipped_min"],
                 scaled_buys=rec["scaled_buys"], alloc_sum_max_error=err,
                 orders=rec["trades"], commissions_equal_orders_x7=bool(abs(rec["commissions"] - 7.0 * rec["trades"])
                                                                        < 1e-6))
        r["ok"] = bool(all(v == 0 for v in rec["violations"].values()) and rec["min_cash"] >= -1e-6
                       and max(rec["holdings"]) <= H.K and err < 1e-9 and r["commissions_equal_orders_x7"])
        return r

    # ------------------------------------------------------------------------------------------------ evaluation
    def _y_eval(self, months):
        w8, ms, sc8, sclv, ck = self._y_frozen(months)
        ck["C4"] = self._y_c4(ms)
        if not (ck["C1"]["ok"] and ck["C2"]["ok"] and ck["C3"]["ok"] and ck["C4"]["spy"]["ok"]):
            raise Exception("S032: the frozen H028 / SPY / LV15 reproduction failed; STOP before any SYS-1 result")
        if not ck["C4"][Y_GATING]["ok"]:
            raise Exception("S032: SPLV failed its historical-data requirements; STOP before the evaluation (OD-4)")
        usmv_ok = bool(ck["C4"]["usmv"]["ok"])
        days = w8["days"]
        cap = Y.CAPITAL
        eb = {n: [m[f"beta_{n}"] for m in ms] for n in ("splv", "usmv")}
        out = dict(integrity=ck, usmv_verified=usmv_ok, months=[m["day"] for m in ms], days=days, capital=cap,
                   arms={}, bmx={}, daily={})
        spec = dict(A1=dict(scores=sc8), A2=dict(scores=sclv), A3=dict(scores=None, targets={"splv": 0.5}))
        if usmv_ok:
            spec["D3"] = dict(scores=None, targets={"usmv": 0.5})
        for lab, slip in (("s10", Y.SLIPS[0]), ("s20", Y.SLIPS[1])):
            a0 = Y.account(ms, None, slip=slip)
            ref = a0["daily"]
            arms = dict(A0=a0)
            for name, kw in spec.items():
                kw = dict(kw)
                arms[name] = Y.account(ms, kw.pop("scores"), slip=slip, **kw)
            for name in ("A1", "A2", "A3"):
                w, raw, cl = Y.exante_weights(ms, arms[name], eb)
                arms[f"BMX_{name}"] = Y.account(ms, None, slip=slip, absorber=None, targets={"spy": w})
                out["bmx"].setdefault(name, {})[lab] = dict(weights=w, raw=raw, clamps=cl,
                                                            mean_weight=float(np.mean(w)))
            arms["D2"] = Y.account(ms, None, slip=slip, absorber=None, targets={"spy": 0.9})
            arms["D1"] = Y.account(ms, sc8, capital=H.CAPITAL, slip=slip, sleeve=1.0, absorber=None, min_ticket=0.0)
            ref100 = Y.account(ms, None, capital=H.CAPITAL, slip=slip)["daily"]
            for name, rec in arms.items():
                c = H.CAPITAL if name == "D1" else cap
                d = dict(summary=Y.summary(rec), metrics=Y.metrics(rec, days, c, ref100 if name == "D1" else ref),
                         overlap=self._y_overlap(ms, rec) if name in ("A1", "A2") else None)
                out["arms"].setdefault(name, {})[lab] = d
                if lab == "s10":
                    out["daily"][name] = rec["daily"]
            if lab == "s10":
                out["sleeve"] = self._y_sleeve(ms, sc8, arms["A1"], slip)
                out["sleeve_lv15"] = self._y_sleeve(ms, sclv, arms["A2"], slip)
        res = self._w_emit("QRSY", out)
        self.st["eval"] = dict(arms=sorted(out["arms"]), usmv_verified=usmv_ok,
                               wealth={n: v["s10"]["summary"]["wealth"] for n, v in out["arms"].items()}, **res)

    @staticmethod
    def _y_overlap(ms, rec):
        """Look-through overlap proxy per review: sum over held stocks of the PIT market-cap share x the account's SPY
        weight (diagnostic only, no netting), and the stocks' total market-cap share."""
        ov, sh = [], []
        for m, p in zip(ms, rec["posts"]):
            s = float(sum(m["mcap_share"][i] for i in p["idx"]))
            sh.append(s)
            ov.append(s * p["etf"].get("spy", 0.0))
        return dict(overlap=ov, held_mcap_share=sh, mean_overlap=float(np.mean(ov)), max_overlap=float(np.max(ov)))

    @staticmethod
    def _y_sleeve(ms, scores, rec, slip):
        """The combined-account sleeve versus the standalone frozen book on the same scores (sleeve 1, no overlay, no
        ETF) at $200,000 and $100,000: held-set differences, skipped / scaled buys, SPY funding and absorption trades,
        ticket sizes, sleeve share and sleeve-return differences (owner D252 clarification 1)."""
        out = {}
        for lab, cap in (("standalone_200k", Y.CAPITAL), ("standalone_100k", H.CAPITAL)):
            fz = Y.account(ms, scores, capital=cap, slip=slip, sleeve=1.0, absorber=None, min_ticket=0.0)
            diff = jac = 0
            js = []
            for a, b in zip(rec["picks"], fz["picks"]):
                sa, sb = set(a), set(b)
                diff += int(sa != sb)
                js.append(len(sa & sb) / len(sa | sb) if (sa | sb) else 1.0)
            ra = np.array([np.nan if x is None else x for x in rec["sleeve_ret"]], float)
            rb = np.array([np.nan if x is None else x for x in fz["sleeve_ret"]], float)
            ok = np.isfinite(ra) & np.isfinite(rb)
            out[lab] = dict(wealth=fz["wealth"], held_set_differs_months=diff, mean_jaccard=float(np.mean(js)),
                            min_jaccard=float(np.min(js)), sleeve_ret_months=int(ok.sum()),
                            sleeve_ret_corr=float(np.corrcoef(ra[ok], rb[ok])[0, 1]) if ok.sum() > 2 else None,
                            sleeve_ret_mean_diff=float(np.mean(ra[ok] - rb[ok])) if ok.any() else None,
                            sleeve_ret_mean_abs_diff=float(np.mean(np.abs(ra[ok] - rb[ok]))) if ok.any() else None,
                            sleeve_log_growth=float(np.sum(np.log1p(ra[ok]))), standalone_log_growth=float(
                                np.sum(np.log1p(rb[ok]))))
        tk = [x for x in rec["tickets"] if x is not None]
        st = np.array([a["stock"] for a in rec["alloc"]], float)
        spy = np.array([a["spy"] for a in rec["alloc"]], float)
        cash = np.array([a["cash"] for a in rec["alloc"]], float)
        r_sl = np.array([0.0 if x is None else x for x in rec["sleeve_ret"]], float)
        r_spy = np.array([m["spy_oc"] if i == len(ms) - 1 else m["spy_oo"] for i, m in enumerate(ms)], float)
        out["account"] = dict(skipped_min=rec["skipped_min"], scaled_buys=rec["scaled_buys"],
                              funding_sales=rec["funding_sales"], absorber_buys=rec["absorber_buys"],
                              tickets=dict(n=len(tk), min=float(min(tk)), median=float(np.median(tk)),
                                           max=float(max(tk))) if tk else None,
                              stock_share=dict(first=float(st[0]), min=float(st.min()), median=float(np.median(st)),
                                               max=float(st.max()), last=float(st[-1])),
                              spy_share=dict(min=float(spy.min()), median=float(np.median(spy)), max=float(spy.max())),
                              cash_share_max=float(cash.max()), stock_share_path=st.tolist(),
                              contribution=dict(stock=float(np.sum(st * r_sl)), spy=float(np.sum(spy * r_spy))))
        return out
