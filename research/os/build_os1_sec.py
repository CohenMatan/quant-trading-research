"""OS-1 / H032 (owner D278 item 6): build the EXTENSION object for the UCR-1 per-filing SEC object.

The original object `rr/ucr_sec_v1.json` (SHA-256 ba3ab515…, research/rr/universe_repair/ucr_sec_v1_manifest.json) is
NOT modified. This builder writes a separate, smaller plain-JSON object with only the H032 additions, from the same
local public SEC cache (XBRL RSS filing index, companyfacts); no network, no QuantConnect data, no new source.

Per registrant of the UCR-1 object (same CIK set):
  s : SIC of each periodic filing, PARALLEL to the UCR-1 `p` list (same rows, same order: filed in 2009-06-01 ..
      2021-12-31, forms 10-K / 10-Q / 10-K/A / 10-Q/A / 10-KT / 10-QT, sorted by filing date and accession). At a
      decision day t the point-in-time SIC is the SIC of the latest periodic filing filed before t (the same filing
      whose prefix gives the UCR-1 identity). null if the index carries none.
  k : one row per ORIGINAL annual report (form 10-K or 10-KT; amendments excluded), in filing order:
      [filed, period_end, ocf, rev, rev_prior]
      period_end = the filing's reporting period (index 'period'); null row values if it is missing.
      Values come ONLY from facts carrying that filing's accession number (as filed in that 10-K):
        ocf       first tag of (NetCashProvidedByUsedInOperatingActivities,
                  NetCashProvidedByUsedInOperatingActivitiesContinuingOperations) with an annual fact
                  (duration 350-380 days) ending within 7 days of period_end;
        rev, rev_prior   the FIRST revenue tag of qresearch.sec_pit.TAGS['revenue'] (frozen order) that reports, in
                  this same filing, BOTH the current annual value (ending within 7 days of period_end) and the prior-
                  year annual comparative (ending 355-375 days before period_end) -> both from that one tag;
                  if no tag has both: rev = the first tag's current value (diagnostic only), rev_prior = null.
      Several different values for one (tag, filing, end, duration) -> ambiguous -> null.
Output: data/sec_derived/os1_sec_v1.json (outside Git; uploaded once on approval) and
research/os/os1_sec_v1_manifest.json (SHA-256, counts, the parent object's SHA-256).

    PYTHONPATH=src python research/os/build_os1_sec.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch.sec_pit import TAGS  # noqa: E402

CACHE = ROOT / "data/sec_cache/data.sec.gov/api/xbrl/companyfacts"
INDEX = ROOT / "data/sec_derived/xbrl_filings.json.gz"
PARENT = ROOT / "data/sec_derived/ucr_sec_v1.json"
PARENT_MANIFEST = ROOT / "research/rr/universe_repair/ucr_sec_v1_manifest.json"
OUT = ROOT / "data/sec_derived/os1_sec_v1.json"
MANIFEST = Path(__file__).with_name("os1_sec_v1_manifest.json")
OBJECT_KEY = "rr/os1_sec_v1.json"

PERIODIC = ("10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-QT")
ANNUAL = ("10-K", "10-KT")
OCF_TAGS = ("NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations")
REV_TAGS = tuple(TAGS["revenue"])
DUR = (350, 380)
END_TOL = 7
PRIOR = (355, 375)


def d(s):
    return date.fromisoformat(s)


def period_iso(p):
    p = str(p or "")
    if len(p) != 8 or not p.isdigit():
        return None
    try:
        return date(int(p[:4]), int(p[4:6]), int(p[6:])).isoformat()
    except ValueError:
        return None


def annual_value(facts, accn, end_lo, end_hi):
    """The single annual value (duration 350-380 days) of `facts` in filing `accn` ending in [end_lo, end_hi];
    None if absent, 'AMB' if several different values."""
    vals = set()
    for f in facts:
        if f.get("accn") != accn or "start" not in f:
            continue
        n = (d(f["end"]) - d(f["start"])).days
        if DUR[0] <= n <= DUR[1] and end_lo <= d(f["end"]) <= end_hi:
            vals.add(float(f["val"]))
    if not vals:
        return None
    return vals.pop() if len(vals) == 1 else "AMB"


def usd(cf, tag):
    return ((cf.get("facts", {}).get("us-gaap") or {}).get(tag) or {}).get("units", {}).get("USD") or []


def annual_row(cf, r, counts):
    pe = period_iso(r.get("period"))
    if pe is None:
        counts["annual_no_period"] += 1
        return [r["filed"], None, None, None, None]
    e = d(pe)
    lo, hi = date.fromordinal(e.toordinal() - END_TOL), date.fromordinal(e.toordinal() + END_TOL)
    plo, phi = date.fromordinal(e.toordinal() - PRIOR[1]), date.fromordinal(e.toordinal() - PRIOR[0])
    ocf = None
    for tag in OCF_TAGS:
        v = annual_value(usd(cf, tag), r["accn"], lo, hi)
        if v is not None:
            ocf = v
            break
    if ocf == "AMB":
        counts["ocf_ambiguous"] += 1
        ocf = None
    rev = prior = None
    first_cur = None
    for tag in REV_TAGS:
        facts = usd(cf, tag)
        cur = annual_value(facts, r["accn"], lo, hi)
        if cur is None:
            continue
        if first_cur is None:
            first_cur = cur
        pri = annual_value(facts, r["accn"], plo, phi)
        if pri is not None and cur != "AMB" and pri != "AMB":
            rev, prior = cur, pri
            break
    if rev is None:
        rev = None if first_cur in (None, "AMB") else first_cur
        counts["rev_no_same_filing_comparative"] += 1
    counts["annual_rows"] += 1
    counts["annual_with_ocf"] += int(ocf is not None)
    counts["annual_with_rev_and_prior"] += int(prior is not None)
    return [r["filed"], pe, ocf, rev, prior]


def build():
    parent_text = PARENT.read_text()
    parent_sha = hashlib.sha256(parent_text.encode()).hexdigest()
    pm = json.loads(PARENT_MANIFEST.read_text())
    if parent_sha != pm["sha256"]:
        raise SystemExit("the local UCR-1 object is not the manifest's object")
    parent = json.loads(parent_text)["r"]
    rows = [r for r in json.load(gzip.open(INDEX, "rt")) if r["form"] in PERIODIC
            and "2009-06-01" <= r["filed"] <= "2021-12-31"]
    by_cik = defaultdict(list)
    for r in rows:
        by_cik[str(r["cik"])].append(r)
    counts = defaultdict(int)
    out = {}
    for cik, rec in sorted(parent.items(), key=lambda kv: int(kv[0])):
        fl = sorted(by_cik[cik], key=lambda r: (r["filed"], r["accn"]))
        if len(fl) != len(rec["p"]) or any(a["filed"] != p[0] for a, p in zip(fl, rec["p"])):
            raise SystemExit(f"CIK {cik}: index rows do not align with the UCR-1 'p' list")
        sic = [r.get("sic") for r in fl]
        counts["sic_missing"] += sum(1 for s in sic if s is None)
        cf = json.load(gzip.open(CACHE / f"CIK{int(cik):010d}.json.gz", "rt"))
        k = [annual_row(cf, r, counts) for r in fl if r["form"] in ANNUAL]
        out[cik] = dict(s=sic, k=k)
        counts["registrants"] += 1
    meta = dict(name="os1_sec_v1", decision="D278", parent="ucr_sec_v1", parent_sha256=parent_sha,
                source="public SEC EDGAR (XBRL RSS index, companyfacts); same cache as UCR-1; H032 additions only",
                rules=dict(annual_forms=list(ANNUAL), duration_days=list(DUR), end_tolerance_days=END_TOL,
                           prior_end_days_before=list(PRIOR), ocf_tags=list(OCF_TAGS), revenue_tags=list(REV_TAGS)),
                counts=dict(sorted(counts.items())))
    text = json.dumps(dict(meta=meta, r=out), sort_keys=True, separators=(",", ":"))
    OUT.write_text(text)
    sha = hashlib.sha256(text.encode()).hexdigest()
    MANIFEST.write_text(json.dumps(dict(file=str(OUT.relative_to(ROOT)), object_store_key=OBJECT_KEY, sha256=sha,
                                        characters=len(text), meta=meta), indent=1, sort_keys=True) + "\n")
    return sha, len(text), meta


if __name__ == "__main__":
    print(json.dumps(build()[2]["counts"], indent=1))
