"""H021-A evaluation (research/phase6/H021A_spec.md v1; owner authorisation 2026-10-06, D160).

  python research/phase6/H021A_eval.py canary -> H021A_canary_report.json (E989-01 fidelity checks)
  python research/phase6/H021A_eval.py null   -> H021A_null_result.json + H021A_null_worlds.csv (E022-01..05): the null
                                                 distribution, c = the 50th largest of 5,000 t_IC, the full-procedure
                                                 false-qualification rate. Committed and pinned BEFORE E022-06.
  python research/phase6/H021A_eval.py real   -> H021A_real_result.json (E022-06, judged with the PINNED c)

Every number comes from the published aggregates of the QuantConnect runs (experiments/<id>/result.json); no price
data is stored. The real evaluation refuses to run unless the pins in qresearch.p6h021 match the run's config.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import qr_h021 as H  # noqa: E402
from qresearch import p6h021  # noqa: E402

HERE = Path(__file__).resolve().parent
CANARY_OUT = HERE / "H021A_canary_report.json"
NULL_OUT = ROOT / p6h021.NULL_RESULT
NULL_TABLE = HERE / "H021A_null_worlds.csv"
REAL_OUT = HERE / "H021A_real_result.json"
FIELDS = ("t", "ic", "top", "mid", "bot", "h1", "h2", "bs", "sum")


def result(exp):
    """The run's result; if the original failed and was recovered (D077, run.py --recover), the latest completed
    recovery of the same QuantConnect backtest."""
    d = ROOT / "experiments" / exp
    r = json.loads((d / "result.json").read_text())
    if r.get("status") == "completed":
        return r
    for rp in sorted((d / "recovery").glob("*/result.json"), reverse=True):
        rr = json.loads(rp.read_text())
        if rr.get("status") == "completed" and rr["provenance"].get("qc_backtest_id") == r["provenance"].get(
                "qc_backtest_id"):
            return rr
    raise SystemExit(f"{exp}: no completed result (status {r.get('status')})")


def lines(exp):
    q = result(exp)["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def tagged(exp, tag):
    return [ln[len(tag) + 1:] for ln in lines(exp) if ln.startswith(tag + "|")]


def summary(exp):
    return json.loads(tagged(exp, "QRX989")[0].split("|", 1)[1])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canary():
    k = json.loads(tagged(p6h021.CANARY, "K")[0])
    s = summary(p6h021.CANARY)
    out = dict(run=p6h021.CANARY, qc_backtest_id=result(p6h021.CANARY)["provenance"].get("qc_backtest_id"),
               checks=k, panel=s["panel"], wall_s=s.get("wall_s"))
    CANARY_OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    oks = {x: v for x, v in k.items() if x.endswith("_ok") or x in ("all_ok", "future_perturbation_changed")}
    print(json.dumps(oks, indent=1))


def null():
    canary_panel = json.loads(CANARY_OUT.read_text())["panel"]
    worlds, batches = {}, []
    for exp, (a, b) in zip(p6h021.NULL_RUNS, p6h021.NULL_BATCHES):
        r = result(exp)
        s = summary(exp)
        if (s["panel"]["panel_sha256"], s["panel"]["diag_sha256"]) != (canary_panel["panel_sha256"],
                                                                         canary_panel["diag_sha256"]):
            raise SystemExit(f"{exp}: the panel differs from the canary's")
        got = 0
        for ln in tagged(exp, "N"):
            seed, js = ln.split("|", 1)
            seed = int(seed)
            if not a <= seed <= b or seed in worlds:
                raise SystemExit(f"{exp}: unexpected or duplicate seed {seed}")
            w = json.loads(js)
            worlds[seed] = dict(t=w["t"], ic=w["ic"], top=w["top"], mid=w["mid"], bot=w["bot"], h1=w["h"][0],
                                h2=w["h"][1], bs=w["bs"], sum=w["sum"])
            got += 1
        orig = json.loads((ROOT / "experiments" / exp / "result.json").read_text()).get("status")
        batches.append(dict(run=exp, seeds=[a, b], worlds=got, qc_backtest_id=r["provenance"].get("qc_backtest_id"),
                            original_status=orig, recovered=orig != "completed",
                            wall_s=s.get("wall_s"), world_s=s.get("null", {}).get("world_s")))
    if sorted(worlds) != list(p6h021.NULL_SEEDS):
        raise SystemExit(f"null incomplete: {len(worlds)} of 5000 worlds")
    with NULL_TABLE.open("w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(("seed",) + FIELDS)
        for seed in sorted(worlds):
            wr.writerow([seed] + [repr(float(worlds[seed][k])) if worlds[seed][k] is not None else "" for k in FIELDS])
    t = np.array([worlds[s]["t"] for s in sorted(worlds)], float)
    c = H.critical_value(t)
    full = 0
    for s in worlds.values():
        g = H.gates(dict(t_ic=s["t"], top_ann=s["top"], mid_ann=s["mid"], bot_ann=s["bot"], halves=[s["h1"], s["h2"]],
                         ic_sum=s["sum"], block_share={"max": s["bs"] if s["bs"] is not None else float("inf")}), c)
        full += int(g["qualified"])
    out = dict(
        spec_sha256=p6h021.SPEC_SHA256, code_sha256=p6h021.CODE_SHA256,
        host_sha256={h: p6h021.sha256(h) for h in p6h021.HOST_CODE},
        worlds_completed=len(worlds), worlds_failed=0, batches=batches,
        c=c, alpha=H.ALPHA, rank_of_c=int(np.ceil(H.ALPHA * t.size)),
        null_t=dict(mean=float(t.mean()), sd=float(t.std()), min=float(t.min()), max=float(t.max()),
                    q=dict(zip(("p01", "p05", "p50", "p95", "p99"),
                               map(float, np.quantile(t, [0.01, 0.05, 0.5, 0.95, 0.99]))))),
        null_share_t_gt_c=float(np.mean(t > c)), null_full_procedure_qualified=full,
        null_full_procedure_rate=full / len(worlds),
        null_share_p2=float(np.mean([w["top"] >= H.ECON_MIN for w in worlds.values()])),
        panel_sha256=canary_panel["panel_sha256"], diag_sha256=canary_panel["diag_sha256"],
        null_worlds_csv_sha256=sha(NULL_TABLE))
    NULL_OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("worlds_completed", "c", "null_t", "null_full_procedure_qualified",
                                          "panel_sha256", "null_worlds_csv_sha256")}, indent=1))
    print("null_result_sha256", sha(NULL_OUT))


def real():
    cfg = json.loads((ROOT / "experiments" / p6h021.REAL_RUN / "config.json").read_text())["params"]
    pins = dict(threshold_c=p6h021.C, threshold_commit=p6h021.THRESHOLD_COMMIT,
                null_result_sha256=p6h021.NULL_RESULT_SHA256, spec_sha256=p6h021.SPEC_SHA256,
                panel_sha256=p6h021.PANEL_SHA256, diag_sha256=p6h021.DIAG_SHA256)
    if any(cfg[k] != v for k, v in pins.items()) or sha(NULL_OUT) != p6h021.NULL_RESULT_SHA256:
        raise SystemExit("the real run's provenance differs from the pins")
    r = json.loads(tagged(p6h021.REAL_RUN, "R")[0])
    ser = json.loads(tagged(p6h021.REAL_RUN, "RS")[0])
    diag = json.loads(tagged(p6h021.REAL_RUN, "RD")[0])
    s = summary(p6h021.REAL_RUN)
    if (s["panel"]["panel_sha256"], s["panel"]["diag_sha256"]) != (p6h021.PANEL_SHA256, p6h021.DIAG_SHA256):
        raise SystemExit("the real panel differs from the pinned one")
    null_t = []
    with NULL_TABLE.open() as f:
        for row in csv.DictReader(f):
            null_t.append(float(row["t"]))
    null_t = np.array(null_t)
    t = r["summary"]["t_ic"]
    sm = r["summary"]
    verdict = "H021-A QUALIFIED FOR PORTFOLIO-DESIGN RESEARCH" if r["gates"]["qualified"] else "H021-A DID NOT QUALIFY"
    out = dict(run=p6h021.REAL_RUN, qc_backtest_id=result(p6h021.REAL_RUN)["provenance"].get("qc_backtest_id"),
               commit=result(p6h021.REAL_RUN)["provenance"].get("git_commit"), pins=pins, summary=sm, gates=r["gates"],
               c=r["c"], verdict=verdict,
               empirical_p=float((1 + np.sum(null_t >= t)) / (1 + null_t.size)),
               null_percentile=float(np.mean(null_t < t)),
               series=ser, diagnostics=diag, panel=s["panel"])
    REAL_OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(summary=sm, gates=r["gates"], c=r["c"], verdict=verdict, p=out["empirical_p"],
                          pct=out["null_percentile"]), indent=1))
    print(json.dumps(diag, indent=1))


if __name__ == "__main__":
    {"canary": canary, "null": null, "real": real}[sys.argv[1]]()
