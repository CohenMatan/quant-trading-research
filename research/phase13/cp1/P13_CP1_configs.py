"""P13-CP1 (owner D217): write the S030 experiment configs from the pins in qresearch.p13h028 (run order of
research/phase13/H028_spec.md section 11). A config is written only when every pin its mode needs exists.

    PYTHONPATH=src python research/phase13/cp1/P13_CP1_configs.py canary|null|rerun|real
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p13h028 as P  # noqa: E402

APPROVAL = ("H028 Fixed Strong Shrinkage Learned Stock Score: canary, 5,000 lambda-100 LOWVOL-conditional null worlds + "
            "seeds 1-25 rerun, then ONE real development run (owner 2026-10-12, D217)")
DESC = {
    "canary": "P13-CP1 (owner D217): H028 canary (S030 canary mode) on frozen Data v2.1: lambda = 100 fit log and call "
              "counts; the real H027 reproduced through the fixed path; H027 conditional rows 1-25 (= E029-02) reproduced "
              "through the fixed path; permutation / LV15 / costs checks; 2016-2021 tolerance calibration (worlds "
              "1-100); synthetic worlds A / B at lambda = 100. NO real H028 result. Infrastructure. Default build.",
    "null": "P13-CP1 (owner D217): H028 lambda-100 LOWVOL-conditional null worlds (S030 null mode): LOWVOL stays with its "
            "stock, the ten other features move together from a persistent tether donor; the complete fixed-lambda "
            "pipeline reruns per world. Infrastructure. Default build (recorded).",
    "real": "P13-CP1 (owner D217): the ONE real H028 development run 2015-2021 (S030 real mode): lambda = 100 for every "
            "fit; H027 reproduction, 2016-2021 equality vs H027 (pinned tolerance), LV15_CONTROL, gates B1-B6 against "
            "the pinned c_WEALTH_H028, diagnostics; final score only if B1-B6 all pass. Research. Default build.",
}


def base(exp, mode, kind):
    return {
        "kind": kind, "hypothesis_id": "H028", "strategy_id": "S030", "strategy_version": "v1.0",
        "strategy_dir": "strategies/S030_h028_fixed_shrinkage", "split_scheme": "2010",
        "split": "AUDIT" if kind != "research" else "DEV",
        "start": "2011-01-03", "end": "2021-12-31", "warmup_start": "2008-07-01", "cash": 100000,
        "universe": {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                     "sec_corrections": False},
        "costs": {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                  "note": "D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)"},
        "portfolio": {"max_position_weight": 0.1, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
                      "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
        "lean_version_id": 18131, "execution_model": "d051", "benchmarks": ["E900-07"], "programme": "P13",
        "cycle": "P13H028", "experiment_id": exp, "stall_minutes": 300,
        "params": dict(mode=mode, spec_sha256=P.SPEC_SHA256,
                       h028_code_sha256=P.CODE_SHA256["src/qresearch/lean/qr_h028.py"],
                       data_v21_manifest_sha256=P.DATA_V21_MANIFEST_SHA256,
                       h026_feature_panel_sha256=P.H026_FEATURE_PANEL_SHA256,
                       h026_response_panel_sha256=P.H026_RESPONSE_PANEL_SHA256,
                       h027_real_wealth=P.H027_REAL_WEALTH, h027_real_s_wealth=P.H027_REAL_S_WEALTH,
                       h027_lambda_schedule=list(P.H027_LAMBDA_SCHEDULE)),
        "description": DESC[mode], "lean_version_policy": "default_build_digest_verified",
        "owner_approval_required": APPROVAL,
    }


def write(cfg):
    d = ROOT / "experiments" / cfg["experiment_id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(cfg, indent=1) + "\n")
    print("wrote", cfg["experiment_id"])


def main(mode):
    assert P.SPEC_SHA256 and all(P.CODE_SHA256.values()), "pins missing"
    if mode == "canary":
        c = base(P.CANARY, "canary", "infrastructure")
        c["params"]["h027_null_rows_sha256"] = P.H027_NULL_ROWS_SHA256
        write(c)
    elif mode in ("null", "rerun"):
        assert P.TOLERANCE is not None, "the tolerance table is pinned from the canary before any null world"
        runs = zip(P.NULL_RUNS, P.NULL_BATCHES) if mode == "null" else [(P.RERUN, P.RERUN_SEEDS)]
        for exp, seeds in runs:
            c = base(exp, "null", "infrastructure")
            c["params"]["seeds"] = list(seeds)
            write(c)
    elif mode == "real":
        assert P.C_WEALTH_H028 is not None and P.THRESHOLD_COMMIT and P.ADEQUATE is True
        c = base(P.REAL, "real", "research")
        c["portfolio"].update(min_position_usd=5000, max_positions=15)      # the approved D051 rules (no order is placed)
        c["params"].update(c_wealth_h028=P.C_WEALTH_H028, null_result_sha256=P.NULL_RESULT_SHA256,
                           threshold_commit=P.THRESHOLD_COMMIT, tolerance=P.TOLERANCE,
                           tolerance_sha256=P.TOLERANCE_SHA256)
        write(c)


if __name__ == "__main__":
    main(sys.argv[1])
