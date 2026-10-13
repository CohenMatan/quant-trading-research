"""P14-CP3 / P14-CP3b (owner D229; Amendment 1 sector-stratified null, owner D233): write the S031 configs from the
pins in qresearch.p14h029 -- canary E031-06, null batches E031-07 / E031-08 (seeds 1-2,500 / 2,501-5,000), rerun
E031-09 (seeds 1-25) and, ONLY once c_UP_H029 / c_INCREMENTAL_H030 / the null result / the threshold commit are pinned,
the ONE real run E031-10. (The original-null configs E031-01..04 stay as committed; P14-CP3a.)

    PYTHONPATH=src python research/phase14/cp3/P14_CP3_configs.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p14datav3, p14h029 as P  # noqa: E402

APPROVAL = ("H029 / H030 sector-stratified null amendment (owner 2026-10-13, D233) of the H029 standalone Business "
            "Improvement Score + H030 fixed 50/50 combination (owner 2026-10-12, D229)")
DESC = dict(
    canary="P14-CP3b (owner D233, Amendment 1): S031 v1.1 canary (amendment A5): Data v3 panel digests, H026 panels, "
           "frozen H028 / LV15 reproduction, mechanics, 50/50 blend, SECTOR-STRATIFIED null constructible, same-sector "
           "donors, recipient sector / returns / eligibility / H028 unchanged, synthetic A / within-sector B. NO real "
           "H029 / H030 result. Infrastructure. Default build.",
    null="P14-CP3b (owner D233, Amendment 1): S031 v1.1 sector-stratified null worlds {a}-{b} (six-signal vectors "
         "tethered whole among same-FF12-sector H029-eligible stocks; H028 real). Null rows only. Infrastructure. "
         "Default build.",
    real="P14-CP3 (owner D229 / D233): the ONE real H029 / H030 development evaluation 2015-2021 with the pinned "
         "sector-stratified-null c_UP_H029 and c_INCREMENTAL_H030 (gates N1-N5, C1-C7). Research, DEV. Default build.")


def config(exp, mode, seeds=None):
    w28, wlv, coef = P.h028_inputs()
    params = dict(mode=mode, spec_sha256=P.SPEC_SHA256, amendment1_sha256=P.AMENDMENT1_SHA256,
                  h029_code_sha256=P.CODE_SHA256["src/qresearch/lean/qr_h029.py"], h028_result_sha256=P.H028_RESULT_SHA256,
                  data_v3_manifest_sha256=P.DATA_V3_MANIFEST_SHA256, guard_sha256=p14datav3.GUARD_SHA256,
                  h029_panel_digests_sha256=P.h029_panel_digests_sha256(),
                  h026_feature_panel_sha256=P.H026_FEATURE_PANEL_SHA256,
                  h026_response_panel_sha256=P.H026_RESPONSE_PANEL_SHA256,
                  h028_real_wealth=w28, lv15_real_wealth=wlv, h028_coefficients=coef)
    if seeds:
        params["seeds"] = list(seeds)
    if mode == "real":
        params.update(c_up_h029=P.C_UP_H029, c_incremental_h030=P.C_INCREMENTAL_H030,
                      null_result_sha256=P.NULL_RESULT_SHA256, threshold_commit=P.THRESHOLD_COMMIT)
    desc = DESC[mode].format(a=seeds[0], b=seeds[1]) if seeds else DESC[mode]
    return {
        "kind": "research" if mode == "real" else "infrastructure", "hypothesis_id": "H029", "strategy_id": "S031",
        "strategy_version": "v1.1", "strategy_dir": "strategies/S031_h029_h030", "split_scheme": "2010",
        "split": "DEV" if mode == "real" else "AUDIT",
        "start": "2011-01-03", "end": "2021-12-31", "warmup_start": "2008-07-01", "cash": 100000,
        "universe": {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                     "sec_corrections": False},
        "costs": {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                  "note": "D039: $7 per order, 0.10% slippage (the portfolio is simulated in-host; no order is placed)"},
        "portfolio": {"max_position_weight": 0.1, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
                      "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
        "lean_version_id": 18131, "execution_model": "d051", "benchmarks": ["E900-07"], "programme": "P14",
        "cycle": "P14H029", "experiment_id": exp, "stall_minutes": 300, "params": params, "description": desc,
        "lean_version_policy": "default_build_digest_verified", "owner_approval_required": APPROVAL,
    }


def write(cfg):
    d = ROOT / "experiments" / cfg["experiment_id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(cfg, indent=1) + "\n")
    print("wrote", cfg["experiment_id"])


def main(which=("canary", "null")):
    assert P.SPEC_SHA256 and P.AMENDMENT1_SHA256 and all(P.CODE_SHA256.values()), "pins missing"
    if "canary" in which:
        write(config(P.CANARY, "canary"))
    if "null" in which:
        for exp in P.NULL_RUNS + (P.RERUN,):
            write(config(exp, "null", P.NULL_SEEDS[exp]))
    if "real" in which:
        assert P.C_UP_H029 is not None and P.THRESHOLD_COMMIT, "thresholds not pinned"
        write(config(P.REAL, "real"))


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or ("canary", "null"))
