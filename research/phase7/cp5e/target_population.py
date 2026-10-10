"""P7-CP5e (D188) item 2: the FROZEN universe-repair target population, fixed by rule before any repair is computed.

Rule: every security that is in the data-v1 eligible set (E993-02, LEAN 18131) at a month-end review but NOT in the
new-build eligible set (E993-03, LEAN 18178; identical to X996's eligibility) at the same review. A target
stock-month is such a (review, security) pair. These are exactly the 560 securities / 18,915 stock-months of P7-CP5d
section 24 (all loss reasons; X996 attributed ~85% to a missing market cap; the in-cloud reason per security is
recomputed by X997 without exporting it). Inputs are our own eligibility tables (security ids per review); no vendor
value. A target 'survives' if it is in the data-v1 set at the last review (2017-12-29).
Output: research/phase7/cp5e/target_population.json (sorted ids; per-review target ids; counts)."""
import gzip
import hashlib
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


def load():
    old = tables(json.loads(gzip.open(ROOT / "research/phase7/P7_CP3R_E993_payload.json.gz").read()))
    new = tables(json.loads(E.unpack(joined(lines("E993-03"), "QRP7X"))))
    return old, new


def main():
    old, new = load()
    last = old[max(old)]
    per = {t: sorted(old[t] - new.get(t, set())) for t in sorted(old)}
    sids = sorted({s for v in per.values() for s in v})
    by_year = {}
    for t, v in per.items():
        y = by_year.setdefault(t[:4], [0, 0])
        y[0] += len(v)
        y[1] += sum(1 for s in v if s in last)
    out = dict(rule="data-v1 eligible (E993-02) and not new-build eligible (E993-03) at the same month-end review",
               securities=len(sids), stock_months=sum(len(v) for v in per.values()),
               survivors_at_2017_12=sum(1 for s in sids if s in last),
               by_year={y: dict(stock_months=a[0], survivor_stock_months=a[1]) for y, a in sorted(by_year.items())},
               sids=sids, per_review=per)
    out["sha256"] = hashlib.sha256(json.dumps([sids, per], sort_keys=True).encode()).hexdigest()
    (Path(__file__).parent / "target_population.json").write_text(json.dumps(out, sort_keys=True) + "\n")
    print({k: v for k, v in out.items() if k not in ("sids", "per_review")})


if __name__ == "__main__":
    main()
