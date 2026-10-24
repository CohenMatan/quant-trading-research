"""OD-1 outcome-discovery study (owner D308): pure module qr_od1 on synthetic data only (no market data)."""
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "qresearch" / "lean"))
import qr_od1 as O  # noqa: E402


def series(n=O.L, g=0.001, seed=0, vol=0.0):
    rng = np.random.default_rng(seed)
    return 100 * np.exp(np.cumsum(np.full(n, g) + rng.normal(0, vol, n)))


def test_tech_features_basic_values():
    c = series(g=0.001)[None, :]
    v = np.full_like(c, 1e7)
    s = series(g=0.0005)
    f = O.tech_features(c, v, s)
    assert abs(f["MOM12_1"][0] - (np.exp(0.001 * 231) - 1)) < 1e-9
    assert abs(f["HI52"][0] - 1.0) < 1e-12 and f["MAXDD252"][0] == 0.0
    assert f["UPDAYS"][0] == 1.0 and f["MONTHSUP"][0] == 12 and f["BIGUP"][0] == 0
    assert f["TRENDAGE"][0] == 200 and abs(f["BETA"][0]) < 1e3
    assert f["BREAKOUT"][0] == 0.0          # new high but no volume surge


def test_tech_features_missing_window_and_breakout():
    c = series(seed=1, vol=0.01)[None, :].repeat(2, axis=0)
    c[1, 10:60] = np.nan                     # 50 of 253 missing -> long-window features missing
    v = np.full_like(c, 1e7)
    v[0, -5:] = 3e7
    c[0, -3:] = c[0].max() * 1.05            # new high on volume
    f = O.tech_features(c, v, series())
    assert np.isnan(f["MOM12_1"][1]) and np.isfinite(f["REV1M"][1])
    assert f["BREAKOUT"][0] == 1.0


def test_features_ignore_future_by_construction():
    """The function only receives the window ending at the review: appending future sessions is impossible, and
    changing any earlier-than-window value does not matter either."""
    c = series(seed=2, vol=0.02, n=400)
    v = np.full(400, 1e7)
    s = series(n=400)
    a = O.tech_features(c[None, -O.L:], v[None, -O.L:], s[-O.L:])
    c2 = c.copy()
    c2[:100] *= 3
    b = O.tech_features(c2[None, -O.L:], v[None, -O.L:], s[-O.L:])
    assert all((np.isnan(a[k]) & np.isnan(b[k])) | (a[k] == b[k]) for k in O.TECH)


def fund_doc():
    rows = [
        ["2010-02-20", "K", "2009-12-31", 100, 90, 10, 8, 40, 36, 15, 200, 180, 100, 95],
        ["2010-05-05", "Q", "2010-03-31", 30, 25, 3, 2, 12, 10, None, 210, None, 102, None],
        ["2010-08-05", "Q", "2010-06-30", 32, 26, 3, 3, 13, 10, None, 215, None, 104, None],
        ["2010-11-05", "Q", "2010-09-30", 33, 30, 4, 3, 13, 12, None, 220, None, 106, None],
        ["2011-02-20", "K", "2010-12-31", 125, 100, 13, 10, 50, 40, 18, 230, 200, 110, 100],
        ["2009-12-01", "Q", "2009-09-30", 1, 1, 1, 1, 1, 1, None, 1, None, 1, None],   # filed before 2010: dropped
    ]
    return {"r": {"1": rows}}


def test_fund_features_pit_and_values():
    F = O.Fund(fund_doc(), ["1"])
    assert len(F.rows[0]) == 5                                          # the 2009 filing is discarded
    t = date(2011, 2, 20).toordinal()                                   # the 10-K filed ON t is not yet usable
    f = F.features(0, t, cap=1000.0)
    assert abs(f["REVYOY"] - (33 / 30 - 1)) < 1e-12                     # latest = 2010-11-05 10-Q
    assert abs(f["REVACCEL"] - ((33 / 30 - 1) - (32 / 26 - 1))) < 1e-12
    assert abs(f["ROA"] - 10 / 200) < 1e-12 and abs(f["AG"] - (200 / 180 - 1)) < 1e-12
    assert f["REVCONS"] == 4.0 and f["NICONS"] == 3.0
    g = F.features(0, t + 1, cap=1000.0)
    assert abs(g["REVYOY"] - 0.25) < 1e-12 and abs(g["DROA"] - (13 / 230 - 10 / 200)) < 1e-12
    assert abs(g["EY"] - 13 / 1000) < 1e-12 and abs(g["BM"] - 0.11) < 1e-12
    late = F.features(0, date(2012, 12, 1).toordinal(), cap=1000.0)  # stale filings -> missing
    assert late["REVYOY"] is None and late["ROA"] is None


def panel(seed=0, R=400, K=60, signal=0.0):
    rng = np.random.default_rng(seed)
    T = [date(2011, 1, 31).toordinal() + 30 * j for j in range(K)]
    years = [date.fromordinal(t).year for t in T]
    feat = rng.normal(size=(R, K))
    rets = rng.normal(0.008, 0.08, size=(R, K)) + signal * np.roll(feat, 1, axis=1)
    rets[:, 0] = 0
    MP = (100 * np.exp(np.cumsum(rets, axis=1))).astype(np.float32)
    last_day = np.full(R, T[-1] + 1)
    last_px = MP[:, -1].astype(float)
    MP[:5, 30:] = np.nan                                                # five securities leave at review 30
    last_day[:5] = T[29] + 3
    last_px[:5] = MP[:5, 29] * 0.5
    ks, rs = [], []
    for k in range(K):
        for r in range(R):
            if np.isfinite(MP[r, k]):
                ks.append(k)
                rs.append(r)
    ks, rs = np.array(ks), np.array(rs)
    X = np.full((ks.size, len(O.FEATURES)), np.nan)
    for j in range(len(O.FEATURES)):
        X[:, j] = rng.normal(size=ks.size)
    X[:, O.FEATURES.index("MOM3")] = feat[rs, ks]
    X[:, O.FEATURES.index("BREAKOUT")] = rng.integers(0, 2, ks.size)
    X[:, O.FEATURES.index("BASE")] = rng.integers(0, 2, ks.size)
    for c in O.INTEGER:
        X[:, O.FEATURES.index(c)] = rng.integers(0, 5, ks.size)
    X[:, O.FEATURES.index("BETA")] = 1.0
    spy = np.exp(np.cumsum(np.r_[0, rng.normal(0.007, 0.03, K - 1)]))
    return dict(T=T, years=years, spy=spy, MP=MP, last_day=last_day, last_px=last_px, k=ks, r=rs, firm=rs, X=X,
                sec=rs % 11, fin=(rs % 13) == 0, cap=np.full(ks.size, 5e9), K1712=35, K1801=36)


def test_labels_delisting_and_horizon():
    P = panel()
    LB = O.build_labels(P, 12)
    j = np.where((P["r"] == 0) & (P["k"] == 25))[0][0]
    assert LB["valid"][j] and LB["left"][j]                             # left at review 30 < 25 + 12
    exp = P["last_px"][0] / P["MP"][0, 25] - 1
    assert abs(LB["tr"][j] - exp) < 1e-5
    assert not LB["valid"][P["k"] > len(P["T"]) - 13].any()             # no label beyond the last review
    PM = O.period_masks(P, LB)
    assert (LB["kk"][PM["DISC"]] <= 35).all() and (P["k"][PM["STRESS"]] >= 36).all()


def test_summarize_detects_planted_signal_and_serializes():
    P = panel(signal=0.03)
    out = O.summarize(P)
    names = [(a, b) for a, b, _ in out]
    assert ("feature", "MOM3") in names and ("grid", "D1") in names
    ser = dict(((a, b), c) for a, b, c in out)[("series", "MOM3")]
    t, n = ser[3]["nw"]["ic"]
    assert t is not None and t > 3                                       # planted: next-month return ~ feature
    null = dict(((a, b), c) for a, b, c in out)[("series", "VOL63")]
    tn, _ = null[3]["nw"]["ic"]
    assert tn is None or abs(tn) < 4
    text = json.dumps(out)
    assert "NaN" not in text and "Infinity" not in text


def test_bounds_requires_ordered_reviews():
    try:
        O.bounds(np.array([0, 1, 0]))
    except ValueError:
        return
    raise AssertionError("expected ValueError")
