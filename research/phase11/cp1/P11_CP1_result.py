"""P11-CP1 (owner D206): assess the ONE real H026 development run (S028 real mode, E028-05) -> P11_CP1_result.json.

Written and committed BEFORE the real run. Re-derives D1-D5 offline from the host's path metrics / yearly returns with the
frozen qr_h026.gates and the pinned c_WEALTH (must equal the host's gates), and adds the reporting the owner asked for:
terminal wealth, CAGR, excess CAGR, volatility, Sharpe, MaxDD, time underwater, turnover, trades, commissions, slippage,
average holdings, cash utilisation, sector concentration; per outer year lambda, the 11 coefficients, returns, turnover,
MaxDD; coefficient stability; diagnostics (non-gating, never rescue). Final status is exactly one of the three D206
strings.

    PYTHONPATH=src python research/phase11/cp1/P11_CP1_result.py
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
from qresearch import p11h026 as P  # noqa: E402

STATUS = dict(
    candidate="H026 DEVELOPMENT CANDIDATE — LEARNED SCORE FROZEN, FINAL HOLDOUT SEALED",
    rejected="H026 REJECTED — LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY",
    blocked="H026 BLOCKED — DATA v2.1 EXTENSION / PIPELINE INVALID")


def year_maxdd(daily, days):
    yrs = np.array([int(str(np.datetime64(int(d), "D"))[:4]) for d in days])
    eq = np.asarray(daily, float)
    return {int(y): H.max_drawdown(eq[yrs == y]) for y in H.OUTER_YEARS if np.any(yrs == y)}


def assess(st, o, prov, pins):
    """st: the host's QRW statistics; o: the unpacked QRWR block; pins: c_wealth, feature/response panel digests,
    null result hash, threshold commit (qresearch.p11h026)."""
    c_w = pins["c_wealth"]
    pins_ok = (st["provenance"]["c_wealth"] == c_w and st["feature_panel_sha256"] == pins["feature_panel_sha256"]
               and st["response_panel_sha256"] == pins["response_panel_sha256"]
               and st["provenance"]["null_result_sha256"] == pins["null_result_sha256"]
               and st["provenance"]["threshold_commit"] == pins["threshold_commit"]
               and all(v == 0 for v in st["pit_audit"].values()))
    yh = {int(k): v for k, v in o["years_h026"].items()}
    ys = {int(k): v for k, v in o["years_spy"].items()}
    g = H.gates(o["h026"], o["spy"], yh, ys, o["stress"]["h026"], o["stress"]["spy"], c_w)
    host = o["gates"]
    same = all(g[k] == host[k] for k in ("D1", "D2", "D3", "D4", "D5", "all")) and \
        abs(g["S_WEALTH"] - host["S_WEALTH"]) < 1e-12
    days = np.asarray(o["days"], float)
    mdd_h, mdd_s = year_maxdd(o["daily_h026"], days), year_maxdd(o["daily_spy"], days)
    coef = o["coefficients"]
    B = np.array([coef[str(y)]["beta"] for y in H.OUTER_YEARS], float)
    adj = [float(np.corrcoef(B[i], B[i + 1])[0, 1]) for i in range(len(B) - 1)]
    stab = {f: dict(mean=float(B[:, j].mean()), sd=float(B[:, j].std(ddof=1)),
                    positive_years=int((B[:, j] > 0).sum()), sign_flips=int((np.diff(np.sign(B[:, j])) != 0).sum()),
                    min=float(B[:, j].min()), max=float(B[:, j].max()))
            for j, f in enumerate(H.FEATURES)}
    tr = o["trades"]
    turn = np.asarray(tr["turnover"], float)
    msel = o["months"]
    turn_year = {}
    for d, t in zip(msel, turn):
        y = int(d[:4]) + (1 if d[5:7] == "12" else 0)            # December review = entry in the next year
        turn_year[y] = turn_year.get(y, 0.0) + float(t)
    years = {str(y): dict(lam=coef[str(y)]["lam"], beta=dict(zip(H.FEATURES, coef[str(y)]["beta"])),
                          b0=coef[str(y)]["b0"], h026=yh[y], spy=ys[y], L=g["L"][y],
                          turnover=turn_year.get(y), maxdd_h026=mdd_h.get(y), maxdd_spy=mdd_s.get(y))
             for y in H.OUTER_YEARS}
    h, s = o["h026"], o["spy"]
    blocked = not pins_ok or not same
    status = STATUS["blocked"] if blocked else (STATUS["candidate"] if g["all"] else STATUS["rejected"])
    out = dict(
        status=status, pins_ok=pins_ok, host_gates_reproduced=same,
        gates=dict(c_wealth=c_w, S_WEALTH=g["S_WEALTH"], D1=g["D1"], D2=g["D2"], D3=g["D3"], D4=g["D4"],
                   D5=g["D5"], all=g["all"], largest_positive_year_share=g["largest_share"],
                   years_beating=int(sum(1 for v in g["L"].values() if v > 0)),
                   L_2015_2017=float(sum(g["L"][y] for y in (2015, 2016, 2017))),
                   L_2018_2021=float(sum(g["L"][y] for y in (2018, 2019, 2020, 2021))),
                   wealth_ratio=h["wealth"] / s["wealth"], excess_cagr=h["cagr"] - s["cagr"],
                   maxdd_ratio=abs(h["maxdd"]) / abs(s["maxdd"]), vol_ratio=h["vol"] / s["vol"],
                   stress_0p20=dict(h026=o["stress"]["h026"], spy=o["stress"]["spy"])),
        portfolio=dict(h026=h, spy=s, trades=dict(buys=tr["buys"], sells=tr["sells"], trades=tr["trades"],
                                                  commissions=tr["commissions"], slippage=tr["slippage"],
                                                  turnover_monthly_mean=float(turn.mean()),
                                                  turnover_annual_mean=float(np.mean(list(turn_year.values()))),
                                                  holdings_mean=float(np.mean(tr["holdings"])),
                                                  cash_share_mean=float(np.mean(tr["cash_share"])),
                                                  cash_utilisation=1.0 - float(np.mean(tr["cash_share"]))),
                       sector_counts=o["sector_counts"],
                       sector_max_share=max(o["sector_counts"].values()) / sum(o["sector_counts"].values())),
        years=years, coefficient_stability=dict(by_feature=stab, adjacent_year_correlation=adj),
        inner_selection=o["selection"], inner=o["inner"], diagnostics=o["diagnostics"],
        final_model=o.get("final_model"),
        provenance=dict(git_commit=prov["git_commit"], lean_version=prov["lean_version"],
                        qc_backtest_id=prov["qc_backtest_id"], code_sha256=prov["code_sha256"]),
        pit_audit=st["pit_audit"], runtime=dict(wall_s=st.get("wall_s"), max_rss_mb=st.get("max_rss_mb")))
    assert math.isfinite(g["S_WEALTH"])
    return out


def main(exp=P.REAL):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRW"))
    blob = joined(ls, "QRWR")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"], "real blob hash"
    o = json.loads(E.unpack(blob))
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    out = assess(st, o, prov, dict(c_wealth=P.C_WEALTH, feature_panel_sha256=P.FEATURE_PANEL_SHA256,
                                   response_panel_sha256=P.RESPONSE_PANEL_SHA256,
                                   null_result_sha256=P.NULL_RESULT_SHA256, threshold_commit=P.THRESHOLD_COMMIT))
    out["experiment"] = exp
    status, h, s, years = out["status"], out["portfolio"]["h026"], out["portfolio"]["spy"], out["years"]
    (HERE / "P11_CP1_result.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps(dict(status=status, gates=out["gates"], h026={k: h[k] for k in (
        "wealth", "cagr", "vol", "sharpe", "maxdd")}, spy={k: s[k] for k in ("wealth", "cagr", "vol", "sharpe", "maxdd")},
        years={y: (round(v["h026"], 4), round(v["spy"], 4), v["lam"]) for y, v in years.items()}), indent=1,
        default=float))


if __name__ == "__main__":
    main(*sys.argv[1:])
