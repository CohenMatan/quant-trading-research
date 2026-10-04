"""Phase 3 shadow-book engine (qr_p3_engine): order sizing identical to the harness's own plan_orders (D051 settled
cash, 15% gap reserve, $4,000 minimum, slot cap, $7, 10 bps) on random scenarios; next-open execution; the fixed
horizon (exit fills exactly H sessions after entry); corporate actions; stale and delisting exits; candidate selection
(strength order, mask, held stocks skipped, no queue); and the primary null (within-date permutation) destroying a
planted signal-return link while keeping entry counts."""
import numpy as np
import pytest

from conftest import ROOT, load_module
from test_commission import _load_harness

E = load_module(ROOT / "src/qresearch/lean/qr_p3_engine.py", "qr_p3_engine_t")
PF = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
      "buy_funding": "settled_cash_only", "gap_reserve": 0.15}


@pytest.fixture
def harness(monkeypatch):
    return _load_harness(monkeypatch)


def test_sizing_equals_harness_plan_orders(harness):
    rng = np.random.default_rng(3)
    for trial in range(300):
        B = E.Books(1, 10, 63, 100_000)
        n_held = int(rng.integers(0, 10))
        prices = rng.uniform(5, 400, 60)
        for k in range(n_held):
            B.state[0, k], B.sid[0, k], B.qty[0, k] = E.HELD, 50 + k, int(rng.integers(10, 200))
        B.cash[0] = float(rng.uniform(-500, 40_000))
        pv = float(B.equity(prices)[0])
        n_sells = int(rng.integers(0, min(n_held, 3) + 1))
        free = 10 - n_held
        stocks = list(rng.choice(40, size=free, replace=False))
        w = harness.slot_weight(10, pv, PF)
        items = [(f"X{k}", 0.0, prices[50 + k], B.qty[0, k], 0.0, False) for k in range(n_sells)]
        items += [(s, w, prices[s], 0.0, 0.0, False) for s in stocks]
        ref = harness.plan_orders(items, pv, float(B.cash[0]), PF, 0.001, lambda q: 7.0, 0.0, n_held)
        got = B.plan_entries(0, stocks, prices, pv, n_sells)
        assert [(int(s), q) for s, q in got] == [(int(s), q) for s, q in ref["buys"]], trial


def world(days=400, S=30, seed=5):
    rng = np.random.default_rng(seed)
    close = 40 * np.exp(np.cumsum(rng.normal(0.0003, 0.015, (days, S)), axis=0))
    gap = np.exp(rng.normal(0, 0.004, (days, S)))
    open_ = np.vstack([close[:1], close[:-1]]) * gap
    return open_, close


def run_book(open_, close, candidates_of, H=63, N=10, cash=100_000):
    """Day loop exactly as the LEAN host drives the engine: open fills, stale check, mark, exits, entries."""
    days, S = close.shape
    B = E.Books(1, N, H, cash)
    B.fills = []
    has = np.ones(S, dtype=bool)
    last_sess = np.zeros(S, dtype=np.int64)
    eq = []
    for t in range(days):
        B.open_fills(open_[t], has, t)
        last_sess[:] = t
        B.stale_exits(t, last_sess, close[t])
        pv = float(B.equity(close[t])[0])
        due = B.exits_due(t)
        cands = E.select_candidates(np.array(candidates_of(t)), np.ones(S, dtype=bool), np.arange(S), B.blocked(0),
                                    int(B.free()[0]))
        B.plan_entries(0, cands, close[t], pv, int(due.sum()))
        eq.append(float(B.equity(close[t])[0]))
    return B, np.array(eq)


def test_timing_next_open_and_exact_horizon():
    open_, close = world()
    buys = {}
    B2 = E.Books(1, 10, 63, 100_000)
    B2.fills = []
    has = np.ones(30, dtype=bool)
    log = []
    for t in range(close.shape[0]):
        n0 = len(B2.fills)
        B2.open_fills(open_[t], has, t)
        for rec in B2.fills[n0:]:
            log.append((t,) + rec)
        pv = float(B2.equity(close[t])[0])
        due = B2.exits_due(t)
        order = np.array([t % 30, (t * 7) % 30, (t * 11 + 3) % 30])
        c = E.select_candidates(order, np.ones(30, dtype=bool), np.arange(30), B2.blocked(0), int(B2.free()[0]))
        for s, q in B2.plan_entries(0, c, close[t], pv, int(due.sum())):
            buys[(s, t)] = q
        assert all(f[5] == 7.0 for f in B2.fills)
    held = {}
    for t, b, kind, s, q, px, fee in log:
        if kind == "buy":
            assert px == pytest.approx(open_[t, s] * 1.001)
            assert (s, t - 1) in buys and buys[(s, t - 1)] == q            # decided at the previous close
            held[s] = t
        else:
            assert px == pytest.approx(open_[t, s] * 0.999)
            assert t - held.pop(s) == 63                                    # exactly H sessions after entry
    assert len(held) <= 10


def test_never_more_than_n_positions_and_no_negative_cash():
    open_, close = world(days=600, S=50)
    B, eq = run_book(open_, close, lambda t: list(np.random.default_rng(t).permutation(50)[:6]))
    assert (B.state != E.EMPTY).sum() <= 10
    assert B.cash[0] >= 0
    assert eq.min() > 0


def test_corporate_actions_and_forced_exits():
    B = E.Books(2, 10, 63, 10_000)
    B.state[0, 0], B.sid[0, 0], B.qty[0, 0] = E.HELD, 3, 101
    B.state[1, 0], B.sid[1, 0], B.qty[1, 0] = E.PENDING, 3, 50
    B.split(3, 0.5, 40.0)                                   # 2-for-1
    assert B.qty[0, 0] == 202 and B.qty[1, 0] == 100
    B.split(3, 2 / 3, 30.0)                                 # 3-for-2: 202 / (2/3) = 303 whole shares
    assert B.qty[0, 0] == 303
    c0 = B.cash[0]
    B.dividend(3, 0.25)
    assert B.cash[0] == pytest.approx(c0 + 303 * 0.25) and B.cash[1] == 10_000
    B.delist(3, 12.0)
    assert B.state[0, 0] == E.EMPTY and B.cash[0] == pytest.approx(c0 + 303 * 0.25 + 303 * 12.0 - 7.0)
    assert B.state[1, 0] == E.EMPTY and B.cash[1] == 10_000      # pending buy cancelled, no fee
    B.state[0, 1], B.sid[0, 1], B.qty[0, 1] = E.HELD, 5, 10
    last = np.zeros(10, dtype=np.int64)
    last[5] = 100
    B.stale_exits(110, last, np.full(10, 20.0))             # 10 sessions: not yet
    assert B.state[0, 1] == E.HELD
    B.stale_exits(111, last, np.full(10, 20.0))             # > 10 sessions without a real bar
    assert B.state[0, 1] == E.EMPTY and B.counts["forced_stale"] == 1


def test_select_candidates_order_mask_blocked_no_queue():
    strength = np.array([0.1, 0.9, np.nan, 0.5, 0.5, 0.7])
    order = E.strength_order(strength)
    assert list(order[:5]) == [1, 5, 3, 4, 0]
    mask = np.array([True, True, False, True, True, False])
    ident = np.arange(6)
    assert E.select_candidates(order, mask, ident, {1}, 2) == [3, 4]
    assert E.select_candidates(order, mask, ident, set(), 0) == []
    perm = np.array([5, 4, 3, 2, 1, 0])
    assert E.select_candidates(order, mask, perm, set(), 2) == [4, 2]   # signal rows 1, 3 trade stocks 4, 2


def test_null_permutation_destroys_planted_edge_but_keeps_counts():
    rng = np.random.default_rng(11)
    days, S = 500, 60
    sig = rng.normal(size=(days, S))
    r = 0.002 * sig + rng.normal(0, 0.01, (days, S))            # tomorrow's return driven by today's signal
    gains_real, gains_null, n_real, n_null = [], [], 0, 0
    for t in range(days - 1):
        order = E.strength_order(sig[t])
        mask = sig[t] > 1.0
        a = E.select_candidates(order, mask, np.arange(S), set(), 5)
        b = E.select_candidates(order, mask, E.null_permutation(1, t, S), set(), 5)
        gains_real += list(r[t, a])
        gains_null += list(r[t, b])
        n_real += len(a)
        n_null += len(b)
    assert n_real == n_null                                      # identical signal frequency
    assert np.mean(gains_real) > 0.002 and abs(np.mean(gains_null)) < 0.001
    assert (E.null_permutation(1, 7, 20) == E.null_permutation(1, 7, 20)).all()
    assert (E.null_permutation(1, 7, 20) != E.null_permutation(2, 7, 20)).any()
    assert (E.null_permutation(1, 70, 20, block=63) == E.null_permutation(1, 100, 20, block=63)).all()


def test_trace_records_only_traced_books_and_delisting_fills():
    """Finalist trace (P3_spec.md section 15): only the traced books' fills are recorded; a delisting close is recorded
    as a fill (the fidelity host flushes fills after corporate actions, so forced exits are reported)."""
    B = E.Books(3, 10, 63, 100_000)
    B.fills, B.trace = [], {1}
    price = np.full(5, 50.0)
    for b in range(3):
        B.plan_entries(b, [2], price, 100_000.0, 0)
    B.open_fills(price, np.ones(5, bool), 1)
    assert [f[0] for f in B.fills] == [1]
    B.delist(2, 48.0)
    assert [(f[0], f[1]) for f in B.fills] == [(1, "buy"), (1, "delist")]
    assert B.counts["forced_delist"] == 3
