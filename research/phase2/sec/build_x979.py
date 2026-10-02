"""Inputs for X979 (D114, owner item 6): field-level SEC verification of the 135 quarantined 'mixed-period' vendor
reports (income statement = original filing, balance sheet = an earlier period; P2-CP6 x971_results.json).

For each record: the SEC ORIGINAL filing for the period (first non-amendment 10-Q/10-K, the one X971 identified),
its filing date, and its as-first-filed values of the fields a field-level release may cover (approved flows only):
  quarterly:  revenue_q, gross_profit_q, net_income_q, operating_cash_flow_q
  fiscal-year (vendor interim '*_ttm' semantics = latest completed fiscal year known on the filing date):
              revenue_ttm, gross_profit_ttm, net_income_ttm, operating_cash_flow_ttm
plus, for disclosure, whether any LATER SEC filing reported a different quarterly value for the same period.
Public SEC data only. Output: strategies/X979_field_release_verification/ref*.py (packed) + x979_inputs.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pack import pack  # noqa: E402
from qresearch.sec_pit import build_company, index_facts, period_versions  # noqa: E402

OUT = Path(__file__).parent
STRAT = ROOT / "strategies" / "X979_field_release_verification"
FIELDS = ("revenue_q", "gross_profit_q", "net_income_q", "operating_cash_flow_q",
          "revenue_ttm", "gross_profit_ttm", "net_income_ttm", "operating_cash_flow_ttm")


def main():
    det = json.loads((OUT / "x971_results.json").read_text())["quarantine"]["detail"]
    recs = [d for d in det if d["verdict"].startswith("mixed-period")]
    client = SECClient()
    built, facts = {}, {}
    ref, audit = {}, []
    for d in recs:
        cik = int(d["cik"])
        if cik not in built:
            cf, sub = client.companyfacts(cik), client.submissions(cik)
            built[cik] = build_company(cf, sub) if cf else []
            facts[cik] = index_facts(cf) if cf else {}
        orig = next((r for r in built[cik] if r["accn"] == d["orig_accn"]), None)
        row = {"sid": d["sid"], "cik": cik, "ticker": d["ticker"], "pe": d["pe"], "fd": d["fd"],
               "orig_accn": d["orig_accn"], "orig_form": d["orig_form"], "orig_filed": d["orig_filed"]}
        if orig is None:
            row["note"] = "original filing not rebuilt from company facts"
            audit.append(row)
            continue
        row["sec"] = {f: orig["values"].get(f) for f in FIELDS}
        later = set()
        for v in period_versions(facts[cik], d["pe"]):
            if v["filed"] <= d["orig_filed"]:
                continue
            for f in ("revenue_q", "net_income_q"):
                a, b = v["values"].get(f), orig["values"].get(f)
                if a and b and abs(a / b - 1) > 0.005:
                    later.add(f)
        row["later_sec_value_differs"] = sorted(later)
        audit.append(row)
        ref.setdefault(d["sid"], []).append([d["pe"], d["fd"], d["orig_filed"], row["sec"]])
    STRAT.mkdir(parents=True, exist_ok=True)
    for p in STRAT.glob("ref*.py"):
        p.unlink()
    for name, text in pack(ref, "ref").items():
        (STRAT / name).write_text(text)
    (OUT / "x979_inputs.json").write_text(json.dumps(audit, indent=1, sort_keys=True) + "\n")
    print(len(recs), "records;", sum(len(v) for v in ref.values()), "with an SEC original;",
          sum(1 for a in audit if a.get("later_sec_value_differs")), "with a later differing SEC value")


if __name__ == "__main__":
    main()
