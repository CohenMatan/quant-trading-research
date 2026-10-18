"""OC-2 Stage 2 (owner D248): SYNTHETIC-ONLY calibration of the universe-wide Fama-MacBeth signal test.

Implements `OC2_S2_protocol.md` (frozen and committed, with this script's and `qresearch/oc2synth.py`'s SHA-256,
before any synthetic result). No real signal, return or market data is used; no QuantConnect run.

    PYTHONPATH=src python research/longhorizon/oc2/stage2/OC2_S2_run.py
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
sys.path[:0] = [str(ROOT / "src")]
from qresearch import oc2synth as O  # noqa: E402

PROTOCOL = HERE / "OC2_S2_protocol.md"
OUT = HERE / "OC2_S2_results.json"
PARTS = ROOT / "data/oc2_stage2_parts"           # per-replication synthetic rows (not committed; reproducible)
N_GATE, N_DIAG, N_POW = 4000, 1000, 1000
ALPHAS = (0.05, 0.01, 0.005, 0.001)
SIZE_1, SIZE_5 = 0.020, (0.035, 0.065)
POWER_TARGET, POWER_EFFECT = 0.80, 0.03
EFFECTS = (0.01, 0.02, 0.03, 0.04, 0.05, 0.06)
STAGE1_FRESH = (0.625, 0.097, 0.270)           # OC2_S1_audit stage2 refresh shares by month type (A, B, C)

N4 = O.World("N4", priced=O.CONTROLS)
GATING = [O.World("N0i", iid=True), O.World("N0"), O.World("N1", priced=("lowvol",)),
          O.World("N2", priced=("ag",)), O.World("N3", priced=("gpa",)), N4,
          replace(N4, name="N6", tv_premia=True), replace(N4, name="N7", sigma_sector=0.05, sigma_factor=0.02),
          replace(N4, name="N8a", churn=0.0), replace(N4, name="N8b", churn=2.0),
          replace(N4, name="N9", signal_ar=0.90, own_tv_premium=True), replace(N4, name="N11", mnar=True),
          replace(N4, name="N12", tails=3.0, hetero=0.60), replace(N4, name="N5a", reliability=0.80)]
DIAG = [replace(N4, name="N5b", reliability=0.60), replace(N4, name="N2L", latent_growth_priced=True),
        replace(N4, name="N13", horizon=3, churn=0.0)]
PESS = replace(N4, sigma_sector=0.05, sigma_factor=0.02, tails=3.0, hetero=0.60)
POWER = ([replace(N4, name=f"PM{int(e * 100)}", planted=e) for e in EFFECTS] +
         [replace(PESS, name=f"PP{int(e * 100)}", planted=e) for e in EFFECTS[1:]] +
         [replace(N4, name="PC0", planted=0.03, corr_scale=0.0), replace(N4, name="PC2", planted=0.03, corr_scale=2.0),
          replace(N4, name="PF3", planted=0.03, fresh_only=True), replace(N4, name="PF5", planted=0.05, fresh_only=True)])


def _job(args):
    w, rep = args
    return O.run_world(w, rep, boot=True)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_scenario(pool, w, n):
    PARTS.mkdir(parents=True, exist_ok=True)
    fp = PARTS / f"{w.name}.json"
    if fp.exists():
        d = json.loads(fp.read_text())
        if d["n"] == n:
            return d["rows"]
    t0 = time.time()
    rows = pool.map(_job, [(w, r) for r in range(n)], chunksize=20)
    fp.write_text(json.dumps(dict(n=n, world=w.__dict__, seconds=round(time.time() - t0, 1), rows=rows)))
    return rows


def summarise(w, rows):
    df = O.T - 1
    t = np.array([r["t_nw3"] for r in rows])
    p = student_t.sf(t, df)
    out = dict(n=len(rows))
    for a in ALPHAS:
        c = O.crit(a)
        out[f"rej_{a}"] = round(float(np.mean(t > c)), 4)
        out[f"rej_iid_{a}"] = round(float(np.mean(np.array([r["t_iid"] for r in rows]) > c)), 4)
        out[f"rej_nw6_{a}"] = round(float(np.mean(np.array([r["t_nw6"] for r in rows]) > c)), 4)
        out[f"rej_boot_{a}"] = round(float(np.mean(np.array([r["p_boot"] for r in rows]) <= a)), 4)
    out["se_rej_0.01"] = round(math.sqrt(0.01 * 0.99 / len(rows)), 4)
    ps = np.sort(p)
    u = np.arange(1, len(ps) + 1) / len(ps)
    out["ks_D"] = round(float(np.max(np.abs(ps - u))), 4)
    out["mean_t"] = round(float(t.mean()), 3)
    out["sd_t"] = round(float(t.std()), 3)
    out["tq_annual_mean"] = round(float(np.mean([r["tq_annual"] for r in rows])), 5)
    out["full_rule_pass"] = round(float(np.mean([O.full_rule(r, O.crit(0.01)) for r in rows])), 4)
    rho = float(np.mean([r["rho1"] for r in rows]))
    out["slope_rho1"] = round(rho, 3)
    out["T_eff_ar1"] = round(O.T * (1 - rho) / (1 + rho), 1)
    out["realised"] = dict(mean_n=round(float(np.mean([r["mean_n"] for r in rows])), 1),
                           fresh_by_phase=[round(float(np.mean([r["fresh_by_phase"][k] for r in rows])), 3)
                                           for k in range(3)],
                           ret_sd=round(float(np.mean([r["ret_sd"] for r in rows])), 4),
                           corr={c: round(float(np.mean([r["corr"][j] for r in rows])), 3)
                                 for j, c in enumerate(O.CONTROLS)})
    return out


def adequacy(s, w):
    """Protocol 6.1 framework checks on a realised world (D triggers)."""
    r = s["realised"]
    tgt_n = float(np.mean(O.n_by_month()))
    issues = []
    if abs(r["mean_n"] - tgt_n) / tgt_n > 0.05:
        issues.append("cross-section size")
    if not w.iid and any(abs(r["fresh_by_phase"][k] - (STAGE1_FRESH[k] + 0.03)) > 0.07 for k in range(3)):
        issues.append("refresh structure")
    if not 0.055 <= r["ret_sd"] <= 0.075:
        issues.append("cross-sectional return sd")
    if not w.iid:
        for c in O.CONTROLS:
            if abs(r["corr"][c] - O.RHO_F5[c] * w.corr_scale) > 0.05:
                issues.append(f"signal-control correlation {c}")
    return issues


def interp_mde(effects, power, level):
    pts = [(0.0, None)] + list(zip(effects, power))
    for (e0, p0), (e1, p1) in zip(pts[1:], pts[2:]):
        if p0 < level <= p1:
            return round(e0 + (e1 - e0) * (level - p0) / (p1 - p0), 4)
    if pts[1][1] >= level:
        return f"<= {pts[1][0]}"
    return f"> {effects[-1]}"


def verify_frozen():
    """Immutability (protocol 9): the module and this script must carry the SHA-256 values written in the
    committed protocol."""
    import re
    txt = PROTOCOL.read_text()
    want = dict(re.findall(r"`(oc2synth\.py|OC2_S2_run\.py)` SHA-256: `([0-9a-f]{64})`", txt))
    have = {"oc2synth.py": sha(ROOT / "src/qresearch/oc2synth.py"), "OC2_S2_run.py": sha(__file__)}
    assert want == have, f"frozen code mismatch: {want} vs {have}"


def main():
    verify_frozen()
    t0 = time.time()
    with Pool(4) as pool:
        res = {}
        for w in GATING:
            res[w.name] = summarise(w, run_scenario(pool, w, N_GATE))
            print(w.name, res[w.name]["rej_0.01"], res[w.name]["rej_0.05"], flush=True)
        for w in DIAG:
            res[w.name] = summarise(w, run_scenario(pool, w, N_DIAG))
            print(w.name, res[w.name]["rej_0.01"], flush=True)
        for w in POWER:
            res[w.name] = summarise(w, run_scenario(pool, w, N_POW))
            print(w.name, res[w.name]["rej_0.01"], flush=True)
    worlds = {w.name: w for w in GATING + DIAG + POWER}
    # ---- size gates (protocol 6.2)
    size = {}
    for w in GATING:
        s = res[w.name]
        ok = s["rej_0.01"] <= SIZE_1 and SIZE_5[0] <= s["rej_0.05"] <= SIZE_5[1]
        size[w.name] = dict(rej_1=s["rej_0.01"], rej_5=s["rej_0.05"], ok=ok,
                            family="identification" if w.name == "N5a" else "standard-error")
    # ---- adequacy (protocol 6.1)
    adq = {n: adequacy(res[n], worlds[n]) for n in ("N0", "N4", "PM3", "N11")}
    # ---- power (protocol 6.3)
    pm = [res[f"PM{int(e * 100)}"] for e in EFFECTS]
    pp = [res[f"PP{int(e * 100)}"] for e in EFFECTS[1:]]
    power = dict(
        main={f"{e:.0%}": {f"alpha_{a}": r[f"rej_{a}"] for a in ALPHAS} | dict(full_rule=r["full_rule_pass"],
                                                                    tq_annual_mean=r["tq_annual_mean"])
              for e, r in zip(EFFECTS, pm)},
        pessimistic={f"{e:.0%}": {f"alpha_{a}": r[f"rej_{a}"] for a in ALPHAS} | dict(full_rule=r["full_rule_pass"],
                                                                           tq_annual_mean=r["tq_annual_mean"])
                     for e, r in zip(EFFECTS[1:], pp)},
        mde_main={f"{int(l * 100)}%": interp_mde(EFFECTS, [r["rej_0.01"] for r in pm], l) for l in (0.5, 0.8)},
        mde_pessimistic={f"{int(l * 100)}%": interp_mde(EFFECTS[1:], [r["rej_0.01"] for r in pp], l)
                         for l in (0.5, 0.8)},
        mde_main_full_rule={f"{int(l * 100)}%": interp_mde(EFFECTS, [r["full_rule_pass"] for r in pm], l)
                            for l in (0.5, 0.8)},
        sensitivity_3pct=dict(corr_x0=res["PC0"]["rej_0.01"], corr_x1=res["PM3"]["rej_0.01"],
                              corr_x2=res["PC2"]["rej_0.01"], fresh_only=res["PF3"]["rej_0.01"],
                              fresh_only_5pct=res["PF5"]["rej_0.01"]))
    p3 = res["PM3"]["rej_0.01"]
    failed_size = [n for n, v in size.items() if not v["ok"]]
    inadequate = {n: v for n, v in adq.items() if v}
    if inadequate:
        outcome = "D — INSUFFICIENT EVIDENCE"
    elif failed_size:
        outcome = "C — METHOD NOT VALIDATED"
    elif p3 >= POWER_TARGET:
        outcome = "A — METHOD VALIDATED WITH USEFUL POWER"
    else:
        outcome = "B — METHOD CALIBRATED BUT UNDERPOWERED"
    out = dict(kind="OC-2 Stage 2 synthetic calibration (synthetic data only)", decision="D248",
               protocol_sha256=sha(PROTOCOL), module_sha256=sha(ROOT / "src/qresearch/oc2synth.py"),
               script_sha256=sha(__file__), replications=dict(gating=N_GATE, diagnostic=N_DIAG, power=N_POW),
               scenarios=res, size_gates=size, adequacy=adq, power=power, failed_size=failed_size,
               outcome=outcome, wall_seconds=round(time.time() - t0, 1),
               worlds={n: w.__dict__ for n, w in worlds.items()})
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(outcome)


if __name__ == "__main__":
    main()
