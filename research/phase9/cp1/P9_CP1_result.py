"""P9-CP1 (owner D201): extract the ONE real H024 development search (E026-08) -> research/phase9/cp1/
P9_CP1_result.json. WRITTEN AND COMMITTED BEFORE THE RUN. Checks the provenance (pinned c_MODEL, c_FEATURE, fold
thresholds, null result, threshold commit, panel / population / library digests); recomputes every feature / model /
control statistic, the gates D1-D6 + N, the frozen selection and the walk-forward selections OFFLINE from the exported
monthly matrices (quintile means from the exported per-year sums) with qr_h024 / qr_h023 and requires agreement with
the host; reports the search-adjusted percentile / p-value of the best feature and the best model against the 5,000
null maxima, every individual feature, the full model search, gate counts, the selected model (if any) with its
leave-one-out models and robust neighbourhood, walk-forward, feature stability, the Score v1 / H023 controls and the
NON-GATING 2- / 3-month diagnostics; and, if a candidate exists, its frozen record and hash. Nothing is chosen by hand;
no portfolio statistic exists."""
import gzip
import hashlib
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7"), str(HERE)]
import qr_h023 as G  # noqa: E402
import qr_h024 as K  # noqa: E402
import qr_p7_export as E  # noqa: E402
import qr_xs as X  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import p9h024  # noqa: E402

FORMULAS = dict(MOM="P[b-21]/P[b-252] - 1 (total-return closes; higher better)",
                LOWVOL="SD (ddof 0) of the last 60 daily log total-return returns (lower better)",
                GPA="gross_profit_TTM / total_assets (ranked within FF12; higher better)",
                ACC="(OCF_TTM - NI_TTM) / total_assets (higher better)",
                BM="stockholders_equity / PIT market cap (higher better)",
                AG="total_assets / total_assets recorded live 12 months earlier - 1 (lower better)",
                REV1M="P[b]/P[b-21] - 1 (lower better)", CBOP="OCF_TTM / total_assets (higher better)",
                HI52="C[b] / max(C[b-251..b]) (split-adjusted closes; higher better)",
                CFP="OCF_TTM / PIT market cap (higher better)",
                EQA="stockholders_equity / total_assets (ranked within FF12; higher better)")
CANDIDATE = "DEVELOPMENT CANDIDATE — H024 SCORE FROZEN, VALIDATION SEALED"
NONE = "NO ROBUST H024 FEATURE MODEL"
DECISIONS = 83


def summ(w, qs, qc, qyears, rows=None):
    """qr_h023.summarise on the exported matrices, with quintile statistics from the per-year sums / counts."""
    g = w["IC"].shape[1]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = G.summarise(dict(w, QM=np.full(w["IC"].shape + (G.N_Q,), np.nan)), rows=rows)
    keep = set(w["years"][rows].tolist()) if rows is not None else set(qyears)
    ix = [i for i, y in enumerate(qyears) if y in keep]
    sm, cn = qs[ix].sum(axis=0), qc[ix].sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        qm = np.where(cn > 0, sm / np.where(cn > 0, cn, 1), np.nan)
    s["q_mean"], s["q_mean_ann"] = qm, qm * G.ANN
    s["q5_minus_q1_ann"] = (qm[:, -1] - qm[:, 0]) * G.ANN
    s["mono"] = np.array([X.spearman(np.arange(1, G.N_Q + 1, dtype=float), qm[c]) for c in range(g)])
    return s


def col_row(s, c, name):
    f = lambda v: None if v is None or (isinstance(v, float) and not math.isfinite(v)) else float(v)  # noqa: E731
    return dict(name=name, t_ic=f(s["t_ic"][c]), ic_mean=f(s["ic_mean"][c]), ic_se=f(s["ic_se"][c]),
                positive_months=int(s["positive_months"][c]), hi_monthly=f(s["hi_monthly"][c]), hi_ann=f(s["hi_ann"][c]),
                hi_stock_months=int(s["hi_stock_months"][c]), hi_months=int(s["hi_months"][c]),
                hi_n_mean=f(s["hi_n_mean"][c]), q_mean_ann=[f(x) for x in s["q_mean_ann"][c]],
                q5_minus_q1_ann=f(s["q5_minus_q1_ann"][c]), mono=f(s["mono"][c]), half1=f(s["half1"][c]),
                half2=f(s["half2"][c]), block_sum=[f(x) for x in s["block_sum"][c]], ic_sum=f(s["ic_sum"][c]),
                block_max=f(s["block_max"][c]), years={str(y): f(v[c]) for y, v in s["years"].items()})


def main(exp="E026-08"):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    blob = joined(ls, "QRK")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"], "result blob hash"
    assert not any(x.startswith(("QRN|", "QRR|", "QRH|")) for x in ls), "unexpected output"
    out = json.loads(E.unpack(blob))
    prov = st["provenance"]
    assert prov["c_model"] == out["c_model"] == p9h024.C_MODEL and prov["c_feature"] == p9h024.C_FEATURE
    assert {k: float(v) for k, v in prov["c_fold"].items()} == {str(k): v for k, v in p9h024.C_FOLD.items()}
    assert prov["null_result_sha256"] == p9h024.NULL_RESULT_SHA256 == hashlib.sha256(
        (ROOT / p9h024.NULL_RESULT).read_bytes()).hexdigest()
    assert prov["threshold_commit"] == p9h024.THRESHOLD_COMMIT
    assert prov["panel_sha256"] == st["panel_sha256"] == p9h024.PANEL_SHA256
    assert prov["population_sha256"] == st["population_sha256"] == p9h024.POPULATION_SHA256
    assert prov["library_sha256"] == p9h024.LIBRARY_SHA256 and st["spec_sha256"] == p9h024.SPEC_SHA256
    lib = K.Library(K.model_library(tuple(p9h024.FEATURES), K.FAMILY, [tuple(x) for x in p9h024.LINKS]),
                    tuple(p9h024.FEATURES))
    assert lib.sha == p9h024.LIBRARY_SHA256 and out["models"] == [list(m) for m in lib.models]
    F, M = lib.F, lib.M
    w = dict(IC=np.array(out["IC"], float), HI=np.array(out["HI"], float), NH=np.array(out["NH"], np.int64),
             years=np.array(out["years"]))
    qs, qc, qyears = np.array(out["QM_year_sum"], float), np.array(out["QM_year_count"], float), out["qyears"]
    assert w["IC"].shape == (len(out["days"]), lib.ncol) and len(out["days"]) == DECISIONS
    s = summ(w, qs, qc, qyears)
    hs = out["summary"]
    recompute = {k: bool(np.allclose(np.array(s[k], float), np.array(hs[k], float), rtol=0, atol=0, equal_nan=True))
                 for k in ("t_ic", "ic_mean", "half1", "half2", "hi_ann", "hi_n_mean", "hi_months")}
    recompute["mono"] = bool(np.allclose(s["mono"], np.array(hs["mono"], float), atol=1e-12, equal_nan=True))
    recompute["q5_minus_q1"] = bool(np.allclose(s["q5_minus_q1_ann"], np.array(hs["q5_minus_q1_ann"], float),
                                                atol=1e-12, equal_nan=True))
    pick, gt, ranked = K.select(s, lib, p9h024.C_MODEL)
    recompute["selection"] = pick == out["pick"] and ranked == out["ranked"]
    for k in ("D1", "D2", "D3", "D4", "D5", "D6", "N", "qualified"):
        recompute[f"gate_{k}"] = [bool(x) for x in gt[k]] == [bool(x) for x in out["gates"][k]]
    fsel = []
    for y, c in zip(K.FOLD_YEARS, [p9h024.C_FOLD[y] for y in K.FOLD_YEARS]):
        if (w["years"] < y).sum() < 2 or not (w["years"] == y).any():      # qr_h024.fold: empty window
            fsel.append(None)
            continue
        sy = summ(w, qs, qc, qyears, rows=w["years"] < y)
        p_, _, _ = K.select(sy, lib, c)
        fsel.append(list(lib.models[p_]) if p_ is not None else
                    list(lib.models[int(np.argmax(sy["t_ic"][F:F + M]))]))
    recompute["walk_forward"] = fsel == [f["selected"] for f in out["walk_forward"]["folds"]]
    recompute["cstar"] = K.cstar(s, lib) == out["cstar"] or (math.isinf(K.cstar(s, lib)) and math.isinf(out["cstar"]))
    assert all(recompute.values()), recompute
    nulls = json.loads(gzip.open(ROOT / p9h024.NULL_WORLDS).read())
    nf = np.array([x["max_t_feature"] for x in nulls])
    nm = np.array([x["max_t_model"] for x in nulls])
    t = s["t_ic"]
    best_m = int(np.argmax(t[F:F + M]))
    best_f = int(np.argmax(t[:F]))
    pv = lambda v, n: dict(t_ic=float(v), null_share_ge=float(np.mean(n >= v)),  # noqa: E731
                           p_value=float((1 + np.sum(n >= v)) / (1 + n.size)), null_percentile=float(np.mean(n < v)))
    features = [dict(col_row(s, j, lib.features[j]), direction=K.DIRECTION[lib.features[j]],
                     passes_c_feature=bool(t[j] > p9h024.C_FEATURE and s["ic_mean"][j] > 0),
                     **{"search_adjusted": pv(t[j], nf)}) for j in range(F)]
    models = []
    for i in range(M):
        r = col_row(s, F + i, "+".join(lib.models[i]))
        r.update(features=list(lib.models[i]), k=int(lib.k[i]),
                 gates={k: bool(gt[k][i]) for k in ("D1", "D2", "D3", "D4", "D5", "D6", "N", "qualified")},
                 robust_neighbours=len(gt["robust_nbrs"][i]))
        models.append(r)
    counts = {k: int(np.sum(gt[k])) for k in ("D1", "D2", "D3", "D4", "D5", "D6", "N", "qualified")}
    selected = None
    record = rec_sha = None
    if pick is not None:
        m = lib.models[pick]
        loo = [dict(removed=f, remaining=[x for x in m if x != f],
                    ic_mean=float(s["ic_mean"][lib.loo[pick][j]]), t_ic=float(t[lib.loo[pick][j]]))
               for j, f in enumerate(m)]
        selected = dict(models[pick], leave_one_out=loo, neighbours=[dict(features=list(lib.models[x]),
                        t_ic=float(t[F + x]), ic_mean=float(s["ic_mean"][F + x]), robust=x in gt["robust_nbrs"][pick])
                        for x in lib.nbr[pick]], formulas={f: FORMULAS[f] for f in m})
        record = p9h024.candidate_record(m, st["real"]["blob_sha256"])
        rec_sha = p9h024.record_sha(record)
    ctrl = {"score_v1_40_45_15": col_row(s, lib.ctrl_cols[0], "Score v1"),
            "h023_80_10_10": col_row(s, lib.ctrl_cols[1], "H023 80/10/10")}
    pr = res["provenance"]
    result = dict(
        experiment=exp, qc_backtest_id=pr.get("qc_backtest_id"), build_commit=pr.get("build_commit"),
        lean_version=pr.get("lean_version"), run_utc=pr.get("run_utc"), status=res["status"],
        orders=res["harness_summary"]["orders"], owner_approved=pr.get("owner_approved"), provenance=prov,
        pit_audit=st.get("pit_audit"), decisions=st["decisions"], days=out["days"], population=out["n"],
        population_rows=int(sum(out["n"])), recompute=recompute,
        verdict=CANDIDATE if pick is not None else NONE, c_model=p9h024.C_MODEL, c_feature=p9h024.C_FEATURE,
        c_fold=p9h024.C_FOLD, best_model=dict(features=list(lib.models[best_m]), **pv(t[F + best_m], nm)),
        best_feature=dict(feature=lib.features[best_f], **pv(t[best_f], nf)), features=features, models=models,
        gate_counts=counts, selected=selected, walk_forward=out["walk_forward"], stability=out["stability"],
        top10=out["top10"], controls=ctrl, diagnostics=dict(h2=out["h2"], h3=out["h3"]), cstar=out["cstar"],
        candidate_record=record, candidate_sha256=rec_sha,
        runtime=dict(wall_s=st["wall_s"], max_rss_mb=st["max_rss_mb"], world_s=st["real"]["world_s"]))
    (HERE / "P9_CP1_result.json").write_text(json.dumps(result, indent=1, sort_keys=True, default=float) + "\n")
    print(result["verdict"])
    print(json.dumps(dict(best_model=result["best_model"], best_feature=result["best_feature"], counts=counts,
                          selected=None if selected is None else selected["features"], candidate_sha256=rec_sha,
                          features=[(x["name"], round(x["t_ic"], 2), round(x["ic_mean"], 4)) for x in features]),
                     indent=1))
    print("result sha256", hashlib.sha256((HERE / "P9_CP1_result.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
