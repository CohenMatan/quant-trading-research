"""P14-CP3 (owner D229): the 5,000 H029 / H030 null worlds (E031-02, E031-03), the seeds 1-25 rerun (E031-04), the
adequacy rule (spec 9) and the thresholds c_UP_H029 / c_INCREMENTAL_H030 (spec 8) -> P14_CP3_null.json.
Committed before the null runs. The thresholds are then pinned in qresearch.p14h029 and merged BEFORE the real run.

    PYTHONPATH=src python research/phase14/cp3/P14_CP3_null.py
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

RUNS = ("E031-02", "E031-03")
RERUN = "E031-04"


def blob(exp):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRY"))
    b = joined(ls, "QRYN")
    assert hashlib.sha256(b.encode()).hexdigest() == st["null"]["blob_sha256"], f"{exp}: blob hash mismatch"
    return st, json.loads(E.unpack(b))


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
    s_up = [r[1] for r in rows]
    s_inc = [r[10] for r in rows]
    c_up, c_inc = Q.critical_value(s_up), Q.critical_value(s_inc)
    canon = json.dumps(rows, separators=(",", ":"))
    out = dict(worlds=len(rows), finite=finite, rerun_seeds_1_25_identical=rerun_equal, runs=stats,
               adequacy=adeq, c_up_h029=c_up, c_incremental_h030=c_inc,
               null_rows_sha256=hashlib.sha256(canon.encode()).hexdigest(),
               s_up_quantiles={q: float(np.percentile(s_up, q)) for q in (1, 5, 50, 95, 99)},
               s_inc_quantiles={q: float(np.percentile(s_inc, q)) for q in (1, 5, 50, 95, 99)},
               real_selection_structure=reals[0],
               verdict=("THRESHOLDS READY" if finite and rerun_equal and adeq["ok"] else
                        ("STOP — H029/H030 NULL INADEQUATE" if not adeq["ok"] else "STOP — NULL NOT REPRODUCIBLE")))
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    (HERE / "P14_CP3_null.json").write_text(text)
    (HERE / "P14_CP3_null_rows.json").write_text(json.dumps(dict(fields=list(Q.NULL_FIELDS), worlds=rows),
                                                            separators=(",", ":")) + "\n")
    print(out["verdict"], "c_up", c_up, "c_inc", c_inc, "result sha", hashlib.sha256(text.encode()).hexdigest())


if __name__ == "__main__":
    main()
