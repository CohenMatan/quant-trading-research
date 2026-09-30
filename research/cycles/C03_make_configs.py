"""Writes the configs of C03's committed runs (CP3e §7, owner-approved; D082/D083), before any C03 run.
Canaries E963-01 and E964-01 run at the infrastructure checkpoint. The 32 C03 runs below are only
written here: none may run before the owner authorises the C03 strategy backtests.

    PYTHONPATH=src python research/cycles/C03_make_configs.py      (refuses to overwrite a config)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from qresearch import config, experiment  # noqa: E402

IS = dict(split_scheme="2010", split="IS", start="2010-01-04", end="2017-12-29")
BASE = dict(
    cash=100000,
    universe={"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20},
    costs={"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
           "note": "D039: $7 per executed buy or sell order; slippage separate"},
    portfolio=dict(config.RESEARCH_PORTFOLIOS["d051"]), lean_version_id=18131, execution_model="d051",
    benchmarks=["E900-07", "E901-07"])
H012_V = {"v1.0": dict(rv_short=21, cadence="monthly"), "v1.1": dict(rv_short=63, cadence="monthly"),
          "v1.2": dict(rv_short=21, cadence="weekly")}
H013_V = {"v1.0": dict(q=0.20, stat="max"), "v1.1": dict(q=0.10, stat="max"), "v1.2": dict(q=0.20, stat="max5")}
PLAN = "Pre-declared in docs/checkpoints/CP3e_C03_final_plan.md §7; methodology research/cycles/C03_statistical_spec.md (D082)."


def h012(eid, kind, version, mode, cash=100000, slots=15, **extra):
    p = dict(H012_V[version], band=0.10, slots=slots, mode=mode)
    c = dict(experiment_id=eid, kind=kind, hypothesis_id="H012", strategy_id="S012", strategy_version=version,
             strategy_dir="strategies/S012_vol_managed", **IS, **BASE, params=p, cycle="C03")
    c["cash"] = cash
    if slots != 15:
        c["portfolio"] = dict(c["portfolio"], max_positions=slots)
    c.update(extra)
    return c


def h013(eid, kind, version, seed, cash=100000, slots=15, **extra):
    p = dict(H013_V[version], seed=seed, slots=slots, hold=60)
    c = dict(experiment_id=eid, kind=kind, hypothesis_id="H013", strategy_id="S013", strategy_version=version,
             strategy_dir="strategies/S013_lottery_avoid", **IS, **BASE, params=p, cycle="C03")
    c["cash"] = cash
    if slots != 15:
        c["portfolio"] = dict(c["portfolio"], max_positions=slots)
    c.update(extra)
    return c


def null(eid, seed, cash, slots, desc):
    c = dict(experiment_id=eid, kind="infrastructure", hypothesis_id=None, strategy_id="X962", strategy_version="v1.0",
             strategy_dir="strategies/X962_random_pick", split_scheme="2010", split="AUDIT",
             start="2010-01-04", end="2017-12-29", **BASE, params=dict(slots=slots, hold=60, seed=seed), cycle="C03",
             description=desc + " Not a trial.")
    c["cash"] = cash
    if slots != 15:
        c["portfolio"] = dict(c["portfolio"], max_positions=slots)
    return c


def build():
    out = []
    out.append(dict(experiment_id="E963-01", kind="infrastructure", hypothesis_id=None, strategy_id="X963",
                    strategy_version="v1.0", strategy_dir="strategies/X963_h012_canary", split_scheme="2010",
                    split="AUDIT", start="2010-01-04", end="2011-12-30", **BASE,
                    params=dict(rv_short=10, cadence="weekly", band=0.10, slots=15, mode="timing"), cycle="C03",
                    description="C03 H012 infrastructure canary: unchanged S012 code with NON-candidate parameters "
                                "(RV(10), weekly, 2010-2011). Verification; not a trial."))
    out.append(dict(experiment_id="E964-01", kind="infrastructure", hypothesis_id=None, strategy_id="X964",
                    strategy_version="v1.0", strategy_dir="strategies/X964_h013_canary", split_scheme="2010",
                    split="AUDIT", start="2010-01-04", end="2017-12-29", **BASE,
                    params=dict(q=0.0, stat="max", seed=1, slots=15, hold=60), cycle="C03", reproduces="E962-22",
                    description="C03 H013 infrastructure canary: unchanged S013 code with the NON-candidate q = 0; "
                                "fills must equal E962-22's; audits exclusion at q = 0.25. Verification; not a trial."))
    for i, v in enumerate(H012_V):
        out.append(h012(f"E012-0{i + 1}", "research", v, "timing",
                        description=f"C03 H012 S012 {v} selection candidate (D069/D082) on IS. {PLAN}"))
    out.append(h012("E012-04", "benchmark", "v1.0", "control_a", control_of=["E012-01", "E012-02", "E012-03"],
                    description=f"C03 H012 Control A (e = 1 always; same basket and execution). Benchmark, not a trial. {PLAN}"))
    for i, v in enumerate(H012_V):
        out.append(h012(f"E012-0{5 + i}", "benchmark", v, "control_b", control_of=f"E012-0{i + 1}",
                        description=f"C03 H012 Control B for {v} (mean of the variation's previous 12 targets). "
                                    f"Benchmark, not a trial. {PLAN}"))
    out.append(h012("E012-08", "sizing", "v1.0", "timing", cash=200000, account_size_test_of="E012-01",
                    sensitivity="S1", description=f"C03 S1 ($200K, 15 positions) of E012-01. Diagnostic, not a trial. {PLAN}"))
    out.append(h012("E012-09", "sizing", "v1.0", "control_a", cash=200000, account_size_test_of="E012-04",
                    sensitivity="S1", description=f"C03 S1 ($200K) of Control A E012-04. Diagnostic. {PLAN}"))
    out.append(h012("E012-10", "sizing", "v1.0", "timing", cash=200000, slots=20, account_size_test_of="E012-01",
                    sensitivity="S2", construction_variant="S2",
                    description=f"C03 S2 ($200K, 20 positions) of E012-01. Diagnostic, not a trial. {PLAN}"))
    out.append(h012("E012-11", "sizing", "v1.0", "control_a", cash=200000, slots=20, account_size_test_of="E012-04",
                    sensitivity="S2", construction_variant="S2",
                    description=f"C03 S2 ($200K, 20 positions) of Control A E012-04. Diagnostic. {PLAN}"))
    n = 1
    for v in H013_V:
        for seed in (1, 2, 3):
            out.append(h013(f"E013-{n:02d}", "research", v, seed, replicate_param="seed",
                            paired_null=f"E962-{21 + seed}",
                            description=f"C03 H013 S013 {v} seed {seed} (one candidate per variation; seeds are "
                                        f"replicates, D082) on IS, paired with null E962-{21 + seed}. {PLAN}"))
            n += 1
    for seed in (1, 2, 3):
        out.append(h013(f"E013-{9 + seed}", "sizing", "v1.0", seed, cash=200000, account_size_test_of=f"E013-0{seed}",
                        sensitivity="S1", paired_null=f"E962-{24 + seed}",
                        description=f"C03 S1 ($200K, 15 positions) of E013-0{seed}. Diagnostic, not a trial. {PLAN}"))
        out.append(null(f"E962-{24 + seed}", seed, 200000, 15, f"C03 S1 null ($200K, 15 slots, hold 60, seed {seed})."))
    for seed in (1, 2, 3):
        out.append(h013(f"E013-{12 + seed}", "sizing", "v1.0", seed, cash=200000, slots=20,
                        account_size_test_of=f"E013-0{seed}", sensitivity="S2", construction_variant="S2",
                        paired_null=f"E962-{27 + seed}",
                        description=f"C03 S2 ($200K, 20 positions) of E013-0{seed}. Diagnostic, not a trial. {PLAN}"))
        out.append(null(f"E962-{27 + seed}", seed, 200000, 20, f"C03 S2 null ($200K, 20 slots, hold 60, seed {seed})."))
    return out


def main():
    cfgs = build()
    for c in cfgs:
        experiment.validate(c)
    for c in cfgs:
        d = config.EXPERIMENTS_DIR / c["experiment_id"]
        if (d / "config.json").exists():
            raise SystemExit(f"{c['experiment_id']} exists; refusing to overwrite")
    for c in cfgs:
        d = config.EXPERIMENTS_DIR / c["experiment_id"]
        d.mkdir(parents=True)
        (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
    print(len(cfgs), "configs:", ", ".join(c["experiment_id"] for c in cfgs))


if __name__ == "__main__":
    main()
