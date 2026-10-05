"""H020 synthetic scenario fixtures A-J (P5-CP2 section 33): the implementation must reproduce the frozen expectations
exactly (conditions, disqualifiers, score, groups, states, key features, snapshot digest and raster hashes) and every
scenario must show what it was built to show (TARGET). SYNTHETIC ONLY."""
import json
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "research" / "phase5"))
import h020_fixtures as F  # noqa: E402
import h020_scenarios as SC  # noqa: E402

EXPECTED = json.loads((ROOT / "research" / "phase5" / "h020_scenarios_expected.json").read_text())["scenarios"]


@pytest.fixture(scope="module")
def table():
    return SC.table()


def test_all_scenarios_present():
    assert set(EXPECTED) == set(F.SCENARIOS) and len(F.SCENARIOS) == 12
    for letter in "ABCDEFGHIJ":
        assert any(n.startswith(letter + "_") for n in F.SCENARIOS)


@pytest.mark.parametrize("name", F.SCENARIOS)
def test_scenario_matches_frozen_expectation_exactly(table, name):
    got, exp = table[name], EXPECTED[name]
    for k in ("score", "categories", "quality_level", "group", "conditions", "disqualifiers", "weekly_state",
              "daily_state", "features", "snapshot_digest", "daily_raster_sha256", "weekly_raster_sha256"):
        assert json.loads(json.dumps(got[k])) == exp[k], (name, k)


@pytest.mark.parametrize("name", F.SCENARIOS)
def test_scenario_shows_its_design_target(table, name):
    r = table[name]
    for k, want in F.TARGET[name].items():
        have = r["conditions"].get(k, r["disqualifiers"].get(k, r.get(k)))
        assert have == want, (name, k, have, want)


def test_score_is_the_count_of_twenty_binary_conditions(table):
    for r in table.values():
        assert len(r["conditions"]) == 20 and len(r["disqualifiers"]) == 5
        assert r["score"] == sum(r["conditions"].values()) == sum(r["categories"].values())
        assert r["quality_level"] == (-1 if any(r["disqualifiers"].values()) else r["score"])


def test_controlled_pairs_differ_only_in_the_tested_element(table):
    def diff(a, b):
        return {k for k in table[a]["conditions"] if table[a]["conditions"][k] != table[b]["conditions"][k]}
    assert diff("I_contracting_volume", "I_control_flat_volume") == {"B4"}
    assert diff("J_expanding_breakout_volume", "J_control_quiet_breakout") == {"T3"}
    assert diff("E_valid_breakout", "C_healthy_base") == {"T1", "T2", "T3", "T4", "R2", "R3"}


def test_ordering_of_illustrative_scenarios(table):
    """Built 'textbook' setups score above built failures (a property of the fixtures, not evidence of any edge)."""
    s = {n: table[n]["quality_level"] for n in table}
    assert s["E_valid_breakout"] > s["C_healthy_base"] > s["F_false_breakout"] > s["D_deep_base"] > s["B_range"]
    assert min(s["G_support_break"], s["H_overextended"], s["B_range"]) == -1
