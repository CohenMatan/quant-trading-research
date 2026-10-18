"""P13-CP6 (owner D239): R1 exposure-matched twin-portfolio test, SYNTHETIC validation only (offline; never uploaded to
QuantConnect; no H028 holdings, prices or returns are used anywhere).

Pieces:
  * real_sim: the frozen H028 portfolio mechanics (qr_h026.simulate arithmetic) on a synthetic panel: monthly Top-15
    with at most 3 per FF12 sector, holdings not in the target sold at the next open, kept positions untouched, new
    positions at equity / 15 (cash-constrained), $7 per order, slippage per side, a delisted holding goes to cash at its
    delisting value (no order), final liquidation after costs. It also records a SLOT for every position, the reason
    each slot closes (score / ineligible / delisted), and every month's costs and pre-trade equity;
  * matching: M1 exact cells, M2 hierarchical cells, M3 within-sector nearest neighbours on point-in-time percentile
    characteristics with a caliper and minimum support (the frozen R1 method), M4 portfolio-level exposure matching
    (feasibility only);
  * twin_sim: R twin worlds vectorised; each real slot has a twin drawn from its pool at the slot's entry date and held
    for exactly the real slot's life; a twin that leaves the eligible set (or is delisted) while the real slot continues
    is replaced from the real stock's CURRENT pool at the next decision (sale and purchase are real trades in Mode B);
    Mode A charges the twin portfolio the real portfolio's cost schedule as a fraction of equity (controlled
    comparison); Mode B makes each twin portfolio pay its own $7 orders and slippage (investable comparison);
  * the Monte Carlo p-value p = (1 + #{W_twin >= W_real}) / (R + 1) (one-sided);
  * R3: monthly factor regression of the real-style portfolio's excess return with Newey-West (lag 2) t(alpha).
"""
import math
import numpy as np

K = 15
SECTOR_CAP = 3
CAPITAL = 100_000.0
COMMISSION = 7.0
SLIPPAGE = 0.001
U_SD = 1.0 / math.sqrt(12.0)                                            # SD of a uniform percentile


# ----------------------------------------------------------------------------------------------- selection scores
# P1 weights: an H028-like composition (structural calibration only: LOWVOL carries ~16% of the absolute weight, as
# LOWVOL carries 15.5% of the committed H028 lambda-100 coefficients; growth (-BM), profitability, momentum and four
# uninformative persistent features carry the rest). Never fitted to any wealth or return outcome.
W_P1 = dict(LV=-0.50, BM=-0.60, PROF=0.45, MOM=0.20, N1=0.35, N2=0.35, N3=0.35, N4=0.35)
W_P1L = dict(LV=-1.00, BM=-0.30, PROF=0.30, N1=0.20, N2=0.20)          # LOWVOL-dominant stress variant (LV15-like)


def scores(months, process, wq=1.0):
    """P1 factor-driven (H028-like composition, no stock-specific information), P1L LOWVOL-dominant, P2 = P1 +
    planted predictor Q (weight wq), P3 = one persistent uninformative feature (randomised but persistent)."""
    out = []
    for m in months:
        z = m["z"]
        if process in ("P1", "P2"):
            sc = sum(w * z[f] for f, w in W_P1.items())
            if process == "P2":
                sc = sc + wq * z["Q"]
        elif process == "P1L":
            sc = sum(w * z[f] for f, w in W_P1L.items())
        elif process == "P3":
            sc = z["N3"].copy()
        else:
            raise ValueError(process)
        out.append(np.asarray(sc, float))
    return out


def pick(m, score, k=K, cap=SECTOR_CAP):
    order = np.lexsort((m["ids"], -np.asarray(score, float)))          # score desc, ties -> id
    out, cnt = [], {}
    for i in order:
        s = int(m["sector"][i])
        if cnt.get(s, 0) >= cap:
            continue
        out.append(int(m["ids"][i]))
        cnt[s] = cnt.get(s, 0) + 1
        if len(out) == k:
            break
    return out


# ----------------------------------------------------------------------------------------------- real-style portfolio
def real_sim(months, score_list, capital=CAPITAL, comm=COMMISSION, slip=SLIPPAGE, k=K, cap=SECTOR_CAP):
    """H028 mechanics on a synthetic panel. Returns dict(wealth, trace, monthly, buys, sells, commissions, slippage)."""
    cash, hold, slot = float(capital), {}, {}
    free = list(range(4 * k))
    trace, monthly = [], []
    nb = ns = 0
    com_t = slp_t = 0.0
    closed_delist = []                                                  # slots whose real stock delisted last period
    last = len(months) - 1
    eq_prev = capital
    for t, (m, sc) in enumerate(zip(months, score_list)):
        pos = {int(s): i for i, s in enumerate(m["ids"])}
        eq_pre = cash + sum(hold.values())
        tgt = pick(m, sc, k, cap)
        tset = set(tgt)
        rec = dict(eq_pre=eq_pre, closes=[(s_, None, "delisted") for s_ in closed_delist], keeps=[], buys=[],
                   cost=0.0, n_buys=0, n_sells=0)
        closed_delist = []
        com = slp = 0.0
        sell_cost = 0.0
        for sid in [s for s in hold if s not in tset]:
            v = hold.pop(sid)
            cash += v * (1.0 - slip) - comm
            com += comm
            slp += v * slip
            sell_cost += v * slip + comm
            ns += 1
            rec["n_sells"] += 1
            sl = slot.pop(sid)
            free.append(sl)
            rec["closes"].append((sl, sid, "score" if sid in pos else "ineligible"))
        rec["keeps"] = [(slot[s], s) for s in hold]
        eq = cash + sum(hold.values())
        new = [s for s in tgt if s not in hold]
        rec["a"] = 0.0
        buy_cost = 0.0
        if new:
            t_val = eq / k
            need = len(new) * (t_val * (1.0 + slip) + comm)
            a = t_val if need <= cash else max((cash - comm * len(new)) / (len(new) * (1.0 + slip)), 0.0)
            rec["a"] = a
            if a > 0:
                free.sort()
                for sid in new:
                    cash -= a * (1.0 + slip) + comm
                    com += comm
                    slp += a * slip
                    buy_cost += a * slip + comm
                    hold[sid] = a
                    sl = free.pop(0)
                    slot[sid] = sl
                    nb += 1
                    rec["n_buys"] += 1
                    rec["buys"].append((sl, sid))
        rec["n_new"] = len(rec["buys"])
        rec["cost"] = com + slp
        rec["sell_cost"], rec["buy_cost"] = sell_cost, buy_cost
        rec["held"] = [(slot[s], s) for s in hold]
        # period return
        for sid in list(hold):
            i = pos[sid]
            v = hold[sid] * (1.0 + m["r"][i])
            if m["dl"][i]:
                cash += v
                del hold[sid]
                sl = slot.pop(sid)
                free.append(sl)
                closed_delist.append(sl)
            else:
                hold[sid] = v
        if t == last:
            fin = 0.0
            rec["eq_pre_liq"] = cash + sum(hold.values())
            for sid, v in hold.items():
                cash += v * (1.0 - slip) - comm
                com += comm
                slp += v * slip
                fin += v * slip + comm
                ns += 1
            rec["final_cost"] = fin
            hold = {}
        com_t += com
        slp_t += slp
        eq_post = cash + sum(hold.values())
        monthly.append(eq_post / eq_prev - 1.0)
        eq_prev = eq_post
        trace.append(rec)
    return dict(wealth=cash, trace=trace, monthly=np.array(monthly), buys=nb, sells=ns, commissions=com_t,
                slippage=slp_t)


# ----------------------------------------------------------------------------------------------- matching
def m3_pool(m, i, dims, k_nn, caliper, m_min, caliper2=None, sector_mode="exact"):
    """M3: candidates in the same sector as row i (excluding i), standardised percentile distance on `dims`
    (Euclidean, divided by sqrt(len(dims)) so the caliper is per-dimension RMS), within the caliper, nearest k_nn
    (ties -> id). Level 1 = caliper; level 2 = caliper2 if given; returns (positions, level) with level 0 = abstain."""
    if sector_mode == "exact":
        same = np.flatnonzero(m["sector"] == m["sector"][i])
    elif sector_mode == "none":
        same = np.arange(m["sector"].size)
    else:                                                               # a dict: sector -> group
        g = np.array([sector_mode[int(x)] for x in m["sector"]])
        same = np.flatnonzero(g == g[i])
    same = same[same != i]
    if same.size == 0:
        return np.zeros(0, np.int64), 0
    P = np.column_stack([m["pct"][d][same] for d in dims])
    p0 = np.array([m["pct"][d][i] for d in dims])
    dist = np.sqrt(((P - p0) ** 2).mean(1))
    order = np.lexsort((m["ids"][same], dist))
    for lvl, cal in ((1, caliper), (2, caliper2)):
        if cal is None:
            continue
        ok = order[dist[order] <= cal][:k_nn]
        if ok.size >= m_min:
            return same[ok], lvl
    return np.zeros(0, np.int64), 0


def m1_cell(m, dims_bins):
    """M1 exact cells: tuple(sector, bin(dim) for dim, nbins in dims_bins) per row."""
    cols = [m["sector"]] + [np.minimum((m["pct"][d] * nb).astype(int), nb - 1) for d, nb in dims_bins]
    return list(zip(*[c.tolist() for c in cols]))


class Pools:
    """Cached M3 pools per (month, stock) for one matching variant."""

    def __init__(self, months, dims, k_nn, caliper, m_min, caliper2=None):
        self.months, self.dims = months, dims
        self.k_nn, self.caliper, self.m_min, self.caliper2 = k_nn, caliper, m_min, caliper2
        self.cache = {}
        self.pos = [{int(s): i for i, s in enumerate(m["ids"])} for m in months]

    def get(self, t, sid):
        key = (t, sid)
        if key not in self.cache:
            m = self.months[t]
            i = self.pos[t][sid]
            p, lvl = m3_pool(m, i, self.dims, self.k_nn, self.caliper, self.m_min, self.caliper2)
            self.cache[key] = (m["ids"][p], lvl, i)
        return self.cache[key]


# ----------------------------------------------------------------------------------------------- twin worlds
def twin_sim(months, real, pools, R, rng, mode="A", comm=COMMISSION, slip=SLIPPAGE, capital=CAPITAL, k=K,
             balance_dims=None, max_resample=10):
    """R twin worlds for one real-style path.

    Mode A (controlled): with rho_w = twin equity / real equity before the month's trades, world w pays rho_w x the
    real portfolio's sell costs and rho_w x its buy costs, buys every new slot at rho_w x the real purchase amount
    (capped by the world's cash), and pays rho_w-scaled final liquidation costs; twin-only replacement trades are
    executed at no cost (the controlled schedule is the real one). A world whose twins are the real stocks reproduces
    the real wealth exactly.
    Mode B (investable): every twin trade pays $comm and slip x value; new slots are sized from the world's own equity
    with the real cash-constrained rule; a replacement is bought with the replaced slot's proceeds after costs."""
    assert mode in ("A", "B")
    S = 4 * k
    tw = np.full((R, S), -1, np.int64)
    val = np.zeros((R, S))
    pend = np.zeros((R, S))                                             # proceeds earmarked for a slot's replacement
    cash = np.full(R, float(capital))
    st = dict(buys=np.zeros(R), sells=np.zeros(R), repl_inelig=np.zeros(R), repl_delist=np.zeros(R),
              commissions=np.zeros(R), slippage=np.zeros(R), dup=0, draws=0, abstain=0, fallback=0, slot_months=0,
              cash_share=[])
    bal = {d: [0.0, 0] for d in (balance_dims or ())}
    last = len(months) - 1
    rows = np.arange(R)
    real_tr = real["trace"]

    def locate(ids, x):
        p = np.minimum(np.searchsorted(ids, np.maximum(x, 0)), ids.size - 1)
        return p, (x >= 0) & (ids[p] == x)

    def draw(t, sid, s, mask):
        pool, lvl, _ = pools.get(t, sid)
        n = int(mask.sum())
        st["draws"] += n
        if lvl == 0:                                                    # honest abstention: self-match
            st["abstain"] += n
            return np.full(n, sid, np.int64)
        if lvl == 2:
            st["fallback"] += n
        w = rows[mask]
        d = pool[rng.integers(pool.size, size=n)]
        for _ in range(max_resample):
            other = tw[w].copy()
            other[:, s] = -1
            bad = (other == d[:, None]).any(1)
            if not bad.any():
                break
            d[bad] = pool[rng.integers(pool.size, size=int(bad.sum()))]
        other = tw[w].copy()
        other[:, s] = -1
        st["dup"] += int((other == d[:, None]).any(1).sum())
        return d

    for t, (m, rec) in enumerate(zip(months, real_tr)):
        ids = m["ids"]
        eq_pre = cash + val.sum(1) + pend.sum(1)
        rho = eq_pre / rec["eq_pre"] if rec["eq_pre"] > 0 else np.ones(R)
        # 1. real closures -> twin slots sold
        for (s, _sid, _why) in rec["closes"]:
            held = tw[:, s] >= 0
            if held.any():
                v = val[held, s]
                if mode == "B":
                    cash[held] += v * (1.0 - slip) - comm
                    st["commissions"][held] += comm
                    st["slippage"][held] += v * slip
                else:
                    cash[held] += v
                st["sells"][held] += 1
                tw[held, s] = -1
                val[held, s] = 0.0
            cash += pend[:, s]
            pend[:, s] = 0.0
        if mode == "A":
            cash -= rho * rec["sell_cost"]
        # 2. continuing real slots: replace twins that left the eligible set or were delisted
        for (s, sid) in rec["keeps"]:
            _, elig = locate(ids, tw[:, s])
            inel = (tw[:, s] >= 0) & ~elig
            if inel.any():
                v = val[inel, s]
                if mode == "B":
                    pend[inel, s] += v * (1.0 - slip) - comm
                    st["commissions"][inel] += comm
                    st["slippage"][inel] += v * slip
                else:
                    pend[inel, s] += v
                st["sells"][inel] += 1
                st["repl_inelig"][inel] += 1
                tw[inel, s] = -1
                val[inel, s] = 0.0
            need = tw[:, s] < 0
            if need.any():
                st["repl_delist"][need & ~inel] += 1
                d = draw(t, sid, s, need)
                amt = pend[need, s]
                if mode == "B":
                    a = np.maximum((amt - comm) / (1.0 + slip), 0.0)
                    st["commissions"][need] += np.where(amt > comm, comm, 0.0)
                    st["slippage"][need] += a * slip
                else:
                    a = amt
                tw[need, s] = d
                val[need, s] = a
                pend[need, s] = 0.0
                st["buys"][need] += 1
        # 3. new real slots
        nn = len(rec["buys"])
        if nn:
            if mode == "B":
                eq = cash + val.sum(1)
                t_val = eq / k
                need_c = nn * (t_val * (1.0 + slip) + comm)
                a = np.where(need_c <= cash, t_val, np.maximum((cash - comm * nn) / (nn * (1.0 + slip)), 0.0))
            else:
                bc = rho * rec["buy_cost"]
                a = rho * rec["a"]
                a = np.where(nn * a + bc <= cash * (1.0 + 1e-12) + 1e-9, a, np.maximum((cash - bc) / nn, 0.0))
                cash -= bc
            for (s, sid) in rec["buys"]:
                d = draw(t, sid, s, np.ones(R, bool))
                tw[:, s] = d
                val[:, s] = a
                if mode == "B":
                    cash -= a * (1.0 + slip) + comm
                    st["commissions"] += comm
                    st["slippage"] += a * slip
                else:
                    cash -= a
                st["buys"] += 1
        # balance of characteristics, real vs twin, per held slot at this decision
        if bal:
            for (s, sid) in rec["held"]:
                i_real = pools.pos[t][sid]
                p, okp = locate(ids, tw[:, s])
                for d_ in bal:
                    bal[d_][0] += float((m["pct"][d_][i_real] - m["pct"][d_][p[okp]]).sum())
                    bal[d_][1] += int(okp.sum())
        st["slot_months"] += len(rec["held"]) * R
        tot = cash + val.sum(1) + pend.sum(1)
        st["cash_share"].append(float(np.mean((cash + pend.sum(1)) / np.where(tot > 0, tot, 1.0))))
        # 4. period returns (a delisted twin's value goes to its slot's pending cash)
        held = tw >= 0
        if held.any():
            p, _ = locate(ids, tw)
            r = np.where(held, m["r"][p], 0.0)
            dl = held & m["dl"][p]
            val *= 1.0 + r
            pend[dl] += val[dl]
            val[dl] = 0.0
            tw[dl] = -1
        if t == last:
            held = tw >= 0
            if mode == "B":
                cash += (val * (1.0 - slip)).sum(1) - comm * held.sum(1) + pend.sum(1)
                st["commissions"] += comm * held.sum(1)
                st["slippage"] += (val * slip).sum(1)
            else:
                eq_end = cash + val.sum(1) + pend.sum(1)
                frac = rec.get("final_cost", 0.0) / rec["eq_pre_liq"] if rec.get("eq_pre_liq", 0) > 0 else 0.0
                cash = eq_end - frac * eq_end
            st["sells"] += held.sum(1)
            val[:] = 0.0
            pend[:] = 0.0
    out = dict(wealth=cash.copy(), **{k_: v for k_, v in st.items()})
    out["balance_smd"] = {d_: (v[0] / v[1] / U_SD if v[1] else float("nan")) for d_, v in bal.items()}
    return out


def mc_p(w_real, w_twin):
    """One-sided Monte Carlo p-value with the finite-sample correction: (1 + #{twin >= real}) / (R + 1)."""
    w_twin = np.asarray(w_twin, float)
    return (1.0 + float((w_twin >= w_real).sum())) / (w_twin.size + 1.0)


# ----------------------------------------------------------------------------------------------- M4 feasibility
def m4_acceptance(m, held_rows, dims, tol, n_try, rng):
    """M4 feasibility: share of random portfolios with the real portfolio's sector counts whose mean percentile on
    every dim is within `tol` of the real portfolio's mean (rejection sampling)."""
    secs = m["sector"][held_rows]
    target = np.array([m["pct"][d][held_rows].mean() for d in dims])
    by = {s: np.flatnonzero(m["sector"] == s) for s in np.unique(secs)}
    need = {s: int((secs == s).sum()) for s in by}
    acc = 0
    for _ in range(n_try):
        rows = np.concatenate([rng.choice(by[s], need[s], replace=False) for s in by if by[s].size >= need[s]])
        if rows.size != held_rows.size:
            continue
        mu = np.array([m["pct"][d][rows].mean() for d in dims])
        acc += int(np.all(np.abs(mu - target) <= tol))
    return acc / n_try


# ----------------------------------------------------------------------------------------------- R3 factor regression
def factors(months):
    """Point-in-time monthly factor returns from the eligible set: equal-weight universe UNI, LVF (lowest-LV quintile
    minus universe), BMF / PROFF / MOMF (top minus bottom tercile)."""
    out = dict(UNI=[], LVF=[], BMF=[], PROFF=[], MOMF=[], SPY=[])
    for m in months:
        r = np.where(m["dl"], m["r"], m["r"])
        u = r.mean()
        out["UNI"].append(u)
        out["SPY"].append(m["spy"])
        out["LVF"].append(r[m["pct"]["LV"] <= 0.2].mean() - u)
        for f, d in (("BMF", "BM"), ("PROFF", "PROF"), ("MOMF", "MOM")):
            p = m["pct"][d]
            out[f].append(r[p >= 2 / 3].mean() - r[p <= 1 / 3].mean())
    return {k_: np.array(v) for k_, v in out.items()}


def nw_ols(y, X, lag=2):
    """OLS with an intercept; Newey-West (Bartlett, `lag`) standard errors. Returns (coef, se, t)."""
    y = np.asarray(y, float)
    Z = np.column_stack([np.ones(len(y))] + [np.asarray(x, float) for x in X])
    ZtZ_inv = np.linalg.inv(Z.T @ Z)
    b = ZtZ_inv @ Z.T @ y
    e = y - Z @ b
    g = Z * e[:, None]
    S = g.T @ g
    for L_ in range(1, lag + 1):
        w = 1.0 - L_ / (lag + 1.0)
        c = g[L_:].T @ g[:-L_]
        S += w * (c + c.T)
    V = ZtZ_inv @ S @ ZtZ_inv
    se = np.sqrt(np.diag(V))
    return b, se, b / se


def r3(real, months, fac=None):
    fac = fac if fac is not None else factors(months)
    y = real["monthly"] - fac["SPY"]
    mkt = fac["SPY"]
    _, _, ta = nw_ols(y, [mkt, fac["LVF"]])
    _, _, tb = nw_ols(y, [mkt, fac["LVF"], fac["BMF"], fac["PROFF"], fac["MOMF"]])
    return dict(t_alpha_lv=float(ta[0]), t_alpha_all=float(tb[0]))
