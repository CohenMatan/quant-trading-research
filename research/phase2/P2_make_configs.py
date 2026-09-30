"""Writes the configs of Phase 2's committed H014 development runs (research/phase2/P2_spec.md §6, D094)
and the X965 canaries, before any H014 backtest. The conditional robustness configs (§9) are written
only with --robustness CHOSEN_ID, and only after P2_eval.py has recorded that the trigger holds.

    PYTHONPATH=src python research/phase2/P2_make_configs.py                    (refuses to overwrite)
    PYTHONPATH=src python research/phase2/P2_make_configs.py --robustness E014-01
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from qresearch import config, experiment  # noqa: E402

DEV = dict(split_scheme="2010", split="DEV", start="2010-01-04", end="2021-12-31")
BASE = dict(
    cash=100000,
    universe={"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20},
    costs={"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
           "note": "D039: $7 per executed buy or sell order; slippage separate"},
    portfolio=dict(config.RESEARCH_PORTFOLIOS["d051"]), lean_version_id=18131, execution_model="d051",
    benchmarks=["E900-07", "E901-07"], programme="P2", cycle="P2C1")
RULE = dict(rsi_pullback=40, window=5, rsi_recovery=45, slots=12)
EXIT = {"A": dict(version="v1.0", limit=63), "B": dict(version="v1.1", limit=126)}
SPEC = "Pre-declared in research/phase2/P2_spec.md (frozen, D094)."
CANDIDATE = {"A": "E014-01", "B": "E014-02"}
# §9: fixed IDs whichever candidate is chosen; (id, change, what)
ROBUSTNESS = [("E014-15", dict(stress=2), "2x slippage (G4b)"),
              ("E014-16", dict(stress=4), "4x slippage (reported)"),
              ("E014-17", dict(stress=6), "6x slippage (reported)"),
              ("E014-18", dict(rsi_pullback=35), "RSI pullback threshold 35"),
              ("E014-19", dict(rsi_pullback=45), "RSI pullback threshold 45"),
              ("E014-20", dict(window=3), "pullback window 3 sessions"),
              ("E014-21", dict(window=8), "pullback window 8 sessions"),
              ("E014-22", dict(limit={"A": 42, "B": 84}), "horizon 42 (A) / cap 84 (B)"),
              ("E014-23", dict(limit={"A": 84, "B": 168}), "horizon 84 (A) / cap 168 (B)")]


def s014(eid, kind, variant, mode, seed=None, cash=100000, **extra):
    p = dict(mode=mode, exit=variant, limit=EXIT[variant]["limit"], **RULE)
    if seed is not None:
        p["seed"] = seed
    c = dict(experiment_id=eid, kind=kind, hypothesis_id="H014" if kind in ("research", "sizing") else None,
             strategy_id="S014", strategy_version=EXIT[variant]["version"],
             strategy_dir="strategies/S014_trend_pullback", **DEV, **BASE, params=p)
    c["cash"] = cash
    c.update(extra)
    return c


def build():
    out = []
    for variant in ("A", "B"):
        out.append(s014(CANDIDATE[variant], "research", variant, "h014",
                        description=f"P2 H014 candidate {variant} (S014 {EXIT[variant]['version']}) on DEV 2010-2021. {SPEC}"))
    n = 3
    for variant in ("A", "B"):
        cand = CANDIDATE[variant]
        for mode, seed, name in (("c1", None, "C1 trend-only"), ("c2", None, "C2 pullback without recovery"),
                                 ("rand", 1, "R random uptrend seed 1"), ("rand", 2, "R random uptrend seed 2"),
                                 ("rand", 3, "R random uptrend seed 3")):
            out.append(s014(f"E014-{n:02d}", "benchmark", variant, mode, seed=seed, control_of=cand,
                            description=f"P2 control {name}, exit {variant} (same code, universe, slots, costs and "
                                        f"exit as {cand}). Benchmark, never a candidate. {SPEC}"))
            n += 1
    for variant in ("A", "B"):
        out.append(s014(f"E014-{n:02d}", "sizing", variant, "h014", cash=200000,
                        account_size_test_of=CANDIDATE[variant], sensitivity="$200K",
                        description=f"P2 $200K sensitivity (12 slots) of {CANDIDATE[variant]}. Diagnostic, "
                                    f"never used for selection. {SPEC}"))
        n += 1
    out += canaries()
    return out


def canaries():
    au = dict(split_scheme="2010", split="AUDIT")
    base = {k: v for k, v in BASE.items()}

    def x(eid, start, end, params, desc, cash=100000):
        c = dict(experiment_id=eid, kind="infrastructure", hypothesis_id=None, strategy_id="X965",
                 strategy_version="v1.1", strategy_dir="strategies/X965_h014_canary", **au, start=start, end=end,
                 **base, params=params, description=desc + " Verification; not a trial.")
        c["cash"] = cash
        return c
    # E965-01 ran with canary v1.0 and stopped on a canary-audit defect (D096); E965-04 re-runs it with v1.1
    return [
        x("E965-04", "2010-01-04", "2012-12-31",
          dict(mode="h014", exit="A", limit=20, rsi_pullback=30, window=4, rsi_recovery=50, slots=12),
          "P2 H014 canary: unchanged S014 code, H014 entry with NON-candidate thresholds (RSI 30/50, window 4) "
          "and a 20-session horizon with roll, 2010-2012, $100K."),
        x("E965-02", "2010-01-04", "2011-12-30",
          dict(mode="rand", exit="B", limit=30, rsi_pullback=40, window=5, rsi_recovery=45, slots=12, seed=7),
          "P2 canary: random-uptrend mode, seed 7 (not a control seed), exit B with a 30-session cap, $60K so "
          "that the $5,000 minimum position binds (slot weight raised, 11-position size cap).", cash=60000),
        x("E965-03", "2010-01-04", "2011-12-30",
          dict(mode="c1", exit="A", limit=20, rsi_pullback=40, window=5, rsi_recovery=45, slots=12),
          "P2 canary: trend-only mode with a 20-session horizon (frequent horizon rolls and MA200 exits), $100K."),
    ]


def robustness(chosen_id):
    """§9 configs for the chosen candidate: only called once the trigger is recorded by P2_eval.py."""
    cand = json.loads((config.EXPERIMENTS_DIR / chosen_id / "config.json").read_text())
    variant = cand["params"]["exit"]
    out = []
    for eid, change, what in ROBUSTNESS:
        c = json.loads(json.dumps(cand))
        c["experiment_id"] = eid
        c["robustness_of"] = chosen_id
        for k, v in change.items():
            if k == "stress":
                c["costs"]["slippage_stress_multiple"] = v
            elif k == "limit":
                c["params"]["limit"] = v[variant]
            else:
                c["params"][k] = v
        c["description"] = f"P2 conditional robustness of {chosen_id}: {what}. {SPEC} §9"
        out.append(c)
    return out


def write(cfgs):
    for c in cfgs:
        experiment.validate(c)
    for c in cfgs:
        d = config.EXPERIMENTS_DIR / c["experiment_id"]
        if (d / "config.json").exists():
            raise SystemExit(f"{c['experiment_id']} already has a config; refusing to overwrite")
    for c in cfgs:
        d = config.EXPERIMENTS_DIR / c["experiment_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
        print("wrote", c["experiment_id"])


def main(argv):
    if len(argv) == 2 and argv[0] == "--robustness":
        res = json.loads((Path(__file__).parent / "P2_results.json").read_text())
        if not res.get("robustness_trigger", {}).get("triggered") or res["selection"]["chosen_id"] != argv[1]:
            raise SystemExit("the §9 trigger is not recorded for this candidate in P2_results.json")
        write(robustness(argv[1]))
    else:
        write(build())


if __name__ == "__main__":
    main(sys.argv[1:])
