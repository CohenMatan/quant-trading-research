"""D114 field-level quarantine release: only SEC-verified flow fields of a quarantined report are released, as a
partial record that feeds True TTM but is never the current report (its balance sheet stays hidden); nothing is
released earlier than the report's own availability; restatement blocks still win."""
from datetime import date, timedelta

from conftest import ROOT, load_module

F = load_module(ROOT / "src/qresearch/lean/qr_fundamentals.py", "qr_fundamentals_frel")

Q = {date(2010, 3, 31): 10, date(2010, 6, 30): 11, date(2010, 9, 30): 12, date(2010, 12, 31): 13,
     date(2011, 3, 31): 14}
FY2009, FY2010 = 40, 46
QUAR = date(2010, 6, 30)              # this 10-Q carries an anomalous (later) accession year -> quarantined


def filed(pe):
    return pe + timedelta(days=60 if pe.month == 12 else 35)


def vals(pe):
    fy = FY2010 if pe >= date(2010, 12, 31) else FY2009
    return {"revenue_q": Q[pe], "revenue_ttm": fy, "net_income_q": 1.0, "total_assets": 999.0 + Q[pe],
            "stockholders_equity": 500.0}


def store(field_releases=None, blocked=None):
    st = F.PITStore(field_releases=field_releases, blocked=blocked)
    for pe in sorted(Q):
        ay = 2011 if pe == QUAR else None     # accession year after the decision year -> quarantine
        st.observe("K", pe, filed(pe), vals(pe), ay, filed(pe))
    return st


REL = {"K": [[str(QUAR), str(filed(QUAR)), ["revenue_q", "revenue_ttm", "total_assets"]]]}
AFTER_10K = filed(date(2010, 12, 31)) + timedelta(days=1)


def test_without_release_the_quarantine_hole_blocks_ttm():
    assert store().ttm("K", "revenue", AFTER_10K) is None


def test_released_flow_fields_complete_the_ttm():
    st = store(REL)
    assert st.ttm("K", "revenue", AFTER_10K) == 10 + 11 + 12 + 13


def test_balance_sheet_is_never_released_and_partial_is_never_current():
    st = store(REL)
    day = filed(QUAR) + timedelta(days=5)
    r = st.record("K", day)                            # promotes everything visible on that day
    # 'total_assets' was listed but is not releasable; 'net_income_q' was not listed
    part = st.hist["K"][QUAR]
    assert part.partial and set(part.values) == {"revenue_q", "revenue_ttm"}
    # between the quarantined 10-Q and the next report, the current report stays the clean Q1 record
    assert r is not None and r.period_end == date(2010, 3, 31) and not r.partial
    assert st.get("K", "total_assets", day) == 999.0 + 10
    # net income was not released -> no net-income TTM through the hole
    assert st.ttm("K", "net_income", AFTER_10K) is None


def test_release_never_earlier_than_availability():
    st2 = F.PITStore(field_releases=REL)
    st2.observe("K", QUAR, filed(QUAR), vals(QUAR), 2011, filed(QUAR))
    st2.record("K", filed(QUAR))                       # the filing day itself: not yet available
    assert QUAR not in st2.hist.get("K", {})
    st2.record("K", filed(QUAR) + timedelta(days=1))
    assert QUAR in st2.hist["K"]


def test_restatement_block_wins_over_field_release():
    blk = {"K": [[str(QUAR), str(filed(QUAR))]]}
    assert store(REL, blocked=blk).ttm("K", "revenue", AFTER_10K) is None


def test_partial_record_never_replaces_an_existing_report():
    st = F.PITStore(field_releases={"K": [[str(QUAR), str(filed(QUAR) + timedelta(days=3)), ["revenue_q"]]]})
    st.observe("K", QUAR, filed(QUAR), vals(QUAR), None, filed(QUAR))                       # clean report
    st.observe("K", QUAR, filed(QUAR) + timedelta(days=3), {"revenue_q": 99.0}, 2011, filed(QUAR) + timedelta(days=3))
    st.record("K", filed(QUAR) + timedelta(days=10))
    assert st.hist["K"][QUAR].values["revenue_q"] == 11 and not st.hist["K"][QUAR].partial


def test_partial_without_fiscal_year_value_does_not_fake_a_fiscal_year_end():
    # Q2 released WITHOUT its fiscal-year value; Q3's fiscal-year value (FY2009 = 40) is unchanged from Q1's, so Q3
    # must not be taken as a fiscal-year end even if its trailing four quarters happened to sum to 40
    rel = {"K": [[str(QUAR), str(filed(QUAR)), ["revenue_q"]]]}
    st = F.PITStore(field_releases=rel)
    q = {date(2009, 12, 31): 9.0, date(2010, 3, 31): 10.0, date(2010, 6, 30): 11.0, date(2010, 9, 30): 10.0}
    for pe, v in sorted(q.items()):
        st.observe("K", pe, filed(pe), {"revenue_q": v, "revenue_ttm": 40.0}, 2011 if pe == QUAR else None, filed(pe))
    # 9 + 10 + 11 + 10 = 40 = FY2009 total by coincidence: no fiscal-year end inside the window -> no TTM
    assert st.ttm("K", "revenue", filed(date(2010, 9, 30)) + timedelta(days=1)) is None
