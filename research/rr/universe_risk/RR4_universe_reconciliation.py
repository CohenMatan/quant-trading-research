"""RR4 universe-risk reconciliation (D265 item 4): offline, committed aggregates only.

No QuantConnect run, no new export, no network. Inputs are aggregates already in the repository:
  - E804-01 (RR3, build 18194, vendor market cap only): yearly E / M / UA / Nx counts and E exit rates;
  - Data v1 (E993-02, old dataset + SEC correction layer, SEC-measured residual 0.5-1.2 % a year, P2-CP7):
    eligible stock-months per year 2011-2017, rebuilt from the E996-01 universe-migration table (P7-CP5d);
  - E996-01 (build 18178): why Data v1 members were not eligible on the new feed, per year;
  - Data v2 / v2.1 (E998-01 / E801-01, build 18178, vendor cap + D111 SEC cap repair + v1 SEC layer).
All four use the same conceptual rule (US common, NYSE/Nasdaq/AMEX, PIT market cap >= $2B, price >= $5,
ADV20 >= $5M, month-end reviews), so their yearly stock-month counts are comparable as aggregates.

Fixed reading rules (descriptive; nothing here is a gate):
  shortfall_v1(y)   = DataV1(y) - E804_E(y)            (net; E804-only names offset it, so gross >= net)
  measured_by_RR3   = E804 M(y)  (structural common, cap missing; UA = its liquidity-matched part)
  not_measured(y)   = shortfall_v1(y) - M(y)           (sits in no-fundamentals / blank-field / cap<$2B /
                                                        override categories RR3 could not see)
  S1 'pessimistic'  : the 18178 no-fundamentals group (Data v1 members never repaired, P7-CP5e) is still
                      absent on 18194 and hidden in Nx: Gap_S1 = (UA + NF) / (E + UA + NF)
  G-SURV break-even : the exit-rate excess over E that a hidden share s would need to lift the universe exit
                      rate by 0.50 points: d* = 0.005 * (1 + s) / s   (24-month years)
Output: research/rr/universe_risk/RR4_universe_reconciliation.json"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_suffix(".json")
YEARS = [str(y) for y in range(2010, 2022)]


def e804():
    res = {}
    for line in (ROOT / "research/rr/universe_baseline/E804-01_ub_lines.txt").read_text().splitlines():
        if line.startswith("UB|year|"):
            y = line.split("|")[2]
            if y in YEARS:
                res[y] = json.loads(line.split("|", 3)[3])
    return res


def data_v1_and_migration():
    mig = json.loads((ROOT / "research/phase7/cp5d/x996_summary.json").read_text())["E996-01"]["universe_migration"]
    v1, why = {}, {}
    for k, n in mig.items():
        y, kind, *reason = k.split("|")
        if kind in ("both", "old_only"):
            v1[y] = v1.get(y, 0) + n
        why.setdefault(y, {})[kind + ("|" + reason[0] if reason else "")] = n
    return v1, why


def data_v2():
    out = {}
    pv = json.loads((ROOT / "research/phase7/data_v2/x998_summary.json").read_text())["E998-01"]["per_year"]
    for y, p in pv.items():
        n = p["reviews"]
        out[y] = {k: round(p[k + "_mean"] * n) for k in ("eligible", "from_qc_cap", "from_sec_repair", "from_v1_sec_layer")}
    pp = json.loads((ROOT / "research/phase11/data_v21/x801_summary.json").read_text())["per_period"]
    for y in ("2018", "2019", "2020", "2021"):
        out[y] = {k: pp[y][k] for k in ("eligible", "from_qc_cap", "from_sec_repair", "from_v1_sec_layer")}
    return out


def main():
    E = e804()
    v1, why = data_v1_and_migration()
    v2 = data_v2()
    x997 = json.loads((ROOT / "research/phase7/cp5e/x997_summary.json").read_text())["E997-03"]
    rows = {}
    for y in YEARS:
        c, s = E[y]["counts"], E[y]["survivorship"]
        e, m, ua = c["E"]["stock_months"], c["M"]["stock_months"], c["UA"]["stock_months"]
        r = {"E804_E": e, "E804_M": m, "E804_UA": ua, "E804_Nx": c["Nx"]["stock_months"],
             "E804_gap_A": round(ua / (e + ua), 4),
             "E804_E_exit_rate": (s.get("exit_rates", {}).get("E") or {}).get("rate"), "horizon": s.get("horizon")}
        if y in v1:
            nf = why[y].get("old_only|no_fundamentals", 0)
            r.update(data_v1=v1[y], shortfall_v1=v1[y] - e, shortfall_v1_pct=round((v1[y] - e) / v1[y], 4),
                     not_measured_by_RR3=v1[y] - e - m, not_measured_pct=round((v1[y] - e - m) / v1[y], 4),
                     nofund_18178=nf, gap_S1=round((ua + nf) / (e + ua + nf), 4))
            sh = nf / e
            r["gsurv_breakeven_excess_exit"] = round(0.005 * (1 + sh) / sh, 3) if sh else None
        if y in v2:
            r.update(data_v2x=v2[y], shortfall_v2x=v2[y]["eligible"] - e,
                     shortfall_v2x_pct=round((v2[y]["eligible"] - e) / v2[y]["eligible"], 4))
        rows[y] = r
    tot = lambda k, ys: sum(rows[y][k] for y in ys)
    p1 = [str(y) for y in range(2011, 2018)]
    res = {"by_year": rows,
           "totals_2011_2017": {"data_v1": tot("data_v1", p1), "E804_E": tot("E804_E", p1),
                                "shortfall_v1": tot("shortfall_v1", p1), "E804_M": tot("E804_M", p1),
                                "not_measured_by_RR3": tot("not_measured_by_RR3", p1),
                                "nofund_18178": tot("nofund_18178", p1)},
           "nofund_group_18178": {"stock_months": x997["recovery_by_reason"]["no_fundamentals"][0],
                                  "recovered_by_v2_repair": x997["recovery_by_reason"]["no_fundamentals"][1],
                                  "securities_never_recovered": {
                                      k.split("|", 1)[1]: v for k, v in
                                      x997["target_securities"]["never_recovered_by_last_reason"].items()
                                      if k.startswith("no_fundamentals")}},
           "inputs": ["research/rr/universe_baseline/E804-01_ub_lines.txt", "research/phase7/cp5d/x996_summary.json",
                      "research/phase7/cp5e/x997_summary.json", "research/phase7/data_v2/x998_summary.json",
                      "research/phase11/data_v21/x801_summary.json"]}
    assert res["totals_2011_2017"]["data_v1"] == 93687          # P7-CP5d table total
    OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    for y, v in r["by_year"].items():
        print(y, {k: v[k] for k in v if k not in ("data_v2x",)})
    print(json.dumps(r["totals_2011_2017"]), json.dumps(r["nofund_group_18178"]))
