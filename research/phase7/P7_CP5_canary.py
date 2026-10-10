"""P7-CP5 (D177): assess the X994 plumbing canary (E994-01) offline -> research/phase7/P7_CP5_canary.json.
Plumbing and integrity only: the canary computed no IC of the real assignment, no gate and no null statistic; this
script reads its exported checks, compares the score side with the frozen E993-02 export (P7-CP3R) and the module /
spec fingerprints with the pins in qresearch.p7pred. No return value is read or written."""
import gzip
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean")]
import qr_p7_export as E  # noqa: E402
from qresearch import p7pred  # noqa: E402

sys.path.insert(0, str(HERE))
from P7_CP3R_extract import joined, lines  # noqa: E402


def uploaded_modules_ok(exp):
    """D178: the files uploaded for a run (re-assembled at its build commit) hash to the recorded code_sha256, and every
    pinned module among them equals its pin (the runner also verified QuantConnect's stored copy before compiling)."""
    from qresearch import run as RUN
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    files = RUN.assemble_files(cfg, prov["build_commit"], False)
    pins = {Path(k).name: v for k, v in p7pred.CODE_SHA256.items() if k.startswith("src/qresearch/lean/")}
    mods = {n: hashlib.sha256(files[n].encode()).hexdigest() == pins[n] for n in pins if n in files}
    host = hashlib.sha256(files["main.py"].encode()).hexdigest() == p7pred.HOST_SHA256
    return RUN.code_hash(files) == prov["code_sha256"] and all(mods.values()) and host and len(mods) >= 8, \
        dict(build_commit=prov["build_commit"], code_sha256=prov["code_sha256"], modules=mods, host=host)


def main(exp="E994-02"):
    ls = lines(exp)
    st = json.loads(joined(ls, "QRP7S"))
    assert not any(x.startswith(("QRN|", "QRR|")) for x in ls), "canary exported null / real statistics"
    ck = st["canary"]
    pay = json.loads(gzip.open(HERE / "P7_CP3R_E993_payload.json.gz").read())
    e993 = [[r[0], hashlib.sha256(r[2].encode()).hexdigest()] for r in pay["reviews"]]
    pop993 = [[r[0], sum(1 for x in E.decode_rows(r[2]) if E.eligible_flag(x["bits"], x["total"]))]
              for r in pay["reviews"][:-1]]
    pop = st["coverage"]["population"]
    tm, fr, inv, sc, nm = (ck[k] for k in ("timing", "fresh_recomputation", "response_invariance", "score_invariance",
                                           "null_machinery"))
    up_ok, up = uploaded_modules_ok(exp)
    status = {}
    for key, n in st["coverage"]["status"].items():
        status[key.split("|")[2]] = status.get(key.split("|")[2], 0) + n
    checks = {
        "1 no real IC / gate / null statistic computed": not ck["real_ic_computed"] and not ck["gates_computed"],
        "2 uploaded host + module fingerprints = pins (runner-verified stored copies, D178)": up_ok,
        "3 spec fingerprint = pinned spec (D177)": st["spec_sha256"] == p7pred.SPEC_SHA256,
        "4 calendar: 84 reviews / weekly checks match the session calendar": st["calendar_check"]["reviews_match"]
        and st["calendar_check"]["weekly_match"] and st["calendar_check"]["reviews"] == 84,
        "5 decisions 2011-01-31 .. 2017-11-30 (83), last response end 2017-12-29":
            st["decisions"] == dict(n=83, first="2011-01-31", last="2017-11-30", last_response_end="2017-12-29"),
        "6 no price after 2017-12-29": st["panel"]["late_rows"] == 0 and tm["response_end_after_last_session"] == 0,
        "7 score fingerprint = E993-02 (every review encoding identical)": st["review_sha256"] == e993,
        "8 regimes = E993-02": [r[1] for r in st["regimes"]] == [x[7] for x in pay["regimes"]],
        "9 population = E993-02 eligible, kept, fully scorable rows": [[d, n] for d, n, _ in pop] == pop993,
        "10 sliced technical inputs = full computation": st["slice_spot_check"]["mismatch"] == 0,
        "11 response timing (entry after t, exit within window)": all(tm[k] == 0 for k in (
            "entry_not_after_t", "entry_on_or_before_t_day", "exit_outside")),
        "12 every response independently recomputed (all horizons)": tm["value_mismatch"] == 0
        and tm["status_mismatch"] == 0,
        "13 corporate actions: fresh single-security history agrees": fr["agree_1e9"] == fr["checked"]
        and fr["status_agree"] == fr["checked"],
        "14 response future / past / truncation invariance": inv["future_changed"] == inv["past_changed"]
        == inv["truncation_changed"] == 0,
        "15 score truncation / future invariance (whole reviews re-scored)": sc["truncated_mismatch"]
        == sc["future_mismatch"] == sc["regime_mismatch"] == 0,
        "16 determinism (responses recomputed identically)": ck["responses_repeat_identical"],
        "17 null machinery deterministic, exact permutations, no self-match": nm["repeat_identical"]
        and nm["tether"]["not_permutation"] == 0 and nm["tether"]["self_matches"] == 0,
        "18 market cap and momentum present for every population row": st["coverage"]["mcap_missing"] == 0
        and st["coverage"]["mom_missing"] == 0,
        "19 status counts cover every population row": sum(status.values()) == sum(n for _, n, _ in pop),
    }
    ns = [n for _, n, _ in pop]
    hi = [h for _, _, h in pop]
    out = dict(experiment=exp, checks=checks, passed=sum(checks.values()), total=len(checks),
               population=dict(min=min(ns), median=statistics.median(ns), max=max(ns), mean=sum(ns) / len(ns)),
               hi80=dict(mean=sum(hi) / len(hi), months_without=sum(1 for h in hi if h == 0)),
               status=status, status_by_year_quintile=st["coverage"]["status"], timing=tm, fresh=fr, invariance=inv,
               score_invariance=sc, null_machinery=nm, uploaded=up, event_classes=ck["event_classes"],
               digests={k: st[k] for k in ("panel_sha256", "score_side_sha256", "response_side_sha256",
                                           "score_tables_sha256", "sids_sha256")},
               runtime={k: st.get(k) for k in ("wall_s", "max_rss_mb", "score_s", "responses_s", "states_s")}
               | dict(canary_s=ck["canary_s"], build_s=st["panel"]["build_s"]))
    name = "P7_CP5_canary.json" if exp == "E994-02" else f"P7_CP5_canary_{exp}.json"
    if exp != "E994-02":
        # D182 (option B): the same canary on QuantConnect's default build, compared with the calibration build
        ref = json.loads((HERE / "P7_CP5_canary.json").read_text())["digests"]
        res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
        out["engine"] = dict(lean_version=res["provenance"].get("lean_version"), reference_build=18131)
        out["vs_calibration"] = {k: st[k] == ref[k] for k in ref} | dict(
            panel_equals_pinned=st["panel_sha256"] == p7pred.PANEL_SHA256)
        out["option_B1_holds"] = bool(out["vs_calibration"]["panel_equals_pinned"])
    (HERE / name).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in checks.items():
        print("PASS" if v else "FAIL", k)
    print(out["passed"], "/", out["total"])
    if "vs_calibration" in out:
        print("engine", out["engine"], "vs calibration build", out["vs_calibration"])


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
