"""Phase 4 design: leakage canaries for the proposed Weekly-bar rule (research/phase4/P4_weekly_bars.py). Synthetic
calendars and prices only."""
import random
from datetime import date, timedelta

from conftest import ROOT, load_module

W = load_module(ROOT / "research/phase4/P4_weekly_bars.py", "p4_weekly_bars_t")

HOLIDAYS = {date(2014, 4, 18), date(2014, 12, 25), date(2015, 1, 1), date(2014, 11, 27), date(2014, 7, 4)}


def calendar(start=date(2014, 3, 3), end=date(2015, 2, 27)):
    d, out = start, []
    while d <= end:
        if d.weekday() < 5 and d not in HOLIDAYS:
            out.append(d)
        d += timedelta(days=1)
    return out


def daily(cal, seed=1, drop=()):
    rng = random.Random(seed)
    px, out = 50.0, []
    for d in cal:
        if d in drop:
            continue
        o = px * (1 + rng.uniform(-0.01, 0.01))
        c = o * (1 + rng.uniform(-0.03, 0.03))
        out.append((d, o, max(o, c) * 1.01, min(o, c) * 0.99, c, rng.randint(1000, 5000)))
        px = c
    return out


def test_truncation_invariance_and_no_future_influence():
    cal = calendar()
    full = daily(cal)
    for asof in cal[::7]:
        a = W.weekly_bars(full, cal, asof)
        b = W.weekly_bars([r for r in full if r[0] <= asof], cal, asof)
        assert a == b                                    # rows after `asof` are never read
        tampered = [r if r[0] <= asof else (r[0], 1e6, 1e6, 1e6, 1e6, 10 ** 9) for r in full]
        assert W.weekly_bars(tampered, cal, asof) == a  # changing the future changes nothing


def test_no_partial_week_and_completion_at_last_session():
    cal = calendar()
    full = daily(cal)
    wed = date(2014, 6, 11)
    fri = date(2014, 6, 13)
    assert W.week_id(wed) not in [b["week"] for b in W.weekly_bars(full, cal, wed)]
    bars = W.weekly_bars(full, cal, fri)
    assert bars[-1]["week"] == W.week_id(fri) and bars[-1]["last_session"] == fri
    assert W.is_decision_day(cal, fri) and not W.is_decision_day(cal, wed)


def test_fields_exact():
    cal = calendar()
    full = daily(cal)
    bars = W.weekly_bars(full, cal, cal[-1])
    for b in bars:
        rows = [r for r in full if W.week_id(r[0]) == b["week"]]
        assert b["open"] == rows[0][1] and b["close"] == rows[-1][4]
        assert b["high"] == max(r[2] for r in rows) and b["low"] == min(r[3] for r in rows)
        assert b["volume"] == sum(r[5] for r in rows) and b["sessions"] == len(rows)


def test_holiday_shortened_weeks():
    cal = calendar()
    full = daily(cal)
    thu = date(2014, 4, 17)                              # Good Friday 2014-04-18: the week ends Thursday
    assert W.is_decision_day(cal, thu)
    b = W.weekly_bars(full, cal, thu)[-1]
    assert b["last_session"] == thu and b["sessions"] == 4
    assert W.next_session(cal, thu) == date(2014, 4, 21)   # execution: the next session (Monday)
    # Thanksgiving week: Thursday closed, the week still ends Friday
    assert W.is_decision_day(cal, date(2014, 11, 28))


def test_missing_last_day_bar_and_empty_week():
    cal = calendar()
    fri = date(2014, 6, 13)
    gone = {fri}
    full = daily(cal, drop=gone)
    b = W.weekly_bars(full, cal, fri)[-1]
    assert b["last_session"] == fri and b["close"] == [r for r in full if r[0] < fri][-1][4] and b["sessions"] == 4
    week = {d for d in cal if W.week_id(d) == W.week_id(date(2014, 6, 20))}
    full2 = daily(cal, drop=week)
    assert W.week_id(date(2014, 6, 20)) not in [x["week"] for x in W.weekly_bars(full2, cal, date(2014, 6, 27))]


def test_iso_year_boundary():
    cal = calendar()
    full = daily(cal)
    # 2014-12-29 .. 2015-01-02 is ISO week 2015-W01 (Jan 1 holiday); it completes on Friday 2015-01-02
    assert W.week_id(date(2014, 12, 29)) == (2015, 1)
    b = W.weekly_bars(full, cal, date(2015, 1, 2))[-1]
    assert b["week"] == (2015, 1) and b["sessions"] == 4 and b["last_session"] == date(2015, 1, 2)
    assert W.week_id(date(2014, 12, 31)) not in [x["week"] for x in W.weekly_bars(full, cal, date(2014, 12, 31))]
