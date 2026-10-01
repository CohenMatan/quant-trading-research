"""Phase 2 H014 development evaluation, written and committed BEFORE any H014 development run
(research/phase2/P2_spec.md, frozen; D094/D095). Every decision is mechanical, via qresearch.p2spec:
  1. Candidate selection (§7): B replaces A iff D_B > D_A in both halves; else A.
  2. Gates on the chosen candidate (§8): G1 (vs EW E901-07 and SPY E900-07), G2 (controls with the same exit),
     G3 (two-year blocks), G4 (perturbations, 2x slippage, realised cost drag).
  3. Robustness trigger (§9): recorded here; the §9 configs are written by P2_make_configs.py --robustness
     only if it holds.
  4. Diagnostics (§10, never gates): DSR at three counts, PBO, paired block-bootstrap intervals, per-year and
     per-block tables, mechanism evidence vs C1/C2/R, stress episodes, trade statistics, $200K sensitivity,
     4x/6x costs, exposure/turnover/slot usage/cash for every book; the non-chosen candidate's gates.
  5. Classification (§11) and whether the Holdout may be requested.
Runs that are missing or not completed are reported as such (never guessed); a gate that cannot be
evaluated fails.

    PYTHONPATH=src python research/phase2/P2_eval.py        -> research/phase2/P2_results.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from qresearch import config, metrics, p2spec, registry, results, stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
CAND = {"A": "E014-01", "B": "E014-02"}
CONTROLS = {"A": dict(C1="E014-03", C2="E014-04", R=["E014-05", "E014-06", "E014-07"]),
            "B": dict(C1="E014-08", C2="E014-09", R=["E014-10", "E014-11", "E014-12"])}
SIZING = {"A": "E014-13", "B": "E014-14"}
STRESS = {2: "E014-15", 4: "E014-16", 6: "E014-17"}
PERTURB = ["E014-18", "E014-19", "E014-20", "E014-21", "E014-22", "E014-23"]
EPISODES = {"2011 US downgrade": ("2011-07-22", "2011-10-03"), "2015-16 sell-off": ("2015-08-01", "2016-02-11"),
            "2018 Q4": ("2018-10-01", "2018-12-24"), "2020 crash": ("2020-02-19", "2020-03-23"),
            "2020 recovery": ("2020-03-24", "2020-08-31")}


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


def summary_line(eid, prefix):
    f = EXP / eid / "messages.txt"
    if not f.exists():
        return None
    for ln in f.read_text().splitlines():
        if ln.startswith(prefix + "|summary|"):
            return json.loads(ln.split("|", 2)[2])
    return None


_CACHE = {}


def repeat_of(eid):
    """A technical repeat (identical configuration re-run after an operational failure) stands in for the run it
    repeats when that run has no completed result (D069/D099)."""
    for p in sorted(EXP.glob("E*/config.json")):
        try:
            c = json.loads(p.read_text())
        except Exception:
            continue
        if c.get("technical_repeat_of") == eid:
            return c["experiment_id"]
    return None


def run(eid):
    if eid not in _CACHE:
        r = load(eid)
        if r is None and repeat_of(eid):
            r = load(repeat_of(eid))
        _CACHE[eid] = r
    return _CACHE[eid]


def eq_of(eid):
    r = run(eid)
    return None if r is None else p2spec.equity_series(r["eq"])


def ret_of(eid):
    e = eq_of(eid)
    return None if e is None else p2spec.returns(e)


def book(eid):
    """Performance, costs and the economic-comparability profile of one completed run."""
    r = run(eid)
    if r is None:
        return dict(exp=eid, status=status(eid))
    if r["cfg"]["experiment_id"] != eid:
        eid = f"{eid} (technical repeat {r['cfg']['experiment_id']})"
    eq = p2spec.equity_series(r["eq"])
    rr = p2spec.returns(eq)
    cfg = r["cfg"]
    slip = cfg["costs"]["slippage_bps"] * cfg["costs"].get("slippage_stress_multiple", 1) / 1e4
    df = r["eq"]
    cash_share = df["cash"].astype(float) / df["equity"].astype(float)
    slots = int(cfg["params"].get("slots", 12))
    ts = metrics.trade_stats(r["tr"])
    closed = r["tr"][r["tr"]["status"] == "closed"] if len(r["tr"]) else r["tr"]
    hold_sessions = None
    if len(closed):
        cal = {d: i for i, d in enumerate(df["date"].astype(str))}
        hs = [cal[x] - cal[y] for x, y in zip(closed["exit_date"].astype(str), closed["entry_date"].astype(str))
              if x in cal and y in cal]
        hold_sessions = dict(mean=float(np.mean(hs)), median=float(np.median(hs)),
                             p10=float(np.percentile(hs, 10)), p90=float(np.percentile(hs, 90)))
    return dict(exp=eid, status=r["res"]["status"], mode=cfg["params"].get("mode"), exit=cfg["params"].get("exit"),
                seed=cfg["params"].get("seed"), cash=cfg["cash"], sharpe=p2spec.sharpe(rr), cagr=metrics.cagr(eq),
                max_dd=metrics.max_drawdown(eq), calmar=p2spec.calmar(eq), vol=float(rr.std(ddof=1) * math.sqrt(252)),
                final_equity=float(eq.iloc[-1]),
                costs=p2spec.cost_drag(r["fi"], eq, slip),
                exposure_mean=float((1 - cash_share).mean()), cash_mean=float(cash_share.mean()),
                cash_min=float(cash_share.min()), slot_usage=float(df["npos"].astype(float).mean() / slots),
                npos_mean=float(df["npos"].astype(float).mean()), npos_max=int(df["npos"].max()),
                trades=ts, holding_sessions=hold_sessions,
                profit_concentration=stats.profit_concentration(closed["pnl"]) if len(closed) else None,
                skipped_min_position=r["res"].get("harness_summary", {}).get("skipped_min_position"),
                strategy_summary=summary_line(r["cfg"]["experiment_id"], "QRS014"))


def yearly(eids):
    out = {}
    for name, eid in eids.items():
        e = eq_of(eid)
        if e is None:
            continue
        rr = p2spec.returns(e)
        out[name] = {str(y): dict(ret=float((1 + rr[rr.index.str[:4] == str(y)]).prod() - 1),
                                  sharpe=p2spec.sharpe(rr[rr.index.str[:4] == str(y)])) for y in range(2010, 2022)}
    return out


def blocks_vs(r_h, r_x):
    return [dict(block=f"{a[:4]}-{z[:4]}",
                 d_sharpe=p2spec.sharpe(p2spec.window(r_h, a, z)) - p2spec.sharpe(p2spec.window(r_x, a, z)))
            for a, z in p2spec.BLOCKS]


def gates_for(variant, r_ew, r_spy, eq_ew, eq_spy, with_robustness):
    cid = CAND[variant]
    eq_h, r_h = eq_of(cid), ret_of(cid)
    if eq_h is None:
        return dict(candidate=cid, status=status(cid), ok=False)
    ctl = CONTROLS[variant]
    s_c1 = p2spec.sharpe(ret_of(ctl["C1"])) if ret_of(ctl["C1"]) is not None else float("nan")
    s_c2 = p2spec.sharpe(ret_of(ctl["C2"])) if ret_of(ctl["C2"]) is not None else float("nan")
    s_r = [p2spec.sharpe(ret_of(e)) for e in ctl["R"] if ret_of(e) is not None]
    g1 = p2spec.g1(eq_h, eq_ew, eq_spy)
    g2 = p2spec.g2(g1["sharpe"], s_c1, s_c2, s_r)
    g2.update(sharpe_c1=s_c1, sharpe_c2=s_c2, sharpe_r=s_r)
    g3 = p2spec.g3(r_h, r_ew)
    base_cost = book(cid)["costs"]["total_pa"]
    trig = p2spec.robustness_triggered(g1["ok"], g2["ok"], g3["ok"])
    pert = two = None
    pert_detail = {}
    if with_robustness and trig:
        se = p2spec.sharpe(r_ew)
        vals = []
        for e in PERTURB:
            rr = ret_of(e)
            if rr is not None and run(e)["cfg"].get("robustness_of") == cid:
                vals.append(p2spec.sharpe(rr) - se)
                pert_detail[e] = dict(change=run(e)["cfg"]["description"], d_ew=vals[-1])
            else:
                pert_detail[e] = dict(status=status(e))
        pert = vals if len(vals) == 6 else None
        r2 = ret_of(STRESS[2])
        two = p2spec.sharpe(r2) - se if r2 is not None and run(STRESS[2])["cfg"].get("robustness_of") == cid else None
    g4 = p2spec.g4(pert, two, base_cost)
    g4["perturbations"] = pert_detail
    if not (with_robustness and trig):
        g4["note"] = "G4a/G4b not run: " + ("candidate not chosen" if not with_robustness else
                                            "the chosen candidate failed G1, G2 or G3 on its base run (spec §9)")
    all_ok = bool(g1["ok"] and g2["ok"] and g3["ok"] and g4["ok"])
    return dict(candidate=cid, variant=variant, G1=g1, G2=g2, G3=g3, G4=g4, robustness_trigger=trig, ok=all_ok,
                classification=p2spec.classify(metrics.cagr(eq_h), g1["ok"], g2["ok"], all_ok))


def trial_counts():
    acc = registry.trial_accounting()
    p2 = {e for e in acc["genuine"]
          if json.loads((config.EXPERIMENTS_DIR / e / "config.json").read_text()).get("programme") == "P2"}
    sel = [e for e in acc["by_category"]["selection"] if e in p2]
    rob = [e for e in acc["by_category"]["robustness"] if e in p2]
    return dict(p2_selection=len(sel), p2_robustness=len(rob), p2_broad=len(sel) + len(rob),
                cumulative_selection=acc["selection_trials"],
                cumulative_conservative=acc["selection_trials"] + acc["replicate_runs"] + acc["robustness_runs"]
                + acc["validation_runs"], p2_selection_ids=sel, p2_robustness_ids=rob,
                p2_runs_registered=sorted({r["experiment_id"] for r in registry.read()
                                           if r["experiment_id"].startswith(("E014", "E965")) and r["run_type"] == "original"}))


def pbo(ids):
    cols = {e: ret_of(e) for e in ids if ret_of(e) is not None}
    if len(cols) < 2:
        return None
    m = pd.concat(cols, axis=1, join="inner").dropna()
    return dict(members=list(cols), **stats.pbo_cscv(m.to_numpy(), n_blocks=16))


def main(out_path=None):
    eq_ew, eq_spy = p2spec.equity_series(load(p2spec.EW_ID)["eq"]), p2spec.equity_series(load(p2spec.SPY_ID)["eq"])
    eq_ew = eq_ew[(eq_ew.index >= p2spec.DEV[0]) & (eq_ew.index <= p2spec.DEV[1])]
    eq_spy = eq_spy[(eq_spy.index >= p2spec.DEV[0]) & (eq_spy.index <= p2spec.DEV[1])]
    r_ew, r_spy = p2spec.returns(eq_ew), p2spec.returns(eq_spy)
    out = dict(spec=p2spec.SPEC, spec_sha256=p2spec.spec_hash(), spec_hash_ok=p2spec.spec_hash() == p2spec.SPEC_SHA256,
               benchmarks=dict(EW=dict(exp=p2spec.EW_ID, sharpe=p2spec.sharpe(r_ew), cagr=metrics.cagr(eq_ew),
                                       max_dd=metrics.max_drawdown(eq_ew), calmar=p2spec.calmar(eq_ew)),
                               SPY=dict(exp=p2spec.SPY_ID, sharpe=p2spec.sharpe(r_spy), cagr=metrics.cagr(eq_spy),
                                        max_dd=metrics.max_drawdown(eq_spy), calmar=p2spec.calmar(eq_spy))))
    ids = [f"E014-{i:02d}" for i in range(1, 24)]
    out["books"] = {e: book(e) for e in ids}
    # 1. selection
    ra, rb = ret_of(CAND["A"]), ret_of(CAND["B"])
    if ra is None or rb is None:
        out["selection"] = dict(chosen=None, note="a candidate run is missing or not completed; A stays primary only "
                                "if B is missing", status={k: status(v) for k, v in CAND.items()})
        chosen = "A" if ra is not None else None
    else:
        sel = p2spec.choose_candidate(ra, rb, r_ew)
        chosen = sel["chosen"]
        out["selection"] = sel
    out["selection"]["chosen_id"] = CAND.get(chosen)
    # 2. gates (chosen: with the §9 robustness runs; the other candidate: diagnostic only)
    out["gates"] = {}
    for v in ("A", "B"):
        if run(CAND[v]) is None:
            continue
        g = gates_for(v, r_ew, r_spy, eq_ew, eq_spy, with_robustness=(v == chosen))
        g["role"] = "CHOSEN candidate (decisive)" if v == chosen else "not chosen (diagnostic only; cannot qualify)"
        if v != chosen:
            g["classification"]["development-qualified"] = False
        out["gates"][v] = g
    ch = out["gates"].get(chosen) if chosen else None
    out["robustness_trigger"] = dict(triggered=bool(ch and ch["robustness_trigger"]), candidate=CAND.get(chosen))
    out["development_qualified"] = bool(ch and ch["ok"])
    out["may_request_holdout"] = out["development_qualified"]
    # 4. diagnostics
    counts = trial_counts()
    out["trial_counts"] = counts
    diag = {}
    if chosen and ret_of(CAND[chosen]) is not None:
        r_h = ret_of(CAND[chosen])
        diag["dsr"] = p2spec.dsr_views(r_h.to_numpy(), max(counts["p2_selection"], 2), max(counts["p2_broad"], 2),
                                       counts["cumulative_selection"])
        diag["dsr_note"] = ("Diagnostic only. V[SR] = programme-1 frozen dispersion. P2 candidates N = Phase 2 selection "
                            "configs; P2 broad = selection + robustness configs; cumulative = every selection candidate "
                            "since C01 (programme 1's 40 + Phase 2's).")
        diag["psr_0"] = stats.probabilistic_sharpe(r_h.to_numpy())
        ctl = CONTROLS[chosen]
        pairs = {"EW": r_ew, "SPY": r_spy, "C1": ret_of(ctl["C1"]), "C2": ret_of(ctl["C2"]),
                 **{f"R seed {i + 1}": ret_of(e) for i, e in enumerate(ctl["R"])}}
        diag["bootstrap_sharpe_diff"] = {k: p2spec.paired_bootstrap_sharpe_diff(r_h, v) for k, v in pairs.items()
                                         if v is not None}
        mech = {}
        for k in ("C1", "C2"):
            if pairs[k] is not None:
                mech[f"H - {k} by block"] = blocks_vs(r_h, pairs[k])
        rs = [pairs[f"R seed {i}"] for i in (1, 2, 3) if pairs[f"R seed {i}"] is not None]
        if pairs["C1"] is not None:
            mech["C1 - EW by block (does the trend filter alone beat EW?)"] = blocks_vs(pairs["C1"], r_ew)
            mech["C1 - EW full"] = p2spec.sharpe(pairs["C1"]) - p2spec.sharpe(r_ew)
        if len(rs) == 3:
            mech["median R - EW full"] = float(np.median([p2spec.sharpe(x) for x in rs])) - p2spec.sharpe(r_ew)
        diag["mechanism"] = mech
        diag["episodes"] = {}
        for name, (a, z) in EPISODES.items():
            row = {}
            for lab, rr in (("H", r_h), ("EW", r_ew), ("SPY", r_spy), ("C1", pairs["C1"])):
                if rr is not None:
                    row[lab] = float((1 + p2spec.window(rr, a, z)).prod() - 1)
            diag["episodes"][name] = row
    diag["pbo_candidates"] = pbo(list(CAND.values()))
    if chosen:
        diag["pbo_chosen_and_perturbations"] = pbo([CAND[chosen]] + PERTURB)
    names = {"H014 A": "E014-01", "H014 B": "E014-02", "C1 A": "E014-03", "C2 A": "E014-04", "R1 A": "E014-05",
             "R2 A": "E014-06", "R3 A": "E014-07", "C1 B": "E014-08", "C2 B": "E014-09", "R1 B": "E014-10",
             "R2 B": "E014-11", "R3 B": "E014-12"}
    yt = yearly(names)
    for lab, e in (("EW", eq_ew), ("SPY", eq_spy)):
        rr = p2spec.returns(e)
        yt[lab] = {str(y): dict(ret=float((1 + rr[rr.index.str[:4] == str(y)]).prod() - 1),
                                sharpe=p2spec.sharpe(rr[rr.index.str[:4] == str(y)])) for y in range(2010, 2022)}
    diag["yearly"] = yt
    diag["sizing_200k"] = {v: dict(base=CAND[v], sizing=SIZING[v],
                                   base_sharpe=out["books"][CAND[v]].get("sharpe"),
                                   sizing_sharpe=out["books"][SIZING[v]].get("sharpe"),
                                   base_cost_pa=(out["books"][CAND[v]].get("costs") or {}).get("total_pa"),
                                   sizing_cost_pa=(out["books"][SIZING[v]].get("costs") or {}).get("total_pa"))
                           for v in ("A", "B")}
    diag["cost_stress"] = {m: dict(exp=e, sharpe=out["books"][e].get("sharpe"), status=out["books"][e].get("status"),
                                   d_ew=(out["books"][e]["sharpe"] - p2spec.sharpe(r_ew)) if out["books"][e].get("sharpe")
                                   is not None else None) for m, e in STRESS.items()}
    out["diagnostics_not_gates"] = diag
    Path(out_path or Path(__file__).parent / "P2_results.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(dict(selection=out["selection"].get("chosen_id"),
                          gates={v: dict(G1=g["G1"]["ok"], G2=g["G2"]["ok"], G3=g["G3"]["ok"], G4=g["G4"]["ok"])
                                 for v, g in out["gates"].items() if "G1" in g},
                          trigger=out["robustness_trigger"], qualified=out["development_qualified"]), indent=1))


if __name__ == "__main__":
    main()
