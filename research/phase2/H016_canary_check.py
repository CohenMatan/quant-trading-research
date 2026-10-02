"""Offline checks of the H016 non-candidate canary E980-01 (research/phase2/H016_spec.md §7; owner 2026-10-02 item 10).
Uses only the canary's own fills, equity curve and summary lines (random book, seed 0): it never computes or prints
any candidate (GP/A-ranked) performance. Writes research/phase2/H016_canary_check.json.

    PYTHONPATH=src python research/phase2/H016_canary_check.py [E980-01]
"""
import gzip
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/phase2/sec"))
from e970_parse import lines  # noqa: E402

START, FIRST_FILL, SLOTS, MIN_POS, MIN_TOPUP, FEE = "2010-03-01", "2010-03-02", 20, 4000.0, 250.0, 7.0
REB_MONTHS = (3, 6, 9, 12)


def load(exp):
    d = ROOT / "experiments" / exp
    fills = pd.read_csv(gzip.open(d / "fills.csv.gz"))
    eq = pd.read_csv(gzip.open(d / "equity.csv.gz"))
    res = json.loads((d / "result.json").read_text())
    return fills, eq, res


def episodes(fills):
    """Per symbol: positions from their entry buy to the next entry (or 0 -> held); counts entry buys, top-ups and
    other buys in each."""
    out = []
    for sid, g in fills.sort_values(["date", "order_id"]).groupby("symbol_id"):
        q, cur = 0.0, None
        for r in g.itertuples():
            tag = str(r.tag).split("|")[0]
            # a new position starts at its entry buy (entries are only placed for names not held); the running
            # quantity alone cannot delimit positions because splits change it without a fill (E980-01: GIS 2010)
            if r.quantity > 0 and (q == 0 or tag == "s016_entry"):
                cur = dict(sid=sid, start=r.date, entry=0, topup=0, other_buys=0, topup_before_entry=0,
                           entry_value=None, topup_values=[])
                out.append(cur)
            if r.quantity > 0 and cur is not None:
                if tag == "s016_entry":
                    cur["entry"] += 1
                    cur["entry_value"] = r.quantity * r.price
                elif tag == "s016_topup":
                    cur["topup"] += 1
                    cur["topup_values"].append(r.quantity * r.price)
                    if cur["entry"] == 0:
                        cur["topup_before_entry"] += 1
                else:
                    cur["other_buys"] += 1
            q += r.quantity
            if abs(q) < 1e-9:
                q, cur = 0.0, None
    return out


def main(exp="E980-01"):
    fills, eq, res = load(exp)
    L = lines(exp)
    summ = [json.loads(x.split("|", 2)[2]) for x in L if x.startswith("QRS016|summary|")]
    st = summ[-1] if summ else {}
    rb = [x.split("|") for x in L if x.startswith("RB|")]
    sh = [x.split("|") for x in L if x.startswith("SH|")]
    eps = episodes(fills)
    tagged = fills.assign(t=fills["tag"].astype(str).str.split("|").str[0])
    buys = tagged[tagged["quantity"] > 0]
    entries, topups = buys[buys["t"] == "s016_entry"], buys[buys["t"] == "s016_topup"]
    # cash: every day's change minus that day's fill flows must be a non-negative credit (dividends etc.)
    flow = (-(fills["quantity"] * fills["price"]) - fills["fee"]).groupby(fills["date"]).sum()
    e = eq.set_index("date")
    dcash = e["cash"].diff().fillna(e["cash"].iloc[0] - 100000.0)
    resid = dcash - flow.reindex(e.index).fillna(0.0)
    rb_dates = [date.fromisoformat(r[1]) for r in rb]
    first_rb_ok = all(d.month in REB_MONTHS and d.day <= 7 for d in rb_dates)
    one_per_q = len({(d.year, d.month) for d in rb_dates}) == len(rb_dates)
    sig = tagged["tag"].astype(str).str.split("sig=").str[-1]
    exit_sig = set(sig[tagged["t"] == "s016_exit"])
    n20 = int(e.loc[FIRST_FILL, "npos"]) if FIRST_FILL in e.index else None
    checks = {
        "equity_starts_2010_03_01_in_cash": e.index[0] == START and float(e["cash"].iloc[0]) == 100000.0
                                            and int(e["npos"].iloc[0]) == 0,
        "first_fills_2010_03_02": fills["date"].min() == FIRST_FILL,
        "twenty_positions_formed_2010_03_02": n20 == SLOTS,
        "never_more_than_20_positions": int(e["npos"].max()) <= SLOTS,
        "quarterly_rebalance_dates": first_rb_ok and one_per_q and len(rb) == 48 and rb_dates[0] == date(2010, 3, 1),
        "exits_only_at_rebalances": exit_sig <= {str(d) for d in rb_dates},
        "no_entry_decision_before_first_rebalance": min(sig[tagged["t"] == "s016_entry"]) >= START,
        "shadow_gpa_logged_every_rebalance": len(sh) == len(rb),
        "pit_violations_zero": st.get("pit_violations") == 0,
        "no_financial_or_reit_in_universe": st.get("financial_in_universe") == 0,
        "no_new_purchase_below_4000_at_decision": (st.get("min_entry_planned_usd") or 0) >= MIN_POS,
        "at_most_one_topup_per_new_position": st.get("max_topups_per_position", 9) <= 1
                                              and all(x["topup"] <= 1 for x in eps),
        "topup_only_after_initial_fill": all(x["topup_before_entry"] == 0 for x in eps),
        "no_other_resizing_buys": all(x["other_buys"] == 0 for x in eps) and set(buys["t"]) <= {"s016_entry",
                                                                                                "s016_topup"},
        "topups_at_least_250_at_decision": st.get("min_topup_planned_usd") is None
                                           or st["min_topup_planned_usd"] >= MIN_TOPUP,
        "topups_never_above_target": st.get("max_topup_over_target_usd", 1.0) <= 1e-6,
        "no_negative_cash": float(e["cash"].min()) >= 0.0,
        "commissions_7_per_order": bool((fills["fee"] == FEE).all()),
        "cash_reconciles_with_fills": float(resid.min()) >= -0.05,
        "harness_integrity_ok": all(c["ok"] for c in res["integrity"]),
    }
    years = (pd.Timestamp(e.index[-1]) - pd.Timestamp(e.index[0])).days / 365.25
    info = {
        "fills": len(fills), "entry_fills": len(entries), "topup_fills": len(topups),
        "positions_opened": len(eps), "positions_with_topup": sum(1 for x in eps if x["topup"]),
        "entry_fill_usd": dict(min=float((entries["quantity"] * entries["price"]).min()),
                               median=float((entries["quantity"] * entries["price"]).median())),
        "topup_fill_usd": dict(min=float((topups["quantity"] * topups["price"]).min()) if len(topups) else None,
                               median=float((topups["quantity"] * topups["price"]).median()) if len(topups) else None),
        "entry_fills_below_4000_after_open_gap": int(((entries["quantity"] * entries["price"]) < MIN_POS).sum()),
        "topup_commissions": float(topups["fee"].sum()),
        "topup_orders_per_year": len(topups) / years,
        "mean_invested_share": float((1 - e["cash"] / e["equity"]).loc[FIRST_FILL:].mean()),
        "min_invested_share_after_formation": float((1 - e["cash"] / e["equity"]).loc["2010-03-05":].min()),
        "days_with_20_positions_share": float((e["npos"].loc[FIRST_FILL:] == SLOTS).mean()),
        "cash_credits_not_from_fills_usd": float(resid[resid > 0].sum()),
        "rebalances": len(rb), "universe_size_first_last": [int(rb[0][3]), int(rb[-1][3])] if rb else None,
        "summary": st,
    }
    out = dict(experiment=exp, ok=all(checks.values()), checks=checks, info=info,
               note="Canary book = random seed 0 (not a control seed). No candidate (GP/A) performance is computed.")
    (ROOT / "research/phase2/H016_canary_check.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    print(json.dumps(info, indent=1, default=str))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(*(sys.argv[1:] or [])))
