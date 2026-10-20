"""RR4 K1 event-frequency estimate (D265 item 5B): offline, public SEC XBRL data already cached; no QuantConnect
data, no prices, no returns, no network (reads data/sec_cache only).

Purpose: an order-of-magnitude count of dividend initiations and large regular-dividend increases among large US
companies 2011-2021, to judge whether K1 can fill a 15-slot book. It is NOT the K1 signal: in QuantConnect the
signal would come from the dividend feed at the ex-date (RR4 section 4).

Rules (fixed before counting):
  population(y) : CIKs with dei:EntityPublicFloat >= $2B at a float date in year y or y-1 (frames CY..Q.I) and a
                  cached companyfacts file. Float <= market cap, so this is a subset of >= $2B companies.
                  No common-stock / financial filter (financials are in the K1 universe too).
  DPS facts     : us-gaap CommonStockDividendsPerShareDeclared, else ...CashPaid (unit USD/shares), duration
                  80-100 days (one quarter); one value per period end = the earliest filed (point-in-time).
  increase      : consecutive quarters (ends 80-100 days apart), previous DPS >= $0.02, ratio >= 1.10 / >= 1.25 /
                  >= 1.50; dated by the later quarter's end; counted if the CIK is in population(y).
  initiation    : first positive quarterly DPS of a CIK, 2012-2021 only, with >= 8 earlier quarterly
                  EarningsPerShareBasic period ends (so the company was already filing XBRL detail) and no earlier
                  positive DPS fact; counted if in population(y). Untagged payers can create false initiations:
                  an upper-side estimate.
Output: research/rr/k1k2/RR4_k1_event_frequency.json"""
from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data/sec_cache/data.sec.gov/api/xbrl"
OUT = Path(__file__).with_suffix(".json")


def load(p):
    with gzip.open(p, "rt") as f:
        return json.load(f)


def days(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def quarterly(facts, unit):
    best = {}
    for f in (facts or {}).get("units", {}).get(unit, []):
        if "start" in f and 80 <= days(f["start"], f["end"]) <= 100:
            if f["end"] not in best or f["filed"] < best[f["end"]]["filed"]:
                best[f["end"]] = f
    return {e: best[e]["val"] for e in sorted(best)}


def main():
    pop = defaultdict(set)
    for p in sorted((CACHE / "frames/dei/EntityPublicFloat/USD").glob("CY*.json.gz")):
        for x in load(p)["data"]:
            if x["val"] >= 2e9:
                y = int(x["end"][:4])
                pop[y].add(x["cik"])
                pop[y + 1].add(x["cik"])
    have = {int(p.name[3:13]) for p in (CACHE / "companyfacts").glob("CIK*.json.gz")}
    inc = {k: Counter() for k in ("10", "25", "50")}
    ini, payers, cover = Counter(), Counter(), {}
    ciks = set().union(*(pop[y] for y in range(2011, 2022))) & have
    for y in range(2011, 2022):
        cover[y] = {"population": len(pop[y]), "with_companyfacts": len(pop[y] & have)}
    for cik in sorted(ciks):
        g = load(CACHE / f"companyfacts/CIK{cik:010d}.json.gz").get("facts", {}).get("us-gaap", {})
        dps = quarterly(g.get("CommonStockDividendsPerShareDeclared"), "USD/shares") or \
            quarterly(g.get("CommonStockDividendsPerShareCashPaid"), "USD/shares")
        eps_ends = sorted(quarterly(g.get("EarningsPerShareBasic"), "USD/shares"))
        ends = sorted(dps)
        for y in range(2011, 2022):
            if cik in pop[y] and any(e[:4] == str(y) and dps[e] > 0 for e in ends):
                payers[y] += 1
        for a, b in zip(ends, ends[1:]):
            y = int(b[:4])
            if 2011 <= y <= 2021 and cik in pop[y] and 80 <= days(a, b) <= 100 and dps[a] >= 0.02:
                r = dps[b] / dps[a]
                for k, t in (("10", 1.10), ("25", 1.25), ("50", 1.50)):
                    inc[k][y] += int(r >= t)
        pos = [e for e in ends if dps[e] > 0]
        if pos:
            first = pos[0]
            y = int(first[:4])
            if 2012 <= y <= 2021 and cik in pop[y] and sum(e < first for e in eps_ends) >= 8:
                ini[y] += 1
    yrs = range(2011, 2022)
    res = {"coverage": {str(y): cover[y] for y in yrs},
           "dividend_payers_with_dps_facts": {str(y): payers[y] for y in yrs},
           "increases_ge_10pct": {str(y): inc["10"][y] for y in yrs},
           "increases_ge_25pct": {str(y): inc["25"][y] for y in yrs},
           "increases_ge_50pct": {str(y): inc["50"][y] for y in yrs},
           "initiations_2012_2021": {str(y): ini[y] for y in range(2012, 2022)}}
    for k in ("increases_ge_10pct", "increases_ge_25pct", "increases_ge_50pct"):
        res[k + "_mean"] = round(sum(res[k].values()) / len(res[k]), 1)
    res["initiations_mean"] = round(sum(ini.values()) / 10, 1)
    OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
