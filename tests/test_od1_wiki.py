"""OD-1 WIKI study helpers (synthetic data only)."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "od"))
import OD1_wiki as W  # noqa: E402


def test_k_features_simple_bars():
    n = 130
    c = np.full((1, n), 100.0)
    o = c.copy()
    h = c * 1.02
    lo = c * 0.98
    o[0, -1] = 104.0                      # gap up of +4% on the last session, closing above the prior close
    c[0, -1] = 106.0
    h[0, -1] = 107.0
    lo[0, -1] = 103.0
    f = W.k_features(o, h, lo, c)
    assert f["GAPUP63"][0] == 1 and f["GAPDN63"][0] == 0 and f["BIGBODY63"][0] == 0
    assert abs(f["CLV21"][0] - (20 * 0.5 + 0.75) / 21) < 1e-12
    assert f["ATRCHG"][0] > 1


def test_binomial_tail():
    assert abs(W.binom_sf(0, 10, 0.5) - 1) < 1e-12
    assert abs(W.binom_sf(10, 10, 0.5) - 2 ** -10) < 1e-15
