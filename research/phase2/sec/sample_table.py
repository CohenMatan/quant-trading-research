"""The owner's SEC verification sample table (checkpoint item 2): one row per required case type, from E971-02.
Per row: company, period, SEC form, SEC filing date, SEC value (as first filed), QuantConnect value expressed as a
ratio to the SEC value (vendor values are not exported; licence), QuantConnect availability date (vendor file date),
PIT-layer exposure date, match/mismatch, status (confirmed / vendor-supported, not independently confirmed /
unresolved / unsafe). Output: research/phase2/sec/sample_table.json and .md"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "src"))
import e970_parse  # noqa: E402
import x971_analyse as A  # noqa: E402

OUT = Path(__file__).parent


def main():
    lines = e970_parse.lines("E971-02")
    ref = A.load_ref()
    V = [A.parse_v(l) for l in lines if l.startswith("V|")]
    for v in V:
        v["ratios"] = A.semantic_ratios(v, ref)
    X = {}
    for l in lines:
        if l.startswith("X|"):
            _, sid, pe, fd, day = l.split("|")
            X.setdefault((sid, pe, fd), day)
    res = json.loads((OUT / "x971_results.json").read_text())
    qd = {(q["sid"], q["pe"], q["fd"]): q for q in res["quarantine"]["detail"]}

    def sec_vals(v):
        recs = ref.get(v["cik"], {}).get("records", [])
        o = next((r for r in recs if r[0] == v["orig_accn"]), None)
        return (o[6] if o else {}), (ref.get(v["cik"], {}).get("name"))

    def row(case, v, field, status=None, note=""):
        sv, name = sec_vals(v)
        r = v["ratios"].get(field)
        expo = X.get((v["sid"], v["pe"], v["fd"]))
        m = A.cls(r)
        st = status or ("confirmed" if m == "match" and expo and v["orig_filed"] and expo > v["orig_filed"]
                        else "unresolved")
        return {"case": case, "company": f"{v['ticker']} ({name})", "period": v["pe"], "sec_form": v["orig_form"],
                "sec_filing_date": v["orig_filed"], "field": field, "sec_value_first_filed": sv.get(field),
                "qc_value_as_ratio_to_sec": None if r is None else round(r, 4), "qc_availability_date": v["fd"],
                "pit_exposure_date": expo or "never (quarantined)" if v["quarantined"] else expo,
                "match": m, "status": st, "note": note}

    def find(pred):
        return next((v for v in V if pred(v)), None)

    rows = []
    v = find(lambda v: v["ticker"] == "MSFT" and v["pe"] == "2016-03-31")
    rows += [row("normal 10-Q", v, "revenue_q"), row("normal 10-Q", v, "total_assets")]
    v = find(lambda v: v["ticker"] == "MSFT" and v["pe"] == "2016-06-30")
    rows += [row("normal 10-K", v, "revenue_ttm"), row("normal 10-K", v, "net_income_ttm")]
    am = [x for x in V if x["orig_accn"] and not x["quarantined"] and any(
        y["sid"] == x["sid"] and y["pe"] == x["pe"] and y["fd"] < x["fd"] for y in V)]
    if am:
        v = am[0]
        rows.append(row("amended filing (vendor amendment of the same period)", v, "total_assets",
                        note="vendor report re-filed for the same period; visible only from its own file date"))
    v = find(lambda v: v["ticker"] == "KHC" and v["pe"] == "2018-12-29")
    rows += [row("delayed filing (Kraft Heinz FY2018 10-K, filed 2019-06-07)", v, "revenue_ttm"),
             row("delayed filing (Kraft Heinz FY2018 10-K, filed 2019-06-07)", v, "total_assets")]
    rs = [x for x in V if not x["quarantined"] and any(t.startswith("later") for t, _ in x["versions"].values())]
    if rs:
        v = rs[0]
        f = next(f for f, (t, _) in v["versions"].items() if t.startswith("later"))
        rows.append(row("accounting restatement (vendor value = a LATER filing's value)", v, f, status="unsafe",
                        note="value equals a later filing's (restated/recast) figure, not the original; "
                             f"{len(rs)} of {sum(1 for x in V if not x['quarantined'])} sample reports have >=1 such field"))
    v = find(lambda v: v["ticker"] == "AAPL" and v["pe"] == "2014-06-28")
    rows.append(row("company with a split (AAPL 7:1, 2014-06-09)", v, "revenue_q",
                    note="statement totals unaffected by the split; SEC cover count 5,987,867,000 (post-split) on "
                         "the 2014-07-23 10-Q; reconstructed market cap / vendor = see market-cap method results"))
    v = find(lambda v: v["ticker"] == "MON" and v["pe"] == "2018-02-28")
    rows.append(row("acquisition/delisting (Monsanto, deal 2018-06-07)", v, "total_assets",
                    note="last report before the acquisition; eligibility ended with the last trading day (E969)"))
    v = find(lambda v: v["ticker"] == "DTV" and v["pe"] == "2015-03-31")
    rows.append(row("acquisition/delisting (DirecTV, deal 2015-07-24)", v, "revenue_q"))
    v = find(lambda v: v["estimated"] and v["orig_accn"] and v["pe"] < "2013" and A.cls(v["ratios"].get("total_assets")) == "match")
    rows.append(row("2010-2012 estimated filing date (vendor = period end + 45)", v, "total_assets",
                    note="exposure held to period end + 90; true SEC filing date earlier than the exposure date"))
    for verdict, st in (("valid", "confirmed (released from quarantine)"), ("restated", "unsafe (kept quarantined)"),
                        ("mixed-period", "vendor-supported but not independently confirmed (kept quarantined)")):
        q = next((q for q in res["quarantine"]["detail"] if q["verdict"].startswith(verdict) and q["ratios"]), None)
        if q:
            v = next(x for x in V if (x["sid"], x["pe"], x["fd"]) == (q["sid"], q["pe"], q["fd"]))
            f = "total_assets" if "total_assets" in v["ratios"] else next(iter(v["ratios"]))
            rows.append(row(f"quarantined record ({verdict})", v, f, status=st, note=q["verdict"]))
    (OUT / "sample_table.json").write_text(json.dumps(rows, indent=1) + "\n")
    hdr = ("| Case | Company | Period | SEC form | SEC filing date | Field | SEC value (first filed) | QC value / SEC "
           "| QC availability | PIT exposure | Match | Status |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    md = hdr + "".join(
        f"| {r['case']} | {r['company']} | {r['period']} | {r['sec_form']} | {r['sec_filing_date']} | {r['field']} | "
        f"{r['sec_value_first_filed']:,.0f} | {r['qc_value_as_ratio_to_sec']} | {r['qc_availability_date']} | "
        f"{r['pit_exposure_date']} | {r['match']} | {r['status']} |\n"
        if r["sec_value_first_filed"] is not None else
        f"| {r['case']} | {r['company']} | {r['period']} | {r['sec_form']} | {r['sec_filing_date']} | {r['field']} | n/a | "
        f"{r['qc_value_as_ratio_to_sec']} | {r['qc_availability_date']} | {r['pit_exposure_date']} | {r['match']} | {r['status']} |\n"
        for r in rows)
    (OUT / "sample_table.md").write_text(md)
    return rows


if __name__ == "__main__":
    for r in main():
        print(r)
