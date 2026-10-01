"""Financial-company exclusion audit (D111, owner item 11). Inputs: E970-01 'F' lines (stock-months where the
PIT financial-format rule and the vendor's statement template disagree; identifiers and flags only) and the
SEC XBRL tags present in each company's own filings (as filed; public). Vendor sector/industry codes are
current-status metadata and are used ONLY to characterise the disagreements, never to classify.

Output: research/phase2/sec/fin_audit.json"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pit import index_facts, periodic_filings  # noqa: E402
import e970_parse  # noqa: E402

GROUPS = {"10420070": "mortgage REIT", "20630010": "managed-care insurer"}
SEC_TAGS = {"revenue": ("Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax"),
            "gross_profit": ("GrossProfit",),
            "cost_of_revenue": ("CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"),
            "operating_income": ("OperatingIncomeLoss",)}


def group(ind, sector):
    if ind in GROUPS:
        return GROUPS[ind]
    if sector == "104":
        return "equity REIT / real estate"
    if sector == "103":
        return "financial services (asset manager, servicer)"
    return "other"


def sec_structure(client, cik):
    cf = client.companyfacts(cik)
    if not cf:
        return {}
    f = index_facts(cf)
    out = Counter()
    for x in periodic_filings(f, None):
        if x["form"] not in ("10-K", "10-Q") or not ("2010" <= x["filed"][:4] <= "2021"):
            continue
        flags = "".join(str(int(any(any(r["accn"] == x["accn"] for r in f.get(t, ())) for t in tags)))
                        for tags in SEC_TAGS.values())
        out[flags] += 1
    return dict(out)


def main():
    t = e970_parse.load()
    client = SECClient()
    fin = t["fin"]
    total_checked = t["counts"]["fin_checked"]
    by = defaultdict(list)
    for r in fin:
        by[(r["ticker"], r["cik"])].append(r)
    companies = []
    for (tic, cik), rows in sorted(by.items(), key=lambda kv: -len(kv[1])):
        r0 = rows[0]
        companies.append({
            "ticker": tic, "cik": cik, "stock_months": len(rows),
            "from": min(r["ym"] for r in rows), "to": max(r["ym"] for r in rows),
            "pit_rule": "financial-format" if r0["fin_format"] else "operating-format",
            "vendor_template": r0["template"], "group (characterisation only)": group(r0["industry"], r0["sector"]),
            "vendor_lines_present(rev,gp,cor,oi)": dict(Counter("".join(str(int(r[k])) for k in ("rev", "gp", "cor", "oi"))
                                                              for r in rows)),
            "sec_filing_tags(rev,gp,cor,oi) per filing": sec_structure(client, cik),
        })
    years = Counter(str(r["ym"] // 100) for r in fin)
    res = {
        "stock_months_checked": total_checked, "disagreeing_stock_months": len(fin),
        "disagreement_share": len(fin) / total_checked, "companies": len(by),
        "by_direction": {f"rule={'fin' if k[0] else 'operating'}|template={k[1]}": v
                         for k, v in Counter((r["fin_format"], r["template"]) for r in fin).items()},
        "by_group": dict(Counter(group(r["industry"], r["sector"]) for r in fin)),
        "by_year": dict(sorted(years.items())),
        "company_detail": companies,
    }
    (Path(__file__).parent / "fin_audit.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if k != "company_detail"}, indent=1))
