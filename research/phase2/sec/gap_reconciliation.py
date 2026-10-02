"""Why the D043 survivorship estimate (X954) overstated the gap, and the pre-XBRL blind spot (D113, owner item 3).

Every liquid QuantConnect security WITHOUT fundamentals (E970-01: 2,928; price >= $5, ADV20 >= $5M) is classified by
SEC filing evidence (dated tickers vs XBRL instance-name prefixes, +-3 months; public SEC data):
  linked                 — in the correction table (repaired);
  10-K/10-Q filer, unlinked — some 10-K/10-Q registrant filed under this ticker while the security carried it,
                           but identity v2 did not link them (reason from identity_v2.json);
  20-F/40-F filer only   — only foreign private issuers filed under the ticker (ADRs etc.: not US common stock);
  no XBRL filer          — no XBRL filer ever used the ticker in that period (ETFs, funds, notes, ADRs of
                           non-filers ... and US companies that ended BEFORE their first XBRL filing).
The last group, restricted to securities that stopped trading before 2011-07-01 (smaller filers' first XBRL periods
end after 2011-06-15), is the pre-XBRL blind spot: SEC structured data cannot identify or size these companies.
Output: research/phase2/sec/gap_reconciliation.json"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
import e970_parse  # noqa: E402
import rss_index  # noqa: E402
from identity_v2 import ym, ym_add  # noqa: E402

OUT = Path(__file__).parent


def main():
    t = e970_parse.load()
    corr = json.loads((OUT / "corrections_v2.json").read_text())["links"]
    v2 = json.loads((OUT / "identity_v2.json").read_text())["links"]
    native_cik = {n["cik"] for n in t["native"].values() if n["cik"]}
    pref = defaultdict(list)
    for r in rss_index.load():
        if r["prefix"]:
            pref[r["prefix"].replace(".", "")].append((ym(r["filed"]), r["form"], r["cik"]))
    out, detail = Counter(), defaultdict(list)
    for sid, m in t["nofund"].items():
        if sid in corr:
            out["linked (repaired)"] += 1
            continue
        dom, forn = set(), set()
        for tk, a, b in m["tickers"]:
            for fy, form, cik in pref.get(tk.replace(".", "").upper(), ()):
                if ym_add(a, -3) <= fy <= ym_add(b, 3):
                    (dom if form.startswith(("10-K", "10-Q")) else forn if form.startswith(("20-F", "40-F", "6-K"))
                     else set()).add(cik)
        if dom:
            why = Counter()
            for c in dom:
                if c in native_cik:
                    why["registrant is covered by QuantConnect under another security"] += 1
                elif str(c) in v2:
                    why[v2[str(c)]["status"].split(":")[0]] += 1
                else:
                    why["identity v2: < 2 dated matching filings or excluded before matching"] += 1
            k = "10-K/10-Q filer, unlinked"
            detail[k].append({"sid": sid, "tickers": [x[0] for x in m["tickers"]], "why": dict(why),
                              "last_seen": str(m["last_seen"])})
        elif forn:
            k = "20-F/40-F filer only (foreign private issuer listing)"
        else:
            k = "no XBRL filer used the ticker"
            if str(m["last_seen"]) < "2011-07-01":
                detail["pre-XBRL blind spot (ended before 2011-07)"].append(
                    {"sid": sid, "tickers": [x[0] for x in m["tickers"]], "last_seen": str(m["last_seen"]),
                     "liquid_months": m["liquid_months"]})
        out[k] += 1
    blind = detail["pre-XBRL blind spot (ended before 2011-07)"]
    res = {"liquid_no_fundamentals_securities": len(t["nofund"]), "classification": dict(out),
           "unlinked_10K_filer_reasons": dict(sum((Counter(d["why"]) for d in detail["10-K/10-Q filer, unlinked"]),
                                                  Counter())),
           "pre_xbrl_blind_spot": {"securities": len(blind),
                                   "by_last_seen_half_year": dict(sorted(Counter(
                                       d["last_seen"][:4] + ("H1" if d["last_seen"][5:7] <= "06" else "H2")
                                       for d in blind).items())),
                                   "list": sorted(blind, key=lambda d: d["last_seen"])},
           "unlinked_10K_filer_detail": detail["10-K/10-Q filer, unlinked"]}
    (OUT / "gap_reconciliation.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if k not in ("unlinked_10K_filer_detail",)}, default=str)[:3000])
