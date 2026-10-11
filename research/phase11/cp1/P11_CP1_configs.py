"""P11-CP1 (owner D206): write the S028 experiment configs from the pins in qresearch.p11h026 (run order of the D206
message). A config is written only when every pin its mode needs exists.

    PYTHONPATH=src python research/phase11/cp1/P11_CP1_configs.py canary|null|rerun|real
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p11h026 as P  # noqa: E402

APPROVAL = ("H026 Learned Stock Score Portfolio: Data v2.1, canary, 5,000 full-pipeline null worlds + seeds 1-25 rerun, "
            "then ONE real 2015-2021 development run (owner 2026-10-11, D206)")
DESC = {
    "canary": "P11-CP1 (owner D206): H026 canary (S028 canary mode) on frozen Data v2.1: review calendar (131 decisions "
              "2011-01 .. 2021-11), H022/H024 population reproduction 2011-2017, all-11-valid coverage by year, feature "
              "recomputation, label purge, entry/exit timing, synthetic planted / zero worlds through the full pipeline, "
              "feature-panel digest, runtime estimate. NO real model fit, portfolio or return result. Infrastructure. "
              "Default build (recorded).",
    "null": "P11-CP1 (owner D206): H026 null worlds (S028 null mode): identity-tether permutation of complete 11-feature "
            "vectors; every world reruns inner lambda selection, annual Ridge fits, Top-15 portfolio, costs and the SPY "
            "comparison; real labels only hashed (response-panel digest). Infrastructure. Default build (recorded).",
    "real": "P11-CP1 (owner D206): the ONE real H026 development run 2015-2021 (S028 real mode) with the pinned "
            "c_WEALTH, null result, threshold commit, feature- and response-panel digests: D1-D5, metrics, "
            "coefficients and the pre-registered diagnostics; final 2011-2021 model only if D1-D5 all pass. Research. "
            "Default build (recorded).",
}


def base(exp, mode, kind):
    return {
        "kind": kind, "hypothesis_id": "H026", "strategy_id": "S028", "strategy_version": "v1.0",
        "strategy_dir": "strategies/S028_h026_learned_score", "split_scheme": "2010",
        "split": "AUDIT" if kind != "research" else "DEV",
        "start": "2011-01-03", "end": "2021-12-31", "warmup_start": "2008-07-01", "cash": 100000,
        "universe": {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                     "sec_corrections": False},
        "costs": {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                  "note": "D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)"},
        "portfolio": {"max_position_weight": 0.1, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
                      "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
        "lean_version_id": 18131, "execution_model": "d051", "benchmarks": ["E900-07"], "programme": "P11",
        "cycle": "P11H026", "experiment_id": exp, "stall_minutes": 300,
        "params": dict(mode=mode, spec_sha256=P.SPEC_SHA256,
                       h026_code_sha256=P.CODE_SHA256["src/qresearch/lean/qr_h026.py"],
                       data_v21_manifest_sha256=P.DATA_V21_MANIFEST_SHA256),
        "description": DESC[mode], "lean_version_policy": "default_build_digest_verified",
        "owner_approval_required": APPROVAL,
    }


def write(cfg):
    d = ROOT / "experiments" / cfg["experiment_id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(cfg, indent=1) + "\n")
    print("wrote", cfg["experiment_id"])


def main(mode):
    assert P.SPEC_SHA256 and P.DATA_V21_MANIFEST_SHA256 and all(P.CODE_SHA256.values()), "pins missing"
    if mode == "canary":
        write(base(P.CANARY, "canary", "infrastructure"))
    elif mode in ("null", "rerun"):
        assert P.FEATURE_PANEL_SHA256
        runs = zip(P.NULL_RUNS, P.NULL_BATCHES) if mode == "null" else [(P.RERUN, P.RERUN_SEEDS)]
        for exp, seeds in runs:
            c = base(exp, "null", "infrastructure")
            c["params"].update(feature_panel_sha256=P.FEATURE_PANEL_SHA256, seeds=list(seeds))
            write(c)
    elif mode == "real":
        assert P.C_WEALTH is not None and P.RESPONSE_PANEL_SHA256 and P.THRESHOLD_COMMIT
        c = base(P.REAL, "real", "research")
        c["portfolio"].update(min_position_usd=5000, max_positions=15)      # the approved D051 rules (no order is placed)
        c["params"].update(feature_panel_sha256=P.FEATURE_PANEL_SHA256, c_wealth=P.C_WEALTH,
                           null_result_sha256=P.NULL_RESULT_SHA256, threshold_commit=P.THRESHOLD_COMMIT,
                           response_panel_sha256=P.RESPONSE_PANEL_SHA256)
        write(c)


if __name__ == "__main__":
    main(sys.argv[1])
