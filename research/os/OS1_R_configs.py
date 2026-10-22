"""H032 R1 / R2 (owner D282): write the run configurations.

    PYTHONPATH=src python research/os/OS1_R_configs.py r1          # E033-01
    PYTHONPATH=src python research/os/OS1_R_configs.py r1retry     # E033-02, only after a documented infrastructure failure
    PYTHONPATH=src python research/os/OS1_R_configs.py r2          # E033-03, only if R1 is valid and passes O1-O7 and O9
    PYTHONPATH=src python research/os/OS1_R_configs.py r2retry     # E033-04
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import experiment, os1r as P  # noqa: E402

APPROVAL = ("OS-CP2 approval: minimum H032 trading host, R1 (2012-07-31 start, $100,000, 10 bps, $7) under the frozen "
            "O1-O9 framework with the fidelity pre-gate; R2 at 20 bps only if R1 is valid and passes every gate "
            "evaluable without R2; at most one documented infrastructure retry per run; no Holdout "
            "(owner 2026-10-22, D282)")


def build(eid):
    slip = P.SLIPPAGE_BPS[eid]
    costs = dict(slippage_bps=10, commission_model="fixed_per_order", commission_per_order=7.0,
                 note="D039: $7 per executed buy or sell order; slippage separate (harness and shadow engine)")
    if slip != 10:
        costs["slippage_stress_multiple"] = slip // 10            # R2: 10 bps x 2 = 20 bps (D024 stress convention)
    desc = (f"H032 {'R1' if slip == 10 else 'R2'} (owner D282; research/os/H032_spec.md section 9 and "
            "research/os/H032_R_protocol.md): S033 on QuantConnect's default build; B1 traded in LEAN, controls and a "
            "shadow replay of B1 in the shadow engine; official start 2012-07-31 (frozen start review), history-only "
            f"warm-up from 2009-05-01; $100,000, {slip} bps slippage per side, $7 per order. EXPLORATORY.")
    cfg = dict(
        kind="research", hypothesis_id="H032", strategy_id="S033", strategy_version="v1.0",
        strategy_dir="strategies/S033_h032_os1", split_scheme="2010", split="DEV",
        start=P.START_REVIEW, end="2021-12-31", warmup_start=P.WARMUP_FROM, cash=100000,
        universe=dict(min_market_cap=2e9, min_price=5.0, min_avg_dollar_volume=5e6, adv_days=20),
        costs=costs,
        portfolio=dict(max_position_weight=0.1, cash_buffer=0.02, min_position_usd=5000, max_positions=15,
                       buy_funding="settled_cash_only", gap_reserve=0.15),
        lean_version_id=18200, execution_model="d051", benchmarks=[], programme=P.PROGRAMME, cycle=P.CYCLE,
        experiment_id=eid, stall_minutes=300, params=P.run_params(), description=desc,
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
    m = dict(r1=P.R1, r1retry=P.R1_RETRY, r2=P.R2, r2retry=P.R2_RETRY)
    a = sys.argv[1:]
    if len(a) != 1 or a[0] not in m:
        raise SystemExit(__doc__)
    write(m[a[0]])
