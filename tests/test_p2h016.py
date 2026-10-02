"""H016 evaluation (qresearch.p2h016) on synthetic equity curves: the common evaluation window, G2 against the median
of five random controls, and the frozen survivorship sensitivity diagnostic."""
import numpy as np
import pandas as pd
import pytest

from qresearch import p2h016, p2spec


def _eq(start, end, mu, sd, seed):
    d = pd.bdate_range(start, end).strftime("%Y-%m-%d")
    r = np.random.default_rng(seed).normal(mu, sd, len(d))
    return pd.Series(100000.0 * np.cumprod(1 + r), index=d)


def test_common_window_is_identical_for_every_book():
    a = _eq("2010-01-04", "2021-12-31", 0.0004, 0.01, 1)
    b = _eq("2010-03-01", "2021-12-31", 0.0004, 0.01, 2)
    wa, wb = p2h016.window_eq(a), p2h016.window_eq(b)
    assert wa.index[0] == wb.index[0] == "2010-03-01" and wa.index[-1] == wb.index[-1] == "2021-12-31"
    assert len(p2h016.rets(a)) == len(p2h016.rets(b))


def test_g2_uses_the_median_of_five_individual_controls():
    out = p2h016.g2(0.9, [0.5, 1.2, 0.7, 0.95, 0.6])
    assert out["median_random"] == 0.7 and out["ok"] and out["random_sharpes"] == [0.5, 1.2, 0.7, 0.95, 0.6]
    assert not p2h016.g2(0.7, [0.5, 1.2, 0.7, 0.95, 0.6])["ok"]          # strictly greater
    assert not p2h016.g2(2.0, [0.5, 1.2, 0.7])["ok"]                     # exactly five or it fails


def test_survivorship_sensitivity_is_frozen_and_only_penalises_the_candidate():
    assert p2h016.survivorship_penalty_pp(2021) == pytest.approx(4.05 + 100 * 11 / 1426 * 0.397)
    assert p2h016.survivorship_penalty_pp(2010) == pytest.approx(100 * 4 / 663 * 0.397)    # negative bias not applied
    h = _eq("2010-01-04", "2021-12-31", 0.0006, 0.01, 3)
    ew = _eq("2010-01-04", "2021-12-31", 0.0004, 0.01, 4)
    s = p2h016.survivorship_sensitivity(h, ew)
    assert s["s1_penalised_d_ew"] < s["base_d_ew"]
    assert s["base_d_ew"] == pytest.approx(p2h016.d_ew(h, ew))
    assert s["s2_from"] == "2012-01-01"


def test_dsr_views_use_the_phase2_counts():
    r = np.random.default_rng(5).normal(0.0004, 0.01, 2900)
    v = p2h016.dsr_views(r, 6)
    assert v["P2 candidates"]["n"] == 3 and v["P2 broad"]["n"] == 9 and v["cumulative"]["n"] == 43


def test_gate_thresholds_are_the_unchanged_phase2_ones():
    assert p2spec.MARGIN_EW == 0.25 and p2spec.MARGIN_SPY == 0.10 and p2spec.G4_MAX_COST == 0.015
    assert p2h016.COMMON_START == "2010-03-01" and len(p2h016.RANDOM) == 5 and len(p2h016.PERTURBATIONS) == 6
