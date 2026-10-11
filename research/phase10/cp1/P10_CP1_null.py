"""P10-CP1 (owner D204): the H025 matched null, offline. Reads the two complete null runs (S027 null mode, worlds
1..5,000: E027-04 and the identical rerun E027-05), checks the uploads, the pinned ledger digests, the response-panel
digest and bit-identical worlds, and computes c_EVENT = max(50th largest null t of 5,000, 2.326) (spec section 11).
Writes research/phase10/cp1/P10_CP1_null.json (summary + digests to pin) and P10_CP1_null_worlds.json.gz.
No real H025 statistic exists in these runs.

    PYTHONPATH=src python research/phase10/cp1/P10_CP1_null.py
"""
import gzip
import hashlib
import json
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


def read(exp):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    blob = joined(ls, "QRH")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["null"]["blob_sha256"]
    return st, json.loads(E.unpack(blob))


def main(exps=P.NULL_RUNS):
    runs = {}
    for exp in exps:
        ok, up = uploaded(exp)
        st, out = read(exp)
        runs[exp] = dict(ok=ok, up=up, st=st, out=out)
    a, b = (runs[e] for e in exps)
    W = a["out"]["worlds"]
    seeds = [w[0] for w in W]
    t = np.array([w[1] for w in W], float)
    checks = dict(
        uploads_ok=all(r["ok"] for r in runs.values()),
        seeds_1_to_5000=seeds == list(range(1, H.R_NULL + 1)),
        all_finite=bool(np.isfinite(t).all()),
        rerun_identical=a["out"] == b["out"],
        panel_identical=a["st"]["response_panel_sha256"] == b["st"]["response_panel_sha256"],
        in_host_ledger_pinned=all(r["st"]["in_host_ledger_sha256"] == P.IN_HOST_LEDGER_SHA256 for r in runs.values()),
        pit_audit_zero=all(all(v == 0 for v in r["st"]["pit_audit"].values()) for r in runs.values()))
    c, raw = H.critical_value(t)
    means = np.array([w[2] for w in W])
    med = np.array([w[3] for w in W])
    win = np.array([w[4] for w in W])
    q = lambda x, p: float(np.quantile(x, p))  # noqa: E731
    text = json.dumps(dict(fields=a["out"]["fields"], worlds=W), separators=(",", ":"))
    with gzip.GzipFile(HERE / "P10_CP1_null_worlds.json.gz", "wb", mtime=0) as f:
        f.write(text.encode())
    res = dict(
        experiments=list(exps), checks=checks, passed=all(checks.values()),
        upload={e: dict(ok=runs[e]["ok"], **runs[e]["up"]) for e in exps},
        null=a["st"]["null"], q_panel=a["st"]["q_panel"],
        response_panel_sha256=a["st"]["response_panel_sha256"], in_host_ledger_sha256=P.IN_HOST_LEDGER_SHA256,
        event_ledger_sha256=P.EVENT_LEDGER_SHA256,
        c_event=c, c_event_raw=raw, floor=H.C_FLOOR, order_statistic="50th largest of 5,000 (qr_xs.critical_value)",
        t_distribution=dict(mean=float(t.mean()), sd=float(t.std(ddof=1)), p50=q(t, .5), p90=q(t, .9), p95=q(t, .95),
                            p99=q(t, .99), max=float(t.max()), min=float(t.min()),
                            share_above_floor=float((t > H.C_FLOOR).mean())),
        random_event_control=dict(mean_of_means=float(means.mean()), p05_mean=q(means, .05), p95_mean=q(means, .95),
                                  mean_of_medians=float(med.mean()), mean_win_rate=float(win.mean()),
                                  share_worlds_mean_ge_2pct=float((means >= H.G2_MIN).mean())),
        worlds_sha256=hashlib.sha256(text.encode()).hexdigest(),
        wall_s={e: runs[e]["st"]["wall_s"] for e in exps})
    body = json.dumps(res, indent=1, sort_keys=True) + "\n"
    (HERE / "P10_CP1_null.json").write_text(body)
    print(json.dumps(dict(passed=res["passed"], checks=checks, c_event=c, c_event_raw=raw,
                          null_result_sha256=hashlib.sha256(body.encode()).hexdigest(),
                          response_panel_sha256=res["response_panel_sha256"]), indent=1))


if __name__ == "__main__":
    main()
