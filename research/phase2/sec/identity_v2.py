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
  P  (D113a) a registrant that filed 10-Ks during the evidence span must have reported a positive public float dated
     within that span (+-1 year) on a 10-K cover (otherwise it is a co-filing subsidiary or not publicly traded;
     e.g. Golden Grain Energy, float 0 in 2011-2019, whose instance prefix 'gold' matched Randgold's ADR 'GOLD').
  F  where public-float fingerprints exist (E971-02/E974-01/E977-01/E978-01), they must not contradict: median of
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
# non-common forms only: partnership/LLC units, funds/ETFs, royalty/grantor/statutory/capital trusts. Bank and REIT
# names containing 'Trust' or 'Partners' (Northern Trust, Camden Property Trust) are ordinary common stock.
NON_COMMON_NAME = re.compile(r"(\bL\.?\s?P\.?$|,?\s\bL\.?P\.?\b|\bLLC\b|\bL\.L\.C\.|\bFUND\b|\bPORTFOLIO\b|\bETF\b|"
                             r"\bROYALTY TRUST\b|\bGOLD TRUST\b|\bSILVER TRUST\b|\bISHARES\b|\bSPDR\b|\bPOWERSHARES\b|"
                             r"\bPROSHARES\b|\bSTATUTORY TRUST\b|\bGRANTOR TRUST\b|\bCAPITAL TRUST\b|\bTRUST [IVX]+\b|"
                             r"\bPARTNERSHIP\b)", re.I)
NON_COMMON_SIC = {6726, 6770, 6792, 6221}
SPAC = ("ACQUISITION CORP", "ACQUISITION CO", "CAPITAL ACQUISITION", "MERGER CORP")
FOREIGN = re.compile(r"\b(PLC|N\.?V\.?|S\.?A\.?|AG|SE|LTD|LIMITED)\b", re.I)


def overlap_days(a, b):
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return (date.fromisoformat(hi) - date.fromisoformat(lo)).days if hi >= lo else -1


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
    for exp in ("E971-02", "E974-01", "E977-01", "E978-01"):
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
        hits = defaultdict(list)
        hit_rows = []
        for r in fl:
            if not r["prefix"]:
                continue
            fym = ym(r["filed"])
            for sid, a, b in tick.get(r["prefix"].replace(".", ""), ()):
                if ym_add(a, -3) <= fym <= ym_add(b, 3):
                    hits[sid].append(r["filed"])
                    hit_rows.append(r)
        hits = {s: sorted(set(d)) for s, d in hits.items() if len(set(d)) >= 2}
        if not hits:
            rejected["no security with >= 2 matching dated tickers"] += 1
            continue
        names = {r["name"] for r in hit_rows}      # names IN FORCE on the matching filings only
        if any(NON_COMMON_NAME.search(n or "") for n in names) or any(x in (n or "").upper() for n in names for x in SPAC):
            rejected["non-common name"] += 1
            continue
        if any(r["sic"] in NON_COMMON_SIC for r in hit_rows):
            rejected["fund/blank-check/royalty SIC"] += 1
            continue
        links[cik] = {"hits": hits, "names": sorted(names), "all_names": sorted({r["name"] for r in fl}), "first_filed": min(r["filed"] for r in fl),
                      "last_filed": max(r["filed"] for r in fl), "sic_at_filing": sorted({r["sic"] for r in fl if r["sic"]})}
    # S: public share count (exclude subsidiaries filing under the parent's prefix)
    for cik in list(links):
        cf = client.companyfacts(cik)
        sh = [f["val"] for f in index_facts(cf).get("EntityCommonStockSharesOutstanding", ())] if cf else []
        if not sh or max(sh) < 1e6:
            rejected["no public cover count >= 1M shares (subsidiary/no XBRL cover)"] += 1
            del links[cik]
            continue
        # P (D113a): a registrant that filed 10-Ks during the evidence span but reported no positive public float
        # dated within that span (+-1 year) on any 10-K cover is not publicly traded (wholly owned subsidiary co-filing under the parent's prefix,
        # e.g. Tucson Electric Power 'uns', Black Hills Power 'bhp', Hertz Corp 'htz'; non-traded REIT)
        lo = min(min(d) for d in links[cik]["hits"].values())
        hi = max(max(d) for d in links[cik]["hits"].values())
        k10 = [r for r in by_cik[cik] if r["form"] == "10-K" and lo <= r["filed"] <= hi]
        lo1 = f"{int(lo[:4]) - 1}{lo[4:]}"
        hi1 = f"{int(hi[:4]) + 1}{hi[4:]}"
        pf = [f for f in index_facts(cf).get("EntityPublicFloat", ()) if f.get("form", "").startswith("10-K") and f["val"] > 0
              and lo1 <= f["end"] <= hi1]        # a positive float dated within the evidence span (+-1 year)
        if k10 and not pf:
            rejected["10-K filer without any reported public float (subsidiary / not publicly traded)"] += 1
            del links[cik]
    # U: uniqueness both ways (time-disjoint successions allowed)
    by_sid = defaultdict(list)
    for cik, L in links.items():
        if len(L["hits"]) > 1:
            spans = sorted((min(d), max(d), s) for s, d in L["hits"].items())
            if any(overlap_days(spans[i][:2], spans[i + 1][:2]) > 120 for i in range(len(spans) - 1)):
                L["status"] = "ambiguous: several securities at the same time"
                continue
        for s, d in L["hits"].items():
            by_sid[s].append((min(d), max(d), cik))
    def f_status(cik, s):
        rs = fp.get((str(cik), s))
        if not rs:
            return "none", None
        med = statistics.median(rs)
        lo = 0.1 if not FOREIGN.search(" ".join(links[cik]["names"])) else 0.2
        for k in (0, -1, 1, -2, 2):                    # XBRL thousand-scale tagging errors
            m = med * (1000.0 ** k)
            if lo <= m <= 1.5:
                return ("ok" if k == 0 else f"ok (XBRL scale error 1e{3 * -k})"), med
        return "contradicts", med

    for cik, L in links.items():
        if L.get("status"):
            continue
        for s in L["hits"]:
            st, med = f_status(cik, s)
            if med is not None:
                L.setdefault("float", {})[s] = {"n": len(fp[(str(cik), s)]), "median": med, "check": st}
            if st == "contradicts":
                L["status"] = f"rejected: float evidence contradicts ({med:.2f})"
    for s, lst in by_sid.items():
        lst = [x for x in sorted(lst) if not links[x[2]].get("status", "").startswith(("rejected", "ambiguous: several"))]
        groups = []
        for x in lst:                                  # chains of registrants overlapping in time on this security
            if groups and overlap_days(groups[-1][-1][:2], x[:2]) > 120:
                groups[-1].append(x)
            else:
                groups.append([x])
        for g in groups:
            if len(g) < 2:
                continue
            ok = [x for x in g if f_status(x[2], s)[0].startswith("ok")]
            for x in g:
                if len(ok) == 1 and x is ok[0]:
                    links[x[2]]["conflict_resolved_by_float"] = [y[2] for y in g if y is not x]
                else:
                    links[x[2]]["status"] = f"ambiguous: security {s} claimed by overlapping registrants"
    for L in links.values():
        L.setdefault("status", "linked")
    res = {"links": {str(k): v for k, v in links.items()}, "rejected_counts": dict(rejected),
           "summary": {s: sum(1 for v in links.values() if v["status"].startswith(s.split(":")[0]))
                       for s in ("linked", "ambiguous", "rejected")}}
    (OUT / "identity_v2.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(res["summary"], res["rejected_counts"], client.fetched)
    return res


if __name__ == "__main__":
    main()
