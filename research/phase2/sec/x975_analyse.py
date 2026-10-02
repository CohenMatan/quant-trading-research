"""True TTM validation results (E975-01, D113, owner item 8). Ratios and dates only.

Field approval rule (fixed before any strategy work; evaluated on the population the fields would serve, i.e.
companies NOT excluded by the financial/REIT policy — SEC-assigned SIC outside 6000-6999 at that time): a field enters
the future H016 field set only if at least 90% of its TTM values are within 0.5% of the authoritative SEC TTM for the
same four quarters, at least 95% within 2%, and no TTM value was exposed before a public SEC source (the company's
own 10-Q/10-K or an earlier earnings-release 8-K). Full-sample statistics are reported alongside.
Output: research/phase2/sec/x975_results.json and x975_sample_table.md"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import e970_parse  # noqa: E402
import rss_index  # noqa: E402

OUT = Path(__file__).parent
NAMED = {"789019": "MSFT", "320193": "AAPL", "1637459": "KHC", "1110783": "MON", "1465112": "DTV",
         "40545": "GE", "1357615": "KBR", "19617": "JPM"}


def cls(r):
    d = abs(r - 1)
    return "match" if d <= 0.005 else "close" if d <= 0.02 else "differs" if d <= 0.10 else "far"


def main(exp="E975-01"):
    L = e970_parse.lines(exp)
    cats = json.loads((OUT / "x975_inputs.json").read_text())
    blocks = json.loads((OUT / "restatement_blocks.json").read_text())
    T = [l.split("|") for l in L if l.startswith("T|")]
    N = [l.split("|") for l in L if l.startswith("N|")]
    U = [l for l in L if l.startswith("U|")]
    client = SECClient()
    sic = defaultdict(list)
    for r in rss_index.load():
        if r["sic"] and r["form"] in ("10-K", "10-Q"):
            sic[r["cik"]].append((r["filed"], r["sic"]))
    for v in sic.values():
        v.sort()

    def financial(cik, day):
        hist = [x for d, x in sic.get(int(cik), ()) if d < day]
        return bool(hist) and 6000 <= hist[-1] <= 6999

    by, fy, timing = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    by_all = defaultdict(Counter)
    early = []
    for p in T:
        b = p[3]
        by_all[b][cls(float(p[6]))] += 1
        if financial(p[1], p[4]):
            continue
        by[b][cls(float(p[6]))] += 1
        if p[8] != "na":
            fy[b][cls(float(p[8]))] += 1
        dd = (date.fromisoformat(p[4]) - date.fromisoformat(p[7])).days
        timing[b]["before SEC periodic filing" if dd < 0 else "same day as SEC" if dd == 0 else "later than SEC"] += 1
        if dd < 0:
            early.append(p)
    # every early value: is there a public earnings-release 8-K (item 2.02) before it?
    unsafe = 0
    for p in early:
        sub = client.submissions(int(p[1]))
        fr = filings_table(sub) if sub else []
        d, pe = date.fromisoformat(p[4]), date.fromisoformat(p[5])
        er = any(r["form"].startswith("8-K") and "2.02" in str(r.get("items") or "")
                 and pe < date.fromisoformat(r["filingDate"]) < d for r in fr)
        own = any(r["form"] in ("10-Q", "10-K") and r.get("reportDate") and
                  abs((date.fromisoformat(r["reportDate"]) - pe).days) <= 6 and date.fromisoformat(r["filingDate"]) < d
                  for r in fr)
        if not (er or own):
            unsafe += 1
    fields = {}
    for b, c in by.items():
        n = sum(c.values())
        m, w2 = c["match"] / n, (c["match"] + c["close"]) / n
        ca = by_all[b]
        na = sum(ca.values())
        fields[b] = {"compared": n, "within_0.5pct": round(m, 4), "within_2pct": round(w2, 4),
                     "all_companies_incl_financial": {"compared": na, "within_0.5pct": round(ca["match"] / na, 4),
                                                      "within_2pct": round((ca["match"] + ca["close"]) / na, 4)},
                     "fy_window_vs_10K_total": dict(fy[b]), "timing": dict(timing[b]),
                     "approved_for_H016_field_set": bool(m >= 0.90 and w2 >= 0.95)}
    reasons = defaultdict(Counter)
    for p in N:
        reasons[p[3]][f"{p[6]} | SEC TTM {'exists' if p[7] == '1' else 'absent'}"] += 1
    # category results
    def cat_of(p):
        out = []
        c = cats.get(p[1], {})
        if c.get("non_calendar"):
            out.append("non-calendar fiscal year")
        else:
            out.append("calendar-year filer")
        if c.get("changed_fiscal_year"):
            out.append("changed fiscal year")
        if c.get("amended"):
            out.append("company with amended filings")
        if p[2] in blocks:
            out.append("company with restatement-blocked reports")
        if p[5] <= "2012-12-31":
            out.append("early 2010-2012 window")
        if p[1] in ("320193", "1045810", "1318605"):
            out.append("stock split company")
        if p[1] in ("1110783", "1465112"):
            out.append("acquisition/delisting company")
        return out
    cat_stats = defaultdict(Counter)
    for p in T:
        if p[3] in ("revenue", "net_income", "operating_cash_flow", "gross_profit"):
            for k in cat_of(p):
                cat_stats[k][cls(float(p[6]))] += 1
    miss = Counter(p[3] for p in N if p[6] == "quarters not consecutive")
    cat_out = {k: {"n": sum(v.values()), "within_0.5pct": round(v["match"] / sum(v.values()), 4)} for k, v in cat_stats.items()}
    cat_out["missing-quarter cases (no TTM: quarters not consecutive)"] = dict(miss)
    # example rows for the owner's table
    ex = []
    want = [("calendar-year filer", lambda p: p[1] == "1637459"), ("non-calendar fiscal year (Microsoft, June FY)", lambda p: p[1] == "789019"),
            ("company with amended filings", lambda p: cats.get(p[1], {}).get("amended")),
            ("restatement-blocked company", lambda p: p[2] in blocks),
            ("stock split (Apple 2014/2020)", lambda p: p[1] == "320193" and p[5][:4] in ("2014", "2020")),
            ("acquisition/delisting (Monsanto)", lambda p: p[1] == "1110783"),
            ("early 2010-2012", lambda p: p[5] <= "2011-06-30"),
            ("changed fiscal year", lambda p: cats.get(p[1], {}).get("changed_fiscal_year"))]
    for label, pred in want:
        for b in ("revenue", "net_income"):
            p = next((p for p in T if pred(p) and p[3] == b), None)
            if p:
                ex.append({"case": label, "cik": p[1], "sid": p[2], "field": b, "component_quarters": p[9].split(","),
                           "component_filed": p[10].split(","), "derived_q4": "the fiscal-year-end quarter is the "
                           "10-K's three-month value (vendor) / FY - 9M YTD (SEC); reconciled to the FY total within 1%",
                           "ttm_vs_sec": float(p[6]), "sec_available": p[7], "pit_available": p[4],
                           "fy_check_vs_10K": p[8]})
    mq = next((p for p in N if p[6] == "quarters not consecutive"), None)
    if mq:
        ex.append({"case": "missing quarter (no TTM produced)", "cik": mq[1], "sid": mq[2], "field": mq[3],
                   "newest_quarter": mq[5], "reason": mq[6], "date": mq[4]})
    res = {"fields": fields, "no_ttm_reasons": {k: dict(v) for k, v in reasons.items()},
           "vendor_ttm_without_sec_reference": len(U), "early_values": len(early),
           "early_values_without_public_sec_source": unsafe, "categories": cat_out, "examples": ex,
           "approved_fields": sorted(b for b, v in fields.items() if v["approved_for_H016_field_set"]),
           "excluded_fields": sorted(b for b, v in fields.items() if not v["approved_for_H016_field_set"])}
    (OUT / "x975_results.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if k not in ("examples", "no_ttm_reasons")}, indent=1))
