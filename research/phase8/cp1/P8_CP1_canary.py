"""P8-CP1 (owner D199): assess the H023 plumbing canary (S025 canary mode, E025-01) offline -> research/phase8/cp1/
P8_CP1_canary_<exp>.json. Plumbing and integrity only: the canary computed no IC of real responses, no gate and no
null statistic of real responses. Checks the inherited H022 / Data v2 canary (same panel as the pinned H022 panel, same
Score v1 / eligibility tables as frozen E998-01), the uploaded files (frozen Data v2 manifest, S024 byte-identical as
qr_s024, qr_h023 / S025 = H023 pins) and the H023 checks; reports the layer-subtotal digest to pin. No return value is
read or written."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7"),
                str(ROOT / "research/phase7/cp6")]
from P7_CP3R_extract import joined, lines  # noqa: E402
from P7_CP6_canary import e998  # noqa: E402
from qresearch import gitutil, p7pred_v2, p8h023  # noqa: E402


def uploaded(exp):
    """Files uploaded for the run, re-assembled at its build commit: code hash = the recorded one; the frozen Data v2
    files = manifest hashes; S024 uploaded byte-identical as qr_s024; qr_h023, S025 and qr_p7_pred = pins."""
    from qresearch import run as RUN
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    bc = prov["build_commit"]
    files = RUN.assemble_files(cfg, bc, False)
    mtxt = gitutil.show_file(bc, "research/phase7/data_v2/data_freeze_v2.json")
    man = json.loads(mtxt)
    h = lambda t: hashlib.sha256(t.encode()).hexdigest()  # noqa: E731
    rel = {"qr_x998.py": "strategies/X998_data_v2_export/main.py"}
    for f in man["files"]:
        if f.startswith("src/qresearch/lean/"):
            rel[Path(f).name] = f
    frozen = {n: h(files[n]) == man["files"][r] for n, r in rel.items() if n in files}
    pins = dict(main=h(files["main.py"]) == p8h023.CODE_SHA256[p8h023.HOST],
                qr_h023=h(files["qr_h023.py"]) == p8h023.CODE_SHA256["src/qresearch/lean/qr_h023.py"],
                qr_s024=files["qr_s024.py"] == gitutil.show_file(bc, p7pred_v2.HOST)
                and h(files["qr_s024.py"]) == p8h023.sha(p7pred_v2.HOST),
                qr_p7_pred=h(files["qr_p7_pred.py"]) == p8h023.PRED_CODE_SHA256,
                spec=h(gitutil.show_file(bc, p8h023.SPEC)) == p8h023.SPEC_SHA256)
    ok = (RUN.code_hash(files) == prov["code_sha256"] and h(mtxt) == p8h023.DATA_FREEZE_MANIFEST_SHA256
          and all(frozen.values()) and all(pins.values())
          and {"qr_x998.py", "qr_v2.py", "qr_data_v2.py", "qr_p7_score.py"} <= set(frozen))
    return ok, dict(build_commit=bc, code_sha256=prov["code_sha256"], frozen_files_equal=frozen, pins=pins,
                    files=len(files))


def main(exp="E025-01"):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    ck = st["canary"]
    g = ck["h023"]
    ref = e998()
    tm, fr, inv, sc, nm = (ck[k] for k in ("timing", "fresh_recomputation", "response_invariance", "score_invariance",
                                           "null_machinery"))
    up_ok, up = uploaded(exp)
    pit = st.get("pit_audit")
    cc = st["components_check"]
    checks = {
        "1 no IC / gate / null statistic of real responses computed or exported":
            not ck["real_ic_computed"] and not ck["gates_computed"]
            and not any(x.startswith(("QRN|", "QRR|", "QRH|")) for x in ls),
        "2 uploaded files: frozen Data v2 manifest; S024 byte-identical as qr_s024; qr_h023 / S025 / qr_p7_pred / spec"
        " = pins": up_ok,
        "3 run completed, 0 orders, LEAN build recorded": res["status"] == "completed"
        and res["harness_summary"]["orders"] == 0 and bool(res["provenance"].get("lean_version")),
        "4 decisions 2011-01-31 .. 2017-11-30 (83), nothing after 2017-12-29":
            st["decisions"] == dict(n=83, first="2011-01-31", last="2017-11-30", last_response_end="2017-12-29")
            and st["panel"]["late_rows"] == 0 and tm["response_end_after_last_session"] == 0,
        "5 prepared panel = the pinned H022 / Data v2 panel": st["panel_sha256"] == p8h023.PANEL_SHA256,
        "6 Score v1 and eligibility tables = frozen E998-01 (84 reviews)":
            st["data_v2_digests"]["review_scores"] == ref["digests"]["review_scores"]
            and st["data_v2_digests"]["review_eligibility"] == ref["digests"]["review_eligibility"],
        "7 inherited H022 canary: timing, recomputation, corporate actions, invariance, determinism, null, NW":
            all(tm[k] == 0 for k in ("entry_not_after_t", "entry_on_or_before_t_day", "exit_outside", "value_mismatch",
                                     "status_mismatch"))
            and fr["agree_1e9"] == fr["checked"] == fr["status_agree"] > 0
            and inv["future_changed"] == inv["past_changed"] == inv["truncation_changed"] == 0
            and sc["truncated_mismatch"] == sc["future_mismatch"] == sc["regime_mismatch"] == 0
            and ck["responses_repeat_identical"] and nm["repeat_identical"] and nm["tether"]["self_matches"] == 0
            and nm["tether"]["not_permutation"] == 0 and ck["newey_west"]["max_abs_diff"] < 1e-9
            and ck["gate_procedure"]["identity_dates"] == 0,
        "8 PIT audit all zero": pit is not None and all(v == 0 for v in pit.values()),
        "9 layer subtotals sum to the Score v1 total for every population row, within layer maxima":
            cc["rows"] > 0 and cc["sum_mismatch"] == cc["total_mismatch"] == cc["out_of_range"]
            == cc["missing_points"] == 0,
        "10 rows with subtotals = H022 population stock-months": cc["rows"] == sum(
            n for _, n, _ in st["coverage"]["population"]),
        "11 grid of 92, control 40/45/15 at index 42": g["grid"] == 92 and g["control"] == [40, 45, 15]
        and g["control_index"] == 42,
        "12 control Score_v2 = 360 x Score v1 total for every row": g["control_z_mismatch"] == 0,
        "13 grid statistics = frozen qr_p7_pred procedure (real + 2 null assignments, 5 configurations; synthetic)":
            g["vs_h022_procedure"]["compared"] == 15 and g["vs_h022_procedure"]["max_abs_diff"] < 1e-12,
        "14 optimiser-null record: deterministic, distinct worlds, control = H022 null world, finite maxima":
            g["null_record"]["repeat_identical"] and g["null_record"]["distinct"] == 10
            and g["null_record"]["control_equals_h022"] and g["null_record"]["finite_max_t"] == 10,
        "15 selection + walk-forward + structure machinery end to end (synthetic)": g["machinery"]["evaluated"]
        and g["machinery"]["folds"] == 4 and g["machinery"]["pseudo_oos_months"] == 47 and g["dates"] == 83,
        "16 5,000 optimiser-null worlds feasible (projected < 30 min of compute per 1,000)":
            g["null_record"]["world_s_1000"] < 1800,
    }
    out = dict(experiment=exp, checks=checks, passed=sum(checks.values()), total=len(checks),
               lean_version=res["provenance"].get("lean_version"), qc_backtest_id=res["provenance"].get("qc_backtest_id"),
               components_sha256=st["components_sha256"], components_check=cc, panel_sha256=st["panel_sha256"],
               h023=g, uploaded=up, runtime_modules=st.get("g_runtime_modules"), pit_audit=pit,
               runtime={k: st.get(k) for k in ("wall_s", "max_rss_mb")} | dict(canary_s=ck["canary_s"],
                                                                               build_s=st["panel"]["build_s"]))
    (HERE / f"P8_CP1_canary_{exp}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in checks.items():
        print("PASS" if v else "FAIL", k)
    print(out["passed"], "/", out["total"], "| build", out["lean_version"], "| components", out["components_sha256"])


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
