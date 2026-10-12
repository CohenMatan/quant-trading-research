"""P13-CP2 (owner D221): H028 2015-2016 descriptive post-mortem -> P13_CP2_postmortem.json.

DESCRIPTIVE ONLY. Offline, deterministic transformations of committed artifacts; no QuantConnect run, no new data, no
parameter / feature / gate change, no fix search. H028 stays REJECTED.

Sources (committed):
  * experiments/E030-05/messages.txt  -> QRHR block (the ONE real H028 run): daily equity of H028 / H027 / LV15 / SPY,
    session days, decision review days, H028 and LV15 monthly turnover / holdings / cash share, the exact replay's
    per-month turnover / orders / commission / slippage for H028 and H027, the 2015 score rank correlations and Top-15
    overlaps (H027 vs H028), coefficients (H028 and H027), the LOWVOL-factor series (lowest-LOWVOL quintile minus
    population, per decision period);
  * research/phase13/cp1/P13_CP1_result.json (gates, yearly returns), research/phase12/cp1/P12_CP1_result.json.
NOT in any committed artifact: per-stock holdings, scores, feature values, sectors or stock returns for H028 / LV15 / H027
(the hosts export aggregates only) -> every holdings / feature / sector / stock item is NOT AVAILABLE FROM COMMITTED
ARTIFACTS.

Definitions (fixed before any output was computed):
  * monthly returns: calendar-month close marks (last session of each month), the starting capital first (P11-CP2 /
    qr_h027.risk definitions); relative month m: L_m = ln((1 + r_H028) / (1 + r_LV15)) (sums exactly to the yearly
    log-relative because year ends are month ends); "approximately equal" month: |L_m| < 0.0025.
  * concentration: G = sum of L_m over the window (net gap, negative); share of the k worst months = (sum of the k most
    negative L_m) / G.
  * per-year risk: volatility = std of daily returns in the year x sqrt(252); MaxDD from the prior year-end mark through
    the year; beta / up-capture / down-capture from the 12 monthly returns vs SPY (P11-CP2 formulas).
  * costs: H028 / H027 exact per decision month (replay); LV15 commissions per month are NOT exported (only the 2015-2021
    total), LV15 slippage per month is ESTIMATED as 0.001 x turnover x the prior month-end equity mark. The cost gap
    (H028 cost - LV15 cost) is therefore reported as an UPPER BOUND (H028 cost - LV15 estimated slippage), as a share of
    the year-start equity.
  * LOWVOL-override diagnostic (owner item 21), coefficient-based because holdings are not available:
    override capacity R(year) = sum_{f != LOWVOL} |beta_f| / |beta_LOWVOL| (features lie in [-1, +1], so R > 1 means the
    other ten features together can move a stock's score by more than the whole LOWVOL range). The realised override
    FREQUENCY (how many H028 holdings displaced an LV15 stock) needs holdings: NOT AVAILABLE.
  * feature emphasis: w_f = beta_f / sum |beta| per model year; model similarity = cosine of beta vectors.
  * classification (owner item 28), per window W (2015, 2016, 2015-2016) with share_behind = months L_m < 0 / months:
      C (mostly transaction cost) if the cost-gap upper bound >= 50% of |G|;
      else A (concentrated) if the 3 worst months >= 75% of G and share_behind <= 0.5;
      else B (broad) if share_behind >= 0.6 and the 3 worst months < 75% of G;
      else E (mixed). D (sector allocation) is NOT DETERMINABLE (no sector P&L).
  * final conclusion (owner item 34): 'C' if the 2015 and 2016 per-year labels differ OR their dominant market side
    differs (side = SPY-up or SPY-down months with the more negative summed L_m); otherwise 'A' / 'B' if the 2015-2016
    label is A / B; otherwise 'D'. Mechanism-level causes (stocks, features, sectors) are NOT AVAILABLE either way.

    PYTHONPATH=src python research/phase13/cp2/P13_CP2_postmortem.py
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402
import qr_h026 as H  # noqa: E402
import qr_p7_export as E  # noqa: E402

EXP = "E030-05"
EQUAL_EPS = 0.0025
YEARS = (2015, 2016, 2017)
SERIES = ("h028", "lv15", "spy", "h027")
CAP = H.CAPITAL


def load():
    ls = lines(EXP)
    st = json.loads(joined(ls, "QRG"))
    blob = joined(ls, "QRHR")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"]
    return json.loads(E.unpack(blob)), hashlib.sha256(blob.encode()).hexdigest()


def ds(d):
    return str(np.datetime64(int(d), "D"))


def month_marks(o):
    days = np.asarray(o["days"], float)
    lab = np.array([ds(d)[:7] for d in days])
    ends = [i for i in range(len(days)) if i == len(days) - 1 or lab[i + 1] != lab[i]]
    marks = {n: np.r_[CAP, np.asarray(o[f"daily_{n}"], float)[ends]] for n in SERIES}
    rets = {n: marks[n][1:] / marks[n][:-1] - 1.0 for n in SERIES}
    return [lab[i] for i in ends], rets, marks, ends, days, lab


def year_risk(o, days, lab, mlab, rets, year):
    y = str(year)
    idx = np.flatnonzero(np.array([l[:4] == y for l in lab]))
    out = {}
    mi = [k for k, l in enumerate(mlab) if l[:4] == y]
    rs = rets["spy"][mi]
    for n in SERIES:
        eq = np.asarray(o[f"daily_{n}"], float)
        prev = eq[idx[0] - 1] if idx[0] > 0 else CAP
        path = np.r_[prev, eq[idx]]
        dr = path[1:] / path[:-1] - 1.0
        rh = rets[n][mi]
        up, dn = rs > 0, rs < 0
        out[n] = dict(ret=float(path[-1] / path[0] - 1.0), vol=float(dr.std(ddof=1) * math.sqrt(252)),
                      maxdd=H.max_drawdown(path),
                      beta=float(np.cov(rh, rs, ddof=1)[0, 1] / np.var(rs, ddof=1)),
                      up_capture=float(rh[up].mean() / rs[up].mean()) if up.any() else None,
                      down_capture=float(rh[dn].mean() / rs[dn].mean()) if dn.any() else None,
                      return_per_vol=float((path[-1] / path[0] - 1.0) / (dr.std(ddof=1) * math.sqrt(252))))
    return out


def classify(L, months_idx, cost_gap_ub):
    Lw = np.array([L[k] for k in months_idx])
    G = float(Lw.sum())
    neg = np.sort(Lw[Lw < 0])
    top = {k: float(neg[:k].sum() / G) if G < 0 and neg.size else None for k in (1, 3, 5)}
    behind = int((Lw < -EQUAL_EPS).sum())
    ahead = int((Lw > EQUAL_EPS).sum())
    equal = int(Lw.size - behind - ahead)
    share_behind = float((Lw < 0).mean())
    cost_share = abs(cost_gap_ub) / abs(G) if G != 0 and cost_gap_ub is not None else None
    if cost_share is not None and cost_share >= 0.5:
        lab = "C"
    elif top[3] is not None and top[3] >= 0.75 and share_behind <= 0.5:
        lab = "A"
    elif share_behind >= 0.6 and (top[3] is None or top[3] < 0.75):
        lab = "B"
    else:
        lab = "E"
    return dict(net_gap_log=G, months=int(Lw.size), share_worst_1=top[1], share_worst_3=top[3], share_worst_5=top[5],
                gross_negative=float(Lw[Lw < 0].sum()), gross_positive=float(Lw[Lw > 0].sum()),
                months_h028_ahead=ahead, months_h028_behind=behind, months_approx_equal=equal,
                share_months_behind=share_behind, cost_gap_upper_bound_share=cost_share, label=lab)


def main():
    o, blob_sha = load()
    mlab, rets, marks, ends, days, lab = month_marks(o)
    L = np.log((1 + rets["h028"]) / (1 + rets["lv15"]))
    win = {str(y): [k for k, l in enumerate(mlab) if l[:4] == str(y)] for y in YEARS}
    win["2015-2016"] = win["2015"] + win["2016"]
    # 6. yearly and compounded comparison (year-end marks)
    yr = {}
    for y in YEARS:
        r = {n: float(np.prod([1 + rets[n][k] for k in win[str(y)]]) - 1) for n in SERIES}
        yr[str(y)] = dict(r, h028_minus_lv15=r["h028"] - r["lv15"], h028_minus_spy=r["h028"] - r["spy"],
                          lv15_minus_spy=r["lv15"] - r["spy"], log_h028_vs_lv15=math.log((1 + r["h028"]) / (1 + r["lv15"])),
                          log_h028_vs_spy=math.log((1 + r["h028"]) / (1 + r["spy"])),
                          log_lv15_vs_spy=math.log((1 + r["lv15"]) / (1 + r["spy"])))
    comp = {}
    for name, ys in (("2015", (2015,)), ("2016", (2016,)), ("2015-2016", (2015, 2016)), ("2015-2017", (2015, 2016, 2017))):
        g = {n: float(np.prod([1 + yr[str(y)][n] for y in ys])) for n in SERIES}
        comp[name] = dict(growth=g, wealth_ratio_h028_lv15=g["h028"] / g["lv15"], wealth_ratio_h028_spy=g["h028"] / g["spy"],
                          wealth_ratio_lv15_spy=g["lv15"] / g["spy"], log_h028_vs_lv15=math.log(g["h028"] / g["lv15"]),
                          log_h028_vs_spy=math.log(g["h028"] / g["spy"]), log_h027_vs_lv15=math.log(g["h027"] / g["lv15"]))
    # 7. monthly table 2015-2016 (+ 2017 context)
    monthly = [dict(month=mlab[k], h028=float(rets["h028"][k]), lv15=float(rets["lv15"][k]), spy=float(rets["spy"][k]),
                    h027=float(rets["h027"][k]), h028_minus_lv15=float(rets["h028"][k] - rets["lv15"][k]),
                    h028_minus_spy=float(rets["h028"][k] - rets["spy"][k]), log_h028_vs_lv15=float(L[k]))
               for y in YEARS for k in win[str(y)]]
    m1516 = [m for m in monthly if m["month"][:4] in ("2015", "2016")]
    ranked = sorted(m1516, key=lambda m: m["log_h028_vs_lv15"])
    # turnover / costs per calendar year (decision review month + 1 = holding month)
    rev = o["months"]
    hold_month = []
    for d in rev:
        y, m = int(d[:4]), int(d[5:7])
        hold_month.append(f"{y + (m == 12)}-{(m % 12) + 1:02d}")
    rp = {n: o["replay_months"][n] for n in ("h028", "h027")}
    lv_t = o["lv15_trades"]["turnover"]
    mark_of = {l: marks["lv15"][k + 1] for k, l in enumerate(mlab)}
    costs = {}
    for y in YEARS:
        ii = [i for i, hm in enumerate(hold_month) if hm[:4] == str(y)]
        start = {n: marks[n][win[str(y)][0]] for n in SERIES}            # prior year-end mark
        c = {}
        for n in ("h028", "h027"):
            com = sum(rp[n][i][3] for i in ii)
            slp = sum(rp[n][i][4] for i in ii)
            c[n] = dict(turnover=float(sum(rp[n][i][1] for i in ii)), orders=int(sum(rp[n][i][2] for i in ii)),
                        commission=float(com), slippage=float(slp), cost_share_of_start_equity=float((com + slp) / start[n]))
        est = 0.0
        for i in ii:
            prev = f"{int(hold_month[i][:4]) - (hold_month[i][5:] == '01')}-{(int(hold_month[i][5:]) - 2) % 12 + 1:02d}"
            eq0 = mark_of.get(prev, CAP)
            est += 0.001 * lv_t[i] * eq0
        c["lv15"] = dict(turnover=float(sum(lv_t[i] for i in ii)), orders="NOT AVAILABLE FROM COMMITTED ARTIFACTS",
                         commission="NOT AVAILABLE FROM COMMITTED ARTIFACTS (2015-2021 total only)",
                         slippage_estimate=float(est), slippage_estimate_share_of_start_equity=float(est / start["lv15"]))
        c["cost_gap_upper_bound_share"] = c["h028"]["cost_share_of_start_equity"] - c["lv15"]["slippage_estimate_share_of_start_equity"]
        c["net_gap_log"] = yr[str(y)]["log_h028_vs_lv15"]
        c["gross_gap_log_lower_bound"] = c["net_gap_log"] + c["cost_gap_upper_bound_share"]
        costs[str(y)] = c
    costs["lv15_commissions_2015_2021_total"] = o["lv15_trades"]["commissions"]
    costs["lv15_trades_2015_2021_total"] = o["lv15_trades"]["trades"]
    # 8 / 28. concentration and classification
    conc = {}
    for w in ("2015", "2016", "2015-2016"):
        ys = (2015, 2016) if w == "2015-2016" else (int(w),)
        cg = sum(costs[str(y)]["cost_gap_upper_bound_share"] for y in ys)
        conc[w] = classify(L, win[w], cg)
    # 24. SPY up / down months
    updown = {}
    for w in ("2015", "2016", "2017", "2015-2016"):
        ks = win[w] if w in win else win[w]
        rs = rets["spy"][ks]
        Lw, Dw = L[ks], (rets["h028"] - rets["lv15"])[ks]
        side = {}
        for nm, msk in (("spy_up", rs > 0), ("spy_down", rs < 0)):
            side[nm] = dict(months=int(msk.sum()), mean_h028_minus_lv15=float(Dw[msk].mean()) if msk.any() else None,
                            sum_log_h028_vs_lv15=float(Lw[msk].sum()), mean_h028=float(rets["h028"][ks][msk].mean()) if msk.any() else None,
                            mean_lv15=float(rets["lv15"][ks][msk].mean()) if msk.any() else None,
                            mean_spy=float(rs[msk].mean()) if msk.any() else None)
        side["dominant_side_of_loss"] = min(("spy_up", "spy_down"), key=lambda s: side[s]["sum_log_h028_vs_lv15"])
        updown[w] = side
    # 23. per-year risk
    risk = {str(y): year_risk(o, days, lab, mlab, rets, y) for y in YEARS}
    # LOWVOL-factor environment (decision periods mapped to holding months)
    fac = o["diagnostics"]["lowvol_factor_regression"]["factor"]
    dep = o["diagnostics"]["lowvol_factor_regression"]["dependent"]
    env = {}
    for y in range(2015, 2022):
        ii = [i for i, hm in enumerate(hold_month) if hm[:4] == str(y)]
        f = np.array([fac[i] for i in ii], float)
        env[str(y)] = dict(months=len(ii), sum=float(np.nansum(f)), mean=float(np.nanmean(f)),
                           months_positive=int((f > 0).sum()), h028_minus_spy_period_sum=float(np.nansum([dep[i] for i in ii])))
    # coefficients: emphasis, similarity, override capacity
    feats = list(H.FEATURES)
    models = {"2015_H027_lambda_0.01": o["coefficients_h027"]["2015"]["beta"]}
    for y in range(2015, 2022):
        models[f"{y}_H028_lambda_100"] = o["coefficients"][str(y)]["beta"]
    lv = feats.index("LOWVOL")
    coef = {}
    for k, b in models.items():
        b = np.asarray(b, float)
        s = np.abs(b).sum()
        coef[k] = dict(beta=dict(zip(feats, b.tolist())), norm=float(np.linalg.norm(b)),
                       emphasis=dict(zip(feats, (b / s).tolist())),
                       override_capacity_R=float((s - abs(b[lv])) / abs(b[lv])),
                       score_range_by_feature=dict(zip(feats, (2 * np.abs(b)).tolist())))
    names = list(models)
    cos = {f"{a}|{b}": float(np.dot(models[a], models[b]) / (np.linalg.norm(models[a]) * np.linalg.norm(models[b])))
           for i, a in enumerate(names) for b in names[i + 1:]}
    # 10 / 25. 2015 H027 vs H028 (available series)
    y15 = dict(score_spearman=o["y2015"]["score_spearman"], held_overlap=o["y2015"]["held_overlap"],
               months=o["y2015"]["months"], spearman_mean=float(np.mean(o["y2015"]["score_spearman"])),
               spearman_range=[float(min(o["y2015"]["score_spearman"])), float(max(o["y2015"]["score_spearman"]))],
               overlap_mean=float(np.mean(o["y2015"]["held_overlap"])),
               overlap_range=[int(min(o["y2015"]["held_overlap"])), int(max(o["y2015"]["held_overlap"]))])
    na = "NOT AVAILABLE FROM COMMITTED ARTIFACTS"
    unavailable = {k: na for k in (
        "h028_vs_lv15_overlap", "h027_vs_lv15_overlap", "feature_profiles", "lowvol_percentile_profiles",
        "score_contribution_profiles_realised", "sector_exposures_by_year", "sector_attribution", "stock_contributors",
        "lv15_score_ranks", "h028_only_holdings", "lowvol_override_frequency_realised", "lv15_orders_and_commissions_by_year")}
    # final conclusion (rule fixed in the docstring)
    l15, l16 = conc["2015"]["label"], conc["2016"]["label"]
    s15, s16 = updown["2015"]["dominant_side_of_loss"], updown["2016"]["dominant_side_of_loss"]
    if l15 != l16 or s15 != s16:
        final = "C"
    elif conc["2015-2016"]["label"] in ("A", "B"):
        final = conc["2015-2016"]["label"]
    else:
        final = "D"
    out = dict(source=dict(experiment=EXP, qrhr_blob_sha256=blob_sha, p13_cp1_result="research/phase13/cp1/P13_CP1_result.json",
                           p12_cp1_result="research/phase12/cp1/P12_CP1_result.json"),
               yearly=yr, compounded=comp, monthly=monthly, worst_relative_months=ranked[:5],
               best_relative_months=ranked[::-1][:5], concentration=conc, updown=updown, risk=risk, costs=costs,
               lowvol_factor_environment=env, coefficients=coef, model_cosine_similarity=cos, y2015_h027_vs_h028=y15,
               unavailable=unavailable, final_conclusion=final,
               rule_inputs=dict(label_2015=l15, label_2016=l16, side_2015=s15, side_2016=s16,
                                label_2015_2016=conc["2015-2016"]["label"]))
    path = HERE / "P13_CP2_postmortem.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps(dict(yearly=yr, compounded=comp, concentration=conc, updown=updown, final=final,
                          rule_inputs=out["rule_inputs"]), indent=1, default=float))
    print("sha256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
