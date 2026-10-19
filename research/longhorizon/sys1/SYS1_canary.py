"""SYS-1 (owner D252): assess the canary E032-01 (S032 canary mode) offline -> SYS1_canary_<exp>.json.

Written and committed BEFORE E032-01 ran (protocol section 11). The canary computes no SYS-1 arm result (no QRSY
block). Every check C0-C9 is mandatory; USMV is reported only (OD-4). If any mandatory check fails: STOP, report, and
do NOT run E032-02. If all pass, the digest of the written JSON is pinned as qresearch.sys1.CANARY_RESULT_SHA256
before E032-02.

    PYTHONPATH=src python research/longhorizon/sys1/SYS1_canary.py [E032-01]
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "src/qresearch/lean"), str(ROOT / "research/phase7")]
from P7_CP3R_extract import joined, lines  # noqa: E402
from qresearch import gitutil, p11h026, p12h027, p13h028, sys1 as P  # noqa: E402

LEAN = "src/qresearch/lean/"
MAX_FILES, MAX_CHARS = 50, 64_000


def uploaded(exp):
    """The uploaded project equals the pinned files (S032, qr_sys1, the frozen S030 / S029 / S028 / X801 chain and
    the frozen Data v2.1 table) and the recorded code hash (C8)."""
    from qresearch import run as RUN
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    prov = json.loads((ROOT / "experiments" / exp / "result.json").read_text())["provenance"]
    bc = prov["build_commit"]
    files = RUN.assemble_files(cfg, bc, False)
    h = lambda t: hashlib.sha256(t.encode()).hexdigest()  # noqa: E731
    man = json.loads(gitutil.show_file(bc, p11h026.DATA_V21_MANIFEST))
    v21 = {Path(f).name: f for f in man["files"] if f.startswith(LEAN + "qr_data_v21")}
    frozen = {n: h(files[n]) == man["files"][r] for n, r in v21.items()}
    pins = dict(main=h(files["main.py"]) == P.CODE_SHA256[P.HOST],
                qr_sys1=h(files["qr_sys1.py"]) == P.CODE_SHA256[P.ENGINE],
                qr_s030=h(files["qr_s030.py"]) == p13h028.CODE_SHA256[p13h028.HOST],
                qr_h028=h(files["qr_h028.py"]) == p13h028.CODE_SHA256[LEAN + "qr_h028.py"],
                qr_s029=h(files["qr_s029.py"]) == p12h027.CODE_SHA256[p12h027.HOST],
                qr_h027=h(files["qr_h027.py"]) == p12h027.CODE_SHA256[LEAN + "qr_h027.py"],
                qr_s028=h(files["qr_s028.py"]) == p11h026.CODE_SHA256[p11h026.HOST],
                qr_h026=h(files["qr_h026.py"]) == p11h026.CODE_SHA256[LEAN + "qr_h026.py"],
                qr_h024=h(files["qr_h024.py"]) == p11h026.CODE_SHA256[LEAN + "qr_h024.py"],
                qr_p7_pred=h(files["qr_p7_pred.py"]) == p11h026.CODE_SHA256[LEAN + "qr_p7_pred.py"],
                qr_x801=h(files["qr_x801.py"]) == p11h026.CODE_SHA256[p11h026.DATA_HOST],
                protocol=h(gitutil.show_file(bc, P.PROTOCOL)) == P.PROTOCOL_SHA256,
                manifest=h(gitutil.show_file(bc, p11h026.DATA_V21_MANIFEST)) == p13h028.DATA_V21_MANIFEST_SHA256)
    n, mx = len(files), max(len(v) for v in files.values())
    ok = (RUN.code_hash(files) == prov["code_sha256"] and all(frozen.values()) and all(pins.values())
          and n <= MAX_FILES and mx <= MAX_CHARS and sorted(files) == sorted(prov["files"]))
    return ok, dict(build_commit=bc, code_sha256=prov["code_sha256"], frozen_files_equal=frozen, pins=pins, files=n,
                    max_file_chars=mx, lean=prov["lean_version"])


def assess(st, ls, res, up_ok):
    ck = st["canary"]
    c4 = ck["C4"]
    ids = {n: st["y_etf"][n]["symbol"] for n in P.ETF_IDS}
    c4_ok = {n: bool(c4[n]["ok"] and ids[n] == P.ETF_IDS[n]) for n in P.ETF_IDS}
    c4_ok["spy"] = bool(c4["spy"]["ok"])
    checks = {
        "C0_panel_equivalence": st["equivalence"] == dict(feature_panel=True, response_panel=True),
        "C1_standalone_h028_exact": ck["C1"]["ok"] is True and ck["C1"]["wealth"] == P.FROZEN_H028["wealth"]
            and ck["C1"]["commissions"] == P.FROZEN_H028["commissions"] and ck["C1"]["buys"] == P.FROZEN_H028["buys"]
            and ck["C1"]["sells"] == P.FROZEN_H028["sells"] and ck["C1"]["slippage"] == P.FROZEN_H028["slippage"]
            and ck["C1"]["engine_equals_frozen_simulate"] is True and ck["C1"]["pick_lists"] == 84,
        "C2_spy_exact": ck["C2"]["ok"] is True and ck["C2"]["wealth_100k"] == P.FROZEN_SPY_WEALTH,
        "C3_lv15_exact": ck["C3"]["ok"] is True and ck["C3"]["wealth"] == P.FROZEN_LV15_WEALTH,
        "C4_spy_and_splv_data": c4_ok["spy"] and c4_ok["splv"],
        "C5_account_rules_and_no_hidden_financing": ck["C5"]["ok"] is True and len(ck["C5"]["random"]) == 6
            and len(ck["C5"]["etf"]) == 2 and len(ck["C5"]["zero"]) == 3,
        "C6_costs_by_hand": ck["C6"]["ok"] is True,
        "C7_beta_truncation": ck["C7"]["ok"] is True and ck["C7"]["compared"] >= 3 * (8 + 2),
        "C8_memory_files_pins": up_ok and st.get("max_rss_mb") is not None,
        "C9_compliance_completed": res["status"] == "completed" and not res["provenance"].get("failure_stage"),
        "no_sys1_arm_result": ck["sys1_arm_result_computed"] is False and not any(x.startswith("QRSY|") for x in ls),
        "host_all_in_host": ck["all_in_host"] is True,
    }
    return checks, dict(usmv_c4=c4_ok["usmv"], etf_ids=ids)


def main(exp=P.CANARY):
    up_ok, up = uploaded(exp)
    res = json.loads((ROOT / "experiments" / exp / "result.json").read_text())
    ls = lines(exp)
    st = json.loads(joined(ls, "QRG"))
    checks, extra = assess(st, ls, res, up_ok)
    out = dict(experiment=exp, decision=P.DECISION, upload=dict(ok=up_ok, **up), checks=checks,
               passed=sum(bool(v) for v in checks.values()), total=len(checks), all_pass=all(checks.values()),
               usmv_verified=extra["usmv_c4"], etf_ids=extra["etf_ids"], canary=st["canary"], y_etf=st["y_etf"],
               pit_audit=st.get("pit_audit"), memory=dict(stages=st.get("memory"), ru_maxrss_mb=st.get("max_rss_mb")),
               feature_panel_sha256=st["feature_panel_sha256"], response_panel_sha256=st["response_panel_sha256"],
               wall_s=st.get("wall_s"))
    path = HERE / f"SYS1_canary_{exp}.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(dict(checks=checks, passed=out["passed"], total=out["total"], all_pass=out["all_pass"],
                          usmv_verified=out["usmv_verified"], rss_mb=st.get("max_rss_mb"),
                          sha256=hashlib.sha256(path.read_bytes()).hexdigest()), indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
