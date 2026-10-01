"""Dated SEC correction layer (D111): availability after filing, cover-share age limit, live split handling,
status gating and feeding the PIT store."""
from datetime import date

from conftest import ROOT, load_module

C = load_module(ROOT / "src/qresearch/lean/qr_sec_corrections.py", "qr_sec_corrections")
F = load_module(ROOT / "src/qresearch/lean/qr_fundamentals.py", "qr_fundamentals_c")


def table(status="repaired"):
    return {"X SID": {"cik": 1, "status": status, "filings": [
        ["a1", "10-K", "2011-02-20", "2010-12-31", "2011-02-10", 100e6, {"revenue_ttm": 5e9, "net_income_ttm": 1e8,
                                                                         "total_assets": 9e9, "stockholders_equity": 4e9}],
        ["a2", "10-Q", "2011-05-05", "2011-03-31", "2011-04-29", 110e6, {"revenue_ttm": 5.2e9}],
        ["a3", "10-Q", "2011-08-05", "2011-06-30", None, None, {}],                      # no unambiguous cover
    ]}}


def test_market_cap_only_after_filing_and_until_age_limit():
    s = C.SECCorrections(table())
    assert s.market_cap("X SID", date(2011, 2, 20), 30.0) is None          # filing day itself: not yet usable
    assert s.market_cap("X SID", date(2011, 2, 21), 30.0) == 100e6 * 30
    assert s.market_cap("X SID", date(2011, 5, 6), 30.0) == 110e6 * 30
    # a3 has no cover count: a2's count stays in use until it is older than the limit, then nothing
    assert s.market_cap("X SID", date(2011, 9, 10), 30.0) == 110e6 * 30
    assert s.market_cap("X SID", date(2011, 4, 29) + __import__("datetime").timedelta(days=136), 30.0) is None


def test_split_after_cover_date_only():
    s = C.SECCorrections(table())
    s.observe_split("X SID", date(2011, 3, 1), 0.5)       # 2-for-1 after a1's cover date
    assert s.market_cap("X SID", date(2011, 3, 2), 15.0) == 200e6 * 15
    assert s.market_cap("X SID", date(2011, 2, 25), 30.0) == 100e6 * 30      # before the ex-date: unchanged
    assert s.market_cap("X SID", date(2011, 5, 6), 15.0) == 110e6 * 15       # a2 cover is after the split


def test_unrepaired_status_never_used():
    for st in ("unresolved", "rejected", "ambiguous"):
        s = C.SECCorrections(table(st))
        assert not s.has("X SID") and s.market_cap("X SID", date(2011, 6, 1), 30.0) is None


def test_feed_respects_pit_rules():
    s = C.SECCorrections(table())
    st = F.PITStore()
    for day in (date(2011, 2, 20), date(2011, 2, 21)):
        s.feed("X SID", day, st)
    assert st.record("X SID", date(2011, 2, 20)) is None
    assert st.get("X SID", "revenue_ttm", date(2011, 2, 21)) == 5e9
    s.feed("X SID", date(2011, 5, 6), st)
    assert st.get("X SID", "revenue_ttm", date(2011, 5, 6)) == 5.2e9
