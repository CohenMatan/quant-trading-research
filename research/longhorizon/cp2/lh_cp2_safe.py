"""LH-CP2 (owner D243): cut-off-enforcing loaders for offline SEC metadata. Every record dated after 2021-12-31
(filing date, report / period date, fact end or start date) is dropped INSIDE the loader, before any caller can see
it; the raw cached objects never leave this module. Cache-only (networking disabled)."""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CUT = "2021-12-31"
_DATE = re.compile(r"(19|20)\d\d-\d\d-\d\d")


class _NoNet:
    def get(self, *a, **k):
        raise RuntimeError("network disabled (LH-CP2 is offline / cache-only)")


def client():
    from qresearch.sec_edgar import SECClient
    return SECClient(cache_dir=ROOT / "data/sec_cache", user_agent="offline-audit", session=_NoNet())


def _ok(*dates) -> bool:
    return all((not d) or str(d)[:10] <= CUT for d in dates)


def filter_companyfacts(cf):
    """New dict with only facts whose filed, end and start dates are <= CUT (units kept; nothing else copied)."""
    out = {"facts": {}}
    for tax, tags in ((cf or {}).get("facts") or {}).items():
        for tag, body in tags.items():
            units = {}
            for u, facts in (body.get("units") or {}).items():
                keep = [dict(f) for f in facts if f.get("filed") and _ok(f.get("filed"), f.get("end"), f.get("start"))]
                if keep:
                    units[u] = keep
            if units:
                out["facts"].setdefault(tax, {})[tag] = {"units": units}
    return out


def companyfacts(c, cik):
    try:
        cf = c.companyfacts(int(cik))
    except RuntimeError:
        return None
    return None if cf is None else filter_companyfacts(cf)


def filter_submission_rows(rows):
    """Submissions rows (filings_table dicts) with filingDate <= CUT and reportDate (if any) <= CUT."""
    return [dict(r) for r in rows if r.get("filingDate") and _ok(r.get("filingDate"), r.get("reportDate"))]


def submissions(c, cik):
    from qresearch.sec_edgar import filings_table
    try:
        sub = c.submissions(int(cik))
    except RuntimeError:
        return None
    return None if sub is None else filter_submission_rows(filings_table(sub))


def xbrl_filings():
    """The SEC XBRL filing index, filed and period <= CUT."""
    xb = json.load(gzip.open(ROOT / "data/sec_derived/xbrl_filings.json.gz"))
    out = []
    for r in xb:
        p = r.get("period") or ""
        pd = f"{p[:4]}-{p[4:6]}-{p[6:8]}" if len(p) == 8 else ""
        if r.get("filed") and _ok(r["filed"], pd):
            out.append(dict(r))
    return out


def assert_no_post_cutoff(obj):
    """Raise if any ISO date string after CUT appears anywhere in obj (outputs, examples)."""
    bad = [m.group(0) for m in (_DATE.search(s) for s in _strings(obj)) if m and m.group(0) > CUT]
    if bad:
        raise AssertionError(f"post-cut-off date in output: {bad[:3]}")


def _strings(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield str(k)
            yield from _strings(v)
    elif isinstance(o, (list, tuple, set)):
        for v in o:
            yield from _strings(v)
    elif isinstance(o, str):
        yield o
