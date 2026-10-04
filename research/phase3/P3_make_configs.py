"""Phase 3 engine run configs (P3-CP2). Infrastructure only:
  E984-01  fidelity replay of the control books' entry decisions (E982-02, E017-03..07), 2010-03-01 .. 2017-12-31
  E984-02  runtime / memory / output canary: the full Stage-1 configuration set with DUMMY masks and strengths,
           1 identity world + 4 within-date permutation worlds, 2010-03-01 .. 2017-12-31
  E984-03  scaling canary: 1 identity + 99 permutation worlds of dummy configurations
  E984-04  fidelity technical repeat of E984-01 after the fill-reporting fix (same tolerances)
  E984-05  output / batch canary: as E984-03 plus the search-mode output format (per-world summaries, 1,533 lines)
  E984-06  batch-independence canary: the identity world alone (digest of the real masks must equal E984-05's)
           -> FAILED (holdings-dependent subscriptions perturbed the windows); fixed in X984
  E984-07  as E984-05 after the fix;  E984-08  as E984-06 after the fix (digests must be equal)
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
    c = dict(BASE, experiment_id="E984-03",
             params=dict(mode="canary", slots=10, hold=63,
                         worlds=[dict(name="identity")] + [dict(name=f"perm{i}", seed=900 + i) for i in range(1, 100)]),
             description="Phase 3 engine SCALING CANARY: as E984-02 with 1 identity + 99 permutation worlds of DUMMY "
                         "configurations (153,300 virtual books), full search window. Timings, memory, output only.")
    d = dict(a, experiment_id="E984-04",
             description="Phase 3 engine FIDELITY, technical repeat of E984-01 after the reporting fix (fills from "
                         "corporate actions, e.g. delisting closes, are now published with their slice date). Same "
                         "replay, same tolerances (research/phase3/P3_fidelity_tolerances.json, unchanged). "
                         "Infrastructure; no strategy evaluated.")
    e = dict(c, experiment_id="E984-05", params=dict(c["params"], publish_format=True),
             description="Phase 3 engine OUTPUT / BATCH CANARY at the frozen batch size: 1 identity + 99 permutation "
                         "worlds of DUMMY configurations (seeds as E984-03, so identical books are expected), publishing "
                         "every world's summary and the first world's 1,533 per-configuration lines in the exact "
                         "search-mode format (output-size test). Timings, memory and output only.")
    f = dict(b, experiment_id="E984-06", params=dict(mode="canary", slots=10, hold=63, worlds=[dict(name="identity")]),
             description="Phase 3 engine BATCH-INDEPENDENCE CANARY: the identity world of DUMMY configurations alone "
                         "(subscriptions then differ from E984-05's 100 worlds); the digest of the real masks and the "
                         "dummy books must equal E984-05's. Timings, counts and digests only.")
    g = dict(e, experiment_id="E984-07",
             description="Phase 3 engine OUTPUT / BATCH CANARY after the batch-independence fix (subscriptions and "
                         "price windows no longer depend on holdings; history without fill-forward): 1 identity + 99 "
                         "permutation worlds of DUMMY configurations with the search-mode output format. Timings, "
                         "memory, output and the digest of the real masks only.")
    h = dict(f, experiment_id="E984-08",
             description="Phase 3 engine BATCH-INDEPENDENCE CANARY after the fix: the identity world alone; the digest "
                         "of the real masks and the dummy books must equal E984-07's.")
    return [a, b, c, d, e, f, g, h]


def main():
    cfgs = build()
    cfgs = [c for c in cfgs if not (Path("experiments") / c["experiment_id"] / "config.json").exists()]
    for c in cfgs:
        experiment.validate(c)
    for c in cfgs:
        d = Path("experiments") / c["experiment_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
        print("wrote", d)


if __name__ == "__main__":
    main()
