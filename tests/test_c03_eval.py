"""C03 after Amendment 1 (D087): the H013 configurations match their approved specification, and the
evaluation enforces the all-three-seeds rule, the mechanical choice and robustness per seed."""
import json

import pytest

from conftest import ROOT, load_module
from qresearch import config

EVAL = load_module(ROOT / "research/cycles/C03_eval.py", "c03_eval")
SPEC = {"v1.0": dict(q=0.20, stat="max"), "v1.1": dict(q=0.10, stat="max"), "v1.2": dict(q=0.20, stat="max5")}


def cfg(e):
    return json.loads((ROOT / "experiments" / e / "config.json").read_text())


def test_h013_selection_configs_match_the_approved_specification():
    base = cfg("E962-22")
    for i, v in enumerate(SPEC):
        for s in (1, 2, 3):
            c = cfg(f"E013-{3 * i + s:02d}")
            assert (c["kind"], c["hypothesis_id"], c["strategy_id"], c["strategy_version"]) == ("research", "H013", "S013", v)
            assert c["params"] == dict(SPEC[v], seed=s, slots=15, hold=60)
            assert (c["split"], c["start"], c["end"], c["cash"]) == ("IS", "2010-01-04", "2017-12-29", 100000)
            assert c["replicate_param"] == "seed" and c["paired_null"] == f"E962-{21 + s}"
            assert cfg(c["paired_null"])["params"] == dict(slots=15, hold=60, seed=s)
            for k in ("universe", "costs", "portfolio", "lean_version_id", "execution_model", "benchmarks"):
                assert c[k] == base[k], k
            assert c["portfolio"] == config.RESEARCH_PORTFOLIOS["d051"]


def test_h013_sizing_and_null_configs():
    for s in (1, 2, 3):
        s1, s2 = cfg(f"E013-{9 + s}"), cfg(f"E013-{12 + s}")
        n1, n2 = cfg(f"E962-{24 + s}"), cfg(f"E962-{27 + s}")
        for c in (s1, s2):
            assert c["kind"] == "sizing" and c["cash"] == 200000 and c["account_size_test_of"] == f"E013-0{s}"
            assert c["strategy_version"] == "v1.0" and c["params"]["seed"] == s
        assert s1["params"]["slots"] == 15 and s1["portfolio"]["max_positions"] == 15
        assert s2["params"]["slots"] == s2["portfolio"]["max_positions"] == 20 and s2["construction_variant"] == "S2"
        assert (n1["cash"], n1["params"]) == (200000, dict(slots=15, hold=60, seed=s))
        assert (n2["cash"], n2["params"]) == (200000, dict(slots=20, hold=60, seed=s))
        assert s1["paired_null"] == n1["experiment_id"] and s2["paired_null"] == n2["experiment_id"]


def test_research_budget_is_21_committed_runs():
    b = load_module(ROOT / "research/cycles/C03_budget.py", "c03_budget").ledger()
    assert b["research_configs_written"] == 21 and b["research_budget_cap"] == 82


def _fake(monkeypatch, sharpe, screen, robust=None):
    """sharpe/screen/robust: {experiment id: value}; everything else 'not run'."""
    def book(eid):
        if eid not in sharpe:
            return dict(exp=eid, status="not run")
        return dict(exp=eid, status="completed", sharpe=sharpe[eid], screen_pass=screen.get(eid, False), avg_pnl_per_trade=1.0)

    def stages(eid, cfgs):
        r = (robust or {}).get(eid)
        return dict(slippage_2x=dict(ok=screen[eid]) if eid in screen else None,
                    robustness=None if r is None else dict(ok=r))
    monkeypatch.setattr(EVAL, "book", book)
    monkeypatch.setattr(EVAL, "stress_and_robustness", stages)
    monkeypatch.setattr(EVAL, "overlap", lambda a, b: None)


def _ids():
    return {v: [EVAL.H013[v][s] for s in (1, 2, 3)] for v in EVAL.H013}


def test_a_variation_passes_only_if_all_three_seeds_pass(monkeypatch):
    ids = _ids()
    sharpe = {e: 1.2 for v in ids for e in ids[v]} | {n: 0.7 for n in EVAL.NULL.values()}
    screen = {e: True for v in ids for e in ids[v]}
    screen[ids["v1.0"][1]] = False                       # one seed of v1.0 fails
    sharpe[ids["v1.1"][0]] = 2.0                         # v1.1 has the best mean
    _fake(monkeypatch, sharpe, screen)
    h = EVAL.h013_section({})
    assert not h["variations"]["v1.0"]["screen_pass"]
    assert h["variations"]["v1.1"]["screen_pass"] and h["variations"]["v1.2"]["screen_pass"]
    assert EVAL.choose(h, lambda r: r["mean_seed_sharpe"]) == "v1.1"


def test_a_missing_seed_fails_and_ties_go_to_the_lower_version(monkeypatch):
    ids = _ids()
    sharpe = {e: 1.0 for v in ids for e in ids[v]} | {n: 0.7 for n in EVAL.NULL.values()}
    del sharpe[ids["v1.0"][2]]                           # a seed that never completed
    screen = {e: True for e in sharpe}
    _fake(monkeypatch, sharpe, screen)
    h = EVAL.h013_section({})
    assert not h["variations"]["v1.0"]["screen_pass"] and not h["variations"]["v1.0"]["all_seeds_run"]
    assert EVAL.choose(h, lambda r: r["mean_seed_sharpe"]) == "v1.1"   # v1.1 and v1.2 tie


def test_robustness_must_pass_for_every_seed(monkeypatch):
    ids = _ids()
    sharpe = {e: 1.0 for v in ids for e in ids[v]} | {n: 0.7 for n in EVAL.NULL.values()}
    screen = {e: True for e in sharpe}
    robust = {e: True for e in ids["v1.0"]} | {ids["v1.1"][0]: True, ids["v1.1"][1]: False, ids["v1.1"][2]: True}
    _fake(monkeypatch, sharpe, screen, robust)
    h = EVAL.h013_section({})
    assert h["variations"]["v1.0"]["robustness_pass"] is True
    assert h["variations"]["v1.1"]["robustness_pass"] is False
    assert h["variations"]["v1.2"]["robustness_pass"] is None      # battery not run


def test_no_seed_averaging_in_acceptance(monkeypatch):
    """Two excellent seeds cannot carry a failing one."""
    ids = _ids()
    sharpe = {e: 3.0 for v in ids for e in ids[v]} | {n: 0.7 for n in EVAL.NULL.values()}
    screen = {e: True for e in sharpe}
    screen[ids["v1.2"][2]] = False
    _fake(monkeypatch, sharpe, screen)
    assert not EVAL.h013_section({})["variations"]["v1.2"]["screen_pass"]
