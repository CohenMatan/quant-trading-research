"""Phase 6 sector-signal test design reference (research/phase6/p6_xs.py): statistics, point-in-time signal, the
identity-tethered derangement null. SYNTHETIC data only (no sector return series exists in the repository)."""
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research" / "phase6"))
import p6_power as PW  # noqa: E402
import p6_xs as P  # noqa: E402


def test_spearman_rows_matches_definition():
    rng = np.random.default_rng(0)
    A, B = rng.normal(size=(20, 9)), rng.normal(size=(20, 9))
    A[3, 2] = A[3, 5]                                            # a tie
    got = P.spearman_rows(A, B)
    for t in range(20):
        ra, rb = P.avg_rank(A[t]), P.avg_rank(B[t])
        assert got[t] == pytest.approx(np.corrcoef(ra, rb)[0, 1], abs=1e-12)


def test_signal_is_point_in_time():
    R = PW.make_panel(60, 9, seed=1)
    S = P.signal(R, 6)
    R2 = R.copy()
    R2[31:] = 0.5                                                 # change everything after month 30
    S2 = P.signal(R2, 6)
    assert np.allclose(S[:31], S2[:31], equal_nan=True)
    assert S[30, 0] == pytest.approx(np.prod(1 + R[25:31, 0]) - 1)
    assert np.isnan(S[4]).all() and np.isfinite(S[5]).all()


def test_derangement_has_no_fixed_point():
    rng = np.random.default_rng(3)
    for _ in range(200):
        p = P.derangement(rng, 9)
        assert sorted(p) == list(range(9)) and not np.any(p == np.arange(9))


def test_planted_momentum_is_found_and_the_null_breaks_it():
    R = PW.make_panel(240, 9, drift_sd=0.02, seed=4)
    real = P.run_world(R, (6,), 5)
    null = [P.run_world(R, (6,), 5, seed=s)["max_t_ic"] for s in range(40)]
    assert real[6]["t_ic"] > 4 and real[6]["top_ann"] > 0
    assert abs(np.mean(null)) < 1.0 and max(null) < real[6]["t_ic"]


def test_no_edge_panels_are_calibrated_roughly():
    st = [P.run_world(PW.make_panel(220, 9, seed=100 + i), (6,), 5)["max_t_ic"] for i in range(150)]
    assert 0.7 < np.std(st) < 1.3 and abs(np.mean(st)) < 0.3


def test_full_procedure_null_uses_the_max_over_declared_lookbacks():
    R = PW.make_panel(240, 9, seed=6)
    w = P.run_world(R, (6, 12), 11, seed=9)
    assert w["max_t_ic"] == max(w[6]["t_ic"], w[12]["t_ic"])
