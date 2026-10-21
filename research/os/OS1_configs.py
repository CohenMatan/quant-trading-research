"""H032 / OS-1 revised (owner D278): write the run configuration of the ONE canary C-OS1.

    PYTHONPATH=src python research/os/OS1_configs.py run      # E807-01
    PYTHONPATH=src python research/os/OS1_configs.py retry    # E807-02, only after a documented infrastructure failure
                                                              # of E807-01
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import experiment, os1 as P  # noqa: E402

APPROVAL = ("OS-CP1 Revision 1 decisions: minimum H032 implementation, H032 frozen before any return, then ONLY the "
            "aggregate-only C-OS1 canary with at most one documented infrastructure retry; no strategy returns, no "
            "R1 / R2, no Holdout (owner 2026-10-21, D278)")
DESC = ("H032 canary C-OS1 (owner D278; research/os/H032_spec.md): X807 on QuantConnect's default build, 2009-05-01 .. "
        "2021-12-31, month-end reviews 2010-01 .. 2021-11. UCR-1 repaired universe; point-in-time identity, SIC, "
        "split-adjusted net share issuance and fiscal-year OCF / same-filing revenue-growth filters from two public "
        "SEC objects; coverage gates G-COV1-3, mechanical start, subperiod lengths; H032 books by name only and their "
        "in-run recomputation. Aggregates only, 0 orders, no returns, no identifiers.")


def build(eid):
    cfg = dict(
        kind="infrastructure", hypothesis_id="H032", strategy_id="X807", strategy_version="v1.0",
        strategy_dir="strategies/X807_os1_canary", split_scheme="2010", split="AUDIT",
        start="2009-05-01", end="2021-12-31", cash=100000,
        universe=dict(min_market_cap=2e9, min_price=5.0, min_avg_dollar_volume=5e6, adv_days=20),
        costs=dict(slippage_bps=10, commission_model="fixed_per_order", commission_per_order=7.0,
                   note="D039: $7 per executed buy or sell order; slippage separate (no order is placed in this run)"),
        portfolio=dict(max_position_weight=0.1, cash_buffer=0.02, min_position_usd=5000, max_positions=15,
                       buy_funding="settled_cash_only", gap_reserve=0.15),
        lean_version_id=18198, execution_model="d051", benchmarks=[], programme=P.PROGRAMME, cycle=P.CYCLE,
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
