"""OC-2 Stage 2 (owner D248): protocol-correct classification and post-hoc diagnostics of the committed synthetic
results. Written AFTER OC2_S2_results.json existed; it applies the frozen protocol text (section 6.1: "any failed
or incomplete scenario ... -> D"), which the driver implemented only partly (it checked the four adequacy worlds,
not failed scenarios). It changes no result, threshold or scenario. Synthetic data only.

    PYTHONPATH=src python research/longhorizon/oc2/stage2/OC2_S2_classify.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
RES = HERE / "OC2_S2_results.json"
OUT = HERE / "OC2_S2_classification.json"
PARTS = ROOT / "data/oc2_stage2_parts"
RANK_SD = 1 / math.sqrt(12)


def main():
    d = json.loads(RES.read_text())
    failed = sorted(n for n, s in d["scenarios"].items()
                    if any(isinstance(s[k], float) and math.isnan(s[k]) for k in ("mean_t", "sd_t", "T_eff_ar1")))
    inadequate = {n: v for n, v in d["adequacy"].items() if v}
    size_fail = d["failed_size"]
    if failed or inadequate:
        outcome = "D — INSUFFICIENT EVIDENCE"
    elif size_fail:
        outcome = "C — METHOD NOT VALIDATED"
    else:
        outcome = d["outcome"]
    diag = {}
    for n in list(d["size_gates"]) + ["N5b", "N2L", "N13", "PM1", "PM3", "PP2", "PP3"]:
        fp = PARTS / f"{n}.json"
        s = d["scenarios"][n]
        row = dict(mean_t=s["mean_t"], sd_t=s["sd_t"], rej_1=s["rej_0.01"], rej_5=s["rej_0.05"],
                   tq_annual_mean=s["tq_annual_mean"], ret_sd=s["realised"]["ret_sd"])
        if fp.exists():
            R = json.loads(fp.read_text())["rows"]
            sd_slope = float(np.nanmean([r["sd_slope"] for r in R]))
            ret_sd = float(np.nanmean([r["ret_sd"] for r in R]))
            row["implied_sd_ic"] = round(sd_slope * RANK_SD / ret_sd, 4)       # sd of the monthly IC equivalent
            row["nan_rows"] = int(sum(1 for r in R if not math.isfinite(r["t_nw3"])))
        diag[n] = row
    out = dict(kind="OC-2 Stage 2 protocol-correct classification + post-hoc diagnostics (synthetic only)",
               decision="D248", results_protocol_sha256=d["protocol_sha256"], driver_outcome=d["outcome"],
               failed_scenarios=failed, adequacy_misses=inadequate, size_failures=size_fail,
               outcome=outcome, diagnostics=diag,
               notes=["protocol 6.1 (frozen text): any failed or incomplete scenario -> D; the driver did not "
                      "implement this clause; the protocol governs",
                      "N13 failed: every replication has NaN statistics (overlapping 3-month responses reach stocks "
                      "that left the sample when the cross-section shrinks); diagnostic scenario",
                      "N7 parameterisation defect: systematic variance exceeds the 6.5% total, so the idiosyncratic "
                      "sd collapsed to the floor (implied sd_IC far below N4)",
                      "power worlds: implied sd_IC ~ the sampling floor (about 0.03) vs the 0.06-0.12 range assumed "
                      "in LH-CP4; synthetic power is therefore not credible"])
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(outcome=outcome, failed=failed, size_fail=size_fail), indent=1))
    for n, r in diag.items():
        print(n, r)


if __name__ == "__main__":
    main()
