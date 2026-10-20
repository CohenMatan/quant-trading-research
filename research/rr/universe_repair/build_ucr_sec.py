"""UCR-1 (owner D269, UR-2 option A): build the POINT-IN-TIME SEC reference for the narrow SEC-based universe repair.

Same independently sourced public SEC data as SCA-1 (local cache only: XBRL RSS filing index, companyfacts), NO new
source, no network, no QuantConnect output. Unlike the SCA-1 measurement object (sca_sec_v1.json: retrospective ticker
windows, whole-history exclusions), every record here is a single periodic filing and carries only what that filing
made public on its filing date, so the in-cloud rule can use exactly the filings filed before each decision day:

  per registrant (CIK):
    p : periodic filings (10-K, 10-Q, 10-K/A, 10-Q/A, 10-KT, 10-QT) in filing-date order, each
        [filed, prefix, common_ok, shares, cover_end]
        prefix    = the filing's XBRL instance prefix (upper case, '.', '-', '/', ' ' removed; '' if none)
        common_ok = 1 unless THAT filing's company name or assigned SIC marks a partnership / LLC / fund / ETF / trust
                    form, a blank-check company, or an investment-vehicle trust (SCA-1 rules, REITs 6798 kept)
        shares    = the filing's own non-dimensional EntityCommonStockSharesOutstanding when exactly one value is
                    reported (several values = multi-class / ambiguous -> null)
        cover_end = that value's as-of date (null with shares)
    f : public float facts [filed, as_of, value] from periodic filings, kept only if plausible with information known
        at that filing: float / cover shares in $0.10 .. $5,000 per share, using the same filing's shares or else the
        latest EARLIER filing's shares filed within 200 days; with no such count, float <= 100 x the largest total
        assets reported in filings filed on or before it.
  population: periodic XBRL filers with a cached companyfacts file and at least one float fact >= $0.5B (any date).
              The in-cloud rule requires a point-in-time float >= $0.5B, which implies membership, so the screen adds
              no look-ahead.
Output: data/sec_derived/ucr_sec_v1.json (outside Git; plain JSON uploaded once to the Object Store) and
research/rr/universe_repair/ucr_sec_v1_manifest.json (SHA-256, counts)."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data/sec_cache/data.sec.gov/api/xbrl"
INDEX = ROOT / "data/sec_derived/xbrl_filings.json.gz"
OUT = ROOT / "data/sec_derived/ucr_sec_v1.json"
MANIFEST = Path(__file__).with_name("ucr_sec_v1_manifest.json")

PERIODIC = ("10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT")
CORE = ("10-K", "10-Q")
MIN_POP_FLOAT = 5e8
FLOAT_PER_SHARE = (0.10, 5000.0)
FLOAT_SHARES_DAYS = 200
FLOAT_ASSETS_MAX = 100
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


def days(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def common_ok(name, sic):
    """The SCA-1 exclusion rules applied to ONE filing's name and SIC (no other filing)."""
    name = name or ""
    if NON_COMMON_NAME.search(name) or sic in NON_COMMON_SIC:
        return 0
    if any(s in name.upper() for s in SPAC):
        return 0
    if INVESTMENT_VEHICLE.search(name) and sic and ((6700 <= sic <= 6799 and sic != 6798) or sic in (6199, 6221)):
        return 0
    return 1


def nondim(facts, unit):
    return [f for f in (facts or {}).get("units", {}).get(unit, []) if f.get("form") in PERIODIC]


def registrant(fl, cf):
    dei, gaap = cf.get("dei", {}), cf.get("us-gaap", {})
    filed_of = {r["accn"]: r["filed"] for r in fl}
    per = defaultdict(set)
    for f in nondim(dei.get("EntityCommonStockSharesOutstanding"), "shares"):
        if f["accn"] in filed_of and f["val"] > 0:
            per[f["accn"]].add((float(f["val"]), f["end"]))
    filings = []
    for r in fl:
        vals = per.get(r["accn"], set())
        one = len({v for v, _ in vals}) == 1
        sh, ce = (sorted(vals)[0] if one else (None, None))
        filings.append([r["filed"], norm(r.get("prefix")), common_ok(r.get("name"), r.get("sic")), sh, ce])
    assets = sorted((filed_of[f["accn"]], f["val"]) for f in nondim(gaap.get("Assets"), "USD")
                    if f["accn"] in filed_of and f["val"] > 0)
    floats, dropped = [], 0
    for f in nondim(dei.get("EntityPublicFloat"), "USD"):
        if f["accn"] not in filed_of or not f["val"] > 0:
            continue
        v, fd = float(f["val"]), filed_of[f["accn"]]
        own = [s for s, _ in per.get(f["accn"], set())]
        if len(set(own)) == 1:
            ref = own[0]
        else:
            ref = next((p[3] for p in reversed(filings) if p[0] < fd and p[3] is not None
                        and days(p[0], fd) <= FLOAT_SHARES_DAYS), None)
        if ref is not None:
            ok = FLOAT_PER_SHARE[0] <= v / ref <= FLOAT_PER_SHARE[1]
        else:
            ta = max((a for d, a in assets if d <= fd), default=None)
            ok = ta is None or v <= FLOAT_ASSETS_MAX * ta
        if ok:
            floats.append([fd, f["end"], v])
        else:
            dropped += 1
    return filings, sorted(floats), dropped


def build():
    rows = [r for r in load(INDEX) if r["form"] in PERIODIC and "2009-06-01" <= r["filed"] <= "2021-12-31"]
    by_cik = defaultdict(list)
    for r in rows:
        by_cik[r["cik"]].append(r)
    have = {int(p.name[3:13]) for p in (CACHE / "companyfacts").glob("CIK*.json.gz")}
    counts = defaultdict(int)
    out = {}
    for cik in sorted(c for c, fl in by_cik.items() if c in have and any(r["form"] in CORE for r in fl)):
        cf = load(CACHE / f"companyfacts/CIK{cik:010d}.json.gz").get("facts", {})
        flo = [f["val"] for f in nondim(cf.get("dei", {}).get("EntityPublicFloat"), "USD")]
        if not flo or max(flo) < MIN_POP_FLOAT:
            continue
        fl = sorted(by_cik[cik], key=lambda r: (r["filed"], r["accn"]))
        filings, floats, dropped = registrant(fl, cf)
        counts["float_unit_dropped"] += dropped
        if not any(v >= MIN_POP_FLOAT for _, _, v in floats):
            counts["no_plausible_float_ge_0.5B"] += 1
            continue
        out[str(cik)] = dict(p=filings, f=floats)
        counts["registrants"] += 1
        counts["filings"] += len(filings)
        counts["filings_not_common"] += sum(1 for p in filings if not p[2])
        counts["filings_with_single_shares"] += sum(1 for p in filings if p[3] is not None)
    meta = dict(name="ucr_sec_v1", decision="D269", source="public SEC EDGAR (XBRL RSS index, companyfacts); same "
                "cache as SCA-1, point-in-time per-filing layout", population_min_float=MIN_POP_FLOAT,
                counts=dict(sorted(counts.items())))
    text = json.dumps(dict(meta=meta, r=out), sort_keys=True, separators=(",", ":"))
    OUT.write_text(text)
    sha = hashlib.sha256(text.encode()).hexdigest()
    MANIFEST.write_text(json.dumps(dict(file=str(OUT.relative_to(ROOT)), object_store_key="rr/ucr_sec_v1.json",
                                        sha256=sha, characters=len(text), meta=meta), indent=1, sort_keys=True) + "\n")
    return sha, len(text), meta


if __name__ == "__main__":
    print(build())
