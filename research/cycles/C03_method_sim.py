"""C03 statistical-methodology simulation (owner request 2026-09-30, before any C03 result).

Simulates the WHOLE C03 decision pipeline on synthetic data to estimate, for alternative evaluation
frameworks, (a) the probability of accepting an ineffective strategy (false acceptance) and (b) the
probability of accepting a genuinely better one (power):

    IS screen (simplified) -> robustness plateau + thirds -> best passing variation per hypothesis
    -> Validation gates -> DSR (official and conservative N) -> [PBO gate or not]

Structure mirrors C03: H012 = 3 deterministic variations; H013 = 3 variations x 3 fixed seeds (a
variation passes a stage only if all 3 seeds pass; DSR/PBO use its seed-averaged series).
Fully synthetic, calibrated to IS statistics only (EW Sharpe 0.92, vol 15.5%; X962 seed correlation
0.86; frozen DSR dispersion). No Validation or Holdout data is used.

    PYTHONPATH=src python research/cycles/C03_method_sim.py   -> research/cycles/C03_method_sim.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, str(Path(__file__).parent))
from C02_pbo_simulation import pbo_fast  # noqa: E402
from qresearch import stats  # noqa: E402

T_IS, T_VAL = 2012, 1008
EW_SR, EW_VOL, C_VOL = 0.92, 0.155, 0.16
VAR_SR = 0.001001          # frozen D069 input (daily Sharpe variance across selection candidates)
N_OFFICIAL, N_CONS = 43, 90
REPS = 1000

# columns: 0 EW | 1-3 H012 v1..v3 | 4-12 H013 (v1 s1, v1 s2, v1 s3, v2 s1, ...)
H012 = [1, 2, 3]
H013 = {v: [4 + 3 * v + s for s in range(3)] for v in range(3)}


def corr_matrix():
    n = 13
    C = np.full((n, n), 0.82)
    for i in range(1, n):
        C[0, i] = C[i, 0] = 0.90
    for a in H012:
        for b in H012:
            C[a, b] = 0.95
    cols13 = [c for v in H013.values() for c in v]
    for a in cols13:
        for b in cols13:
            va, sa = divmod(a - 4, 3)
            vb, sb = divmod(b - 4, 3)
            C[a, b] = 0.95 if sa == sb else (0.86 if va == vb else 0.84)
    np.fill_diagonal(C, 1.0)
    assert np.linalg.eigvalsh(C).min() > 0
    return C


CHOL = np.linalg.cholesky(corr_matrix())


def sharpe(x):
    sd = x.std(ddof=1)
    return float(x.mean() / sd * math.sqrt(252)) if sd > 0 else 0.0


def maxdd(x):
    e = np.cumprod(1 + x)
    return float((e / np.maximum.accumulate(e) - 1).min())


def draw(rng, sr12, sr13, decay=1.0):
    """Daily returns (T_IS + T_VAL) x 13. `decay` multiplies the candidates' drift in VAL
    (1 = the same edge persists; < 1 = an IS-only edge)."""
    z = rng.standard_normal((T_IS + T_VAL, 13)) @ CHOL.T
    out = np.empty_like(z)
    out[:, 0] = EW_VOL / math.sqrt(252) * z[:, 0] + EW_SR / 252 * EW_VOL
    for j in range(1, 13):
        sr = sr12 if j in H012 else sr13
        mu = sr / 252 * C_VOL
        out[:, j] = C_VOL / math.sqrt(252) * z[:, j] + mu
        if sr > EW_SR:                      # only an above-benchmark edge can decay in VAL
            out[T_IS:, j] -= (1 - decay) * mu
    return out


def is_screen(r, ew):
    """Simplified D036 screen: Sharpe >= 0.5 and >= EW + 0.10; max DD >= -35% and >= EW DD.
    (Trade-level items are not modelled, so pass rates are OVERSTATED: conservative for false acceptance.)"""
    s, se = sharpe(r), sharpe(ew)
    return s >= 0.5 and s >= se + 0.10 and maxdd(r) >= max(-0.35, maxdd(ew))


def robust(rng, r):
    """Plateau: 8 perturbations (corr 0.9 with the base, same true drift) -> >= 7 keep Sharpe >= 70% of
    base; and every third of IS has Sharpe > 0."""
    base = sharpe(r)
    mu = r.mean()
    z = (r - mu) / r.std()
    ok = 0
    for _ in range(8):
        p = (0.9 * z + math.sqrt(1 - 0.81) * rng.standard_normal(len(r))) * r.std() + mu
        ok += sharpe(p) >= 0.7 * base
    thirds = all(sharpe(part) > 0 for part in np.array_split(r, 3))
    return ok >= 7 and thirds


def val_gates(v, ew_v, is_sr):
    s = sharpe(v)
    return s >= 0.4 and s >= 0.5 * is_sr and s > sharpe(ew_v) and maxdd(v) >= -0.35


def dsr(r, n):
    return stats.deflated_sharpe(r, n, VAR_SR)


def one(rng, sr12, sr13, decay):
    x = draw(rng, sr12, sr13, decay)
    IS, VAL = x[:T_IS], x[T_IS:]
    ew_is, ew_val = IS[:, 0], VAL[:, 0]
    # candidate series used for selection statistics (H013: seed-averaged)
    cand_is = {("H012", v): IS[:, c] for v, c in enumerate(H012)}
    cand_all = {("H012", v): x[:, c] for v, c in enumerate(H012)}
    for v, cols in H013.items():
        cand_is[("H013", v)] = IS[:, cols].mean(axis=1)
        cand_all[("H013", v)] = x[:, cols].mean(axis=1)
    # IS screen (+ H013 all seeds) and robustness (H013: all seeds)
    passed = {}
    for (h, v), r in cand_is.items():
        if h == "H012":
            ok = is_screen(r, ew_is) and robust(rng, r)
        else:
            ok = all(is_screen(IS[:, c], ew_is) for c in H013[v]) and all(robust(rng, IS[:, c]) for c in H013[v])
        passed[(h, v)] = ok
    pbo = pbo_fast(np.column_stack(list(cand_is.values())))
    res = {}
    for h in ("H012", "H013"):
        pv = [k for k in passed if k[0] == h and passed[k]]
        if not pv:
            res[h] = dict(screen=False)
            continue
        best = max(pv, key=lambda k: sharpe(cand_is[k]))            # best passing variation (pre-declared)
        v = best[1]
        if h == "H012":
            vok = val_gates(VAL[:, H012[v]], ew_val, sharpe(IS[:, H012[v]]))
        else:
            vok = all(val_gates(VAL[:, c], ew_val, sharpe(IS[:, c])) for c in H013[v])
        # DSR on each DEPLOYABLE book: H012 its own series; H013 every seed separately (all must pass).
        # The seed average is a ~45-stock book nobody would trade, so it is used only for PBO (diagnostic).
        books = [x[:, H012[v]]] if h == "H012" else [x[:, c] for c in H013[v]]
        res[h] = dict(screen=True, val=vok,
                      dsr_off=all(dsr(b, N_OFFICIAL) >= 0.90 for b in books),
                      dsr_cons=all(dsr(b, N_CONS) >= 0.90 for b in books), pbo_ok=pbo <= 0.30)
    return res


FRAMEWORKS = {
    "F0 current (D073): screen+robust+VAL+DSR(official)+PBO gate":
        lambda r: r["screen"] and r["val"] and r["dsr_off"] and r["pbo_ok"],
    "F1 proposed: screen+robust+VAL+DSR(official AND conservative), PBO diagnostic":
        lambda r: r["screen"] and r["val"] and r["dsr_off"] and r["dsr_cons"],
    "F2 screen+robust+VAL+DSR(official only), PBO diagnostic":
        lambda r: r["screen"] and r["val"] and r["dsr_off"],
    "F3 screen+robust+VAL only (no multiple-testing adjustment)":
        lambda r: r["screen"] and r["val"],
}

SCENARIOS = {  # (true annual Sharpe of H012 variations, of H013 variations, VAL persistence)
    "N0 no skill, our structure (SR 0.75 both)": (0.75, 0.75, 1.0),
    "N1 no alpha vs EW (SR 0.92 both)": (0.92, 0.92, 1.0),
    "N2 small edge EW+0.10 (SR 1.02 both)": (1.02, 1.02, 1.0),
    "N3 IS-only edge: SR 1.3 in IS, 0.92 in VAL (decay)": (1.30, 1.30, 0.92 / 1.30),
    "N4 IS-only edge in ONE hypothesis (H012 1.3 -> 0.92 in VAL; H013 no skill 0.75)": (1.30, 0.75, 0.92 / 1.30),
    "A1 real edge SR 1.3 (one hypothesis)": (1.30, 0.75, 1.0),
    "A2 real edge SR 1.3 (both)": (1.30, 1.30, 1.0),
    "A3 strong edge SR 1.6 (both)": (1.60, 1.60, 1.0),
    "A4 very strong edge SR 2.0 (one)": (2.00, 0.75, 1.0),
}


def main(reps=REPS, seed=20260930):
    rng = np.random.default_rng(seed)
    out = dict(setup=dict(reps=reps, T_IS=T_IS, T_VAL=T_VAL, ew_sr=EW_SR, var_sr=VAR_SR,
                          n_official=N_OFFICIAL, n_conservative=N_CONS,
                          note="synthetic; IS screen simplified (overstates passes); VAL gates without the trade-count and 2020 items"))
    for name, (s12, s13, dec) in SCENARIOS.items():
        rows = [one(rng, s12, s13, dec) for _ in range(reps)]
        sc = {}
        for fname, f in FRAMEWORKS.items():
            any_acc = np.mean([any(f(r[h]) for h in ("H012", "H013") if r[h].get("screen")) for r in rows])
            per_h = {h: float(np.mean([bool(r[h].get("screen")) and f(r[h]) for r in rows])) for h in ("H012", "H013")}
            sc[fname] = dict(any_accepted=float(any_acc), **per_h)
        att = {h: dict(screen=float(np.mean([bool(r[h].get("screen")) for r in rows])),
                       screen_val=float(np.mean([bool(r[h].get("screen")) and r[h]["val"] for r in rows])),
                       screen_val_dsr_off=float(np.mean([bool(r[h].get("screen")) and r[h]["val"] and r[h]["dsr_off"] for r in rows])),
                       pbo_pass_given_screen=float(np.mean([r[h]["pbo_ok"] for r in rows if r[h].get("screen")] or [np.nan])))
               for h in ("H012", "H013")}
        out[name] = dict(frameworks=sc, attrition=att)
        print(name, json.dumps(sc, indent=0))
    # DSR hurdle: annual Sharpe needed over IS+VAL for DSR >= 0.90 (normal returns)
    hurdle = {}
    for n in (N_OFFICIAL, N_CONS):
        e = stats.expected_max_sharpe(n, VAR_SR)
        hurdle[n] = dict(expected_max_annual=e * math.sqrt(252),
                         needed_observed_annual=(e + 1.2816 / math.sqrt(T_IS + T_VAL - 1)) * math.sqrt(252))
    out["dsr_hurdles"] = hurdle
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps(hurdle, indent=1))


if __name__ == "__main__":
    main()
