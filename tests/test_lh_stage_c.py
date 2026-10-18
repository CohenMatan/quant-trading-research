"""Long-horizon Stage C (owner D242): the OF-A data / PIT feasibility audit protocol is frozen before any aggregate,
and the audit is non-return and Holdout-safe."""
import hashlib

from conftest import ROOT

PROTOCOL = ROOT / "research/longhorizon/stage_c/LH_StageC_protocol.md"
PROTOCOL_SHA256 = "ff97789b02007599f9e4bdb914dc8b56f50566c1d61e4015c2383a829a195a97"


def test_protocol_hash_pinned():
    assert hashlib.sha256(PROTOCOL.read_bytes()).hexdigest() == PROTOCOL_SHA256


import importlib.util  # noqa: E402
import json  # noqa: E402
from datetime import date, timedelta  # noqa: E402

import pytest  # noqa: E402

from qresearch import data_v3 as V3  # noqa: E402

_spec = importlib.util.spec_from_file_location("lh_stage_c_audit", ROOT / "research/longhorizon/stage_c/LH_StageC_audit.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
OUT = ROOT / "research/longhorizon/stage_c/LH_StageC_audit.json"


def _fact(start, end, val, filed, accn="a"):
    return dict(start=start, end=end, val=val, filed=filed, accn=accn)


def _cf(facts_ni, facts_rev=()):
    return {"facts": {"us-gaap": {"NetIncomeLoss": {"units": {"USD": list(facts_ni)}},
                                  "Revenues": {"units": {"USD": list(facts_rev)}}}}}


CF = _cf([
    _fact("2015-01-01", "2015-03-31", 10.0, "2015-05-01", "q1"),
    _fact("2015-01-01", "2015-06-30", 25.0, "2015-08-01", "h1"),          # year-to-date only -> Q2 = 25 - 10
    _fact("2015-01-01", "2015-09-30", 45.0, "2015-11-01", "n9"),
    _fact("2015-01-01", "2015-12-31", 70.0, "2016-02-20", "fy"),          # Q4 = FY - 9M = 25
    _fact("2015-01-01", "2015-03-31", 12.0, "2016-05-01", "recast"),      # later recast of Q1
])


@pytest.mark.parametrize("pe,d", [("2015-03-31", "2015-06-01"), ("2015-06-30", "2015-09-01"),
                                  ("2015-12-31", "2016-03-01"), ("2015-03-31", "2016-06-01"),
                                  ("2015-12-31", "2016-02-19")])
def test_q_detail_equals_frozen_q_known(pe, d):
    fx = V3.Facts(CF)
    p, dn = V3.dn(pe), V3.dn(d)
    v, method, mf = A.q_detail(fx, "net_income", p, dn)
    assert v == fx.q_known("net_income", p, dn)
    if v is not None:
        assert mf <= dn and method in ("direct", "ytd")


def test_q4_and_ytd_derivation():
    fx = V3.Facts(CF)
    assert A.q_detail(fx, "net_income", V3.dn("2015-06-30"), V3.dn("2015-09-01"))[:2] == (15.0, "ytd")
    assert A.q_detail(fx, "net_income", V3.dn("2015-12-31"), V3.dn("2016-03-01"))[:2] == (25.0, "ytd")
    assert A.q_detail(fx, "net_income", V3.dn("2015-12-31"), V3.dn("2016-02-19"))[0] is None   # FY not yet filed


def test_truncation_no_lookahead():
    """A value as known on day d is unchanged when every fact filed after d is removed (point-in-time)."""
    for d in ("2015-06-01", "2015-12-01", "2016-03-01", "2016-06-01"):
        dn = V3.dn(d)
        full = V3.Facts(CF)
        trunc = V3.Facts(CF, end=d)
        for pe in ("2015-03-31", "2015-06-30", "2015-09-30", "2015-12-31"):
            p = V3.dn(pe)
            assert A.q_detail(full, "net_income", p, dn)[0] == A.q_detail(trunc, "net_income", p, dn)[0]


def test_cut_off_drops_post_2021_facts():
    cf = _cf([_fact("2021-10-01", "2021-12-31", 5.0, "2022-02-01")])
    fx = V3.Facts(cf)
    assert A.q_detail(fx, "net_income", V3.dn("2021-12-31"), V3.dn("2022-06-01"))[0] is None


def test_release_matching_and_categories():
    p0, fd = date(2019, 3, 31), date(2019, 5, 3)
    rel = [(date(2019, 4, 25), dict(t=None, xbrl_numeric=0))]
    cls, cands, after = A.match_releases(p0, fd, rel)
    assert cls == "unambiguous" and len(cands) == 1 and after is None
    assert A.disclosure_category(cls, date(2019, 4, 25), None, fd, None) == 1
    rel2 = rel + [(date(2019, 5, 1), dict(t=None, xbrl_numeric=0))]
    assert A.match_releases(p0, fd, rel2)[0] == "ambiguous"
    assert A.disclosure_category("ambiguous", date(2019, 4, 25), None, fd, None) == 2
    assert A.match_releases(p0, fd, [(date(2019, 5, 6), {})])[0] == "release_after_filing"
    assert A.match_releases(p0, fd, [(date(2019, 3, 30), {})])[0] == "no_release_found"   # before period end
    assert A.disclosure_category("no_release_found", None, None, fd, None) == 3
    assert A.disclosure_category("unambiguous", fd, None, fd, None) == 2                     # same day, order unknown


def test_sessions_helpers():
    S = A.Sessions([date(2020, 1, 2), date(2020, 1, 3), date(2020, 1, 6), date(2020, 1, 7)])
    assert S.after(date(2020, 1, 3)) == date(2020, 1, 6)
    assert S.on_or_after(date(2020, 1, 4)) == date(2020, 1, 6)
    assert S.between(date(2020, 1, 2), date(2020, 1, 6)) == 2
    assert S.between(date(2020, 1, 6), date(2020, 1, 2)) == -2


@pytest.mark.skipif(not OUT.exists(), reason="Stage C audit not generated")
def test_output_is_aggregate_non_return_and_holdout_safe():
    d = json.loads(OUT.read_text())
    assert d["protocol_sha256"] == PROTOCOL_SHA256
    assert d["returns_computed"] is False and d["surprise_values_computed"] is False
    assert d["quantconnect_run"] is False and d["holdout_accessed"] is False and d["network_requests"] == 0
    assert d["pit"]["violations"] == 0
    text = OUT.read_text()
    assert "2022-" not in text and "2023-" not in text and "2026-" not in text
