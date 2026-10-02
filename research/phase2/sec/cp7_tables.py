"""Markdown tables for the P2-CP7 checkpoint, generated from the evidence files (no hand-typed numbers).
python research/phase2/sec/cp7_tables.py E976-04            # print the tables
python research/phase2/sec/cp7_tables.py --fill <doc> E976-04  # replace {{TABLE_*}} placeholders in the checkpoint"""
from __future__ import annotations

import json
import sys
from pathlib import Path

OUT = Path(__file__).parent


def pct(x, d=1):
    return "–" if x is None else f"{100 * x:.{d}f}%"


def tables(exp="E976-04"):
    """{placeholder: markdown} for the checkpoint."""
    out, cur = {}, []

    def print(line=""):                        # noqa: A001 — collect instead of printing
        cur.append(line)

    def cut(name):
        out[name] = "\n".join(x for x in "\n".join(cur).split("\n") if not x.startswith("### ")).strip()
        cur.clear()

    r = json.loads((OUT / f"e976_results_{exp}.json").read_text())
    ra = json.loads((OUT / "residual_audit.json").read_text())["by_year"]
    cov = r["coverage_by_year"]
    print("### Table A — survivorship (eligible ≥ $2B, NYSE/Nasdaq, liquid; names per month)\n")
    print("| Year | Native (vendor) | SEC-repaired | SEC-side unresolved registrants ≥ $2B float (+ $1–2B 'possible') | "
          "Missing share: D043 estimate → P2-CP6 → **now** (upper bound) |")
    print("|---|---|---|---|---|")
    for y, v in cov.items():
        a = ra.get(y, {})
        print(f"| {y} | {v['native_per_month']:,.0f} | {v['sec_repaired_per_month']:.0f} | "
              f"{a.get('missing', 0)} (+{a.get('possible|missing', 0)}) | "
              f"{pct(v['D043_estimate_missing_share_before'])} → {pct(v['P2_CP6_missing_share_after'])} → "
              f"**{pct(v['missing_share_after (upper bound incl. possible)'])}** |")
    cut("TABLE_A")
    print("\n### Table B — usable data (names per month)\n")
    print("| Year | Usable PIT record (any) | Excluded: financial / REIT / financial-format | Non-financial eligible | "
          "True TTM present (revenue / net income / OCF) | **Final usable** (count, share of non-financial) | "
          "Final usable: native / repaired | Quarantine-lost stock-months |")
    print("|---|---|---|---|---|---|---|---|")
    for y, v in cov.items():
        e, t = v["excluded_per_month"], v["usable_true_TTM_share_by_field"]
        nr = v["final_usable_coverage_native / repaired"]
        print(f"| {y} | {pct(v['usable_PIT_fundamentals_share'])} | {e['financial']:.0f} / {e['REIT']:.0f} / "
              f"{e['financial-format']:.0f} | {v['non_financial_eligible_per_month']:,.0f} | "
              f"{pct(t['revenue'], 0)} / {pct(t['net_income'], 0)} / {pct(t['operating_cash_flow'], 0)} | "
              f"**{v['final_usable_per_month (non-financial, approved TTM revenue/net income/OCF + assets/equity)']:,.0f} "
              f"({pct(v['final_usable_coverage_of_non_financial'])})** | {pct(nr[0], 0)} / {pct(nr[1], 0)} "
              f"(of {v['non_financial_repaired_per_month']:.0f}) | {v['quarantine_lost_stock_months']} |")
    cut("TABLE_B")
    print("\n### Table C — why non-financial names lack final usable data (names per month)\n")
    keys = ["fewer than four visible quarters", "quarters not consecutive", "no fiscal-year reconciliation inside the window",
            "missing quarterly value", "stale", "no balance-sheet snapshot"]
    print("| Year | " + " | ".join(keys) + " |")
    print("|---|" + "---|" * len(keys))
    for y, v in cov.items():
        n = v["non_financial_not_usable_per_month_by_reason"]
        print(f"| {y} | " + " | ".join(f"{n.get(k, 0):.0f}" for k in keys) + " |")
    cut("TABLE_C")
    print("\n### Table D — composition (equal-weight month returns, annualised; characterisation, not a factor)\n")
    print("| Year | Repaired share of eligible | Effect of the repair on the EW universe (pp/yr) | "
          "Non-financial names without usable data | Availability bias of a usable-only universe (pp/yr) |")
    print("|---|---|---|---|---|")
    for y, g in r["composition_returns"].items():
        print(f"| {y} | {pct(g.get('repaired_share'))} | {g.get('effect_of_repair_on_EW_universe_pp', 0):+.2f} | "
              f"{pct(g.get('ttm_missing_share'))} | {g.get('availability_bias_of_usable_only_universe_pp', 0):+.2f} |")
    cr, ct = r["composition_returns_2010_2021"], r["composition_returns_ttm_2010_2021"]
    print(f"\n2010–2021 equal-weight: native {pct(cr['native'])}/yr vs repaired {pct(cr['corrected'])}/yr; "
          f"non-financial names with usable data {pct(ct['ttm_usable'])}/yr vs without {pct(ct['ttm_missing'])}/yr.")
    cut("TABLE_D")
    print("\n### Table E — usable data by later outcome (non-financial eligible stock-months)\n")
    print("| Outcome (from the company's own SEC filings) | Securities | Eligible months | Usable months | Usable share |")
    print("|---|---|---|---|---|")
    for o, v in r["ttm_missingness_by_outcome"].items():
        print(f"| {o} | {v['securities']:,} | {v['eligible_months']:,} | {v['usable_months']:,} | {pct(v['usable_share'])} |")
    cut("TABLE_E")
    print("\n### Table F — final usable share by size tercile (non-financial)\n")
    print("| Year | T1 (smallest) | T2 | T3 (largest) |")
    print("|---|---|---|---|")
    for y, v in r["final_usable_share_by_size_tercile"].items():
        print(f"| {y} | {pct(v.get('T1'))} | {pct(v.get('T2'))} | {pct(v.get('T3'))} |")
    cut("TABLE_F")
    agg = {}
    for k, n in r["sic_vs_structure (stock-months)"].items():
        parts = dict(x.split("=") for x in k.split("|"))
        sic = {"REIT": "REIT (6798)", "fin": "financial (6000-6999)", "op": "operating"}[parts["sic"]]
        if parts["sic"] == "fin":
            sic += " — " + {"60": "banks", "61": "credit (non-bank)", "62": "brokers/asset managers", "63": "insurers incl. health",
                            "64": "insurance agents", "65": "real estate", "67": "holding/investment offices"}.get(parts.get("sic2"), parts.get("sic2"))
        cell = agg.setdefault(sic, [0, 0])
        cell[0 if parts["structure_fin"] == "True" else 1] += n
    print("| SEC SIC at filing | Bank/insurer layout | Operating layout |")
    print("|---|---|---|")
    for k, (a, b) in sorted(agg.items()):
        print(f"| {k} | {a:,} | {b:,} |")
    cut("TABLE_SIC")
    return out


def fill(doc, exp="E976-04"):
    path = Path(doc)
    text = path.read_text()
    for k, v in tables(exp).items():
        text = text.replace("{{" + k + "}}", v)
    path.write_text(text)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--fill"]:
        fill(*sys.argv[2:])
    else:
        for k, v in tables(*sys.argv[1:]).items():
            __builtins__.print(f"## {k}\n\n{v}\n")
