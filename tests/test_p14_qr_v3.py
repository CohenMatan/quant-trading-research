"""Data v3 in-host module qr_v3 (owner D229; research/phase14/data_v3/DATA_V3_spec.md): guard-v3 rule, the v3 view
(overlay never changes the v2.1 store), the six H029 signals against the frozen qr_h029a constructions, F7 with the
corruption bounds, equal-weight H029 score (>= 5 of 6), percentile helpers, and the packed tables."""
import math
import sys
from datetime import date, timedelta

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_h029a as Z  # noqa: E402
import qr_v3 as V  # noqa: E402
from qr_fundamentals import PITStore  # noqa: E402
from qr_sec_corrections import SECFiling  # noqa: E402
from qresearch import data_v3 as D3  # noqa: E402


# ----------------------------------------------------------------------------------------------- guard v3
def test_guard_rule_future_vs_known():
    pe = V.dn(date(2015, 3, 31))
    C = D3.columnar({"100": [(pe, 2, 400, D3.g4(110.0e6)), (pe, 2, 800, D3.g4(130.0e6))]})
    g = V.Guard3(C)
    assert g.n == 2 and g.rows("100", pe) is not None and g.rows("100", pe + 1) is None
    before = V.dd(pe + 400)              # restated value filed on pe+400 -> public pe+401
    # vendor value equals the first restated value on the filing day itself: not yet public -> blocked
    b, cats = g.check("100", pe, {"net_income_q": 110.0e6, "revenue_q": 5.0}, before)
    assert b and cats["net_income_q"] == "blocked_future" and cats["revenue_q"] == "no_restatement"
    # one day later it is public -> known
    b, cats = g.check("100", pe, {"net_income_q": 110.2e6}, before + timedelta(days=1))
    assert not b and cats["net_income_q"] == "restated_known"
    # the second restatement while only the first is public: future match, no known match -> blocked
    b, cats = g.check("100", pe, {"net_income_q": 130.0e6}, V.dd(pe + 500))
    assert b
    # the original value (never stored) is 'unmatched', never blocked
    b, cats = g.check("100", pe, {"net_income_q": 100.0e6}, V.dd(pe + 50))
    assert not b and cats["net_income_q"] == "unmatched"
    # no timeline for the registrant / period
    b, cats = g.check("999", pe, {"total_assets": 1.0}, V.dd(pe + 50))
    assert not b and cats == {"total_assets": "no_restatement"}


# ----------------------------------------------------------------------------------------------- overlay
def _feed(store, ov, sid, pe, fd, vals, today, blocked, retain=True):
    store.observe(sid, pe, fd, vals, None, today)
    rec = store.pending[sid][-1]
    ov.fed(sid, rec, retain, blocked)
    return rec


def test_overlay_replaces_blocked_version_and_never_changes_the_store():
    st, ov = PITStore(200), V.V3Overlay()
    pe = date(2015, 3, 31)
    r1 = _feed(st, ov, "A", pe, date(2015, 5, 1), {"revenue_q": 100.0}, date(2015, 5, 2), False)
    r2 = _feed(st, ov, "A", pe, date(2015, 6, 1), {"revenue_q": 120.0}, date(2015, 6, 2), True)
    today = date(2015, 7, 1)
    cur = st.record("A", today)
    hist = st.hist["A"]
    assert cur is r2 and hist[pe] is r2                       # the v2.1 store keeps the later version
    h3, c3 = ov.view(hist, cur, "A", today)
    assert h3[pe] is r1 and c3 is r1 and hist[pe] is r2       # v3 view: the earlier clean version
    assert ov.check["replaced"] == 1 and ov.check["newer_replacement"] == 0
    # only blocked version of a period -> the period is absent in v3
    pe2 = date(2015, 6, 30)
    _feed(st, ov, "A", pe2, date(2015, 8, 1), {"revenue_q": 130.0}, date(2015, 8, 2), True)
    t2 = date(2015, 9, 1)
    cur = st.record("A", t2)
    h3, c3 = ov.view(st.hist["A"], cur, "A", t2)
    assert pe2 not in h3 and c3 is r1
    # a security without any blocked version: the identical objects
    _feed(st, ov, "B", pe, date(2015, 5, 1), {"revenue_q": 1.0}, date(2015, 5, 2), False)
    cur = st.record("B", t2)
    h, c = ov.view(st.hist["B"], cur, "B", t2)
    assert h is st.hist["B"] and c is cur


def test_overlay_keeps_v21_record_when_it_is_clean():
    st, ov = PITStore(200), V.V3Overlay()
    pe = date(2015, 3, 31)
    _feed(st, ov, "A", pe, date(2015, 5, 1), {"revenue_q": 100.0}, date(2015, 5, 2), True)     # blocked original
    r2 = _feed(st, ov, "A", pe, date(2015, 6, 1), {"revenue_q": 101.0}, date(2015, 6, 2), False)
    today = date(2015, 7, 1)
    cur = st.record("A", today)
    h3, c3 = ov.view(st.hist["A"], cur, "A", today)
    assert h3 is st.hist["A"] and c3 is r2
    # before the clean revision is visible, the blocked original is removed
    t0 = date(2015, 5, 20)
    st2, ov2 = PITStore(200), V.V3Overlay()
    _feed(st2, ov2, "A", pe, date(2015, 5, 1), {"revenue_q": 100.0}, date(2015, 5, 2), True)
    cur = st2.record("A", t0)
    h3, c3 = ov2.view(st2.hist["A"], cur, "A", t0)
    assert pe not in h3 and c3 is None


# ----------------------------------------------------------------------------------------------- signals
def _store_with_quarters(n=9, rev0=100.0, step=10.0, neg_at=None):
    st = PITStore(200)
    pe = date(2013, 3, 31)
    ends = []
    for i in range(n):
        y, m = 2013 + (i * 3) // 12, (i * 3) % 12 + 3
        e = date(y, m, 31 if m in (3, 12) else 30)
        ends.append(e)
        r = rev0 + step * i
        if neg_at == i:
            r = -5.0
        vals = dict(revenue_q=r, gross_profit_q=0.4 * r, net_income_q=0.1 * r, operating_cash_flow_q=0.15 * r,
                    total_assets=1000.0 + 20 * i)
        if e.month == 12:                         # fiscal year end: FY totals for the reconciliation
            q = [rev0 + step * k for k in range(i - 3, i + 1)]
            if neg_at is not None and i - 3 <= neg_at <= i:
                q[neg_at - (i - 3)] = -5.0
            vals.update(revenue_ttm=sum(q), gross_profit_ttm=0.4 * sum(q), net_income_ttm=0.1 * sum(q),
                        operating_cash_flow_ttm=0.15 * sum(q))
        st.observe("A", e, e + timedelta(days=40), vals, None, e + timedelta(days=41))
        pe = e
    return st, ends


def test_signals_match_frozen_h029a_forms():
    st, ends = _store_with_quarters(9)
    today = ends[-1] + timedelta(days=60)
    cur = st.record("A", today)
    w = Z.Window(st.hist["A"], cur, today)
    s = V.signals(w)
    c = Z.candidates(w)
    assert s["F1"][0] == pytest.approx(c["F1Q"][0])
    for mine, frozen in (("F2", "F2"), ("F4", "F4B"), ("F5", "F5A"), ("F8", "F8")):
        assert s[mine][1] == c[frozen][1]
        if c[frozen][0] is None:
            assert s[mine][0] is None
        else:
            assert s[mine][0] == pytest.approx(c[frozen][0])
    assert set(s) == {"F1", "F2", "F4", "F5", "F8"}           # F3 / F6 are never computed


def test_f1_missing_when_any_revenue_nonpositive():
    st, ends = _store_with_quarters(9, neg_at=8)               # r0 <= 0
    today = ends[-1] + timedelta(days=60)
    cur = st.record("A", today)                                # promote before reading the history
    w = Z.Window(st.hist["A"], cur, today)
    assert V.signals(w)["F1"] == (None, "denominator")
    assert Z.candidates(w)["F1Q"][0] is not None               # the P14-CP1 form only checked r4, r5


def test_f7_equals_frozen_dilution_and_corruption_bounds():
    def fil(cover, filed, shares, accn):
        return SECFiling([accn, "10-Q", filed, cover, cover, shares, {}])
    fs = [fil("2014-03-31", "2014-05-01", 100.0, "a"), fil("2015-03-31", "2015-05-01", 110.0, "b")]
    today = date(2015, 6, 1)
    v = V.f7(fs, [], today)
    z = Z.dilution(fs, [], today)
    assert v[0] == pytest.approx(z[0]) and v[0] == pytest.approx(-0.1) and v[1] == "ok"
    assert v[2] == date(2014, 3, 31)
    # 2:1 split between the counts, ex-date before today: S1 restated -> no dilution
    sp = [(date(2014, 9, 1), 0.5)]
    fs2 = [fil("2014-03-31", "2014-05-01", 100.0, "a"), fil("2015-03-31", "2015-05-01", 200.0, "b")]
    assert V.f7(fs2, sp, today)[0] == pytest.approx(0.0)
    assert V.f7(fs2, sp, today)[0] == pytest.approx(Z.dilution(fs2, sp, today)[0])
    # the same split dated after today is not applied
    assert V.f7(fs2, [(date(2015, 7, 1), 0.5)], today)[0] == pytest.approx(-1.0)
    # a tenfold jump is corrupted
    fs3 = [fil("2014-03-31", "2014-05-01", 1.0, "a"), fil("2015-03-31", "2015-05-01", 20.0, "b")]
    assert V.f7(fs3, [], today)[:2] == (None, "corrupted")
    assert Z.dilution(fs3, [], today)[0] is not None


# ----------------------------------------------------------------------------------------------- score / helpers
def test_h029_score_equal_weights_and_minimum_count():
    rng = np.random.default_rng(1)
    M = rng.normal(size=(40, 6))
    M[0, :2] = np.nan                                   # 4 valid -> no score
    M[1, 0] = np.nan                                    # 5 valid -> mean of 5
    sc, cnt = V.h029_score(M)
    P = np.column_stack([V.centred(M[:, j]) for j in range(6)])
    assert math.isnan(sc[0]) and cnt[0] == 4
    assert sc[1] == pytest.approx(np.nanmean(P[1])) and cnt[1] == 5
    assert sc[2] == pytest.approx(P[2].mean())
    # equal weights: permuting the columns does not change the score
    sc2, _ = V.h029_score(M[:, ::-1])
    assert np.allclose(sc, sc2, equal_nan=True)
    assert np.nanmax(np.abs(P)) <= 1.0


def test_centred_equals_frozen_h026_percentile():
    import qr_h026 as H
    x = np.array([3.0, 1.0, np.nan, 2.0, 2.0, 5.0])
    assert np.allclose(V.centred(x), H.centred_percentile(x), equal_nan=True)


def test_cdf_mid_and_raw_class():
    o = np.array([1.0, 2.0, 2.0, 4.0])
    assert V.cdf_mid(o, 2.0) == pytest.approx((1 + 1.0) / 4)
    assert V.cdf_mid(o, 0.0) == 0.0 and V.cdf_mid(o, 9.0) == 1.0
    assert V.raw_class(100.0, 100.4) == "match" and V.raw_class(100.0, 101.5) == "minor"
    assert V.raw_class(100.0, 105.0) == "moderate" and V.raw_class(100.0, 150.0) == "major"
    assert V.raw_class(-1.0, 1.0) == "sign" and V.raw_class(None, 1.0) == "missing"


def test_packed_guard_table_decodes_to_the_builder_rows():
    files = {p.name: p.read_text() for p in (ROOT / "src/qresearch/lean").glob("qr_data_v3_*.py")}
    assert 1 <= len(files) <= D3.MAX_PARTS and all(len(t) <= 64_000 for t in files.values())
    C = D3.unpack_parts(files, "qr_data_v3")
    g = V.Guard3(C)
    back = D3.decolumnar(C)
    assert g.n == sum(len(r) for c in back.values() for r in c.values())
    k = sorted(back, key=int)[0]
    p = sorted(back[k])[0]
    assert [(fi, off) for fi, off, _v in g.rows(k, p)] == [(fi, off) for fi, off, _v in back[k][p]]
    vfiles = {p.name: p.read_text() for p in (ROOT / "src/qresearch/lean").glob("qr_v3val_*.py")}
    vt = D3.unpack_parts(vfiles, "qr_v3val")
    assert len(vt["days"]) == 131 and set(vt["ref"]) == set(vt["sector"])
