"""H017 development evaluation, written and committed BEFORE any H017 candidate, control or diagnostic run
(research/phase2/H017_spec.md, frozen 2026-10-03). Every decision is mechanical, via qresearch.p2h017 and the frozen
Amendment 3 (qresearch.wealth), on the common window 2010-03-01 -> 2021-12-31 for every book:
  1. Gates on the single candidate E017-01: W1 vs SPY (E900-07), W2, W3 vs EW-H017 (E017-02) and the median CAGR of the
     random-event books E017-03..07 (each reported), R1-R4 (R4 inputs from the run records).
  2. Which conditional runs the rules allow (E017-09; E017-10..17).
  3. G4' (only if E017-09..17 exist), PbNQ rules 1-7 (rule 7 from E983-01), the decision tree (Case A / B / C).
  4. Diagnostics (never gates): terminal-wealth tables, rolling 1/3/5/10-year reports, yearly returns, each random
     book, the $200K sensitivity, cost stress, costs, slot usage.
Runs that are missing or not completed are reported as such (never guessed); a gate that cannot be evaluated fails.

    PYTHONPATH=src python research/phase2/H017_eval.py        -> research/phase2/H017_results.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from qresearch import p2h017 as H, p2spec, results, wealth  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
OUT = Path(__file__).with_name("H017_results.json")
ALL = [f"E017-{i:02d}" for i in range(1, 18)]


def load(eid):
    d = EXP / eid
    if not (d / "result.json").exists():
        return None
    res = json.loads((d / "result.json").read_text())
    if not str(res.get("status", "")).startswith("completed"):
        return None
    return dict(cfg=json.loads((d / "config.json").read_text()), res=res,
                eq=results.read_csv_gz(d / "equity.csv.gz"), fi=results.read_csv_gz(d / "fills.csv.gz"))


def status(eid):
    d = EXP / eid / "result.json"
    return json.loads(d.read_text()).get("status") if d.exists() else "not run"


def eq_of(r):
    return H.window_eq(p2spec.equity_series(r["eq"]))


def lines_of(r):
    q = r["res"]["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def r4_inputs(r):
    """R4: realised costs a year; no leverage (gross <= 1, no negative cash or quantity); limits (holdings <= slots,
    every entry <= 10% of equity when placed: the EP lines' planned weights, one per buy order)."""
    cfg = r["cfg"]
    slip = cfg["costs"]["slippage_bps"] * cfg["costs"].get("slippage_stress_multiple", 1) / 1e4
    eq = eq_of(r)
    cost = p2spec.cost_drag(r["fi"], eq, slip)
    hs = r["res"].get("harness_summary", {})
    no_lev = bool(hs.get("max_gross", 2.0) <= 1.0 + 1e-9 and hs.get("min_cash_frac", -1.0) >= 0.0
                  and hs.get("negative_qty", 1) == 0)
    df = r["eq"]
    slots = int(cfg["params"].get("slots", 10))
    msgs = lines_of(r)
    w_pl = [float(x.split("|")[4]) for x in msgs if x.startswith("EP|")]   # planned weight at placement (spec §9.10)
    max_w = max(w_pl) if w_pl else float("nan")
    n_buy_orders = int(r["fi"].loc[r["fi"]["quantity"] > 0, "order_id"].nunique())
    limits = bool(int(df["npos"].max()) <= slots and w_pl and len(w_pl) >= n_buy_orders
                  and max_w <= float(cfg["portfolio"]["max_position_weight"]) + 1e-9)
    return dict(cost=cost, no_leverage=no_lev, limits_ok=limits, max_entry_weight=max_w, max_holdings=int(df["npos"].max()))


def book_report(eid, r, spy_eq):
    eq = eq_of(r)
    rr = p2spec.returns(eq)
    df = r["eq"][(r["eq"]["date"].astype(str) >= H.COMMON_START) & (r["eq"]["date"].astype(str) <= H.END)]
    cash_share = df["cash"].astype(float) / df["equity"].astype(float)
    sp = spy_eq.reindex(eq.index)
    out = dict(exp=eid, status=r["res"]["status"], book=r["cfg"]["params"].get("book"),
               seed=r["cfg"]["params"].get("seed"), cash=r["cfg"]["cash"], cagr=wealth.cagr(rr.to_numpy()),
               sharpe=wealth.sharpe(rr.to_numpy()), max_dd=wealth.max_drawdown(rr.to_numpy()),
               wealth_vs_spy=wealth.wealth_table(eq.to_numpy(), sp.to_numpy()),
               invested_mean=float((1 - cash_share).mean()), npos_mean=float(df["npos"].astype(float).mean()),
               integrity_ok=all(c["ok"] for c in r["res"].get("integrity", [])))
    if out["book"] != "ew":
        out["r4"] = r4_inputs(r)
        out["slot_usage"] = out["npos_mean"] / int(r["cfg"]["params"].get("slots", 10))
    return out


def lab(k):
    return {"H": "H017 (E017-01)", "SPY": "SPY (E900-07)", "EW": "EW-H017 (E017-02)"}.get(
        k, f"random seed {H.SEEDS.get(k)} ({k})")


def yearly(r):
    return {str(y): float((1 + r[r.index.str[:4] == str(y)]).prod() - 1) for y in range(2010, 2022)}


def w1_of(eid, spy_eq):
    r = load(eid)
    if r is None:
        return None
    R = H.aligned_returns({"h": eq_of(r), "spy": spy_eq})
    return bool(wealth.cagr(R["h"].to_numpy()) > wealth.cagr(R["spy"].to_numpy()))


def main(out_path=None):
    out = dict(spec=H.SPEC, spec_sha256=H.spec_hash(), spec_hash_ok=H.spec_hash() == H.SPEC_SHA256,
               event_table_sha256=H.event_manifest()["payload_sha256"],
               event_table_ok=H.event_manifest()["payload_sha256"] == H.EVENT_TABLE_SHA256,
               amendment3_ok=wealth.spec_hash() == wealth.AMENDMENT3_SHA256, window=[H.COMMON_START, H.END],
               status={e: status(e) for e in ALL + [H.EVENT_DIAG, H.CANARY]})
    spy_eq = H.window_eq(p2spec.equity_series(load(H.SPY_ID)["eq"]))
    cand, ew = load(H.CANDIDATE), load(H.EW_H017)
    rnd = {e: load(e) for e in H.RANDOM}
    if cand is None or ew is None or any(v is None for v in rnd.values()):
        out.update(note="candidate, EW-H017 or a random-event book missing / not completed: no decision possible; "
                        "every gate that cannot be evaluated fails", decision=None)
        Path(out_path or OUT).write_text(json.dumps(out, indent=1, default=float) + "\n")
        print(json.dumps(out["status"], indent=1))
        return out
    eqs = {"H": eq_of(cand), "SPY": spy_eq, "EW": eq_of(ew), **{e: eq_of(r) for e, r in rnd.items()}}
    R = H.aligned_returns(eqs)
    r4 = r4_inputs(cand)
    g = H.gates(R, "H", "SPY", "EW", list(H.RANDOM), r4["cost"]["total_pa"], r4["no_leverage"], r4["limits_ok"])
    out["gates"] = g
    d = wealth.log_excess(R["H"].to_numpy(), R["SPY"].to_numpy())
    out["w2_components"] = dict(g=g["W2"]["g"], se_iid=wealth.se_iid(d),
                                se_stationary_bootstrap=wealth.se_stationary_bootstrap(d, wealth.W2_MEAN_BLOCK),
                                se_used=g["W2"]["se"], ratio=g["W2"]["z"], critical=wealth.W2_CRITICAL,
                                threshold=g["W2"]["threshold"], mean_block=wealth.W2_MEAN_BLOCK, n_days=len(d))
    out["r4_inputs"] = r4
    out["conditional_runs_allowed"] = H.conditional_runs(g)
    out["case_path_after_committed_set"] = ("C (W1-W3, R1-R4 pass: run E017-09..17 + E983-01)" if g["core_ok"] and g["R4"]["ok"]
                                            else "B (PbNQ rules 1-5 hold: run E017-09 + E983-01 only)"
                                            if out["conditional_runs_allowed"][H.SLIP_2X] else "A (stop)")
    w1_2x = w1_of(H.SLIP_2X, spy_eq)
    pert = [w1_of(e, spy_eq) for e in H.PERTURBATIONS]
    g4 = wealth.g4_prime(None if any(p is None for p in pert) else pert, w1_2x) if g["core_ok"] and g["R4"]["ok"] \
        else None
    out["g4_prime"] = g4 if g4 is not None else "not evaluated: W1-W3 / R1-R4 do not all pass (spec §7)"
    ev_path = ROOT / "research/phase2/h017/E983_results.json"
    ev = json.loads(ev_path.read_text())["pbnq_rule_7"] if ev_path.exists() else None
    pb = H.pbnq(g, w1_2x, ev)
    out["pbnq"] = pb
    out["decision"] = H.decide(g, g4, pb)
    # ---- diagnostics (never gates)
    books = {e: book_report(e, r, spy_eq) for e in ALL if (r := load(e)) is not None}
    out["books"] = books
    out["diagnostics_not_gates"] = dict(
        wealth_table=wealth.wealth_table(eqs["H"].reindex(R.index.insert(0, eqs["H"].index[0])).to_numpy(),
                                         spy_eq.reindex(R.index.insert(0, spy_eq.index[0])).to_numpy()),
        wealth_tables={lab(k): wealth.wealth_table(np.concatenate([[1.0], np.cumprod(1 + R[k].to_numpy())]) * 100000.0,
                                                   np.concatenate([[1.0], np.cumprod(1 + R["SPY"].to_numpy())]))
                       for k in R.columns if k != "SPY"},
        rolling_vs_spy=wealth.rolling_report(R["H"].to_numpy(), R["SPY"].to_numpy()),
        rolling_ew_vs_spy=wealth.rolling_report(R["EW"].to_numpy(), R["SPY"].to_numpy()),
        rolling_all_vs_spy={lab(k): wealth.rolling_report(R[k].to_numpy(), R["SPY"].to_numpy())
                            for k in R.columns if k != "SPY"},
        book_metrics={lab(k): dict(cagr=wealth.cagr(R[k].to_numpy()), sharpe=wealth.sharpe(R[k].to_numpy()),
                                   max_dd=wealth.max_drawdown(R[k].to_numpy())) for k in R.columns},
        yearly={k: yearly(R[k]) for k in R.columns},
        random_books={f"seed {H.SEEDS[e]}": dict(cagr=wealth.cagr(R[e].to_numpy()),
                                                 sharpe=wealth.sharpe(R[e].to_numpy())) for e in H.RANDOM},
        sizing_200k=dict(books.get(H.SIZING_200K, {"status": status(H.SIZING_200K)}),
                         note="sensitivity only: never decides, never rescues"),
        cost_stress={m: books.get(e, {"status": status(e)}) for m, e in ((2, H.SLIP_2X), (4, H.SLIP_4X),
                                                                        (6, H.SLIP_6X))})
    Path(out_path or OUT).write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(dict(W1=g["W1"]["ok"], W2=g["W2"]["ok"], W3=g["W3"]["ok"], R1=g["R1"]["ok"], R2=g["R2"]["ok"],
                          R3=g["R3"]["ok"], R4=g["R4"]["ok"], decision=out["decision"]["case"]), indent=1))
    return out


if __name__ == "__main__":
    main()
