"""Point-in-time fundamentals layer (D108): availability timing, estimated filing dates (+90), quarantine of
accession anomalies, amendments, freshness, missing values, whitelist/blacklist hard failures, financial-format
classification. Pure logic, no QuantConnect."""
from datetime import date, timedelta

import pytest

from conftest import ROOT, load_module

F = load_module(ROOT / "src/qresearch/lean/qr_fundamentals.py", "qr_fundamentals_t")
D = date


def vals(**kw):
    v = {k: None for k in F.WHITELIST}
    v.update(kw)
    return v


def test_whitelist_and_blacklist_fail_loudly():
    F.check_field("gross_profit_ttm")
    F.check_field("market_cap")
    for bad in ("shares_outstanding", "basic_eps", "roe", "accession_number", "book_value_per_share", "morningstar_sector_code"):
        with pytest.raises(F.FundamentalFieldError, match="BLACKLISTED"):
            F.check_field(bad)
    with pytest.raises(F.FundamentalFieldError, match="whitelist"):
        F.check_field("total_revenue_growth")
    store = F.PITStore()
    with pytest.raises(F.FundamentalFieldError):
        store.get("X", "shares_outstanding", D(2015, 1, 1))
    assert all(not any(b == n for b in F.BLACKLIST) for n in F.WHITELIST)


def test_report_visible_only_after_its_filing_date():
    s = F.PITStore()
    pe, fd = D(2020, 12, 31), D(2021, 2, 15)
    s.observe("A", pe, fd, vals(revenue_ttm=10.0), 2021, today=fd)
    assert s.record("A", fd) is None                          # not on the filing date itself
    assert s.record("A", fd + timedelta(days=1)).period_end == pe
    assert s.get("A", "revenue_ttm", fd + timedelta(days=1)) == 10.0
    assert s.record("A", D(2020, 12, 31)) is None             # never before


def test_estimated_file_date_waits_90_days():
    s = F.PITStore()
    pe = D(2011, 3, 31)
    fd = pe + timedelta(days=45)                              # vendor approximation
    assert F.is_estimated_file_date(pe, fd)
    s.observe("A", pe, fd, vals(revenue_ttm=5.0), 2011, today=fd + timedelta(days=1))
    assert s.record("A", fd + timedelta(days=1)) is None
    assert s.record("A", pe + timedelta(days=89)) is None
    assert s.record("A", pe + timedelta(days=90)).period_end == pe
    assert s.stats["estimated"] == 1 and s.stats["delayed_until_available"] == 1


def test_estimated_report_does_not_hide_the_previous_one():
    s = F.PITStore()
    s.observe("A", D(2010, 12, 31), D(2011, 2, 20), vals(revenue_ttm=1.0), 2011, today=D(2011, 2, 21))
    pe2 = D(2011, 3, 31)
    s.observe("A", pe2, pe2 + timedelta(days=45), vals(revenue_ttm=2.0), 2011, today=D(2011, 5, 16))
    assert s.get("A", "revenue_ttm", D(2011, 5, 20)) == 1.0   # previous report still in use
    assert s.get("A", "revenue_ttm", D(2011, 6, 29)) == 2.0   # pe + 90


def test_accession_anomaly_is_quarantined_and_counted_once():
    s = F.PITStore()
    s.observe("A", D(2010, 3, 31), D(2010, 4, 30), vals(revenue_ttm=1.0), 2010, today=D(2010, 5, 1))
    for day in range(3):                                      # the vendor repeats the record daily
        s.observe("A", D(2010, 6, 30), D(2010, 7, 22), vals(revenue_ttm=9.0), 2011, today=D(2010, 7, 23 + day))
    assert s.stats["quarantined"] == 1
    assert s.get("A", "revenue_ttm", D(2010, 8, 1)) == 1.0    # the clean earlier report, never the suspect one


def test_amendment_replaces_only_from_its_own_date():
    s = F.PITStore()
    pe = D(2015, 9, 30)
    s.observe("A", pe, D(2015, 10, 30), vals(net_income_ttm=5.0), 2015, today=D(2015, 10, 31))
    s.observe("A", pe, D(2015, 12, 10), vals(net_income_ttm=4.0), 2015, today=D(2015, 12, 11))
    assert s.get("A", "net_income_ttm", D(2015, 12, 10)) == 5.0
    assert s.get("A", "net_income_ttm", D(2015, 12, 11)) == 4.0
    assert s.stats["amendments"] == 1


def test_freshness_policy():
    s = F.PITStore(max_age_days=200)
    pe = D(2016, 3, 31)
    s.observe("A", pe, D(2016, 5, 1), vals(revenue_ttm=1.0), 2016, today=D(2016, 5, 2))
    assert s.record("A", pe + timedelta(days=200)) is not None
    assert s.record("A", pe + timedelta(days=201)) is None


def test_unknown_or_impossible_timing_never_exposed():
    s = F.PITStore()
    s.observe("A", None, D(2012, 1, 1), vals(revenue_ttm=1.0), None, today=D(2012, 1, 2))
    s.observe("B", D(2012, 3, 31), D(2012, 3, 1), vals(revenue_ttm=1.0), 2012, today=D(2012, 4, 2))
    assert s.record("A", D(2012, 6, 1)) is None and s.record("B", D(2012, 6, 1)) is None
    assert s.stats["timing_unknown"] == 2


def test_missing_values_are_none_not_filled():
    assert F.clean(float("nan")) is None and F.clean(0.0) is None and F.clean(None) is None and F.clean("x") is None
    assert F.clean(3.5) == 3.5


def test_read_values_reads_only_whitelisted_paths():
    seen = []

    class Obj:
        def __getattr__(self, name):
            return 7.0

    def getter(f, path):
        seen.append(path)
        return Obj()
    v = F.read_values(object(), getter)
    assert set(v) == set(F.WHITELIST) and all(x == 7.0 for x in v.values())
    assert all("shares" not in p and "eps" not in p for p in seen)


def test_financial_format_classification():
    bank = vals(revenue_ttm=100.0, net_income_ttm=10.0, total_assets=1000.0)
    industrial = vals(revenue_ttm=100.0, gross_profit_ttm=40.0, cost_of_revenue_ttm=60.0, operating_income_ttm=15.0)
    services = vals(revenue_ttm=100.0, operating_income_ttm=12.0)          # no COGS line, but operating income
    assert F.financial_format(bank) is True
    assert F.financial_format(industrial) is False and F.financial_format(services) is False
    assert F.financial_format(vals()) is None                              # no revenue: unclassifiable


def test_accession_year_parse():
    assert F.accession_year("0000320193-14-000005") == 2014 and F.accession_year("x") is None


def test_sec_timing_hold_only_delays():
    """D111: a hold delays a vendor report to the day after its first public SEC source; never earlier."""
    from datetime import date
    st = F.PITStore(holds={"K": {"2016-03-31": "2016-05-07"}})
    st.observe("K", date(2016, 3, 31), date(2016, 4, 28), {"revenue_ttm": 1.0}, None, date(2016, 4, 29))
    assert st.record("K", date(2016, 5, 6)) is None and st.record("K", date(2016, 5, 7)) is not None
    st2 = F.PITStore(holds={"K": {"2016-03-31": "2016-04-01"}})       # hold earlier than vendor date: no effect
    st2.observe("K", date(2016, 3, 31), date(2016, 4, 28), {"revenue_ttm": 1.0}, None, date(2016, 4, 29))
    assert st2.record("K", date(2016, 4, 28)) is None and st2.record("K", date(2016, 4, 29)) is not None
    assert F.PITStore().holds == {}


def test_quarantine_release_only_listed_records():
    """D111: only quarantined reports on the SEC-verified release list leave quarantine."""
    from datetime import date
    rel = {"K": [["2009-12-31", "2010-02-20"]]}
    st = F.PITStore(releases=rel)
    today = date(2010, 3, 1)
    st.observe("K", date(2009, 12, 31), date(2010, 2, 20), {"revenue_ttm": 1.0}, 2011, today)   # listed
    st.observe("J", date(2009, 12, 31), date(2010, 2, 20), {"revenue_ttm": 1.0}, 2011, today)   # not listed
    assert st.get("K", "revenue_ttm", today) == 1.0 and st.record("J", today) is None
    assert st.stats["quarantine_released"] == 1 and st.stats["quarantined"] == 1


def test_restatement_block_keeps_previous_record():
    """D111: a vendor report carrying a later (restated) value is never exposed; the previous record stays."""
    from datetime import date
    st = F.PITStore(blocked={"K": [["2012-06-30", "2012-07-25"]]})
    st.observe("K", date(2012, 3, 31), date(2012, 4, 25), {"revenue_ttm": 1.0}, None, date(2012, 4, 26))
    st.observe("K", date(2012, 6, 30), date(2012, 7, 25), {"revenue_ttm": 2.0}, None, date(2012, 7, 26))
    r = st.record("K", date(2012, 8, 1))
    assert r.period_end == date(2012, 3, 31) and st.stats["restatement_blocked"] == 1
