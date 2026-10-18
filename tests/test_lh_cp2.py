"""LH-CP2 (owner D243): offline fiscal-calendar anomaly investigation. The 2021-12-31 cut-off is enforced inside the
loaders before any record is visible; outputs carry no later date."""
import importlib.util
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research/longhorizon/cp2"))
import lh_cp2_safe as SAFE  # noqa: E402


def test_companyfacts_filter_drops_post_cutoff():
    cf = {"facts": {"us-gaap": {"NetIncomeLoss": {"units": {"USD": [
        dict(start="2021-07-01", end="2021-09-30", val=1, filed="2021-11-01", accn="a", fp="Q3", fy=2021),
        dict(start="2021-10-01", end="2021-12-31", val=2, filed="2022-02-01", accn="b", fp="FY", fy=2021),
        dict(start="2022-01-01", end="2022-03-31", val=3, filed="2022-05-01", accn="c", fp="Q1", fy=2022)]}}}}}
    out = SAFE.filter_companyfacts(cf)
    vals = out["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]
    assert [f["accn"] for f in vals] == ["a"]
    SAFE.assert_no_post_cutoff(out)


def test_submission_filter_drops_post_cutoff():
    rows = [dict(filingDate="2021-12-30", reportDate="2021-09-30", form="10-Q"),
            dict(filingDate="2022-01-05", reportDate="2021-12-31", form="8-K"),
            dict(filingDate="2021-12-31", reportDate="2022-01-02", form="10-Q")]
    out = SAFE.filter_submission_rows(rows)
    assert [r["filingDate"] for r in out] == ["2021-12-30"]


def test_assert_no_post_cutoff_raises():
    with pytest.raises(AssertionError):
        SAFE.assert_no_post_cutoff({"x": ["2019-01-01", {"y": "2026-07-30"}]})
    SAFE.assert_no_post_cutoff({"x": ["2019-01-01", "2021-12-31"]})


@pytest.mark.skipif(not (ROOT / "data/sec_cache").exists(), reason="SEC cache not present")
def test_real_cache_loaders_enforce_cutoff():
    c = SAFE.client()
    rows = SAFE.submissions(c, 320193)
    cf = SAFE.companyfacts(c, 320193)
    if rows is not None:
        assert all(r["filingDate"] <= SAFE.CUT for r in rows)
        SAFE.assert_no_post_cutoff([{k: r.get(k) for k in ("filingDate", "reportDate")} for r in rows])
    if cf is not None:
        SAFE.assert_no_post_cutoff(cf)
    assert c.fetched == 0


import hashlib  # noqa: E402

PROTOCOL_SHA256 = "f7cbac944e433fcda235b6c5e1c98cd2c62e486805c4b6cdaf98bc7e18819ed9"


def test_protocol_hash_pinned():
    p = ROOT / "research/longhorizon/cp2/LH_CP2_protocol.md"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == PROTOCOL_SHA256


def test_stage_c_protocol_unchanged():
    p = ROOT / "research/longhorizon/stage_c/LH_StageC_protocol.md"
    assert hashlib.sha256(p.read_bytes()).hexdigest().startswith("ff97789b02007599")


_spec = importlib.util.spec_from_file_location("lh_cp2_inv", ROOT / "research/longhorizon/cp2/LH_CP2_investigation.py")
INV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(INV)


def test_code_groups_match_committed_bands():
    assert INV.code_group(["1231", "1231", "1231"]) == "EQUAL"
    assert INV.code_group(["0926", "0927", "0925"]) == "S7"            # 52/53-week drift
    assert INV.code_group(["0131", "0102", "0131"]) == "S31"
    assert INV.code_group(["1231", "0930", "1231"]) == "QA"            # ~3 months
    assert INV.code_group(["1231", "0630", "1231"]) == "QA"            # ~6 months
    assert INV.code_group(["1231", "0531", "1231"]) == "OTHER"
    assert INV.code_group(["1231", None, "1231"]) == "NOCODE"


# Illustrative label histories, newest first (q0 .. q12); 4 = FY
CAL = [2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4, 3, 2]                     # regular calendar-quarter filer, q0 = Q2


def test_label_status_regular_and_52_53_week():
    assert INV.label_status(CAL) == "consistent"                   # a 52/53-week filer has the same labels


def test_label_status_fiscal_year_change_is_broken():
    shifted = [3, 2, 1, 4, 2, 1, 4, 3, 2, 1, 4, 3, 2]              # fiscal year moved: labels re-based mid-chain
    assert INV.label_status(shifted) == "broken"


def test_label_status_unknown():
    assert INV.label_status(CAL[:6] + [None] + CAL[7:]) == "unknown"


def test_categories_first_match():
    assert INV.categorize("OTHER", True, False, False, "consistent") == "F"
    assert INV.categorize("OTHER", False, True, False, "consistent") == "D"
    assert INV.categorize("OTHER", False, False, True, "consistent") == "E"
    assert INV.categorize("OTHER", False, False, False, "broken") == "B"
    assert INV.categorize("OTHER", False, False, False, "unknown") == "G"
    assert INV.categorize("S7", False, False, False, "consistent") == "A"
    assert INV.categorize("OTHER", False, False, False, "consistent") == "C"
    assert INV.categorize("QA", False, False, False, "consistent") == "C"


def test_rule_v_outcomes():
    assert INV.rule_v("consistent", False, False) == "valid"
    assert INV.rule_v("broken", False, False) == "invalid"
    assert INV.rule_v("consistent", True, False) == "invalid"       # transition form inside the history
    assert INV.rule_v("consistent", False, True) == "invalid"       # quarter mapped to the wrong filing
    assert INV.rule_v("unknown", False, False) == "unknown"         # excluded (conservative)


OUT2 = ROOT / "research/longhorizon/cp2/LH_CP2_investigation.json"


@pytest.mark.skipif(not OUT2.exists(), reason="LH-CP2 investigation not generated")
def test_investigation_output_safe_and_reproducing():
    import json
    d = json.loads(OUT2.read_text())
    assert d["protocol_sha256"] == PROTOCOL_SHA256 and d["network_requests"] == 0
    assert d["returns_computed"] is False and d["holdout_accessed"] is False
    assert d["p1_reproduction"]["identical_to_committed"] and d["p2_reproduction"]["identical_to_stage_c"]
    SAFE.assert_no_post_cutoff(d)


sys.path.insert(0, str(ROOT / "research/longhorizon/cp2"))
import lh_cp2_rule_proposal as RP  # noqa: E402

REG = [2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4, 3, 2]                     # calendar-quarter or 52/53-week filer, q0 = Q2


def test_proposed_rule_regular_and_52_53_week_valid():
    assert RP.proposed_validity(REG) == ("valid", ())


def test_proposed_rule_isolated_mis_tag_is_valid_flagged():
    mis = [2, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4, 3]                 # q0 tagged Q2 although its cycle position is Q3
    out, flags = RP.proposed_validity(mis)
    assert out == "valid" and "isolated_tag_error" in flags


def test_proposed_rule_fiscal_change_invalid():
    rebased = [3, 2, 1, 4, 2, 1, 4, 3, 2, 1, 4, 3, 2]             # labels re-based for 4 periods: fiscal year moved
    assert RP.proposed_validity(rebased)[0] == "invalid"


def test_proposed_rule_transition_and_mapping_invalid():
    assert RP.proposed_validity(REG, transition=True) == ("invalid", ("transition_form",))
    assert RP.proposed_validity(REG, mapping_fail=True) == ("invalid", ("mapping",))


def test_proposed_rule_unknown_strict_vs_assume():
    pre_xbrl = REG[:8] + [None] * 5                              # oldest five quarters filed before XBRL
    assert RP.proposed_validity(pre_xbrl)[0] == "unknown"
    out, flags = RP.proposed_validity(pre_xbrl, variant="assume")
    assert out == "valid" and "labels_assumed" in flags
    assert RP.proposed_validity([None] * 13, variant="assume")[0] == "unknown"
