"""Writes every H017 run config (research/phase2/H017_spec.md §6, frozen) before any H017 backtest: the canary E982-01,
the committed runs E017-01..08, the conditional runs E017-09..17 and the event-level diagnostic E983-01.
Owner 2026-10-03: only the canary E982-01 is authorised to run now. Every other config carries
`owner_approval_required`; the runner refuses it without `--owner-approved <decision id>` (E017-01 consumes Phase 2
slot 3; E983-01 computes post-event returns; E017-09..17 run only when the pre-registered conditions hold).

    PYTHONPATH=src python research/phase2/H017_make_configs.py                  (refuses to overwrite)
    PYTHONPATH=src python research/phase2/H017_make_configs.py --canary-rerun   (E982-02 only)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from qresearch import config, experiment, p2h017 as H  # noqa: E402

DATES = dict(split_scheme="2010", split="DEV", start=H.COMMON_START, end=H.END, warmup_start=H.WARMUP_START)
BASE = dict(
    cash=100000,
    universe={"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
              "sec_corrections": True},
    costs={"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
           "note": "D039: $7 per executed buy or sell order; slippage separate"},
    portfolio=dict(config.H017_PORTFOLIO), lean_version_id=18131, execution_model="d051",
    benchmarks=["E900-07", "E901-07"], programme="P2", cycle="P2C3")
EW_PORTFOLIO = {"max_position_weight": 1.0, "cash_buffer": 0.02, "buy_funding": "settled_cash_only",
                "gap_reserve": 0.15}
SPEC = "Pre-declared in research/phase2/H017_spec.md (frozen 2026-10-03)."
APPROVAL = "owner approval required (2026-10-03: implementation + canary only authorised)"
# §6 conditional runs: (id, change, what, condition)
CONDITIONAL = [
    ("E017-09", dict(stress=2), "2x slippage (PbNQ rule 6 / G4')", "only if PbNQ rules 1-5 or the Case C prerequisites hold"),
    ("E017-10", dict(stress=4), "4x slippage (reported)", "only if W1-W3 and R1-R4 pass"),
    ("E017-11", dict(stress=6), "6x slippage (reported)", "only if W1-W3 and R1-R4 pass"),
    ("E017-12", dict(hold_sessions=40), "P1: holding 40 sessions", "only if W1-W3 and R1-R4 pass"),
    ("E017-13", dict(hold_sessions=80), "P2: holding 80 sessions", "only if W1-W3 and R1-R4 pass"),
    ("E017-14", dict(quantile=0.80), "P3: top quintile (80th percentile)", "only if W1-W3 and R1-R4 pass"),
    ("E017-15", dict(reaction_lag=0), "P4: one-session reaction (close E-1 -> close E), decision at close E, entry "
                                      "at open E+1", "only if W1-W3 and R1-R4 pass"),
    ("E017-16", dict(slots=8, variant="H017_P5"), "P5: 8 slots (10% cap)", "only if W1-W3 and R1-R4 pass"),
    ("E017-17", dict(slots=12, variant="H017_P6"), "P6: 12 slots", "only if W1-W3 and R1-R4 pass"),
]


def s017(eid, kind, params, cash=100000, portfolio=None, **extra):
    p = dict(slots=10, hold_sessions=60, quantile=0.90, reaction_lag=1)
    p.update(params)
    c = dict(experiment_id=eid, kind=kind, hypothesis_id="H017" if kind in ("research", "sizing") else None,
             strategy_id="S017", strategy_version="v1.0", strategy_dir="strategies/S017_earnings_continuation",
             **DATES, **BASE, params=p)
    c["cash"] = cash
    if portfolio is not None:
        c["portfolio"] = portfolio
    c.update(extra)
    return c


def build():
    out = [canary(),
           s017(H.CANDIDATE, "research", dict(book="candidate"), owner_approval_required=APPROVAL,
                description=f"P2 H017 candidate: top-decile 2-session SPY-adjusted 8-K earnings reaction, entry E+2, "
                            f"60-session hold, 10 slots, $100K. CONSUMES PHASE 2 SLOT 3. {SPEC}"),
           s017(H.EW_H017, "benchmark", dict(book="ew", band=0.25), cash=10_000_000, portfolio=EW_PORTFOLIO,
                control_of=H.CANDIDATE, owner_approval_required=APPROVAL,
                description=f"P2 EW-H017: equal weight of the exact H017 universe (eligible and a verified domestic "
                            f"8-K earnings filer), monthly, 25% band (B901 mechanics), $10M paper notional. W3. {SPEC}")]
    for eid in H.RANDOM:
        seed = H.SEEDS[eid]
        out.append(s017(eid, "benchmark", dict(book="random", seed=seed), control_of=H.CANDIDATE,
                        owner_approval_required=APPROVAL,
                        description=f"P2 H017 random-event control seed {seed}: identical code path, timing, sizing, "
                                    f"holding, costs and daily k_t as {H.CANDIDATE}; only the selection differs. {SPEC}"))
    out.append(s017(H.SIZING_200K, "sizing", dict(book="candidate"), cash=200000, account_size_test_of=H.CANDIDATE,
                    sensitivity="$200K", owner_approval_required=APPROVAL,
                    description=f"P2 $200K sensitivity of {H.CANDIDATE}. Never decides, never rescues. {SPEC}"))
    for eid, ch, what, cond in CONDITIONAL:
        c = s017(eid, "research", dict(book="candidate"), robustness_of=H.CANDIDATE, run_condition=cond,
                 owner_approval_required=APPROVAL)
        if "stress" in ch:
            c["costs"] = dict(c["costs"], slippage_stress_multiple=ch["stress"])
        for k in ("hold_sessions", "quantile", "reaction_lag", "slots"):
            if k in ch:
                c["params"][k] = ch[k]
        if "variant" in ch:
            c["construction_variant"] = ch["variant"]
            c["portfolio"] = dict(config.H017_PORTFOLIO, max_positions=ch["slots"])
        c["description"] = f"P2 H017 conditional run of {H.CANDIDATE}: {what}; {cond}. {SPEC}"
        out.append(c)
    out.append(diagnostic())
    return out


def canary(eid=H.CANARY_FIRST, note=""):
    c = s017(eid, "infrastructure", dict(book="random", seed=0, canary=True))
    c.update(strategy_id="X982", strategy_version="v1.0", strategy_dir="strategies/X982_h017_canary",
             split="AUDIT", hypothesis_id=None,
             description="H017 non-candidate technical canary: byte copy of S017, random-event book seed 0 (not a "
                         "control seed), full window with the 2009-07-01 history-only warm-up. Checks the event table "
                         "hash, PIT reactions and breakpoints, E+2 entries, 60-session exits, 10 slots, k_t, held-stock "
                         "events, sizing, cash, costs. Verification; not a trial." + note)
    return c


def diagnostic():
    c = s017(H.EVENT_DIAG, "infrastructure", dict(book="diagnostic"), owner_approval_required=APPROVAL)
    c.update(strategy_id="X983", strategy_version="v1.0", strategy_dir="strategies/X983_h017_event_diagnostic",
             split="AUDIT", hypothesis_id=None, portfolio={"max_position_weight": 0.0, "cash_buffer": 0.02},
             description="H017 event-level diagnostic (spec §8): non-trading, aggregated; reaction decile x 60-session "
                         "excess return over SPY, month-clustered; used only within PbNQ rule 7; never a gate. "
                         "Computes post-event returns: runs only after its separate owner approval.")
    c["params"] = {"book": "diagnostic"}
    return c


CANARY_RERUN_NOTE = (" Re-run of E982-01 on the S017 code that also logs each entry's planned weight at placement (EP "
                     "lines), so the 10% cap is verified exactly (E982-01's offline sizing check measured weights at "
                     "the next-open fill, which move with the overnight gap).")


def main(argv):
    if "--canary-rerun" in argv:
        cfgs = [canary(H.CANARY, CANARY_RERUN_NOTE)]
    else:
        cfgs = build()
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
