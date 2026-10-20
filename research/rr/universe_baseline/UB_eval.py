"""UB-1 offline evaluation (owner D263; UB_protocol.md §4–§6, frozen and SHA-256-pinned in qresearch.rr_ub before any
run). Reads the X804 aggregate lines ('UB|<section>|<json>') from an experiment's messages.txt and applies the
pre-registered gates. Pure function of the exported aggregates; no QuantConnect call.

    python research/rr/universe_baseline/UB_eval.py experiments/E804-01/messages.txt [out.json]
"""
from __future__ import annotations

import json
import sys

GAP_MAX = 0.03
BIAS_MAX = {24: 0.005, 12: 0.0025}
V1A, V1B = 0.95, 0.99
V2A_RESTATED, V2A_RAW, V2A_MIN = 0.90, 0.05, 30
V2B, V3_LEAD, V3_SAME, V3_MIN = 0.95, 0.10, 0.70, 100
PRE_PLAUS, PRE_DEAD = 0.50, 0.10
WINDOWS = {"W0": (1999, 2009), "W1": (2010, 2021)}


def parse(lines) -> dict:
    res = dict(years={})
    for ln in lines:
        ln = ln.strip()
        if not ln.startswith("UB|"):
            continue
        parts = ln.split("|", 3)
        if parts[1] == "year":
            res["years"][parts[2]] = json.loads(parts[3])
        else:
            res[parts[1]] = json.loads(ln.split("|", 2)[2])
    return res


def _validity(v: dict, w: str, years: list[str]) -> dict:
    out = {}
    v1 = [v["V1"].get(y, {}) for y in years]
    v1_ok = [x for x in v1 if x.get("n")]
    out["V1a"] = bool(v1_ok) and all(x["within_2pct"] >= V1A for x in v1_ok) and len(v1_ok) == len(years)
    out["V1b"] = bool(v1_ok) and all(x["threshold_agree"] >= V1B for x in v1_ok) and len(v1_ok) == len(years)
    s2 = v["V2"][w]
    if s2["events"] < V2A_MIN:
        out["V2a"] = out["V2b"] = "INSUFFICIENT"
    else:
        out["V2a"] = s2["restated"] / s2["events"] >= V2A_RESTATED and s2["raw_like"] / s2["events"] <= V2A_RAW
        out["V2b"] = "INSUFFICIENT" if s2["r_events"] < V2A_MIN else s2["r_continuous"] / s2["r_events"] >= V2B
    s3 = v["V3"][w]
    if s3["events"] < V3_MIN:
        out["V3"] = "INSUFFICIENT"
    else:
        out["V3"] = s3["lead"] / s3["events"] <= V3_LEAD and s3["same"] / s3["events"] >= V3_SAME
    s4 = v["V4"][w]
    se, sr = s4["stale_E"], s4["stale_R2B"]
    stale_ok = sr is None or (se is not None and sr <= max(2 * se, se + 0.10))
    fa, fm = s4["flat_A"], s4["flat_M"]
    fa_s = fa[1] / fa[0] if fa[0] else 0.0
    flat_ok = fm[0] == 0 or fm[1] / fm[0] <= 2 * fa_s + 0.05
    out["V4"] = bool(stale_ok and flat_ok)
    tests = [out[t] for t in ("V1a", "V1b", "V2a", "V2b", "V3", "V4")]
    out["insufficient"] = any(t == "INSUFFICIENT" for t in tests)
    out["valid"] = all(t is True for t in tests)
    return out


def _view(res: dict, years: list[str], view: str) -> dict:
    gap_key = "gap_" + view
    rows, cov_ok, surv_ok, surv_point_ok, fail_hard, unassessable = {}, True, True, True, False, []
    for y in years:
        r = res["years"][y]
        g = r[gap_key]
        sv = r["survivorship"]
        h = sv.get("horizon")
        row = dict(gap=g, horizon=h)
        if g is None or g > GAP_MAX:
            cov_ok = False
            fail_hard = fail_hard or (g is not None and g > GAP_MAX)
        if h is None:
            unassessable.append(y)
        else:
            b = sv["bias_" + view]
            thr = BIAS_MAX[h]
            row.update(bias=b["point"], bias_ci=b["ci_b"], d=b["d"], d_ci=b["ci_d"], threshold=thr)
            up = b["ci_b"][1]
            if b["point"] is not None and b["point"] > thr:
                surv_point_ok = False
                fail_hard = True
            if up is None or up > thr:
                surv_ok = False
        rows[y] = row
    return dict(years=rows, coverage=cov_ok, survivorship=surv_ok and surv_point_ok,
                survivorship_point=surv_point_ok, hard_fail=fail_hard, unassessable_years=unassessable)


def _pre(res: dict, view: str) -> dict:
    ys = {y: r for y, r in res["years"].items()}
    key = "monthly_E" if view == "A" else "monthly_E_R2B"
    base = [ys[y][key][1] for y in ("2010", "2011", "2012") if y in ys]
    ref = sum(base) / len(base) if base else None
    ratios = {y: (ys[y][key][1] / ref if ref else None) for y in sorted(ys) if "1999" <= y <= "2009"}
    plaus = bool(ratios) and all(r is not None and r >= PRE_PLAUS for r in ratios.values())
    dead = res["pre2010"][view]
    dead_ok = dead["share"] is not None and dead["share"] >= PRE_DEAD
    return dict(ratios={y: (None if r is None else round(r, 4)) for y, r in ratios.items()}, reference=ref,
                plausible=plaus, dead=dead, dead_ok=dead_ok, passed=plaus and dead_ok)


def evaluate(res: dict) -> dict:
    out = dict(protocol="UB-1", windows={})
    for w, (y0, y1) in WINDOWS.items():
        years = [y for y in sorted(res["years"]) if y0 <= int(y) <= y1]
        val = _validity(res["validity"], w, years)
        vA, vB = _view(res, years, "A"), _view(res, years, "B")
        pre = {v: _pre(res, v) for v in ("A", "B")} if w == "W0" else None
        preA = pre is None or pre["A"]["passed"]
        preB = pre is None or pre["B"]["passed"]
        if vA["coverage"] and vA["survivorship"] and preA:
            outcome = "PASS-A"
        elif val["valid"] and vB["coverage"] and vB["survivorship"] and preB:
            outcome = "PASS-B"
        else:
            best, pre_ok = (vB, preB) if val["valid"] else (vA, preA)
            if best["hard_fail"] or not pre_ok:
                outcome = "FAIL"
            else:
                outcome = "AMBIGUOUS"
        note = None
        if outcome == "PASS-B":
            note = ("formula-consistent and internally PIT-consistent; independent PIT validity not established "
                    "(no external source in-run)")
        out["windows"][w] = dict(outcome=outcome, note=note, ub_validity=val, view_A=vA, view_B=vB, pre2010=pre)
    return out


def main(argv):
    res = parse(open(argv[1]).read().splitlines())
    ev = evaluate(res)
    txt = json.dumps(ev, indent=1, sort_keys=True)
    if len(argv) > 2:
        open(argv[2], "w").write(txt + "\n")
    print(json.dumps({w: v["outcome"] for w, v in ev["windows"].items()}))


if __name__ == "__main__":
    main(sys.argv)
