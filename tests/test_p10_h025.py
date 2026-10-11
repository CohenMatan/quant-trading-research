"""H025 in-host logic (src/qresearch/lean/qr_h025.py): identity, review choice, responses, statistic, matched null,
c_EVENT and gates. Synthetic inputs only."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "qresearch" / "lean"))
import qr_h025 as H  # noqa: E402
import qr_p7_pred as R  # noqa: E402
import qr_xs as X  # noqa: E402


def test_latest_review_strictly_before_trigger():
    rv = ["2011-01-31", "2011-02-28", "2011-03-31"]
    assert H.latest_review(rv, "2011-02-28") == "2011-01-31"      # same-day review is not yet available
    assert H.latest_review(rv, "2011-03-01") == "2011-02-28"
    assert H.latest_review(rv, "2011-01-31") is None
    assert H.latest_review(rv, "2017-12-01") == "2011-03-31"


def test_identity_mapping_rules():
    elig = {"A": "100", "B1": "200", "B2": "200", "C": None}
    adv = {"B1": 5e6, "B2": 9e6}
    assert H.map_issuer(100, elig, adv) == ("ELIGIBLE", "A")
    assert H.map_issuer(200, elig, adv) == ("ELIGIBLE_MULTICLASS", "B2")
    assert H.map_issuer(200, elig, {"B1": 9e6, "B2": 9e6}) == ("ELIGIBLE_MULTICLASS", "B1")
    assert H.map_issuer(300, elig, adv, {"XYZ"}, "XYZ") == ("IDENTITY_UNRESOLVED", None)
    assert H.map_issuer(300, elig, adv, {"XYZ"}, "QQQ") == ("NOT_ELIGIBLE", None)
    assert H.map_issuer(300, elig, adv) == ("NOT_ELIGIBLE", None)
    assert H.map_issuer(100, {"A": "0000000100"}, {}) == ("ELIGIBLE", "A")


def test_quintiles_convention_matches_frozen():
    rng = np.random.default_rng(1)
    x = rng.lognormal(22, 1, 503)
    np.testing.assert_array_equal(H.quintiles(x), R.quintile_labels(x))
    x[[3, 7]] = np.nan
    q = H.quintiles(x)
    assert q[3] == 0 and q[7] == 0 and set(np.unique(q[q > 0])) == {1, 2, 3, 4, 5}


def panel(n=80, seed=0):
    rng = np.random.default_rng(seed)
    c = 50 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    o = c * np.exp(rng.normal(0, 0.003, n))
    return o, c, np.ones(n)


def test_tsr_matches_frozen_response_convention():
    for seed in range(20):
        o, c, m = panel(seed=seed)
        m = np.cumprod(np.r_[np.ones(40), np.full(40, 1.0)])[::-1].copy()
        m[:30] *= 1.01                                          # a dividend factor before row 30
        if seed % 3 == 0:
            o[22:25] = np.nan                                   # missing bars at entry
        if seed % 4 == 0:
            c[35:] = np.nan                                     # delisting inside the window
        v, st, e, x = H.tsr(o, c, m, 20, 39)
        rv, rst = R.response(o, c, m, 19, 39)
        assert v == pytest.approx(rv, abs=1e-15)
        assert {"ok": "ok", "truncated": "truncated"}[st] == rst


def test_excess_uses_stock_entry_row_and_planned_exit_for_spy():
    o, c, m = panel(seed=3)
    so, sc, sm = panel(seed=4)
    o[20] = np.nan                                              # entry shifts to row 21
    c[30:] = np.nan
    o[30:] = np.nan                                             # delisted after row 29
    ex, v, s, st = H.excess((o, c, m), so, sc, sm, 20, 39)
    assert st == "truncated"
    assert v == pytest.approx(c[29] / o[21] - 1)
    assert s == pytest.approx(sc[39] / so[21] - 1)
    assert ex == pytest.approx(v - s)
    nb = np.full(80, np.nan)
    assert math.isnan(H.excess((nb, nb, m), so, sc, sm, 20, 39)[0])
    assert math.isnan(H.excess((o, c, m), so, sc, sm, 20, 39, unverified_rows=(25,))[0])


def test_response_window_invariance():
    """Prices before the entry row and after the exit row never change the response; a split handled through the
    multiplier leaves the TSR unchanged."""
    o, c, m = panel(seed=5)
    so, sc, sm = panel(seed=6)
    base = H.excess((o, c, m), so, sc, sm, 20, 39)
    o2, c2 = o.copy(), c.copy()
    o2[:20] *= 3
    c2[:20] *= 0.2
    o2[40:] *= 9
    c2[40:] *= 9
    assert H.excess((o2, c2, m), so, sc, sm, 20, 39) == base
    o3, c3, m3 = o.copy(), c.copy(), m.copy()
    o3[30:] /= 2
    c3[30:] /= 2
    m3[:30] /= 2                                                # 2-for-1 split effective row 30
    assert H.excess((o3, c3, m3), so, sc, sm, 20, 39)[0] == pytest.approx(base[0], abs=1e-12)
    for h in (5, 10):                                           # diagnostic horizon timing
        assert H.excess((o, c, m), so, sc, sm, 20, 20 + h - 1)[1] == pytest.approx(c[19 + h] / o[20] - 1)


def test_nw_t_equals_frozen_convention():
    rng = np.random.default_rng(2)
    for _ in range(10):
        x = rng.normal(0.01, 0.05, rng.integers(20, 90))
        assert H.nw_t(x, 2) == pytest.approx(X.nw_tstat(x, 2))


def test_monthly_series_and_summary():
    y = np.array([0.1, -0.1, 0.05, 0.02, 0.03])
    months = ["2011-03", "2011-03", "2011-05", "2015-01", "2015-01"]
    years = [2011, 2011, 2011, 2015, 2015]
    s = H.summary(y, months, years)
    assert s["months"] == 3 and s["n"] == 5
    ser = np.array([0.0, 0.05, 0.025])
    assert s["monthly_mean"] == pytest.approx(ser.mean())
    assert s["t"] == pytest.approx(X.nw_tstat(ser, 2)[2])
    assert s["median"] == pytest.approx(0.03) and s["win_rate"] == pytest.approx(0.8)
    assert s["first_half"] == pytest.approx(np.mean([0.1, -0.1, 0.05]))
    assert s["by_year"]["2015"] == dict(n=2, mean=pytest.approx(0.025))
    assert s["positive_years"] == 2


def synthetic(effect, seed, n_years=7, per_year=40):
    rng = np.random.default_rng(seed)
    months, years, y = [], [], []
    for yr in range(2011, 2011 + n_years):
        for _ in range(per_year):
            mo = int(rng.integers(1, 13))
            months.append(f"{yr}-{mo:02d}")
            years.append(yr)
            y.append(effect + rng.normal(0, 0.08))
    return np.array(y), months, years


def test_gates_detect_planted_effect_and_reject_none():
    y, mo, yr = synthetic(0.04, 1)
    s = H.summary(y, mo, yr)
    g = H.gates(s, 2.5)
    assert g["all"] and all(g[k] for k in ("G1", "G2", "G3", "G4", "G5"))
    y0, mo0, yr0 = synthetic(0.0, 2)
    assert not H.gates(H.summary(y0, mo0, yr0), 2.5)["all"]
    small = H.summary(y[:60], mo[:60], yr[:60])
    assert not H.gates(small, 2.5)["G5"]
    assert H.sample_ok({"2011": 10, "2012": 10, "2013": 10, "2014": 10, "2015": 60}, 100)
    assert not H.sample_ok({"2011": 10, "2012": 10, "2013": 10, "2014": 9, "2015": 61}, 100)
    assert not H.sample_ok({str(y): 14 for y in range(2011, 2018)}, 98)


def test_critical_value_convention():
    t = np.arange(5000, dtype=float) / 1000.0
    c, raw = H.critical_value(t)
    assert raw == pytest.approx(X.critical_value(t, 0.01)) and raw == pytest.approx(4.95)
    assert c == raw
    assert H.critical_value(np.zeros(5000)) == (2.326, 0.0)


def test_match_pool_hierarchy():
    # (sid, cik, sector, quintile, blocked)
    cand = [("S0", "1", "Tech", 3, False), ("A", "2", "Tech", 3, False), ("B", "3", "Tech", 2, False),
            ("C", "4", "Tech", 4, False), ("D", "5", "Hlth", 3, False), ("E", "6", "Tech", 3, True),
            ("F", "1", "Tech", 3, False), ("G", None, "Tech", 3, False)]
    assert H.match_pool("S0", 1, "Tech", 3, cand) == ("L1", ["A"])                 # not self, not same CIK, not blocked
    no_l1 = [c for c in cand if c[0] != "A"]
    assert H.match_pool("S0", 1, "Tech", 3, no_l1) == ("L2", ["B"])                # lower quintile first
    assert H.match_pool("S0", 1, "Tech", 3, [c for c in no_l1 if c[0] != "B"]) == ("L2", ["C"])
    assert H.match_pool("S0", 1, "Util", 3, cand) == ("L3", ["A", "D"])
    assert H.match_pool("S0", 1, "Util", 5, cand) == ("L4", ["A", "B", "C", "D"])


def test_null_draw_deterministic_and_uniform():
    sizes = [1, 2, 7, 50] * 50
    a, b = H.null_draw(sizes, 17), H.null_draw(sizes, 17)
    np.testing.assert_array_equal(a, b)
    assert not np.array_equal(a, H.null_draw(sizes, 18))
    assert all(0 <= k < n for k, n in zip(a, sizes))
    big = H.null_draw([4] * 40000, 3)
    assert np.bincount(big, minlength=4).min() > 9500


def test_null_world_statistic_and_false_positive_rate():
    """Null worlds built from pools with NO event effect: c_EVENT keeps the false-pass rate near 1%."""
    rng = np.random.default_rng(9)
    y, months, years = synthetic(0.0, 3)
    u, idx = H.month_index(months)
    pools = [rng.normal(0.003, 0.08, int(rng.integers(3, 40))) for _ in y]
    worlds = [H.null_world(pools, idx, len(u), s) for s in range(1, 1001)]
    w = H.null_world(pools, idx, len(u), 5)
    assert w == worlds[4]
    c, _ = H.critical_value([x["t"] for x in worlds])
    fresh = [H.primary(np.array([p[rng.integers(p.size)] for p in pools]), idx, len(u)) for _ in range(1000)]
    rate = np.mean(np.array(fresh) > c)
    assert rate < 0.03


def test_read_ledger_types():
    text = ("event_id,kind,issuer_cik,symbol_as_filed,trigger_et,trigger_date,entry_session,exit_session,"
            "window_status,n_insiders,cluster_value,ceo_cfo,director_only,n_qualifying_filings,median_delay_days,"
            "near_cluster\nC1,cluster,0000100,XYZ,2011-03-10 17:00:00,2011-03-10,2011-03-11,2011-04-07,in_window,"
            "2,120000.00,1,0,2,2.5,0\n")
    r = H.read_ledger(text)[0]
    assert r["issuer_cik"] == "100" and r["cluster_value"] == 120000.0 and r["median_delay_days"] == 2.5
