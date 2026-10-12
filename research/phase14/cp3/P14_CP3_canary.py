"""P14-CP3 (owner D229): offline check of the S031 canary E031-01 against spec section 13 -> P14_CP3_canary.json.
Committed before E031-01 ran. Any failure: STOP, no null world is run.

    PYTHONPATH=src python research/phase14/cp3/P14_CP3_canary.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402

EXP = "E031-01"
PERSIST_MIN = 0.95


def main():
    st = json.loads(joined(lines(EXP), "QRY"))
    ck = st["canary"]
    m, n, syn, rep, eq = ck["mechanics"], ck["null_checks"], ck["synthetic"], st["h028_reproduction"], st["equivalence"]
    checks = {
        "1_data_v3_panel_digests": eq["h029_panel"],
        "1_pit_audit_zero": all(v == 0 for v in st["pit_audit"].values()),
        "1_v3_view_future_records_zero": st["v3"]["view_future_records"] == 0,
        "2_no_real_result": ck["real_h029_h030_result_computed"] is False,
        "3_six_signals_min_valid_ge_5": m["min_valid_signals"] >= 5 and m["score_mismatch"] == 0,
        "4_h026_feature_panel": eq["feature_panel"],
        "4_h026_response_panel": eq["response_panel"],
        "4_h028_coefficients_and_wealth_and_lv15": rep["ok"],
        "5_blend_exact_50_50": m["blend_mismatch"] == 0,
        "6_entries_after_review_joint_subset": m["entry_not_after_review"] == 0 and m["joint_not_subset"] == 0,
        "7_null_h028_unchanged": n["h028_changed"] == 0,
        "7_null_eligibility_unchanged": n["eligibility_changed"] == 0,
        "7_null_complete_donor_vectors": n["not_donor_vector"] == 0 and n["self_match"] == 0,
        "7_null_persistence": n["persist_possible"] > 0 and n["persist_kept"] / n["persist_possible"] >= PERSIST_MIN,
        "7_world_deterministic": ck["world_repeat_identical"] is True,
        "8_synthetic_A": syn["A_pass"],
        "9_synthetic_B": syn["B_pass"],
    }
    out = dict(experiment=EXP, checks=checks, passed=sum(checks.values()), total=len(checks),
               result="CANARY PASS" if all(checks.values()) else "CANARY FAIL — STOP",
               details=dict(mechanics=m, null_checks=n, synthetic=syn, h028_reproduction=rep, equivalence=eq,
                            h029_months=st.get("h029_months", {}).get("eligible"), v3=st["v3"],
                            estimated_5000_world_minutes=ck["estimated_5000_world_minutes"],
                            memory=st.get("memory"), max_rss_mb=st.get("max_rss_mb"), wall_s=st.get("wall_s")))
    (HERE / "P14_CP3_canary.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(out["result"], f"{out['passed']}/{out['total']}", [k for k, v in checks.items() if not v])


if __name__ == "__main__":
    main()
