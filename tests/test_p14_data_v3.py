"""Data v3 (owner D229; research/phase14/data_v3/DATA_V3_spec.md): offline builder functions (qresearch.data_v3) on
synthetic SEC company facts: as-known quarterly values (direct, year-to-date differencing, fourth quarter), restated-
value timelines, guard rows, packing, the review calendar and the SEC-side signals."""
import sys
from datetime import date

import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src"))
from qresearch import data_v3 as V  # noqa: E402


def fact(start, end, val, filed, accn="a"):
    d = {"end": end, "val": val, "filed": filed, "accn": accn, "form": "10-Q"}
    if start:
        d["start"] = start
    return d


def cf(**tags):
    return {"facts": {"us-gaap": {t: {"units": {"USD": v}} for t, v in tags.items()}}}


def test_direct_quarter_and_restatement_timeline():
    fx = V.Facts(cf(Revenues=[fact("2015-01-01", "2015-03-31", 100.0, "2015-05-01", "q1"),
                              fact("2015-01-01", "2015-03-31", 100.5, "2016-05-01", "q1b"),     # within 1.5%
                              fact("2015-01-01", "2015-03-31", 110.0, "2017-05-01", "q1c")]))   # restated
    p = V.dn("2015-03-31")
    assert fx.q_known("revenue", p, V.dn("2015-04-30")) is None            # not filed yet
    assert fx.q_known("revenue", p, V.dn("2015-05-01")) == 100.0
    tl = V.field_timeline(fx, "revenue_q", p)
    assert [v for _d, v in tl] == [100.0, 110.0]
    rows = V.guard_rows(fx, [p])
    assert rows == [(p, 0, V.dn("2017-05-01") - p, V.g4(110.0))]


def test_ytd_differencing_never_takes_ytd_as_quarter():
    # operating cash flow is reported year-to-date only: Q2 = 6M - 3M
    fx = V.Facts(cf(NetCashProvidedByUsedInOperatingActivities=[
        fact("2015-01-01", "2015-03-31", 40.0, "2015-05-01", "a1"),
        fact("2015-01-01", "2015-06-30", 100.0, "2015-08-01", "a2")]))
    p2 = V.dn("2015-06-30")
    assert fx.q_known("operating_cash_flow", p2, V.dn("2015-08-02")) == 60.0
    # without the prior quarter the value is missing (never the 6-month total)
    fx2 = V.Facts(cf(NetCashProvidedByUsedInOperatingActivities=[
        fact("2015-01-01", "2015-06-30", 100.0, "2015-08-01", "a2")]))
    assert fx2.q_known("operating_cash_flow", p2, V.dn("2015-08-02")) is None


def test_fourth_quarter_from_fiscal_year_minus_nine_months():
    fx = V.Facts(cf(Revenues=[fact("2015-01-01", "2015-09-30", 300.0, "2015-11-01", "q3"),
                              fact("2015-01-01", "2015-12-31", 420.0, "2016-02-20", "k")]))
    p4 = V.dn("2015-12-31")
    assert fx.q_known("revenue", p4, V.dn("2016-02-21")) == 120.0
    assert fx.q_known("revenue", p4, V.dn("2016-02-19")) is None


def test_total_assets_and_tag_priority_within_a_filing():
    fx = V.Facts(cf(Assets=[fact(None, "2015-03-31", 500.0, "2015-05-01", "x"),
                            fact(None, "2015-03-31", 520.0, "2016-05-01", "y")],
                    Revenues=[fact("2015-01-01", "2015-03-31", 100.0, "2015-05-01", "x")],
                    SalesRevenueNet=[fact("2015-01-01", "2015-03-31", 90.0, "2015-05-01", "x")]))
    p = V.dn("2015-03-31")
    assert fx.ta_known(p, V.dn("2015-06-01")) == 500.0
    assert fx.ta_known(p, V.dn("2016-06-01")) == 520.0
    assert fx.q_known("revenue", p, V.dn("2015-06-01")) == 100.0      # 'Revenues' precedes 'SalesRevenueNet'


def test_facts_after_2021_are_ignored():
    fx = V.Facts(cf(Revenues=[fact("2021-07-01", "2021-09-30", 100.0, "2021-11-01", "a"),
                              fact("2021-07-01", "2021-09-30", 150.0, "2022-11-01", "b")]))
    tl = V.field_timeline(fx, "revenue_q", V.dn("2021-09-30"))
    assert [v for _d, v in tl] == [100.0]


def test_columnar_round_trip_and_packing():
    rows = {"20": [(5000, 0, 400, 12345609), (5000, 2, 410, -5000607)], "7": [(4000, 4, 90, 20000610)]}
    C = V.columnar(rows)
    back = V.decolumnar(C)
    assert back == {"7": {4000: [(4, 90, 20000610)]}, "20": {5000: [(0, 400, 12345609), (2, 410, -5000607)]}}
    files, sha = V.pack_parts(C, "qr_test")
    assert all(len(t) <= 64_000 for t in files.values())
    assert V.unpack_parts(files, "qr_test") == C
    assert V.ug4(V.g4(123456.0)) == pytest.approx(123500.0)
    assert V.g4(0.5) == 0


def test_review_calendar():
    r = V.review_days()
    assert len(r) == 131 and str(r[0][0]) == "2011-01-31" and str(r[-1][0]) == "2021-11-30"
    d = dict((str(t)[:7], str(t)) for t, _s in r)
    assert d["2013-03"] == "2013-03-28"         # Good Friday 2013-03-29
    assert d["2021-05"] == "2021-05-28"         # Memorial Day 2021-05-31
    assert d["2018-03"] == "2018-03-29"         # Good Friday 2018-03-30
    assert all((s - t).days == 1 for t, s in r)


def _company():
    """Eight consecutive calendar quarters 2014Q1..2015Q4 (+2016Q1), quarterly revenue / GP / NI direct, OCF YTD."""
    rev, gp, ni, ocf, ta = [], [], [], [], []
    ends = ["2014-03-31", "2014-06-30", "2014-09-30", "2014-12-31", "2015-03-31", "2015-06-30", "2015-09-30",
            "2015-12-31", "2016-03-31"]
    starts = ["2014-01-01", "2014-04-01", "2014-07-01", "2014-10-01", "2015-01-01", "2015-04-01", "2015-07-01",
              "2015-10-01", "2016-01-01"]
    for i, (s, e) in enumerate(zip(starts, ends)):
        filed = str(date.fromisoformat(e).replace(day=1).toordinal())
        filed = date.fromordinal(date.fromisoformat(e).toordinal() + 40).isoformat()
        rev.append(fact(s, e, 100.0 + 10 * i, filed, f"x{i}"))
        gp.append(fact(s, e, 40.0 + 5 * i, filed, f"x{i}"))
        ni.append(fact(s, e, 10.0 + i, filed, f"x{i}"))
        ta.append(fact(None, e, 1000.0 + 50 * i, filed, f"x{i}"))
        ystart = e[:4] + "-01-01"
        ocf.append(fact(ystart, e, 20.0 * ((i % 4) + 1), filed, f"x{i}"))     # YTD: 20, 40, 60, 80 -> 20 a quarter
    facts = V.Facts(cf(Revenues=rev, GrossProfit=gp, NetIncomeLoss=ni, Assets=ta,
                       NetCashProvidedByUsedInOperatingActivities=ocf))
    orig = {V.dn(e): V.dn(date.fromordinal(date.fromisoformat(e).toordinal() + 40).isoformat()) for e in ends}
    return facts, orig, ends


def test_sec_signals_anchor_and_formulas():
    fx, orig, ends = _company()
    D = V.dn("2016-05-15")                            # 2016Q1 filed 2016-05-10 -> visible
    a, sig, raw = V.sec_signals(fx, orig, D)
    assert a == V.dn("2016-03-31")
    r = [100.0 + 10 * i for i in range(9)]            # r[8] = 2016Q1
    assert sig["F1"] == pytest.approx((r[8] / r[4] - 1) - (r[7] / r[3] - 1))
    R0, R4 = sum(r[5:9]), sum(r[1:5])
    g = [40.0 + 5 * i for i in range(9)]
    assert sig["F2"] == pytest.approx(sum(g[5:9]) / R0 - sum(g[1:5]) / R4)
    ta0, ta4 = 1000.0 + 50 * 8, 1000.0 + 50 * 4
    assert sig["F4"] == pytest.approx(80.0 / ta0 - 80.0 / ta4)          # OCF TTM = 4 x 20 both years
    assert sig["F8"] == pytest.approx(R0 / ta0 - R4 / ta4)
    assert raw["rq0"] == r[8] and raw["TA0"] == ta0
    # one day before 2016Q1 is public, the anchor is 2015Q4 and needs 2014Q1 .. for the 8-chain -> F2 missing
    a2, sig2, _ = V.sec_signals(fx, orig, V.dn("2016-05-10"))
    assert a2 == V.dn("2015-12-31") and sig2["F2"] is not None and sig2["F1"] is not None
    # stale anchor (> 200 days) -> nothing
    a3, sig3, _ = V.sec_signals(fx, orig, V.dn("2016-12-31"))
    assert a3 is None and all(v is None for v in sig3.values())


def test_sec_signals_invalid_denominator_is_missing():
    fx, orig, ends = _company()
    fx.flows["revenue"][V.dn("2015-03-31")] = [(V.dn("2015-05-10"), "z", 0, V.dn("2015-01-01"), 1, -5.0)]
    _a, sig, _r = V.sec_signals(fx, orig, V.dn("2016-05-15"))
    assert sig["F1"] is None                          # r4 <= 0
