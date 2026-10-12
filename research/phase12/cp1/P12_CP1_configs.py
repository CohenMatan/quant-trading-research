"""P12-CP1 (owner D213): write the S029 experiment configs from the pins in qresearch.p12h027 (run order of
research/phase12/H027_spec.md section 11). A config is written only when every pin its mode needs exists.

    PYTHONPATH=src python research/phase12/cp1/P12_CP1_configs.py canary|null|rerun|real
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p12h027 as P  # noqa: E402

APPROVAL = ("H027 Exposure-Controlled Learned Stock Score: memory work + canary, 5,000 LOWVOL-conditional null worlds + "
            "seeds 1-25 rerun, then ONE real development run (owner 2026-10-12, D213)")
DESC = {
    "canary": "P12-CP1 (owner D213): H027 canary (S029 canary mode) on frozen Data v2.1: memory stages; equivalence gate "
              "(feature / response panels = H026 pins; H026 unconditional null worlds 1-25 = committed E028-04 rows); "
              "conditional permutation checks; LV15 pick check; costs; synthetic worlds A (LOWVOL only) / B (LOWVOL + "
              "GPA). NO real H027, LV15 or factor result. Infrastructure. Default build (recorded).",
    "null": "P12-CP1 (owner D213): H027 LOWVOL-conditional null worlds (S029 null mode): LOWVOL stays with its stock, the ten "
            "other features move together from a persistent tether donor; the complete pipeline reruns per world; the "
            "real assignment only hashed. Infrastructure. Default build (recorded).",
    "real": "P12-CP1 (owner D213): the ONE real H027 development run 2015-2021 (S029 real mode) = the frozen H026 procedure "
            "(must reproduce E028-05) with LV15_CONTROL, gates A1-A6 against the pinned c_WEALTH_CONDITIONAL and the "
            "pre-registered diagnostics; final score only if A1-A6 all pass. Research. Default build (recorded).",
}


def base(exp, mode, kind):
    return {
        "kind": kind, "hypothesis_id": "H027", "strategy_id": "S029", "strategy_version": "v1.0",
        "strategy_dir": "strategies/S029_h027_exposure_controlled", "split_scheme": "2010",
        "split": "AUDIT" if kind != "research" else "DEV",
        "start": "2011-01-03", "end": "2021-12-31", "warmup_start": "2008-07-01", "cash": 100000,
        "universe": {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                     "sec_corrections": False},
        "costs": {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                  "note": "D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)"},
        "portfolio": {"max_position_weight": 0.1, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
                      "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
        "lean_version_id": 18131, "execution_model": "d051", "benchmarks": ["E900-07"], "programme": "P12",
        "cycle": "P12H027", "experiment_id": exp, "stall_minutes": 300,
        "params": dict(mode=mode, spec_sha256=P.SPEC_SHA256,
                       h027_code_sha256=P.CODE_SHA256["src/qresearch/lean/qr_h027.py"],
                       data_v21_manifest_sha256=P.DATA_V21_MANIFEST_SHA256,
                       h026_feature_panel_sha256=P.H026_FEATURE_PANEL_SHA256,
                       h026_response_panel_sha256=P.H026_RESPONSE_PANEL_SHA256),
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
        c["params"]["h026_null_rows_sha256"] = P.H026_NULL_ROWS_SHA256
        write(c)
    elif mode in ("null", "rerun"):
        runs = zip(P.NULL_RUNS, P.NULL_BATCHES) if mode == "null" else [(P.RERUN, P.RERUN_SEEDS)]
        for exp, seeds in runs:
            c = base(exp, "null", "infrastructure")
            c["params"]["seeds"] = list(seeds)
            write(c)
    elif mode == "real":
        assert P.C_WEALTH_CONDITIONAL is not None and P.THRESHOLD_COMMIT and P.ADEQUATE is True
        c = base(P.REAL, "real", "research")
        c["portfolio"].update(min_position_usd=5000, max_positions=15)      # the approved D051 rules (no order is placed)
        c["params"].update(c_wealth_conditional=P.C_WEALTH_CONDITIONAL, null_result_sha256=P.NULL_RESULT_SHA256,
                           threshold_commit=P.THRESHOLD_COMMIT, h026_real_wealth=P.H026_REAL_WEALTH,
                           h026_real_s_wealth=P.H026_REAL_S_WEALTH)
        write(c)


if __name__ == "__main__":
    main(sys.argv[1])
