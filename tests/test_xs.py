"""Phase 4 cross-sectional signal-validation plumbing (qr_xs, P4-CP3 draft) on synthetic inputs only: signal formulas,
look-ahead truncation, ranks and buckets, Spearman / partial correlations, Newey-West, the promotion rule and the
identity-tethered within-date permutation. No market data is used."""
import math

import numpy as np
import pytest
from scipy import stats as sps

from conftest import ROOT, load_module

X = load_module(ROOT / "src/qresearch/lean/qr_xs.py", "qr_xs_t")


def test_mom_12_1_and_missing():
    m = X.mom_12_1([110.0, np.nan, 50.0], [100.0, 10.0, 0.0])
    assert m[0] == pytest.approx(0.10)
    assert np.isnan(m[1]) and np.isnan(m[2])


def test_nud_counts_zero_days_in_denominator_only():
    r = np.r_[np.full(120, 0.01), np.full(60, -0.01), np.zeros(40)]
    assert X.nud(r) == pytest.approx((120 - 60) / 220)
    assert np.isnan(X.nud(r[:150]))                      # fewer than 200 valid returns
    r2 = np.r_[r, np.full(30, np.nan)]
    assert X.nud(r2) == pytest.approx((120 - 60) / 220)  # missing returns ignored


def test_nud_distinguishes_smooth_from_jumpy_paths_with_equal_total_return():
    smooth = np.full(230, math.exp(math.log(1.3) / 230) - 1)            # +30% in many small steps
    jumpy = np.full(230, -0.0005)
    jumpy[[10, 50]] = (1.3 / 0.9995 ** 228) ** 0.5 - 1                    # same +30% from two jumps
    assert np.prod(1 + smooth) == pytest.approx(np.prod(1 + jumpy))
    assert X.nud(smooth) > X.nud(jumpy)


def test_trend_score_formula_and_history_requirement():
    c = np.linspace(50, 100, 260)
    exp = np.mean([math.log(c[-1] / c[-L:].mean()) for L in (50, 100, 200)])
    assert X.trend_score(c) == pytest.approx(exp)
    assert np.isnan(X.trend_score(c[-199:]))
    assert X.trend_score(c) > 0 > X.trend_score(c[::-1])


def test_signals_use_no_data_after_the_decision_close():
    """Truncation test: appending future bars cannot change a signal computed on the history up to the decision."""
    rng = np.random.default_rng(1)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 400)))
    d = 300
    t_now = X.trend_score(c[:d + 1])
    assert X.trend_score(np.r_[c[:d + 1]]) == t_now
    for k in (d + 2, 350, 400):                                          # later data exists but is not passed
        assert X.trend_score(c[:d + 1]) == t_now
        assert X.trend_score(c[:k]) != t_now


def test_avg_rank_and_spearman_match_scipy():
    rng = np.random.default_rng(2)
    x = rng.integers(0, 20, 300).astype(float)
    y = x + rng.normal(0, 5, 300)
    assert np.allclose(X.avg_rank(x), sps.rankdata(x))
    assert X.spearman(x, y) == pytest.approx(sps.spearmanr(x, y)[0])


def test_buckets_equal_counts_and_order():
    rng = np.random.default_rng(3)
    s = rng.normal(size=1003)
    b = X.buckets(s, 10)
    cnt = np.bincount(b, minlength=10)
    assert cnt.max() - cnt.min() <= 1
    assert s[b == 9].min() >= s[b == 8].max()


def test_smooth_score_is_sequential_sort():
    rng = np.random.default_rng(4)
    mom, nd = rng.normal(size=500), rng.normal(size=500)
    sc = X.smooth_momentum_score(mom, nd)
    q = X.buckets(mom, 5)
    for b in range(4):                                                   # every stock in a higher MOM quintile ranks above
        assert sc[q == b].max() < sc[q == b + 1].min()
    ix = np.flatnonzero(q == 4)                                          # within a quintile: ordered by NUD
    assert X.spearman(sc[ix], nd[ix]) == pytest.approx(1.0)


def test_partial_corr_matches_regression_residuals():
    rng = np.random.default_rng(5)
    m = rng.normal(size=2000)
    x = 0.7 * m + rng.normal(size=2000)
    y = 0.5 * m + 0.2 * x + rng.normal(size=2000)
    rx = x - np.polyval(np.polyfit(m, x, 1), m)
    ry = y - np.polyval(np.polyfit(m, y, 1), m)
    exp = np.corrcoef(rx, ry)[0, 1]
    got = X.partial_corr(np.corrcoef(y, x)[0, 1], np.corrcoef(y, m)[0, 1], np.corrcoef(x, m)[0, 1])
    assert got == pytest.approx(exp, abs=1e-12)


def test_incremental_statistic_detects_only_information_beyond_momentum():
    rng = np.random.default_rng(6)
    n = 3000
    mom = rng.normal(size=n)
    comp_redundant = mom + 0.3 * rng.normal(size=n)                     # carries only momentum's information
    comp_new = rng.normal(size=n)
    y0 = 0.3 * mom + rng.normal(size=n)
    inc_red, _ = X.within_quintile_partial_ic(comp_redundant, mom, y0)
    assert abs(inc_red) < 0.06
    y1 = y0 + 0.3 * comp_new
    inc_new, per = X.within_quintile_partial_ic(comp_new, mom, y1)
    assert inc_new > 0.15 and all(p > 0 for p in per)


def test_newey_west_lag0_is_iid_and_lag_inflates_for_overlap():
    rng = np.random.default_rng(7)
    e = rng.normal(size=5000)
    m, se, t = X.nw_tstat(e, lag=0)
    assert se == pytest.approx(e.std() / math.sqrt(e.size), rel=1e-9)
    ov = np.convolve(rng.normal(size=5002), np.ones(3), "valid")        # 3-period overlapping sums
    se0 = X.nw_tstat(ov, 0)[1]
    se6 = X.nw_tstat(ov, 6)[1]
    assert se6 / se0 == pytest.approx(math.sqrt(3), rel=0.15)


def test_date_stats_and_summary_on_a_planted_signal():
    rng = np.random.default_rng(8)
    series, years = [], []
    for t in range(92):
        n = 800
        mom = rng.normal(size=n)
        nd = rng.normal(size=n)
        tr = 0.6 * mom + 0.8 * rng.normal(size=n)
        y = 0.02 * mom + 0.02 * nd + rng.normal(0, 0.12, n)
        sig = {"S1": mom, "S2": X.smooth_momentum_score(mom, nd), "S3": tr}
        series.append(X.date_stats(sig, {"S2": nd, "S3": tr}, y))
        years.append(2010 + (t + 1) // 12)
    S = X.summarise(series, years)
    assert S["S1"]["t"] > 3 and S["S2"]["t_inc"] > 2 and abs(S["S3"]["t_inc"]) < 3
    assert S["S1"]["dec_mean"][-1] > S["S1"]["dec_mean"][0]
    P = X.promotion(S, c=3.0)
    assert P["S2"]["P6_incremental"] and not P["S3"]["P6_incremental"]
    assert P["outcome"] in ("candidate", "replication_only", "none")


def test_promotion_requires_every_criterion():
    base = dict(ic_mean=0.05, t=5.0, top_ann=0.05, spread_ann=0.1, mono=0.9, half_gap=0.01, sub=[0.04, 0.05],
                block_max=0.3, t_inc=4.0)
    S = {s: dict(base) for s in X.SIGNALS}
    assert X.promotion(S, 3.0)["S2"]["pass"]
    for k, v in (("top_ann", 0.02), ("mono", 0.5), ("t", 2.9), ("sub", [0.05, -0.01]), ("block_max", 0.6),
                 ("t_inc", 2.0)):
        S2 = {s: dict(base) for s in X.SIGNALS}
        S2["S2"][k] = v
        assert not X.promotion(S2, 3.0)["S2"]["pass"], k
    S3 = {s: dict(base) for s in X.SIGNALS}
    S3["S2"]["t_inc"] = S3["S3"]["t_inc"] = 1.0
    assert X.promotion(S3, 3.0)["outcome"] == "replication_only"


def test_critical_value_is_kth_largest():
    v = np.arange(1, 5001, dtype=float)
    assert X.critical_value(v, 0.01) == 4951.0                          # the 50th largest of 5,000


def test_tether_is_a_within_date_permutation_and_persistent():
    T = X.Tether(seed=11)
    E1 = list(range(100))
    s1 = T.step(E1)
    assert sorted(s1) == E1                                              # a bijection on the eligible set
    s2 = T.step(E1)
    assert s1 == s2                                                      # partners persist
    E2 = list(range(5, 103))                                             # 5 exits, 3 entries
    s3 = T.step(E2)
    assert sorted(s3) == E2
    kept = [i for i in E2 if i < 100 and s1[i] in E2]
    assert all(s3[E2.index(i)] == s1[i] for i in kept)                   # surviving pairs keep their partner
    assert sum(a != b for a, b in zip(s1, range(100))) > 90              # not the identity


def test_tether_worlds_are_seed_deterministic():
    E = list(range(50))
    assert X.Tether(3).step(E) == X.Tether(3).step(E)
    assert X.Tether(3).step(E) != X.Tether(4).step(E)
