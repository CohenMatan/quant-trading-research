"""SCA-1 (owner D267): write the run configuration of the ONE SEC classification audit run.

    PYTHONPATH=src python research/rr/sec_classification/SCA_configs.py run      # E805-01
    PYTHONPATH=src python research/rr/sec_classification/SCA_configs.py retry    # E805-02, only after a documented
                                                                                 # infrastructure failure of E805-01
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import experiment, rr_sca as P  # noqa: E402

APPROVAL = ("RR4 review, UR-1 option A: narrow free SEC classification assessment, ONE aggregate-only run, at most one "
            "documented infrastructure retry, no returns, no Platform Data export, no repair, no Holdout (owner "
            "2026-10-20, D267)")
DESC = ("SCA-1 SEC classification audit (owner D267; research/rr/sec_classification/SCA_protocol.md): X805 on "
        "QuantConnect's default build, 2009-11-02 .. 2021-12-31, month-end points 2010-01 .. 2021-11. Public SEC "
        "registrants (plain JSON, Object Store) matched in-cloud by dated ticker evidence / share fingerprint to the "
        "vendor universe: matched / confirmed missing / possible missing / unresolved, gaps, survivorship bounds, "
        "frozen verdict. Aggregates only, 0 orders, no returns, no identifiers. Infrastructure.")


def build(eid):
    cfg = dict(
        kind="infrastructure", hypothesis_id=None, strategy_id="X805", strategy_version="v1.0",
        strategy_dir="strategies/X805_sec_classification", split_scheme="2010", split="AUDIT",
        start="2009-11-02", end="2021-12-31", cash=100000,
        universe=dict(min_market_cap=2e9, min_price=5.0, min_avg_dollar_volume=5e6, adv_days=20),
        costs=dict(slippage_bps=10, commission_model="fixed_per_order", commission_per_order=7.0,
                   note="D039: $7 per executed buy or sell order; slippage separate (no order is placed in this run)"),
        portfolio=dict(max_position_weight=0.1, cash_buffer=0.02, min_position_usd=5000, max_positions=15,
                       buy_funding="settled_cash_only", gap_reserve=0.15),
        lean_version_id=18194, execution_model="d051", benchmarks=[], programme=P.PROGRAMME, cycle=P.CYCLE,
        experiment_id=eid, stall_minutes=240, params=P.run_params(), description=DESC,
        owner_approval_required=APPROVAL, lean_version_policy="default_build_digest_verified")
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
    a = sys.argv[1:]
    if a == ["run"]:
        write(P.RUN)
    elif a == ["retry"]:
        write(P.RETRY)
    else:
        raise SystemExit(__doc__)
