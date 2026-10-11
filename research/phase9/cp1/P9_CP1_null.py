"""P9-CP1 (owner D201): extract the H024 null worlds E026-02..06 (seeds 1..5,000) and the determinism rerun E026-07
-> research/phase9/cp1/P9_CP1_null_worlds.json.gz and research/phase9/cp1/P9_CP1_null.json: integrity (pinned
population / library / panel in every batch, exact seeds, identical rerun), the null distributions of the maximum
feature t_IC and the maximum model t_IC, c_FEATURE, c_MODEL, the walk-forward fold thresholds and the full-procedure
false-promotion rate. Reads no real-assignment statistic (none exists before E026-08)."""
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
import qr_h024 as K  # noqa: E402
import qr_p7_export as E  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from P9_CP1_canary import uploaded  # noqa: E402
from qresearch import p9h024  # noqa: E402


def batch(exp):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    blob = joined(ls, "QRK")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["null"]["blob_sha256"], f"{exp}: blob hash"
    assert not any(x.startswith(("QRR|", "QRN|", "QRH|")) for x in ls), f"{exp}: unexpected output"
    pay = json.loads(E.unpack(blob))
    assert pay["fields"] == list(K.NULL_FIELDS)
    ws = [dict(zip(pay["fields"], r)) for r in pay["worlds"]]
    a, b = json.loads((ROOT / "experiments" / exp / "config.json").read_text())["params"]["seeds"]
    pv = res["provenance"]
    run = dict(experiment=exp, qc_backtest_id=pv.get("qc_backtest_id"), build_commit=pv.get("build_commit"),
               lean_version=pv.get("lean_version"), status=res["status"], orders=res["harness_summary"]["orders"],
               seeds=[a, b], worlds=len(ws), complete=[w["seed"] for w in ws] == list(range(a, b + 1)),
               panel_sha256=st["panel_sha256"], population_sha256=st["population_sha256"],
               decisions=st["null"]["dates"], models=st["null"]["models"], features=st["null"]["features"],
               world_s=st["null"]["world_s"], wall_s=st["wall_s"], max_rss_mb=st["max_rss_mb"],
               spec_sha256=st["spec_sha256"], pit_audit=st.get("pit_audit"), uploaded_ok=uploaded(exp)[0])
    return run, ws


def main():
    worlds, runs = [], []
    for exp in p9h024.NULL_RUNS:
        r, ws = batch(exp)
        runs.append(r)
        worlds += ws
    rr, rws = batch(p9h024.RERUN)
    by_seed = {w["seed"]: w for w in worlds}
    rerun_identical = len(rws) == p9h024.RERUN_SEEDS[1] - p9h024.RERUN_SEEDS[0] + 1 and all(
        json.dumps(w, sort_keys=True) == json.dumps(by_seed[w["seed"]], sort_keys=True) for w in rws)
    seeds = [w["seed"] for w in worlds]
    allr = runs + [rr]
    integrity = dict(
        requested=5000, completed=len(worlds), seeds_exact=sorted(seeds) == list(p9h024.NULL_SEEDS),
        duplicate_seeds=len(seeds) - len(set(seeds)),
        panel_equals_pinned=all(r["panel_sha256"] == p9h024.PANEL_SHA256 for r in allr),
        population_equals_pinned=all(r["population_sha256"] == p9h024.POPULATION_SHA256 for r in allr),
        models_equal_pinned=all(r["models"] == p9h024.MODEL_COUNT for r in allr),
        spec_all=all(r["spec_sha256"] == p9h024.SPEC_SHA256 for r in allr),
        uploaded_all=all(r["uploaded_ok"] for r in allr), builds=sorted({r["lean_version"] for r in allr}),
        zero_orders=all(r["orders"] == 0 for r in allr), decisions_83=all(r["decisions"] == 83 for r in allr),
        pit_audit_zero=all(r["pit_audit"] and all(v == 0 for v in r["pit_audit"].values()) for r in allr),
        rerun_identical=rerun_identical, finite=int(sum(math.isfinite(w["max_t_model"]) for w in worlds)))
    worlds.sort(key=lambda w: w["seed"])
    mf = np.array([w["max_t_feature"] for w in worlds])
    mm = np.array([w["max_t_model"] for w in worlds])
    c_feature, c_model = K.critical_value(mf), K.critical_value(mm)
    c_fold = {str(y): K.critical_value([w[f"max_t_model_fold{y}"] for w in worlds]) for y in K.FOLD_YEARS}
    cs = np.array([w["cstar"] for w in worlds])
    q = lambda v, p: float(np.percentile(v, p))  # noqa: E731
    dist = lambda v: dict(mean=float(v.mean()), sd=float(v.std(ddof=1)), min=float(v.min()), max=float(v.max()),  # noqa: E731
                          p50=q(v, 50), p90=q(v, 90), p95=q(v, 95), p99=q(v, 99),
                          rank50=float(np.sort(v)[::-1][49]), rank51=float(np.sort(v)[::-1][50]))
    feats = list(p9h024.FEATURES)
    summary = dict(
        hypothesis="H024", decision=p9h024.DECISION, data_manifest=p9h024.DATA_FREEZE_MANIFEST_SHA256,
        library_sha256=p9h024.LIBRARY_SHA256, models=p9h024.MODEL_COUNT, features=feats,
        integrity=integrity, runs=runs, rerun=dict(experiment=p9h024.RERUN, worlds=len(rws), identical=rerun_identical,
                                                   lean_version=rr["lean_version"]),
        null_max_feature_t=dist(mf), null_max_model_t=dist(mm),
        argmax_feature_counts={feats[i]: int(n) for i, n in enumerate(np.bincount([w["argmax_feature"] for w in worlds],
                                                                                  minlength=len(feats)))},
        c_feature=float(c_feature), c_model=float(c_model), c_fold=c_fold,
        floor=K.CRIT_FLOOR, floor_binding=dict(feature=bool(c_feature == K.CRIT_FLOOR), model=bool(c_model == K.CRIT_FLOOR)),
        false_promotion=float(np.mean(cs > c_model)),
        worlds_with_pre_d1_models=float(np.mean([w["n_pre_d1"] > 0 for w in worlds])),
        threshold_rule="c = max(k-th largest of the 5,000 null maxima, k = ceil(0.01 x 5,000) = 50, 2.326) -- "
                       "qr_xs.critical_value (frozen convention); c_FEATURE over the 11 oriented features, c_MODEL over "
                       "the model library, c_FOLD(Y) over the model library on decision years < Y",
        seed_definition="null world w uses qr_p7_pred.Tether(w) (the H022 seeds); one permutation per date re-indexes "
                        "each stock's complete feature vector; E026-02 1-1000 .. E026-06 4001-5000; E026-07 rerun 1-25",
        false_promotion_definition="share of null worlds in which the full frozen procedure (D1-D6 + neighbourhood "
                                   "with c_MODEL) would produce a candidate: cstar > c_MODEL",
        spec_sha256=p9h024.SPEC_SHA256, feature_code_sha256=p9h024.CODE_SHA256["src/qresearch/lean/qr_h024.py"])
    raw = json.dumps(worlds, sort_keys=True, separators=(",", ":")).encode()
    with gzip.GzipFile(HERE / "P9_CP1_null_worlds.json.gz", "wb", mtime=0) as f:
        f.write(raw)
    summary["worlds_file_sha256"] = hashlib.sha256((HERE / "P9_CP1_null_worlds.json.gz").read_bytes()).hexdigest()
    summary["worlds_json_sha256"] = hashlib.sha256(raw).hexdigest()
    (HERE / "P9_CP1_null.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in ("integrity", "null_max_feature_t", "null_max_model_t", "c_feature",
                                              "c_model", "c_fold", "false_promotion", "worlds_with_pre_d1_models")},
                     indent=1))
    print("null result sha256", hashlib.sha256((HERE / "P9_CP1_null.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    sys.exit(main())
