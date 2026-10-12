# X803 v1.0 — DATA v3 AUDIT (owner D229; research/phase14/data_v3/DATA_V3_spec.md, committed before any build).
# INFRASTRUCTURE / DATA QUALITY ONLY: NO orders, NO returns, NO portfolio, NO performance statistic of any kind; the
# outputs are aggregate counts, quantiles and digests only. Nothing after 2021-12-31 is requested (the Holdout
# 2022-01-01 .. 2026-08-31 stays sealed). A subclass of the frozen Data v2.1 host X801 (uploaded byte-identical as
# qr_x801); every Data v2.1 rule (universe, M2 timing, v2.1 restatement guard, identity, freshness, True TTM, SEC
# market-cap repair) is used unchanged and the v2.1 point-in-time store receives exactly the versions it always did.
# X803 only ADDS (all through qr_v3):
#   - guard v3 (spec 4): every version fed to the v2.1 store is checked against the restated SEC values of its period
#     (packed table qr_data_v3_NN); provenance categories are counted; a blocked version is excluded from the H029 v3
#     view only (V3Overlay), never from the v2.1 store;
#   - at every month-end review, the five fundamental H029 signals (F1, F2, F4, F5, F8) of every universe member
#     computed LIVE on the v3 view as known on the selection day, and on the v2.1 store where the two differ;
#   - for the stratified SEC sample (packed reference qr_v3val_NN), the vendor anchor and raw values;
#   - at the end: F7 from SEC cover counts (splits dated on or before each review), the H029 universe U_H029, coverage,
#     the SEC validation and F7 split-comparability aggregates, v2.1 differences, per-review panel digests.
# No price panel is built (no return can be formed). New attribute / method names carry the prefix v_ / _v_ (X801 /
# X998 names keep their meanings; D194).
# Modules uploaded by the runner (named here because its upload rules read this file): qr_x801, qr_v3, qr_data_v3,
# qr_v3val, qr_p7, qr_p7_score, qr_p7_export, qr_p7_mech, qr_xs, qr_xs_diag, qr_xs_panel, qr_v2, qr_data_v21,
# qr_sec_corrections, qr_industry, qr_fundamentals.
from AlgorithmImports import *
from datetime import date, timedelta
import gc
import hashlib
import json
import math
import time
import numpy as np
import qr_x801 as X81
import qr_v3 as V
import qr_xs_diag as XD
from qr_fundamentals import DEFAULT_MAX_AGE_DAYS, PITStore
from qr_sec_corrections import SECFiling

V_REVIEW_FROM = date(2011, 1, 1)
V_LAST = "2021-12-31"
Z = V.Z


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


def _trim():
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


def _add(h, k, n=1):
    h[k] = h.get(k, 0) + n


def _q(xs):
    a = np.asarray([x for x in xs if x is not None and math.isfinite(x)], float)
    if not a.size:
        return dict(n=0)
    return dict(n=int(a.size), share_gt_0_20=float((a > V.MATERIAL).mean()), median=float(np.median(a)),
                p90=float(np.percentile(a, 90)), p99=float(np.percentile(a, 99)), max=float(a.max()))


class _V3Store(PITStore):
    """The v2.1 store, unchanged, plus a notification of every version it queues (the guard-v3 hook)."""

    def __init__(self, host):
        super().__init__(DEFAULT_MAX_AGE_DAYS)
        self.v_host = host

    def observe(self, key, period_end, file_date, values, accession_year_, today):
        pend = self.pending.get(key)
        n0 = len(pend) if pend else 0
        super().observe(key, period_end, file_date, values, accession_year_, today)
        pend = self.pending.get(key)
        if pend and len(pend) > n0:
            self.v_host._v_fed(key, pend[-1], values, today)


class DataV3Audit(X81.DataV2Export):

    def qr_initialize(self):
        p = self.qr_params
        if p.get("mode") != "audit":
            raise Exception("X803: mode must be 'audit'")
        for k in ("spec_sha256", "v3_code_sha256", "guard_sha256", "val_sha256", "data_v21_manifest_sha256"):
            if not p.get(k):
                raise Exception(f"X803: params need {k}")
        if self.qr["end"] != V_LAST:
            raise Exception("X803: the audit ends on 2021-12-31")
        self.qr_params = dict(p, mode="export")              # the X801 / X998 initialisation (export mode)
        try:
            super().qr_initialize()
        finally:
            self.qr_params = p
        C, self.v_gparts = V.load_parts(V.GUARD_PREFIX, p["guard_sha256"])
        self.g3 = V.Guard3(C)
        del C
        vt, self.v_vparts = V.load_parts(V.VAL_PREFIX, p["val_sha256"])
        self.v_days = vt["days"]
        self.v_sector = vt["sector"]
        self.v_ref = {}
        nrev = len(self.v_days)
        for cik, rows in vt["ref"].items():
            arr, k = [None] * nrev, 0
            for i, r in enumerate(rows):
                j0 = r[0]
                j1 = rows[i + 1][0] if i + 1 < len(rows) else nrev
                for j in range(j0, j1):
                    arr[j] = r[1:]
            self.v_ref[cik] = arr
        del vt
        self.store = _V3Store(self)                  # replaces X801's (still empty) PITStore; same rules
        self.ov = V.V3Overlay()
        self.v_prov, self.v_block = {}, {}
        self.v_rows, self.v_samp = {}, []
        self.v_check = dict(fed=0, fed_no_match=0, fed_with_timeline=0, blocked=0, view_future_records=0,
                            vendor_anchor_ahead_of_sec=0, sample_day_mismatch=0)
        self.v_t = 0.0

    # ------------------------------------------------------------------------------------------------ guard v3 hook
    def _v_fed(self, sid, rec, vals, today):
        self.v_check["fed"] += 1
        cik, _src = self.ident.m2(sid, today, self.pres_start.get(sid), self.first_day)
        m = self.ref.match(cik, rec.period_end) if cik is not None else None
        y = str(today.year)
        if m is None:
            self.v_check["fed_no_match"] += 1
            self.ov.fed(sid, rec, False, False)
            return
        rows = self.g3.rows(cik, m[0])
        blocked, cats = self.g3.check(cik, m[0], vals, today)
        self.v_check["fed_with_timeline"] += int(rows is not None)
        for f, c in cats.items():
            _add(self.v_prov, f"{f}|{c}|{y}")
        if blocked:
            self.v_check["blocked"] += 1
            for f, c in cats.items():
                if c == "blocked_future":
                    _add(self.v_block, f"{f}|{y}")
        self.ov.fed(sid, rec, rows is not None, blocked)

    # ------------------------------------------------------------------------------------------------ live (month end)
    def _month_end(self, t, today, elig, adv, fl):
        super()._month_end(t, today, elig, adv, fl)
        if t < V_REVIEW_FROM or t not in self.mon:
            return
        t1 = time.perf_counter()
        members = sorted(set(self.mon[t]) | set(self.cand.get(t, {})))
        n = len(members)
        S5 = V.SEC_SIGNALS
        V3, dif = np.full((n, len(S5)), np.nan), np.zeros((n, len(S5)), np.int8)
        why = np.zeros((n, len(S5)), np.int8)
        td = V.dn(today)
        for i, sid in enumerate(members):
            cur = self.store.record(sid, today)          # promotes reports visible today BEFORE any history is read
            hist = self.store.hist.get(sid, {})
            h3, c3 = self.ov.view(hist, cur, sid, today)
            w3 = Z.Window(h3, c3, today)
            self.v_check["view_future_records"] += w3.viol
            s3 = V.signals(w3)
            if h3 is not hist or c3 is not cur:
                s2 = V.signals(Z.Window(hist, cur, today))
            else:
                s2 = s3
            for j, f in enumerate(S5):
                a, b = s3[f][0], s2[f][0]
                why[i, j] = Z.W[s3[f][1]]
                if a is not None and math.isfinite(a):
                    V3[i, j] = a
                if (a is None) != (b is None):
                    dif[i, j] = 2 if a is None else 3
                elif a is not None and a != b:
                    dif[i, j] = 1
            cik, _src = self.ident.m2(sid, today, self.pres_start.get(sid), self.first_day)
            if cik is not None and str(cik) in self.v_ref:
                ape, raw = V.vendor_raw(w3)
                if ape is not None:
                    m = self.ref.match(cik, ape)
                    if m is not None and m[1] + 1 > td:
                        self.v_check["vendor_anchor_ahead_of_sec"] += 1
                self.v_samp.append((t, sid, str(cik), None if ape is None else V.dn(ape), raw, td))
        rc = [(self.mon[t].get(sid) or self.cand[t][sid]).get("cik") for sid in members]
        self.v_rows[t] = dict(ids=members, pos={s: i for i, s in enumerate(members)}, V=V3, dif=dif, why=why, cik=rc,
                              today=today)
        self.v_t += time.perf_counter() - t1

    # ------------------------------------------------------------------------------------------------ end
    def _v_f7(self, reviews):
        need = sorted({s for t in reviews for s in self.mon[t] if s not in self.splits})
        if need:
            self.splits.update(self._split_history(need))
        fil, out = {}, {}
        chk = dict(filing_not_public=0)
        for t in reviews:
            zr = self.v_rows[t]
            today = zr["today"]
            for sid in self.mon[t]:
                i = zr["pos"].get(sid)
                if i is None:
                    continue
                cik = zr["cik"][i]
                if cik is None or cik not in self.ref.shrows:
                    out[(t, sid)] = (None, "no_identity", None, None)
                    continue
                if cik not in fil:
                    fil[cik] = sorted((SECFiling(x) for x in self.ref.shrows[cik]), key=lambda x: (x.filed, x.accn))
                v = V.f7(fil[cik], self.splits.get(sid, ()), today)     # only splits dated <= today apply (D111)
                if v[3] is not None and v[0] is not None and v[3] + timedelta(days=1) > today:
                    chk["filing_not_public"] += 1
                out[(t, sid)] = v
        return out, chk

    def qr_on_end(self):
        p = self.qr_params
        self.st = dict(self.st0, mode="audit", hypothesis="H029 (Data v3)", checks=self.c,
                       store_stats=dict(self.store.stats), spec_sha256=p["spec_sha256"], live_s=round(self.v_t, 1),
                       guard_parts=self.v_gparts, val_parts=self.v_vparts, guard_values=self.g3.n)
        self.st["v3"] = dict(self.v_check, overlay=dict(self.ov.check), overlay_blocked=len(self.ov.blocked))
        for a in ("store", "rev", "led", "wk", "dg", "ov"):                # run-time state no longer read
            if hasattr(self, a):
                setattr(self, a, None)
        _trim()
        self._repair()
        reviews = sorted(self.mon)
        if str(reviews[-1]) != "2021-11-30" or str(reviews[0])[:7] != "2011-01" or len(reviews) != 131:
            raise Exception(f"X803: reviews {reviews[0]} .. {reviews[-1]} differ from 2011-01 .. 2021-11 (131)")
        f7, self.st["f7_checks"] = self._v_f7(reviews)
        jt = {t: j for j, t in enumerate(reviews)}
        S6 = V.SIGNALS
        F7I = S6.index("F7")
        agg = dict(monthly=dict(day=[], universe=[], ge5=[], ge4=[], all6=[], **{f: [] for f in S6}),
                   digests={}, eligibility={}, reasons={}, v21_diff={}, f7_reasons={},
                   validation=dict(availability={}, anchor={}, delta={}, delta_sector={}, raw={}, composite={},
                                   composite_counts={}))
        dl, dls, cl = {}, {}, {}
        samp = {}
        for (t, sid, cik, ape, raw, td) in self.v_samp:
            samp[(t, sid)] = (cik, ape, raw, td)
        self.v_samp = None
        for t in reviews:
            zr = self.v_rows[t]
            per = V.period_of(t.year)
            ids = []
            for sid in sorted(self.mon[t]):
                sic = self.mon[t][sid].get("sic")
                if sic is None or 6000 <= int(sic) <= 6999:
                    continue
                ids.append(sid)
            n = len(ids)
            M = np.full((n, len(S6)), np.nan)
            ff = np.zeros(n, np.int64)
            for i, sid in enumerate(ids):
                k = zr["pos"].get(sid)
                ff[i] = XD.FF12_NAMES.index(XD.ff12(self.mon[t][sid].get("sic")))
                if k is not None:
                    for j, f in enumerate(V.SEC_SIGNALS):
                        M[i, S6.index(f)] = zr["V"][k, j]
                        _add(agg["reasons"], f"{f}|{int(zr['why'][k, j])}|{per}")
                        d = int(zr["dif"][k, j])
                        if d:
                            _add(agg["v21_diff"], f"{f}|{('', 'value', 'valid_only_v21', 'valid_only_v3')[d]}|{per}")
                else:
                    _add(agg["reasons"], f"no_row|{per}")
                v, wy, _c1, _fd = f7.get((t, sid), (None, "no_identity", None, None))
                M[i, F7I] = v if v is not None and math.isfinite(v) else np.nan
                _add(agg["f7_reasons"], f"{wy}|{per}")
            cnt = np.isfinite(M).sum(1)
            mo = agg["monthly"]
            mo["day"].append(str(t))
            mo["universe"].append(n)
            mo["ge5"].append(int((cnt >= 5).sum()))
            mo["ge4"].append(int((cnt >= 4).sum()))
            mo["all6"].append(int((cnt == 6).sum()))
            for j, f in enumerate(S6):
                mo[f].append(int(np.isfinite(M[:, j]).sum()))
            agg["digests"][str(t)] = V.panel_digest(ids, M)
            agg["eligibility"][str(t)] = X81.sha(sorted(self.mon[t]))
            # ----------------------------------------------------------------- SEC validation (sample stock-months)
            score, _cntv = V.h029_score(M)
            sorted_cols = [np.sort(M[np.isfinite(M[:, j]), j]) for j in range(len(S6))]
            sc_sorted = np.sort(score[np.isfinite(score)])
            j = jt[t]
            for i, sid in enumerate(ids):
                s = samp.get((t, sid))
                if s is None:
                    continue
                cik, ape, raw, td = s
                refs = self.v_ref.get(cik)
                ref = refs[j] if refs else None
                if ref is None:
                    continue
                sec = self.v_sector.get(cik, "?")
                if self.v_days[j] != td:
                    self.v_check["sample_day_mismatch"] += 1
                sa = ref[0]
                agree = ape is not None and sa is not None and abs(ape - sa) <= 6
                ak = "both_missing" if ape is None and sa is None else (
                    "vendor_missing" if ape is None else ("sec_missing" if sa is None else (
                        "agree" if agree else ("vendor_older" if ape < sa else "vendor_newer"))))
                _add(agg["validation"]["anchor"], f"{ak}|{per}")
                subs = M[i].copy()
                for q, f in enumerate(V.SEC_SIGNALS):
                    jj = S6.index(f)
                    vv, ss = M[i, jj], ref[1 + q]
                    hv, hs = math.isfinite(vv), ss is not None
                    _add(agg["validation"]["availability"], f"{f}|{'both' if hv and hs else ('vendor_only' if hv else ('sec_only' if hs else 'neither'))}|{per}")
                    subs[jj] = ss if hs else np.nan
                    if hv and hs and agree:
                        others = sorted_cols[jj]
                        dlt = abs(V.cdf_mid(others, vv) - V.cdf_mid(others, ss))
                        dl.setdefault(f"{f}|{per}", []).append(dlt)
                        dls.setdefault(f"{f}|{sec}", []).append(dlt)
                if agree:
                    for q, k in enumerate(V.RAW):
                        sv = ref[1 + len(V.SEC_SIGNALS) + q]
                        _add(agg["validation"]["raw"], f"{k}|{V.raw_class(raw.get(k), None if sv is None else V.ug4(sv))}|{per}")
                # composite: the stock's SEC values substituted; both sides use the same mid-rank percentile of the
                # value in the vendor cross-section of each signal (spec 7.3)
                pv, ps = [], []
                for jj in range(len(S6)):
                    others = sorted_cols[jj]
                    x, y_ = M[i, jj], subs[jj]
                    pv.append(np.nan if not math.isfinite(x) else 2.0 * V.cdf_mid(others, x) - 1.0)
                    ps.append(np.nan if not math.isfinite(y_) else 2.0 * V.cdf_mid(others, y_) - 1.0)
                pv, ps = np.asarray(pv), np.asarray(ps)
                okv, oks = np.isfinite(pv).sum() >= V.MIN_SIGNALS, np.isfinite(ps).sum() >= V.MIN_SIGNALS
                _add(agg["validation"]["composite_counts"], f"{'both' if okv and oks else ('vendor_only' if okv else ('sec_only' if oks else 'neither'))}|{per}")
                if okv and oks:
                    a_, b_ = float(np.nanmean(pv)), float(np.nanmean(ps))
                    cl.setdefault(per, []).append(abs(V.cdf_mid(sc_sorted, a_) - V.cdf_mid(sc_sorted, b_)))
        agg["validation"]["delta"] = {k: _q(v) for k, v in sorted(dl.items())}
        agg["validation"]["delta_sector"] = {k: _q(v) for k, v in sorted(dls.items())}
        agg["validation"]["composite"] = {k: _q(v) for k, v in sorted(cl.items())}
        agg["validation"]["sample_registrants"] = len(self.v_ref)
        # ----------------------------------------------------------------------- F7 split comparability (spec 8)
        valm = {}
        for (t, sid, cik, mc, px) in self.val:
            if mc and px and mc > 0 and px > 0:
                valm[(t, sid)] = (cik, mc / px)
        sp = dict(split=dict(n=0, disagree=0, big=0), non=dict(n=0, disagree=0, big=0), no_t12=0)
        for j, t in enumerate(reviews):
            if j < 12:
                continue
            t12 = reviews[j - 12]
            sel, sel12 = self.mon_sel[t], self.mon_sel[t12]
            for sid in self.mon[t]:
                sic = self.mon[t][sid].get("sic")
                if sic is None or 6000 <= int(sic) <= 6999:
                    continue
                v, wy, c1, _fd = f7.get((t, sid), (None, None, None, None))
                if v is None:
                    continue
                a, b = valm.get((t, sid)), valm.get((t12, sid))
                if a is None or b is None or a[0] != b[0]:
                    sp["no_t12"] += 1
                    continue
                mult = 1.0
                lo = min(c1, sel12) if c1 is not None else sel12
                inwin = False
                for ex, fac in self.splits.get(sid, ()):
                    if sel12 < ex <= sel and fac > 0:
                        mult *= 1.0 / fac
                    if lo < ex <= sel:
                        inwin = True
                rq = a[1] / (b[1] * mult)
                ratio = 1.0 - v
                g = sp["split" if inwin else "non"]
                g["n"] += 1
                g["disagree"] += int(abs(math.log(ratio) - math.log(rq)) > V.DISAGREE)
                g["big"] += int(abs(v) > 0.4)
        agg["f7_split"] = sp
        self.st["v3"]["sample_day_mismatch"] = self.v_check["sample_day_mismatch"]
        agg["provenance"] = self.v_prov
        agg["blocked"] = self.v_block
        agg["ff12_names"] = list(XD.FF12_NAMES)
        self.v_rows = None
        _trim()
        self.st["pit_audit"] = dict(self.audit)
        self.st["wall_s"] = round(time.perf_counter() - self.t0, 1)
        try:
            import resource
            self.st["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
        except Exception as ex:
            self.st["max_rss_mb"] = f"unavailable: {type(ex).__name__}"
        blob = X81.E.pack(json.dumps(_plain(agg), sort_keys=True, separators=(",", ":")))
        self.st["audit_blob"] = dict(sha256=hashlib.sha256(blob.encode()).hexdigest(), chars=len(blob))
        for i in range(0, len(blob), 9000):
            self._qr_log(f"QRVA|{i // 9000}|{blob[i:i + 9000]}")
        text = json.dumps(_plain(self.st), sort_keys=True, default=str)
        for i in range(0, len(text), 9000):
            self._qr_log(f"QRV|{i // 9000}|{text[i:i + 9000]}")
