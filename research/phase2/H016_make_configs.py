"""Writes the configs of H016's canary and committed development runs (research/phase2/H016_spec.md §7, frozen,
D116), before any H016 backtest. The conditional robustness configs (§9) are written only with --robustness, and
only after the evaluation has recorded that the trigger (G1, G2 and G3 all pass on E016-01) holds.

    PYTHONPATH=src python research/phase2/H016_make_configs.py                 (refuses to overwrite)
    PYTHONPATH=src python research/phase2/H016_make_configs.py --robustness
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from qresearch import config, experiment, p2h016  # noqa: E402

DATES = dict(split_scheme="2010", split="DEV", start=p2h016.COMMON_START, end=p2h016.END, warmup_start="2008-07-01")
BASE = dict(
    cash=100000,
    universe={"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
              "sec_corrections": True},
    costs={"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
           "note": "D039: $7 per executed buy or sell order; slippage separate"},
    portfolio=dict(config.H016_PORTFOLIO), lean_version_id=18131, execution_model="d051",
    benchmarks=["E900-07", "E901-07"], programme="P2", cycle="P2C2")
EW_PORTFOLIO = {"max_position_weight": 1.0, "cash_buffer": 0.02, "buy_funding": "settled_cash_only",
                "gap_reserve": 0.15}
SPEC = "Pre-declared in research/phase2/H016_spec.md (frozen, D116)."
SEEDS = (1, 2, 3, 4, 5)
# §7 conditional robustness: (id, change, what)
ROBUSTNESS = [("E016-09", dict(stress=2), "2x slippage (G4b)"),
              ("E016-10", dict(stress=4), "4x slippage (reported)"),
              ("E016-11", dict(stress=6), "6x slippage (reported)"),
              ("E016-12", dict(slots=15), "P1: 15 slots"),
              ("E016-13", dict(slots=25, variant="H016_P2"), "P2: 25 slots, minimum new position $3,200"),
              ("E016-14", dict(months=[1, 4, 7, 10]), "P3: rebalance Jan/Apr/Jul/Oct"),
              ("E016-15", dict(months=[2, 5, 8, 11]), "P4: rebalance Feb/May/Aug/Nov"),
              ("E016-16", dict(months=[3, 9]), "P5: semiannual Mar/Sep"),
              ("E016-17", dict(max_age_days=120), "P6: GP/A freshness 120 days")]


def s016(eid, kind, params, cash=100000, portfolio=None, **extra):
    p = dict(slots=20, months=[3, 6, 9, 12])
    p.update(params)
    c = dict(experiment_id=eid, kind=kind, hypothesis_id="H016" if kind in ("research", "sizing") else None,
             strategy_id="S016", strategy_version="v1.0", strategy_dir="strategies/S016_gross_profitability",
             **DATES, **BASE, params=p)
    c["cash"] = cash
    if portfolio is not None:
        c["portfolio"] = portfolio
    c.update(extra)
    return c


def build():
    out = [s016(p2h016.CANDIDATE, "research", dict(book="gpa"),
                description=f"P2 H016 candidate: top 20 by GP/A (True TTM gross profit / same-quarter total assets), "
                            f"quarterly, $100K, one-time top-up rule (D116). Consumes Phase 2 slot 2. {SPEC}"),
           s016(p2h016.EW_H016, "benchmark", dict(book="ew", band=0.25), cash=10_000_000, portfolio=EW_PORTFOLIO,
                control_of=p2h016.CANDIDATE,
                description=f"P2 EW-H016: equal weight of the exact H016 universe, monthly, 25% band (B901 mechanics), "
                            f"$10M paper notional. Primary benchmark of G1/G3/G4. {SPEC}")]
    for eid, seed in zip(p2h016.RANDOM, SEEDS):
        out.append(s016(eid, "benchmark", dict(book="random", seed=seed), control_of=p2h016.CANDIDATE,
                        description=f"P2 H016 random control seed {seed}: same universe, 20 slots, schedule, costs and "
                                    f"position rules as {p2h016.CANDIDATE}; only the ranking differs. {SPEC}"))
    out.append(s016(p2h016.SIZING_200K, "sizing", dict(book="gpa"), cash=200000,
                    account_size_test_of=p2h016.CANDIDATE, sensitivity="$200K",
                    description=f"P2 $200K sensitivity of {p2h016.CANDIDATE}. Never decides, never rescues. {SPEC}"))
    out.append(canary())
    return out


def canary():
    c = s016("E980-01", "infrastructure", dict(book="random", seed=0, canary=True))
    c.update(strategy_id="X980", strategy_version="v1.0", strategy_dir="strategies/X980_h016_canary",
             split="AUDIT", hypothesis_id=None,
             description="H016 non-candidate technical canary: byte copy of S016, random book seed 0 (not a control "
                         "seed), full common window. Checks PIT timing, universe exclusions, quarterly dates, 20 "
                         "positions, the $4,000 minimum, the 15% reserve, at most one top-up >= $250 per new "
                         "position, no leverage, cash/commission reconciliation, the 2010-03-01 start. The GP/A "
                         "ranking is shadow-computed only (counts and a hash). Verification; not a trial.")
    return c


def robustness():
    out = []
    for eid, ch, what in ROBUSTNESS:
        p = dict(book="gpa")
        extra = dict(robustness_of=p2h016.CANDIDATE)
        c = s016(eid, "research", p, **extra)
        if "stress" in ch:
            c["costs"] = dict(c["costs"], slippage_stress_multiple=ch["stress"])
        for k in ("slots", "months", "max_age_days"):
            if k in ch:
                c["params"][k] = ch[k]
        if ch.get("variant") == "H016_P2":
            c["construction_variant"] = "H016_P2"
            c["portfolio"] = dict(config.H016_PORTFOLIO, max_positions=25,
                                  min_position_usd=config.H016_PORTFOLIO["min_position_usd"] * 20 // 25)
        c["description"] = f"P2 H016 conditional robustness of {p2h016.CANDIDATE}: {what}. {SPEC}"
        out.append(c)
    return out


def main(argv):
    cfgs = robustness() if "--robustness" in argv else build()
    for c in cfgs:
        experiment.validate(c)
        d = Path("experiments") / c["experiment_id"]
        if (d / "config.json").exists():
            raise SystemExit(f"{d}/config.json exists; refusing to overwrite")
    for c in cfgs:
        d = Path("experiments") / c["experiment_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
        print("wrote", d / "config.json")


if __name__ == "__main__":
    main(sys.argv[1:])
