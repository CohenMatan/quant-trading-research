# S027 v1.0 — H025 INSIDER CLUSTER BUYING ON FROZEN DATA v2 (owner D204; research/phase10/H025_spec.md, pinned by
# qresearch.p10h025). NO orders, NO portfolio, NO performance; nothing after 2017-12-31 is requested (the last price row
# is the 2017-12-29 session): 2011-2017 is H025's DEVELOPMENT / TRAINING period; 2018-2021 and the Holdout stay sealed.
# Event timing comes ONLY from the frozen SEC ledger (qr_h025_events, built offline from SEC Form 4 data); QuantConnect
# supplies the frozen Data v2 universe, verified identity and prices. A subclass of the pinned H022 / Data v2 host S024
# (uploaded byte-identical as qr_s024; S024 subclasses the frozen X998, uploaded as qr_x998): S027 skips Score v1
# entirely and only ADDS:
#   - the verified identity (qr_v2.Identity.m2) of every eligible / repair-candidate security recorded LIVE at every
#     monthly review, and the then-current ticker of eligible securities WITHOUT a verified identity;
#   - SPY RAW open / close with its split x dividend multiplier;
#   - modes: audit (eligibility / identity of every ledger event; NO price read for any response), canary (ledger,
#     identity, calendar, cooldown, timing and corporate-action checks; SYNTHETIC returns only), null (5,000 matched
#     null worlds; real event responses only hashed), real (the ONE development evaluation with the pinned c_EVENT).
# New attribute / method names carry the prefix q_ / _q_ (S024 and X998 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_s024, qr_x998, qr_h025,
# qr_h025_events, qr_h023, qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred, qr_p7_mech, qr_h020_stats, qr_xs, qr_xs_diag,
# qr_xs_panel, qr_v2, qr_data_v2, qr_sec_corrections, qr_industry, qr_fundamentals.
from AlgorithmImports import *
from datetime import date, datetime, timedelta
import hashlib
import json
import math
import time
import numpy as np
import qr_x998  # noqa: F401  (the frozen Data v2 host, imported by qr_s024)
import qr_s024 as S24
import qr_h025 as H
import qr_h025_events as EV
import qr_p7 as P7
import qr_p7_export as E
import qr_p7_pred as R
import qr_xs_diag as XD
import qr_xs_panel as XP

Q_SALT = "P10CP1-S027"
Q_FRESH = 25                      # fresh-history corporate-action recomputations per class (canary; non-event windows)
Q_SPY_FRESH = 25                  # fresh-history SPY total-return recomputations (canary)
Q_SYNTH_WORLDS = 200              # null machinery on SYNTHETIC responses (canary)
Q_FIRST_CAL = "2010-10-01"        # calendar digest range (ledger sessions)
Q_PRIMARY = ("ELIGIBLE", "ELIGIBLE_MULTICLASS")
Q_LAST = int(S24.LAST_SESSION)


def _ds(day):
    return str(np.datetime64(int(day), "D"))


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
        return None if not math.isfinite(float(x)) else float(x)
    if isinstance(x, float) and not math.isfinite(x):
        return None
    return x


class H025Insider(S24.H022DataV2):

    def qr_initialize(self):
        p = self.qr_params
        mode = p.get("mode")
        if mode not in ("audit", "canary", "null", "real"):
            raise Exception(f"S027: unknown mode {mode!r}")
        for k in ("payload_sha256", "calendar_sha256", "h025_code_sha256", "spec_sha256", "pred_code_sha256"):
            if not p.get(k):
                raise Exception(f"S027: params need {k}")
        if mode in ("canary", "null", "real") and not p.get("in_host_ledger_sha256"):
            raise Exception("S027: canary / null / real runs need the pinned in-host ledger digest")
        if mode == "null":
            a, b = (int(x) for x in p["seeds"])
            if not (1 <= a <= b <= H.R_NULL):
                raise Exception("S027: null seeds must lie in 1..5000")
            self.q_seeds = list(range(a, b + 1))
        if mode == "real":
            for k in ("c_event", "null_result_sha256", "threshold_commit", "response_panel_sha256",
                      "event_ledger_sha256"):
                if p.get(k) in (None, ""):
                    raise Exception(f"S027: real mode needs the pinned null provenance ({k})")
        self.qr_params = dict(p, mode="canary")         # the S024 / X998 initialisation (no S024 step is run)
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.h_mode = mode
        self.q_id, self.q_tick = {}, {}

    def _month_end(self, t, today, elig, adv, fl):
        super()._month_end(t, today, elig, adv, fl)
        if t in self.mon:
            ids, tick = {}, {}
            for sid in sorted(set(self.mon[t]) | set(self.cand.get(t, {}))):
                c, src = self.ident.m2(sid, today, self.pres_start.get(sid), self.first_day)
                ids[sid] = (H.cik_key(c), src)
                if c is None and sid in elig:
                    tick[sid] = str(elig[sid].value)
            self.q_id[t], self.q_tick[t] = ids, tick

    # ------------------------------------------------------------------------------------------------ SPY
    def _q_spy(self):
        spy = self.history(self.spy, S24.HIST_START, self.hist_end, Resolution.DAILY, fill_forward=False,
                           data_normalization_mode=DataNormalizationMode.RAW)
        D = self.cal.size
        O, C = np.full(D, np.nan), np.full(D, np.nan)
        d = XP.session_days(spy.index.get_level_values(-1).values)
        ok = d <= Q_LAST
        r = np.searchsorted(self.cal, d[ok])
        if not np.array_equal(self.cal[r], d[ok]):
            raise Exception("S027: SPY sessions differ from the panel calendar")
        O[r], C[r] = spy["open"].to_numpy(dtype=float)[ok], spy["close"].to_numpy(dtype=float)[ok]
        m = np.ones(D)
        key = {S24._sid(self.spy): 0}
        for r_, typ, ref, f in self._events(self.history(Split, [self.spy], S24.HIST_START, self.hist_end), key,
                                            self.cal, ("type", "referenceprice", "splitfactor")).get(0, []):
            if "OCCUR" in str(typ).upper() or float(ref) > 0:
                m[:r_] *= float(f)
        de = [(r_, float(a), float(rf)) for r_, a, rf in self._events(
            self.history(Dividend, [self.spy], S24.HIST_START, self.hist_end), key, self.cal,
            ("distribution", "referenceprice")).get(0, [])]
        self.q_spy = (O, C, m * XP.dividend_multiplier(D, de))
        lo = int(np.searchsorted(self.cal, int(np.datetime64(Q_FIRST_CAL).astype(np.int64))))
        self.st["spy"] = dict(dividends=len(de), missing_rows=int((~(np.isfinite(O[lo:]) & np.isfinite(C[lo:]))).sum()))
        if self.st["spy"]["missing_rows"]:
            raise Exception("S027: SPY has missing sessions in the H025 range")

    # ------------------------------------------------------------------------------------------------ ledger map
    def _q_review_tables(self, t):
        if t not in self.q_tab:
            elig = self.mon[t]
            sids = sorted(elig)
            mc = [self.h_mcap.get(t, {}).get(s) for s in sids]
            q = H.quintiles([np.nan if v is None else v for v in mc])
            ids = self.q_id.get(t, {})
            self.q_tab[t] = dict(
                sids=sids, q={s: int(x) for s, x in zip(sids, q)},
                sector={s: XD.ff12(elig[s]["sic"]) for s in sids},
                cik={s: ids.get(s, (None, None))[0] for s in sids},
                src={s: ids.get(s, (None, None))[1] for s in sids},
                unres={self.q_tick.get(t, {}).get(s) for s in sids if ids.get(s, (None, None))[0] is None} - {None})
        return self.q_tab[t]

    def _q_map(self, led):
        reviews = sorted(self.mon)
        rev_s = [str(t) for t in reviews]
        rmap = {str(t): t for t in reviews}
        self.q_tab = {}
        out = []
        for r in led:
            e = dict(r)
            if r["entry_session"] not in self.q_row:
                raise Exception(f"S027: entry session {r['entry_session']} is not a LEAN session")
            e["e0"] = self.q_row[r["entry_session"]]
            rv = H.latest_review(rev_s, r["trigger_date"])
            e["review"] = rv
            e["sid"], e["sector"], e["q"], e["id_src"] = None, None, None, None
            if rv is None:
                e["status"] = "NO_REVIEW"
            else:
                t = rmap[rv]
                tab = self._q_review_tables(t)
                adv = {s: self.mon[t][s]["adv"] for s in tab["sids"]}
                st, sid = H.map_issuer(r["issuer_cik"], tab["cik"], adv, tab["unres"], r["symbol_as_filed"])
                e["status"], e["sid"] = st, sid
                if sid is not None:
                    e["sector"], e["q"], e["id_src"] = tab["sector"][sid], tab["q"][sid], tab["src"][sid]
            e["primary"] = r["kind"] == "cluster" and r["window_status"] == "in_window" and e["status"] in Q_PRIMARY
            e["control"] = (r["kind"] == "single" and r["window_status"] == "in_window" and e["status"] in Q_PRIMARY
                            and not r["near_cluster"])
            out.append(e)
        return out

    @staticmethod
    def _q_in_host_rows(events):
        return [[e["event_id"], e["status"], e["review"], e["sid"], e["sector"], e["q"], e["id_src"]] for e in events]

    def _q_counts(self, events):
        c = {}
        for e in events:
            k = f"{e['kind']}|{e['window_status']}|{e['status']}"
            c[k] = c.get(k, 0) + 1
        yr = {}
        for e in events:
            if e["primary"]:
                y = e["trigger_date"][:4]
                yr[y] = yr.get(y, 0) + 1
        mc = sum(1 for e in events if e["primary"] and e["status"] == "ELIGIBLE_MULTICLASS")
        ids = {}
        for e in events:
            if e["primary"]:
                ids[e["id_src"]] = ids.get(e["id_src"], 0) + 1
        unres_rows = sum(len(v["unres"]) for v in self.q_tab.values())
        return dict(by_kind_window_status=c, primary_by_year=yr, primary=sum(yr.values()),
                    single_controls=sum(1 for e in events if e["control"]), multiclass=mc, primary_id_source=ids,
                    reviews_used=len(self.q_tab), unresolved_symbols_at_used_reviews=unres_rows,
                    sample_ok=H.sample_ok(yr, sum(yr.values())))

    # ------------------------------------------------------------------------------------------------ responses
    def _q_excess(self, j, e0, x0):
        return H.excess((self.RO[:, j], self.RC[:, j], self.M[:, j]), *self.q_spy, e0, x0, self.unv.get(j, ()))

    def _q_blocked(self, events):
        """issuer CIKs with an H025 CLUSTER event (any window status) whose entry row is within HOLD - 1 rows."""
        rows = sorted((e["e0"], H.cik_key(e["issuer_cik"])) for e in events if e["kind"] == "cluster")
        er = np.array([a for a, _ in rows], dtype=np.int64)
        ck = [b for _, b in rows]

        def at(e0):
            lo, hi = np.searchsorted(er, e0 - (H.HOLD - 1)), np.searchsorted(er, e0 + (H.HOLD - 1), side="right")
            return set(ck[lo:hi])
        return at

    def _q_panel(self, events):
        """Responses of every primary event and its matched-null pool, plus the single-insider controls and the
        diagnostic horizons. Returns (prim, ctrl, digest)."""
        blocked = self._q_blocked(events)
        cache = {}
        last = int(np.searchsorted(self.cal, Q_LAST))

        def cross(t, e0):
            key = (t, e0)
            if key not in cache:
                tab = self._q_review_tables(t)
                vals = {}
                for s in tab["sids"]:
                    ex, v, sp, st = self._q_excess(self.col[s], e0, e0 + H.HOLD - 1)
                    vals[s] = (ex, v, st)
                cache[key] = vals
            return cache[key]
        rmap = {str(t): t for t in self.mon}
        prim, ctrl = [], []
        h = hashlib.sha256()
        levels = {}
        for e in events:
            if not (e["primary"] or e["control"]):
                continue
            t, e0 = rmap[e["review"]], e["e0"]
            if self.cal[e0 + H.HOLD - 1] != np.datetime64(e["exit_session"]).astype(np.int64):
                raise Exception(f"S027: exit session mismatch for {e['event_id']}")
            tab = self._q_review_tables(t)
            vals = cross(t, e0)
            ex, v, st = vals[e["sid"]]
            rec = dict(id=e["event_id"], kind=e["kind"], month=e["trigger_date"][:7], year=int(e["trigger_date"][:4]),
                       y=ex, tsr=v, status=st, sector=e["sector"], q=e["q"])
            j = self.col[e["sid"]]
            for hz in H.DIAG_HORIZONS:
                x0 = e0 + hz - 1
                rec[f"h{hz}"] = self._q_excess(j, e0, x0)[0] if x0 <= last else float("nan")
            peers = [vals[s][1] for s in tab["sids"] if s != e["sid"] and tab["sector"][s] == e["sector"]
                     and math.isfinite(vals[s][1])]
            rec["sector_rel"] = v - float(np.mean(peers)) if peers and math.isfinite(v) else float("nan")
            for k in ("n_insiders", "cluster_value", "ceo_cfo", "director_only", "n_qualifying_filings",
                      "median_delay_days"):
                rec[k] = e[k]
            if e["primary"]:
                bl = blocked(e0)
                cand = [(s, tab["cik"][s], tab["sector"][s], tab["q"][s],
                         tab["cik"][s] is not None and tab["cik"][s] in bl)
                        for s in tab["sids"] if math.isfinite(vals[s][0])]
                lvl, pool = H.match_pool(e["sid"], e["issuer_cik"], e["sector"], e["q"], cand)
                rec["level"], rec["pool"] = lvl, np.array([vals[s][0] for s in pool])
                rec["pool_ids"] = pool
                levels[lvl] = levels.get(lvl, 0) + 1
                prim.append(rec)
            else:
                ctrl.append(rec)
            h.update(json.dumps([rec["id"], int(e0), e["sid"], _plain(rec["y"]), _plain(rec["tsr"]),
                                 rec.get("pool_ids"), _plain(rec.get("pool"))], separators=(",", ":")).encode())
        self.st["q_panel"] = dict(primary=len(prim), controls=len(ctrl), levels=levels, windows=len(cache),
                                pool_size=dict(min=min((p["pool"].size for p in prim), default=0),
                                               median=float(np.median([p["pool"].size for p in prim])) if prim else 0,
                                               empty=sum(1 for p in prim if p["pool"].size == 0)))
        return prim, ctrl, h.hexdigest()

    @staticmethod
    def _q_eval(prim):
        ok = [p for p in prim if math.isfinite(p["y"])]
        return ok, [p for p in prim if not math.isfinite(p["y"])]

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        p = self.qr_params
        self.st = dict(self.st0, mode=self.h_mode, checks=self.c, store_stats=dict(self.store.stats),
                       runtime_modules=S24._module_hashes(), spec_sha256=p["spec_sha256"])
        self._repair()
        self._build()
        self._q_spy()
        cal_s = [_ds(x) for x in self.cal if _ds(x) >= Q_FIRST_CAL]
        self.q_row = {_ds(x): i for i, x in enumerate(self.cal)}
        self.st["calendar"] = dict(sha256=H.sha(cal_s), sessions=len(cal_s), first=cal_s[0], last=cal_s[-1])
        if self.st["calendar"]["sha256"] != p["calendar_sha256"]:
            raise Exception("S027: LEAN sessions differ from the ledger calendar; nothing computed")
        if EV.PAYLOAD_SHA256 != p["payload_sha256"]:
            raise Exception("S027: the SEC event ledger differs from the pinned payload; nothing computed")
        led = H.read_ledger(EV.payload())
        t0 = time.perf_counter()
        events = self._q_map(led)
        rows = self._q_in_host_rows(events)
        self.st["in_host_ledger_sha256"] = H.sha(rows)
        self.st["counts"] = self._q_counts(events)
        self.st["map_s"] = round(time.perf_counter() - t0, 1)
        if self.h_mode == "audit":
            self.st["ledger_rows"] = self._q_emit("QRH", dict(rows=rows))
        else:
            if self.st["in_host_ledger_sha256"] != p["in_host_ledger_sha256"]:
                raise Exception("S027: the in-host ledger differs from the pinned digest; nothing computed")
            if self.h_mode == "canary":
                self._q_canary(events)
            elif self.h_mode == "null":
                self._q_null(events)
            else:
                self._q_real(events)
        self.st["pit_audit"] = dict(self.audit)
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        text = json.dumps(_plain(self.st), sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRP7V|{i // 9000}|{text[i:i + 9000]}")

    def _q_emit(self, tag, obj):
        blob = E.pack(json.dumps(_plain(obj), sort_keys=True, separators=(",", ":")))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"{tag}|{i // 9000}|{blob[i:i + 9000]}")
        return dict(blob_sha256=hashlib.sha256(blob.encode()).hexdigest(), blob_chars=len(blob))

    # ------------------------------------------------------------------------------------------------ canary
    def _q_canary(self, events):
        ck = dict(real_responses_computed=False, gates_on_real_data=False)
        rmap = {str(t): t for t in self.mon}
        reviews = sorted(self.mon)
        # 1. ledger / review / identity / calendar / cooldown
        g = dict(mapped=0, review_not_before_trigger=0, review_not_latest=0, sid_not_eligible=0, cik_mismatch=0,
                 entry_mismatch=0, exit_mismatch=0, cooldown_violations=0, events=len(events))
        for e in events:
            trig = datetime.strptime(e["trigger_et"], "%Y-%m-%d %H:%M:%S")
            d = int(np.datetime64(trig.date()).astype(np.int64))
            i = int(np.searchsorted(self.cal, d))
            if not (i < self.cal.size and self.cal[i] == d and trig.time() < datetime(2000, 1, 1, 9, 30).time()):
                i = int(np.searchsorted(self.cal, d, side="right"))
            g["entry_mismatch"] += int(i != e["e0"])
            if e["window_status"] == "in_window":
                g["exit_mismatch"] += int(_ds(self.cal[e["e0"] + H.HOLD - 1]) != e["exit_session"])
            if e["sid"] is None:
                continue
            g["mapped"] += 1
            t = rmap[e["review"]]
            g["review_not_before_trigger"] += int(not str(t) < e["trigger_date"])
            later = [x for x in reviews if str(x) < e["trigger_date"]]
            g["review_not_latest"] += int(later[-1] != t)
            g["sid_not_eligible"] += int(e["sid"] not in self.mon[t])
            g["cik_mismatch"] += int(self.q_id[t].get(e["sid"], (None,))[0] != H.cik_key(e["issuer_cik"]))
        by = {}
        for e in events:
            if e["kind"] == "cluster":
                by.setdefault(e["issuer_cik"], []).append(e["e0"])
        for v in by.values():
            v.sort()
            g["cooldown_violations"] += sum(1 for a, b in zip(v, v[1:]) if b - a < H.HOLD)
        ck["ledger"] = g
        # 2. SPY total return: fresh RAW history + events (S024's independent path) on deterministic windows
        last = int(np.searchsorted(self.cal, Q_LAST))
        lo = int(np.searchsorted(self.cal, int(np.datetime64("2011-02-01").astype(np.int64))))
        rng = np.random.default_rng(250027)
        sp = dict(checked=0, worst_rel=0.0)
        for e0 in sorted(rng.integers(lo, last - H.HOLD, Q_SPY_FRESH).tolist()):
            x0 = e0 + H.HOLD - 1
            O, C, M = self.q_spy
            a = (C[x0] * M[x0]) / (O[e0] * M[e0]) - 1.0
            b, _ = self._fresh_response(self.spy, e0 - 1, x0)
            sp["checked"] += 1
            sp["worst_rel"] = max(sp["worst_rel"], abs((1 + a) / (1 + b) - 1))
        ck["spy_total_return"] = sp
        # 3. corporate actions on NON-event windows: panel TSR vs the frozen response function vs a fresh history
        ev_sids = {(e["review"], e["sid"]) for e in events if e["sid"]}
        cls = dict(split=[], dividend=[], truncated=[], plain=[])
        prim = [e for e in events if e["primary"]]
        for e in prim:
            t = rmap[e["review"]]
            e0, x0 = e["e0"], e["e0"] + H.HOLD - 1
            for s in self._q_review_tables(t)["sids"]:
                if (e["review"], s) in ev_sids:
                    continue
                j = self.col[s]
                tag = f"{s}|{e0}"
                if any(e0 <= r <= x0 for r in self.splits.get(j, ())):
                    cls["split"].append(tag)
                elif any(e0 < r <= x0 for r, _ in self.dist.get(j, ())):
                    cls["dividend"].append(tag)
                elif not (np.isfinite(self.RC[x0, j]) and self.RC[x0, j] > 0):
                    cls["truncated"].append(tag)
                else:
                    cls["plain"].append(tag)
        fr = dict(by_class={}, frozen_fn_mismatch=0, examples=[])
        for c_, tags in cls.items():
            got = dict(available=len(tags), n=0, agree_1e9=0, worst_rel=0.0, status_agree=0)
            for tag in P7.pick(sorted(set(tags)), Q_FRESH, f"{Q_SALT}|{c_}"):
                s, e0 = tag.split("|")
                e0 = int(e0)
                x0 = e0 + H.HOLD - 1
                j = self.col[s]
                v, st, _, _ = H.tsr(self.RO[:, j], self.RC[:, j], self.M[:, j], e0, x0, self.unv.get(j, ()))
                rv, rst = R.response(self.RO[:, j], self.RC[:, j], self.M[:, j], e0 - 1, x0, self.unv.get(j, ()))
                same = (v == rv or (math.isnan(v) and math.isnan(rv)))
                fr["frozen_fn_mismatch"] += int(not same)
                if not math.isfinite(v):
                    continue
                vf, sf = self._fresh_response(self.sym[s], e0 - 1, x0)
                rel = abs((1.0 + vf) / (1.0 + v) - 1.0) if (1.0 + v) > 0 else float("inf")
                got["n"] += 1
                got["agree_1e9"] += int(rel <= 1e-9)
                got["status_agree"] += int(sf == {"ok": "ok", "truncated": "truncated"}.get(st, st))
                got["worst_rel"] = max(got["worst_rel"], rel)
                if rel > 1e-9 and len(fr["examples"]) < 10:
                    fr["examples"].append([c_, s, _ds(self.cal[e0]), float(f"{rel:.3g}")])
            fr["by_class"][c_] = got
        ck["corporate_actions"] = fr
        # 4. next-open and window timing on SYNTHETIC prices (planted overnight gap, prices outside the window)
        n = 60
        o = np.full(n, 100.0)
        c = np.full(n, 100.0)
        o[20], c[20:] = 110.0, 110.0                       # the gap happens at the entry open
        c[39] = 121.0
        o[40:], c[40:] = 500.0, 500.0                      # after the exit
        o[:19], c[:19] = 1.0, 1.0                          # before the entry
        so, sc, sm = np.full(n, 50.0), np.full(n, 50.0), np.ones(n)
        sc[39] = 55.0
        x = H.excess((o, c, np.ones(n)), so, sc, sm, 20, 39)
        ck["synthetic_timing"] = dict(stock=x[1], spy=x[2], excess=x[0],
                                      ok=abs(x[1] - 0.1) < 1e-12 and abs(x[2] - 0.1) < 1e-12 and abs(x[0]) < 1e-12)
        # 5. statistic, gates and null machinery on SYNTHETIC responses with the real event dates and pool sizes
        months = [e["trigger_date"][:7] for e in prim]
        years = [int(e["trigger_date"][:4]) for e in prim]
        u, idx = H.month_index(months)
        sizes = []
        for e in prim:
            tab = self._q_review_tables(rmap[e["review"]])
            bl = self._q_blocked(events)(e["e0"])
            cand = [(s, tab["cik"][s], tab["sector"][s], tab["q"][s], tab["cik"][s] is not None and tab["cik"][s] in bl)
                    for s in tab["sids"]]
            sizes.append(len(H.match_pool(e["sid"], e["issuer_cik"], e["sector"], e["q"], cand)[1]))
        syn = {}
        for eff in (0.0, 0.04):
            y = rng.normal(eff, 0.08, len(prim))
            s_ = H.summary(y, months, years)
            syn[str(eff)] = dict(t=s_["t"], mean=s_["mean"], gates=H.gates(s_, H.C_FLOOR))
        pools = [rng.normal(0.0, 0.08, max(1, k)) for k in sizes]
        t1 = time.perf_counter()
        worlds = [H.null_world(pools, idx, len(u), w) for w in range(1, Q_SYNTH_WORLDS + 1)]
        ws = (time.perf_counter() - t1) / Q_SYNTH_WORLDS
        cs = H.critical_value([w["t"] for w in worlds])
        ck["synthetic_statistics"] = dict(events=len(prim), months=len(u), planted=syn, world_s=round(ws, 5),
                                          world_s_5000=round(ws * 5000, 1),
                                          repeat_identical=H.null_world(pools, idx, len(u), 7) == worlds[6],
                                          c_synthetic=cs, empty_pools=sum(1 for k in sizes if k == 0),
                                          pool_size_median=float(np.median(sizes)) if sizes else 0.0)
        self.st["canary"] = ck

    # ------------------------------------------------------------------------------------------------ null / real
    def _q_null(self, events):
        prim, ctrl, dg = self._q_panel(events)
        self.st["response_panel_sha256"] = dg
        if self.qr_params.get("response_panel_sha256") and dg != self.qr_params["response_panel_sha256"]:
            raise Exception("S027: the response panel differs from the pinned digest; no null world computed")
        ok, bad = self._q_eval(prim)
        if any(p["pool"].size == 0 for p in ok):
            raise Exception("S027: an evaluable event has an empty null pool; null calibration failed")
        u, idx = H.month_index([p["month"] for p in ok])
        t0 = time.perf_counter()
        worlds = [H.null_world([p["pool"] for p in ok], idx, len(u), s) for s in self.q_seeds]
        out = self._q_emit("QRH", dict(fields=["seed", "t", "mean", "median", "win", "draws_sha"],
                                      worlds=[[w["seed"], w["t"], w["mean"], w["median"], w["win"], w["draws_sha"]]
                                              for w in worlds]))
        self.st["null"] = dict(seeds=[self.q_seeds[0], self.q_seeds[-1]], worlds=len(worlds), evaluable=len(ok),
                               not_evaluable=len(bad), months=len(u),
                               nonfinite=sum(1 for w in worlds if not math.isfinite(w["t"])),
                               world_s=round(time.perf_counter() - t0, 1), **out)

    def _q_real(self, events):
        p = self.qr_params
        self.st["provenance"] = {k: p[k] for k in ("c_event", "null_result_sha256", "threshold_commit",
                                                   "response_panel_sha256", "event_ledger_sha256")}
        prim, ctrl, dg = self._q_panel(events)
        self.st["response_panel_sha256"] = dg
        if dg != p["response_panel_sha256"]:
            raise Exception("S027: the response panel differs from the pinned digest; nothing evaluated")
        ok, bad = self._q_eval(prim)
        c_event = float(p["c_event"])
        y = np.array([q["y"] for q in ok])
        s = H.summary(y, [q["month"] for q in ok], [q["year"] for q in ok])          # the primary result first
        g = H.gates(s, c_event)
        keys = ("id", "month", "year", "y", "tsr", "status", "sector", "q", "h5", "h10", "h40", "h60", "sector_rel",
                "n_insiders", "cluster_value", "ceo_cfo", "director_only", "n_qualifying_filings",
                "median_delay_days")
        out = dict(c_event=c_event, summary=s, gates=g, not_evaluable=[q["id"] for q in bad],
                   fields=list(keys) + ["level"], events=[[q[k] for k in keys] + [q["level"]] for q in ok],
                   controls=[[q[k] for k in keys] + [None] for q in ctrl])
        res = self._q_emit("QRH", out)
        self.st["real"] = dict(evaluable=len(ok), not_evaluable=len(bad), controls=len(ctrl), t=s["t"],
                               mean=s["mean"], gates=g, **res)
