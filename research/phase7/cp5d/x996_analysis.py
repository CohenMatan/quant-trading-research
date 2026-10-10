"""P7-CP5d (D186): offline summary of the X996 aggregate outputs (E996-01 M1 full, E996-02 M1 truncated at
2013-12-31, E996-03 M2 full). Inputs are only the aggregate JSON each run published (counts, histograms, SHA-256
digests); no vendor value exists anywhere. No return, IC or performance is computed. Comparison figures for data v1
(E993-02, LEAN 18131) and the frozen layer on the new build (E993-03) come from P7-CP5b.
Output: research/phase7/cp5d/x996_summary.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNS = {"E996-01": "M1 full", "E996-02": "M1 to 2013-12-31", "E996-03": "M2 full"}


def load(eid):
    p = ROOT / "experiments" / eid / "messages.txt"
    if not p.exists():
        return None
    parts = sorted((ln for ln in p.read_text().splitlines() if ln.startswith("QRP5D|")),
                   key=lambda ln: int(ln.split("|")[1]))
    if not parts:
        return None
    return json.loads("".join(ln.split("|", 2)[2] for ln in parts))


def pct(a, b):
    return None if not b else round(100.0 * a / b, 2)


def timing(tm):
    """first seen - SEC original filing (days), by form and era; early cases by explanation."""
    out = {}
    for k, v in tm.items():
        p = k.split("|")
        if p[0] in ("Q", "K") and p[1] in ("2008", "2009-2012", "2013-2017"):
            d = out.setdefault(f"{p[0]}|{p[1]}", {})
            d[p[2]] = d.get(p[2], 0) + v
    for d in out.values():
        n = sum(d.values())
        d["n"] = n
        d["early_pct"] = pct(d.get("le0", 0), n)
        d["within_1_pct"] = pct(d.get("1", 0), n)
        d["within_5_pct"] = pct(d.get("le0", 0) + d.get("1", 0) + d.get("2-5", 0), n)
    early = {}
    for k, v in tm.items():
        if k.startswith("early|"):
            _, form, era, why, b = k.split("|")
            early[f"{form}|{era}|{why}"] = early.get(f"{form}|{era}|{why}", 0) + v
    by_year = {}
    for k, v in tm.items():
        p = k.split("|")
        if p[0] in ("Q", "K") and p[1].isdigit():
            d = by_year.setdefault(p[1], {})
            d[p[2]] = d.get(p[2], 0) + v
    for y, d in by_year.items():
        d["early_pct"] = pct(d.get("le0", 0), sum(d.values()))
    return dict(by_form_era=out, early=early, by_year=dict(sorted(by_year.items())))


def vintage(vt):
    out = {}
    for k, v in vt.items():
        p = k.split("|")
        kind, field = p[0], p[1]
        sub = "restated_pending" if len(p) == 4 else "all"
        cat = p[-1]
        d = out.setdefault(f"{kind}|{field}|{sub}", {})
        d[cat] = d.get(cat, 0) + v
    for d in out.values():
        n = sum(d.values())
        d["n"] = n
        ref = n - d.get("no_ref", 0) - d.get("vendor_missing", 0)
        d["match_first_pct_of_compared"] = pct(d.get("first", 0) + d.get("first_before_sec", 0) + d.get("both", 0), ref)
        d["later_future_pct_of_compared"] = pct(d.get("later_FUTURE", 0), ref)
    return out


def coverage(st):
    yr = st["per_year"]
    out = {}
    for y, a in sorted(yr.items()):
        out[y] = dict(reviews=a["reviews"], eligible_mean=round(a["eligible"] / a["reviews"], 1),
                      nonfin_mean=round(a["nonfin"] / a["reviews"], 1), h2_pct_nonfin=pct(a["h2_nonfin"], a["nonfin"]),
                      scored_mean=round(a["scored"] / a["reviews"], 1),
                      candidates_mean=round(a["candidates"] / a["reviews"], 1),
                      ge80_mean=round(a["ge80"] / a["reviews"], 2),
                      field_present_pct=[pct(x, a["nonfin"]) for x in a["field_present"]],
                      old_overlap_h2_pct=pct(a["old_overlap_h2"], a["old_overlap_nonfin"]))
    pr = st["per_review"]
    tot = {k: sum(a[k] for a in yr.values()) for k in ("eligible", "nonfin", "h2_nonfin", "scored", "candidates",
                                                      "ge75", "ge80", "ge85", "ge90")}
    sc = [r[4] for r in pr]
    return dict(by_year=out, totals=tot, h2_pct_nonfin=pct(tot["h2_nonfin"], tot["nonfin"]),
                scored_per_review=dict(min=min(sc), median=sorted(sc)[len(sc) // 2], mean=round(sum(sc) / len(sc), 1),
                                       max=max(sc)),
                ge80_per_review_mean=round(tot["ge80"] / len(pr), 2),
                months_ge80_zero=sum(1 for r in pr if r[7] == 0))


def main():
    st = {e: load(e) for e in RUNS}
    out = {}
    for e, s in st.items():
        if s is None:
            out[e] = "no aggregate output"
            continue
        out[e] = dict(label=RUNS[e], checks=s["checks"], store_stats=s["store_stats"], baseline=s["baseline"],
                      calendar=s["calendar_check"], spot=s["slice_spot_check"], timing=timing(s["timing"]),
                      vintage=vintage(s["vintage"]), vendor_file_date=s["vendor_file_date"],
                      universe_migration=s["universe_migration"], mcap_split_check=s["mcap_split_check"],
                      coverage=coverage(s), totals_candidates=s["totals_candidates"], totals_scored=s["totals_scored"],
                      hist_candidates=s["totals_hist5_candidates"], layers=s["layers"], layer_corr=s["layer_corr"],
                      ledger_reports=s["ledger_reports"], ledger_sids=s["ledger_sids"], wall_s=s["wall_s"],
                      max_rss_mb=s["max_rss_mb"], synthetic=s["synthetic_export_check"])
    a, b, c = st["E996-01"], st["E996-02"], st["E996-03"]
    inv = {}
    if a and b:
        common = sorted(set(a["digests"]["review_scores"]) & set(b["digests"]["review_scores"]))
        inv["truncation"] = dict(
            ledger_to_2013_equal=a["digests"]["ledger_to_2013"] == b["digests"]["ledger_to_2013"],
            eligible_to_2013_equal=a["digests"]["eligible_to_2013"] == b["digests"]["eligible_to_2013"],
            ledger_years_equal={y: a["digests"]["ledger_by_year"].get(y) == h
                                for y, h in b["digests"]["ledger_by_year"].items() if y < "2014"},
            reviews_compared=len(common),
            review_scores_equal=sum(a["digests"]["review_scores"][t] == b["digests"]["review_scores"][t] for t in common),
            first_differing=[t for t in common if a["digests"]["review_scores"][t] != b["digests"]["review_scores"][t]][:5])
    if a and c:
        inv["determinism_M1_vs_M2_observation"] = dict(
            ledger_years_equal={y: c["digests"]["ledger_by_year"].get(y) == h for y, h in a["digests"]["ledger_by_year"].items()},
            eligible_years_equal={y: c["digests"]["eligible_by_year"].get(y) == h
                                  for y, h in a["digests"]["eligible_by_year"].items()})
    out["invariance"] = inv
    p = Path(__file__).parent / "x996_summary.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1, sort_keys=True)[:20000])


if __name__ == "__main__":
    sys.exit(main())
