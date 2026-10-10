"""P7-CP5d (D186) item 24/25: are the securities that left the eligible universe on the new default build (E993-03,
LEAN 18178; 'market cap missing' for ~85% of them, X996 E996-01 reason counts) biased toward companies that later
disappear? Uses only our own eligibility membership (E993-02 data v1 vs E993-03 new build; security ids per review),
no vendor value and no price or return. A security 'survives' if it is still in the data-v1 eligible set at the last
review (2017-12-29); 'later absent' otherwise (delisted, acquired, or fell below the filters)."""
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
import qr_p7_export as E  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402


def tables(pay):
    sids = pay["sids"]
    return {t: {sids[r["i"]] for r in E.decode_rows(enc)} for t, tk, enc in pay["reviews"]}


def main():
    old = tables(json.loads(gzip.open(ROOT / "research/phase7/P7_CP3R_E993_payload.json.gz").read()))
    new = tables(json.loads(E.unpack(joined(lines("E993-03"), "QRP7X"))))
    last = old[max(old)]
    out = dict(by_year={}, totals={})
    tot = {"both": [0, 0], "old_only": [0, 0], "new_only": [0, 0]}
    for t in sorted(old):
        y = t[:4]
        d = out["by_year"].setdefault(y, {"both": [0, 0], "old_only": [0, 0], "new_only": [0, 0]})
        for k, s in (("both", old[t] & new[t]), ("old_only", old[t] - new[t]), ("new_only", new[t] - old[t])):
            surv = sum(1 for x in s if x in last)
            d[k][0] += len(s)
            d[k][1] += surv
            tot[k][0] += len(s)
            tot[k][1] += surv
    for d in list(out["by_year"].values()) + [tot]:
        for k in list(d):
            n, s = d[k]
            d[k] = dict(stock_reviews=n, survivor_share=round(s / n, 4) if n else None)
    out["totals"] = tot
    persistent = {}
    for t in sorted(old):
        for x in old[t] - new[t]:
            persistent[x] = persistent.get(x, 0) + 1
    out["old_only_securities"] = len(persistent)
    out["old_only_securities_in_last_review"] = sum(1 for x in persistent if x in last)
    out["old_securities"] = len(set().union(*old.values()))
    p = Path(__file__).parent / "universe_survivorship.json"
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
