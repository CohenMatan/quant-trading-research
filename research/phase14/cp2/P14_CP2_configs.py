"""P14-CP2 (owner D229): write the ONE Data v3 audit config (X803, E803-01) from the pins in qresearch.p14datav3.
Infrastructure / data quality only (aggregates; no returns). Written only when every pin exists.

    PYTHONPATH=src python research/phase14/cp2/P14_CP2_configs.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p14datav3 as P  # noqa: E402

APPROVAL = ("Data v3 targeted PIT / restatement hardening audit (aggregates only, no returns; owner 2026-10-12, D229)")
DESC = ("P14-CP2 (owner D229): Data v3 audit (X803 audit mode) on frozen Data v2.1 + the guard-v3 table: guard-v3 "
        "provenance / blocks of every fed vendor version, the H029 v3 view, the six H029 signals live at each of the "
        "131 reviews 2011-01 .. 2021-11 (U_H029 coverage, >= 5 of 6), stratified SEC validation (rank materiality), "
        "F7 split comparability, PIT checks, v2.1 differences, per-review panel digests. NO return, IC, wealth or "
        "feature-return statistic. Infrastructure. Default build.")


def config():
    return {
        "kind": "infrastructure", "hypothesis_id": "H029", "strategy_id": "X803", "strategy_version": "v1.0",
        "strategy_dir": "strategies/X803_data_v3_audit", "split_scheme": "2010", "split": "AUDIT",
        "start": "2011-01-03", "end": "2021-12-31", "warmup_start": "2008-07-01", "cash": 100000,
        "universe": {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                     "sec_corrections": False},
        "costs": {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                  "note": "D039: $7 per executed buy or sell order (no order is ever placed by X803)"},
        "portfolio": {"max_position_weight": 0.1, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
                      "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
        "lean_version_id": 18131, "execution_model": "d051", "benchmarks": ["E900-07"], "programme": "P14",
        "cycle": "P14DATAV3", "experiment_id": P.AUDIT, "stall_minutes": 300,
        "params": dict(mode="audit", spec_sha256=P.SPEC_SHA256,
                       v3_code_sha256=P.CODE_SHA256["src/qresearch/lean/qr_v3.py"], guard_sha256=P.GUARD_SHA256,
                       val_sha256=P.VAL_SHA256, data_v21_manifest_sha256=P.DATA_V21_MANIFEST_SHA256),
        "description": DESC, "lean_version_policy": "default_build_digest_verified",
        "owner_approval_required": APPROVAL,
    }


def main():
    assert P.SPEC_SHA256 and all(P.CODE_SHA256.values()) and P.GUARD_SHA256 and P.VAL_SHA256, "pins missing"
    cfg = config()
    d = ROOT / "experiments" / cfg["experiment_id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(cfg, indent=1) + "\n")
    print("wrote", cfg["experiment_id"])


if __name__ == "__main__":
    main()
