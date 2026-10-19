"""SYS-1 single-account engine (src/qresearch/lean/qr_sys1.py; owner D251 / D252) on SYNTHETIC months: exact frozen
reproductions (qr_h026.simulate, spy_simulate), cash-ledger sequencing, no hidden financing, the $5,000 overlay,
ETF targets, BM-X weights and the trailing-beta truncation property."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT_ = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT_ / "src" / "qresearch" / "lean"), str(ROOT_ / "tests")]
import qr_h026 as H  # noqa: E402
import qr_sys1 as Y  # noqa: E402
from test_p11_h026 import synth  # noqa: E402


def months_with_etfs(seed=0, n=80, zero=False):
    ms = [m for m in synth(np.r_[0.5, np.zeros(10)], seed=seed, n=n) if m["test_year"] in H.OUTER_YEARS]
    rng = np.random.default_rng(seed + 99)
    for m in ms:
        nd = m["daily"].shape[0]
        for name in ("splv", "usmv"):
            r = 0.006 + rng.normal(0, 0.02)
            m[f"{name}_oo"], m[f"{name}_oc"] = r, r
            m[f"{name}_daily"] = np.linspace(1 / nd, 1, nd) * r
        m["beta"] = np.clip(1.0 + rng.normal(0, 0.3, len(m["ids"])), -0.5, 2.5)
        if zero:
            for key in ("r_oo", "r_oc"):
                m[key] = np.zeros(len(m["ids"]))
            m["daily"] = np.zeros_like(m["daily"])
            for name in Y.ETFS:
                m[f"{name}_oo"] = m[f"{name}_oc"] = 0.0
                m[f"{name}_daily"] = np.zeros(nd)
    return ms


def scores_for(ms, seed=1):
    rng = np.random.default_rng(seed)
    return [rng.normal(size=len(m["ids"])) for m in ms]


def test_sleeve_one_without_etf_is_frozen_simulate_bit_for_bit():
    ms = months_with_etfs()
    sc = scores_for(ms)
    for cap in (100_000.0, 200_000.0):
        for slip in Y.SLIPS:
            ref = H.simulate(ms, sc, cap, slip=slip, daily=True, keep_trades=True)
            got = Y.account(ms, sc, capital=cap, slip=slip, sleeve=1.0, absorber=None, min_ticket=0.0)
            assert got["wealth"] == ref["wealth"]
            assert got["commissions"] == ref["commissions"] and got["slippage"] == ref["slippage"]
            assert got["buys"] == ref["buys"] and got["sells"] == ref["sells"] and got["etf_orders"] == 0
            assert got["picks"] == ref["picks"]
            assert np.array_equal(got["daily"], ref["daily"])


def test_spy_only_is_frozen_spy_simulate_bit_for_bit():
    ms = months_with_etfs()
    for cap in (100_000.0, 200_000.0):
        for slip in Y.SLIPS:
            ref = H.spy_simulate(ms, cap, slip=slip, daily=True)
            got = Y.account(ms, None, capital=cap, slip=slip, absorber="spy")
            assert got["wealth"] == ref["wealth"] and got["etf_orders"] == 2
            assert np.array_equal(got["daily"], ref["daily"])


def test_costs_by_hand():
    c = Y.costs_check()
    assert c["ok"], c


def test_no_hidden_financing_zero_returns():
    ms = months_with_etfs(zero=True)
    sc = scores_for(ms)
    for kw in (dict(), dict(targets={"splv": 0.5}, scores=None), dict(absorber=None, targets={"spy": 0.8}, scores=None)):
        args = dict(scores=sc, slip=0.0, comm=0.0)
        args.update(kw)
        rec = Y.account(ms, args.pop("scores"), **args)
        assert rec["wealth"] == pytest.approx(Y.CAPITAL, abs=1e-6)
        assert rec["violations"]["negative_cash"] == 0
    # with costs the account can only lose exactly its costs when returns are zero
    rec = Y.account(ms, sc, slip=0.001, comm=7.0)
    assert rec["wealth"] == pytest.approx(Y.CAPITAL - rec["commissions"] - rec["slippage"], abs=1e-6)


def test_combined_account_rules():
    ms = months_with_etfs(seed=3)
    sc = scores_for(ms, 4)
    for slip in Y.SLIPS:
        rec = Y.account(ms, sc, slip=slip)
        assert rec["violations"] == dict(negative_cash=0, positions_over_k=0, ticket_below_min=0,
                                         initial_weight_over_cap=0)
        assert rec["min_cash"] >= -1e-6 and max(rec["holdings"]) <= H.K
        for a in rec["alloc"]:
            assert a["cash"] >= -1e-9 and a["stock"] <= 0.80
            assert abs(sum(a[k] for k in ("stock", "cash") + Y.ETFS) - 1.0) < 1e-9
        # the stock picks are the frozen picks; tickets are 50% of account equity / 15 at entry
        frozen = H.simulate(ms, sc, Y.CAPITAL, slip=slip, keep_trades=True)
        assert rec["picks"][0] == frozen["picks"][0]


def test_minimum_ticket_skips_buys_and_cash_goes_to_spy():
    ms = months_with_etfs()
    sc = scores_for(ms)
    rec = Y.account(ms, sc, capital=100_000.0)            # 0.5 x 100,000 / 15 = 3,333 < 5,000 -> no stock ever
    assert rec["buys"] == 0 and rec["skipped_min"] > 0 and max(rec["holdings"]) == 0
    assert rec["wealth"] == H.spy_simulate(ms, 100_000.0)["wealth"]


def test_etf_targets_and_absorber():
    ms = months_with_etfs(seed=5)
    rec = Y.account(ms, None, targets={"splv": 0.5}, absorber="spy")
    for a in rec["alloc"]:
        assert abs(a["splv"] - 0.5) < 0.02 and a["cash"] < 1e-9 and abs(a["spy"] + a["splv"] - 1.0) < 1e-9
    rec = Y.account(ms, None, targets={"spy": 0.9}, absorber=None)
    for a in rec["alloc"]:
        assert abs(a["spy"] - 0.9) < 0.02 and abs(a["cash"] - 0.1) < 0.02
    w = [0.6 + 0.01 * i for i in range(len(ms))]
    rec = Y.account(ms, None, targets={"spy": w}, absorber=None)
    assert rec["violations"]["negative_cash"] == 0


def test_exante_weights_clamped_long_only():
    ms = months_with_etfs(seed=6)
    sc = scores_for(ms, 7)
    rec = Y.account(ms, sc)
    w, raw, cl = Y.exante_weights(ms, rec)
    assert len(w) == len(ms) and all(0.0 <= x <= 1.0 for x in w)
    for x, r in zip(w, raw):
        assert x == min(max(r, 0.0), 1.0)
    # by hand for one month
    p, m = rec["posts"][10], ms[10]
    b = sum(wi * m["beta"][i] for i, wi in zip(p["idx"], p["w"])) + p["etf"].get("spy", 0.0)
    assert raw[10] == pytest.approx(b)
    rec3 = Y.account(ms, None, targets={"splv": 0.5})
    eb = {"splv": [0.4] * len(ms)}
    w3, raw3, _ = Y.exante_weights(ms, rec3, eb)
    assert raw3[5] == pytest.approx(rec3["posts"][5]["etf"]["spy"] + 0.4 * rec3["posts"][5]["etf"]["splv"])


def test_beta_truncation_and_insufficient_data():
    rng = np.random.default_rng(11)
    mkt = np.cumprod(1 + rng.normal(0.0004, 0.01, 800))
    tr = np.cumprod(1 + 0.7 * (np.r_[0, np.diff(mkt) / mkt[:-1]]) + rng.normal(0, 0.008, 800))
    for k in (300, 500, 799):
        b, n = Y.beta_at(tr, mkt, k)
        b2, n2 = Y.beta_at(tr[:k + 1], mkt[:k + 1], k)
        assert b == b2 and n == n2 == Y.BETA_WIN
        assert 0.5 < b < 0.9
    assert math.isnan(Y.beta_at(tr, mkt, 100)[0])                     # fewer than 252 sessions of history
    gappy = tr.copy()
    gappy[300:450] = np.nan
    b, n = Y.beta_at(gappy, mkt, 500)
    assert math.isnan(b) and n < Y.BETA_MIN_OBS
    assert Y.blume(float("nan")) == 1.0 and Y.blume(0.5) == pytest.approx(0.665)


def test_metrics_and_summary_shapes():
    ms = months_with_etfs()
    days = np.concatenate([m["days"] for m in ms])
    ref = Y.account(ms, None)
    rec = Y.account(ms, scores_for(ms))
    out = Y.metrics(rec, days, Y.CAPITAL, ref["daily"])
    import qr_h027 as G
    assert set(out) == {"path", "risk", "years", "month_end"}
    assert len(out["month_end"]) == len(G.month_ends(days)) + 1        # synthetic days do not follow calendar months
    s = Y.summary(rec)
    assert s["stock_positions_max"] <= H.K and set(s["alloc"]) == {"stock", "cash", "spy", "splv", "usmv"}
