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
    assert set(p5h020.CODE_SHA256) == set(p5h020.CODE)
    for rel, h in p5h020.CODE_SHA256.items():
        assert p5h020.sha256(rel) == h, rel


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


def test_real_run_never_precedes_the_pinned_thresholds():
    """D154: E021-06 may exist only after c_ic, c_inc and the null result hash are pinned, and its committed config
    must carry exactly those pins."""
    import json
    idx = (ROOT / "experiments" / "INDEX.csv").read_text().splitlines()
    real_rows = [ln for ln in idx if ln.startswith("E021-06,")]
    if p5h020.C_IC is None:
        assert p5h020.C_INC is None and p5h020.NULL_RESULT_SHA256 is None
        assert not real_rows
        return
    cfg = ROOT / "experiments" / "E021-06" / "config.json"
    if cfg.exists():
        p = json.loads(cfg.read_text())["params"]
        assert p["c_ic"] == p5h020.C_IC and p["c_inc"] == p5h020.C_INC
        assert p["null_result_sha256"] == p5h020.NULL_RESULT_SHA256 and p["spec_sha256"] == p5h020.SPEC_SHA256
        assert p["addendum_sha256"] == p5h020.ADDENDUM_SHA256 and p["chart_panel_sha256"] == p5h020.CHART_PANEL_SHA256
        assert p["threshold_commit"] == p5h020.THRESHOLD_COMMIT


def test_addendum_pinned_and_host_copy():
    assert p5h020.ADDENDUM_SHA256 is not None and p5h020.sha256(p5h020.ADDENDUM) == p5h020.ADDENDUM_SHA256
    a = (ROOT / "strategies/X987_h020_chart/main.py").read_bytes()
    assert a == (ROOT / "strategies/S021_h020_chart/main.py").read_bytes()
    s = (ROOT / p5h020.ADDENDUM).read_text()
    for frag in ("NON-GATING SECTOR DIAGNOSTIC", "total shareholder return", "last real close",
                 "changes **nothing** in", "50th-largest of the 5,000"):
        assert frag in s, frag


def test_chart_code_has_no_network_or_ai_dependency():
    for rel in p5h020.CODE:
        src = (ROOT / rel).read_text().lower()
        for banned in ("import requests", "urllib", "anthropic", "openai", "socket", "http.client"):
            assert banned not in src, (rel, banned)


def test_null_thresholds_pinned():
    """D154: c_ic, c_inc, the null result and the per-world table are pinned before the one real evaluation."""
    import csv
    import json
    if p5h020.C_IC is None:
        return
    assert p5h020.sha256(p5h020.NULL_RESULT) == p5h020.NULL_RESULT_SHA256
    n = json.loads((ROOT / p5h020.NULL_RESULT).read_text())
    assert n["worlds"] == 5000 and n["failed_worlds"] == 0 and n["rank_k"] == 50 and n["seeds"] == [1, 5000]
    assert n["c_ic"] == p5h020.C_IC and n["c_inc"] == p5h020.C_INC
    assert n["chart_panel_sha256"] == p5h020.CHART_PANEL_SHA256
    assert n["spec_sha256"] == p5h020.SPEC_SHA256 and n["addendum_sha256"] == p5h020.ADDENDUM_SHA256
    table = ROOT / "research/phase5/H020_null_worlds.csv"
    assert p5h020.sha256("research/phase5/H020_null_worlds.csv") == n["null_worlds_csv_sha256"] == \
        p5h020.NULL_WORLDS_CSV_SHA256
    rows = list(csv.DictReader(table.open()))
    assert [int(r["seed"]) for r in rows] == list(range(1, 5001))
    for k, c in (("t_ic", p5h020.C_IC), ("t_inc", p5h020.C_INC)):
        assert sorted((float(r[k]) for r in rows), reverse=True)[49] == c
