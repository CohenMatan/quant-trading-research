"""Phase 3 search run configs (P3_spec.md §19), written at P3-CP2 BEFORE any search or null run. Every config carries
owner_approval_required: the runner refuses to start them without --owner-approved <decision id>.

  E018-01 .. E018-05  primary null worlds, within-date permutation, seeds 1..500 in 5 batches of 100 consecutive seeds
  E018-06             secondary diagnostic null worlds, 63-session block permutation, seeds 1001..1100
  E018-07             the real world (identity mapping): all 1,533 configurations; started only after the null threshold
                      tau has been computed from E018-01..05 and committed (research/phase3/P3_null_result.json)

Batch size 100 = the scale verified by the runtime / output canaries (E984-03, E984-05). A world's result does not
depend on its batch (independent seeded book sets; verified across E984-02 / E984-03 / E984-05).

    PYTHONPATH=src python research/phase3/P3_make_search_configs.py      (refuses to overwrite)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from qresearch import config, experiment, p3spec  # noqa: E402

APPROVAL = "Phase 3 search and null calibration (P3_spec.md; explicit owner approval after P3-CP2)"
BASE = dict(hypothesis_id="H018", strategy_id="S018", strategy_version="v1.0", strategy_dir="strategies/S018_p3_search",
            split_scheme="2010", start=p3spec.SEARCH[0], end=p3spec.SEARCH[1], warmup_start=p3spec.WARMUP_START,
            cash=p3spec.CASH,
            universe={"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                      "sec_corrections": True},
            costs={"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                   "note": "D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)"},
            portfolio=dict(config.H017_PORTFOLIO), lean_version_id=18131, execution_model="d051",
            benchmarks=["E900-07"], programme="P3", cycle="P3C1", owner_approval_required=APPROVAL)
PARAMS = dict(mode="search", slots=p3spec.SLOTS, hold=p3spec.HOLD)


def build():
    out = []
    seeds = p3spec.NULL_SEEDS
    for k in range(5):
        batch = seeds[100 * k:100 * (k + 1)]
        out.append(dict(BASE, kind="infrastructure", split="AUDIT", experiment_id=f"E018-{k + 1:02d}",
                        params=dict(PARAMS, worlds=[dict(name=f"null{s}", seed=s) for s in batch]),
                        description=f"Phase 3 PRIMARY NULL batch {k + 1}/5: the entire frozen search on within-date "
                                    f"permutation worlds, seeds {batch[0]}..{batch[-1]} (P3_spec.md section 12)"))
    out.append(dict(BASE, kind="infrastructure", split="AUDIT", experiment_id="E018-06",
                    params=dict(PARAMS, worlds=[dict(name=f"block{s}", seed=s, block=p3spec.BLOCK)
                                                for s in p3spec.BLOCK_SEEDS]),
                    description="Phase 3 SECONDARY (diagnostic) NULL: 63-session block permutation worlds, seeds "
                                "1001..1100 (P3_spec.md section 12.2); never a gate"))
    out.append(dict(BASE, kind="research", split="IS", experiment_id="E018-07",
                    params=dict(PARAMS, worlds=[dict(name="real")]),
                    description="Phase 3 REAL SEARCH: all 1,533 frozen configurations on real signals, 2010-03-01 .. "
                                "2017-12-31. Started only after tau is committed (P3_null_result.json)."))
    return out


def main():
    cfgs = [c for c in build() if not (Path("experiments") / c["experiment_id"] / "config.json").exists()]
    for c in cfgs:
        experiment.validate(c)
    for c in cfgs:
        d = Path("experiments") / c["experiment_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
        print("wrote", d)


if __name__ == "__main__":
    main()
