"""P2-CP12 audit follow-up: how many 'registrant has no SEC filings around the quarter' gaps are predecessor /
successor registrants that the frozen identity rule T (dated XBRL instance-prefix = the security's ticker within +-3
months) can link point-in-time. Evidence only; nothing is added to the frozen data infrastructure.

For each security-quarter in that category: candidate CIKs = registrants (other than the mapped one) with >= 2 XBRL
filings whose prefix equals a ticker the security carried within +-3 months, filed within the security's eligible span,
and NOT overlapping the mapped CIK's own filing period (time-disjoint succession). If exactly one candidate exists and it
has an earnings 8-K event in the quarter, the gap is 'recoverable'.

    PYTHONPATH=src python research/phase2/earnings_audit/predecessor_recovery.py -> predecessor_recovery.json
"""
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch import sec_events as S  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import earnings_event_audit as A  # noqa: E402


def main():
    U = A.load_universe()
    cal = A.calendar()
    sec = SECClient()
    tzc = {int(k): v["convention"] for k, v in json.loads((Path(__file__).parent / "tz_conventions.json").read_text())["ciks"].items()}
    xb = json.load(gzip.open(ROOT / "data/sec_derived/xbrl_filings.json.gz"))
    by_prefix = defaultdict(list)
    span_of = defaultdict(list)
    for r in xb:
        if r.get("prefix") and r.get("filed"):
            ym = int(r["filed"][:4]) * 100 + int(r["filed"][5:7])
            by_prefix[r["prefix"].upper()].append((int(r["cik"]), ym))
            span_of[int(r["cik"])].append(ym)
    out = Counter()
    examples = []
    for sid, u in U.items():
        if not u["ciks"] or u["corrected"]:
            continue
        own = u["ciks"][0]
        own_span = (min(span_of[own]), max(span_of[own])) if span_of.get(own) else None
        cands = Counter()
        for t, a, b in u["tickers"]:
            for cik, ym in by_prefix.get(t, ()):
                if cik == own or not (A.ym_add(a, -3) <= ym <= A.ym_add(b, 3)):
                    continue
                if own_span and own_span[0] <= ym <= own_span[1]:
                    continue                      # overlapping the mapped registrant: not a succession
                cands[cik] += 1
        cands = [c for c, n in cands.items() if n >= 2]
        own_rows = filings_table(sec.submissions(own)) if sec.submissions(own) else []
        filed_q = {(int(str(f["filingDate"])[:4]), (int(str(f["filingDate"])[5:7]) - 1) // 3) for f in own_rows}
        missing = [q for q in A.quarters(u["months"])
                   if q not in filed_q and (q[0], q[1] - 1) not in filed_q and (q[0], q[1] + 1) not in filed_q]
        if not missing:
            continue
        out["quarters_no_registrant_filings"] += len(missing)
        if len(cands) != 1:
            out["no_unique_predecessor" if not cands else "ambiguous_predecessor"] += len(missing)
            continue
        alt = cands[0]
        sub = sec.submissions(alt)
        if sub is None:
            out["predecessor_without_submissions"] += len(missing)
            continue
        ev = S.build_events(alt, filings_table(sub), cal, tz=tzc.get(alt, "UTC"))["events"]
        evq = {(e.event_session.year, (e.event_session.month - 1) // 3) for e in ev if e.event_session}
        rec = [q for q in missing if q in evq]
        out["recoverable"] += len(rec)
        out["predecessor_found_no_event"] += len(missing) - len(rec)
        if rec:
            examples.append(dict(sid=sid, mapped_cik=own, predecessor_cik=alt, predecessor_name=sub.get("name"),
                                 recovered_quarters=len(rec)))
    res = dict(counts=dict(out), examples=sorted(examples, key=lambda x: -x["recovered_quarters"])[:30],
               note="predecessors whose time-zone convention was not measured default to UTC here (counting only)")
    Path(__file__).with_suffix(".json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res["counts"]), "fetched", sec.fetched)
    for e in res["examples"][:12]:
        print(e)


if __name__ == "__main__":
    main()
