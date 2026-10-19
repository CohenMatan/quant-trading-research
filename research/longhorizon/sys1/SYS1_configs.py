"""SYS-1 (owner D252): write the run configurations from the frozen E030-05 configuration and qresearch.sys1.

    PYTHONPATH=src python research/longhorizon/sys1/SYS1_configs.py canary     # E032-01 (before any run)
    PYTHONPATH=src python research/longhorizon/sys1/SYS1_configs.py eval       # E032-02 (after the canary digest pin)
    PYTHONPATH=src python research/longhorizon/sys1/SYS1_configs.py retry E032-0X <canary|eval>   # documented retry

The QuantConnect account cash stays at the frozen $100,000 of E030-05 (no order is ever placed; the runtime state of
the frozen chain stays identical); the SYS-1 account capital ($200,000, owner OD-2) is simulated in-host by qr_sys1.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import experiment, p13h028, sys1 as P  # noqa: E402

APPROVAL = ("SYS-1 Controlled Development Experiment: one canary E032-01, then one evaluation E032-02 only if every "
            "mandatory canary check passes; at most two documented infrastructure retries (owner 2026-10-19, D252)")
DESC = dict(
    canary=("SYS-1 canary (owner D252; research/longhorizon/sys1/SYS1_protocol.md section 11): S032 canary mode = the "
            "frozen H028 / SPY / LV15 reproduction (C1-C3), SPLV / USMV data (C4), account rules on seeded random scores "
            "and zero-return worlds (C5), costs by hand (C6), beta truncation (C7); NO SYS-1 arm result. H028 remains "
            "REJECTED. Infrastructure. Default build."),
    eval=("SYS-1 evaluation (owner D252; SYS1_protocol.md sections 6-13): the ONE single-account development run 2015-"
          "2021 at $200,000 (in-host): A0 SPY, A1 H028 sleeve + SPY, A2 LV15 + SPY, A3 SPLV + SPY, BM-X(A1-A3), D1-D3, "
          "at 0.10% and 0.20% slippage; FS-1..FS-6 offline (SYS1_eval.py). Development evidence only; H028 remains "
          "REJECTED; Holdout sealed. Research. Default build."))


def build(mode, eid):
    base = json.loads((ROOT / "experiments" / p13h028.REAL / "config.json").read_text())
    cfg = {k: v for k, v in base.items() if k not in ("params", "description", "owner_approval_required")}
    cfg.update(strategy_id="S032", strategy_version="v1.0", strategy_dir="strategies/S032_sys1_account",
               experiment_id=eid, hypothesis_id="H028", programme=P.PROGRAMME, cycle=P.CYCLE,
               kind="infrastructure" if mode == "canary" else "research", split="AUDIT" if mode == "canary" else "DEV",
               params=P.run_params(mode), description=DESC[mode], owner_approval_required=APPROVAL,
               note_capital="QuantConnect cash = the frozen E030-05 $100,000 (no orders); SYS-1 capital $200,000 is "
                            "simulated in-host (owner OD-2)")
    experiment.validate(cfg)
    return cfg


def write(mode, eid):
    d = ROOT / "experiments" / eid
    if (d / "result.json").exists():
        raise SystemExit(f"{eid} already ran")
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(build(mode, eid), indent=1) + "\n")
    print(f"wrote experiments/{eid}/config.json")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["canary"]:
        write("canary", P.CANARY)
    elif a[:1] == ["eval"]:
        write("eval", P.EVAL)
    elif a[:1] == ["retry"] and len(a) == 3 and a[1] in P.RETRIES and a[2] in ("canary", "eval"):
        write(a[2], a[1])
    else:
        raise SystemExit(__doc__)
