"""P12-CP1 (owner D213): assess the H027 canary (S029 canary mode, E029-01) offline -> P12_CP1_canary_E029-01.json.

The checks below and their tolerances were written and committed BEFORE the E029-01 output was read. No real H027, LV15
or factor result exists in a canary (the host emits no QRGN / QRGR block). The equivalence gate (spec section 9) must
pass exactly; any difference means STOP.

    PYTHONPATH=src python research/phase12/cp1/P12_CP1_canary.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import gitutil, p11h026, p12h027 as P  # noqa: E402

TOL = dict(null_minutes_max=480.0)
STAGES = ("on_end_start", "after_run_state_released", "after_repair", "after_x801_build_hl_freed", "after_build",
          "after_scores", "after_months", "after_panel_freed", "end")


def uploaded(exp):
    from qresearch import run as RUN
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    bc = prov["build_commit"]
    files = RUN.assemble_files(cfg, bc, False)
    h = lambda t: hashlib.sha256(t.encode()).hexdigest()  # noqa: E731
    man = json.loads(gitutil.show_file(bc, p11h026.DATA_V21_MANIFEST))
    v21 = {Path(f).name: f for f in man["files"] if f.startswith("src/qresearch/lean/qr_data_v21")}
    frozen = {n: h(files[n]) == man["files"][r] for n, r in v21.items()}
    pins = dict(main=h(files["main.py"]) == P.CODE_SHA256[P.HOST],
                qr_s028=h(files["qr_s028.py"]) == p11h026.CODE_SHA256[p11h026.HOST],
                qr_h027=h(files["qr_h027.py"]) == P.CODE_SHA256["src/qresearch/lean/qr_h027.py"],
                qr_h026=h(files["qr_h026.py"]) == p11h026.CODE_SHA256["src/qresearch/lean/qr_h026.py"],
                qr_h024=h(files["qr_h024.py"]) == p11h026.CODE_SHA256["src/qresearch/lean/qr_h024.py"],
                qr_p7_pred=h(files["qr_p7_pred.py"]) == p11h026.CODE_SHA256["src/qresearch/lean/qr_p7_pred.py"],
                qr_x801=h(files["qr_x801.py"]) == p11h026.CODE_SHA256[p11h026.DATA_HOST],
                spec=h(gitutil.show_file(bc, P.SPEC)) == P.SPEC_SHA256,
                manifest=h(gitutil.show_file(bc, p11h026.DATA_V21_MANIFEST)) == P.DATA_V21_MANIFEST_SHA256)
    ok = RUN.code_hash(files) == prov["code_sha256"] and all(frozen.values()) and all(pins.values())
    return ok, dict(build_commit=bc, code_sha256=prov["code_sha256"], frozen_files_equal=frozen, pins=pins,
                    files=len(files), max_file_chars=max(len(v) for v in files.values()), lean=prov["lean_version"])


def main(exp=P.CANARY):
    ok, up = uploaded(exp)
    ls = lines(exp)
    st = json.loads(joined(ls, "QRG"))
    ck = st["canary"]
    c26 = json.loads((ROOT / "research/phase11/cp1/P11_CP1_canary_E028-01.json").read_text())
    pc, syn = ck["conditional_permutation"], ck["synthetic"]
    mem = {m[0]: m[2] for m in st["memory"]}
    checks = {
        "1_upload_matches_pins": ok,
        "2_feature_and_response_panels_equal_h026_pins": st["equivalence"] == dict(feature_panel=True, response_panel=True),
        "3_h026_null_worlds_1_25_equal_e028_04": ck["h026_null_rows"]["equal_to_e028_04"] is True,
        "4_population_reproduction_equals_p11_canary":
            st["reproduction"]["per_decision"] == c26["reproduction"]["per_decision"]
            and st["reproduction"]["h024_population_rows"] == c26["reproduction"]["h024_stock_months"]
            and st["coverage"] == c26["coverage"],
        "5_pit_audit_zero": all(v == 0 for v in st["pit_audit"].values()),
        "6_lowvol_never_permuted": pc["lowvol_changed"] == 0,
        "7_other_ten_move_as_one_donor_vector": pc["other_not_donor_row"] == 0 and pc["permutation_not_exact"] == 0,
        "8_no_self_match_and_persistence": pc["self_matches"] == 0 and pc["persistence_within_splice_bound"],
        "9_recipient_returns_unchanged": pc["responses_unchanged"] is True,
        "10_lv15_picks_independent_walk": ck["lv15_picks"]["mismatch"] == 0 and ck["lv15_picks"]["months"] == 84,
        "11_costs_and_threshold_code": ck["costs_by_hand"]["ok"] and ck["critical_value_50th_of_5000"],
        "12_synthetic_A_lowvol_only_not_beating_null": syn["A"]["pass"],
        "13_synthetic_B_incremental_signal_beats_null": syn["B"]["pass"],
        "14_synthetic_deterministic": all(r["repeat_identical"] for r in syn["A"]["replicates"] + syn["B"]["replicates"]),
        "15_no_real_result_computed": ck["real_h027_result_computed"] is False and not any(
            x.startswith(("QRGN|", "QRGR|")) for x in ls),
        "16_null_feasible": ck["estimated_5000_world_minutes"] <= TOL["null_minutes_max"],
        "17_memory_stages_reported": all(s in mem for s in STAGES),
    }
    hwm = max(v.get("VmHWM", 0) for v in mem.values())
    res = dict(experiment=exp, upload=dict(ok=ok, **up), checks=checks, passed=sum(checks.values()),
               total=len(checks), tolerances=TOL, canary=ck, coverage=st["coverage"],
               reproduction={k: v for k, v in st["reproduction"].items() if k != "per_decision"},
               memory=dict(stages=st["memory"], peak_vmhwm_mb=hwm, ru_maxrss_mb=st.get("max_rss_mb"),
                           before_h026_mb=P.H026_PEAK_MEMORY_MB, target_mb=6500),
               feature_panel_sha256=st["feature_panel_sha256"], response_panel_sha256=st["response_panel_sha256"],
               wall_s=st["wall_s"])
    (HERE / f"P12_CP1_canary_{exp}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(checks=checks, passed=res["passed"], total=res["total"], memory_peak_mb=hwm,
                          ru_maxrss_mb=st.get("max_rss_mb"), stages={s: mem.get(s) for s in STAGES},
                          synthetic={k: syn[k] for k in ("A", "B")}, permutation=pc,
                          minutes=ck["estimated_5000_world_minutes"]), indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
