"""P11-CP2 (owner D211): descriptive post-mortem of H026 from COMMITTED artifacts only -> P11_CP2_postmortem.json.

Inputs (all committed before this script existed): the E028-05 real-run blocks (QRW statistics + QRWR result: daily H026 / SPY
equity marks, yearly returns, coefficients, inner-validation objectives, monthly turnover / holdings / cash share, sector
counts, non-gating diagnostics), the 5,000 null-world rows of E028-02 / E028-03 (QRWN), the Data v2.1 audit summary and the
H024 canary's 2011-2017 feature-correlation matrix. Nothing is rerun, refitted or re-simulated; no QuantConnect call; no
2022+ data. Items needing information E028-05 did not export (security-level holdings, trades, scores, selected-stock
feature percentiles, sector-by-period P&L) are recorded as NOT COMPUTED.

    PYTHONPATH=src python research/phase11/cp2/P11_CP2_postmortem.py
"""
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
from qresearch import p11h026 as P  # noqa: E402

NOT_EXPORTED = ("NOT COMPUTED — NOT IN THE COMMITTED E028-05 ARTIFACTS (security-level holdings, trades, scores and "
                "selected-stock feature percentiles were not exported); obtaining it would need a new QuantConnect export "
                "run of the frozen H026 pipeline, which D211 does not authorise")
COUNTERFACTUAL = "NOT COMPUTED — WOULD REQUIRE A NEW COUNTERFACTUAL RUN"
FEATURES = list(H.FEATURES)


def q(x, ps=(10, 25, 50, 75, 90)):
    x = np.asarray(x, float)
    return {f"p{p}": float(np.percentile(x, p)) for p in ps}


def day_str(d):
    return str(np.datetime64(int(d), "D"))


def load_real():
    ls = lines(P.REAL)
    st = json.loads(joined(ls, "QRW"))
    return st, json.loads(E.unpack(joined(ls, "QRWR")))


def load_null():
    W = []
    fields = None
    for e in P.NULL_RUNS:
        b = json.loads(E.unpack(joined(lines(e), "QRWN")))
        fields = b["fields"]
        W += b["worlds"]
    return fields, sorted(W, key=lambda w: w[0])


def capm(r, m):
    """Descriptive OLS of monthly H026 returns on SPY returns (rf = 0): alpha, beta, alpha t (iid), R^2."""
    X = np.c_[np.ones_like(m), m]
    b, *_ = np.linalg.lstsq(X, r, rcond=None)
    e = r - X @ b
    s2 = float(e @ e) / (len(r) - 2)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return dict(capm_alpha_monthly=float(b[0]), capm_alpha_annualised=float(b[0] * 12), capm_beta=float(b[1]),
                capm_alpha_t_iid=float(b[0] / se[0]), capm_r2=float(1 - (e @ e) / ((r - r.mean()) @ (r - r.mean()))))


def path_section(o):
    cap = float(H.CAPITAL)
    days = np.asarray(o["days"], float)
    eh, es = np.asarray(o["daily_h026"], float), np.asarray(o["daily_spy"], float)
    dates = [day_str(d) for d in days]
    yrs = np.array([int(d[:4]) for d in dates])
    mon = np.array([d[:7] for d in dates])
    # month-end marks (last session of each calendar month), with the starting capital as month 0
    ends = [i for i in range(len(days)) if i == len(days) - 1 or mon[i + 1] != mon[i]]
    mh = np.r_[cap, eh[ends]]
    ms = np.r_[cap, es[ends]]
    rel_m = mh / ms
    monthly = [dict(month=mon[i], h026=float(eh[i]), spy=float(es[i]), relative_wealth=float(eh[i] / es[i]))
               for i in ends]
    lm = np.diff(np.log(rel_m))                                   # monthly log-relative contributions
    # annual
    yh = {int(k): v for k, v in o["years_h026"].items()}
    ys = {int(k): v for k, v in o["years_spy"].items()}
    annual, start_rel = {}, 1.0
    for y in H.OUTER_YEARS:
        L = math.log((1 + yh[y]) / (1 + ys[y]))
        end_rel = start_rel * math.exp(L)
        idx = np.flatnonzero(yrs == y)
        prev_h = cap if y == H.OUTER_YEARS[0] else eh[np.flatnonzero(yrs == y - 1)[-1]]
        prev_s = cap if y == H.OUTER_YEARS[0] else es[np.flatnonzero(yrs == y - 1)[-1]]
        rh = np.diff(np.r_[prev_h, eh[idx]]) / np.r_[prev_h, eh[idx]][:-1]
        rs = np.diff(np.r_[prev_s, es[idx]]) / np.r_[prev_s, es[idx]][:-1]
        annual[str(y)] = dict(h026=yh[y], spy=ys[y], relative_arithmetic=yh[y] - ys[y], relative_log=L,
                              start_relative_wealth=start_rel, end_relative_wealth=end_rel,
                              vol_h026=float(rh.std(ddof=1) * math.sqrt(252)), vol_spy=float(rs.std(ddof=1) * math.sqrt(252)),
                              maxdd_h026=H.max_drawdown(np.r_[prev_h, eh[idx]]),
                              maxdd_spy=H.max_drawdown(np.r_[prev_s, es[idx]]), beat_spy=L > 0)
        start_rel = end_rel
    S = math.log(o["h026"]["wealth"] / o["spy"]["wealth"])
    liq = S - sum(a["relative_log"] for a in annual.values())     # final liquidation (closing costs) term
    contrib = {y: a["relative_log"] for y, a in annual.items()}
    contrib["final_liquidation_costs"] = liq
    assert abs(sum(contrib.values()) - S) < 1e-12
    # concentration
    pos_m = float(lm[lm > 0].sum())
    srt = np.sort(lm)[::-1]

    def best_window(k, worst=False):
        c = np.convolve(lm, np.ones(k), "valid")
        i = int(np.argmin(c) if worst else np.argmax(c))
        return dict(value=float(c[i]), start=monthly[i]["month"], end=monthly[i + k - 1]["month"])
    Ly = np.array([annual[str(y)]["relative_log"] for y in H.OUTER_YEARS])
    pos_y = float(Ly[Ly > 0].sum())
    conc = dict(
        S_WEALTH=S, sum_positive_monthly=pos_m, sum_negative_monthly=float(lm[lm < 0].sum()),
        months_positive=int((lm > 0).sum()), months=int(lm.size),
        best_month=dict(value=float(srt[0]), month=monthly[int(np.argmax(lm))]["month"], share_of_S=float(srt[0] / S),
                        share_of_positive_months=float(srt[0] / pos_m)),
        best_3_individual_months=dict(value=float(srt[:3].sum()), share_of_S=float(srt[:3].sum() / S),
                                      share_of_positive_months=float(srt[:3].sum() / pos_m)),
        best_6_individual_months=dict(value=float(srt[:6].sum()), share_of_S=float(srt[:6].sum() / S),
                                      share_of_positive_months=float(srt[:6].sum() / pos_m)),
        best_consecutive_3_months=best_window(3), best_consecutive_6_months=best_window(6),
        best_year=dict(year=int(H.OUTER_YEARS[int(np.argmax(Ly))]), value=float(Ly.max()), share_of_S=float(Ly.max() / S),
                       share_of_positive_years=float(Ly.max() / pos_y)),
        best_2_years=dict(years=[int(H.OUTER_YEARS[i]) for i in np.argsort(Ly)[::-1][:2]],
                          value=float(np.sort(Ly)[::-1][:2].sum()), share_of_S=float(np.sort(Ly)[::-1][:2].sum() / S),
                          share_of_positive_years=float(np.sort(Ly)[::-1][:2].sum() / pos_y)),
        worst_month=dict(value=float(lm.min()), month=monthly[int(np.argmin(lm))]["month"]),
        worst_3_individual_months=float(np.sort(lm)[:3].sum()), worst_consecutive_3_months=best_window(3, worst=True),
        worst_year=dict(year=int(H.OUTER_YEARS[int(np.argmin(Ly))]), value=float(Ly.min())),
        sum_positive_years=pos_y,
        share_of_positive_years={str(y): (float(Ly[i] / pos_y) if Ly[i] > 0 else 0.0)
                                 for i, y in enumerate(H.OUTER_YEARS)})
    # rolling k-month H026 minus SPY returns (month-end marks, starting capital included)
    rolling = {}
    for k in (3, 6, 12, 24):
        d = (mh[k:] / mh[:-k] - 1.0) - (ms[k:] / ms[:-k] - 1.0)
        rolling[f"{k}m"] = dict(windows=int(d.size), median=float(np.median(d)), share_positive=float((d > 0).mean()),
                                **{kk: v for kk, v in q(d, (10, 25, 75, 90)).items()}, min=float(d.min()),
                                max=float(d.max()))
    # risk: beta / correlation / capture
    rh_d = np.diff(np.r_[cap, eh]) / np.r_[cap, eh][:-1]
    rs_d = np.diff(np.r_[cap, es]) / np.r_[cap, es][:-1]
    rh_m, rs_m = mh[1:] / mh[:-1] - 1, ms[1:] / ms[:-1] - 1
    up, dn = rs_m > 0, rs_m < 0

    def beta(a, b):
        return float(np.cov(a, b, ddof=1)[0, 1] / np.var(b, ddof=1))
    risk = dict(beta_daily=beta(rh_d, rs_d), corr_daily=float(np.corrcoef(rh_d, rs_d)[0, 1]),
                beta_monthly=beta(rh_m, rs_m), corr_monthly=float(np.corrcoef(rh_m, rs_m)[0, 1]),
                spy_up_months=int(up.sum()), spy_down_months=int(dn.sum()),
                mean_h026_when_spy_up=float(rh_m[up].mean()), mean_spy_when_up=float(rs_m[up].mean()),
                mean_h026_when_spy_down=float(rh_m[dn].mean()), mean_spy_when_down=float(rs_m[dn].mean()),
                up_capture=float(rh_m[up].mean() / rs_m[up].mean()),
                down_capture=float(rh_m[dn].mean() / rs_m[dn].mean()),
                up_capture_geometric=float((np.prod(1 + rh_m[up]) ** (1 / up.sum()) - 1)
                                           / (np.prod(1 + rs_m[up]) ** (1 / up.sum()) - 1)),
                down_capture_geometric=float((np.prod(1 + rh_m[dn]) ** (1 / dn.sum()) - 1)
                                             / (np.prod(1 + rs_m[dn]) ** (1 / dn.sum()) - 1)),
                tracking_error_annual=float((rh_d - rs_d).std(ddof=1) * math.sqrt(252)),
                **capm(rh_m, rs_m),
                log_relative_in_spy_up_months=float(lm[up].sum()), log_relative_in_spy_down_months=float(lm[dn].sum()),
                share_positive_relative_months_when_spy_up=float((lm[up] > 0).mean()),
                share_positive_relative_months_when_spy_down=float((lm[dn] > 0).mean()),
                definitions="monthly returns from month-end marks; capture = mean H026 return / mean SPY return over "
                            "the SPY-up (or SPY-down) months; geometric capture uses geometric mean monthly returns")
    # sub-periods 2015-2017 vs 2018-2021
    sub = {}
    for name, (y0, y1) in (("2015-2017", (2015, 2017)), ("2018-2021", (2018, 2021))):
        idx = np.flatnonzero((yrs >= y0) & (yrs <= y1))
        i0 = idx[0] - 1
        bh = cap if i0 < 0 else eh[i0]
        bs = cap if i0 < 0 else es[i0]
        gh, gs = eh[idx[-1]] / bh, es[idx[-1]] / bs
        yrs_n = (days[idx[-1]] - (days[i0] if i0 >= 0 else days[0] - 1)) / 365.25
        rh = np.diff(np.r_[bh, eh[idx]]) / np.r_[bh, eh[idx]][:-1]
        rs = np.diff(np.r_[bs, es[idx]]) / np.r_[bs, es[idx]][:-1]
        sub[name] = dict(wealth_ratio=float(gh / gs), relative_log=float(math.log(gh / gs)),
                         cagr_h026=float(gh ** (1 / yrs_n) - 1), cagr_spy=float(gs ** (1 / yrs_n) - 1),
                         excess_cagr=float(gh ** (1 / yrs_n) - gs ** (1 / yrs_n)),
                         vol_ratio=float(rh.std(ddof=1) / rs.std(ddof=1)),
                         maxdd_h026=H.max_drawdown(np.r_[bh, eh[idx]]), maxdd_spy=H.max_drawdown(np.r_[bs, es[idx]]),
                         years_beating=int(sum(annual[str(y)]["beat_spy"] for y in range(y0, y1 + 1))))
        sub[name]["maxdd_ratio"] = abs(sub[name]["maxdd_h026"]) / abs(sub[name]["maxdd_spy"])
    return dict(monthly=monthly, annual=annual, annual_log_contribution=contrib, concentration=conc, rolling=rolling,
                risk=risk, subperiods=sub, monthly_log_relative=[float(x) for x in lm])


def mechanics_section(o):
    tr = o["trades"]
    months = o["months"]
    ent = [int(d[:4]) + (1 if d[5:7] == "12" else 0) for d in months]
    by = {}
    for y, t, hld, cs in zip(ent, tr["turnover"], tr["holdings"], tr["cash_share"]):
        b = by.setdefault(str(y), dict(rebalances=0, turnover=0.0, holdings=[], cash=[]))
        b["rebalances"] += 1
        b["turnover"] += float(t)
        b["holdings"].append(hld)
        b["cash"].append(cs)
    per_year = {y: dict(rebalances=b["rebalances"], turnover_sum=b["turnover"], holdings_mean=float(np.mean(b["holdings"])),
                        holdings_min=int(min(b["holdings"])), cash_share_mean=float(np.mean(b["cash"])),
                        cash_utilisation=1 - float(np.mean(b["cash"]))) for y, b in by.items()}
    W, Wst = o["h026"]["wealth"], o["stress"]["h026"]
    costs = dict(
        commissions=tr["commissions"], slippage=tr["slippage"], total_nominal=tr["commissions"] + tr["slippage"],
        trades=tr["trades"], buys=tr["buys"], sells=tr["sells"],
        net_terminal_wealth=W, terminal_wealth_at_0p20_slippage=Wst, spy_at_0p20=o["stress"]["spy"],
        marginal_wealth_of_extra_0p10_slippage=W - Wst,
        indicative_wealth_without_slippage=W + (W - Wst),
        indicative_note=("linear extrapolation from the committed 0.10% and 0.20% runs of the SAME selections; not a "
                         "counterfactual run; commissions are reported at face value only"),
        gross_terminal_wealth_before_costs=COUNTERFACTUAL,
        annual_cost_drag_nominal=(tr["commissions"] + tr["slippage"]) / 7.0 / float(np.mean(o["daily_h026"])),
        turnover_monthly_mean=float(np.mean(tr["turnover"])), turnover_annual_mean=float(np.sum(tr["turnover"]) / 7.0))
    return dict(per_year=per_year, costs=costs, sector_counts=o["sector_counts"],
                sector_share={k: v / sum(o["sector_counts"].values()) for k, v in o["sector_counts"].items()})


def coefficient_section(o):
    coef = o["coefficients"]
    B = np.array([coef[str(y)]["beta"] for y in H.OUTER_YEARS], float)
    lam = [coef[str(y)]["lam"] for y in H.OUTER_YEARS]
    years = {str(y): dict(lam=coef[str(y)]["lam"], intercept=coef[str(y)]["b0"],
                          beta=dict(zip(FEATURES, B[i].tolist())), l2_norm=float(np.linalg.norm(B[i])))
             for i, y in enumerate(H.OUTER_YEARS)}

    def spear(a, b):
        ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
        return float(np.corrcoef(ra, rb)[0, 1])

    def cmp(a, b):
        na, nb = a / np.linalg.norm(a), b / np.linalg.norm(b)
        return dict(pearson=float(np.corrcoef(a, b)[0, 1]), spearman=spear(a, b), cosine=float(na @ nb),
                    l2_distance=float(np.linalg.norm(a - b)), l2_distance_unit_vectors=float(np.linalg.norm(na - nb)))
    adj = {f"{H.OUTER_YEARS[i]}-{H.OUTER_YEARS[i + 1]}": cmp(B[i], B[i + 1]) for i in range(len(B) - 1)}
    mean = B.mean(axis=0)
    to_mean = {str(y): cmp(B[i], mean) for i, y in enumerate(H.OUTER_YEARS)}
    # scale-free: the plain mean is dominated by 2015 (lambda 0.01, about 10x the norm of the lambda-100 years)
    Un = B / np.linalg.norm(B, axis=1, keepdims=True)
    umean = Un.mean(axis=0)
    to_mean_unit = {str(y): cmp(Un[i], umean) for i, y in enumerate(H.OUTER_YEARS)}
    stats = {}
    for j, f in enumerate(FEATURES):
        c = B[:, j]
        stats[f] = dict(mean=float(c.mean()), median=float(np.median(c)), sd=float(c.std(ddof=1)), min=float(c.min()),
                        max=float(c.max()), positive_years=int((c > 0).sum()), negative_years=int((c < 0).sum()),
                        sign_flips=int((np.diff(np.sign(c)) != 0).sum()), mean_abs=float(np.abs(c).mean()),
                        mean_2016_2021=float(c[1:].mean()), mean_abs_2016_2021=float(np.abs(c[1:]).mean()))
    rank_abs = sorted(FEATURES, key=lambda f: -stats[f]["mean_abs"])
    rank_abs_16_21 = sorted(FEATURES, key=lambda f: -stats[f]["mean_abs_2016_2021"])
    # unit-norm weight shares (scale-free view of what the ranking depends on), 2016-2021 mean
    U = B / np.linalg.norm(B, axis=1, keepdims=True)
    unit = {f: dict(mean_unit_weight_2016_2021=float(U[1:, j].mean()), mean_unit_weight_all=float(U[:, j].mean()))
            for j, f in enumerate(FEATURES)}
    # lambda behaviour: complete inner objectives
    sel = o["selection"]
    inner = {}
    for y in H.OUTER_YEARS:
        rows = sorted(sel[str(y)], key=lambda r: (r[0], r[1], r[2]), reverse=True)
        inner[str(y)] = dict(chosen=coef[str(y)]["lam"],
                             objectives={str(r[2]): dict(sum_log_rel=r[0], worst_year=r[1]) for r in sel[str(y)]},
                             winner_margin_over_runner_up=float(rows[0][0] - rows[1][0]),
                             runner_up=rows[1][2], chosen_is_max_lambda=coef[str(y)]["lam"] == max(H.LAMBDAS),
                             inner_years=list(range(H.FIRST_INNER, y)))
    inner_year_values = {f"{r[0]}|{r[1]}": r[2] for r in o["inner"]}
    freq = {str(l): int(sum(1 for x in lam if x == l)) for l in H.LAMBDAS}
    # APPROXIMATE score dispersion: SD of x.beta using the H024 canary's 2011-2017 median Spearman matrix of the raw
    # features (x = 2p - 1 has variance 1/3). Not per review; flagged as an approximation.
    C = np.array(json.loads((ROOT / "research/phase9/cp1/P9_CP1_canary_E026-01.json").read_text())["correlation"]["median"])
    disp = {}
    for i, y in enumerate(H.OUTER_YEARS):
        v = float(B[i] @ C @ B[i]) / 3.0
        disp[str(y)] = dict(approx_sd_prediction=math.sqrt(v), approx_p90_minus_p10=2.563 * math.sqrt(v),
                            approx_implied_r2_vs_label=float(B[i] @ C @ B[i]))
    return dict(years=years, feature_stats=stats, rank_by_mean_abs=rank_abs, rank_by_mean_abs_2016_2021=rank_abs_16_21,
                unit_weights=unit, adjacent=adj, to_mean=to_mean, to_mean_unit=to_mean_unit, lambda_frequency=freq, inner=inner,
                inner_single_year_log_rel=inner_year_values, approximate_dispersion=disp,
                approximate_dispersion_note=(
                    "APPROXIMATION: SD of the raw Ridge prediction x.beta from the H024 canary's median 2011-2017 "
                    "Spearman matrix (raw features), assuming x uniform on [-1, 1]; not the exported per-review "
                    "dispersion (not exported). Implied R^2 = beta' C beta (label variance 1/3 cancels)."))


def null_section(fields, W, o):
    col = {f: i for i, f in enumerate(fields)}
    A = np.array([[w[col[f]] for f in fields] for w in W], float)
    S = A[:, col["S_WEALTH"]]
    real = dict(S_WEALTH=math.log(o["h026"]["wealth"] / o["spy"]["wealth"]),
                excess_cagr=o["h026"]["cagr"] - o["spy"]["cagr"], maxdd=o["h026"]["maxdd"], vol=o["h026"]["vol"],
                years_beating=int(sum(1 for v in o["gates"]["L"].values() if v > 0)))
    spy = o["spy"]
    dist = {}
    for key in ("S_WEALTH", "excess_cagr", "maxdd", "vol", "years_beating"):
        x = A[:, col[key]]
        dist[key] = dict(mean=float(x.mean()), sd=float(x.std(ddof=1)), min=float(x.min()), max=float(x.max()),
                         **q(x, (1, 5, 10, 25, 50, 75, 90, 95, 99)),
                         real=real[key], share_null_below_real=float((x < real[key]).mean()),
                         share_null_at_or_above_real=float((x >= real[key]).mean()))
    wr = np.exp(S)
    dist["wealth_ratio"] = dict(mean=float(wr.mean()), **q(wr, (1, 5, 50, 95, 99)), max=float(wr.max()),
                                real=float(math.exp(real["S_WEALTH"])),
                                share_null_at_or_above_real=float((wr >= math.exp(real["S_WEALTH"])).mean()))
    dist["years_beating"]["histogram"] = {str(k): int((A[:, col["years_beating"]] == k).sum()) for k in range(8)}
    win = S >= real["S_WEALTH"]
    lamcols = [f"lam_{y}" for y in H.OUTER_YEARS]
    L = A[:, [col[c] for c in lamcols]]
    real_lam = np.array([o["coefficients"][str(y)]["lam"] for y in H.OUTER_YEARS])

    def lam_profile(mask):
        return {str(y): {str(l): int(((L[mask, i]) == l).sum()) for l in H.LAMBDAS} for i, y in enumerate(H.OUTER_YEARS)}
    winners = dict(
        count=int(win.sum()),
        S_WEALTH=dict(median=float(np.median(S[win])), min=float(S[win].min()), max=float(S[win].max())),
        wealth_ratio_median=float(np.median(wr[win])),
        excess_cagr=dict(median=float(np.median(A[win, col["excess_cagr"]])), real=real["excess_cagr"]),
        maxdd=dict(median=float(np.median(A[win, col["maxdd"]])), share_no_worse_than_real=float(
            (A[win, col["maxdd"]] >= real["maxdd"]).mean()), real=real["maxdd"]),
        vol=dict(median=float(np.median(A[win, col["vol"]])), share_no_higher_than_real=float(
            (A[win, col["vol"]] <= real["vol"]).mean()), real=real["vol"]),
        years_beating={str(k): int((A[win, col["years_beating"]] == k).sum()) for k in range(8)},
        lambda_profile=lam_profile(win), all_null_lambda_profile=lam_profile(np.ones(len(S), bool)),
        same_lambda_sequence_as_real=int(np.all(L[win] == real_lam, axis=1).sum()),
        all_null_same_lambda_sequence_as_real=int(np.all(L == real_lam, axis=1).sum()),
        lambda_100_in_at_least_6_years=int(((L[win] == 100.0).sum(axis=1) >= 6).sum()),
        all_null_lambda_100_in_at_least_6_years=int(((L == 100.0).sum(axis=1) >= 6).sum()),
        turnover=NOT_EXPORTED.replace("security-level holdings, trades, scores and selected-stock feature percentiles",
                                      "null-world turnover and coefficients"),
        coefficient_stability="NOT COMPUTED — null-world coefficients were not stored (only lambda by year)")
    d2 = (wr >= H.D2_WEALTH_RATIO) & (A[:, col["excess_cagr"]] >= H.D2_EXCESS_CAGR)
    d4 = (np.abs(A[:, col["maxdd"]]) <= H.D4_RATIO * abs(spy["maxdd"])) & (A[:, col["vol"]] <= H.D4_RATIO * spy["vol"])
    d3n = A[:, col["years_beating"]] >= H.D3_MIN_YEARS
    d1 = S > P.C_WEALTH
    joint = dict(
        wealth_ge_real=int((wr >= math.exp(real["S_WEALTH"])).sum()),
        wealth_ge_real_and_maxdd_no_worse=int(((wr >= math.exp(real["S_WEALTH"])) & (A[:, col["maxdd"]] >= real["maxdd"])).sum()),
        wealth_ge_real_maxdd_no_worse_vol_no_higher=int(((wr >= math.exp(real["S_WEALTH"]))
                                                         & (A[:, col["maxdd"]] >= real["maxdd"])
                                                         & (A[:, col["vol"]] <= real["vol"])).sum()),
        D1=int(d1.sum()), D2=int(d2.sum()), D4=int(d4.sum()), D3_necessary_years_ge_5=int(d3n.sum()),
        D3_full="NOT COMPUTED — the null rows store only the count of years beating SPY, not the yearly log-relatives "
                "needed for the 2015-2017 / 2018-2021 sums and the 50% concentration rule",
        D5="NOT COMPUTED — the 0.20%-slippage wealth was not stored for null worlds",
        D2_and_D4=int((d2 & d4).sum()),
        D2_and_D4_and_not_D1=int((d2 & d4 & ~d1).sum()),
        D2_and_D4_and_D3_necessary=int((d2 & d4 & d3n).sum()),
        D1_and_D2_and_D4_and_D3_necessary=int((d1 & d2 & d4 & d3n).sum()),
        D2_and_D4_and_years_le_3=int((d2 & d4 & (A[:, col["years_beating"]] <= 3)).sum()),
        spy_reference=dict(maxdd=spy["maxdd"], vol=spy["vol"]),
        note="post-hoc descriptive counts only; no new p-value or qualification rule")
    # descriptive return-per-risk: CAGR / annualised volatility (CAGR_null = CAGR_SPY + stored excess CAGR)
    cagr_n = spy["cagr"] + A[:, col["excess_cagr"]]
    rpv_n = cagr_n / A[:, col["vol"]]
    rpv_real = o["h026"]["cagr"] / o["h026"]["vol"]
    rpv = dict(real=rpv_real, spy=spy["cagr"] / spy["vol"], null_median=float(np.median(rpv_n)),
               null_p99=float(np.percentile(rpv_n, 99)), null_max=float(rpv_n.max()),
               null_at_or_above_real=int((rpv_n >= rpv_real).sum()),
               null_vol_at_or_below_spy=int((A[:, col["vol"]] <= spy["vol"]).sum()),
               null_maxdd_no_worse_than_spy=int((A[:, col["maxdd"]] >= spy["maxdd"]).sum()),
               note="post-hoc descriptive; CAGR / volatility is not a pre-registered statistic")
    return dict(worlds=len(W), real=real, distributions=dist, winners=winners, joint=joint, return_per_vol=rpv)


def governance_section():
    s = json.loads((ROOT / "research/phase11/data_v21/x801_summary.json").read_text())
    m = json.loads((ROOT / P.DATA_V21_MANIFEST).read_text())
    corr = s["mapping_specification_correction"]
    full = s["per_period"]
    return dict(
        d207_status=m["status"], owner_approval_exists=False, manifest_sha256=P.DATA_V21_MANIFEST_SHA256,
        gate=dict(name="NEW_YEARS_MAPPING", threshold=s["thresholds"]["new_year_mapping_min"],
                  result=s["gates"]["NEW_YEARS_MAPPING"],
                  as_written="share of NEW vendor fundamental reports (first appearance in QuantConnect's stream) whose "
                             "period maps to an SEC filing of the reporting company, over ALL new reports",
                  intended="the same share over new reports of companies that HAVE an SEC identity row (a report of a "
                           "company with no SEC identity can never map; those companies are outside the identity scope "
                           "and never feed fundamentals under Data v2)"),
        by_year=corr["e801_01"], frozen_data_v2_by_year=corr["frozen_e998_01"],
        frozen_years_identical=corr["frozen_years_identical"],
        new_reports_by_period={k: dict(new_reports=v.get("new_reports"), mapped_share_as_written=v.get(
            "new_reports_mapped_share")) for k, v in full.items()},
        population_2011_2017=s["h022_population_2011_2017"])


def main():
    st, o = load_real()
    fields, W = load_null()
    out = dict(
        status="H026 REMAINS REJECTED (post-mortem cannot alter the status)",
        source=dict(real=P.REAL, nulls=list(P.NULL_RUNS), null_result_sha256=P.NULL_RESULT_SHA256,
                    real_blob_sha256=st["real"]["blob_sha256"]),
        gates={k: o["gates"][k] for k in ("S_WEALTH", "D1", "D2", "D3", "D4", "D5", "all", "largest_share")},
        c_wealth=P.C_WEALTH, path=path_section(o), mechanics=mechanics_section(o), coefficients=coefficient_section(o),
        null=null_section(fields, W, o), governance=governance_section(), diagnostics=o["diagnostics"],
        not_computed=dict(
            security_contributors=NOT_EXPORTED, profit_concentration=NOT_EXPORTED, holding_distribution=NOT_EXPORTED,
            monthly_breadth=NOT_EXPORTED, selected_stock_feature_exposures=NOT_EXPORTED,
            exact_score_dispersion=NOT_EXPORTED, score_rank_stability_and_top15_overlap=NOT_EXPORTED,
            sector_weights_by_period_and_sector_pnl=NOT_EXPORTED, universe_relative_attribution=NOT_EXPORTED,
            jackknife_without_winners="NOT COMPUTED — no holding-level contributions were recorded (and D211 allows it "
                                      "only analytically from recorded contributions)",
            gross_wealth_before_costs=COUNTERFACTUAL))
    (HERE / "P11_CP2_postmortem.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    p = out["path"]
    print(json.dumps(dict(annual={y: (round(a["h026"], 4), round(a["spy"], 4), round(a["relative_log"], 4),
                                      round(a["end_relative_wealth"], 4)) for y, a in p["annual"].items()},
                          contrib=p["annual_log_contribution"], risk=p["risk"], sub=p["subperiods"],
                          joint=out["null"]["joint"]), indent=1, default=float))


if __name__ == "__main__":
    main()
