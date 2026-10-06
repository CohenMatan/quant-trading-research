"""P7-CP1 technical-feature audit helpers (src/qresearch/lean/qr_p7.py): the vectorised primary implementation equals
the independent loop implementation; features at t are invariant to anything after t (future perturbation,
truncation) and to corporate-action factors dated after t; breadth uses the point-in-time denominator. SYNTHETIC."""
import math

import numpy as np
import pytest

import qr_p7 as P


@pytest.fixture(scope="module")
def panel():
    rng = np.random.default_rng(3)
    D = 900
    P_ = 40 * np.exp(np.cumsum(rng.normal(0.0004, 0.015, D)))
    C = P_ * np.linspace(0.97, 1.0, D)                      # chart close differs from TR by a slow dividend factor
    H = C * np.exp(np.abs(rng.normal(0, 0.006, D)))
    L = C * np.exp(-np.abs(rng.normal(0, 0.006, D)))
    V = rng.uniform(1e5, 1e6, D)
    for arr in (C, H, L, V, P_):
        arr[[100, 101, 450, 777]] = np.nan                   # missing sessions
    C[:30] = H[:30] = L[:30] = P_[:30] = V[:30] = np.nan     # listed from row 30
    return dict(C=C, H=H, L=L, V=V, P=P_)


def _bars(pn, t):
    return [(pn["C"][r], pn["H"][r], pn["L"][r], pn["V"][r], pn["P"][r]) for r in range(t + 1)
            if np.isfinite(pn["C"][r])]


def test_primary_equals_independent_implementation(panel):
    rows = np.arange(40, 900, 7)
    A = P.features_at(panel["C"], panel["H"], panel["L"], panel["V"], panel["P"], rows)
    worst = 0.0
    for k, t in enumerate(rows):
        a = {f: A[f][k] for f in P.FEATURES}
        b = P.features_slow(_bars(panel, t))
        ok, w, bad = P.compare(a, b)
        assert ok, (t, bad)
        worst = max(worst, w)
    assert worst < 1e-12
    # history requirements: NaN exactly when the security's own bars are insufficient
    first = 30
    k = list(rows).index(next(r for r in rows if r >= first + 252 + 2))
    assert math.isfinite(A["mom_12_1"][k])
    assert np.isnan(A["sma200_ratio"][0]) and np.isnan(A["mom_6_1"][0])


def test_features_are_point_in_time(panel):
    rows = np.array([300, 500, 700])
    A = P.features_at(panel["C"], panel["H"], panel["L"], panel["V"], panel["P"], rows)
    rng = np.random.default_rng(9)
    for i, t in enumerate(rows):
        pert = {k: v.copy() for k, v in panel.items()}
        for k in pert:
            pert[k][t + 1:] *= rng.uniform(0.3, 3.0, pert[k].size - t - 1)      # anything after t
        B = P.features_at(pert["C"], pert["H"], pert["L"], pert["V"], pert["P"], rows[i:i + 1])
        trunc = {k: v[:t + 1] for k, v in panel.items()}                         # dataset truncated at t
        T = P.features_at(trunc["C"], trunc["H"], trunc["L"], trunc["V"], trunc["P"], rows[i:i + 1])
        for f in P.FEATURES:
            for X in (B, T):
                x, y = X[f][0], A[f][i]
                assert (np.isnan(x) and np.isnan(y)) or x == y, (f, t)


def test_later_corporate_action_factors_cancel(panel):
    """A split / dividend dated after t rescales every row before it by the same factor: features at t unchanged."""
    rows = np.array([400, 600])
    A = P.features_at(panel["C"], panel["H"], panel["L"], panel["V"], panel["P"], rows)
    adj = {k: v.copy() for k, v in panel.items()}
    for k in ("C", "H", "L", "P"):
        adj[k][:650] *= 0.5                                  # a 2:1 split on row 650 (prices before x 0.5)
    adj["V"][:650] /= 0.5                                    # volume / factor: dollar volume unchanged
    B = P.features_at(adj["C"], adj["H"], adj["L"], adj["V"], adj["P"], rows)
    for f in P.FEATURES:
        np.testing.assert_allclose(B[f], A[f], rtol=1e-12, atol=1e-15)


def test_breadth_uses_point_in_time_denominator():
    state = {"A": True, "B": False, "C": None, "DEAD": True, "NEW": None}
    share, up, known, n_el, insuff = P.breadth(state, ["A", "B", "C", "DEAD"])   # NEW not yet eligible
    assert (up, known, n_el, insuff) == (2, 3, 4, 1) and abs(share - 2 / 3) < 1e-12
    # after DEAD delists it leaves the denominator; survivors-only would have kept it out on every date
    assert P.breadth(state, ["A", "B", "C"])[1:4] == (1, 2, 3)


def test_sampling_combos_alignment():
    keys = [f"S{i}|2012-0{m}" for i in range(50) for m in range(1, 4)]
    assert P.pick(keys, 10, "x") == P.pick(list(reversed(keys)), 10, "x") and len(P.pick(keys, 10, "x")) == 10
    assert P.pick(keys, 10, "x") != P.pick(keys, 10, "y")
    c = P.combos({"net_income_ttm4q", "total_assets", "operating_cash_flow_ttm4q"})
    assert c["technical_only"] and c["tech+profitability_NI+cashflow"] and not c["tech+all_core"]
    assert P.alignment("2012-03-30", price="2012-03-30", filing="2012-02-28") == (True, [])
    assert P.alignment("2012-03-30", price="2012-03-30", filing="2012-04-02") == (False, ["filing"])


def test_calendar_states_match_primary_features(panel):
    st = P.calendar_states(panel["C"], panel["H"], panel["L"])
    rows = np.arange(0, 900)
    A = P.features_at(panel["C"], panel["H"], panel["L"], panel["V"], panel["P"], rows)
    for t in rows:
        age = A["last_bar_age"][t]
        if np.isnan(age):
            assert np.isnan(st["nbars"][t])
            continue
        assert st["age"][t] == age
        fresh = age <= P.MAX_LAST_BAR_AGE
        r200 = A["sma200_ratio"][t]
        exp = np.nan if (not fresh or np.isnan(r200)) else float(r200 > 0)
        assert (np.isnan(exp) and np.isnan(st["above200"][t])) or exp == st["above200"][t], t
        r50 = A["sma50_ratio"][t]
        exp = np.nan if (not fresh or np.isnan(r50)) else float(r50 > 0)
        assert (np.isnan(exp) and np.isnan(st["above50"][t])) or exp == st["above50"][t], t
    # new 52-week high: the last bar's high is the 252-bar maximum (independent brute force)
    v = P.valid_rows(panel["C"], panel["H"], panel["L"])
    h = panel["H"][v]
    for i in range(251, v.size, 37):
        assert st["new_high"][v[i]] == float(h[i] >= h[i - 251:i + 1].max())
