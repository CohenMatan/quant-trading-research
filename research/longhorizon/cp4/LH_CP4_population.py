"""LH-CP4 (owner D245): the approved 2015-2021 population under the narrow Stage C exception — counts only.
Reads the cached LH-CP3 Stage C P2 metadata records (data/lh_cp3/p2.pkl, rebuilt by LH_CP3_part_a.py; no returns,
prices, signal values or rankings exist in it). Output: LH_CP4_population.json (aggregates only).

    PYTHONPATH=src python research/longhorizon/cp4/LH_CP4_population.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(ROOT / "research/longhorizon/cp3")]
import lh_cp3_data as DATA  # noqa: E402
import lh_cp4_power as P  # noqa: E402

OUT = HERE / "LH_CP4_population.json"


def main():
    from qr_xs_diag import ff12
    p2 = DATA.load_cache("p2.pkl")
    den, recs, chains = p2["den"], p2["recs"], p2["chains"]
    revs = DATA.V3.review_days()
    js = [j for j, (T, _D) in enumerate(revs) if T.year in P.YEARS]
    out = dict(kind="LH-CP4 approved-population aggregates (metadata only; no returns)", decision="D245",
               source="data/lh_cp3/p2.pkl (LH-CP3 Part A Stage C P2 rebuild; reproduces LH_StageC_audit.json exactly)",
               review_months=len(js), first_review=str(revs[js[0]][0]), last_review=str(revs[js[-1]][0]))
    per_month = {c: Counter() for c in ("C1", "C2", "C6")}
    yearly = {c: Counter() for c in ("C1", "C2", "C6")}
    comp = defaultdict(Counter)
    fresh_by_cal = defaultdict(Counter)
    sectors = defaultdict(Counter)
    regs, secs, anchors = set(), set(), defaultdict(set)
    last_anchor = {}
    for rec in sorted(recs, key=lambda r: (r["sid"], r["j"])):
        if rec["year"] not in P.YEARS:
            continue
        ch = chains[rec["key"]]
        incl = {c: P.approved(rec, ch, c) for c in ("C1", "C2", "C6")}
        for c, v in incl.items():
            if v:
                per_month[c][rec["j"]] += 1
                yearly[c][rec["year"]] += 1
        if rec["ok1"]:
            for g in ("all", "entrant" if rec["entrant"] else None, "leaver" if rec["leaver"] else None):
                if g:
                    comp[g]["c1_complete"] += 1
                    comp[g]["approved_c1"] += incl["C1"]
        if incl["C1"]:
            regs.add(rec["key"][0])
            secs.add(rec["sid"])
            anchor = rec["key"][1][0]
            anchors[rec["sid"]].add(anchor)
            prev = last_anchor.get(rec["sid"])
            month = revs[rec["j"]][0].month
            if prev is not None and prev[0] == rec["j"] - 1:
                fresh_by_cal[month]["n"] += 1
                fresh_by_cal[month]["new_quarter"] += anchor != prev[1]
            last_anchor[rec["sid"]] = (rec["j"], anchor)
            sectors[rec["j"]][ff12(rec["sic"])] += 1
    for c in per_month:
        v = sorted(per_month[c][j] for j in js)
        out[f"{c}_per_month"] = dict(min=v[0], median=v[len(v) // 2], max=v[-1], mean=round(sum(v) / len(v), 1))
        out[f"{c}_by_year"] = {str(y): dict(den=den[y], num=yearly[c][y], share=round(yearly[c][y] / den[y], 4))
                               for y in P.YEARS}
        out[f"{c}_min_share"] = min(out[f"{c}_by_year"][str(y)]["share"] for y in P.YEARS)
    out["eligible_per_month_by_year"] = {str(y): round(den[y] / sum(1 for j in js if revs[j][0].year == y), 1)
                                         for y in P.YEARS}
    out["composition_c1"] = {g: dict(v, approved_share=round(v["approved_c1"] / v["c1_complete"], 4))
                             for g, v in comp.items()}
    out["distinct_registrants_c1"] = len(regs)
    out["distinct_securities_c1"] = len(secs)
    nq = sorted(len(a) for a in anchors.values())
    out["distinct_quarters_per_security_c1"] = dict(median=nq[len(nq) // 2], mean=round(sum(nq) / len(nq), 1))
    out["new_quarter_share_by_calendar_month_c1"] = {str(m): round(v["new_quarter"] / v["n"], 3)
                                                     for m, v in sorted(fresh_by_cal.items())}
    tot = Counter()
    for v in fresh_by_cal.values():
        tot.update(v)
    out["new_quarter_share_all_c1"] = round(tot["new_quarter"] / tot["n"], 3)
    hh = []
    sec_counts = defaultdict(list)
    for j in js:
        s = sectors[j]
        n = sum(s.values())
        if n:
            hh.append(sum((k / n) ** 2 for k in s.values()))
            for g, k in s.items():
                sec_counts[g].append(k)
    out["sector_hhi_mean_c1"] = round(sum(hh) / len(hh), 4)
    out["stocks_per_ff12_sector_mean_c1"] = {g: round(sum(v) / len(js), 1) for g, v in sorted(sec_counts.items())}
    out["returns_computed"] = False
    out["signal_values_computed"] = False
    out["cache_sha256"] = hashlib.sha256((DATA.CACHE / "p2.pkl").read_bytes()).hexdigest()
    DATA.SAFE.assert_no_post_cutoff({k: v for k, v in out.items() if k != "cache_sha256"})
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
