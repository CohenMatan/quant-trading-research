"""P7-CP5b (D182, owner option B): compare the X993 v1.1 score export on QuantConnect's DEFAULT build (E993-03) with the
calibration-build export E993-02 (LEAN 18131) -> research/phase7/P7_CP5b_engine_diagnosis.json. Scores, eligibility and
disqualifier bits only: no price, no return, no IC."""
import gzip
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(HERE)]
import qr_p7_export as E  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402


def load(exp):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7S"))
    pay = json.loads(E.unpack(joined(ls, "QRP7X")))
    rows = {}
    for t, tk, enc in pay["reviews"]:
        rows[t] = {pay["sids"][r["i"]]: r for r in E.decode_rows(enc)}
    return st, pay, rows


def bits_count(rr):
    c = Counter()
    for r in rr.values():
        for b in ("H1_financial", "H1_no_sic", "H2", "H3", "H4", "H5", "H6", "H7", "duplicate_class"):
            if r["bits"] & E.BIT[b]:
                c[b] += 1
    return c


def main(new="E993-03", ref="E993-02"):
    st_n, pay_n, rows_n = load(new)
    st_r, pay_r, rows_r = load(ref)
    res_n = json.loads((ROOT / "experiments" / new / "result.json").read_text())["provenance"]
    reviews = sorted(set(rows_r) | set(rows_n))
    per = []
    tot = Counter()
    for t in reviews:
        a, b = rows_r.get(t, {}), rows_n.get(t, {})
        pa = {s for s, r in a.items() if E.eligible_flag(r["bits"], r["total"])}
        pb = {s for s, r in b.items() if E.eligible_flag(r["bits"], r["total"])}
        common = set(a) & set(b)
        same_total = sum(1 for s in common if a[s]["total"] == b[s]["total"])
        same_all = sum(1 for s in common if a[s] == b[s])
        tot.update(dict(eligible_ref=len(a), eligible_new=len(b), common=len(common), same_row=same_all,
                        same_total=same_total, pop_ref=len(pa), pop_new=len(pb), pop_common=len(pa & pb)))
        per.append(dict(review=t, eligible=[len(a), len(b)], population=[len(pa), len(pb)], common=len(common),
                        identical_rows=same_all, bits_ref=dict(bits_count(a)), bits_new=dict(bits_count(b))))
    bt_r, bt_n = Counter(), Counter()
    for p in per:
        bt_r.update(p["bits_ref"])
        bt_n.update(p["bits_new"])
    pops_n = [p["population"][1] for p in per if p["review"] < "2017-12"]
    out = dict(new=new, ref=ref, lean_new=res_n.get("lean_version"), lean_ref="v2.5.0.0.18131",
               reviews=[len(rows_r), len(rows_n)], totals=dict(tot), bits_total_ref=dict(bt_r), bits_total_new=dict(bt_n),
               population_new=dict(min=min(pops_n), median=statistics.median(pops_n), max=max(pops_n)),
               store_stats=[st_r.get("store_stats"), st_n.get("store_stats")],
               checks=[st_r.get("checks"), st_n.get("checks")], baseline=[st_r.get("baseline"), st_n.get("baseline")],
               panel=[st_r.get("panel"), st_n.get("panel")], calendar=[st_r.get("calendar_check"), st_n.get("calendar_check")],
               per_review=per)
    (HERE / "P7_CP5b_engine_diagnosis.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("lean_new", "reviews", "totals", "bits_total_ref", "bits_total_new",
                                          "population_new")}, indent=1))


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
