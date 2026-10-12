"""P13-CP4 (owner D225): the objective-alignment review is a deterministic, descriptive transformation of committed
artifacts. Synthetic mechanics checks (captures, rolling windows, decomposition, patterns, rules) plus consistency of the
committed output with P13-CP3 and with its own pre-registered rules; H028 stays rejected."""
import json
import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research/phase13/cp4"))
import P13_CP4_alignment as M  # noqa: E402

OUT = ROOT / "research/phase13/cp4/P13_CP4_alignment.json"


def test_capture_and_asymmetry_mechanics():
    s = np.array([0.02, 0.04, -0.02, -0.04])
    h = np.array([0.02, 0.04, -0.01, -0.02])
    up, dn = s > 0, s < 0
    assert M.capture(h[up], s[up]) == pytest.approx(1.0)
    assert M.capture(h[dn], s[dn]) == pytest.approx(0.5)
    assert M.asym(1.0, 0.5)["value"] == pytest.approx(2.0)
    assert M.asym(1.0, 0.01)["value"] is None
    assert M.asym(1.0, -0.5)["flag"] == "ROSE ON AVERAGE WHEN SPY FELL"
    assert M.participation(1.0).startswith("STRONG") and M.participation(0.9).startswith("NEAR")
    assert M.participation(0.8999).startswith("MATERIAL")


def test_rolling_windows_and_counts():
    months = [f"{2015 + i // 12}-{i % 12 + 1:02d}" for i in range(84)]
    h = np.full(84, 0.01)
    s = np.zeros(84)
    for n, w in ((12, 73), (36, 49), (60, 25)):
        r = M.rolling(h, s, n, months)
        assert r["windows"] == w and r["share_h_gt_spy"] == 1.0
        assert r["ratio"]["min"] == pytest.approx(1.01 ** n)
        assert r["annualised_excess"]["p50"] == pytest.approx(1.01 ** 12 - 1)
    assert M.rolling(h, s, 60, months)["windows_with_all_2018"] == 25


def test_pattern_rules():
    yrs = np.repeat(np.array(M.YEARS), 12)
    lm = np.zeros(84)
    lm[yrs == 2018] = 0.01
    lm[yrs == 2020] = 0.01
    lm[yrs == 2015] = -0.001
    p = M.pattern(lm, yrs, 0.95, 0.7, 0.1)
    assert p["C_holds"] and p["best_supported"] == "C" and p["A_criteria_hold"]
    lm = np.full(84, 0.001)
    p = M.pattern(lm, yrs, 0.95, 0.7, 0.1)
    assert not p["C_holds"] and p["best_supported"] == "A"
    assert M.pattern(lm, yrs, 0.80, 0.7, 0.1)["best_supported"] == "B"
    assert M.pattern(lm, yrs, 0.80, 0.95, 0.1)["best_supported"] == "NONE OF A-C"


def test_exclusion_drops_whole_years():
    months = [f"{2015 + i // 12}-{i % 12 + 1:02d}" for i in range(84)]
    yrs = np.array([int(m[:4]) for m in months])
    r = np.zeros((84, 3))
    r[:, 2] = np.where(np.arange(84) % 2 == 0, 0.01, -0.01)
    r[:, 0] = r[:, 2] * np.where(r[:, 2] > 0, 1.0, 0.5)
    r[:, 1] = r[:, 0]
    e = M.exclusion(r, yrs, (2018, 2020))
    assert e["months"] == 60 and e["up_capture"] == pytest.approx(1.0) and e["down_capture"] == pytest.approx(0.5)


@pytest.mark.skipif(not OUT.exists(), reason="result not yet computed")
def test_committed_output_consistent():
    o = json.loads(OUT.read_text())
    c = json.loads((ROOT / "research/phase13/cp3/P13_CP3_bootstrap.json").read_text())
    assert o["original_research_status"] == "H028 REJECTED"
    assert o["synthetic"]["horizons"]["30y"]["p_beat_spy"] == c["methods"]["year"]["summary"]["30y"]["p_beat_spy"]
    assert o["synthetic_conditional"]["digest_matches_committed"] is True
    d = o["decomposition"]
    assert d["LU"] + d["LD"] + d["L0"] == pytest.approx(d["T"])
    assert sum(v["total"] for v in d["per_year"].values()) == pytest.approx(d["T"])
    for y, v in o["years"]["per_year"].items():
        for n in ("h028", "spy", "lv15"):
            assert v[n] == pytest.approx(c["donor_years"][y][n], abs=1e-12)
    assert o["exclusions"]["full"]["sum_log_rel"] == pytest.approx(d["T"])
    dims = o["dimensions"]
    W = sum(v["label"] == "WEAK" for v in dims.values())
    assert W == o["weak_count"]
    exp = ("NOT OBJECTIVE-ALIGNED" if dims["C"]["label"] == "WEAK" or
           (dims["A"]["label"] == "WEAK" and dims["B"]["label"] == "WEAK") or W >= 3 else
           "OBJECTIVE-ALIGNED" if W == 0 and o["pattern"]["best_supported"] != "C" else "PARTIALLY OBJECTIVE-ALIGNED")
    assert o["objective_alignment"] == exp
    assert o["rolling_10y"] == "NOT AVAILABLE FROM REAL DEVELOPMENT HISTORY"
