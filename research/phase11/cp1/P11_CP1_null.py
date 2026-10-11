"""P11-CP1 (owner D206): aggregate the H026 null worlds (S028 null mode) -> P11_CP1_null.json.

E028-02 (seeds 1-2,500) + E028-03 (2,501-5,000) = the 5,000 full-pipeline worlds (identity-tether permutation of complete
11-feature vectors; inner lambda selection, annual Ridge fits, Top-15 portfolio, costs, SPY comparison rerun in every
world). E028-04 reruns seeds 1-25 independently: every value must reproduce exactly. Every run must carry the pinned
feature panel and the same response-panel digest (real labels only hashed, never summarised).
c_WEALTH = the 50th largest S_WEALTH of 5,000 (qr_h026.critical_value; empirical one-sided 99th percentile).

    PYTHONPATH=src python research/phase11/cp1/P11_CP1_null.py
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402
import qr_h026 as H  # noqa: E402
import qr_p7_export as E  # noqa: E402
from qresearch import p11h026 as P  # noqa: E402


def run(exp):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRW"))
    blob = joined(ls, "QRWN")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["null"]["blob_sha256"], f"{exp}: null blob hash"
    nb = json.loads(E.unpack(blob))
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    return st, nb, prov


def main():
    runs = {e: run(e) for e in P.NULL_RUNS + (P.RERUN,)}
    fields = runs[P.NULL_RUNS[0]][1]["fields"]
    worlds = {}
    for e in P.NULL_RUNS:
        for w in runs[e][1]["worlds"]:
            assert w[0] not in worlds
            worlds[w[0]] = w
    seeds = sorted(worlds)
    rr = {w[0]: w for w in runs[P.RERUN][1]["worlds"]}
    S = np.array([worlds[s][1] for s in seeds], float)
    c = H.critical_value(S.tolist())
    col = {f: i for i, f in enumerate(fields)}
    arr = lambda f: np.array([worlds[s][col[f]] for s in seeds], float)  # noqa: E731
    checks = dict(
        seeds_1_to_5000=seeds == list(range(1, H.R_NULL + 1)),
        all_finite=bool(np.all(np.isfinite(S))),
        feature_panel_pinned=all(r[0]["feature_panel_sha256"] == P.FEATURE_PANEL_SHA256 for r in runs.values()),
        response_panel_identical=len({r[0]["response_panel_sha256"] for r in runs.values()}) == 1,
        rerun_1_25_identical=sorted(rr) == list(range(1, 26)) and all(rr[s] == worlds[s] for s in rr),
        same_lean_build=len({r[2]["lean_version"] for r in runs.values()}) == 1,
        pit_audit_zero=all(all(v == 0 for v in r[0]["pit_audit"].values()) for r in runs.values()))
    lam = {y: dict(zip(*np.unique(arr(f"lam_{y}"), return_counts=True))) for y in H.OUTER_YEARS}
    out = dict(
        worlds=len(seeds), fields=fields, c_wealth=c, rank=50, alpha=H.ALPHA, checks=checks,
        all_checks=all(checks.values()),
        response_panel_sha256=runs[P.NULL_RUNS[0]][0]["response_panel_sha256"],
        feature_panel_sha256=P.FEATURE_PANEL_SHA256,
        S_WEALTH=dict(mean=float(S.mean()), sd=float(S.std(ddof=1)), median=float(np.median(S)),
                      p90=float(np.quantile(S, 0.90)), p95=float(np.quantile(S, 0.95)), p99=float(np.quantile(S, 0.99)),
                      max=float(S.max()), min=float(S.min()), share_positive=float(np.mean(S > 0))),
        excess_cagr=dict(median=float(np.median(arr("excess_cagr"))), p99=float(np.quantile(arr("excess_cagr"), 0.99))),
        years_beating=dict(zip(*[x.tolist() for x in np.unique(arr("years_beating"), return_counts=True)])),
        maxdd_median=float(np.median(arr("maxdd"))), vol_median=float(np.median(arr("vol"))),
        lambda_choice_by_year={str(y): {str(k): int(v) for k, v in d.items()} for y, d in lam.items()},
        runs={e: dict(git_commit=r[2]["git_commit"], lean_version=r[2]["lean_version"],
                      qc_backtest_id=r[2]["qc_backtest_id"], seeds=r[0]["null"]["seeds"], worlds=r[0]["null"]["worlds"],
                      world_s=r[0]["null"]["world_s"], blob_sha256=r[0]["null"]["blob_sha256"],
                      max_rss_mb=r[0].get("max_rss_mb"), wall_s=r[0].get("wall_s")) for e, r in runs.items()},
        world_values_sha256=hashlib.sha256(json.dumps([worlds[s] for s in seeds]).encode()).hexdigest())
    assert math.isfinite(c)
    path = HERE / "P11_CP1_null.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("worlds", "c_wealth", "checks", "S_WEALTH", "excess_cagr", "years_beating",
                                          "response_panel_sha256")}, indent=1, default=float))
    print("null result sha256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
