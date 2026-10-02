"""H016 prerequisite 7 (owner 2026-10-02): can the approved portfolio rules (20 equal positions, $4,500 minimum new
position, D051: settled-cash funding, 2% buffer, 15% gap reserve) actually form and maintain the portfolio?
Deterministic simulation with the harness's own pure order planner (qr_harness.plan_orders / slot_weight): constant
prices, fills at planned quantities, $7 per order, 10 bps slippage; formation from all-cash over up to 6 sessions.
No market data, no strategy returns. Output: research/phase2/H016_position_rule_check.json"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLIP, FEE, PX = 0.001, 7.0, 50.0


def harness():
    stub = types.ModuleType("AlgorithmImports")

    class _A:
        def __init__(self, *a, **k):
            pass
    for n in ("FeeModel", "CashAmount", "OrderFee", "QCAlgorithm"):
        setattr(stub, n, _A)
    sys.modules["AlgorithmImports"] = stub
    p = types.ModuleType("qr_params")
    p.EXPERIMENT = {}
    sys.modules["qr_params"] = p
    sys.path.insert(0, str(ROOT / "src/qresearch/lean"))
    spec = importlib.util.spec_from_file_location("h", ROOT / "src/qresearch/lean/qr_harness.py")
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    return h


def simulate(h, pv0, minpos, gap, mode, n=20, days=6):
    pf = {"max_position_weight": 0.10, "cash_buffer": 0.02, "min_position_usd": minpos, "max_positions": n,
          "buy_funding": "settled_cash_only", "gap_reserve": gap}
    cash, held, orders = pv0, {}, 0
    names = [f"S{i}" for i in range(n)]
    for _ in range(days):
        pv = cash + sum(q * PX for q in held.values())
        w = h.slot_weight(n, pv, pf)
        if mode == "affordable":
            per = w * pv * (1 + SLIP) * (1 + gap) + FEE
            k = max(0, int((cash - 0.02 * pv) // per))
            items = [(s, w, PX, 0, 0, False) for s in [s for s in names if s not in held][:k]]
        elif mode == "build":
            items = [(s, w, PX, held.get(s, 0), 0, False) for s in names]
        else:
            items = [(s, w, PX, 0, 0, False) for s in names if s not in held]
        if not items:
            break
        plan = h.plan_orders(items, pv, cash, pf, SLIP, lambda q: FEE, 0.0, len(held))
        if not plan["buys"]:
            break
        for s, q in plan["buys"]:
            held[s] = held.get(s, 0) + q
            cash -= q * PX * (1 + SLIP) + FEE
            orders += 1
    pv = cash + sum(q * PX for q in held.values())
    return dict(positions=len(held), invested=round(1 - cash / pv, 3),
                avg_position_usd=round(sum(q * PX for q in held.values()) / max(len(held), 1)), orders=orders)


CASES = {
    "approved rules as written ($4,500 min, 15% gap reserve), entries scaled by the planner": (100000, 4500, 0.15, "new"),
    "A: $4,000 min, 15% gap reserve, positions built to slot weight from settled cash": (100000, 4000, 0.15, "build"),
    "A without building ($4,000 min, scaled entries only)": (100000, 4000, 0.15, "new"),
    "B: 5% gap reserve for H016, $4,500 min": (100000, 4500, 0.05, "new"),
    "C: approved rules, only entries settled cash funds at full size": (100000, 4500, 0.15, "affordable"),
    "$200K, approved rules, scaled entries": (200000, 4500, 0.15, "new"),
    "$200K, approved rules, positions built to slot weight": (200000, 4500, 0.15, "build"),
}


def main():
    h = harness()
    res = {k: simulate(h, *v) for k, v in CASES.items()}
    (ROOT / "research/phase2/H016_position_rule_check.json").write_text(json.dumps(res, indent=1) + "\n")
    return res


if __name__ == "__main__":
    for k, v in main().items():
        print(k, v)
