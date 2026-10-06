"""D082 (frozen 2026-09-30, before any C03 result): C03 trial accounting and Deflated Sharpe.
Clarification A = the counts; Clarification B = the DSR calculation. See research/cycles/C03_statistical_spec.md."""
import json
import math

import numpy as np
import pandas as pd
import pytest
from scipy.stats import kurtosis, norm, skew

from qresearch import c03stats, config, registry, stats

IS = dict(split="IS", start="2010-01-04", end="2017-12-29")
VAL = dict(split="VAL", start="2018-01-02", end="2021-12-31")


def _cfg(h, s, v, params, **kw):
    c = dict(hypothesis_id=h, strategy_id=s, strategy_version=v, params=params, costs={"slippage_bps": 10}, **IS)
    c.update(kw)
    return c


def _write(tmp_path, runs, annotations=()):
    """runs: [(experiment_id, kind, cfg or None, sharpe)] in registry order."""
    exp, p = tmp_path / "experiments", tmp_path / "INDEX.csv"
    for eid, kind, cfg, sr in runs:
        if cfg is not None and not (exp / eid).exists():
            (exp / eid).mkdir(parents=True)
            (exp / eid / "config.json").write_text(json.dumps(cfg))
        registry.append(dict(experiment_id=eid, run_type="original", kind=kind, status="completed",
                             sharpe="" if sr is None else sr), p)
    for eid, run_type, status in annotations:
        registry.append(dict(experiment_id=eid, run_type=run_type, kind="research", status=status), p)
    return p, exp


def h013(v, seed, **kw):
    return _cfg("H013", "S013", v, {"q": 0.2 if v != "v1.1" else 0.1, "seed": seed, "slots": 15, "hold": 60},
                replicate_param="seed", **kw)


def c03_like_registry(tmp_path):
    """A miniature of C03: 2 earlier candidates, H012 x 3, H013 x 3 variations x 3 seeds, controls,
    nulls, sizing, a canary, a technical repeat, a not-started run, a recovery row, then the
    conditional stages (2x-slippage items, robustness, Validation incl. every H013 seed)."""
    runs = [("E001-01", "research", _cfg("H001", "S001", "v1.0", {"a": 1}), 0.5),
            ("E002-01", "research", _cfg("H002", "S002", "v1.0", {"a": 1}), 0.9),
            ("E963-01", "infrastructure", None, None)]
    for i, v in enumerate(("v1.0", "v1.1", "v1.2")):
        runs.append((f"E012-0{i + 1}", "research", _cfg("H012", "S012", v, {"rv": 21 + i}), 1.0 + 0.1 * i))
    runs += [("E012-04", "benchmark", None, None), ("E012-05", "benchmark", None, None)]      # controls
    n = 1
    for v in ("v1.0", "v1.1", "v1.2"):
        for seed in (1, 2, 3):
            runs.append((f"E013-{n:02d}", "research", h013(v, seed), 0.6 + 0.1 * seed))
            n += 1
    runs += [("E013-10", "research", h013("v1.0", 2), 0.8),            # technical repeat of v1.0 seed 2
             ("E013-11", "sizing", None, None), ("E962-25", "infrastructure", None, None),
             ("E013-12", "research", h013("v1.2", 1, end="2017-12-28"), 0.7)]   # not started (annotated)
    stress = {"slippage_bps": 10, "slippage_stress_multiple": 2}
    runs += [("E012-06", "research", _cfg("H012", "S012", "v1.0", {"rv": 21}, costs=stress), 0.9)]
    for k, seed in enumerate((1, 2, 3)):
        runs.append((f"E013-{13 + k}", "research", h013("v1.0", seed, costs=stress), 0.6))
    runs += [("E012-07", "research", _cfg("H012", "S012", "v1.0", {"rv": 15}, robustness_of="E012-01"), 0.9),
             ("E012-08", "research", _cfg("H012", "S012", "v1.0", {"rv": 21}, **VAL), 0.5)]
    for k, seed in enumerate((1, 2, 3)):
        runs.append((f"E013-{16 + k}", "research", h013("v1.0", seed, **VAL), 0.5))
    ann = [("E013-12", "annotation", registry.NOT_STARTED), ("E012-01", "recovery", "completed")]
    return _write(tmp_path, runs, ann)


def test_clarification_a_counts(tmp_path):
    p, exp = c03_like_registry(tmp_path)
    a = registry.trial_accounting(p, exp)
    # S: 2 earlier + 3 H012 + 3 H013 variations; P: seeds 2 and 3 of each H013 variation
    assert a["selection_trials"] == 8 and a["replicate_runs"] == 6
    # R: H012 2x slippage + 1 plateau; H013 2x slippage per seed (each seed its own configuration)
    assert a["robustness_runs"] == 5
    # V: H012 once; H013 every seed separately
    assert a["validation_runs"] == 4
    assert a["technical_repeats"] == 1 and a["not_started"] == 1
    assert a["verification_and_benchmark_runs"] == 5            # canary, 2 controls, sizing, null
    assert registry.dsr_trial_count(p, exp) == dict(official=8, conservative=8 + 6 + 5 + 4)
    assert a["selection_members"]["E013-01"] == ["E013-01", "E013-10", "E013-03"]   # latest valid run per seed
    assert a["replicate_of"]["E013-02"] == "E013-01"


def test_first_started_seed_is_the_candidate_and_order_does_not_change_counts(tmp_path):
    runs = [("E013-02", "research", h013("v1.0", 2), 0.7), ("E013-01", "research", h013("v1.0", 1), 0.6),
            ("E013-03", "research", h013("v1.0", 3), 0.8)]
    p, exp = _write(tmp_path, runs)
    a = registry.trial_accounting(p, exp)
    assert a["by_category"]["selection"] == ["E013-02"] and a["replicate_runs"] == 2


def test_not_started_seed_does_not_become_the_candidate(tmp_path):
    runs = [("E013-01", "research", h013("v1.0", 1), None), ("E013-04", "research", h013("v1.0", 1), 0.6),
            ("E013-02", "research", h013("v1.0", 2), 0.7)]
    p, exp = _write(tmp_path, runs, [("E013-01", "annotation", registry.NOT_STARTED)])
    a = registry.trial_accounting(p, exp)
    assert a["by_category"]["selection"] == ["E013-04"] and a["replicate_runs"] == 1


def test_failed_started_runs_count(tmp_path):
    """D069 unchanged: a run that started counts whatever its outcome; only not_started is excluded."""
    p, exp = _write(tmp_path, [("E013-01", "research", h013("v1.0", 1), None)])
    registry.append(dict(experiment_id="E013-01", run_type="annotation", kind="research", status="failed"), p)
    assert registry.dsr_trial_count(p, exp)["official"] == 1


def test_replicate_param_must_be_a_parameter(tmp_path):
    bad = dict(h013("v1.0", 1), replicate_param="nonexistent")
    p, exp = _write(tmp_path, [("E013-01", "research", bad, 0.5)])
    with pytest.raises(registry.RegistryError):
        registry.trial_accounting(p, exp)


def test_var_sr_uses_the_seed_mean_per_candidate(tmp_path):
    p, exp = c03_like_registry(tmp_path)
    snap = c03stats.snapshot(p, exp, retired=set())
    d = 1 / math.sqrt(252)
    h013_mean = np.mean([0.7, 0.8, 0.9])            # v1.0: seed 2's latest run is the repeat (0.8)
    others = [np.mean([0.7, 0.8, 0.9])] * 2          # v1.1 and v1.2: seeds at 0.7, 0.8, 0.9
    vals = np.array([0.5, 0.9, 1.0, 1.1, 1.2, h013_mean] + others) * d
    assert snap["n_sharpes"] == 8
    assert snap["var_sr"] == pytest.approx(np.var(vals, ddof=1), rel=1e-12)
    assert snap["official"] == 8 and snap["conservative"] == 23
    with pytest.raises(c03stats.SpecError):
        c03stats.snapshot(p, exp, retired=set(), expect_official=40)


def test_real_registry_before_c03():
    """Pins the frozen pre-C03 counts: official 37, conservative 64 (no replicates); C03 adds on top."""
    a = registry.trial_accounting(config.INDEX_CSV, config.EXPERIMENTS_DIR)

    def pre(ids):
        return [e for e in ids if json.loads((config.EXPERIMENTS_DIR / e / "config.json").read_text())
                .get("cycle") != "C03" and not str(json.loads((config.EXPERIMENTS_DIR / e / "config.json")
                .read_text()).get("cycle", "")).startswith(("P2", "P3", "P4", "P5", "P6"))]   # C03 and every Phase 2-6 cycle add on top
    cats = a["by_category"]
    assert [len(pre(cats[c])) for c in ("selection", "replicate", "robustness", "validation")] == [37, 0, 26, 1]
    assert c03stats.PRE_C03 == dict(official=37, conservative=64)


# ---------------------------------------------------------------- Clarification B: the DSR itself

def _eq(values, start):
    idx = pd.bdate_range(start, periods=len(values)).strftime("%Y-%m-%d")
    return pd.Series(values, index=idx, dtype=float)


def test_is_and_val_are_concatenated_without_a_bridging_return():
    r = c03stats.book_returns(_eq([100, 110, 99], "2017-12-27"), _eq([100, 105], "2018-01-02"))
    assert r == pytest.approx([0.10, -0.10, 0.05])
    with pytest.raises(c03stats.SpecError):
        c03stats.book_returns(_eq([100, 110], "2017-12-28"), _eq([100, 105], "2017-12-29"))


def _reference_dsr(r, n, var_sr):
    """Independent re-implementation of the frozen formula (scipy moments, bias-corrected)."""
    r = np.asarray(r, float)
    sr = r.mean() / r.std(ddof=1)
    g = 0.5772156649015329
    star = math.sqrt(var_sr) * ((1 - g) * norm.ppf(1 - 1 / n) + g * norm.ppf(1 - 1 / (n * math.e)))
    sk, ku = skew(r, bias=False), kurtosis(r, bias=False) + 3
    return norm.cdf((sr - star) * math.sqrt(len(r) - 1) / math.sqrt(1 - sk * sr + (ku - 1) / 4 * sr ** 2))


def test_dsr_matches_an_independent_implementation():
    rng = np.random.default_rng(7)
    r = rng.standard_t(5, 3020) * 0.009 + 0.0008
    for n in (43, 76, 104):
        assert c03stats.dsr_at(r, n, 0.001001)["dsr"] == pytest.approx(_reference_dsr(r, n, 0.001001), abs=1e-12)


def test_dsr_falls_as_n_rises_and_both_counts_must_pass():
    rng = np.random.default_rng(3)
    base = rng.standard_normal(3020) * 0.01
    target = None
    for mu in np.linspace(0.0005, 0.0015, 201):          # a series that passes at 43 but not at 200
        r = base - base.mean() + mu
        if c03stats.dsr_at(r, 43, 0.001001)["ok"] and not c03stats.dsr_at(r, 200, 0.001001)["ok"]:
            target = r
            break
    assert target is not None
    ds = [c03stats.dsr_at(target, n, 0.001001)["dsr"] for n in (2, 10, 43, 76, 200)]
    assert all(a > b for a, b in zip(ds, ds[1:]))
    snap = dict(official=43, conservative=200, var_sr=0.001001)
    half = len(target) * 2 // 3
    res = c03stats.evaluate_book("x", _eq(np.r_[100, 100 * np.cumprod(1 + target[:half])], "2010-01-04"),
                                 _eq(np.r_[100, 100 * np.cumprod(1 + target[half:])], "2018-01-02"), snap)
    assert res["official"]["ok"] and not res["conservative"]["ok"] and not res["ok"]
    assert res["combined"]["n_obs"] == len(target)
    assert set(res["diagnostics_not_gates"]) == {"is_only", "val_only", "sensitivity_n43"}


def test_threshold_is_inclusive_and_nan_fails(monkeypatch):
    monkeypatch.setattr(stats, "deflated_sharpe", lambda r, n, v: 0.90)
    assert c03stats.dsr_at(np.ones(5), 43, 0.001)["ok"]
    monkeypatch.setattr(stats, "deflated_sharpe", lambda r, n, v: 0.8999999)
    assert not c03stats.dsr_at(np.ones(5), 43, 0.001)["ok"]
    monkeypatch.setattr(stats, "deflated_sharpe", lambda r, n, v: float("nan"))
    assert not c03stats.dsr_at(np.ones(5), 43, 0.001)["ok"]


def test_every_seed_must_pass():
    ok, bad = dict(ok=True), dict(ok=False)
    assert c03stats.hypothesis_passes([ok, ok, ok])
    assert not c03stats.hypothesis_passes([ok, bad, ok])
    assert not c03stats.hypothesis_passes([])


def test_spec_is_frozen():
    """The written specification may not change after approval (D082)."""
    assert c03stats.spec_hash() == c03stats.SPEC_SHA256
    assert c03stats.THRESHOLD == 0.90


def test_committed_c03_runs_give_40_and_73(tmp_path):
    """Amendment 1 (D087): registering the committed H013 runs (21 research-budget configs, H012's withdrawn
    configs excluded) on top of the pre-C03 registry gives official N = 40 and conservative N = 73; the
    canaries, nulls and sizing runs add nothing."""
    import shutil
    from qresearch import experiment
    gone = experiment.withdrawn()
    ids = [p.parent.name for p in sorted(config.EXPERIMENTS_DIR.glob("E*/config.json"))
           if json.loads(p.read_text()).get("cycle") == "C03" and p.parent.name not in gone]
    cfgs = {e: json.loads((config.EXPERIMENTS_DIR / e / "config.json").read_text()) for e in ids}
    kinds = [c["kind"] for c in cfgs.values() if not c.get("technical_repeat_of")]
    assert kinds.count("research") == 9 and not [e for e in ids if e.startswith("E012")]
    # technical repeats (e.g. E013-16 of E013-06) are registered too and must not change the counts
    p = tmp_path / "INDEX.csv"
    p2 = {p.parent.name for p in config.EXPERIMENTS_DIR.glob("E*/config.json")
          if json.loads(p.read_text()).get("programme") in ("P2", "P3", "P4", "P5", "P6")}  # Phases 2-6 count on top (D094)
    rows = [r for r in registry.read(config.INDEX_CSV) if r["experiment_id"] not in set(ids) | p2]
    shutil.copy(config.INDEX_CSV, p)
    p.write_text(p.read_text().splitlines()[0] + "\n")
    for r in rows:
        registry.append(r, p)
    assert registry.dsr_trial_count(p, config.EXPERIMENTS_DIR) == dict(official=37, conservative=64)
    before = registry.trial_accounting(p, config.EXPERIMENTS_DIR)["verification_and_benchmark_runs"]
    for e in ids:
        c = json.loads((config.EXPERIMENTS_DIR / e / "config.json").read_text())
        registry.append(dict(experiment_id=e, run_type="original", kind=c["kind"], status="completed"), p)
    assert registry.dsr_trial_count(p, config.EXPERIMENTS_DIR) == dict(official=40, conservative=73)
    a = registry.trial_accounting(p, config.EXPERIMENTS_DIR)
    n_rep = sum(1 for c in cfgs.values() if c.get("technical_repeat_of"))
    assert a["replicate_runs"] == 6 and a["verification_and_benchmark_runs"] - before == len(ids) - 9 - n_rep


# ---------------------------------------------------------------- Amendment 1 (D087)
def test_amendment_1_is_recorded_and_frozen():
    """H012 removed before any C03 backtest: official N = 40, N = 43 kept as a reported sensitivity.
    The original frozen specification is unchanged (its own hash test above still holds)."""
    assert c03stats.OFFICIAL_N_C03 == 40 and c03stats.SENSITIVITY_N_C03 == 43
    assert c03stats.amendment_hashes() == c03stats.AMENDMENTS
    text = (config.REPO_ROOT / "research/cycles/C03_statistical_spec_amendment_1.md").read_text()
    assert "N = 40" in text or "= 40" in text


def test_sensitivity_n43_is_reported_but_never_gates():
    rng = np.random.default_rng(5)
    r = rng.standard_normal(3020) * 0.01 + 0.0012
    half = 2012
    snap = dict(official=40, conservative=73, var_sr=0.001001)
    res = c03stats.evaluate_book("x", _eq(np.r_[100, 100 * np.cumprod(1 + r[:half])], "2010-01-04"),
                                 _eq(np.r_[100, 100 * np.cumprod(1 + r[half:])], "2018-01-02"), snap)
    s43 = res["diagnostics_not_gates"]["sensitivity_n43"]
    assert s43["n_trials"] == 43 and "sensitivity_n43" not in res and set(res) >= {"official", "conservative", "ok"}
    assert res["ok"] == (res["official"]["ok"] and res["conservative"]["ok"])


def test_withdrawn_h012_configs_can_never_run():
    from qresearch import experiment, run
    w = experiment.withdrawn()
    assert sorted(w) == [f"E012-{i:02d}" for i in range(1, 12)]
    assert not [r for r in registry.read() if r["experiment_id"] in w]      # none ever ran
    with pytest.raises(SystemExit, match="withdrawn"):
        run.run("E012-01")
