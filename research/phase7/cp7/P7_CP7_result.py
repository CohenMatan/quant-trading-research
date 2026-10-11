"""P7-CP7 (owner D197): extract the ONE real H022 evaluation on frozen Data v2 (E024-07) -> research/phase7/cp7/
P7_CP7_result.json. WRITTEN AND COMMITTED BEFORE THE RUN. Checks the provenance (pinned Data-v2 c_IC, threshold commit,
null result hash, panel digest), re-applies the frozen gates (qr_p7_pred.promotion) to the exported statistics, reports
the gate inputs in full precision, the calendar-block contributions, the null percentile / p-value of t_IC and of the
incremental slope t-statistic from the committed Data-v2 null worlds, and the pre-registered NON-GATING diagnostics
(sector-demeaned IC, regime IC, Fama-MacBeth incremental, 2- and 3-month horizons, IC and population by year). Gates and
verdict are exactly the frozen ones. No portfolio statistic exists anywhere."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
import qr_p7_export as E  # noqa: E402
import qr_p7_pred as R  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import p7pred, p7pred_v2  # noqa: E402

THRESHOLD_COMMIT = "cc2b0d8a26f97ba666e2d0455e9c2b64e5bef84d"
QUALIFIED = "QUALIFIED — H022 passes G1–G4 on Data v2"
NOT_QUALIFIED = "NOT QUALIFIED — H022 fails one or more frozen gates"


def main(exp="E024-07"):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    blob = joined(ls, "QRR")
    assert hashlib.sha256(blob.encode()).hexdigest() == st["real"]["blob_sha256"], "result blob hash"
    assert not any(x.startswith("QRN|") for x in ls), "a null-world output exists in the real run"
    out = json.loads(E.unpack(blob))
    prov = st["provenance"]
    c = p7pred_v2.C_IC_V2
    assert prov["c_ic"] == c == out["c_ic"] == 2.3798883324991866 and c != p7pred.C_IC
    assert prov["threshold_commit"] == THRESHOLD_COMMIT
    assert prov["null_result_sha256"] == p7pred_v2.NULL_RESULT_SHA256 == \
        hashlib.sha256((ROOT / p7pred_v2.NULL_RESULT).read_bytes()).hexdigest()
    assert prov["panel_sha256"] == st["panel_sha256"] == p7pred_v2.PANEL_SHA256
    assert st["spec_sha256"] == p7pred.SPEC_SHA256
    s = out["summary"]
    gates = R.promotion(s, c)
    assert gates == out["gates"], "gates differ from the host's"
    worlds = json.loads(gzip.open(ROOT / p7pred_v2.NULL_WORLDS).read())
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
    status = {}
    for key, n in st["coverage"]["status"].items():
        status[key.split("|")[2]] = status.get(key.split("|")[2], 0) + n
    pop = st["coverage"]["population"]
    ns = [n for _, n, _ in pop]
    by_year = {}
    for d, n, h in pop:
        y = by_year.setdefault(d[:4], dict(decisions=0, population=0, hi80=0))
        y["decisions"] += 1
        y["population"] += n
        y["hi80"] += h
    pv = res["provenance"]
    result = dict(
        experiment=exp, qc_backtest_id=pv.get("qc_backtest_id"), build_commit=pv.get("build_commit"),
        lean_version=pv.get("lean_version"), run_utc=pv.get("run_utc"), status=res["status"],
        orders=res["harness_summary"]["orders"], owner_approved=pv.get("owner_approved"),
        provenance=prov, panel_observed=st["panel_sha256"], pit_audit=st.get("pit_audit"),
        decisions=st["decisions"], calendar_check=st["calendar_check"],
        summary=s, gates=gates, c_ic=c, verdict=QUALIFIED if gates["pass"] else NOT_QUALIFIED,
        ic=dict(mean=s["ic_mean"], median=float(np.median(ic)), se_nw=s["ic_se"], t=s["t_ic"], c_ic=c,
                t_minus_c=s["t_ic"] - c, null_share_ge=float(np.mean(nt >= s["t_ic"])),
                p_value=float((1 + np.sum(nt >= s["t_ic"])) / (1 + nt.size)),
                null_percentile=float(np.mean(nt < s["t_ic"])), positive_months=int((ic > 0).sum()),
                months=int(ic.size), sd=float(ic.std(ddof=1)), min=float(ic.min()), max=float(ic.max())),
        economic=dict(hi_ann=s["hi_ann"], hi_monthly=float(np.mean(fin)) if fin else None, hi_months=s["hi_months"],
                      hi_n_mean=s["hi_n_mean"], hi_stock_months=int(sum(x["n_hi"] for x in ser)),
                      months_with_80=int(sum(1 for x in ser if x["n_hi"] > 0)),
                      months_without_80=int(sum(1 for x in ser if x["n_hi"] == 0))),
        monotonicity=dict(q_mean_ann=s["q_mean_ann"], q_mean_monthly=[q / R.ANN for q in s["q_mean_ann"]],
                          q5_minus_q1_ann=s["q5_minus_q1_ann"], spearman=s["mono"]),
        stability=dict(halves=s["halves"], blocks=blocks, largest_share=s["block_max"], total_ic_sum=tot),
        diagnostics=dict(
            sector=dict(ic_mean=s["ic_sector_mean"], t=s["t_ic_sector"], flag_sector_driven=out["flags"]["sector_driven"]),
            regime=s.get("regime_ic"),
            incremental=dict(slope=s["inc_mean"], t=s["t_inc"], null_percentile=float(np.mean(ni < s["t_inc"])),
                             null_share_ge=float(np.mean(ni >= s["t_inc"])),
                             flag_no_increment=out["flags"]["no_increment_beyond_momentum_size"]),
            h2={k: v for k, v in out["h2"].items() if k != "years"} | dict(lag=2, years=out["h2"].get("years")),
            h3={k: v for k, v in out["h3"].items() if k != "years"} | dict(lag=3, years=out["h3"].get("years")),
            ic_by_year=s["years"], population_by_year=by_year),
        population=dict(min=min(ns), median=sorted(ns)[len(ns) // 2], mean=sum(ns) / len(ns), max=max(ns),
                        responses=int(sum(ns)), per_decision=pop),
        response_status=status, series=ser,
        digests={k: st[k] for k in ("panel_sha256", "score_side_sha256", "response_side_sha256", "availability_sha256",
                                    "calendar_sha256")},
        data_v2_digests_equal_e998=None,
        runtime=dict(wall_s=st["wall_s"], max_rss_mb=st["max_rss_mb"], world_s=st["real"]["world_s"]))
    ref = json.loads(joined((ROOT / "experiments/E998-01/messages.txt").read_text().splitlines(), "QRV2"))["digests"]
    result["data_v2_digests_equal_e998"] = (st["data_v2_digests"]["review_scores"] == ref["review_scores"]
                                            and st["data_v2_digests"]["review_eligibility"] == ref["review_eligibility"])
    (HERE / "P7_CP7_result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("verdict", "gates", "ic", "economic", "monotonicity", "stability")},
                     indent=1))
    print(json.dumps(result["diagnostics"], indent=1))
    print("result sha256", hashlib.sha256((HERE / "P7_CP7_result.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
