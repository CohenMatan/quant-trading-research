# X802 v1.0 — H029-A BUSINESS IMPROVEMENT DATA-FEASIBILITY AUDIT on Data v2.1 (owner D227;
# research/phase14/H029A_audit_spec.md). INFRASTRUCTURE / DATA QUALITY ONLY: NO orders, NO returns, NO performance
# statistic of any kind; the outputs are aggregate counts, quantiles and input-to-input rank correlations only.
# Nothing after 2021-12-31 is requested (the Holdout 2022-01-01 .. 2026-08-31 stays sealed).
# A subclass of the frozen Data v2.1 host X801 (uploaded byte-identical as qr_x801); every Data v2.1 rule (universe,
# M2 timing, restatement guard, identity, freshness, True TTM, SEC market-cap repair) is used unchanged. X802 only ADDS:
#   - at every month-end review, the eleven H029 candidate forms (qr_h029a) of every universe member, computed LIVE
#     from the point-in-time store as known on the selection day, with staleness, revision, pathology, seasonality
#     and True-TTM diagnostics; the SEC cover-count identity for F7;
#   - the market cap / price / ADV20 of each member (universe-bias audit) and the live total-assets ledger (H024 AG);
#   - at the end: F7 from SEC cover counts restated with splits dated on or before each review; the frozen Score v1
#     H022 population and the eleven H024 feature values (S028 / S029 code paths) for the input-overlap correlations;
#   - memory reduction (S029 pattern): run-time store released before the panel; high / low freed after the 200-day
#     state; no open-price / multiplier matrices are built (no return is ever formed).
# New attribute / method names carry the prefix z_ / _z_ (X801 / X998 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_x801, qr_h029a, qr_h024,
# qr_h023, qr_p7, qr_p7_score, qr_p7_export, qr_p7_pred, qr_p7_mech, qr_h020_stats, qr_xs, qr_xs_diag, qr_xs_panel,
# qr_v2, qr_data_v21, qr_sec_corrections, qr_industry, qr_fundamentals.
from AlgorithmImports import *
from datetime import date, datetime
import gc
import hashlib
import json
import math
import time
import numpy as np
import qr_x801 as X81
import qr_h029a as Z
import qr_h024 as K
import qr_p7 as P
import qr_p7_export as E
import qr_xs_diag as XD
from qr_sec_corrections import SECFiling

Z_REVIEW_FROM = date(2011, 1, 1)
Z_LAST = "2021-12-31"
Z_LEDGER_FROM, Z_LEDGER_TO = date(2010, 1, 1), date(2021, 1, 1)


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
    return out


def _trim():
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


def _log(x):
    return math.log(x) if x is not None and x > 0 else float("nan")


class H029AAudit(X81.DataV2Export):

    def qr_initialize(self):
        p = self.qr_params
        if p.get("mode") != "audit":
            raise Exception("X802: mode must be 'audit'")
        for k in ("spec_sha256", "h029a_code_sha256", "data_v21_manifest_sha256"):
            if not p.get(k):
                raise Exception(f"X802: params need {k}")
        if self.qr["end"] != Z_LAST:
            raise Exception("X802: the audit ends on 2021-12-31")
        self.qr_params = dict(p, mode="export")              # the X801 / X998 initialisation (export mode)
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        self.z_rows, self.z_px, self.z_mcap, self.z_ta, self.z_first, self.z_sec = {}, {}, {}, {}, {}, {}
        self.z_mem = []
        self.z_t = 0.0

    def _z_stage(self, name):
        self.z_mem.append([name, round(time.perf_counter() - self.t0, 1), _mem_now()])

    # ------------------------------------------------------------------------------------------------ live (month end)
    def _month_end(self, t, today, elig, adv, fl):
        super()._month_end(t, today, elig, adv, fl)
        if Z_LEDGER_FROM <= t < Z_LEDGER_TO:               # S028 live total-assets ledger (H024 AG), verbatim rule
            d = {}
            for sid in sorted(set(self.store.hist) | set(self.store.pending)):
                r = self.store.record(sid, today)
                v = r.values.get("total_assets") if r is not None else None
                if v is not None and math.isfinite(v):
                    d[sid] = float(v)
            self.z_ta[(t.year, t.month)] = d
        if t < Z_REVIEW_FROM or t not in self.mon:
            return
        t1 = time.perf_counter()
        info = {str(s.id): v[0] for s, v in self.qr_eligible_info.items()}
        px = {str(f.symbol.id): f.price for f in fl}
        members = sorted(set(self.mon[t]) | set(self.cand.get(t, {})))
        self.z_mcap[t] = {sid: info.get(sid) for sid in self.mon[t]}
        self.z_px[t] = {sid: (float(px[sid]) if sid in px else self.cand.get(t, {}).get(sid, {}).get("px"))
                        for sid in members}
        n, F = len(members), len(Z.FORMS)
        V, why = np.full((n, F), np.nan), np.zeros((n, F), np.int8)
        dst, age, rev, pth = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, bool), np.zeros(n, np.int64)
        seas, tw, t4 = np.full((n, 6), np.nan), np.zeros((n, 5), np.int8), np.zeros((n, 5), bool)
        viol = 0
        for i, sid in enumerate(members):
            cur = self.store.record(sid, today)           # promotes reports visible today BEFORE the grid is read
            w = Z.Window(self.store.hist.get(sid, {}), cur, today)
            cand = Z.candidates(w)
            for j, f in enumerate(Z.FORMS):
                if f != "F7":
                    v, wy = cand[f]
                    if v is not None and math.isfinite(v):
                        V[i, j] = v
                    why[i, j] = Z.W[wy]
            if w.ok:
                for r in w.grid[max(0, w.i0 - 8):w.i0 + 1]:   # the window's periods: first version seen at a review
                    first = self.z_first.setdefault((sid, r.period_end), r.file_date)
                    rev[i] |= r.file_date > first
                dst[i], age[i] = (today - w.q0.file_date).days, (today - w.q0.period_end).days
            pth[i], seas[i] = Z.pathology(w), Z.seasonality(w)
            tw[i], t4[i] = Z.ttm_reasons(w)
            viol += w.viol
        ciks = [(self.mon[t].get(sid) or self.cand[t][sid]).get("cik") for sid in members]
        self.z_rows[t] = dict(ids=members, pos={sid: i for i, sid in enumerate(members)}, V=V, why=why, dstale=dst,
                              age=age, revised=rev, path=pth, seas=seas, ttmw=tw, ttm4=t4, viol=viol, cik=ciks,
                              today=today)
        self.z_t += time.perf_counter() - t1

    def _repair(self):
        super()._repair()
        for t, keep in self.repaired.items():
            for sid in keep:
                r = self.cand[t][sid]
                self.z_mcap.setdefault(t, {})[sid] = self._secmcap(sid, r["cik_sh"], self.mon_sel[t], r["px"])[0]

    # ------------------------------------------------------------------------------------------------ panel (no returns)
    def _build(self):
        """X801's panel, the 200-day state for the review rows (S029 construction), then high / low freed. No open
        prices, no total-return multipliers for returns, nothing forward-looking is ever formed."""
        X81.DataV2Export._build(self)
        reviews = sorted(self.mon)
        need = sorted({self._row(t) for t in reviews})
        self.a200 = {j: P.calendar_states(self.C[:, j], self.H[:, j], self.L[:, j])["above200"][need]
                     for j in range(len(self.sids))}
        self.rix = {k: i for i, k in enumerate(need)}
        self.H = self.L = None
        _trim()

    def _z_scores(self, reviews, rows_k):
        """S029._w_scores (frozen Score v1 -> the H022 population), without the regime (not needed here)."""
        self._baselines(reviews, rows_k)
        pops, edig, tech_cache = {}, {}, {}
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
            edig[str(t)] = X81.sha(sorted(elig))
            pop = []
            for s, (bits, tot, pts) in res["rows"].items():
                if E.eligible_flag(bits, tot):
                    pop.append(s)
                    tech_cache[(t, s)] = tech(s)
            pops[t] = sorted(pop)
        return pops, edig, tech_cache

    def _z_h024(self, t, k, ids, tech_cache):
        """S028._w_features (the eleven H024 raw values), oriented by qr_h024.DIRECTION; rows with all 11 valid."""
        ta_prev = self.z_ta.get((t.year - 1, t.month), {})
        keep, out = [], []
        for s in ids:
            j = self.col[s]
            ti = tech_cache[(t, s)][0]
            pf = K.price_features(self.C[:, j], self.P[:, j], k, self.unv.get(j, ()), self.dist.get(j, ()))
            ff = K.fund_features(self.mon[t][s]["vals"], ta_prev.get(s), self.z_mcap.get(t, {}).get(s))
            row = K.feature_row(ti, pf, ff)
            if all(math.isfinite(x) for x in row):
                keep.append(s)
                out.append([K.DIRECTION[f] * x for f, x in zip(K.LIBRARY, row)])
        return keep, out

    def _z_f7(self, reviews):
        """F7 per (review, member) from the SEC cover counts of the Data v2 reference table, restated to the review's
        share basis with the security's splits dated on or before the review (frozen D111 rule)."""
        need = sorted({s for t in reviews for s in self.mon[t] if s not in self.splits})
        if need:
            self.splits.update(self._split_history(need))
        fil, st = {}, dict(no_identity=0, used=0, filing_after_today=0, split_after_today=0)
        out = {}
        for t in reviews:
            zr = self.z_rows[t]
            today = zr["today"]
            for sid in self.mon[t]:
                i = zr["pos"].get(sid)
                if i is None:
                    continue
                cik = zr["cik"][i]
                if cik is None or cik not in self.ref.shrows:
                    out[(t, sid)] = (None, "no_identity", None)
                    st["no_identity"] += 1
                    continue
                if cik not in fil:
                    fil[cik] = sorted((SECFiling(x) for x in self.ref.shrows[cik]), key=lambda x: (x.filed, x.accn))
                sp = self.splits.get(sid, ())
                st["split_after_today"] += 0          # dilution() applies only splits dated <= today
                v = Z.dilution(fil[cik], sp, today)
                out[(t, sid)] = v
                if v[2] is not None and v[2] >= today:
                    st["filing_after_today"] += 1
                st["used"] += 1
        return out, st

    # ------------------------------------------------------------------------------------------------ end
    def qr_on_end(self):
        p = self.qr_params
        self.st = dict(self.st0, mode="audit", hypothesis="H029", checks=self.c, store_stats=dict(self.store.stats),
                       spec_sha256=p["spec_sha256"], live_feature_s=round(self.z_t, 1))
        self._z_stage("on_end_start")
        for a in ("store", "rev", "led", "wk", "dg"):           # run-time state no longer read (S029 pattern)
            if hasattr(self, a):
                setattr(self, a, None)
        _trim()
        self._repair()
        self._build()
        self._z_stage("after_build")
        reviews = sorted(self.mon)
        rows_k = {t: self._row(t) for t in reviews}
        if str(reviews[-1]) != "2021-11-30" or str(reviews[0])[:7] != "2011-01" or len(reviews) != 131:
            raise Exception(f"X802: reviews {reviews[0]} .. {reviews[-1]} differ from 2011-01 .. 2021-11 (131)")
        f7, self.st["f7"] = self._z_f7(reviews)
        pops, edig, tech_cache = self._z_scores(reviews, rows_k)
        h024 = {}
        for t in reviews:
            keep, X = self._z_h024(t, rows_k[t], pops[t], tech_cache)
            h024[str(t)] = (keep, X)
        del tech_cache
        self._z_stage("after_h024")
        self.st["data_v21_digests"] = dict(review_eligibility=edig)
        self.st["h026_population"] = {str(t): len(h024[str(t)][0]) for t in reviews}
        months = []
        F7I = Z.FORMS.index("F7")
        for t in reviews:
            zr = self.z_rows[t]
            ids = sorted(self.mon[t])
            n = len(ids)
            ix = np.array([zr["pos"].get(s, -1) for s in ids], np.int64)
            have = ix >= 0
            g = np.where(have, ix, 0)
            V = np.where(have[:, None], zr["V"][g], np.nan)
            why = np.where(have[:, None], zr["why"][g], Z.W["no_fresh_report"]).astype(np.int64)
            d7 = np.full(n, np.nan)
            nf, ff = np.zeros(n, bool), np.zeros(n, np.int64)
            lmc, lpx, lad = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
            for i, s in enumerate(ids):
                sic = self.mon[t][s].get("sic")
                nf[i] = not (sic is not None and 6000 <= int(sic) <= 6999)
                ff[i] = XD.FF12_NAMES.index(XD.ff12(sic)) if sic is not None else -1
                lmc[i] = _log(self.z_mcap.get(t, {}).get(s))
                lpx[i] = _log(self.z_px.get(t, {}).get(s))
                lad[i] = _log(self.mon[t][s].get("adv"))
                v, wy, fd = f7.get((t, s), (None, "no_identity", None))
                V[i, F7I] = v if v is not None and math.isfinite(v) else np.nan
                why[i, F7I] = Z.W[wy]
                if fd is not None and v is not None:
                    d7[i] = float((zr["today"] - fd).days)
            months.append(dict(day=str(t), sid=ids, nf=nf, ff=ff, lmc=lmc, lpx=lpx, ladv=lad, V=V, why=why,
                               dstale=np.where(have, zr["dstale"][g], np.nan), age=np.where(have, zr["age"][g], np.nan),
                               d7=d7, revised=np.where(have, zr["revised"][g], False),
                               path=np.where(have, zr["path"][g], 0), seas=np.where(have[:, None], zr["seas"][g], np.nan),
                               ttmw=np.where(have[:, None], zr["ttmw"][g], Z.TTM_WHY.index("stale")),
                               ttm4=np.where(have[:, None], zr["ttm4"][g], False), viol=zr["viol"],
                               missing_rows=int((~have).sum())))
        self.z_rows = None
        _trim()
        self._z_stage("after_months")
        agg = Z.aggregate(months, h024=h024, h024_names=K.LIBRARY)
        agg["ff12_names"] = list(XD.FF12_NAMES)
        self._z_stage("after_aggregate")
        self.st["pit_audit"] = dict(self.audit)
        self.st["memory_stages"] = self.z_mem
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        blob = E.pack(json.dumps(_plain(agg), sort_keys=True, separators=(",", ":")))
        self.st["audit_blob"] = dict(sha256=hashlib.sha256(blob.encode()).hexdigest(), chars=len(blob))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"QRZA|{i // 9000}|{blob[i:i + 9000]}")
        text = json.dumps(_plain(self.st), sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRZ|{i // 9000}|{text[i:i + 9000]}")
