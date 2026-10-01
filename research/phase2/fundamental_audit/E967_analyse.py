"""Tables from the X967 fundamental-data audit run E967-02 (2010-2021): coverage by year, missingness of the core
profitability/quality set by size/sector/exchange/age/distress, market cap vs shares by year and field, EPS
consistency, staleness, timing histograms, sample-company timelines. Counts and ratios only (no raw values).

    python research/phase2/fundamental_audit/E967_analyse.py -> research/phase2/fundamental_audit/E967_tables.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MSG = ROOT / "experiments/E967-02/messages.txt"
NEAR = "<=1.02"
NEAR_LO = "<=0.98"


def summary(lines):
    text = "".join(l.split("|", 3)[3] for l in lines if l.startswith("QRF67|summary|"))
    return json.loads(text)


def share(h, keys):
    n = sum(h.values())
    return round(sum(h.get(k, 0) for k in keys) / n, 4) if n else None


def main():
    lines = MSG.read_text().splitlines()
    s = summary(lines)
    out = {}
    elig = s["eligible_by_year"]                 # stock-months per year
    cov = {}
    for y, c in sorted(s["coverage"].items()):
        n = elig[y]
        cov[y] = {k: round(v / n, 4) for k, v in sorted(c.items())}
        cov[y]["stock_months"] = n
    out["coverage_share_by_year"] = cov
    out["missing_core_by_dimension"] = {k: dict(n=v[0], missing=v[1], missing_share=round(v[1] / v[0], 4))
                                        for k, v in sorted(s["missing_core"].items())}
    out["cap_over_price_x_shares_within_2pct"] = {lab: {y: share(h, (NEAR,)) for y, h in sorted(v.items())}
                                                  for lab, v in s["cap_ratio"].items()}
    out["cap_over_price_x_shares_below_0.45"] = {lab: {y: share(h, ("<=0.0", "<=0.2", "<=0.45")) for y, h in sorted(v.items())}
                                                 for lab, v in s["cap_ratio"].items()}
    out["eps_consistency_within_2pct"] = {y: share(h, (NEAR,)) for y, h in sorted(s["eps_consistency"].items())}
    out["staleness_by_year"] = s["staleness_by_year"]
    keys = ["days", "stock_days", "read_errors", "no_file_date", "file_date_after_today", "statement_file_date_after_today",
            "accession_year_after_today", "accession_year_ne_file_year", "accession_unparsed", "default_period_ne_quarter",
            "statements_period_ne_report_period", "new_periods", "period_backwards", "amended_same_period",
            "amended_file_date_changed", "silent_value_change_same_period", "fiscal_year_end_changes", "ever_eligible",
            "eligible_then_disappeared_before_end"]
    out["timing_counts"] = {k: s[k] for k in keys}
    out["lag_first_seen_minus_file_days"] = s["lag_first_seen_minus_file"]
    out["gap_file_minus_period_end_days"] = s["gap_file_minus_period_end"]
    out["gap_exactly_45_by_year"] = s["gap_exactly_45_by_year"]
    out["new_periods_by_year"] = s["new_periods_by_year"]
    out["approximated_file_date_share_by_year"] = {y: round(s["gap_exactly_45_by_year"].get(y, 0) / n, 4)
                                                   for y, n in s["new_periods_by_year"].items()}
    out["disappeared_by_year"] = s["disappeared_by_year"]
    out["examples"] = s["examples"]
    out["sample_seen"] = s["sample_seen"]
    out["sample_lines"] = [l for l in lines if l.startswith("QRF67|sample|") or l.startswith("QRF67|shares|")]
    (Path(__file__).parent / "E967_tables.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("cap_over_price_x_shares_within_2pct", "cap_over_price_x_shares_below_0.45",
                                          "eps_consistency_within_2pct", "approximated_file_date_share_by_year")}, indent=0))
    for y, c in cov.items():
        print(y, c["stock_months"], {k: c[k] for k in ("CORE_SET", "gross_profit.twelve_months", "operating_income.twelve_months",
                                                       "revenue.twelve_months", "total_assets.three_months",
                                                       "operating_cash_flow.twelve_months", "free_cash_flow.twelve_months", "roa.value")})
    for k, v in out["missing_core_by_dimension"].items():
        print(k, v)


if __name__ == "__main__":
    main()
