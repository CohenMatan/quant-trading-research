"""Phase 2 frozen development rules (research/phase2/P2_spec.md, D094): the spec hash, the candidate
selection metric, gates G1-G4, the robustness trigger and IDs, and the diagnostics."""
import importlib.util
import json

import numpy as np
import pandas as pd
import pytest

from conftest import ROOT
from qresearch import config, experiment, p2spec, registry


def test_spec_hash_is_pinned():
    assert p2spec.spec_hash() == p2spec.SPEC_SHA256


def test_spec_constants():
    assert (p2spec.MARGIN_EW, p2spec.MARGIN_SPY, p2spec.CAGR_TOL, p2spec.DD_TOL) == (0.25, 0.10, 0.02, 0.05)
    assert (p2spec.G3_MIN_BLOCKS, p2spec.G3_MAX_SHARE) == (4, 0.50)
    assert (p2spec.G4_KEEP, p2spec.G4_MIN_PERTURB, p2spec.G4_MAX_COST) == (0.10, 5, 0.015)
    assert p2spec.HALVES == (("2010-01-04", "2015-12-31"), ("2016-01-01", "2021-12-31"))
    assert [b[0][:4] for b in p2spec.BLOCKS] == ["2010", "2012", "2014", "2016", "2018", "2020"]
    assert config.SCHEMES["2010"]["DEV"] == (config.OFFICIAL_START, config.LAST_UNLOCKED_DATE)


def _r(seed, mu=0.0004, sd=0.01, idx=None):
    idx = idx if idx is not None else pd.bdate_range("2010-01-04", "2021-12-31").strftime("%Y-%m-%d")
    return pd.Series(np.random.default_rng(seed).normal(mu, sd, len(idx)), index=idx)


def test_choose_candidate_b_only_if_better_in_both_halves():
    ew = _r(1)
    a = ew + 0.0002
    b_both = ew + 0.0004
    first = (ew.index <= "2015-12-31")
    b_one = ew + np.where(first, 0.001, 0.0)                 # far better in one half, equal-ish in the other
    assert p2spec.choose_candidate(a, b_both, ew)["chosen"] == "B"
    assert p2spec.choose_candidate(a, b_one, ew)["chosen"] == "A"
    assert p2spec.choose_candidate(a, a, ew)["chosen"] == "A"   # ties keep the primary


def _eq(r, start=100000.0):
    return pd.Series(start * np.cumprod(1 + r.to_numpy()), index=r.index)


def test_g1_items():
    ew = _r(2, mu=0.0008)
    spy = ew + _r(3, mu=0.0, sd=0.001)
    strong = ew * 0.8 + 0.0003
    g = p2spec.g1(_eq(strong), _eq(ew), _eq(spy))
    assert g["items"]["G1.1"]["ok"] and g["ok"]
    weak = ew * 1.0 + 0.00002
    g = p2spec.g1(_eq(weak), _eq(ew), _eq(spy))
    assert not g["items"]["G1.1"]["ok"] and not g["ok"]
    cash = ew * 0.3 + 0.0001                                 # higher Sharpe by holding little stock
    g = p2spec.g1(_eq(cash), _eq(ew), _eq(spy))
    assert not g["items"]["G1.2"]["ok"]
    lev = ew * 2.0                                           # same Sharpe, drawdown much deeper
    g = p2spec.g1(_eq(lev), _eq(ew), _eq(spy))
    assert not g["items"]["G1.4"]["ok"] and not g["items"]["G1.1"]["ok"]


def test_g2_strict_and_median():
    assert p2spec.g2(1.0, 0.9, 0.8, [0.7, 1.2, 0.95])["ok"]
    assert not p2spec.g2(1.0, 1.0, 0.8, [0.7, 0.8, 0.9])["ok"]             # equal is not beating
    assert not p2spec.g2(1.0, 0.9, 0.8, [0.7, 1.05, 1.2])["ok"]            # below the median seed
    assert not p2spec.g2(1.0, 0.9, 0.8, [0.7, 0.8])["ok"]                  # a missing seed fails


def test_g3_blocks_and_concentration():
    ew = _r(4)
    even = ew + 0.0002
    g = p2spec.g3(even, ew)
    assert g["blocks_beating_ew"] == 6 and g["max_block_share"] == pytest.approx(1 / 6, rel=0.05) and g["ok"]
    lumpy = ew + np.where((ew.index >= "2020-01-01"), 0.002, 0.00001)
    g = p2spec.g3(lumpy, ew)
    assert g["max_block_share"] > 0.5 and not g["ok"]
    few = ew + np.where((ew.index < "2014-01-01"), 0.0005, -0.00005)
    assert p2spec.g3(few, ew)["blocks_beating_ew"] <= 3 and not p2spec.g3(few, ew)["ok"]


def test_g4_and_cost_drag():
    assert p2spec.g4([0.2] * 5 + [0.0], 0.15, 0.012)["ok"]
    assert not p2spec.g4([0.2] * 4 + [0.0, 0.05], 0.15, 0.012)["ok"]
    assert not p2spec.g4([0.2] * 6, 0.09, 0.012)["ok"]
    assert not p2spec.g4([0.2] * 6, 0.2, 0.016)["ok"]
    g = p2spec.g4(None, None, 0.01)                         # not run -> fails, but (c) still evaluated
    assert not g["ok"] and g["items"]["G4c"]["ok"]
    eq = pd.Series([100000.0] * 253, index=pd.bdate_range("2010-01-04", periods=253).strftime("%Y-%m-%d"))
    fills = pd.DataFrame(dict(order_id=range(10), quantity=[100] * 10, price=[100.0] * 10, fee=[7.0] * 10))
    d = p2spec.cost_drag(fills, eq, 0.001)
    yrs = (pd.Timestamp(eq.index[-1]) - pd.Timestamp(eq.index[0])).days / 365.25
    assert d["total_pa"] == pytest.approx((70 + 100000 * 0.001) / 100000 / yrs)


def test_robustness_trigger():
    assert p2spec.robustness_triggered(True, True, True)
    for x in [(False, True, True), (True, False, True), (True, True, False)]:
        assert not p2spec.robustness_triggered(*x)


def test_dsr_views_and_bootstrap():
    r = _r(5, mu=0.0006)
    v = p2spec.dsr_views(r.to_numpy(), 2, 11, 42)
    assert v["P2 candidates"]["dsr"] > v["P2 broad"]["dsr"] > v["cumulative"]["dsr"]
    assert v["cumulative"]["sr_star_annual"] == pytest.approx(1.08, abs=0.02)   # SR* (not the DSR>=0.9 hurdle)
    a = p2spec.paired_bootstrap_sharpe_diff(r, _r(6), n_boot=200)
    b = p2spec.paired_bootstrap_sharpe_diff(r, _r(6), n_boot=200)
    assert a == b and a["ci95"][0] < a["point"] < a["ci95"][1]


def test_classification():
    c = p2spec.classify(0.05, False, True, False)
    assert c == {"profitable": True, "benchmark-beating": False, "control-beating": True, "development-qualified": False}


def _mk():
    spec = importlib.util.spec_from_file_location("p2mk", ROOT / "research/phase2/P2_make_configs.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_robustness_configs_are_the_pre_declared_nine():
    mk = _mk()
    for cand, lim in (("E014-01", (42, 84)), ("E014-02", (84, 168))):
        cfgs = mk.robustness(cand)
        base = json.loads((config.EXPERIMENTS_DIR / cand / "config.json").read_text())
        assert [c["experiment_id"] for c in cfgs] == [f"E014-{i}" for i in range(15, 24)]
        for c in cfgs:
            experiment.validate(c)
            assert c["robustness_of"] == cand and registry.trial_category(c) == registry.ROBUSTNESS
            diff = {k for k in c["params"] if c["params"][k] != base["params"][k]}
            stress = c["costs"].get("slippage_stress_multiple", 1)
            assert len(diff) + (stress != 1) == 1
        assert [c["costs"].get("slippage_stress_multiple", 1) for c in cfgs[:3]] == [2, 4, 6]
        assert [c["params"]["rsi_pullback"] for c in cfgs[3:5]] == [35, 45]
        assert [c["params"]["window"] for c in cfgs[5:7]] == [3, 8]
        assert tuple(c["params"]["limit"] for c in cfgs[7:9]) == lim


def test_p2_trial_categories():
    c = json.loads((config.EXPERIMENTS_DIR / "E014-01" / "config.json").read_text())
    assert registry.trial_category(c) == registry.SELECTION
    ctrl = json.loads((config.EXPERIMENTS_DIR / "E014-03" / "config.json").read_text())
    assert ctrl["kind"] == "benchmark"          # controls are never trials (verification/benchmark runs)
