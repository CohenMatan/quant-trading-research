"""C03 evaluation, written and committed BEFORE any C03 run (CP3e, D082 frozen spec, D083).

Implements exactly the approved procedure; every decision is mechanical:
  1. IS screen (D036, unchanged) per book; the 2x-slippage item from the run whose config has
     robustness_of = the book and slippage_stress_multiple = 2. H013: a variation passes only if all
     three seeds pass.
  2. Choice per hypothesis: the passing variation with the highest IS Sharpe (H013: mean of its seeds'
     Sharpes); ties to the lower version. H012 and H013 never compete.
  3. Robustness (unchanged, per seed for H013): plateau >= 80% of perturbations keep Sharpe >= 70% of
     the base; Sharpe > 0 at 4x costs; every third of IS has Sharpe > 0. Runs found by robustness_of.
  4. Validation gates and DSR: only with --val (after separate owner approval), via
     qresearch.validation.val_gate items and qresearch.c03stats (dual-count DSR, per book).
Diagnostics (never gates): H012 Controls A/B and the falsification tests of H012.md; H013 paired
nulls, per-seed differences, trade overlap; PBO (cycle-level over the 6 candidates with H013 as the
seed-averaged series, and per hypothesis); S1/S2 capital sensitivity.

    PYTHONPATH=src python research/cycles/C03_eval.py                -> research/cycles/C03_results.json
    PYTHONPATH=src python research/cycles/C03_eval.py --val val.json (only after owner approval)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from qresearch import c03stats, gates, metrics, results, stats, validation  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
EW_ID, SPY_ID = "E901-07", "E900-07"
VERSIONS = ("v1.0", "v1.1", "v1.2")
H012 = {"v1.0": "E012-01", "v1.1": "E012-02", "v1.2": "E012-03"}
CONTROL_A, CONTROL_B = "E012-04", {"v1.0": "E012-05", "v1.1": "E012-06", "v1.2": "E012-07"}
H013 = {v: {s: f"E013-{3 * i + s:02d}" for s in (1, 2, 3)} for i, v in enumerate(VERSIONS)}
NULL = {1: "E962-22", 2: "E962-23", 3: "E962-24"}
SIZING = {"S1": {"H012 v1.0": ("E012-08", "E012-01"), "Control A": ("E012-09", "E012-04"),
                 **{f"H013 v1.0 seed {s}": (f"E013-{9 + s}", f"E013-0{s}") for s in (1, 2, 3)},
                 **{f"null seed {s}": (f"E962-{24 + s}", NULL[s]) for s in (1, 2, 3)}},
          "S2": {"H012 v1.0": ("E012-10", "E012-01"), "Control A": ("E012-11", "E012-04"),
                 **{f"H013 v1.0 seed {s}": (f"E013-{12 + s}", f"E013-0{s}") for s in (1, 2, 3)},
                 **{f"null seed {s}": (f"E962-{27 + s}", NULL[s]) for s in (1, 2, 3)}}}
PLATEAU_SHARE, PLATEAU_KEEP = 0.80, 0.70


def _series(df, col="equity"):
    return pd.Series(df[col].to_numpy(float), index=df["date"].astype(str))


def load(eid):
    """Completed run -> dict(cfg, eq, tr, fi, res); None if not run or not completed (never guessed)."""
    d = EXP / eid
    if not (d / "result.json").exists():
        return None
    res = json.loads((d / "result.json").read_text())
    if not str(res.get("status", "")).startswith("completed"):
        return None
    return dict(cfg=json.loads((d / "config.json").read_text()), res=res,
                eq=results.read_csv_gz(d / "equity.csv.gz"), tr=results.read_csv_gz(d / "trades.csv.gz"),
                fi=results.read_csv_gz(d / "fills.csv.gz"))


BENCH = {}


def bench():
    if not BENCH:
        BENCH["ew"] = load(EW_ID)["eq"]
        BENCH["spy"] = load(SPY_ID)["eq"]
    return BENCH


def messages(run, prefix):
    lines = run["res"].get("harness_messages") or []
    for ln in lines:
        if ln.startswith(prefix + "|summary|"):
            return json.loads(ln.split("|", 2)[2])
    return None


def book(eid):
    """Metrics, the unchanged IS screen and the robustness thirds for one completed run."""
    run = load(eid)
    if run is None:
        return dict(exp=eid, status="not run")
    eq, tr = run["eq"], run["tr"]
    s = _series(eq)
    ew = _series(bench()["ew"])
    b = bench()["ew"][(bench()["ew"]["date"].astype(str) >= s.index[0]) & (bench()["ew"]["date"].astype(str) <= s.index[-1])]
    m = metrics.compute_metrics(eq, tr, run["fi"])
    chk = gates.is_screen(eq, tr, b)
    closed = tr[tr["status"] == "closed"] if len(tr) else tr
    expo = validation.exposure(eq)
    return dict(exp=eid, status="completed", sharpe=m["sharpe"], cagr=m["cagr"], max_dd=m["max_drawdown"],
                trades=int(len(closed)), avg_pnl_per_trade=float(closed["pnl"].mean()) if len(closed) else float("nan"),
                exposure_mean=float(expo.mean()), screen=chk, screen_pass=gates.passed(chk),
                failed_items=[c["gate"] for c in chk if not c["ok"]], thirds=gates.thirds_positive(eq),
                skipped_min_position=run["res"].get("harness_summary", {}).get("skipped_min_position"),
                ew_sharpe=metrics.sharpe(metrics.returns_from_equity(ew[(ew.index >= s.index[0]) & (ew.index <= s.index[-1])])),
                strategy_summary=messages(run, "QRS012") or messages(run, "QRS013"))


def c03_configs():
    out = {}
    for p in sorted(EXP.glob("E*/config.json")):
        c = json.loads(p.read_text())
        if c.get("cycle") == "C03":
            out[c["experiment_id"]] = c
    return out


def stress_and_robustness(base_id, cfgs):
    """The 2x-slippage screen item and the robustness battery of one book (runs found by robustness_of)."""
    two = [e for e, c in cfgs.items() if c.get("robustness_of") == base_id
           and c["costs"].get("slippage_stress_multiple", 1) == 2]
    cost = {m: [e for e, c in cfgs.items() if c.get("robustness_of") == base_id
                and c["costs"].get("slippage_stress_multiple", 1) == m] for m in (4, 6)}
    pert = [e for e, c in cfgs.items() if c.get("robustness_of") == base_id
            and c["costs"].get("slippage_stress_multiple", 1) == 1]
    out = dict(slippage_2x=None, robustness=None)
    if two:
        b2 = book(two[0])
        out["slippage_2x"] = dict(exp=two[0], sharpe=b2.get("sharpe"),
                                  ok=b2.get("status") == "completed" and b2["sharpe"] >= 0.4)
    if pert or cost[4]:
        base = book(base_id)
        ps = [book(e) for e in pert]
        keep = sum(1 for p in ps if p.get("status") == "completed" and p["sharpe"] >= PLATEAU_KEEP * base["sharpe"])
        c4 = book(cost[4][0]) if cost[4] else dict(status="not run")
        c6 = book(cost[6][0]) if cost[6] else dict(status="not run")
        out["robustness"] = dict(
            perturbations=[(p["exp"], p.get("sharpe")) for p in ps], kept=keep, n=len(ps),
            plateau_ok=len(ps) > 0 and keep >= PLATEAU_SHARE * len(ps) - 1e-9,
            cost_4x=c4.get("sharpe"), cost_4x_ok=c4.get("status") == "completed" and c4["sharpe"] > 0,
            cost_6x_reported=c6.get("sharpe"), thirds=base.get("thirds"),
            thirds_ok=all(x > 0 for x in (base.get("thirds") or [float("nan")])))
        out["robustness"]["ok"] = (out["robustness"]["plateau_ok"] and out["robustness"]["cost_4x_ok"]
                                   and out["robustness"]["thirds_ok"])
    return out


def h012_section(cfgs):
    ca = book(CONTROL_A)
    out = dict(control_a=ca, variations={})
    for v, eid in H012.items():
        b, cb = book(eid), book(CONTROL_B[v])
        row = dict(book=b, control_b=cb, stages=stress_and_robustness(eid, cfgs))
        if b["status"] == "completed" and ca["status"] == "completed" and cb["status"] == "completed":
            row["timing"] = dict(
                sharpe_minus_control_a=b["sharpe"] - ca["sharpe"], sharpe_minus_control_b=b["sharpe"] - cb["sharpe"],
                exposure_gap_vs_b=b["exposure_mean"] - cb["exposure_mean"],
                drawdown_evidence=bool(b["max_dd"] > cb["max_dd"] and abs(b["exposure_mean"] - cb["exposure_mean"]) <= 0.05))
        row["base_screen_pass"] = b.get("screen_pass", False)      # decides whether the 2x run is made
        row["screen_pass"] = b.get("screen_pass", False) and bool((row["stages"]["slippage_2x"] or {}).get("ok"))
        out["variations"][v] = row
    tm = [r.get("timing") for r in out["variations"].values()]
    out["timing_value_refuted"] = (all(t is not None for t in tm)
                                   and all(t["sharpe_minus_control_a"] <= 0.05 and t["sharpe_minus_control_b"] <= 0.05 for t in tm))
    return out


def overlap(a_id, b_id):
    """Share of the book's entries (symbol, entry date) that the paired null also made."""
    a, b = load(a_id), load(b_id)
    if a is None or b is None:
        return None
    ea = set(zip(a["tr"]["symbol_id"], a["tr"]["entry_date"]))
    eb = set(zip(b["tr"]["symbol_id"], b["tr"]["entry_date"]))
    return len(ea & eb) / len(ea) if ea else float("nan")


def h013_section(cfgs):
    out = dict(nulls={s: book(e) for s, e in NULL.items()}, variations={})
    for v, seeds in H013.items():
        rows = {}
        for s, eid in seeds.items():
            b, n = book(eid), out["nulls"][s]
            r = dict(book=b, stages=stress_and_robustness(eid, cfgs))
            if b["status"] == "completed" and n["status"] == "completed":
                r["vs_null"] = dict(sharpe_diff=b["sharpe"] - n["sharpe"],
                                    avg_pnl_diff=b["avg_pnl_per_trade"] - n["avg_pnl_per_trade"],
                                    entry_overlap=overlap(eid, NULL[s]))
            r["base_screen_pass"] = b.get("screen_pass", False)
            r["screen_pass"] = b.get("screen_pass", False) and bool((r["stages"]["slippage_2x"] or {}).get("ok"))
            rows[s] = r
        done = all(r["book"]["status"] == "completed" for r in rows.values())
        diffs = [r["vs_null"]["sharpe_diff"] for r in rows.values() if "vs_null" in r]
        pnl = [r["vs_null"]["avg_pnl_diff"] for r in rows.values() if "vs_null" in r]
        out["variations"][v] = dict(
            seeds=rows, all_seeds_run=done,
            base_screen_pass=done and all(r["base_screen_pass"] for r in rows.values()),
            screen_pass=done and all(r["screen_pass"] for r in rows.values()),
            mean_seed_sharpe=float(np.mean([r["book"]["sharpe"] for r in rows.values()])) if done else None,
            mean_sharpe_diff_vs_null=float(np.mean(diffs)) if len(diffs) == 3 else None,
            mean_avg_pnl_diff_vs_null=float(np.mean(pnl)) if len(pnl) == 3 else None)
    vs = out["variations"].values()
    out["avoidance_refuted"] = (all(x["mean_sharpe_diff_vs_null"] is not None for x in vs)
                                and all(x["mean_sharpe_diff_vs_null"] <= 0.05 or x["mean_avg_pnl_diff_vs_null"] <= 0
                                        for x in vs))
    return out


def choose(section, key):
    """Mechanical choice: the passing variation with the highest IS Sharpe; ties to the lower version."""
    ok = [(v, key(r)) for v, r in section["variations"].items() if r["screen_pass"]]
    if not ok:
        return None
    best = max(s for _, s in ok)
    return min(v for v, s in ok if s == best)


def returns_of(eid):
    run = load(eid)
    return None if run is None else metrics.returns_from_equity(_series(run["eq"]))


def pbo_diagnostic():
    """Diagnostic only (D082): never passes, fails, ranks or selects."""
    cols = {}
    for v, eid in H012.items():
        r = returns_of(eid)
        if r is not None:
            cols[f"H012 {v}"] = r
    for v, seeds in H013.items():
        rs = [returns_of(e) for e in seeds.values()]
        if all(r is not None for r in rs):
            cols[f"H013 {v} (seed-averaged, PBO only)"] = pd.concat(rs, axis=1, join="inner").mean(axis=1)
    out = dict(note="diagnostic only; see research/cycles/C03_statistical_spec.md §1 and CP3f §3 for its limitations",
               candidates=list(cols))
    if len(cols) >= 2:
        mat = pd.concat(cols, axis=1, join="inner").dropna()
        out["cycle"] = stats.pbo_cscv(mat.to_numpy(), n_blocks=16)
        for h in ("H012", "H013"):
            sub = [c for c in mat.columns if c.startswith(h)]
            if len(sub) >= 2:
                out[h] = stats.pbo_cscv(mat[sub].to_numpy(), n_blocks=16)
    return out


def sizing_section():
    out = {}
    for sname, rows in SIZING.items():
        out[sname] = {}
        for label, (eid, base) in rows.items():
            a, b = book(eid), book(base)
            out[sname][label] = dict(exp=eid, base=base, status=a["status"], sharpe=a.get("sharpe"),
                                     cagr=a.get("cagr"), max_dd=a.get("max_dd"), exposure=a.get("exposure_mean"),
                                     sharpe_minus_base=(a["sharpe"] - b["sharpe"]) if a["status"] == b["status"] == "completed" else None)
    return out


def val_stage(val_map):
    """Only after separate owner approval. val_map: {IS experiment id: VAL experiment id} for every book
    of the chosen variations. Validation gates (unchanged; PBO item dropped for C03 per D082) and the
    dual-count DSR on IS + VAL per book, with the registry snapshot at this commit."""
    snap = c03stats.snapshot(expect_official=c03stats.OFFICIAL_N_C03)
    ew = _series(bench()["ew"])
    out = dict(snapshot=snap, spec_sha256=c03stats.spec_hash(), books={})
    for is_id, val_id in val_map.items():
        i, v = load(is_id), load(val_id)
        if i is None or v is None:
            out["books"][is_id] = dict(val=val_id, status="not run", ok=False)
            continue
        is_sr = metrics.sharpe(metrics.returns_from_equity(_series(i["eq"])))
        g = [c for c in validation.val_gate(v["eq"], v["tr"], is_sr, ew,
                                            c03stats.book_returns(_series(i["eq"]), _series(v["eq"])), 1, 0.0, 0.0)
             if not c["gate"].startswith(("Deflated", "PBO"))]
        d = c03stats.evaluate_book(is_id, _series(i["eq"]), _series(v["eq"]), snap)
        out["books"][is_id] = dict(val=val_id, gates=g, gates_ok=all(c["ok"] for c in g), dsr=d,
                                   ok=all(c["ok"] for c in g) and d["ok"])
    return out


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    cfgs = c03_configs()
    h12, h13 = h012_section(cfgs), h013_section(cfgs)
    out = dict(
        note="C03 evaluation (D082/D083); screen and robustness thresholds unchanged; diagnostics never gate",
        h012=h12, h013=h13,
        chosen=dict(H012=choose(h12, lambda r: r["book"]["sharpe"]),
                    H013=choose(h13, lambda r: r["mean_seed_sharpe"])),
        pbo_diagnostic=pbo_diagnostic(), sizing=sizing_section(),
        trial_counts_now=c03stats.snapshot())
    if args and args[0] == "--val":
        out["validation"] = val_stage(json.loads(Path(args[1]).read_text()))
    p = ROOT / "research" / "cycles" / "C03_results.json"
    p.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(dict(chosen=out["chosen"], counts=out["trial_counts_now"]), indent=1))
    return out


if __name__ == "__main__":
    main()
