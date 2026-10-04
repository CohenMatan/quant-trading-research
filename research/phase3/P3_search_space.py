"""P3-CP1 support: SIZE of the proposed Phase 3 search space (arithmetic counts only; no configuration is generated,
evaluated or stored, no data is read). Compares the proposed constrained grammar with unconstrained combinatorial
search over the same indicator variants.

    python research/phase3/P3_search_space.py -> P3_search_space.json
"""
import json
from math import comb
from pathlib import Path

# ---- primary setups (one per strategy), by information family: variant counts from the proposed grids
PRIMARY = {
    "trend": {"T1 close > SMA(L), L in {50,100,150,200}": 4,
              "T2 SMA(S) > SMA(L), (S,L) in {(20,100),(50,150),(50,200)}": 3,
              "T3 21-session slope of SMA(L) > 0, L in {100,200}": 2},
    "momentum": {"M1 cross-sectional rank of return(K skip 21), K in {63,126,252} x top q in {10,20,30}%": 9,
                 "M2 time-series return(K) > 0, K in {63,126,252}": 3,
                 "M3 return(K) - SPY return(K) > 0, K in {63,126,252}": 3},
    "breakout": {"B1 close >= (1-x) max close(N), N in {63,126,252}, x in {0,5,10}%": 9},
    "pullback": {"R1 RSI(n) <= theta, (n,theta) in {(2,10),(2,20),(5,30),(14,40)}": 4,
                 "R2 close <= SMA(20) x (1-y), y in {3,6}%": 2,
                 "R3 Bollinger %b(20,2) <= z, z in {0,0.2}": 2},
}
# ---- optional confirmation (0 or 1), from a family different from the primary's
CONFIRM = {
    "trend": {"close > SMA200": 1, "SMA50 > SMA200": 1, "ADX(14) >= {20,25}": 2, "MACD(12,26) > 0": 1},
    "momentum": {"return(126) > 0": 1, "return(252 skip 21) > 0": 1, "RSI(14) >= {50,60}": 2,
                 "MACD line > signal(9)": 1},
    "breakout": {"close >= 0.9 x max close(252)": 1},
    "pullback": {"RSI(5) <= 30": 1, "close < SMA(20)": 1},
    "participation": {"relative volume 20/120 >= {1.0,1.25}": 2},
}
RISK = {"none": 1, "63-session realised-volatility cross-sectional rank <= {50,80}%": 2}
STAGE2_PER_CLUSTER = {"exits: H=63 (base), H=126 (N=20), primary-reversal (weekly, min 21, max 126), 3xATR(14) trailing "
                      "stop (max 126)": 4, "market regime overlay SPY > SMA200 for new entries: off/on": 2}
MAX_STAGE2_CLUSTERS = 3


def n(d):
    return sum(d.values())


def main():
    prim = {f: n(v) for f, v in PRIMARY.items()}
    conf = {f: n(v) for f, v in CONFIRM.items()}
    conf_total = sum(conf.values())
    risk = n(RISK)
    per_family = {}
    for f, p in prim.items():
        c = conf_total - conf.get(f, 0) + 1                    # other families' confirmations, or none
        per_family[f] = dict(primaries=p, confirmation_options=c, risk_options=risk, configs=p * c * risk)
    stage1 = sum(v["configs"] for v in per_family.values())
    stage2 = MAX_STAGE2_CLUSTERS * STAGE2_PER_CLUSTER[list(STAGE2_PER_CLUSTER)[0]] * 2
    # ---- unconstrained alternative: any AND-combination of 1..k of the same base condition variants (+ the risk
    # variants), each with the same grids, no family restriction, plus the 4 Stage-2 exits and regime overlay
    base = sum(prim.values()) + conf_total + (risk - 1)
    unconstrained = {f"up to {k} conditions": sum(comb(base, j) for j in range(1, k + 1)) for k in (3, 4, 6, 8)}
    unconstrained_with_exits = {k: v * 8 for k, v in unconstrained.items()}
    # an illustrative fine-grid parameter sweep of a single 7-indicator template
    fine = dict(template="MA length 50..250 step 5 (41) x RSI period 2..20 (19) x RSI threshold 20..80 step 1 (61) x "
                         "momentum 21..252 step 21 (12) x MACD fast/slow/signal 3 x 3 x 3 (27) x ATR window 5..30 (26) "
                         "x volume ratio 1.0..2.0 step 0.1 (11) x holding 5..126 step 1 (122)",
                configs=41 * 19 * 61 * 12 * 27 * 26 * 11 * 122)
    out = dict(stage1_per_family=per_family, stage1_total=stage1, stage2_max=stage2,
               total_configurations_budget=stage1 + stage2, base_condition_variants=base,
               primaries=PRIMARY, confirmations=CONFIRM, risk=RISK, stage2_per_cluster=STAGE2_PER_CLUSTER,
               max_conditions_per_strategy="1 primary + <=1 confirmation + <=1 risk filter (+ Stage 2: exit variant, "
                                           "optional regime overlay)",
               unconstrained_and_combinations=unconstrained,
               unconstrained_with_stage2_exits_and_regime=unconstrained_with_exits, fine_grid_example=fine)
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("stage1_per_family", "stage1_total", "stage2_max",
                                          "total_configurations_budget", "base_condition_variants",
                                          "unconstrained_and_combinations")}, indent=1))
    print("fine grid", f"{fine['configs']:.3e}")


if __name__ == "__main__":
    main()
