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


def test_d073_cycle_pbo_gate_uses_the_full_selection_set():
    """D073 (frozen): the hard gate is PBO <= 0.30 over ALL the cycle's selection candidates; a
    candidate without a return series makes the gate fail (incomplete), never silently shrink."""
    import pandas as pd
    from qresearch import cycle
    rng = np.random.default_rng(9)
    idx = pd.RangeIndex(2012)
    m = SIM.simulate(rng, [1.5] * 3 + [0.0] * 15, [j // 3 for j in range(18)], 0.8, 0.5)
    ids = [f"E0{6 + j // 3:02d}-0{1 + j % 3}" for j in range(18)]
    rets = {i: pd.Series(m[:, k], index=idx) for k, i in enumerate(ids)}
    out = cycle.cycle_pbo(rets, ids)
    assert out["n_candidates"] == 18 and out["complete"] and out["threshold"] == 0.30
    assert out["pbo"] == stats.pbo_cscv(m, n_blocks=16)["pbo"]
    assert out["gate_ok"] == (out["pbo"] <= 0.30)
    rets.pop(ids[4])
    assert cycle.cycle_pbo(rets, ids)["complete"] is False and cycle.cycle_pbo(rets, ids)["gate_ok"] is False
    assert cycle.PBO_GATE == 0.30
