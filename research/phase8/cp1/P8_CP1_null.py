"""P8-CP1 (owner D199): extract the H023 optimiser-null worlds E025-02..06 (seeds 1..5,000) and the determinism rerun
E025-07 -> research/phase8/cp1/P8_CP1_null_worlds.json.gz (per-world records) and research/phase8/cp1/P8_CP1_null.json
(integrity, the null distribution of max_t_IC across the 92-configuration grid, c_SEARCH, the walk-forward fold
thresholds and the full-procedure false-promotion rate). Pre-registered integrity checks (spec section 7): pinned panel
and layer-subtotal digests in every batch, seeds exactly 1..5,000, identical rerun, and every world's control column
(40/45/15) equal to the frozen H022 / Data v2 null world of the same seed. Reads no real-assignment statistic (none
exists before E025-08)."""
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
from P7_CP3R_extract import joined, lines  # noqa: E402
from P8_CP1_canary import uploaded  # noqa: E402
from qresearch import p8h023  # noqa: E402


def batch(exp):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    blob = joined(ls, "QRH")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["null"]["blob_sha256"], f"{exp}: blob hash"
    assert not any(x.startswith(("QRR|", "QRN|")) for x in ls), f"{exp}: unexpected output"
    pay = json.loads(E.unpack(blob))
    assert pay["fields"] == list(G.NULL_FIELDS)
    ws = [dict(zip(pay["fields"], r)) for r in pay["worlds"]]
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    a, b = cfg["params"]["seeds"]
    pv = res["provenance"]
    run = dict(experiment=exp, qc_backtest_id=pv.get("qc_backtest_id"), build_commit=pv.get("build_commit"),
               lean_version=pv.get("lean_version"), status=res["status"], orders=res["harness_summary"]["orders"],
               seeds=[a, b], worlds=len(ws), complete=[w["seed"] for w in ws] == list(range(a, b + 1)),
               panel_sha256=st["panel_sha256"], components_sha256=st["components_sha256"],
               decisions=st["null"]["dates"], grid=st["null"]["grid"], world_s=st["null"]["world_s"],
               wall_s=st["wall_s"], max_rss_mb=st["max_rss_mb"], spec_sha256=st["spec_sha256"],
               pit_audit=st.get("pit_audit"), uploaded_ok=uploaded(exp)[0])
    return run, ws


def main():
    worlds, runs = [], []
    for exp in p8h023.NULL_RUNS:
        r, ws = batch(exp)
        runs.append(r)
        worlds += ws
    rr, rws = batch(p8h023.RERUN)
    by_seed = {w["seed"]: w for w in worlds}
    h022 = {w["seed"]: w for w in json.loads(gzip.open(ROOT / p8h023.H022_NULL_WORLDS).read())}
    dc = [abs(w["t_control"] - h022[w["seed"]]["t_ic"]) for w in worlds]
    di = [abs(w["ic_control"] - h022[w["seed"]]["ic_mean"]) for w in worlds]
    rerun_identical = len(rws) == p8h023.RERUN_SEEDS[1] - p8h023.RERUN_SEEDS[0] + 1 and all(
        json.dumps(w, sort_keys=True) == json.dumps(by_seed[w["seed"]], sort_keys=True) for w in rws)
    seeds = [w["seed"] for w in worlds]
    allr = runs + [rr]
    integrity = dict(
        requested=5000, completed=len(worlds), seeds_exact=sorted(seeds) == list(p8h023.NULL_SEEDS),
        duplicate_seeds=len(seeds) - len(set(seeds)),
        panel_equals_pinned=all(r["panel_sha256"] == p8h023.PANEL_SHA256 for r in allr),
        components_equal_pinned=all(r["components_sha256"] == p8h023.COMPONENTS_SHA256 for r in allr),
        spec_all=all(r["spec_sha256"] == p8h023.SPEC_SHA256 for r in allr),
        uploaded_all=all(r["uploaded_ok"] for r in allr), builds=sorted({r["lean_version"] for r in allr}),
        zero_orders=all(r["orders"] == 0 for r in allr), grid_92=all(r["grid"] == 92 for r in allr),
        decisions_83=all(r["decisions"] == 83 for r in allr),
        pit_audit_zero=all(r["pit_audit"] and all(v == 0 for v in r["pit_audit"].values()) for r in allr),
        rerun_identical=rerun_identical,
        control_equals_h022_null=dict(max_abs_diff_t=max(dc), max_abs_diff_ic=max(di), all_within_1e9=max(dc) <= 1e-9),
        finite_max_t=int(sum(math.isfinite(w["max_t"]) for w in worlds)))
    worlds.sort(key=lambda w: w["seed"])
    mt = np.array([w["max_t"] for w in worlds])
    c_search = G.critical_value(mt)
    c_emp = G.critical_value(mt, floor=-math.inf)
    c_fold = {}
    for y in G.FOLD_YEARS:
        c_fold[str(y)] = G.critical_value([w[f"max_t_fold{y}"] for w in worlds])
    cs = np.array([w["cstar"] for w in worlds])
    q = lambda v, p: float(np.percentile(v, p))  # noqa: E731
    srt = np.sort(mt)[::-1]
    am = np.bincount([w["argmax"] for w in worlds], minlength=len(G.GRID))
    summary = dict(
        hypothesis="H023", decision=p8h023.DECISION, data_manifest=p8h023.DATA_FREEZE_MANIFEST_SHA256,
        integrity=integrity, runs=runs, rerun=dict(experiment=p8h023.RERUN, worlds=len(rws), identical=rerun_identical,
                                                   lean_version=rr["lean_version"]),
        null_max_t=dict(mean=float(mt.mean()), sd=float(mt.std(ddof=1)), min=float(mt.min()), max=float(mt.max()),
                        p50=q(mt, 50), p90=q(mt, 90), p95=q(mt, 95), p99=q(mt, 99), rank50=float(srt[49]),
                        rank51=float(srt[50])),
        null_control_t=dict(mean=float(np.mean([w["t_control"] for w in worlds])),
                            p99=q([w["t_control"] for w in worlds], 99)),
        argmax_counts={str(list(G.GRID[i])): int(n) for i, n in enumerate(am) if n},
        argmax_on_boundary_share=float(np.mean([G.on_boundary(G.GRID[w["argmax"]]) for w in worlds])),
        empirical_threshold=float(c_emp), floor=G.CRIT_FLOOR, c_search=float(c_search),
        floor_binding=bool(c_search == G.CRIT_FLOOR), c_fold=c_fold,
        share_max_t_above_c=float(np.mean(mt > c_search)),
        plateaus=dict(mean_n=float(np.mean([w["n_plateaus"] for w in worlds])),
                      share_any=float(np.mean([w["n_plateaus"] > 0 for w in worlds])),
                      mean_n_base=float(np.mean([w["n_base"] for w in worlds]))),
        false_promotion=float(np.mean(cs > c_search)),
        any_config_d1_d5_share=float(np.mean([w["max_t_d2_5"] > c_search for w in worlds])),
        threshold_rule="c_SEARCH = max(k-th largest of the 5,000 null max_t_IC across the 92-configuration grid, k = "
                       "ceil(0.01 x 5,000) = 50, 2.326) -- qr_h023.critical_value = qr_xs.critical_value, the H022 "
                       "convention; c_fold(Y) by the same rule on the null maxima over decision years < Y",
        seed_definition="null world w uses qr_p7_pred.Tether(w) (= the H022 seeds); one permutation per date for the "
                        "whole grid; w = 1..5,000 (E025-02 1-1000 .. E025-06 4001-5000); E025-07 = rerun of seeds 1-25",
        false_promotion_definition="share of null worlds in which the full frozen procedure (plateau + D1-D5 with "
                                   "c_SEARCH) would produce a candidate: cstar > c_SEARCH",
        spec_sha256=p8h023.SPEC_SHA256, grid_code_sha256=p8h023.CODE_SHA256["src/qresearch/lean/qr_h023.py"])
    raw = json.dumps(worlds, sort_keys=True, separators=(",", ":")).encode()
    with gzip.GzipFile(HERE / "P8_CP1_null_worlds.json.gz", "wb", mtime=0) as f:
        f.write(raw)
    summary["worlds_file_sha256"] = hashlib.sha256((HERE / "P8_CP1_null_worlds.json.gz").read_bytes()).hexdigest()
    summary["worlds_json_sha256"] = hashlib.sha256(raw).hexdigest()
    (HERE / "P8_CP1_null.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in ("integrity", "null_max_t", "c_search", "c_fold", "false_promotion",
                                              "any_config_d1_d5_share", "plateaus")}, indent=1))
    print("null result sha256", hashlib.sha256((HERE / "P8_CP1_null.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    sys.exit(main())
