"""C02 strategy signals (H006-H011): semantics, look-ahead truncation, H010 timing, references."""
import numpy as np
import pandas as pd
import pytest

from conftest import ROOT, load_module
from qresearch.lookahead import truncation_violations

S006 = load_module(ROOT / "strategies/S006_breakout/signals.py", "s006_signals")
S007 = load_module(ROOT / "strategies/S007_squeeze/signals.py", "s007_signals")
S008 = load_module(ROOT / "strategies/S008_residual_rs/signals.py", "s008_signals")
S009 = load_module(ROOT / "strategies/S009_volume_shock/signals.py", "s009_signals")
S010 = load_module(ROOT / "strategies/S010_gap_hold/signals.py", "s010_signals")
S011 = load_module(ROOT / "strategies/S011_seasonality/signals.py", "s011_signals")


def _bars(n=320, seed=7, drift=0.0006):
    rng = np.random.default_rng(seed)
    c = 40 * np.exp(np.cumsum(rng.normal(drift, 0.012, n)))
    o = np.r_[c[0], c[:-1]] * (1 + rng.normal(0, 0.003, n))
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.004, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.004, n)))
    v = rng.integers(900_000, 1_100_000, n).astype(float)
    idx = pd.bdate_range("2011-01-03", periods=n)
    return pd.DataFrame(dict(open=o, high=h, low=l, close=c, volume=v), index=idx)


def _rolling(fn, df):
    """Signal series: at each bar t the function sees only the windows ending at t (as in LEAN)."""
    out = []
    for t in range(len(df)):
        w = df.iloc[: t + 1]
        r = fn(w)
        out.append(np.nan if r is None else float(r if not isinstance(r, tuple) else r[0]))
    return pd.Series(out, index=df.index)


def _truncation(fn, df):
    close = df["close"]

    def signal(closes):
        return _rolling(fn, df.loc[closes.index])
    return truncation_violations(signal, close, n_checks=25)


# ---------------------------------------------------------------- look-ahead truncation (all six)
LOOKAHEAD = {
    "S006": lambda w: S006.breakout_strength(w.high, w.low, w.close, w.volume, 55, 1.0),
    "S007": lambda w: float(S007.expansion(w.high, w.low, w.close, w.volume, tr_mult=0.5, vol_mult=0.5)),
    "S009": lambda w: S009.volume_shock(w.high, w.low, w.close, w.volume, vol_mult=1.0, price_cap_atr=5.0),
    "S010": lambda w: S010.gap_hold(w.open, w.high, w.low, w.close, w.volume, min_gap=0.0, gap_atr=0.0, vol_mult=0.5),
}


@pytest.mark.parametrize("name", sorted(LOOKAHEAD))
def test_signals_have_no_lookahead(name):
    assert _truncation(LOOKAHEAD[name], _bars()) == []


def test_residual_and_seasonal_scores_have_no_lookahead():
    df = _bars(420)
    mkt = _bars(420, seed=11)["close"].to_numpy()
    # short windows so that 420 bars give real scores (the production est = 756 needs 758 bars)
    fn = lambda w: S008.residual_score(w.close, mkt[: len(w)], 60, 5, True, est=120, min_est=100)
    assert _truncation(fn, df) == []
    assert _rolling(fn, df).notna().sum() > 250                 # the check is not vacuous
    months = df["close"].groupby(df.index.to_period("M")).last()
    mc = [[p.year * 100 + p.month, float(v)] for p, v in months.items()]
    assert S011.seasonal_score(mc[:13], 2012, 1, 1) == S011.seasonal_score(mc[:13] + [[209901, 1.0]], 2012, 1, 1)


# ---------------------------------------------------------------- H006 semantics
def test_breakout_needs_a_new_high_with_volume_and_trend():
    df = _bars()
    h, l, c, v = (df[k].to_list() for k in ("high", "low", "close", "volume"))
    top = max(h[-56:-1])
    c[-1] = top * 1.01; h[-1] = c[-1] * 1.001; v[-1] = 3e6
    c200 = sum(c[-200:]) / 200
    s = S006.breakout_strength(h, l, c, v, 55, 1.5)
    assert (s is not None) == (c[-1] > c200)
    assert S006.breakout_strength(h, l, c, v[:-1] + [1e6], 55, 1.5) is None                 # volume fails
    assert S006.breakout_strength(h, l, c, v[:-1] + [1e6], 55, 1.5, use_volume=False) == s  # v1.2
    c2 = c[:-1] + [top * 0.999]
    assert S006.breakout_strength(h, l, c2, v, 55, 1.5) is None                             # no new high


def test_chandelier_and_time_exits():
    df = _bars()
    h, l, c = df.high.to_list(), df.low.to_list(), df.close.to_list()
    assert S006.exit_signal(h, l, c, 60, 3.0, 60) is True
    assert S006.exit_signal(h, l, c, None, 3.0, 60) is False
    c2 = c[:-1] + [max(c[-11:-1]) * 0.80]                                                      # 20% below peak
    assert S006.exit_signal(h, l, c2, 10, 3.0, 60) is True


# ---------------------------------------------------------------- H007 semantics
def test_incremental_bandwidth_equals_rebuild():
    c = _bars().close.to_list()
    full = S007.bandwidth_series(c)
    step = S007.bandwidth_series(c[:-1]) + [S007.bandwidth(c, 20, 2.0)]
    assert full == pytest.approx(step)


def test_contraction_is_measured_on_the_day_before_the_trigger():
    bw = [1.0] * 260 + [0.1, 5.0]                    # T-1 extremely narrow, T wide (the expansion day)
    assert S007.contracted_bw(bw, 0.10) == 0.0
    assert S007.contracted_bw([1.0] * 260 + [5.0, 0.1], 0.10) is None   # narrow only on T: not a setup


# ---------------------------------------------------------------- H008 reference
def _bhm_reference(s, m, window, skip, est, scaled):
    """Independent numpy reference: alpha/beta on the est returns ending T-1; residuals summed over
    returns T-window+1 .. T-skip (Blitz, Huij & Martens 2011, one factor)."""
    rs, rm = np.diff(s) / s[:-1], np.diff(m) / m[:-1]
    xe, ye = rm[-est - 1:-1], rs[-est - 1:-1]
    X = np.c_[np.ones_like(xe), xe]
    a, b = np.linalg.lstsq(X, ye, rcond=None)[0]
    e = rs[-window:len(rs) - skip] - (a + b * rm[-window:len(rm) - skip])
    return e.sum() / e.std(ddof=1) if scaled else e.sum()


def _market_and_stock(alpha_daily, n=800, seed=5, beta=1.3):
    rng = np.random.default_rng(seed)
    rm = rng.normal(0.0004, 0.01, n)
    rs = alpha_daily + beta * rm + rng.normal(0, 0.012, n)
    return 50 * np.cumprod(np.r_[1.0, 1 + rs]), 100 * np.cumprod(np.r_[1.0, 1 + rm])


def test_residual_score_matches_reference_and_is_not_degenerate():
    """D074: the first version summed residuals over the regression's own window (always 0). The
    score must equal an independent reference AND be materially non-zero."""
    s, m = _market_and_stock(0.0)
    for window, scaled in ((252, True), (126, True), (252, False)):           # v1.0, v1.1, v1.2
        ref = _bhm_reference(s, m, window, 21, 756, scaled)
        got = S008.residual_score(s, m, window, 21, scaled)
        assert got == pytest.approx(ref, rel=1e-9, abs=1e-12)
        assert abs(got) > (0.5 if scaled else 1e-3)                            # not ~1e-16
    assert S008.residual_score(s[:700], m[:700], 252, 21) is None              # < 36 months: unscorable


def test_residual_ranking_has_real_dispersion_and_orders_by_alpha():
    """Cross-section: stocks with higher formation-period residual drift must score higher, with
    meaningful spread (not floating-point noise)."""
    scores = []
    for i, a in enumerate(np.linspace(-0.002, 0.002, 21)):
        rng = np.random.default_rng(100 + i)
        rm = np.random.default_rng(7).normal(0.0004, 0.01, 800)
        drift = np.where(np.arange(800) >= 800 - 252, a, 0.0)                  # drift only in the recent year
        rs = drift + 1.1 * rm + rng.normal(0, 0.004, 800)
        s, m = 50 * np.cumprod(np.r_[1.0, 1 + rs]), 100 * np.cumprod(np.r_[1.0, 1 + rm])
        scores.append(S008.residual_score(s, m, 252, 21, True))
    sc = np.array(scores)
    assert sc.std() > 1.0
    assert pd.Series(sc).corr(pd.Series(np.arange(21)), method="spearman") > 0.9


def test_residual_score_uses_nothing_after_T():
    s, m = _market_and_stock(0.0005)
    base = S008.residual_score(s[:790], m[:790], 252, 21, True)
    s2, m2 = s.copy(), m.copy()
    s2[790:] *= 3.0                                                            # change the future only
    assert S008.residual_score(s2[:790], m2[:790], 252, 21, True) == base
    # the day-T return is not in the estimation window and not in the formation window (skip 21)
    s3 = s[:790].copy(); s3[-1] *= 1.5
    assert S008.residual_score(s3, m[:790], 252, 21, True) == pytest.approx(base, rel=1e-12)


def test_monthly_keep_band():
    exits, ranked = S008.monthly_targets(list("ABCDEFGHIJKL"), ["B", "K", "Z"], 3, 10)
    assert exits == ["K", "Z"] and ranked[0] == "A"


# ---------------------------------------------------------------- H009 semantics
def test_volume_shock_requires_volume_without_a_big_move():
    df = _bars()
    h, l, c, v = (df[k].to_list() for k in ("high", "low", "close", "volume"))
    v[-1] = 4e6
    assert S009.volume_shock(h, l, c, v) is not None or abs(c[-1] / c[-2] - 1) > 0.02
    c_jump = c[:-1] + [c[-2] * 1.10]
    assert S009.volume_shock(h, l, c_jump, v) is None                  # big price move: excluded
    assert S009.volume_shock(h, l, c, v[:-1] + [1e6]) is None          # no shock
    assert S009.exit_signal(20, 20) and not S009.exit_signal(19, 20)


# ---------------------------------------------------------------- H010 timing (owner requirement)
def _gap_day(close_vs_open):
    df = _bars()
    o, h, l, c, v = (df[k].to_list() for k in ("open", "high", "low", "close", "volume"))
    o[-1] = c[-2] * 1.05                                               # +5% gap at the open of day T
    c[-1] = o[-1] * close_vs_open
    h[-1] = max(o[-1], c[-1]) * 1.002
    l[-1] = min(o[-1], c[-1]) * 0.998
    v[-1] = 5e6
    return o, h, l, c, v


def test_h010_signal_needs_the_close_of_the_gap_day():
    held = S010.gap_hold(*_gap_day(1.01))
    faded = S010.gap_hold(*_gap_day(0.99))
    assert held is not None and faded is None                         # decided by close_T: known only after T
    o, h, l, c, v = _gap_day(1.01)
    # evaluated before day T is complete (windows ending T-1) there is no signal, whatever T's open is
    assert S010.gap_hold(o[:-1], h[:-1], l[:-1], c[:-1], v[:-1]) is None
    assert S010.gap_hold(*_gap_day(0.99), require_hold=False) is not None   # v1.2 drops the hold condition


def test_h010_orders_are_next_open_orders_placed_at_the_close():
    main = (ROOT / "strategies/S010_gap_hold/main.py").read_text()
    assert "def qr_on_close" in main and "self.qr_event_step(" in main
    assert "market_order" not in main and "set_holdings" not in main   # only harness next-open orders
    harness = (ROOT / "src/qresearch/lean/qr_harness.py").read_text()
    assert "raise Exception(\"QR timing guard: orders may only be placed from qr_on_close\")" in harness
    assert "t = self.market_on_open_order(sym, qty, tag=tag)" in harness
    assert "if fill_day <= sig:" in harness                            # every fill must be after its signal day


def test_h010_gap_day_low_and_invalidation():
    lows = [9.0, 8.0, 7.5, 7.0]                                        # ... gap day T, entry T+1, today
    assert S010.gap_day_low(lows, 1) == 8.0                            # held 1 session: gap day is 3rd from end
    assert S010.gap_day_low(lows[:-1], 0) == 8.0                       # at the entry close
    assert S010.exit_signal([10, 7.9], 1, 8.0, 40) is True
    assert S010.exit_signal([10, 8.1], 1, 8.0, 40) is False
    assert S010.exit_signal([10, 8.1], 40, 8.0, 40) is True


# ---------------------------------------------------------------- H011 reference
def test_seasonal_score_by_hand():
    mc = [[201012, 100.0], [201101, 110.0], [201112, 100.0], [201201, 90.0], [201212, 100.0], [201301, 105.0]]
    # January returns: 2011 +10%, 2012 -10%, 2013 +5%
    assert S011.seasonal_score(mc, 2014, 1, 3) == pytest.approx((0.10 - 0.10 + 0.05) / 3)
    assert S011.seasonal_score(mc, 2014, 1, 4) is None                 # needs all lags
    assert S011.seasonal_score(mc, 2014, 2, 1) is None
    assert S011.next_month(2013, 12) == (2014, 1)


def test_monthly_returns_skip_gaps():
    r = S011.monthly_returns([[201101, 1.0], [201103, 2.0], [201104, 3.0]])
    assert r == {201104: pytest.approx(0.5)}


@pytest.mark.parametrize("sdir", ["S006_breakout", "S007_squeeze", "S008_residual_rs", "S009_volume_shock",
                                  "S010_gap_hold", "S011_seasonality"])
def test_all_c02_orders_are_next_open_orders_from_the_close(sdir):
    """Every C02 strategy decides at the T close and trades only through the harness's event step,
    which sends market-on-open orders for T+1 (the harness raises if an order is placed elsewhere)."""
    main = (ROOT / "strategies" / sdir / "main.py").read_text()
    assert "def qr_on_close" in main and "self.qr_event_step(" in main
    for forbidden in ("market_order", "set_holdings", "limit_order", "liquidate(", "market_on_close"):
        assert forbidden not in main
