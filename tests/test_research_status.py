"""D240: the hypothesis status index records the closed state, so later sessions never restart H026-H030."""
from conftest import ROOT

STATUS = ROOT / "research/hypotheses/STATUS.md"


def _row(hid):
    return next(l for l in STATUS.read_text().splitlines() if l.startswith(f"| {hid} |"))


def test_status_index_lists_every_hypothesis():
    text = STATUS.read_text()
    for h in ["H001", "H005", "H013", "H014", "H016", "H017", "H018", "H019", "H020"] + [f"H0{n}" for n in range(22, 31)]:
        assert f"| {h} " in text, h


def test_closed_phase13_14_statuses():
    for h in ("H026", "H027", "H028"):
        assert "REJECTED" in _row(h)
    for h in ("H029", "H030"):
        r = _row(h)
        assert "NOT EVALUABLE" in r and "BLOCKED" in r and "REJECTED" not in r.replace("never REJECTED", "")
    assert "No Production Candidate Found" in STATUS.read_text()


def test_closure_documents_exist():
    for p in ("docs/checkpoints/RC1_research_cycle_closure_phases_13_14.md",
              "docs/checkpoints/RM1_long_term_defensive_offensive_equity_roadmap.md",
              "docs/owner/2026-10-18_close_phases_13_14_roadmap.md"):
        assert (ROOT / p).exists(), p
    assert not (ROOT / "HOLDOUT_UNLOCK.md").exists()


def test_d241_design_documents_and_h028_designation():
    assert "REJECTED" in _row("H028") and "Frozen Defensive Research Reference" in _row("H028")
    for p in ("docs/checkpoints/RM2_h028_defensive_reference_offensive_companion_design.md",
              "docs/owner/2026-10-18_h028_defensive_reference_offensive_companion.md",
              "research/longhorizon/SELECTION_LEDGER.md"):
        assert (ROOT / p).exists(), p
    rm2 = (ROOT / "docs/checkpoints/RM2_h028_defensive_reference_offensive_companion_design.md").read_text()
    assert all(f"## {n}." in rm2 for n in range(1, 26))
