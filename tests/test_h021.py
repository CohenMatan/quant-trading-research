"""H021-A sector relative-momentum falsification test (src/qresearch/lean/qr_h021.py): calendar, total-return signal
and response vs an independent day-by-day recomputation from RAW prices + events, point-in-time truncation, gates,
and the identity-tethered derangement null. SYNTHETIC data only."""
import numpy as np
import pytest

import qr_h021 as H
import qr_xs_panel as XP


def _cal(start="1998-12-01", end="2018-01-01"):
    d = np.arange(np.datetime64(start), np.datetime64(end))
    return d[np.is_busday(d)].astype(np.int64)


@pytest.fixture(scope="module")
def panel():
    cal = _cal()
    D, N = cal.size, 9
    rng = np.random.default_rng(1)
    raw_c = 50 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, (D, N)), axis=0))
    raw_o = raw_c * np.exp(rng.normal(0, 0.003, (D, N)))
    raw_c[100:, 3] /= 2.0                                   # a 2:1 split of ETF 3 at row 100
    raw_o[100:, 3] /= 2.0
    splits = {3: {100: 0.5}}
    divs = {i: {} for i in range(N)}
    for i in range(N):
        for b in range(70, D, 63):
            divs[i][b] = (0.004 * raw_c[b - 1, i], raw_c[b - 1, i])
    b_xlf = 4400
    divs[2][b_xlf] = (0.188 * raw_c[b_xlf - 1, 2], raw_c[b_xlf - 1, 2])   # an XLF-like 18.8% distribution
    raw_c[b_xlf:, 2] *= (1 - 0.188)
    raw_o[b_xlf:, 2] *= (1 - 0.188)
    P, O = np.empty((D, N)), np.empty((D, N))
    for i in range(N):
        mult = np.ones(D)
        for b, f in splits.get(i, {}).items():
            mult[:b] *= f
        dm = XP.dividend_multiplier(D, [(b, a, r) for b, (a, r) in divs[i].items()])
        P[:, i] = raw_c[:, i] * mult * dm
        O[:, i] = raw_o[:, i] * mult * dm
    months, me = H.month_end_rows(cal)
    ks = H.decision_index(months)
    return dict(cal=cal, raw_c=raw_c, raw_o=raw_o, splits=splits, divs=divs, P=P, O=O, months=months, me=me, ks=ks)


def test_calendar_and_decisions(panel):
    months, ks, me, cal = panel["months"], panel["ks"], panel["me"], panel["cal"]
    assert ks.size == 215 and months[ks[0]] == (2000, 1) and months[ks[-1]] == (2017, 11)
    assert months[ks[0] - 6] == (1999, 7)
    assert str(np.datetime64(int(cal[me[ks[-1] + 1]]), "D")) == "2017-12-29"


def test_signal_and_response_match_independent_daily_recomputation(panel):
    P, O, me, ks = panel["P"], panel["O"], panel["me"], panel["ks"]
    S = H.signal(P, me, ks)
    F = H.forward(P, O, me, ks, 1)
    worst = 0.0
    for j in range(0, ks.size, 7):
        k = ks[j]
        for i in range(9):
            sp, dv = panel["splits"].get(i, {}), panel["divs"][i]
            s = H.slow_total_return(panel["raw_c"][:, i], panel["raw_o"][:, i], sp, dv, me[k - 6], me[k])
            f = H.slow_total_return(panel["raw_c"][:, i], panel["raw_o"][:, i], sp, dv, me[k] + 1, me[k + 1],
                                    from_open=True)
            worst = max(worst, abs(s - S[j, i]), abs(f - F[j, i]))
    assert worst < 1e-10


def test_total_return_includes_distributions(panel):
    """Across the 18.8% distribution the total-return series does not drop; the raw price does."""
    P, raw = panel["P"][:, 2], panel["raw_c"][:, 2]
    b = 4400
    assert raw[b] / raw[b - 1] < 0.85 and 0.95 < P[b] / P[b - 1] < 1.05


def test_signal_is_point_in_time(panel):
    P, me, ks = panel["P"].copy(), panel["me"], panel["ks"]
    j = 100
    d = me[ks[j]]
    S = H.signal(P, me, ks)
    P2 = P.copy()
    P2[d + 1:] *= np.exp(np.random.default_rng(5).normal(0, 0.3, P2[d + 1:].shape))
    S2 = H.signal(P2, me, ks)
    assert np.array_equal(S[:j + 1], S2[:j + 1])
    # a later price factor (uniform rescale of everything up to the cut) leaves every earlier signal unchanged
    P3 = P.copy()
    P3[:d + 1] *= 1.7
    assert np.allclose(H.signal(P3, me, ks)[:j + 1], S[:j + 1], rtol=1e-12)


def test_planted_placebo_and_gates(panel):
    P, O, me, ks, months = panel["P"], panel["O"], panel["me"], panel["ks"], panel["months"]
    Y = H.relative(H.forward(P, O, me, ks, 1))
    years = np.array([months[k][0] for k in ks])
    s, ic = H.evaluate(Y.copy(), Y, years)
    assert np.allclose(ic, 1.0) and s["top_ann"] > s["mid_ann"] > s["bot_ann"]
    sp, _ = H.evaluate(np.random.default_rng(2).normal(size=Y.shape), Y, years)
    assert abs(sp["t_ic"]) < 4
    good = dict(t_ic=3.0, top_ann=0.04, mid_ann=0.0, bot_ann=-0.04, halves=[0.01, 0.02], ic_sum=5.0,
                block_share={"a": 0.3, "b": 0.3, "c": 0.4})
    assert H.gates(good, 2.5)["qualified"]
    for k, v in (("t_ic", 2.5), ("top_ann", 0.029), ("mid_ann", 0.05), ("halves", [-0.01, 0.02]),
                 ("block_share", {"a": 0.51, "b": 0.3, "c": 0.19}), ("ic_sum", -1.0)):
        assert not H.gates(dict(good, **{k: v}), 2.5)["qualified"], k


def test_null_is_a_deterministic_derangement_that_breaks_a_planted_signal(panel):
    P, O, me, ks, months = panel["P"], panel["O"], panel["me"], panel["ks"], panel["months"]
    Y = H.relative(H.forward(P, O, me, ks, 1))
    years = np.array([months[k][0] for k in ks])
    for seed in (1, 2, 5000):
        p = H.derangement(seed)
        assert np.array_equal(p, H.derangement(seed)) and not np.any(p == np.arange(9))
    a = H.null_world(Y, Y, years, 7)
    assert a == H.null_world(Y, Y, years, 7)
    real = H.evaluate(Y.copy(), Y, years)[0]
    ts = [H.null_world(Y, Y, years, s)["ic_mean"] for s in range(1, 41)]
    # a planted signal equal to the demeaned response is destroyed: another sector's demeaned return is mechanically
    # NEGATIVELY correlated with one's own within a date (about -1/(N-1)), so the null t is negative, far below real
    assert max(ts) < 0 and real["ic_mean"] == pytest.approx(1.0)


def test_critical_value_is_50th_largest_of_5000():
    assert H.critical_value(np.arange(1, 5001, dtype=float)) == 4951.0


def test_frozen_constants():
    assert H.UNIVERSE == ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY")
    assert (H.LOOKBACK, H.TOP_K, H.ECON_MIN, H.ALPHA, H.R_NULL) == (6, 3, 0.03, 0.01, 5000)
    assert H.BLOCKS == ((2000, 2005), (2006, 2011), (2012, 2017)) and H.FIRST_DECISION == (2000, 1)


def test_missing_bars_carry_forward_and_entry_is_first_bar_after_decision(panel):
    """Spec section 4: a missing close carries the last total-return close forward; a missing entry open moves the
    entry to the ETF's first bar after the decision row. Both agree with the day-by-day recomputation."""
    P, O, me, ks = panel["P"].copy(), panel["O"].copy(), panel["me"], panel["ks"]
    rc, ro = panel["raw_c"].copy(), panel["raw_o"].copy()
    j = 50
    k = ks[j]
    for arr in (P, O, rc, ro):
        arr[me[k], 4] = np.nan                 # ETF 4: no bar on the decision session
        arr[me[k] + 1, 5] = np.nan             # ETF 5: no bar on the first session after it
    S = H.signal(P, me, ks)
    F = H.forward(P, O, me, ks, 1)
    sp4, sp5 = panel["splits"].get(4, {}), panel["splits"].get(5, {})
    s4 = H.slow_total_return(rc[:, 4], ro[:, 4], sp4, panel["divs"][4], me[k - 6], me[k])
    f5 = H.slow_total_return(rc[:, 5], ro[:, 5], sp5, panel["divs"][5], me[k] + 2, me[k + 1], from_open=True)
    assert abs(S[j, 4] - s4) < 1e-10 and abs(F[j, 5] - f5) < 1e-10
    assert abs(S[j, 4] - (P[me[k] - 1, 4] / P[me[k - 6], 4] - 1)) < 1e-12
    E = H.entry_rows(O, me, ks)
    assert E[j, 5] == me[k] + 2 and E[j, 4] == me[k] + 1


def test_step_consistency_detects_a_missed_distribution(panel):
    P = panel["P"][:, 2]
    A = P * 3.7                                               # an independently adjusted series: a constant multiple
    assert H.step_consistency(P, A)[0] < 1e-12
    B = A.copy()
    B[:4400] *= 1 - 0.188                                     # a series that treats the 18.8% distribution differently
    dev, row, n = H.step_consistency(P, B)
    assert row == 4400 and abs(dev - 0.188) < 1e-9 and n == P.size


def test_slow_total_return_handles_gaps_and_same_day_events(panel):
    rc, ro = panel["raw_c"][:, 0].copy(), panel["raw_o"][:, 0].copy()
    d = {b: v for b, v in panel["divs"][0].items()}
    b = sorted(d)[3]
    d2 = dict(d)
    d2[b] = [d[b], (0.0, 1.0)]                                 # a second (empty) event on the same day
    a = H.slow_total_return(rc, ro, {}, d, b - 30, b + 30)
    assert abs(a - H.slow_total_return(rc, ro, {}, d2, b - 30, b + 30)) < 1e-14
    P = panel["P"][:, 0].copy()
    rc[b] = np.nan                                             # no bar on the ex-day: the factor carries to b + 1
    P[b] = np.nan
    assert abs(H.slow_total_return(rc, ro, {}, d, b - 30, b + 30) - (P[b + 30] / P[b - 30] - 1)) < 1e-12
