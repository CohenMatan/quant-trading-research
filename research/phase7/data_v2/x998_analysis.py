"""P7-CP5f (D190): offline summary of the X998 Data v2 aggregate outputs and the freeze gates A-P.

Inputs are only the aggregate JSON each run published (counts, distributions, SHA-256 digests) plus the runner's own
record (result.json: status, LEAN build, orders); no vendor value, no return. Thresholds below were written and
committed BEFORE any E998 output was read (they restate the pre-registered P7-CP5e criteria MC2-MC7 and fix the
remaining D190 gates). Output: research/phase7/data_v2/x998_summary.json."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNS = {"E998-01": "export, full window", "E998-02": "export, full window (independent repeat)",
        "E998-03": "export, truncated at 2013-12-31", "E998-04": "power study, full window"}
V1_SURV = {"all": 0.8327, "2011": 0.7448, "2012": 0.783, "2013": 0.781, "2014": 0.7908, "2015": 0.8279,
           "2016": 0.9007, "2017": 0.9567}
# P7-CP5e residuals (E997-03, research/phase7/cp5e/x997_summary.json) for the "about the same range" re-check
CP5E = dict(recovered_pct=68.93, gap_all=0.79, agree_away=98.42, split_continuous=99.55, mcap_fresh=85.95,
            scored_mean={"2011": 355.4, "2012": 388.1, "2013+": 630.6}, ge80_per_review=7.07)
# (fix after E998-01, documented in P7-CP5f: these P7-CP5e means are X997 per_review column 5 = 'scored' (fully scored
# stocks), so they are compared with X998 'scored', not 'eligible'; the threshold is unchanged)
# freeze-gate thresholds (fixed before any E998 output was read)
TH = dict(MC2=75.0, MC3=95.0, MC4=97.0, MC5_dis=30.0, MC5_rel=0.05, MC6=60.0, MC7_all=2.0, MC7_year=4.0,
          residual_recovery=(60.0, 78.0), residual_population_rel=0.15, min_scored_2011_2012=200,
          min_scored_any=20, identity_bias_points=1.0, identity_excluded_share_year=0.03)
AUDIT_ZERO = ("fed_before_sec_filing", "fed_before_first_seen", "future_identity_row", "fed_after_guard_trigger",
              "stale_share_count_used", "share_filing_not_yet_public", "repaired_with_vendor_cap", "repaired_below_2B",
              "record_older_than_200d", "baseline_pit_violations", "baseline_used_despite_reject")
TIMING = ("wall_s", "score_s", "power_s", "max_rss_mb", "store_stats")


def load(eid):
    p = ROOT / "experiments" / eid / "messages.txt"
    if not p.exists():
        return None
    parts = sorted((ln for ln in p.read_text().splitlines() if ln.startswith("QRV2|")), key=lambda ln: int(ln.split("|")[1]))
    return json.loads("".join(ln.split("|", 2)[2] for ln in parts)) if parts else None


def record(eid):
    p = ROOT / "experiments" / eid / "result.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text())
    pv = r.get("provenance", {})
    return dict(status=r.get("status"), lean_version=pv.get("lean_version"), git_commit=pv.get("git_commit"),
                qc_backtest_id=pv.get("qc_backtest_id"), holdout_unlocked=pv.get("holdout_unlocked"), orders=r.get("harness_summary", {}).get("orders"),
                runtime_s=pv.get("runtime_s"), integrity_ok=all(c.get("ok") for c in r.get("integrity", [])
                                                                if c.get("level") == "fail"))


def pct(a, b):
    return None if not b else round(100.0 * a / b, 2)


def strip(s):
    out = {k: v for k, v in s.items() if k not in TIMING}
    out["repair"] = {k: v for k, v in s["repair"].items() if k != "repair_s"}
    if "panel" in out:                      # panel build time is a timing field (E998-02: 90.7 s vs 86.5 s)
        out["panel"] = {k: v for k, v in s["panel"].items() if k != "build_s"}
    return out


def survivorship(s):
    tot, surv = {}, {}
    for y, g in sorted(s["survivorship"].items()):
        surv[y] = {k: dict(stock_months=v[0], survivor_share=round(v[1] / v[0], 4) if v[0] else None) for k, v in g.items()}
        for k, v in g.items():
            t = tot.setdefault(k, [0, 0])
            t[0] += v[0]
            t[1] += v[1]
    surv["all"] = {k: dict(stock_months=v[0], survivor_share=round(v[1] / v[0], 4) if v[0] else None) for k, v in tot.items()}
    gap = {y: round(100 * (surv[y]["v2_universe"]["survivor_share"] - V1_SURV[y]), 2) for y in V1_SURV if y in surv}
    return surv, gap


def identity_sanity(s, surv):
    i = s["identity_sanity"]
    by = {}
    for y, g in sorted(i["by_year"].items()):
        el = surv[y]["v2_universe"]["stock_months"]
        by[y] = dict(g, eligible=el, excluded_share=round(g["affected_eligible"] / el, 4) if el else None)
    a, r = i["affected_survival"], i["retained_survival"]
    n_a, n_r = i["affected_stock_months"], i["retained_fully_scorable_stock_months"]
    bias = None if a is None or r is None else round(100 * n_a / (n_a + n_r) * (r - a), 3)
    return dict(i, by_year=by, survival_difference_points=None if a is None or r is None else round(100 * (r - a), 2),
                implied_scored_population_bias_points=bias)


def summarise(s):
    surv, gap = survivorship(s)
    cm, rec, mc2, split = s["mcap_comparison"], s["target_recovery_by_reason"], s["target_mcap_missing_status"], s["sec_split_check"]
    lost, recovered = sum(v[0] for v in rec.values()), sum(v[1] for v in rec.values())
    nonsurv_lost = surv["all"]["lost"]["stock_months"] * (1 - surv["all"]["lost"]["survivor_share"])
    nonsurv_rec = sum(v[2] for v in rec.values())
    mc2_n = sum(v[0] for v in mc2.values())
    fresh = sum(v[0] for k, v in mc2.items() if k in ("repaired", "below_2B"))
    ev = sum(v for k, v in split.items() if k in ("continuous", "jumps_with_price", "ambiguous"))
    pr = [dict(zip(s["per_review_cols"], r)) for r in s["per_review"]]

    def pop(rows, key):
        xs = sorted(r[key] for r in rows)
        return None if not xs else dict(months=len(xs), min=xs[0], median=xs[len(xs) // 2],
                                         mean=round(sum(xs) / len(xs), 1), max=xs[-1])
    grp = {"2011": [r for r in pr if r["review"] < "2012"], "2012": [r for r in pr if "2012" <= r["review"] < "2013"],
           "2013+": [r for r in pr if r["review"] >= "2013"], "all": pr}
    yr = {}
    for y, a in sorted(s["per_year"].items()):
        n = a["reviews"]
        yr[y] = dict(reviews=n, eligible_mean=round(a["eligible"] / n, 1), from_qc_cap_mean=round(a["from_qc_cap"] / n, 1),
                     from_sec_repair_mean=round(a["from_sec_repair"] / n, 1),
                     from_v1_sec_layer_mean=round(a["from_v1_sec_layer"] / n, 1), nonfin_mean=round(a["nonfin"] / n, 1),
                     h2_pct_nonfin=pct(a["h2_nonfin"], a["nonfin"]), scored_mean=round(a["scored"] / n, 1),
                     candidates_mean=round(a["candidates"] / n, 1),
                     ge75_mean=round(a["ge75"] / n, 2), ge80_mean=round(a["ge80"] / n, 2), ge85_mean=round(a["ge85"] / n, 2),
                     ge90_mean=round(a["ge90"] / n, 2), mappable_pct=pct(a["mappable_v2"] + a["mappable_ext"], a["eligible"]),
                     mappable_ext=a["mappable_ext"], field_present_pct=[pct(x, a["nonfin"]) for x in a["field_present"]],
                     h_bits=a["bits"])
    guard = s["restatement_guard"]
    blocked = sum(v for k, v in guard.items() if k.startswith("blocked|"))
    return dict(
        digests_sha256=hashlib.sha256(json.dumps(s["digests"], sort_keys=True).encode()).hexdigest(), digests=s["digests"],
        target_check=s["target_check"], checks=s["checks"], repair=s["repair"], pit_audit=s["pit_audit"],
        criteria=dict(MC2_fresh_sec_mcap_pct=pct(fresh, mc2_n), MC3_split_continuous_pct=pct(split.get("continuous", 0), ev),
                      MC3_evaluable=ev, MC4_agreement_away_pct=pct(cm["agree_away"], cm["n_away"]),
                      MC5_disagreement_near_pct=None if not cm["n_near"] else round(100 - pct(cm["agree_near"], cm["n_near"]), 2),
                      MC5_abs_rel_median=cm["abs_rel_median"], MC6_recovered_pct=pct(recovered, lost),
                      MC6_recovered_later_disappearing_pct=pct(nonsurv_rec, nonsurv_lost), MC7_gap_points=gap),
        recovery_by_reason=rec, mcap_missing_status=mc2, mcap_comparison=cm, split=split, survivorship=surv,
        target_securities=s["target_securities"], per_year=yr,
        population={k: dict(eligible=pop(v, "eligible"), scored=pop(v, "scored"), candidates=pop(v, "candidates"),
                            ge80=pop(v, "ge80")) for k, v in grp.items()},
        ge80_per_review=round(sum(r["ge80"] for r in pr) / len(pr), 2), months_ge80_zero=sum(1 for r in pr if r["ge80"] == 0),
        regimes=s["regimes"], sectors_80plus=s["sectors_80plus"], totals_candidates=s["totals_candidates"],
        totals_scored=s["totals_scored"], totals_hist5_candidates=s["totals_hist5_candidates"],
        totals_hist5_scored=s["totals_hist5_scored"], layers=s["layers"], layer_corr=s["layer_corr"],
        identity_mapping=s["identity_mapping"], identity_value_check=s["identity_value_check"],
        restatement_guard=dict(categories=guard, blocked=blocked, fed=s["checks"]["fed"],
                               blocked_pct_of_matched=pct(blocked, blocked + s["checks"]["fed"] + s["checks"]["m2_revision_unfed"])),
        identity_sanity=identity_sanity(s, surv), baseline=s["baseline"], spot=s["slice_spot_check"],
        mechanics=s["mechanics"], weekly_checks=s["weekly_checks"], wall_s=s["wall_s"], max_rss_mb=s["max_rss_mb"])


def truncation(a, c):
    da, dc = a["digests"], c["digests"]
    common = sorted(set(da["review_scores"]) & set(dc["review_scores"]))
    return dict(reviews_compared=len(common),
                review_scores_equal=sum(da["review_scores"][t] == dc["review_scores"][t] for t in common),
                review_eligibility_equal=sum(da["review_eligibility"][t] == dc["review_eligibility"][t] for t in common),
                ledger_to_2013_equal=da["ledger_to_2013"] == dc["ledger_to_2013"],
                ledger_years_equal={y: da["ledger_by_year"].get(y) == dc["ledger_by_year"][y] for y in dc["ledger_by_year"]},
                # (fix after E998-03, documented in P7-CP5f: a run ending 2013-12-31 never reaches its December review,
                # stamped 2014-01-01, so a whole-year digest is comparable only for years whose review sets are equal;
                # the partial year is covered review by review by review_eligibility / review_scores above)
                universe_years_equal={y: da["universe_by_year"].get(y) == dc["universe_by_year"][y] for y in dc["universe_by_year"]
                                      if sorted(t for t in da["review_scores"] if t[:4] == y) ==
                                      sorted(t for t in dc["review_scores"] if t[:4] == y)},
                universe_years_partial=sorted(y for y in dc["universe_by_year"]
                                              if sorted(t for t in da["review_scores"] if t[:4] == y) !=
                                              sorted(t for t in dc["review_scores"] if t[:4] == y)),
                per_review_equal=sum(x == y for x, y in zip(a["per_review"], c["per_review"])), per_review_compared=len(c["per_review"]))


def gates(out, st, rec):
    s1 = out.get("E998-01")
    if not isinstance(s1, dict):
        return {"all": False, "reason": "E998-01 has no aggregate output"}
    c = s1["criteria"]
    g = {}
    g["A_score_v1_hash"] = "checked by tests/test_p7_score_spec.py and test_p7_pred_spec.py (pinned hashes unchanged)"
    pa = {e: out[e]["pit_audit"] for e in ("E998-01", "E998-02", "E998-03", "E998-04") if isinstance(out.get(e), dict)}
    g["B_m2_timing"] = all(p["fed_before_sec_filing"] == 0 and p["fed_before_first_seen"] == 0 for p in pa.values())
    g["C_market_cap_repair"] = (c["MC2_fresh_sec_mcap_pct"] >= TH["MC2"] and c["MC4_agreement_away_pct"] >= TH["MC4"]
                                and c["MC5_disagreement_near_pct"] <= TH["MC5_dis"] and c["MC5_abs_rel_median"] <= TH["MC5_rel"]
                                and c["MC6_recovered_pct"] >= TH["MC6"] and c["MC6_recovered_later_disappearing_pct"] >= TH["MC6"])
    # (relabelled after E998-01, documented in P7-CP5f: the owner's gate D is "SEC identity extension implemented
    # exactly"; the D190 item-7 identity sanity check is a survivorship STOP condition and is evaluated under gate K with
    # the SAME pre-set criteria)
    ids = s1["identity_sanity"]
    g["D_identity"] = all(p["future_identity_row"] == 0 for p in pa.values())
    g["K_identity_sanity_not_material"] = (ids["implied_scored_population_bias_points"] is not None
                                           and abs(ids["implied_scored_population_bias_points"]) <= TH["identity_bias_points"]
                                           and all((v["excluded_share"] or 0) <= TH["identity_excluded_share_year"]
                                                   for v in ids["by_year"].values()))
    g["E_restatement_guard"] = all(p["fed_after_guard_trigger"] == 0 for p in pa.values()) and s1["restatement_guard"]["blocked"] >= 0
    g["F_pit_zero"] = all(all(p[k] == 0 for k in AUDIT_ZERO) for p in pa.values())
    g["G_splits"] = c["MC3_split_continuous_pct"] >= TH["MC3"]
    d = out.get("determinism_E998_01_vs_02")
    g["H_determinism"] = bool(d and d["digests_equal"] and d["aggregates_equal"])
    t = out.get("truncation_E998_01_vs_03")
    g["I_truncation"] = bool(t and t["reviews_compared"] > 0 and t["review_scores_equal"] == t["reviews_compared"]
                             and t["review_eligibility_equal"] == t["reviews_compared"] and t["ledger_to_2013_equal"]
                             and all(t["universe_years_equal"].values()) and t["per_review_equal"] == t["per_review_compared"])
    p11 = [r for r in st["E998-01"]["per_review"] if r[0] < "2013"]
    cols = st["E998-01"]["per_review_cols"]
    isc = cols.index("scored")
    g["J_2011_2012_operational"] = (len(p11) == 24 and min(r[isc] for r in p11) >= TH["min_scored_2011_2012"]
                                    and min(r[isc] for r in st["E998-01"]["per_review"]) >= TH["min_scored_any"])
    gap = c["MC7_gap_points"]
    g["K_mc7_survivor_gap_within_bounds"] = (abs(gap["all"]) <= TH["MC7_all"] and all(abs(v) <= TH["MC7_year"] for v in gap.values()))
    g["K_residuals_same_range"] = residuals(s1)["same_range"]
    g["K_survivorship_bounds"] = (g["K_mc7_survivor_gap_within_bounds"] and g["K_identity_sanity_not_material"]
                                  and g["K_residuals_same_range"])
    g["L_compliance"] = all(r and r["status"] == "completed" for r in rec.values())
    mech = s1["mechanics"]["rule_checks"]
    g["M_export"] = (all(isinstance(out.get(e), dict) for e in RUNS) and all(v == 0 for k, v in mech.items() if k != "max_holdings_le_K")
                     and mech.get("max_holdings_le_K") is True and all(r and r["orders"] == 0 for r in rec.values()))
    g["N_no_real_return"] = "by construction: X998 computes no forward / portfolio / SPY return (tests/test_data_v2.py)"
    g["O_2018_2021_untouched"] = all(json.loads((ROOT / "experiments" / e / "config.json").read_text())["end"] <= "2017-12-31" for e in RUNS)
    g["P_holdout_untouched"] = not (ROOT / "HOLDOUT_UNLOCK.md").exists() and all(r and r["status"] and not r.get("holdout_unlocked")
                                                                              for r in rec.values())
    g["all"] = all(v is True or isinstance(v, str) for k, v in g.items())
    return g


def residuals(s1):
    c = s1["criteria"]
    pop = s1["population"]
    rel = {k: round(pop[k]["scored"]["mean"] / CP5E["scored_mean"][k] - 1, 4) for k in ("2011", "2012", "2013+")}
    lo, hi = TH["residual_recovery"]
    return dict(cp5e=CP5E, recovered_pct=c["MC6_recovered_pct"], gap_all=c["MC7_gap_points"]["all"],
                agree_away=c["MC4_agreement_away_pct"], split_continuous=c["MC3_split_continuous_pct"],
                mcap_fresh=c["MC2_fresh_sec_mcap_pct"], scored_mean_rel_change=rel, ge80_per_review=s1["ge80_per_review"],
                same_range=(lo <= c["MC6_recovered_pct"] <= hi and abs(c["MC7_gap_points"]["all"]) <= TH["MC7_all"]
                            and all(abs(v) <= TH["residual_population_rel"] for v in rel.values())))


def main():
    st = {e: load(e) for e in RUNS}
    rec = {e: record(e) for e in RUNS}
    out = {e: (summarise(s) if s else "no aggregate output") for e, s in st.items()}
    out["records"] = rec
    if st["E998-01"] and st["E998-02"]:
        a, b = strip(st["E998-01"]), strip(st["E998-02"])
        out["determinism_E998_01_vs_02"] = dict(
            digests_equal=a["digests"] == b["digests"], digest_keys=sorted(a["digests"]),
            aggregates_equal=all(a[k] == b[k] for k in a if k not in ("digests",)),
            unequal_keys=sorted(k for k in a if a[k] != b.get(k)))
    if st["E998-01"] and st["E998-03"]:
        out["truncation_E998_01_vs_03"] = truncation(st["E998-01"], st["E998-03"])
    if st["E998-01"] and st["E998-04"]:
        a, p = strip(st["E998-01"]), strip(st["E998-04"])
        out["E998_04_export_part_equals_E998_01"] = a["digests"] == p["digests"]
        out["power"] = st["E998-04"].get("power")
    if isinstance(out.get("E998-01"), dict):
        out["residual_recheck"] = residuals(out["E998-01"])
        out["freeze_gates"] = gates(out, st, rec)
    (Path(__file__).parent / "x998_summary.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("freeze_gates", "residual_recheck", "determinism_E998_01_vs_02",
                                          "truncation_E998_01_vs_03") if k in out}, indent=1, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
