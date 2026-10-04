"""Phase 3 selection procedure (qr_p3_pipeline) on synthetic inputs over the real 1,533-configuration grammar: folds,
score and safeguards, plateau score (an isolated peak loses to a plateau), clusters and interior centres, the
one-standard-error simplicity rule, and a walk-forward that never uses data after the selection cut (truncation)."""
import numpy as np
import pytest

from conftest import ROOT, load_module

G = load_module(ROOT / "src/qresearch/lean/qr_p3_grammar.py", "qr_p3_grammar_p")
P = load_module(ROOT / "src/qresearch/lean/qr_p3_pipeline.py", "qr_p3_pipeline_p")
YEARS = list(range(2010, 2018))
SESS = np.array([210] + [252] * 7, float)

C = G.enumerate_configs()
IDS = [c["id"] for c in C]
IX = {c: i for i, c in enumerate(IDS)}
NB = G.neighbours(C)
NBI = [np.array([IX[o] for o in NB[c]], dtype=int) for c in IDS]
CPX = [G.complexity(c) for c in C]


def inputs(seed=0, mu=None, sd=0.08):
    rng = np.random.default_rng(seed)
    n = len(C)
    logex = rng.normal(-0.02, sd, (n, 8)) * SESS / 252
    if mu is not None:
        logex += mu[:, None] * SESS / 252
    cost = np.full((n, 8), 1000.0)
    eqsum = np.full((n, 8), 100_000.0) * SESS
    notional = np.full((n, 8), 400_000.0)
    maxdd = np.full((n, 8), -0.20)
    return P.Inputs(IDS, logex, cost, eqsum, notional, maxdd, SESS, np.full(8, -0.20), np.zeros(8), YEARS)


def test_folds():
    assert P.folds_upto(2017) == [(2010, 2011), (2012, 2013), (2014, 2015), (2016, 2017)]
    assert P.folds_upto(2014) == [(2010, 2011), (2012, 2013), (2014,)]
    assert P.folds_upto(2013) == [(2010, 2011), (2012, 2013)]


def test_score_and_safeguards():
    inp = inputs()
    inp.logex[0] = np.array([0.05, 0.05, 0.05, 0.05, -0.01, -0.01, 0.05, 0.05])
    t = P.score_table(inp, 2017)
    expect = [(0.10) / 462 * 252, 0.10 / 504 * 252, -0.02 / 504 * 252, 0.10 / 504 * 252]
    assert t["F"][0] == pytest.approx(expect)
    assert t["s"][0] == pytest.approx(np.median(expect))
    assert t["eligible"][0]                                   # 3 of 4 folds positive
    inp.cost[0] = 4000.0                                      # 4000 / 100000 a year = 4% > 1.5%
    assert not P.score_table(inp, 2017)["eligible"][0]
    inp.cost[0] = 1000.0
    inp.maxdd[0, -1] = -0.31                                  # deeper than SPY - 10 points
    assert not P.score_table(inp, 2017)["eligible"][0]


def test_isolated_peak_loses_to_plateau():
    mu = np.zeros(len(C))
    peak = IX[IDS[500]]
    mu[peak] = 0.30                                           # one spectacular configuration, neighbours ordinary
    region = [IX[IDS[900]]] + list(NBI[IX[IDS[900]]])
    for i in list(region):
        region += list(NBI[i])
    region = sorted(set(region))
    mu[region] = 0.12                                         # a broad region of good configurations
    inp = inputs(seed=4, mu=mu, sd=0.01)
    r = P.select(inp, NBI, CPX, 2017)
    assert r["ps"][peak] < r["ps"][IX[IDS[900]]]
    top = r["ranked"][0]
    assert top["centre"] in region and top["centre"] != peak
    assert all(k in set(top["members"]) for k in NBI[top["centre"]]) == top["interior"]


def test_one_standard_error_rule_prefers_simpler():
    ids = ["C0000000001", "C0000000002", "C0000000003"]
    cl = [dict(members=[0], centre=0, interior=True, size=3), dict(members=[1], centre=1, interior=True, size=3),
          dict(members=[2], centre=2, interior=True, size=3)]
    cpx = [(1, 1), (3, 4), (2, 2)]
    turn = [4.0, 4.0, 4.0]
    F = np.array([[0.10, 0.10, 0.10, 0.10], [0.05, 0.17, 0.08, 0.14], [0.0, 0.0, 0.0, 0.0]])
    se_b = P.SE_MEDIAN * np.std(F[1], ddof=1) / 2                 # = 0.034
    ps = np.array([0.11 - se_b + 0.001, 0.11, 0.02])           # simple cluster within one SE of the best
    r = P.rank_clusters(cl, ps, F, cpx, turn, ids)
    assert [c["centre"] for c in r] == [0, 1, 2] and r[0]["se"] == pytest.approx(se_b)
    ps2 = np.array([0.11 - se_b - 0.001, 0.11, 0.02])          # simple cluster just outside one SE -> the best wins
    assert [c["centre"] for c in P.rank_clusters(cl, ps2, F, cpx, turn, ids)][0] == 1
    turn2 = [4.0, 4.0, 1.0]                                    # equal complexity -> lower turnover first
    cpx2 = [(2, 2), (3, 4), (2, 2)]
    ps3 = np.array([0.11 - 0.01, 0.11, 0.11 - 0.02])
    assert P.rank_clusters(cl, ps3, F, cpx2, turn2, ids)[0]["centre"] == 2


def test_walk_forward_uses_only_past_data():
    mu = np.zeros(len(C))
    mu[IX[IDS[50]]] = 0.05
    inp = inputs(seed=9, mu=mu)
    wf = P.walk_forward(inp, NBI, CPX)
    for k, Y in enumerate(P.WF_YEARS):
        alt = inputs(seed=9, mu=mu)
        col = alt.col(Y)
        alt.logex[:, col:] = np.random.default_rng(99).normal(0, 0.5, alt.logex[:, col:].shape)   # rewrite the future
        wf2 = P.walk_forward(alt, NBI, CPX, years=(Y,))
        assert wf2["years"][0]["pick"] == wf["years"][k]["pick"]


def test_world_summary_shape():
    s = P.world_summary(inputs(seed=1), NBI, CPX)
    assert set(s) >= {"best_ps", "n_eligible", "n_clusters", "ranked", "wf"}
    assert len(s["ranked"]) <= 3 and len(s["wf"]["years"]) == 4
