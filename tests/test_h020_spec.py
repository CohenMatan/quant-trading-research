"""H020 pre-registration v1 (P5-CP2): the specification, the frozen scenario table and the constants of the chart /
statistics code are pinned; no real-data run exists or is configured to run without owner approval."""
import sys

from qresearch import config, p5h020

sys.path.insert(0, str(config.REPO_ROOT / "src/qresearch/lean"))
import qr_chart as C  # noqa: E402
import qr_h020_stats as H  # noqa: E402

ROOT = config.REPO_ROOT


def test_spec_and_scenarios_hash_pinned():
    assert p5h020.SPEC_SHA256 is not None and p5h020.spec_hash() == p5h020.SPEC_SHA256
    assert p5h020.sha256(p5h020.SCENARIOS) == p5h020.SCENARIOS_SHA256


def test_code_constants_pinned():
    for k, v in p5h020.CHART_CONSTANTS.items():
        assert getattr(C, k) == v, k
    for k, v in p5h020.STATS_CONSTANTS.items():
        assert getattr(H, k) == v, k


def test_spec_states_the_frozen_design():
    s = (ROOT / p5h020.SPEC).read_text()
    for frag in ("**No LLM or vision model is part of H020.**", "Practitioner rules are hypotheses / frameworks, not proof",
                 "**open of t+1** to the **close of t+20**", "**Valid iff 7 ≤ L ≤ 65**", "**Permanent invalidation:**",
                 "**No weights.**", "G0 = disqualified", "High = G3 ∪ G4; Low = G0 ∪ G1.", "**lag 3**",
                 "R = 5,000", "α = 1% each", "intersection-union", "**One stratum**", "+3.0%/yr",
                 "2018-01-01 → 2021-12-31", "Holdout locked", "**never** tune base depth"):
        assert frag in s, frag
    assert len(p5h020.NULL_SEEDS) == 5000 and p5h020.NULL_BATCHES[-1] == (4001, 5000)


def test_provenance_table_covers_every_rule():
    s = (ROOT / p5h020.PROVENANCE).read_text()
    assert "Practitioner rules are hypotheses / frameworks, not proof of predictive alpha." in s
    for r in C.CONDITIONS + C.DISQUALIFIERS:
        assert "| **%s** |" % r in s, r
    assert "Universe minimum history" in s


def test_no_real_run_exists_and_the_threshold_is_not_pinned():
    assert p5h020.C_IC is None and p5h020.C_INC is None and p5h020.NULL_RESULT_SHA256 is None
    idx = (ROOT / "experiments" / "INDEX.csv").read_text()
    for run in p5h020.RUNS:
        assert not any(line.startswith(run + ",") for line in idx.splitlines()), run


def test_chart_code_has_no_network_or_ai_dependency():
    for rel in p5h020.CODE:
        src = (ROOT / rel).read_text().lower()
        for banned in ("import requests", "urllib", "anthropic", "openai", "socket", "http.client"):
            assert banned not in src, (rel, banned)
