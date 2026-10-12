"""P14-CP1 (owner D227): write the ONE H029-A audit config (X802, E802-01) from the pins in qresearch.p14h029a.
Infrastructure / data quality only (aggregates; no returns). Written only when every pin exists.

    PYTHONPATH=src python research/phase14/cp1/P14_CP1_configs.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p14h029a as P  # noqa: E402

APPROVAL = ("H029-A Business Improvement data-feasibility audit (aggregates only, no returns; owner 2026-10-12, D227)")
DESC = ("P14-CP1 (owner D227): H029-A data-feasibility audit (X802 audit mode) on frozen Data v2.1: the eleven "
        "Business Improvement candidate forms F1-F8 computed live from the PIT store at each of the 131 reviews "
        "2011-01 .. 2021-11; coverage, breadth, sector, staleness, update frequency, distributions, pathology, "
        "seasonality, True-TTM feasibility, PIT / revision checks, input-to-input rank correlations (incl. the H024 "
        "features), validity patterns. NO return, IC, wealth or feature-return statistic. Infrastructure. Default build.")


def config():
    return {
        "kind": "infrastructure", "hypothesis_id": "H029", "strategy_id": "X802", "strategy_version": "v1.0",
        "strategy_dir": "strategies/X802_h029a_feasibility_audit", "split_scheme": "2010", "split": "AUDIT",
        "start": "2011-01-03", "end": "2021-12-31", "warmup_start": "2008-07-01", "cash": 100000,
        "universe": {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                     "sec_corrections": False},
        "costs": {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                  "note": "D039: $7 per executed buy or sell order (no order is ever placed by X802)"},
        "portfolio": {"max_position_weight": 0.1, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
                      "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
        "lean_version_id": 18131, "execution_model": "d051", "benchmarks": ["E900-07"], "programme": "P14",
        "cycle": "P14H029A", "experiment_id": P.AUDIT, "stall_minutes": 300,
        "params": dict(mode="audit", spec_sha256=P.SPEC_SHA256,
                       h029a_code_sha256=P.CODE_SHA256["src/qresearch/lean/qr_h029a.py"],
                       data_v21_manifest_sha256=P.DATA_V21_MANIFEST_SHA256),
        "description": DESC, "lean_version_policy": "default_build_digest_verified",
        "owner_approval_required": APPROVAL,
    }


def main():
    assert P.SPEC_SHA256 and all(P.CODE_SHA256.values()), "pins missing"
    cfg = config()
    d = ROOT / "experiments" / cfg["experiment_id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(cfg, indent=1) + "\n")
    print("wrote", cfg["experiment_id"])


if __name__ == "__main__":
    main()
