"""Offline checks of the H017 non-candidate canary E982-01 (research/phase2/H017_spec.md; owner 2026-10-03 "required
canary checks"). Uses only the canary's fills, logged identifiers/counters, the equity curve's mechanics (dates,
positions, cash) and the frozen event table: it never computes or prints any return or performance (the canary book is
a random-event book, seed 0; the candidate's signals are only counted, never traded or valued).

    PYTHONPATH=src python research/phase2/H017_canary_check.py [E982-01] -> research/phase2/H017_canary_check.json
"""
from __future__ import annotations

import gzip
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research/phase2/sec"))
from qresearch import p2h017 as H, wealth  # noqa: E402

OUT = Path(__file__).with_name("H017_canary_check.json")
SLOTS, HOLD, FEE, SLIP, MIN_POS, MAX_W, BUFFER, GAP = 10, 60, 7.0, 0.001, 4000.0, 0.10, 0.02, 0.15


def run_dir(exp):
    """experiments/<exp>, or an explicit directory (a scratch development run of the checker itself)."""
    p = Path(exp)
    return p if p.is_dir() else ROOT / "experiments" / exp


def lines(exp):
    q = json.loads((run_dir(exp) / "result.json").read_text())["qc_statistics"]
    return "".join(q[f"qr_msgs_{i:02d}"] for i in range(int(q["qr_msgs_n"]))).split("\n")


def load(exp):
    d = run_dir(exp)
    return (pd.read_csv(gzip.open(d / "fills.csv.gz")), pd.read_csv(gzip.open(d / "equity.csv.gz")),
            json.loads((d / "result.json").read_text()), json.loads((d / "config.json").read_text()))


def table():
    cb = gzip.decompress((ROOT / "research/phase2/h017/event_table_v1.csv.gz").read_bytes())
    return pd.read_csv(io.BytesIO(cb), dtype=str, keep_default_na=False)


def ok(d, cond):
    d["ok"] = bool(cond)
    return d


def main(exp=H.CANARY, out_path=OUT):
    fills, eq, res, cfg = load(exp)
    L = lines(exp)
    summ = next(json.loads(x.split("|", 2)[2]) for x in L if x.startswith("QRS017|summary|"))
    hs = res.get("harness_summary", {})
    ev = [x.split("|") for x in L if x.startswith("EV|")]
    wev = [x.split("|") for x in L if x.startswith("WEV|")]
    en = [x.split("|") for x in L if x.startswith("EN|")]
    xt = [x.split("|") for x in L if x.startswith("XT|")]
    T = table()
    dec_of = {(r.sid, r.event_session): r.decision_session for r in T.itertuples()}
    sess = list(eq["date"].astype(str))
    pos = {d: i for i, d in enumerate(sess)}
    nxt = {sess[i]: sess[i + 1] for i in range(len(sess) - 1)}
    out = dict(experiment=exp, config=dict(book=cfg["params"]["book"], seed=cfg["params"]["seed"],
                                           canary=cfg["params"].get("canary"), warmup_start=cfg["warmup_start"],
                                           start=cfg["start"], end=cfg["end"]),
               status=res.get("status"), checks={})
    C = out["checks"]
    # ---------------------------------------------------------------- A. event integrity
    tc = json.loads((ROOT / "research/phase2/h017/h017_event_table_canary.json").read_text())
    man = H.event_manifest()
    C["A1_event_table_hash_in_lean"] = ok(dict(lean=summ["events_table_sha256"], pinned=H.EVENT_TABLE_SHA256,
                                               table_events_loaded=summ["table_events"], manifest=man["counts"]["events"]),
                                          summ["events_table_sha256"] == H.EVENT_TABLE_SHA256 ==
                                          man["payload_sha256"] and summ["table_events"] == man["counts"]["events"])
    C["A2_offline_table_canary"] = ok({k: v["ok"] for k, v in tc["checks"].items()}, tc["all_ok"])
    C["A3_table_event_sessions_are_lean_sessions"] = ok(dict(not_session=summ["table_E_not_lean_session"],
                                                             lean_sessions=summ["lean_sessions"],
                                                             first_session=summ["first_session"]),
                                                        summ["table_E_not_lean_session"] == 0)
    C["A4_no_event_after_2021"] = ok(dict(last_decision=man["counts"]["last_decision"]),
                                     man["counts"]["last_decision"] <= "2021-12-31")
    # ---------------------------------------------------------------- B. PIT / leakage
    C["B1_breakpoint_strictly_earlier_sessions"] = ok(dict(violations=summ["threshold_future_violations"]),
                                                      summ["threshold_future_violations"] == 0)
    C["B2_reaction_bars_never_after_decision_close"] = ok(dict(bars_after_today=summ["bars_after_today"],
                                                               today_close_from_slice=summ["today_close_from_slice"]),
                                                          summ["bars_after_today"] == 0)
    n_hist = [int(x[5]) for x in ev if x[2] != "0" and int(x[4]) > 0]
    C["B3_breakpoint_sample_ge_400_from_start"] = ok(dict(min_hist_official=summ["min_hist_official"],
                                                          days_without_threshold=summ["days_no_threshold_official"],
                                                          min_logged=min(n_hist) if n_hist else None),
                                                     (summ["min_hist_official"] or 0) >= 400
                                                     and summ["days_no_threshold_official"] == 0)
    C["B4_warmup_history_only"] = ok(dict(first_trade_decision=summ["first_trade_decision"], first_equity=sess[0],
                                          first_fill=str(fills["date"].min()), warmup_days_logged=len(wev),
                                          warmup_decision_days=summ["warmup_decision_days"],
                                          harness_warmup_days=hs.get("warmup_days")),
                                     summ["first_trade_decision"] == H.COMMON_START == sess[0]
                                     and str(fills["date"].min()) > H.COMMON_START and len(wev) > 0)
    C["B5_no_holdout_data"] = ok(dict(end=cfg["end"], last_equity=sess[-1], last_fill=str(fills["date"].max()),
                                      last_table_decision=man["counts"]["last_decision"]),
                                 cfg["end"] <= "2021-12-31" and sess[-1] <= "2021-12-31"
                                 and str(fills["date"].max()) <= "2021-12-31")
    # ---------------------------------------------------------------- C. execution
    fills = fills.sort_values(["date", "order_id"]).reset_index(drop=True)
    fills["sig"] = fills["tag"].astype(str).str.extract(r"sig=(\d{4}-\d\d-\d\d)")[0]
    fills["kind"] = fills["tag"].astype(str).str.split("|").str[0]
    buys = fills[fills["quantity"] > 0]
    en_by = {(x[1], x[2]): x[3] for x in en}               # (decision date, sid) -> E
    bad_entry = []
    for r in buys.itertuples():
        E = en_by.get((r.sig, r.symbol_id))
        if E is None or dec_of.get((r.symbol_id, E)) != r.sig or nxt.get(r.sig) != r.date or r.kind != "s017":
            bad_entry.append((r.symbol_id, r.sig, r.date, E))
    bought = {(r.sig, r.symbol_id) for r in buys.itertuples()}
    unfilled = [x for x in en if (x[1], x[2]) not in bought]
    unf_last = [x for x in unfilled if x[1] == sess[-1]]          # decided at the final close: no next open in the run
    explained = hs.get("skipped_min_position", 0) + hs.get("skipped_max_positions", 0) + hs.get("cancelled_harness_buys", 0)
    C["C1_every_entry_at_open_E_plus_2"] = ok(dict(entries=len(buys), entry_lines=len(en), violations=len(bad_entry),
                                                   examples=bad_entry[:5], unfilled_decided_at_final_close=len(unf_last),
                                                   unfilled_other=len(unfilled) - len(unf_last),
                                                   skipped_or_cancelled_buys=explained),
                                              not bad_entry and len(unfilled) - len(unf_last) <= explained)
    # positions: each buy opens a position closed by the next sell-type fill of the symbol
    eps, top_ups = [], []
    openp = {}
    for r in fills.itertuples():
        s = r.symbol_id
        if r.quantity > 0:
            if s in openp:
                top_ups.append((s, r.date))
            openp[s] = dict(sid=s, entry=r.date, sig=r.sig)
        elif s in openp:
            e = openp.pop(s)
            e.update(exit=r.date, exit_kind=r.kind, exit_sig=r.sig if isinstance(r.sig, str) else None)
            eps.append(e)
    still_open = list(openp.values())
    normal = [e for e in eps if e["exit_kind"] == "s017"]
    forced = [e for e in eps if e["exit_kind"] != "s017"]
    bad_hold = [e for e in normal if pos[e["exit"]] - pos[e["entry"]] != HOLD]
    xt_held = Counter(int(x[3]) for x in xt)
    C["C2_normal_exits_exactly_60_sessions"] = ok(dict(normal_exits=len(normal), violations=len(bad_hold),
                                                       examples=bad_hold[:5], held_at_exit_order=dict(xt_held),
                                                       forced_exits=len(forced),
                                                       forced_kinds=dict(Counter(e["exit_kind"] for e in forced)),
                                                       open_at_end=len(still_open),
                                                       open_at_end_max_sessions=max((len(sess) - 1 - pos[e["entry"]]
                                                                                     for e in still_open), default=0)),
                                                  not bad_hold and set(xt_held) <= {HOLD - 1}
                                                  and all(len(sess) - 1 - pos[e["entry"]] <= HOLD for e in still_open))
    stale = [x for x in L if x.startswith(("QRSTALE|", "QRDELIST|"))]
    C["C3_forced_exits_are_logged_integrity_exits"] = ok(dict(forced=len(forced), stale_or_delist_lines=len(stale),
                                                              harness_stale_exits=hs.get("stale_exits"),
                                                              held_delistings=hs.get("held_delistings")),
                                                         len(forced) <= len(stale) + hs.get("held_delistings", 0))
    # ---------------------------------------------------------------- D. portfolio / cash / costs
    C["D1_max_10_holdings"] = ok(dict(max_npos_chart=int(eq["npos"].max()), max_holdings=summ["max_holdings"]),
                                 int(eq["npos"].max()) <= SLOTS and summ["max_holdings"] <= SLOTS)
    C["D2_no_leverage_no_negative_cash"] = ok(dict(max_gross=hs.get("max_gross"), min_cash_frac=hs.get("min_cash_frac"),
                                                   min_cash_chart=float(eq["cash"].min()),
                                                   negative_qty=hs.get("negative_qty")),
                                              hs.get("max_gross", 2) <= 1 + 1e-9 and hs.get("min_cash_frac", -1) >= 0
                                              and float(eq["cash"].min()) >= 0 and hs.get("negative_qty", 1) == 0)
    e_by = dict(zip(eq["date"].astype(str), eq["equity"].astype(float)))
    w = [(r.quantity * r.price) / e_by[r.sig] for r in buys.itertuples() if r.sig in e_by]
    val = [r.quantity * r.price for r in buys.itertuples()]
    C["D3_sizing"] = ok(dict(target_weight=(1 - BUFFER) / SLOTS, max_entry_weight=max(w), median_entry_weight=float(
        pd.Series(w).median()), min_entry_value=min(val), entries_below_4000=sum(v < MIN_POS for v in val),
        scaled_buys=hs.get("buys_scaled"), skipped_min_position=hs.get("skipped_min_position"),
        skipped_max_positions=hs.get("skipped_max_positions")),
        max(w) <= MAX_W * 1.03 and min(val) >= MIN_POS * 0.85)
    fee = fills.groupby("order_id")["fee"].sum()
    C["D4_commission_7_per_order"] = ok(dict(orders=int(len(fee)), not_7=int((fee.round(6) != FEE).sum()),
                                             forced_fee_debits=hs.get("forced_fee_debits")),
                                        int((fee.round(6) != FEE).sum()) == 0)
    C["D5_slippage_10bps_and_fill_timing"] = ok(dict(max_fill_dev=hs.get("max_fill_dev"),
                                                     timing_violations=hs.get("timing_violations"),
                                                     slippage_bps=cfg["costs"]["slippage_bps"]),
                                                hs.get("max_fill_dev", 1) <= 1e-6 and hs.get("timing_violations", 1) == 0
                                                and cfg["costs"]["slippage_bps"] == 10)
    C["D6_no_top_ups"] = ok(dict(buys_while_held=len(top_ups), examples=top_ups[:5]), not top_ups)
    queued = [r for r in buys.itertuples() if (r.symbol_id, en_by.get((r.sig, r.symbol_id))) not in dec_of]
    C["D7_no_queued_signals"] = ok(dict(entries_not_decided_on_their_E_plus_1=len(queued)), not queued)
    early = [e for e in normal if e["exit_sig"] is None or pos[e["exit_sig"]] - pos[e["entry"]] != HOLD - 1]
    C["D8_no_early_replacement"] = ok(dict(normal_exit_orders_not_at_59=len(early),
                                           sells=int((fills["quantity"] < 0).sum())), not early)
    C["D9_held_stock_events_ignored"] = ok(dict(held_events_ignored=summ["held_events_ignored"],
                                                buys_while_held=len(top_ups)),
                                           not top_ups and summ["held_events_ignored"] >= 0)
    C["D10_run_integrity_checks"] = ok({c["check"]: c["ok"] for c in res.get("integrity", [])},
                                       all(c["ok"] for c in res.get("integrity", [])))
    # ---------------------------------------------------------------- E. controls
    over_k = [x for x in ev if x[9] and int(x[9]) > int(x[7])]
    over_free = [x for x in ev if x[8] and int(x[9]) > int(x[8])]
    C["E1_random_entries_le_k_t_and_free"] = ok(dict(days=len(ev), over_k=len(over_k), over_free=len(over_free),
                                                     lean_over_k=summ["entries_over_kt"],
                                                     lean_over_free=summ["entries_over_free"],
                                                     signals_total=summ["signals"],
                                                     entries_planned=summ["entries_planned"]),
                                                not over_k and not over_free and summ["entries_over_kt"] == 0
                                                and summ["entries_over_free"] == 0)
    s017 = (ROOT / "strategies/S017_earnings_continuation/main.py").read_bytes()
    C["E2_same_code_path"] = ok(dict(x982_is_byte_copy_of_s017=(ROOT / "strategies/X982_h017_canary/main.py")
                                     .read_bytes() == s017, book=cfg["params"]["book"], seed=cfg["params"]["seed"]),
                                (ROOT / "strategies/X982_h017_canary/main.py").read_bytes() == s017
                                and cfg["params"]["book"] == "random" and cfg["params"]["seed"] == 0)
    C["E3_event_counts"] = ok(dict(events_seen=summ["events_seen"], events_universe=summ["events_universe"],
                                   events_valid=summ["events_valid"], events_missing_close=summ["events_missing_close"],
                                   decision_days=summ["decision_days"], ev_lines=len(ev)),
                              summ["events_valid"] > 0 and summ["events_universe"] >= summ["events_valid"])
    out["all_ok"] = all(v["ok"] for v in C.values())
    out["frozen"] = dict(spec_ok=H.spec_hash() == H.SPEC_SHA256, amendment3_ok=wealth.spec_hash() ==
                         wealth.AMENDMENT3_SHA256, event_table=H.EVENT_TABLE_SHA256)
    out["note"] = "no return, CAGR, Sharpe or drawdown was computed or printed (mechanics only)"
    Path(out_path).write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({k: v["ok"] for k, v in C.items()}, indent=1), "\nall_ok", out["all_ok"])
    return out


if __name__ == "__main__":
    main(*(sys.argv[1:2] or []))
