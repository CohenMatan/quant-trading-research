"""Financial/REIT exclusion policy audit (D113, owner item 10). Characterisation only — nothing here classifies.

1. The 13 companies where the D108 filing-structure rule and the vendor template disagreed (fin_audit.json, P2-CP6):
   their SEC-assigned SIC timeline and the category the SIC policy (qr_industry) gives them now.
2. Every move into or out of SIC 6798 (REIT) in the SEC SIC histories of the universe's securities, with the
   registrant name as filed — REIT conversions (e.g. towers, data centres, prisons, timber) and the reverse moves,
   which the owner must see because a registrant can stay a REIT under a non-6798 code (Host Hotels, 7011).
3. Securities whose SIC is outside 6000-6999 while the registrant's name as filed says REIT/Realty/Properties/
   Trust (possible REIT-like issuers kept by the policy) — names are used for this listing only.
Output: research/phase2/sec/industry_audit.json"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import e970_parse  # noqa: E402
import rss_index  # noqa: E402
import sic_history  # noqa: E402
from qr_industry import SICHistory, classify  # noqa: E402

OUT = Path(__file__).parent
REITLIKE = re.compile(r"\b(REIT|REALTY|PROPERTIES|PROPERTY TRUST|REAL ESTATE)\b", re.I)


def main():
    t = e970_parse.load()
    corr = json.loads((OUT / "corrections_v2.json").read_text())["links"]
    tl, _ = sic_history.build({s: [x["cik"] for x in v] for s, v in corr.items()})
    hist = SICHistory(tl)
    names = defaultdict(dict)
    for r in rss_index.load():
        names[r["cik"]][r["filed"]] = r["name"]

    def name_at(cik, d):
        ds = sorted(x for x in names.get(cik, {}) if x <= d)
        return names[cik][ds[-1]] if ds else None

    fin = json.loads((OUT / "fin_audit.json").read_text())
    tick2sid = defaultdict(set)
    for sid, n in t["native"].items():
        for tk in n["tickers"]:
            tick2sid[tk].add(sid)
    dis = []
    for c in fin["company_detail"]:
        sids = sorted(s for s in tick2sid.get(c["ticker"], ()) if t["native"][s]["cik"] == c["cik"]) or \
            sorted(tick2sid.get(c["ticker"], ()))
        sid = sids[0] if sids else None
        mid = date(int(str(c["from"])[:4]), int(str(c["from"])[4:]), 15)
        sic = hist.sic_on(sid, mid) if sid else None
        dis.append({"ticker": c["ticker"], "group (characterisation)": c["group (characterisation only)"],
                    "old_structure_rule": c["pit_rule"], "sic_timeline": tl.get(sid, []),
                    "sic_policy_category_at_start": classify(sic, None)[0] if sic else "no SEC SIC (structure rule)"})
    moves = []
    for sid, rows in tl.items():
        for (e0, s0, c0), (e1, s1, c1) in zip(rows, rows[1:]):
            if (s0 == 6798) != (s1 == 6798):
                moves.append({"sid": sid, "date": e1, "from": s0, "to": s1, "cik": c1,
                              "name_as_filed": name_at(c1, e1), "direction": "into REIT code" if s1 == 6798 else "out of REIT code"})
    reitlike = []
    for sid, rows in tl.items():
        for e, s, c in rows:
            n = name_at(c, e) or ""
            if not (6000 <= s <= 6999) and REITLIKE.search(n):
                reitlike.append({"sid": sid, "from": e, "sic": s, "name_as_filed": n})
                break
    res = {"disagreement_companies_P2_CP6": dis, "reit_code_moves": sorted(moves, key=lambda m: m["date"]),
           "reit_like_names_outside_financial_codes": reitlike,
           "summary": {"reit_code_moves": len(moves),
                       "into": sum(m["direction"] == "into REIT code" for m in moves),
                       "out_of": sum(m["direction"] == "out of REIT code" for m in moves),
                       "reit_like_names_kept": len(reitlike)}}
    (OUT / "industry_audit.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["summary"]))
    for d in r["disagreement_companies_P2_CP6"]:
        print(d["ticker"], d["group (characterisation)"], d["old_structure_rule"], d["sic_policy_category_at_start"],
              [x[1] for x in d["sic_timeline"]])
    for m in r["reit_code_moves"]:
        print(m["date"], m["from"], "->", m["to"], m["name_as_filed"])
    for m in r["reit_like_names_outside_financial_codes"]:
        print("REIT-like kept:", m["sic"], m["name_as_filed"])
