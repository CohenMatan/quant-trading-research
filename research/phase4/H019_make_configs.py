"""Writes the H019 run configs from the canary config E985-01 (research/phase4/P4_xs_spec.md section 10).

  python research/phase4/H019_make_configs.py null   -> experiments/E020-01..05/config.json (null batches)
  python research/phase4/H019_make_configs.py real   -> experiments/E020-06/config.json (needs the pinned threshold)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p4xs  # noqa: E402

APPROVAL = "H019 final cross-sectional signal validation (owner authorisation 2026-10-04, D145)"


def base():
    c = json.loads((ROOT / "experiments/E985-01/config.json").read_text())
    c.update(strategy_id="S020", strategy_dir="strategies/S020_h019_xs", hypothesis_id="H019", programme="P4",
             cycle="P4H019", owner_approval_required=APPROVAL)
    return c


def write(eid, c):
    d = ROOT / "experiments" / eid
    d.mkdir(exist_ok=True)
    c["experiment_id"] = eid
    (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
    print("wrote", eid)


def null():
    for i, (a, b) in enumerate(p4xs.NULL_BATCHES):
        c = base()
        c.update(kind="infrastructure", split="AUDIT", params=dict(mode="null", seeds=[a, b]),
                 description=(f"H019 NULL worlds {a}-{b} of 5,000 (stratified identity-tethered within-date permutation, "
                              "full re-estimation per world; P4_xs_spec.md v2 section 6). Publishes per-world null "
                              "statistics only. Infrastructure (never a strategy trial)."))
        write(f"E020-{i + 1:02d}", c)


def real():
    if p4xs.THRESHOLD_C is None or p4xs.THRESHOLD_COMMIT is None:
        raise SystemExit("pin the threshold first")
    c = base()
    c.update(kind="research", split="IS",
             params=dict(mode="real", threshold_c=p4xs.THRESHOLD_C, threshold_commit=p4xs.THRESHOLD_COMMIT,
                         null_result_sha256=p4xs.NULL_RESULT_SHA256, spec_sha256=p4xs.SPEC_SHA256),
             description=("H019 REAL EVALUATION, ONCE: S1 / S2 / S3 on the frozen 2011-01 .. 2017-11 window (83 monthly "
                          "decisions), judged with the pinned family threshold c; then the section-8 diagnostics and the "
                          "NON-GATING 3-month diagnostic. No portfolio."))
    write("E020-06", c)


if __name__ == "__main__":
    {"null": null, "real": real}[sys.argv[1]]()
