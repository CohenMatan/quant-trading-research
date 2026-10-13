"""P14-CP3b (owner D233, Amendment 1): offline check of the S031 v1.1 canary E031-06 against amendment section A5 (and
the unchanged spec section 13 items) -> P14_CP3b_canary.json. Committed before E031-06 ran. Any failure: STOP, no
sector-stratified null world is run. (The original canary E031-01 record is P14_CP3_canary.json, unchanged.)

    PYTHONPATH=src python research/phase14/cp3/P14_CP3b_canary.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import p14h029 as P  # noqa: E402

EXP = P.CANARY
PERSIST_MIN = 0.95
MECHANICS = dict(K=15, SECTOR_CAP=3, CAPITAL=100000.0, COMMISSION=7.0, SLIPPAGE=0.001, STRESS_SLIPPAGE=0.002,
                 LAMBDA=100.0)


def main():
    st = json.loads(joined(lines(EXP), "QRY"))
    ck = st["canary"]
    m, n, rep, eq = ck["mechanics"], ck["null_checks"], st["h028_reproduction"], st["equivalence"]
    syn = ck.get("synthetic")
    constructible = n["constructible"] is True and n["min_sector_size"] >= 2 and n["singleton_sector_reviews"] == 0
    checks = {
        "1_data_v3_panel_digests": eq["h029_panel"],
        "1_pit_audit_zero": all(v == 0 for v in st["pit_audit"].values()),
        "1_v3_view_future_records_zero": st["v3"]["view_future_records"] == 0,
        "2_no_real_result": ck["real_h029_h030_result_computed"] is False,
        "3_h029_score_unchanged_six_signals_min_valid_ge_5": m["min_valid_signals"] >= 5 and m["score_mismatch"] == 0,
        "4_h026_feature_panel": eq["feature_panel"],
        "4_h026_response_panel": eq["response_panel"],
        "4_h028_coefficients_and_wealth_and_lv15": rep["ok"],
        "5_h030_blend_exact_50_50": m["blend_mismatch"] == 0,
        "6_entries_after_review_joint_subset": m["entry_not_after_review"] == 0 and m["joint_not_subset"] == 0,
        "7_sector_null_constructible": constructible,
        "7_donor_sector_equals_recipient_sector": constructible and n["mapped"] > 0 and n["donor_other_sector"] == 0,
        "7_recipient_sector_unchanged": n["recipient_sector_changed"] == 0,
        "7_recipient_eligible_sets_unchanged": constructible and n["eligibility_changed"] == 0,
        "7_complete_six_signal_vector_moves": constructible and n["not_donor_vector"] == 0,
        "7_no_self_matches": constructible and n["self_match"] == 0,
        "7_persistent_donor_mapping": (n["persist_possible"] > 0
                                       and n["persist_kept"] / n["persist_possible"] >= PERSIST_MIN),
        "7_recipient_returns_unchanged": n["recipient_data_changed"] == 0,
        "7_recipient_h028_unchanged": constructible and n["h028_changed"] == 0,
        "7_costs_and_mechanics_unchanged": n["mechanics_constants"] == MECHANICS,
        "7_world_deterministic": ck.get("world_repeat_identical") is True,
        "8_synthetic_A_noise_within_sectors": bool(syn and syn["A_pass"]),
        "9_synthetic_B_planted_within_sector": bool(syn and syn["B_pass"]),
    }
    ok = all(checks.values())
    result = ("CANARY PASS" if ok else
              "STOP — SECTOR-STRATIFIED NULL NOT CONSTRUCTIBLE" if not constructible else "CANARY FAIL — STOP")
    out = dict(experiment=EXP, amendment=P.AMENDMENT1, checks=checks, passed=sum(checks.values()), total=len(checks),
               result=result,
               details=dict(mechanics=m, null_checks=n, synthetic=syn, h028_reproduction=rep, equivalence=eq,
                            h029_months=st.get("h029_months", {}).get("eligible"), v3=st["v3"],
                            estimated_5000_world_minutes=ck.get("estimated_5000_world_minutes"),
                            memory=st.get("memory"), max_rss_mb=st.get("max_rss_mb"), wall_s=st.get("wall_s")))
    (HERE / "P14_CP3b_canary.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(out["result"], f"{out['passed']}/{out['total']}", [k for k, v in checks.items() if not v])


if __name__ == "__main__":
    main()
