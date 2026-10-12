"""P12-CP1 (owner D213): assess the ONE real H027 development run (S029 real mode, E029-05) -> P12_CP1_result.json.

Written and committed BEFORE the real run. Steps (spec sections 3, 7, 8):
  1. pins: c_WEALTH_CONDITIONAL, null result hash, threshold commit, H026 feature / response panels, PIT audit 0;
  2. H026 reproduction: terminal wealth and S_WEALTH (1e-9) plus, offline, the yearly returns, lambdas and coefficients
     of the committed P11-CP1 result, and the real risk values used by the adequacy audit (P11-CP2 definitions).
     Any difference -> STOP (no gate is judged);
  3. A1-A6 re-derived offline with the frozen qr_h027.gates (must equal the host's), A1 with the empirical p against
     the 5,000 committed conditional-null worlds (p <= 0.01);
  4. non-gating diagnostics (never rescue): LOWVOL-factor regression, sector-neutral, March 2020 attribution (nothing
     removed or winsorised), $200K / Top-10 / Top-20, market regime; where the real portfolio sits in the null's risk
     distributions.
A3 is reported as A CARRIED-FORWARD ECONOMIC REQUIREMENT, NOT NEW INDEPENDENT EVIDENCE. Final status is exactly one of
the D213 strings. Development evidence only.

    PYTHONPATH=src python research/phase12/cp1/P12_CP1_result.py
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
import P12_CP1_null as NULL  # noqa: E402
import qr_h026 as H  # noqa: E402
import qr_h027 as G  # noqa: E402
import qr_p7_export as E  # noqa: E402
from qresearch import p12h027 as P  # noqa: E402

STATUS = dict(
    candidate="H027 DEVELOPMENT CANDIDATE — INCREMENTAL EDGE BEYOND LOWVOL DETECTED — FINAL HOLDOUT SEALED",
    rejected="H027 REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE",
    stop="STOP — REAL RUN DOES NOT REPRODUCE THE FROZEN H026 RESULT (E028-05) OR PINS DIFFER")
FINAL_SCORE_STATUS = "H027 DEVELOPMENT CANDIDATE — EXPOSURE-CONTROLLED SCORE FROZEN — HOLDOUT NOT RUN"
A3_NOTE = "A CARRIED-FORWARD ECONOMIC REQUIREMENT, NOT NEW INDEPENDENT EVIDENCE"


def null_rows():
    rows = []
    for e in P.NULL_RUNS:
        rows += NULL.run(e)[1]["worlds"]
    return sorted(rows, key=lambda r: r[0])


def h026_reference():
    r = json.loads((ROOT / "research/phase11/cp1/P11_CP1_result.json").read_text())
    return r


def reproduction(o, ref):
    yh = {int(k): v for k, v in o["years_h027"].items()}
    checks = dict(
        host_wealth_and_s=o["reproduction"]["ok"] is True,
        wealth=o["h027"]["wealth"] == ref["portfolio"]["h026"]["wealth"],
        spy_wealth=o["spy"]["wealth"] == ref["portfolio"]["spy"]["wealth"],
        yearly_returns=all(yh[y] == ref["years"][str(y)]["h026"] for y in H.OUTER_YEARS),
        lambdas=all(o["coefficients"][str(y)]["lam"] == ref["years"][str(y)]["lam"] for y in H.OUTER_YEARS),
        coefficients=all(o["coefficients"][str(y)]["beta"] == [ref["years"][str(y)]["beta"][f] for f in H.FEATURES]
                         for y in H.OUTER_YEARS))
    return checks


def assess(st, o, prov, rows):
    c = P.C_WEALTH_CONDITIONAL
    pv = st["provenance"]
    pins = dict(c=pv["c_wealth_conditional"] == c, null_result=pv["null_result_sha256"] == P.NULL_RESULT_SHA256,
                threshold_commit=pv["threshold_commit"] == P.THRESHOLD_COMMIT,
                feature_panel=st["feature_panel_sha256"] == P.H026_FEATURE_PANEL_SHA256,
                response_panel=st["response_panel_sha256"] == P.H026_RESPONSE_PANEL_SHA256,
                equivalence=st["equivalence"] == dict(feature_panel=True, response_panel=True),
                pit_audit_zero=all(v == 0 for v in st["pit_audit"].values()),
                adequate=P.ADEQUATE is True)
    rep = reproduction(o, h026_reference())
    days = np.asarray(o["days"], float)
    rk_h = G.risk(o["daily_h027"], o["daily_spy"], days, H.CAPITAL)
    rk_lv = G.risk(o["daily_lv15"], o["daily_spy"], days, H.CAPITAL)
    real_risk = dict(vol=o["h027"]["vol"], maxdd=o["h027"]["maxdd"], beta=rk_h["beta"],
                     down_capture=rk_h["down_capture"])
    rep["risk_equals_adequacy_reference"] = all(abs(real_risk[k] - P.H026_REAL_RISK[k]) <= 1e-12 for k in real_risk)
    yh = {int(k): v for k, v in o["years_h027"].items()}
    ys = {int(k): v for k, v in o["years_spy"].items()}
    ylv = {int(k): v for k, v in o["years_lv15"].items()}
    g = G.gates(o["h027"], o["spy"], o["lv15"], yh, ys, ylv, o["stress"]["h027"], o["stress"]["spy"],
                o["stress"]["lv15"], c)
    host = o["gates"]
    same = all(g[k] == host[k] for k in ("A1", "A2", "A3", "A4", "A5", "A6", "all")) and \
        abs(g["S_WEALTH"] - host["S_WEALTH"]) < 1e-12
    col = {f: i for i, f in enumerate(G.FIELDS)}
    S = np.array([r[col["S_WEALTH"]] for r in rows], float)
    p = G.empirical_p(S, g["S_WEALTH"])
    a1 = bool(g["S_WEALTH"] > c and p <= G.ALPHA)
    gates = dict(A1=a1, A2=g["A2"], A3=g["A3"], A4=g["A4"], A5=g["A5"], A6=g["A6"])
    gates["all"] = all(gates.values())
    ok = all(pins.values()) and all(rep.values()) and same and len(rows) == G.R_NULL
    status = STATUS["stop"] if not ok else (STATUS["candidate"] if gates["all"] else STATUS["rejected"])
    h, s, lv = o["h027"], o["spy"], o["lv15"]

    def pct(key, val, lower_is_more_defensive=True):
        x = np.array([r[col[key]] for r in rows], float)
        return dict(real=val, null_share_at_least_as_defensive=float(np.mean(x <= val if lower_is_more_defensive
                                                                             else x >= val)),
                    null_median=float(np.median(x)))
    d = o["diagnostics"]
    mar = d["march_2020"]["2020-03"]
    lmar_spy = math.log((1 + mar["h027"]) / (1 + mar["spy"]))
    lmar_lv = math.log((1 + mar["h027"]) / (1 + mar["lv15"]))
    S_lv = math.log(h["wealth"] / lv["wealth"])
    out = dict(
        status=status, final_score_status=FINAL_SCORE_STATUS if status == STATUS["candidate"] else None,
        development_evidence_only=True, pins=pins, reproduction=rep, host_gates_reproduced=same,
        gates=dict(gates, c_wealth_conditional=c, S_WEALTH=g["S_WEALTH"], p_empirical=p, null_worlds=len(rows),
                   null_at_or_above=int((S >= g["S_WEALTH"]).sum()),
                   A2_detail=dict(wealth_h027=h["wealth"], wealth_lv15=lv["wealth"], cagr_h027=h["cagr"],
                                  cagr_lv15=lv["cagr"], S_vs_lv15=S_lv),
                   A3_note=A3_NOTE, A3_detail=dict(wealth_ratio=h["wealth"] / s["wealth"],
                                                   excess_cagr=h["cagr"] - s["cagr"]),
                   A4_detail=dict(L_vs_lv15={str(k): v for k, v in g["L_vs_lv15"].items()},
                                  years_beating_lv15=g["years_beating_lv15"],
                                  L_2015_2017=float(sum(g["L_vs_lv15"][y] for y in (2015, 2016, 2017))),
                                  L_2018_2021=float(sum(g["L_vs_lv15"][y] for y in (2018, 2019, 2020, 2021)))),
                   A5_detail=dict(maxdd_ratio=abs(h["maxdd"]) / abs(s["maxdd"]), vol_ratio=h["vol"] / s["vol"]),
                   A6_detail=o["stress"]),
        portfolio=dict(h027=h, spy=s, lv15=lv, lv15_vs_spy=dict(S=math.log(lv["wealth"] / s["wealth"]),
                                                                excess_cagr=lv["cagr"] - s["cagr"]),
                       trades=o["trades"] | dict(turnover=None, holdings=None, cash_share=None),
                       lv15_trades=o["lv15_trades"] | dict(turnover=None, holdings=None, cash_share=None)),
        years={str(y): dict(h027=yh[y], spy=ys[y], lv15=ylv[y], lam=o["coefficients"][str(y)]["lam"])
               for y in H.OUTER_YEARS},
        risk=dict(h027={k: v for k, v in rk_h.items() if k not in ("rh", "rs")},
                  lv15={k: v for k, v in rk_lv.items() if k not in ("rh", "rs")}),
        real_in_null_risk=dict(vol=pct("vol", real_risk["vol"]), maxdd=pct("maxdd", real_risk["maxdd"], False),
                               beta=pct("beta", real_risk["beta"]),
                               down_capture=pct("down_capture", real_risk["down_capture"])),
        diagnostics=dict(
            lowvol_factor_regression={k: v for k, v in d["lowvol_factor_regression"].items()
                                      if k not in ("factor", "dependent")},
            sector_neutral=d["sector_neutral"], regime=d["regime"], capital_200k=d["capital_200k"], top10=d["top10"],
            top20=d["top20"],
            march_2020=dict(returns=d["march_2020"], log_relative_vs_spy=lmar_spy, log_relative_vs_lv15=lmar_lv,
                            share_of_S_WEALTH=lmar_spy / g["S_WEALTH"] if g["S_WEALTH"] else None,
                            share_of_S_vs_lv15=lmar_lv / S_lv if S_lv else None,
                            note="included as recorded; nothing removed or winsorised")),
        final_model=o.get("final_model"),
        provenance=dict(git_commit=prov["git_commit"], lean_version=prov["lean_version"],
                        qc_backtest_id=prov["qc_backtest_id"], code_sha256=prov["code_sha256"]),
        pit_audit=st["pit_audit"], runtime=dict(wall_s=st.get("wall_s"), max_rss_mb=st.get("max_rss_mb")))
    assert math.isfinite(g["S_WEALTH"])
    return out


def main(exp=P.REAL):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRG"))
    blob = joined(ls, "QRGR")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"], "real blob hash"
    o = json.loads(E.unpack(blob))
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    out = assess(st, o, prov, null_rows())
    out["experiment"] = exp
    (HERE / "P12_CP1_result.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps(dict(status=out["status"], pins=out["pins"], reproduction=out["reproduction"],
                          gates=out["gates"], years=out["years"], risk=out["real_in_null_risk"],
                          factor=out["diagnostics"]["lowvol_factor_regression"],
                          march_2020=out["diagnostics"]["march_2020"]), indent=1, default=float))


if __name__ == "__main__":
    main(*sys.argv[1:])
