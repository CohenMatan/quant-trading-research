"""Amendment 3 (terminal-wealth framework, qresearch.wealth): estimators, gate logic, reporting, spec freeze."""
import numpy as np
import pytest

from qresearch import wealth as W


def _sb_mc(d, block, reps, rng):
    n = len(d)
    out = []
    for _ in range(reps):
        flags = rng.random(n) < 1.0 / block
        flags[0] = True
        pos = np.flatnonzero(flags)
        seg = np.cumsum(flags) - 1
        starts = rng.integers(n, size=len(pos))
        out.append(d[(starts[seg] + np.arange(n) - pos[seg]) % n].mean() * 252)
    return float(np.std(out))


@pytest.mark.parametrize("rho,block", [(0.0, 21), (0.4, 63)])
def test_exact_stationary_bootstrap_se_matches_monte_carlo(rho, block):
    rng = np.random.default_rng(3)
    n = 800
    e = rng.normal(0, 0.01, n)
    d = np.zeros(n)
    for t in range(1, n):
        d[t] = rho * d[t - 1] + e[t]
    assert W.se_stationary_bootstrap(d, block) == pytest.approx(_sb_mc(d, block, 4000, rng), rel=0.06)


def test_w2_standard_error_never_below_iid_and_tracks_persistence():
    rng = np.random.default_rng(4)
    iid = rng.normal(0, 0.01, 3000)
    assert W.se_w2(iid) >= W.se_iid(iid)
    pers = np.convolve(rng.normal(0, 0.01, 3100), np.ones(100) / 10, mode="valid")[:3000]   # positively dependent
    assert W.se_w2(pers) > 1.5 * W.se_iid(pers)


def test_w2_test_uses_the_frozen_constants():
    rng = np.random.default_rng(5)
    spy = rng.normal(0.0005, 0.01, 3000)
    h = spy + rng.normal(0.0, 0.004, 3000) + 0.10 / 252          # a large, steady edge
    t = W.w2_test(h, spy)
    assert t["ok"] and t["threshold"] == pytest.approx(W.W2_CRITICAL * W.se_w2(W.log_excess(h, spy)))
    t0 = W.w2_test(spy + rng.normal(0.0, 0.004, 3000), spy)
    assert not t0["ok"]


def test_owner_examples_r1_r2():
    # owner example: CAGR 13.5% vs 10.5%, Sharpe 0.77 vs 0.80, MaxDD -39% vs -35% must not fail R1/R2
    assert W.r2_ok(0.77, 0.80) and W.r1_ok(-0.39, -0.35)
    # +0.5% CAGR with a catastrophic drawdown fails R1; a materially worse Sharpe fails R2
    assert not W.r1_ok(-0.60, -0.35)
    assert not W.r2_ok(0.55, 0.80)
    assert W.R2_TOLERANCE == 0.15 and W.R1_MAX_EXTRA_DD == 0.10 and W.W2_CRITICAL == 2.15 and W.W2_MEAN_BLOCK == 126


def _books(rng, n=3024, edge=0.0):
    spy = rng.normal(0.0006, 0.011, n)
    ew = spy + rng.normal(0, 0.003, n)
    rand = [ew + rng.normal(0, 0.005, n) for _ in range(5)]
    h = ew + rng.normal(0, 0.005, n) + edge / 252
    return h, spy, ew, rand


def test_gates_w3_needs_five_random_books_and_qualification_requires_r4():
    rng = np.random.default_rng(6)
    h, spy, ew, rand = _books(rng, edge=0.15)
    g = W.evaluate_gates(h, spy, ew, rand, cost_pa=0.004)
    assert g["W1"]["ok"] and g["W2"]["ok"] and g["W3"]["ok"] and g["qualified"]
    assert not W.evaluate_gates(h, spy, ew, rand[:4], cost_pa=0.004)["W3"]["ok"]
    assert not W.evaluate_gates(h, spy, ew, rand, cost_pa=0.02)["qualified"]          # R4 cost cap
    assert not W.evaluate_gates(h, spy, ew, rand, cost_pa=0.004, no_leverage=False)["qualified"]


def test_r3_rejects_a_single_lucky_block():
    n = 3024
    spy = np.full(n, 0.0004)
    h = spy.copy()
    h[:504] += 0.002                       # all excess in the first two-year block
    g = W.evaluate_gates(h, spy, spy, [spy] * 5)
    assert g["R3"]["max_block_share"] == pytest.approx(1.0) and not g["R3"]["ok"]


def test_wealth_table_and_rolling_report():
    n = 2521
    spy = np.full(n - 1, 0.0003)
    h = np.full(n - 1, 0.0004)
    eq_h = 100000 * np.concatenate([[1], np.cumprod(1 + h)])
    eq_s = 100000 * np.concatenate([[1], np.cumprod(1 + spy)])
    t = W.wealth_table(eq_h, eq_s)
    assert t["starting_capital"] == 100000 and t["terminal_wealth_ratio"] > 1 and t["excess_cagr"] > 0
    r = W.rolling_report(h, spy)
    assert r["1y"]["share_beats_spy"] == 1.0 and r["10y"]["windows"] == n - 1 - 2520 + 1
    assert r["10y"]["independent_windows"] == pytest.approx((n - 1) / 2520, abs=0.01)


def test_g4_prime():
    assert W.g4_prime([True] * 5 + [False], True)["ok"]
    assert not W.g4_prime([True] * 4 + [False] * 2, True)["ok"]
    assert not W.g4_prime([True] * 6, False)["ok"]
    assert not W.g4_prime(None, True)["ok"]


def test_amendment3_spec_is_frozen_and_hash_pinned():
    assert W.AMENDMENT3_SHA256 != "PENDING"
    assert W.spec_hash() == W.AMENDMENT3_SHA256      # any change -> STOP and ask the owner
