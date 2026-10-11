"""P11-CP2 (owner D211): the descriptive H026 post-mortem is internally consistent with the committed P11-CP1 result and
the pinned null, reads no period after 2021-12-31, and leaves H026's status, pins and Data v2.1 untouched."""
import json
import math

import pytest

from conftest import ROOT
from qresearch import datafreeze_v21, p11h026 as P

PM = ROOT / "research/phase11/cp2/P11_CP2_postmortem.json"


@pytest.fixture(scope="module")
def pm():
    return json.loads(PM.read_text())


def test_status_and_pins_unchanged(pm):
    assert pm["status"].startswith("H026 REMAINS REJECTED")
    assert pm["gates"]["D1"] is False and pm["gates"]["D3"] is False and pm["gates"]["all"] is False
    assert pm["c_wealth"] == P.C_WEALTH and P.CANDIDATE is None
    assert datafreeze_v21.manifest_sha() == datafreeze_v21.MANIFEST_SHA256      # Data v2.1 not changed (D211)
    assert pm["governance"]["owner_approval_exists"] is False


def test_annual_attribution_sums_to_s_wealth(pm):
    c = pm["path"]["annual_log_contribution"]
    assert set(c) == {str(y) for y in range(2015, 2022)} | {"final_liquidation_costs"}
    assert abs(sum(c.values()) - pm["gates"]["S_WEALTH"]) < 1e-12
    a = pm["path"]["annual"]
    assert [y for y, v in sorted(a.items()) if v["beat_spy"]] == ["2017", "2018", "2020"]
    assert math.isclose(a["2021"]["end_relative_wealth"] * math.exp(c["final_liquidation_costs"]),
                        math.exp(pm["gates"]["S_WEALTH"]), rel_tol=1e-12)


def test_monthly_path_inside_development_window(pm):
    m = pm["path"]["monthly"]
    assert len(m) == 84 and m[0]["month"] == "2015-01" and m[-1]["month"] == "2021-12"
    assert all(x["month"] < "2022-01" for x in m)
    assert pm["path"]["rolling"]["3m"]["windows"] == 82 and pm["path"]["rolling"]["24m"]["windows"] == 61


def test_null_counts_match_the_pinned_null(pm):
    n = pm["null"]
    assert n["worlds"] == 5000
    assert n["joint"]["D1"] == 49                                   # S > c_WEALTH (c = the 50th largest)
    assert n["joint"]["wealth_ge_real"] == 99
    null = json.loads((ROOT / "research/phase11/cp1/P11_CP1_null.json").read_text())
    assert n["distributions"]["S_WEALTH"]["p50"] == pytest.approx(null["S_WEALTH"]["median"])
    assert sum(n["distributions"]["years_beating"]["histogram"].values()) == 5000


def test_coefficients_match_the_real_result(pm):
    r = json.loads((ROOT / "research/phase11/cp1/P11_CP1_result.json").read_text())
    for y, v in pm["coefficients"]["years"].items():
        assert v["lam"] == r["years"][y]["lam"]
        assert v["beta"] == pytest.approx(r["years"][y]["beta"])
    assert pm["coefficients"]["lambda_frequency"] == {"0.01": 1, "0.1": 0, "1.0": 0, "10.0": 0, "100.0": 6}
