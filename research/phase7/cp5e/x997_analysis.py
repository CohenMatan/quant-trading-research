"""P7-CP5e (D188): offline summary of the X997 aggregate outputs (E997-01 identity extended, E997-02 identity-v2 only)
against the pre-registered criteria (P7_CP5e_preregistration.md). Inputs are only the aggregate JSON each run published
(counts, distributions, SHA-256 digests); no vendor value, no return. Output: research/phase7/cp5e/x997_summary.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNS = {"E997-01": "identity extended", "E997-02": "identity v2 only"}
V1_SURV = {"all": 0.8327, "2011": 0.7448, "2012": 0.783, "2013": 0.781, "2014": 0.7908, "2015": 0.8279,
           "2016": 0.9007, "2017": 0.9567}


def load(eid):
    p = ROOT / "experiments" / eid / "messages.txt"
    if not p.exists():
        return None
    parts = sorted((ln for ln in p.read_text().splitlines() if ln.startswith("QRP5E|")),
                   key=lambda ln: int(ln.split("|")[1]))
    return json.loads("".join(ln.split("|", 2)[2] for ln in parts)) if parts else None


def pct(a, b):
    return None if not b else round(100.0 * a / b, 2)


def pop_stats(rows):
    xs = sorted(r[5] for r in rows)
    if not xs:
        return None
    return dict(months=len(xs), min=xs[0], median=xs[len(xs) // 2], mean=round(sum(xs) / len(xs), 1), max=xs[-1])


def summarise(s):
    sv = s["survivorship"]
    surv = {}
    tot = {}
    for y, g in sorted(sv.items()):
        surv[y] = {k: dict(stock_months=v[0], survivor_share=round(v[1] / v[0], 4) if v[0] else None)
                   for k, v in g.items()}
        for k, v in g.items():
            t = tot.setdefault(k, [0, 0])
            t[0] += v[0]
            t[1] += v[1]
    surv["all"] = {k: dict(stock_months=v[0], survivor_share=round(v[1] / v[0], 4) if v[0] else None)
                   for k, v in tot.items()}
    mc7 = {y: round(100 * (surv[y]["repaired_universe"]["survivor_share"] - V1_SURV[y]), 2) for y in V1_SURV}
    pr = s["per_review"]
    yr = s["per_year"]
    cov = {}
    for y, a in sorted(yr.items()):
        cov[y] = dict(eligible_mean=round(a["eligible"] / a["reviews"], 1), repaired_mean=round(a["repaired"] / a["reviews"], 1),
                      h2_pct_nonfin=pct(a["h2_nonfin"], a["nonfin"]),
                      h2_pct_nonfin_repaired=pct(a["h2_repaired_nonfin"], a["nonfin_repaired"]),
                      mappable_pct=pct(a["mappable_v2"] + a["mappable_ext"], a["eligible"]),
                      mappable_ext=a["mappable_ext"], scored_mean=round(a["scored"] / a["reviews"], 1),
                      candidates_mean=round(a["candidates"] / a["reviews"], 1), ge80_mean=round(a["ge80"] / a["reviews"], 2),
                      field_present_pct=[pct(x, a["nonfin"]) for x in a["field_present"]])
    cm = s["mcap_comparison"]
    rec = s["target_recovery_by_reason"]
    lost = sum(v[0] for v in rec.values())
    recovered = sum(v[1] for v in rec.values())
    nonsurv_lost = surv["all"]["lost"]["stock_months"] * (1 - surv["all"]["lost"]["survivor_share"])
    nonsurv_rec = sum(v[2] for v in rec.values())
    mc2 = s["target_mcap_missing_status"]
    mc2_n = sum(v[0] for v in mc2.values())
    fresh = sum(v[0] for k, v in mc2.items() if k in ("repaired", "below_2B"))
    split = s["sec_split_check"]
    ev = sum(v for k, v in split.items() if k in ("continuous", "jumps_with_price", "ambiguous"))
    return dict(
        target_check=s["target_check"], checks=s["checks"], repair=s["repair"],
        criteria=dict(
            MC2_fresh_sec_mcap_pct_of_mcap_missing_targets=pct(fresh, mc2_n),
            MC3_split_continuous_pct=pct(split.get("continuous", 0), ev), MC3_evaluable=ev,
            MC4_agreement_away_pct=pct(cm["agree_away"], cm["n_away"]),
            MC5_disagreement_near_pct=None if not cm["n_near"] else round(100 - pct(cm["agree_near"], cm["n_near"]), 2),
            MC5_abs_rel_median=cm["abs_rel_median"],
            MC6_recovered_pct=pct(recovered, lost), MC6_recovered_later_disappearing_pct=pct(nonsurv_rec, nonsurv_lost),
            MC7_survivor_share_gap_points=mc7),
        mcap_missing_status=mc2, recovery_by_reason=rec, mcap_comparison=cm, split=split, survivorship=surv,
        coverage=cov, population=dict(y2011=pop_stats([r for r in pr if r[0] < "2012"]),
                                      y2012=pop_stats([r for r in pr if "2012" <= r[0] < "2013"]),
                                      y2013plus=pop_stats([r for r in pr if r[0] >= "2013"]),
                                      all=pop_stats(pr)),
        ge80_per_review=round(sum(r[8] for r in pr) / len(pr), 2), months_ge80_zero=sum(1 for r in pr if r[8] == 0),
        identity_mapping=s["identity_mapping"], identity_value_check=s["identity_value_check"],
        totals_candidates=s["totals_candidates"], layers={k: v["stats"] for k, v in s["layers"].items()},
        layer_corr=s["layer_corr"], baseline=s["baseline"], spot=s["slice_spot_check"], wall_s=s["wall_s"],
        max_rss_mb=s["max_rss_mb"])


def id2(s):
    out = {}
    for k, v in s["identity_value_check"].items():
        src, fld, cat = k.split("|")
        d = out.setdefault(f"{src}|{fld}", {})
        d[cat] = v
    for d in out.values():
        n = d.get("match", 0) + d.get("differ", 0)
        d["match_pct"] = pct(d.get("match", 0), n)
    return out


def main():
    st = {e: load(e) for e in RUNS}
    out = {e: (summarise(s) if s else "no aggregate output") for e, s in st.items()}
    if st["E997-01"]:
        out["E997-01"]["identity_value_rates"] = id2(st["E997-01"])
    if st["E997-01"] and st["E997-02"]:
        a, b = st["E997-01"], st["E997-02"]
        out["determinism_universe_digests_equal"] = a["digests"]["universe_by_year"] == b["digests"]["universe_by_year"]
    (Path(__file__).parent / "x997_summary.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1, sort_keys=True)[:30000])


if __name__ == "__main__":
    sys.exit(main())
