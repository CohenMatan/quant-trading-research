"""OC-2 Stage 1 (owner D248): pure metadata rules of the integrity audit, the frozen protocol hash and the committed
result's internal consistency. No data access beyond committed files."""
import hashlib
import json
import sys

from conftest import ROOT

sys.path[:0] = [str(ROOT / "research/longhorizon/oc2/stage1"), str(ROOT / "src")]
import OC2_S1_audit as A  # noqa: E402
from qresearch import data_v3 as V3  # noqa: E402

PROTO = ROOT / "research/longhorizon/oc2/stage1/OC2_S1_protocol.md"
OUT = ROOT / "research/longhorizon/oc2/stage1/OC2_S1_audit.json"


def test_protocol_frozen():
    assert hashlib.sha256(PROTO.read_bytes()).hexdigest() == A.PROTOCOL_SHA


def test_window_regularity():
    assert A.regular(364) and A.regular(371) and A.regular(365) and A.regular(366)
    assert not A.regular(355) and not A.regular(380) and not A.regular(None)


def test_annual_positions():
    ch = [500, 410, 320, 230, 140, 50, -40, -130]
    ann = {320: True, -40: True}
    assert A.annual_positions(ch, ann) == ([2, 6], True)
    assert A.annual_positions(ch, {320: True, 50: True})[1] is False      # 3 apart: fiscal-year change
    assert A.annual_positions(ch, {320: True})[1] is False                 # one annual report only


def test_classify_order():
    assert A.classify(364, 364, True, False, False) == "COMPARABLE"
    assert A.classify(364, None, True, False, False) == "COMPARABLE"
    assert A.classify(364, 364, False, False, False) == "FY_CHANGE_WINDOW_VALID"
    assert A.classify(364, 364, True, True, False) == "FY_CHANGE_WINDOW_VALID"
    assert A.classify(340, 364, True, False, False) == "NON_COMPARABLE_RISK"
    assert A.classify(364, 390, False, True, False) == "NON_COMPARABLE_RISK"
    assert A.classify(364, 364, True, False, True) == "NON_COMPARABLE_RISK"


def _facts(rows):
    fx = V3.Facts({})
    for end, start, filed, cls in rows:
        fx.flows["net_income"].setdefault(V3.dn(end), []).append(
            (V3.dn(filed), "a", 0, V3.dn(start), cls, 0.0))
    return fx


def test_q_method_from_dates_only():
    fx = _facts([("2015-03-31", "2015-01-01", "2015-05-01", 1),
                 ("2015-12-31", "2015-01-01", "2016-02-20", 4), ("2015-09-30", "2015-01-01", "2015-11-01", 3)])
    p = V3.dn("2015-03-31")
    assert A.q_method(fx, p, V3.dn("2015-05-02")) == "direct"
    assert A.q_method(fx, p, V3.dn("2015-04-30")) == "none"               # not yet filed
    q4 = V3.dn("2015-12-31")
    assert A.q_method(fx, q4, V3.dn("2016-03-01")) == "ytd4"              # FY minus nine months
    fx2 = _facts([("2015-12-31", "2015-01-01", "2016-02-20", 4)])
    assert A.q_method(fx2, q4, V3.dn("2016-03-01")) == "none"             # no matching nine-month piece


def test_committed_result_consistent():
    if not OUT.exists():
        return
    d = json.loads(OUT.read_text())
    assert d["protocol_sha256"] == A.PROTOCOL_SHA and d["decision"] == "D248"
    assert d["pit_violations"] == 0 or d["gates"]["G-PIT"] == "FAIL"
    vals = set(d["gates"].values())
    exp = ("FAIL — NOT SUPPORTED" if "FAIL" in vals else
           "CONDITIONAL" if "CONDITIONAL" in vals else "PASS — PIT-SAFE AND SUFFICIENT")
    assert d["classification"] == exp
    s = json.dumps(d)
    for banned in ("return", "ic_", "rank_ic", "sharpe", "wealth"):
        assert f'"{banned}' not in s.lower()
