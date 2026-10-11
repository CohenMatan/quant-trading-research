"""P9-CP1 (owner D201): assess the H024 canary (S026 canary mode, E026-01) offline -> research/phase9/cp1/
P9_CP1_canary_<exp>.json. Plumbing, feature coverage and redundancy only: the canary read no response for any H024
statistic. Checks the inherited H022 / Data v2 canary, the uploaded files (frozen Data v2 manifest, S024 byte-identical
as qr_s024, qr_h024 / qr_h023 / S026 / qr_p7_pred / spec = pins), feature recomputation, the asset ledger, the coverage
rule, the redundancy links and the model library (regenerated offline from the exported correlations with the frozen
rule), and reports the values to pin (retained features, links, library hash, population digest)."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7"),
                str(ROOT / "research/phase7/cp6")]
import qr_h024 as K  # noqa: E402
from P7_CP3R_extract import joined, lines  # noqa: E402
from P7_CP6_canary import e998  # noqa: E402
from qresearch import gitutil, p7pred_v2, p9h024  # noqa: E402


def uploaded(exp):
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
    pins = dict(main=h(files["main.py"]) == p9h024.CODE_SHA256[p9h024.HOST],
                qr_h024=h(files["qr_h024.py"]) == p9h024.CODE_SHA256["src/qresearch/lean/qr_h024.py"],
                qr_h023=h(files["qr_h023.py"]) == p9h024.ENGINE_SHA256,
                qr_s024=files["qr_s024.py"] == gitutil.show_file(bc, p7pred_v2.HOST),
                qr_p7_pred=h(files["qr_p7_pred.py"]) == p9h024.PRED_CODE_SHA256,
                spec=h(gitutil.show_file(bc, p9h024.SPEC)) == p9h024.SPEC_SHA256)
    ok = (RUN.code_hash(files) == prov["code_sha256"] and h(mtxt) == p9h024.DATA_FREEZE_MANIFEST_SHA256
          and all(frozen.values()) and all(pins.values())
          and {"qr_x998.py", "qr_v2.py", "qr_data_v2.py", "qr_p7_score.py"} <= set(frozen))
    return ok, dict(build_commit=bc, code_sha256=prov["code_sha256"], frozen_files_equal=frozen, pins=pins,
                    files=len(files))


def main(exp="E026-01"):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    ck = st["canary"]
    g = ck["h024"]
    ref = e998()
    tm, fr, inv, sc, nm = (ck[k] for k in ("timing", "fresh_recomputation", "response_invariance", "score_invariance",
                                           "null_machinery"))
    up_ok, up = uploaded(exp)
    pit = st.get("pit_audit")
    retained = [f for f in K.LIBRARY if g["coverage"][f] >= K.COVERAGE_MIN]
    links = K.redundancy_links(g["correlation"]["median_abs"], tuple(retained))
    lib = K.Library(K.model_library(tuple(retained), K.FAMILY, links), tuple(retained))
    checks = {
        "1 no IC / gate / null statistic of real responses computed or exported":
            not ck["real_ic_computed"] and not ck["gates_computed"]
            and not any(x.startswith(("QRN|", "QRR|", "QRH|", "QRK|")) for x in ls),
        "2 uploaded files: frozen Data v2 manifest; S024 byte-identical as qr_s024; qr_h024 / qr_h023 / S026 / "
        "qr_p7_pred / spec = pins": up_ok,
        "3 run completed, 0 orders, LEAN build recorded": res["status"] == "completed"
        and res["harness_summary"]["orders"] == 0 and bool(res["provenance"].get("lean_version")),
        "4 decisions 2011-01-31 .. 2017-11-30 (83), nothing after 2017-12-29":
            st["decisions"] == dict(n=83, first="2011-01-31", last="2017-11-30", last_response_end="2017-12-29")
            and st["panel"]["late_rows"] == 0 and tm["response_end_after_last_session"] == 0,
        "5 prepared H022 panel = the pinned panel": st["panel_sha256"] == p9h024.PANEL_SHA256,
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
            and ck["newey_west"]["max_abs_diff"] < 1e-9 and ck["gate_procedure"]["identity_dates"] == 0,
        "8 PIT audit all zero": pit is not None and all(v == 0 for v in pit.values()),
        "9 every feature recomputed independently on 400 stock-dates (full histories): 0 mismatches":
            g["recomputation"]["checked"] == 400 and g["recomputation"]["mismatch"] == 0,
        "10 asset growth = ledger lookup; ledger 2010-01 .. 2016-12": g["recomputation"]["ledger_mismatch"] == 0
        and g["ledger"]["first"] == [2010, 1] and g["ledger"]["last"] == [2016, 12] and g["ledger"]["months"] == 84,
        "11 coverage rule applied as frozen (>= 90% of H022 stock-months)": g["retained"] == retained,
        "12 redundancy links / components / model library regenerate offline from the exported correlations":
            [list(x) for x in links] == g["links"] and lib.sha == g["library_sha256"] and lib.M == g["models"],
        "13 model count <= 500 and only 2-4 features": lib.M <= K.MODEL_BUDGET and set(lib.k.tolist()) <= {2, 3, 4},
        "14 feature / model / control columns = frozen qr_p7_pred procedure (real + 2 null assignments; synthetic)":
            g["vs_h022_procedure"]["compared"] >= 18 and g["vs_h022_procedure"]["max_abs_diff"] < 1e-12,
        "15 Score v1 control column = Score v1 total": g["control_equals_score_v1"],
        "16 null record deterministic, distinct worlds; selection / walk-forward machinery end to end (synthetic)":
            g["null_record"]["repeat_identical"] and g["null_record"]["distinct"] == 6 and g["machinery"]["folds"] == 4,
        "17 5,000 null worlds feasible (projected < 30 min of compute per 1,000)": g["null_record"]["world_s_1000"] < 1800,
    }
    out = dict(experiment=exp, checks=checks, passed=sum(checks.values()), total=len(checks),
               lean_version=res["provenance"].get("lean_version"), qc_backtest_id=res["provenance"].get("qc_backtest_id"),
               pins=dict(features=retained, links=[list(x) for x in links], library_sha256=lib.sha, models=lib.M,
                         models_by_size=g["models_by_size"], population_sha256=g["population_sha256"],
                         population_rows=g["population_rows"], panel_sha256=st["panel_sha256"]),
               coverage=g["coverage"], coverage_by_year=st["feature_coverage"]["by_year"], h022_rows=st["feature_coverage"]["rows"],
               population_share_of_h022=g["population_share_of_h022"], correlation=g["correlation"],
               components=g["components"], recomputation=g["recomputation"], ledger=g["ledger"],
               vs_h022=g["vs_h022_procedure"], null_record=g["null_record"], uploaded=up, pit_audit=pit,
               runtime={k: st.get(k) for k in ("wall_s", "max_rss_mb")},
               score_v1_tables_vs_e998=dict(
                   differing_reviews=[k for k in ref["digests"]["review_scores"]
                                      if st["data_v2_digests"]["review_scores"].get(k) != ref["digests"]["review_scores"][k]],
                   eligibility_equal=st["data_v2_digests"]["review_eligibility"] == ref["digests"]["review_eligibility"],
                   h022_panel_equal_pinned=st["panel_sha256"] == p9h024.PANEL_SHA256,
                   note="D202: QuantConnect data snapshot changed on 2026-10-11 between 07:58Z (E025-04) and 08:10Z "
                        "(E025-05); only rows outside the H022 population differ (eligibility sets and the pinned "
                        "H022 panel reproduce exactly)"))
    (HERE / f"P9_CP1_canary_{exp}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in checks.items():
        print("PASS" if v else "FAIL", k)
    print(out["passed"], "/", out["total"], "| build", out["lean_version"])
    print(json.dumps(out["pins"]))
    print("coverage", {k: round(v, 4) for k, v in g["coverage"].items()})
    print("median |rho|", np.round(np.array(g["correlation"]["median_abs"]), 2).tolist())


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
