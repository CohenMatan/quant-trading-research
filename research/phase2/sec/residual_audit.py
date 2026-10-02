"""Residual survivorship audit after the SEC repair (D113, owner items 3/4/12/13).

Direct SEC-side measurement (no QuantConnect estimate needed): for each year 2010-2021, every registrant that filed
10-K/10-Q and reported a public float >= $2B (float <= market cap, so these are certainly >= $2B companies) at a
float date in that year or the previous one. Each registrant-year is
  native     — QuantConnect has the company with fundamentals: its CIK is a vendor CIK, or its filings' ticker
               (instance prefix) equals the ticker of a security with fundamentals at that time (successor CIKs);
  repaired   — linked to a security in the SEC correction table v2;
  missing    — neither (the residual gap; lower bound — companies with float < $2B but market cap >= $2B and
               pre-XBRL companies are not in this list and are estimated separately with the D043 method).
Missing registrants are characterised by: industry (SEC-assigned SIC at the time), financial/REIT or not, outcome
(bankruptcy 8-K item 1.03 within two years before the last equity report; ended otherwise; still filing), size
(public float), and why no match was made (identity v2 status / no QuantConnect security with that ticker).
Outcome classification is used only to characterise the residual, never to decide eligibility.
Output: research/phase2/sec/residual_audit.json"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import e970_parse  # noqa: E402
import rss_index  # noqa: E402
from identity_v2 import NON_COMMON_NAME, NON_COMMON_SIC, ym, ym_add  # noqa: E402

OUT = Path(__file__).parent


def industry(sic):
    if sic is None:
        return "unknown"
    if sic == 6798:
        return "REIT"
    if 6000 <= sic <= 6999:
        return "financial"
    return {1: "mining/energy", 2: "manufacturing", 3: "manufacturing", 4: "transport/utilities/telecom",
            5: "trade", 7: "services", 8: "services"}.get(sic // 1000, "other")


def main():
    t = e970_parse.load()
    client = SECClient()
    native_cik = {n["cik"] for n in t["native"].values() if n["cik"]}
    nat_tick = defaultdict(list)
    for sid, n in t["native"].items():
        for tk in n["tickers"]:
            nat_tick[tk.replace(".", "").upper()].append((n["first"], n["last"]))
    nof_tick = defaultdict(list)
    for sid, m in t["nofund"].items():
        for tk, a, b in m["tickers"]:
            nof_tick[tk.replace(".", "").upper()].append((a, b))
    rows = [r for r in rss_index.load() if r["form"] in ("10-K", "10-Q") and "2009-06-01" <= r["filed"] <= "2021-12-31"]
    by_cik = defaultdict(list)
    for r in rows:
        by_cik[r["cik"]].append(r)
    v2 = json.loads((OUT / "identity_v2.json").read_text())["links"]
    rep = {int(x["cik"]) for v in json.loads((OUT / "corrections_v2.json").read_text())["links"].values() for x in v}
    flo = defaultdict(dict)
    for y in range(2009, 2022):
        for q in range(1, 5):
            fr = client.frame("dei", "EntityPublicFloat", "USD", f"CY{y}Q{q}I")
            for x in fr["data"]:
                flo[x["cik"]][x["end"]] = x["val"]
    # native via the market-cap fingerprint (E971-02 'Q': SEC cover shares x close within 3% of a native security's
    # point-in-time market cap on >= 2 float dates and >= 50% of them)
    qnat = set()
    for l in e970_parse.lines("E971-02"):
        if l.startswith("Q|"):
            _, c, _sid, n, k = l.split("|")
            if int(k) >= 2 and int(k) >= 0.5 * int(n):
                qnat.add(int(c))
    shares = {}
    from qresearch.sec_pit import index_facts
    years = defaultdict(Counter)
    missing = {}
    excluded = Counter()
    for cik, obs in flo.items():
        fl = by_cik.get(cik)
        if not fl:
            continue                                # not a 10-K/10-Q XBRL filer (foreign private issuers etc.)
        names = {r["name"] for r in fl}
        if any(NON_COMMON_NAME.search(n or "") for n in names) or any(r["sic"] in NON_COMMON_SIC for r in fl):
            excluded["non-common (partnership/LLC/trust/fund name or fund/blank-check/royalty SIC)"] += 1
            continue
        if max(obs.values()) >= 1e9:               # plausibility: float per cover share within $1-$2,000
            cf = client.companyfacts(cik)
            sh = [f["val"] for f in index_facts(cf).get("EntityCommonStockSharesOutstanding", ()) if f["val"] > 0] if cf else []
            if sh:                                 # multi-class registrants report no single count: kept unchecked
                obs = {d: v for d, v in obs.items() if 1.0 <= v / max(sh) and v / min(sh) <= 2000.0}
            if not obs:
                excluded["implausible float (XBRL unit error)"] += 1
                continue
        all_pref = {r["prefix"].replace(".", "") for r in fl if r["prefix"]}
        life = (min(ym(r["filed"]) for r in fl), max(ym(r["filed"]) for r in fl))
        for y in range(2010, 2022):
            vals = [v for d, v in obs.items() if d[:4] in (str(y), str(y - 1)) and v < 5e12]   # drop unit errors
            if not vals or max(vals) < 1e9:
                continue
            band = "" if max(vals) >= 2e9 else "possible|"   # float $1-2B: market cap may exceed $2B (upper bound)
            yr = [r for r in fl if r["filed"][:4] == str(y)]
            if not yr:
                continue                            # not filing that year (ended earlier)
            if cik in native_cik:
                st = "native"
            elif any(a <= ym_add(life[1], 3) and ym_add(life[0], -3) <= b for p in all_pref for a, b in nat_tick.get(p, ())) \
                    or cik in qnat:
                st = "native (via ticker or market-cap evidence; vendor CIK is another registrant)"
            elif cik in rep:
                st = "repaired"
            else:
                st = "missing"
            sic = yr[-1]["sic"]
            ind = industry(sic)
            years[str(y)][band + st] += 1
            years[str(y)][f"{band}{st}|{'fin/REIT' if ind in ('financial', 'REIT') else 'non-financial'}"] += 1
            if st == "missing" and not band:
                m = missing.setdefault(cik, {"name": sorted(names)[0], "years": [], "sic": sic, "industry": ind,
                                             "max_float": max(v for v in obs.values() if v < 5e12)})
                m["years"].append(y)
    # characterise the missing registrants
    for cik, m in missing.items():
        sub = client.submissions(cik)
        fr = filings_table(sub) if sub else []
        per = sorted(r["filingDate"] for r in fr if r["form"] in ("10-K", "10-Q"))
        last = per[-1] if per else None
        lo = (date.fromisoformat(last) - timedelta(days=730)).isoformat() if last else "9999"
        bk = any(r["form"].startswith("8-K") and "1.03" in str(r.get("items") or "") and lo <= r["filingDate"] <= (last or "")
                 for r in fr)
        m["outcome"] = ("failed (bankruptcy 8-K)" if bk else "ended (acquired/other)" if last and last < "2022-01-01"
                        else "still filing after 2021")
        prefixes = {r["prefix"] for r in by_cik[cik] if r["prefix"]}
        in_qc = any(p.replace(".", "") in nof_tick for p in prefixes)
        L = v2.get(str(cik))
        m["why_unmatched"] = (L["status"] if L else
                              "ticker found among QuantConnect securities without fundamentals, but < 2 dated matches"
                              if in_qc else "no QuantConnect security without fundamentals carries its ticker "
                                            "(not in QuantConnect price data under that ticker, or a non-common/ADS listing)")
        m["foreign_form"] = any(x in m["name"].upper() for x in (" PLC", " N.V.", " NV", " LTD", " S.A.", " AG", " SE"))
    char = {k: dict(Counter(m[k] for m in missing.values())) for k in ("industry", "outcome", "why_unmatched", "foreign_form")}
    size = Counter("2-5B" if m["max_float"] < 5e9 else "5-20B" if m["max_float"] < 2e10 else ">20B" for m in missing.values())
    first_year = Counter(min(m["years"]) for m in missing.values())
    res = {"by_year": {y: dict(v) for y, v in sorted(years.items())}, "missing_registrants": len(missing),
           "excluded_before_classification": dict(excluded),
           "missing_characteristics": char, "missing_by_float_size": dict(size),
           "missing_by_first_missing_year": dict(sorted(first_year.items())),
           "missing_detail": {str(k): v for k, v in sorted(missing.items(), key=lambda kv: -kv[1]["max_float"])}}
    (OUT / "residual_audit.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if k != "missing_detail"}, indent=1))
