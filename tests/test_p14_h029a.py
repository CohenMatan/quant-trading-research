"""P14 H029-A (owner D227): the Business Improvement data-feasibility audit module qr_h029a. Synthetic data only:
TTM windows equal the frozen PITStore rules, constructions match hand calculations, nothing dated after the
selection day can enter (truncation / look-ahead), F7 restates SEC cover counts with past splits only, and the
aggregation counts, correlations and run lengths are exact. No return or price series exists in this module."""
import math
import sys
from datetime import date, timedelta

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
import qr_fundamentals as F  # noqa: E402
import qr_h029a as Z  # noqa: E402
from qr_sec_corrections import SECFiling  # noqa: E402

D0 = date(2009, 3, 31)


def qend(i):
    """Quarter ends 2009-03-31, 2009-06-30, ... (consecutive, 90-92 day gaps)."""
    y, q = 2009 + (i // 4), i % 4
    return date(y, 3 * (q + 1), (31, 30, 30, 31)[q])


def _vals(i, rev=100.0, gp=40.0, oi=20.0, ni=10.0, ocf=15.0, ta=1000.0, eq=500.0, debt=200.0, g=0.02):
    f = (1 + g) ** i
    q = dict(revenue_q=rev * f, gross_profit_q=gp * f * (1 + 0.001 * i), operating_income_q=oi * f,
             net_income_q=ni * f, operating_cash_flow_q=ocf * f, total_assets=ta * (1 + 0.01 * i),
             stockholders_equity=eq, total_debt=debt * (1 - 0.01 * i))
    return q


def build(n, fy_q=3, **kw):
    """A store fed with n consecutive quarters; quarter index i with (i % 4) == fy_q is the fiscal-year end, whose
    record carries the fiscal-year totals (sum of its four quarters) in '<base>_ttm'; interim records carry the latest
    completed fiscal year (vendor convention D111)."""
    st = F.PITStore()
    vals = [_vals(i, **kw) for i in range(n)]
    fy = {}
    for i in range(n):
        v = dict(vals[i])
        if i % 4 == fy_q and i >= 3:
            for b in Z.BASES:
                fy[b] = sum(vals[k][b + "_q"] for k in range(i - 3, i + 1))
        for b in Z.BASES:
            if b in fy:
                v[b + "_ttm"] = fy[b]
        pe = qend(i)
        st.observe("A", pe, pe + timedelta(days=40), v, None, pe + timedelta(days=41))
    return st, vals


def win(st, today, key="A"):
    cur = st.record(key, today)                 # promotes visible reports first (host order)
    return Z.Window(st.hist.get(key, {}), cur, today)


def at(n):
    return qend(n - 1) + timedelta(days=60)


def test_ttm_at_equals_frozen_store_rule():
    for n in (3, 4, 5, 8, 12):
        st, _ = build(n)
        today = at(n)
        ref = st.ttm_detail("A", "revenue", today)       # promotes as a side effect
        recs = Z.base_recs(st.hist["A"], "revenue", today)
        got = Z.ttm_at(recs, len(recs) - 1, "revenue")
        assert (got[0] is None) == (ref[0] is None)
        if ref[0] is not None:
            assert got[0] == pytest.approx(ref[0], rel=1e-15)


def test_constructions_match_hand_calculation():
    st, v = build(16)
    today = at(16)
    w = win(st, today)
    c = Z.candidates(w)
    i0 = 15
    T = lambda b, k: sum(v[i0 - k - j][b + "_q"] for j in range(4))  # noqa: E731
    R = lambda k: T("revenue", k)  # noqa: E731
    assert c["F1"][0] == pytest.approx((R(0) / R(4) - 1) - (R(1) / R(5) - 1))
    r = lambda k: v[i0 - k]["revenue_q"]  # noqa: E731
    assert c["F1Q"][0] == pytest.approx((r(0) / r(4) - 1) - (r(1) / r(5) - 1))
    assert c["F2"][0] == pytest.approx(T("gross_profit", 0) / R(0) - T("gross_profit", 4) / R(4))
    assert c["F3"][0] == pytest.approx(T("operating_income", 0) / R(0) - T("operating_income", 4) / R(4))
    ta = lambda k: v[i0 - k]["total_assets"]  # noqa: E731
    assert c["F4B"][0] == pytest.approx(T("operating_cash_flow", 0) / ta(0) - T("operating_cash_flow", 4) / ta(4))
    assert c["F5A"][0] == pytest.approx(T("net_income", 0) / ta(0) - T("net_income", 4) / ta(4))
    d = lambda k: v[i0 - k]["total_debt"]  # noqa: E731
    assert c["F6"][0] == pytest.approx(-(d(0) / ta(0) - d(4) / ta(4)))
    assert c["F6"][0] > 0                       # debt falls, assets grow: deleveraging is an improvement (+)
    assert c["F8"][0] == pytest.approx(R(0) / ta(0) - R(4) / ta(4))
    assert all(c[f][1] == "ok" for f in c)


def test_history_requirements():
    for n, ok8, ok9 in ((7, False, False), (8, True, False), (9, True, True)):
        st, _ = build(n)
        today = at(n)
        c = Z.candidates(win(st, today))
        assert (c["F2"][1] == "ok") == ok8, n           # exactly 8 consecutive quarters (q0..q7)
        assert (c["F1"][1] == "ok") == ok9, n
    st, _ = build(16)
    stale = at(16) + timedelta(days=200)
    c = Z.candidates(win(st, stale))
    assert all(x == (None, "no_fresh_report") for x in c.values())


def test_no_look_ahead_truncation():
    """Values at T from a store that has ALSO seen later reports (not yet available) equal those from a store fed only
    with reports available on or before T."""
    full, _ = build(20)
    T = at(14)
    full.record("A", at(20))
    part = F.PITStore()
    for i in range(14):
        pe = qend(i)
        rec = full.hist["A"][pe]
        part.observe("A", pe, rec.file_date, rec.values, None, pe + timedelta(days=41))
    # a fresh store that sees every report on its first day but is queried at T
    late = F.PITStore()
    for i in range(20):
        pe = qend(i)
        rec = full.hist["A"][pe]
        late.observe("A", pe, rec.file_date, rec.values, None, T)
    a = Z.candidates(win(part, T))
    b = Z.candidates(win(late, T))
    assert a == b
    w = win(late, T)
    assert w.viol == 0 and all(r.available <= T for r in w.grid)


def test_denominators_and_missing_fields():
    st, v = build(16, debt=0.0)                 # vendor 0 debt is read as missing (frozen clean rule)
    today = at(16)
    st.record("A", today)
    st2 = F.PITStore()
    for pe, r in st.hist["A"].items():
        vv = {k: F.clean(x) for k, x in r.values.items()}
        st2.observe("A", pe, r.file_date, vv, None, pe + timedelta(days=41))
    c = Z.candidates(win(st2, today))
    assert c["F6"] == (None, "field_missing")
    st3, _ = build(16, ta=-5.0)
    c = Z.candidates(win(st3, today))
    assert c["F8"] == (None, "denominator") and c["F2"][1] == "ok"
    assert Z.pathology(win(st3, today)) & Z.PB["ta_nonpos"]


def test_nonconsecutive_quarters_never_interpolated():
    full, _ = build(16)
    today = at(16)
    full.record("A", today)
    st = F.PITStore()
    for pe, r in sorted(full.hist["A"].items()):
        if pe != qend(12):                                   # one quarter missing inside the span
            st.observe("A", pe, r.file_date, r.values, None, pe + timedelta(days=41))
    c = Z.candidates(win(st, today))
    assert c["F2"] == (None, "not_consecutive") and c["F1"] == (None, "not_consecutive")
    assert c["F1Q"] == (None, "not_consecutive")


def _filing(i, filed, cover, shares):
    return SECFiling([f"acc-{i}", "10-Q", str(filed), str(cover), str(cover), shares, {}])


def test_f7_cover_counts_and_splits():
    fs = [_filing(0, date(2014, 2, 20), date(2014, 2, 10), 1000.0),
          _filing(1, date(2015, 2, 20), date(2015, 2, 10), 525.0)]      # after a 1:2 reverse? no: 2:1 split below
    splits = [(date(2014, 8, 1), 2.0)]           # QuantConnect factor 2.0 = 1-for-2 reverse split (shares halve)
    today = date(2015, 3, 31)
    v, why, fd = Z.dilution(fs, splits, today)
    # S1 = 1000 restated with the split after its cover date (x 1/2) = 500; S0 = 525 (cover after the split)
    assert why == "ok" and fd == date(2015, 2, 20) and v == pytest.approx(-(525.0 / 500.0 - 1.0))
    # a split dated after today never enters; a filing not yet public never enters
    v2, _, _ = Z.dilution(fs, splits + [(date(2015, 6, 1), 0.5)], today)
    assert v2 == pytest.approx(v)
    v3, why3, _ = Z.dilution(fs, splits, date(2015, 2, 20))   # filed 2015-02-20 -> usable from 2015-02-21
    assert why3 == "no_cover_count" or v3 != pytest.approx(v)
    v4, why4, _ = Z.dilution(fs[1:], splits, today)
    assert v4 is None and why4 == "no_prior_count"
    v5, why5, _ = Z.dilution(fs, splits, date(2015, 8, 1))    # cover 172 days old > 135
    assert v5 is None and why5 == "no_cover_count"


def test_runs_and_spearman():
    assert Z.runs([1, 1, 2, 2, 2, 3, 3]) == [3]
    assert Z.runs([1, 1, 1]) == []
    assert Z.runs([1, 2, 3, 3, 4]) == [1, 2]
    a = np.arange(40.0)
    assert Z.spearman(a, a) == pytest.approx(1.0) and Z.spearman(a, -a) == pytest.approx(-1.0)
    assert math.isnan(Z.spearman(a[:10], a[:10]))


def _month(day, V, nf=None, ff=None, path=None):
    n = V.shape[0]
    return dict(day=day, sid=[f"s{i}" for i in range(n)], nf=np.ones(n, bool) if nf is None else nf,
                ff=np.zeros(n, np.int64) if ff is None else ff, lmc=np.log(np.arange(1, n + 1) * 1e9),
                lpx=np.zeros(n), ladv=np.zeros(n), V=V, why=np.zeros(V.shape, np.int64), dstale=np.full(n, 30.0),
                age=np.full(n, 70.0), d7=np.full(n, 20.0), revised=np.zeros(n, bool),
                path=np.zeros(n, np.int64) if path is None else path, seas=np.full((n, 6), np.nan),
                ttmw=np.zeros((n, 5), np.int64), ttm4=np.ones((n, 5), bool), viol=0)


def test_aggregate_counts_patterns_and_updates():
    F_ = len(Z.FORMS)
    rng = np.random.default_rng(1)
    base = rng.normal(size=(50, F_))
    V1 = base.copy()
    V1[:10, 0] = np.nan
    V2 = base.copy()
    V2[:5, 1] += 1.0                               # five stocks change form F1Q between the two reviews
    nf = np.ones(50, bool)
    nf[-4:] = False
    out = Z.aggregate([_month("2015-01-30", V1, nf=nf), _month("2015-02-27", V2, nf=nf)])
    assert out["monthly"]["nf_eligible"] == [46, 46] and out["monthly"]["all_eligible"] == [50, 50]
    assert out["monthly"]["F1"]["nf_valid"] == [36, 46] and out["monthly"]["F1"]["all_valid"] == [40, 50]
    u = out["update"]["F1Q"]
    assert u["pairs"] == 46 and u["changed_pairs"] == 5
    assert out["update"]["F1"]["pairs"] == 36
    pats = out["patterns"]["2015-01-30"]
    full = (1 << F_) - 1
    assert pats[str(full)] == 36 and pats[str(full - 1)] == 10
    pp = out["pattern_periods"]["2015-2017"]
    assert pp[str(full)][0] == 36 + 46
    assert out["corr"]["F1|F1Q"]["months"] == 2


def test_avg_rank_matches_reference():
    from scipy.stats import rankdata
    rng = np.random.default_rng(5)
    for _ in range(20):
        x = rng.integers(0, 15, 120).astype(float)
        assert np.allclose(Z.avg_rank(x), rankdata(x))


AUDIT = ROOT / "research/phase14/cp1/P14_CP1_audit.json"


@pytest.mark.skipif(not AUDIT.exists(), reason="audit not yet computed")
def test_committed_audit_reproducible_and_rule_consistent(tmp_path, monkeypatch):
    import json
    sys.path.insert(0, str(ROOT / "research/phase14/cp1"))
    import P14_CP1_analysis as A
    monkeypatch.setattr(A, "HERE", tmp_path)
    A.main()
    got = json.loads((tmp_path / "P14_CP1_audit.json").read_text())
    ref = json.loads(AUDIT.read_text())
    assert got == ref
    g = ref["gate"]
    ab = [k for k, v in ref["classification"].items() if v["cls"] in ("A", "B")]
    assert g["families"] == ab and g["condition_1"] == (len(ab) >= 5)
    assert g["condition_2"] == (max(r["median"] for r in g["combined_rules"].values()) >= 0.70)
    assert g["result"].endswith("PASS") == (g["condition_1"] and g["condition_2"])
    assert ref["pit"] == dict(record_after_today=0, universe_rows_without_live_values=0)
    assert ref["run"]["f7"]["filing_after_today"] == 0
    assert all(v == 0 for v in ref["run"]["pit_audit"].values())
