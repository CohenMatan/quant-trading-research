"""Architecture review (P2-CP11): metadata-only probe of SEC 8-K earnings-release filings as a free, point-in-time
source of earnings-announcement timestamps (no prices, no returns, no QuantConnect data).

For a fixed sample of large companies that existed in 2000 (40 survivors, chosen by name before looking at any data,
plus 10 large companies that failed or were acquired before 2010), count per calendar year:
  * 8-K filings carrying Item 2.02 "Results of Operations and Financial Condition" (in force from 2004-08-23),
  * 8-K filings carrying the predecessor Item 12 (2003-03-28 .. 2004-08-22),
  * 8-K filings with no item metadata, and whether an acceptance timestamp (time of day) is present.

    PYTHONPATH=src python research/phase2/architecture/sec_8k_earnings_probe.py -> sec_8k_earnings_probe.json
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "src")
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402

SURVIVORS = ["AAPL", "MSFT", "XOM", "JNJ", "PG", "KO", "PEP", "WMT", "IBM", "INTC", "CSCO", "ORCL", "HD", "MCD",
             "MMM", "CAT", "DE", "BA", "HON", "GE", "PFE", "MRK", "LLY", "ABT", "AMGN", "T", "VZ", "DIS", "NKE", "TGT",
             "LOW", "COST", "UNP", "CSX", "FDX", "EMR", "ITW", "DOV", "GIS", "CL"]
# CIK, expected name fragment (verified against the submissions record; a mismatch is reported, not guessed)
FAILED = {806085: "LEHMAN", 777001: "BEAR STEARNS", 1024401: "ENRON", 723527: "WORLDCOM", 933136: "WASHINGTON MUTUAL",
          65100: "MERRILL LYNCH", 25191: "COUNTRYWIDE", 36995: "WACHOVIA", 40730: "GENERAL MOTORS", 1006240: "LUCENT"}
YEARS = range(1998, 2022)


def per_company(sub):
    out = defaultdict(Counter)
    for f in filings_table(sub):
        if f.get("form") not in ("8-K", "8-K/A"):
            continue
        y = int(str(f["filingDate"])[:4])
        items = [i.strip() for i in str(f.get("items") or "").split(",") if i.strip()]
        out[y]["8k"] += 1
        if "2.02" in items:
            out[y]["item_2_02"] += 1
        if "12" in items:
            out[y]["item_12"] += 1
        if not items:
            out[y]["no_items"] += 1
        acc = str(f.get("acceptanceDateTime") or "")
        if len(acc) >= 19 and acc[11:19] != "00:00:00":
            out[y]["has_time"] += 1
    return out


def main():
    c = SECClient()
    tick = c.get_json("https://www.sec.gov/files/company_tickers.json", allow_missing=False)
    by_t = {v["ticker"]: int(v["cik_str"]) for v in tick.values()}
    sample, names = {}, {}
    for t in SURVIVORS:
        if t in by_t:
            sample[t] = by_t[t]
    for cik, frag in FAILED.items():
        sample[f"failed:{frag}"] = cik
    totals = {"survivors": defaultdict(Counter), "failed": defaultdict(Counter)}
    companies = {}
    for label, cik in sample.items():
        sub = c.submissions(cik)
        if sub is None:
            companies[label] = dict(cik=cik, status="no submissions record")
            continue
        names[label] = sub.get("name", "")
        grp = "failed" if label.startswith("failed:") else "survivors"
        if grp == "failed" and label.split(":", 1)[1] not in names[label].upper():
            companies[label] = dict(cik=cik, name=names[label], status="NAME MISMATCH: excluded")
            continue
        pc = per_company(sub)
        companies[label] = dict(cik=cik, name=names[label], first_8k=min(pc) if pc else None,
                                item_2_02_by_year={y: pc[y]["item_2_02"] for y in sorted(pc)})
        for y, cnt in pc.items():
            totals[grp][y].update(cnt)
            if cnt["item_2_02"] or cnt["item_12"]:
                totals[grp][y]["companies_with_earnings_8k"] += 1
    out = dict(sample_size={g: sum(1 for k in companies if (k.startswith("failed:")) == (g == "failed")
                                  and "item_2_02_by_year" in companies[k]) for g in totals},
               by_year={g: {y: dict(totals[g][y]) for y in YEARS if y in totals[g]} for g in totals},
               companies=companies,
               notes=["Item 2.02 exists from 2004-08-23; Item 12 from 2003-03-28; before 2003 earnings releases were "
                      "filed (if at all) under Item 5/7 and cannot be identified from metadata alone.",
                      "has_time = acceptanceDateTime carries a time of day (needed to tell before-open from "
                      "after-close releases)."])
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    for g in totals:
        print(g, out["sample_size"][g])
        for y in YEARS:
            v = out["by_year"][g].get(y)
            if v:
                print(" ", y, {k: v.get(k, 0) for k in ("8k", "item_12", "item_2_02", "companies_with_earnings_8k",
                                                         "no_items", "has_time")})
    print("fetched", c.fetched, "cache", c.cache_hits)


if __name__ == "__main__":
    main()
