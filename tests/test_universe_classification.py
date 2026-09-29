"""D057: only operating-company US common stock passes the universe filter."""
import json
import types

import pytest

from conftest import ROOT

CASES = json.loads((ROOT / "tests/fixtures/universe_classification_cases.json").read_text())["cases"]


def _fundamental(c):
    ns = types.SimpleNamespace
    return ns(symbol=ns(id=c["sid"]),
              security_reference=ns(security_type="ST00000001", is_depositary_receipt=False, is_primary_share=True,
                                    share_class_description=c["share_class_description"]),
              company_reference=ns(country_id="USA", is_limited_partnership=c["is_limited_partnership"],
                                   is_limited_liability_company=c["is_limited_liability_company"],
                                   industry_template_code=c["industry_template_code"]),
              asset_classification=ns(sic=c["sic"]))


@pytest.fixture
def harness(monkeypatch):
    from test_commission import _load_harness
    return _load_harness(monkeypatch)


@pytest.mark.parametrize("case", CASES, ids=[f"{c['ticker']}-{c.get('day', 'any')}" for c in CASES])
def test_known_securities_are_classified(harness, case):
    ok = harness.is_us_common(_fundamental(case), case.get("day", "2015-01-02"))
    assert ok == (case["expected"] == "eligible"), (case["ticker"], harness.non_common_reason(_fundamental(case), case.get("day")))


def test_named_owner_examples_are_excluded(harness):
    by = {c["ticker"]: c for c in CASES if "day" not in c}
    for t in ("MIC", "NEA", "NVG", "NZF", "DSL", "BCAT", "UTG", "BPL", "OAK"):
        assert harness.non_common_reason(_fundamental(by[t]), "2020-01-02") is not None, t


def test_acquired_corporations_flagged_llc_today_stay_eligible(harness):
    """Morningstar's LLC flag reflects the current (post-acquisition) entity; excluding these
    would delete acquired companies from history (a survivorship bias)."""
    by = {c["ticker"]: c for c in CASES}
    for t in ("VMW", "S", "BNI", "LVLT", "MOLX", "P", "HOT"):
        assert by[t]["is_limited_liability_company"] and harness.is_us_common(_fundamental(by[t]), "2015-01-02"), t


def test_structural_rules_still_apply(harness):
    c = dict(CASES[0], sid="X", is_limited_partnership=False, is_limited_liability_company=False,
             industry_template_code="N", sic=2834, share_class_description="Some Company Inc")
    f = _fundamental(c)
    assert harness.is_us_common(f, "2015-01-02")
    f.security_reference.is_depositary_receipt = True
    assert not harness.is_us_common(f, "2015-01-02")
    f.security_reference.is_depositary_receipt = False
    f.security_reference.is_primary_share = False
    f.company_reference.country_id = "CAN"
    assert not harness.is_us_common(f, "2015-01-02")            # D030 unchanged
    for sic in (6726, 6770, 6792):
        g = _fundamental(dict(c, sic=sic))
        assert harness.non_common_reason(g, "2015-01-02") is not None


def test_universe_selection_passes_the_date():
    src = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert "if not is_us_common(f, day):" in src
