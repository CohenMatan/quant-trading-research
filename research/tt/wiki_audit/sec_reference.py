"""Independent SEC reference frame for the WIKI Prices audit (D298; protocol WIKI_AUDIT_protocol.md section 2).

Cache-only: reads data/sec_cache (XBRL public-float frames, submissions) and data/sec_derived/xbrl_filings.json.gz.
It never fetches from the network and uses no QuantConnect and no WIKI data.

Outputs
  data/wiki_audit/sec_frame.json.gz              registrant-month rows (public SEC-derived; git-ignored)
  research/tt/wiki_audit/SEC_REFERENCE_summary.json  aggregates only (committed)

Point-in-time rule (protocol 2.2): a filing counts for month m only if filed on or before the last calendar day of
the previous month. That is never later than "before m's first session", so it never uses information that was
not yet public.
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "phase2" / "sec"))

SEC_CACHE = ROOT / "data" / "sec_cache" / "data.sec.gov"
FILINGS = ROOT / "data" / "sec_derived" / "xbrl_filings.json.gz"
FRAME_OUT = ROOT / "data" / "wiki_audit" / "sec_frame.json.gz"
SUMMARY_OUT = Path(__file__).parent / "SEC_REFERENCE_summary.json"

FLOAT_MIN = 2_000_000_000
K_FORMS = {"10-K", "10-K405", "10-KT"}
PERIODIC = {"10-K", "10-Q", "10-K/A", "10-Q/A", "10-K405", "10-KT"}
NON_COMMON_SIC = {6726, 6770, 6792, 6221}
# identity_v2.NON_COMMON_NAME / FOREIGN, copied verbatim (importing identity_v2 pulls in unrelated QuantConnect parsers)
NON_COMMON_NAME = re.compile(r"(\bL\.?\s?P\.?$|,?\s\bL\.?P\.?\b|\bLLC\b|\bL\.L\.C\.|\bFUND\b|\bPORTFOLIO\b|\bETF\b|"
                             r"\bROYALTY TRUST\b|\bGOLD TRUST\b|\bSILVER TRUST\b|\bISHARES\b|\bSPDR\b|\bPOWERSHARES\b|"
                             r"\bPROSHARES\b|\bSTATUTORY TRUST\b|\bGRANTOR TRUST\b|\bCAPITAL TRUST\b|\bTRUST [IVX]+\b|"
                             r"\bPARTNERSHIP\b)", re.I)
FOREIGN = re.compile(r"\b(PLC|N\.?V\.?|S\.?A\.?|AG|SE|LTD|LIMITED)\b", re.I)
ACQ_FORMS = {"DEFM14A", "DEFM14C", "PREM14A", "SC 14D9", "SC TO-T", "425"}
MONTHS = [y * 100 + m for y in range(2010, 2018) for m in range(1, 13)]


def ym(d: str) -> int:
    return int(d[:4]) * 100 + int(d[5:7])


def ym_add(v: int, k: int) -> int:
    y, m = divmod(v, 100)
    t = y * 12 + (m - 1) + k
    return (t // 12) * 100 + t % 12 + 1


def months_between(a: int, b: int) -> int:
    return (b // 100 - a // 100) * 12 + (b % 100 - a % 100)


def load_floats() -> dict:
    """accession -> (cik, float date, value) from every cached EntityPublicFloat frame."""
    out = {}
    for f in sorted((SEC_CACHE / "api/xbrl/frames/dei/EntityPublicFloat/USD").glob("CY*I.json.gz")):
        for e in json.load(gzip.open(f, "rt"))["data"]:
            out[e["accn"]] = (int(e["cik"]), e["end"], float(e["val"]))
    return out


def load_filings() -> list[dict]:
    return json.load(gzip.open(FILINGS, "rt"))


def load_forms(cik: int) -> list[tuple[str, str, str]] | None:
    """(filing date, form, 8-K items) from the cached submissions files only; None if not cached."""
    base = SEC_CACHE / "submissions"
    main = base / f"CIK{cik:010d}.json.gz"
    if not main.exists():
        return None
    d = json.load(gzip.open(main, "rt"))
    pages = [d["filings"]["recent"]] + [json.load(gzip.open(base / (p["name"] + ".gz"), "rt"))
                                        for p in d["filings"].get("files", []) if (base / (p["name"] + ".gz")).exists()]
    rows = []
    for c in pages:
        items = c.get("items") or [""] * len(c["form"])
        rows += list(zip(c["filingDate"], c["form"], items))
    return rows


def exit_type(forms, exit_ym: int) -> str:
    """Protocol 2.6: forms filed within [exit - 24 months, exit + 6 months]."""
    if forms is None:
        return "UNKNOWN"
    lo, hi = ym_add(exit_ym, -24), ym_add(exit_ym, 6)
    win = [(d, f, it) for d, f, it in forms if d and lo <= ym(d) <= hi]
    k103 = [d for d, f, it in win if f.startswith("8-K") and "1.03" in (it or "")]
    failed = bool(k103) or any(f.startswith("15") and any(0 <= months_between(ym(x), ym(d)) <= 12 for x in k103)
                               for d, f, _ in win)
    if failed:
        return "FAILED"
    if any(f in ACQ_FORMS for _, f, _ in win):
        return "ACQUIRED"
    if any(f in ("25", "25-NSE") for _, f, _ in win):
        return "DELISTED-OTHER"
    return "UNKNOWN"


def build(floats: dict, filings: list[dict], forms_of=load_forms) -> list[dict]:
    by_cik = defaultdict(list)
    for r in filings:
        if r["form"] in PERIODIC:
            by_cik[int(r["cik"])].append(r)
    rows = []
    for cik, fl in by_cik.items():
        fl.sort(key=lambda r: r["filed"])
        tenk = [(r, floats[r["accn"]][2]) for r in fl if r["form"] in K_FORMS and r["accn"] in floats
                and floats[r["accn"]][0] == cik]
        if not tenk:
            continue
        last_periodic = fl[-1]["filed"]
        left = last_periodic < "2018-01-01"
        exit_ym = ym(last_periodic) if left else None
        forms = None
        for m in MONTHS:
            prev_end = ym_add(m, -1)
            known = [(r, v) for r, v in tenk if ym(r["filed"]) <= prev_end]
            if not known:
                continue
            r10, val = known[-1]
            if months_between(ym(r10["filed"]), m) > 15 or val < FLOAT_MIN:
                continue
            if left and m > exit_ym:
                continue
            latest = [r for r in fl if ym(r["filed"]) <= prev_end][-1]
            name = latest["name"] or ""
            sic = latest["sic"]
            if sic in NON_COMMON_SIC or NON_COMMON_NAME.search(name):
                continue
            if left and forms is None:
                forms = forms_of(cik) or []
            rows.append({"cik": cik, "ym": m, "float": val, "prefix": (latest["prefix"] or "").upper(),
                         "sic": sic, "fin": bool(sic and 6000 <= sic <= 6799), "foreign_name": bool(FOREIGN.search(name)),
                         "left": left, "exit_ym": exit_ym,
                         "exit_type": exit_type(forms if forms else None, exit_ym) if left else None,
                         "leaver_month": bool(left and months_between(m, exit_ym) < 24)})
    # size tercile within each month (public float; never used as liquidity)
    by_m = defaultdict(list)
    for r in rows:
        by_m[r["ym"]].append(r)
    for m, rs in by_m.items():
        rs.sort(key=lambda r: (r["float"], r["cik"]))
        n = len(rs)
        for i, r in enumerate(rs):
            r["size_tercile"] = 1 + (3 * i) // n
    # prefix shared by >= 2 frame registrants in the same month
    share = Counter((r["ym"], r["prefix"]) for r in rows)
    for r in rows:
        r["prefix_shared"] = (not r["prefix"]) or share[(r["ym"], r["prefix"])] > 1
    return rows


def prefix_ciks(filings: list[dict]) -> dict[str, list[int]]:
    """R2 ticker reuse: CIKs whose 2010-2017 periodic filings carry each prefix."""
    out = defaultdict(set)
    for r in filings:
        if r["form"] in PERIODIC and "2010-01-01" <= r["filed"] <= "2017-12-31" and r["prefix"]:
            out[r["prefix"].upper()].add(int(r["cik"]))
    return {k: sorted(v) for k, v in out.items()}


def summarise(rows: list[dict]) -> dict:
    yrs = defaultdict(lambda: {"registrant_months": 0, "registrants": set(), "leaver_months": 0})
    for r in rows:
        y = yrs[r["ym"] // 100]
        y["registrant_months"] += 1
        y["registrants"].add(r["cik"])
        y["leaver_months"] += r["leaver_month"]
    left = {r["cik"]: r["exit_type"] for r in rows if r["left"]}
    return {
        "frame": "R1 public float >= $2B (10-K, PIT by filing date) x R2 XBRL index; exclusions per protocol 2.3",
        "registrant_months": len(rows), "registrants": len({r["cik"] for r in rows}),
        "by_year": {y: {"registrant_months": v["registrant_months"], "registrants": len(v["registrants"]),
                        "leaver_months": v["leaver_months"]} for y, v in sorted(yrs.items())},
        "leaver_registrants_by_exit_type": dict(Counter(left.values())),
        "financial_reit_registrant_months": sum(r["fin"] for r in rows),
        "foreign_style_name_registrant_months": sum(r["foreign_name"] for r in rows),
        "prefix_missing_or_shared_registrant_months": sum(r["prefix_shared"] for r in rows),
    }


def main():
    floats, filings = load_floats(), load_filings()
    rows = build(floats, filings)
    FRAME_OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(FRAME_OUT, "wt") as fh:
        json.dump({"rows": rows, "prefix_ciks": prefix_ciks(filings)}, fh)
    s = summarise(rows)
    SUMMARY_OUT.write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
