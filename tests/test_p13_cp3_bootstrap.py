"""P13-CP3 (owner D223): bootstrap mechanics on SYNTHETIC donor returns (paired blocks, whole years, no circular wrap,
exclusions, deterministic seeds, metric definitions); and, once committed, the real output's consistency."""
import json
import math
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research/phase13/cp3"))
import P13_CP3_bootstrap as B  # noqa: E402


def _lr(seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(0.008, 0.04, (84, 3))


def test_year_blocks_paired_whole_years_and_deterministic():
    idx = B.month_index("year", 7)
    assert idx.size == 360 and np.array_equal(idx, B.month_index("year", 7))
    blocks = idx.reshape(30, 12)
    assert all(b[0] % 12 == 0 and np.array_equal(b, np.arange(b[0], b[0] + 12)) for b in blocks)
    L, _ = B.simulate(_lr(), "year", [7])
    assert np.array_equal(L[0], _lr()[idx])                       # the same months for all three series (paired)


def test_moving_blocks_no_wrap_and_exclusions():
    for meth, Lb in (("mb12", 12), ("mb24", 24)):
        idx = B.month_index(meth, 3).reshape(-1, Lb)
        assert idx.shape[0] * Lb == 360 and idx.max() <= 83
        assert all(np.array_equal(b, np.arange(b[0], b[0] + Lb)) for b in idx)
    for s in range(1, 50):
        yrs = set(B.month_index("ex1820", s)[::12] // 12)
        assert not yrs & {3, 5}                                    # 2018, 2020 never drawn
        assert 0 not in set(B.month_index("loo_2015", s)[::12] // 12)
    assert not np.array_equal(B.month_index("year", 1), B.month_index("mb12", 1))


def test_metric_definitions_on_a_constructed_world():
    L = np.zeros((1, 360, 3))
    L[0, :, 0] = 0.01                       # H028 +1%/month (log)
    L[0, :12, 0] = -0.02                    # first year behind
    m = B.world_metrics(L)
    assert m["log_rel_spy_30"][0] == pytest.approx(0.01 * 348 - 0.24)
    assert m["streak_spy"][0] == 1 and m["win_years_spy"][0] == 29
    assert m["rel_maxdd_spy"][0] == pytest.approx(math.exp(-0.24) - 1)
    assert m["recovery_spy"][0] == 35                               # 12 down months + 23 to regain the high
    assert m["roll_min_spy"][0] == pytest.approx(-0.24 + 0.48)


def test_committed_output_consistent():
    p = ROOT / "research/phase13/cp3/P13_CP3_bootstrap.json"
    if not p.exists():
        return
    o = json.loads(p.read_text())
    assert o["formal_status"] == "H028 REJECTED" and o["reproducibility_all_identical"] and o["audit"]["ok"]
    assert o["audit"]["months"] == 84 and set(o["methods"]) == {"year", "mb12", "mb24", "ex1820"} | {
        f"loo_{y}" for y in B.YEARS}
    assert all(v["worlds"] == (5000 if k.startswith("loo_") else 10000) for k, v in o["methods"].items())
