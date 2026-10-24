"""OD-1 (owner D308): the SEC extension-object builder's fact selection on synthetic companyfacts (no network)."""
import sys
from datetime import date

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research/od"))
import build_od1_sec as B  # noqa: E402


def fact(accn, start, end, val):
    f = {"accn": accn, "end": end, "val": val}
    if start:
        f["start"] = start
    return f


def cf(tags):
    return {"facts": {"us-gaap": {t: {"units": {"USD": fs}} for t, fs in tags.items()}}}


def test_value_filters_by_filing_duration_and_instant():
    fs = [fact("A", "2020-01-01", "2020-12-31", 100), fact("B", "2020-01-01", "2020-12-31", 999),
          fact("A", "2020-10-01", "2020-12-31", 30), fact("A", None, "2020-12-31", 500)]
    lo, hi = date(2020, 12, 24), date(2021, 1, 7)
    assert B.value(fs, "A", lo, hi, (350, 380)) == 100
    assert B.value(fs, "A", lo, hi, (80, 100)) == 30
    assert B.value(fs, "A", lo, hi) == 500
    assert B.value(fs + [fact("A", "2020-01-01", "2020-12-31", 101)], "A", lo, hi, (350, 380)) == "AMB"


def test_row_k_and_q_with_comparatives_and_gp_fallback():
    acc = "0001-21-000001"
    c = cf({
        "Revenues": [fact(acc, "2020-01-01", "2020-12-31", 1000), fact(acc, "2019-01-01", "2019-12-31", 800)],
        "NetIncomeLoss": [fact(acc, "2020-01-01", "2020-12-31", 100), fact(acc, "2019-01-01", "2019-12-31", 90)],
        "CostOfRevenue": [fact(acc, "2020-01-01", "2020-12-31", 600), fact(acc, "2019-01-01", "2019-12-31", 500)],
        "NetCashProvidedByUsedInOperatingActivities": [fact(acc, "2020-01-01", "2020-12-31", 150)],
        "Assets": [fact(acc, None, "2020-12-31", 2000), fact(acc, None, "2019-12-31", 1800)],
        "StockholdersEquity": [fact(acc, None, "2020-12-31", 900), fact(acc, None, "2019-12-31", 850)],
    })
    from collections import defaultdict
    cnt = defaultdict(int)
    r = B.row(c, {"form": "10-K", "period": "20201231", "filed": "2021-02-20", "accn": acc}, cnt)
    d = dict(zip(B.FIELDS, r))
    assert (d["rev"], d["rev_py"], d["ni"], d["ni_py"]) == (1000, 800, 100, 90)
    assert (d["gp"], d["gp_py"]) == (400, 300) and cnt["gp_from_cost"] == 1
    assert (d["ocf"], d["ta"], d["ta_py"], d["eq"], d["eq_py"]) == (150, 2000, 1800, 900, 850)
    q = B.row(c, {"form": "10-Q", "period": "20201231", "filed": "2021-02-20", "accn": acc}, cnt)
    dq = dict(zip(B.FIELDS, q))
    assert dq["kind"] == "Q" and dq["rev"] is None and dq["ocf"] is None and dq["ta_py"] is None
    assert dq["ta"] == 2000                                               # instants do not depend on the form
