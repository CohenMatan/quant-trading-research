"""Integrity checks run on every experiment's results before they are accepted.

Each check returns (name, ok, detail). "fail" checks make the run status integrity_failed;
"warn" checks are reported but do not invalidate the run.
"""
from __future__ import annotations

import re

import pandas as pd

SIG = re.compile(r"\|sig=(\d{4}-\d{2}-\d{2})$")
CASH_FAIL = -0.01    # cash below −1% of equity at a daily close counts as leverage
CASH_WARN = 0.0


def check_all(equity: pd.DataFrame, fills: pd.DataFrame, summary: dict, start: str, end: str,
              commission_per_order: float | None = None) -> list[dict]:
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
    cash_frac = (equity["cash"] / equity["equity"]).min()
    add("no_leverage", cash_frac >= CASH_FAIL, f"min cash/equity {cash_frac:.4f}")
    add("cash_never_negative", cash_frac >= CASH_WARN, f"min cash/equity {cash_frac:.4f}", level="warn")

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
    if commission_per_order is not None and len(fills):
        per_order = fills.groupby("order_id")["fee"].sum()
        wrong = per_order[(per_order - commission_per_order).abs() > 1e-9]
        add("commission_fixed_per_order", wrong.empty,
            f"{len(per_order)} executed orders; {len(wrong)} not charged exactly ${commission_per_order:g}")
    return out


def status_from(checks: list[dict]) -> str:
    if any(not c["ok"] and c["level"] == "fail" for c in checks):
        return "integrity_failed"
    if any(not c["ok"] for c in checks):
        return "completed_with_warnings"
    return "completed"
