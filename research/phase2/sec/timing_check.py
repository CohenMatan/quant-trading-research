"""QuantConnect-vs-SEC TIMING comparison at full scale (D111): every vendor report of an eligible company seen in
E970-01 (2010-2021) against the SEC filing record (data.sec.gov submissions; public domain).

For each report: SEC filing found by accession and/or the first periodic filing for the same period; then
  * vendor file date vs SEC filing date;
  * vendor first-seen date (when the report first appeared in QuantConnect's data) vs SEC filing date;
  * PIT-layer exposure date (qr_fundamentals.available_from) vs SEC filing date: an exposure ON or BEFORE the SEC
    filing date would be look-ahead.
Output: research/phase2/sec/timing_check.json (counts and distributions; dates only)."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
sys.path.insert(0, str(Path(__file__).parent))

from qr_fundamentals import available_from, is_estimated_file_date  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import e970_parse  # noqa: E402

PERIODIC = ("10-K", "10-Q", "10-K/A", "10-Q/A", "10-KT", "10-KT/A", "10-K405")


def bucket(n):
    for b in (-30, -1, 0, 1, 2, 3, 5, 10, 30, 90, 365):
        if n <= b:
            return f"<={b}"
    return ">365"


def sec_index(client, cik):
    sub = client.submissions(cik)
    if not sub:
        return None
    rows = filings_table(sub)
    by_acc = {r["accessionNumber"]: r for r in rows}
    by_pe = defaultdict(list)
    er = []
    for r in rows:
        if r["form"] in PERIODIC and r.get("reportDate"):
            by_pe[r["reportDate"]].append(r)
        if r["form"] in ("8-K", "8-K/A") and "2.02" in str(r.get("items") or ""):
            er.append(r["filingDate"])           # results of operations (earnings release)
    return by_acc, by_pe, sorted(er)


def first_for_period(by_pe, pe):
    best = None
    for k in (pe + timedelta(days=i) for i in range(-6, 7)):
        for r in by_pe.get(k.isoformat(), ()):
            if not r["form"].endswith("/A") and (best is None or r["filingDate"] < best["filingDate"]):
                best = r
    return best


def public_date(r):
    """Calendar date the filing became public: the EDGAR acceptance date if earlier than the filing date
    (filings accepted after 17:30 carry the next business day's filing date)."""
    fd = date.fromisoformat(r["filingDate"])
    acc = r.get("acceptanceDateTime")
    try:
        ad = date.fromisoformat(acc[:10]) if acc else fd
    except ValueError:
        ad = fd
    return min(fd, ad)


def main(fetch=True):
    t = e970_parse.load()
    client = SECClient()
    idx = {}
    out = Counter()
    dist = defaultdict(Counter)
    examples = defaultdict(list)
    for r in t["reports"]:
        cik = r["cik"]
        out["reports"] += 1
        kind = ("quarantined" if r["quarantined"] else "estimated" if r["estimated"] else
                "amendment" if r["amendment"] else "normal")
        if cik not in idx:
            idx[cik] = sec_index(client, cik) if (fetch and cik) else None
        ix = idx[cik]
        if ix is None:
            out[f"no_sec_record|{kind}"] += 1
            continue
        by_acc, by_pe, ers = ix
        pe, fd, seen = r["period_end"], r["file_date"], r["first_seen"]
        first = first_for_period(by_pe, pe) if pe else None
        acc_row = by_acc.get(r["accession"])
        acc_class = ("accession_not_found" if acc_row is None else
                     "own_period" if (acc_row.get("reportDate") and pe and
                                      abs((date.fromisoformat(acc_row["reportDate"]) - pe).days) <= 6)
                     else f"other_{acc_row['form']}")
        dist[f"accession_class|{kind}"][acc_class] += 1
        if first is None:
            out[f"no_sec_periodic_filing_for_period|{kind}"] += 1      # CIK mismatch (vendor CIK is current-status), foreign filer, pre-registration period
            continue
        out[f"matched|{kind}"] += 1
        pub = public_date(first)
        er = next((date.fromisoformat(d) for d in ers if pe < date.fromisoformat(d) <= pub), None)
        expo = available_from(pe, fd) if pe and fd else None
        dist[f"file_minus_periodic_public|{kind}"][bucket((fd - pub).days) if fd else "none"] += 1
        dist[f"seen_minus_periodic_public|{kind}"][bucket((seen - pub).days)] += 1
        if expo is None:
            dist[f"exposure_class|{kind}"]["never (timing unknown)"] += 1
            continue
        if kind == "quarantined":
            cls = "never exposed (quarantine)"
        elif expo > pub:
            cls = "after periodic filing public"
        elif er is not None and expo > er:
            cls = "after earnings release 8-K, before 10-Q/10-K"
        else:
            cls = "EARLY: no public SEC source before exposure"
        dist[f"exposure_class|{kind}"][cls] += 1
        if (seen <= pub) and not (er is not None and seen > er):
            out[f"SEEN_WITHOUT_PUBLIC_SOURCE|{kind}"] += 1
            if len(examples[f"seen_early|{kind}"]) < 40:
                examples[f"seen_early|{kind}"].append([r["ticker"], cik, str(pe), str(fd), str(seen), str(pub),
                                                       str(er), first["form"], first["accessionNumber"]])
        if cls.startswith("EARLY") and len(examples[f"early|{kind}"]) < 60:
            examples[f"early|{kind}"].append([r["ticker"], cik, str(pe), str(fd), str(expo), str(pub), str(er),
                                              first["form"], first["accessionNumber"]])
        if r["estimated"]:
            dist["estimated_true_public_lag_days"][bucket((pub - pe).days)] += 1
            if expo <= pub and not (er is not None and expo > er):
                out["estimated_exposed_before_any_public_source"] += 1
    res = dict(counts=dict(out), distributions={k: dict(v) for k, v in dist.items()},
               examples=dict(examples), sec_requests=client.fetched)
    (Path(__file__).parent / "timing_check.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["counts"], indent=1, sort_keys=True))
