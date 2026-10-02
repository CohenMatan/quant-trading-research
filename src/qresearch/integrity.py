"""Integrity checks run on every experiment's results before they are accepted.

Each check returns (name, ok, detail). "fail" checks make the run status integrity_failed;
"warn" checks are reported but do not invalidate the run.
"""
from __future__ import annotations

import re

import pandas as pd

SIG = re.compile(r"\|sig=(\d{4}-\d{2}-\d{2})$")
CASH_FAIL = -1e-9    # D051: ANY negative cash at a daily close is borrowing and fails the run


def official_tradeable_dates(tradeable_dates, summary: dict):
    """QuantConnect's tradeable-date count covers the whole LEAN run; with a history-only warm-up (D114) the harness
    counts the warm-up sessions, which carry no equity record, so they are removed before the comparison."""
    if tradeable_dates is None:
        return None
    return int(tradeable_dates) - int((summary or {}).get("warmup_days", 0) or 0)


def check_all(equity: pd.DataFrame, fills: pd.DataFrame, summary: dict, start: str, end: str,
              commission_per_order: float | None = None, tradeable_dates: int | None = None,
              expected_orders: int | None = None, downloaded_orders: int | None = None,
              late_open_orders: list | None = None, initial_cash: float | None = None) -> list[dict]:
    out: list[dict] = []

    def add(name, ok, detail, level="fail"):
        out.append(dict(check=name, ok=bool(ok), level=level, detail=str(detail)))

    d = equity["date"].astype(str)
    add("equity_nonempty", len(equity) > 0, f"{len(equity)} rows")
    if len(equity) == 0:
        return out
    add("equity_dates_increasing", d.is_monotonic_increasing and d.is_unique, "strictly increasing dates")
    add("equity_within_dates", d.iloc[0] >= start and d.iloc[-1] <= end, f"{d.iloc[0]}..{d.iloc[-1]}")
    add("equity_no_nan", not equity[["equity", "cash"]].isna().any().any(), "no missing values")
    add("equity_positive", bool((equity["equity"] > 0).all()), f"min {equity['equity'].min():.2f}")
    days = summary.get("days")
    add("equity_complete", days == len(equity), f"chart rows {len(equity)} vs algorithm days {days}")
    if tradeable_dates is not None:
        add("equity_matches_qc_tradeable_dates", int(tradeable_dates) == len(equity),
            f"chart rows {len(equity)} vs QuantConnect tradeableDates {tradeable_dates}")
    if int(summary.get("warmup_days", 0) or 0) > 0 and initial_cash is not None:
        # D114: a history-only warm-up must leave the account untouched until the official start
        first = float(equity["equity"].iloc[0])
        add("warmup_left_account_untouched", abs(first - float(initial_cash)) < 1e-6,
            f"first recorded equity {first:.2f} vs initial cash {float(initial_cash):.2f}; "
            f"{summary.get('warmup_days')} warm-up sessions")
    cash_frac = (equity["cash"] / equity["equity"]).min()
    neg_days = int((equity["cash"] < -1e-6).sum())
    add("no_leverage", cash_frac >= CASH_FAIL, f"min cash/equity {cash_frac:.6f}; {neg_days} closes with negative cash")

    # execution timing: every harness order fills strictly after its signal date
    bad = 0
    forced = 0
    for tag, day in zip(fills["tag"].astype(str), fills["date"].astype(str)):
        m = SIG.search(tag)
        if not m:
            forced += 1
            continue
        if day <= m.group(1):
            bad += 1
    add("fills_after_signal_date", bad == 0, f"{bad} violations, {forced} LEAN-generated fills")
    add("fills_within_dates", fills.empty or (fills["date"].astype(str).between(start, end).all()),
        "fill dates inside the backtest window")
    add("harness_timing_selfcheck", summary.get("timing_violations", -1) == 0,
        f"violations={summary.get('timing_violations')} max_fill_dev={summary.get('max_fill_dev')}")
    add("harness_no_short", summary.get("negative_qty", -1) == 0, f"negative_qty={summary.get('negative_qty')}")
    add("no_invalid_orders", summary.get("invalid", 0) == 0, f"invalid={summary.get('invalid')}", level="warn")
    add("summary_present", bool(summary), "QRSUMMARY log line parsed")
    # completeness of the downloaded orders/fills (E901-02 incident: an empty download looked "clean")
    if expected_orders is not None:
        add("orders_download_complete", downloaded_orders == expected_orders,
            f"downloaded {downloaded_orders} orders vs QuantConnect Total Orders {expected_orders}")
    # D059 fallback exits are mirrored rows, not LEAN fills: exclude them from the fill-count check
    stale_rows = fills["tag"].astype(str).str.startswith("stale_exit") if len(fills) else pd.Series(dtype=bool)
    n_real = int(len(fills) - int(stale_rows.sum())) if len(fills) else 0
    if "fills" in summary:
        add("fills_match_harness_count", n_real == int(summary["fills"]),
            f"downloaded fill events {n_real} vs harness-recorded fills {summary['fills']}")
    # D059: an order that can never fill, or a dead holding left unresolved, fails the run loudly
    if late_open_orders is not None:
        add("no_stale_open_orders", len(late_open_orders) == 0,
            f"{len(late_open_orders)} orders still open more than 10 days before the end: {late_open_orders[:5]}")
    if "stale_open_orders" in summary:
        add("harness_no_stale_open_orders", summary["stale_open_orders"] == 0,
            f"harness orders open > 5 sessions at the end: {summary['stale_open_orders']}")
    if "stale_unresolved" in summary:
        add("no_unresolved_stale_holdings", summary["stale_unresolved"] == 0,
            f"held positions without a real price bar that the fallback could not close: {summary['stale_unresolved']}")
    if "windows_restored" in summary:   # D063: should never be needed once windows are kept for pending orders
        add("windows_restored", summary["windows_restored"] == 0,
            f"{summary['windows_restored']} holdings found without a price window and restored", level="warn")
    if "stale_exits" in summary:
        add("stale_exits", summary["stale_exits"] == 0,
            f"{summary['stale_exits']} holdings taken out at their last real close after "
            f"> 10 sessions without data (D059 fallback): {int(stale_rows.sum()) if len(fills) else 0} mirrored",
            level="warn")
    if commission_per_order is not None:
        if len(fills):
            per_order = fills.groupby("order_id")["fee"].sum()
            wrong = per_order[(per_order - commission_per_order).abs() > 1e-9]
            add("commission_fixed_per_order", wrong.empty,
                f"{len(per_order)} executed orders; {len(wrong)} not charged exactly ${commission_per_order:g}")
        else:   # never skip silently: no fills is only acceptable if the algorithm really had none
            add("commission_fixed_per_order", int(summary.get("fills", 0)) == 0,
                f"no fills downloaded; harness recorded {summary.get('fills')} fills")
    return out


def status_from(checks: list[dict]) -> str:
    if any(not c["ok"] and c["level"] == "fail" for c in checks):
        return "integrity_failed"
    if any(not c["ok"] for c in checks):
        return "completed_with_warnings"
    return "completed"
