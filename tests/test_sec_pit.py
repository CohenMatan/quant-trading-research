"""SEC XBRL point-in-time record builder (D111): values as first filed, TTM arithmetic only from filings made on or
before the record's filing date, cover-page shares from the filing's own cover only."""
from qresearch import sec_pit as P


def fact(val, end, accn, filed, form="10-Q", start=None):
    f = {"val": val, "end": end, "accn": accn, "filed": filed, "form": form, "fy": 2011, "fp": "Q"}
    if start:
        f["start"] = start
    return f


def company(extra_later=False):
    rev = [
        # 10-K FY2010 (filed 2011-02-20)
        fact(400, "2010-12-31", "K10", "2011-02-20", "10-K", "2010-01-01"),
        fact(300, "2010-09-30", "Q310", "2010-11-05", "10-Q", "2010-01-01"),       # 9M 2010
        # Q1 2011 10-Q: current quarter and prior-year comparative
        fact(110, "2011-03-31", "Q111", "2011-05-05", "10-Q", "2011-01-01"),
        fact(90, "2010-03-31", "Q111", "2011-05-05", "10-Q", "2010-01-01"),
        # Q2 2011 10-Q: quarter + 6M YTD and comparatives
        fact(120, "2011-06-30", "Q211", "2011-08-05", "10-Q", "2011-04-01"),
        fact(230, "2011-06-30", "Q211", "2011-08-05", "10-Q", "2011-01-01"),
        fact(190, "2010-06-30", "Q211", "2011-08-05", "10-Q", "2010-01-01"),
    ]
    if extra_later:   # a later 10-K restates FY2010 (must never reach the Q1/Q2 2011 records)
        rev.append(fact(999, "2010-12-31", "K11", "2012-02-20", "10-K", "2010-01-01"))
    assets = [fact(1000, "2011-03-31", "Q111", "2011-05-05"), fact(1100, "2011-06-30", "Q211", "2011-08-05"),
              fact(950, "2010-12-31", "K10", "2011-02-20", "10-K")]
    shares = [fact(50, "2011-04-29", "Q111", "2011-05-05"), fact(51, "2011-07-29", "Q211", "2011-08-05"),
              fact(49, "2011-02-10", "K10", "2011-02-20", "10-K")]
    return {"facts": {"us-gaap": {"Revenues": {"units": {"USD": rev}}, "Assets": {"units": {"USD": assets}}},
                      "dei": {"EntityCommonStockSharesOutstanding": {"units": {"shares": shares}}}}}


def recs(cf):
    facts = P.index_facts(cf)
    subs = [{"accessionNumber": a, "reportDate": pe, "acceptanceDateTime": None}
            for a, pe in (("K10", "2010-12-31"), ("Q111", "2011-03-31"), ("Q211", "2011-06-30"), ("Q310", "2010-09-30"),
                          ("K11", "2011-12-31"))]
    out = {}
    for fl in P.periodic_filings(facts, subs):
        out[fl["accn"]] = (fl, P.record_for(facts, fl)["values"], P.cover_shares(facts, fl))
    return out


def test_ttm_and_quarters_as_first_filed():
    r = recs(company())
    assert r["K10"][1]["revenue_ttm"] == 400 and r["K10"][1]["revenue_q"] == 100        # FY - 9M (known earlier)
    # interim "ttm" = latest completed fiscal year as filed (vendor semantics, E971-02)
    assert r["Q111"][1]["revenue_ttm"] == 400 and r["Q111"][1]["revenue_q"] == 110
    assert r["Q211"][1]["revenue_ttm"] == 400 and r["Q211"][1]["revenue_q"] == 120
    assert r["Q111"][1]["total_assets"] == 1000 and r["Q111"][1]["total_debt"] is None


def test_later_restatement_never_used_before_its_filing():
    r = recs(company(extra_later=True))
    assert r["Q111"][1]["revenue_ttm"] == 400 and r["Q211"][1]["revenue_ttm"] == 400


def test_cover_shares_own_filing_only():
    r = recs(company())
    assert r["Q111"][2] == ("2011-04-29", 50.0) and r["K10"][2] == ("2011-02-10", 49.0)
    assert r["Q310"][2] == (None, None)


def test_ambiguous_cover_is_unresolved():
    cf = company()
    cf["facts"]["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"].append(
        fact(7, "2011-04-29", "Q111", "2011-05-05"))
    assert recs(cf)["Q111"][2] == (None, None)


def test_duration_classes():
    assert P.dur_class("2011-01-01", "2011-03-31") == 1 and P.dur_class("2011-01-01", "2011-12-31") == 4
    assert P.dur_class("2011-01-01", "2011-06-30") == 2 and P.dur_class("2011-01-01", "2011-09-30") == 3
    assert P.dur_class("2011-01-01", "2011-02-15") is None
