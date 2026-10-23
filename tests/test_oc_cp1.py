"""OC-CP1 (owner D246): documentation-only checkpoint for the H028 offensive complement. Checks completeness and that
no hypothesis was activated and no frozen result changed."""
import hashlib
import re

from conftest import ROOT

CP = ROOT / "docs/checkpoints/OC_CP1_h028_offensive_complement_candidate_selection_test_design.md"


def test_checkpoint_complete():
    cp = CP.read_text()
    assert [int(m) for m in re.findall(r"^## (\d+)\. ", cp, re.M)] == list(range(1, 25))
    for s in ("OC-1", "OC-B", "SYS-1", "STOPPED", "beta-matched", "NOT SUPPORTED", "DEVELOPMENT-CONSISTENT"):
        assert s in cp


def test_records_and_no_new_active_hypothesis():
    assert "| D246 |" in (ROOT / "DECISIONS.md").read_text()
    st = (ROOT / "research/hypotheses/STATUS.md").read_text()
    # H031 was later drafted but never registered (D268); H032 was registered and closed (D285)
    assert all("never registered" in ln for ln in st.splitlines() if ln.startswith("| H031 |"))
    assert "Still no active hypothesis" in st.split("D246")[-1]
    assert "| 5 | 2026-10-18 | D246 |" in (ROOT / "research/longhorizon/SELECTION_LEDGER.md").read_text()
    assert (ROOT / "docs/owner/2026-10-18_h028_offensive_complement_direction.md").exists()
    assert not (ROOT / "HOLDOUT_UNLOCK.md").exists()


def test_frozen_protocols_unchanged():
    pins = {"research/longhorizon/stage_c/LH_StageC_protocol.md": "ff97789b",
            "research/longhorizon/cp2/LH_CP2_protocol.md": "f7cbac94",
            "research/longhorizon/cp3/LH_CP3_protocol.md": "38d790e5",
            "research/longhorizon/cp3/lh_cp3_rules.py": "9a72c5c8"}
    for p, h in pins.items():
        assert hashlib.sha256((ROOT / p).read_bytes()).hexdigest().startswith(h)
