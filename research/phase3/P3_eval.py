"""Phase 3 frozen evaluation (P3_spec.md §9-§13), written at P3-CP2 before any search or null run.

  null : reads the primary null runs E018-01..05 (and the diagnostic block null E018-06 if present), computes the null
         threshold tau (25th largest of 500 T values), the search-stage false-pass rate with its Clopper-Pearson
         interval, and writes research/phase3/P3_null_result.json. Must be committed BEFORE E018-07 starts.
  real : reads E018-07 (real world) and the committed null result: T_real, Q1 (p-value), the clusters at tau, the
         one-standard-error ranking (<= 3), the walk-forward (Q2), the diagnostics (PBO, effective N, DSR), and writes
         research/phase3/P3_search_result.json. The local recomputation must equal the in-LEAN world summary.

    PYTHONPATH=src python research/phase3/P3_eval.py null|real
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

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
    return dict(worlds=names, T=T.tolist(), tau=p3spec.tau_of(T), false_pass=p3spec.false_pass(T, wf),
                T_quantiles={q: float(np.percentile(fin, q)) for q in (5, 25, 50, 75, 95, 99)} if len(fin) else {},
                wf_total_ex_spy_median=float(np.median([ws[n]["wf"]["total_ex_spy"] for n in names])))


def run_null():
    ws = {}
    for e in NULL_RUNS:
        ws.update(worlds(e))
    out = dict(spec_sha256=p3spec.spec_hash(), runs=list(NULL_RUNS), primary=summarise_null(ws, len(p3spec.NULL_SEEDS)))
    if (ROOT / "experiments" / BLOCK_RUN / "result.json").exists():
        out["secondary_block"] = summarise_null(worlds(BLOCK_RUN), len(p3spec.BLOCK_SEEDS))
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


def run_real():
    nul = json.loads(NULL_OUT.read_text())
    tau = float(nul["primary"]["tau"])
    null_T = np.array(nul["primary"]["T"], float)
    C, inp, monthly = real_inputs(REAL_RUN)
    nbg = G.neighbours(C)
    ix = {c["id"]: i for i, c in enumerate(C)}
    nbi = [np.array([ix[o] for o in nbg[c["id"]]], dtype=int) for c in C]
    cpx = [G.complexity(c) for c in C]
    summ = P.world_summary(inp, nbi, cpx)
    lean = worlds(REAL_RUN)["real"]
    T = _T(lean)                                          # the official statistic: full precision, computed in LEAN
    if not (T == summ["T"] or abs(T - summ["T"]) <= 1e-5) or lean["wf"]["passed"] != summ["wf"]["passed"]:
        raise SystemExit("local recomputation (published precision) differs from the in-LEAN world summary")
    q1 = p3spec.q1(T, null_T)
    sel = P.select(inp, nbi, cpx, 2017, tau=tau, k=3)
    ranked = [dict(rank=i + 1, centre=C[r["centre"]]["key"], centre_id=C[r["centre"]]["id"],
                   ps=float(sel["ps"][r["centre"]]), size=r["size"], se=r["se"],
                   members=[C[m]["key"] for m in r["members"]]) for i, r in enumerate(sel["ranked"])]
    m_eff = effective_n(monthly)
    pbo = stats.pbo_cscv(monthly.T, n_blocks=8)
    out = dict(spec_sha256=p3spec.spec_hash(), tau=tau, T_real=T, p_value=p3spec.p_value(T, null_T), Q1=q1,
               n_eligible=sel["n_eligible"], n_survivors=sel["n_survivors"], n_clusters=len(sel["clusters"]),
               ranked=ranked if q1 else [], walk_forward=lean["wf"], Q2=bool(lean["wf"]["passed"]),
               diagnostics=dict(pbo=pbo, effective_n=m_eff))
    if q1 and ranked:
        c = ix[ranked[0]["centre_id"]]
        out["diagnostics"]["dsr_rank1"] = stats.deflated_sharpe(monthly[c], max(int(round(m_eff)), 1),
                                                                float(np.var([stats.sharpe_per_period(m)
                                                                              for m in monthly])))
    REAL_OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("tau", "T_real", "p_value", "Q1", "Q2", "n_clusters")}, default=float))
    return out


if __name__ == "__main__":
    {"null": run_null, "real": run_real}[sys.argv[1]]()
