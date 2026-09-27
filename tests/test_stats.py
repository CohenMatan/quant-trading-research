import numpy as np
import pandas as pd
import pytest

from qresearch import stats


def test_psr_increases_with_sharpe_and_sample():
    rng = np.random.default_rng(0)
    noise = rng.normal(0, 0.01, 2000)
    lo, hi = noise + 0.0002, noise + 0.001
    assert stats.probabilistic_sharpe(hi) > stats.probabilistic_sharpe(lo)
    assert stats.probabilistic_sharpe(hi[:200]) < stats.probabilistic_sharpe(hi)


def test_psr_normal_case_matches_closed_form():
    # with zero skew and kurtosis 3 the denominator is 1 + SR^2 / 2
    rng = np.random.default_rng(1)
    r = rng.normal(0.0005, 0.01, 5000)
    s = pd.Series(r)
    sr = r.mean() / r.std(ddof=1)
    denom = 1 - s.skew() * sr + (s.kurt() + 3 - 1) / 4 * sr * sr
    from scipy.stats import norm
    assert stats.probabilistic_sharpe(r) == pytest.approx(norm.cdf(sr * np.sqrt(len(r) - 1) / np.sqrt(denom)))


def test_expected_max_sharpe_grows_with_trials():
    assert stats.expected_max_sharpe(1, 0.01) == 0.0
    v = [stats.expected_max_sharpe(n, 0.0004) for n in (2, 10, 100, 1000)]
    assert v == sorted(v) and v[0] > 0


def test_dsr_penalises_many_trials():
    rng = np.random.default_rng(2)
    r = rng.normal(0.0006, 0.01, 2500)
    one = stats.deflated_sharpe(r, 1, 0.0004)
    many = stats.deflated_sharpe(r, 200, 0.0004)
    assert one == pytest.approx(stats.probabilistic_sharpe(r))
    assert many < one


def test_pbo_dominant_strategy_is_zero():
    rng = np.random.default_rng(3)
    m = rng.normal(0, 0.01, (1600, 6))
    m[:, 0] += 0.01                                   # best everywhere
    assert stats.pbo_cscv(m, n_blocks=8)["pbo"] == 0.0


def test_pbo_pure_noise_is_about_half():
    rng = np.random.default_rng(4)
    vals = [stats.pbo_cscv(rng.normal(0, 0.01, (800, 10)), n_blocks=8)["pbo"] for _ in range(12)]
    assert 0.25 < float(np.mean(vals)) < 0.75


def test_pbo_overfit_construction_is_one():
    # variation k is strong in block k's half and weak elsewhere: IS winner reverses OOS
    t, n = 800, 2
    m = np.zeros((t, n))
    m[: t // 2, 0], m[t // 2:, 0] = 0.01, -0.01
    m[: t // 2, 1], m[t // 2:, 1] = -0.01, 0.01
    m += np.random.default_rng(5).normal(0, 1e-4, m.shape)
    out = stats.pbo_cscv(m, n_blocks=2)
    assert out["n_splits"] == 2 and out["pbo"] == 1.0


def test_pbo_validates_input():
    with pytest.raises(ValueError):
        stats.pbo_cscv(np.zeros((100, 1)))
    with pytest.raises(ValueError):
        stats.pbo_cscv(np.zeros((100, 3)), n_blocks=5)


def test_trade_distribution_helpers():
    pnl = pd.Series([100.0] + [1.0] * 99)
    c = stats.profit_concentration(pnl)
    assert c["top_1pct_share"] == pytest.approx(100 / 199)
    ret = pd.Series([0.5, 0.1, 0.0, -0.1])
    assert stats.expectancy_without_best(ret, 1) == pytest.approx(0.0)
    lo, hi = stats.bootstrap_mean_ci(np.random.default_rng(6).normal(0.01, 0.05, 500))
    assert lo < 0.01 < hi
    assert stats.bootstrap_mean_ci(np.array([1.0, 2.0, 3.0])) == stats.bootstrap_mean_ci(np.array([1.0, 2.0, 3.0]))
