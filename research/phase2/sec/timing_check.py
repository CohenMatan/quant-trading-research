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
    for r in rows:
        if r["form"] in PERIODIC and r.get("reportDate"):
            by_pe[r["reportDate"]].append(r)
    return by_acc, by_pe


def first_for_period(by_pe, pe):
    best = None
    for k in (pe + timedelta(days=i) for i in range(-6, 7)):
        for r in by_pe.get(k.isoformat(), ()):
            if not r["form"].endswith("/A") and (best is None or r["filingDate"] < best["filingDate"]):
                best = r
    return best


def main(fetch=True):
    t = e970_parse.load()
    client = SECClient()
    idx = {}
    out = Counter()
    dist = defaultdict(Counter)
    examples = defaultdict(list)
    rows = []
    for r in t["reports"]:
        cik = r["cik"]
        out["reports"] += 1
        if not cik:
            out["no_cik"] += 1
            continue
        if cik not in idx:
            idx[cik] = sec_index(client, cik) if fetch else None
        ix = idx[cik]
        if ix is None:
            out["no_sec_record"] += 1
            continue
        by_acc, by_pe = ix
        pe, fd, seen = r["period_end"], r["file_date"], r["first_seen"]
        acc_row = by_acc.get(r["accession"])
        first = first_for_period(by_pe, pe) if pe else None
        if acc_row is None and first is None:
            out["unmatched"] += 1
            continue
        out["matched"] += 1
        sec_first = date.fromisoformat(first["filingDate"]) if first else None
        acc_date = date.fromisoformat(acc_row["filingDate"]) if acc_row else None
        acc_pe_ok = acc_row is not None and acc_row.get("reportDate") and pe and \
            abs((date.fromisoformat(acc_row["reportDate"]) - pe).days) <= 6
        kind = ("quarantined" if r["quarantined"] else "estimated" if r["estimated"] else
                "amendment" if r["amendment"] else "normal")
        out[f"kind_{kind}"] += 1
        # which SEC filing does the vendor's accession point to?
        if acc_row is None:
            acc_class = "accession_not_found"
        elif acc_pe_ok and not acc_row["form"].endswith("/A"):
            acc_class = "own_original_filing"
        elif acc_pe_ok:
            acc_class = "own_period_amendment"
        else:
            acc_class = f"other_period_{acc_row['form']}"
        dist[f"accession_class|{kind}"][acc_class] += 1
        # the SEC filing the report represents: the accession's filing if it is for this period, else the first
        ref = acc_date if acc_pe_ok else sec_first
        if ref is None:
            out["no_reference_date"] += 1
            continue
        expo = available_from(pe, fd) if pe and fd else None
        dist[f"file_minus_sec|{kind}"][bucket((fd - ref).days) if fd else "none"] += 1
        dist[f"seen_minus_sec|{kind}"][bucket((seen - ref).days)] += 1
        if expo is not None:
            gap = (expo - ref).days
            dist[f"exposure_minus_sec|{kind}"][bucket(gap)] += 1
            if gap <= 0:
                out[f"EXPOSED_ON_OR_BEFORE_SEC_FILING|{kind}"] += 1
                if len(examples[f"early|{kind}"]) < 30:
                    examples[f"early|{kind}"].append([r["ticker"], cik, str(pe), str(fd), str(ref), str(expo),
                                                      r["accession"], acc_class])
        if (seen - ref).days < 0:
            out[f"SEEN_BEFORE_SEC_FILING|{kind}"] += 1
            if len(examples[f"seen_early|{kind}"]) < 30:
                examples[f"seen_early|{kind}"].append([r["ticker"], cik, str(pe), str(fd), str(ref), str(seen),
                                                       r["accession"], acc_class])
        if r["estimated"] and sec_first:
            late = (sec_first - pe).days
            dist["estimated_true_filing_lag_days"][bucket(late)] += 1
            if expo is not None and expo <= sec_first:
                out["estimated_exposed_before_true_filing"] += 1
        rows.append([r["sid"], cik, str(pe), str(fd), str(seen), str(ref), kind, acc_class])
    res = dict(counts=dict(out), distributions={k: dict(v) for k, v in dist.items()},
               examples=dict(examples), sec_requests=client.fetched)
    (Path(__file__).parent / "timing_check.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["counts"], indent=1, sort_keys=True))
