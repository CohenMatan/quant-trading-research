"""P7-CP5 (D177): extract the H022 null worlds E023-01..05 -> research/phase7/P7_CP5_null_worlds.json.gz (per-world null
statistics, seeds 1..5,000) and research/phase7/P7_CP5_null.json (integrity, the null t_IC distribution, the empirical
one-sided 1% threshold, c_IC = max(threshold, 2.326) and the full-procedure gate pass rates with that c_IC). Run before
c_IC is pinned (qresearch.p7pred) and before the one real evaluation E023-06; reads no real-assignment statistic."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean")]
import qr_p7_export as E  # noqa: E402
import qr_p7_pred as R  # noqa: E402
import qr_xs as X  # noqa: E402
from qresearch import p7pred  # noqa: E402

sys.path.insert(0, str(HERE))
from P7_CP3R_extract import joined, lines  # noqa: E402
from P7_CP5_canary import uploaded_modules_ok  # noqa: E402

RUNS = ("E023-01", "E023-02", "E023-03", "E023-04", "E023-05")


def world(row, fields):
    d = dict(zip(fields, row))
    return dict(seed=int(d["seed"]), t_ic=d["t_ic"], ic_mean=d["ic_mean"], ic_se=d["ic_se"], hi_ann=d["hi_ann"],
                hi_months=d["hi_months"], hi_n_mean=d["hi_n_mean"], mono=d["mono"],
                q5_minus_q1_ann=d["q5_minus_q1_ann"], halves=[d["half1"], d["half2"]], block_max=d["block_max"],
                t_inc=d["t_inc"], inc_mean=d["inc_mean"], t_ic_sector=d["t_ic_sector"])


def main():
    can = json.loads((HERE / "P7_CP5_canary.json").read_text())
    worlds, runs = [], []
    for exp in RUNS:
        res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
        ls = lines(exp)
        st = json.loads(joined(ls, "QRP7S"))
        blob = joined(ls, "QRN")
        assert hashlib.sha256(blob.encode()).hexdigest() == st["null"]["blob_sha256"], f"{exp}: blob hash"
        pay = json.loads(E.unpack(blob))
        ws = [world(r, pay["fields"]) for r in pay["worlds"]]
        cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
        a, b = cfg["params"]["seeds"]
        runs.append(dict(experiment=exp, qc_backtest_id=res.get("qc_backtest_id"), commit=res.get("commit"),
                         seeds=[a, b], worlds=len(ws), complete=[w["seed"] for w in ws] == list(range(a, b + 1)),
                         panel_sha256=st["panel_sha256"], score_side_sha256=st["score_side_sha256"],
                         response_side_sha256=st["response_side_sha256"], decisions=st["null"]["dates"],
                         world_s=st["null"]["world_s"], wall_s=st["wall_s"], max_rss_mb=st["max_rss_mb"],
                         spec_sha256=st["spec_sha256"], uploaded_ok=uploaded_modules_ok(exp)[0]))
        worlds += ws
    seeds = [w["seed"] for w in worlds]
    panel = {r["panel_sha256"] for r in runs}
    integrity = dict(requested=5000, completed=len(worlds), failed=5000 - len(worlds), retried=0, recovered_runs=[],
                     seeds_exact=sorted(seeds) == list(p7pred.NULL_SEEDS), duplicate_seeds=len(seeds) - len(set(seeds)),
                     identical_panel_all_batches=len(panel) == 1,
                     panel_equals_canary=panel == {can["digests"]["panel_sha256"]},
                     finite_t_ic=int(sum(np.isfinite(w["t_ic"]) for w in worlds)),
                     spec_all=all(r["spec_sha256"] == p7pred.SPEC_SHA256 for r in runs),
                     module_all=all(r["uploaded_ok"] for r in runs))
    worlds.sort(key=lambda w: w["seed"])
    t = np.array([w["t_ic"] for w in worlds])
    c_emp = X.critical_value(list(t), R.ALPHA)
    c_ic = R.critical_value(worlds)
    gates = [R.promotion(w, c_ic) for w in worlds]
    gp = {g: int(sum(x[g] for x in gates)) for g in ("G1_significant", "G2_economic", "G3_monotonic", "G4_stable",
                                                       "pass")}
    q = lambda v, p: float(np.percentile(v, p))  # noqa: E731
    ti = np.array([w["t_inc"] for w in worlds])
    summary = dict(
        integrity=integrity, runs=runs,
        null_t_ic=dict(mean=float(t.mean()), sd=float(t.std(ddof=1)), min=float(t.min()), max=float(t.max()),
                       p50=q(t, 50), p90=q(t, 90), p95=q(t, 95), p99=q(t, 99), p995=q(t, 99.5),
                       rank50=float(np.sort(t)[::-1][49]), rank51=float(np.sort(t)[::-1][50])),
        null_t_inc=dict(mean=float(ti.mean()), sd=float(ti.std(ddof=1)), p95=q(ti, 95), p99=q(ti, 99)),
        empirical_threshold=float(c_emp), floor=R.CRIT_FLOOR, c_ic=float(c_ic), floor_binding=bool(c_ic == R.CRIT_FLOOR),
        share_t_ic_above_c=float(np.mean(t > c_ic)),
        gate_pass_counts=gp, gate_pass_shares={k: v / len(worlds) for k, v in gp.items()},
        false_promotion=R.false_promotion(worlds, c_ic),
        other=dict(hi_ann_mean=float(np.nanmean([w["hi_ann"] for w in worlds])),
                   hi_months_mean=float(np.mean([w["hi_months"] for w in worlds])),
                   mono_ge_090=float(np.mean([w["mono"] >= R.MONO_MIN for w in worlds]))),
        seed_definition="null world w uses numpy default_rng(w) in qr_p7_pred.Tether; w = 1..5,000 (E023-01 1-1000 ... "
                        "E023-05 4001-5000)",
        gate_definition="qr_p7_pred.promotion: G1 t_IC > c_IC and mean IC > 0; G2 80+ >= +3.0%/yr; G3 Spearman >= 0.90 "
                        "and Q5 > Q1; G4 both halves > 0 and largest block share <= 50%; all four required",
        spec_sha256=p7pred.SPEC_SHA256, code_sha256=p7pred.CODE_SHA256, host_sha256=p7pred.HOST_SHA256)
    raw = json.dumps(worlds, sort_keys=True, separators=(",", ":")).encode()
    with gzip.GzipFile(HERE / "P7_CP5_null_worlds.json.gz", "wb", mtime=0) as f:
        f.write(raw)
    summary["worlds_file_sha256"] = hashlib.sha256((HERE / "P7_CP5_null_worlds.json.gz").read_bytes()).hexdigest()
    summary["worlds_json_sha256"] = hashlib.sha256(raw).hexdigest()
    (HERE / "P7_CP5_null.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in ("integrity", "null_t_ic", "empirical_threshold", "c_ic",
                                              "gate_pass_counts", "false_promotion")}, indent=1))
    print("null result sha256", hashlib.sha256((HERE / "P7_CP5_null.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    sys.exit(main())
