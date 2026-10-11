"""P8-CP1 (owner D199): extract the ONE real H023 development search (E025-08) -> research/phase8/cp1/
P8_CP1_result.json. WRITTEN AND COMMITTED BEFORE THE RUN. Checks the provenance (pinned c_SEARCH, fold thresholds, null
result, threshold commit, panel and layer-subtotal digests), recomputes every configuration's statistics, the frozen
selection rule and the walk-forward diagnostic OFFLINE from the exported monthly matrices with qr_h023 and requires
equality with the host, and reports: the search-adjusted percentile / p-value of the highest real t_IC against the 5,000
null maxima, the weight surface (plateaus, broad vs sharp, boundary flags, descriptive layer tendencies), the absolute
best and the pre-registered selected configuration, the control 40/45/15 (= H022, reported only), structure counts and
the non-gating 2- / 3-month diagnostics. If a candidate exists, its frozen record and hash (qresearch.p8h023
.candidate_record). Selection is exactly the frozen rule; nothing is chosen by hand; no portfolio statistic exists."""
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7"), str(HERE)]
import qr_h023 as G  # noqa: E402
import qr_p7_export as E  # noqa: E402
import qr_xs as X  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import p8h023  # noqa: E402

CANDIDATE = "DEVELOPMENT CANDIDATE — SCORE V2 FROZEN, VALIDATION STILL SEALED"
NONE = "NO ROBUST SCORE V2 CANDIDATE"
CMP = ("t_ic", "ic_mean", "ic_se", "hi_ann", "mono", "q5_minus_q1_ann", "block_max", "hi_n_mean", "hi_months",
       "half1", "half2")


def _same(a, b, tol=0.0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    both = (np.isnan(a) & np.isnan(b)) | (a == b)
    return bool(np.all(both | (np.abs(a - b) <= tol)))


def cfg_row(s, sel, i):
    f = sel["filters"]
    return dict(
        weights=list(G.GRID[i]), index=i, t_ic=float(s["t_ic"][i]), ic_mean=float(s["ic_mean"][i]),
        ic_se=float(s["ic_se"][i]), positive_months=int(s["positive_months"][i]),
        hi_monthly=float(s["hi_monthly"][i]), hi_ann=float(s["hi_ann"][i]), hi_stock_months=int(s["hi_stock_months"][i]),
        hi_months=int(s["hi_months"][i]), hi_n_mean=float(s["hi_n_mean"][i]),
        q_mean_ann=[float(x) for x in s["q_mean_ann"][i]], q_mean_monthly=[float(x) for x in s["q_mean"][i]],
        q5_minus_q1_ann=float(s["q5_minus_q1_ann"][i]), mono=float(s["mono"][i]),
        half1=float(s["half1"][i]), half2=float(s["half2"][i]),
        block_sum=[float(x) for x in s["block_sum"][i]], ic_sum=float(s["ic_sum"][i]),
        block_share=[float(x / s["ic_sum"][i]) if s["ic_sum"][i] > 0 else None for x in s["block_sum"][i]],
        block_max=float(s["block_max"][i]), years={str(y): float(v[i]) for y, v in s["years"].items()},
        base=bool(G.base_ok(s)[i]), boundary=G.on_boundary(G.GRID[i]),
        filters={k: bool(f[k][i]) for k in ("D1", "D2", "D3", "D4", "D5", "qualified")})


def main(exp="E025-08"):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    blob = joined(ls, "QRH")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"], "result blob hash"
    assert not any(x.startswith(("QRN|", "QRR|")) for x in ls), "unexpected output"
    out = json.loads(E.unpack(blob))
    prov = st["provenance"]
    assert prov["c_search"] == out["c_search"] == p8h023.C_SEARCH
    assert {k: float(v) for k, v in prov["c_fold"].items()} == {str(k): v for k, v in p8h023.C_FOLD.items()}
    assert out["c_fold"] == [p8h023.C_FOLD[y] for y in G.FOLD_YEARS]
    assert prov["null_result_sha256"] == p8h023.NULL_RESULT_SHA256 == hashlib.sha256(
        (ROOT / p8h023.NULL_RESULT).read_bytes()).hexdigest()
    assert prov["threshold_commit"] == p8h023.THRESHOLD_COMMIT
    assert prov["panel_sha256"] == st["panel_sha256"] == p8h023.PANEL_SHA256
    assert prov["components_sha256"] == st["components_sha256"] == p8h023.COMPONENTS_SHA256
    assert st["spec_sha256"] == p8h023.SPEC_SHA256 and out["grid"] == [list(w) for w in G.GRID]
    # ---- offline recomputation from the exported monthly matrices
    w = dict(IC=np.array(out["IC"], float), QM=np.array(out["QM"], float), HI=np.array(out["HI"], float),
             NH=np.array(out["NH"], np.int64), years=np.array(out["years"]))
    assert w["IC"].shape == (83, 92) and len(out["days"]) == 83
    s = G.summarise(w)
    hs = out["summary"]
    recompute = {k: _same(s[k], hs[k]) for k in CMP}
    sel = G.select(s, p8h023.C_SEARCH)
    hsel = out["selection"]
    recompute["selection"] = (sel["candidate"] == hsel["candidate"] and sel["argmax"] == hsel["argmax"]
                              and sel["plateaus"] == hsel["plateaus"] and sel["winner"] == hsel["winner"])
    wf = G.walk_forward(w, [p8h023.C_FOLD[y] for y in G.FOLD_YEARS])
    recompute["walk_forward"] = [f["selected"] for f in wf["folds"]] == [f["selected"] for f in
                                                                         out["walk_forward"]["folds"]]
    recompute["cstar"] = G.cstar(s) == out["cstar"] or (math.isinf(G.cstar(s)) and math.isinf(out["cstar"]))
    assert all(recompute.values()), recompute
    # ---- null comparison of the highest real t_IC
    nulls = json.loads(gzip.open(ROOT / p8h023.NULL_WORLDS).read())
    nm = np.array([x["max_t"] for x in nulls])
    best = sel["argmax"]
    tbest = float(s["t_ic"][best])
    rows = [cfg_row(s, sel, i) for i in range(len(G.GRID))]
    t = s["t_ic"]
    # ---- surface
    wT = np.array([g[0] for g in G.GRID])
    wF = np.array([g[1] for g in G.GRID])
    wS = np.array([g[2] for g in G.GRID])
    tend = {name: dict(spearman_t=X.spearman(v.astype(float), t), spearman_ic=X.spearman(v.astype(float), s["ic_mean"]),
                       spearman_hi=X.spearman(v.astype(float), np.nan_to_num(s["hi_ann"], nan=-1.0)),
                       mean_t_by_level={str(int(L)): float(t[v == L].mean()) for L in sorted(set(v.tolist()))})
            for name, v in (("technical", wT), ("fundamental", wF), ("sector", wS))}
    surface = dict(
        max_t=tbest, share_within_80pct_of_max=float(np.mean(t >= 0.8 * tbest)) if tbest > 0 else 0.0,
        neighbours_of_best=[dict(weights=list(G.GRID[j]), t_ic=float(t[j])) for j in G.ADJ[best]],
        n_base=int(G.base_ok(s).sum()), regions=[[list(G.GRID[i]) for i in r] for r in sel["regions"]],
        plateaus=[dict(members=[list(G.GRID[i]) for i in c], size=len(c), median_t=float(np.median(t[c])),
                       median_hi_ann=float(np.median(np.nan_to_num(s["hi_ann"][c], nan=-np.inf))),
                       qualified=[list(G.GRID[i]) for i in c if sel["filters"]["qualified"][i]],
                       boundary=any(G.on_boundary(G.GRID[i]) for i in c)) for c in sel["ranked"]],
        counts={k: int(sel["filters"][k].sum()) for k in ("D1", "D2", "D3", "D4", "D5", "D2_5", "qualified")},
        layer_tendencies=tend, positive_ic_configs=int((s["ic_mean"] > 0).sum()),
        positive_hi_configs=int((np.nan_to_num(s["hi_ann"], nan=-1) > 0).sum()))
    cand = sel["candidate"]
    verdict = CANDIDATE if cand is not None else NONE
    boundary = dict(absolute_best=G.on_boundary(G.GRID[best]),
                    winning_plateau=None if sel["winner"] is None else any(G.on_boundary(G.GRID[i]) for i in sel["winner"]),
                    candidate=None if cand is None else G.on_boundary(G.GRID[cand]))
    grid_sha = hashlib.sha256(json.dumps([list(x) for x in G.GRID], separators=(",", ":")).encode()).hexdigest()
    record = rec_sha = None
    if cand is not None:
        record = p8h023.candidate_record(G.GRID[cand], [G.GRID[i] for i in sel["winner"]], st["real"]["blob_sha256"],
                                         grid_sha)
        rec_sha = p8h023.record_sha(record)
    pv = res["provenance"]
    result = dict(
        experiment=exp, qc_backtest_id=pv.get("qc_backtest_id"), build_commit=pv.get("build_commit"),
        lean_version=pv.get("lean_version"), run_utc=pv.get("run_utc"), status=res["status"],
        orders=res["harness_summary"]["orders"], owner_approved=pv.get("owner_approved"), provenance=prov,
        pit_audit=st.get("pit_audit"), components_check=st["components_check"], decisions=st["decisions"],
        days=out["days"], population=out["n"], grid_sha256=grid_sha, recompute=recompute,
        verdict=verdict, c_search=p8h023.C_SEARCH, c_fold=p8h023.C_FOLD,
        absolute_best=dict(weights=list(G.GRID[best]), t_ic=tbest,
                           null_share_ge=float(np.mean(nm >= tbest)),
                           p_value=float((1 + np.sum(nm >= tbest)) / (1 + nm.size)),
                           null_percentile=float(np.mean(nm < tbest)), t_minus_c=tbest - p8h023.C_SEARCH),
        selected=None if cand is None else cfg_row(s, sel, cand),
        winning_plateau=None if sel["winner"] is None else [list(G.GRID[i]) for i in sel["winner"]],
        unrestricted=dict(winner=None if sel["unrestricted_winner"] is None else
                          [list(G.GRID[i]) for i in sel["unrestricted_winner"]],
                          medoid=None if sel["unrestricted_medoid"] is None else list(G.GRID[sel["unrestricted_medoid"]])),
        control=cfg_row(s, sel, G.CONTROL_INDEX), boundary_flags=boundary, surface=surface, configs=rows,
        walk_forward=out["walk_forward"], structure=out["structure"],
        diagnostics=dict(h2=out["h2"], h3=out["h3"]), cstar=out["cstar"],
        candidate_record=record, candidate_sha256=rec_sha,
        runtime=dict(wall_s=st["wall_s"], max_rss_mb=st["max_rss_mb"], world_s=st["real"]["world_s"]))
    (HERE / "P8_CP1_result.json").write_text(json.dumps(result, indent=1, sort_keys=True, default=float) + "\n")
    print(verdict)
    print(json.dumps(dict(absolute_best=result["absolute_best"], counts=surface["counts"],
                          plateaus=[(p["size"], p["median_t"], p["qualified"][:3]) for p in surface["plateaus"]],
                          selected=None if cand is None else result["selected"]["weights"],
                          boundary=boundary, candidate_sha256=rec_sha), indent=1))
    print("result sha256", hashlib.sha256((HERE / "P8_CP1_result.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
