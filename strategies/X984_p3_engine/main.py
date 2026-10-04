# X984 — Phase 3 shadow-book engine host (research/phase3/P3_spec.md). NON-TRADING: no orders are ever placed; the
# harness supplies the frozen universe (data infrastructure v1), sessions, warm-up and the Holdout lock. Many virtual
# books are simulated with qr_p3_engine (exact harness mechanics) inside one LEAN backtest, so QuantConnect data never
# leaves the platform; only derived results are published (summary statistics).
# Modes (params.mode):
#   fidelity : replay the ENTRY DECISIONS of completed control books (qr_p3_replay: E982-02, E017-03..07, decisions
#              <= 2017-12-31) through the engine; publish daily equity / cash and every fill for comparison with LEAN.
#   canary   : runtime / memory / output canary of the search configuration with DUMMY masks and strengths (random,
#              seeded): the real features and real configuration masks are computed for timing only and discarded
#              (only a SHA-256 digest of the real masks is kept, to verify that worlds do not depend on their batch).
#              params.publish_format = true also publishes every world's summary and the first world's per-configuration
#              lines in the exact search-mode format (output-size test; dummy books only).
#   search   : the Phase 3 Stage-1 search (real world = identity) and / or null worlds (within-date permutation of the
#              signal rows; params.worlds). Runs ONLY with explicit owner approval (configs carry
#              owner_approval_required). params.trace = [configuration ids]: the real world additionally publishes
#              those books' daily equity / cash and every fill (finalist verification, P3_spec.md section 15).
# Every run ends on or before 2017-12-31 (search window); 2018+ data is never loaded.
from AlgorithmImports import *
from datetime import timedelta
import hashlib
import json
import time
import numpy as np
from qr_harness import QRAlgorithm, in_warmup
import qr_p3_engine as EN
import qr_p3_features as FE
import qr_p3_grammar as GR
import qr_p3_pipeline as PL

YEARS = list(range(2010, 2018))
MAXG = 14000
W = FE.WINDOW


class P3Engine(QRAlgorithm):
    USES_UNIVERSE = True

    def qr_initialize(self):
        p = self.qr_params
        self.p3_mode = p["mode"]
        if self.p3_mode not in ("fidelity", "canary", "search"):
            raise Exception(f"X984: unknown mode {self.p3_mode!r}")
        if self.qr_sec is None:
            raise Exception("X984 needs universe.sec_corrections (frozen data infrastructure v1)")
        if self.qr["end"] > "2017-12-31":
            raise Exception("X984: Phase 3 engine runs end on or before 2017-12-31")
        self._qr_log_budget = 400000
        self.p3_clock = {k: 0.0 for k in ("corp", "bars", "history", "features", "masks", "select", "engine", "stats",
                                       "pipeline")}
        self.t_start = time.perf_counter()
        self.g_of, self.sym_of, self.sid_of = {}, {}, []
        self.last_close = np.full(MAXG, np.nan)
        self.prev_close = np.full(MAXG, np.nan)
        self.open_px = np.full(MAXG, np.nan)
        self.has_bar = np.zeros(MAXG, dtype=bool)
        self.last_real_sess = np.full(MAXG, -10 ** 6, dtype=np.int64)
        self.div_today = np.zeros(MAXG)
        self.p3_warned = set()
        self.p3_done = None
        self.day_index = 0
        self.slots, self.hold = int(p.get("slots", 10)), int(p.get("hold", 63))
        self.spy_prev = None
        self.spy_div = 0.0
        self.spy_level = 1.0
        self.ew_level = 1.0
        self.p3_st = {"official_sessions": 0, "max_eligible": 0, "loaded_histories": 0, "history_calls": 0,
                   "replay_unknown_sid": 0, "replay_not_free": 0, "replay_blocked": 0}
        if self.p3_mode == "fidelity":
            from qr_p3_replay import SHA256 as RSHA, load_replay
            r = load_replay()
            self.p3_st["replay_sha256"] = RSHA
            self.replay_books = r["books"]
            self.p3_schedule = {}
            for b, d, sid in r["entries"]:
                self.p3_schedule.setdefault(d, []).append((b, sid))
            self.hold = int(p.get("hold", 60))
            self.p3_worlds = [dict(name="fidelity", perm=None)]
            self.p3_books = [EN.Books(len(self.replay_books), self.slots, self.hold, float(self.qr["cash"]))]
            self.p3_books[0].fills = []
            self.fill_day = []
            self.p3_fill_mark = 0
        else:
            self.p3_configs = GR.enumerate_configs()
            self.p3_table = FE.SignalTable(self.p3_configs, GR.PRIMARY_TYPES, GR.CONFIRM_TYPES, GR.RISK_LEVELS)
            n = len(self.p3_configs)
            self.p3_worlds = [dict(name=w["name"], seed=w.get("seed"), block=w.get("block")) for w in p["worlds"]]
            self.p3_books = [EN.Books(n, self.slots, self.hold, float(self.qr["cash"])) for _ in self.p3_worlds]
            self.Cw = np.full((MAXG, W), np.nan)
            self.Hw = np.full((MAXG, W), np.nan)
            self.Lw = np.full((MAXG, W), np.nan)
            self.Vw = np.full((MAXG, W), np.nan)
            self.ptr = np.zeros(MAXG, dtype=np.int64)
            self.loaded = np.zeros(MAXG, dtype=bool)
            self.spy_hist = []
            self.dummy_density = np.random.default_rng(20261004).uniform(0.02, 0.5, n)
            self.p3_digest = hashlib.sha256()                 # canary: digest of the REAL masks (batch independence)
            self.p3_mask_cells = 0
            fmt0 = self.p3_mode == "canary" and bool(p.get("publish_format"))
            self.p3_stats = [self._new_stats(n, w["name"] == "real" or (fmt0 and i == 0))
                             for i, w in enumerate(self.p3_worlds)]
            self.p3_trace = []
            if p.get("trace"):
                if self.p3_mode != "search" or self.p3_worlds[0]["name"] != "real":
                    raise Exception("X984: trace needs search mode with the real world first")
                ix = {c["id"]: i for i, c in enumerate(self.p3_configs)}
                self.p3_trace = [ix[c] for c in p["trace"]]
                self.p3_books[0].fills = []
                self.p3_books[0].trace = set(self.p3_trace)
                self.fill_day = []
                self.p3_fill_mark = 0
        nb = len(self.p3_books[0].cash)
        self.eq_prev = [np.full(len(b.cash), float(self.qr["cash"])) for b in self.p3_books]
        self.spy_peak, self.spy_dd = 1.0, 0.0
        self.spy_maxdd = np.zeros(len(YEARS))
        self.p3_sessions = np.zeros(len(YEARS))
        self.ew_logex = np.zeros(len(YEARS))
        self.p3_st["books_per_world"] = nb
        self.p3_st["worlds"] = len(self.p3_worlds)

    def _new_stats(self, n, monthly):
        z = lambda: np.zeros((n, len(YEARS)))
        s = dict(logex=z(), cost=z(), eqsum=z(), notional=z(), maxdd=z(), peak=np.full(n, float(self.qr["cash"])),
                 dd=np.zeros(n))
        if monthly:
            s["months"] = []
            s["mlogex"] = []
            s["cur_m"] = None
        return s

    # ---------------------------------------------------------------- identifiers
    def _g(self, sym, create=True):
        sid = str(sym.id)
        g = self.g_of.get(sid)
        if g is None and create:
            g = len(self.sid_of)
            if g >= MAXG:
                raise Exception("X984: stock index capacity exceeded")
            self.g_of[sid] = g
            self.sid_of.append(sid)
            self.sym_of[g] = sym
        return g

    def _held_g(self):
        out = set()
        for b in self.p3_books:
            out.update(b.sid[b.state != EN.EMPTY].tolist())
        return out

    def qr_select_universe(self, eligible):
        chosen = [f.symbol for f in eligible]
        for f in eligible:
            self._g(f.symbol)
        chosen += [self.sym_of[g] for g in self._held_g() if g in self.sym_of]
        return list(dict.fromkeys(chosen))

    # ---------------------------------------------------------------- windows (search / canary modes)
    def on_securities_changed(self, changes):
        super().on_securities_changed(changes)
        if self.p3_mode == "fidelity":
            return
        t0 = time.perf_counter()
        for sec in changes.removed_securities:
            g = self._g(sec.symbol, create=False)
            if g is not None:
                self.loaded[g] = False
        add = [sec.symbol for sec in changes.added_securities if sec.symbol != self.spy]
        add = [s for s in add if not self.loaded[self._g(s)]]
        for i in range(0, len(add), 200):
            part = add[i:i + 200]
            h = self.history(part, W, Resolution.DAILY, data_normalization_mode=DataNormalizationMode.SCALED_RAW)
            self.p3_st["history_calls"] += 1
            rows = {}
            if h is not None and not h.empty:
                for (sym, tt), r in h[["open", "high", "low", "close", "volume"]].iterrows():
                    rows.setdefault(sym, []).append((float(r["high"]), float(r["low"]), float(r["close"]),
                                                     float(r["volume"])))
            for sym in part:
                g = self._g(sym)
                self.Cw[g], self.Hw[g], self.Lw[g], self.Vw[g] = np.nan, np.nan, np.nan, np.nan
                v = rows.get(sym, [])[-W:]
                for k, (hh, ll, cc, vv) in enumerate(v):
                    self.Hw[g, k], self.Lw[g, k], self.Cw[g, k], self.Vw[g, k] = hh, ll, cc, vv
                self.ptr[g] = len(v) % W
                self.loaded[g] = True
                self.p3_st["loaded_histories"] += 1
        self.p3_clock["history"] += time.perf_counter() - t0

    def _rescale(self, g, pf, vf):
        if self.p3_mode != "fidelity":
            self.Cw[g] *= pf
            self.Hw[g] *= pf
            self.Lw[g] *= pf
            self.Vw[g] *= vf

    def _windows(self, E):
        idx = (self.ptr[E][:, None] + np.arange(W)[None, :]) % W
        rows = E[:, None]
        return self.Cw[rows, idx], self.Hw[rows, idx], self.Lw[rows, idx], self.Vw[rows, idx]

    # ---------------------------------------------------------------- data
    def on_data(self, data):
        t0 = time.perf_counter()
        for sym, sp in data.splits.items():
            if sp.type != SplitType.SPLIT_OCCURRED:
                continue
            g = self._g(sym, create=False)
            f = float(sp.split_factor)
            if g is None:
                continue
            for b in self.p3_books:
                b.split(g, f, float(sp.reference_price))
            self.last_close[g] *= f
            self._rescale(g, f, 1.0 / f)
        for sym, dv in data.dividends.items():
            amt, ref = float(dv.distribution), float(dv.reference_price)
            if sym == self.spy:
                self.spy_div += amt
                continue
            g = self._g(sym, create=False)
            if g is None:
                continue
            for b in self.p3_books:
                b.dividend(g, amt)
            self.div_today[g] += amt
            if ref > 0:
                f = 1.0 - amt / ref
                self._rescale(g, f, 1.0 / f)
        for sym, dl in data.delistings.items():
            g = self._g(sym, create=False)
            if g is None:
                continue
            if dl.type == DelistingType.WARNING:
                self.p3_warned.add(g)
            else:
                for b in self.p3_books:
                    b.delist(g, float(self.last_close[g]))
        self.p3_clock["corp"] += time.perf_counter() - t0
        if self.p3_books[0].fills is not None:
            self._flush_fills(str(self.time.date()))
        super().on_data(data)
        if data.bars.count == 0 or self.time.hour < 9:
            return
        today = self.time.date()
        if self.p3_done == today or self._qr_session_day != today:
            return
        self.p3_done = today
        t0 = time.perf_counter()
        self.has_bar[:] = False
        spy_bar = data.bars[self.spy] if data.bars.contains_key(self.spy) else None
        for sym, bar in data.bars.items():
            if bar.is_fill_forward or sym == self.spy:
                continue
            g = self._g(sym, create=self.p3_mode != "fidelity")
            if g is None:
                continue
            self.prev_close[g] = self.last_close[g]
            self.open_px[g], self.last_close[g] = float(bar.open), float(bar.close)
            self.has_bar[g] = True
            self.last_real_sess[g] = self._qr_session
            if self.p3_mode != "fidelity" and self.loaded[g]:
                k = self.ptr[g]
                self.Cw[g, k], self.Hw[g, k], self.Lw[g, k] = float(bar.close), float(bar.high), float(bar.low)
                self.Vw[g, k] = float(bar.volume)
                self.ptr[g] = (k + 1) % W
        self.p3_clock["bars"] += time.perf_counter() - t0
        warm = in_warmup(today, self.qr_official_start)
        spy_close = float(spy_bar.close) if spy_bar is not None else None
        if self.p3_mode != "fidelity" and spy_close is not None:
            self.spy_hist.append(spy_close)
            self.spy_hist = self.spy_hist[-W:]
        if not warm:
            self._step(today, spy_close)
        if spy_close is not None:
            self.spy_prev = spy_close
        self.spy_div = 0.0
        self.div_today[:] = 0.0
        self.day_index += 1

    # ---------------------------------------------------------------- one official session
    def _eligible_rows(self):
        E = [self.g_of[str(s.id)] for s in self.qr_eligible if str(s.id) in self.g_of]
        E = sorted(set(E), key=lambda g: self.sid_of[g])
        return np.array(E, dtype=np.int64)

    def _step(self, today, spy_close):
        s = self._qr_session
        yi = YEARS.index(today.year)
        self.p3_st["official_sessions"] += 1
        self.p3_sessions[yi] += 1
        # SPY total return and the EW universe index (daily equal weight of eligible stocks with two real closes)
        r_spy = 0.0
        if self.spy_prev and spy_close:
            r_spy = (spy_close + self.spy_div) / self.spy_prev - 1.0
        self.spy_level *= 1 + r_spy
        self.spy_peak = max(self.spy_peak, self.spy_level)
        self.spy_dd = min(self.spy_dd, self.spy_level / self.spy_peak - 1)
        self.spy_maxdd[yi] = self.spy_dd
        E = self._eligible_rows()
        self.p3_st["max_eligible"] = max(self.p3_st["max_eligible"], len(E))
        if len(E):
            ok = self.has_bar[E] & np.isfinite(self.prev_close[E]) & (self.prev_close[E] > 0)
            if ok.any():
                rr = (self.last_close[E][ok] + self.div_today[E][ok]) / self.prev_close[E][ok] - 1.0
                r_ew = float(np.mean(rr))
                self.ew_level *= 1 + r_ew
                self.ew_logex[yi] += np.log1p(r_ew) - np.log1p(r_spy)
        if self.p3_mode == "fidelity":
            self._fidelity_step(today, s)
            return
        t0 = time.perf_counter()
        masks = strength = p_of = None
        if len(E):
            c, h, l, v = self._windows(E)
            f = FE.features(c, h, l, v, np.array(self.spy_hist))
            self.p3_clock["features"] += time.perf_counter() - t0
            t0 = time.perf_counter()
            masks, strength, p_of = self.p3_table.evaluate(f)
            if self.p3_mode == "canary":                            # discard real masks: dummy random masks and keys
                self.p3_digest.update(str(today).encode() + "|".join(self.sid_of[g] for g in E).encode())
                self.p3_digest.update(np.packbits(masks).tobytes())
                self.p3_mask_cells += int(masks.sum())
                rng = np.random.default_rng([20261004, self.day_index])
                masks = rng.random(masks.shape) < self.dummy_density[:, None]
                strength = rng.random(strength.shape)
            orders = [EN.strength_order(strength[i]) for i in range(strength.shape[0])]
            self.p3_clock["masks"] += time.perf_counter() - t0
        for wi, (w, B) in enumerate(zip(self.p3_worlds, self.p3_books)):
            t0 = time.perf_counter()
            B.open_fills(self.open_px, self.has_bar, s)
            B.stale_exits(s, self.last_real_sess, self.last_close)
            pv = B.equity(self.last_close)
            due = B.exits_due(s)
            n_sells = due.sum(axis=1)
            self.p3_clock["engine"] += time.perf_counter() - t0
            if masks is not None:
                t0 = time.perf_counter()
                if w.get("seed") is None:
                    perm_g = E
                else:
                    perm_g = E[EN.null_permutation(w["seed"], self.day_index, len(E), w.get("block"))]
                free = B.free()
                for b in np.nonzero(free > 0)[0]:
                    cand = EN.select_candidates(orders[p_of[b]], masks[b], perm_g, B.blocked(b), int(free[b]))
                    if cand:
                        B.plan_entries(b, cand, self.last_close, float(pv[b]), int(n_sells[b]), skip=self.p3_warned)
                self.p3_clock["select"] += time.perf_counter() - t0
            t0 = time.perf_counter()
            self._update_stats(wi, B, pv, r_spy, yi, today)
            self.p3_clock["stats"] += time.perf_counter() - t0
            if wi == 0 and self.p3_trace:
                d = str(today)
                self._flush_fills(d)
                eq = B.equity(self.last_close)
                self._qr_log("D|" + d + "|" + ";".join(f"{eq[b]:.2f},{B.cash[b]:.2f},{int((B.state[b] == EN.HELD).sum())}"
                                                       for b in self.p3_trace))

    def _update_stats(self, wi, B, eq, r_spy, yi, today):
        S = self.p3_stats[wi]
        with np.errstate(divide="ignore", invalid="ignore"):
            lr = np.log(eq / self.eq_prev[wi]) - np.log1p(r_spy)
        lr = np.nan_to_num(lr)
        S["logex"][:, yi] += lr
        S["eqsum"][:, yi] += eq
        c, sl, nt = B.reset_costs()
        S["cost"][:, yi] += c + sl
        S["notional"][:, yi] += nt
        S["peak"] = np.maximum(S["peak"], eq)
        S["dd"] = np.minimum(S["dd"], eq / S["peak"] - 1.0)
        S["maxdd"][:, yi] = S["dd"]
        if "mlogex" in S:
            m = today.strftime("%Y-%m")
            if m != S["cur_m"]:
                S["months"].append(m)
                S["mlogex"].append(np.zeros(len(eq)))
                S["cur_m"] = m
            S["mlogex"][-1] += lr
        self.eq_prev[wi] = eq

    def _fidelity_step(self, today, s):
        B = self.p3_books[0]
        B.open_fills(self.open_px, self.has_bar, s)
        B.stale_exits(s, self.last_real_sess, self.last_close)
        pv = B.equity(self.last_close)
        due = B.exits_due(s)
        n_sells = due.sum(axis=1)
        d = str(today)
        by_book = {}
        for b, sid in self.p3_schedule.get(d, []):
            by_book.setdefault(b, []).append(sid)
        for b, sids in by_book.items():
            stocks = []
            blocked = B.blocked(b)
            for sid in sids:
                g = self.g_of.get(sid)
                if g is None:
                    self.p3_st["replay_unknown_sid"] += 1
                    continue
                if g in blocked:
                    self.p3_st["replay_blocked"] += 1
                    continue
                stocks.append(g)
            free = int(B.free()[b])
            if len(stocks) > free:
                self.p3_st["replay_not_free"] += len(stocks) - free
                stocks = stocks[:free]
            B.plan_entries(b, stocks, self.last_close, float(pv[b]), int(n_sells[b]), skip=self.p3_warned)
        self._flush_fills(d)
        eq = B.equity(self.last_close)
        self._qr_log("D|" + d + "|" + ";".join(f"{e:.2f},{c:.2f},{n}" for e, c, n in
                                               zip(eq, B.cash, (B.state == EN.HELD).sum(axis=1))))

    def _flush_fills(self, d):
        B = self.p3_books[0]
        for rec in B.fills[self.p3_fill_mark:]:
            self.fill_day.append((d,) + rec)
        self.p3_fill_mark = len(B.fills)

    # ---------------------------------------------------------------- end
    def qr_on_end(self):
        self.p3_st["clock_s"] = {k: round(v, 2) for k, v in self.p3_clock.items()}
        self.p3_st["wall_s"] = round(time.perf_counter() - self.t_start, 1)
        try:
            import resource
            self.p3_st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as e:
            self.p3_st["max_rss_mb"] = f"unavailable: {type(e).__name__}"
        self.p3_st["stocks_indexed"] = len(self.sid_of)
        if self.p3_mode == "fidelity":
            B = self.p3_books[0]
            self.p3_st["counts"] = B.counts
            for d, b, kind, g, q, px, fee in self.fill_day:
                self._qr_log(f"F|{b}|{d}|{self.sid_of[g]}|{kind}|{q:.0f}|{px:.6f}|{fee:.2f}")
            self._qr_log("QRX984|summary|" + json.dumps(self.p3_st, sort_keys=True))
            return
        t0 = time.perf_counter()
        nbg = GR.neighbours(self.p3_configs)
        ix = {c["id"]: i for i, c in enumerate(self.p3_configs)}
        nbi = [np.array([ix[o] for o in nbg[c["id"]]], dtype=int) for c in self.p3_configs]
        cpx = [GR.complexity(c) for c in self.p3_configs]
        ids = [c["id"] for c in self.p3_configs]
        out_bytes = 0
        for w, S in zip(self.p3_worlds, self.p3_stats):
            inp = PL.Inputs(ids, S["logex"], S["cost"], S["eqsum"], S["notional"], S["maxdd"], self.p3_sessions,
                            self.spy_maxdd, self.ew_logex, YEARS)
            tw = time.perf_counter()
            summ = PL.world_summary(inp, nbi, cpx)
            fmt = self.p3_mode == "canary" and bool(self.qr_params.get("publish_format"))
            if self.p3_mode == "canary":                            # dummy configurations: timings (and format test)
                B = self.p3_books[self.p3_worlds.index(w)]
                line = (f"WC|{w['name']}|{time.perf_counter() - tw:.3f}|{B.counts['entries']}|{B.counts['exits']}|"
                        f"{B.counts['forced_delist'] + B.counts['forced_stale']}")
                if fmt:
                    line += "\nWF|" + w["name"] + "|" + json.dumps(summ, sort_keys=True, default=float)
            else:
                line = "W|" + w["name"] + "|" + json.dumps(summ, sort_keys=True, default=float)
            self._qr_log(line)
            out_bytes += len(line)
            if (self.p3_mode == "search" and w["name"] == "real") or (fmt and w is self.p3_worlds[0]):
                for i, cid in enumerate(ids):
                    ln = PL.y_line(cid, S["logex"][i], S["cost"][i], S["eqsum"][i], S["notional"][i], S["maxdd"][i],
                                   [m[i] for m in S["mlogex"]])
                    self._qr_log(ln)
                    out_bytes += len(ln)
        if self.p3_trace:
            for d, b, kind, g, q, px, fee in self.fill_day:
                self._qr_log(f"F|{self.p3_trace.index(b)}|{d}|{self.sid_of[g]}|{kind}|{q:.0f}|{px:.6f}|{fee:.2f}")
        self.p3_clock["pipeline"] += time.perf_counter() - t0
        self.p3_st["clock_s"] = {k: round(v, 2) for k, v in self.p3_clock.items()}
        self.p3_st["published_bytes_worlds"] = out_bytes
        if self.p3_mode == "canary":
            self.p3_st["real_mask_digest"] = self.p3_digest.hexdigest()
            self.p3_st["real_mask_cells"] = self.p3_mask_cells
        self._qr_log("G|" + json.dumps(dict(sessions=self.p3_sessions.tolist(), spy_maxdd=self.spy_maxdd.tolist(),
                                            ew_logex=self.ew_logex.tolist()) if self.p3_mode == "search" else
                                       dict(sessions=self.p3_sessions.tolist())))
        self._qr_log("QRX984|summary|" + json.dumps(self.p3_st, sort_keys=True, default=str))
