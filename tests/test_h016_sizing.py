"""H016 position sizing (owner 2026-10-02, option A): $4,000 minimum new position, D051 settled cash + 2% buffer +
15% gap reserve kept, AT MOST ONE top-up per newly opened position (minimum $250), no other resizing. Verified offline
with the harness's actual order planner (qr_harness.plan_orders / slot_weight) and the frozen top-up planner
(qr_h016.plan_topups), in a day-by-day simulation that mirrors S016: a decision at the close, fills at the next open
(optionally gapped), $7 per order, 10 bps slippage."""
import pytest

from conftest import ROOT, load_module
from test_commission import _load_harness

H = load_module(ROOT / "src/qresearch/lean/qr_h016.py", "qr_h016_sizing")
SLIP, FEE = 0.001, 7.0
PF = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 20,
      "buy_funding": "settled_cash_only", "gap_reserve": 0.15}


class Book:
    """S016's order sequence on constant close prices; orders fill at the next open = close x gap."""

    def __init__(self, h, cash, n=20, price=50.0):
        self.h, self.cash, self.n = h, float(cash), n
        self.px = {}
        self.price0 = price
        self.held, self.orders, self.log = {}, [], []
        self.target, self.awaiting, self.pending = {}, set(), []
        self.topups = {}
        self.min_cash = self.cash

    def pv(self):
        return self.cash + sum(q * self.px[k] for k, q in self.held.items())

    def _plan(self, targets, tag):
        items = []
        for k, w in targets.items():
            pend = sum(q for kk, q, _ in self.orders if kk == k)
            items.append((k, w, self.px[k], self.held.get(k, 0), pend, False))
        n_open = len(self.held) + sum(1 for k, q, _ in self.orders if q > 0 and k not in self.held)
        plan = self.h.plan_orders(items, self.pv(), self.cash, PF, SLIP, lambda q: FEE, 0.0, n_open)
        for k, q in plan["sells"] + plan["buys"]:
            self.orders.append((k, q, tag))
        return plan

    def rebalance(self, selection):
        for k in selection:
            self.px.setdefault(k, self.price0)
        sel, exits, entries = self.h_sel(selection)
        w = self.h.slot_weight(self.n, self.pv(), PF)
        self.pending = list(entries)
        for k in entries:
            self.target[k] = w * self.pv()
            self.awaiting.add(k)
        if exits:
            self._plan({k: 0.0 for k in exits}, "exit")
        self.close(rebalance=True)

    def h_sel(self, selection):
        return H.plan_selection(selection, self.held, self.n)

    def close(self, rebalance=False):
        w = self.h.slot_weight(self.n, self.pv(), PF)
        self.pending = [k for k in self.pending if k not in self.held]
        if self.pending:
            self._plan({k: w for k in self.pending}, "entry")
        open_keys = {k for k, _, _ in self.orders}
        cands = [(k, self.target[k], self.held[k] * self.px[k], self.px[k]) for k in sorted(self.awaiting)
                 if k in self.held and k not in open_keys]
        if cands:
            reserved = sum(q * self.px[k] * (1 + SLIP) * (1 + PF["gap_reserve"]) + FEE for k, q, _ in self.orders if q > 0)
            plan = H.plan_topups(cands, self.cash, self.pv(), PF["cash_buffer"], PF["gap_reserve"], SLIP, FEE, reserved)
            for k, *_ in cands:
                self.awaiting.discard(k)
            for k, q in plan.items():
                self.orders.append((k, q, "topup"))
                self.topups[k] = self.topups.get(k, 0) + 1

    def open(self, gap=1.0):
        for k, q, tag in self.orders:
            p = self.px[k] * gap
            if q < 0:
                self.cash += -q * p * (1 - SLIP) - FEE
                self.held[k] += q
                if self.held[k] == 0:
                    del self.held[k]
            else:
                self.cash -= q * p * (1 + SLIP) + FEE
                self.held[k] = self.held.get(k, 0) + q
            self.log.append((tag, k, q, p))
            self.min_cash = min(self.min_cash, self.cash)
        self.orders = []

    def day(self, gap=1.0):
        self.open(gap)
        self.close()


def run_formation(cash, gap=1.0, days=4):
    b = Book(_harness(), cash)
    b.rebalance([f"S{i:02d}" for i in range(40)])
    for _ in range(days):
        b.day(gap)
    return b


_H = {}


def _harness():
    return _H["h"]


@pytest.fixture(autouse=True)
def harness(monkeypatch):
    _H["h"] = _load_harness(monkeypatch)
    yield


def _new_buys(b):
    return [q * p for tag, k, q, p in b.log if tag == "entry"]


@pytest.mark.parametrize("cash", [100_000, 200_000])
def test_twenty_positions_form_and_are_topped_up_once(cash):
    b = run_formation(cash)
    assert len(b.held) == 20
    assert min(_new_buys(b)) >= 4000                                   # no new purchase below the minimum
    assert all(n == 1 for n in b.topups.values()) and len(b.topups) == 20   # exactly one top-up each here
    assert b.min_cash >= 0 and b.cash >= 0                              # no borrowing, no negative cash
    invested = 1 - b.cash / b.pv()
    assert 0.95 <= invested <= 0.98                                     # near-full, never above 98%
    for k, q in b.held.items():
        assert q * b.px[k] <= b.target[k] + b.px[k]                     # never above the original target (1 share)
    b.day()
    b.day()
    assert all(n == 1 for n in b.topups.values())                      # no repeated top-ups


def test_reserve_scaled_first_fill_then_top_up_amounts():
    b = run_formation(100_000)
    first = _new_buys(b)
    top = [q * p for tag, k, q, p in b.log if tag == "topup"]
    assert 4000 <= min(first) and max(first) < 4900                     # first fills scaled by the 15% reserve
    assert min(top) >= H.MIN_TOPUP_USD                                  # every top-up clears the threshold
    assert len([t for t in b.log if t[0] == "entry"]) == 20 and len(top) == 20


def test_price_gaps_never_cause_negative_cash():
    for gap in (1.05, 1.10, 1.149):
        b = run_formation(100_000, gap=gap)
        assert b.min_cash >= 0 and len(b.held) == 20


def test_cash_reconciles_with_commissions_and_slippage():
    b = run_formation(100_000, gap=1.03)
    spent = sum(q * p * (1 + SLIP) + FEE for tag, k, q, p in b.log if q > 0)
    assert b.cash == pytest.approx(100_000 - spent)
    assert len(b.log) * FEE == pytest.approx(sum(FEE for _ in b.log))


def test_partial_slot_replacement_follows_the_same_process():
    b = run_formation(100_000)
    old = dict(b.topups)
    sel = [k for k in sorted(b.held)][5:] + [f"N{i}" for i in range(5)]      # 5 exits, 5 replacements
    b.rebalance(sel + [f"Z{i}" for i in range(10)])
    for _ in range(4):
        b.day()
    assert len(b.held) == 20
    new = [k for k in b.held if k.startswith("N")]
    assert len(new) == 5 and all(b.topups.get(k, 0) <= 1 for k in new)
    assert all(b.topups[k] == old[k] for k in old if k in b.held)       # continuing holdings never topped up again
    assert min(q * p for tag, k, q, p in b.log if tag == "entry" and k.startswith("N")) >= 4000
    assert b.min_cash >= 0


def test_insufficient_settled_cash_is_never_borrowed():
    b = Book(_harness(), 100_000)
    b.rebalance([f"S{i:02d}" for i in range(20)])
    b.cash = 3_000.0                                                    # simulate cash drained before the fills
    b.orders = []
    for _ in range(3):
        b.day()
    assert b.min_cash >= 0 and len(b.held) == 0                          # nothing affordable -> nothing bought


def test_top_up_below_threshold_is_not_placed():
    assert H.MIN_TOPUP_USD == 250.0
    out = H.plan_topups([("A", 4900.0, 4700.0, 50.0)], 20_000, 100_000, 0.02, 0.15, SLIP, FEE)
    assert out == {}                                                    # $200 shortfall < $250 (trivial)
    out = H.plan_topups([("A", 4900.0, 4300.0, 50.0)], 20_000, 100_000, 0.02, 0.15, SLIP, FEE)
    assert out == {"A": 12}                                             # $600 -> 12 shares at $50
    # scaled below the threshold by scarce cash -> dropped, the others keep their funding
    out = H.plan_topups([("A", 4900.0, 4250.0, 50.0), ("B", 4900.0, 4250.0, 50.0)], 2_000 + 450, 100_000,
                        0.02, 0.15, SLIP, FEE)
    assert out == {} or all(q * 50 >= H.MIN_TOPUP_USD for q in out.values())


def test_multiple_simultaneous_fills_share_cash_without_overspending():
    cands = [(f"K{i}", 4900.0, 4250.0, 50.0) for i in range(20)]
    out = H.plan_topups(cands, 15_000, 100_000, 0.02, 0.15, SLIP, FEE)
    cost = sum(q * 50 * (1 + SLIP) * 1.15 + FEE for q in out.values())
    assert cost <= 15_000 - 0.02 * 100_000 + 1e-6
    assert all(q * 50 >= H.MIN_TOPUP_USD for q in out.values())


def test_200k_uses_the_same_rule():
    b = run_formation(200_000)
    assert len(b.held) == 20 and min(_new_buys(b)) >= 4000 and all(n == 1 for n in b.topups.values())


@pytest.mark.parametrize("cash", [100_000, 200_000])
def test_random_prices_and_gaps(cash):
    import random
    inv = []
    for seed in range(60):
        rnd = random.Random(seed)
        b = Book(_harness(), cash)
        sel = [f"S{i:02d}" for i in range(20)]
        for k in sel:
            b.px[k] = rnd.choice([rnd.uniform(15, 60), rnd.uniform(60, 250), rnd.uniform(250, 900)])
        b.rebalance(sel)
        for _ in range(4):
            b.day(gap=rnd.uniform(0.95, 1.08))
        assert b.min_cash >= 0 and len(b.held) >= 19                  # an unbuyable high price can leave one slot
        assert all(n == 1 for n in b.topups.values())
        assert all(q * b.px[k] <= b.target[k] + b.px[k] for k, q in b.held.items())
        inv.append(1 - b.cash / b.pv())
    inv.sort()
    assert inv[len(inv) // 2] >= (0.92 if cash == 100_000 else 0.94)


def test_canary_runs_the_identical_s016_code():
    s016 = (ROOT / "strategies/S016_gross_profitability/main.py").read_bytes()
    assert (ROOT / "strategies/X980_h016_canary/main.py").read_bytes() == s016    # same mechanics, every book
    assert b"MIN_TOPUP_USD" in s016 and b"plan_topups" in s016


def test_runner_uploads_the_h016_logic_only_for_strategies_that_import_it():
    import json
    from qresearch import run
    for eid in ("E980-01", "E016-01", "E016-02"):
        cfg = json.loads((ROOT / "experiments" / eid / "config.json").read_text())
        files = run.assemble_files(cfg, None, False)
        assert files["qr_h016.py"] == (ROOT / "src/qresearch/lean/qr_h016.py").read_text()
        assert any(n.startswith("qr_sec_data") for n in files) and "qr_industry.py" in files
    other = json.loads((ROOT / "experiments/E014-01/config.json").read_text())
    assert "qr_h016.py" not in run.assemble_files(other, None, False)
