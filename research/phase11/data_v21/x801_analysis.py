"""Data Infrastructure v2.1 (owner D206): offline integrity audit of the X801 runs -> x801_summary.json.

Inputs: the aggregate JSON each X801 run published (counts, distributions, per-review SHA-256 digests) and the frozen
Data v2 export E998-01 (and its truncated E998-03); no vendor value, no return. The gate thresholds below were written
and committed BEFORE any E801 output was read.

Runs: E801-01 full 2011-2021; E801-02 identical repeat; E801-03 ending 2017-12-31; E801-04 ending 2013-12-31.
    PYTHONPATH=src python research/phase11/data_v21/x801_analysis.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/phase7/data_v2"))
from x998_analysis import AUDIT_ZERO, load, record, strip  # noqa: E402

RUNS = ("E801-01", "E801-02", "E801-03", "E801-04")
TH = dict(repro_eligibility_share=0.99,       # 2011-2017 review eligibility digests equal to the frozen E998-01
          new_year_mapping_min=0.90,          # 2018-2021: share of new vendor reports mapped to an SEC filing
          new_year_scored_ratio_min=0.50)     # 2018-2021 scored stocks per review >= 50% of the 2011-2017 mean
PERIODS = {"2011-2017": [str(y) for y in range(2011, 2018)], "2018": ["2018"], "2019": ["2019"], "2020": ["2020"],
           "2021": ["2021"]}


def per_period(st):
    yr = st["per_year"]
    out = {}
    for name, ys in PERIODS.items():
        a = {}
        for y in ys:
            for k, v in yr.get(y, {}).items():
                if isinstance(v, (int, float)):
                    a[k] = a.get(k, 0) + v
        rv = a.get("reviews", 0)
        idc = st["identity_mapping"]
        mapped = sum(v for k, v in idc.items() if k.startswith("mapped|") and k.split("|")[-1] in ys)
        unmapped = sum(v for k, v in idc.items() if k.startswith("unmapped|") and k.split("|")[-1] in ys)
        a["new_reports_mapped_share"] = round(mapped / (mapped + unmapped), 4) if mapped + unmapped else None
        a["new_reports"] = mapped + unmapped
        for k in ("eligible", "scored", "candidates", "nonfin", "h2_nonfin", "from_sec_repair", "from_qc_cap"):
            a[f"{k}_per_review"] = round(a.get(k, 0) / rv, 1) if rv else None
        a["h2_share_nonfin"] = round(a.get("h2_nonfin", 0) / a["nonfin"], 4) if a.get("nonfin") else None
        out[name] = a
    return out


def same(d1, d2, keys):
    return [k for k in keys if d1.get(k) == d2.get(k)], [k for k in keys if d1.get(k) != d2.get(k)]


def main():
    S = {e: load(e) for e in RUNS}
    rec = {e: record(e) for e in RUNS}
    v2, v2t = load("E998-01"), load("E998-03")
    out = dict(runs={e: dict(record=rec[e], end=(S[e] or {}).get("end"), table=(S[e] or {}).get("table_version"))
                     for e in RUNS})
    full = S["E801-01"]
    out["per_period"] = per_period(full)
    out["pit_audit"] = {e: S[e]["pit_audit"] for e in RUNS if S[e]}
    out["repair"] = full["repair"]
    out["mcap_comparison"] = full["mcap_comparison"]
    out["sec_split_check"] = full["sec_split_check"]
    out["identity_sanity"] = full["identity_sanity"]
    out["restatement_guard"] = full["restatement_guard"]
    d1, d3, d4 = full["digests"], S["E801-03"]["digests"], S["E801-04"]["digests"]
    r17 = sorted(r for r in d3["review_eligibility"])
    r13 = sorted(r for r in d4["review_eligibility"])
    fut_e = same(d1["review_eligibility"], d3["review_eligibility"], r17)
    fut_s = same(d1["review_scores"], d3["review_scores"], r17)
    tr_e = same(d1["review_eligibility"], d4["review_eligibility"], r13)
    tr_s = same(d1["review_scores"], d4["review_scores"], r13)
    rp_e = same(v2["digests"]["review_eligibility"], d3["review_eligibility"], r17)
    rp_s = same(v2["digests"]["review_scores"], d3["review_scores"], r17)
    out["future_invariance_2011_2017"] = dict(reviews=len(r17), eligibility_equal=len(fut_e[0]), scores_equal=len(fut_s[0]),
                                              differing=fut_e[1] + fut_s[1])
    out["truncation_2011_2013"] = dict(reviews=len(r13), eligibility_equal=len(tr_e[0]), scores_equal=len(tr_s[0]),
                                       ledger_to_2013_equal=d1["ledger_to_2013"] == d4["ledger_to_2013"],
                                       differing=tr_e[1] + tr_s[1])
    out["reproduction_vs_frozen_E998_01"] = dict(reviews=len(r17), eligibility_equal=len(rp_e[0]),
                                                 scores_equal=len(rp_s[0]), eligibility_differing=rp_e[1],
                                                 scores_differing=rp_s[1],
                                                 ledger_by_year_equal={y: v2["digests"]["ledger_by_year"].get(y) == h
                                                                       for y, h in d3["ledger_by_year"].items()})
    a, b = strip(S["E801-01"]), strip(S["E801-02"])
    out["determinism_E801_02"] = dict(identical=a == b,
                                      differing_keys=sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k)))
    pp = out["per_period"]
    base = pp["2011-2017"]["scored_per_review"]
    gates = dict(
        PIT=all(all(S[e]["pit_audit"].get(k, 0) == 0 for k in AUDIT_ZERO) for e in RUNS),
        DETERMINISM=out["determinism_E801_02"]["identical"],
        FUTURE_INVARIANCE=not out["future_invariance_2011_2017"]["differing"],
        TRUNCATION=not out["truncation_2011_2013"]["differing"] and out["truncation_2011_2013"]["ledger_to_2013_equal"],
        REPRODUCTION_ELIGIBILITY=len(rp_e[0]) / len(r17) >= TH["repro_eligibility_share"],
        NEW_YEARS_MAPPING=all((pp[y]["new_reports_mapped_share"] or 0) >= TH["new_year_mapping_min"]
                              for y in ("2018", "2019", "2020", "2021")),
        NEW_YEARS_SCORED=all((pp[y]["scored_per_review"] or 0) >= TH["new_year_scored_ratio_min"] * base
                             for y in ("2018", "2019", "2020", "2021")),
        RUNS_COMPLETED=all(rec[e] and rec[e]["status"] == "completed" and rec[e]["orders"] == 0 for e in RUNS))
    out["gates"] = gates
    out["thresholds"] = TH
    out["all_pass"] = all(gates.values())
    # ---- added AFTER the gate results were seen (D207); the gates and TH above are unchanged ----------------------
    # (a) NEW_YEARS_MAPPING specification error: the counter's denominator includes vendor reports of companies with
    #     no SEC identity row ('unmapped|no_cik'); the same counter is ~0.53-0.59 in the frozen Data v2 years. The
    #     share among reports WITH an SEC identity is reported per year beside it (record only, never a gate).
    def mapping(idc):
        m, u, nc = {}, {}, {}
        for k, v in idc.items():
            p_ = k.split("|")
            y = p_[-1]
            if p_[0] == "mapped":
                m[y] = m.get(y, 0) + v
            else:
                u[y] = u.get(y, 0) + v
                if p_[1] == "no_cik":
                    nc[y] = nc.get(y, 0) + v
        return {y: dict(as_written=round(m[y] / (m[y] + u.get(y, 0)), 4),
                        with_sec_identity=round(m[y] / (m[y] + u.get(y, 0) - nc.get(y, 0)), 4))
                for y in sorted(m)}
    out["mapping_specification_correction"] = dict(
        decision="D207", gate_as_written="NEW_YEARS_MAPPING FAILED (threshold 0.90 on the as-written share)",
        e801_01=mapping(full["identity_mapping"]), frozen_e998_01=mapping(v2["identity_mapping"]),
        frozen_years_identical=all(full["identity_mapping"].get(k) == v for k, v in v2["identity_mapping"].items()))
    # (b) 2011-2017 analysed-population reproduction (H022 population = 'candidates' per review) vs frozen E998-01
    col = full["per_review_cols"]
    a = {r[0]: dict(zip(col, r)) for r in S["E801-03"]["per_review"]}
    b = {r[0]: dict(zip(col, r)) for r in v2["per_review"]}
    dec = [d for d in sorted(b) if d < "2017-12-01"]
    out["h022_population_2011_2017"] = dict(
        decisions=len(dec), frozen_stock_months=sum(b[d]["candidates"] for d in dec),
        v21_stock_months=sum(a[d]["candidates"] for d in dec),
        reviews_differing=[[d, b[d]["candidates"], a[d]["candidates"], b[d]["scored"], a[d]["scored"]]
                           for d in sorted(b) if a[d] != b[d]],
        score_digest_differing=rp_s[1], d202_snapshot_reviews=[d for d in rp_s[1] if "2011-02" <= d <= "2012-01-31"])
    hp = out["h022_population_2011_2017"]
    hp["relative_change"] = round(hp["v21_stock_months"] / hp["frozen_stock_months"] - 1.0, 6)
    import hashlib
    out["review_calendar_sha256"] = hashlib.sha256(json.dumps([r[0] for r in full["per_review"]]).encode()).hexdigest()
    out["reviews"] = dict(n=len(full["per_review"]), first=full["per_review"][0][0], last=full["per_review"][-1][0])
    (Path(__file__).parent / "x801_summary.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(dict(gates=gates, per_period={k: {kk: v.get(kk) for kk in (
        "eligible_per_review", "scored_per_review", "new_reports_mapped_share", "h2_share_nonfin", "from_sec_repair_per_review")}
        for k, v in pp.items()}), indent=1))


if __name__ == "__main__":
    main()
