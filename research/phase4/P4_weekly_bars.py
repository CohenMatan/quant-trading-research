"""P4-CP1 design prototype: the PROPOSED exact Weekly-bar construction and its timing rule (pure Python; no data).
tests/test_p4_weekly_bars.py holds the leakage canaries. If Phase 4 is approved, this rule is frozen in the spec and
re-implemented inside the LEAN engine with the same tests.

Rule:
  * a week is the ISO week (Monday..Sunday) of the exchange-local session date;
  * the week's LAST SESSION is the last exchange session of that ISO week according to the exchange calendar (holidays
    are published in advance; no price is used to know it);
  * the weekly bar of week w is COMPLETE at the close of w's last session and only then usable; partial weeks never
    produce a bar;
  * fields from the stock's adjusted daily bars of that week: open = first daily open, high = max high, low = min low,
    close = close of the last daily bar of the week (if the stock has no bar on the last session, its last available
    bar in that week), volume = sum, sessions = number of daily bars; a week without any daily bar of the stock yields
    no weekly bar (the series skips it);
  * decision at the close of the week's last session; orders fill at the open of the NEXT exchange session.
"""
from datetime import date


def week_id(d: date):
    y, w, _ = d.isocalendar()
    return (y, w)


def last_sessions(calendar):
    """{week_id: last session date} from the ordered exchange session calendar."""
    out = {}
    for d in calendar:
        out[week_id(d)] = d
    return out


def next_session(calendar, d):
    """First exchange session strictly after d (the earliest execution of a decision taken at d's close)."""
    for x in calendar:
        if x > d:
            return x
    return None


def weekly_bars(daily, calendar, asof):
    """daily: ordered list of (date, open, high, low, close, volume) of one stock (adjusted as known at `asof`).
    Returns the completed weekly bars as of the close of `asof`: list of dicts, oldest first. Only daily rows dated
    <= asof are read, and only weeks whose last session <= asof are emitted."""
    last = last_sessions([d for d in calendar])
    weeks = {}
    for row in daily:
        d = row[0]
        if d > asof:
            break
        weeks.setdefault(week_id(d), []).append(row)
    out = []
    for wk in sorted(weeks):
        ls = last.get(wk)
        if ls is None or ls > asof:
            continue                                    # the week is not complete at `asof`
        rows = weeks[wk]
        out.append(dict(week=wk, last_session=ls, open=rows[0][1], high=max(r[2] for r in rows),
                        low=min(r[3] for r in rows), close=rows[-1][4], volume=sum(r[5] for r in rows),
                        sessions=len(rows)))
    return out


def is_decision_day(calendar, d):
    """True iff d is the last exchange session of its ISO week (a Weekly decision is taken at d's close)."""
    return last_sessions(calendar).get(week_id(d)) == d
