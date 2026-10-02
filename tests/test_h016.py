"""H016 decision logic (qr_h016): GP/A from historically available data only (same-quarter assets, positive assets,
negative gross profit allowed, truncation-safe), the quarterly schedule, deterministic GP/A and random rankings, and
the selection plan (exits, entries in rank order, continuing holdings untouched)."""
from datetime import date, timedelta

from conftest import ROOT, load_module

F = load_module(ROOT / "src/qresearch/lean/qr_fundamentals.py", "qr_fundamentals_h016")
H = load_module(ROOT / "src/qresearch/lean/qr_h016.py", "qr_h016_under_test")

GP = {date(2010, 3, 31): 10.0, date(2010, 6, 30): 11.0, date(2010, 9, 30): 12.0, date(2010, 12, 31): 13.0,
      date(2011, 3, 31): 14.0}


def filed(pe):
    return pe + timedelta(days=60 if pe.month == 12 else 35)


def build(gp=GP, assets=lambda pe: 1000.0, upto=None):
    st = F.PITStore()
    for pe in sorted(gp):
        if upto is not None and filed(pe) > upto:
            continue
        fy = 46.0 if pe >= date(2010, 12, 31) else 40.0
        st.observe("K", pe, filed(pe), {"gross_profit_q": gp[pe], "gross_profit_ttm": fy, "total_assets": assets(pe)},
                   None, filed(pe))
    return st


def test_gpa_uses_ttm_and_same_quarter_assets():
    day = filed(date(2010, 12, 31)) + timedelta(days=1)
    v, det = H.gpa(build(), "K", day)
    assert v == (10 + 11 + 12 + 13) / 1000.0
    assert det["assets_period"] == det["quarters"][-1] == "2010-12-31"
    assert all(fd < str(day) for fd in det["filed"]) and det["assets_filed"] < str(day)


def test_gpa_never_uses_information_after_the_decision_date():
    # truncation test: the value on T is identical whether or not later filings exist in the store
    day = filed(date(2010, 12, 31)) + timedelta(days=10)
    full, trunc = build(), build(upto=day - timedelta(days=1))
    assert H.gpa(full, "K", day)[0] == H.gpa(trunc, "K", day)[0]
    assert H.gpa(full, "K", filed(date(2010, 12, 31)))[0] is None          # the 10-K's own filing day: not yet


def test_gpa_invalid_denominator_and_negative_gross_profit():
    day = filed(date(2010, 12, 31)) + timedelta(days=1)
    assert H.gpa(build(assets=lambda pe: 0.0), "K", day)[0] is None
    assert H.gpa(build(assets=lambda pe: -5.0), "K", day)[0] is None
    neg = dict(GP)
    neg[date(2010, 12, 31)] = -60.0                      # FY total must reconcile: Q1..Q4 = 10+11+12-60 = -27
    st = F.PITStore()
    for pe in sorted(neg):
        fy = -27.0 if pe >= date(2010, 12, 31) else 40.0
        st.observe("K", pe, filed(pe), {"gross_profit_q": neg[pe], "gross_profit_ttm": fy, "total_assets": 1000.0},
                   None, filed(pe))
    assert H.gpa(st, "K", day)[0] == -27.0 / 1000.0


def test_gpa_requires_assets_from_the_newest_ttm_quarter():
    st = F.PITStore()
    for pe in sorted(GP):
        if pe == date(2011, 3, 31):
            continue
        fy = 46.0 if pe >= date(2010, 12, 31) else 40.0
        vals = {"gross_profit_q": GP[pe], "gross_profit_ttm": fy}
        if pe != date(2010, 12, 31):
            vals["total_assets"] = 1000.0
        st.observe("K", pe, filed(pe), vals, None, filed(pe))
    day = filed(date(2010, 12, 31)) + timedelta(days=1)
    assert H.gpa(st, "K", day)[0] is None                 # newest report lacks total assets: no mixing with older


def test_freshness_limit_for_the_perturbation():
    day = filed(date(2010, 12, 31)) + timedelta(days=1)                       # newest quarter 61 days old
    assert H.gpa(build(), "K", day, max_age_days=120)[0] is not None
    no_q1 = {pe: v for pe, v in GP.items() if pe <= date(2010, 12, 31)}  # no newer quarter ever arrives
    assert H.gpa(build(no_q1), "K", day + timedelta(days=70), max_age_days=120)[0] is None   # 131 days old
    assert H.gpa(build(no_q1), "K", day + timedelta(days=70))[0] is not None                 # base: 200 days


def test_rebalance_days_are_first_sessions_of_the_quarter_months():
    assert H.is_rebalance_day(date(2010, 3, 1), date(2010, 2, 26))
    assert not H.is_rebalance_day(date(2010, 3, 2), date(2010, 3, 1))
    assert not H.is_rebalance_day(date(2010, 4, 1), date(2010, 3, 31))
    assert H.is_rebalance_day(date(2010, 6, 1), date(2010, 5, 28))
    assert H.is_rebalance_day(date(2010, 3, 1), None)
    assert H.is_rebalance_day(date(2010, 4, 1), date(2010, 3, 31), months=(1, 4, 7, 10))


def test_rankings_are_deterministic():
    assert H.rank_gpa({"B": 0.5, "A": 0.5, "C": 0.9, "D": -0.1}) == ["C", "A", "B", "D"]
    keys = [f"S{i}" for i in range(50)]
    r1 = H.rank_random(keys, 1)
    assert r1 == H.rank_random(list(reversed(keys)), 1)              # order-independent
    assert r1 != H.rank_random(keys, 2)                              # seeds differ
    assert H.rank_random(keys[:10], 1) == [k for k in r1 if k in keys[:10]]   # persistent key per security


def test_selection_plan_keeps_continuing_holdings():
    sel, exits, entries = H.plan_selection(["A", "B", "C", "D", "E"], {"B": 1, "X": 1, "D": 1}, 3)
    assert sel == ["A", "B", "C"] and exits == ["D", "X"] and entries == ["A", "C"]
