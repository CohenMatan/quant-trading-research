"""Inputs for X973, the universe-wide restatement guard (D111). For every company and period the vendor reported in
E970-01, the SEC filings that reported that period's values (period_versions); only periods where filings DISAGREE
(> 0.5% between two filings of the same field: original vs restatement/recast) are kept, since only there can a
vendor value come from a later filing. Also each company's fiscal-year ends (for the vendor's interim '*_ttm' =
latest fiscal year semantics). Public SEC data only.
Output: strategies/X973_restatement_guard/guard_ref*.py (packed)."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pack import pack  # noqa: E402
from qresearch.sec_pit import dur_class, index_facts, period_versions, TAGS  # noqa: E402
import e970_parse  # noqa: E402

STRAT = ROOT / "strategies" / "X973_restatement_guard"


def disagree(vals):
    vals = [v for v in vals if v]
    return len(vals) >= 2 and max(vals) / min(vals) - 1 > 0.005 if all(v > 0 for v in vals) else \
        len({round(v, -3) for v in vals}) >= 2


def fy_ends(facts):
    ends = set()
    for t in TAGS["revenue"] + TAGS["net_income"]:
        for f in facts.get(t, ()):
            if "start" in f and dur_class(f["start"], f["end"]) == 4 and f.get("form", "").startswith("10-K"):
                ends.add(f["end"])
    return sorted(ends)


def main():
    t = e970_parse.load()
    pes = defaultdict(set)
    for r in t["reports"]:
        if r["cik"] and r["period_end"]:
            pes[r["cik"]].add(str(r["period_end"]))
    client = SECClient()
    out, fys = {}, {}
    n_periods = n_kept = 0
    for cik in sorted(pes):
        cf = client.companyfacts(cik)
        if not cf:
            continue
        facts = index_facts(cf)
        fe = fy_ends(facts)
        fys[str(cik)] = fe
        want = set(pes[cik]) | {e for e in fe if "2008-06-30" <= e <= "2021-12-31"}
        for pe in sorted(want):
            n_periods += 1
            vers = period_versions(facts, pe)
            by_field = defaultdict(list)
            for v in vers:
                for f, x in v["values"].items():
                    by_field[f].append([v["filed"], x, v["form"]])
            keep = {f: sorted(rows) for f, rows in by_field.items() if disagree([x for _, x, _ in rows])}
            if keep:
                n_kept += 1
                out.setdefault(str(cik), {})[pe] = keep
    table = {"versions": out, "fy_ends": fys}
    STRAT.mkdir(parents=True, exist_ok=True)
    for p in STRAT.glob("guard_ref*.py"):
        p.unlink()
    for name, text in pack(table, "guard_ref").items():
        (STRAT / name).write_text(text)
    stats = {"companies": len(pes), "periods_checked": n_periods, "periods_with_disagreeing_filings": n_kept}
    (Path(__file__).parent / "x973_inputs.json").write_text(json.dumps(stats, indent=1) + "\n")
    print(stats, len(list(STRAT.glob("guard_ref*.py"))), "files")


if __name__ == "__main__":
    main()
