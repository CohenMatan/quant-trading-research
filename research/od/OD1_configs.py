"""OD-1 (owner D308): write the run configuration of the ONE outcome-study run E808-01 (E808-02 only after a
documented infrastructure failure).

    PYTHONPATH=src python research/od/OD1_configs.py E808-01
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import experiment, od1 as P  # noqa: E402

APPROVAL = ("D308 owner direction 2026-10-24: outcome-driven discovery on the exposed 2010-2021 development data "
            "(narrow exception to FA-CP1), exploratory only; no 1999-2009, Holdout sealed, no purchases; aggregates only")


def build(eid):
    cfg = dict(experiment_id=eid, kind="infrastructure", hypothesis_id=None, strategy_id="X808", strategy_version="v1.0",
               strategy_dir="strategies/X808_od1_outcomes", split_scheme="2010", split="AUDIT",
               start="2010-01-04", end="2021-12-31", cash=100000,
               universe=dict(min_market_cap=2e9, min_price=5.0, min_avg_dollar_volume=5e6, adv_days=20),
               costs=dict(slippage_bps=10, commission_model="fixed_per_order", commission_per_order=7.0,
                          note="D039: $7 per executed buy or sell order; no order is placed in this run"),
               portfolio=dict(max_position_weight=0.1, cash_buffer=0.02, min_position_usd=5000, max_positions=15,
                              buy_funding="settled_cash_only", gap_reserve=0.15),
               lean_version_id=18203, execution_model="d051", benchmarks=[], programme=P.PROGRAMME, cycle="OD1",
               stall_minutes=300, params=P.run_params(), owner_approval_required=APPROVAL,
               lean_version_policy="default_build_digest_verified",
               description="OD-1 outcome-driven discovery study (owner D308; research/od/OD1_protocol.md): X808 on "
                           "QuantConnect's default build, 2010-01-04 .. 2021-12-31 without warm-up; UCR-1 repaired "
                           "universe, month-end reviews 2011-01 .. 2021-11; technical features from the Fundamental "
                           "stream, as-filed SEC fundamentals (rr/od1_sec_v1.json); forward outcomes 3/6/12/24 months "
                           "never past 2021-11; aggregates only, 0 orders. EXPLORATORY.")
    experiment.validate(cfg)
    return cfg


if __name__ == "__main__":
    eid = sys.argv[1]
    d = ROOT / "experiments" / eid
    if (d / "result.json").exists():
        raise SystemExit(f"{eid} already ran")
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(build(eid), indent=1) + "\n")
    print(f"wrote experiments/{eid}/config.json")
