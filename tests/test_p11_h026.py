"""H026 pure module (src/qresearch/lean/qr_h026.py): transforms, weighted Ridge vs an independent reference, label
availability, the Top-15 portfolio accounting, SPY, metrics, gates and the complete procedure on SYNTHETIC worlds
(planted coefficients -> edge recovered; zero relationship -> no edge; null permutation moves complete vectors)."""
import math
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pytest

ROOT_ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_ / "src" / "qresearch" / "lean"))
import qr_h026 as H  # noqa: E402


def test_centred_percentile():
    x = np.array([3.0, 1.0, 2.0, 2.0, np.nan])
    p = H.centred_percentile(x)
    assert np.isnan(p[4])
    np.testing.assert_allclose(p[:4], [1.0, -1.0, 0.0, 0.0])
    assert H.centred_percentile(np.array([5.0]))[0] == 0.0
    X = H.feature_matrix(np.random.default_rng(1).normal(size=(50, 11)))
    assert X.min() == -1.0 and X.max() == 1.0 and X.shape == (50, 11)


def test_weighted_ridge_equals_independent_reference():
    rng = np.random.default_rng(3)
    months, stats, Xa, ya, wa = [], [], [], [], []
    for t in range(12):
        n = int(rng.integers(20, 60))
        X = rng.uniform(-1, 1, (n, 11))
        y = X @ rng.normal(size=11) * 0.1 + rng.normal(size=n)
        y[rng.random(n) < 0.1] = np.nan
        stats.append(H.month_stats(X, y))
        ok = np.isfinite(y)
        Xa.append(X[ok]), ya.append(y[ok]), wa.append(np.full(ok.sum(), 1.0 / ok.sum()))
    Xa, ya, wa = np.vstack(Xa), np.concatenate(ya), np.concatenate(wa)
    for lam in H.LAMBDAS:
        b0, b = H.ridge_from_stats(stats, lam)
        r0, rb = H.ridge_reference(Xa, ya, wa, lam)
        assert b0 == pytest.approx(r0, abs=1e-9) and np.allclose(b, rb, atol=1e-9)
    # equal month weight: duplicating every row of one month changes nothing
    s2 = list(stats)
    X0 = rng.uniform(-1, 1, (30, 11))
    y0 = rng.normal(size=30)
    s2[0] = H.month_stats(X0, y0)
    s3 = list(s2)
    s3[0] = H.month_stats(np.vstack([X0, X0]), np.r_[y0, y0])
    assert np.allclose(H.ridge_from_stats(s2, 1.0)[1], H.ridge_from_stats(s3, 1.0)[1])


# ----------------------------------------------------------------------------------------------- synthetic market
def synth(beta, seed=0, n=80, sigma=0.06, years=range(2011, 2022), dead=True):
    """Monthly decision months 2011-01 .. 2021-11 with persistent ids; next-month returns = X.beta*scale + noise."""
    rng = np.random.default_rng(seed)
    ids = [f"S{i:03d}" for i in range(n)]
    sector = rng.integers(0, 12, n)
    raw = rng.normal(size=(n, 11))
    months, day = [], (date(2011, 1, 31) - date(1970, 1, 1)).days
    T = [(y, mo) for y in years for mo in range(1, 13)][:-1]          # 2011-01 .. 2021-11
    for t, (y, mo) in enumerate(T):
        raw = 0.9 * raw + 0.44 * rng.normal(size=(n, 11))
        X = H.feature_matrix(raw)
        mu = X @ np.asarray(beta, float)
        r = mu + rng.normal(0, sigma, n)
        spy = 0.008 + rng.normal(0, 0.03)
        cutoff = day + 31 * t
        ndays = 21
        months.append(dict(ids=list(ids), sector=sector.copy(), X=X, raw=raw.copy(), r_true=r, spy_r=spy,
                           cutoff_day=cutoff, test_year=y + (1 if mo == 12 else 0) if False else None, mo=(y, mo),
                           open_ok=np.ones(n, bool), r_oo=r.copy(), r_oc=r.copy(), alive_next=np.ones(n, bool),
                           alive_end=np.ones(n, bool), spy_oo=spy, spy_oc=spy,
                           daily=np.outer(np.linspace(1 / ndays, 1, ndays), r),
                           spy_daily=np.linspace(1 / ndays, 1, ndays) * spy,
                           days=cutoff + 1 + np.arange(ndays)))
    for t, m in enumerate(months):
        y, mo = m["mo"]
        m["test_year"] = y + 1 if mo == 12 else y                     # the December review trades in January
        fut = months[t:t + 3]
        if len(fut) == 3:
            ex = np.prod([1 + f["r_true"] for f in fut], axis=0) - np.prod([1 + f["spy_r"] for f in fut])
            m["label"] = H.centred_percentile(ex)
            m["exit_day"] = months[t]["cutoff_day"] + 92
        else:
            m["label"] = np.full(n, np.nan)
            m["exit_day"] = float("inf")
    if dead:                                                            # one stock dies mid-sample
        m = months[60]
        m["alive_next"][5] = False
    return [m for m in months if m["test_year"] <= 2021]


def test_label_availability_never_crosses_the_cutoff():
    ms = synth(np.zeros(11))
    fit = H.Fitter(ms, [m["X"] for m in ms])
    for m in ms:
        used = fit.months_used(m["cutoff_day"])
        assert all(ms[i]["exit_day"] < m["cutoff_day"] for i in used)
        assert all(ms[i]["exit_day"] >= m["cutoff_day"] for i in range(len(ms)) if i not in used)
    # prefix-sum fit = direct fit on the same months
    cut = ms[60]["cutoff_day"]
    b0, b, n = fit.fit(cut, 1.0)
    stats = [H.month_stats(ms[i]["X"], ms[i]["label"]) for i in fit.months_used(cut)]
    r0, rb = H.ridge_from_stats(stats, 1.0)
    assert n == len(stats) and np.allclose(b, rb) and b0 == pytest.approx(r0)


def test_pick_sector_cap_open_and_ties():
    m = dict(ids=[f"S{i}" for i in range(8)], sector=np.array([0, 0, 0, 0, 1, 1, 2, 2]),
             open_ok=np.array([True] * 7 + [False]))
    sc = np.array([9, 8, 7, 6, 5, 5, 4, 10.0])
    assert H.pick(m, sc, k=5, cap=3) == [0, 1, 2, 4, 5]                # S7 no open, S3 sector full, tie by id
    assert H.pick(m, sc, k=15, cap=3) == [0, 1, 2, 4, 5, 6]


def test_portfolio_accounting_by_hand():
    def mo(ids, r, sector=None):
        n = len(ids)
        return dict(ids=ids, sector=np.array(sector or list(range(n))), open_ok=np.ones(n, bool), r_oo=np.array(r, float),
                    r_oc=np.array(r, float), alive_next=np.ones(n, bool), alive_end=np.ones(n, bool),
                    daily=np.array([r], float), spy_daily=np.array([0.0]), spy_oo=0.0, spy_oc=0.0)
    m1, m2 = mo(["A", "B"], [0.10, 0.0]), mo(["A", "C"], [0.0, 0.0])
    out = H.simulate([m1, m2], [np.array([2.0, 1.0]), np.array([2.0, 1.0])], capital=1000.0, k=2, slip=0.001, comm=1.0)
    # month 1: targets 500 each cannot be funded (need 2 x (500.5 + 1) > 1000) -> each buy scaled to (1000-2)/(2x1.001)
    a1 = 998.0 / 2.002
    # month 2: sell B (a1 x 0.999 - 1); keep A (1.1 a1); new C target = equity / 2 > cash -> scaled to (cash - 1)/1.001
    cash = a1 * 0.999 - 1.0
    a2 = (cash - 1.0) / 1.001
    cash = (1.1 * a1 + a2) * 0.999 - 2.0                                  # end: liquidate A and C
    assert out["wealth"] == pytest.approx(cash)
    assert (out["buys"], out["sells"], out["trades"]) == (3, 3, 6)
    assert out["commissions"] == pytest.approx(6.0)
    # a dead position becomes cash at its last close, with no cost
    m1d = dict(m1, alive_next=np.array([False, True]))
    out2 = H.simulate([m1d, m2], [np.array([2.0, 1.0]), np.array([1.0, 2.0])], capital=1000.0, k=2, slip=0.0, comm=0.0)
    assert out2["wealth"] == pytest.approx(1050.0)


def test_spy_and_metrics():
    m = dict(spy_oo=0.1, spy_oc=0.05, spy_daily=np.array([0.05, 0.1]))
    s = H.spy_simulate([m, dict(m)], capital=1000.0, slip=0.001, comm=1.0, daily=True)
    v = 999 / 1.001 * 1.1 * 1.05
    assert s["wealth"] == pytest.approx(v * 0.999 - 1)
    eq = np.array([100, 110, 90, 95, 120.0])
    assert H.max_drawdown(eq) == pytest.approx(90 / 110 - 1)
    assert H.underwater(eq) == (0.4, 2)
    assert H.critical_value(np.arange(5000.0)) == 4950.0


def test_planted_edge_recovered_and_zero_rejected():
    beta = np.zeros(11)
    beta[0], beta[4] = 0.03, -0.02
    good = H.run_world(synth(beta, seed=1), full=True)
    zero = H.run_world(synth(np.zeros(11), seed=1), full=True)
    assert good["rec"]["S_WEALTH"] > 0.3 > zero["rec"]["S_WEALTH"]
    b = good["coef"][(2021, good["lam_y"][2021])][1]
    assert b[0] > 0 and b[4] < 0 and abs(b[0]) > max(abs(b[j]) for j in range(11) if j not in (0, 4))
    assert set(good["lam_y"].values()) <= set(H.LAMBDAS)
    # null permutation destroys the planted edge (tether moves complete feature vectors)
    nulls = [H.run_world(synth(beta, seed=1), seed=s)["S_WEALTH"] for s in (1, 2, 3)]
    assert max(nulls) < good["rec"]["S_WEALTH"]


def test_null_world_deterministic_and_vectors_move_together():
    ms = synth(np.zeros(11), seed=2)
    a, b = H.run_world(ms, seed=7), H.run_world(ms, seed=7)
    assert a == b
    X1 = H.permuted(ms, 7)
    for m, Xw in zip(ms[:20], X1[:20]):
        rows = {tuple(r) for r in m["X"]}
        assert all(tuple(r) in rows for r in Xw)                      # whole rows, not per-feature shuffles
        assert sorted(map(tuple, Xw)) == sorted(map(tuple, m["X"]))   # an exact permutation each month


def test_gates_logic():
    h = dict(wealth=200.0, cagr=0.15, maxdd=-0.2, vol=0.18)
    s = dict(wealth=150.0, cagr=0.10, maxdd=-0.2, vol=0.16)
    yh = {y: 0.12 for y in H.OUTER_YEARS}
    ys = {y: 0.08 for y in H.OUTER_YEARS}
    g = H.gates(h, s, yh, ys, 190.0, 150.0, 0.1)
    assert g["all"] and g["S_WEALTH"] == pytest.approx(math.log(200 / 150))
    yh2 = {**yh, 2015: 0.9}
    assert not H.gates(h, s, yh2, ys, 190.0, 150.0, 0.1)["D3"]          # one year > 50% of positive log-relative
    assert not H.gates(dict(h, maxdd=-0.3), s, yh, ys, 190.0, 150.0, 0.1)["D4"]
    assert not H.gates(h, s, yh, ys, 140.0, 150.0, 0.1)["D5"]
    assert not H.gates(h, s, yh, ys, 190.0, 150.0, 0.5)["D1"]


def test_tsr_and_holding_conventions():
    import qr_p7_pred as R
    rng = np.random.default_rng(4)
    for seed in range(15):
        c = 50 * np.exp(np.cumsum(rng.normal(0, 0.01, 90)))
        o = c * np.exp(rng.normal(0, 0.003, 90))
        m = np.ones(90)
        m[:40] *= 1.01
        if seed % 3 == 0:
            o[20:22] = np.nan
        if seed % 4 == 0:
            c[70:] = np.nan
            o[70:] = np.nan
        v, st, _, _ = H.tsr(o, c, m, 20, 82)
        rv, rst = R.response(o, c, m, 19, 82)
        if np.isfinite(v):
            assert v == pytest.approx(rv, abs=1e-15) and st == rst
    c = np.array([10, 10, 11, 12, np.nan, np.nan, 13.0])
    o = np.array([10, 10, 10.5, 11.5, np.nan, np.nan, 13.0])
    m = np.ones(7)
    ok, roo, an, roc, ae, tr = H.holding(o, c, m, 1, 6, 5)
    assert ok and an and roo == pytest.approx(0.3) and roc == pytest.approx(0.2) and not ae
    np.testing.assert_allclose(tr, [0.0, 0.1, 0.2, 0.2, 0.2])
    ok, roo, an, roc, ae, tr = H.holding(o, c, m, 1, 5, 4)
    assert ok and not an and roo == pytest.approx(0.2)
    assert H.holding(o, c, m, 4, 6, 5)[0] is False
    assert H.holding(o, c, m, 1, 6, 5, unverified_rows=(3,))[0] is False
