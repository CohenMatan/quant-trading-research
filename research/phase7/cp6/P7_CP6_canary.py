"""P7-CP6 (owner D194): assess the H022 / Data v2 plumbing canary (X999) offline -> research/phase7/cp6/
P7_CP6_canary_<exp>.json. Plumbing and integrity only: the canary computed no IC of the real assignment, no gate and no
null statistic of real responses; this script reads its exported checks and digests and compares them with
- the frozen Data v2 manifest (uploaded files = frozen file hashes, at the run's build commit),
- the frozen E998-01 export (per-review Score v1 / eligibility digests, H022 populations, regimes),
- the H022 pins (spec, qr_p7_pred, Score v1).
No return value is read or written."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import gitutil, p7pred, p7pred_v2, p7score  # noqa: E402


def e998(exp="E998-01"):
    txt = (ROOT / "experiments" / exp / "messages.txt").read_text().splitlines()
    return json.loads(joined(txt, "QRV2"))


def uploaded(exp):
    """Files uploaded for the run, re-assembled at its build commit: hash = recorded code_sha256; every Data v2 / Score
    v1 / H022 module equals its frozen pin; the frozen manifest at that commit is the pinned one."""
    from qresearch import run as RUN
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    files = RUN.assemble_files(cfg, prov["build_commit"], False)
    man = json.loads(gitutil.show_file(prov["build_commit"], "research/phase7/data_v2/data_freeze_v2.json"))
    man_sha = hashlib.sha256(gitutil.show_file(prov["build_commit"], "research/phase7/data_v2/data_freeze_v2.json")
                             .encode()).hexdigest()
    rel = {"qr_x998.py": "strategies/X998_data_v2_export/main.py"}
    for f in man["files"]:
        if f.startswith("src/qresearch/lean/"):
            rel[Path(f).name] = f
    frozen = {n: hashlib.sha256(files[n].encode()).hexdigest() == man["files"][r] for n, r in rel.items() if n in files}
    pins = {Path(k).name: v for k, v in p7score.CODE_SHA256.items() if k.startswith("src/qresearch/lean/")} \
        if hasattr(p7score, "CODE_SHA256") else {}
    score = {n: hashlib.sha256(files[n].encode()).hexdigest() == v for n, v in pins.items() if n in files}
    host = hashlib.sha256(files["main.py"].encode()).hexdigest() == hashlib.sha256(
        gitutil.show_file(prov["build_commit"], p7pred_v2.HOST).encode()).hexdigest()
    pred = hashlib.sha256(files["qr_p7_pred.py"].encode()).hexdigest() == p7pred_v2.PRED_CODE_SHA256
    ok = (RUN.code_hash(files) == prov["code_sha256"] and man_sha == p7pred_v2.DATA_FREEZE_MANIFEST_SHA256
          and all(frozen.values()) and all(score.values()) and host and pred
          and {"qr_x998.py", "qr_v2.py", "qr_data_v2.py", "qr_p7_score.py"} <= set(frozen))
    return ok, dict(build_commit=prov["build_commit"], code_sha256=prov["code_sha256"], manifest_sha256=man_sha,
                    frozen_files_equal=frozen, score_v1_files_equal=score, host_equal=host, qr_p7_pred_equal=pred,
                    files=len(files))


def main(exp="E999-01"):
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7V"))
    real_lines = any(x.startswith(("QRN|", "QRR|")) for x in ls)
    ck = st["canary"]
    ref = e998()
    cols = ref["per_review_cols"]
    ic, ir = cols.index("candidates"), cols.index("regime")
    pop_ref = [[r[0], r[ic]] for r in ref["per_review"][:-1]]
    pop = st["coverage"]["population"]
    tm, fr, inv, sc, nm = (ck[k] for k in ("timing", "fresh_recomputation", "response_invariance", "score_invariance",
                                           "null_machinery"))
    up_ok, up = uploaded(exp)
    status = {}
    for key, n in st["coverage"]["status"].items():
        status[key.split("|")[2]] = status.get(key.split("|")[2], 0) + n
    pit = st.get("pit_audit")
    checks = {
        "1 no real IC / gate / null statistic of real responses computed or exported":
            not ck["real_ic_computed"] and not ck["gates_computed"] and not real_lines,
        "2 frozen Data v2 manifest + uploaded files = frozen hashes; Score v1 / qr_p7_pred / host = pins": up_ok,
        "3 H022 spec fingerprint = pinned spec": st["spec_sha256"] == p7pred.SPEC_SHA256 == p7pred_v2.SPEC_SHA256,
        "4 Data v2 reference table loaded (hash-checked by its loader)": st.get("table_version") == "data_v2"
        and st.get("table_end") == "2017-12-31",
        "5 LEAN build recorded; run completed with 0 orders": bool(res["provenance"].get("lean_version"))
        and res["status"] == "completed" and res["harness_summary"]["orders"] == 0,
        "6 calendar: 84 reviews / weekly checks match the session calendar": st["calendar_check"]["reviews_match"]
        and st["calendar_check"]["weekly_match"] and st["calendar_check"]["reviews"] == 84,
        "7 decisions 2011-01-31 .. 2017-11-30 (83), last response end 2017-12-29":
            st["decisions"] == dict(n=83, first="2011-01-31", last="2017-11-30", last_response_end="2017-12-29"),
        "8 no price after 2017-12-29": st["panel"]["late_rows"] == 0 and tm["response_end_after_last_session"] == 0,
        "9 Score v1 tables = frozen E998-01 (all 84 reviews)":
            st["data_v2_digests"]["review_scores"] == ref["digests"]["review_scores"],
        "10 eligibility sets = frozen E998-01 (all 84 reviews)":
            st["data_v2_digests"]["review_eligibility"] == ref["digests"]["review_eligibility"],
        "11 H022 population per decision = E998-01 candidates (no hard disqualifier)":
            [[d, n] for d, n, _ in pop] == pop_ref,
        "12 regimes = E998-01": [r[1] for r in st["regimes"]] == [r[ir] for r in ref["per_review"]],
        "13 sliced technical inputs = full computation": st["slice_spot_check"]["mismatch"] == 0,
        "14 response timing (entry after t, exit within window)": all(tm[k] == 0 for k in (
            "entry_not_after_t", "entry_on_or_before_t_day", "exit_outside")),
        "15 every response independently recomputed (all horizons)": tm["value_mismatch"] == 0
        and tm["status_mismatch"] == 0,
        "16 corporate actions: fresh single-security history agrees": fr["agree_1e9"] == fr["checked"] > 0
        and fr["status_agree"] == fr["checked"],
        "17 response future / past / truncation invariance": inv["future_changed"] == inv["past_changed"]
        == inv["truncation_changed"] == 0,
        "18 score truncation / future invariance (whole reviews re-scored)": sc["truncated_mismatch"]
        == sc["future_mismatch"] == sc["regime_mismatch"] == 0,
        "19 determinism (responses recomputed identically)": ck["responses_repeat_identical"],
        "20 null machinery deterministic, exact permutations, no self-match": nm["repeat_identical"]
        and nm["tether"]["not_permutation"] == 0 and nm["tether"]["self_matches"] == 0,
        "21 Newey-West implementation = independent computation": ck["newey_west"]["max_abs_diff"] < 1e-9,
        "22 full G1-G4 null procedure (synthetic responses), never the identity assignment":
            ck["gate_procedure"]["worlds"] == ck["gate_procedure"]["complete"] == ck["gate_procedure"]["gates_evaluated"]
            > 0 and ck["gate_procedure"]["identity_dates"] == 0,
        "23 market cap and momentum present for every population row": st["coverage"]["mcap_missing"] == 0
        and st["coverage"]["mom_missing"] == 0,
        "24 status counts cover every population row": sum(status.values()) == sum(n for _, n, _ in pop),
        "25 PIT audit all zero": pit is not None and all(v == 0 for v in pit.values()),
    }
    ns = [n for _, n, _ in pop]
    hi = [h for _, _, h in pop]
    out = dict(experiment=exp, checks=checks, passed=sum(checks.values()), total=len(checks),
               lean_version=res["provenance"].get("lean_version"), qc_backtest_id=res["provenance"].get("qc_backtest_id"),
               population=dict(min=min(ns), median=sorted(ns)[len(ns) // 2], max=max(ns), mean=sum(ns) / len(ns)),
               hi80=dict(mean=sum(hi) / len(hi), months_without=sum(1 for h in hi if h == 0)),
               status=status, timing=tm, fresh=fr, invariance=inv, score_invariance=sc, null_machinery=nm,
               newey_west=ck["newey_west"], gate_procedure=ck["gate_procedure"], uploaded=up,
               event_classes=ck["event_classes"], pit_audit=pit, coverage_repaired_rows=st["coverage"]["repaired_rows"],
               digests={k: st[k] for k in ("panel_sha256", "score_side_sha256", "response_side_sha256",
                                           "availability_sha256", "calendar_sha256", "sids_sha256")},
               runtime={k: st.get(k) for k in ("wall_s", "max_rss_mb", "score_s", "responses_s", "states_s")}
               | dict(canary_s=ck["canary_s"], build_s=st["panel"]["build_s"],
                      null_world_s_1000=nm["world_s_1000"]))
    (HERE / f"P7_CP6_canary_{exp}.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in checks.items():
        print("PASS" if v else "FAIL", k)
    print(out["passed"], "/", out["total"], "| build", out["lean_version"], "| panel", out["digests"]["panel_sha256"])


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
