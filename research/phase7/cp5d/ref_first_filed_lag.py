"""P7-CP5d (D186): public-SEC-only explanation of the 'first_before_sec' vintage category. For every SEC period in the
X996 reference table, compare the day the field's value was FIRST filed with the period's original periodic filing
(10-Q / 10-K). A quarterly revenue value that the company did not tag as a three-month figure in its original filing
(typically the fourth quarter, reported only as a fiscal-year total in the 10-K) is first 'filed' as a comparative a
year later; a vendor value equal to it is then classed 'first_before_sec' although it was derivable from public filings
(fiscal year minus nine months). No QuantConnect data."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "strategies/X996_first_seen_ledger"))
from p5d_ref import load_table  # noqa: E402


def main():
    t = load_table()
    out = {}
    for cik, flat in t["filings"].items():
        pe, orig = 0, {}
        for i in range(0, len(flat), 3):
            pe += flat[i]
            fd, fm = pe + flat[i + 1], flat[i + 2]
            if fm in (1, 2):
                orig[pe] = min(orig.get(pe, fd), fd)
        for pk, row in t["vint"].get(cik, {}).items():
            p = int(pk)
            if p not in orig:
                continue
            for j, f in enumerate(t["vfields"]):
                r = (row + [None] * 8)[4 * j:4 * j + 4]
                if r[0] is None:
                    continue
                lag = p + r[1] - orig[p]
                k = f"{f}|{'same_filing' if lag <= 0 else ('within_5d' if lag <= 5 else 'later_filing')}"
                out[k] = out.get(k, 0) + 1
    for f in t["vfields"]:
        n = sum(v for k, v in out.items() if k.startswith(f + "|"))
        out[f + "|later_filing_pct"] = round(100 * out.get(f + "|later_filing", 0) / n, 2)
    (Path(__file__).parent / "ref_first_filed_lag.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
