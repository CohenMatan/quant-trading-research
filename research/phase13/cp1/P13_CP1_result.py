"""P13-CP1 (owner D217): assess the ONE real H028 development run (S030 real mode, E030-05) -> P13_CP1_result.json.

Written and committed BEFORE the real run. Order (spec sections 5, 6, 8, 9; each step can stop the assessment):
  1. pins: c_WEALTH_H028, null result hash, threshold commit, tolerance table digest, H026 panels, PIT audit 0, ADEQUATE;
  2. H027 reproduction: the recomputed H027 = E029-05 (wealth, S_WEALTH, lambda schedule) and, offline, its yearly
     returns and coefficients = the committed P12-CP1 result; the fixed path with H027's schedule = qr_h026.run_world;
  3. 2016-2021 equality with H027: every EXACT part identical (else "STOP — UNEXPECTED PIPELINE DIFFERENCE"); the
     path-dependent yearly-return / turnover differences within the pinned tolerance (else STOP and explain);
  4. risk adequacy step 2: the pre-registered rule with the realised H028 values against the 5,000 committed null worlds
     (else "H028 BLOCKED — CONDITIONAL NULL INADEQUATE");
  5. B1-B6 re-derived offline with the frozen qr_h027.gates (A1..A6 = B1..B6; must equal the host's), B1 with the
     empirical p (<= 0.01);
  6. the pre-registered reporting and non-gating diagnostics (2015 H027-vs-H028 comparison, yearly table vs LV15 / SPY /
     H027, H027/H028 comparison table, LOWVOL-factor regression, sector-neutral, March 2020, $200K / Top-10 / Top-20,
     regime). Nothing rescues a failed gate. Development evidence only.

    PYTHONPATH=src python research/phase13/cp1/P13_CP1_result.py
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7"), str(HERE)]
from P7_CP3R_extract import joined, lines  # noqa: E402
import P13_CP1_null as NULL  # noqa: E402
import qr_h026 as H  # noqa: E402
import qr_h027 as G  # noqa: E402
import qr_h028 as F  # noqa: E402
import qr_p7_export as E  # noqa: E402
from qresearch import p13h028 as P  # noqa: E402

STATUS = dict(
    candidate="H028 DEVELOPMENT CANDIDATE — FIXED λ=100 SCORE FROZEN — FINAL HOLDOUT SEALED",
    rejected="H028 REJECTED — FIXED STRONG SHRINKAGE DOES NOT ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM",
    blocked="H028 BLOCKED — CONDITIONAL NULL INADEQUATE",
    stop_pipeline="STOP — UNEXPECTED PIPELINE DIFFERENCE",
    stop_tolerance="STOP — 2016-2021 DIFFERENCE FROM H027 EXCEEDS THE PRE-REGISTERED TOLERANCE",
    stop_reproduction="STOP — REAL RUN DOES NOT REPRODUCE H027 OR PINS DIFFER")
B4_DISCLOSURE = ("The temporal gate was repaired by the pre-registered fixed-λ change primarily through 2015; the later "
                 "years were already observed under H027.")
B3_NOTE = "an economic requirement carried forward from H026 / H027 (not new independent evidence)"


def null_rows():
    rows = []
    for e in P.NULL_RUNS:
        rows += NULL.run(e)[1]["worlds"]
    return sorted(rows, key=lambda r: r[0])


def year_slice(daily, days, year):
    yrs = np.array([int(str(np.datetime64(int(d), "D"))[:4]) for d in days])
    return np.asarray(daily, float)[yrs == year], yrs


def assess(st, o, prov, rows):
    c = P.C_WEALTH_H028
    pv = st["provenance"]
    pins = dict(c=pv["c_wealth_h028"] == c, null_result=pv["null_result_sha256"] == P.NULL_RESULT_SHA256,
                threshold_commit=pv["threshold_commit"] == P.THRESHOLD_COMMIT,
                tolerance=pv["tolerance_sha256"] == P.TOLERANCE_SHA256,
                feature_panel=st["feature_panel_sha256"] == P.H026_FEATURE_PANEL_SHA256,
                response_panel=st["response_panel_sha256"] == P.H026_RESPONSE_PANEL_SHA256,
                equivalence=st["equivalence"] == dict(feature_panel=True, response_panel=True),
                pit_audit_zero=all(v == 0 for v in st["pit_audit"].values()), adequate_step1=P.ADEQUATE is True,
                null_worlds=len(rows) == G.R_NULL)
    # 2. H027 reproduction (host + committed P12-CP1 result)
    ref = json.loads((ROOT / "research/phase12/cp1/P12_CP1_result.json").read_text())
    ref26 = json.loads((ROOT / "research/phase11/cp1/P11_CP1_result.json").read_text())   # H026 = H027 coefficients
    y27 = {int(k): v for k, v in o["years_h027"].items()}
    rep = dict(host=o["reproduction_h027"]["ok"] is True,
               wealth=o["h027"]["wealth"] == ref["portfolio"]["h027"]["wealth"],
               yearly_returns=all(y27[y] == ref["years"][str(y)]["h027"] for y in H.OUTER_YEARS),
               coefficients=all(o["coefficients_h027"][str(y)]["beta"] == [ref26["years"][str(y)]["beta"][f]
                                                                           for f in H.FEATURES] for y in H.OUTER_YEARS),
               lambdas=[o["coefficients_h027"][str(y)]["lam"] for y in H.OUTER_YEARS] == P.H027_LAMBDA_SCHEDULE)
    # 3. 2016-2021 equality
    eq = o["equality"]
    tol_ok = F.within_tolerance(dict(per_year={int(k): v for k, v in eq["per_year"].items()}), P.TOLERANCE)
    # 4. adequacy step 2 with the realised H028 values
    days = np.asarray(o["days"], float)
    rk8 = G.risk(o["daily_h028"], o["daily_spy"], days, H.CAPITAL)
    real_risk = dict(vol=o["h028"]["vol"], maxdd=o["h028"]["maxdd"], beta=rk8["beta"], down_capture=rk8["down_capture"])
    adq2 = G.adequacy(rows, real_risk)
    # 5. gates
    yh = {int(k): v for k, v in o["years_h028"].items()}
    ys = {int(k): v for k, v in o["years_spy"].items()}
    ylv = {int(k): v for k, v in o["years_lv15"].items()}
    g = G.gates(o["h028"], o["spy"], o["lv15"], yh, ys, ylv, o["stress"]["h028"], o["stress"]["spy"],
                o["stress"]["lv15"], c)
    host = o["gates"]
    same = all(g[k] == host[k] for k in ("A1", "A2", "A3", "A4", "A5", "A6", "all")) and \
        abs(g["S_WEALTH"] - host["S_WEALTH"]) < 1e-12
    col = {f: i for i, f in enumerate(G.FIELDS)}
    S = np.array([r[col["S_WEALTH"]] for r in rows], float)
    p = G.empirical_p(S, g["S_WEALTH"])
    gates = dict(B1=bool(g["S_WEALTH"] > c and p <= G.ALPHA), B2=g["A2"], B3=g["A3"], B4=g["A4"], B5=g["A5"], B6=g["A6"])
    gates["all"] = all(gates.values())
    if not (all(pins.values()) and all(rep.values()) and same):
        status = STATUS["stop_reproduction"]
    elif not eq["exact_ok"]:
        status = STATUS["stop_pipeline"]
    elif not tol_ok["ok"]:
        status = STATUS["stop_tolerance"]
    elif not adq2["adequate"]:
        status = STATUS["blocked"]
    else:
        status = STATUS["candidate"] if gates["all"] else STATUS["rejected"]
    h8, h7, s, lv = o["h028"], o["h027"], o["spy"], o["lv15"]
    L = g["L_vs_lv15"]
    L27 = {y: math.log((1 + y27[y]) / (1 + ylv[y])) for y in H.OUTER_YEARS}
    # 2015 comparison (spec 9.1)
    c15_8, c15_7 = o["coefficients"]["2015"], o["coefficients_h027"]["2015"]
    coef15 = {f: dict(h027=c15_7["beta"][j], h028=c15_8["beta"][j], abs_change=abs(c15_8["beta"][j] - c15_7["beta"][j]),
                      sign_change=bool(np.sign(c15_8["beta"][j]) != np.sign(c15_7["beta"][j])))
              for j, f in enumerate(H.FEATURES)}
    d8, _ = year_slice(o["daily_h028"], days, 2015)
    d7, _ = year_slice(o["daily_h027"], days, 2015)
    rm8 = [r for r in o["replay_months"]["h028"]]
    rm7 = [r for r in o["replay_months"]["h027"]]
    m15 = set(o["y2015"]["months"])
    y2015 = dict(
        coefficients=coef15, intercept=dict(h027=c15_7["b0"], h028=c15_8["b0"]),
        coef_norm=dict(h027=float(np.linalg.norm(c15_7["beta"])), h028=float(np.linalg.norm(c15_8["beta"]))),
        ret=dict(h028=yh[2015], h027=y27[2015], spy=ys[2015], lv15=ylv[2015], change=yh[2015] - y27[2015]),
        rel_spy=dict(h028=math.log((1 + yh[2015]) / (1 + ys[2015])), h027=math.log((1 + y27[2015]) / (1 + ys[2015]))),
        rel_lv15=dict(h028=L[2015], h027=L27[2015]),
        maxdd=dict(h028=H.max_drawdown(np.r_[H.CAPITAL, d8]), h027=H.max_drawdown(np.r_[H.CAPITAL, d7])),
        turnover=dict(h028=float(sum(r[1] for r in rm8 if r[0] in m15)), h027=float(sum(r[1] for r in rm7 if r[0] in m15))),
        year_end_wealth=dict(h028=float(d8[-1]), h027=float(d7[-1])),
        score_spearman=dict(by_month=dict(zip(o["y2015"]["months"], o["y2015"]["score_spearman"])),
                            mean=float(np.mean(o["y2015"]["score_spearman"]))),
        top15_overlap=dict(by_month=dict(zip(o["y2015"]["months"], o["y2015"]["held_overlap"])),
                           mean=float(np.mean(o["y2015"]["held_overlap"]))))
    years = {str(y): dict(h028=yh[y], h027=y27[y], spy=ys[y], lv15=ylv[y], L_h028_vs_lv15=L[y], L_h027_vs_lv15=L27[y],
                          h028_beats_spy=yh[y] > ys[y], h028_beats_lv15=L[y] > 0) for y in H.OUTER_YEARS}
    t8, t7 = np.asarray(o["trades"]["turnover"], float), np.asarray(o["trades_h027"]["turnover"], float)
    comparison = dict(
        terminal_wealth=dict(h027=h7["wealth"], h028=h8["wealth"]), cagr=dict(h027=h7["cagr"], h028=h8["cagr"]),
        excess_cagr_vs_spy=dict(h027=h7["cagr"] - s["cagr"], h028=h8["cagr"] - s["cagr"]),
        S_WEALTH=dict(h027=math.log(h7["wealth"] / s["wealth"]), h028=g["S_WEALTH"]),
        null_p=dict(h027="0.0006 vs the H027 lambda-selecting conditional null (E029-02/03)",
                    h028=f"{p} vs the H028 lambda-100 conditional null (E030-02/03)"),
        maxdd=dict(h027=h7["maxdd"], h028=h8["maxdd"]), vol=dict(h027=h7["vol"], h028=h8["vol"]),
        years_beating_spy=dict(h027=sum(1 for y in H.OUTER_YEARS if y27[y] > ys[y]),
                               h028=sum(1 for y in H.OUTER_YEARS if yh[y] > ys[y])),
        years_beating_lv15=dict(h027=sum(1 for v in L27.values() if v > 0), h028=g["years_beating_lv15"]),
        L_2015_2017_vs_lv15=dict(h027=sum(L27[y] for y in (2015, 2016, 2017)), h028=sum(L[y] for y in (2015, 2016, 2017))),
        L_2018_2021_vs_lv15=dict(h027=sum(L27[y] for y in (2018, 2019, 2020, 2021)),
                                 h028=sum(L[y] for y in (2018, 2019, 2020, 2021))),
        turnover_monthly_mean=dict(h027=float(t7.mean()), h028=float(t8.mean())),
        trades=dict(h027=o["trades_h027"]["trades"], h028=o["trades"]["trades"]))
    dg = o["diagnostics"]
    mar = dg["march_2020"]["2020-03"]
    lm_spy, lm_lv = math.log((1 + mar["h028"]) / (1 + mar["spy"])), math.log((1 + mar["h028"]) / (1 + mar["lv15"]))
    S_lv = math.log(h8["wealth"] / lv["wealth"])
    def pct(key, val, lower=True):  # noqa: E306
        x = np.array([r[col[key]] for r in rows], float)
        return dict(real=val, null_share_at_least_as_defensive=float(np.mean(x <= val if lower else x >= val)),
                    null_median=float(np.median(x)))
    fm = o.get("final_model")
    out = dict(
        status=status, final_score_status=STATUS["candidate"] if status == STATUS["candidate"] else None,
        development_evidence_only=True, post_hoc=True, pins=pins, reproduction_h027=rep, host_gates_reproduced=same,
        equality=dict(exact=dict((k, eq[k]) for k in ("same_idx", "lambda_100_both", "coefficients_identical",
                                                      "scores_identical", "targets_identical", "held_sets_identical",
                                                      "replay_exact", "orders_identical_after_transition", "exact_ok")),
                      transition_month=eq["transition_month"], transition=eq["transition"], per_year=eq["per_year"],
                      tolerance=P.TOLERANCE, tolerance_check=tol_ok),
        adequacy_step2=adq2,
        gates=dict(gates, c_wealth_h028=c, S_WEALTH=g["S_WEALTH"], p_empirical=p, null_worlds=len(rows),
                   null_at_or_above=int((S >= g["S_WEALTH"]).sum()), null_percentile=float(np.mean(S < g["S_WEALTH"])),
                   B2_detail=dict(wealth_h028=h8["wealth"], wealth_lv15=lv["wealth"], cagr_h028=h8["cagr"],
                                  cagr_lv15=lv["cagr"], S_vs_lv15=S_lv),
                   B3_note=B3_NOTE, B3_detail=dict(wealth_ratio=h8["wealth"] / s["wealth"], excess_cagr=h8["cagr"] - s["cagr"]),
                   B4_detail=dict(L_vs_lv15={str(k): v for k, v in L.items()}, years_beating_lv15=g["years_beating_lv15"],
                                  L_2015_2017=float(sum(L[y] for y in (2015, 2016, 2017))),
                                  L_2018_2021=float(sum(L[y] for y in (2018, 2019, 2020, 2021))),
                                  disclosure=B4_DISCLOSURE if gates["B4"] else None),
                   B5_detail=dict(maxdd_ratio=abs(h8["maxdd"]) / abs(s["maxdd"]), vol_ratio=h8["vol"] / s["vol"]),
                   B6_detail=o["stress"]),
        portfolio=dict(h028=h8, h027=h7, spy=s, lv15=lv, trades=dict(o["trades"], turnover=None, holdings=None,
                                                                     cash_share=None)),
        years=years, y2015=y2015, comparison=comparison,
        risk=o["risk"], real_in_null_risk=dict(vol=pct("vol", real_risk["vol"]), maxdd=pct("maxdd", real_risk["maxdd"], False),
                                               beta=pct("beta", real_risk["beta"]),
                                               down_capture=pct("down_capture", real_risk["down_capture"])),
        coefficients=o["coefficients"], coefficients_h027=o["coefficients_h027"],
        diagnostics=dict(
            lowvol_factor_regression={k: v for k, v in dg["lowvol_factor_regression"].items() if k not in ("factor", "dependent")},
            sector_neutral=dg["sector_neutral"], regime=dg["regime"], capital_200k=dg["capital_200k"], top10=dg["top10"],
            top20=dg["top20"],
            march_2020=dict(returns=dg["march_2020"], log_relative_vs_spy=lm_spy, log_relative_vs_lv15=lm_lv,
                            share_of_S_WEALTH=lm_spy / g["S_WEALTH"] if g["S_WEALTH"] else None,
                            share_of_S_vs_lv15=lm_lv / S_lv if S_lv else None,
                            h027_march_reproduced=dg["march_2020"]["2020-03"]["h027"],
                            note="included as recorded; nothing removed or winsorised")),
        final_model=fm if status == STATUS["candidate"] else None,
        final_model_sha256=(hashlib.sha256(json.dumps(fm, sort_keys=True).encode()).hexdigest()
                            if fm and status == STATUS["candidate"] else None),
        provenance=dict(git_commit=prov["git_commit"], lean_version=prov["lean_version"],
                        qc_backtest_id=prov["qc_backtest_id"], code_sha256=prov["code_sha256"]),
        pit_audit=st["pit_audit"], runtime=dict(wall_s=st.get("wall_s"), max_rss_mb=st.get("max_rss_mb"),
                                                peak_vmhwm_mb=max((m[2].get("VmHWM", 0) for m in st.get("memory", [])),
                                                                  default=None)))
    assert math.isfinite(g["S_WEALTH"])
    return out


def main(exp=P.REAL):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRG"))
    blob = joined(ls, "QRHR")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"], "real blob hash"
    o = json.loads(E.unpack(blob))
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    out = assess(st, o, prov, null_rows())
    out["experiment"] = exp
    (HERE / "P13_CP1_result.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps(dict(status=out["status"], pins=out["pins"], reproduction=out["reproduction_h027"],
                          equality=out["equality"]["exact"], tolerance=out["equality"]["tolerance_check"],
                          adequacy2=out["adequacy_step2"]["adequate"], gates=out["gates"], years=out["years"],
                          y2015={k: out["y2015"][k] for k in ("ret", "rel_lv15", "rel_spy", "maxdd", "turnover")},
                          comparison=out["comparison"]), indent=1, default=float))


if __name__ == "__main__":
    main(*sys.argv[1:])
