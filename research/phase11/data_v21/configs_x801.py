"""Data v2.1 (owner D206): the X801 audit configs. E801-01 full 2011-2021; E801-02 identical repeat (determinism);
E801-03 ending 2017-12-31 (2011-2017 reproduction vs the frozen E998-01 and future invariance vs E801-01); E801-04 ending
2013-12-31 (truncation invariance).    PYTHONPATH=src python research/phase11/data_v21/configs_x801.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNS = (("E801-01", "2021-12-31", "full 2011-2021 export"), ("E801-02", "2021-12-31", "identical repeat (determinism)"),
        ("E801-03", "2017-12-31", "2017 end: reproduction of the frozen Data v2 E998-01 and future invariance"),
        ("E801-04", "2013-12-31", "2013 end: truncation invariance"))


def main():
    for exp, end, what in RUNS:
        cfg = {
            "kind": "infrastructure", "hypothesis_id": "H026", "strategy_id": "X801", "strategy_version": "v1.0",
            "strategy_dir": "strategies/X801_data_v21_export", "split_scheme": "2010", "split": "AUDIT",
            "start": "2011-01-03", "end": end, "warmup_start": "2008-07-01", "cash": 100000,
            "universe": {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                         "sec_corrections": False},
            "costs": {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                      "note": "D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)"},
            "portfolio": {"max_position_weight": 0.1, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
                          "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
            "lean_version_id": 18131, "execution_model": "d051", "benchmarks": ["E900-07"], "programme": "P11",
            "cycle": "P11H026", "experiment_id": exp, "stall_minutes": 240, "params": {"mode": "export"},
            "description": f"P11-CP1 (owner D206): Data Infrastructure v2.1 audit X801 ({what}). The frozen X998 export "
                           "(universe, coverage, Score v1 distributions, mechanics, PIT audit, per-review digests) on "
                           "the v2.1 table; aggregates and digests only; no return; nothing after 2021-12-31. "
                           "Infrastructure. Default build (recorded).",
            "lean_version_policy": "default_build_digest_verified",
            "owner_approval_required": "H026 Data v2.1 extension and audit (owner 2026-10-11, D206)"}
        d = ROOT / "experiments" / exp
        d.mkdir(parents=True, exist_ok=True)
        (d / "config.json").write_text(json.dumps(cfg, indent=1) + "\n")
        print("wrote", exp)


if __name__ == "__main__":
    main()
