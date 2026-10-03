"""SEC 8-K earnings-release events (qresearch.sec_events): timing classes, de-duplication, amendments and
point-in-time visibility (the P2-CP12 leakage canaries)."""
from datetime import date, datetime, timedelta

import pytest

from qresearch import sec_events as S

CAL = S.Calendar([date(2019, 10, d) for d in (28, 29, 30, 31)] + [date(2019, 11, d) for d in (1, 4, 5)]
                 + [date(2019, 11, 27), date(2019, 11, 29), date(2019, 12, 2)])


def f(acc, accept_utc, form="8-K", items="2.02,9.01", filed=None):
    return dict(accessionNumber=acc, acceptanceDateTime=accept_utc, form=form, items=items,
                filingDate=filed or accept_utc[:10], reportDate=accept_utc[:10])


def test_acceptance_is_utc_converted_to_eastern_with_dst():
    assert S.acceptance_et("2019-10-30T20:30:40.000Z") == datetime(2019, 10, 30, 16, 30, 40)    # EDT (UTC-4)
    assert S.acceptance_et("2019-12-02T21:05:00.000Z") == datetime(2019, 12, 2, 16, 5, 0)      # EST (UTC-5)
    assert S.acceptance_et("") is None


@pytest.mark.parametrize("utc,cls,event,execution", [
    ("2019-10-30T12:01:00.000Z", "BMO", date(2019, 10, 30), date(2019, 10, 31)),     # 08:01 ET
    ("2019-10-30T15:00:00.000Z", "DURING", date(2019, 10, 30), date(2019, 10, 31)),  # 11:00 ET
    ("2019-10-30T20:30:40.000Z", "AMC", date(2019, 10, 31), date(2019, 11, 1)),     # 16:30 ET
    ("2019-11-02T14:00:00.000Z", "NONSESSION", date(2019, 11, 4), date(2019, 11, 5)),  # Saturday
    ("2019-11-29T18:30:00.000Z", "AMC", date(2019, 12, 2), None),                    # 13:30 ET on an early close
])
def test_timing_classes_and_earliest_execution(utc, cls, event, execution):
    a = S.acceptance_et(utc)
    c = S.classify(a, a.date(), CAL)
    assert c["cls"] == cls and c["event_session"] == event
    if execution is not None:
        assert c["execution_session"] == execution


def test_after_close_event_never_trades_the_same_day_or_the_next_open():
    a = S.acceptance_et("2019-10-30T20:30:40.000Z")
    c = S.classify(a, a.date(), CAL)
    assert c["decision_session"] > a.date() and c["execution_session"] > c["decision_session"]


def test_unknown_time_is_treated_as_after_close_of_the_filing_date():
    c = S.classify(None, date(2019, 10, 30), CAL)
    assert c["cls"] == "UNKNOWN" and c["event_session"] == date(2019, 10, 31)


def test_filing_is_invisible_before_sec_acceptance():
    ev = S.build_events(1, [f("a1", "2019-10-30T20:30:40.000Z")], CAL)["events"]
    acc = ev[0].acceptance
    assert S.visible(ev, acc - timedelta(seconds=1)) == []
    assert S.visible(ev, acc) == ev
    # decision close (16:00 ET of the decision session) is never before acceptance
    assert datetime.combine(ev[0].decision_session, S.CLOSE) >= acc


def test_amendments_never_create_or_modify_events():
    base = [f("a1", "2019-10-30T20:30:40.000Z")]
    with_amend = base + [f("a2", "2019-10-28T12:00:00.000Z", form="8-K/A")]     # earlier time, amended form
    e1, e2 = S.build_events(1, base, CAL), S.build_events(1, with_amend, CAL)
    assert [(e.accession, e.acceptance, e.cls) for e in e1["events"]] == \
           [(e.accession, e.acceptance, e.cls) for e in e2["events"]]
    assert e2["amendments"] == ["a2"]


def test_duplicates_cannot_create_duplicate_opportunities():
    rows = [f("a1", "2019-10-30T20:30:40.000Z"), f("a2", "2019-10-30T20:31:10.000Z"),   # same-day re-filing
            f("a3", "2019-11-27T12:00:00.000Z")]                                     # within 30 days
    r = S.build_events(1, rows, CAL)
    assert len(r["events"]) == 1 and r["events"][0].accession == "a1" and r["duplicates"] == 2


def test_non_earnings_and_item12_filings():
    rows = [f("x", "2019-10-29T12:00:00.000Z", items="8.01,9.01"),
            f("y", "2019-10-30T12:00:00.000Z", items="12")]
    r = S.build_events(1, rows, CAL)
    assert [e.accession for e in r["events"]] == ["y"]


def test_mislabelled_eastern_files_are_not_shifted():
    assert S.acceptance_et("2016-07-12T18:07:04.000Z", "ET") == datetime(2016, 7, 12, 18, 7, 4)
    assert S.acceptance_et("2016-07-12T22:07:04.000Z", "UTC") == datetime(2016, 7, 12, 18, 7, 4)
    with pytest.raises(ValueError):
        S.acceptance_et("2016-07-12T22:07:04.000Z", "PST")
    r = S.build_events(1, [f("a1", "2019-10-30T16:30:40.000Z")], CAL, tz="ET")
    assert r["events"][0].cls == "AMC" and r["events"][0].acceptance == datetime(2019, 10, 30, 16, 30, 40)
