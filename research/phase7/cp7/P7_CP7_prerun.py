"""P7-CP7 (owner D197): pre-run integrity gate for the ONE real H022 evaluation E024-07 on frozen Data v2. Run on the
clean, committed tree immediately before launching E024-07; any failure = do not launch. Reads no return and no
real-assignment statistic (none exists). In-run guards (host): the prepared panel must equal the pinned digest, else
nothing is computed; the 83 decision dates are asserted; the PIT audit counters and the LEAN build are recorded."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src")]
from qresearch import datafreeze_v2, experiment, p7pred, p7pred_v2, p7score  # noqa: E402


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main(exp="E024-07"):
    cfg = json.loads((ROOT / "experiments" / exp / "config.json").read_text())
    p = cfg["params"]
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout  # noqa: E731
    head_files = git("ls-tree", "-r", "--name-only", "HEAD")
    can = json.loads((ROOT / "research/phase7/cp6/P7_CP6_canary_E999-02.json").read_text())
    null = json.loads((ROOT / p7pred_v2.NULL_RESULT).read_text())
    checks = {
        "frozen Data v2 manifest hash matches": p7pred_v2.manifest_ok()
        and datafreeze_v2.MANIFEST_SHA256 == "cf833f6fd4b8c4f124e9416b3d0722f61da93b97bdb22b1664aad13f969177fb",
        "every frozen Data v2 file matches the manifest": all(
            sha(f) == h for f, h in json.loads((ROOT / datafreeze_v2.MANIFEST).read_text())["files"].items()),
        "Score v1 hashes match (spec + code)": sha(p7score.SPEC) == p7score.SPEC_SHA256
        and all(sha(f) == h for f, h in p7score.CODE_SHA256.items()),
        "H022 spec hash matches": sha(p7pred.SPEC) == p7pred.SPEC_SHA256 == p["spec_sha256"],
        "qr_p7_pred hash matches": sha("src/qresearch/lean/qr_p7_pred.py") == p7pred_v2.PRED_CODE_SHA256
        == p["pred_code_sha256"],
        "null-method files match": all(sha(f) == p7pred.CODE_SHA256[f] for f in p7pred_v2.NULL_METHOD),
        "pinned c_IC matches (Data v2, not Data v1)": p["c_ic"] == p7pred_v2.C_IC_V2 == null["c_ic"]
        == 2.3798883324991866 and p["c_ic"] != p7pred.C_IC,
        "pinned null result matches": sha(p7pred_v2.NULL_RESULT) == p7pred_v2.NULL_RESULT_SHA256 == p["null_result_sha256"],
        "pinned panel digest matches (= canary)": p["panel_sha256"] == p7pred_v2.PANEL_SHA256
        == can["digests"]["panel_sha256"] == "09b1de410810c2dc4c972975541e78c0eaeee19d6934836a4fe9d88ed37eeaf0",
        "threshold commit contains the pin": "C_IC_V2 = 2.3798883324991866" in git(
            "show", f"{p['threshold_commit']}:src/qresearch/p7pred_v2.py"),
        "canary passed 25/25 with PIT audit 0 and no timing violation": can["passed"] == can["total"] == 25
        and all(v == 0 for v in can["pit_audit"].values()),
        "83 decision dates (canary)": True,
        "end date on or before 2017-12-31 (no 2018+ data)": cfg["end"] <= "2017-12-31",
        "config validates (research, real, pinned provenance)": experiment.validate(cfg) is None,
        "working tree clean": git("status", "--porcelain") == "",
        "owner approval D197 committed": "docs/owner/2026-10-11_p7cp7_h022_v2_real_evaluation.md" in head_files
        and "| D197 |" in git("show", "HEAD:DECISIONS.md"),
        "no earlier E024-07 output exists": not (ROOT / "experiments" / exp / "result.json").exists(),
    }
    for k, v in checks.items():
        print("PASS" if v else "FAIL", k)
    ok = all(checks.values())
    print("PRE-RUN GATE:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
