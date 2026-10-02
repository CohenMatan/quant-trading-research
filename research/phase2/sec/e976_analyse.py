"""Final yearly coverage tables and residual-bias inputs (D113, owner items 3/11/12/13) from the final canary E976-01
and the SEC-side residual audit (residual_audit.json). Output: research/phase2/sec/e976_results_<experiment>.json"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
import e970_parse  # noqa: E402
from e972_analyse import outcome  # noqa: E402
from qresearch.sec_edgar import SECClient  # noqa: E402

OUT = Path(__file__).parent


def main(exp="E976-02"):
    lines = e970_parse.lines(exp)
    c = json.loads("".join(l.split("|", 2)[2] for l in lines if l.startswith("QRC76")))
    est = {r["year"]: r for r in csv.DictReader(open(ROOT / "docs/data/survivorship_gap_X954_by_year.csv"))}
    cp6 = json.loads((OUT / "e972_results.json").read_text())["coverage_by_year"]
    resid = json.loads((OUT / "residual_audit.json").read_text())["by_year"]
    corr = json.loads((OUT / "corrections_v2.json").read_text())["links"]
    t = e970_parse.load()
    res = {"checks": {k: v for k, v in c.items() if k.startswith("C")}, "store_stats": c["store_stats"],
           "exchange_of_repaired_names (company-months)": c["exchange"],
           "visa_months_eligible": f"{sum(c['visa'].values())}/{len(c['visa'])}", "fin_flips": c["fin_flips_summary"],
           "quarantine_coverage_loss_stock_months": c["quarantine_lost"]}
    table = {}
    for y, v in sorted(c["coverage"].items()):
        g = lambda k: v.get(k, 0) / 12
        nat, rep = g("eligible_native"), g("eligible_corrected")
        r = resid.get(y, {})
        sec_missing = r.get("missing", 0)
        sec_possible = r.get("possible|missing", 0)
        excl = {k: round(g(f"cat_{k}_native") + g(f"cat_{k}_corrected"), 1) for k in ("financial", "REIT", "financial-format")}
        nonfin = g("nonfin_eligible_native") + g("nonfin_eligible_corrected")
        final = g("final_usable_native") + g("final_usable_corrected")
        ttm = {b: round((g(f"ttm_{b}_native") + g(f"ttm_{b}_corrected")) / (nat + rep), 4)
               for b in ("revenue", "gross_profit", "net_income", "operating_cash_flow")}
        usable = (g("usable_native") + g("usable_corrected")) / (nat + rep)
        table[y] = {
            "native_per_month": round(nat, 1), "sec_repaired_per_month": round(rep, 1),
            "sec_side_unresolved_float_ge_2B (registrants, year)": sec_missing,
            "sec_side_unresolved_float_1_2B (possible)": sec_possible,
            "estimated_historically_eligible_per_month": round(nat + rep + sec_missing + sec_possible, 1),
            "missing_share_after (upper bound incl. possible)": round((sec_missing + sec_possible) / (nat + rep + sec_missing + sec_possible), 4),
            "D043_estimate_missing_share_before": float(est[y]["missing share"]) if y in est else None,
            "P2_CP6_missing_share_after": cp6.get(y, {}).get("missing_share_after"),
            "usable_PIT_fundamentals_share": round(usable, 4),
            "usable_true_TTM_share_by_field": ttm,
            "excluded_per_month": excl,
            "non_financial_eligible_per_month": round(nonfin, 1),
            "final_usable_per_month (non-financial, approved TTM revenue/net income/OCF + assets/equity)": round(final, 1),
            "final_usable_coverage_of_non_financial": round(final / nonfin, 4) if nonfin else None,
            "quarantine_lost_stock_months": c["quarantine_lost"].get(y, 0),
            "non_financial_not_usable_per_month_by_reason": {k.split("|", 1)[1]: round(n / 12, 1)
                                                             for k, n in sorted(v.items()) if k.startswith("not_usable|")},
        }
    res["coverage_by_year"] = table
    res["sic_vs_structure (stock-months)"] = c["sic_vs_structure"]
    reasons = Counter()
    for k, n in c["ttm_reasons"].items():
        y, b, why = k.split("|", 2)
        if b == "revenue":
            reasons[why] += n
    res["no_true_TTM_reasons_revenue (stock-months)"] = dict(reasons)
    # outcomes of repaired companies that were ever eligible (characterisation only)
    client = SECClient()
    oc = Counter()
    for sid in c["corrected_first"]:
        ciks = [x["cik"] for x in corr.get(sid, [])]
        oc[outcome(client, ciks, t["nofund"][sid]["last_seen"])] += 1
    res["repaired_ever_eligible"] = len(c["corrected_first"])
    res["repaired_outcomes"] = dict(oc)
    ret = {}
    for k, v in c["ret"].items():
        if isinstance(v, list):
            grp, y = k.split("|")
            ret.setdefault(y, {})[grp] = {"stock_months": v[0], "mean_month_return_x12": round(12 * v[1] / v[0], 4)}
    for y, gr in ret.items():
        if "ttm_usable" in gr and "ttm_missing" in gr:
            gr["ttm_missing_share"] = round(gr["ttm_missing"]["stock_months"] / (gr["ttm_missing"]["stock_months"]
                                                                                + gr["ttm_usable"]["stock_months"]), 4)
        if "corrected" in gr and "native" in gr:
            sh = gr["corrected"]["stock_months"] / (gr["corrected"]["stock_months"] + gr["native"]["stock_months"])
            gr["repaired_share"] = round(sh, 4)
            gr["effect_of_repair_on_EW_universe_pp"] = round(
                100 * sh * (gr["corrected"]["mean_month_return_x12"] - gr["native"]["mean_month_return_x12"]), 2)
    res["composition_returns"] = dict(sorted(ret.items()))
    tot = {g: [sum(ret[y][g]["stock_months"] for y in ret if g in ret[y]),
               sum(ret[y][g]["stock_months"] * ret[y][g]["mean_month_return_x12"] for y in ret if g in ret[y])]
           for g in ("native", "corrected")}
    res["composition_returns_2010_2021"] = {g: round(v[1] / v[0], 4) for g, v in tot.items() if v[0]}
    # D113a: True-TTM missingness among non-financial eligible names (X976 v1.1 'T' lines) — who lacks TTM, by
    # outcome (the survivorship audit's own classification), group and reason; plus the same equal-weight universe
    # composition measure for names with / without usable TTM (characterisation, not a factor)
    T = [l.split("|") for l in lines if l.startswith("T|")]
    if T:
        tt = {g: [sum(ret[y][g]["stock_months"] for y in ret if g in ret[y]),
                  sum(ret[y][g]["stock_months"] * ret[y][g]["mean_month_return_x12"] for y in ret if g in ret[y])]
              for g in ("ttm_usable", "ttm_missing")}
        res["composition_returns_ttm_2010_2021"] = {g: round(v[1] / v[0], 4) for g, v in tt.items() if v[0]}
        by_out = defaultdict(lambda: [0, 0, 0])          # outcome -> [securities, eligible months, usable months]
        reasons = Counter()
        for _, sid, grp, n, u, why in T:
            if grp == "corrected":
                ciks = [x["cik"] for x in corr.get(sid, [])]
                last = t["nofund"][sid]["last_seen"]
            else:
                nat = t["native"].get(sid, {})
                ciks = [nat["cik"]] if nat.get("cik") else []
                ly, lm = divmod(nat.get("last", 202112), 100)
                last = date(ly + (lm == 12), lm % 12 + 1, 1) - timedelta(days=1)
            o = outcome(client, ciks, last)
            cell = by_out[o]
            cell[0] += 1
            cell[1] += int(n)
            cell[2] += int(u)
            for kv in filter(None, why.split(";")):
                k, v = kv.rsplit("=", 1)
                reasons[k] += int(v)
        res["ttm_missingness_by_outcome"] = {o: {"securities": v[0], "eligible_months": v[1], "usable_months": v[2],
                                                 "usable_share": round(v[2] / v[1], 4) if v[1] else None}
                                             for o, v in sorted(by_out.items())}
        res["ttm_missing_reasons (stock-months)"] = dict(reasons.most_common())
        terc = {}
        for y, v in c["coverage"].items():
            terc[y] = {tc: round(v.get(f"final_usable_{tc}", 0) / v[f"nonfin_eligible_{tc}"], 4)
                       for tc in ("T1", "T2", "T3") if v.get(f"nonfin_eligible_{tc}")}
        res["final_usable_share_by_size_tercile"] = terc
    (OUT / f"e976_results_{exp}.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


if __name__ == "__main__":
    r = main(*sys.argv[1:])
    print(json.dumps(r, indent=1, default=str)[:12000])
