"""Phase 3 frozen evaluation (P3_spec.md §9-§13), written at P3-CP2 before any search or null run; the REPORTING
parts (per-stage null counts, the fake-winner distributions, the per-configuration and per-world history tables, the
cluster details) were added before the real run, at the threshold commit (D137). The decision quantities (T, tau, Q1,
clusters, ranking, Q2) come only from qr_p3_pipeline and qresearch.p3spec.

  null : reads the primary null runs E018-01..05 (and the diagnostic block null E018-06 if present), computes the null
         threshold tau (25th largest of 500 T values), the search-stage false-pass rate with its Clopper-Pearson
         interval, and writes research/phase3/P3_null_result.json. Must be committed BEFORE E018-07 starts.
  real : reads E018-07 (real world) and the committed null result: T_real, Q1 (p-value), the clusters at tau, the
         one-standard-error ranking (<= 3), the walk-forward (Q2), the diagnostics (PBO, effective N, DSR), and writes
         research/phase3/P3_search_result.json. The local recomputation must equal the in-LEAN world summary.

    PYTHONPATH=src python research/phase3/P3_eval.py null|real
"""
from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
from qresearch import p3spec, stats  # noqa: E402
import qr_p3_grammar as G  # noqa: E402
import qr_p3_pipeline as P  # noqa: E402

NULL_RUNS = tuple(f"E018-{k:02d}" for k in range(1, 6))
BLOCK_RUN, REAL_RUN = "E018-06", "E018-07"
NULL_OUT = ROOT / "research/phase3/P3_null_result.json"
REAL_OUT = ROOT / "research/phase3/P3_search_result.json"
NULL_TABLE = ROOT / "research/phase3/P3_null_worlds.csv"
REAL_TABLE = ROOT / "research/phase3/P3_search_configs.csv.gz"
SPY_RUN = "E900-07"
QS = (5, 25, 50, 75, 95, 99)


def spy_growth(start_prev="2010-02-26", end="2017-12-29"):
    """REPORTING ONLY: SPY total-return growth over the search window from the frozen benchmark run E900-07 (close of
    the session before the official start to the last session) and the calendar years, to express log excess as an
    approximate excess CAGR (CAGR(config) - CAGR(SPY)) and a terminal-wealth ratio."""
    e = pd.read_csv(gzip.open(ROOT / "experiments" / SPY_RUN / "equity.csv.gz")).set_index("date")["equity"]
    g = float(e[end] / e[start_prev])
    yrs = (date.fromisoformat(end) - date.fromisoformat(start_prev)).days / 365.25
    return g, yrs


def excess_cagr(total_logex, g=None, yrs=None):
    if g is None:
        g, yrs = spy_growth()
    x = np.asarray(total_logex, float)
    with np.errstate(over="ignore", invalid="ignore"):
        return (g * np.exp(x)) ** (1 / yrs) - g ** (1 / yrs)


def qdist(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if not len(x):
        return {}
    return dict({f"p{q}": float(np.percentile(x, q)) for q in QS}, min=float(x.min()), max=float(x.max()),
                mean=float(x.mean()), n=int(len(x)))


def lines(exp):
    q = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def worlds(exp):
    out = {}
    for x in lines(exp):
        if x.startswith("W|"):
            _, name, js = x.split("|", 2)
            out[name] = json.loads(js)
    return out


def _T(w):
    return float(w["T"])                                  # JSON -Infinity = no cluster


def summarise_null(ws, expected):
    names = sorted(ws, key=lambda n: int("".join(ch for ch in n if ch.isdigit())))
    if len(names) != expected:
        raise SystemExit(f"expected {expected} null worlds, found {len(names)}: incomplete null; do not evaluate")
    T = np.array([_T(ws[n]) for n in names])
    wf = np.array([bool(ws[n]["wf"]["passed"]) for n in names])
    fin = T[np.isfinite(T)]
    out = dict(worlds=names, T=T.tolist(), tau=p3spec.tau_of(T), false_pass=p3spec.false_pass(T, wf),
               T_quantiles={q: float(np.percentile(fin, q)) for q in (5, 25, 50, 75, 95, 99)} if len(fin) else {},
               wf_total_ex_spy_median=float(np.median([ws[n]["wf"]["total_ex_spy"] for n in names])))
    fp = out["false_pass"]
    out["stages"] = dict(worlds=len(names), with_eligible=int(sum(ws[n]["n_eligible"] > 0 for n in names)),
                         with_cluster=int(np.isfinite(T).sum()), q1_loo=fp["q1_passes"], q2_walk_forward=fp["wf_passes"],
                         q1_and_q2=fp["full_pipeline_passes"])
    if all("apparent" in ws[n] for n in names):        # the fake-winner effect (reporting only)
        g, yrs = spy_growth()
        a = {k: np.array([ws[n]["apparent"][k] for n in names], float) for k in ws[names[0]]["apparent"]}
        out["fake_winners"] = dict(
            spy_growth=g, years=yrs,
            best_excess_cagr=qdist(excess_cagr(a["best_total_logex"], g, yrs)),
            best_excess_cagr_eligible=qdist(excess_cagr(a["best_total_logex_eligible"], g, yrs)),
            best_terminal_wealth_ratio=qdist(np.exp(a["best_total_logex"])),
            best_fold_median_score=qdist(a["best_s"]), best_cluster_centre_ps=qdist([ws[n]["best_ps"] for n in names]),
            T=qdist(T), apparent_winning_clusters=qdist([ws[n]["n_clusters"] for n in names]),
            eligible_configurations=qdist([ws[n]["n_eligible"] for n in names]),
            configurations_beating_spy=qdist(a["n_beat_spy"]),
            share_worlds_best_beats_spy=float(np.mean(a["best_total_logex"] > 0)),
            share_worlds_with_eligible_cluster=float(np.mean(np.isfinite(T))))
    return out


def null_table(ws_all):
    """Per-world history (owner item 13): one row per null world, every run."""
    rows = []
    for run, ws in ws_all.items():
        for n, w in ws.items():
            a = w.get("apparent", {})
            rows.append(dict(run=run, world=n, T=w["T"], best_ps=w["best_ps"], n_eligible=w["n_eligible"],
                             n_survivors=w["n_survivors"], n_clusters=w["n_clusters"], wf_passed=w["wf"]["passed"],
                             wf_picks=w["wf"]["picks"], wf_total_ex_spy=w["wf"]["total_ex_spy"],
                             wf_total_ex_ew=w["wf"]["total_ex_ew"],
                             rank1_centre=w["ranked"][0]["centre"] if w["ranked"] else "",
                             **{f"apparent_{k}": v for k, v in a.items()}))
    return rows


def _block_present():
    return (ROOT / "experiments" / BLOCK_RUN / "result.json").exists()


def _provenance(exp):
    return json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]


def run_null():
    ws, ws_all = {}, {}
    for e in NULL_RUNS:
        ws_all[e] = worlds(e)
        ws.update(ws_all[e])
    out = dict(spec_sha256=p3spec.spec_hash(), runs=list(NULL_RUNS), primary=summarise_null(ws, len(p3spec.NULL_SEEDS)))
    if _block_present():
        ws_all[BLOCK_RUN] = worlds(BLOCK_RUN)
        out["secondary_block"] = summarise_null(ws_all[BLOCK_RUN], len(p3spec.BLOCK_SEEDS))
    out["run_provenance"] = {e: _provenance(e) for e in ws_all}
    rows = null_table(ws_all)
    with open(NULL_TABLE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    NULL_OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    p = out["primary"]
    print("tau", p["tau"], "false-pass", p["false_pass"])
    return out


def real_inputs(exp, L=None):
    C = G.enumerate_configs()
    ids = [c["id"] for c in C]
    L = lines(exp) if L is None else L
    g = json.loads(next(x for x in L if x.startswith("G|"))[2:])
    rows = {}
    for x in L:
        if x.startswith("Y|"):
            cid, parts = P.parse_y_line(x)
            rows[cid] = parts
    if sorted(rows) != sorted(ids):
        raise SystemExit("real run does not contain exactly the frozen configuration list")
    st = lambda k: np.stack([rows[c][k] for c in ids])  # noqa: E731
    years = list(range(2010, 2018))
    inp = P.Inputs(ids, st(0), st(1), st(2), st(3), st(4), np.array(g["sessions"]), np.array(g["spy_maxdd"]),
                   np.array(g["ew_logex"]), years)
    return C, inp, st(5)


def effective_n(monthly):
    """Li & Ji (2005) effective number of tests from the eigenvalues of the correlation matrix."""
    x = monthly[np.nanstd(monthly, axis=1) > 0]
    lam = np.clip(np.linalg.eigvalsh(np.corrcoef(x)), 0, None)
    return float(np.sum((lam >= 1) + (lam - np.floor(lam))))


def describe(c):
    """Families and parameters of a configuration (its frozen grammar key, in words)."""
    pt, pf, pi = c["primary"]
    d = dict(id=c["id"], key=c["key"], primary=pt, primary_family=pf, primary_params=G.params_of(G.PRIMARY_TYPES, pt, pi),
             confirm=None, confirm_family=None, confirm_params=None, risk=G.RISK_LEVELS[c["risk"]],
             complexity=list(G.complexity(c)))
    if c["confirm"] is not None:
        ct, cf, ci = c["confirm"]
        d.update(confirm=ct, confirm_family=cf, confirm_params=G.params_of(G.CONFIRM_TYPES, ct, ci))
    return d


def config_rows(C, inp, t, ps, cluster_of, g, yrs):
    tot = inp.logex.sum(axis=1)
    dd_ok = inp.maxdd[:, -1] >= inp.spy_maxdd[-1] - P.DD_TOL
    need = math.ceil(P.POS_SHARE * t["F"].shape[1])
    rows = []
    for i, c in enumerate(C):
        d = describe(c)
        rows.append(dict(id=c["id"], key=c["key"], primary_family=d["primary_family"],
                         confirm_family=d["confirm_family"] or "", risk=d["risk"] if d["risk"] is not None else "",
                         n_cond=d["complexity"][0], n_par=d["complexity"][1], s=float(t["s"][i]), ps=float(ps[i]),
                         folds=";".join(f"{x:.6f}" for x in t["F"][i]), total_logex=float(tot[i]),
                         excess_cagr=float(excess_cagr(tot[i], g, yrs)), cost_pa=float(t["cost_pa"][i]),
                         turnover_pa=float(t["turnover"][i]), maxdd=float(inp.maxdd[i, -1]),
                         gate_cost=bool(t["cost_pa"][i] <= P.COST_CAP), gate_dd=bool(dd_ok[i]),
                         gate_folds=bool((t["F"][i] > 0).sum() >= need), eligible=bool(t["eligible"][i]),
                         cluster=cluster_of.get(i, "")))
    return rows


def cluster_detail(k, cl, C, inp, t, ps, nbi, g, yrs, ix):
    ctr = cl["centre"]
    mem = cl["members"]
    tot = inp.logex.sum(axis=1)
    cs = set(mem)
    axis = [dict(neighbour=C[n]["key"], s=float(t["s"][n]), ps=float(ps[n]), in_cluster=n in cs) for n in nbi[ctr]]
    return dict(rank=k, centre=describe(C[ctr]), size=cl["size"], interior=cl["interior"], ps_centre=float(ps[ctr]),
                s_centre=float(t["s"][ctr]), folds_centre=t["F"][ctr].tolist(), se=cl.get("se"),
                total_logex_centre=float(tot[ctr]), wealth_ratio_centre=float(math.exp(tot[ctr])),
                excess_cagr_centre=float(excess_cagr(tot[ctr], g, yrs)), cost_pa_centre=float(t["cost_pa"][ctr]),
                turnover_pa_centre=float(t["turnover"][ctr]), maxdd_centre=float(inp.maxdd[ctr, -1]),
                spy_maxdd=float(inp.spy_maxdd[-1]),
                members=[C[m]["key"] for m in mem],
                member_s=qdist(t["s"][mem]), member_ps=qdist(ps[mem]),
                member_positive_share_by_fold=[float(np.mean(t["F"][mem, f] > 0)) for f in range(t["F"].shape[1])],
                centre_neighbourhood=axis)


def simplicity_trace(sel, ps, t, cpx, ids):
    """Re-derives the one-standard-error bands for the report and asserts the pipeline's picks."""
    rest, out = list(sel["clusters"]), []
    for r in sel["ranked"]:
        best = max(rest, key=lambda c: ps[c["centre"]])
        band = [c for c in rest if ps[c["centre"]] >= ps[best["centre"]] - r["se"]]
        keyf = lambda c: (cpx[c["centre"]][0], cpx[c["centre"]][1], float(t["turnover"][c["centre"]]),  # noqa: E731
                          -float(ps[c["centre"]]), ids[c["centre"]])
        pick = min(band, key=keyf)
        assert pick["centre"] == r["centre"], "simplicity trace disagrees with the frozen pipeline"
        out.append(dict(best_ps=float(ps[best["centre"]]), se=r["se"], band_floor=float(ps[best["centre"]] - r["se"]),
                        band=[dict(centre=ids[c["centre"]], key=list(keyf(c))[:4]) for c in sorted(band, key=keyf)],
                        pick=ids[r["centre"]]))
        rest = [c for c in rest if c["centre"] != r["centre"]]
    return out


def run_real():
    if NULL_OUT == ROOT / p3spec.NULL_RESULT:          # the official evaluation uses only the pinned threshold (D137)
        if __import__("hashlib").sha256(NULL_OUT.read_bytes()).hexdigest() != p3spec.NULL_RESULT_SHA256:
            raise SystemExit("the null result differs from the frozen, pinned calibration: STOP")
    nul = json.loads(NULL_OUT.read_text())
    tau = float(nul["primary"]["tau"])
    null_T = np.array(nul["primary"]["T"], float)
    C, inp, monthly = real_inputs(REAL_RUN)
    nbg = G.neighbours(C)
    ix = {c["id"]: i for i, c in enumerate(C)}
    ids = [c["id"] for c in C]
    nbi = [np.array([ix[o] for o in nbg[c["id"]]], dtype=int) for c in C]
    cpx = [G.complexity(c) for c in C]
    summ = P.world_summary(inp, nbi, cpx)
    lean = worlds(REAL_RUN)["real"]
    T = _T(lean)                                          # the official statistic: full precision, computed in LEAN
    if not (T == summ["T"] or abs(T - summ["T"]) <= 1e-5) or lean["wf"]["passed"] != summ["wf"]["passed"]:
        raise SystemExit("local recomputation (published precision) differs from the in-LEAN world summary")
    q1 = p3spec.q1(T, null_T)
    g, yrs = spy_growth()
    sel = P.select(inp, nbi, cpx, 2017, tau=tau, k=3)
    t, ps = sel["table"], sel["ps"]
    cluster_of = {m: f"K{k + 1}" for k, cl in enumerate(sorted(sel["clusters"], key=lambda c: -ps[c["centre"]]))
                  for m in cl["members"]}
    ranked = [cluster_detail(i + 1, r, C, inp, t, ps, nbi, g, yrs, ix) for i, r in enumerate(sel["ranked"])]
    # every cluster at tau = -inf too (the unthresholded landscape, reporting only)
    open_sel = P.select(inp, nbi, cpx, 2017, k=3)
    m_eff = effective_n(monthly)
    pbo = stats.pbo_cscv(monthly.T, n_blocks=8)
    tot = inp.logex.sum(axis=1)
    rows = config_rows(C, inp, t, ps, cluster_of, g, yrs)
    with gzip.open(REAL_TABLE, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    fam = {}
    for r in rows:
        fam.setdefault(r["primary_family"], []).append(r)
    by_family = {k: dict(configs=len(v), eligible=sum(r["eligible"] for r in v), best_s=max(r["s"] for r in v),
                         median_s=float(np.median([r["s"] for r in v])),
                         beat_spy=sum(r["total_logex"] > 0 for r in v)) for k, v in fam.items()}
    nf = nul["primary"].get("fake_winners", {})
    wf = dict(lean["wf"])
    wf["years"] = [dict(y, pick_key=C[ix[y["pick"]]]["key"] if y["pick"] else None) for y in wf["years"]]
    out = dict(
        spec_sha256=p3spec.spec_hash(), null_result_sha256=__import__("hashlib").sha256(NULL_OUT.read_bytes()).hexdigest(),
        configurations=len(C), tau=tau, T_real=T, p_value=p3spec.p_value(T, null_T),
        null_percentile=float(np.mean(null_T < T)), null_percentile_le=float(np.mean(null_T <= T)), Q1=q1,
        n_eligible=sel["n_eligible"], n_survivors=sel["n_survivors"], n_clusters_at_tau=len(sel["clusters"]),
        clusters_at_tau=[dict(id=cluster_of[c["members"][0]], size=c["size"], centre=C[c["centre"]]["key"],
                              ps=float(ps[c["centre"]]), interior=c["interior"]) for c in sel["clusters"]],
        ranked=ranked, simplicity=simplicity_trace(sel, ps, t, cpx, ids),
        walk_forward=wf, Q2=bool(lean["wf"]["passed"]),
        gates=dict(fail_cost=int(sum(not r["gate_cost"] for r in rows)), fail_dd=int(sum(not r["gate_dd"] for r in rows)),
                   fail_folds=int(sum(not r["gate_folds"] for r in rows)), eligible=sel["n_eligible"],
                   eligible_ps_above_tau=sel["n_survivors"],
                   survivors_in_clusters=int(sum(c["size"] for c in sel["clusters"]))),
        unthresholded=dict(n_clusters=len(open_sel["clusters"]), best_centre_ps=open_sel["best_ps"],
                           rank1=C[open_sel["ranked"][0]["centre"]]["key"] if open_sel["ranked"] else None),
        distribution=dict(s=qdist(t["s"]), ps=qdist(ps), excess_cagr=qdist(excess_cagr(tot, g, yrs)),
                          wealth_ratio=qdist(np.exp(tot)), cost_pa=qdist(t["cost_pa"]), turnover_pa=qdist(t["turnover"]),
                          beat_spy=int((tot > 0).sum()), by_primary_family=by_family),
        apparent=dict(summ["apparent"], best_excess_cagr=float(excess_cagr(summ["apparent"]["best_total_logex"], g, yrs)),
                      best_wealth_ratio=float(math.exp(summ["apparent"]["best_total_logex"]))),
        fake_winners_null=nf, spy_growth=g, years=yrs,
        diagnostics=dict(pbo=pbo, effective_n=m_eff))
    if q1 and ranked:
        c = ix[ranked[0]["centre"]["id"]]
        out["diagnostics"]["dsr_rank1"] = stats.deflated_sharpe(monthly[c], max(int(round(m_eff)), 1),
                                                                float(np.var([stats.sharpe_per_period(m)
                                                                              for m in monthly])))
    # frozen promotion path (P3_spec.md section 14): Q1 -> ranked clusters -> Q2 -> <= 2 LEAN finalists
    out["promotion"] = dict(q1=q1, q2=out["Q2"], finalists_for_lean_verification=(
        [r["centre"]["key"] for r in ranked[:2]] if (q1 and out["Q2"] and ranked) else []),
        rank3_reported_only=ranked[2]["centre"]["key"] if (q1 and len(ranked) > 2) else None)
    REAL_OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("tau", "T_real", "p_value", "null_percentile", "Q1", "Q2",
                                          "n_clusters_at_tau", "promotion")}, default=float))
    return out


if __name__ == "__main__":
    {"null": run_null, "real": run_real}[sys.argv[1]]()
