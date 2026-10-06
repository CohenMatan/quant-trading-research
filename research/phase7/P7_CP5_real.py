"""P7-CP5 (D177; PREPARED, NOT RUN — see P7-CP5a): evaluate the ONE real H022 evaluation with the pinned c_IC -> research/phase7/P7_CP5_result.json.
Checks the provenance (pinned c_IC, threshold commit, null result hash, panel digest), re-applies the frozen gates
(qr_p7_pred.promotion) to the exported statistics, and adds the null percentile / p-value of t_IC and of the incremental
slope t-statistic from the committed null worlds. Gates and verdict are exactly the frozen ones; diagnostics are
non-gating. No portfolio statistic exists anywhere."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean")]
import qr_p7_export as E  # noqa: E402
import qr_p7_pred as R  # noqa: E402
import qr_xs as X  # noqa: E402
from qresearch import p7pred  # noqa: E402

sys.path.insert(0, str(HERE))
from P7_CP3R_extract import joined, lines  # noqa: E402


def main(exp):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7S"))
    blob = joined(ls, "QRR")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"], "result blob hash"
    out = json.loads(E.unpack(blob))
    prov = st["provenance"]
    assert prov["c_ic"] == p7pred.C_IC and prov["threshold_commit"] == p7pred.THRESHOLD_COMMIT
    assert prov["null_result_sha256"] == p7pred.NULL_RESULT_SHA256 == \
        hashlib.sha256((HERE / "P7_CP5_null.json").read_bytes()).hexdigest()
    assert prov["panel_sha256"] == st["panel_sha256"] == p7pred.PANEL_SHA256
    assert st["spec_sha256"] == p7pred.SPEC_SHA256
    s, c = out["summary"], p7pred.C_IC
    gates = R.promotion(s, c)
    assert gates == out["gates"], "gates differ from the host's"
    worlds = json.loads(gzip.open(HERE / "P7_CP5_null_worlds.json.gz").read())
    nt = np.array([w["t_ic"] for w in worlds])
    ni = np.array([w["t_inc"] for w in worlds])
    ser = out["series"]
    ic = np.array([x["ic"] for x in ser])
    yrs = np.array([int(x["day"][:4]) for x in ser])
    tot = float(ic.sum())
    blocks = {f"{a}-{b}": dict(sum=float(ic[(yrs >= a) & (yrs <= b)].sum()),
                               share=float(ic[(yrs >= a) & (yrs <= b)].sum() / tot) if tot else None,
                               months=int(((yrs >= a) & (yrs <= b)).sum()))
              for a, b in R.BLOCKS}
    hi = [x["hi"] for x in ser]
    fin = [h for h in hi if h is not None and np.isfinite(h)]
    result = dict(
        experiment=exp, qc_backtest_id=res.get("qc_backtest_id"), commit=res.get("commit"),
        lean_version=res.get("lean_version_id"), run_utc=res.get("run_utc"), orders=res.get("orders"),
        provenance=prov, summary=s, gates=gates, verdict="H022 QUALIFIED FOR PORTFOLIO-DESIGN RESEARCH"
        if gates["pass"] else "H022 NOT QUALIFIED",
        ic=dict(mean=s["ic_mean"], median=float(np.median(ic)), se_nw=s["ic_se"], t=s["t_ic"], c_ic=c,
                null_share_ge=float(np.mean(nt >= s["t_ic"])), p_value=float((1 + np.sum(nt >= s["t_ic"])) / (1 + nt.size)),
                null_percentile=float(np.mean(nt < s["t_ic"])), positive_months=int((ic > 0).sum()), months=int(ic.size),
                sd=float(ic.std(ddof=1))),
        economic=dict(hi_ann=s["hi_ann"], hi_monthly=float(np.mean(fin)) if fin else None, hi_months=s["hi_months"],
                      hi_n_mean=s["hi_n_mean"], months_without_80=int(sum(1 for x in ser if x["n_hi"] == 0))),
        monotonicity=dict(q_mean_ann=s["q_mean_ann"], q5_minus_q1_ann=s["q5_minus_q1_ann"], spearman=s["mono"]),
        stability=dict(halves=s["halves"], blocks=blocks, largest_share=s["block_max"], years=s["years"]),
        diagnostics=dict(
            sector=dict(ic_mean=s["ic_sector_mean"], t=s["t_ic_sector"], flag_sector_driven=out["flags"]["sector_driven"]),
            regime=s.get("regime_ic"),
            incremental=dict(slope=s["inc_mean"], t=s["t_inc"], null_percentile=float(np.mean(ni < s["t_inc"])),
                             null_share_ge=float(np.mean(ni >= s["t_inc"]))),
            h2=dict(ic_mean=out["h2"]["ic_mean"], t=out["h2"]["t_ic"], dates=out["h2"]["n_dates"], lag=2),
            h3=dict(ic_mean=out["h3"]["ic_mean"], t=out["h3"]["t_ic"], dates=out["h3"]["n_dates"], lag=3)),
        population=[[x["day"], x["n"], x["n_hi"]] for x in ser],
        series=ser, coverage_status=st["coverage"]["status"],
        digests={k: st[k] for k in ("panel_sha256", "score_side_sha256", "response_side_sha256", "score_tables_sha256")},
        runtime=dict(wall_s=st["wall_s"], max_rss_mb=st["max_rss_mb"], world_s=st["real"]["world_s"]))
    (HERE / "P7_CP5_result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("gates", "verdict", "ic", "economic", "monotonicity")}, indent=1))
    print(json.dumps(result["stability"], indent=1))
    print(json.dumps(result["diagnostics"], indent=1))


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
