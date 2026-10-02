"""H016 development evaluation, written and committed BEFORE any H016 candidate run (research/phase2/H016_spec.md,
frozen, D116). Every decision is mechanical, via qresearch.p2h016 (common window 2010-03-01 -> 2021-12-31 for every
book):
  1. Gates on the single candidate E016-01 (§8): G1 vs EW-H016 (E016-02) and SPY (E900-07); G2 vs the median Sharpe of
     the five random controls (E016-03..07, each reported); G3 two-year blocks vs EW-H016; G4 perturbations, 2x
     slippage, realised cost drag.
  2. Robustness trigger (§9): recorded here; E016-09..17 are written by H016_make_configs.py --robustness only if it
     holds.
  3. Diagnostics (§10, never gates): survivorship sensitivity S1/S2, DSR at three counts, PBO, paired block-bootstrap
     intervals, per-year and per-block tables, whether the ranking adds value (candidate vs each random seed by block),
     exposure/turnover/cash/slot usage and costs incl. the separate top-up cost accounting for every book, $200K
     sensitivity, 4x/6x costs, the broad EW (E901-07) reference, universe coverage per rebalance.
  4. Classification (§11) and whether the Holdout may be requested.
Runs that are missing or not completed are reported as such (never guessed); a gate that cannot be evaluated fails.

    PYTHONPATH=src python research/phase2/H016_eval.py        -> research/phase2/H016_results.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from qresearch import metrics, p2h016 as H, p2spec, registry, results, stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
sys.path.insert(0, str(ROOT / "research/phase2/sec"))
from e970_parse import lines  # noqa: E402

ALL = [f"E016-{i:02d}" for i in range(1, 18)]
SEEDS = dict(zip(H.RANDOM, (1, 2, 3, 4, 5)))


def load(eid):
    d = EXP / eid
    if not (d / "result.json").exists():
        return None
    res = json.loads((d / "result.json").read_text())
    if not str(res.get("status", "")).startswith("completed"):
        return None
    return dict(cfg=json.loads((d / "config.json").read_text()), res=res,
                eq=results.read_csv_gz(d / "equity.csv.gz"), tr=results.read_csv_gz(d / "trades.csv.gz"),
                fi=results.read_csv_gz(d / "fills.csv.gz"))


def status(eid):
    d = EXP / eid / "result.json"
    return json.loads(d.read_text()).get("status") if d.exists() else "not run"


_C = {}


def run(eid):
    if eid not in _C:
        r = load(eid)
        if r is None:   # a technical repeat (identical config after an operational failure) stands in (D069/D099)
            for p in sorted(EXP.glob("E016-*/config.json")) + sorted(EXP.glob("E980-*/config.json")):
                c = json.loads(p.read_text())
                if c.get("technical_repeat_of") == eid:
                    r = load(c["experiment_id"]) or r
        _C[eid] = r
    return _C[eid]


def eq_of(eid):
    r = run(eid)
    return None if r is None else H.window_eq(p2spec.equity_series(r["eq"]))


def ret_of(eid):
    e = eq_of(eid)
    return None if e is None else p2spec.returns(e)


def summary(eid):
    try:
        for ln in lines(run(eid)["cfg"]["experiment_id"]):
            if ln.startswith("QRS016|summary|"):
                return json.loads(ln.split("|", 2)[2])
    except Exception:
        return None
    return None


def rebalance_lines(eid):
    try:
        return [x.split("|") for x in lines(run(eid)["cfg"]["experiment_id"]) if x.startswith("RB|")]
    except Exception:
        return []


def book(eid):
    r = run(eid)
    if r is None:
        return dict(exp=eid, status=status(eid))
    cfg = r["cfg"]
    eq = eq_of(eid)
    rr = p2spec.returns(eq)
    slip = cfg["costs"]["slippage_bps"] * cfg["costs"].get("slippage_stress_multiple", 1) / 1e4
    df = r["eq"][(r["eq"]["date"].astype(str) >= H.COMMON_START) & (r["eq"]["date"].astype(str) <= H.END)]
    cash_share = df["cash"].astype(float) / df["equity"].astype(float)
    slots = int(cfg["params"].get("slots", 20))
    closed = r["tr"][r["tr"]["status"] == "closed"] if len(r["tr"]) else r["tr"]
    out = dict(exp=eid, status=r["res"]["status"], book=cfg["params"].get("book"), seed=cfg["params"].get("seed"),
               cash=cfg["cash"], sharpe=p2spec.sharpe(rr), cagr=metrics.cagr(eq), max_dd=metrics.max_drawdown(eq),
               calmar=p2spec.calmar(eq), vol=float(rr.std(ddof=1) * math.sqrt(252)), final_equity=float(eq.iloc[-1]),
               costs=H.cost_drag(r["fi"], p2spec.equity_series(r["eq"]), slip),
               exposure_mean=float((1 - cash_share).mean()), cash_mean=float(cash_share.mean()),
               cash_min=float(cash_share.min()), npos_mean=float(df["npos"].astype(float).mean()),
               npos_max=int(df["npos"].max()), trades=metrics.trade_stats(r["tr"]),
               profit_concentration=stats.profit_concentration(closed["pnl"]) if len(closed) else None,
               skipped_min_position=r["res"].get("harness_summary", {}).get("skipped_min_position"),
               integrity_ok=all(c["ok"] for c in r["res"].get("integrity", [])),
               strategy_summary=summary(eid))
    if cfg["params"].get("book") != "ew":
        out["slot_usage"] = float(df["npos"].astype(float).mean() / slots)
        out["topup_costs"] = H.topup_costs(r["fi"], p2spec.equity_series(r["eq"]), slip)
    return out


def blocks_vs(r_h, r_x):
    return [dict(block=f"{a[:4]}-{z[:4]}",
                 d_sharpe=p2spec.sharpe(p2spec.window(r_h, a, z)) - p2spec.sharpe(p2spec.window(r_x, a, z)))
            for a, z in p2spec.BLOCKS]


def yearly(r):
    return {str(y): dict(ret=float((1 + r[r.index.str[:4] == str(y)]).prod() - 1),
                         sharpe=p2spec.sharpe(r[r.index.str[:4] == str(y)])) for y in range(2010, 2022)}


def trial_counts():
    acc = registry.trial_accounting()
    rob = [e for e in acc["by_category"]["robustness"] if e.startswith("E016-")]
    return dict(p2_robustness_h016=len(rob), robustness_ids=rob, cumulative_selection=acc["selection_trials"])


def pbo(ids):
    cols = {e: ret_of(e) for e in ids if ret_of(e) is not None}
    if len(cols) < 2:
        return "not computable: single candidate"
    m = pd.concat(cols, axis=1, join="inner").dropna()
    return dict(members=list(cols), **stats.pbo_cscv(m.to_numpy(), n_blocks=16))


def main(out_path=None):
    out = dict(spec=H.SPEC, spec_sha256=H.spec_hash(), spec_hash_ok=H.spec_hash() == H.SPEC_SHA256,
               window=[H.COMMON_START, H.END])
    eq_spy = H.window_eq(p2spec.equity_series(load(H.SPY_ID)["eq"]))
    eq_bew = H.window_eq(p2spec.equity_series(load(H.EW_BROAD_ID)["eq"]))
    eq_ew = eq_of(H.EW_H016)
    out["books"] = {e: book(e) for e in ALL}
    refs = {}
    for lab, eid, e in (("SPY", H.SPY_ID, eq_spy), ("broad EW (reference)", H.EW_BROAD_ID, eq_bew)):
        rr = p2spec.returns(e)
        refs[lab] = dict(exp=eid, sharpe=p2spec.sharpe(rr), cagr=metrics.cagr(e), max_dd=metrics.max_drawdown(e),
                         calmar=p2spec.calmar(e))
    out["references"] = refs
    eq_h = eq_of(H.CANDIDATE)
    if eq_h is None or eq_ew is None:
        out.update(ok=False, note="candidate or EW-H016 missing/not completed: every gate fails",
                   status={H.CANDIDATE: status(H.CANDIDATE), H.EW_H016: status(H.EW_H016)},
                   development_qualified=False, may_request_holdout=False)
        Path(out_path or Path(__file__).parent / "H016_results.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
        print(json.dumps(out["status"]))
        return
    r_h, r_ew, r_spy = p2spec.returns(eq_h), p2spec.returns(eq_ew), p2spec.returns(eq_spy)
    g1 = H.g1(eq_h, eq_ew, eq_spy)
    s_rand = [p2spec.sharpe(ret_of(e)) if ret_of(e) is not None else float("nan") for e in H.RANDOM]
    g2 = H.g2(g1["sharpe"], s_rand)
    g2["random_status"] = {e: status(e) for e in H.RANDOM}
    g3 = H.g3(eq_h, eq_ew)
    base_cost = out["books"][H.CANDIDATE]["costs"]["total_pa"]
    trig = H.robustness_triggered(g1["ok"], g2["ok"], g3["ok"])
    pert = two = None
    pert_detail = {}
    if trig:
        se = p2spec.sharpe(r_ew)
        vals = []
        for e in H.PERTURBATIONS:
            rr = ret_of(e)
            if rr is not None:
                vals.append(p2spec.sharpe(rr) - se)
                pert_detail[e] = dict(change=run(e)["cfg"]["description"], d_ew=vals[-1])
            else:
                pert_detail[e] = dict(status=status(e))
        pert = vals if len(vals) == 6 else None
        r2 = ret_of(H.SLIP_2X)
        two = p2spec.sharpe(r2) - se if r2 is not None else None
    g4 = H.g4(pert, two, base_cost)
    g4["perturbations"] = pert_detail
    if not trig:
        g4["note"] = "G4a/G4b not run: candidate already failed G1, G2 or G3 on its base run (spec §9)"
    all_ok = bool(g1["ok"] and g2["ok"] and g3["ok"] and g4["ok"])
    out["gates"] = dict(G1=g1, G2=g2, G3=g3, G4=g4)
    out["robustness_trigger"] = trig
    out["classification"] = H.classify(metrics.cagr(eq_h), g1["ok"], g2["ok"], all_ok)
    out["development_qualified"] = all_ok
    out["may_request_holdout"] = all_ok
    # ---- diagnostics (never gates)
    tc = trial_counts()
    diag = dict(trial_counts=tc)
    diag["survivorship_sensitivity"] = H.survivorship_sensitivity(eq_h, eq_ew)
    diag["dsr"] = H.dsr_views(r_h.to_numpy(), tc["p2_robustness_h016"])
    diag["psr_0"] = stats.probabilistic_sharpe(r_h.to_numpy())
    diag["pbo"] = pbo([H.CANDIDATE] + list(H.PERTURBATIONS)) if trig else "not computable: single candidate"
    pairs = {"EW-H016": r_ew, "SPY": r_spy, **{f"random seed {SEEDS[e]}": ret_of(e) for e in H.RANDOM}}
    diag["bootstrap_sharpe_diff"] = {k: p2spec.paired_bootstrap_sharpe_diff(r_h, v) for k, v in pairs.items()
                                     if v is not None}
    rv = {f"seed {SEEDS[e]}": ret_of(e) for e in H.RANDOM if ret_of(e) is not None}
    diag["ranking_adds_value"] = dict(
        candidate_minus_random_by_block={k: blocks_vs(r_h, v) for k, v in rv.items()},
        random_minus_ew_full={k: p2spec.sharpe(v) - p2spec.sharpe(r_ew) for k, v in rv.items()},
        candidate_minus_median_random=g1["sharpe"] - g2["median_random"] if np.isfinite(g2["median_random"]) else None,
        seeds_beaten=sum(1 for v in rv.values() if g1["sharpe"] > p2spec.sharpe(v)))
    diag["blocks_vs_ew"] = g3["blocks"]
    yt = {"H016": yearly(r_h), "EW-H016": yearly(r_ew), "SPY": yearly(r_spy)}
    yt.update({f"random seed {SEEDS[e]}": yearly(ret_of(e)) for e in H.RANDOM if ret_of(e) is not None})
    diag["yearly"] = yt
    b = out["books"]
    diag["sizing_200k"] = dict(exp=H.SIZING_200K, status=b[H.SIZING_200K].get("status"),
                               sharpe=b[H.SIZING_200K].get("sharpe"), cagr=b[H.SIZING_200K].get("cagr"),
                               d_ew=(b[H.SIZING_200K]["sharpe"] - p2spec.sharpe(r_ew)) if b[H.SIZING_200K].get("sharpe")
                               is not None else None, cost_pa=(b[H.SIZING_200K].get("costs") or {}).get("total_pa"),
                               note="sensitivity only: never decides, never rescues")
    diag["cost_stress"] = {m: dict(exp=e, status=b[e].get("status"), sharpe=b[e].get("sharpe"))
                           for m, e in ((2, H.SLIP_2X), (4, H.SLIP_4X), (6, H.SLIP_6X))}
    cov = {}
    for x in rebalance_lines(H.CANDIDATE):
        cov[x[1]] = dict(eligible=int(x[2]), universe=int(x[3]), exits=int(x[4]), entries=int(x[5]))
    diag["universe_per_rebalance"] = cov
    diag["yearly_coverage_mean_universe"] = {y: float(np.mean([v["universe"] for d, v in cov.items() if d[:4] == y]))
                                             for y in sorted({d[:4] for d in cov})}
    out["diagnostics_not_gates"] = diag
    Path(out_path or Path(__file__).parent / "H016_results.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(dict(G1=g1["ok"], G2=g2["ok"], G3=g3["ok"], G4=g4["ok"], trigger=trig, qualified=all_ok,
                          classification=out["classification"]), indent=1))


if __name__ == "__main__":
    main()
