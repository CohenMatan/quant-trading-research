"""Correction table v2 (D113): merge identity v1 (D111: float/lifetime/name evidence) and identity v2 (SEC-filed
dated ticker evidence) under evidence priority, then pack everything the opt-in SEC layer needs.

Tiers (strongest first):
  A  SEC ticker-evidenced (identity v2, >= 2 filings whose instance prefix equals the security's dated ticker),
     float evidence consistent or absent;
  B  v1 link CONFIRMED by v2 is tier A; v1 links WITHOUT v2 evidence keep their v1 tier (high / medium / tier 2 /
     no-equity-end); a v1 link CONTRADICTED by v2 (the registrant is v2-linked to another security, or the security
     to another registrant, over an overlapping period of more than 120 days) is dropped.
Records per registrant: periodic filings up to its equity end (Form 25/15 or last equity report) and 2021-12-31.
Packed into src/qresearch/lean/qr_sec_data*.py: corrections, timing holds (D111), quarantine releases (D111),
restatement blocks (E973-01), SEC SIC history (sic_history.py). Audit copy: corrections_v2.json."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
from qresearch.sec_pack import pack  # noqa: E402
from qresearch.sec_pit import build_company, index_facts  # noqa: E402
import e970_parse  # noqa: E402
import sic_history  # noqa: E402
from build_x971 import equity_end  # noqa: E402
from identity_v2 import overlap_days  # noqa: E402

OUT = Path(__file__).parent
LEAN = ROOT / "src" / "qresearch" / "lean"


def main():
    v1 = json.loads((OUT / "corrections.json").read_text())
    v2 = {c: L for c, L in json.loads((OUT / "identity_v2.json").read_text())["links"].items() if L["status"] == "linked"}
    v2pairs = {}
    for c, L in v2.items():
        for s, d in L["hits"].items():
            v2pairs[(c, s)] = (min(d), max(d))
    links = {}
    dropped = []
    for (c, s), span in v2pairs.items():
        fl = v2[c].get("float", {}).get(s, {}).get("check", "none")
        links[(c, s)] = {"tier": "A: SEC ticker-evidenced", "float_check": fl, "span": span,
                         "v1": None, "names": v2[c]["names"]}
    for s, lst in v1.items():
        for x in lst:
            c = str(x["cik"])
            span1 = (x.get("effective_from") or "2009-01-01", min(x.get("equity_end") or "2021-12-31", "2021-12-31"))
            if (c, s) in links:
                links[(c, s)]["v1"] = x["confidence"]
                continue
            contra = [(c2, s2) for (c2, s2), sp in v2pairs.items()
                      if ((c2 == c and s2 != s) or (s2 == s and c2 != c)) and overlap_days(span1, sp) > 120]
            if contra:
                dropped.append({"cik": c, "sid": s, "v1": x["confidence"], "contradicted_by": contra})
                continue
            links[(c, s)] = {"tier": f"B: v1 {x['confidence']}", "float_check": "v1", "span": span1, "v1": x["confidence"],
                             "names": x["names"]}
    client = SECClient()
    table, audit = {}, {}
    for (c, s), L in sorted(links.items()):
        cf, sub = client.companyfacts(int(c)), client.submissions(int(c))
        if not cf or not sub:
            continue
        end, src = equity_end(filings_table(sub), index_facts(cf))
        last = min(end or "2021-12-31", "2021-12-31")
        recs = [r for r in build_company(cf, sub) if r["filed"] <= last]
        rows = [[r["accn"], r["form"], r["filed"], r["period_end"], r["cover_date"], r["cover_shares"],
                 {k: v for k, v in r["values"].items() if v is not None}] for r in recs]
        ent = table.setdefault(s, {"cik": [], "name": [], "status": "repaired", "confidence": [], "filings": [],
                                   "method": "SEC XBRL cover shares x QuantConnect raw close (live split adjustment); "
                                             "statement totals as first filed"})
        ent["cik"].append(int(c))
        ent["name"].append(L["names"][0])
        ent["confidence"].append(L["tier"])
        ent["filings"] = sorted(ent["filings"] + rows, key=lambda r: (r[2], r[0]))
        audit.setdefault(s, []).append({"cik": int(c), "names": L["names"], "tier": L["tier"], "v1": L["v1"],
                                        "float_check": L["float_check"], "evidence_span": list(L["span"]),
                                        "equity_end": end, "end_source": src, "n_filings": len(rows),
                                        "filings": [{"accn": r[0], "form": r[1], "filed": r[2], "period_end": r[3],
                                                     "cover_date": r[4], "cover_shares": r[5]} for r in rows]})
    holds = json.loads((OUT / "timing_holds.json").read_text())
    releases = json.loads((OUT / "quarantine_release.json").read_text())
    blocks = json.loads((OUT / "restatement_blocks.json").read_text())
    sic, sic_src = sic_history.build({s: v["cik"] for s, v in table.items()})
    for p in LEAN.glob("qr_sec_data*.py"):
        p.unlink()
    for name, text in pack({"corrections": table, "timing_holds": holds, "quarantine_releases": releases,
                            "restatement_blocks": blocks, "sic_history": sic}, "qr_sec_data").items():
        (LEAN / name).write_text(text)
    (OUT / "corrections_v2.json").write_text(json.dumps({"links": audit, "dropped_v1": dropped,
                                                         "sic_sources": sic_src}, indent=1, sort_keys=True) + "\n")
    tiers = defaultdict(int)
    for v in audit.values():
        for x in v:
            tiers[x["tier"]] += 1
    print(len(table), "securities;", dict(tiers), "; dropped v1:", len(dropped), "; sic:", sic_src)


if __name__ == "__main__":
    main()
