"""OD-1 (owner D308): build the fundamental EXTENSION object rr/od1_sec_v1.json from the local public SEC cache.

Same registrant set (CIKs) as the UCR-1 object `rr/ucr_sec_v1.json`, which is NOT modified. No network, no
QuantConnect data, no new source: the XBRL RSS filing index and companyfacts already cached for UCR-1 / H032.

Per registrant, one row per ORIGINAL periodic filing (forms 10-K, 10-KT, 10-Q, 10-QT; amendments excluded) FILED
2010-01-01 .. 2021-12-31 (nothing filed before 2010 is used: owner D308), in filing order:
    [filed, kind, period_end, rev, rev_py, ni, ni_py, gp, gp_py, ocf, ta, ta_py, eq, eq_py]
kind = 'K' (10-K / 10-KT) or 'Q' (10-Q / 10-QT). Values come ONLY from facts carrying that filing's accession number
(as filed). Flows: 'K' annual facts (duration 350-380 days), 'Q' three-month facts (80-100 days), ending within 7
days of period_end; *_py = the same tag's same-duration comparative in the same filing ending 355-375 days earlier.
For each flow the FIRST tag (qresearch.sec_pit.TAGS order) that reports both current and comparative is used; if no
tag has both, the first tag's current value is kept and *_py is null. gp falls back to rev - cost of revenue (same
filing, first cost tag with both values) when GrossProfit is absent. ocf: 'K' only (10-Q cash flows are
year-to-date). Stocks (ta, eq): instant facts at period_end (+-7 days); *_py for 'K' at the prior fiscal year-end
(355-375 days earlier), null for 'Q'. Several different values for one (tag, filing, end, duration) -> null.

    PYTHONPATH=src python research/od/build_od1_sec.py
Output: data/sec_derived/od1_sec_v1.json (outside Git) and research/od/od1_sec_v1_manifest.json.
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
OUT = ROOT / "data/sec_derived/od1_sec_v1.json"
MANIFEST = Path(__file__).with_name("od1_sec_v1_manifest.json")
OBJECT_KEY = "rr/od1_sec_v1.json"

FORMS = {"10-K": "K", "10-KT": "K", "10-Q": "Q", "10-QT": "Q"}
FILED_FROM, FILED_TO = "2010-01-01", "2021-12-31"
DUR = {"K": (350, 380), "Q": (80, 100)}
END_TOL = 7
PRIOR = (355, 375)
FIELDS = ("filed", "kind", "period_end", "rev", "rev_py", "ni", "ni_py", "gp", "gp_py", "ocf", "ta", "ta_py",
          "eq", "eq_py")


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


def usd(cf, tag):
    return ((cf.get("facts", {}).get("us-gaap") or {}).get(tag) or {}).get("units", {}).get("USD") or []


def value(facts, accn, end_lo, end_hi, dur=None):
    """The single value of `facts` in filing `accn` ending in [end_lo, end_hi]: a flow of duration `dur` (days range)
    or, with dur None, an instant. None if absent; 'AMB' if several different values."""
    vals = set()
    for f in facts:
        if f.get("accn") != accn:
            continue
        e = d(f["end"])
        if not end_lo <= e <= end_hi:
            continue
        if dur is None:
            if "start" in f:
                continue
        else:
            if "start" not in f:
                continue
            n = (e - d(f["start"])).days
            if not dur[0] <= n <= dur[1]:
                continue
        v = float(f["val"])
        vals.add(int(v) if v.is_integer() else v)
    if not vals:
        return None
    return vals.pop() if len(vals) == 1 else "AMB"


def windows(pe):
    e = d(pe)
    cur = (date.fromordinal(e.toordinal() - END_TOL), date.fromordinal(e.toordinal() + END_TOL))
    pri = (date.fromordinal(e.toordinal() - PRIOR[1]), date.fromordinal(e.toordinal() - PRIOR[0]))
    return cur, pri


def flow_pair(cf, tags, accn, cur, pri, dur):
    """(current, prior) from the first tag with both; else (first tag's current, None)."""
    first = None
    for tag in tags:
        facts = usd(cf, tag)
        c = value(facts, accn, *cur, dur)
        if c is None:
            continue
        if first is None:
            first = c
        p = value(facts, accn, *pri, dur)
        if p is not None and c != "AMB" and p != "AMB":
            return c, p
    return (None if first == "AMB" else first), None


def stock_pair(cf, tags, accn, cur, pri, want_prior):
    for tag in tags:
        facts = usd(cf, tag)
        c = value(facts, accn, *cur)
        if c is None or c == "AMB":
            continue
        p = value(facts, accn, *pri) if want_prior else None
        return c, (None if p == "AMB" else p)
    return None, None


def row(cf, r, counts):
    kind = FORMS[r["form"]]
    pe = period_iso(r.get("period"))
    out = dict.fromkeys(FIELDS)
    out.update(filed=r["filed"], kind=kind, period_end=pe)
    if pe is None:
        counts["no_period"] += 1
        return [out[k] for k in FIELDS]
    cur, pri = windows(pe)
    dur, acc = DUR[kind], r["accn"]
    out["rev"], out["rev_py"] = flow_pair(cf, TAGS["revenue"], acc, cur, pri, dur)
    out["ni"], out["ni_py"] = flow_pair(cf, TAGS["net_income"], acc, cur, pri, dur)
    out["gp"], out["gp_py"] = flow_pair(cf, TAGS["gross_profit"], acc, cur, pri, dur)
    if out["gp"] is None and out["rev"] is not None:
        c, p = flow_pair(cf, TAGS["cost_of_revenue"], acc, cur, pri, dur)
        if c is not None:
            out["gp"] = out["rev"] - c
            out["gp_py"] = out["rev_py"] - p if (p is not None and out["rev_py"] is not None) else None
            counts["gp_from_cost"] += 1
    if kind == "K":
        o, _ = flow_pair(cf, TAGS["operating_cash_flow"], acc, cur, pri, dur)
        out["ocf"] = o
    out["ta"], out["ta_py"] = stock_pair(cf, TAGS["total_assets"], acc, cur, pri, kind == "K")
    out["eq"], out["eq_py"] = stock_pair(cf, TAGS["stockholders_equity"], acc, cur, pri, kind == "K")
    for k in ("rev", "rev_py", "ni", "ni_py", "gp", "gp_py", "ocf", "ta", "ta_py", "eq", "eq_py"):
        if out[k] is not None:
            counts[f"{kind}_{k}"] += 1
    counts[f"rows_{kind}"] += 1
    return [out[k] for k in FIELDS]


def build():
    parent_text = PARENT.read_text()
    parent_sha = hashlib.sha256(parent_text.encode()).hexdigest()
    if parent_sha != json.loads(PARENT_MANIFEST.read_text())["sha256"]:
        raise SystemExit("the local UCR-1 object is not the manifest's object")
    ciks = sorted(json.loads(parent_text)["r"], key=int)
    rows = [r for r in json.load(gzip.open(INDEX, "rt"))
            if r["form"] in FORMS and FILED_FROM <= r["filed"] <= FILED_TO]
    by_cik = defaultdict(list)
    for r in rows:
        by_cik[str(r["cik"])].append(r)
    counts = defaultdict(int)
    out = {}
    for cik in ciks:
        fl = sorted(by_cik.get(cik, []), key=lambda r: (r["filed"], r["accn"]))
        p = CACHE / f"CIK{int(cik):010d}.json.gz"
        if not fl or not p.exists():
            counts["registrants_without_rows" if not fl else "registrants_without_companyfacts"] += 1
            out[cik] = []
            continue
        cf = json.load(gzip.open(p, "rt"))
        out[cik] = [row(cf, r, counts) for r in fl]
        counts["registrants"] += 1
    meta = dict(name="od1_sec_v1", decision="D308", parent="ucr_sec_v1", parent_sha256=parent_sha, fields=list(FIELDS),
                source="public SEC EDGAR (XBRL RSS index, companyfacts); same cache as UCR-1 / H032",
                rules=dict(forms=FORMS, filed=[FILED_FROM, FILED_TO], duration_days=DUR, end_tolerance_days=END_TOL,
                           prior_end_days_before=list(PRIOR), tags={k: list(v) for k, v in TAGS.items()}),
                counts=dict(sorted(counts.items())))
    text = json.dumps(dict(meta=meta, r=out), sort_keys=True, separators=(",", ":"))
    OUT.write_text(text)
    sha = hashlib.sha256(text.encode()).hexdigest()
    MANIFEST.write_text(json.dumps(dict(file=str(OUT.relative_to(ROOT)), object_store_key=OBJECT_KEY, sha256=sha,
                                        characters=len(text), meta=meta), indent=1, sort_keys=True) + "\n")
    return sha, len(text), meta


if __name__ == "__main__":
    sha, n, meta = build()
    print(sha, n)
    print(json.dumps(meta["counts"], indent=1))
