"""P14-CP3 (owner D229): offline evaluation of the ONE real H029 / H030 run E031-05 -> P14_CP3_result.json.
Committed before E031-05 ran (spec sections 7, 10, 11). Recomputes every gate from the exported daily paths and the
committed null rows (exact empirical p), checks it against the host, and computes the pre-registered descriptive
metrics. No rule, threshold or definition changes after the result.

    PYTHONPATH=src python research/phase14/cp3/P14_CP3_result.py
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
import qr_h026 as H  # noqa: E402
import qr_h029 as Q  # noqa: E402
import qr_p7_export as E  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import p14h029 as P  # noqa: E402

EXP = P.REAL
NAMES = ("spy", "lv15", "h028", "h029", "h030")
CAP = H.CAPITAL


def load():
    ls = lines(EXP)
    st = json.loads(joined(ls, "QRY"))
    blob = joined(ls, "QRYR")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"], "blob hash mismatch"
    return st, json.loads(E.unpack(blob))


def path_stats(eq, days, rs, labels, wealth):
    eq = np.asarray(eq, float)
    pm = H.path_metrics(eq, days, CAP, wealth)
    r, lab = Q.monthly(eq, days)
    assert lab == labels
    rk = Q.risk(r, rs)
    rel = Q.relative(r, rs, lab)
    yrs = H.year_returns(eq, days, CAP)
    return pm, r, rk, rel, yrs


def rolling(rl, w):
    c = np.r_[0.0, np.cumsum(rl)]
    x = c[w:] - c[:-w]
    return dict(windows=int(x.size), win_rate=float(np.mean(x > 0)) if x.size else None)


def bucket(r, rs, mask):
    if not mask.any():
        return dict(months=0)
    return dict(months=int(mask.sum()), capture=float(r[mask].mean() / rs[mask].mean()),
                mean_excess=float((r[mask] - rs[mask]).mean()), win_rate=float(np.mean(r[mask] > rs[mask])))


def main():
    st, o = load()
    null = json.loads((HERE / "P14_CP3_null_rows.json").read_text())["worlds"]
    days = np.asarray(o["days"], float)
    spy_d = np.asarray(o["daily"]["spy"], float)
    rs, labels = Q.monthly(spy_d, days)
    spy_pm = H.path_metrics(spy_d, days, CAP, o["wealth"]["spy"])
    spy = dict(pm=spy_pm, wealth=o["wealth"]["spy"], r=rs)
    res, ser = {}, {}
    for n in NAMES[1:]:
        pm, r, rk, rel, yrs = path_stats(o["daily"][n], days, rs, labels, o["wealth"][n])
        ser[n] = r
        res[n] = dict(wealth=pm["wealth"], cagr=pm["cagr"], vol=pm["vol"], maxdd=pm["maxdd"], sharpe=pm["sharpe"],
                      up_capture=rk["up_capture"], down_capture=rk["down_capture"], beta=rk["beta"],
                      spy_up_contribution=rel["s_up"], spy_down_contribution=rel["s_down"], total_relative=rel["total"],
                      ex_2018_2020=rel["ex1820"], up_by_year=rel["U"], all_by_year=rel["A"],
                      share_2018_2020=(rel["A"].get(2018, 0) + rel["A"].get(2020, 0)) / rel["total"] if rel["total"] else None,
                      years_above_spy=sum(1 for y in yrs if yrs[y] > H.year_returns(spy_d, days, CAP)[y]),
                      year_returns=yrs,
                      rolling={f"{w}m": rolling(rel["rl"], w) for w in (12, 36, 60)},
                      strong_up={f"ge_{k}": bucket(r, rs, rs >= k / 100) for k in (2, 5)},
                      falling={"lt_0": bucket(r, rs, rs < 0), "le_-2": bucket(r, rs, rs <= -0.02),
                               "le_-5": bucket(r, rs, rs <= -0.05)})
        if n in o["trades"]:
            t = o["trades"][n]
            res[n]["costs"] = dict(trades=t["trades"], commissions=t["commissions"], slippage=t["slippage"],
                                   mean_turnover=float(np.mean(t["turnover"])), mean_holdings=float(np.mean(t["holdings"])),
                                   mean_cash_share=float(np.mean(t["cash_share"])))
    res["spy"] = dict(wealth=spy_pm["wealth"], cagr=spy_pm["cagr"], vol=spy_pm["vol"], maxdd=spy_pm["maxdd"],
                      year_returns=H.year_returns(spy_d, days, CAP))
    # ---------------------------------------------------------------- gates (offline recomputation, exact p)
    s_up_null = [r[1] for r in null]
    s_inc_null = [r[10] for r in null]
    c_up, c_inc = P.C_UP_H029, P.C_INCREMENTAL_H030
    assert c_up == Q.critical_value(s_up_null) and c_inc == Q.critical_value(s_inc_null)
    e29 = dict(rel=Q.relative(ser["h029"], rs, labels), risk=Q.risk(ser["h029"], rs),
               pm=dict(maxdd=res["h029"]["maxdd"], vol=res["h029"]["vol"]), wealth=res["h029"]["wealth"])
    sp_s = np.asarray(o["stress"]["daily_spy"], float)
    r29s, _ = Q.monthly(o["stress"]["daily_h029"], days)
    rss, _ = Q.monthly(sp_s, days)
    s_up_stress = Q.relative(r29s, rss, labels)["s_up"]
    p_up = Q.empirical_p(s_up_null, e29["rel"]["s_up"])
    g29 = Q.gates_h029(e29, spy, s_up_stress, c_up, p_up)
    e30 = dict(rel=Q.relative(ser["h030"], rs, labels), risk=Q.risk(ser["h030"], rs),
               pm=dict(maxdd=res["h030"]["maxdd"], vol=res["h030"]["vol"]), wealth=res["h030"]["wealth"])
    s_inc = math.log(res["h030"]["wealth"] / res["h028"]["wealth"])
    p_inc = Q.empirical_p(s_inc_null, s_inc)
    stress = dict(w30=o["stress"]["w30"], w28=o["stress"]["w28"], spy=o["stress"]["spy"])
    g30 = Q.gates_h030(e30, res["h028"]["wealth"], spy, c_inc, p_inc, stress)
    host_match = all(g29[k] == o["gates_h029"][k] for k in ("N1", "N2", "N3", "N4", "N5")) and \
        all(g30[k] == o["gates_h030"][k] for k in ("C1", "C2", "C3", "C4", "C5", "C6", "C7"))
    # ---------------------------------------------------------------- real-in-null (descriptive)
    a = np.asarray([r[1:] for r in null], float)
    col = {f: a[:, i] for i, f in enumerate(Q.NULL_FIELDS[1:])}
    rin = {}
    for key, real in (("vol29", res["h029"]["vol"]), ("beta29", res["h029"]["beta"]), ("up29", res["h029"]["up_capture"]),
                      ("dn29", res["h029"]["down_capture"]), ("vol30", res["h030"]["vol"]), ("beta30", res["h030"]["beta"]),
                      ("up30", res["h030"]["up_capture"]), ("dn30", res["h030"]["down_capture"]),
                      ("w29", res["h029"]["wealth"]), ("w30", res["h030"]["wealth"])):
        rin[key] = dict(real=real, null_median=float(np.median(col[key])),
                        percentile=float(np.mean(col[key] < real) * 100.0))
    synth_eligible = bool(g30["all"])
    out = dict(experiment=EXP, gates_h029=g29, gates_h030=g30, host_gates_match=host_match,
               verdict_h029=g29["verdict"], verdict_h030=g30["verdict"], p_up=p_up, p_inc=p_inc, s_inc=s_inc,
               strategies=res, real_in_null=rin, sectors=o["sectors"],
               eligible29=o["eligible29"], joint30=o["joint30"], synthetic_robustness_eligible=synth_eligible,
               months=len(labels), first=labels[0], last=labels[-1])
    (HERE / "P14_CP3_result.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    print(g29["verdict"], "|", g30["verdict"], "| host gates match:", host_match)


if __name__ == "__main__":
    main()
