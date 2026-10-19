# qr_sys1.py — SYS-1 single-account engine (owner D251 / D252; research/longhorizon/sys1/SYS1_protocol.md, pinned by
# qresearch.sys1). Pure numpy on the FROZEN qr_h026 month data (outer months 2015-2021); the same file is unit-tested
# offline and uploaded to the host S032. No signal is created here: stock selection is the frozen qr_h026.pick on the
# frozen H028 / LV15 scores; ETFs (SPY, SPLV, USMV) are held as single positions.
#   * ONE cash ledger per account; every trade pays $7 + slippage on its traded value; no borrowing, no leverage;
#   * E1 execution (owner OD-3): the frozen H028 shadow-book convention (notional fractional orders at the entry open,
#     total-return valuation with dividends inside each position, delisted stocks valued at the last real close and
#     turned into cash at the next review) — an IDEALISED research model, not a validated implementation;
#   * deterministic order at every review (protocol section 6): (1) stock sells, (2) stock buys sized at
#     sleeve x account equity / 15 (funded first by cash, then by selling the absorbing ETF), (3) target-ETF sells,
#     (4) target-ETF buys, (5) the absorbing ETF takes the residual cash;
#   * account(sleeve=1, absorber=None, targets=None, min_ticket=0) is qr_h026.simulate bit for bit (canary C1) and
#     account(scores=None, absorber="spy") is qr_h026.spy_simulate bit for bit (canary C2).
import math
import numpy as np

import qr_h026 as H
import qr_h027 as G

CAPITAL = 200_000.0                   # SYS-1 only (owner OD-2); the programme baseline stays $100,000
SLEEVE = 0.5                          # new stock tickets = 50% of account equity / 15 (owner OD-5)
MIN_TICKET = 5_000.0                  # minimum new stock position (D041 / D044, unchanged)
MAX_INIT_W = 0.10                     # maximum initial stock weight in the account (unchanged)
ETF_MIN_TRADE = 1_000.0               # ETF trades smaller than this are not executed; that cash stays at 0%
BETA_WIN = 252                        # trailing sessions for ex-ante betas
BETA_MIN_OBS = 189                    # paired daily returns required (75% of the window)
BLUME = (0.67, 0.33)                  # Blume (1971) adjustment: 0.67 beta + 0.33
SLIPS = (H.SLIPPAGE, H.STRESS_SLIPPAGE)
ETFS = ("spy", "splv", "usmv")


def _etf_fields(m, name):
    return m[f"{name}_oo"], m[f"{name}_oc"], m[f"{name}_daily"]


def account(months, scores=None, capital=CAPITAL, slip=H.SLIPPAGE, comm=H.COMMISSION, k=H.K, cap=H.SECTOR_CAP,
            sleeve=SLEEVE, absorber="spy", targets=None, min_ticket=MIN_TICKET, etf_min=ETF_MIN_TRADE):
    """One account over consecutive decision months (each month: entry open -> next month's entry open; the last month
    ends at its final close and is liquidated after costs). scores: per-month stock scores (None = no stock sleeve);
    absorber: ETF that takes the residual cash and funds stock-buy shortfalls (None = cash stays cash); targets:
    {etf: weight or list of per-month weights} of account equity, rebalanced at every review (|trade| >= etf_min)."""
    targets = dict(targets or {})
    cash, hold, etf = float(capital), {}, {}
    nb = ns = ne = 0
    com = slp = 0.0
    skipped_min = scaled = fund_sales = absorb_buys = 0
    viol = dict(negative_cash=0, positions_over_k=0, ticket_below_min=0, initial_weight_over_cap=0)
    turnover, nhold, alloc, posts, picks, path, tickets, sleeve_ret = [], [], [], [], [], [], [], []
    min_cash = float(capital)
    last = len(months) - 1
    for m_i, m in enumerate(months):
        traded = 0.0
        pos = {}
        if scores is not None:
            tgt = H.pick(m, scores[m_i], k, cap)
            pos = {m["ids"][i]: i for i in tgt}
            # (1) stock sells (frozen qr_h026.simulate order)
            for sid in [s for s in hold if s not in pos]:
                v = hold.pop(sid)
                cash += v * (1.0 - slip) - comm
                com += comm
                slp += v * slip
                traded += v
                ns += 1
        eq = cash + sum(hold.values())
        if etf:
            eq += sum(etf.values())
        # (2) stock buys: ticket = sleeve x equity / k; skipped when below the minimum; funded by cash, then by the
        # absorbing ETF; if still short, scaled down equally (frozen rule) and re-checked against the minimum
        new = [sid for sid in pos if sid not in hold]
        tickets.append(sleeve * eq / k if new else None)
        if new:
            n = len(new)
            t_val = sleeve * eq / k
            if min_ticket > 0 and t_val < min_ticket:
                skipped_min += n
                new = []
        if new:
            need = n * (t_val * (1.0 + slip) + comm)
            funded = False
            if need > cash and absorber is not None and etf.get(absorber, 0.0) > 0.0:
                x = (need - cash + comm) / (1.0 - slip)
                funded = x < etf[absorber]                  # the sale covers the whole shortfall
                x = min(x, etf[absorber])
                etf[absorber] = 0.0 if not funded else etf[absorber] - x
                cash += x * (1.0 - slip) - comm
                com += comm
                slp += x * slip
                traded += x
                ne += 1
                fund_sales += 1
            a = t_val if (need <= cash or funded) else max((cash - comm * n) / (n * (1.0 + slip)), 0.0)
            if a < t_val:
                scaled += 1
            if min_ticket > 0 and 0.0 < a < min_ticket:
                skipped_min += n
                a = 0.0
            if a > 0:
                for sid in new:
                    cash -= a * (1.0 + slip) + comm
                    com += comm
                    slp += a * slip
                    traded += a
                    hold[sid] = a
                    nb += 1
                if min_ticket > 0 and a < min_ticket:
                    viol["ticket_below_min"] += n
                if a > MAX_INIT_W * eq + 1e-9:
                    viol["initial_weight_over_cap"] += n
        # (3)-(4) target ETFs: sells first, then buys (a buy short of cash first sells the absorber)
        if targets:
            eq2 = cash + sum(hold.values()) + sum(etf.values())
            want = {}
            for name in sorted(targets):
                w = targets[name]
                w = float(w[m_i]) if isinstance(w, (list, tuple, np.ndarray)) else float(w)
                want[name] = w * eq2 - etf.get(name, 0.0)
            for name in sorted(want):
                d = want[name]
                if d < 0 and d <= -etf_min:
                    x = min(-d, etf.get(name, 0.0))
                    etf[name] = etf.get(name, 0.0) - x
                    cash += x * (1.0 - slip) - comm
                    com += comm
                    slp += x * slip
                    traded += x
                    ne += 1
            for name in sorted(want):
                d = want[name]
                if d > 0 and d >= etf_min:
                    need = d * (1.0 + slip) + comm
                    funded = False
                    if need > cash and absorber is not None and absorber != name and etf.get(absorber, 0.0) > 0.0:
                        x = (need - cash + comm) / (1.0 - slip)
                        funded = x < etf[absorber]
                        x = min(x, etf[absorber])
                        etf[absorber] = 0.0 if not funded else etf[absorber] - x
                        cash += x * (1.0 - slip) - comm
                        com += comm
                        slp += x * slip
                        traded += x
                        ne += 1
                    if need > cash and not funded:
                        d = max((cash - comm) / (1.0 + slip), 0.0)
                    if d > 0 and d >= etf_min:
                        cash -= d * (1.0 + slip) + comm
                        etf[name] = etf.get(name, 0.0) + d
                        com += comm
                        slp += d * slip
                        traded += d
                        ne += 1
        # (5) the absorbing ETF takes the residual cash (the buy is sized to use all of it)
        if absorber is not None and cash > comm and cash >= etf_min:
            y = (cash - comm) / (1.0 + slip)
            etf[absorber] = etf.get(absorber, 0.0) + y
            com += comm
            slp += y * slip
            traded += y
            ne += 1
            absorb_buys += 1
            cash = 0.0
        if cash < -1e-6:
            viol["negative_cash"] += 1
        if len(hold) > k:
            viol["positions_over_k"] += 1
        min_cash = min(min_cash, cash)
        eqp = cash + sum(hold.values()) + sum(etf.values())
        turnover.append(traded / eq if eq > 0 else 0.0)
        nhold.append(len(hold))
        stock = sum(hold.values())
        alloc.append(dict(stock=stock / eqp if eqp > 0 else 0.0, cash=cash / eqp if eqp > 0 else 1.0,
                          **{x: etf.get(x, 0.0) / eqp if eqp > 0 else 0.0 for x in ETFS}))
        posts.append(dict(idx=[pos[s] for s in hold], w=[hold[s] / eqp for s in hold] if eqp > 0 else [],
                          etf={x: v / eqp for x, v in etf.items()} if eqp > 0 else {}))
        picks.append(sorted(hold))
        idx = np.array([pos[s] for s in hold], dtype=np.int64)
        vals = np.array([hold[s] for s in hold], float)
        dm = m["daily"][:, idx] if idx.size else np.zeros((m["daily"].shape[0], 0))
        day_eq = cash + (vals * (1.0 + dm)).sum(1)
        for name in sorted(etf):
            day_eq = day_eq + etf[name] * (1.0 + _etf_fields(m, name)[2])
        path.append(day_eq)
        if m_i == last:
            end = vals * (1.0 + m["r_oc"][idx])
            sleeve_ret.append(float(end.sum() / vals.sum() - 1.0) if vals.size else None)
            alive = m["alive_end"][idx]
            cash += float(end[~alive].sum()) + float((end[alive] * (1.0 - slip)).sum()) - comm * int(alive.sum())
            com += comm * int(alive.sum())
            slp += float(end[alive].sum()) * slip
            ns += int(alive.sum())
            hold = {}
            for name in sorted(etf):
                v = etf[name] * (1.0 + _etf_fields(m, name)[1])
                if v > 0:
                    cash += v * (1.0 - slip) - comm
                    com += comm
                    slp += v * slip
                    ne += 1
            etf = {}
        else:
            nv = vals * (1.0 + m["r_oo"][idx])
            sleeve_ret.append(float(nv.sum() / vals.sum() - 1.0) if vals.size else None)
            alive = m["alive_next"][idx]
            hold = {s: float(v) for s, v, a in zip(list(hold), nv, alive) if a}
            cash += float(nv[~alive].sum())
            etf = {name: v * (1.0 + _etf_fields(m, name)[0]) for name, v in etf.items()}
    return dict(wealth=cash, buys=nb, sells=ns, etf_orders=ne, trades=nb + ns + ne, commissions=com, slippage=slp,
                turnover=turnover, holdings=nhold, alloc=alloc, posts=posts, picks=picks, skipped_min=skipped_min,
                scaled_buys=scaled, funding_sales=fund_sales, absorber_buys=absorb_buys, tickets=tickets,
                sleeve_ret=sleeve_ret, violations=viol, min_cash=min_cash, months=len(months),
                daily=np.concatenate(path) if path else np.zeros(0))


# ----------------------------------------------------------------------------------------------- ex-ante betas
def beta_at(tr, mkt, k, win=BETA_WIN, min_obs=BETA_MIN_OBS):
    """Trailing OLS beta of daily total returns over rows k - win .. k (data at or before row k only).
    Returns (beta or nan, paired observations)."""
    lo = k - win
    if lo < 0:
        return float("nan"), 0
    a, b = np.asarray(tr[lo:k + 1], float), np.asarray(mkt[lo:k + 1], float)
    with np.errstate(divide="ignore", invalid="ignore"):
        ra, rb = a[1:] / a[:-1] - 1.0, b[1:] / b[:-1] - 1.0
    ok = np.isfinite(ra) & np.isfinite(rb)
    n = int(ok.sum())
    if n < min_obs:
        return float("nan"), n
    x, y = rb[ok], ra[ok]
    vx = float(np.var(x, ddof=1))
    if not vx > 0:
        return float("nan"), n
    return float(np.cov(y, x, ddof=1)[0, 1] / vx), n


def blume(beta):
    """Blume-adjusted beta; an insufficient-data (nan) beta takes the market value 1.0 (protocol section 7)."""
    return BLUME[0] * float(beta) + BLUME[1] if math.isfinite(beta) else 1.0


def exante_weights(months, rec, etf_beta=None):
    """BM-X SPY weights: at review t, w_t = clip(sum post-trade stock weight x Blume beta + sum ETF weight x ETF beta,
    0, 1) of the system's planned holdings (cash = 0). Stock betas come from month['beta'] (Blume-adjusted, aligned
    with month['ids']); etf_beta: {etf: per-month list} (SPY = 1). Returns (weights, raw values, clamp counts)."""
    raw, w = [], []
    low = high = 0
    for m_i, (m, p) in enumerate(zip(months, rec["posts"])):
        b = float(sum(wi * m["beta"][i] for i, wi in zip(p["idx"], p["w"])))
        for name, wi in p["etf"].items():
            b += wi * (1.0 if name == "spy" else float(etf_beta[name][m_i]))
        raw.append(b)
        if b < 0:
            low += 1
        if b > 1:
            high += 1
        w.append(min(max(b, 0.0), 1.0))
    return w, raw, dict(below_0=low, above_1=high)


# ----------------------------------------------------------------------------------------------- metrics
def metrics(rec, days, capital, ref_daily):
    """Path metrics (frozen qr_h026.path_metrics), beta / capture against the reference path (frozen qr_h027.risk,
    monthly marks), strong-up capture (reference month >= +5%), yearly returns and month-end equity."""
    pm = H.path_metrics(rec["daily"], days, capital, rec["wealth"])
    rk = G.risk(rec["daily"], ref_daily, days, capital)
    rh, rs = rk.pop("rh"), rk.pop("rs")
    strong = rs >= 0.05
    rk["strong_up_capture"] = float(rh[strong].mean() / rs[strong].mean()) if strong.any() else float("nan")
    rk["strong_up_months"] = int(strong.sum())
    ends = G.month_ends(days)
    return dict(path=pm, risk=rk, years=H.year_returns(rec["daily"], days, capital),
                month_end=[float(capital)] + [float(rec["daily"][i]) for i in ends])


def summary(rec):
    """Costs, trades, allocations and rule checks of one account run (no prices or returns)."""
    al = rec["alloc"]

    def q(key):
        v = np.array([a[key] for a in al], float)
        return dict(min=float(v.min()), median=float(np.median(v)), mean=float(v.mean()), max=float(v.max()))
    return dict(wealth=rec["wealth"], buys=rec["buys"], sells=rec["sells"], etf_orders=rec["etf_orders"],
                trades=rec["trades"], commissions=rec["commissions"], slippage=rec["slippage"],
                turnover_monthly_mean=float(np.mean(rec["turnover"])), stock_positions_max=max(rec["holdings"]),
                stock_positions_mean=float(np.mean(rec["holdings"])), skipped_min=rec["skipped_min"],
                scaled_buys=rec["scaled_buys"], funding_sales=rec["funding_sales"], absorber_buys=rec["absorber_buys"],
                violations=dict(rec["violations"]), min_cash=rec["min_cash"],
                alloc={key: q(key) for key in ("stock", "cash") + ETFS})


def costs_check(slip=H.SLIPPAGE, comm=H.COMMISSION):
    """Two toy months, $10,000, sleeve 0.5, one stock (ticket 5,000 / k=1 -> sleeve x equity), SPY absorber; the
    ending wealth recomputed by hand."""
    ms = []
    for r_stock, r_spy in ((0.10, 0.02), (0.05, -0.01)):
        ms.append(dict(ids=["A"], sector=np.array([0]), open_ok=np.array([True]), r_oo=np.array([r_stock]),
                       r_oc=np.array([r_stock]), alive_next=np.array([True]), alive_end=np.array([True]),
                       daily=np.array([[r_stock]]), spy_oo=r_spy, spy_oc=r_spy, spy_daily=np.array([r_spy])))
    rec = account(ms, [np.array([1.0])] * 2, capital=10_000.0, slip=slip, comm=comm, k=1, sleeve=0.5,
                  min_ticket=0.0, etf_min=0.0)
    a = 0.5 * 10_000.0
    cash = 10_000.0 - (a * (1 + slip) + comm)
    spy = (cash - comm) / (1 + slip)
    st, spy = a * 1.10, spy * 1.02
    st *= 1.05
    spy *= 0.99
    hand = st * (1 - slip) - comm + spy * (1 - slip) - comm
    return dict(engine=rec["wealth"], by_hand=hand, ok=abs(rec["wealth"] - hand) < 1e-9)
