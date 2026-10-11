"""P10-CP1 (owner D204): assess the H025 canary (S027 canary mode, E027-03) offline -> P10_CP1_canary.json. Synthetic
returns only: no real H025 response was computed (the host reports real_responses_computed = False and emits no QRH
block). Checks the upload against the pins and every canary item of spec section 14 / owner item 22.

Status-label note (decided from the code, not from any return): in the 'truncated' class (no close on the planned exit
row) a security with NO bar at all in the window is labelled 'no_bar' by qr_h025.tsr and 'no_bar_after_t' by S024's
fresh-history path (_fresh_response); both return 0.0 and H025 treats such an event / candidate as NOT evaluable (NaN,
spec section 9). Those labels are mapped before comparison; the VALUE comparison is unaffected.

    PYTHONPATH=src python research/phase10/cp1/P10_CP1_canary.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7"), str(HERE)]
from P10_CP1_audit import uploaded  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import p10h025 as P  # noqa: E402


def main(exp=P.CANARY):
    ok, up = uploaded(exp)
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    ck = st["canary"]
    led, ca, sy = ck["ledger"], ck["corporate_actions"], ck["synthetic_statistics"]
    by = ca["by_class"]
    checks = {
        "1_upload_matches_pins": ok,
        "2_in_host_ledger_equals_pin": st["in_host_ledger_sha256"] == P.IN_HOST_LEDGER_SHA256,
        "3_calendar_equals_pin": st["calendar"]["sha256"] == P.CALENDAR_SHA256,
        "4_sec_timing_entry_strictly_after_acceptance": led["entry_mismatch"] == 0,
        "5_20_session_exit": led["exit_mismatch"] == 0,
        "6_cooldown": led["cooldown_violations"] == 0,
        "7_review_strictly_before_trigger_and_latest": led["review_not_before_trigger"] == 0
        and led["review_not_latest"] == 0,
        "8_identity_cik_and_eligibility": led["cik_mismatch"] == 0 and led["sid_not_eligible"] == 0,
        "9_spy_total_return_fresh_history": sy is not None and ck["spy_total_return"]["worst_rel"] < 1e-9,
        "10_response_fn_equals_frozen_qr_p7_pred": ca["frozen_fn_mismatch"] == 0,
        "11_corporate_action_values_fresh_history": all(c["agree_1e9"] == c["n"] > 0 for c in by.values()),
        "12_corporate_action_status_labels": all(c["status_agree"] == c["n"] for k, c in by.items() if k != "truncated"),
        "13_next_open_timing_synthetic": ck["synthetic_timing"]["ok"],
        "14_planted_effect_detected_zero_rejected": sy["planted"]["0.04"]["gates"]["all"]
        and not sy["planted"]["0.0"]["gates"]["all"],
        "15_null_machinery_deterministic_no_empty_pool": sy["repeat_identical"] and sy["empty_pools"] == 0,
        "16_no_real_response_computed": ck["real_responses_computed"] is False and not any(
            x.startswith("QRH|") for x in ls),
        "17_pit_audit_zero": all(v == 0 for v in st["pit_audit"].values()),
    }
    res = dict(experiment=exp, upload=dict(ok=ok, **up), checks=checks, passed=sum(checks.values()),
               total=len(checks), canary=ck, note_truncated_labels=dict(
                   status_agree=by["truncated"]["status_agree"], n=by["truncated"]["n"],
                   values_agree=by["truncated"]["agree_1e9"],
                   explanation="'no_bar' (qr_h025.tsr) vs 'no_bar_after_t' (S024 fresh path) for securities without "
                               "any bar in the window; both 0.0; such responses are NaN / not evaluable in H025"),
               wall_s=st["wall_s"])
    (HERE / "P10_CP1_canary.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(res["passed"], "/", res["total"], [k for k, v in checks.items() if not v])


if __name__ == "__main__":
    main()
