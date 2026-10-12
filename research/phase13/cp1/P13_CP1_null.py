"""P13-CP1 (owner D217): aggregate the H028 lambda-100 LOWVOL-conditional null worlds (S030 null mode) ->
P13_CP1_null.json.

Written and committed BEFORE any E030-02 / E030-03 / E030-04 output was read.

E030-02 (seeds 1-2,500) + E030-03 (2,501-5,000) = the 5,000 full-pipeline worlds (LOWVOL stays with its stock; the ten
other features move together from a persistent identity-tether donor; seven annual Ridge fits at lambda = 100, Top-15
portfolio, costs and the SPY comparison rerun in every world; no lambda selection). E030-04 reruns seeds 1-25
independently: coefficients, yearly returns, terminal wealth and S_WEALTH (every row value and every coefficient) must
reproduce exactly, otherwise STOP. Every run must carry the pinned H026 feature and response panels, and every world's
seven lambdas must be 100.

c_WEALTH_H028 = the one-sided empirical 99th percentile = the 50th largest S_WEALTH of 5,000 (qr_h026.critical_value).

Risk-adequacy audit step 1 (spec section 5, pre-registered): for EACH of volatility, MaxDD, beta and down-capture at
least 1% of the worlds must be at least as defensive as the reference (the real H027 values, p13h028.H027_REAL_RISK;
step 2 repeats it with the realised H028 values in the real-result assessment). Otherwise: "H028 BLOCKED — CONDITIONAL
NULL INADEQUATE" (no c is pinned, no real run).

    PYTHONPATH=src python research/phase13/cp1/P13_CP1_null.py
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
import qr_h027 as G  # noqa: E402
import qr_h028 as F  # noqa: E402
import qr_p7_export as E  # noqa: E402
from qresearch import p13h028 as P  # noqa: E402

QUANTILES = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)


def run(exp):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRG"))
    blob = joined(ls, "QRHN")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["null"]["blob_sha256"], f"{exp}: null blob hash"
    nb = json.loads(E.unpack(blob))
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    return st, nb, prov


def dist(x):
    x = np.asarray(x, float)
    return dict(mean=float(x.mean()), sd=float(x.std(ddof=1)), min=float(x.min()), max=float(x.max()),
                **{f"q{int(q * 100):02d}": float(np.quantile(x, q)) for q in QUANTILES})


def main():
    runs = {e: run(e) for e in P.NULL_RUNS + (P.RERUN,)}
    fields = runs[P.NULL_RUNS[0]][1]["fields"]
    assert fields == list(F.FIELDS)
    worlds, coef = {}, {}
    for e in P.NULL_RUNS:
        for w in runs[e][1]["worlds"]:
            assert w[0] not in worlds
            worlds[w[0]] = w
        coef.update(runs[e][1]["coef"])
    seeds = sorted(worlds)
    rr = {w[0]: w for w in runs[P.RERUN][1]["worlds"]}
    rc = runs[P.RERUN][1]["coef"]
    S = np.array([worlds[s][1] for s in seeds], float)
    c = H.critical_value(S.tolist())
    col = {f: i for i, f in enumerate(fields)}
    arr = lambda f: np.array([worlds[s][col[f]] for s in seeds], float)  # noqa: E731
    lo, hi = P.RERUN_SEEDS
    det = list(range(lo, hi + 1))
    checks = dict(
        seeds_1_to_5000=seeds == list(range(1, G.R_NULL + 1)),
        all_finite=bool(np.all(np.isfinite(S))) and all(r[0]["null"]["nonfinite"] == 0 for r in runs.values()),
        feature_panel_pinned=all(r[0]["feature_panel_sha256"] == P.H026_FEATURE_PANEL_SHA256 for r in runs.values()),
        response_panel_pinned=all(r[0]["response_panel_sha256"] == P.H026_RESPONSE_PANEL_SHA256 for r in runs.values()),
        equivalence_flags=all(r[0]["equivalence"] == dict(feature_panel=True, response_panel=True)
                              for r in runs.values()),
        rerun_1_25_rows_identical=sorted(rr) == det and all(rr[s] == worlds[s] for s in det),
        rerun_1_25_coefficients_identical=sorted(map(int, rc)) == det and all(rc[str(s)] == coef[str(s)] for s in det),
        same_lean_build=len({r[2]["lean_version"] for r in runs.values()}) == 1,
        pit_audit_zero=all(all(v == 0 for v in r[0]["pit_audit"].values()) for r in runs.values()),
        lambda_100_every_world=all(worlds[s][col[f"lam_{y}"]] == F.LAMBDA for s in seeds for y in H.OUTER_YEARS),
        hypothesis_h028=all(r[0].get("hypothesis") == "H028" for r in runs.values()))
    rows = [worlds[s] for s in seeds]
    adq = G.adequacy(rows, P.H027_REAL_RISK)
    lam = {y: dict(zip(*np.unique(arr(f"lam_{y}"), return_counts=True))) for y in H.OUTER_YEARS}
    h027 = json.loads((ROOT / "research/phase12/cp1/P12_CP1_null.json").read_text())
    reproduction_ok = checks["rerun_1_25_rows_identical"] and checks["rerun_1_25_coefficients_identical"]
    status = ("STOP — RERUN DOES NOT REPRODUCE" if not reproduction_ok else
              "STOP — NULL CHECKS FAILED" if not all(checks.values()) else
              "H028 BLOCKED — CONDITIONAL NULL INADEQUATE" if not adq["adequate"] else
              "ADEQUATE — c_WEALTH_H028 MAY BE PINNED")
    out = dict(
        worlds=len(seeds), fields=fields, c_wealth_h028=c, rank=50, alpha=G.ALPHA, checks=checks,
        all_checks=all(checks.values()), adequacy=adq, status=status,
        response_panel_sha256=P.H026_RESPONSE_PANEL_SHA256, feature_panel_sha256=P.H026_FEATURE_PANEL_SHA256,
        S_WEALTH=dict(dist(S), share_positive=float(np.mean(S > 0))),
        wealth=dist(arr("wealth")), excess_cagr=dist(arr("excess_cagr")),
        risk_distributions={k: dist(arr(k)) for k in ("vol", "maxdd", "beta", "up_capture", "down_capture")},
        real_reference_risk=P.H027_REAL_RISK, lambda_rule="lambda = 100 for every outer-year fit",
        years_beating=dict(zip(*[x.tolist() for x in np.unique(arr("years_beating"), return_counts=True)])),
        yearly_returns={str(y): dist(arr(f"ret_{y}")) for y in H.OUTER_YEARS},
        lambda_choice_by_year={str(y): {str(k): int(v) for k, v in d.items()} for y, d in lam.items()},
        h027_conditional_null_reference=dict(c_wealth_conditional=h027["c_wealth_conditional"],
                                             S_WEALTH=h027["S_WEALTH"], risk_distributions=h027["risk_distributions"]),
        data_v21_manifest_sha256=P.DATA_V21_MANIFEST_SHA256, spec_sha256=P.SPEC_SHA256, code_sha256=P.CODE_SHA256,
        runs={e: dict(git_commit=r[2]["git_commit"], lean_version=r[2]["lean_version"],
                      qc_backtest_id=r[2]["qc_backtest_id"], seeds=r[0]["null"]["seeds"], worlds=r[0]["null"]["worlds"],
                      world_s=r[0]["null"]["world_s"], blob_sha256=r[0]["null"]["blob_sha256"],
                      max_rss_mb=r[0].get("max_rss_mb"),
                      peak_vmhwm_mb=max((m[2].get("VmHWM", 0) for m in r[0].get("memory", [])), default=None),
                      wall_s=r[0].get("wall_s")) for e, r in runs.items()},
        world_values_sha256=hashlib.sha256(json.dumps(rows).encode()).hexdigest())
    assert math.isfinite(c)
    path = HERE / "P13_CP1_null.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("worlds", "c_wealth_h028", "checks", "status", "adequacy", "S_WEALTH",
                                          "years_beating")}, indent=1, default=float))
    print("null result sha256", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
