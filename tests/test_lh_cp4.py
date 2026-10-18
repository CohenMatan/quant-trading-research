"""LH-CP4 (owner D245): analytical power equations, effect-size mapping, cost hurdles and the narrow Stage C exception
(approved-population rule). Analytical only: no data, no returns, no simulation."""
import json
import math
import re
import sys

import pytest

from conftest import ROOT

CP4 = ROOT / "research/longhorizon/cp4"
sys.path.insert(0, str(CP4))
import lh_cp4_power as P  # noqa: E402


def test_effective_sample_size():
    assert P.t_eff_ar1(83, 0.0) == 83
    assert P.t_eff_ar1(83, 0.2) == pytest.approx(83 * 0.8 / 1.2)
    assert P.t_eff_overlap(83, 3) == pytest.approx(27.667, abs=1e-3)


def test_critical_values_and_bonferroni():
    assert P.crit(0.05) == pytest.approx(1.95996, abs=1e-4)
    assert P.crit(0.01) == pytest.approx(2.57583, abs=1e-4)
    assert P.crit(0.05, m=2) == pytest.approx(2.24140, abs=1e-4)
    assert P.crit(0.05, df=60) > P.crit(0.05)


def test_mde_and_power_are_consistent():
    for sig, te, a, m in [(0.09, 83, 0.05, 1), (0.12, 25, 0.01, 2), (0.06, 67.9, 0.05, 2)]:
        d = P.mde(sig, te, a, 0.80, m)
        assert P.power_at(d, sig, te, a, m) == pytest.approx(0.80, abs=0.005)
    # normal approximation: (1.96 + 0.8416) * 0.09 / sqrt(83)
    assert P.mde(0.09, 83, use_t=False) == pytest.approx((1.95996 + 0.84162) * 0.09 / math.sqrt(83), abs=1e-5)


def test_effect_size_mapping():
    assert P.QUINTILE_TOP_MEAN_Z == pytest.approx(1.39981, abs=1e-4)
    assert P.top_quintile_excess_annual(0.02, 0.08) == pytest.approx(12 * 0.02 * 0.08 * 1.39981, abs=1e-6)
    ic = P.ic_for_top_quintile_excess(0.03, 0.065)
    assert P.top_quintile_excess_annual(ic, 0.065) == pytest.approx(0.03)
    assert P.fresh_dilution(0.06, 0.337) == pytest.approx(0.02022)


def test_cost_hurdle_formula():
    # 20 positions, $100K, 2x one-way turnover: 80 orders x $7 = $560 (0.56%) + slippage 2 x 0.10% x 2 = 0.40%
    assert P.annual_cost(100_000, 20, 2) == pytest.approx(0.0096)
    assert P.annual_cost(200_000, 20, 2) == pytest.approx(0.0068)
    assert P.min_trade_size(100_000, 165) == pytest.approx(606.06, abs=0.01)


def _chain(**kw):
    c = dict(rule_v_v="valid", identity=False, srcs_v=["L0"] * 12 + ["L1"], labels_v=[4, 3, 2, 1] * 3 + [4])
    c.update(kw)
    return c


def test_stage_c_exception_population_rule():
    rec = dict(year=2015, ok1=True, ok2=False)
    assert P.approved(rec, _chain(), "C1") and not P.approved(rec, _chain(), "C2")
    assert not P.approved(rec, _chain(), "C6")
    for y in (2013, 2014, 2022):
        assert not P.approved(dict(rec, year=y), _chain(), "C1")
    assert not P.approved(rec, _chain(rule_v_v="unknown"), "C1")
    assert not P.approved(rec, _chain(rule_v_v="invalid"), "C1")
    assert not P.approved(rec, _chain(identity=True), "C1")
    assert not P.approved(rec, _chain(srcs_v=["L0"] * 12 + ["L2"]), "C1")
    assert not P.approved(rec, _chain(labels_v=[4, 3, 2, 1] * 3 + [None]), "C1")
    with pytest.raises(ValueError):
        P.approved(rec, _chain(), "C9")


def test_exception_record():
    ex = json.loads((ROOT / "research/longhorizon/STAGE_C_EXCEPTION_D245.json").read_text())
    assert ex["decision"] == "D245" and ex["decision_years"] == list(range(2015, 2022))
    assert ex["fiscal_label_sources_allowed"] == ["L0", "L1"]
    for x in ("P-assume", "rule P", "unknown fiscal-period histories", "invalid fiscal-period histories"):
        assert x in ex["excluded"]
    assert "Stage B" in ex["does_not_authorise"]
    assert ex["historical_results_unchanged"]["LH-CP1 Stage C"] == "C - NOT FEASIBLE"


def test_outputs_are_analytical_and_match_lh_cp3():
    pop = json.loads((CP4 / "LH_CP4_population.json").read_text())
    fin = json.loads((ROOT / "research/longhorizon/cp3/LH_CP3_final.json").read_text())
    assert pop["returns_computed"] is False and pop["signal_values_computed"] is False
    assert pop["review_months"] == 83
    for c in ("C1", "C2", "C6"):
        for y, v in pop[f"{c}_by_year"].items():
            assert v["num"] == fin["scenarios"]["A"][c]["by_year"][y]["num"]
            assert v["den"] == fin["scenarios"]["A"][c]["by_year"][y]["den"]
        assert pop[f"{c}_min_share"] >= 0.70
    pw = json.loads((CP4 / "LH_CP4_power.json").read_text())
    assert pw["T_monthly"] == 83 and "assumptions" in pw


def test_checkpoint_complete():
    cp = (ROOT / "docs/checkpoints/LH_CP4_ofa_statistical_feasibility_research_horizon.md").read_text()
    assert [int(m) for m in re.findall(r"^## (\d+)\. ", cp, re.M)] == list(range(1, 25))
    assert "B — UNDERPOWERED FOR MODEST EFFECTS" in cp and "STOPPED" in cp
    assert "| D245 |" in (ROOT / "DECISIONS.md").read_text()
