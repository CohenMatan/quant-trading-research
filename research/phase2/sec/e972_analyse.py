"""Coverage and bias re-audit after the D043 repair (D111, owner items 9-10), from the final canary E972-02.

Coverage: per year, native eligible names (vendor data), names recovered by the SEC correction layer, the D043
estimate of missing >= $2B companies (X954, docs/data/survivorship_gap_X954_by_year.csv), the remaining estimated
gap, usable-record coverage. Outcomes of recovered companies from their own SEC filings: 'failed' if an 8-K item
1.03 (bankruptcy) was filed in the two years before the last trade, else 'acquired/other' if trading ended before
2021-11, else 'still trading'. Composition returns: equal-weight next-month returns of recovered vs native eligible
names (the D043 bias measure; universe composition, no ranking, no factor). Output: e972_results.json."""
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
from qresearch.sec_edgar import SECClient, filings_table  # noqa: E402
import e970_parse  # noqa: E402

OUT = Path(__file__).parent


def summary(exp):
    lines = e970_parse.lines(exp)
    txt = "".join(l.split("|", 2)[2] for l in lines if l.startswith("QRC72"))
    return json.loads(txt), lines


def outcome(client, ciks, last_trade):
    if last_trade >= date(2021, 11, 1):
        return "still trading"
    lo = (last_trade - timedelta(days=730)).isoformat()
    for cik in ciks:
        sub = client.submissions(int(cik))
        if not sub:
            continue
        for r in filings_table(sub):
            if r["form"].startswith("8-K") and "1.03" in str(r.get("items") or "") and lo <= r["filingDate"] <= \
                    (last_trade + timedelta(days=60)).isoformat():
                return "failed (bankruptcy 8-K item 1.03)"
    return "acquired/other"


def main(exp="E972-02"):
    c, lines = summary(exp)
    est = {r["year"]: r for r in csv.DictReader(open(ROOT / "docs/data/survivorship_gap_X954_by_year.csv"))}
    corr = json.loads((OUT / "corrections.json").read_text())
    t = e970_parse.load()
    res = {"checks": {k: v for k, v in c.items() if k.startswith("C")}, "store_stats": c["store_stats"],
           "exchange_of_recovered_names (company-months)": c["exchange"], "visa_months_eligible":
           f"{sum(c['visa'].values())}/{len(c['visa'])}", "fin_flips": c["fin_flips_summary"],
           "quarantine_coverage_loss_stock_months": c["quarantine_lost"]}
    cov = {}
    for y, v in sorted(c["coverage"].items()):
        nat, cor = v.get("eligible_native", 0) / 12, v.get("eligible_corrected", 0) / 12
        e = float(est[y]["est. missing >= $2B"]) if y in est else None
        rem = max(e - cor, 0.0) if e is not None else None
        cov[y] = {
            "native_eligible_per_month": round(nat, 1), "recovered_per_month": round(cor, 1),
            "D043_estimated_missing_per_month": e,
            "share_of_estimated_gap_repaired": round(min(cor / e, 1.0), 3) if e else None,
            "remaining_estimated_missing_per_month": round(rem, 1) if rem is not None else None,
            "missing_share_before (D043 published)": float(est[y]["missing share"]) if y in est else None,
            "missing_share_after": round(rem / (nat + cor + rem), 3) if e else None,
            "usable_record_coverage_native": round(v.get("usable_native", 0) / max(v.get("eligible_native", 1), 1), 4),
            "usable_record_coverage_recovered": round(v.get("usable_corrected", 0) / v["eligible_corrected"], 4)
            if v.get("eligible_corrected") else None,
            "financial_format_excluded_recovered": v.get("financial_format_corrected", 0),
        }
    res["coverage_by_year"] = cov
    # size of recovered names (stock-months by universe market-cap tercile)
    size = defaultdict(Counter)
    for k, n in c["size"].items():
        y, terc, grp = k.split("|")
        size[grp][terc] += n
    res["size_terciles_stock_months"] = {g: dict(v) for g, v in size.items()}
    # outcomes of recovered companies (eligible at least once)
    client = SECClient()
    oc = Counter()
    oc_by = defaultdict(Counter)
    detail = []
    for sid in c["corrected_first"]:
        links = corr.get(sid, [])
        ciks = [x["cik"] for x in links]
        lt = t["nofund"][sid]["last_seen"]
        o = outcome(client, ciks, lt)
        oc[o] += 1
        for y in range(int(c["corrected_first"][sid][:4]), int(c["corrected_last"][sid][:4]) + 1):
            oc_by[str(y)][o] += 1
        detail.append([sid, links[0]["names"][0] if links else "?", c["corrected_first"][sid], c["corrected_last"][sid],
                       str(lt), o, links[0]["confidence"] if links else "?"])
    res["recovered_companies_ever_eligible"] = len(detail)
    res["recovered_outcomes"] = dict(oc)
    res["recovered_outcomes_by_year (companies eligible that year)"] = {y: dict(v) for y, v in sorted(oc_by.items())}
    res["recovered_detail"] = sorted(detail, key=lambda r: r[2])
    # composition returns (EW next-month, average per stock-month, x12)
    ret = {}
    for k, v in c["ret"].items():
        if isinstance(v, list):
            grp, y = k.split("|")
            ret.setdefault(y, {})[grp] = {"stock_months": v[0], "mean_month_return_x12": round(12 * v[1] / v[0], 4)}
    for y, g in ret.items():
        if "corrected" in g and "native" in g:
            sh = g["corrected"]["stock_months"] / (g["corrected"]["stock_months"] + g["native"]["stock_months"])
            g["recovered_share"] = round(sh, 4)
            g["effect_of_repair_on_EW_universe_pp"] = round(
                100 * sh * (g["corrected"]["mean_month_return_x12"] - g["native"]["mean_month_return_x12"]), 2)
    res["composition_returns"] = dict(sorted(ret.items()))
    tot = {g: [sum(ret[y][g]["stock_months"] for y in ret if g in ret[y]),
               sum(ret[y][g]["stock_months"] * ret[y][g]["mean_month_return_x12"] for y in ret if g in ret[y])]
           for g in ("native", "corrected")}
    res["composition_returns_2010_2021"] = {g: round(v[1] / v[0], 4) for g, v in tot.items()}
    res["ended_in_month_counts"] = {k: v for k, v in c["ret"].items() if not isinstance(v, list)}
    (OUT / "e972_results.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    return res


if __name__ == "__main__":
    r = main(sys.argv[1] if len(sys.argv) > 1 else "E972-02")
    print(json.dumps({k: v for k, v in r.items() if k != "recovered_detail"}, indent=1, default=str))
