"""P3-CP1 support: analytic trading-cost feasibility of technical portfolios under the frozen cost model ($7 per order,
10 bps slippage per side, D051 2% buffer). NO returns of any kind. For a slot-filling book with N equal slots held H
sessions on average, at starting equity PV:
    round trips a year per slot = 252 / H
    cost per round trip = 2 x slippage x position + 2 x $7,  position = 0.98 x PV / N
    portfolio cost a year (share of equity) = N x (252 / H) x (2 x 0.001 x 0.98 PV / N + 14) / PV
                                            = (252 / H) x (0.00196 + 14 N / PV)
(conservative: equity growth later lowers the commission share). R4 caps realised costs at 1.5% a year.

    python research/phase3/P3_cost_feasibility.py -> P3_cost_feasibility.json
"""
import json
from pathlib import Path

SLIP, FEE, BUF = 0.001, 7.0, 0.02
HS = (5, 10, 21, 42, 63, 84, 126, 252)
NS = (5, 8, 10, 12, 15, 20, 25, 30)


def cost(H, N, pv):
    return 252 / H * (2 * SLIP * (1 - BUF) + 2 * FEE * N / pv)


def max_n(H, pv, cap, n_max=60):
    ok = [n for n in range(1, n_max + 1) if cost(H, n, pv) <= cap and (1 - BUF) * pv / n >= 4000]
    return max(ok) if ok else 0


def min_h(N, pv, cap):
    return 252 * (2 * SLIP * (1 - BUF) + 2 * FEE * N / pv) / cap


def main():
    out = dict(model="cost a year = (252/H) * (2*0.001*0.98 + 14*N/PV); R4 cap 1.5%/yr", tables={})
    for pv in (100_000, 200_000):
        out["tables"][f"${pv // 1000}K"] = {f"H={h}": {f"N={n}": round(cost(h, n, pv), 4) for n in NS} for h in HS}
        out[f"max_N_${pv // 1000}K"] = {f"H={h}": {"cap_1.5%": max_n(h, pv, 0.015), "cap_1.25%": max_n(h, pv, 0.0125)}
                                        for h in HS}
        out[f"min_H_${pv // 1000}K"] = {f"N={n}": {"cap_1.5%": round(min_h(n, pv, 0.015), 1),
                                                   "cap_1.25%": round(min_h(n, pv, 0.0125), 1)} for n in NS}
    out["slippage_only_cost_by_H"] = {f"H={h}": round(252 / h * 2 * SLIP * (1 - BUF), 4) for h in HS}
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    for k in ("slippage_only_cost_by_H", "max_N_$100K", "min_H_$100K"):
        print(k, json.dumps(out[k]))


if __name__ == "__main__":
    main()
