"""X962 portfolio-structure diagnostic (pre-registered): deterministic, price-free random picks,
next-open orders only, and a controlled configuration grid (one factor changes at a time)."""
import json

import pytest

from conftest import ROOT, load_module
from qresearch import experiment

SIG = load_module(ROOT / "strategies/X962_random_pick/signals.py", "x962_signals")
IDS = [f"E962-{i:02d}" for i in range(1, 25)]


def _cfg(eid):
    return json.loads((ROOT / "experiments" / eid / "config.json").read_text())


def test_pick_order_is_deterministic_and_input_order_free():
    a = SIG.pick_order(["c", "a", "b", "d"], 1, 7)
    assert a == SIG.pick_order(["d", "b", "a", "c"], 1, 7) and sorted(a) == ["a", "b", "c", "d"]
    ids = [f"S{i:04d}" for i in range(200)]
    assert SIG.pick_order(ids, 1, 7) != SIG.pick_order(ids, 2, 7)      # seed matters
    assert SIG.pick_order(ids, 1, 7) != SIG.pick_order(ids, 1, 8)      # new draw every session


def test_selection_uses_no_price_information_and_trades_next_open():
    main = (ROOT / "strategies/X962_random_pick/main.py").read_text()
    assert "self.qr_event_step(" in main and "def qr_on_close" in main
    for forbidden in ("market_order", "set_holdings", "qr_close", "qr_volume", "history("):
        assert forbidden not in main


def test_grid_is_valid_and_controlled():
    cfgs = {e: _cfg(e) for e in IDS}
    for c in cfgs.values():
        experiment.validate(c)
        assert c["kind"] == "infrastructure" and c["start"] == "2010-01-04" and c["end"] == "2017-12-29"
        assert c["costs"]["commission_per_order"] == 7.0 and c["costs"]["slippage_bps"] == 10
        assert c["portfolio"]["max_positions"] == c["params"]["slots"]
    key = lambda c: (c["params"]["slots"], c["cash"], c["params"]["hold"])
    base = (15, 100000, 20)
    for e, c in cfgs.items():                       # every non-base cell differs from base in ONE factor
        k = key(c)
        if c["diagnostic_series"] in ("S", "A", "H"):
            assert sum(a != b for a, b in zip(k, base)) <= 1, e
    for k in {key(c) for c in cfgs.values()}:       # three seeds per cell
        assert sorted(c["params"]["seed"] for c in cfgs.values() if key(c) == k) == [1, 2, 3]
