"""P7-CP4 (D175) canaries for the Phase 7 predictive test (H022), on SYNTHETIC data only:
A future-data invariance, B truncation, C response timing, D corporate actions / delisting, E null determinism,
F positive control, G negative control; plus the tethered null's structural guarantees."""
import numpy as np

import qr_p7_pred as R
import qr_p7_score as S
import qr_xs_panel as XP


def _series(seed=3, D=700):
    rng = np.random.default_rng(seed)
    c = 40 * np.exp(np.cumsum(rng.normal(0.0004, 0.018, D)))
    return c, c * np.exp(np.cumsum(np.full(D, 0.0001)))


# ----------------------------------------------------------------------------------------------- A / B / C
def test_A_future_prices_cannot_change_the_score_inputs_at_t():
    C, P = _series()
    t = 500
    base = S.technical_inputs(C, P, t)
    C2, P2 = C.copy(), P.copy()
    C2[t + 1:] *= 3.0
    P2[t + 1:] *= 0.2
    alt = S.technical_inputs(C2, P2, t)
    for k in ("close", "sma50", "sma200", "sma200_lag", "mom_12_1", "vol60", "trend_state", "broken_trend", "bars"):
        assert base[k] == alt[k], k


def test_B_truncated_history_gives_the_same_score_inputs():
    C, P = _series()
    t = 480
    full = S.technical_inputs(C, P, t)
    trunc = S.technical_inputs(C[:t + 1], P[:t + 1], t)
    for k in ("close", "sma50", "sma200", "mom_12_1", "vol60", "trend_state", "broken_trend"):
        assert full[k] == trunc[k], k


def test_C_response_starts_after_t_and_never_uses_the_close_at_t():
    rng = np.random.default_rng(1)
    O = 50 + rng.normal(0, 1, 60).cumsum()
    Cl = O + rng.normal(0, 0.5, 60)
    m = np.ones(60)
    t, tn = 20, 41
    v, st = R.response(O, Cl, m, t, tn)
    assert st == "ok" and abs(v - (Cl[tn] / O[t + 1] - 1)) < 1e-12
    O2, C2 = O.copy(), Cl.copy()
    C2[:t + 1] *= 7.0                                   # any price at or before t (incl. the close of t)
    O2[:t + 1] *= 0.3
    assert R.response(O2, C2, m, t, tn)[0] == v


# ----------------------------------------------------------------------------------------------- D
def test_D_split_dividend_and_delisting_total_return():
    D = 40
    raw_o = np.full(D, np.nan)
    raw_c = np.full(D, np.nan)
    raw_o[:] = 100.0
    raw_c[:] = 100.0
    s_row, d_row = 15, 25
    raw_o[s_row:] /= 2.0                                # 2-for-1 split: raw prices halve
    raw_c[s_row:] /= 2.0
    raw_c[d_row - 1] = 52.0                             # reference close before the ex-date
    raw_o[d_row:] = 51.0
    raw_c[d_row:] = 51.0
    raw_c[30] = 55.0
    mult_s, _ = XP.split_multiplier(raw_c, raw_c * np.where(np.arange(D) < s_row, 0.5, 1.0), [(s_row, 0.5)])
    mult_d = XP.dividend_multiplier(D, [(d_row, 1.0, 52.0)])
    m = mult_s * mult_d
    t, tn = 5, 30
    v, st = R.response(raw_o, raw_c, m, t, tn)
    # hand computation: buy 1 share at 100; split -> 2 shares; $1 per share reinvested at the reference price 52
    shares = 2.0 / (1.0 - 1.0 / 52.0)
    assert st == "ok" and abs(v - (shares * 55.0 / 100.0 - 1.0)) < 1e-9
    # delisting inside the window: last real close, status 'truncated'
    raw_c2, raw_o2 = raw_c.copy(), raw_o.copy()
    raw_c2[28:] = np.nan
    raw_o2[28:] = np.nan
    v2, st2 = R.response(raw_o2, raw_c2, m, t, tn)
    assert st2 == "truncated" and abs(v2 - (shares * 51.0 / 100.0 - 1.0)) < 1e-9
    # no bar at all after t: 0 (the position could not be opened)
    raw_o3, raw_c3 = raw_o.copy(), raw_c.copy()
    raw_o3[t + 1:] = np.nan
    raw_c3[t + 1:] = np.nan
    assert R.response(raw_o3, raw_c3, m, t, tn) == (0.0, "no_bar_after_t")
    # an unverified split inside the window: excluded (NaN), counted by status
    assert R.response(raw_o, raw_c, m, t, tn, unverified_rows=[12])[1] == "unverified_split"


# ----------------------------------------------------------------------------------------------- synthetic panel
def _panel(n_dates=40, n=120, gamma=0.0, seed=0, churn=0.03):
    """Persistent scores (0..100), a changing universe, sectors, factor returns and an optional planted edge."""
    rng = np.random.default_rng(seed)
    ids = [f"S{i:04d}" for i in range(int(n * 1.6))]
    live = set(ids[:n])
    latent = {i: rng.normal() for i in ids}
    sector = {i: int(rng.integers(0, 10)) for i in ids}
    beta = {i: 1 + 0.25 * rng.normal() for i in ids}
    vol = {i: float(np.exp(rng.normal(np.log(0.065), 0.3))) for i in ids}
    dates = []
    for t in range(n_dates):
        for i in list(live):
            if rng.random() < churn:
                live.discard(i)
        while len(live) < n:
            live.add(ids[int(rng.integers(len(ids)))])
        for i in ids:
            latent[i] = 0.9 * latent[i] + np.sqrt(1 - 0.81) * rng.normal()
        E = sorted(live)
        lat = np.array([latent[i] for i in E])
        Sc = np.clip(np.round(50 + 18 * lat), 0, 100).astype(int)
        mkt, sec = rng.normal(0.008, 0.035), rng.normal(0, 0.025, 10)
        z = np.array([float(np.sqrt(2) * _erfinv(2 * r - 1)) for r in R.rank01(Sc)])
        y = np.array([beta[i] * mkt + sec[sector[i]] + vol[i] * rng.standard_t(5) / np.sqrt(5 / 3) for i in E]) \
            + gamma * z
        dates.append(dict(ids=np.array(E), S=Sc, sector=np.array([sector[i] for i in E]), mom=rng.normal(size=len(E)),
                          size=rng.normal(size=len(E)), y=y, year=2011 + t * 7 // n_dates, regime="STRONG"))
    return dates


def _erfinv(x):
    a = 0.147
    ln = np.log(1 - x * x)
    t1 = 2 / (np.pi * a) + ln / 2
    return float(np.sign(x) * np.sqrt(np.sqrt(t1 * t1 - ln / a) - t1))


# ----------------------------------------------------------------------------------------------- E / null structure
def test_E_null_is_deterministic_and_a_true_permutation():
    prep = R.prepare(_panel())
    a = R.run_world(prep, seed=11)
    b = R.run_world(prep, seed=11)
    c = R.run_world(prep, seed=12)
    assert a == b and a != c
    T = R.Tether(5)
    prev = None
    kept = 0
    for p in prep:
        part = T.step(p["ids"])
        assert sorted(part) == sorted(p["ids"])                       # exact permutation of the date's scores
        assert all(i != j for i, j in zip(p["ids"], part))            # no self-match
        if prev is not None:
            kept += sum(1 for i, j in zip(p["ids"], part) if prev.get(i) == j)
        prev = dict(zip(p["ids"], part))
    assert kept > 0.8 * sum(len(p["ids"]) for p in prep[1:])          # partners persist (score persistence kept)


# ----------------------------------------------------------------------------------------------- F / G
def test_F_positive_control_is_detected():
    prep = R.prepare(_panel(gamma=0.02, seed=4))
    real = R.run_world(prep)
    nulls = [R.run_world(prep, seed=s) for s in range(1, 101)]
    c = R.critical_value(nulls)
    g = R.promotion(real, c)
    assert real["t_ic"] > c and g["G1_significant"] and g["pass"], (real["t_ic"], c, g)


def test_G_negative_control_rarely_qualifies():
    passes = 0
    nulls = [R.run_world(R.prepare(_panel(seed=100)), seed=s) for s in range(1, 101)]
    c = R.critical_value(nulls)
    for k in range(12):
        s = R.run_world(R.prepare(_panel(seed=200 + k)))
        passes += R.promotion(s, c)["pass"]
    assert passes <= 1
    assert R.false_promotion(nulls, c) <= 0.01


def test_gates_and_constants_frozen():
    s = dict(t_ic=3.0, ic_mean=0.02, hi_ann=0.031, mono=0.9, q5_minus_q1_ann=0.04, halves=[0.01, 0.02], block_max=0.4)
    assert R.promotion(s, 2.5)["pass"]
    for k, v in (("hi_ann", 0.029), ("mono", 0.89), ("block_max", 0.51), ("t_ic", 2.4)):
        bad = dict(s)
        bad[k] = v
        assert not R.promotion(bad, 2.5)["pass"], k
    assert (R.ENTRY, R.ECON_MIN, R.MONO_MIN, R.ALPHA, R.R_NULL, R.NW_LAG, R.HORIZON_MONTHS) == \
        (80, 0.03, 0.90, 0.01, 5000, 2, 1)


def test_quintiles_match_the_frozen_score_convention():
    rng = np.random.default_rng(2)
    Sc = rng.integers(0, 101, 300)
    q = R.quintile_labels(Sc)
    ref = S.quintiles({i: float(v) for i, v in enumerate(Sc)})
    assert all(q[i] == ref[i] for i in range(300))


def test_critical_value_floor_and_grown_winner_rule():
    import qr_p7_mech as M
    worlds = [dict(t_ic=x) for x in np.linspace(-3, 1.5, 200)]
    assert R.critical_value(worlds) == R.CRIT_FLOOR == 2.326
    worlds = [dict(t_ic=x) for x in np.linspace(-3, 4.0, 200)]
    assert R.critical_value(worlds) > R.CRIT_FLOOR
    assert M.grown_winner_trims({"A": 25_000.0, "B": 19_999.0, "C": 20_000.0}, 100_000.0) == {"A": 5_000.0}
    assert M.GROWN_WINNER_CAP == 0.20 and M.INITIAL_POSITION_CAP == 0.10
