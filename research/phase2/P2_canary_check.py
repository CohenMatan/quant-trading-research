"""Offline verification of the Phase 2 X965 canaries (E965-04, -02, -03; E965-01 bugged, D096) and their reproduction, from committed
outputs only (D095). Checks on top of the on-QuantConnect audits (QRC65 summary):
  - run completed; integrity fail-level checks pass; harness timing violations 0 and fills at the open +/- slippage;
  - every fill costs exactly $7 (one per order); every opening buy is >= $5,000 at the signal close's price
    (reported as the minimum opening notional at fill price, and the harness's skipped-minimum count);
  - session counting: every time exit happens exactly `limit` sessions after the entry fill or the last roll
    (trading calendar = the run's own daily records), and the sell fills at the next session's open;
  - every opening buy is a name ranked at the previous session's close (QRC65|rank lines);
  - E965-02 ($60K): the $5,000 minimum and the size-aware position cap are exercised;
  - reproduction of E965-03: identical equity, fills and trades hashes.

    PYTHONPATH=src python research/phase2/P2_canary_check.py  -> research/phase2/P2_canary_check.json
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
from qresearch import results  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
CANARIES = ("E965-04", "E965-02", "E965-03")   # E965-01 bugged (canary v1.0 defect, D096)
ZERO_KEYS = ("mask_mismatches", "rank_errors", "time_exit_errors", "ma200_exit_errors",
             "roll_errors", "ranked_not_eligible", "ranked_cap_below_2b", "ranked_no_real_bar", "window_not_today")


def run_dir(eid):
    """E965-04's result is its D077 recovery (runner lost in a container restart; same QC backtest)."""
    rec = sorted((EXP / eid / "recovery").glob("*/result.json")) if (EXP / eid / "recovery").exists() else []
    return rec[-1].parent if rec else EXP / eid


def lines(eid):
    return (run_dir(eid) / "messages.txt").read_text().splitlines()


def summary(ls, prefix):
    for ln in ls:
        if ln.startswith(prefix + "|summary|"):
            return json.loads(ln.split("|", 2)[2])
    return None


def check(eid):
    res = json.loads((run_dir(eid) / "result.json").read_text())
    cfg = json.loads((EXP / eid / "config.json").read_text())
    out = dict(exp=eid, status=res["status"], problems=[])
    P = out["problems"]
    if not str(res["status"]).startswith("completed"):
        P.append("not completed")
        return out
    hs = res["harness_summary"]
    if hs["timing_violations"] or hs["max_fill_dev"] > 1e-6:
        P.append(f"timing/fill-price: {hs['timing_violations']} / {hs['max_fill_dev']}")
    bad = [c["check"] for c in res["integrity"] if c["level"] == "fail" and not c["ok"]]
    if bad:
        P.append(f"integrity: {bad}")
    ls = lines(eid)
    c65, s14 = summary(ls, "QRC65"), summary(ls, "QRS014")
    out["qrc65"], out["qrs014"] = c65, s14
    for k in ZERO_KEYS:
        if c65[k]:
            P.append(f"{k} = {c65[k]}")
    for k in ("held_short_window", "held_no_entry"):
        if s14[k]:
            P.append(f"{k} = {s14[k]}")
    # D097 criterion (from the E966-02 diagnosis): today's close exact; older-bar dividend-factor differences
    # <= 1e-3 relative for the price averages and High(T-1); entry masks 100% equal. The strict 1e-6 count is reported.
    dev = c65["max_rel_dev"]
    out["strict_feature_mismatches_reported"] = c65["feature_mismatches"]
    if dev.get("close", 1) != 0 or max(dev.get(k, 1) for k in ("ma50", "ma200", "high_prev")) > 1e-3:
        P.append(f"feature deviation beyond the D097 criterion: {dev}")
    if c65["feature_checks"] < 100 or c65["mask_checks"] < 100 or c65["rank_checks"] < 200:
        P.append("too few audit checks")
    fi = results.read_csv_gz(run_dir(eid) / "fills.csv.gz")
    eq = results.read_csv_gz(run_dir(eid) / "equity.csv.gz")
    cal = list(eq["date"].astype(str))
    pos = {d: i for i, d in enumerate(cal)}
    if (fi["fee"] != 7.0).any():
        P.append("fee != $7 on some fill")
    if fi.groupby("order_id").size().max() != 1 and (fi.groupby("order_id")["fee"].sum() != 7.0).any():
        P.append("an order was charged other than once")
    # opening buys and session counting
    limit = int(cfg["params"]["limit"])
    exits = [ln.split("|") for ln in ls if ln.startswith("QRC65|exit|")]
    rolls = [ln.split("|") for ln in ls if ln.startswith("QRC65|roll|")]
    ranks = {}
    for ln in ls:
        if ln.startswith("QRC65|rank|"):
            _, _, d, sid, k = ln.split("|")
            ranks.setdefault(d, set()).add(sid)
    fi = fi.sort_values(["date", "order_id"]).reset_index(drop=True)
    holding, entry, last_roll = {}, {}, {}   # last_roll: sid -> roll dates (filled while replaying events)
    opening = []
    for r in fi.itertuples():
        q0 = holding.get(r.symbol_id, 0.0)
        if q0 <= 0 and r.quantity > 0:
            entry[r.symbol_id] = r.date
            opening.append(r)
        holding[r.symbol_id] = q0 + r.quantity
    out["opening_buys"] = len(opening)
    out["min_opening_notional_at_fill"] = float(min(r.quantity * r.price for r in opening)) if opening else None
    not_ranked = [(r.date, r.symbol_id) for r in opening
                  if pos.get(r.date, 0) == 0 or r.symbol_id not in ranks.get(cal[pos[r.date] - 1], set())]
    if not_ranked:
        P.append(f"{len(not_ranked)} opening buys not ranked at the previous close, e.g. {not_ranked[:3]}")
    # session counting for time exits and rolls, replayed in date order
    events = sorted([(e[2], "exit", e[3], e[4], int(e[5])) for e in exits] +
                    [(e[2], "roll", e[3], "roll", int(e[4])) for e in rolls])
    sells = {(r.date, r.symbol_id) for r in fi.itertuples() if r.quantity < 0}
    n_time = n_roll = n_ma = 0
    entry_of = {}
    for r in opening:
        entry_of.setdefault(r.symbol_id, []).append(r.date)
    for d, kind, sid, reason, held in events:
        starts = [x for x in entry_of.get(sid, []) if x <= d]
        if not starts:
            P.append(f"{kind} of {sid} on {d} without an entry")
            continue
        start = max(starts)
        rl = [x for x in last_roll.get(sid, []) if start <= x < d]
        base = max(rl) if rl else start
        sessions = pos[d] - pos[base]
        if sessions != held:
            P.append(f"{kind} {sid} {d}: logged held {held} != calendar {sessions}")
        if kind == "roll":
            n_roll += 1
            last_roll.setdefault(sid, []).append(d)
            if held != limit:
                P.append(f"roll {sid} {d} at held {held}")
            continue
        if reason == "time":
            n_time += 1
            if held != limit:
                P.append(f"time exit {sid} {d} at held {held}")
        else:
            n_ma += 1
        nxt = cal[pos[d] + 1] if pos[d] + 1 < len(cal) else None
        if nxt is not None and (nxt, sid) not in sells:
            P.append(f"exit {sid} signalled {d} not sold at the next open {nxt}")
    out.update(time_exits=n_time, rolls=n_roll, ma200_exits=n_ma)
    if eid == "E965-02":
        out["skipped_min_position"] = hs.get("skipped_min_position")
        out["max_positions_held"] = int(eq["npos"].max())
        out["size_cap_by_equity"] = int((eq["equity"].max() * 0.98) // 5000)
        if out["max_positions_held"] > out["size_cap_by_equity"]:
            P.append("more positions than the size-aware cap allows")
        # The $5,000 minimum applies to the value planned at the signal close (plan_orders); an overnight gap can
        # make the next-open fill smaller. Planned values come from QC's order records (orderSubmissionData.lastPrice),
        # checked read-only by the one-off script output P2_canary_min_position.json (no prices stored).
        mp = json.loads((Path(__file__).parent / "P2_canary_min_position.json").read_text())
        out["min_position_check"] = mp
        if mp["planned_below_5000"] != 0 or mp["opening_buys"] != out["opening_buys"]:
            P.append("an opening buy planned below $5,000")
        if not out["skipped_min_position"]:
            P.append("the $5,000 minimum never bound at $60K")
    out["ok"] = not P
    return out


def reproduction(eid):
    d = EXP / eid / "reproductions"
    runs = sorted(d.glob("*/result.json")) if d.exists() else []
    if not runs:
        return dict(exp=eid, reproduced=None)
    r = json.loads(runs[-1].read_text())
    return dict(exp=eid, reproduced=r.get("reproduction", {}).get("identical"),
                hashes_match=r.get("reproduction", {}).get("hashes_match"))


def main():
    out = dict(canaries=[check(e) for e in CANARIES], reproduction=reproduction("E965-03"))
    out["all_ok"] = all(c.get("ok") for c in out["canaries"]) and out["reproduction"]["reproduced"] is True
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({c["exp"]: (c.get("ok"), c["problems"][:5]) for c in out["canaries"]}, indent=1))
    print("reproduction", out["reproduction"], "ALL OK" if out["all_ok"] else "NOT OK")


if __name__ == "__main__":
    main()
