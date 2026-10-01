"""Build the SEC reference tables for X971 (D111): the verification sample, and the identity-matching candidate
pairs for the D043 survivorship repair. Public SEC data only; QuantConnect identifiers from E970-01.

Outputs
  strategies/X971_sec_verification/sec_ref*.py   packed table uploaded to QuantConnect
  research/phase2/sec/x971_sample.json            the sample (which companies and why), for the record
  research/phase2/sec/candidates.json             non-native large SEC filers and the pairs to test

Sample (deterministic, seed 20261004):
  * every company with a quarantined vendor report (accession-anomaly audit, all 213 records);
  * every company with a vendor amendment (E970: 24);
  * 80 companies with estimated filing dates (vendor date = period end + 45);
  * 150 random eligible companies (normal 10-Q / 10-K timing and values; also the market-cap method check);
  * named cases: splits (AAPL, NVDA, TSLA), multi-class (GOOGL, BRK), acquisitions (Monsanto, DirecTV),
    delayed filing (Kraft Heinz 2018 10-K), large banks/insurers (JPM, AIG), Visa.
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
from qresearch.sec_pack import pack  # noqa: E402
from qresearch.sec_pit import build_company, index_facts, period_versions  # noqa: E402
import e970_parse  # noqa: E402

SEED = 20261004
OUT = Path(__file__).parent
STRAT = ROOT / "strategies" / "X971_sec_verification"
NAMED = {320193: "split (AAPL 7:1 2014, 4:1 2020)", 1045810: "split (NVDA 2021 4:1)",
         1318605: "split (TSLA 2020 5:1)", 1652044: "multi-class (Alphabet)", 1067983: "multi-class (Berkshire)",
         1110783: "acquisition/delisting (Monsanto 2018)", 1465112: "acquisition/delisting (DirecTV 2015)",
         1637459: "delayed filing (Kraft Heinz 2018 10-K)", 19617: "bank (JPMorgan)", 5272: "insurer (AIG)",
         1403161: "Visa (dated exchange correction)", 789019: "normal (Microsoft)"}
NON_COMMON_NAME = re.compile(r"\b(L\.?P\.?|LLC|L\.L\.C\.|PARTNERS|PARTNERSHIP|TRUST|FUND|PORTFOLIO|ETF|ROYALTY)\b", re.I)
NON_COMMON_SIC = {6726, 6770, 6792, 6221}
FLOAT_WINDOW = (0.45, 1.05)


def compact(vals):
    return {k: v for k, v in vals.items() if v is not None}


def sample(t):
    rnd = random.Random(SEED)
    why = defaultdict(list)
    reps = t["reports"]
    for r in reps:
        if r["quarantined"]:
            why[r["cik"]].append("quarantined")
        if r["amendment"]:
            why[r["cik"]].append("amendment")
    est = sorted({r["cik"] for r in reps if r["estimated"]} - set(why))
    for c in rnd.sample(est, min(80, len(est))):
        why[c].append("estimated_date")
    rest = sorted({r["cik"] for r in reps} - set(why))
    for c in rnd.sample(rest, 150):
        why[c].append("random")
    for c, w in NAMED.items():
        why[c].append(w)
    return {c: sorted(set(w)) for c, w in why.items()}


def sec_refs(client, why, t):
    pes = defaultdict(set)
    sids = defaultdict(set)
    for r in t["reports"]:
        if r["cik"] in why:
            pes[r["cik"]].add(str(r["period_end"]))
            sids[r["cik"]].add(r["sid"])
    for sid, n in t["native"].items():
        if n["cik"] in why:
            sids[n["cik"]].add(sid)
    ref = {}
    for cik in sorted(why):
        cf = client.companyfacts(cik)
        sub = client.submissions(cik)
        if not cf:
            ref[str(cik)] = {"sids": sorted(sids[cik]), "why": why[cik], "records": [], "versions": {},
                             "note": "no XBRL company facts"}
            continue
        facts = index_facts(cf)
        recs = [r for r in build_company(cf, sub) if "2008-06-30" <= r["period_end"] <= "2021-12-31"]
        ref[str(cik)] = {
            "sids": sorted(sids[cik]), "why": why[cik], "name": cf.get("entityName"),
            "records": [[r["accn"], r["form"], r["filed"], r["period_end"], r["cover_date"], r["cover_shares"],
                         compact(r["values"])] for r in recs],
            "versions": {pe: [[v["accn"], v["form"], v["filed"], v["values"]] for v in period_versions(facts, pe)]
                         for pe in sorted(pes[cik]) if pe != "None"},
        }
    return ref


def equity_end(rows, facts=None):
    """Date the registrant's LISTED EQUITY ended, from its own filing history. The last periodic report with a
    cover count of at least 1 million shares marks the last equity report (an acquired company that keeps filing
    for its debt reports a nominal parent-held count); the end is the first Form 25 (delisting) or Form 15
    (deregistration) filed after it (within 400 days), else that last equity report. Returns (date, source)."""
    per = sorted(r["filingDate"] for r in rows if r["form"] in ("10-K", "10-Q"))
    if not per:
        return None, None
    last_eq = per[-1]
    if facts is not None:
        eq = sorted(f["filed"] for f in facts.get("EntityCommonStockSharesOutstanding", ())
                    if f.get("form") in ("10-K", "10-Q") and f["val"] >= 1e6)
        if eq:
            last_eq = eq[-1]
    lim = (date.fromisoformat(last_eq) + timedelta(days=400)).isoformat()
    for forms, src in ((("25-NSE", "25"), "form25"), (("15-12B", "15-12G", "15-15D", "15"), "form15")):
        ds = sorted(r["filingDate"] for r in rows if r["form"] in forms and last_eq <= r["filingDate"] <= lim)
        if ds:
            return ds[0], src
    return last_eq, "last_equity_report"


def name_on(sub, day):
    """Registrant name in force on `day` (SEC formerNames carry dated history)."""
    for fn in sub.get("formerNames") or []:
        if fn["from"][:10] <= day <= fn["to"][:10]:
            return fn["name"]
    return sub.get("name")


def candidates(client, t):
    nat = {n["cik"] for n in t["native"].values() if n["cik"]}
    big = defaultdict(list)
    for y in range(2009, 2022):
        for q in range(1, 5):
            fr = client.frame("dei", "EntityPublicFloat", "USD", f"CY{y}Q{q}I")
            for x in fr["data"]:
                big[x["cik"]].append(x)
    cands = {}
    stats = defaultdict(int)
    for cik, obs in sorted(big.items()):
        if max(o["val"] for o in obs) < 5e8 or cik in nat:
            continue
        stats["nonnative_float_ge_0.5B"] += 1
        sub = client.submissions(cik)
        cf = client.companyfacts(cik)
        if not sub or not cf:
            stats["no_sec_data"] += 1
            continue
        rows = filings_table(sub)
        forms = {r["form"] for r in rows}
        if not ({"10-K", "10-Q"} & forms):
            stats["not_10K_filer"] += 1          # 20-F / 40-F filers: foreign private issuers (ADRs etc.)
            continue
        facts = index_facts(cf)
        fl = [f for f in facts.get("EntityPublicFloat", ()) if f.get("form", "").startswith("10-K")]
        sh = [f for f in facts.get("EntityCommonStockSharesOutstanding", ())]
        flo = []
        for f in sorted(fl, key=lambda x: x["end"]):
            if not ("2009-01-01" <= f["end"] <= "2021-12-31"):
                continue
            near = [s for s in sh if abs((date.fromisoformat(s["end"]) - date.fromisoformat(f["end"])).days) <= 100]
            if not near:
                continue
            s = min(near, key=lambda s: abs((date.fromisoformat(s["end"]) - date.fromisoformat(f["end"])).days))
            vals = {x["val"] for x in sh if x["accn"] == s["accn"]}
            if len(vals) > 1:
                continue                          # several cover values in one filing: class split, ambiguous
            flo.append([f["end"], float(f["val"]), float(s["val"]), s["end"]])
        end, src = equity_end(rows, facts)
        names = sorted({name_on(sub, o[0]) for o in flo} | {sub.get("name")})
        nonc = any(NON_COMMON_NAME.search(n or "") for n in names)
        try:
            sic = int(sub.get("sic") or 0)
        except ValueError:
            sic = 0
        cands[str(cik)] = {"name": sub.get("name"), "names": names, "sic": sic, "end": end, "end_source": src,
                           "float_obs": flo, "non_common_name": nonc, "non_common_sic": sic in NON_COMMON_SIC,
                           "first_periodic": min((r["filingDate"] for r in rows if r["form"] in ("10-K", "10-Q")),
                                                 default=None)}
        stats["candidate_10K_filers"] += 1
    return cands, dict(stats)


def pairs(cands, t):
    """Candidate (security, filer) pairs to test on QuantConnect: the security was liquid at some float date of
    the filer, and its trading ended near the filer's equity end (registrants whose equity is still listed after
    2021 are not the D043 population; they get the native-coverage check only)."""
    out = defaultdict(list)
    for cik, c in cands.items():
        if not c["float_obs"]:
            continue
        months = {int(o[0][:4]) * 100 + int(o[0][5:7]) for o in c["float_obs"]}
        end = date.fromisoformat(c["end"]) if c["end"] else None
        if end is None or end >= date(2021, 10, 1):
            continue        # equity still listed after 2021: not the D043 population (checked for native cover, Q)
        for sid, m in t["nofund"].items():
            ls = m["last_seen"]
            if not any(m["first_ym"] <= ym <= m["last_ym"] for ym in months):
                continue
            if not (end - timedelta(days=45) <= ls <= end + timedelta(days=200)):
                continue
            out[cik].append(sid)
    return dict(out)


def main():
    t = e970_parse.load()
    client = SECClient()
    why = sample(t)
    ref = sec_refs(client, why, t)
    cands, cstats = candidates(client, t)
    pr = pairs(cands, t)
    fobs = {cik: c["float_obs"] for cik, c in cands.items() if c["float_obs"]}
    table = {"sample": ref, "float_obs": fobs, "pairs": pr}
    for p in STRAT.glob("sec_ref*.py"):
        p.unlink()
    for name, text in pack(table, "sec_ref").items():
        (STRAT / name).write_text(text)
    (OUT / "x971_sample.json").write_text(json.dumps(
        {str(c): {"why": v["why"], "name": v.get("name"), "sids": v["sids"], "n_records": len(v["records"])}
         for c, v in ref.items()}, indent=1, sort_keys=True) + "\n")
    (OUT / "candidates.json").write_text(json.dumps({"stats": cstats, "candidates": cands, "pairs": pr},
                                                    indent=1, sort_keys=True) + "\n")
    print(len(ref), cstats, sum(len(v) for v in pr.values()), "pairs over", len(pr), "filers", client.fetched)


if __name__ == "__main__":
    main()
