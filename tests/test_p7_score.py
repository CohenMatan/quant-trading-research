"""P7-CP2 Multi-Factor Conviction Score v1 (src/qresearch/lean/qr_p7_score.py; research/phase7/P7_score_spec.md):
sanity behaviour on SYNTHETIC / mock companies only (no market data, no returns)."""
import numpy as np
import pytest

import qr_p7_score as S

GROUPS = ("BusEq", "Manuf", "Hlth")


def tech(trend="moderate", mom=0.0, vol=0.02, bars=400, age=0, broken=False):
    return dict(bars=bars, age=age, trend_state=trend, broken_trend=broken, mom_12_1=mom, vol60=vol)


def fund(gpa=0.3, cc=0.0, eqa=0.4, g=0.05, impaired=False):
    return (dict(gpa=gpa, cash_conversion=cc, eqa=eqa, rev_growth=g, impaired=impaired), "")


def crowd(seed=1, n_per_group=20):
    """60 ordinary mock companies with mid-range, random features."""
    rng = np.random.default_rng(seed)
    st = {}
    for g in GROUPS:
        for i in range(n_per_group):
            st[f"{g}{i:02d}"] = dict(ff12=g, sic=3000, contaminated=False,
                                     tech=tech(trend=rng.choice(["strong", "moderate", "weak"]), mom=rng.normal(0.1, 0.2),
                                               vol=abs(rng.normal(0.018, 0.006))),
                                     fund=fund(gpa=rng.normal(0.3, 0.1), cc=rng.normal(0, 0.03), eqa=rng.normal(0.45, 0.15),
                                               g=rng.normal(0.06, 0.1)))
    return st


BEST_T = dict(trend="strong", mom=5.0, vol=0.001)
BEST_F = dict(gpa=9.0, cc=1.0, eqa=0.99, g=9.0)
WORST_T = dict(trend="weak", mom=-0.9, vol=0.5)
WORST_F = dict(gpa=-1.0, cc=-1.0, eqa=0.01, g=-0.9)


def one(name, t, f, ctx="neutral", group="BusEq", **kw):
    st = crowd()
    st[name] = dict(ff12=group, sic=kw.get("sic", 3570), contaminated=kw.get("contaminated", False),
                    tech=t if "trend_state" in t else tech(**t), fund=fund(**f) if isinstance(f, dict) else f)
    return S.score_date(st, {group: ctx})[name]


def test_case_A_strong_everywhere_is_high():
    r = one("A", BEST_T, BEST_F, ctx="supportive")
    assert r["eligible"] and r["total"] == 100 and r["subtotals"] == dict(technical=40, fundamental=45, sector=15)
    assert "Total:       100 / 100" in S.explain(r)


def test_case_B_strong_chart_weak_fundamentals_is_not_exceptional():
    r = one("B", BEST_T, WORST_F, ctx="supportive")
    assert r["subtotals"] == dict(technical=40, fundamental=0, sector=15) and r["total"] == 55


def test_case_C_strong_fundamentals_severe_downtrend_is_disqualified():
    r = one("C", dict(trend="weak", mom=-0.5, vol=0.03, broken=True), BEST_F, ctx="neutral")
    assert not r["eligible"] and "H6_broken_long_term_trend" in r["dq"]
    assert r["subtotals"]["technical"] <= 10                       # and the points are low anyway


def test_case_D_strong_company_weak_sector_keeps_most_points():
    weak = one("D", BEST_T, BEST_F, ctx="weak")
    sup = one("D", BEST_T, BEST_F, ctx="supportive")
    assert weak["eligible"] and weak["total"] == 85 and sup["total"] - weak["total"] == 15


def test_sector_cannot_rescue_a_weak_stock():
    r = one("W", WORST_T, WORST_F, ctx="supportive")
    assert r["total"] <= 15 + 8 and r["points"]["sector"] == 15      # trend weak 0, all bottom quintiles


def test_case_E_missing_or_untrusted_data_is_ineligible():
    cases = {
        "H2_fundamentals_missing_or_stale": dict(f=(None, "missing: revenue_prev")),
        "H5_stale_price": dict(t=tech(trend="strong", mom=1.0, vol=0.01, age=6)),
        "H3_insufficient_history": dict(t=tech(trend="strong", mom=1.0, vol=0.01, bars=200)),
        "H1_sector_not_scorable": dict(sic=6798),
        "H4_corporate_event_contamination": dict(contaminated=True),
    }
    for dq, kw in cases.items():
        r = one("E", kw.get("t", BEST_T), kw.get("f", BEST_F), sic=kw.get("sic", 3570),
                contaminated=kw.get("contaminated", False))
        assert r["total"] is None and not r["eligible"] and dq in r["dq"], dq
    st = crowd()
    st["N"] = dict(ff12="BusEq", sic=None, contaminated=False, tech=tech(), fund=fund())   # no PIT SIC yet
    assert "H1_sector_not_scorable" in S.score_date(st, {})["N"]["dq"]


def test_financial_impairment_is_a_hard_disqualifier():
    r = one("I", BEST_T, (dict(gpa=9.0, cash_conversion=1.0, eqa=0.5, rev_growth=9.0, impaired=True), ""))
    assert not r["eligible"] and r["dq"] == ["H7_financial_impairment"] and r["total"] is not None


def test_scale_points_and_bands():
    assert [S.pts(15, f) for f in S.BAND_FRACTION] == [0, 0, 5, 10, 15]
    assert [S.pts(10, f) for f in S.BAND_FRACTION] == [0, 0, 3, 7, 10]
    assert sum(S.POINTS.values()) == 100
    assert {c: sum(S.POINTS[d] for d in ds) for c, ds in S.CATEGORIES.items()} == dict(technical=40, fundamental=45,
                                                                                         sector=15)
    recs = S.score_date(crowd(seed=3), {g: "neutral" for g in GROUPS})
    tot = [r["total"] for r in recs.values()]
    assert all(isinstance(x, int) and 0 <= x <= 100 for x in tot)


def test_quintiles_ties_and_scope():
    q = S.quintiles({f"k{i}": float(i) for i in range(10)})
    assert [q[f"k{i}"] for i in range(10)] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    assert len(set(S.quintiles({"a": 1.0, "b": 1.0, "c": 1.0}).values())) == 1
    vals = {f"s{i}": float(i) for i in range(5)}
    vals.update({f"b{i}": float(i) for i in range(30)})
    groups = {k: ("small" if k.startswith("s") else "big") for k in vals}
    sq = S.scoped_quintiles(vals, groups, "sector")
    mk = S.quintiles(vals)
    assert all(sq[k] == mk[k] for k in vals if k.startswith("s"))     # < MIN_SECTOR_GROUP -> market ranks
    assert sq["b29"] == 5 and sq["b0"] == 1


def test_percentile_points_are_invariant_to_market_level():
    st = crowd(seed=5)
    a = S.score_date(st, {})
    for s in st.values():
        s["tech"] = dict(s["tech"], mom_12_1=s["tech"]["mom_12_1"] + 0.5)     # an unusually strong market year
    b = S.score_date(st, {})
    assert {k: r["points"]["momentum"] for k, r in a.items()} == {k: r["points"]["momentum"] for k, r in b.items()}


def _series(n=600, drift=0.0008, seed=2, div_factor=0.999, noise=0.01):
    """Total-return closes P and the split-adjusted (not dividend-adjusted) chart closes C = P / dividend multiplier
    (earlier rows carry the factors of later distributions)."""
    rng = np.random.default_rng(seed)
    P = 50 * np.exp(np.cumsum(rng.normal(drift, noise, n)))
    C = P / div_factor ** (n - 1 - np.arange(n))
    return C, P


def test_technical_inputs_use_the_declared_series():
    C, P = _series()
    t = 550
    ti = S.technical_inputs(C, P, t)
    assert ti["bars"] == 551 and ti["age"] == 0
    assert abs(ti["sma50"] - C[501:551].mean()) < 1e-9 and abs(ti["sma200"] - C[351:551].mean()) < 1e-9
    assert abs(ti["sma200_lag"] - C[330:530].mean()) < 1e-9
    assert abs(ti["mom_12_1"] - (P[529] / P[298] - 1)) < 1e-12                # total-return series
    lr = np.log(P[491:551] / P[490:550])
    assert abs(ti["vol60"] - lr.std()) < 1e-12
    up = S.technical_inputs(*_series(drift=0.002, noise=0.002), t)
    dn = S.technical_inputs(*_series(drift=-0.002, noise=0.002), t)
    assert up["trend_state"] == "strong" and not up["broken_trend"]
    assert dn["trend_state"] == "weak" and dn["broken_trend"]


def test_security_life_rule_resets_history():
    C, P = _series()
    C2, P2 = C.copy(), P.copy()
    C2[200:300] = P2[200:300] = np.nan                                     # a 100-session gap: a new life
    ti = S.technical_inputs(C2, P2, 550)
    assert ti["bars"] == 251 and ti["mom_12_1"] is None                   # < 253 bars -> H3 in the score


def test_corporate_event_window_is_mechanical():
    C, P = _series(n=900)
    t = 550
    ti = S.technical_inputs(C, P, t)
    e = 400                                                                 # an unverified split at row 400
    flag, why, clear = S.contamination(ti, unverified_split_rows=[e])
    assert flag and why == ["unverified split"] and clear == S.TR_WINDOW - 1 - (t - e)
    later = S.technical_inputs(C, P, t + clear)
    assert not S.contamination(later, unverified_split_rows=[e])[0]
    assert S.contamination(S.technical_inputs(C, P, t + clear - 1), unverified_split_rows=[e])[0]
    # a large distribution affects only the split-adjusted trend window (221 bars); a small one never
    f2, w2, c2 = S.contamination(ti, distributions=[(e, 0.12)])
    assert f2 and c2 == S.TREND_WINDOW - 1 - (t - e)
    assert not S.contamination(ti, distributions=[(e, 0.05)])[0]
    assert not S.contamination(ti, distributions=[(t - 230, 0.5)])[0]       # already outside the 221-bar window


def test_fundamental_inputs_and_missing_rules():
    fi, _ = S.fundamental_inputs(rev=100.0, gp=40.0, ni=8.0, ocf=12.0, assets=200.0, equity=90.0, rev_prev=80.0)
    assert fi == dict(gpa=0.2, cash_conversion=0.02, eqa=0.45, rev_growth=0.25, impaired=False)
    assert S.fundamental_inputs(100.0, 40.0, 8.0, 12.0, 200.0, 90.0, None)[0] is None
    assert S.fundamental_inputs(100.0, 40.0, 8.0, 12.0, 0.0, 90.0, 80.0)[0] is None
    assert S.fundamental_inputs(100.0, 40.0, -8.0, -1.0, 200.0, 90.0, 80.0)[0]["impaired"]
    assert S.fundamental_inputs(100.0, 40.0, 8.0, 12.0, 200.0, -5.0, 80.0)[0]["impaired"]


def test_one_share_class_per_company():
    sel = S.select_share_classes({"GOOG": ("cik1", 5e8), "GOOGL": ("cik1", 6e8), "BRKA": ("cik2", 1e8),
                                  "BRKB": ("cik2", 1e8), "SOLO": (None, 1e7)})
    assert sel == {"GOOGL", "BRKA", "SOLO"}                              # tie -> smallest id (BRKA < BRKB)


def test_market_regime_cases_and_no_effect_on_ranking():
    up = 100 * np.exp(np.linspace(0, 0.4, 400))
    dn = 100 * np.exp(np.linspace(0, -0.4, 400))
    assert S.spy_trend(up, 399) == "up" and S.spy_trend(dn, 399) == "down"
    assert S.regime("up", 0.75) == "STRONG"
    assert S.regime("up", 0.50) == "NORMAL"                                 # index up, breadth deteriorating
    assert S.regime("down", 0.30) == "RISK_OFF"
    assert S.REGIMES.index(S.regime("up", 0.50)) > S.REGIMES.index(S.regime("up", 0.75))
    assert S.regime("mixed", 0.7) == "NORMAL" and S.regime("down", 0.7) == "WEAK"
    # the regime never enters score_date; it only caps the number of positions in the planner
    recs = S.score_date(crowd(seed=9), {g: "neutral" for g in GROUPS})
    adv = {k: 1e7 for k in recs}
    elig = [k for k, r in recs.items() if r["eligible"]]
    lo = min(recs[k]["total"] for k in elig)
    big = S.plan_review(set(), recs, adv, entry=lo, exit_=lo - 1, buffer=5, max_positions=10, regime_cap_positions=10)
    small = S.plan_review(set(), recs, adv, entry=lo, exit_=lo - 1, buffer=5, max_positions=10, regime_cap_positions=4)
    assert small["buy"] == big["buy"][:4]                                   # same order; only fewer positions


def _recs(scores):
    return {k: dict(total=v, eligible=True, dq=[]) for k, v in scores.items()}


def test_hysteresis_replacement_and_no_forced_filling():
    # TEST-ONLY placeholder thresholds (the real ones are chosen in P7-CP3 without returns)
    E, X, B = 80, 65, 10
    recs = _recs({"H1": 72, "H2": 75, "C1": 81, "C2": 79})
    adv = {k: 1e7 for k in recs}
    p = S.plan_review({"H1", "H2"}, recs, adv, E, X, B, max_positions=2, regime_cap_positions=2)
    assert p["sell"] == [] and p["buy"] == []          # 72 / 75 >= exit: held; 81 < 72 + 10: no replacement
    recs["C1"]["total"] = 85
    p = S.plan_review({"H1", "H2"}, recs, adv, E, X, B, max_positions=2, regime_cap_positions=2)
    assert p["sell"] == ["H1"] and p["buy"] == ["C1"]  # 85 >= 72 + 10: replaces only the weakest holding
    recs["H2"]["total"] = 60
    p = S.plan_review({"H1", "H2"}, recs, adv, E, X, B, max_positions=10, regime_cap_positions=10)
    assert p["sell"] == ["H2"] and p["buy"] == ["C1"]  # H2 below exit -> sold; C2 (79 < entry) never bought:
    #                                                    free slots stay in cash (no forced filling)
    recs["H2"]["total"] = 75
    p = S.plan_review({"H1", "H2"}, recs, adv, E, X, B, max_positions=10, regime_cap_positions=1)
    assert p["sell"][0] == "H1" and p["reasons"]["H1"] == "regime exposure cap"   # over the cap: weakest leaves
    assert p["buy"] == ["C1"] and "H2" in p["sell"]    # then 85 >= 75 + 10 replaces H2 in the single slot
    with pytest.raises(AssertionError):
        S.plan_review(set(), recs, adv, 70, 70, B, 10, 10)                  # exit must be below entry


def test_frozen_holding_and_weekly_checks():
    recs = {"F": dict(total=None, eligible=False, dq=["H4_corporate_event_contamination", "H6_broken_long_term_trend"]),
            "G": dict(total=88, eligible=False, dq=["H7_financial_impairment"]), "K": dict(total=75, eligible=True, dq=[])}
    p = S.plan_review({"F", "G", "K"}, recs, {}, 80, 65, 10, 10, 10, frozen={"F"})
    assert "F" not in p["sell"] and "G" in p["sell"] and "K" not in p["sell"]
    w = S.weekly_check({"F", "G", "K"}, recs, frozen={"F"})
    assert w == {"G": ["H7_financial_impairment"]}


def test_high_score_is_rare_under_independent_dimensions():
    """Synthetic: 5,000 mock companies whose six percentile dimensions are independent, trend states 40% strong /
    30% moderate / 30% weak and sector contexts 30 / 40 / 30. A high total needs agreement across dimensions."""
    rng = np.random.default_rng(42)
    n = 5000
    st = {}
    for i in range(n):
        st[f"x{i:04d}"] = dict(ff12=GROUPS[i % 3], sic=3000, contaminated=False,
                               tech=tech(trend=rng.choice(["strong", "moderate", "weak"], p=[0.4, 0.3, 0.3]),
                                         mom=rng.random(), vol=rng.random()),
                               fund=fund(gpa=rng.random(), cc=rng.random(), eqa=rng.random(), g=rng.random()))
    ctx = {g: c for g, c in zip(GROUPS, ("supportive", "neutral", "weak"))}
    tot = np.array([r["total"] for r in S.score_date(st, ctx).values()])
    assert (tot >= 80).mean() < 0.02 and (tot >= 90).mean() < 0.002 and np.median(tot) < 50


def test_constant_count_is_small():
    c = S.tunable_constants()
    assert len(c["judgment"]) == 7 and len(c["weights"]) == 8 and len(c["windows"]) == 7
    assert len(S.HARD_DQ) == 7
