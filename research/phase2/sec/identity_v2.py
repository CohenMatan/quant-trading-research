"""D043 identity repair, version 2 (D113): SEC-filed, dated ticker evidence.

Evidence (all historical, all from SEC filings):
  T  the registrant's XBRL instance documents are named '<ticker>-<period>.xml'; on 2,688 securities whose identity
     is known (QuantConnect vendor CIK), the prefix equals the security's QuantConnect ticker on 97.9% of 59,265
     10-K/10-Q filings. A registrant <-> security link needs >= 2 filings whose prefix EQUALS a ticker the security
     carried within +-3 months of the filing date (QuantConnect's dated ticker history, E970-01).
  U  uniqueness both ways: one security per registrant (successive SIDs allowed if time-disjoint) and one registrant
     per security at any time (holding-company successions allowed if their filing periods do not overlap).
  S  registrant files 10-K/10-Q with a public cover count >= 1,000,000 shares (excludes wholly owned subsidiaries
     that share the parent's prefix); no partnership/LLC/trust/fund name in force; SIC (as assigned at filing time)
     not a fund, blank-check or royalty-trust code.
  F  where public-float fingerprints exist (E971-02/E974-01/E977-01), they must not contradict: median of
     float / (cover shares x close) within [0.2, 1.5].
Stronger evidence overrides weaker: a v2 (ticker-evidenced) link replaces any v1 link it contradicts; v1 links that
v2 confirms are upgraded; v1 links without v2 evidence keep their v1 tier.
Output: research/phase2/sec/identity_v2.json (links, evidence, conflicts)."""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pit import index_facts  # noqa: E402
import e970_parse  # noqa: E402
import rss_index  # noqa: E402

OUT = Path(__file__).parent
NON_COMMON_NAME = re.compile(r"\b(L\.?P\.?|LLC|L\.L\.C\.|PARTNERS|PARTNERSHIP|TRUST|FUND|PORTFOLIO|ETF|ROYALTY)\b", re.I)
NON_COMMON_SIC = {6726, 6770, 6792, 6221}
SPAC = ("ACQUISITION CORP", "ACQUISITION CO", "CAPITAL ACQUISITION", "MERGER CORP")


def ym(d):
    return int(d[:4]) * 100 + int(d[5:7])


def ym_add(v, k):
    y, m = divmod(v, 100)
    m += k
    while m > 12:
        y, m = y + 1, m - 12
    while m < 1:
        y, m = y - 1, m + 12
    return y * 100 + m


def float_pairs():
    out = {}
    for exp in ("E971-02", "E974-01", "E977-01"):
        try:
            lines = e970_parse.lines(exp)
        except Exception:
            continue
        for l in lines:
            p = l.split("|")
            if p[0] == "P":
                out[(p[1], p[2])] = [float(x) for x in p[5].split(",")]
    return out


def main():
    t = e970_parse.load()
    native = {n["cik"] for n in t["native"].values() if n["cik"]}
    rows = [r for r in rss_index.load() if r["form"] in ("10-K", "10-Q", "10-K/A", "10-Q/A")
            and "2009-06-01" <= r["filed"] <= "2021-12-31"]
    by_cik = defaultdict(list)
    for r in rows:
        if r["cik"] not in native:
            by_cik[r["cik"]].append(r)
    # QuantConnect dated ticker history of securities without fundamentals
    tick = defaultdict(list)
    for sid, m in t["nofund"].items():
        for tk, a, b in m["tickers"]:
            tick[tk.replace(".", "").upper()].append((sid, a, b))
    client = SECClient()
    fp = float_pairs()
    links, rejected = {}, defaultdict(int)
    for cik, fl in by_cik.items():
        names = {r["name"] for r in fl}
        if any(NON_COMMON_NAME.search(n or "") for n in names) or any(x in (n or "").upper() for n in names for x in SPAC):
            rejected["non-common name"] += 1
            continue
        if any(r["sic"] in NON_COMMON_SIC for r in fl):
            rejected["fund/blank-check/royalty SIC"] += 1
            continue
        hits = defaultdict(list)
        for r in fl:
            if not r["prefix"]:
                continue
            fym = ym(r["filed"])
            for sid, a, b in tick.get(r["prefix"].replace(".", ""), ()):
                if ym_add(a, -3) <= fym <= ym_add(b, 3):
                    hits[sid].append(r["filed"])
        hits = {s: sorted(set(d)) for s, d in hits.items() if len(set(d)) >= 2}
        if not hits:
            rejected["no security with >= 2 matching dated tickers"] += 1
            continue
        links[cik] = {"hits": hits, "names": sorted(names), "first_filed": min(r["filed"] for r in fl),
                      "last_filed": max(r["filed"] for r in fl), "sic_at_filing": sorted({r["sic"] for r in fl if r["sic"]})}
    # S: public share count (exclude subsidiaries filing under the parent's prefix)
    for cik in list(links):
        cf = client.companyfacts(cik)
        sh = [f["val"] for f in index_facts(cf).get("EntityCommonStockSharesOutstanding", ())] if cf else []
        if not sh or max(sh) < 1e6:
            rejected["no public cover count >= 1M shares (subsidiary/no XBRL cover)"] += 1
            del links[cik]
    # U: uniqueness both ways (time-disjoint successions allowed)
    by_sid = defaultdict(list)
    for cik, L in links.items():
        if len(L["hits"]) > 1:
            spans = sorted((min(d), max(d), s) for s, d in L["hits"].items())
            if any(spans[i][1] >= spans[i + 1][0] for i in range(len(spans) - 1)):
                L["status"] = "ambiguous: several securities at the same time"
                continue
        for s, d in L["hits"].items():
            by_sid[s].append((min(d), max(d), cik))
    for s, lst in by_sid.items():
        lst.sort()
        for i in range(len(lst) - 1):
            if lst[i][1] >= lst[i + 1][0]:
                for x in (lst[i], lst[i + 1]):
                    links[x[2]]["status"] = f"ambiguous: security {s} claimed by overlapping registrants"
    # F: no contradiction from public-float fingerprints
    for cik, L in links.items():
        if L.get("status"):
            continue
        for s in L["hits"]:
            rs = fp.get((str(cik), s))
            if rs:
                med = statistics.median(rs)
                L.setdefault("float", {})[s] = {"n": len(rs), "median": med}
                if not (0.2 <= med <= 1.5):
                    L["status"] = f"rejected: float evidence contradicts ({med:.2f})"
        L.setdefault("status", "linked")
    res = {"links": {str(k): v for k, v in links.items()}, "rejected_counts": dict(rejected),
           "summary": {s: sum(1 for v in links.values() if v["status"].startswith(s.split(":")[0]))
                       for s in ("linked", "ambiguous", "rejected")}}
    (OUT / "identity_v2.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(res["summary"], res["rejected_counts"], client.fetched)
    return res


if __name__ == "__main__":
    main()
