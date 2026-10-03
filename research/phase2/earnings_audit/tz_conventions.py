"""Per-registrant time-zone convention of the cached SEC submissions files (P2-CP12 timestamp canary finding).
The submissions JSON labels acceptanceDateTime 'Z', but some registrant files carry true UTC and others US Eastern
wall-clock time. For each CIK of the audit, up to three earnings 8-Ks (2010-2021) are compared with the EDGAR filing
index page ('Accepted', Eastern). Convention = the one all checked filings agree on; disagreement or no index page ->
'UNRESOLVED' (such registrants' events are then classified UNKNOWN-time, never guessed).

    PYTHONPATH=src python research/phase2/earnings_audit/tz_conventions.py -> tz_conventions.json
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from qresearch import sec_events as S  # noqa: E402
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import earnings_event_audit as A  # noqa: E402


def page_time(sec, cik, acc):
    b = sec.get_bytes(f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{acc}-index.htm") or b""
    m = re.search(rb'Accepted</div>\s*<div class="info">([^<]+)<', b)
    return m.group(1).decode().strip() if m else None


def main():
    U = A.load_universe()
    ciks = sorted({c for u in U.values() for c in u["ciks"]})
    sec = SECClient()
    out, stats = {}, {"UTC": 0, "ET": 0, "UNRESOLVED": 0}
    for i, cik in enumerate(ciks):
        sub = sec.submissions(cik)
        rows = [f for f in filings_table(sub) if str(f.get("form")) == "8-K" and S.is_earnings_filing(f)
                and "2010" <= str(f["filingDate"])[:4] <= "2021" and len(str(f.get("acceptanceDateTime"))) >= 19]
        if not rows:
            rows = [f for f in filings_table(sub) if len(str(f.get("acceptanceDateTime"))) >= 19][:3]
        step = max(1, len(rows) // 3)
        votes = []
        for f in rows[::step][:3]:
            pg = page_time(sec, cik, f["accessionNumber"])
            if pg is None:
                continue
            raw = str(f["acceptanceDateTime"])[:19].replace("T", " ")
            if pg == raw:
                votes.append("ET")
            elif pg == str(S.acceptance_et(f["acceptanceDateTime"], "UTC")):
                votes.append("UTC")
            else:
                votes.append("?")
        conv = votes[0] if votes and len(set(votes)) == 1 and votes[0] != "?" else "UNRESOLVED"
        out[str(cik)] = dict(convention=conv, votes=votes)
        stats[conv] += 1
        if i % 250 == 0:
            print(i, len(ciks), stats, "fetched", sec.fetched, flush=True)
    Path(__file__).with_suffix(".json").write_text(json.dumps(dict(stats=stats, ciks=out), indent=1) + "\n")
    print(stats)


if __name__ == "__main__":
    main()
