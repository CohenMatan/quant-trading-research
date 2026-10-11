"""P10-CP1 (owner D204): write the S027 experiment configs from the pins in qresearch.p10h025 (run order of
research/phase10/H025_spec.md section 14). A config is written only when every pin its mode needs exists.

    PYTHONPATH=src python research/phase10/cp1/P10_CP1_configs.py audit|canary|null|real
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p10h025 as P  # noqa: E402

APPROVAL = ("H025 Insider Cluster Buying: no-return audit, canary, 5,000 matched null worlds, then ONE real "
            "development evaluation (owner 2026-10-11, D204)")
DESC = {
    "audit": "P10-CP1 (owner D204): H025 no-return feasibility audit on frozen Data v2 (S027 audit mode): every SEC "
             "ledger event mapped to the latest Data v2 review strictly before its trigger, verified identity (issuer "
             "CIK = the Data v2 identity CIK of an eligible security), multi-class rule, eligibility result, FF12 and "
             "market-cap quintile; in-host ledger digest. NO price is read for any response; no return. 2011-2017 only "
             "(H025 development); 2018-2021 and the Holdout sealed. Infrastructure. Default build (recorded).",
    "canary": "P10-CP1 (owner D204): H025 canary (S027 canary mode): ledger / review / identity / calendar / cooldown / "
              "entry and exit timing checks, SPY total return and corporate actions against fresh histories on "
              "NON-event windows, next-open timing on synthetic prices, statistic / gates / null machinery on "
              "SYNTHETIC responses only. No real H025 response computed. Infrastructure. Default build (recorded).",
    "null": "P10-CP1 (owner D204): H025 matched null, worlds 1..5,000 (S027 null mode): every evaluable event's excess "
            "replaced by a control drawn from its FF12 x market-cap-quintile pool (frozen hierarchy); real event "
            "responses only hashed (response-panel digest), never summarised. Infrastructure. Default build (recorded).",
    "real": "P10-CP1 (owner D204): the ONE real H025 development evaluation 2011-2017 (S027 real mode) with the pinned "
            "c_EVENT, null result, event-ledger and response-panel digests: G1-G5 and the pre-registered diagnostics. "
            "Research. Default build (recorded).",
}


def base(exp, mode, kind):
    return {
        "kind": kind, "hypothesis_id": "H025", "strategy_id": "S027", "strategy_version": "v1.0",
        "strategy_dir": "strategies/S027_h025_insider", "split_scheme": "2010", "split": "AUDIT" if kind != "research" else "IS",
        "start": "2011-01-03", "end": "2017-12-31", "warmup_start": "2008-07-01", "cash": 100000,
        "universe": {"min_market_cap": 2e9, "min_price": 5.0, "min_avg_dollar_volume": 5e6, "adv_days": 20,
                     "sec_corrections": False},
        "costs": {"slippage_bps": 10, "commission_model": "fixed_per_order", "commission_per_order": 7.0,
                  "note": "D039: $7 per executed buy or sell order; slippage separate (applied inside the engine)"},
        "portfolio": {"max_position_weight": 0.1, "cash_buffer": 0.02, "min_position_usd": 4000, "max_positions": 10,
                      "buy_funding": "settled_cash_only", "gap_reserve": 0.15},
        "lean_version_id": 18131, "execution_model": "d051", "benchmarks": ["E900-07"], "programme": "P10",
        "cycle": "P10H025", "experiment_id": exp, "stall_minutes": 240,
        "params": dict(mode=mode, spec_sha256=P.SPEC_SHA256, pred_code_sha256=P.PRED_CODE_SHA256,
                       h025_code_sha256=P.CODE_SHA256["src/qresearch/lean/qr_h025.py"],
                       payload_sha256=P.PAYLOAD_SHA256, calendar_sha256=P.CALENDAR_SHA256),
        "description": DESC[mode], "lean_version_policy": "default_build_digest_verified",
        "owner_approval_required": APPROVAL,
    }


def write(cfg):
    d = ROOT / "experiments" / cfg["experiment_id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(cfg, indent=1) + "\n")
    print("wrote", cfg["experiment_id"])


def main(mode):
    assert P.SPEC_SHA256 and P.PAYLOAD_SHA256 and all(P.CODE_SHA256.values()), "pins missing"
    if mode == "audit":
        for exp in P.AUDIT:
            write(base(exp, "audit", "infrastructure"))
    elif mode == "canary":
        c = base(P.CANARY, "canary", "infrastructure")
        c["params"]["in_host_ledger_sha256"] = P.IN_HOST_LEDGER_SHA256
        assert P.IN_HOST_LEDGER_SHA256
        write(c)
    elif mode == "null":
        assert P.IN_HOST_LEDGER_SHA256 and P.EVENT_LEDGER_SHA256
        for i, exp in enumerate(P.NULL_RUNS):
            if i > 0 and not P.RESPONSE_PANEL_SHA256:
                continue                         # the rerun is written once E027-04's panel digest is pinned
            c = base(exp, "null", "infrastructure")
            c["params"].update(in_host_ledger_sha256=P.IN_HOST_LEDGER_SHA256, seeds=list(P.NULL_SEEDS_RANGE))
            if i > 0:
                c["params"]["response_panel_sha256"] = P.RESPONSE_PANEL_SHA256
            write(c)
    elif mode == "real":
        assert P.C_EVENT is not None
        c = base(P.REAL, "real", "research")
        c["params"].update(in_host_ledger_sha256=P.IN_HOST_LEDGER_SHA256, c_event=P.C_EVENT,
                           null_result_sha256=P.NULL_RESULT_SHA256, threshold_commit=P.THRESHOLD_COMMIT,
                           response_panel_sha256=P.RESPONSE_PANEL_SHA256, event_ledger_sha256=P.EVENT_LEDGER_SHA256)
        write(c)


if __name__ == "__main__":
    main(sys.argv[1])
