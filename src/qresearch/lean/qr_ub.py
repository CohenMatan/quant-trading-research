# qr_ub v1.0 — Universe Baseline Audit UB-1 (owner D263; research/rr/universe_baseline/UB_protocol.md, frozen and
# SHA-256-pinned in qresearch.rr_ub). Pure statistics on plain records: no QuantConnect object, no I/O. The host
# (X804) feeds one record per liquid security at each month-end audit point and the last day each security was
# seen; summarize() returns aggregates only (counts, rates, quantiles, bootstrap intervals, digests). No identifier,
# ticker, per-security value, price or return leaves this module.
import calendar
import hashlib
import json
from datetime import date

import numpy as np

MIN_CAP = 2e9
MIN_PRICE = 5.0
MIN_ADV = 5e6
ADV_Q = 0.10                 # U sets: ADV20 >= the 10th percentile of ADV20 over E(t)
TOL_V1 = 0.02                # V1a |R / market_cap - 1|
SPLIT_Q = 1.4                # V2 split detection: q >= 1.4 or <= 1 / 1.4
TOL_S_SPLIT = 0.03           # V2a restated / raw-like tolerance
TOL_R_SPLIT = 0.05           # V2b continuity tolerance
NOSPLIT = 0.01               # V3: |q - 1| < 1%
DS_EVENT = 0.05              # V3: |S2 / S1 - 1| >= 5%
DV_MOVE = 0.025              # V3: vendor-implied share move >= 2.5%
STALE_MONTHS = 18            # V4
FLAT_MONTHS = 24             # V4 flat-life
BOOT_B = 1000
BOOT_SEED = 20261020
H_PRIMARY, H_SECONDARY = 24, 12
CAT_A, CAT_M, CAT_N = 0, 1, 2
WINDOWS = {"W0": ((1999, 2), (2009, 12)), "W1": ((2010, 1), (2021, 11))}


def add_months(ordinal, h):
    d = date.fromordinal(int(ordinal))
    m = d.month - 1 + h
    y, m = d.year + m // 12, m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1])).toordinal()


def wilson(x, n, z=1.959963984540054):
    if n <= 0:
        return [None, None, None]
    p = x / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    w = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(p, 6), round(float(c - w), 6), round(float(c + w), 6)]


def _r(x, n=6):
    return None if x is None or not np.isfinite(x) else round(float(x), n)


class Audit:
    """Collects plain records. `observe(key, ordinal)` once per security per selection day; `audit_point(...)`
    once per month-end with the rows of the liquid set L(t)."""

    def __init__(self):
        self.ids = {}                     # security key -> dense int (in-memory only)
        self.last_seen, self.first_seen = [], []
        self.points = []                  # (year, month, call ordinal)
        self.cols = tuple([] for _ in range(10))   # sec, k, cat, mc, R, adv, S, SF, VS, scmc_present
        self.ever_common = set()
        self.c = dict(struct_errors=0, cap_errors=0, shares_errors=0, sf_errors=0, noncommon=0,
                      liquid=0, liquid_no_fund=0)

    def _id(self, key, ordinal):
        i = self.ids.get(key)
        if i is None:
            i = self.ids[key] = len(self.ids)
            self.last_seen.append(ordinal)
            self.first_seen.append(ordinal)
        return i

    def observe(self, key, ordinal):
        i = self._id(key, ordinal)
        if ordinal > self.last_seen[i]:
            self.last_seen[i] = ordinal

    def audit_point(self, year, month, call_ordinal, rows):
        """rows: (key, cat, market_cap, S, SF, price, adv, scmc_present); only L(t) names (price / ADV passed)."""
        k = len(self.points)
        self.points.append((year, month, call_ordinal))
        for key, cat, mc, S, SF, px, adv, scmc in rows:
            i = self._id(key, call_ordinal)
            R = S * px * SF if (cat != CAT_N and S is not None and SF is not None and S > 0 and SF > 0
                                and px > 0) else np.nan
            VS = mc / (px * SF) if (cat == CAT_A and SF is not None and SF > 0 and px > 0) else np.nan
            if cat != CAT_N:
                self.ever_common.add(i)
            vals = (i, k, cat, float(mc or 0.0), float(R), float(adv),
                    float(S) if S is not None and S > 0 else np.nan,
                    float(SF) if SF is not None and SF > 0 else np.nan, float(VS), bool(scmc))
            for col, v in zip(self.cols, vals):
                col.append(v)

    # ------------------------------------------------------------------------------------------- summary
    def summarize(self):
        P = self.points
        K = len(P)
        if K == 0 or not self.cols[0]:
            return dict(error="no audit points")
        Y = np.array([p[0] for p in P])
        MO = np.array([p[1] for p in P])
        CALL = np.array([p[2] for p in P], dtype=np.int64)
        c = self.cols
        sec, k, cat = (np.array(c[j], dtype=np.int64) for j in (0, 1, 2))
        mc, R, adv, S, SF, VS = (np.array(c[j], dtype=float) for j in (3, 4, 5, 6, 7, 8))
        scmc = np.array(c[9], dtype=bool)
        last = np.array(self.last_seen, dtype=np.int64)
        final_call = int(CALL.max())
        ever = np.zeros(len(self.ids), bool)
        if self.ever_common:
            ever[np.fromiter(self.ever_common, np.int64)] = True
        yr = Y[k]
        E = (cat == CAT_A) & (mc >= MIN_CAP)
        A_lt = (cat == CAT_A) & (mc < MIN_CAP)
        Mm = cat == CAT_M
        Rok = np.isfinite(R)
        R2B = Mm & Rok & (R >= MIN_CAP)
        M_Rlt = Mm & Rok & (R < MIN_CAP)
        M_inv = Mm & ~Rok
        Nc = (cat == CAT_N) & ever[sec]
        Nx = (cat == CAT_N) & ~ever[sec]
        q10 = np.full(K, np.inf)
        for kk in range(K):
            v = adv[E & (k == kk)]
            if v.size:
                q10[kk] = float(np.quantile(v, ADV_Q))
        match = adv >= q10[k]
        UA = (Mm | Nc) & match
        UB = (M_inv | Nc) & match
        UA_all = Mm | Nc
        UB_all = M_inv | Nc
        groups = dict(E=E, A_lt=A_lt, M=Mm, R2B=R2B, M_Rlt=M_Rlt, M_inv=M_inv, Nc=Nc, Nx=Nx, UA=UA, UB=UB,
                      UA_all=UA_all, UB_all=UB_all)
        # exits with censoring
        h24 = np.array([add_months(c, H_PRIMARY) for c in CALL], dtype=np.int64)
        h12 = np.array([add_months(c, H_SECONDARY) for c in CALL], dtype=np.int64)
        ok24, ok12 = h24 <= final_call, h12 <= final_call
        ex24 = last[sec] < h24[k]
        ex12 = last[sec] < h12[k]
        years = sorted(set(Y.tolist()))
        rng = np.random.default_rng(BOOT_SEED)
        out_years = {}
        for y in years:
            ky = Y == y
            m_y = yr == y
            months = int(ky.sum())
            cnt = {g: dict(stock_months=int((v & m_y).sum()), securities=int(np.unique(sec[v & m_y]).size))
                   for g, v in groups.items()}
            cnt["L"] = dict(stock_months=int(m_y.sum()), securities=int(np.unique(sec[m_y]).size))
            mon_E = [int((E & (k == kk)).sum()) for kk in np.where(ky)[0]]
            mon_EB = [int(((E | R2B) & (k == kk)).sum()) for kk in np.where(ky)[0]]
            nE, nR2B, nUA, nUB = (int((g & m_y).sum()) for g in (E, R2B, UA, UB))
            nUA_all, nUB_all = int((UA_all & m_y).sum()), int((UB_all & m_y).sum())
            rec = dict(months=months, counts=cnt,
                       monthly_E=[min(mon_E), _r(np.mean(mon_E), 2), max(mon_E)],
                       monthly_E_R2B=[min(mon_EB), _r(np.mean(mon_EB), 2), max(mon_EB)],
                       gap_A=_r(nUA / (nE + nUA)) if nE + nUA else None,
                       gap_B=_r(nUB / (nE + nR2B + nUB)) if nE + nR2B + nUB else None,
                       gap_A_unmatched=_r(nUA_all / (nE + nUA_all)) if nE + nUA_all else None,
                       gap_B_unmatched=_r(nUB_all / (nE + nR2B + nUB_all)) if nE + nR2B + nUB_all else None)
            # survivorship: primary horizon 24 months on assessable months; else 12; else unassessable
            if (ok24[ky]).any():
                h, okk, ex = H_PRIMARY, ok24, ex24
            elif (ok12[ky]).any():
                h, okk, ex = H_SECONDARY, ok12, ex12
            else:
                h = None
            if h is None:
                rec["survivorship"] = dict(horizon=None, assessable_months=0)
            else:
                ass = m_y & okk[k]
                sv = dict(horizon=h, assessable_months=int((ky & okk).sum()))
                rates = {}
                for g in ("E", "R2B", "UA", "UB", "A_lt", "Nc", "Nx", "M_inv", "M_Rlt"):
                    v = groups[g] & ass
                    n = int(v.sum())
                    rates[g] = dict(stock_months=n, exits=int(ex[v].sum()),
                                    rate=_r(ex[v].mean()) if n else None,
                                    securities=self._sec_level(sec, k, v, ex))
                sv["exit_rates"] = rates
                for view, inc, U in (("A", E, UA), ("B", E | R2B, UB)):
                    sv["bias_" + view] = self._boot(rng, sec, ass & inc, ass & U, ex)
                rec["survivorship"] = sv
            out_years[str(y)] = rec
        res = dict(protocol="UB-1", audit_points=K, first_point=f"{P[0][0]}-{P[0][1]:02d}",
                   last_point=f"{P[-1][0]}-{P[-1][1]:02d}", securities_seen=len(self.ids),
                   final_call=str(date.fromordinal(final_call)), checks=dict(self.c), years=out_years)
        res["validity"] = self._validity(Y, MO, sec, k, cat, mc, R, S, SF, VS, scmc, E, R2B, Mm)
        res["pre2010"] = self._pre(Y, sec, k, E, R2B, last)
        dig = hashlib.sha256()
        for kk in range(K):
            dig.update(json.dumps([P[kk][0], P[kk][1]] + [int((g & (k == kk)).sum()) for g in
                                  (E, A_lt, Mm, R2B, M_inv, Nc, Nx, UA, UB)]).encode())
        res["digest_monthly_counts"] = dig.hexdigest()
        return res

    @staticmethod
    def _sec_level(sec, k, v, ex):
        """Each security's first assessable stock-month in the group / year; exit share with a Wilson interval."""
        idx = np.where(v)[0]
        if idx.size == 0:
            return dict(n=0, exits=0, wilson=[None, None, None])
        order = np.lexsort((k[idx], sec[idx]))
        s_sorted = sec[idx][order]
        first = idx[order][np.r_[True, s_sorted[1:] != s_sorted[:-1]]]
        x = int(ex[first].sum())
        return dict(n=int(first.size), exits=x, wilson=wilson(x, first.size))

    @staticmethod
    def _boot(rng, sec, inc, unr, ex):
        """b = e(I u U) - e(I) and d = e(U) - e(I); securities are the bootstrap clusters (B = 1,000)."""
        pool = inc | unr
        if not pool.any() or not inc.any():
            return dict(point=None, d=None, ci_b=[None, None], ci_d=[None, None], n_inc=int(inc.sum()),
                        n_unr=int(unr.sum()), clusters=0)
        u, inv = np.unique(sec[pool], return_inverse=True)
        p_inc, p_unr, p_ex = inc[pool], unr[pool], ex[pool].astype(float)
        nI = np.bincount(inv, weights=p_inc.astype(float), minlength=u.size)
        xI = np.bincount(inv, weights=p_inc * p_ex, minlength=u.size)
        nU = np.bincount(inv, weights=p_unr.astype(float), minlength=u.size)
        xU = np.bincount(inv, weights=p_unr * p_ex, minlength=u.size)

        def stat(w):
            sI, sxI, sU, sxU = w @ nI, w @ xI, w @ nU, w @ xU
            eI = sxI / sI if sI else np.nan
            eA = (sxI + sxU) / (sI + sU) if sI + sU else np.nan
            eU = sxU / sU if sU else np.nan
            return eA - eI, eU - eI
        b0, d0 = stat(np.ones(u.size))
        bs, ds = np.empty(BOOT_B), np.empty(BOOT_B)
        for i in range(BOOT_B):
            w = np.bincount(rng.integers(0, u.size, u.size), minlength=u.size).astype(float)
            bs[i], ds[i] = stat(w)
        q = lambda x: [_r(np.nanquantile(x, 0.025)), _r(np.nanquantile(x, 0.975))] if np.isfinite(x).any() \
            else [None, None]
        return dict(point=_r(b0), d=_r(d0), ci_b=q(bs), ci_d=q(ds), n_inc=int(inc.sum()), n_unr=int(unr.sum()),
                    clusters=int(u.size))

    def _validity(self, Y, MO, sec, k, cat, mc, R, S, SF, VS, scmc, E, R2B, Mm):
        out = {}
        A_ok = (cat == CAT_A) & np.isfinite(R) & (mc > 0)
        v1 = {}
        for y in sorted(set(Y.tolist())):
            m = A_ok & (Y[k] == y)
            n = int(m.sum())
            if not n:
                v1[str(y)] = dict(n=0)
                continue
            ratio = R[m] / mc[m]
            v1[str(y)] = dict(n=n, within_2pct=_r(np.mean(np.abs(ratio - 1) <= TOL_V1)),
                              threshold_agree=_r(np.mean((R[m] >= MIN_CAP) == (mc[m] >= MIN_CAP))),
                              q=[_r(x, 4) for x in np.quantile(ratio, [0.01, 0.05, 0.5, 0.95, 0.99])])
        out["V1"] = v1
        # consecutive audit points of one security (sorted by security, then point)
        o = np.lexsort((k, sec))
        s_o, k_o = sec[o], k[o]
        nxt = (s_o[1:] == s_o[:-1]) & (k_o[1:] == k_o[:-1] + 1)
        i1, i2 = o[:-1][nxt], o[1:][nxt]
        wcode = np.array([next((i for i, w in enumerate(WINDOWS) if WINDOWS[w][0] <= (int(y), int(mo))
                                <= WINDOWS[w][1]), -1) for y, mo in zip(Y, MO)])
        wnames = list(WINDOWS)

        def wmask(idx, w):
            return wcode[k[idx]] == wnames.index(w)
        q = SF[i2] / SF[i1]
        split = np.isfinite(q) & ((q >= SPLIT_Q) | (q <= 1 / SPLIT_Q))
        sok = split & np.isfinite(S[i1]) & np.isfinite(S[i2])
        rs = S[i2] / S[i1]
        restated = sok & (np.abs(rs - 1) <= TOL_S_SPLIT)
        rawlike = sok & ~restated & (np.abs(rs / q - 1) <= TOL_S_SPLIT)
        bothA = (cat[i1] == CAT_A) & (cat[i2] == CAT_A) & (mc[i1] > 0) & (mc[i2] > 0)
        rok = sok & bothA & np.isfinite(R[i1]) & np.isfinite(R[i2])
        with np.errstate(divide="ignore", invalid="ignore"):
            cont = rok & (np.abs((R[i2] / R[i1]) / (mc[i2] / mc[i1]) - 1) <= TOL_R_SPLIT)
        v2 = {}
        for w in WINDOWS:
            wm = wmask(i2, w)
            v2[w] = dict(events=int((sok & wm).sum()), restated=int((restated & wm).sum()),
                         raw_like=int((rawlike & wm).sum()),
                         other=int((sok & wm & ~restated & ~rawlike).sum()),
                         events_M=int((sok & wm & (cat[i2] == CAT_M)).sum()),
                         restated_M=int((restated & wm & (cat[i2] == CAT_M)).sum()),
                         r_events=int((rok & wm).sum()), r_continuous=int((cont & wm).sum()),
                         splits_detected=int((split & wm).sum()))
        out["V2"] = v2
        # V3: four consecutive points k-2 .. k+1 of an A security; the share change between k-1 and k
        pos = {}
        for j in range(len(sec)):
            pos[(int(sec[j]), int(k[j]))] = j
        v3 = {w: dict(events=0, same=0, lead=0, lag=0, none=0) for w in WINDOWS}
        for j in np.where((cat == CAT_A) & np.isfinite(S) & np.isfinite(VS))[0]:
            s_, kk = int(sec[j]), int(k[j])
            jm1, jm2, jp1 = pos.get((s_, kk - 1)), pos.get((s_, kk - 2)), pos.get((s_, kk + 1))
            if jm1 is None or jm2 is None or jp1 is None:
                continue
            if not all(cat[x] == CAT_A and np.isfinite(VS[x]) for x in (jm1, jm2, jp1)):
                continue
            if not (np.isfinite(S[jm1]) and np.isfinite(SF[jm1]) and np.isfinite(SF[jp1]) and np.isfinite(SF[j])):
                continue
            if abs(SF[j] / SF[jm1] - 1) >= NOSPLIT or abs(SF[jp1] / SF[j] - 1) >= NOSPLIT:
                continue
            dS = S[j] / S[jm1] - 1
            if abs(dS) < DS_EVENT:
                continue
            sg = np.sign(dS)

            def moved(a1, a0):
                d = VS[a1] / VS[a0] - 1
                return np.sign(d) == sg and abs(d) >= DV_MOVE
            if wcode[kk] < 0:
                continue
            w = wnames[wcode[kk]]
            v3[w]["events"] += 1
            if moved(j, jm1):
                v3[w]["same"] += 1
            elif moved(jp1, j):
                v3[w]["lead"] += 1
            elif moved(jm1, jm2):
                v3[w]["lag"] += 1
            else:
                v3[w]["none"] += 1
        out["V3"] = v3
        # V4 staleness (S unchanged for >= 18 audit months) and flat-life securities
        stale = np.zeros(len(sec), bool)
        run_start = {}
        for j in o:
            if not np.isfinite(S[j]):
                continue
            s_ = int(sec[j])
            prev = run_start.get(s_)
            if prev is None or prev[0] != S[j]:
                run_start[s_] = (S[j], int(k[j]))
            else:
                stale[j] = int(k[j]) - prev[1] >= STALE_MONTHS
        v4 = {}
        anyM = np.zeros(len(self.ids), bool)
        anyM[np.unique(sec[Mm])] = True
        for w in WINDOWS:
            wm = wmask(np.arange(len(sec)), w)
            eS = E & np.isfinite(S) & wm
            rS = R2B & wm
            flat = dict(A=[0, 0], M=[0, 0])
            sel = np.where(wm & np.isfinite(S))[0]
            if sel.size:
                ss = sec[sel]
                order = np.argsort(ss, kind="stable")
                ss, sv = ss[order], S[sel][order]
                cut = np.r_[0, np.where(ss[1:] != ss[:-1])[0] + 1, ss.size]
                for a0, a1 in zip(cut[:-1], cut[1:]):
                    if a1 - a0 < FLAT_MONTHS:
                        continue
                    grp = "M" if anyM[ss[a0]] else "A"
                    flat[grp][0] += 1
                    flat[grp][1] += int(sv[a0:a1].min() == sv[a0:a1].max())
            v4[w] = dict(stale_E=_r(stale[eS].mean()) if eS.any() else None, n_E=int(eS.sum()),
                         stale_R2B=_r(stale[rS].mean()) if rS.any() else None, n_R2B=int(rS.sum()),
                         flat_A=flat["A"], flat_M=flat["M"])
        out["V4"] = v4
        v5 = {}
        for w in WINDOWS:
            wm = wmask(np.arange(len(sec)), w)
            mw = Mm & wm
            v5[w] = dict(M_stock_months=int(mw.sum()), S_present=_r(np.isfinite(S[mw]).mean()) if mw.any() else None,
                         R_valid=_r(np.isfinite(R[mw]).mean()) if mw.any() else None,
                         share_class_cap_present=_r(scmc[mw].mean()) if mw.any() else None)
        out["V5"] = v5
        return out

    def _pre(self, Y, sec, k, E, R2B, last):
        yr = Y[k]
        out = {}
        cut = date(2010, 1, 1).toordinal()
        for view, inc in (("A", E), ("B", E | R2B)):
            m99 = inc & (yr == 1999)
            s99 = np.unique(sec[m99])
            dead = int((last[s99] < cut).sum()) if s99.size else 0
            out[view] = dict(securities_1999=int(s99.size), dead_before_2010=dead,
                             share=_r(dead / s99.size) if s99.size else None)
        return out
