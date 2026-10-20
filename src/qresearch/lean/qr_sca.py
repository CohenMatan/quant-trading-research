# qr_sca v1.0 — SEC Classification Audit SCA-1 (owner D267, UR-1 option A; research/rr/sec_classification/
# SCA_protocol.md, frozen and SHA-256-pinned in qresearch.rr_sca). Pure logic on plain records: no QuantConnect object,
# no I/O. The host (X805) passes the public SEC reference (plain JSON from the Object Store) and, at each month-end
# audit point, one row per security QuantConnect passed to universe selection that day; summarize() returns aggregates
# only (counts, rates, bootstrap intervals, outcome). No identifier, ticker, per-security value, price or return
# leaves this module. Measurement only: nothing here repairs or changes any universe.
import calendar
import hashlib
import json
from bisect import bisect_left, bisect_right
from datetime import date

import numpy as np

MIN_CAP = 2e9
SHARES_FRESH_DAYS = 200          # cover shares: filed before the audit day and at most 200 days earlier
FLOAT_ASOF_DAYS = 456            # public float: as-of date at most ~15 months before the audit day
BAND = (0.5, 10.0)               # strong evidence: SEC cap / public float inside this band (identity plausibility)
FP_TOL = 0.02                    # fingerprint: |SEC shares / vendor-implied shares - 1| <= 2%, unique
SEC_EXIT_MARGIN = 150            # SEC-side exits assessable only if call + h <= last index day - 150 days
INDEX_END = date(2021, 12, 31).toordinal()
H_PRIMARY, H_SECONDARY = 24, 12
THR = {24: 0.005, 12: 0.0025}    # survivorship gate (RR3 / UB-1 values)
GAP_MAX = 0.03                   # coverage gate (RR3 / UB-1 value)
I_COVER_MIN = 0.80               # instrument: share of E stock-months matched to an SEC registrant
I_AGREE_MIN = 0.95               # instrument: among ticker-matched E with an SEC cap, SEC cap >= $2B
BOOT_B = 1000
BOOT_SEED = 20261020
# QuantConnect category of a security at an audit point (the host decides it; see the protocol, section 3)
CAT_E, CAT_ALT, CAT_M, CAT_X, CAT_B, CAT_N, CAT_I = range(7)
CAT_NAMES = ("E", "A_lt", "M", "X", "B", "N", "I")
# audit classes of a QuantConnect security
MATCHED, CONFIRMED, POSSIBLE = "matched", "confirmed", "possible"
WINDOWS = {"W1": ((2010, 1), (2021, 11)), "W1a": ((2011, 1), (2021, 11)), "W1b": ((2016, 1), (2021, 11))}


def norm(t):
    return "".join(ch for ch in str(t or "").upper() if ch not in ".-/ ")


def ordinal(iso):
    return date.fromisoformat(iso).toordinal()


def add_months(o, h):
    d = date.fromordinal(int(o))
    m = d.month - 1 + h
    y, m = d.year + m // 12, m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1])).toordinal()


def _r(x, n=6):
    return None if x is None or not np.isfinite(x) else round(float(x), n)


class SecRef:
    """The public SEC reference: per registrant dated ticker evidence, cover shares and public float (all dated by
    SEC filing date), and the last periodic filing date."""

    def __init__(self, doc):
        self.meta = doc["meta"]
        self.ciks = sorted(doc["r"], key=int)
        self.tick, self.s_day, self.s_val, self.f_day, self.f_asof, self.f_val, self.last = [], [], [], [], [], [], []
        for c in self.ciks:
            r = doc["r"][c]
            self.tick.append([(norm(t), ordinal(a), ordinal(b)) for t, a, b in r["t"]])
            s = sorted((ordinal(d), float(v)) for d, v in r["s"])
            self.s_day.append([d for d, _ in s])
            self.s_val.append([v for _, v in s])
            f = sorted((ordinal(d), ordinal(e), float(v)) for d, e, v in r["f"])
            self.f_day.append([d for d, _, _ in f])
            self.f_asof.append([e for _, e, _ in f])
            self.f_val.append([v for _, _, v in f])
            self.last.append(ordinal(r["l"]))

    def tickers_at(self, o):
        """registrant index -> set of tickers whose evidence window covers day o."""
        out = {}
        for i, tl in enumerate(self.tick):
            ts = {t for t, a, b in tl if a <= o <= b}
            if ts:
                out[i] = ts
        return out

    def shares_at(self, i, o):
        k = bisect_left(self.s_day[i], o) - 1          # filed strictly before the audit day
        if k < 0 or o - self.s_day[i][k] > SHARES_FRESH_DAYS:
            return None
        return self.s_val[i][k]

    def float_at(self, i, o):
        k = bisect_left(self.f_day[i], o) - 1
        while k >= 0:                                   # latest filed float whose as-of date is recent enough
            if o - self.f_asof[i][k] <= FLOAT_ASOF_DAYS:
                return self.f_val[i][k]
            k -= 1
        return None


def evidence(cap, flt):
    """'strong' / 'weak' / None from the SEC cap (cover shares x raw price) and the public float."""
    if cap is not None and flt is not None and cap >= MIN_CAP and flt >= MIN_CAP and BAND[0] <= cap / flt <= BAND[1]:
        return "strong"
    if (cap is not None and cap >= MIN_CAP) or (cap is None and flt is not None and flt >= MIN_CAP):
        return "weak"
    return None


class Audit:
    def __init__(self, ref):
        self.ref = ref
        self.ids = {}
        self.last_seen = []
        self.points = []                                # (year, month, call ordinal)
        self.sec_rows = []                              # (k, sec id, class code)  QuantConnect side
        self.reg_rows = []                              # (k, registrant, kind)  SEC side: 0 E-matched, 1 unresolved
        self.n_e = []                                   # E stock-months per point
        self.cnt = {}                                   # (k, name) -> count
        self.inst = []                                  # per point: dict of instrument counters
        self.c = dict(rows=0, ambiguous=0, fp_multi=0)

    def _id(self, key, o):
        i = self.ids.get(key)
        if i is None:
            i = self.ids[key] = len(self.ids)
            self.last_seen.append(o)
        return i

    def observe(self, key, o):
        i = self._id(key, o)
        if o > self.last_seen[i]:
            self.last_seen[i] = o

    def _add(self, k, name, n=1):
        self.cnt[(k, name)] = self.cnt.get((k, name), 0) + n

    def audit_point(self, year, month, call_o, day_o, rows):
        """rows: (key, ticker, cat, price, vendor_market_cap) for EVERY security passed to selection on the audit
        day (cat from CAT_*; price raw; market cap 0 if missing). day_o = the audit session's ordinal (PIT cut-off
        for SEC filings: filed strictly before it)."""
        k = len(self.points)
        self.points.append((year, month, call_o))
        ref = self.ref
        n = len(rows)
        self.c["rows"] += n
        cat = np.array([r[2] for r in rows], dtype=np.int64)
        px = np.array([r[3] for r in rows], dtype=float)
        mc = np.array([r[4] for r in rows], dtype=float)
        sid = [self._id(r[0], call_o) for r in rows]
        tmap = {}
        for j, r in enumerate(rows):
            t = norm(r[1])
            if t:
                tmap.setdefault(t, []).append(j)
        # fingerprint index: vendor-implied shares of securities with a vendor cap (E and A_lt)
        fp = [j for j in range(n) if cat[j] in (CAT_E, CAT_ALT) and px[j] > 0 and mc[j] > 0]
        fp_vs = sorted((mc[j] / px[j], j) for j in fp)
        fp_keys = [v for v, _ in fp_vs]
        best = {}                                       # row -> class rank (0 matched, 1 confirmed, 2 possible)
        inst = dict(e_matched_ticker=0, e_matched_fp=0, agree_n=0, agree_ge2b=0, ratio_within5=0, ratio_within2x=0)
        e_reg = set()
        for i, ts in ref.tickers_at(day_o).items():
            S = ref.shares_at(i, day_o)
            F = ref.float_at(i, day_o)
            cand = sorted({j for t in ts for j in tmap.get(t, ())})
            how = None
            if len(set(sid[j] for j in cand)) == 1:
                j, how = cand[0], "ticker"
            elif len(cand) > 1:
                self.c["ambiguous"] += 1
            if how is None and S is not None and fp_keys:
                lo, hi = bisect_left(fp_keys, S / (1 + FP_TOL)), bisect_right(fp_keys, S / (1 - FP_TOL))
                hits = [fp_vs[q][1] for q in range(lo, hi) if abs(S / fp_vs[q][0] - 1) <= FP_TOL]
                if len(hits) == 1:
                    j, how = hits[0], "fingerprint"
                elif len(hits) > 1:
                    self.c["fp_multi"] += 1
            if how is None:
                if F is not None and F >= MIN_CAP:
                    self.reg_rows.append((k, i, 1))
                    self._add(k, "unresolved")
                elif F is not None or S is not None:
                    self._add(k, "unresolved_weak")
                continue
            cap = S * px[j] if (S is not None and px[j] > 0) else None
            ev = evidence(cap, F)
            cj = int(cat[j])
            if cj == CAT_E:
                best[j] = 0
                e_reg.add(i)
                inst["e_matched_ticker" if how == "ticker" else "e_matched_fp"] += 1
                if how == "ticker" and cap is not None:
                    ratio = cap / mc[j]
                    inst["agree_n"] += 1
                    inst["agree_ge2b"] += int(cap >= MIN_CAP)
                    inst["ratio_within5"] += int(abs(ratio - 1) <= 0.05)
                    inst["ratio_within2x"] += int(0.5 <= ratio <= 2.0)
                continue
            if ev is None:
                self._add(k, "matched_not_sec_eligible_" + CAT_NAMES[cj])
                continue
            if cj in (CAT_M, CAT_N, CAT_B):
                rank = 1 if ev == "strong" else 2
                self._add(k, ("confirmed_" if rank == 1 else "possible_") + CAT_NAMES[cj])
                if best.get(j, 9) > rank:
                    best[j] = rank
            else:                                       # A_lt (vendor disagrees), X (other exchange), I (illiquid)
                self._add(k, {CAT_ALT: "disagree_vendor_below_2B", CAT_X: "legit_other_exchange",
                              CAT_I: "legit_illiquid"}[cj] + "_" + ev)
        for i in e_reg:
            self.reg_rows.append((k, i, 0))
        for j, rank in best.items():
            self.sec_rows.append((k, sid[j], rank))
        e_rows = np.where(cat == CAT_E)[0]
        for j in e_rows:
            if j not in best:
                self.sec_rows.append((k, sid[j], 3))  # E, not matched to an SEC registrant
        self.n_e.append(int(e_rows.size))
        for c_ in range(7):
            self._add(k, "qc_" + CAT_NAMES[c_], int((cat == c_).sum()))
        self.inst.append(inst)

    # ------------------------------------------------------------------------------------------- summary
    def summarize(self):
        P = self.points
        K = len(P)
        if K == 0:
            return dict(error="no audit points")
        Y = np.array([p[0] for p in P])
        CALL = np.array([p[2] for p in P], dtype=np.int64)
        final_call = int(CALL.max())
        last = np.array(self.last_seen, dtype=np.int64)
        sr = np.array(self.sec_rows, dtype=np.int64).reshape(-1, 3)
        rr = np.array(self.reg_rows, dtype=np.int64).reshape(-1, 3)
        k_s, sec, rank = sr[:, 0], sr[:, 1], sr[:, 2]
        k_r, reg, kind = rr[:, 0], rr[:, 1], rr[:, 2]
        reg_last = np.array(self.ref.last, dtype=np.int64)
        rng = np.random.default_rng(BOOT_SEED)
        years = {}
        for y in sorted(set(Y.tolist())):
            ky = np.where(Y == y)[0]
            ms, mr = np.isin(k_s, ky), np.isin(k_r, ky)
            E = ms & ((rank == 0) | (rank == 3))
            C, Pp = ms & (rank == 1), ms & (rank == 2)
            U = mr & (kind == 1)
            nE, nC, nP, nU = int(E.sum()), int(C.sum()), int(Pp.sum()), int(U.sum())
            rec = dict(months=int(ky.size), E=nE, confirmed=nC, possible=nP, unresolved=nU,
                       E_matched=int((ms & (rank == 0)).sum()),
                       securities=dict(confirmed=int(np.unique(sec[C]).size), possible=int(np.unique(sec[Pp]).size),
                                       unresolved_registrants=int(np.unique(reg[U]).size)),
                       gap_C=_r(nC / (nE + nC)) if nE + nC else None,
                       gap_CP=_r((nC + nP) / (nE + nC + nP)) if nE + nC + nP else None,
                       gap_max=_r((nC + nP + nU) / (nE + nC + nP + nU)) if nE + nC + nP + nU else None)
            rec["counts"] = {name: sum(v for (kk, nm), v in self.cnt.items() if nm == name and kk in set(ky.tolist()))
                             for name in sorted({nm for (_, nm) in self.cnt})}
            ins = {key: sum(self.inst[kk][key] for kk in ky) for key in self.inst[0]}
            ins["E_cover"] = _r(rec["E_matched"] / nE) if nE else None
            ins["agree_share"] = _r(ins["agree_ge2b"] / ins["agree_n"]) if ins["agree_n"] else None
            ins["within5_share"] = _r(ins["ratio_within5"] / ins["agree_n"]) if ins["agree_n"] else None
            ins["within2x_share"] = _r(ins["ratio_within2x"] / ins["agree_n"]) if ins["agree_n"] else None
            rec["instrument"] = ins
            # survivorship, QuantConnect side (exits = last day seen in the run), primary 24 months else 12
            h = None
            for hh in (H_PRIMARY, H_SECONDARY):
                hz = np.array([add_months(c, hh) for c in CALL], dtype=np.int64)
                if (hz[ky] <= final_call).any():
                    h = hh
                    break
            if h is None:
                rec["survivorship"] = dict(horizon=None)
            else:
                hz = np.array([add_months(c, h) for c in CALL], dtype=np.int64)
                ass = (hz <= final_call)[k_s]
                ex = last[sec] < hz[k_s]
                sv = dict(horizon=h, threshold=THR[h])
                sv["b_C"] = _boot(rng, sec, E & ass, C & ass, ex)
                sv["b_CP"] = _boot(rng, sec, E & ass, (C | Pp) & ass, ex)
                hr = np.array([add_months(c, h) for c in CALL], dtype=np.int64)
                ass_r = (hr <= INDEX_END - SEC_EXIT_MARGIN)[k_r]
                ex_r = reg_last[reg] < hr[k_r]
                sv["b_U_sec"] = _boot(rng, reg, mr & (kind == 0) & ass_r, U & ass_r, ex_r)
                rec["survivorship"] = sv
            rec["verdict"] = year_verdict(rec)
            years[str(y)] = rec
        res = dict(protocol="SCA-1", audit_points=K, first_point=f"{P[0][0]}-{P[0][1]:02d}",
                   last_point=f"{P[-1][0]}-{P[-1][1]:02d}", securities_seen=len(self.ids),
                   registrants=len(self.ref.ciks), sec_reference_sha256=None, checks=dict(self.c), years=years)
        res["windows"] = {w: window_verdict(years, a, b) for w, (a, b) in WINDOWS.items()}
        dig = hashlib.sha256()
        for kk in range(K):
            dig.update(json.dumps([P[kk][0], P[kk][1], self.n_e[kk]]).encode())
        res["digest_monthly_E"] = dig.hexdigest()
        return res


def _boot(rng, clus, inc, unr, ex):
    """b = e(I u U) - e(I), d = e(U) - e(I); clusters (securities / registrants) resampled B = 1,000 times."""
    pool = inc | unr
    if not inc.any():
        return dict(point=None, d=None, ci_b=[None, None], n_inc=0, n_unr=int(unr.sum()))
    u, inv = np.unique(clus[pool], return_inverse=True)
    p_inc, p_unr, p_ex = inc[pool].astype(float), unr[pool].astype(float), ex[pool].astype(float)
    nI, xI = np.bincount(inv, p_inc, u.size), np.bincount(inv, p_inc * p_ex, u.size)
    nU, xU = np.bincount(inv, p_unr, u.size), np.bincount(inv, p_unr * p_ex, u.size)

    def stat(w):
        sI, sxI, sU, sxU = w @ nI, w @ xI, w @ nU, w @ xU
        eI = sxI / sI if sI else np.nan
        return ((sxI + sxU) / (sI + sU) - eI) if sI + sU else np.nan, (sxU / sU - eI) if sU else np.nan
    b0, d0 = stat(np.ones(u.size))
    bs = np.empty(BOOT_B)
    for i in range(BOOT_B):
        bs[i] = stat(np.bincount(rng.integers(0, u.size, u.size), minlength=u.size).astype(float))[0]
    ci = [_r(np.nanquantile(bs, 0.025)), _r(np.nanquantile(bs, 0.975))] if np.isfinite(bs).any() else [None, None]
    return dict(point=_r(b0), d=_r(d0), ci_b=ci, n_inc=int(inc.sum()), n_unr=int(unr.sum()))


def year_verdict(rec):
    """Frozen interpretation rule (protocol section 5): FAIL / PASS / INCONCLUSIVE with the reasons."""
    why = []
    gc, gm = rec["gap_C"], rec["gap_max"]
    sv = rec["survivorship"]
    ins = rec["instrument"]
    fail = gc is not None and gc > GAP_MAX
    if fail:
        why.append("confirmed gap > 3%")
    if sv.get("horizon"):
        bc = sv["b_C"]["point"]
        if bc is not None and bc > sv["threshold"]:
            fail = True
            why.append("confirmed survivorship bias point > threshold")
    if fail:
        return dict(verdict="FAIL", reasons=why)
    ok = True
    if gm is None or gm > GAP_MAX:
        ok = False
        why.append("gap with possible + unresolved > 3%")
    if sv.get("horizon"):
        up = sv["b_CP"]["ci_b"][1]
        uu = sv["b_U_sec"]["ci_b"][1]
        tot = (up if up is not None else 0.0) + max(0.0, uu if uu is not None else 0.0)
        if up is None and sv["b_CP"]["n_unr"]:
            ok = False
            why.append("survivorship bound not computable")
        elif tot > sv["threshold"]:
            ok = False
            why.append("survivorship upper bound (confirmed + possible + unresolved) > threshold")
    else:
        why.append("survivorship not assessable (censoring)")
    if ins["E_cover"] is None or ins["E_cover"] < I_COVER_MIN:
        ok = False
        why.append("instrument: SEC reach of E < 80%")
    if ins["agree_share"] is None or ins["agree_share"] < I_AGREE_MIN:
        ok = False
        why.append("instrument: SEC cap agreement < 95%")
    return dict(verdict="PASS" if ok else "INCONCLUSIVE", reasons=why)


def window_verdict(years, a, b):
    ys = [y for y in years if a <= (int(y), 12) and (int(y), 1) <= b]
    v = [years[y]["verdict"]["verdict"] for y in ys]
    out = "FAIL" if "FAIL" in v else "PASS" if v and all(x == "PASS" for x in v) else "INCONCLUSIVE"
    return dict(outcome=out, years=dict(zip(ys, v)))
