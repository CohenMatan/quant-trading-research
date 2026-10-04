"""Phase 3 frozen specification (P3-CP2): spec and configuration-list pins, the null threshold / Q1 equivalence, the
leave-one-out false-pass accounting, the cluster-level statistic T, and the run-config gates."""
import sys

import numpy as np
import pytest

from qresearch import config, experiment, p3spec

sys.path.insert(0, str(config.REPO_ROOT / "src/qresearch/lean"))
import qr_p3_grammar as G  # noqa: E402
import qr_p3_pipeline as P  # noqa: E402


def test_spec_hash_pinned():
    assert p3spec.spec_hash() == p3spec.SPEC_SHA256


def test_config_list_pinned():
    assert len(G.enumerate_configs()) == p3spec.N_CONFIGS
    assert p3spec.config_list_hash() == p3spec.CONFIG_LIST_SHA256


def test_spec_states_frozen_values():
    s = (config.REPO_ROOT / p3spec.SPEC).read_text()
    for frag in ("1,533", "R = 500", "63 sessions", "**10**", "$7 per executed buy", "10 bps", "25th largest",
                 "2018-01-01 → 2021-12-31", "2022-01-01 → 2026-08-31", "Stage 2", "126-session / 20-position"):
        assert frag in s, frag
    assert p3spec.NULL_SEEDS == tuple(range(1, 501)) and len(p3spec.BLOCK_SEEDS) == 100


@pytest.mark.parametrize("R", [39, 100, 499, 500, 1000])
def test_tau_equals_p_value_rule(R):
    rng = np.random.default_rng(R)
    null = rng.normal(size=R)
    null[:3] = -np.inf                                   # worlds without a cluster
    tau = p3spec.tau_of(null)
    m = int(np.floor(0.05 * (R + 1)))
    assert tau == np.sort(null)[::-1][m - 1]
    for t in np.concatenate([null, null + 1e-9, null - 1e-9, rng.normal(size=200) * 2]):
        assert p3spec.q1(t, null) == (np.isfinite(t) and p3spec.p_value(t, null) <= 0.05)


def test_q1_needs_a_cluster():
    assert not p3spec.q1(-np.inf, np.full(500, -np.inf))


def test_false_pass_leave_one_out():
    rng = np.random.default_rng(7)
    T = rng.normal(size=500)
    wf = rng.random(500) < 0.3
    r = p3spec.false_pass(T, wf)
    assert 20 <= r["q1_passes"] <= 26                    # ~5% by construction
    assert r["full_pipeline_passes"] <= r["q1_passes"]
    lo, hi = r["ci95"]
    assert lo <= r["false_pass_rate"] <= hi
    assert p3spec.clopper_pearson(0, 500)[1] == pytest.approx(0.00735, abs=1e-4)


def _line_graph(n):
    return [np.array([j for j in (i - 1, i + 1) if 0 <= j < n]) for i in range(n)]


def test_cluster_level_definition():
    nb = _line_graph(7)
    ps = np.array([0.9, 0.1, 0.8, 0.7, 0.6, 0.05, 0.95])
    el = np.ones(7, bool)
    # descending: 6 (0.95), 0 (0.9), 2 (0.8), 3 (0.7) -> {2,3} size 2, 4 (0.6) -> {2,3,4} size 3 -> T = 0.6
    assert P.cluster_level(ps, el, nb) == 0.6
    el[3] = False
    # without 3 the line breaks: 1 (0.1) joins {0,1,2} -> T = 0.1
    assert P.cluster_level(ps, el, nb) == pytest.approx(0.1)
    assert P.cluster_level(ps, np.zeros(7, bool), nb) == -np.inf


def test_cluster_level_matches_threshold_rule():
    """T > tau  <=>  a connected cluster of >= 3 survivors exists at tau (the promotion rule)."""
    rng = np.random.default_rng(3)
    C = G.enumerate_configs()
    ix = {c["id"]: i for i, c in enumerate(C)}
    nbg = G.neighbours(C)
    nbi = [np.array([ix[o] for o in nbg[c["id"]]], dtype=int) for c in C]
    ids = [c["id"] for c in C]
    for _ in range(5):
        ps = rng.normal(size=len(C))
        el = rng.random(len(C)) < 0.4
        T = P.cluster_level(ps, el, nbi)
        for tau in (T - 1e-9, T, T + 1e-9, np.percentile(ps, 90), np.percentile(ps, 99)):
            has = len(P.clusters(el & (ps > tau), nbi, ps, ids)) > 0
            assert has == (T > tau)


def test_world_summary_reports_T():
    rng = np.random.default_rng(11)
    C = G.enumerate_configs()
    ix = {c["id"]: i for i, c in enumerate(C)}
    nbg = G.neighbours(C)
    nbi = [np.array([ix[o] for o in nbg[c["id"]]], dtype=int) for c in C]
    n, years = len(C), list(range(2010, 2018))
    sess = np.array([210] + [252] * 7, float)
    inp = P.Inputs([c["id"] for c in C], rng.normal(0.01, 0.05, (n, 8)) * sess / 252, np.full((n, 8), 500.0),
                   np.full((n, 8), 1e5) * sess, np.full((n, 8), 3e5), np.full((n, 8), -0.2), sess, np.full(8, -0.2),
                   np.zeros(8), years)
    s = P.world_summary(inp, nbi, [G.complexity(c) for c in C])
    assert "T" in s and (not np.isfinite(s["T"]) or s["T"] <= s["best_ps"] + 1e-12)


def _cfg(**kw):
    c = dict(kind="research", hypothesis_id="H018", strategy_id="S018", strategy_version="v1.0",
             strategy_dir="strategies/S018_p3_search", split_scheme="2010", split="IS", start="2010-03-01",
             end="2017-12-31", warmup_start="2009-07-01", cash=100000,
             universe={"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                       "sec_corrections": True},
             costs={"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0},
             portfolio=dict(config.H017_PORTFOLIO), lean_version_id=18131, execution_model="d051",
             benchmarks=["E900-07"], programme="P3", cycle="P3C1", experiment_id="E018-01",
             params=dict(mode="search", slots=10, hold=63, worlds=[dict(name="real")]),
             owner_approval_required="Phase 3 search (P3-CP2)")
    c.update(kw)
    return c


def test_s018_configs_gated():
    experiment.validate(_cfg())
    null = dict(kind="infrastructure", split="AUDIT", params=dict(mode="search", slots=10, hold=63,
                                                                   worlds=[dict(name="null1", seed=1)]))
    experiment.validate(_cfg(**null))
    experiment.validate(_cfg(kind="infrastructure", split="AUDIT",                     # finalist trace (spec section 15)
                             params=dict(mode="search", slots=10, hold=63, worlds=[dict(name="real")], trace=["Cx"])))
    bad = [dict(owner_approval_required=None), dict(end="2018-06-30"), dict(start="2010-01-04"),
           dict(params=dict(mode="search", slots=20, hold=126, worlds=[dict(name="real")])),
           dict(params=dict(mode="search", slots=10, hold=63, worlds=[dict(name="real"), dict(name="n1", seed=1)])),
           dict(params=dict(mode="search", slots=10, hold=63, worlds=[dict(name="n1", seed=1)])),   # null as research
           dict(kind="infrastructure", split="AUDIT"),                                                 # real as infra
           dict(hypothesis_id="H017"), dict(costs={"slippage_bps": 20, "commission_model": "fixed_per_order",
                                                    "commission_per_order": 7.0}),
           dict(kind="infrastructure", split="AUDIT", params=dict(mode="search", slots=10, hold=63,     # trace on a null
                                                                  worlds=[dict(name="n1", seed=1)], trace=["Cx"])),
           dict(params=dict(mode="search", slots=10, hold=63, worlds=[dict(name="real")], trace=["Cx"]))]  # as research
    for b in bad:
        with pytest.raises(experiment.ConfigError):
            experiment.validate(_cfg(**b))


def test_search_configs_frozen_plan():
    import importlib.util
    spec = importlib.util.spec_from_file_location("p3_make", config.REPO_ROOT / "research/phase3/P3_make_search_configs.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cfgs = m.build()
    for c in cfgs:
        experiment.validate(c)
        assert c["owner_approval_required"]
    seeds = [w["seed"] for c in cfgs[:5] for w in c["params"]["worlds"]]
    assert seeds == list(p3spec.NULL_SEEDS)
    assert [w["seed"] for w in cfgs[5]["params"]["worlds"]] == list(p3spec.BLOCK_SEEDS)
    assert all(w["block"] == 63 for w in cfgs[5]["params"]["worlds"])
    assert cfgs[6]["params"]["worlds"] == [dict(name="real")] and cfgs[6]["kind"] == "research"


def test_s018_is_byte_copy_of_verified_engine():
    a = (config.REPO_ROOT / "strategies/S018_p3_search/main.py").read_bytes()
    b = (config.REPO_ROOT / "strategies/X984_p3_engine/main.py").read_bytes()
    assert a == b


def test_null_threshold_frozen_before_real_search():
    """D137: the null calibration is pinned (file hash and tau) and tau is the frozen rule applied to its 500 worlds."""
    import hashlib
    import json
    f = config.REPO_ROOT / p3spec.NULL_RESULT
    assert hashlib.sha256(f.read_bytes()).hexdigest() == p3spec.NULL_RESULT_SHA256
    d = json.loads(f.read_text())
    assert d["spec_sha256"] == p3spec.SPEC_SHA256
    assert len(d["primary"]["T"]) == 500 and d["primary"]["tau"] == p3spec.TAU
    assert p3spec.tau_of(d["primary"]["T"]) == p3spec.TAU
