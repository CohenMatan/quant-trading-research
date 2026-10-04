"""Phase 3 engine run configs (P3-CP2). Infrastructure only:
  E984-01  fidelity replay of the control books' entry decisions (E982-02, E017-03..07), 2010-03-01 .. 2017-12-31
  E984-02  runtime / memory / output canary: the full Stage-1 configuration set with DUMMY masks and strengths,
           1 identity world + 4 within-date permutation worlds, 2010-03-01 .. 2017-12-31
The real Stage-1 search and the null calibration (mode "search") are NOT written here: they need the owner's approval
after the frozen Phase 3 specification (P3-CP2).

    PYTHONPATH=src python research/phase3/P3_make_configs.py      (refuses to overwrite)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from qresearch import config, experiment  # noqa: E402

BASE = dict(kind="infrastructure", hypothesis_id=None, strategy_id="X984", strategy_version="v1.0",
            strategy_dir="strategies/X984_p3_engine", split_scheme="2010", split="AUDIT", start="2010-03-01",
            end="2017-12-31", warmup_start="2009-07-01", cash=100000,
            universe={"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                      "sec_corrections": True},
            costs={"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                   "note": "D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)"},
            portfolio=dict(config.H017_PORTFOLIO), lean_version_id=18131, execution_model="d051",
            benchmarks=["E900-07"], programme="P3", cycle="P3C1")


def build():
    a = dict(BASE, experiment_id="E984-01", params=dict(mode="fidelity", slots=10, hold=60),
             description="Phase 3 engine FIDELITY: replay of the entry decisions of the completed control books "
                         "E982-02 and E017-03..07 (decisions <= 2017-12-31) through the shadow engine; compared offline "
                         "with the LEAN results against tolerances declared before the run "
                         "(research/phase3/P3_fidelity_tolerances.json). Infrastructure; no strategy evaluated.")
    b = dict(BASE, experiment_id="E984-02",
             params=dict(mode="canary", slots=10, hold=63,
                         worlds=[dict(name="identity")] + [dict(name=f"perm{i}", seed=900 + i) for i in range(1, 5)]),
             description="Phase 3 engine RUNTIME / MEMORY CANARY: all 1,533 Stage-1 configurations with DUMMY random "
                         "masks and keys (real features computed for timing and discarded), 1 identity + 4 permutation "
                         "worlds, full search window. Publishes timings, memory and output size only.")
    return [a, b]


def main():
    cfgs = build()
    for c in cfgs:
        experiment.validate(c)
        if (Path("experiments") / c["experiment_id"] / "config.json").exists():
            raise SystemExit(f"{c['experiment_id']} exists; refusing to overwrite")
    for c in cfgs:
        d = Path("experiments") / c["experiment_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
        print("wrote", d)


if __name__ == "__main__":
    main()
