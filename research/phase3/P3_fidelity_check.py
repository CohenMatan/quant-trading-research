"""Phase 3 engine fidelity check (P3-CP2): the shadow engine's replay of the completed control books (run E984-01) vs
the same books' LEAN results (E982-02, E017-03..07), sessions 2010-03-01 .. 2017-12-29, against the tolerances in
research/phase3/P3_fidelity_tolerances.json (declared and committed before any fidelity run). Compares mechanics only
(entries, exits, quantities, prices, costs, cash, equity path); no strategy is evaluated.

    PYTHONPATH=src python research/phase3/P3_fidelity_check.py [E984-01] -> research/phase3/P3_fidelity_check.json
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TOL = json.loads((ROOT / "research/phase3/P3_fidelity_tolerances.json").read_text())["per_book_tolerances"]
OUT = Path(__file__).with_name("P3_fidelity_check.json")
END = "2017-12-31"


def lines(exp):
    q = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def lean_book(exp):
    d = ROOT / "experiments" / exp
    f = pd.read_csv(gzip.open(d / "fills.csv.gz"))
    f = f[f["date"].astype(str) <= END].copy()
    eq = pd.read_csv(gzip.open(d / "equity.csv.gz"))
    eq = eq[eq["date"].astype(str) <= END]
    return f, eq


def compare(book, f_lean, eq_lean, sh_fills, sh_eq):
    t = TOL
    lb = f_lean[f_lean["quantity"] > 0]
    ls = f_lean[f_lean["quantity"] < 0]
    sb = sh_fills[sh_fills["qty"] > 0]
    ss = sh_fills[sh_fills["qty"] < 0]
    kb = {(d, s): (q, p) for d, s, q, p in zip(lb["date"], lb["symbol_id"], lb["quantity"], lb["price"])}
    kbs = {(d, s): (q, p) for d, s, q, p in zip(sb["date"], sb["sid"], sb["qty"], sb["px"])}
    match_b = set(kb) & set(kbs)
    q_exact = sum(1 for k in match_b if abs(kb[k][0] - kbs[k][0]) < 0.5)
    p_exact = sum(1 for k in match_b if abs(kb[k][1] - kbs[k][1]) / kb[k][1] <= t["fill_price_rel_diff_max"])
    ks = {(d, s) for d, s in zip(ls["date"], ls["symbol_id"])}
    kss = {(d, s) for d, s in zip(ss["date"], ss["sid"])}
    n_l, n_s = len(f_lean), len(sh_fills)
    comm_l, comm_s = float(f_lean["fee"].sum()), float(sh_fills["fee"].sum())
    e = eq_lean.set_index(eq_lean["date"].astype(str))
    x = sh_eq.reindex(e.index)
    r_l = e["equity"].astype(float).pct_change().dropna()
    r_s = x["equity"].astype(float).pct_change().reindex(r_l.index)
    dr = (r_l - r_s).abs()
    cash_dev = ((e["cash"].astype(float) - x["cash"].astype(float)).abs() / e["equity"].astype(float))
    forced_l = int((~f_lean["tag"].astype(str).str.startswith("s017")).sum())
    forced_s = int(sh_fills["kind"].isin(["delist", "stale"]).sum())
    slip_l = float((f_lean["quantity"].abs() * f_lean["price"]).sum())  # notional proxy for slippage (10 bps of it)
    slip_s = float((sh_fills["qty"].abs() * sh_fills["px"]).sum())
    res = dict(
        lean_buys=len(lb), shadow_buys=len(sb), buy_match_share=len(match_b) / max(len(kb), 1),
        buy_quantity_exact_share=q_exact / max(len(match_b), 1), fill_price_exact_share=p_exact / max(len(match_b), 1),
        lean_sells=len(ls), shadow_sells=len(ss), sell_match_share=len(ks & kss) / max(len(ks), 1),
        trade_count_diff_share=abs(n_l - n_s) / max(n_l, 1),
        commission_lean=comm_l, commission_shadow=comm_s, commission_rel_diff=abs(comm_l - comm_s) / max(comm_l, 1),
        notional_rel_diff=abs(slip_l - slip_s) / max(slip_l, 1),
        daily_return_rmse=float(np.sqrt((dr ** 2).mean())), daily_return_abs_diff_max=float(dr.max()),
        terminal_lean=float(e["equity"].iloc[-1]), terminal_shadow=float(x["equity"].iloc[-1]),
        terminal_rel_diff=abs(float(e["equity"].iloc[-1]) - float(x["equity"].iloc[-1])) / float(e["equity"].iloc[-1]),
        cash_within_tol_share=float((cash_dev <= t["cash_rel_equity_diff_max"]).mean()),
        cash_dev_max=float(cash_dev.max()), forced_lean=forced_l, forced_shadow=forced_s,
        missing_shadow_days=int(x["equity"].isna().sum()),
        unmatched_buys_examples=sorted(set(kb) - set(kbs))[:5], extra_shadow_buys=sorted(set(kbs) - set(kb))[:5],
        unmatched_sells_examples=sorted(ks - kss)[:5])
    ok = dict(
        buy_match=res["buy_match_share"] >= t["buy_match_share_min"],
        buy_quantity=res["buy_quantity_exact_share"] >= t["buy_quantity_exact_share_min"],
        sell_match=res["sell_match_share"] >= t["sell_match_share_min"],
        trade_count=res["trade_count_diff_share"] <= t["trade_count_diff_max_share"],
        fill_price=res["fill_price_exact_share"] >= t["fill_price_exact_share_min"],
        commission=res["commission_rel_diff"] <= t["commission_total_rel_diff_max"],
        slippage=res["notional_rel_diff"] <= t["slippage_total_rel_diff_max"],
        daily_rmse=res["daily_return_rmse"] <= t["daily_return_rmse_max"],
        daily_max=res["daily_return_abs_diff_max"] <= t["daily_return_abs_diff_max"],
        terminal=res["terminal_rel_diff"] <= t["terminal_wealth_rel_diff_max"],
        cash=res["cash_within_tol_share"] >= t["cash_within_tolerance_share_min"],
        forced=(res["forced_lean"] == res["forced_shadow"]) if t["forced_exit_count_equal"] else True,
        complete=res["missing_shadow_days"] == 0)
    res["checks"] = ok
    res["ok"] = all(ok.values())
    return res


def main(exp="E984-01"):
    L = lines(exp)
    summ = next(json.loads(x.split("|", 2)[2]) for x in L if x.startswith("QRX984|summary|"))
    from importlib import util
    spec = util.spec_from_file_location("qr_p3_replay", ROOT / "src/qresearch/lean/qr_p3_replay.py")
    sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    books = mod.load_replay()["books"]
    rows = [x.split("|") for x in L if x.startswith("D|")]
    fills = [x.split("|") for x in L if x.startswith("F|")]
    F = pd.DataFrame([dict(book=int(b), date=d, sid=s, kind=k, qty=float(q), px=float(p), fee=float(fe))
                      for _, b, d, s, k, q, p, fe in fills])
    out = dict(experiment=exp, engine_summary=summ, tolerances=TOL, books={})
    for i, e in enumerate(books):
        eq = pd.DataFrame([dict(date=r[1], equity=float(r[2].split(";")[i].split(",")[0]),
                                cash=float(r[2].split(";")[i].split(",")[1])) for r in rows]).set_index("date")
        fl, el = lean_book(e)
        out["books"][e] = compare(e, fl, el, F[F["book"] == i] if len(F) else F, eq)
    out["all_ok"] = all(b["ok"] for b in out["books"].values())
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    for e, b in out["books"].items():
        print(e, "OK" if b["ok"] else "FAIL", {k: v for k, v in b["checks"].items() if not v},
              dict(rmse=round(b["daily_return_rmse"], 7), term=round(b["terminal_rel_diff"], 6),
                   buys=(b["lean_buys"], b["shadow_buys"]), forced=(b["forced_lean"], b["forced_shadow"])))
    print("all_ok", out["all_ok"])
    return out


if __name__ == "__main__":
    main(*(sys.argv[1:2] or []))
