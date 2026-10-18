"""OC-2 Stage 2 (owner D248): mechanics of the synthetic generator and the Fama-MacBeth inference (software checks
only; no calibration statistic is computed here)."""
import math

import numpy as np

from qresearch import oc2synth as O


def test_correlation_matrix_valid_and_signal_feasible():
    C = O.corr_matrix()
    assert np.all(np.linalg.eigvalsh(C) > 0)
    for s in (0.0, 1.0, 2.0):
        rho = np.array([O.RHO_F5[c] for c in O.CHARS]) * s
        b = np.linalg.solve(C, rho)
        assert b @ C @ b < 1.0


def test_theta_mapping():
    assert math.isclose(12 * O.theta_from_annual(0.03) * O.Z80, 0.03)


def test_nw_and_ranks():
    rng = np.random.default_rng(1)
    b = rng.standard_normal(200) + 0.1
    assert math.isclose(O.nw_t(b, 0), b.mean() / (b.std() / math.sqrt(len(b))), rel_tol=1e-12)
    ar = np.zeros(400)
    for i in range(1, 400):
        ar[i] = 0.6 * ar[i - 1] + rng.standard_normal()
    ar = ar + 0.2
    assert abs(O.nw_t(ar, 6)) < abs(O.nw_t(ar, 0))                       # positive autocorrelation widens the SE
    r = O.crank(np.array([3.0, 1.0, 2.0, 10.0]))
    assert np.allclose(sorted(r), [-0.375, -0.125, 0.125, 0.375]) and r[3] == 0.375


def test_design_recovers_slope():
    rng = np.random.default_rng(2)
    n = 600
    sig, Z = rng.standard_normal(n), rng.standard_normal((n, 8))
    sec = rng.integers(0, len(O.SECTORS), n)
    X = O.design(sig, Z, sec)
    y = 0.02 * X[:, 0] + 0.01 * X[:, 3] + 0.005 * (sec == 2)
    assert math.isclose(O.ols_first(X, y), 0.02, rel_tol=1e-9)


def test_year_concentration():
    b = np.zeros(O.T)
    b[:] = 0.001
    assert O.year_concentration_ok(b)
    b[30] = 1.0
    assert not O.year_concentration_ok(b)
    assert not O.year_concentration_ok(-np.ones(O.T))


def test_population_structure_and_seeds():
    n = O.n_by_month()
    assert len(n) == O.T and n[0] < n[-1] and abs(n.mean() - 760) < 40
    assert O.seed_of("X", 0) != O.seed_of("Y", 0) and O.seed_of("X", 1) == O.seed_of("X", 0) + 1
    o = O.run_world(O.World("TEST-structure"), 0)
    assert abs(o["mean_n"] - n.mean()) / n.mean() < 0.02
    assert abs(o["fresh_by_phase"][0] - 0.62) < 0.08 and abs(o["fresh_by_phase"][1] - 0.10) < 0.08
    m = O.run_world(O.World("TEST-mnar", mnar=True), 0)
    assert abs(m["mean_n"] - n.mean()) / n.mean() < 0.05
    assert 0.05 < o["ret_sd"] < 0.08


def test_gross_planted_effect_is_detected():
    o = O.run_world(O.World("TEST-planted", planted=0.30), 0)        # ten times the reference effect
    assert o["t_nw3"] > 5 and o["tq_annual"] > 0.15


def test_bootstrap_p_range():
    rng = np.random.default_rng(3)
    p = O.block_boot_p(rng.standard_normal(O.T), rng)
    assert 0 < p <= 1
