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
    for t in ("NEA", "NVG", "NZF", "DSL", "BCAT", "UTG", "BPL", "OAK"):
        assert harness.non_common_reason(_fundamental(by[t]), "2020-01-02") is not None, t
    # MIC: LLC interests until its conversion to a corporation on 2015-05-21 (MIC 8-K)
    assert harness.non_common_reason(_fundamental(by["MIC"]), "2015-05-20") is not None
    assert harness.is_us_common(_fundamental(by["MIC"]), "2015-05-21")
    assert harness.is_us_common(_fundamental(by["MIC"]), "2021-10-08")


# D065: every dated override, tested on both sides of its boundary with the real Morningstar fields
DATED = [  # (sid, ticker, last excluded day or None, first eligible day or None)
    ("KKR UO9UUQST4HUT", "KKR", "2018-06-30", "2018-07-01"),
    ("APO UVBW6V6CV59H", "APO", "2019-09-04", "2019-09-05"),
    ("ARES VQ7JWF5X8XGL", "ARES", "2018-11-25", "2018-11-26"),
    ("BX TTO1M4GXI99H", "BX", "2019-06-30", "2019-07-01"),
    ("CG V69R09HVGXGL", "CG", "2019-12-31", "2020-01-01"),
    ("TPL R735QTJ8XC9X", "TPL", "2021-01-10", "2021-01-11"),
    ("YHOO R735QTJ8XC9X", "AABA", "2017-06-16", "2017-06-15"),     # eligible BEFORE, fund from 2017-06-16
    ("KFN T9R86261T0F9", "KFN", "2013-03-01", None),
]


@pytest.mark.parametrize("sid,ticker,excluded_on,eligible_on", DATED, ids=[d[1] for d in DATED])
def test_dated_overrides(harness, sid, ticker, excluded_on, eligible_on):
    import json as _json
    rec = next(c for c in _json.loads((ROOT / "tests/fixtures/universe_override_cases.json").read_text())["cases"]
               if c["sid"] == sid)
    f = _fundamental(rec)
    assert not harness.is_us_common(f, excluded_on), (ticker, excluded_on)
    if eligible_on:
        assert harness.is_us_common(f, eligible_on), (ticker, eligible_on)


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
