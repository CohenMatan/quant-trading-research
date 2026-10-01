"""Tables from the PIT-layer canary E969-01 (D108): rule checks, coverage by year and cause, missingness
concentration, classification point-in-time audit, financial-format vs vendor labels, Visa and deal-date checks,
D043 context. Counts only.

    python research/phase2/fundamental_audit/E969_analyse.py -> research/phase2/fundamental_audit/E969_tables.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    lines = (ROOT / "experiments/E969-01/messages.txt").read_text().splitlines()
    s = json.loads("".join(l.split("|", 3)[3] for l in lines if l.startswith("QRC69|summary|")))
    cov = {}
    for y, c in sorted(s["coverage"].items()):
        n = c.get("eligible", 0)
        cov[y] = dict(eligible_stock_months=n,
                      usable=c.get("usable", 0), usable_share=round(c.get("usable", 0) / n, 4) if n else None,
                      non_financial_usable=c.get("non_financial_usable", 0),
                      financial_format_excluded=c.get("financial_format", 0),
                      unclassifiable=c.get("unclassifiable", 0),
                      missing_unsafe_timing=c.get("withheld_timing_rule", 0),
                      missing_absent_filing_data=c.get("no_filing_data", 0),
                      missing_fields_in_filing=c.get("missing_fields_in_filing", 0),
                      missing_stale=c.get("stale_beyond_policy", 0))
    conc = {k: dict(n=v.get("n", 0), usable_share=round(v.get("usable", 0) / v["n"], 4) if v.get("n") else None,
                    **{c: v[c] for c in v if c not in ("n",)}) for k, v in sorted(s["missing_concentration"].items())}
    out = dict(rule_checks={k: s[k] for k in ("days", "stock_days", "exposed_before_available", "exposed_before_filing",
                                              "estimated_exposed_before_pe90", "stale_exposed", "amendment_exposed_early",
                                              "vendor_new_reports", "quarantine_companies")},
               store_stats=s["store_stats"], quarantine_by_year=s["quarantine_by_year"], field_guard=s["field_guard"],
               classification_changes=s["classification_changes"], fin_vs_sector=s["fin_vs_sector"],
               visa=s["visa"], named_eligible_months=s["named_eligible_months"], deal_check=s["deal_check"],
               coverage_by_year=cov, missing_concentration=conc,
               survivorship_liquid_no_fundamentals_stock_months=s["survivorship_liquid_no_fundamentals"],
               survivorship_top=s["survivorship_top"])
    (Path(__file__).parent / "E969_tables.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("rule_checks", "store_stats", "quarantine_by_year", "field_guard",
                                          "classification_changes", "deal_check")}, indent=0))
    for y, c in cov.items():
        print(y, c)
    for k, v in conc.items():
        print(k, v)
    print(sorted(out["fin_vs_sector"].items(), key=lambda x: -x[1])[:14])
    v = out["visa"]
    print("visa", min(v), max(v), sum(x["eligible"] for x in v.values()), len(v))


if __name__ == "__main__":
    main()
