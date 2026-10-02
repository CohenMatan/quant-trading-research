"""Markdown tables for P2-CP8 part A (2011 cleanup), generated from evidence files only.
python research/phase2/sec/cp8_tables.py --fill <doc> [before=E976-04] [after=E976-06]"""
from __future__ import annotations

import json
import sys
from pathlib import Path

OUT = Path(__file__).parent


def pct(x, d=1):
    return "–" if x is None else f"{100 * x:.{d}f}%"


def tables(before="E976-04", after="E976-06"):
    b = json.loads((OUT / f"e976_results_{before}.json").read_text())["coverage_by_year"]
    ra = json.loads((OUT / f"e976_results_{after}.json").read_text())
    a = ra["coverage_by_year"]
    out = {}
    rows = ["| Year | Non-financial eligible (names/month) | Final usable before (E976-04) | **Final usable after (" + after +
            ")** | Native / repaired after | TTM values using a field release (stock-months: revenue / net income / OCF / gross profit) |",
            "|---|---|---|---|---|---|"]
    for y in a:
        u = a[y]["ttm_values_using_a_field_release (stock-months)"]
        nr = a[y]["final_usable_coverage_native / repaired"]
        rows.append(f"| {y} | {a[y]['non_financial_eligible_per_month']:,.0f} | {pct(b[y]['final_usable_coverage_of_non_financial'])} | "
                    f"**{pct(a[y]['final_usable_coverage_of_non_financial'])}** | {pct(nr[0], 0)} / {pct(nr[1], 0)} | "
                    + (" / ".join(str(u.get(k, 0)) for k in ("revenue", "net_income", "operating_cash_flow", "gross_profit")) if u else "–")
                    + " |")
    out["TABLE_COVERAGE"] = "\n".join(rows)
    keys = [("gross_profit_ttm4q_and_assets_pos", "GP/A computable"), ("operating_cash_flow_ttm4q_and_assets_pos", "OCF/A"),
            ("net_income_ttm4q_and_assets_pos", "NI/A"), ("net_income_ttm4q_and_equity_pos", "NI/E (equity > 0)"),
            ("revenue_ttm4q", "Revenue TTM"), ("assets_pos", "Total assets > 0"), ("equity_pos", "Equity > 0")]
    rows = ["| Year | " + " | ".join(n for _, n in keys) + " |", "|---|" + "---|" * len(keys)]
    for y in a:
        f = a[y]["approved_field_availability_share_of_non_financial"]
        rows.append(f"| {y} | " + " | ".join(pct(f.get(k), 0) for k, _ in keys) + " |")
    out["TABLE_FIELDS"] = "\n".join(rows)
    rows = ["| Year | Effect of the repair on the EW universe (pp/yr) | Non-financial names without usable data | "
            "Availability bias of a usable-only universe (pp/yr) |", "|---|---|---|---|"]
    for y, g in ra["composition_returns"].items():
        rows.append(f"| {y} | {g.get('effect_of_repair_on_EW_universe_pp', 0):+.2f} | {pct(g.get('ttm_missing_share'))} | "
                    f"{g.get('availability_bias_of_usable_only_universe_pp', 0):+.2f} |")
    cr, ct = ra["composition_returns_2010_2021"], ra["composition_returns_ttm_2010_2021"]
    rows.append(f"\n2010–2021 equal-weight: native {pct(cr['native'])}/yr vs repaired {pct(cr['corrected'])}/yr; "
                f"non-financial names with usable data {pct(ct['ttm_usable'])}/yr vs without {pct(ct['ttm_missing'])}/yr.")
    out["TABLE_BIAS"] = "\n".join(rows)
    rows = ["| Later outcome | Securities | Eligible months | Usable months | Usable share |", "|---|---|---|---|---|"]
    for o, v in ra["ttm_missingness_by_outcome"].items():
        rows.append(f"| {o} | {v['securities']:,} | {v['eligible_months']:,} | {v['usable_months']:,} | {pct(v['usable_share'])} |")
    out["TABLE_OUTCOME"] = "\n".join(rows)
    return out


def fill(doc, before="E976-04", after="E976-06"):
    p = Path(doc)
    t = p.read_text()
    for k, v in tables(before, after).items():
        t = t.replace("{{" + k + "}}", v)
    p.write_text(t)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--fill"]:
        fill(*sys.argv[2:])
    else:
        for k, v in tables(*sys.argv[1:]).items():
            print(f"## {k}\n\n{v}\n")
