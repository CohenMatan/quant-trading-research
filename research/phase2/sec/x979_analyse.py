"""Field-level release decisions for the 135 quarantined mixed-period reports (D114, owner item 6), from E979-01.

A FIELD of a quarantined vendor report is released only if ALL hold:
  1. the vendor report was observed with exactly this (period end, vendor file date) — E979-01 'R' line;
  2. the field is a releasable flow (FIELD_RELEASABLE: quarterly and fiscal-year revenue, gross profit, net income,
     operating cash flow); balance-sheet fields are never released, so the mismatched balance sheet cannot reach
     a released value (each flow was compared on its own against the SEC);
  3. the SEC original filing (first non-amendment 10-Q/10-K for the period) was filed no later than the vendor's
     file date — the value was public at the historical date (availability still follows the vendor date and every
     PIT rule, timing holds included);
  4. the vendor value equals the SEC AS-FIRST-FILED value within 0.5% — it is the original figure, so no later
     restatement is introduced (restatement-blocked reports are excluded by the PIT store before any release).
Everything else stays quarantined. Output: research/phase2/sec/field_releases.json (packed into the SEC table) and
research/phase2/sec/x979_results.json (counts and per-record detail)."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
sys.path.insert(0, str(Path(__file__).parent))
import e970_parse  # noqa: E402
from qr_fundamentals import FIELD_RELEASABLE  # noqa: E402

OUT = Path(__file__).parent
TOL = 0.005


def main(exp="E979-01"):
    inputs = {(a["sid"], a["pe"], a["fd"]): a for a in json.loads((OUT / "x979_inputs.json").read_text())}
    seen = {}
    for l in e970_parse.lines(exp):
        if l.startswith("R|"):
            _, sid, pe, fd, day, quar, orig_filed, parts = l.split("|", 7)
            seen[(sid, pe, fd)] = (day, quar, orig_filed,
                                   dict(x.split("=", 1) for x in parts.split(";") if "=" in x))
    releases, detail = {}, []
    fields = Counter()
    why_not = Counter()
    for key, a in sorted(inputs.items()):
        row = {"sid": key[0], "ticker": a["ticker"], "pe": key[1], "fd": key[2], "orig_filed": a["orig_filed"],
               "later_sec_value_differs": a.get("later_sec_value_differs", [])}
        if key not in seen:
            row["status"] = "not observed in E979-01 (stays quarantined)"
            detail.append(row)
            why_not["record not observed"] += 1
            continue
        day, quar, orig_filed, ratios = seen[key]
        row["observed"] = day
        row["quarantined_when_observed"] = quar == "1"
        rel, checks = [], {}
        for f in FIELD_RELEASABLE:
            r = ratios.get(f, "missing")
            if orig_filed > key[2]:
                checks[f] = "SEC original filed after the vendor date"
            elif r in ("vendor_na", "sec_na", "missing", "na"):
                checks[f] = r
            elif abs(float(r) - 1) > TOL:
                checks[f] = f"differs ({float(r):.4f})"
            else:
                checks[f] = "verified"
                rel.append(f)
        row["fields"] = checks
        for f, v in checks.items():
            if v != "verified":
                why_not[f"{f}: {v.split(' (')[0]}"] += 1
        if rel:
            releases.setdefault(key[0], []).append([key[1], key[2], rel])
            fields.update(rel)
        row["released_fields"] = rel
        row["status"] = ("released: " + ", ".join(rel)) if rel else "nothing verified (stays quarantined)"
        detail.append(row)
    n_q = sum(1 for d in detail if d.get("released_fields") and all(f + "" in d["released_fields"] for f in ("revenue_q", "net_income_q", "operating_cash_flow_q")))
    res = {"records": len(inputs), "observed": len([k for k in inputs if k in seen]),
           "records_with_any_release": sum(len(v) for v in releases.values()),
           "records_with_core_quarterly_flows_released (revenue, net income, OCF)": n_q,
           "records_fully_quarantined": len(inputs) - sum(len(v) for v in releases.values()),
           "fields_released": dict(sorted(fields.items())),
           "not_released_reasons (field-records)": dict(why_not.most_common()),
           "detail": detail}
    (OUT / "field_releases.json").write_text(json.dumps(releases, indent=1, sort_keys=True) + "\n")
    (OUT / "x979_results.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if k != "detail"}, indent=1))
