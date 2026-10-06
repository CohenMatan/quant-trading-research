"""P7-CP3R (D173): CP3 (E993-01, eligible-only revenue-baseline ledger) vs CP3R (E993-02, store-wide company ledger).
Scores and mechanics only (no price, no return). Writes research/phase7/P7_CP3R_compare.json and P7_CP3R_compare.md.
  * rescued-row audit from the E993-02 bits (count, year, share of non-financial rows, reason outside the universe a
    year earlier, listing age), rows lost to the new same-life / same-registrant checks;
  * consistency: E993-02's CP3-rule H2 flag must equal E993-01's H2 flag on every kept-class row (isolates the change);
  * before / after: funnel, H2, availability, distributions, correlations, composition, persistence, churn, costs,
    sector concentration, capacity, market regime; the owner's provisional mechanics."""
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_p7_export as E  # noqa: E402

TH = ("90", "85", "80", "75")
KS = ("6", "8", "10", "12")


def rows_of(path):
    pay = json.loads(gzip.open(path).read())
    sids = pay["sids"]
    out = {}
    for t, tk, enc in pay["reviews"]:
        out[tk] = {sids[r["i"]]: r for r in E.decode_rows(enc)}
    return pay, out


def has(r, b):
    return bool(r["bits"] & E.BIT[b])


def nonfin(r):
    return not (has(r, "H1_financial") or has(r, "H1_no_sic"))


def pct(a, b):
    return None if not b else round(100.0 * (a - b) / b, 1)


def main():
    p1, R1 = rows_of(HERE / "P7_CP3_E993_payload.json.gz")
    p2, R2 = rows_of(HERE / "P7_CP3R_E993_payload.json.gz")
    m1 = json.loads((HERE / "P7_CP3_mechanics.json").read_text())
    m2 = json.loads((HERE / "P7_CP3R_mechanics.json").read_text())
    st2 = json.loads((HERE / "P7_CP3R_E993_stats.json").read_text())
    out = dict(source="E993-01 (CP3) vs E993-02 (CP3R)")
    # ---- consistency: same universe, CP3-rule H2 reproduces E993-01's H2 exactly on kept-class rows
    assert list(R1) == list(R2)
    same_universe = all(set(R1[t]) == set(R2[t]) for t in R1)
    mism = dup_diff = 0
    for t in R1:
        for s, a in R1[t].items():
            b = R2[t][s]
            if has(a, "duplicate_class") != has(b, "duplicate_class"):
                dup_diff += 1
                continue
            if has(a, "duplicate_class"):
                continue
            mism += int(has(a, "H2") != has(b, "H2_old_rule"))
    out["consistency"] = dict(same_eligible_universe_every_review=same_universe, share_class_choice_differences=dup_diff,
                              cp3_rule_h2_mismatches=mism)
    # ---- rescued / lost rows (E993-02)
    by = defaultdict(Counter)
    reasons, reasons_y = Counter(), defaultdict(Counter)
    for t, rows in R2.items():
        y = t[:4]
        for s, r in rows.items():
            if has(r, "duplicate_class"):
                continue
            c = by[y]
            c["rows"] += 1
            if nonfin(r):
                c["nonfin_rows"] += 1
                c["h2_new"] += has(r, "H2")
                c["h2_old"] += has(r, "H2_old_rule")
            if has(r, "rescued"):
                c["rescued"] += 1
                code = (r["bits"] >> E.REASON_SHIFT) & 7
                reasons[E.REASONS[code]] += 1
                reasons_y[y][E.REASONS[code]] += 1
                c["rescued_listed_lt_1y"] += has(r, "listed_lt_1y_at_baseline")
                c["rescued_now_fully_eligible"] += int(E.eligible_flag(r["bits"], r["total"]))
                for th in (75, 80, 85, 90):
                    c[f"rescued_ge{th}"] += int(E.eligible_flag(r["bits"], r["total"]) and r["total"] >= th)
            if has(r, "H2") and not has(r, "H2_old_rule"):
                c["lost"] += 1
                c["lost_life"] += has(r, "baseline_life_reject")
                c["lost_cik"] += has(r, "baseline_cik_reject")
            c["life_reject_any"] += has(r, "baseline_life_reject")
            c["cik_reject_any"] += has(r, "baseline_cik_reject")
    tot = Counter()
    for c in by.values():
        tot.update(c)
    # registrant coverage of rescued baselines: SEC CIK (PIT SIC table) known at the baseline date and now? A baseline
    # whose CIK is unknown at the baseline date cannot be checked for a registrant change (e.g. a holding-company
    # successor such as Zillow Group / Zillow, Inc.); counted here, verified on the SEC sample
    import qr_sec_data
    from datetime import date as _date
    hist = qr_sec_data.load_table()["sic_history"]

    def cik_on(sid, d):
        out_ = None
        for eff, _s, c in hist.get(sid, ()):
            if _date.fromisoformat(eff) <= d:
                out_ = c
        return out_
    reg = Counter()
    for t, rows in R2.items():
        y, m = int(t[:4]), int(t[5:7])
        bday, now = _date(y - 1, m, 28), _date.fromisoformat(t)
        for s, r in rows.items():
            if has(r, "duplicate_class") or not has(r, "rescued"):
                continue
            cb, cn = cik_on(s, bday), cik_on(s, now)
            reg["known_at_both_same" if cb and cn and cb == cn else
                "unknown_at_baseline_known_now" if cn and not cb else
                "known_at_both_different" if cb and cn else "unknown_now"] += 1
    out["rescued"] = dict(by_year={y: dict(c) for y, c in sorted(by.items())}, total=dict(tot),
                          share_of_nonfin_rows={y: round(100 * c["rescued"] / c["nonfin_rows"], 2)
                                                for y, c in sorted(by.items())},
                          share_total=round(100 * tot["rescued"] / tot["nonfin_rows"], 2),
                          reasons=dict(reasons.most_common()), reasons_by_year={y: dict(c) for y, c in
                                                                               sorted(reasons_y.items())},
                          host=st2.get("baseline"), registrant_coverage=dict(reg))
    # ---- before / after tables
    f1, f2 = m1["funnel"]["all"], m2["funnel"]["all"]
    out["funnel"] = [[a[0], a[1], b[1], round(b[1] - a[1], 1), pct(b[1], a[1])] for a, b in zip(f1, f2)]
    out["funnel_by_year"] = {y: [[a[0], a[1], b[1]] for a, b in zip(m1["funnel"][y], m2["funnel"][y])]
                             for y in m1["funnel"] if y != "all"}
    out["dq_share"] = {k: [m1["dq"]["share_of_rows"][k], m2["dq"]["share_of_rows"][k]] for k in m1["dq"]["share_of_rows"]}
    out["h2_rows"] = dict(cp3=m1["dq"]["any_flag"]["H2"], cp3r=m2["dq"]["any_flag"]["H2"],
                          nonfin_cp3=tot["h2_old"], nonfin_cp3r=tot["h2_new"], nonfin_rows=tot["nonfin_rows"])
    out["candidates"] = {th: dict(cp3=m1["candidates"][th]["stats"], cp3r=m2["candidates"][th]["stats"],
                                  zero_cp3=m1["candidates"][th]["zero_months"], zero_cp3r=m2["candidates"][th]["zero_months"],
                                  buckets_cp3=m1["candidates"][th]["buckets"], buckets_cp3r=m2["candidates"][th]["buckets"],
                                  by_year={y: [m1["candidates"][th]["by_year"][y]["mean"],
                                               m2["candidates"][th]["by_year"][y]["mean"],
                                               m1["candidates"][th]["by_year"][y]["zero_months"],
                                               m2["candidates"][th]["by_year"][y]["zero_months"]]
                                           for y in m1["candidates"][th]["by_year"]})
                         for th in TH}
    out["distribution"] = {pop: dict(cp3=dict(n=m1["distributions"][pop]["all"]["n"],
                                              median=m1["distributions"][pop]["all"]["quantiles"]["p50"],
                                              at_least=m1["distributions"][pop]["all"]["at_least"]),
                                     cp3r=dict(n=m2["distributions"][pop]["all"]["n"],
                                               median=m2["distributions"][pop]["all"]["quantiles"]["p50"],
                                               at_least=m2["distributions"][pop]["all"]["at_least"]))
                           for pop in ("data_scorable", "eligible")}
    out["layers"] = dict(cp3=m1["layers"]["pearson_pooled"], cp3r=m2["layers"]["pearson_pooled"],
                         cp3_spearman=m1["layers"]["spearman_mean_per_review"],
                         cp3r_spearman=m2["layers"]["spearman_mean_per_review"],
                         means={k: [m1["layers"][k]["mean"], m2["layers"][k]["mean"]]
                                for k in ("technical", "fundamental", "sector", "total")})
    out["composition"] = {th: {k: [m1["composition"][th].get(k), m2["composition"][th].get(k)]
                               for k in ("stock_months", "distinct_stocks", "mean_layers", "share_with_a_weak_layer",
                                         "trend_state", "sector_state")}
                          for th in ("80", "85")}
    out["composition_ff12"] = {th: [m1["composition"][th]["ff12_share"], m2["composition"][th]["ff12_share"]]
                               for th in ("80", "85")}
    out["persistence"] = {th: dict(cp3=dict(median=m1["persistence"][th]["run_months"]["p50"],
                                            survival=m1["persistence"][th]["survival"],
                                            reentries_per_year=m1["persistence"][th]["reentries_per_year"]),
                                   cp3r=dict(median=m2["persistence"][th]["run_months"]["p50"],
                                             survival=m2["persistence"][th]["survival"],
                                             reentries_per_year=m2["persistence"][th]["reentries_per_year"]),
                                   band_cp3={k: v["p50"] for k, v in m1["persistence"][th]["band_persistence"].items()},
                                   band_cp3r={k: v["p50"] for k, v in m2["persistence"][th]["band_persistence"].items()})
                          for th in TH}

    def ch(m, th, p, K):
        return [x for x in m["churn"] if x["entry"] == int(th) and x["profile"] == p and x["K"] == int(K)][0]
    keys = ("entries_per_year", "normal_exits_per_year", "dq_exits_per_year", "replacements_per_year",
            "sell_then_rebuy", "orders_per_year")
    out["churn"] = {f"{th}/{p}/{K}": dict(
        cp3={**{k: ch(m1, th, p, K)[k] for k in keys}, "median_hold": ch(m1, th, p, K)["holding_months_closed"].get("p50"),
             "utilisation": ch(m1, th, p, K)["utilisation"]["mean"],
             "cost_100k": ch(m1, th, p, K)["costs"]["100000"]["total_pct"],
             "cost_200k": ch(m1, th, p, K)["costs"]["200000"]["total_pct"]},
        cp3r={**{k: ch(m2, th, p, K)[k] for k in keys}, "median_hold": ch(m2, th, p, K)["holding_months_closed"].get("p50"),
              "utilisation": ch(m2, th, p, K)["utilisation"]["mean"],
              "cost_100k": ch(m2, th, p, K)["costs"]["100000"]["total_pct"],
              "cost_200k": ch(m2, th, p, K)["costs"]["200000"]["total_pct"]})
        for th in TH for p in ("H1", "H2", "H3") for K in KS}
    out["sector"] = {th: dict(cp3=m1["sector_concentration"][th]["max_sector_share"].get("p50"),
                              cp3r=m2["sector_concentration"][th]["max_sector_share"].get("p50"),
                              gt50_cp3=m1["sector_concentration"][th]["reviews_one_sector_gt_50pct"],
                              gt50_cp3r=m2["sector_concentration"][th]["reviews_one_sector_gt_50pct"],
                              n_cp3=m1["sector_concentration"][th]["reviews_with_ge5"],
                              n_cp3r=m2["sector_concentration"][th]["reviews_with_ge5"]) for th in TH}
    out["capacity"] = {th: {K: [m1["capacity"][th][K]["all_slots"], m2["capacity"][th][K]["all_slots"],
                                m1["capacity"][th][K]["mean_fill"], m2["capacity"][th][K]["mean_fill"]] for K in KS}
                       for th in TH}
    out["regime"] = dict(identical=p1["regimes"] == p2["regimes"],
                         spy_trend_identical=[x[1] for x in p1["regimes"]] == [x[1] for x in p2["regimes"]],
                         breadth_identical=[x[2:6] for x in p1["regimes"]] == [x[2:6] for x in p2["regimes"]],
                         cp3=m1["regime"]["counts"], cp3r=m2["regime"]["counts"])
    out["provisional"] = dict(cp3=m1.get("provisional"), cp3r=m2["provisional"])
    # ---- material-change table (numbers only; the owner judges)
    pv1 = (m1.get("provisional") or {}).get("v2_regime_limits_10_8_5_2", {})
    pv2 = m2["provisional"]["v2_regime_limits_10_8_5_2"]
    fs = [r for r in out["funnel"] if r[0].startswith("fully scorable")][0]
    out["material"] = [
        ["Fully scorable stocks per review", fs[1], fs[2]],
        ["80+ candidates: median", m1["candidates"]["80"]["stats"]["p50"], m2["candidates"]["80"]["stats"]["p50"]],
        ["80+ candidates: mean", m1["candidates"]["80"]["stats"]["mean"], m2["candidates"]["80"]["stats"]["mean"]],
        ["80+ share of eligible stock-months", m1["distributions"]["eligible"]["all"]["at_least"]["80"],
         m2["distributions"]["eligible"]["all"]["at_least"]["80"]],
        ["80+ zero-candidate months", m1["candidates"]["80"]["zero_months"], m2["candidates"]["80"]["zero_months"]],
        ["80+ median spell (months)", m1["persistence"]["80"]["run_months"]["p50"],
         m2["persistence"]["80"]["run_months"]["p50"]],
        ["80+ spells surviving 3 months", m1["persistence"]["80"]["survival"]["3"],
         m2["persistence"]["80"]["survival"]["3"]],
        ["80/H2/10 orders per year (frozen planner)", ch(m1, "80", "H2", "10")["orders_per_year"],
         ch(m2, "80", "H2", "10")["orders_per_year"]],
        ["80/H2/10 cost % ($100K)", ch(m1, "80", "H2", "10")["costs"]["100000"]["total_pct"],
         ch(m2, "80", "H2", "10")["costs"]["100000"]["total_pct"]],
        ["80/H2/10 mean utilisation", ch(m1, "80", "H2", "10")["utilisation"]["mean"],
         ch(m2, "80", "H2", "10")["utilisation"]["mean"]],
        ["80+ median largest-sector share", m1["sector_concentration"]["80"]["max_sector_share"].get("p50"),
         m2["sector_concentration"]["80"]["max_sector_share"].get("p50")],
        ["Provisional (regime limits) orders per year", pv1.get("orders_per_year"), pv2["orders_per_year"]],
        ["Provisional (regime limits) cost % ($100K)", (pv1.get("costs") or {}).get("100000", {}).get("total_pct"),
         pv2["costs"]["100000"]["total_pct"]],
        ["Provisional (regime limits) mean utilisation", (pv1.get("utilisation") or {}).get("mean"),
         pv2["utilisation"]["mean"]],
        ["Median total score (eligible)", m1["distributions"]["eligible"]["all"]["quantiles"]["p50"],
         m2["distributions"]["eligible"]["all"]["quantiles"]["p50"]],
        ["Market regime STRONG months", m1["regime"]["counts"].get("STRONG"), m2["regime"]["counts"].get("STRONG")],
    ]
    txt = json.dumps(out, indent=1, sort_keys=True, default=str)
    for bad in ("return", "cagr", "sharpe", "alpha", "drawdown", "forward"):
        assert bad not in txt.lower(), bad
    (HERE / "P7_CP3R_compare.json").write_text(txt + "\n")
    print(json.dumps(dict(consistency=out["consistency"], rescued_total=out["rescued"]["total"],
                          share=out["rescued"]["share_total"], reasons=out["rescued"]["reasons"],
                          regime=out["regime"]["identical"]), indent=0))
    for row in out["material"]:
        print(row)


if __name__ == "__main__":
    sys.exit(main())
