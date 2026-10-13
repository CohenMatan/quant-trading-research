# qr_h029n3.py — Null #3 "Event-Copy Relay" for H029 / H030 (owner D237; DRAFT, research/phase14/
# H029_H030_amendment2_event_copy_relay.md, NOT frozen). Offline / research module on top of the frozen qr_h029 (which
# stays byte-identical as the Null #1 / #2 record). NOT uploaded by any host: P14-CP6a stopped before any real-data
# Null #3 world (the synthetic feasibility check showed B2 cannot preserve the real selection's persistence under
# realistic universe churn). Unit-tested in tests/test_p14_null3.py.
import math

import numpy as np

import qr_h026 as H
import qr_v3 as V3
from qr_h029 import (ADEQ_MEDIAN, ADEQ_Q, NULL_FIELDS, NullNotConstructible, blend, evaluate, h029_scores,
                     selection_structure)

# Event-Copy Relay (owner D237; research/phase14/H029_H030_amendment2_event_copy_relay.md, section B): a stock's null
# six-signal vector is a COPY rewritten only at its OWN events (entry, FF12 sector change, own vector change) with the
# current vector of a same-sector event stock at the same review, coupled monotonically by rank (recipient's NULL
# previous score <-> donor's REAL previous score); otherwise held. No pointer to a living donor exists, so another
# stock's entry / exit can never move it. The functions above (Null #1 / #2) are kept unchanged as the record.
FALLBACK_MAX = 0.05
Z99 = 2.576
KS_C01 = 1.6276
DUP_MAX = 0.05
SYNTH3_B_NOISE = 0.01
NULL3_FIELDS = NULL_FIELDS + ("p1_29", "p2_29", "ks29", "rho29", "dup29", "mult29", "miss29")


def rank_avg(x):
    """Average ranks 1..n (ties averaged); vectorised equivalent of qr_h026.avg_rank."""
    x = np.asarray(x, float)
    n = x.size
    if n == 0:
        return np.zeros(0)
    o = np.argsort(x, kind="mergesort")
    sx = x[o]
    st = np.flatnonzero(np.r_[True, sx[1:] != sx[:-1]])
    cnt = np.diff(np.r_[st, n])
    r = np.empty(n)
    r[o] = np.repeat(st + (cnt - 1) / 2.0 + 1.0, cnt)
    return r


def spearman(a, b):
    ra, rb = rank_avg(a), rank_avg(b)
    sa, sb = ra.std(), rb.std()
    if a.size < 3 or sa == 0 or sb == 0:
        return float("nan")
    return float(((ra - ra.mean()) * (rb - rb.mean())).mean() / (sa * sb))


def _same_rows(a, b):
    return ((a == b) | (np.isnan(a) & np.isnan(b))).all(1)


def relay_plan(m29, Vs):
    """World-independent part of Null #3 (spec B.2, B.4, D): per month the previous positions, event masks and kinds,
    per-sector event groups (ascending FF12), fallback candidates, real previous scores, global ids and vintages."""
    real = h029_scores(Vs)
    gids, gid_of = {}, []
    for m in m29:
        for s in m["ids"]:
            gids.setdefault(s, len(gids))
    last_vec, last_chg = {}, {}
    plan = []
    for t, (m, V) in enumerate(zip(m29, Vs)):
        ids, n = m["ids"], len(m["ids"])
        sec = np.asarray(m["sector"]).astype(np.int64)
        gid = np.array([gids[s] for s in ids], np.int64)
        vint = np.empty(n, np.int64)
        for k, s in enumerate(ids):
            if s not in last_vec or not _same_rows(V[k:k + 1], last_vec[s][None, :])[0]:
                last_chg[s] = t
            last_vec[s] = V[k].copy()
            vint[k] = last_chg[s]
        if t == 0:
            prev = np.full(n, -1, np.int64)
            ev = np.ones(n, bool)
            entry, secchg, upd = ev.copy(), np.zeros(n, bool), np.zeros(n, bool)
            yprev = np.full(n, np.nan)
        else:
            pm, PV = m29[t - 1], Vs[t - 1]
            pos = {s: k for k, s in enumerate(pm["ids"])}
            prev = np.array([pos.get(s, -1) for s in ids], np.int64)
            has = prev >= 0
            entry = ~has
            psec = np.asarray(pm["sector"]).astype(np.int64)
            secchg = np.zeros(n, bool)
            secchg[has] = psec[prev[has]] != sec[has]
            upd = np.zeros(n, bool)
            upd[has] = ~_same_rows(V[has], PV[prev[has]])
            ev = entry | secchg | upd
            yprev = np.full(n, np.nan)
            yprev[has] = real[t - 1][prev[has]]
        groups, fb = {}, {}
        for g in sorted(set(sec[ev].tolist())):
            ix = np.flatnonzero(ev & (sec == g))
            groups[g] = ix
            if ix.size == 1:
                cand = np.flatnonzero((sec == g) & (prev >= 0) & (np.arange(n) != ix[0]))
                if cand.size == 0:
                    raise NullNotConstructible(f"STOP — NULL #3 NOT CONSTRUCTIBLE (review {t}, sector {g})")
                fb[g] = cand
        plan.append(dict(t=t, prev=prev, ev=ev, entry=entry, secchg=secchg, upd=upd, yprev=yprev, sec=sec,
                         groups=groups, fb=fb, gid=gid, vint=vint, n=n))
    return plan, real


def constructibility(plan):
    """Spec D: fallback events / event recipients over t >= 2, and the frequency table by review and sector."""
    events = fallback = 0
    table = []
    for p in plan[1:]:
        events += int(p["ev"].sum())
        for g in p["fb"]:
            fallback += 1
            table.append((p["t"], int(g)))
    share = fallback / events if events else 0.0
    return dict(events=events, fallback=fallback, share=share, ok=bool(share <= FALLBACK_MAX), table=table,
                entries=int(sum(int(p["entry"].sum()) for p in plan[1:])),
                sector_changes=int(sum(int(p["secchg"].sum()) for p in plan[1:])),
                updates=int(sum(int(p["upd"].sum()) for p in plan[1:])))


def relay(m29, Vs, plan, seed, log=False, continuation=False):
    """One Null #3 world (spec B.3): (null vectors, null H029 scores, origin gids, origin vintages, assignment log).
    continuation=True is the P14-CP6a exploratory refinement (a recipient first continues with its held origin
    company when that company is an event in the same sector at the review); False = the approved B2 coupling."""
    rng = np.random.default_rng(seed)
    N, OI, OV, sc, logs = [], [], [], [], []
    for m, V, p in zip(m29, Vs, plan):
        n = p["n"]
        Nt = np.empty_like(V)
        oi = np.empty(n, np.int64)
        ov = np.empty(n, np.int64)
        if p["t"] > 0:
            keep = ~p["ev"]
            src = p["prev"][keep]
            Nt[keep], oi[keep], ov[keep] = N[-1][src], OI[-1][src], OV[-1][src]
            z = sc[-1]
        lg = []
        for g in sorted(p["groups"]):
            ix = p["groups"][g]
            k = ix.size
            uR, uD = rng.uniform(-1.0, 1.0, k), rng.uniform(-1.0, 1.0, k)
            tR, tD = rng.random(k), rng.random(k)
            if p["t"] > 0:
                pv = p["prev"][ix]
                kR = np.where(pv >= 0, z[np.maximum(pv, 0)], uR)
                yp = p["yprev"][ix]
                kD = np.where(np.isfinite(yp), yp, uD)
            else:
                kR, kD = uR, uD
            if k >= 2:
                pi = np.full(k, -1, np.int64)
                if continuation and p["t"] > 0:
                    loc = {int(p["gid"][j]): q for q, j in enumerate(ix)}
                    for q in np.argsort(tR, kind="stable"):
                        if pv[q] >= 0:
                            c = loc.get(int(OI[-1][pv[q]]), -1)
                            if c >= 0 and c != q and c not in set(pi[pi >= 0].tolist()):
                                pi[q] = c
                rq = np.flatnonzero(pi < 0)
                if rq.size:
                    used = set(pi[pi >= 0].tolist())
                    dq = np.array([q for q in range(k) if q not in used], np.int64)
                    oR, oD = rq[np.lexsort((tR[rq], kR[rq]))], dq[np.lexsort((tD[dq], kD[dq]))]
                    pi[oR] = oD
                    for q in range(oR.size):
                        r = oR[q]
                        if pi[r] == r:
                            if oR.size >= 2:
                                r2 = oR[q + 1] if q + 1 < oR.size else oR[q - 1]
                            else:
                                r2 = [x for x in np.argsort(tR, kind="stable") if x != r][0]
                            pi[r], pi[r2] = pi[r2], pi[r]
                don = ix[pi]
            else:
                cand = p["fb"][g]
                tF = rng.random(cand.size)
                don = np.array([cand[np.lexsort((tF, np.abs(p["yprev"][cand] - kR[0])))[0]]], np.int64)
            Nt[ix], oi[ix], ov[ix] = V[don], p["gid"][don], p["vint"][don]
            if log:
                lg.append((g, ix.copy(), don.copy()))
        N.append(Nt)
        OI.append(oi)
        OV.append(ov)
        sc.append(V3.h029_score(Nt)[0])
        logs.append(lg)
    return N, sc, OI, OV, logs


# ----------------------------------------------------------------------------------------------- structure (spec E, F)
def picks(ms, scores, k=H.K, cap=H.SECTOR_CAP):
    """Per-month Top-15 target id sets (frozen qr_h026.pick)."""
    return [set(m["ids"][i] for i in H.pick(m, sc, k, cap)) for m, sc in zip(ms, scores)]


def p1_persistence(m29, plan, scores):
    """Spec F P1: within-sector Spearman of H029 scores between t-1 and t among continuing same-sector names."""
    vals = []
    for p, sc in zip(plan[1:], scores[1:]):
        prev_sc = scores[p["t"] - 1]
        cont = (p["prev"] >= 0) & ~p["secchg"]
        num = den = 0.0
        for g in np.unique(p["sec"][cont]):
            ix = np.flatnonzero(cont & (p["sec"] == g))
            if ix.size < 3:
                continue
            r = spearman(prev_sc[p["prev"][ix]], sc[ix])
            if math.isfinite(r):
                num += r * ix.size
                den += ix.size
        if den > 0:
            vals.append(num / den)
    return float(np.mean(vals)) if vals else float("nan")


def p2_survival(m29, plan, pk):
    """Spec F P2: sum |S_t & S_t-1 & C_t| / sum |S_t-1 & C_t|, C_t = eligible at t-1 and t."""
    num = den = 0
    for p, m, pm, S, Sp in zip(plan[1:], m29[1:], m29[:-1], pk[1:], pk[:-1]):
        cont = set(m["ids"]) & set(pm["ids"])
        base = Sp & cont
        den += len(base)
        num += len(base & S)
    return num / den if den else float("nan")


def q_rule(m29, pk):
    """Spec C: exits / entries held by the real Top-15 vs random holding (99% normal interval)."""
    X = Ex = Vx = Y = Ey = Vy = 0.0
    nx = ny = 0
    for t in range(1, len(m29)):
        cur, prv = set(m29[t]["ids"]), set(m29[t - 1]["ids"])
        ex, en = prv - cur, cur - prv
        p = len(pk[t - 1]) / len(prv)
        X += len(ex & pk[t - 1])
        Ex += len(ex) * p
        Vx += len(ex) * p * (1 - p)
        q = len(pk[t]) / len(cur)
        Y += len(en & pk[t])
        Ey += len(en) * q
        Vy += len(en) * q * (1 - q)
        nx, ny = nx + len(ex), ny + len(en)
    zx = (X - Ex) / math.sqrt(Vx) if Vx > 0 else 0.0
    zy = (Y - Ey) / math.sqrt(Vy) if Vy > 0 else 0.0
    ok = abs(zx) <= Z99 and abs(zy) <= Z99
    return dict(exits=nx, held_exits=int(X), expected_exits=Ex, z_exit=zx, entries=ny, held_entries=int(Y),
                expected_entries=Ey, z_entry=zy, both_within=bool(ok), g_turn_29="gate" if ok else "diagnostic")


def _props(V):
    fin = np.isfinite(V)
    return np.r_[1.0 - fin.mean(0), fin.all(1).mean()]


def _rho6(V):
    C = V[np.isfinite(V).all(1)]
    if C.shape[0] < 4:
        return np.full(15, np.nan), C.shape[0]
    R = np.column_stack([rank_avg(C[:, j]) for j in range(6)])
    M = np.corrcoef(R, rowvar=False)
    return M[np.triu_indices(6, 1)], C.shape[0]


def xs_reference(Vs, real):
    """World-independent real side of spec E per month: sorted real scores, real complete-case Spearman pairs and
    counts, real missing proportions, sizes; plus the fixed bounds B1, B2."""
    ref = []
    for V, y in zip(Vs, real):
        rho, c = _rho6(V)
        ref.append(dict(ys=np.sort(y), rho=rho, c=c, props=_props(V), n=V.shape[0]))
    b1 = float(np.mean([KS_C01 * math.sqrt(2.0 / r["n"]) for r in ref]))
    b2 = float(np.mean([1.0 / math.sqrt(r["c"] - 3) for r in ref]))
    return ref, dict(B1=b1, B2=b2, B3=DUP_MAX, B4=Z99)


def ks_distance(sa, b):
    """Two-sample KS distance; sa sorted."""
    sb = np.sort(np.asarray(b, float))
    allv = np.r_[sa, sb]
    fa = np.searchsorted(sa, allv, side="right") / sa.size
    fb = np.searchsorted(sb, allv, side="right") / sb.size
    return float(np.abs(fa - fb).max())


def xs_stats(ref, N, sc, OI, OV):
    """Spec E world statistics (means over reviews): KS, joint |d rho|, exact-duplicate share, company multiplicity,
    missing-pattern z."""
    ks, rho, dup, mult, mz = [], [], [], [], []
    for r, Nt, s, oi, ov in zip(ref, N, sc, OI, OV):
        n = r["n"]
        ks.append(ks_distance(r["ys"], s))
        rn, _ = _rho6(Nt)
        rho.append(float(np.nanmean(np.abs(rn - r["rho"]))))
        key = oi * 100000 + ov
        _, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
        dup.append(float((cnt[inv] > 1).mean()))
        _, inv2, cnt2 = np.unique(oi, return_inverse=True, return_counts=True)
        mult.append(float((cnt2[inv2] > 1).mean()))
        q = np.clip(r["props"], 1.0 / n, 1.0 - 1.0 / n)
        mz.append(float((np.abs(_props(Nt) - r["props"]) / np.sqrt(2.0 * q * (1.0 - q) / n)).max()))
    return [float(np.mean(ks)), float(np.mean(rho)), float(np.mean(dup)), float(np.mean(mult)), float(np.mean(mz))]


def world3(m29, m30, V29, sc28_j, j29, w28, spy, days, plan, ref, seed):
    """One Null #3 world: the frozen evaluation of world() on the relay vectors + the spec E / F statistics."""
    N, sc29, OI, OV, _ = relay(m29, V29, plan, seed)
    e29 = evaluate(m29, sc29, spy, days)
    sc30 = [blend(a, s[j]) for a, s, j in zip(sc28_j, sc29, j29)]
    e30 = evaluate(m30, sc30, spy, days)
    t29, h29 = selection_structure(m29, sc29)
    t30, h30 = selection_structure(m30, sc30)
    p1 = p1_persistence(m29, plan, sc29)
    p2 = p2_survival(m29, plan, picks(m29, sc29))
    return [seed, e29["rel"]["s_up"], e29["wealth"], e29["risk"]["up_capture"], e29["risk"]["down_capture"],
            e29["risk"]["beta"], e29["pm"]["vol"], e29["pm"]["maxdd"], t29, h29,
            math.log(e30["wealth"] / w28), e30["wealth"], e30["risk"]["up_capture"], e30["risk"]["down_capture"],
            e30["risk"]["beta"], e30["pm"]["vol"], e30["pm"]["maxdd"], t30, h30, e30["rel"]["s_up"],
            p1, p2] + xs_stats(ref, N, sc29, OI, OV)


def real_structure3(m29, m30, V29, sc28_j, j29, plan, real):
    """Real side of spec F (scores only): turnover / HHI (H029, H030), P1, P2, eligible counts."""
    sc30 = [blend(a, s[j]) for a, s, j in zip(sc28_j, real, j29)]
    t29, h29 = selection_structure(m29, real)
    t30, h30 = selection_structure(m30, sc30)
    return dict(turn29=t29, hhi29=h29, turn30=t30, hhi30=h30, p1_29=p1_persistence(m29, plan, real),
                p2_29=p2_survival(m29, plan, picks(m29, real)), eligible29=[len(m["ids"]) for m in m29],
                joint30=[len(m["ids"]) for m in m30])


def adequacy3(rows, real, bounds, g_turn_29, cons):
    """Spec F: constructibility, structure (real inside the null [0.5, 99.5] %), cross-section (99.5th pct <= bound),
    risk (spec 9 C)."""
    a = np.asarray([r[1:] for r in rows], float)
    col = {f: a[:, i] for i, f in enumerate(NULL3_FIELDS[1:])}
    out, ok = {"constructibility": dict(share=cons["share"], ok=cons["ok"])}, cons["ok"]
    gates = ["hhi29", "hhi30", "turn30", "p1_29", "p2_29"] + (["turn29"] if g_turn_29 == "gate" else [])
    for k in ("turn29", "hhi29", "turn30", "hhi30", "p1_29", "p2_29"):
        lo, hi = np.percentile(col[k], ADEQ_Q)
        v = real[k]
        good = bool(lo <= v <= hi)
        out[k] = dict(real=v, lo=float(lo), hi=float(hi), median=float(np.median(col[k])), ok=good,
                      gate=k in gates)
        if k in gates:
            ok &= good
    for k, b in (("ks29", "B1"), ("rho29", "B2"), ("dup29", "B3"), ("miss29", "B4")):
        x = col[k]
        q = float(np.percentile(x, 99.5))
        good = bool(np.all(np.isfinite(x)) and q <= bounds[b])
        out[k] = dict(p99_5=q, median=float(np.median(x)), bound=bounds[b], ok=good)
        ok &= good
    out["mult29"] = dict(median=float(np.median(col["mult29"])), p99_5=float(np.percentile(col["mult29"], 99.5)),
                         gate=False)
    for k in ("vol29", "beta29", "up29", "dn29", "vol30", "beta30", "up30", "dn30"):
        x = col[k]
        good = bool(np.all(np.isfinite(x)) and x.std() > 0)
        if k[:-2] in ("beta", "up", "dn"):
            good &= bool(ADEQ_MEDIAN[0] <= float(np.median(x)) <= ADEQ_MEDIAN[1])
        out[k] = dict(median=float(np.median(x)), sd=float(x.std()), ok=good)
        ok &= good
    out["ok"] = bool(ok)
    out["verdict"] = "ADEQUATE" if ok else "H029/H030 NOT EVALUABLE — NULL #3 FAILED A FORMAL ADEQUACY GATE"
    return out


# ----------------------------------------------------------------------------------------------- canary synthetics (G)
def synthetic3(m29, plan, kind, seed):
    """Spec G: six identical columns. 'A' persistent noise updated at real events; 'B' planted persistent within-sector
    upside predictor (look-ahead, canary only); 'C2' = A minus 1.0 for stocks leaving E within 3 months."""
    rng = np.random.default_rng(seed)
    T = len(m29)
    if kind == "B":
        u = []
        for m in m29:
            r = np.nan_to_num(np.asarray(m["r_oo"], float))
            sec = np.asarray(m["sector"]).astype(np.int64)
            dm = r.copy()
            for g in np.unique(sec):
                k = sec == g
                dm[k] = r[k] - r[k].mean()
            u.append(dict(zip(m["ids"], dm * (1.0 if m["spy_oo"] > 0 else 0.0))))
    out, prev = [], None
    for t, (m, p) in enumerate(zip(m29, plan)):
        n = p["n"]
        if kind == "B":
            f = np.array([np.mean([u[t + h].get(s, 0.0) if t + h < T else 0.0 for h in range(3)])
                          for s in m["ids"]]) + rng.normal(0.0, SYNTH3_B_NOISE, n)
        else:
            f = rng.normal(0.0, 1.0, n)
        if t == 0:
            z = f
        else:
            held = prev[np.maximum(p["prev"], 0)]
            if kind == "B":
                z = np.where(p["ev"], f, held)
            else:
                new = np.where(p["entry"], f, 0.9 * held + math.sqrt(0.19) * f)
                z = np.where(p["ev"], new, held)
        prev = z
        out.append(z)
    if kind == "C2":                                     # stocks absent from E at some review t+1..t+3
        for t, m in enumerate(m29):
            ahead = [set(x["ids"]) for x in m29[t + 1:t + 4]]
            out[t] = out[t] - np.array([1.0 if any(s not in a for a in ahead) else 0.0 for s in m["ids"]])
    return [np.repeat(z[:, None], 6, axis=1) for z in out]
