"""C03 strategies S012 (H012) and S013 (H013): pure helpers, look-ahead truncation, and the algorithms'
decision logic run offline against a fake harness (no QuantConnect). Canary code copies are pinned."""
import math
import sys
import types
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from conftest import ROOT, load_module
from qresearch.lookahead import truncation_violations

S012 = load_module(ROOT / "strategies/S012_vol_managed/signals.py", "s012_signals")
S013 = load_module(ROOT / "strategies/S013_lottery_avoid/signals.py", "s013_signals")
NULL = load_module(ROOT / "strategies/X962_random_pick/signals.py", "x962_signals")


def _closes(n=700, seed=5):
    rng = np.random.default_rng(seed)
    vol = np.where(np.arange(n) % 250 < 40, 0.025, 0.008)          # calm periods with volatility bursts
    c = 100 * np.exp(np.cumsum(rng.normal(0.0003, 1, n) * vol))
    return pd.Series(c, index=pd.bdate_range("2008-01-02", periods=n))


# ---------------------------------------------------------------- S012 pure helpers
def test_realized_vol_matches_numpy():
    c = _closes().to_numpy()
    for n in (10, 21, 63, 252):
        r = np.diff(c[-(n + 1):]) / c[-(n + 1):-1]
        assert S012.realized_vol(c, n) == pytest.approx(r.std(ddof=1) * math.sqrt(252), rel=1e-12)
    assert S012.realized_vol(c[:21], 21) is None


def test_exposure_target_is_capped_and_scales_down_in_high_volatility():
    c = _closes().to_numpy()
    e = [S012.exposure_target(c[: t + 1], 21) for t in range(253, len(c))]
    assert all(0 < x <= 1 for x in e) and min(e) < 0.6 and max(e) == 1.0
    assert S012.exposure_target(c[:200], 21) is None


def test_exposure_target_has_no_lookahead():
    c = _closes()

    def signal(s):
        return pd.Series([S012.exposure_target(s.iloc[: t + 1].to_numpy(), 21) or np.nan for t in range(len(s))],
                         index=s.index)
    assert truncation_violations(signal, c.iloc[:420], n_checks=20) == []


def test_band_control_b_largest_and_calendar():
    assert S012.band_exceeded(0.75, 0.9, 0.10) and not S012.band_exceeded(0.8, 0.9, 0.10 + 1e-12)
    assert S012.control_b([0.5] * 3 + [1.0] * 12) == 1.0 and S012.control_b([0.4, 0.6]) == 0.5
    assert S012.control_b([]) is None
    assert S012.largest({"b": 5.0, "a": 5.0, "c": 9.0, "d": 1.0}, 3) == ["c", "a", "b"]
    assert S012.is_reconstitution(None, 3) and S012.is_reconstitution(12, 1) and not S012.is_reconstitution(1, 1)
    assert not S012.is_reconstitution(2, 3) and S012.is_reconstitution(3, 4)
    assert S012.is_rescale_day(date(2015, 1, 30), date(2015, 2, 2), "monthly")
    assert not S012.is_rescale_day(date(2015, 1, 29), date(2015, 1, 30), "monthly")
    assert S012.is_rescale_day(date(2015, 12, 31), date(2016, 1, 4), "weekly")      # Thursday before New Year
    assert not S012.is_rescale_day(date(2015, 12, 30), date(2015, 12, 31), "weekly")
    with pytest.raises(ValueError):
        S012.is_rescale_day(date(2015, 1, 30), date(2015, 2, 2), "daily")


def test_history_targets_equal_the_live_rule():
    c = _closes()
    dates = [d.date() for d in c.index]
    got = S012.history_targets(dates, list(c), 21, "monthly", date(2010, 9, 1))
    for d, e in got:
        i = dates.index(d)
        assert (i + 1 == len(dates)) or dates[i + 1].month != d.month
        assert e == S012.exposure_target(list(c)[: i + 1], 21)
    assert len(got) >= 12


# ---------------------------------------------------------------- fake harness for the algorithms
class _Sym(str):
    @property
    def id(self):
        return str(self)

    @property
    def value(self):
        return str(self)


class _Hours:
    def __init__(self, days):
        self.days = days

    def get_next_market_open(self, t, extended):
        d = t.date() if isinstance(t, datetime) else t
        nxt = next(x for x in self.days if x > d)
        return datetime(nxt.year, nxt.month, nxt.day, 9, 30)


class _Sec:
    def __init__(self, hours, price=50.0):
        self.exchange = types.SimpleNamespace(hours=hours)
        self.price = price


class _Securities(dict):
    def contains_key(self, k):
        return k in self


class _Bars(dict):
    def contains_key(self, k):
        return k in self


def _fake_modules(monkeypatch):
    ai = types.ModuleType("AlgorithmImports")
    for name in ("Chart", "Series"):
        setattr(ai, name, lambda *a, **k: types.SimpleNamespace(add_series=lambda *x: None))
    ai.SeriesType = types.SimpleNamespace(LINE=0)
    ai.Resolution = types.SimpleNamespace(DAILY=0)
    ai.DataNormalizationMode = types.SimpleNamespace(SCALED_RAW=0)
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    h = types.ModuleType("qr_harness")

    class QRAlgorithm:
        pass
    h.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", h)


def _load_main(monkeypatch, sdir, name):
    _fake_modules(monkeypatch)
    monkeypatch.syspath_prepend(str(ROOT / "strategies" / sdir))
    for m in ("signals", "nullorder"):
        monkeypatch.delitem(sys.modules, m, raising=False)
    return load_module(ROOT / "strategies" / sdir / "main.py", name)


class _S012Run:
    """Drives S012's qr_on_close over synthetic sessions; records rebalance calls."""

    def __init__(self, mod, params, spy, caps_by_day, start):
        self.mod, self.spy_series = mod, spy
        days = [d.date() for d in spy.index]
        algo = mod.VolManaged.__new__(mod.VolManaged)
        algo.qr_params = params
        algo.spy = _Sym("SPY")
        hours = _Hours(days + [days[-1] + timedelta(days=3)])
        algo.securities = _Securities({algo.spy: _Sec(hours)})
        algo.start_date = datetime(start.year, start.month, start.day)
        pre = spy[spy.index < pd.Timestamp(start)]
        idx = pd.MultiIndex.from_tuples([(algo.spy, t + pd.Timedelta(hours=16)) for t in pre.index])
        algo.history = lambda *a, **k: pd.DataFrame({"close": pre.to_numpy()}, index=idx)
        algo.logs, algo.calls = [], []
        algo._qr_log = algo.logs.append
        algo.qr_slot_weight = lambda n: 0.98 / n
        algo.returns = []

        def rebalance(targets, tag, liquidate_others, band):
            algo.calls.append((algo.time.date(), dict(targets), band))
            return algo.returns.pop(0) if algo.returns else len(targets)
        algo.qr_rebalance = rebalance
        algo.qr_initialize()
        self.algo, self.caps_by_day, self.start = algo, caps_by_day, start

    def run(self, until=None, orders_after_event=None):
        a = self.algo
        closes = list(self.spy_series[self.spy_series.index < pd.Timestamp(self.start)])
        a.qr_close = {a.spy: closes}
        log = []
        for t, c in self.spy_series[self.spy_series.index >= pd.Timestamp(self.start)].items():
            if until is not None and t > until:
                break
            closes.append(float(c))
            a.time = datetime(t.year, t.month, t.day, 16)
            caps = self.caps_by_day(t)
            a.qr_eligible_info = {s: (cap, 1e7) for s, cap in caps.items()}
            for s in caps:
                a.securities.setdefault(s, _Sec(None))
            if orders_after_event is not None:
                a.returns = list(orders_after_event)
            n_calls = len(a.calls)
            a.qr_on_close(None)
            log.append(dict(date=t.date(), e=a.e_cur, basket=tuple(a.basket), rebalanced=len(a.calls) > n_calls,
                            targets=list(a.targets)))
        return log


def _caps(t):
    """30 names; ranks rotate once a quarter so reconstitutions change the basket."""
    q = (t.year * 4 + (t.month - 1) // 3) % 5
    return {_Sym(f"N{i:02d}"): 1e9 * (100 - ((i + 3 * q) % 30)) for i in range(30)}


@pytest.fixture
def s012(monkeypatch):
    return _load_main(monkeypatch, "S012_vol_managed", "s012_main")


def _params(**kw):
    p = dict(rv_short=21, cadence="monthly", band=0.10, slots=15, mode="timing")
    p.update(kw)
    return p


def test_s012_timing_rescales_only_on_rescale_days_and_outside_the_band(s012):
    spy = _closes(900)
    r = _S012Run(s012, _params(), spy, _caps, date(2009, 12, 1))
    log = r.run()
    days = [d.date() for d in spy.index]
    for prev, cur in zip(log, log[1:]):
        if cur["e"] != prev["e"]:
            i = days.index(cur["date"])
            assert days[i + 1].month != cur["date"].month                  # last session of the month
            assert abs(cur["e"] - prev["e"]) > 0.10
    assert any(x["e"] < 0.7 for x in log) and any(x["e"] == 1.0 for x in log)
    # every target recorded live is the rule applied to that day's window
    closes = list(spy)
    idx = {d.date(): i for i, d in enumerate(spy.index)}
    n0 = r.algo.s12["history_targets"]
    live = [x for p, x in zip(log, log[1:]) if len(x["targets"]) > len(p["targets"])]
    assert len(live) >= 15
    for x in live:
        assert x["targets"][-1] == S012.exposure_target(closes[: idx[x["date"]] + 1], 21)
    assert len(log[-1]["targets"]) - n0 == len(live) + (len(log[0]["targets"]) > n0)
    lines = [ln.split("|") for ln in r.algo.logs if ln.startswith("QRS012|e|")]
    assert len(lines) == len(log[-1]["targets"]) - n0
    assert all(float(a) == pytest.approx(b, abs=1e-6) for (_, _, _, a, _), b in zip(lines, log[-1]["targets"][n0:]))
    first = log[0]
    assert first["rebalanced"] and len(first["basket"]) == 15


def test_s012_basket_is_largest_15_reconstituted_quarterly(s012):
    spy = _closes(900)
    log = _S012Run(s012, _params(), spy, _caps, date(2009, 12, 1)).run()
    changes = [x for p, x in zip(log, log[1:]) if x["basket"] != p["basket"]]
    assert changes and all(x["date"].month in (1, 4, 7, 10) for x in changes)
    for x in log:
        ref = S012.largest({str(s): c for s, c in _caps(pd.Timestamp(x["date"])).items()}, 15)
        if x in changes or x is log[0]:
            assert [str(s) for s in x["basket"]] == ref


def test_s012_rebalance_window_after_events(s012):
    spy = _closes(900)
    r = _S012Run(s012, _params(), spy, _caps, date(2009, 12, 1))
    r.algo.returns = []
    log = r.run(orders_after_event=[3])            # every close places orders -> window runs 5 closes
    reb = [i for i, x in enumerate(log) if x["rebalanced"]]
    assert reb[:5] == [0, 1, 2, 3, 4]
    events = {0} | {i for i, (p, x) in enumerate(zip(log, log[1:]), 1)
                    if x["basket"] != p["basket"] or x["e"] != p["e"]}
    for i in reb:
        assert any(0 <= i - e < 5 for e in events)
    # a close that places no order ends the window
    r2 = _S012Run(s012, _params(), spy, _caps, date(2009, 12, 1))
    log2 = r2.run(orders_after_event=[0])
    assert not log2[1]["rebalanced"]
    for d, targets, band in r.algo.calls:
        assert band == 0.05 and len(targets) == 15
        w = next(iter(targets.values()))
        e = next(x["e"] for x in log if x["date"] == d)
        assert all(v == pytest.approx(e * 0.98 / 15) for v in targets.values()) and w > 0


def test_s012_control_b_uses_only_previous_targets(s012):
    spy = _closes(900)
    timing = _S012Run(s012, _params(), spy, _caps, date(2009, 12, 1))
    tlog = timing.run()
    ctrl = _S012Run(s012, _params(mode="control_b"), spy, _caps, date(2009, 12, 1))
    clog = ctrl.run()
    hist = list(ctrl.algo.targets)
    assert hist == list(timing.algo.targets)                          # same target series as the variation
    n0 = ctrl.algo.s12["history_targets"]
    assert n0 >= 12
    first = clog[0]
    assert first["e"] == pytest.approx(np.mean(hist[n0 - 12:n0]))
    prev_e = first["e"]
    for x in clog[1:]:
        if x["e"] != prev_e:
            k = len(x["targets"]) - 1                                  # today's target was appended last
            assert x["e"] == pytest.approx(np.mean(x["targets"][k - 12:k]))
            assert abs(x["e"] - prev_e) > 0.10
            prev_e = x["e"]
    assert np.mean([x["e"] for x in clog]) == pytest.approx(np.mean([x["e"] for x in tlog]), abs=0.15)


def test_s012_control_a_is_always_fully_invested(s012):
    log = _S012Run(s012, _params(mode="control_a"), _closes(900), _caps, date(2009, 12, 1)).run()
    assert all(x["e"] == 1.0 for x in log)


def test_s012_history_uses_only_bars_before_the_start(s012):
    spy = _closes(900)
    r = _S012Run(s012, _params(), spy, _caps, date(2009, 12, 1))
    assert r.algo.s12["history_last_date"] < "2009-12-01"
    assert r.algo.targets == [e for _, e in S012.history_targets(
        [d.date() for d in spy.index if d < pd.Timestamp("2009-12-01")],
        list(spy[spy.index < pd.Timestamp("2009-12-01")]), 21, "monthly", date(2009, 12, 1))]


def test_s012_decisions_have_no_lookahead(s012):
    """Truncation: running to day T gives the same exposure and basket at every day <= T as the full run."""
    spy = _closes(900)
    full = _S012Run(s012, _params(cadence="weekly"), spy, _caps, date(2009, 12, 1)).run()
    for cut in (pd.Timestamp("2010-03-15"), pd.Timestamp("2010-11-30")):
        part = _S012Run(s012, _params(cadence="weekly"), spy, _caps, date(2009, 12, 1)).run(until=cut)
        assert [(x["e"], x["basket"]) for x in part] == [(x["e"], x["basket"]) for x in full[:len(part)]]


# ---------------------------------------------------------------- S013 pure helpers
def test_lottery_stats():
    c = [100.0]
    for r in [0.01] * 15 + [0.10, -0.05, 0.03, 0.02, 0.04, 0.05]:
        c.append(c[-1] * (1 + r))
    assert S013.lottery_stat(c, "max") == pytest.approx(0.10)
    assert S013.lottery_stat(c, "max5") == pytest.approx(np.mean([0.10, 0.05, 0.04, 0.03, 0.02]))
    assert S013.lottery_stat(c[:21], "max") is None                     # 20 returns: not enough
    assert S013.lottery_stat([50.0] + c, "max") == pytest.approx(0.10)  # only the last 21 returns count


def test_excluded_ids_top_fraction_ties_and_short_histories():
    base = [100.0] * 22
    w = {}
    for i in range(10):
        x = list(base)
        x[-1] = 100.0 * (1 + 0.01 * i)
        w[f"s{i}"] = x
    w["tie"] = list(w["s9"])
    w["short"] = [100.0, 200.0]                                         # huge jump but only 1 return
    ex = S013.excluded_ids(w, 0.2, "max")
    assert ex == {"s9", "tie"}                                          # floor(0.2 x 11) = 2
    assert "short" not in S013.excluded_ids(w, 0.99, "max")
    assert S013.excluded_ids(w, 0.1, "max") == {"s9"}                   # tie broken by id
    assert S013.excluded_ids(w, 0.0, "max") == set()


def test_lottery_stat_has_no_lookahead():
    c = _closes(200)

    def signal(s):
        return pd.Series([S013.lottery_stat(s.iloc[: t + 1].to_numpy(), "max5") or np.nan for t in range(len(s))],
                         index=s.index)
    assert truncation_violations(signal, c, n_checks=20) == []


def test_allowed_order_is_the_null_order_minus_excluded():
    ids = [f"id{i}" for i in range(50)]
    null = NULL.pick_order(ids, 1, 17)
    ex = set(ids[::7])
    got = S013.allowed_order(null, ex)
    assert got == [k for k in null if k not in ex]
    # common random numbers: the first allowed name is the null's own first pick whenever that is allowed
    for session in range(1, 200):
        n = NULL.pick_order(ids, 2, session)
        a = S013.allowed_order(n, ex)
        if n[0] not in ex:
            assert a[0] == n[0]


def test_nullorder_is_a_byte_copy_of_x962():
    assert (ROOT / "strategies/S013_lottery_avoid/nullorder.py").read_bytes() == \
        (ROOT / "strategies/X962_random_pick/signals.py").read_bytes()


@pytest.fixture
def s013(monkeypatch):
    return _load_main(monkeypatch, "S013_lottery_avoid", "s013_main")


def _s013_algo(mod, q, seed=1):
    a = mod.LotteryAvoid.__new__(mod.LotteryAvoid)
    a.qr_params = dict(hold=60, slots=15, seed=seed, q=q, stat="max")
    a.qr_initialize()
    a.portfolio = {}
    a.calls = []
    a.qr_event_step = lambda exits, ranked, slots, tag: a.calls.append([str(s) for s in ranked])
    return a


def test_s013_equals_the_null_when_nothing_is_excluded_and_skips_excluded_names(s013):
    rng = np.random.default_rng(1)
    syms = [_Sym(f"S{i:03d}") for i in range(80)]
    windows = {s: list(100 * np.cumprod(1 + rng.normal(0, 0.02, 22))) for s in syms}
    data = types.SimpleNamespace(bars=_Bars({s: types.SimpleNamespace(is_fill_forward=False) for s in syms[:70]}))
    for q in (0.0, 0.2):
        a = _s013_algo(s013, q)
        a.qr_eligible, a.qr_close, a._qr_session = syms, windows, 42
        a.qr_on_close(data)
        null = NULL.pick_order([str(s) for s in syms[:70]], 1, 42)
        ex = S013.excluded_ids({str(s): w for s, w in windows.items()}, q, "max")
        assert a.calls[-1] == [k for k in null if k not in ex]
        assert len(ex) == int(q * 80)
        if q == 0.0:
            assert a.calls[-1] == null


# ---------------------------------------------------------------- canaries run the unchanged code
@pytest.mark.parametrize("copy,orig", [
    ("X963_h012_canary/s012.py", "S012_vol_managed/main.py"),
    ("X963_h012_canary/signals.py", "S012_vol_managed/signals.py"),
    ("X964_h013_canary/s013.py", "S013_lottery_avoid/main.py"),
    ("X964_h013_canary/signals.py", "S013_lottery_avoid/signals.py"),
    ("X964_h013_canary/nullorder.py", "S013_lottery_avoid/nullorder.py")])
def test_canary_copies_are_identical(copy, orig):
    assert (ROOT / "strategies" / copy).read_bytes() == (ROOT / "strategies" / orig).read_bytes()


def test_s012_forms_the_basket_at_the_first_close_with_eligible_names(s012):
    """E963-02 finding: the universe has no eligible names during its 20-session warm-up; the basket must
    then form at the first close that has them, not wait for the next quarter (D083 addendum)."""
    spy = _closes(900)
    warm = pd.Timestamp("2009-12-29")

    def caps(t):
        return {} if t < warm else _caps(t)
    r = _S012Run(s012, _params(), spy, caps, date(2009, 12, 1))
    log = r.run()
    first = next(i for i, x in enumerate(log) if x["basket"])
    assert log[first]["date"] == warm.date() and log[first]["rebalanced"]
    assert r.algo.s12["closes_without_eligible"] == first
    assert all(x["basket"] == log[first]["basket"] for x in log[first:] if x["date"] < date(2010, 1, 1))


def test_x964_reproduces_the_null_exactly():
    """E964-01 (S013 code, q = 0) must have exactly E962-22's fills and equity: S013's order is the null's."""
    from conftest import experiment_result
    from qresearch import results
    experiment_result("E964-01")
    cols = ["date", "symbol_id", "quantity", "price", "fee"]
    a = results.read_csv_gz(ROOT / "experiments/E964-01/fills.csv.gz")[cols].reset_index(drop=True)
    b = results.read_csv_gz(ROOT / "experiments/E962-22/fills.csv.gz")[cols].reset_index(drop=True)
    assert len(a) > 900 and a.equals(b)
    ea = results.read_csv_gz(ROOT / "experiments/E964-01/equity.csv.gz")["equity"]
    eb = results.read_csv_gz(ROOT / "experiments/E962-22/equity.csv.gz")["equity"]
    assert ea.equals(eb)


@pytest.mark.parametrize("eid,prefix", [("E963-03", "QRC63"), ("E964-01", "QRC64")])
def test_c03_canaries_passed(eid, prefix):
    import json as _json
    from conftest import experiment_result
    r = experiment_result(eid)
    assert r["status"].startswith("completed") and r["harness_summary"]["timing_violations"] == 0
    assert all(c["ok"] for c in r["integrity"] if c["level"] == "fail")
    lines = (ROOT / "experiments" / eid / "messages.txt").read_text().splitlines()   # result.json keeps 100 lines
    s = next(_json.loads(m.split("|", 2)[2]) for m in lines if m.startswith(prefix + "|summary|"))
    if prefix == "QRC63":
        assert s["rv_checks"] > 100 and s["rv_mismatches"] == 0 and s["last_close_mismatches"] == 0
        assert s["recon_checks"] == 8 and s["recon_mismatches"] == 0 and s["orders_outside_window"] == 0
        assert s["history_after_start"] == 0 and s["history_targets"] >= 12
    else:
        assert s["audits"] > 150 and s["max_checks"] > 5000
        assert s["max_mismatches"] == s["count_errors"] == s["order_errors"] == 0
        assert s["pairing_errors"] == s["short_excluded"] == s["window_not_today"] == 0
