"""P14-CP2 (owner D229): offline analysis of the Data v3 audit run E803-01 -> P14_CP2_audit.json.

Applies the gate pre-registered in research/phase14/data_v3/DATA_V3_spec.md (committed a43d706, before any build) to
the aggregate export of X803. Written and committed before E803-01 ran. DATA QUALITY ONLY: the export holds counts,
quantiles and digests; no return, price path or performance figure exists anywhere in it.

    PYTHONPATH=src python research/phase14/cp2/P14_CP2_analysis.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
import qr_p7_export as E  # noqa: E402
import qr_v3 as V  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import data_v3 as D3  # noqa: E402

EXP, REF_EXP = "E803-01", "E802-01"
PER = [p for p, _, _ in V.PERIODS]
FAM_COVERAGE_MIN, COVERAGE_MIN = 0.50, 0.70
SHARE_MAX, PER_PERIOD_MIN, SECTORS_MIN, SECTOR_N_MIN = 0.05, 300, 8, 100
F7_MIN_SPLIT, F7_MARGIN = 30, 0.05


def load(exp, tag, blob_tag):
    ls = lines(exp)
    st = json.loads(joined(ls, tag))
    if blob_tag is None:
        return st, None
    blob = joined(ls, blob_tag)
    assert hashlib.sha256(blob.encode()).hexdigest() == st["audit_blob"]["sha256"], "blob hash mismatch"
    text = E.unpack(blob)
    for bad in ("return", "sharpe", "cagr", "wealth", "alpha", "forward"):
        assert bad not in text.lower(), bad
    return st, json.loads(text)


def pooled(qs):
    """Pool per-period / per-sector summaries (share above 0.20 weighted by n)."""
    n = sum(q.get("n", 0) for q in qs)
    if not n:
        return dict(n=0, share_gt_0_20=None)
    return dict(n=n, share_gt_0_20=sum(q["n"] * q["share_gt_0_20"] for q in qs if q.get("n")) / n)


def coverage(agg):
    mo = agg["monthly"]
    u = np.asarray(mo["universe"], float)
    yrs = np.array([int(d[:4]) for d in mo["day"]])
    out = dict(reviews=len(u), universe_median=float(np.median(u)))
    for k in ("ge5", "ge4", "all6") + V.SIGNALS:
        s = np.asarray(mo[k], float) / u
        out[k] = dict(median=float(np.median(s)), median_2015_2021=float(np.median(s[yrs >= 2015])),
                      by_period={p: float(np.median(s[(yrs >= a) & (yrs <= b)])) for p, a, b in V.PERIODS},
                      min=float(s.min()))
    return out


def validation(agg):
    va = agg["validation"]
    out = {}
    for f in V.SEC_SIGNALS:
        per = {p: va["delta"].get(f"{f}|{p}", dict(n=0)) for p in PER}
        sec = {k.split("|", 1)[1]: v for k, v in va["delta_sector"].items() if k.startswith(f + "|")}
        pool = pooled(per.values())
        big = sorted(s for s, q in sec.items() if q.get("n", 0) >= SECTOR_N_MIN)
        suff = all(per[p].get("n", 0) >= PER_PERIOD_MIN for p in PER) and len(big) >= SECTORS_MIN
        avail = {k.split("|")[1]: 0 for k in va["availability"] if k.startswith(f + "|")}
        for k, v in va["availability"].items():
            if k.startswith(f + "|"):
                avail[k.split("|")[1]] += v
        ok = suff and pool["share_gt_0_20"] is not None and pool["share_gt_0_20"] <= SHARE_MAX
        out[f] = dict(by_period=per, pooled=pool, sectors_with_100=len(big), sufficient=suff,
                      availability=avail, by_sector=sec, passes=ok,
                      status="PASS" if ok else ("INCONCLUSIVE" if not suff else "FAIL"))
    comp = pooled(va["composite"].values())
    out["composite"] = dict(by_period=va["composite"], pooled=comp,
                            passes=comp["share_gt_0_20"] is not None and comp["share_gt_0_20"] <= SHARE_MAX,
                            counts=va["composite_counts"])
    raw = {}
    for k, v in va["raw"].items():
        fld, cls, per = k.split("|")
        raw.setdefault(fld, {}).setdefault(cls, 0)
        raw[fld][cls] += v
    out["raw_field_agreement"] = raw
    anc = {}
    for k, v in va["anchor"].items():
        a = k.split("|")[0]
        anc[a] = anc.get(a, 0) + v
    out["anchor"] = anc
    return out


def f7_test(agg):
    sp = agg["f7_split"]
    d_s = sp["split"]["disagree"] / sp["split"]["n"] if sp["split"]["n"] else None
    d_n = sp["non"]["disagree"] / sp["non"]["n"] if sp["non"]["n"] else None
    ok = sp["split"]["n"] >= F7_MIN_SPLIT and d_s is not None and d_n is not None and d_s <= d_n + F7_MARGIN
    return dict(raw=sp, d_split=d_s, d_non_split=d_n, passes=ok,
                big_split=sp["split"]["big"] / sp["split"]["n"] if sp["split"]["n"] else None,
                big_non=sp["non"]["big"] / sp["non"]["n"] if sp["non"]["n"] else None)


def guard_after_2021():
    files = {p.name: p.read_text() for p in (ROOT / "src/qresearch/lean").glob("qr_data_v3_*.py")}
    back = D3.decolumnar(D3.unpack_parts(files, "qr_data_v3"))
    end = D3.dn(D3.END)
    return sum(1 for c in back.values() for p, rows in c.items() for _fi, off, _v in rows if p + off > end)


def main():
    st, agg = load(EXP, "QRV", "QRVA")
    ref, _ = load(REF_EXP, "QRZ", None)
    cov = coverage(agg)
    val = validation(agg)
    f7 = f7_test(agg)
    v3 = st["v3"]
    pit = dict(st["pit_audit"])
    pit.update(view_future_records=v3["view_future_records"], vendor_anchor_ahead_of_sec=v3["vendor_anchor_ahead_of_sec"],
               f7_filing_not_public=st["f7_checks"]["filing_not_public"],
               overlay_newer_replacement=v3["overlay"]["newer_replacement"], guard_entries_after_2021=guard_after_2021())
    pit_ok = all(v == 0 for v in pit.values())
    eld = agg["eligibility"]
    refd = ref["data_v21_digests"]["review_eligibility"]
    universe_equal = sum(1 for k in refd if eld.get(k) == refd[k])
    fam = {}
    for f in V.SIGNALS:
        c_ok = cov[f]["median"] >= FAM_COVERAGE_MIN
        v_ok = f7["passes"] if f == "F7" else val[f]["passes"]
        fam[f] = dict(coverage_median=cov[f]["median"], coverage_ok=c_ok, validation_ok=v_ok,
                      usable=bool(c_ok and v_ok and pit_ok))
    usable = [f for f in V.SIGNALS if fam[f]["usable"]]
    cov_ok = cov["ge5"]["median"] >= COVERAGE_MIN
    if len(usable) == 6 and val["composite"]["passes"] and cov_ok and pit_ok:
        outcome = "DATA V3 PASS"
    elif len(usable) == 5 and val["composite"]["passes"] and cov_ok and pit_ok:
        outcome = "STOP FOR OWNER REVIEW"
    else:
        outcome = "DATA V3 FAIL"
    prov = {}
    for k, v in agg["provenance"].items():
        f, c, y = k.split("|")
        prov.setdefault(f, {}).setdefault(c, 0)
        prov[f][c] += v
    blocked = {}
    for k, v in agg["blocked"].items():
        f, y = k.split("|")
        blocked.setdefault(f, {})[y] = v
    diff = {}
    for k, v in agg["v21_diff"].items():
        f, kind, per = k.split("|")
        diff.setdefault(f, {}).setdefault(kind, 0)
        diff[f][kind] += v
    out = dict(experiment=EXP, outcome=outcome, families=fam, usable=usable, coverage=cov, coverage_ok=cov_ok,
               validation=val, f7_split=f7, pit=pit, pit_ok=pit_ok,
               universe=dict(reviews_equal_to_E802_01=universe_equal, reviews=len(refd)),
               guard=dict(fed=v3["fed"], fed_no_match=v3["fed_no_match"], with_timeline=v3["fed_with_timeline"],
                          blocked=v3["blocked"], overlay=v3["overlay"], provenance=prov, blocked_by_field_year=blocked,
                          sample_day_mismatch=v3["sample_day_mismatch"]),
               v21_differences=diff, f7_reasons=agg["f7_reasons"], digests=agg["digests"],
               run=dict(max_rss_mb=st.get("max_rss_mb"), wall_s=st.get("wall_s"), live_s=st.get("live_s"),
                        guard_parts=st.get("guard_parts"), val_parts=st.get("val_parts"),
                        guard_values=st.get("guard_values")))
    (HERE / "P14_CP2_audit.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("outcome", "usable", "coverage_ok", "pit_ok", "universe")}, indent=1))


if __name__ == "__main__":
    main()
