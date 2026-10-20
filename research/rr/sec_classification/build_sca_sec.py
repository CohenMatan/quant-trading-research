"""SCA-1 (owner D267, UR-1 option A): build the SEC reference JSON for the SEC classification audit.

Independently sourced public SEC data ONLY, read from the local cache (no network, no QuantConnect output of any
kind, no identifier from an earlier QuantConnect extraction, D257):
  - data/sec_derived/xbrl_filings.json.gz : index of every XBRL filing 2009-06 .. 2021-12 from the SEC's monthly
    XBRL RSS archives (research/phase2/sec/rss_index.py): CIK, form, filing date, period, SIC, name, instance prefix;
  - data/sec_cache/data.sec.gov/api/xbrl/frames/dei/EntityPublicFloat/USD/*.json.gz : population screen;
  - data/sec_cache/data.sec.gov/api/xbrl/companyfacts/CIK*.json.gz : dei:EntityPublicFloat,
    dei:EntityCommonStockSharesOutstanding, us-gaap:Assets.

Rules (frozen with the protocol, research/rr/sec_classification/SCA_protocol.md):
  registrants : CIKs with a 10-K or 10-Q XBRL filing 2009-06 .. 2021-12, a public float >= $0.5B in some EntityPublicFloat
                frame CY2009Q1 .. CY2021Q4, a cached companyfacts file, and none of: a non-common name or SIC
                (partnership / LLC / fund / ETF / trust forms; SIC 6726, 6770, 6792, 6221), a blank-check name, an
                investment-vehicle name (TRUST / FUND under SIC 6700-6799 except REITs 6798, 6199, 6221) on any periodic filing.
  ticker evidence : each distinct instance prefix (upper case, '.', '-' removed) of the registrant's 10-K / 10-Q /
                10-K/A / 10-Q/A / 10-KT / 10-QT filings, valid from its first filing date - 100 days to its last
                filing date + 100 days (EVIDENCE, never proof: a prefix is usually but not always the ticker).
  cover shares : per periodic filing, the filing's own non-dimensional EntityCommonStockSharesOutstanding (one value;
                several different values on one cover = unknown), dated by the FILING date.
  public float : every non-dimensional EntityPublicFloat fact of a periodic filing (as-of date, value), dated by the
                filing date; dropped as a unit error if float / cover-share count is outside $0.10 .. $5,000 per share (kept if
                any cover-share count filed within 200 days of the float's filing gives a ratio in range; no test
                without one), or, when no such count exists, float > 100 x the registrant's largest total assets.
  last periodic : the registrant's last 10-K / 10-Q filing date in the index (for SEC-side exit rates).
Output: data/sec_derived/sca_sec_v1.json (plain JSON, uploaded once to the Object Store; outside Git) and its
SHA-256 + counts in research/rr/sec_classification/sca_sec_v1_manifest.json."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data/sec_cache/data.sec.gov/api/xbrl"
INDEX = ROOT / "data/sec_derived/xbrl_filings.json.gz"
OUT = ROOT / "data/sec_derived/sca_sec_v1.json"
MANIFEST = Path(__file__).with_name("sca_sec_v1_manifest.json")

PERIODIC = ("10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT")
CORE = ("10-K", "10-Q")
MIN_SCREEN_FLOAT = 5e8
TICKER_PAD = 100
FLOAT_PER_SHARE = (0.10, 5000.0)      # float / cover-share count, $ per share
FLOAT_SHARES_DAYS = 200
FLOAT_ASSETS_MAX = 100                # only when no cover-share count is available
NON_COMMON_NAME = re.compile(r"(\bL\.?\s?P\.?$|,?\s\bL\.?P\.?\b|\bLLC\b|\bL\.L\.C\.|\bFUND\b|\bPORTFOLIO\b|\bETF\b|"
                             r"\bROYALTY TRUST\b|\bGOLD TRUST\b|\bSILVER TRUST\b|\bISHARES\b|\bSPDR\b|\bPOWERSHARES\b|"
                             r"\bPROSHARES\b|\bSTATUTORY TRUST\b|\bGRANTOR TRUST\b|\bCAPITAL TRUST\b|\bTRUST [IVX]+\b|"
                             r"\bPARTNERSHIP\b)", re.I)
NON_COMMON_SIC = {6726, 6770, 6792, 6221}
SPAC = ("ACQUISITION CORP", "ACQUISITION CO", "CAPITAL ACQUISITION", "MERGER CORP")
INVESTMENT_VEHICLE = re.compile(r"\bTRUST\b|\bFUND\b", re.I)


def norm(t: str) -> str:
    return re.sub(r"[.\-\s/]", "", t or "").upper()


def load(p):
    with gzip.open(p, "rt") as f:
        return json.load(f)


def shift(iso, days):
    return (date.fromisoformat(iso) + timedelta(days=days)).isoformat()


def nondim(facts, unit):
    return [f for f in (facts or {}).get("units", {}).get(unit, []) if f.get("form") in PERIODIC]


def excluded(fl):
    names = {r["name"] or "" for r in fl}
    sics = {r["sic"] for r in fl}
    if any(NON_COMMON_NAME.search(n) for n in names) or sics & NON_COMMON_SIC:
        return "non_common"
    if any(any(s in n.upper() for s in SPAC) for n in names):
        return "blank_check"
    if any(INVESTMENT_VEHICLE.search(n) for n in names) and any(
            s and ((6700 <= s <= 6799 and s != 6798) or s in (6199, 6221)) for s in sics):
        return "investment_vehicle"
    return None


def build():
    rows = [r for r in load(INDEX) if r["form"] in PERIODIC and "2009-06-01" <= r["filed"] <= "2021-12-31"]
    by_cik = defaultdict(list)
    for r in rows:
        by_cik[r["cik"]].append(r)
    screen = defaultdict(float)
    for p in sorted((CACHE / "frames/dei/EntityPublicFloat/USD").glob("CY*.json.gz")):
        for x in load(p)["data"]:
            screen[x["cik"]] = max(screen[x["cik"]], x["val"])
    have = {int(p.name[3:13]) for p in (CACHE / "companyfacts").glob("CIK*.json.gz")}
    counts = defaultdict(int)
    out = {}
    for cik in sorted(c for c, fl in by_cik.items() if any(r["form"] in CORE for r in fl)):
        if screen.get(cik, 0.0) < MIN_SCREEN_FLOAT:
            continue
        counts["screened"] += 1
        fl = sorted(by_cik[cik], key=lambda r: (r["filed"], r["accn"]))
        why = excluded(fl)
        if why:
            counts["excluded_" + why] += 1
            continue
        if cik not in have:
            counts["excluded_no_companyfacts"] += 1
            continue
        cf = load(CACHE / f"companyfacts/CIK{cik:010d}.json.gz").get("facts", {})
        dei, gaap = cf.get("dei", {}), cf.get("us-gaap", {})
        filed_of = {r["accn"]: r["filed"] for r in fl}
        # ticker evidence
        span = {}
        for r in fl:
            t = norm(r.get("prefix"))
            if t:
                a, b = span.get(t, (r["filed"], r["filed"]))
                span[t] = (min(a, r["filed"]), max(b, r["filed"]))
        tick = sorted([t, shift(a, -TICKER_PAD), shift(b, TICKER_PAD)] for t, (a, b) in span.items())
        # cover shares, one value per filing
        per = defaultdict(set)
        for f in nondim(dei.get("EntityCommonStockSharesOutstanding"), "shares"):
            if f["accn"] in filed_of and f["val"] > 0:
                per[f["accn"]].add(float(f["val"]))
        shares = sorted([filed_of[a], v.pop()] for a, v in per.items() if len(v) == 1)
        counts["cover_ambiguous"] += sum(len(v) > 1 for v in per.values())
        # public float with unit-error filters
        tamax = max((f["val"] for f in nondim(gaap.get("Assets"), "USD") if f["val"] > 0), default=None)
        flo = set()
        for f in nondim(dei.get("EntityPublicFloat"), "USD"):
            if f["accn"] not in filed_of or not f["val"] > 0:
                continue
            v = float(f["val"])
            fd = filed_of[f["accn"]]
            near = [s for d, s in shares if abs((date.fromisoformat(d) - date.fromisoformat(fd)).days) <= FLOAT_SHARES_DAYS]
            if near and not any(FLOAT_PER_SHARE[0] <= v / s <= FLOAT_PER_SHARE[1] for s in near):
                counts["float_unit_dropped_per_share"] += 1
                continue
            if not near and tamax and v > FLOAT_ASSETS_MAX * tamax:
                counts["float_unit_dropped_assets"] += 1
                continue
            flo.add((filed_of[f["accn"]], f["end"], v))
        last = max(r["filed"] for r in fl if r["form"] in CORE)
        out[str(cik)] = dict(t=tick, s=shares, f=sorted([a, b, c] for a, b, c in flo), l=last)
        counts["registrants"] += 1
        counts["with_ticker"] += bool(tick)
        counts["with_shares"] += bool(shares)
        counts["with_float_ge_2B"] += any(v >= 2e9 for _, _, v in flo)
    meta = dict(name="sca_sec_v1", decision="D267", source="public SEC EDGAR (XBRL RSS index, companyfacts, frames)",
                index_rows=len(rows), screen_min_float=MIN_SCREEN_FLOAT, ticker_pad_days=TICKER_PAD,
                counts=dict(sorted(counts.items())))
    doc = dict(meta=meta, r=out)
    text = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    OUT.write_text(text)
    sha = hashlib.sha256(text.encode()).hexdigest()
    MANIFEST.write_text(json.dumps(dict(file=str(OUT.relative_to(ROOT)), object_store_key="rr/sca_sec_v1.json",
                                        sha256=sha, characters=len(text), meta=meta), indent=1, sort_keys=True) + "\n")
    return sha, len(text), meta


if __name__ == "__main__":
    print(build())
