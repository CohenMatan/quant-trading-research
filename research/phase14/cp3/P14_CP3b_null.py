"""P14-CP3b (owner D233, Amendment 1): the 5,000 SECTOR-STRATIFIED H029 / H030 null worlds (E031-07, E031-08), the seeds
1-25 rerun (E031-09), the UNCHANGED adequacy rule (spec 9), the descriptive original-vs-sector null comparison
(amendment A6) and -- only if adequate -- the thresholds c_UP_H029 / c_INCREMENTAL_H030 -> P14_CP3b_null.json (+ rows).
Committed before the null runs. The thresholds are then pinned in qresearch.p14h029 and merged BEFORE the real run.
The original-null record (P14_CP3_null.json / _rows.json) is read only, never rewritten.

    PYTHONPATH=src python research/phase14/cp3/P14_CP3b_null.py
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
import qr_h029 as Q  # noqa: E402
import qr_p7_export as E  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import p14h029 as P  # noqa: E402

RUNS = P.NULL_RUNS
RERUN = P.RERUN
COMPARE = ("hhi29", "turn29", "hhi30", "turn30", "beta29", "up29", "dn29", "vol29", "beta30", "up30", "dn30", "vol30")
INADEQUATE = "H029/H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE"


def blob(exp):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRY"))
    b = joined(ls, "QRYN")
    assert hashlib.sha256(b.encode()).hexdigest() == st["null"]["blob_sha256"], f"{exp}: blob hash mismatch"
    return st, json.loads(E.unpack(b))


def dist(rows, field, real=None):
    x = np.asarray([r[Q.NULL_FIELDS.index(field)] for r in rows], float)
    d = {q: float(np.percentile(x, q)) for q in (0.5, 5, 50, 95, 99.5)}
    d.update(mean=float(x.mean()), sd=float(x.std(ddof=1)))
    if real is not None:
        d["real_percentile"] = float(100.0 * np.mean(x < real) + 50.0 * np.mean(x == real))
    return d


def main():
    rows, reals, stats = [], [], {}
    for e in RUNS:
        st, b = blob(e)
        assert b["fields"] == list(Q.NULL_FIELDS)
        rows += b["worlds"]
        reals.append(b["real_selection_structure"])
        stats[e] = dict(worlds=st["null"]["worlds"], world_s=st["null"]["world_s"], max_rss_mb=st.get("max_rss_mb"),
                        equivalence=st["equivalence"], h028_ok=st["h028_reproduction"]["ok"])
    seeds = [r[0] for r in rows]
    assert seeds == list(range(1, Q.R_NULL + 1)), "seeds 1..5000 not complete"
    finite = all(math.isfinite(x) for r in rows for x in r[1:])
    assert reals[0] == reals[1], "the real selection structure differs between the null runs"
    _st, rb = blob(RERUN)
    rerun_equal = rb["worlds"] == rows[:25]
    adeq = Q.adequacy(rows, reals[0])
    # descriptive original (single-stratum, inadequate) vs sector-stratified null; NOT a choice between nulls
    orig = json.loads((HERE / "P14_CP3_null_rows.json").read_text())
    assert hashlib.sha256((ROOT / P.ORIGINAL_NULL_RESULT).read_bytes()).hexdigest() == P.ORIGINAL_NULL_RESULT_SHA256
    assert orig["fields"] == list(Q.NULL_FIELDS) and len(orig["worlds"]) == Q.R_NULL
    rs = reals[0]
    realv = dict(hhi29=rs["hhi29"], turn29=rs["turn29"], hhi30=rs["hhi30"], turn30=rs["turn30"])
    comparison = {f: dict(original_single_stratum=dist(orig["worlds"], f, realv.get(f)),
                          sector_stratified=dist(rows, f, realv.get(f))) for f in COMPARE}
    ok = finite and rerun_equal and adeq["ok"]
    out = dict(amendment=P.AMENDMENT1, worlds=len(rows), finite=finite, rerun_seeds_1_25_identical=rerun_equal,
               runs=stats, adequacy=adeq, real_selection_structure=rs, original_vs_sector_null=comparison,
               verdict=("THRESHOLDS READY" if ok else
                        "STOP — SECTOR-STRATIFIED NULL NOT REPRODUCIBLE" if not rerun_equal else INADEQUATE))
    s_up = [r[1] for r in rows]
    s_inc = [r[10] for r in rows]
    if ok:                                      # thresholds exist ONLY for an adequate sector-stratified null
        c_up, c_inc = Q.critical_value(s_up), Q.critical_value(s_inc)
        assert (c_up, c_inc) != P.INVALID_THRESHOLDS
        out.update(c_up_h029=c_up, c_incremental_h030=c_inc,
                   s_up_quantiles={q: float(np.percentile(s_up, q)) for q in (1, 5, 50, 95, 99)},
                   s_inc_quantiles={q: float(np.percentile(s_inc, q)) for q in (1, 5, 50, 95, 99)})
    canon = json.dumps(rows, separators=(",", ":"))
    out["null_rows_sha256"] = hashlib.sha256(canon.encode()).hexdigest()
    out["invalid_original_thresholds_not_used"] = list(P.INVALID_THRESHOLDS)
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    (HERE / "P14_CP3b_null.json").write_text(text)
    (HERE / "P14_CP3b_null_rows.json").write_text(json.dumps(dict(fields=list(Q.NULL_FIELDS), worlds=rows),
                                                             separators=(",", ":")) + "\n")
    print(out["verdict"], "c_up", out.get("c_up_h029"), "c_inc", out.get("c_incremental_h030"),
          "result sha", hashlib.sha256(text.encode()).hexdigest())


if __name__ == "__main__":
    main()
