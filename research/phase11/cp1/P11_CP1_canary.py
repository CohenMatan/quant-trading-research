"""P11-CP1 (owner D206): assess the H026 canary (S028 canary mode, E028-01) offline -> P11_CP1_canary.json.

No real model fit, portfolio or return result exists in a canary (the host emits no QRWN / QRWR block). The checks
below and their tolerances were written and committed BEFORE the E028-01 output was read.

Reproduction rule (owner D206 item: '2011-2017 must reproduce the frozen H024/H022 population where expected; a
material change means STOP'): exact digests are reported; the gate is (a) the per-decision H022 population counts equal
the Data v2.1 audit E801-03 'candidates' exactly (same data layer, same rule), and (b) the 2011-2017 H022 and H024
population totals within 0.1% of the frozen 34,863 / 34,831 (D207 documented -16 / -0.05% from the restatement guard).

    PYTHONPATH=src python research/phase11/cp1/P11_CP1_canary.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7"),
                str(ROOT / "research/phase7/data_v2")]
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import gitutil, p7pred_v2, p9h024, p11h026 as P  # noqa: E402

TOL = dict(population_rel=0.001, coverage_min=0.75, recomputed_min=250, null_minutes_max=480.0)
FROZEN_H022, FROZEN_H024 = 34863, 34831


def uploaded(exp):
    from qresearch import run as RUN
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    bc = prov["build_commit"]
    files = RUN.assemble_files(cfg, bc, False)
    h = lambda t: hashlib.sha256(t.encode()).hexdigest()  # noqa: E731
    man = json.loads(gitutil.show_file(bc, P.DATA_V21_MANIFEST))
    v21 = {Path(f).name: f for f in man["files"] if f.startswith("src/qresearch/lean/qr_data_v21")}
    v21["qr_x801.py"] = P.DATA_HOST
    frozen = {n: h(files[n]) == man["files"][r] for n, r in v21.items()}
    pins = dict(main=h(files["main.py"]) == P.CODE_SHA256[P.HOST],
                qr_h026=h(files["qr_h026.py"]) == P.CODE_SHA256["src/qresearch/lean/qr_h026.py"],
                qr_h024=h(files["qr_h024.py"]) == P.CODE_SHA256["src/qresearch/lean/qr_h024.py"],
                qr_p7_pred=h(files["qr_p7_pred.py"]) == P.CODE_SHA256["src/qresearch/lean/qr_p7_pred.py"],
                qr_x801=h(files["qr_x801.py"]) == P.CODE_SHA256[P.DATA_HOST],
                spec=h(gitutil.show_file(bc, P.SPEC)) == P.SPEC_SHA256,
                manifest=hashlib.sha256(gitutil.show_file(bc, P.DATA_V21_MANIFEST).encode()).hexdigest()
                == P.DATA_V21_MANIFEST_SHA256)
    ok = RUN.code_hash(files) == prov["code_sha256"] and all(frozen.values()) and all(pins.values())
    return ok, dict(build_commit=bc, code_sha256=prov["code_sha256"], frozen_files_equal=frozen, pins=pins,
                    files=len(files), max_file_chars=max(len(v) for v in files.values()), lean=prov["lean_version"])


def main(exp=P.CANARY):
    ok, up = uploaded(exp)
    ls = lines(exp)
    st = json.loads(joined(ls, "QRW"))
    ck, cov, rep = st["canary"], st["coverage"], st["reproduction"]
    summ = json.loads((ROOT / "research/phase11/data_v21/x801_summary.json").read_text())
    from x998_analysis import load
    e3 = load("E801-03")
    cand = {r[0]: r[e3["per_review_cols"].index("candidates")] for r in e3["per_review"]}
    per = rep["per_decision"]
    pop_diff = [[d, a, cand.get(d)] for d, a, _b, _c in per if cand.get(d) != a]
    h022 = sum(r[1] for r in per)
    h024 = rep["h024_population_rows"]
    shares = {y: v["share"] for y, v in cov["by_year"].items()}
    syn = ck["synthetic"]
    checks = {
        "1_upload_matches_pins_and_data_v21": ok,
        "2_review_calendar_131": (cov["decisions"], cov["first"], cov["last"]) == (131, "2011-01-31", "2021-11-30"),
        "3_pit_audit_zero": all(v == 0 for v in st["pit_audit"].values()),
        "4_all_11_valid_coverage_ge_75pct_every_year": all(s is not None and s >= TOL["coverage_min"]
                                                             for s in shares.values()),
        "5_feature_recomputation": ck["feature_recomputation"]["mismatch"] == 0
        and ck["feature_recomputation"]["checked"] >= TOL["recomputed_min"],
        "6_label_purge": ck["label_purge"]["violations"] == 0 and ck["label_purge"]["checked"] == 9,
        "7_63_session_timing": ck["timing"]["exit_row_mismatch"] == 0 and ck["timing"]["entry_not_after_review"] == 0,
        "8_planted_beats_zero_deterministic": syn["planted"]["S_WEALTH"] > syn["zero"]["S_WEALTH"]
        and syn["planted"]["repeat_identical"] and syn["zero"]["repeat_identical"],
        "9_h022_population_equals_data_v21_audit": rep["decisions"] == 83 and not pop_diff,
        "10_h022_h024_population_within_0p1pct_of_frozen": abs(h022 / FROZEN_H022 - 1) <= TOL["population_rel"]
        and abs(h024 / FROZEN_H024 - 1) <= TOL["population_rel"],
        "11_null_feasible": ck["estimated_5000_world_minutes"] <= TOL["null_minutes_max"],
        "12_no_real_result_computed": ck["real_portfolio_computed"] is False and not any(
            x.startswith(("QRWN|", "QRWR|")) for x in ls),
        "13_feature_panel_digest": len(st.get("feature_panel_sha256") or "") == 64,
    }
    res = dict(experiment=exp, upload=dict(ok=ok, **up), checks=checks, passed=sum(checks.values()),
               total=len(checks), tolerances=TOL,
               reproduction=dict(h022_panel_sha256=rep["h022_panel_sha256"],
                                 h022_panel_equals_frozen=rep["h022_panel_sha256"] == p7pred_v2.PANEL_SHA256,
                                 h024_population_sha256=rep["h024_population_sha256"],
                                 h024_population_equals_frozen=rep["h024_population_sha256"] == p9h024.POPULATION_SHA256,
                                 h022_stock_months=h022, h024_stock_months=h024, frozen=[FROZEN_H022, FROZEN_H024],
                                 per_decision_vs_e801_03=pop_diff, per_decision=per,
                                 d207_population=summ["h022_population_2011_2017"]),
               coverage=cov, feature_panel_sha256=st["feature_panel_sha256"],
               data_v21_digests_equal_e801_01=None, canary=ck,
               runtime=dict(wall_s=st["wall_s"], scores_s=st.get("scores_s"), months_s=st.get("months_s"),
                            max_rss_mb=st.get("max_rss_mb")), w_spy=st.get("w_spy"))
    d1 = load("E801-01")["digests"]
    dd = st["data_v21_digests"]
    res["data_v21_digests_equal_e801_01"] = dict(
        review_scores=sum(d1["review_scores"].get(k) == v for k, v in dd["review_scores"].items()),
        review_eligibility=sum(d1["review_eligibility"].get(k) == v for k, v in dd["review_eligibility"].items()),
        reviews=len(dd["review_scores"]))
    (HERE / f"P11_CP1_canary_{exp}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(checks=checks, passed=res["passed"], total=res["total"], reproduction={
        k: v for k, v in res["reproduction"].items() if k not in ("per_decision", "d207_population")},
        coverage={y: v for y, v in shares.items()}, runtime=res["runtime"], digests=res["data_v21_digests_equal_e801_01"],
        null_minutes=ck["estimated_5000_world_minutes"]), indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
