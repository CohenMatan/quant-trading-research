"""Phase 3 runtime / memory / output canary analysis (P3-CP2; owner instruction: infrastructure only, dummy configs).
Reads the X984 canary runs (DUMMY random masks over the real universe; no technical signal is ever used) and reports:
wall time and its components, per-world marginal cost, memory, published bytes, QuantConnect limits observed,
determinism of identical seeds across runs (batch independence), and the projected runtime of the frozen run plan
(P3_spec.md §19: 5 x 100 primary null worlds, 100 block-null worlds, 1 real world).

    PYTHONPATH=src python research/phase3/P3_canary_report.py -> research/phase3/P3_canary_report.json
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RUNS = ("E984-02", "E984-03", "E984-05", "E984-06", "E984-07", "E984-08")
DIGEST_PAIRS = (("E984-05", "E984-06"), ("E984-07", "E984-08"))     # 100 worlds vs 1 world, before / after the fix
OUT = Path(__file__).with_name("P3_canary_report.json")
PER_WORLD = ("engine", "select", "stats", "pipeline")
SHARED = ("bars", "corp", "history", "features", "masks")


def load(exp):
    p = ROOT / "experiments" / exp / "result.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text())
    q = r["qc_statistics"]
    text = "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"])))
    L = text.split("\n")
    summ = json.loads(next(x for x in L if x.startswith("QRX984|summary|")).split("|", 2)[2])
    wc = {}
    for x in L:
        if x.startswith("WC|"):
            _, name, t, ent, ex, forced = x.split("|")
            wc[name] = dict(pipeline_s=float(t), entries=int(ent), exits=int(ex), forced=int(forced))
    return dict(summary=summ, wc=wc, published_chars=len(text), chunks=int(q["qr_msgs_n"]),
                runtime_s=r["provenance"]["runtime_s"], status=r["status"],
                y_lines=sum(1 for x in L if x.startswith("Y|")), wf_lines=sum(1 for x in L if x.startswith("WF|")))


def main():
    runs = {e: load(e) for e in RUNS}
    runs = {e: v for e, v in runs.items() if v is not None}
    rows = {}
    for e, v in runs.items():
        s = v["summary"]
        c = s["clock_s"]
        rows[e] = dict(worlds=s["worlds"], books=s["worlds"] * s["books_per_world"], sessions=s["official_sessions"],
                       algorithm_wall_s=s["wall_s"], runner_runtime_s=round(v["runtime_s"], 1),
                       shared_s=round(sum(c[k] for k in SHARED), 1), per_world_total_s=round(sum(c[k] for k in PER_WORLD), 1),
                       clock_s=c, max_rss_mb=s["max_rss_mb"], max_eligible=s["max_eligible"],
                       stocks_indexed=s["stocks_indexed"], published_chars=v["published_chars"], chunks=v["chunks"],
                       y_lines=v["y_lines"], wf_lines=v["wf_lines"], status=v["status"],
                       real_mask_digest=s.get("real_mask_digest"), real_mask_cells=s.get("real_mask_cells"),
                       loaded_histories=s["loaded_histories"])
    # marginal cost per world from the two sizes (least squares over runs on wall time)
    w = np.array([rows[e]["worlds"] for e in rows], float)
    t = np.array([rows[e]["algorithm_wall_s"] for e in rows], float)
    rt = np.array([rows[e]["runner_runtime_s"] for e in rows], float)
    fit = np.polyfit(w, t, 1) if len(set(w)) > 1 else (np.nan, np.nan)
    fit_rt = np.polyfit(w, rt, 1) if len(set(w)) > 1 else (np.nan, np.nan)
    # determinism: identical seeds in different runs (batch independence)
    det = []
    names = set().union(*[set(v["wc"]) for v in runs.values()]) if runs else set()
    for n in sorted(names):
        vals = {e: (runs[e]["wc"][n]["entries"], runs[e]["wc"][n]["exits"], runs[e]["wc"][n]["forced"])
                for e in runs if n in runs[e]["wc"]}
        if len(vals) > 1:                                   # the same seeded world in several runs
            det.append(dict(world=n, runs=sorted(vals), identical=len(set(vals.values())) == 1, counts=vals))
    digests = [dict(pair=list(p), equal=rows[p[0]]["real_mask_digest"] == rows[p[1]]["real_mask_digest"],
                    cells=[rows[p[0]]["real_mask_cells"], rows[p[1]]["real_mask_cells"]])
               for p in DIGEST_PAIRS if p[0] in rows and p[1] in rows]
    plan_worlds = [100] * 6 + [1]
    proj = [float(fit_rt[0] * k + fit_rt[1]) for k in plan_worlds]
    out = dict(runs=rows, marginal_wall_s_per_world=float(fit[0]), fixed_wall_s=float(fit[1]),
               marginal_runtime_s_per_world=float(fit_rt[0]), fixed_runtime_s=float(fit_rt[1]),
               determinism=dict(worlds_compared=len(det), all_identical=all(d["identical"] for d in det),
                                details=det[:10]),
               real_mask_digests=digests,
               plan=dict(runs=len(plan_worlds), worlds=plan_worlds, projected_runtime_s=proj,
                         projected_total_h=sum(proj) / 3600.0),
               note="dummy masks (random, seeded) over the real universe: timing, memory and output only; the "
                    "real search has fewer entries than the dense dummy masks, so per-world costs are upper bounds")
    OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("marginal_wall_s_per_world", "fixed_wall_s", "determinism", "plan")},
                     indent=1, default=float)[:3000])
    for e, r in rows.items():
        print(e, r["worlds"], r["algorithm_wall_s"], r["runner_runtime_s"], r["max_rss_mb"], r["published_chars"])


if __name__ == "__main__":
    main()
