"""P13-CP4 (owner D225): H028 30-year objective-alignment review -> P13_CP4_alignment.json.

DESCRIPTIVE ONLY. H028 stays REJECTED (B4 unchanged); the alignment label is a description against the owner's
clarified 30-year objective, never a research status, a gate or a repair. No QuantConnect run, no new data, no
retraining, no new parameters, nothing after 2021-12-31 (the sources end there), Holdout sealed.

Committed BEFORE any P13-CP4 statistic was computed. Nothing below changes after results.

Already known before this file was written (disclosed, P13-CP1 / P13-CP2 / P13-CP3): full-period H028 down-capture
0.69 and beta 0.76; H028 yearly returns 2015-2021 and 3 of 7 years ahead of SPY; per-year captures for 2015-2017; every
P13-CP3 synthetic number (so dimensions C, E and F below are effectively determined by already-published numbers;
their thresholds are Claude's judgement, written to be read against the owner's wording, not calibrated). NOT known
before this file: the full-period up-capture, the subset (+-2% / +-5%) statistics, the rolling 12 / 36 / 60-month
distributions, the up / down log decomposition, the real-history exclusion captures and the conditional-on-winning
synthetic patience statistics.

1. Data. The 84 paired monthly total returns 2015-01..2021-12 of H028, LV15 and SPY (after each one's actual costs)
   = P13-CP3 donor_panel (committed P13_CP3_bootstrap.json), re-derived here from experiments/E030-05 with the
   committed P13-CP3 loader and required to be identical. Month-end marks are pre-liquidation (P13-CP3 audit).
2. Monthly sets. UP = SPY > 0; DOWN = SPY < 0 (SPY == 0 in neither; counted). Subsets SPY >= +2%, >= +5%,
   <= -2%, <= -5%. Per set: n, mean / median of H028, SPY, H028 - SPY; capture = mean(H028) / mean(SPY) over the set
   (the P11-CP2 / qr_h027.risk definition; PRIMARY); compounded capture = (prod(1 + H) - 1) / (prod(1 + S) - 1)
   (supplementary); share of months H028 > SPY (strict); compounded return of H028 and SPY over the set's months.
   The same for LV15 (context).
3. Participation (owner 6, thresholds verbatim, on the PRIMARY up-capture): >= 1.00 STRONG UPSIDE PARTICIPATION;
   0.90-1.00 NEAR-FULL PARTICIPATION; < 0.90 MATERIAL UPSIDE SACRIFICE. Protection 'becomes stronger as losses
   grow' iff down-capture(SPY <= -5%) < down-capture(SPY <= -2%) < down-capture(all DOWN).
4. ASYMMETRY_RATIO = up-capture / down-capture (primary captures); not computed ('NOT MEANINGFUL') when
   |down-capture| < 0.05; a negative down-capture is reported with the flag 'ROSE ON AVERAGE WHEN SPY FELL'.
   Descriptive only, never a gate. H028 and LV15; full period and the three exclusion sets.
5. Years: compounded calendar-year returns; SPY year UP iff > 0; mean H028 - SPY over SPY-UP and SPY-DOWN years;
   number of SPY-UP years with H028 >= SPY and SPY-DOWN years with H028 > SPY (and H028 return >= SPY return).
6. Rolling windows of n consecutive months (n = 12, 36, 60 -> 73, 49, 25 windows; overlapping, not independent):
   R = prod(1 + r) - 1 for H028 and SPY; relative wealth (1 + R_H) / (1 + R_S); excess = R_H - R_S; annualised
   excess = (1 + R_H)^(12/n) - (1 + R_S)^(12/n); share of windows R_H > R_S; percentiles 5 / 25 / 50 / 75 / 95, min,
   max. Overlap disclosure: windows containing all 12 months of 2018 / any month of 2020. 10-year windows:
   'NOT AVAILABLE FROM REAL DEVELOPMENT HISTORY'.
7. Decomposition: l_t = log((1 + H_t) / (1 + S_t)); LU = sum over UP months, LD = sum over DOWN months, L0 over
   SPY == 0 months, T = LU + LD + L0; shares LU / T and LD / T (reported only when T > 0). Also per calendar year
   (LU, LD, total) and the two largest positive monthly l_t with their share of T.
8. Patterns (owner 18), evaluated in this order:
   C if, after removing the two calendar years with the largest yearly sum of l_t, the remaining sum of l_t <= 0,
     OR after removing the two months with the largest l_t, the remaining sum <= 0 ('the entire edge comes from one or
     two exceptional episodes');
   else A if primary up-capture >= 0.90 AND primary down-capture <= 0.85;
   else B if primary up-capture < 0.90 AND primary down-capture <= 0.85 AND LD > 0;
   else 'NONE OF A-C'. The A / B criteria are reported whether or not C holds.
9. Real-history exclusions (owner 19-20; no retraining: the recorded months are simply dropped and the rest
   concatenated): ex-2018-and-2020 (60 months), ex-2018 (72), ex-2020 (72), plus the full period (84):
   annualised return = prod(1 + r)^(12/n) - 1 for H028 and SPY, the difference, sum of l_t, primary up / down capture,
   asymmetry ratio, monthly win rate vs SPY (share H028 > SPY). Not an independent test.
10. Synthetic (owner 21-23) = the committed P13-CP3 numbers, copied. The one statistic not saved there, patience
   conditional on winning (owner 22: 'even in synthetic paths where it ultimately wins'), is recomputed
   deterministically: the P13-CP3 'year' worlds (seeds 1..10,000) are regenerated with the committed P13-CP3 code and
   their world-metric digest must equal the committed world_metric_sha256 (else STOP); among worlds with 30-year
   H028 > SPY: longest losing-year streak vs SPY (median, 90th, share >= 5, share >= 10), longest recovery months
   (median, 90th, share open at the end), relative MaxDD (median, 5th percentile = worse tail), share with any
   rolling 5-year window behind SPY; the same for the worlds where H028 ends behind SPY.
11. Dimensions (owner 25; STRONG / ACCEPTABLE / WEAK; not combined into a score):
   A Upside participation (primary up-capture u): STRONG u >= 1.00; ACCEPTABLE 0.90 <= u < 1.00; WEAK u < 0.90.
   B Downside protection (primary down-capture d, d5 = capture in SPY <= -5% months): STRONG d <= 0.75 AND
     d5 <= 0.75; ACCEPTABLE d <= 0.90; WEAK d > 0.90.
   C Long-run compounding (real annualised excess vs SPY x = annualised H028 - annualised SPY over 84 months;
     P13-CP3 'year' 30y P(H028 > SPY) p and median ratio m): STRONG x >= 0.02 AND p >= 0.80 AND m >= 1.5;
     ACCEPTABLE x > 0 AND p >= 0.60; WEAK otherwise.
   D Temporal consistency (real shares of windows ahead s12, s36, s60): STRONG s12 >= 0.65 AND s36 >= 0.80 AND
     s60 >= 0.90; ACCEPTABLE s12 >= 0.50 AND s36 >= 0.60 AND s60 >= 0.75; WEAK otherwise.
   E Regime dependence (P13-CP3 30y P(H028 > SPY): q = ex-2018-and-2020, qmin = min over leave-one-year-out; real
     ex-2018-and-2020 annualised excess e): STRONG q >= 0.80 AND qmin >= 0.80 AND e > 0; ACCEPTABLE q >= 0.50 AND
     qmin >= 0.50 AND e > 0; WEAK otherwise.
   F Relative drawdown / patience burden (P13-CP3 'year', vs SPY, all worlds: median longest losing streak k years,
     median longest recovery r months, median relative MaxDD g): STRONG k <= 2 AND r <= 36 AND g >= -0.10;
     ACCEPTABLE k <= 4 AND r <= 60 AND g >= -0.20; WEAK otherwise.
12. Overall (owner 26-28), W = number of WEAK dimensions:
   OBJECTIVE-ALIGNED if W == 0 and the pattern is not C;
   NOT OBJECTIVE-ALIGNED if C is WEAK, or A and B are both WEAK, or W >= 3;
   PARTIALLY OBJECTIVE-ALIGNED otherwise.
13. Missing capability (owner 27; wording chosen by rule, no design): upside need iff A WEAK; downside need iff B WEAK;
   regime need iff E WEAK or the pattern is C; consistency need iff D or F WEAK. Reported as the list of needs.

    PYTHONPATH=src python research/phase13/cp4/P13_CP4_alignment.py
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "research/phase13/cp3")]
import P13_CP3_bootstrap as B  # noqa: E402

CP3 = ROOT / "research/phase13/cp3/P13_CP3_bootstrap.json"
YEARS = B.YEARS
SETS = (("up", lambda s: s > 0), ("up_ge_2pct", lambda s: s >= 0.02), ("up_ge_5pct", lambda s: s >= 0.05),
        ("down", lambda s: s < 0), ("down_le_2pct", lambda s: s <= -0.02), ("down_le_5pct", lambda s: s <= -0.05))
EXCL = (("full", ()), ("ex_2018", (2018,)), ("ex_2020", (2020,)), ("ex_2018_2020", (2018, 2020)))
WINDOWS = (12, 36, 60)
Q = (5, 25, 50, 75, 95)


def _plain(x):
    return x.item() if hasattr(x, "item") else str(x)


def cp3():
    return json.loads(CP3.read_text())


def donor_panel():
    """84 x 3 returns (h028, lv15, spy) + month labels; committed CP3 panel == fresh rebuild from E030-05."""
    c = cp3()
    months = c["donor_panel"]["months"]
    r = np.stack([np.asarray(c["donor_panel"]["returns"][n], float) for n in B.SERIES], axis=1)
    o, sha = B.load()
    m2, r2, _ = B.panel(o)
    assert sha == c["source"]["qrhr_blob_sha256"] and m2 == months and np.array_equal(r2, r), "panel mismatch"
    return months, r


def capture(h, s):
    return float(h.mean() / s.mean()) if s.size else float("nan")


def comp_capture(h, s):
    rs = float(np.prod(1 + s) - 1)
    return float((np.prod(1 + h) - 1) / rs) if s.size and rs != 0 else float("nan")


def set_stats(h, s, l=None):
    d = h - s
    out = dict(n=int(s.size), mean_h=float(h.mean()), mean_spy=float(s.mean()), mean_rel=float(d.mean()),
               median_h=float(np.median(h)), median_spy=float(np.median(s)), median_rel=float(np.median(d)),
               capture=capture(h, s), compounded_capture=comp_capture(h, s),
               share_h_gt_spy=float(np.mean(h > s)), compounded_h=float(np.prod(1 + h) - 1),
               compounded_spy=float(np.prod(1 + s) - 1))
    if l is not None:
        out.update(mean_lv15=float(l.mean()), lv15_capture=capture(l, s), share_lv15_gt_spy=float(np.mean(l > s)))
    return out


def asym(u, d):
    if not (math.isfinite(u) and math.isfinite(d)) or abs(d) < 0.05:
        return dict(value=None, flag="NOT MEANINGFUL (|down-capture| < 0.05)")
    return dict(value=u / d, flag="ROSE ON AVERAGE WHEN SPY FELL" if d < 0 else "")


def participation(u):
    return ("STRONG UPSIDE PARTICIPATION" if u >= 1.0 else "NEAR-FULL PARTICIPATION" if u >= 0.90
            else "MATERIAL UPSIDE SACRIFICE")


def rolling(h, s, n, months):
    rh = np.array([np.prod(1 + h[i:i + n]) - 1 for i in range(len(h) - n + 1)])
    rs = np.array([np.prod(1 + s[i:i + n]) - 1 for i in range(len(s) - n + 1)])
    ratio, ex = (1 + rh) / (1 + rs), rh - rs
    ann = (1 + rh) ** (12 / n) - (1 + rs) ** (12 / n)
    yrs = np.array([int(m[:4]) for m in months])
    full18 = sum(int(np.sum(yrs[i:i + n] == 2018) == 12) for i in range(len(h) - n + 1))
    any20 = sum(int(np.any(yrs[i:i + n] == 2020)) for i in range(len(h) - n + 1))
    worst, best = int(np.argmin(ex)), int(np.argmax(ex))
    return dict(windows=int(rh.size), share_h_gt_spy=float(np.mean(rh > rs)),
                excess=dict({f"p{q}": float(np.percentile(ex, q)) for q in Q}, min=float(ex.min()), max=float(ex.max())),
                ratio=dict({f"p{q}": float(np.percentile(ratio, q)) for q in Q}, min=float(ratio.min()),
                           max=float(ratio.max())),
                annualised_excess=dict({f"p{q}": float(np.percentile(ann, q)) for q in Q}, min=float(ann.min()),
                                       max=float(ann.max())),
                worst_window=dict(start=months[worst], end=months[worst + n - 1], h=float(rh[worst]), spy=float(rs[worst])),
                best_window=dict(start=months[best], end=months[best + n - 1], h=float(rh[best]), spy=float(rs[best])),
                windows_with_all_2018=full18, windows_with_any_2020=any20)


def exclusion(r, yrs, drop):
    keep = ~np.isin(yrs, drop)
    h, l, s = r[keep, 0], r[keep, 1], r[keep, 2]
    n = int(keep.sum())
    ah, as_ = float(np.prod(1 + h) ** (12 / n) - 1), float(np.prod(1 + s) ** (12 / n) - 1)
    up, dn = s > 0, s < 0
    u, d = capture(h[up], s[up]), capture(h[dn], s[dn])
    return dict(months=n, ann_h=ah, ann_spy=as_, ann_diff=ah - as_, ann_lv15=float(np.prod(1 + l) ** (12 / n) - 1),
                sum_log_rel=float(np.sum(np.log1p(h) - np.log1p(s))), up_capture=u, down_capture=d,
                asymmetry=asym(u, d), monthly_win_rate=float(np.mean(h > s)),
                lv15_up_capture=capture(l[up], s[up]), lv15_down_capture=capture(l[dn], s[dn]))


def synthetic_conditional():
    """Regenerate the CP3 'year' worlds; verify the committed digest; patience stats conditional on the 30y outcome."""
    c = cp3()
    lr = np.log1p(np.stack([np.asarray(c["donor_panel"]["returns"][n], float) for n in B.SERIES], axis=1))
    L, _ = B.simulate(lr, "year", range(1, B.METHODS["year"][1] + 1))
    m = B.world_metrics(L)
    dig = B.digest(m)
    if dig != c["methods"]["year"]["world_metric_sha256"]:
        raise RuntimeError("STOP — regenerated P13-CP3 worlds differ from the committed digest")
    out = dict(world_metric_sha256=dig, digest_matches_committed=True)
    for lab, sel in (("winners_30y", m["log_rel_spy_30"] > 0), ("losers_30y", m["log_rel_spy_30"] < 0)):
        st, rc, dd = m["streak_spy"][sel], m["recovery_spy"][sel], m["rel_maxdd_spy"][sel]
        out[lab] = dict(worlds=int(sel.sum()), streak_p50=float(np.median(st)), streak_p90=float(np.percentile(st, 90)),
                        streak_share_ge5=float(np.mean(st >= 5)), streak_share_ge10=float(np.mean(st >= 10)),
                        recovery_p50_months=float(np.median(rc)), recovery_p90_months=float(np.percentile(rc, 90)),
                        recovery_share_open=float(np.mean(m["recovery_open_spy"][sel])),
                        rel_maxdd_p50=float(np.median(dd)), rel_maxdd_p5=float(np.percentile(dd, 5)),
                        share_any_rolling5y_behind=float(np.mean(m["roll_min_spy"][sel] < 0)),
                        win_years_p50=float(np.median(m["win_years_spy"][sel])))
    return out


def synthetic_copy():
    c = cp3()
    y = c["methods"]["year"]["summary"]
    s30 = lambda k: c["methods"][k]["summary"]["30y"]  # noqa: E731
    reg = {k: dict(p_beat_spy_30y=s30(k)["p_beat_spy"], median_ratio_30y=s30(k)["ratio_spy"]["p50"],
                   median_excess_cagr_30y=s30(k)["excess_cagr"]["p50"], p_beat_lv15_30y=s30(k)["p_beat_lv15"])
           for k in ["year", "mb12", "mb24", "ex1820"] + [f"loo_{yy}" for yy in YEARS]}
    return dict(
        horizons={h: dict(p_beat_spy=y[h]["p_beat_spy"], p_beat_lv15=y[h]["p_beat_lv15"],
                          ratio_spy=y[h]["ratio_spy"], excess_cagr=y[h]["excess_cagr"]) for h in ("5y", "10y", "20y", "30y")},
        streak_spy=y["streak_spy"], recovery_spy=y["recovery_spy"], rel_maxdd_spy=y["rel_maxdd_spy"],
        rolling5y_spy=y["rolling5y_spy"], win_years_spy=y["win_years_spy"], regime=reg,
        seven_year=c["seven_year"], regime_frequency={k: c["regime_frequency"][k] for k in ("2018", "2020")},
        cp3_result=c["result"])


def classify(u, d, d5, x, syn, roll, ex1820_e):
    p, mr = syn["regime"]["year"]["p_beat_spy_30y"], syn["regime"]["year"]["median_ratio_30y"]
    q = syn["regime"]["ex1820"]["p_beat_spy_30y"]
    qmin = min(syn["regime"][f"loo_{yy}"]["p_beat_spy_30y"] for yy in YEARS)
    s12, s36, s60 = (roll[n]["share_h_gt_spy"] for n in WINDOWS)
    k, r, g = syn["streak_spy"]["p50"], syn["recovery_spy"]["p50_months"], syn["rel_maxdd_spy"]["p50"]
    dims = dict(
        A=("STRONG" if u >= 1.0 else "ACCEPTABLE" if u >= 0.90 else "WEAK", dict(up_capture=u)),
        B=("STRONG" if d <= 0.75 and d5 <= 0.75 else "ACCEPTABLE" if d <= 0.90 else "WEAK",
           dict(down_capture=d, down_capture_le_5pct=d5)),
        C=("STRONG" if x >= 0.02 and p >= 0.80 and mr >= 1.5 else "ACCEPTABLE" if x > 0 and p >= 0.60 else "WEAK",
           dict(real_ann_excess=x, p30=p, median_ratio_30=mr)),
        D=("STRONG" if s12 >= 0.65 and s36 >= 0.80 and s60 >= 0.90 else
           "ACCEPTABLE" if s12 >= 0.50 and s36 >= 0.60 and s60 >= 0.75 else "WEAK", dict(s12=s12, s36=s36, s60=s60)),
        E=("STRONG" if q >= 0.80 and qmin >= 0.80 and ex1820_e > 0 else
           "ACCEPTABLE" if q >= 0.50 and qmin >= 0.50 and ex1820_e > 0 else "WEAK",
           dict(ex1820_p30=q, min_loo_p30=qmin, real_ex1820_ann_excess=ex1820_e)),
        F=("STRONG" if k <= 2 and r <= 36 and g >= -0.10 else
           "ACCEPTABLE" if k <= 4 and r <= 60 and g >= -0.20 else "WEAK",
           dict(median_streak_years=k, median_recovery_months=r, median_rel_maxdd=g)))
    return {kk: dict(label=v[0], inputs=v[1]) for kk, v in dims.items()}


def pattern(lm, yrs, u, d, LD):
    ysum = {y: float(lm[yrs == y].sum()) for y in YEARS}
    top2y = sorted(ysum, key=ysum.get, reverse=True)[:2]
    rest_y = float(sum(v for y, v in ysum.items() if y not in top2y))
    top2m = np.argsort(lm)[::-1][:2]
    rest_m = float(lm.sum() - lm[top2m].sum())
    c_hold = rest_y <= 0 or rest_m <= 0
    a_hold = u >= 0.90 and d <= 0.85
    b_hold = u < 0.90 and d <= 0.85 and LD > 0
    best = "C" if c_hold else "A" if a_hold else "B" if b_hold else "NONE OF A-C"
    return dict(best_supported=best, C_holds=bool(c_hold), A_criteria_hold=bool(a_hold), B_criteria_hold=bool(b_hold),
                top2_years=top2y, sum_without_top2_years=rest_y, top2_month_indices=[int(i) for i in top2m],
                sum_without_top2_months=rest_m)


def main():
    months, r = donor_panel()
    yrs = np.array([int(m[:4]) for m in months])
    h, l, s = r[:, 0], r[:, 1], r[:, 2]
    sets = {name: set_stats(h[f(s)], s[f(s)], l[f(s)]) for name, f in SETS}
    u, d = sets["up"]["capture"], sets["down"]["capture"]
    lu, ld = sets["up"]["lv15_capture"], sets["down"]["lv15_capture"]
    d2, d5 = sets["down_le_2pct"]["capture"], sets["down_le_5pct"]["capture"]
    yearly = {}
    for y in YEARS:
        k = yrs == y
        hy, sy, ly = (float(np.prod(1 + x[k]) - 1) for x in (h, s, l))
        yearly[str(y)] = dict(h028=hy, spy=sy, lv15=ly, h_minus_spy=hy - sy, spy_year="UP" if sy > 0 else "DOWN")
    upy = [v for v in yearly.values() if v["spy_year"] == "UP"]
    dny = [v for v in yearly.values() if v["spy_year"] == "DOWN"]
    years = dict(per_year=yearly, n_up_years=len(upy), n_down_years=len(dny),
                 mean_rel_up_years=float(np.mean([v["h_minus_spy"] for v in upy])) if upy else None,
                 mean_rel_down_years=float(np.mean([v["h_minus_spy"] for v in dny])) if dny else None,
                 up_years_h_ge_spy=sum(v["h028"] >= v["spy"] for v in upy),
                 down_years_h_gt_spy=sum(v["h028"] > v["spy"] for v in dny),
                 down_years_h_nonnegative=sum(v["h028"] >= 0 for v in dny))
    roll = {n: rolling(h, s, n, months) for n in WINDOWS}
    lm = np.log1p(h) - np.log1p(s)
    LU, LD, L0 = float(lm[s > 0].sum()), float(lm[s < 0].sum()), float(lm[s == 0].sum())
    T = LU + LD + L0
    decomp = dict(LU=LU, LD=LD, L0=L0, T=T, n_zero_months=int(np.sum(s == 0)),
                  share_up=LU / T if T > 0 else None, share_down=LD / T if T > 0 else None,
                  per_year={str(y): dict(LU=float(lm[(yrs == y) & (s > 0)].sum()), LD=float(lm[(yrs == y) & (s < 0)].sum()),
                                         total=float(lm[yrs == y].sum())) for y in YEARS},
                  top_months=[dict(month=months[i], log_rel=float(lm[i]), h=float(h[i]), spy=float(s[i]),
                                   share_of_T=float(lm[i] / T) if T > 0 else None) for i in np.argsort(lm)[::-1][:2]],
                  worst_months=[dict(month=months[i], log_rel=float(lm[i]), h=float(h[i]), spy=float(s[i]))
                                for i in np.argsort(lm)[:2]])
    excl = {name: exclusion(r, yrs, drop) for name, drop in EXCL}
    syn = synthetic_copy()
    cond = synthetic_conditional()
    pat = pattern(lm, yrs, u, d, LD)
    dims = classify(u, d, d5, excl["full"]["ann_diff"], syn, roll, excl["ex_2018_2020"]["ann_diff"])
    W = sum(v["label"] == "WEAK" for v in dims.values())
    overall = ("NOT OBJECTIVE-ALIGNED" if dims["C"]["label"] == "WEAK" or
               (dims["A"]["label"] == "WEAK" and dims["B"]["label"] == "WEAK") or W >= 3 else
               "OBJECTIVE-ALIGNED" if W == 0 and pat["best_supported"] != "C" else "PARTIALLY OBJECTIVE-ALIGNED")
    needs = [n for n, c in (("upside participation", dims["A"]["label"] == "WEAK"),
                            ("downside protection", dims["B"]["label"] == "WEAK"),
                            ("regime independence (relative returns outside crash / sell-off episodes)",
                             dims["E"]["label"] == "WEAK" or pat["best_supported"] == "C"),
                            ("temporal consistency / shorter relative drawdowns",
                             dims["D"]["label"] == "WEAK" or dims["F"]["label"] == "WEAK")) if c]
    out = dict(
        source=dict(cp3_json_sha256=hashlib.sha256(CP3.read_bytes()).hexdigest(), experiment=B.EXP,
                    months=[months[0], months[-1], len(months)], panel_rebuilt_identical=True),
        monthly_sets=sets, participation=participation(u),
        protection_strengthens_with_loss_size=bool(d5 < d2 < d),
        asymmetry=dict(h028=asym(u, d), lv15=asym(lu, ld), h028_compounded=asym(sets["up"]["compounded_capture"],
                                                                                sets["down"]["compounded_capture"])),
        years=years, rolling={str(n): v for n, v in roll.items()},
        rolling_10y="NOT AVAILABLE FROM REAL DEVELOPMENT HISTORY", decomposition=decomp, pattern=pat,
        exclusions=excl, synthetic=syn, synthetic_conditional=cond, dimensions=dims, weak_count=W,
        objective_alignment=overall, missing_capability=needs,
        original_research_status="H028 REJECTED")
    path = HERE / "P13_CP4_alignment.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain) + "\n")
    print(json.dumps(dict(alignment=overall, dims={k: v["label"] for k, v in dims.items()}, pattern=pat["best_supported"],
                          up=u, down=d), default=_plain))
    print("sha256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
