"""P7-CP5d (D186): the packed reference table for the in-cloud first-seen ledger probe X996. Public SEC data and our
own E993-02 universe membership only (no QuantConnect data). COMPLETE populations, fixed by rule before any result:

  filings  (delta-encoded, see below) every SEC periodic filing (10-K / 10-Q / 10-KT and amendments) with period end 2008-06-30 .. 2017-12-31 of
           every SEC registrant mapped (identity v2 dated CIK rows, or the correction layer) to any security eligible
           at any review under E993-02 (LEAN 18131) or E993-03 (LEAN 18178): (period end, filing date, form);
  vint     for every such period [first, first filed - period end, later, later filed - first filed] per field:
           the value AS FIRST FILED and the first LATER differing value (> 0.5%) with its filing
           date, for quarterly revenue and total assets (sec_pit.period_versions) -- the
           restatement-vintage reference; 4 significant digits (comparison tolerance 0.5%);
  events   every 8-K earnings release (Item 2.02) filing date per registrant (Event Data v1, D123);
  old      the E993-02 eligible set at each of the 84 reviews (universe-migration diagnosis).
Dates are day numbers since 2000-01-01. Output: strategies/X996_first_seen_ledger/p5d_ref*.py,
research/phase7/cp5d/x996_ref_summary.json."""
import csv
import gzip
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
import qr_p7_export as E  # noqa: E402
import qr_sec_data as D  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch.sec_edgar import SECClient  # noqa: E402
from qresearch.sec_pack import pack  # noqa: E402
from qresearch.sec_pit import build_company, index_facts, period_versions  # noqa: E402

EPOCH = date(2000, 1, 1)
STRAT = ROOT / "strategies" / "X996_first_seen_ledger"
FORMS = {"10-Q": 1, "10-K": 2, "10-KT": 2, "10-Q/A": 3, "10-K/A": 4, "10-KT/A": 4}
VFIELDS = ("revenue_q", "total_assets")          # 50-file project limit: fiscal-year revenue dropped


def dn(s):
    return (date.fromisoformat(s[:10]) - EPOCH).days


def g4(x):
    """A value to 4 significant digits as one integer code m * 100 + e (value = sign * m * 10**(e - 3)); compact for
    the 50-file project limit; the in-cloud comparison tolerance (0.5%) is far above the 0.05% rounding."""
    if not x:
        return None
    sgn = -1 if x < 0 else 1
    m, e = f"{abs(x):.3e}".split("e")
    return sgn * (int(m.replace(".", "")) * 100 + int(e))


def tables(pay):
    sids = pay["sids"]
    return {t: [sids[r["i"]] for r in E.decode_rows(enc)] for t, tk, enc in pay["reviews"]}


def main():
    old = tables(json.loads(gzip.open(ROOT / "research/phase7/P7_CP3R_E993_payload.json.gz").read()))
    new = tables(json.loads(E.unpack(joined(lines("E993-03"), "QRP7X"))))
    sec = D.load_table()
    ciks = set()
    for tab in (old, new):
        for t, sids in tab.items():
            for s in sids:
                for _e, _sic, c in sec["sic_history"].get(s, ()):
                    if c not in (None, ""):
                        ciks.add(int(c))
                if s in sec["corrections"]:
                    ciks.update(int(c) for c in sec["corrections"][s]["cik"])
    client = SECClient()
    filings, vint = {}, {}
    nvint = nlater = 0
    for cik in sorted(ciks):
        cf, sub = client.companyfacts(cik), client.submissions(cik)
        if not cf:
            continue
        recs = [r for r in build_company(cf, sub) if "2008-06-30" <= r["period_end"] <= "2017-12-31"
                and r["form"] in FORMS]
        if not recs:
            continue
        rows = sorted({(dn(r["period_end"]), dn(r["filed"]), FORMS[r["form"]]) for r in recs})
        # flat, delta-encoded: [pe - previous pe, filed - pe, form, ...] (decode: running sum of pe deltas)
        flat, prev = [], 0
        for pe_, fd_, fm in rows:
            flat += [pe_ - prev, fd_ - pe_, fm]
            prev = pe_
        filings[str(cik)] = flat
        facts = index_facts(cf)
        vv = {}
        for pe in sorted({r["period_end"] for r in recs}):
            vers = period_versions(facts, pe)
            row = []
            for f in VFIELDS:
                vals = [(v["filed"], v["values"][f]) for v in vers if v["values"].get(f)]
                if not vals:
                    row += [None, None, None, None]
                    continue
                fi, fv = vals[0]
                lat = next(((d, x) for d, x in vals[1:] if abs(x / fv - 1) > 0.005), None)
                # dates as day offsets: first filing - period end; later filing - first filing
                row += [g4(fv), dn(fi) - dn(pe), g4(lat[1]) if lat else None,
                        (dn(lat[0]) - dn(fi)) if lat else None]
                nvint += 1
                nlater += int(lat is not None)
            while row and row[-1] is None:
                row.pop()
            if row:
                vv[str(dn(pe))] = row
        vint[str(cik)] = vv
    events = {}
    with gzip.open(ROOT / "research/phase2/h017/event_table_v1.csv.gz", "rt") as fh:
        for r in csv.DictReader(fh):
            if r["cik"] and int(r["cik"]) in ciks and r["filing_date"] <= "2017-12-31":
                events.setdefault(r["cik"], set()).add(dn(r["filing_date"]))
    events = {k: [b - a for a, b in zip([0] + sorted(v)[:-1], sorted(v))] for k, v in events.items()}   # deltas
    osids = sorted({s for t in old for s in old[t]})
    oi = {s: i for i, s in enumerate(osids)}
    oldtab = {"sids": osids, "reviews": {t: sorted(oi[s] for s in old[t]) for t in sorted(old)}}
    table = {"filings": filings, "vint": vint, "events": events, "old": oldtab, "epoch": str(EPOCH),
             "forms": FORMS, "vfields": list(VFIELDS)}
    for p in STRAT.glob("p5d_ref*.py"):
        p.unlink()
    out = pack(table, "p5d_ref")
    for name, text in out.items():
        (STRAT / name).write_text(text)
    summ = dict(registrants=len(ciks), with_filings=len(filings), filings=sum(len(v) // 3 for v in filings.values()),
                vintage_values=nvint, later_differing=nlater, event_registrants=len(events),
                events=sum(len(v) for v in events.values()), old_sids=len(osids), parts=len(out) - 1,
                chars=sum(len(v) for v in out.values()), sec_requests=client.fetched)
    (Path(__file__).parent / "x996_ref_summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(summ)


if __name__ == "__main__":
    main()
