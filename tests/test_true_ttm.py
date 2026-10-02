"""D113 True TTM: four most recent visible consecutive quarters, Q4 validated by fiscal-year reconciliation, PIT
timing from the newest component, quarantine/blocks/amendments inherited, no filling."""
from datetime import date, timedelta

from conftest import ROOT, load_module

F = load_module(ROOT / "src/qresearch/lean/qr_fundamentals.py", "qr_fundamentals_ttm")

# fiscal year = calendar year; vendor semantics: '_ttm' on a 10-Q = previous FY total, on the 10-K = this FY
Q = {date(2010, 3, 31): 10, date(2010, 6, 30): 11, date(2010, 9, 30): 12, date(2010, 12, 31): 13,
     date(2011, 3, 31): 14, date(2011, 6, 30): 15}
FY2009, FY2010 = 40, 46


def rec(pe):
    fy = FY2010 if pe >= date(2010, 12, 31) else FY2009
    return {"revenue_q": Q[pe], "revenue_ttm": fy, "total_assets": 1000 + Q[pe]}


def filed(pe):
    return pe + timedelta(days=60 if pe.month == 12 else 35)


def store(blocked=None, skip=(), override=None):
    st = F.PITStore(blocked=blocked)
    for pe in sorted(Q):
        if pe in skip:
            continue
        v = rec(pe)
        if override and pe in override:
            v.update(override[pe])
        st.observe("K", pe, filed(pe), v, None, filed(pe))
    return st


def test_ttm_available_only_after_the_filing_that_completes_it():
    st = store()
    fy_avail = filed(date(2010, 12, 31)) + timedelta(days=1)
    # before the 10-K is visible only three quarters of 2010 exist (Q1-Q3) -> no TTM
    assert st.ttm("K", "revenue", fy_avail - timedelta(days=1)) is None
    st2 = store()
    v, det = st2.ttm_detail("K", "revenue", fy_avail)
    assert v == 10 + 11 + 12 + 13 and det["fy_check_period"] == "2010-12-31"
    st3 = store()
    assert st3.ttm("K", "revenue", filed(date(2011, 6, 30)) + timedelta(days=1)) == 12 + 13 + 14 + 15


def test_inconsistent_q4_gives_no_ttm():
    st = store(override={date(2010, 12, 31): {"revenue_q": 20}})        # Q1..Q4 = 53 != FY 46
    assert st.ttm("K", "revenue", filed(date(2011, 6, 30)) + timedelta(days=1)) is None


def test_missing_or_blocked_quarter_gives_no_ttm():
    assert store(skip=(date(2011, 3, 31),)).ttm("K", "revenue", date(2011, 9, 1)) is None
    blk = {"K": [["2010-09-30", str(filed(date(2010, 9, 30)))]]}
    assert store(blocked=blk).ttm("K", "revenue", date(2011, 9, 1)) is None


def test_snapshot_fields_are_not_summed_and_ttm4q_name_is_whitelisted():
    st = store()
    day = filed(date(2011, 6, 30)) + timedelta(days=1)
    assert st.get("K", "total_assets", day) == 1015 and st.get("K", "revenue_ttm4q", day) == 54
    F.check_field("net_income_ttm4q")


def test_amendment_changes_ttm_only_from_its_filing():
    st = store()
    day = filed(date(2011, 6, 30)) + timedelta(days=1)
    assert st.ttm("K", "revenue", day) == 54
    amend_day = day + timedelta(days=10)
    v = rec(date(2011, 3, 31)); v["revenue_q"] = 16                    # restated Q1 2011 filed later
    st.observe("K", date(2011, 3, 31), amend_day - timedelta(days=1), v, None, amend_day - timedelta(days=1))
    assert st.ttm("K", "revenue", amend_day - timedelta(days=1)) == 54
    assert st.ttm("K", "revenue", amend_day) == 56


def test_approved_field_set_is_the_validated_one():
    assert F.APPROVED_H016_FIELDS == ("revenue_ttm4q", "gross_profit_ttm4q", "net_income_ttm4q",
                                      "operating_cash_flow_ttm4q", "total_assets", "stockholders_equity", "market_cap")
    for f in ("operating_income_ttm4q", "free_cash_flow_ttm4q", "total_debt", "revenue_ttm"):
        assert f not in F.APPROVED_H016_FIELDS
