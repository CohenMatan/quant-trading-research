"""Phase 2 S014 (H014 and its controls): pure signal functions against independent reference code,
look-ahead truncation, masks, ranking, exits, the algorithm's decision logic on a fake harness, canary
copies and the committed configs (research/phase2/P2_spec.md, D094)."""
import json
import sys
import types
from collections import deque

import numpy as np
import pandas as pd
import pytest

from conftest import ROOT, load_module
from qresearch import config, experiment

SIG = load_module(ROOT / "strategies/S014_trend_pullback/signals.py", "s014_signals")
NULL = load_module(ROOT / "strategies/X962_random_pick/signals.py", "x962_signals_p2")


def _path(n=700, seed=3, drift=0.0006):
    rng = np.random.default_rng(seed)
    return 50 * np.exp(np.cumsum(rng.normal(drift, 0.018, n)))


def wilder_reference(closes):
    """Textbook Wilder RSI14 over the whole series (seed = mean of the first 14 changes), one value per close
    from the 15th on. Written independently of signals.py (plain loop)."""
    d = np.diff(np.asarray(closes, float))
    g, l = np.maximum(d, 0), np.maximum(-d, 0)
    ag, al = g[:14].mean(), l[:14].mean()
    vals = []
    for i in range(14, len(d) + 1):
        if i > 14:
            ag = (13 * ag + g[i - 1]) / 14
            al = (13 * al + l[i - 1]) / 14
        vals.append(100.0 if al == 0 else 100 - 100 / (1 + ag / al))
    return np.array(vals)


# ---------------------------------------------------------------- RSI14
def test_rsi_weights_sum_to_one_and_match_the_recursion():
    w = SIG.rsi_weights()
    assert len(w) == 250 and w.sum() == pytest.approx(1.0, abs=1e-12)
    c = _path(400)
    for end in (260, 300, 399):
        win = c[end - 250:end + 1]                              # 251 closes = 250 changes ending at `end`
        ref = wilder_reference(win)[-1]
        got = SIG.rsi_matrix(c[None, :end + 1], days=1)[0, -1]
        assert got == pytest.approx(ref, abs=1e-9)


def test_rsi_matrix_days_are_each_over_their_own_250_changes():
    c = _path(500, seed=9)
    m = SIG.rsi_matrix(c[None, :], days=9)[0]
    for j in range(9):
        end = len(c) - 9 + j
        assert m[j] == pytest.approx(wilder_reference(c[end - 250:end + 1])[-1], abs=1e-9)


def test_rsi_equals_full_history_wilder_to_seven_digits():
    c = _path(1500, seed=11)
    full = wilder_reference(c)
    got = SIG.rsi_matrix(c[None, :], days=9)[0]
    assert np.max(np.abs(got - full[-9:])) < 1e-5


def test_rsi_edge_cases_and_scale_invariance():
    up = np.linspace(10, 50, 300)
    flat = np.full(300, 20.0)
    r = SIG.rsi_matrix(np.vstack([up, flat]), days=2)
    assert np.all(r[0] == 100.0) and np.all(r[1] == 50.0)
    c = _path(300, seed=4)
    a = SIG.rsi_matrix(c[None, :])
    b = SIG.rsi_matrix(3.7 * c[None, :])                         # a split/dividend rescale of the window
    assert np.allclose(a, b, atol=1e-9)


# ---------------------------------------------------------------- features, look-ahead
def test_features_match_direct_definitions():
    c = _path(259, seed=2)
    f = SIG.features(c[None, :], [c[-2] * 1.01])
    assert f["close"][0] == c[-1]
    assert f["ma50"][0] == pytest.approx(c[-50:].mean()) and f["ma200"][0] == pytest.approx(c[-200:].mean())
    assert f["mom"][0] == pytest.approx(c[-22] / c[-253] - 1)      # 12-1: T-252 -> T-21
    assert f["rsi"].shape == (1, 9)
    with pytest.raises(ValueError):
        SIG.features(c[None, :258], [1.0])


def _timeline(closes, highs, mode="h014", **rule):
    """Entry signal and features at every close from MIN_BARS on, each from the window ending at that close."""
    out = {}
    for t in range(SIG.MIN_BARS - 1, len(closes)):
        f = SIG.features(closes[None, t - SIG.MIN_BARS + 1:t + 1], [highs[t - 1]])
        out[t] = (bool(SIG.entry_mask(f, mode, **rule)[0]), float(f["rsi"][0, -1]), float(f["mom"][0]))
    return pd.Series({k: v[1] + 1000 * v[0] + v[2] for k, v in out.items()})


def test_signals_have_no_lookahead():
    from qresearch.lookahead import truncation_violations
    c = _path(420, seed=21)
    h = c * 1.005
    hist = pd.DataFrame({"c": c, "h": h}, index=pd.bdate_range("2009-01-02", periods=len(c)))

    def fn(df):
        s = _timeline(df["c"].to_numpy(), df["h"].to_numpy())
        out = pd.Series(np.nan, index=df.index)
        if len(s):
            out.iloc[list(s.index)] = s.to_numpy()
        return out
    assert truncation_violations(fn, hist, n_checks=25) == []
    # changing every bar after T leaves the decision at T unchanged
    t = 330
    c2 = c.copy()
    c2[t + 1:] *= 0.5
    assert _timeline(c, h)[t] == _timeline(c2, h)[t]


# ---------------------------------------------------------------- entry masks
def _f(close, ma50, ma200, rsi, high_prev, mom=0.1):
    rsi = np.atleast_2d(np.asarray(rsi, float))
    n = rsi.shape[0]
    arr = lambda x: np.full(n, float(x)) if np.isscalar(x) else np.asarray(x, float)  # noqa: E731
    return dict(close=arr(close), ma50=arr(ma50), ma200=arr(ma200), rsi=rsi, high_prev=arr(high_prev), mom=arr(mom))


def test_h014_mask_worked_example_and_each_condition():
    # RSI at T-8..T: 38 on T-3, 36 on T-2, 47 at T; trend holds; Close(T) > High(T-1)
    rsi = [60, 60, 60, 55, 50, 38, 36, 44, 47]
    ok = _f(105, 102, 100, rsi, 104)
    assert SIG.entry_mask(ok, "h014")[0]
    assert not SIG.entry_mask(_f(99, 102, 100, rsi, 98), "h014")[0]            # U1 fails
    assert not SIG.entry_mask(_f(105, 99, 100, rsi, 104), "h014")[0]           # U2 fails
    assert not SIG.entry_mask(_f(105, 102, 100, rsi, 105), "h014")[0]          # R2: Close must exceed High(T-1)
    assert not SIG.entry_mask(_f(105, 102, 100, rsi[:-1] + [45], 104), "h014")[0]   # R1: RSI(T) must be > 45
    assert not SIG.entry_mask(_f(105, 102, 100, [60] * 8 + [47], 104), "h014")[0]   # P: no pullback


def test_pullback_window_is_the_previous_w_sessions_only():
    base = [60] * 9
    at = lambda k: base[:k] + [39] + base[k + 1:]   # noqa: E731  (RSI <= 40 only at index k; index 8 = T)
    for w in (3, 5, 8):
        for k in range(9):
            r = at(k)
            r[8] = 50 if k != 8 else 39
            f = _f(105, 102, 100, r, 104)
            expect = 8 - w <= k <= 7                      # T-w ... T-1
            assert bool(SIG.entry_mask(f, "h014", window=w)[0]) == expect, (w, k)
    with pytest.raises(ValueError):
        SIG.entry_mask(_f(105, 102, 100, base, 104), "h014", window=9)


def test_control_masks():
    rsi = [[60] * 8 + [39], [60] * 8 + [41]]
    f = _f([105, 105], [102, 102], [100, 100], rsi, [200, 200])
    assert SIG.entry_mask(f, "c1").tolist() == [True, True]
    assert SIG.entry_mask(f, "rand").tolist() == [True, True]
    assert SIG.entry_mask(f, "c2").tolist() == [True, False]                  # RSI14(T) <= 40 today
    assert SIG.entry_mask(f, "h014").tolist() == [False, False]
    with pytest.raises(ValueError):
        SIG.entry_mask(f, "other")


def test_rule_thresholds_are_parameters():
    rsi = [60] * 5 + [44, 60, 60, 47]
    f = _f(105, 102, 100, rsi, 104)
    assert not SIG.entry_mask(f, "h014")[0]
    assert SIG.entry_mask(f, "h014", rsi_pullback=45)[0]
    assert not SIG.entry_mask(f, "h014", rsi_pullback=45, rsi_recovery=50)[0]


# ---------------------------------------------------------------- ranking and exits
def test_momentum_order_highest_first_ties_by_id_nan_last():
    ids = ["B", "A", "C", "D", "E"]
    assert SIG.momentum_order(ids, [0.2, 0.2, 0.5, float("nan"), -0.1]) == ["C", "A", "B", "E", "D"]


def test_random_order_is_x962_and_deterministic():
    assert (ROOT / "strategies/S014_trend_pullback/nullorder.py").read_bytes() == \
        (ROOT / "strategies/X962_random_pick/signals.py").read_bytes()
    ids = [f"S{i}" for i in range(40)]
    assert NULL.pick_order(ids, 1, 7) == NULL.pick_order(list(reversed(ids)), 1, 7)
    assert NULL.pick_order(ids, 1, 7) != NULL.pick_order(ids, 2, 7)


@pytest.mark.parametrize("held,close,ma200,variant,limit,sig,expect", [
    (5, 99, 100, "A", 63, False, "ma200"), (5, 99, 100, "B", 126, True, "ma200"),
    (62, 101, 100, "A", 63, False, None), (63, 101, 100, "A", 63, False, "time"),
    (63, 101, 100, "A", 63, True, "roll"), (125, 101, 100, "B", 126, True, None),
    (126, 101, 100, "B", 126, True, "time"), (0, 101, 100, "A", 63, True, None),
    (None, 101, 100, "A", 63, True, None), (63, 100, 100, "A", 63, False, "time")])
def test_exit_decision(held, close, ma200, variant, limit, sig, expect):
    assert SIG.exit_decision(held, close, ma200, variant, limit, sig) == expect


# ---------------------------------------------------------------- the algorithm on a fake harness
class _Sym(str):
    @property
    def id(self):
        return str(self)

    @property
    def value(self):
        return str(self)


class _Bars(dict):
    def contains_key(self, k):
        return k in self


def _load_main(monkeypatch, sdir="S014_trend_pullback", module="s014_main"):
    ai = types.ModuleType("AlgorithmImports")
    monkeypatch.setitem(sys.modules, "AlgorithmImports", ai)
    h = types.ModuleType("qr_harness")

    class QRAlgorithm:
        pass
    h.QRAlgorithm = QRAlgorithm
    monkeypatch.setitem(sys.modules, "qr_harness", h)
    monkeypatch.syspath_prepend(str(ROOT / "strategies" / sdir))
    for m in ("signals", "nullorder"):
        monkeypatch.delitem(sys.modules, m, raising=False)
    return load_module(ROOT / "strategies" / sdir / "main.py", module)


def _series_up(seed, n=SIG.MIN_BARS):
    """A clear uptrend (Close > MA200, MA50 > MA200) with a seed-dependent slope, so momentum differs."""
    rng = np.random.default_rng(seed)
    return list(50 * np.exp(np.cumsum(rng.normal(0.002 + 0.0005 * seed, 0.004, n))))


def _algo(mod, mode="h014", variant="A", limit=63, seed=None, cls=None, **rule):
    cls = cls or mod.TrendPullback
    a = cls.__new__(cls)
    p = dict(mode=mode, exit=variant, limit=limit, slots=12, rsi_pullback=40, window=5, rsi_recovery=45)
    p.update(rule)
    if seed is not None:
        p["seed"] = seed
    a.qr_params = p
    a.qr_initialize()
    a.calls, a.logs = [], []
    a._qr_log = a.logs.append
    a.qr_event_step = lambda exits, ranked, slots, tag: a.calls.append((sorted(map(str, exits)), [str(s) for s in ranked]))
    a._qr_entry, a._qr_session = {}, 100
    a.qr_sessions_held = lambda s: None if s not in a._qr_entry else a._qr_session - a._qr_entry[s]["session"]
    a.portfolio = []
    return a


def _setup(a, syms, closes, highs=None, held=(), real=None):
    a.qr_eligible = list(syms)
    a.qr_close = {s: deque(c, maxlen=SIG.MIN_BARS) for s, c in zip(syms, closes)}
    a.qr_high = {s: deque(highs[i] if highs else [x * 1.01 for x in c], maxlen=SIG.MIN_BARS)
                 for i, (s, c) in enumerate(zip(syms, closes))}
    a.portfolio = [types.SimpleNamespace(key=s, value=types.SimpleNamespace(invested=s in held)) for s in syms]
    real = syms if real is None else real
    return types.SimpleNamespace(bars=_Bars({s: types.SimpleNamespace(is_fill_forward=False) for s in real}))


def test_c1_ranks_trend_names_by_momentum_and_skips_short_or_stale(monkeypatch):
    mod = _load_main(monkeypatch)
    a = _algo(mod, mode="c1")
    syms = [_Sym(f"S{i}") for i in range(6)]
    closes = [_series_up(i) for i in range(6)]
    closes[5] = list(reversed(closes[5]))                     # a downtrend: not a candidate
    closes[4] = closes[4][-200:]                              # fewer than 259 closes: not evaluated
    data = _setup(a, syms, closes, real=syms[:4] + syms[4:])
    del data.bars[syms[3]]                                    # no real bar today
    a.qr_on_close(data)
    mom = {str(s): c[-22] / c[-253] - 1 for s, c in zip(syms[:3], closes[:3])}
    assert a.calls[-1] == ([], sorted(mom, key=lambda k: (-mom[k], k)))


def test_rand_uses_the_seeded_order_over_trend_names(monkeypatch):
    mod = _load_main(monkeypatch)
    a = _algo(mod, mode="rand", seed=2)
    syms = [_Sym(f"S{i:02d}") for i in range(10)]
    data = _setup(a, syms, [_series_up(i) for i in range(10)])
    a.qr_on_close(data)
    assert a.calls[-1][1] == NULL.pick_order([str(s) for s in syms], 2, 100)


def test_time_exit_roll_and_ma200_exit(monkeypatch):
    mod = _load_main(monkeypatch)
    a = _algo(mod, mode="c1", variant="A", limit=63)
    up = [_Sym("UP1"), _Sym("UP2")]
    down = _Sym("DN")
    closes = [_series_up(1), _series_up(2), list(reversed(_series_up(3)))]
    data = _setup(a, up + [down], closes, held=set(up + [down]))
    a.qr_eligible = [up[0], down]                              # UP2 held but no longer eligible
    a._qr_entry = {up[0]: dict(session=37), up[1]: dict(session=37), down: dict(session=90)}
    a.qr_on_close(data)
    exits, ranked = a.calls[-1]
    assert exits == ["DN", "UP2"]                              # MA200 break; UP2 not a candidate -> time exit
    assert a._qr_entry[up[0]]["session"] == 100                # UP1 is a c1 candidate: rolled, clock restarts
    assert a.s14["rolls"] == 1 and a.s14["exits_time"] == 1 and a.s14["exits_ma200"] == 1
    b = _algo(mod, mode="c1", variant="B", limit=63)
    data = _setup(b, up, closes[:2], held=set(up))
    b._qr_entry = {up[0]: dict(session=37), up[1]: dict(session=38)}
    b.qr_on_close(data)
    assert b.calls[-1][0] == ["UP1"] and b.s14["rolls"] == 0  # B never rolls; UP2 held 62 < 63


def test_h014_signal_reaches_the_order_step(monkeypatch):
    mod = _load_main(monkeypatch)
    rng = np.random.default_rng(0)
    for trial in range(200):            # search a synthetic path with a signal at its last close
        c = list(50 * np.exp(np.cumsum(rng.normal(0.0015, 0.02, SIG.MIN_BARS))))
        h = [x * 1.003 for x in c]
        f = SIG.features(np.array([c]), [h[-2]])
        if SIG.entry_mask(f, "h014")[0]:
            break
    else:
        pytest.skip("no synthetic signal found")
    a = _algo(mod, mode="h014")
    s = _Sym("SIG")
    data = _setup(a, [s], [c], highs=[h])
    a.qr_on_close(data)
    assert a.calls[-1] == ([], ["SIG"]) and a.s14["signals_sum"] == 1


# ---------------------------------------------------------------- canary copies and configs
@pytest.mark.parametrize("copy,orig", [("X965_h014_canary/s014.py", "S014_trend_pullback/main.py"),
                                       ("X965_h014_canary/signals.py", "S014_trend_pullback/signals.py"),
                                       ("X965_h014_canary/nullorder.py", "S014_trend_pullback/nullorder.py")])
def test_canary_copies_are_identical(copy, orig):
    assert (ROOT / "strategies" / copy).read_bytes() == (ROOT / "strategies" / orig).read_bytes()


P2_IDS = [f"E014-{i:02d}" for i in range(1, 15)]


def _cfg(eid):
    return json.loads((config.EXPERIMENTS_DIR / eid / "config.json").read_text())


def test_committed_configs_match_the_frozen_spec():
    cfgs = {e: _cfg(e) for e in P2_IDS}
    for e, c in cfgs.items():
        experiment.validate(c)
        assert (c["split"], c["start"], c["end"]) == ("DEV", "2010-01-04", "2021-12-31")
        assert c["programme"] == "P2" and c["cycle"] == "P2C1" and c["lean_version_id"] == 18131
        p = c["params"]
        assert (p["rsi_pullback"], p["window"], p["rsi_recovery"], p["slots"]) == (40, 5, 45, 12)
        assert p["limit"] == {"A": 63, "B": 126}[p["exit"]]
        assert c["strategy_version"] == {"A": "v1.0", "B": "v1.1"}[p["exit"]]
        assert c["costs"]["slippage_bps"] == 10 and "slippage_stress_multiple" not in c["costs"]
        assert c["cash"] == (200000 if c["kind"] == "sizing" else 100000)
    assert [cfgs[e]["kind"] for e in P2_IDS].count("research") == 2
    assert cfgs["E014-01"]["params"]["exit"] == "A" and cfgs["E014-02"]["params"]["exit"] == "B"
    modes = [(cfgs[e]["params"]["exit"], cfgs[e]["params"]["mode"], cfgs[e]["params"].get("seed")) for e in P2_IDS[2:12]]
    assert modes == [(v, m, s) for v in "AB" for m, s in (("c1", None), ("c2", None), ("rand", 1), ("rand", 2), ("rand", 3))]
    for e in P2_IDS[2:12]:        # controls differ from their candidate only in mode/seed and bookkeeping
        c, cand = cfgs[e], cfgs[cfgs[e]["control_of"]]
        assert c["kind"] == "benchmark" and cand["params"]["exit"] == c["params"]["exit"]
        strip = lambda x: {k: v for k, v in x.items() if k not in ("mode", "seed")}   # noqa: E731
        assert strip(c["params"]) == strip(cand["params"])
        for k in ("universe", "costs", "portfolio", "cash", "strategy_dir", "strategy_version"):
            assert c[k] == cand[k]


def test_no_p2_config_reaches_locked_data():
    for p in config.EXPERIMENTS_DIR.glob("E01[4]-*/config.json"):
        c = json.loads(p.read_text())
        assert c["end"] <= "2021-12-31"
    for p in config.EXPERIMENTS_DIR.glob("E965-*/config.json"):
        assert json.loads(p.read_text())["end"] <= "2012-12-31"


def test_dev_split_rules():
    c = _cfg("E014-01")
    bad = dict(c, programme=None)
    with pytest.raises(experiment.ConfigError):
        experiment.validate(bad)
    with pytest.raises(Exception):
        experiment.validate(dict(c, end="2022-01-03"))


def test_x965_canary_logic_on_empty_and_normal_closes(monkeypatch):
    """E965-01 stopped on the first close (no eligible names during the universe warm-up): the canary's
    audits must handle empty closes, and agree with S014 on a normal close (no rank or roll errors)."""
    for m in ("s014", "signals", "nullorder"):
        monkeypatch.delitem(sys.modules, m, raising=False)
    mod = _load_main(monkeypatch, sdir="X965_h014_canary", module="x965_main")
    for mode, seed in (("c1", None), ("rand", 3), ("h014", None)):
        a = _algo(mod, mode=mode, seed=seed, variant="A", limit=63, cls=mod.H014Canary)
        a._qr_session = 101                                   # not an audit session (history not faked)
        from datetime import datetime
        a.time = datetime(2010, 3, 1, 16)
        data = _setup(a, [], [])
        a.qr_eligible_info = {}
        a.qr_on_close(data)                                   # empty universe: no error
        syms = [_Sym(f"S{i}") for i in range(5)]
        data = _setup(a, syms, [_series_up(i) for i in range(5)], held={syms[0]})
        a.qr_eligible_info = {s: (5e9, 1e7) for s in syms}
        a._qr_entry = {syms[0]: dict(session=101 - 63)}
        a.qr_on_close(data)
        c = a.c
        assert c["rank_errors"] == 0 and c["ranked_not_eligible"] == 0 and c["ranked_cap_below_2b"] == 0
        assert c["roll_errors"] == 0 and c["time_exit_errors"] == 0
        if mode != "h014":
            assert c["roll_checks"] == 1


def test_p2_canaries_passed():
    """X965 canaries (E965-04 recovered, E965-02, E965-03) pass every audit and offline check; E965-03 reproduces
    byte-identically (D096/D097). Reads committed outputs only."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("p2chk", ROOT / "research/phase2/P2_canary_check.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for e in m.CANARIES:
        r = m.check(e)
        assert r["ok"], (e, r["problems"])
    assert m.reproduction("E965-03")["reproduced"] is True
    r3 = m.check("E965-03")
    assert r3["rolls"] > 100 and r3["ma200_exits"] > 20
    r2 = m.check("E965-02")
    assert r2["min_position_check"]["planned_below_5000"] == 0 and r2["skipped_min_position"] > 0
