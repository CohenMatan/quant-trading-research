"""Point-in-time earnings-release events from SEC 8-K filings (P2-CP12 audit; infrastructure, no returns).

Source: data.sec.gov submissions (form, items, filingDate, reportDate, acceptanceDateTime, accession).
TIME ZONE (P2-CP12 timestamp canary): the submissions JSON labels acceptanceDateTime with 'Z', but per registrant file
it is EITHER true UTC OR US Eastern wall-clock time mislabelled as UTC (consistent within a file; verified against the
EDGAR filing index pages, which show Eastern time). The convention of each cached file is therefore determined
against index pages (research/phase2/earnings_audit/tz_conventions.json) and passed as `tz` ("UTC" or "ET").

An earnings-release filing is an ORIGINAL 8-K whose items include 2.02 "Results of Operations and Financial
Condition" (from 2004-08-23) or its predecessor 12 (2003-03-28 .. 2004-08-22).

Deterministic rules (frozen for the audit; any later strategy must re-use them unchanged):
  * Amendments (8-K/A) never create, move or modify an event; they are only counted.
  * De-duplication: an original earnings 8-K starts a new event only if no event of the same registrant (CIK) started
    within the previous DEDUP_DAYS calendar days (measured from that event's first acceptance); otherwise it is
    recorded as a duplicate of the open event (pre-announcement + full release, corrected re-filings, multi-class
    co-filings). The event keeps the FIRST acceptance time.
  * Timing class from the Eastern acceptance time on the acceptance date D:
        BMO     D is a session and time < 09:30
        DURING  D is a session and 09:30 <= time < close (16:00; 13:00 on early-close days)
        AMC     D is a session and time >= close
        NONSESSION  D is a weekend or holiday
        UNKNOWN no usable time of day (missing or 00:00:00); handled as AMC of the filing date (conservative)
  * Event session E = D for BMO and DURING; the next session after D for AMC, NONSESSION and UNKNOWN.
  * Under the project's engine (decisions at a session's close, orders at the next open), the earliest decision is
    the close of E and the earliest execution is the open of the session after E. (For BMO, a trade at E's open would
    be legal in reality, but the engine never decides before a close.)
  * Visibility: an event is visible at Eastern time t only if its first acceptance <= t (visible()).
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
OPEN, CLOSE, EARLY_CLOSE_TIME = time(9, 30), time(16, 0), time(13, 0)
DEDUP_DAYS = 30
EARNINGS_ITEMS = ("2.02", "12")
# NYSE early closes (13:00 ET), 2010-2021
EARLY_CLOSE = {date(2010, 11, 26), date(2011, 11, 25), date(2012, 7, 3), date(2012, 11, 23), date(2012, 12, 24),
               date(2013, 7, 3), date(2013, 11, 29), date(2013, 12, 24), date(2014, 7, 3), date(2014, 11, 28),
               date(2014, 12, 24), date(2015, 11, 27), date(2015, 12, 24), date(2016, 11, 25), date(2017, 7, 3),
               date(2017, 11, 24), date(2018, 7, 3), date(2018, 11, 23), date(2018, 12, 24), date(2019, 7, 3),
               date(2019, 11, 29), date(2019, 12, 24), date(2020, 11, 27), date(2020, 12, 24), date(2021, 11, 26)}


def acceptance_et(s, tz: str = "UTC") -> datetime | None:
    """submissions acceptanceDateTime ('2019-10-30T20:30:40.000Z') -> naive US Eastern datetime. tz = the file's
    actual convention: "UTC" (convert) or "ET" (already Eastern wall-clock time despite the 'Z')."""
    s = str(s or "").strip()
    if len(s) < 19:
        return None
    try:
        dt = datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    if tz == "ET":
        return dt
    if tz != "UTC":
        raise ValueError(f"unknown time-zone convention {tz!r}")
    return dt.replace(tzinfo=timezone.utc).astimezone(ET).replace(tzinfo=None)


def items_of(f) -> list[str]:
    return [i.strip() for i in str(f.get("items") or "").split(",") if i.strip()]


def is_earnings_filing(f) -> bool:
    return any(i in EARNINGS_ITEMS for i in items_of(f))


class Calendar:
    def __init__(self, sessions):
        self.sessions = sorted(set(sessions))
        self._set = set(self.sessions)

    def is_session(self, d):
        return d in self._set

    def next_after(self, d):
        i = bisect.bisect_right(self.sessions, d)
        return self.sessions[i] if i < len(self.sessions) else None

    def close_time(self, d):
        return EARLY_CLOSE_TIME if d in EARLY_CLOSE else CLOSE


def classify(acc: datetime | None, filing_date: date, cal: Calendar) -> dict:
    """Timing class, event session, earliest decision session (close) and earliest execution session (open)."""
    if acc is None or acc.time() == time(0, 0, 0):
        cls, d = "UNKNOWN", filing_date
        e = cal.next_after(d)
    else:
        d, t = acc.date(), acc.time()
        if not cal.is_session(d):
            cls, e = "NONSESSION", cal.next_after(d)
        elif t < OPEN:
            cls, e = "BMO", d
        elif t < cal.close_time(d):
            cls, e = "DURING", d
        else:
            cls, e = "AMC", cal.next_after(d)
    return dict(cls=cls, event_session=e, decision_session=e, execution_session=None if e is None else cal.next_after(e))


@dataclass
class Event:
    cik: int
    accession: str
    acceptance: datetime | None
    filing_date: date
    report_date: date | None
    items: list[str]
    cls: str = ""
    event_session: date | None = None
    decision_session: date | None = None
    execution_session: date | None = None
    duplicates: list[str] = field(default_factory=list)


def _d(s):
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def build_events(cik: int, filings: list[dict], cal: Calendar, dedup_days: int = DEDUP_DAYS, tz: str = "UTC") -> dict:
    """Events of one registrant from its submissions rows. Returns dict(events, amendments, duplicates)."""
    orig, amends = [], []
    for f in filings:
        if not is_earnings_filing(f):
            continue
        form = str(f.get("form", ""))
        if form == "8-K":
            orig.append(f)
        elif form == "8-K/A":
            amends.append(f["accessionNumber"])

    def key(f):
        a = acceptance_et(f.get("acceptanceDateTime"), tz)
        return (a or datetime.combine(_d(f["filingDate"]), time(23, 59, 59)), f["accessionNumber"])
    events = []
    for f in sorted(orig, key=key):
        a = acceptance_et(f.get("acceptanceDateTime"), tz)
        when = key(f)[0]
        if events:
            last = events[-1]
            ref = last.acceptance or datetime.combine(last.filing_date, time(23, 59, 59))
            if (when - ref) < timedelta(days=dedup_days):
                last.duplicates.append(f["accessionNumber"])
                continue
        fd = _d(f["filingDate"])
        ev = Event(cik=int(cik), accession=f["accessionNumber"], acceptance=a, filing_date=fd,
                   report_date=_d(f.get("reportDate")), items=items_of(f))
        c = classify(a, fd, cal)
        ev.cls, ev.event_session = c["cls"], c["event_session"]
        ev.decision_session, ev.execution_session = c["decision_session"], c["execution_session"]
        events.append(ev)
    return dict(events=events, amendments=amends, duplicates=sum(len(e.duplicates) for e in events))


def visible(events: list[Event], as_of: datetime) -> list[Event]:
    """Events whose first SEC acceptance is at or before Eastern time `as_of` (point-in-time view)."""
    return [e for e in events if e.acceptance is not None and e.acceptance <= as_of
            or e.acceptance is None and datetime.combine(e.filing_date, time(23, 59, 59)) <= as_of]
