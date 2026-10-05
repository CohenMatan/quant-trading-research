"""Writes the H020 run configs from the canary config E987-01 (research/phase5/H020_spec_addendum_1.md A4).

  python research/phase5/H020_make_configs.py null   -> experiments/E021-01..05/config.json (null batches)
  python research/phase5/H020_make_configs.py real   -> experiments/E021-06/config.json (needs the pinned thresholds)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from qresearch import p5h020  # noqa: E402

APPROVAL = "H020 real structured chart score validation (owner authorisation 2026-10-05, D154)"


def base():
    c = json.loads((ROOT / "experiments/E987-01/config.json").read_text())
    c.update(strategy_id="S021", strategy_dir="strategies/S021_h020_chart", hypothesis_id="H020", programme="P5",
             cycle="P5H020", owner_approval_required=APPROVAL)
    return c


def write(eid, c):
    d = ROOT / "experiments" / eid
    d.mkdir(exist_ok=True)
    c["experiment_id"] = eid
    (d / "config.json").write_text(json.dumps(c, indent=1) + "\n")
    print("wrote", eid)


def null():
    for i, (a, b) in enumerate(p5h020.NULL_BATCHES):
        c = base()
        c.update(kind="infrastructure", split="AUDIT", params=dict(mode="null", seeds=[a, b]),
                 description=(f"H020 NULL worlds {a}-{b} of 5,000 (unstratified identity-tethered within-date "
                              "permutation of the chart side, no self-matches; the complete procedure per world; "
                              "H020_spec.md section 18). Publishes per-world null statistics only. Infrastructure "
                              "(never a strategy trial)."))
        write(f"E021-{i + 1:02d}", c)


def real():
    pins = (p5h020.C_IC, p5h020.C_INC, p5h020.THRESHOLD_COMMIT, p5h020.NULL_RESULT_SHA256, p5h020.CHART_PANEL_SHA256)
    if any(x is None for x in pins):
        raise SystemExit("pin the thresholds first")
    c = base()
    c.update(kind="research", split="IS",
             params=dict(mode="real", c_ic=p5h020.C_IC, c_inc=p5h020.C_INC, threshold_commit=p5h020.THRESHOLD_COMMIT,
                         null_result_sha256=p5h020.NULL_RESULT_SHA256, spec_sha256=p5h020.SPEC_SHA256,
                         addendum_sha256=p5h020.ADDENDUM_SHA256, chart_panel_sha256=p5h020.CHART_PANEL_SHA256),
             description=("H020 REAL EVALUATION, ONCE: the frozen structured chart score on the 2010-2017 weekly "
                          "decisions (4-week total-shareholder-return responses), judged with the pinned c_ic / c_inc "
                          "(gates G1-G5); then the descriptives, the NON-GATING SECTOR DIAGNOSTIC and the NON-GATING "
                          "13-week diagnostic. No portfolio."))
    write("E021-06", c)


if __name__ == "__main__":
    {"null": null, "real": real}[sys.argv[1]]()
