"""Writes the H021-A run configs (research/phase6/H021A_spec.md section 11).

  python research/phase6/H021A_make_configs.py canary -> experiments/E989-01/config.json (fidelity canary)
  python research/phase6/H021A_make_configs.py null   -> experiments/E022-01..05/config.json (null batches)
  python research/phase6/H021A_make_configs.py real   -> experiments/E022-06/config.json (needs the pinned threshold)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p6h021  # noqa: E402

APPROVAL = "H021-A sector relative-momentum falsification test (owner authorisation 2026-10-06, D160)"


def base():
    c = json.loads((ROOT / "experiments/E988-01/config.json").read_text())
    for k in ("experiment_id", "params", "description"):
        c.pop(k, None)
    c.update(kind="infrastructure", hypothesis_id=None, strategy_id="X989", strategy_version="v1.0",
             strategy_dir="strategies/X989_h021_sector", split="AUDIT", start="2017-12-01", end="2017-12-31",
             programme="P6", cycle="P6H021")
    return c


def s022():
    c = base()
    c.update(strategy_id="S022", strategy_dir="strategies/S022_h021_sector", hypothesis_id="H021",
             owner_approval_required=APPROVAL)
    return c


def write(eid, c):
    d = ROOT / "experiments" / eid
    d.mkdir(exist_ok=True)
    c["experiment_id"] = eid
    (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
    print("wrote", eid)


def canary():
    c = base()
    c.update(params=dict(mode="canary"),
             description=("H021-A FIDELITY CANARY (infrastructure): the 9 Select Sector SPDRs + SPY, history "
                          "1998-12-01..2017-12-31 only; histories / launch / calendar / independent day-by-day "
                          "recomputation of every signal and response / ADJUSTED cross-check / XLF 2016 XLRE "
                          "distribution / future perturbation / truncation / placebo / planted / null determinism. "
                          "Publishes NO real IC and no other signal-response statistic."))
    write(p6h021.CANARY, c)


def null():
    for eid, (a, b) in zip(p6h021.NULL_RUNS, p6h021.NULL_BATCHES):
        c = s022()
        c.update(params=dict(mode="null", seeds=[a, b]),
                 description=(f"H021-A NULL worlds {a}-{b} of 5,000 (identity-tethered derangement of the nine "
                              "sector identities; the complete evaluation per world; H021A_spec.md section 10). "
                              "Publishes per-world null statistics only. Infrastructure (never a strategy trial)."))
        write(eid, c)


def real():
    pins = (p6h021.C, p6h021.THRESHOLD_COMMIT, p6h021.NULL_RESULT_SHA256, p6h021.PANEL_SHA256, p6h021.DIAG_SHA256)
    if any(x is None for x in pins):
        raise SystemExit("pin the threshold first")
    c = s022()
    c.update(kind="research", split="IS",
             params=dict(mode="real", threshold_c=p6h021.C, threshold_commit=p6h021.THRESHOLD_COMMIT,
                         null_result_sha256=p6h021.NULL_RESULT_SHA256, spec_sha256=p6h021.SPEC_SHA256,
                         panel_sha256=p6h021.PANEL_SHA256, diag_sha256=p6h021.DIAG_SHA256),
             description=("H021-A REAL EVALUATION, ONCE: 6-month total-return relative momentum of the 9 Select "
                          "Sector SPDRs, 215 monthly decisions 2000-01..2017-11, next-month sector-relative TSR; "
                          "gates P1-P4 with the pinned c; then the NON-GATING DIAGNOSTICS. No portfolio."))
    write(p6h021.REAL_RUN, c)


if __name__ == "__main__":
    {"canary": canary, "null": null, "real": real}[sys.argv[1]]()
