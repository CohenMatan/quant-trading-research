"""OC-CP2 (owner D247): documentation-only independent offensive stock-selection candidate review. Checks completeness,
the 18-item test specification, the analytical power artifact, and that no hypothesis was activated and no frozen
result changed."""
import hashlib
import json
import re
import subprocess
import sys

from conftest import ROOT

CP = ROOT / "docs/checkpoints/OC_CP2_independent_offensive_stock_selection_candidate_review.md"
POWER = ROOT / "research/longhorizon/oc_cp2/OC_CP2_power.json"


def test_checkpoint_complete():
    cp = CP.read_text()
    assert [int(m) for m in re.findall(r"^## (\d+)\. ", cp, re.M)] == list(range(1, 16))
    spec = cp.split("## 10. ")[1].split("## 11. ")[0]
    assert [int(m) for m in re.findall(r"^\| (\d+) \| ", spec, re.M)] == list(range(1, 19))
    for s in ("OC-2", "SYS-1", "SPY", "STOP", "Stage B-OC2", "D245 does not apply", "2012-02", "118",
              "Fama–MacBeth", "D235, D238, D239", "supersede"):
        assert s in cp


def test_power_artifact_reproducible(tmp_path):
    before = POWER.read_bytes()
    subprocess.run([sys.executable, str(ROOT / "research/longhorizon/oc_cp2/OC_CP2_power.py")], check=True,
                   cwd=ROOT, capture_output=True)
    assert POWER.read_bytes() == before
    d = json.loads(before)
    assert d["window"]["first_review"] == "2012-02" and d["window"]["reviews"] == 118
    k = "main 2012-02 -> 2021-11 (118) | sigma_ic main 0.09 | rho 0.1 | two-sided 2% (one-sided 1%)"
    assert abs(d["mde_80"][k]["top_quintile_80_naive"] - 0.0321) < 1e-4
    assert abs(d["power"][k]["3%"]["structure"] - 0.452) < 1e-3


def test_records_and_no_new_active_hypothesis():
    assert "| D247 |" in (ROOT / "DECISIONS.md").read_text()
    st = (ROOT / "research/hypotheses/STATUS.md").read_text()
    # H031 was later drafted but never registered (D268); H032 was registered and closed (D285)
    assert all("never registered" in ln for ln in st.splitlines() if ln.startswith("| H031 |"))
    assert "Still no active hypothesis" in st.split("D247")[-1]
    assert "| 6 | 2026-10-18 | D247 |" in (ROOT / "research/longhorizon/SELECTION_LEDGER.md").read_text()
    assert (ROOT / "docs/owner/2026-10-18_independent_offensive_stock_selection.md").exists()
    assert not (ROOT / "research/hypotheses/H031.md").exists()
    assert not (ROOT / "HOLDOUT_UNLOCK.md").exists()


def test_frozen_inputs_unchanged():
    pins = {"research/longhorizon/stage_c/LH_StageC_protocol.md": "ff97789b",
            "research/longhorizon/cp2/LH_CP2_protocol.md": "f7cbac94",
            "research/longhorizon/cp3/LH_CP3_protocol.md": "38d790e5",
            "research/longhorizon/cp3/lh_cp3_rules.py": "9a72c5c8"}
    for p, h in pins.items():
        assert hashlib.sha256((ROOT / p).read_bytes()).hexdigest().startswith(h)
    ex = json.loads((ROOT / "research/longhorizon/STAGE_C_EXCEPTION_D245.json").read_text())
    assert ex["decision"] == "D245" and ex["decision_years"] == list(range(2015, 2022))
