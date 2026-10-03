"""E983-01 (X983) event-level diagnostic analysis (research/phase2/H017_spec.md §8): PREPARED 2026-10-03, before any
H017 run. Reads only the aggregated lines of a completed E983-01 run (A|month|group|class|tercile|n|sum|sumsq and
M|key|n|mean|median|p25|p75) and reports the pre-declared tables plus PbNQ rule 7 (qresearch.p2h017.event_rule).
Diagnostic only: never a gate, never a design input.

    PYTHONPATH=src python research/phase2/h017/E983_analyse.py  -> research/phase2/h017/E983_results.json
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research/phase2/sec"))
from qresearch import p2h017 as H  # noqa: E402

OUT = Path(__file__).with_name("E983_results.json")


def parse(lines):
    agg, med, summary = [], {}, None
    for ln in lines:
        p = ln.split("|")
        if p[0] == "A":
            agg.append(dict(month=p[1], group=p[2], cls=p[3], ter=int(p[4]), n=int(p[5]), s=float(p[6]),
                            ss=float(p[7])))
        elif p[0] == "M":
            med[p[1]] = dict(n=int(p[2]), mean=float(p[3]), median=float(p[4]), p25=float(p[5]), p75=float(p[6]))
        elif ln.startswith("QRX983|summary|"):
            summary = json.loads(ln.split("|", 2)[2])
    return agg, med, summary


def group_stats(rows):
    n_m, s_m = defaultdict(int), defaultdict(float)
    n = ss = 0.0
    for r in rows:
        n_m[r["month"]] += r["n"]
        s_m[r["month"]] += r["s"]
        n += r["n"]
        ss += r["ss"]
    c = H.clustered_from_sums(n_m, s_m)
    if n > 1:
        mu = sum(s_m.values()) / n
        c["sd"] = math.sqrt(max(ss / n - mu * mu, 0.0) * n / (n - 1))
    return c


def analyse(lines):
    agg, med, summary = parse(lines)
    out = dict(summary=summary, groups={}, blocks={}, by_class={}, by_volume_tercile={})
    for g in ("top", "mid", "bottom", "d10_nonpos"):
        rows = [r for r in agg if r["group"] == g]
        out["groups"][g] = dict(group_stats(rows), **{f"q_{k}": v for k, v in med.get(g, {}).items()})
        for y in range(2010, 2022, 2):
            b = f"{y}-{y + 1}"
            rb = [r for r in rows if b[:4] <= r["month"][:4] <= b[5:]]
            out["blocks"].setdefault(g, {})[b] = dict(group_stats(rb), **{f"q_{k}": v for k, v in
                                                                          med.get(f"{g}/block/{b}", {}).items()})
        for c in ("BMO", "DURING", "AMC", "other"):
            out["by_class"].setdefault(g, {})[c] = dict(group_stats([r for r in rows if r["cls"] == c]),
                                                        **{f"q_{k}": v for k, v in med.get(f"{g}/class/{c}", {}).items()})
        for t in (1, 2, 3, 0):
            out["by_volume_tercile"].setdefault(g, {})[str(t)] = dict(
                group_stats([r for r in rows if r["ter"] == t]),
                **{f"q_{k}": v for k, v in med.get(f"{g}/av/{t}", {}).items()})
    out["pbnq_rule_7"] = H.event_rule(out["groups"]["top"], out["groups"]["mid"])
    return out


def main():
    res = ROOT / "experiments" / H.EVENT_DIAG / "result.json"
    if not res.exists() or not str(json.loads(res.read_text()).get("status", "")).startswith("completed"):
        raise SystemExit(f"{H.EVENT_DIAG} has not run (it needs its separate owner approval); nothing to analyse")
    from e970_parse import lines
    out = analyse(lines(H.EVENT_DIAG))
    OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(out["pbnq_rule_7"], default=float))


if __name__ == "__main__":
    main()
