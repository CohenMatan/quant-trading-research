"""H006X exit-policy comparison (owner D304; research/tt/h006_exit/H006X_spec.md): the frozen offline evaluation of
Control A (E006-04), Experiment B (E006-05) and SPY (E900-08). Written and pinned (qresearch.h006x) BEFORE any run;
it reads only the runs' committed equity, fills and trades.

    PYTHONPATH=src python research/tt/h006_exit/H006X_eval.py [A_ID B_ID SPY_ID]   -> H006X_result.json
"""
from __future__ import annotations

import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
OUT = HERE / "H006X_result.json"
RUNS = ("E006-04", "E006-05", "E900-08")
HALVES = (("2010-01-04", "2015-12-31"), ("2016-01-01", "2021-12-31"))
SLIPPAGE = 0.0010                              # 10 bps per side (config costs.slippage_bps)
NW_LAG = 6
REF_E006_01 = dict(cagr=0.121936, sharpe=0.880581, max_drawdown=-0.192902, n_trades=529, end="2017-12-29")
RR5_BIAS = {"2010-2015": 0.78, "2016-2021": 0.36}   # largest confirmed survivorship bias, points a year (RR5)


def _csv(eid, name):
    with gzip.open(ROOT / "experiments" / eid / f"{name}.csv.gz", "rt") as f:
        return pd.read_csv(f)


def load(eid):
    eq = _csv(eid, "equity")
    eq["date"] = pd.to_datetime(eq["date"])
    eq = eq.set_index("date")
    tr = _csv(eid, "trades") if (ROOT / "experiments" / eid / "trades.csv.gz").exists() else None
    fi = _csv(eid, "fills")
    return eq, tr, fi


def nw_t(x, lag=NW_LAG):
    x = np.asarray(x, float)
    n = x.size
    if n < 3:
        return float("nan")
    m = x.mean()
    e = x - m
    s = (e @ e) / n
    for k in range(1, lag + 1):
        s += 2 * (1 - k / (lag + 1)) * (e[k:] @ e[:-k]) / n
    return float(m / math.sqrt(s / n)) if s > 0 else float("nan")


def ols_alpha(y, x, lag=NW_LAG):
    """y = a + b x; Newey-West t of a."""
    X = np.column_stack([np.ones_like(x), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ b
    n = len(y)
    S = (X * e[:, None]).T @ (X * e[:, None]) / n
    for k in range(1, lag + 1):
        G = (X[k:] * e[k:, None]).T @ (X[:-k] * e[:-k, None]) / n
        S += (1 - k / (lag + 1)) * (G + G.T)
    Q = np.linalg.inv(X.T @ X / n)
    V = Q @ S @ Q / n
    return float(b[0]), float(b[1]), float(b[0] / math.sqrt(V[0, 0]))


def monthly(eq):
    e = eq["equity"]
    m = e.resample("ME").last()
    first = pd.Series([e.iloc[0]], index=[e.index[0] - pd.Timedelta(days=1)])
    return pd.concat([first, m]).pct_change().dropna()


def wealth_at(eq, day):
    e = eq["equity"]
    return float(e[e.index <= pd.Timestamp(day)].iloc[-1])


def cagr(eq):
    e = eq["equity"]
    yrs = (e.index[-1] - e.index[0]).days / 365.25
    return float((e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1)


def max_dd(eq):
    e = eq["equity"]
    return float((e / e.cummax() - 1).min())


def risk(eq):
    r = eq["equity"].pct_change().dropna()
    vol = float(r.std(ddof=1) * math.sqrt(252))
    return dict(vol=vol, sharpe=float(r.mean() / r.std(ddof=1) * math.sqrt(252)), max_drawdown=max_dd(eq))


def holding(tr, eq):
    sessions = eq.index
    pos = {d: i for i, d in enumerate(sessions)}
    last = sessions[-1]

    def nsess(a, b):
        a, b = pd.Timestamp(a), pd.Timestamp(b) if isinstance(b, str) and b else last
        ia = pos.get(a, int(np.searchsorted(sessions, a)))
        ib = pos.get(b, int(np.searchsorted(sessions, b)))
        return ib - ia

    closed = tr[tr["status"] == "closed"]
    opened = tr[tr["status"] != "closed"]
    h = np.array([nsess(a, b) for a, b in zip(closed["entry_date"], closed["exit_date"])], float)
    ho = np.array([nsess(a, "") for a in opened["entry_date"]], float)
    allh = np.concatenate([h, ho])
    return dict(closed=int(h.size), open_at_end=int(ho.size),
                mean=float(h.mean()), median=float(np.median(h)), p90=float(np.percentile(h, 90)),
                max_closed=float(h.max()), max_incl_open=float(allh.max()) if allh.size else None,
                share_gt_60=float((allh > 60).mean()), share_gt_126=float((allh > 126).mean()),
                share_gt_252=float((allh > 252).mean()))


def costs(fi, eq, tr):
    traded = float((fi["quantity"].abs() * fi["price"]).sum())
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    avg = float(eq["equity"].mean())
    comm = float(fi["fee"].sum())
    slip = SLIPPAGE * traded
    return dict(orders=int(len(fi)), round_trips=int((tr["status"] == "closed").sum()) if tr is not None else None,
                turnover_one_way_pa=traded / 2 / avg / yrs, commissions=comm, slippage_est=slip,
                cost_pct_avg_equity_pa=(comm + slip) / avg / yrs)


def concentration(tr, eq):
    closed = tr[tr["status"] == "closed"].copy()
    realised = float(closed["pnl"].sum())
    final_eq, final_cash = float(eq["equity"].iloc[-1]), float(eq["cash"].iloc[-1])
    open_cost = float(tr.loc[tr["status"] != "closed", "cost"].sum())
    unrealised = (final_eq - final_cash) - open_cost
    net = final_eq - float(eq["equity"].iloc[0])
    by = closed.groupby("symbol")["pnl"].sum().sort_values(ascending=False)
    top = lambda k: float(by.head(k).sum())   # noqa: E731
    closed["year"] = pd.to_datetime(closed["exit_date"]).dt.year
    yr = closed.groupby("year")["pnl"].sum()
    forced = closed[closed["exit_tag"].astype(str) == "forced"]
    long_held = closed[(pd.to_datetime(closed["exit_date"]) - pd.to_datetime(closed["entry_date"])).dt.days > 365]
    gains = float(closed.loc[closed["pnl"] > 0, "pnl"].sum())
    return dict(net_pnl=net, realised_pnl=realised, unrealised_open_at_end=unrealised,
                top1_share_of_net=top(1) / net if net else None, top5_share_of_net=top(5) / net if net else None,
                top10_share_of_net=top(10) / net if net else None,
                top5=[[s, float(v)] for s, v in by.head(5).items()],
                realised_pnl_by_exit_year={int(k): float(v) for k, v in yr.items()},
                forced_exits=int(len(forced)), forced_pnl=float(forced["pnl"].sum()),
                gains_on_holds_over_365d_share=float(long_held.loc[long_held["pnl"] > 0, "pnl"].sum()) / gains
                if gains else None)


def capture_beta(rs, rspy):
    j = pd.concat([rs, rspy], axis=1, join="inner").dropna()
    s, m = j.iloc[:, 0].to_numpy(), j.iloc[:, 1].to_numpy()
    up, dn = m > 0, m < 0
    a, b, t = ols_alpha(s, m)
    ex = s - m
    return dict(months=int(len(s)), up_capture=float(s[up].mean() / m[up].mean()),
                down_capture=float(s[dn].mean() / m[dn].mean()), beta=b, alpha_pa=a * 12, alpha_t=t,
                info_ratio=float(ex.mean() / ex.std(ddof=1) * math.sqrt(12)))


def yearly(eq):
    e = eq["equity"]
    ye = e.resample("YE").last()
    first = pd.Series([e.iloc[0]], index=[e.index[0] - pd.Timedelta(days=1)])
    r = pd.concat([first, ye]).pct_change().dropna()
    return {int(d.year): float(v) for d, v in r.items()}


def evaluate(a_id=RUNS[0], b_id=RUNS[1], spy_id=RUNS[2]):
    (ea, ta, fa), (eb, tb, fb), (es, _, fs) = load(a_id), load(b_id), load(spy_id)
    if not (ea.index.equals(eb.index) and ea.index.equals(es.index)):
        raise SystemExit("the three runs must share the session calendar")
    W = {k: float(e["equity"].iloc[-1]) for k, e in (("A", ea), ("B", eb), ("SPY", es))}
    C = {k: cagr(e) for k, e in (("A", ea), ("B", eb), ("SPY", es))}
    ma, mb, ms = monthly(ea), monthly(eb), monthly(es)
    d = np.log1p(mb) - np.log1p(ma)
    halves = {}
    for lo, hi in HALVES:
        key = f"{lo[:4]}-{hi[:4]}"
        w0 = {k: (wealth_at(e, pd.Timestamp(lo) - pd.Timedelta(days=1)) if lo > "2010-01-04" else float(e["equity"].iloc[0]))
              for k, e in (("A", ea), ("B", eb), ("SPY", es))}
        w1 = {k: wealth_at(e, hi) for k, e in (("A", ea), ("B", eb), ("SPY", es))}
        lw = {k: math.log(w1[k] / w0[k]) for k in w0}
        halves[key] = dict(log_wealth=lw, B_minus_A=lw["B"] - lw["A"], B_minus_SPY=lw["B"] - lw["SPY"],
                           A_minus_SPY=lw["A"] - lw["SPY"],
                           cagr_B_minus_SPY=math.exp(lw["B"] / 6) - math.exp(lw["SPY"] / 6))
    ya, yb, ysp = yearly(ea), yearly(eb), yearly(es)
    ydiff = {y: math.log1p(yb[y]) - math.log1p(ya[y]) for y in ya}
    pos = [v for v in ydiff.values() if v > 0]
    v3_share = max(pos) / sum(pos) if pos else None
    cap = {k: capture_beta(m, ms) for k, m in (("A", ma), ("B", mb))}
    conc = {k: concentration(t, e) for k, t, e in (("A", ta, ea), ("B", tb, eb))}
    res = dict(
        runs=dict(A=a_id, B=b_id, SPY=spy_id), dates=[str(ea.index[0].date()), str(ea.index[-1].date())],
        terminal_wealth=W, cagr=C, ratio=dict(B_over_A=W["B"] / W["A"], B_over_SPY=W["B"] / W["SPY"],
                                              A_over_SPY=W["A"] / W["SPY"]),
        paired_B_minus_A=dict(months=int(d.size), mean_monthly_log=float(d.mean()), nw_t=nw_t(d),
                              yearly_log_diff=ydiff, largest_positive_year_share=v3_share),
        halves=halves, yearly_returns=dict(A=ya, B=yb, SPY=ysp), capture_beta=cap,
        risk={k: risk(e) for k, e in (("A", ea), ("B", eb), ("SPY", es))},
        holding={k: holding(t, e) for k, t, e in (("A", ta, ea), ("B", tb, eb))},
        costs={k: costs(f, e, t) for k, f, e, t in (("A", fa, ea, ta), ("B", fb, eb, tb))},
        concentration=conc)
    # drift diagnostic: A's 2010-01-04 .. 2017-12-29 sub-path vs E006-01 (old dataset; not a gate)
    sub = ea[ea.index <= pd.Timestamp(REF_E006_01["end"])]
    res["drift_vs_E006_01"] = dict(reference=REF_E006_01, cagr=cagr(sub), sharpe=risk(sub)["sharpe"],
                                   max_drawdown=max_dd(sub),
                                   trades_entered=int((pd.to_datetime(ta["entry_date"]) <= REF_E006_01["end"]).sum()))
    # universe sensitivity: excess over SPY per half vs the largest confirmed RR5 bias
    res["universe_sensitivity"] = {k: dict(cagr_B_minus_SPY_pts=100 * h["cagr_B_minus_SPY"], rr5_bias_pts=RR5_BIAS[k],
                                           survives_bias=bool(100 * h["cagr_B_minus_SPY"] > RR5_BIAS[k]))
                                   for k, h in halves.items()}
    # pre-declared answers (spec section 5)
    v1 = W["B"] / W["A"] >= 1.10
    v2 = all(h["B_minus_A"] > 0 for h in halves.values())
    v3 = v3_share is not None and v3_share <= 0.50
    q1 = "YES" if (v1 and v2 and v3) else ("NO" if W["B"] <= W["A"] else "NOT MEANINGFUL")
    q2 = "YES" if W["B"] > W["SPY"] else "NO"
    top5 = conc["B"]["top5_share_of_net"]
    r = dict(R1=q1 == "YES" and q2 == "YES", R2=100 * (C["B"] - C["SPY"]) >= 1.0,
             R3=all(h["B_minus_SPY"] > 0 for h in halves.values()), R4=cap["B"]["alpha_pa"] > 0,
             R5=top5 is not None and top5 < 0.50)
    res["answers"] = dict(V1=v1, V2=v2, V3=v3, Q1_time_limit_removal_adds_meaningful_value=q1,
                          Q2_B_beats_SPY=q2, A_beats_SPY="YES" if W["A"] > W["SPY"] else "NO", R=r,
                          Q3_robust_enough_for_independent_evidence="YES" if all(r.values()) else "NO",
                          recommendation="seek independent evidence" if all(r.values()) else "close")
    return res


if __name__ == "__main__":
    ids = sys.argv[1:] or list(RUNS)
    out = evaluate(*ids)
    OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(out["answers"], indent=1))
