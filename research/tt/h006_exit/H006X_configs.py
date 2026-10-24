"""H006X (owner D304): write the run configurations.

    PYTHONPATH=src python research/tt/h006_exit/H006X_configs.py E006-04|E006-05|E900-08   (retries E006-06 / E006-07 /
    E900-09 only after a documented infrastructure failure)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import experiment, h006x as H  # noqa: E402

APPROVAL = ("D304 owner direction 2026-10-24: one H006 exit-policy comparison, Control A (60-session time stop) vs "
            "Experiment B (no time stop), identical otherwise; no grid, no tuning; no 1999-2009, no Holdout; EXPLORATORY "
            "(research/tt/h006_exit/H006X_spec.md flags 1-2)")
COSTS = dict(slippage_bps=10, commission_model="fixed_per_order", commission_per_order=7.0,
             note="D039: $7 per executed buy or sell order; slippage separate")
UNIVERSE = dict(min_market_cap=2e9, min_price=5.0, min_avg_dollar_volume=5e6, adv_days=20)


def build(eid):
    a = H.arm(eid)
    common = dict(experiment_id=eid, split_scheme="2010", start=H.START, end=H.END, cash=100000,
                  universe=UNIVERSE, costs=COSTS, lean_version_id=18201, execution_model="d051",
                  programme=H.PROGRAMME, cycle=H.CYCLE, params=H.run_params(eid), owner_approval_required=APPROVAL,
                  lean_version_policy="default_build_digest_verified", stall_minutes=120)
    if a == H.SPY:
        cfg = dict(common, kind="benchmark", hypothesis_id=None, strategy_id="B900", strategy_version="v1.0",
                   strategy_dir="strategies/B900_spy_buyhold", split="FULL",
                   portfolio=dict(max_position_weight=1.0, cash_buffer=0.02, buy_funding="settled_cash_only",
                                  gap_reserve=0.15), benchmarks=[],
                   description="H006X SPY benchmark (D304): B900 SPY buy-and-hold, dividends reinvested monthly, on "
                               "QuantConnect's default build, 2010-01-04 .. 2021-12-31 (E900-07 = the same on build 18131)")
    else:
        b = a == H.B
        cfg = dict(common, kind="research", hypothesis_id="H006", strategy_id="S006",
                   strategy_version="v1.3" if b else "v1.0", strategy_dir="strategies/S006_breakout", split="DEV",
                   portfolio=dict(max_position_weight=0.1, cash_buffer=0.02, min_position_usd=5000, max_positions=15,
                                  buy_funding="settled_cash_only", gap_reserve=0.15),
                   benchmarks=[H.SPY],
                   description=("H006X Experiment B (D304): H006 v1.0 entry, ranking, chandelier K 3.0 and 10 slots "
                                "WITHOUT the 60-session time stop" if b else
                                "H006X Control A (D304): H006 v1.0 exactly (55-day high, volume >= 1.5x, SMA200, "
                                "chandelier K 3.0, 60-session time stop, 10 slots)")
                               + " on QuantConnect's default build, DEV 2010-01-04 .. 2021-12-31. EXPLORATORY; H006 "
                               "stays REJECTED.")
    experiment.validate(cfg)
    return cfg


def write(eid):
    d = ROOT / "experiments" / eid
    if (d / "result.json").exists():
        raise SystemExit(f"{eid} already ran")
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(build(eid), indent=1) + "\n")
    print(f"wrote experiments/{eid}/config.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    write(sys.argv[1])
