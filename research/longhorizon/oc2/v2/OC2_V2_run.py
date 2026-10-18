"""OC-2 synthetic calibration v2 (owner D249): the ONE confirmatory evaluation driver. LOCKED: it refuses to run
until the v2 protocol is FROZEN (its status line and SHA-256 recorded in FROZEN.json, with the owner's choice of
the identification-family treatment, protocol section 9). FINAL seeds only. Synthetic only; no real data path.

    OMP_NUM_THREADS=1 PYTHONPATH=src python research/longhorizon/oc2/v2/OC2_V2_run.py
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
sys.path[:0] = [str(ROOT / "src"), str(HERE)]
from qresearch import oc2synth_v2 as V  # noqa: E402
import OC2_V2_scenarios as S  # noqa: E402

PROTOCOL = HERE / "OC2_V2_protocol.md"
FROZEN = HERE / "FROZEN.json"            # written only by the owner-approved freeze step
OUT = HERE / "OC2_V2_results.json"
PARTS = ROOT / "data/oc2_v2_parts"       # per-replication rows (gitignored, re-creatable from FINAL seeds)
CODE = [ROOT / "src/qresearch/oc2synth_v2.py", ROOT / "src/qresearch/oc2synth.py", HERE / "OC2_V2_scenarios.py",
        Path(__file__)]

N_GATE, N_REGIME, N_DIAG, N_POW = 4000, 2000, 1000, 1000
SIZE_1, SIZE_5 = 0.020, (0.035, 0.065)
FAIL_MAX = 0.01                          # computational-failure share above which a scenario is incomplete (-> D)
IDENT_FP_MAX = 0.020                     # option 2 only: full-rule false promotion bound in the gated ident worlds
IDENT_GATED_OPT2 = ("N5a", "N2L")        # option 2: gated by full-rule false promotion (all regimes run)
POWER_TARGET, POWER_CELL = 0.80, "P3-0.09"
ADEQ = dict(pic_rel=0.15, fresh_abs=0.05, corr_abs=0.03, n_rel=0.03)
STAGE1_FRESH = (0.625, 0.097, 0.270)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def frozen_or_refuse():
    if not FROZEN.exists():
        raise SystemExit("REFUSED: the v2 protocol is not frozen (owner decision pending; protocol section 9)")
    f = json.loads(FROZEN.read_text())
    if f.get("protocol_sha256") != sha(PROTOCOL):
        raise SystemExit("REFUSED: protocol hash differs from FROZEN.json")
    for p in CODE:
        if f["code_sha256"].get(p.name) != sha(p):
            raise SystemExit(f"REFUSED: {p.name} differs from FROZEN.json")
    if f.get("ident_treatment") not in (1, 2):
        raise SystemExit("REFUSED: no owner-approved identification-family treatment")
    return f


def plan():
    """(world, reps, role) for every scenario; roles: gate / ident / diag / power."""
    out = []
    for w in S.all_nulls():
        base = w.name.split("@")[0]
        n = N_GATE if "@" not in w.name else N_REGIME
        out.append((w, n, "ident" if base in S.IDENT else "gate"))
    out.append((S.ORACLE, N_DIAG, "diag"))
    out += [(w, N_POW, "power") for w in S.POWER]
    return out


def _job(args):
    w, rep, tag = args
    return V.run_world(w, rep, tag=tag)


def wilson(k, n, z=1.959964):
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def summarise(w, rows, cv=V.CV):
    n = len(rows)
    ok = [r for r in rows if "failed" not in r]
    nf = n - len(ok)
    s = dict(n=n, failures=nf, failure_share=nf / n if n else math.nan,
             failure_reasons=sorted({r["failed"] for r in rows if "failed" in r})[:5])
    if not ok:
        return s
    t = np.array([r["t"] for r in ok])
    for a in (0.05, 0.01, 0.005, 0.001):
        k = int(np.sum(t > cv[a]))
        s[f"rej_{a}"] = k / n                       # failures counted as non-rejections (never excluded)
        s[f"rej_{a}_completed"] = k / len(ok)
        s[f"rej_{a}_ci95"] = wilson(k, n)
    for key, lab in (("t_nw4", "nw4"), ("t_iid", "iid"), ("t_rank_ctrl", "rank_ctrl")):
        tt = np.array([r[key] for r in ok if key in r])
        if len(tt):
            s[f"diag_rej_0.05_{lab}"] = float(np.mean(tt > (cv[0.05] if lab != "iid" else 1.6449)))
    slope = np.array([r["mean_slope"] for r in ok])
    se = np.array([r["se_nw7"] for r in ok])
    fr = np.array([V.full_rule(r, cv[0.01]) for r in ok])
    rho = np.array([r["rho1"] for r in ok])
    s.update(mean_t=float(t.mean()), sd_t=float(t.std()), bias_mean_slope=float(slope.mean()),
             sd_mean_slope=float(slope.std()), mean_se=float(se.mean()),
             se_ratio=float(se.mean() / slope.std()) if slope.std() > 0 else math.nan,
             tq_annual_mean=float(np.mean([r["tq_annual"] for r in ok])),
             full_rule=float(fr.sum() / n), full_rule_ci95=wilson(int(fr.sum()), n),
             pic_sd=float(np.mean([r["pic_sd"] for r in ok])), ic_sd=float(np.mean([r["ic_sd"] for r in ok])),
             rho1=float(rho.mean()), T_eff=float(np.mean(V.T * (1 - rho) / (1 + rho))),
             mean_n=float(np.mean([r["mean_n"] for r in ok])), min_n=int(min(r["min_n"] for r in ok)),
             fresh_by_phase=np.mean([r["fresh_by_phase"] for r in ok], axis=0).tolist(),
             corr=np.mean([r["corr"] for r in ok], axis=0).tolist())
    return s


def size_ok(s):
    return s.get("rej_0.01", 1) <= SIZE_1 and SIZE_5[0] <= s.get("rej_0.05", 0) <= SIZE_5[1] and \
        s.get("rej_0.01_completed", 1) <= SIZE_1 and SIZE_5[0] <= s.get("rej_0.05_completed", 0) <= SIZE_5[1]


def adequacy(res):
    """Generator adequacy (protocol 10.1): IC regime, refresh shares, cross-section, signal-control correlations."""
    from qresearch import oc2synth as O
    miss = {}
    for nm, s in res.items():
        base, _, reg = nm.partition("@")
        if base not in ("N0", "N4") or "pic_sd" not in s:
            continue
        target = float(reg) if reg else S.CENTRAL
        if abs(s["pic_sd"] / target - 1) > ADEQ["pic_rel"]:
            miss[f"{nm}:pic_sd"] = s["pic_sd"]
        if max(abs(a - b) for a, b in zip(s["fresh_by_phase"], STAGE1_FRESH)) > ADEQ["fresh_abs"]:
            miss[f"{nm}:fresh"] = s["fresh_by_phase"]
        n_target = float(np.mean(O.n_by_month())) * (1 - 0.05)
        if abs(s["mean_n"] / n_target - 1) > ADEQ["n_rel"]:
            miss[f"{nm}:mean_n"] = s["mean_n"]
        if nm == "N4" and max(abs(c - O.RHO_F5[k]) for c, k in zip(s["corr"], O.CONTROLS)) > ADEQ["corr_abs"]:
            miss[f"{nm}:corr"] = s["corr"]
    return miss


def decide(res, roles, ident_treatment):
    incomplete = sorted(n for n, s in res.items() if s["failure_share"] > FAIL_MAX or "rej_0.05" not in s)
    miss = adequacy(res)
    gate_fail = sorted(n for n, s in res.items() if roles[n] == "gate" and not size_ok(s))
    if ident_treatment == 1:                       # strict: N5a (all regimes) under the size gates
        ident_fail = sorted(n for n, s in res.items() if n.split("@")[0] == "N5a" and not size_ok(s))
    else:                                          # option 2: bounded full-rule false promotion
        ident_fail = sorted(n for n, s in res.items() if n.split("@")[0] in IDENT_GATED_OPT2
                            and s.get("full_rule", 1) > IDENT_FP_MAX)
    p3 = res.get(POWER_CELL, {}).get("rej_0.01", 0.0)
    outcome = V.classify(not incomplete, not miss, not gate_fail, not ident_fail, p3, POWER_TARGET)
    return dict(outcome=outcome, incomplete=incomplete, adequacy_misses=miss, size_failures=gate_fail,
                ident_failures=ident_fail, power_3pct_central=p3)


def main():
    f = frozen_or_refuse()
    PARTS.mkdir(parents=True, exist_ok=True)
    res, roles = {}, {}
    t0 = time.time()
    with Pool(os.cpu_count()) as pool:
        for w, n, role in plan():
            fp = PARTS / f"{w.name}.json"
            rows = None
            if fp.exists():
                d = json.loads(fp.read_text())
                rows = d["rows"] if d["n"] == n else None
            if rows is None:
                t1 = time.time()
                rows = pool.map(_job, [(w, r, "FINAL") for r in range(n)], chunksize=20)
                fp.write_text(json.dumps(dict(n=n, world=w.__dict__, seconds=round(time.time() - t1, 1),
                                              rows=rows)))
            res[w.name] = summarise(w, rows)
            roles[w.name] = role
            print(w.name, role, round(time.time() - t0), flush=True)
    out = dict(kind="OC-2 synthetic calibration v2 — confirmatory evaluation (synthetic only)", decision="D249",
               protocol_sha256=sha(PROTOCOL), code_sha256={p.name: sha(p) for p in CODE},
               ident_treatment=f["ident_treatment"], roles=roles, scenarios=res, cv=V.CV,
               decision_record=decide(res, roles, f["ident_treatment"]), seconds=round(time.time() - t0))
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps(out["decision_record"], indent=1, default=float))


if __name__ == "__main__":
    main()
