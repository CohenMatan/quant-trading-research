"""P10-CP1 (owner D204): the ONE real H025 development evaluation (S027 real mode, E027-06), offline. Pre-committed
BEFORE the run. Checks the upload and the pinned provenance, recomputes the primary statistic and G1-G5 from the
exported event table (must equal the host's), then the pre-registered NON-GATING diagnostics (spec section 13) and the
null percentile. Writes research/phase10/cp1/P10_CP1_result.json.

    PYTHONPATH=src python research/phase10/cp1/P10_CP1_result.py
"""
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
import qr_h025 as H  # noqa: E402
import qr_p7_export as E  # noqa: E402
from P10_CP1_audit import uploaded  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import p10h025 as P  # noqa: E402


def stats(rows, key="y"):
    y = np.array([r[key] for r in rows if r[key] is not None and math.isfinite(r[key])], float)
    ms = [r["month"] for r in rows if r[key] is not None and math.isfinite(r[key])]
    if y.size == 0:
        return dict(n=0)
    u, idx = H.month_index(ms)
    m, se, t = H.nw_t(H.monthly_series(y, idx, len(u)))
    return dict(n=int(y.size), mean=float(y.mean()), median=float(np.median(y)), win_rate=float((y > 0).mean()),
                months=len(u), t=t)


def group(rows, fn):
    out = {}
    for r in rows:
        out.setdefault(fn(r), []).append(r)
    return {k: stats(v) for k, v in sorted(out.items())}


def main(exp=P.REAL):
    ok, up = uploaded(exp)
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    blob = joined(ls, "QRH")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"]
    out = json.loads(E.unpack(blob))
    f = out["fields"]
    ev = [dict(zip(f, r)) for r in out["events"]]
    ctrl = [dict(zip(f, r)) for r in out["controls"]]
    prov = st["provenance"]
    pins = dict(c_event=prov["c_event"] == P.C_EVENT, null=prov["null_result_sha256"] == P.NULL_RESULT_SHA256,
                commit=prov["threshold_commit"] == P.THRESHOLD_COMMIT,
                panel=st["response_panel_sha256"] == P.RESPONSE_PANEL_SHA256,
                ledger=prov["event_ledger_sha256"] == P.EVENT_LEDGER_SHA256,
                in_host=st["in_host_ledger_sha256"] == P.IN_HOST_LEDGER_SHA256)
    y = np.array([e["y"] for e in ev], float)
    s = H.summary(y, [e["month"] for e in ev], [e["year"] for e in ev])
    g = H.gates(s, P.C_EVENT)
    same = json.loads(json.dumps(s)) == out["summary"] and g == out["gates"]
    with gzip.open(HERE / "P10_CP1_null_worlds.json.gz") as fh:
        W = json.loads(fh.read())["worlds"]
    nt = np.array([w[1] for w in W])
    diag = dict(
        insiders=group(ev, lambda r: "2" if r["n_insiders"] == 2 else "3+"),
        cluster_value=group(ev, lambda r: "100k-250k" if r["cluster_value"] < 250e3 else
                            ("250k-1m" if r["cluster_value"] <= 1e6 else ">1m")),
        ceo_cfo=group(ev, lambda r: "ceo_cfo" if r["ceo_cfo"] else "no_ceo_cfo"),
        director_only=group(ev, lambda r: "director_only" if r["director_only"] else "with_officer"),
        qualifying_filings=group(ev, lambda r: str(r["n_qualifying_filings"]) if r["n_qualifying_filings"] < 4 else "4+"),
        filing_delay=group(ev, lambda r: "<=2d" if r["median_delay_days"] <= 2 else
                           ("3-5d" if r["median_delay_days"] <= 5 else ">5d")),
        horizons={f"h{h}": stats(ev, f"h{h}") for h in H.DIAG_HORIZONS},
        raw_tsr=stats(ev, "tsr"), sector_relative=stats(ev, "sector_rel"),
        null_level=group(ev, lambda r: r["level"]),
        single_insider_control=dict(primary=stats(ctrl), raw_tsr=stats(ctrl, "tsr"),
                                    by_year=group(ctrl, lambda r: str(r["year"]))),
        random_event_control=dict(mean_of_world_means=float(np.mean([w[2] for w in W])),
                                  mean_of_world_medians=float(np.mean([w[3] for w in W])),
                                  mean_world_win_rate=float(np.mean([w[4] for w in W]))),
        null_percentile=dict(share_null_t_ge_real=float((nt >= s["t"]).mean()),
                             p_value=float((1 + (nt >= s["t"]).sum()) / (1 + nt.size))))
    verdict = ("DEVELOPMENT CANDIDATE — H025 PASSED, VALIDATION NOT YET RUN" if g["all"] else
               "H025 REJECTED — NO ROBUST INSIDER-CLUSTER EDGE")
    res = dict(experiment=exp, upload=dict(ok=ok, **up), pins=pins, host_equals_offline=same, c_event=P.C_EVENT,
               summary=s, gates=g, verdict=verdict, not_evaluable=out["not_evaluable"], diagnostics=diag,
               pit_audit=st["pit_audit"], wall_s=st["wall_s"])
    (HERE / "P10_CP1_result.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(pins=pins, upload_ok=ok, host_equals_offline=same, t=s["t"], mean=s["mean"],
                          median=s["median"], win=s["win_rate"], n=s["n"], gates=g, verdict=verdict), indent=1))


if __name__ == "__main__":
    main()
