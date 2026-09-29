"""The C02 PBO calibration uses a vectorised CSCV; it must equal the official stats.pbo_cscv."""
import numpy as np

from conftest import ROOT, load_module
from qresearch import stats

SIM = load_module(ROOT / "research/cycles/C02_pbo_simulation.py", "c02_pbo_sim")


def test_fast_pbo_equals_official_implementation():
    rng = np.random.default_rng(3)
    for n, d in ((3, 0.0), (3, 1.0), (5, 0.5)):
        m = SIM.simulate(rng, [0.5 + d] + [0.5] * (n - 1), [0] * n, 0.8, 0.8)
        assert SIM.pbo_fast(m) == stats.pbo_cscv(m, n_blocks=16)["pbo"]


def test_three_variations_attainable_values():
    """With N = 3 the IS winner's OOS relative rank is 1/4, 2/4 or 3/4; the middle counts as overfit,
    so PBO is the share of splits where the IS winner is not also the OOS winner."""
    m = np.zeros((2012, 3))
    m[:, 0] = 1e-3 + np.random.default_rng(1).normal(0, 1e-4, 2012)   # dominates in every split
    m[:, 1] = np.random.default_rng(2).normal(0, 1e-2, 2012)
    m[:, 2] = np.random.default_rng(4).normal(0, 1e-2, 2012)
    assert stats.pbo_cscv(m)["pbo"] == 0.0
