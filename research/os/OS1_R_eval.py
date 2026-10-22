"""H032 R1 / R2 (owner D282): offline evaluation, frozen with research/os/H032_R_protocol.md (pinned in qresearch.os1r)
BEFORE any run. Reads only the run's own records: experiments/<run>/result.json (runner status, integrity checks,
harness summary, LEAN version, the host's 'OS1R|' lines), fills.csv.gz (LEAN costs, turnover) and the canary's committed
lines (research/os/E807-02_os1_lines.txt). Applies validity I1-I5 + the fidelity pre-gate F, then gates O1-O7 and O9
(R1) and O8 (R2), and the non-gating report (protocol section 6).

    PYTHONPATH=src python research/os/OS1_R_eval.py E033-01 [--r2 E033-03]"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import wealth  # noqa: E402

START = "2012-07-31"
SUB_A_END = "2015-12-31"
CASH = 100000.0
FID_TERMINAL, FID_MONTH = 0.01, 0.005
CANARY_TOL = 0.02
SEEDS = dict(B2=(20261121, 20261122, 20261123, 20261124, 20261125), RND=(20261131, 20261132, 20261133, 20261134,
             20261135), BETA=(20261141, 20261142, 20261143, 20261144, 20261145))
BLOCKS = ((2012, 2013), (2014, 2015), (2016, 2017), (2018, 2019), (2020, 2021))


# ---------------------------------------------------------------- parsing
def parse(lines):
    out, eq = {}, {}
    for ln in lines:
        if not ln.startswith("OS1R|"):
            continue
        kind = ln.split("|", 2)[1]
        if kind == "eq":
            _, _, name, vals = ln.split("|", 3)
            eq[name] = np.array([float(v) for v in vals.split(",")])
        elif kind in ("dates", "npos", "maxw"):
            out[kind] = ln.split("|", 2)[2].split(",")
        else:
            out[kind] = json.loads(ln.split("|", 2)[2])
    return out, eq


def load_run(eid):
    from qresearch import results
    r = json.loads((ROOT / "experiments" / eid / "result.json").read_text())
    lines = results.lines_from_statistics(r["qc_statistics"]) if r.get("qc_statistics") else []
    out, eq = parse(lines)
    return r, out, eq, lines


# ---------------------------------------------------------------- statistics
def rets(e):
    e = np.asarray(e, float)
    return e[1:] / e[:-1] - 1.0


def cagr_eq(e):
    return wealth.cagr(rets(e))


def month_ends(dates):
    """Indices of the last close of every calendar month (the base 2012-07-31 included)."""
    idx = [i for i in range(len(dates)) if i + 1 == len(dates) or dates[i + 1][:7] != dates[i][:7]]
    return idx


def monthly(e, dates):
    m = month_ends(dates)
    v = np.asarray(e, float)[m]
    return v[1:] / v[:-1] - 1.0, [dates[i][:7] for i in m[1:]]


def max_dd(e):
    e = np.asarray(e, float)
    return float(np.min(e / np.maximum.accumulate(e) - 1.0))


def vol(r):
    return float(np.std(r, ddof=1) * math.sqrt(252))


def nw_ols(y, x, lags=2):
    """OLS y = a + b x; Newey-West (Bartlett) standard errors. -> (a, b, t_a, t_b)."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    X = np.column_stack([np.ones_like(x), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    u = y - X @ beta
    n = len(y)
    S = (X * u[:, None]).T @ (X * u[:, None])
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        G = (X[L:] * u[L:, None]).T @ (X[:-L] * u[:-L, None])
        S += w * (G + G.T)
    Q = np.linalg.inv(X.T @ X)
    V = Q @ S @ Q
    se = np.sqrt(np.diag(V))
    return float(beta[0]), float(beta[1]), float(beta[0] / se[0]), float(beta[1] / se[1])


def captures(rh, rs):
    up, dn = rs > 0, rs <= 0
    u = float(rh[up].mean() / rs[up].mean()) if up.any() else None
    d = float(rh[dn].mean() / rs[dn].mean()) if dn.any() else None
    cu = float((np.prod(1 + rh[up]) - 1) / (np.prod(1 + rs[up]) - 1)) if up.any() else None
    cd = float((np.prod(1 + rh[dn]) - 1) / (np.prod(1 + rs[dn]) - 1)) if dn.any() else None
    return dict(up=u, down=d, spread=(u - d) if u is not None and d is not None else None, up_compounded=cu,
                down_compounded=cd, up_months=int(up.sum()), down_months=int(dn.sum()))


def ew_series(ew):
    """[(end, r_all, r_vendor, ...)] -> (ends, r_all, r_vendor)."""
    ends = [x[0] for x in ew]
    return ends, np.array([x[1] if x[1] is not None else 0.0 for x in ew]), \
        np.array([x[2] if x[2] is not None else 0.0 for x in ew])


def growth(r):
    return float(np.prod(1 + np.asarray(r, float)))


# ---------------------------------------------------------------- validity
def validity(r, out, eq):
    res = {}
    failed = [c["check"] for c in r.get("integrity", []) if not c["ok"] and c.get("level", "fail") == "fail"]
    res["I1"] = dict(passed=r.get("status") == "completed" and not failed, status=r.get("status"), failed=failed)
    meta = out.get("meta", {})
    res["I2"] = dict(passed=meta.get("first_review_traded") == START and out.get("dates", [None])[0] == START,
                     first_review_traded=meta.get("first_review_traded"),
                     first_close=out.get("dates", [None])[0])
    ch = meta.get("checks", {})
    keys = ("identity_duplicates", "repaired_without_identity", "nsi_filing_on_or_after_t",
            "annual_filing_on_or_after_t", "pit_violations_ext")
    res["I3"] = dict(passed=bool(ch) and all(ch.get(k, 1) == 0 for k in keys), detail={k: ch.get(k) for k in keys})
    hs = r.get("harness_summary") or {}
    st = meta.get("stats", {})
    hk = ("timing_violations", "invalid", "negative_qty", "stale_open_orders")
    res["I4"] = dict(passed=bool(hs) and all(hs.get(k, 1) == 0 for k in hk) and st.get("lean_missing_symbol", 1) == 0,
                     detail=dict({k: hs.get(k) for k in hk}, lean_missing_symbol=st.get("lean_missing_symbol")))
    res["I5"] = canary_consistency(out)
    res["F"] = fidelity(out, eq)
    return res


def canary_consistency(out):
    p = ROOT / "research/os/E807-02_os1_lines.txt"
    can = {}
    for ln in p.read_text().splitlines():
        if ln.startswith("OS1|year|"):
            _, _, y, body = ln.split("|", 3)
            for c in json.loads(body)["reviews"]:
                can[c["t"]] = c
    worst, differing, n = 0.0, [], 0
    for c in out.get("reviews", []):
        if c["t"] < START:
            continue
        k = can.get(c["t"])
        n += 1
        if k is None:
            differing.append((c["t"], "missing in canary"))
            worst = max(worst, 1.0)
            continue
        for f in ("den", "cov", "passed"):
            if c[f] != k[f]:
                rel = abs(c[f] - k[f]) / max(k[f], 1)
                worst = max(worst, rel)
                differing.append((c["t"], f, c[f], k[f]))
    return dict(passed=n > 0 and worst <= CANARY_TOL, reviews=n, differing=differing[:50],
                n_differing=len(differing), worst_relative=worst)


def fidelity(out, eq):
    if "LEAN" not in eq or "B1" not in eq or "dates" not in out:
        return dict(passed=False, reason="missing series")
    lean, sh, dates = eq["LEAN"], eq["B1"], out["dates"]
    term = float(sh[-1] / lean[-1] - 1.0)
    ml, _ = monthly(lean, dates)
    ms, months = monthly(sh, dates)
    diff = np.abs(ms - ml)
    j = int(np.argmax(diff))
    return dict(passed=abs(term) <= FID_TERMINAL and float(diff.max()) <= FID_MONTH, terminal_relative=term,
                terminal_lean=float(lean[-1]), terminal_shadow=float(sh[-1]), max_month_abs=float(diff.max()),
                max_month_at=months[j], mean_month_abs=float(diff.mean()), months=len(months))


# ---------------------------------------------------------------- gates
def gates(out, eq):
    dates = out["dates"]
    lean = eq["LEAN"]
    spy = eq["SPY"] / eq["SPY"][0] * CASH
    r_l, r_s = rets(lean), rets(spy)
    years = len(r_l) / wealth.TRADING_DAYS
    c_l, c_s = wealth.cagr(r_l), wealth.cagr(r_s)
    g = {}
    g["O1"] = dict(passed=bool(lean[-1] > spy[-1] and c_l - c_s >= 0.010), wealth_lean=float(lean[-1]),
                   wealth_spy=float(spy[-1]), cagr_lean=c_l, cagr_spy=c_s, excess=c_l - c_s)
    d = np.log1p(r_l) - np.log1p(r_s)
    gg = wealth.TRADING_DAYS * float(d.mean())
    se = wealth.se_w2(d)
    g["O2"] = dict(passed=bool(gg / se >= 1.0), g=gg, se=se, ratio=gg / se)
    ml, months = monthly(lean, dates)
    ms, _ = monthly(spy, dates)
    cap = captures(ml, ms)
    g["O3"] = dict(passed=bool(cap["up"] is not None and cap["up"] >= 1.0 and cap["spread"] >= 0.05), **cap)
    a, b, ta, tb = nw_ols(ml, ms, 2)
    g["O4"] = dict(passed=bool(a > 0 and ta >= 1.0), alpha_monthly=a, alpha_annual=(1 + a) ** 12 - 1, beta=b,
                   t_alpha=ta, t_beta=tb)
    ends, ew_all, ew_v = ew_series(out["ew"])
    c_ew = growth(ew_all) ** (1 / years) - 1
    c_ewv = growth(ew_v) ** (1 / years) - 1
    cg = {name: cagr_eq(eq[name]) for name in eq if name not in ("LEAN", "SPY")}
    beat = {k: sum(1 for s in SEEDS[k] if c_l > cg[f"{k}_{s}"]) for k in SEEDS}
    g["O5"] = dict(passed=bool(c_l > c_ew and all(v >= 4 for v in beat.values())), cagr_ew=c_ew, beaten=beat,
                   cagr_controls={k: cg[k] for k in sorted(cg)})
    sub = {}
    ia = max(i for i, x in enumerate(dates) if x <= SUB_A_END)
    for lab, i0, i1 in (("A", 0, ia), ("B", ia, len(dates) - 1)):
        lg = math.log(lean[i1] / lean[i0])
        sg = math.log(spy[i1] / spy[i0])
        sel = [j for j, e in enumerate(ends) if (e <= SUB_A_END if lab == "A" else (e > SUB_A_END or e == "end"))]
        eg = math.log(growth(ew_all[sel]))
        sub[lab] = dict(vs_spy=lg - sg, vs_ew=lg - eg, from_=dates[i0], to=dates[i1])
    g["O6"] = dict(passed=all(v["vs_spy"] > 0 and v["vs_ew"] > 0 for v in sub.values()), **sub)
    yrs = np.array([int(x[:4]) for x in dates[1:]])
    tot = float(d.sum())
    blk = {f"{a_}-{b_}": float(d[(yrs >= a_) & (yrs <= b_)].sum()) for a_, b_ in BLOCKS}
    share = {k: (v / tot if tot > 0 else None) for k, v in blk.items()}
    g["O7"] = dict(passed=bool(tot > 0 and max(share.values()) <= 0.50), total=tot, blocks=blk, shares=share)
    vb1 = eq["VB1"]
    g["O9"] = dict(passed=bool(vb1[-1] > spy[-1] and cg["VB1"] > c_ewv), wealth_vb1=float(vb1[-1]),
                   cagr_vb1=cg["VB1"], cagr_ew_vendor=c_ewv)
    return g


def report(r, out, eq, eid):
    dates = out["dates"]
    spy = eq["SPY"] / eq["SPY"][0] * CASH
    books = {k: v for k, v in eq.items() if k != "SPY"}
    books["SPY"] = spy
    rs = rets(spy)
    tab = {}
    for k, e in books.items():
        r_ = rets(e)
        tab[k] = dict(wealth=float(e[-1]), cagr=wealth.cagr(r_), excess_vs_spy=wealth.cagr(r_) - wealth.cagr(rs),
                      max_dd=max_dd(e), vol=vol(r_), sharpe=wealth.sharpe(r_))
    ml, months = monthly(eq["LEAN"], dates)
    ms, _ = monthly(spy, dates)
    strong = ms >= 0.03
    lvl = np.asarray(spy)[month_ends(dates)]
    bull = np.array([i >= 12 and lvl[i] / lvl[i - 12] > 1 for i in range(len(lvl) - 1)])   # state at previous month-end
    reg = dict(strong_up=dict(months=int(strong.sum()), mean_excess=float((ml - ms)[strong].mean()) if strong.any() else None),
               bull_state=dict(months=int(bull.sum()), mean_excess=float((ml - ms)[bull].mean()) if bull.any() else None),
               not_bull=dict(months=int((~bull).sum()), mean_excess=float((ml - ms)[~bull].mean()) if (~bull).any() else None))
    diag = {}
    for k in ("B0", "MOM", "VB1"):
        mk, _ = monthly(eq[k], dates)
        diag[k] = dict(corr_monthly_excess_with_lean=float(np.corrcoef(ml - ms, mk - ms)[0, 1]))
    costs = {}
    cl = out.get("costs", [])
    if cl:
        names = out["meta"]["books"]
        for j, nme in enumerate(names):
            costs[nme] = dict(commission=float(sum(c[1][j] for c in cl)), slippage=float(sum(c[2][j] for c in cl)),
                              notional=float(sum(c[3][j] for c in cl)))
    lean_costs = lean_fill_costs(eid, r)
    npos = [int(x) for x in out.get("npos", [])]
    maxw = [float(x) for x in out.get("maxw", [])]
    return dict(table=tab, regimes=reg, diagnostics=diag, shadow_costs=costs, lean_costs=lean_costs,
                positions=dict(mean=float(np.mean(npos)) if npos else None, max=max(npos) if npos else None),
                max_position_weight=max(maxw) if maxw else None, years=out.get("years"),
                pnl_b1_shadow=out["meta"].get("pnl_b1_shadow"), engine=out["meta"].get("engine"),
                host_stats=out["meta"].get("stats"), lean_version=(r.get("provenance") or {}).get("lean_version"),
                harness=r.get("harness_summary"), restored_in_targets=[x.get("restored_in_target") for x in out.get("rlog", [])])


def lean_fill_costs(eid, r):
    p = ROOT / "experiments" / eid / "fills.csv.gz"
    if not p.exists():
        return None
    from qresearch import results
    f = results.read_csv_gz(p)
    cfg = json.loads((ROOT / "experiments" / eid / "config.json").read_text())
    slip = float(cfg["costs"]["slippage_bps"]) * float(cfg["costs"].get("slippage_stress_multiple", 1)) / 1e4
    cols = set(f.columns)
    fee = float(f["fee"].sum()) if "fee" in cols else None
    q = f["quantity"].abs() if "quantity" in cols else None
    px = f["price"] if "price" in cols else None
    out = dict(fills=int(len(f)), fees=fee)
    if q is not None and px is not None:
        notional = float((q * px).sum())
        out["notional"] = notional
        if slip > 0:
            out["slippage_est"] = float((q * px * slip / (1 + slip)).sum())
    return out


def evaluate(eid, r2=None):
    r, out, eq, lines = load_run(eid)
    v = validity(r, out, eq)
    valid = all(x["passed"] for x in v.values())
    res = dict(run=eid, validity=v, valid=valid)
    if not valid:
        res["outcome"] = "STOP — RUN NOT VALID (no strategy verdict)"
        return res
    g = gates(out, eq)
    res["gates"] = g
    res["report"] = report(r, out, eq, eid)
    r1_fail = [k for k in ("O1", "O2", "O3", "O4", "O5", "O6", "O7", "O9") if not g[k]["passed"]]
    res["r1_failed"] = r1_fail
    if r1_fail:
        res["outcome"] = "H032 NOT PROMISING (R1 fails " + ", ".join(r1_fail) + "); R2 not run"
        return res
    if r2 is None:
        res["outcome"] = "R1 PASSES O1-O7 and O9: R2 authorised (D282)"
        return res
    rr, o2, e2, _ = load_run(r2)
    v2 = validity(rr, o2, e2)
    res["r2_validity"] = v2
    if not all(x["passed"] for x in v2.values()):
        res["outcome"] = "STOP — R2 NOT VALID (no O8 verdict)"
        return res
    spy2 = e2["SPY"] / e2["SPY"][0] * CASH
    o8 = dict(passed=bool(e2["LEAN"][-1] > spy2[-1]), wealth_lean_r2=float(e2["LEAN"][-1]), wealth_spy=float(spy2[-1]),
              cagr_lean_r2=cagr_eq(e2["LEAN"]))
    res["gates"]["O8"] = o8
    res["outcome"] = ("EXPLORATORY PASS — UNIVERSE INCONCLUSIVE (RR6)" if o8["passed"]
                      else "H032 NOT PROMISING (R2 fails O8)")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--r2")
    a = ap.parse_args()
    res = evaluate(a.run, a.r2)
    name = a.run + (f"_{a.r2}" if a.r2 else "")
    (ROOT / f"research/os/OS1_R_result_{name}.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    r, _, _, lines = load_run(a.run)
    (ROOT / f"research/os/{a.run}_os1r_lines.txt").write_text("\n".join(ln for ln in lines if ln.startswith("OS1R|"))
                                                               + "\n")
    print(json.dumps(dict(outcome=res["outcome"], valid=res["valid"]), indent=1))


if __name__ == "__main__":
    main()
