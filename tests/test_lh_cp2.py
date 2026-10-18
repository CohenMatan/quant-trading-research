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
