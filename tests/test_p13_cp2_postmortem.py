"""P13-CP2 (owner D221): the descriptive post-mortem is a deterministic transformation of committed artifacts; its
yearly numbers equal the committed P13-CP1 result; monthly log-relatives sum to the yearly ones; the classification
follows the pre-registered rules; H028 stays rejected."""
import json
import math
import sys

import pytest

from conftest import ROOT

PM = ROOT / "research/phase13/cp2/P13_CP2_postmortem.json"


def _pm():
    return json.loads(PM.read_text())


def test_reproducible_from_committed_artifacts(tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT / "research/phase13/cp2"))
    import P13_CP2_postmortem as M
    monkeypatch.setattr(M, "HERE", tmp_path)
    M.main()
    assert json.loads((tmp_path / "P13_CP2_postmortem.json").read_text()) == _pm()


def test_consistent_with_the_committed_h028_result():
    pm = _pm()
    r = json.loads((ROOT / "research/phase13/cp1/P13_CP1_result.json").read_text())
    assert r["status"].startswith("H028 REJECTED") and r["gates"]["B4"] is False
    for y in ("2015", "2016", "2017"):
        for n in ("h028", "h027", "spy", "lv15"):
            assert pm["yearly"][y][n] == pytest.approx(r["years"][y][n], abs=1e-12)
    assert pm["compounded"]["2015-2017"]["log_h028_vs_lv15"] == pytest.approx(r["gates"]["B4_detail"]["L_2015_2017"], abs=1e-12)


def test_monthly_logs_sum_to_years_and_rules_hold():
    pm = _pm()
    for y in ("2015", "2016", "2017"):
        s = sum(m["log_h028_vs_lv15"] for m in pm["monthly"] if m["month"][:4] == y)
        assert s == pytest.approx(pm["yearly"][y]["log_h028_vs_lv15"], abs=1e-12)
    c = pm["concentration"]
    for w, v in c.items():
        assert v["months_h028_ahead"] + v["months_h028_behind"] + v["months_approx_equal"] == v["months"]
        exp = ("C" if v["cost_gap_upper_bound_share"] >= 0.5 else
               "A" if v["share_worst_3"] >= 0.75 and v["share_months_behind"] <= 0.5 else
               "B" if v["share_months_behind"] >= 0.6 and v["share_worst_3"] < 0.75 else "E")
        assert v["label"] == exp
    ri = pm["rule_inputs"]
    final = ("C" if ri["label_2015"] != ri["label_2016"] or ri["side_2015"] != ri["side_2016"]
             else ri["label_2015_2016"] if ri["label_2015_2016"] in ("A", "B") else "D")
    assert pm["final_conclusion"] == final
    assert all(v.startswith("NOT AVAILABLE") for v in pm["unavailable"].values())
    cf = pm["coefficients"]
    for k, v in cf.items():
        b = v["beta"]
        s = sum(abs(x) for x in b.values())
        assert v["override_capacity_R"] == pytest.approx((s - abs(b["LOWVOL"])) / abs(b["LOWVOL"]))
        assert math.isclose(sum(abs(x) for x in v["emphasis"].values()), 1.0)
