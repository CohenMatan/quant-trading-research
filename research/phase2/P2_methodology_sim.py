"""Phase 2 evaluation-philosophy simulation (owner request "Revise Evaluation Philosophy", 2026-09-30).

How often does the proposed pipeline - development screen on 2010-2021, then ONE frozen candidate to the
2022-2026 Holdout - accept a strategy with NO real edge, and how often does it accept a real one?

Model (transparent, normal approximation):
  * Each hypothesis has 2 candidates (H014 has 2 exit variants). A candidate's observed Sharpe difference
    vs the equal-weight benchmark over a period of Y years is  dSR_obs = delta + e,
    e ~ N(0, se(Y)), se(Y) = sqrt(2 (1 - rho) / Y)  (Jobson-Korkie / Memmel, equal volatility).
    The two candidates of one hypothesis have correlated errors (0.8).
  * rho (strategy vs EW daily-return correlation) is calibrated on committed pre-Phase-2 IS books:
    selective programme-1 strategies had rho 0.72-0.80 (H002, H005, H006, H008, H009); we use 0.76.
  * Development: Y = 12 (2010-2021). Holdout: Y = 4.67 (2022-01-01 .. 2026-08-31). Holdout errors are
    independent of development errors.
  * Research process: K hypotheses are screened on development data; those whose best candidate clears
    the development margin m_dev are eligible; the best eligible candidate (highest development dSR) is
    frozen and goes to the Holdout (the Holdout is used once). It is accepted if its holdout dSR >= m_hold.
  * Other development gates (robustness, controls, consistency, costs) are not modelled: they filter
    some noise, so these false-acceptance figures are UPPER bounds.
Also: a forward paper-trading stage of F years (F = 2) with gate dSR_fwd >= 0.

    PYTHONPATH=src python research/phase2/P2_methodology_sim.py -> research/phase2/P2_methodology_sim.json
No market data is used beyond the rho calibration quoted above (computed from committed IS results).
"""
import json
import math
from pathlib import Path

import numpy as np

RHO, DEV_Y, HOLD_Y, FWD_Y = 0.76, 12.0, 4.67, 2.0
REPS = 200_000
SEED = 20261002


def se(years, rho=RHO):
    return math.sqrt(2 * (1 - rho) / years)


def pipeline(rng, k, deltas, m_dev, m_hold, fwd=False, reps=REPS):
    """m_dev may be a list (one margin per hypothesis, in screening order)."""
    m_dev = np.broadcast_to(np.asarray(m_dev, float), (k,))
    return _pipeline(rng, k, deltas, m_dev, m_hold, fwd, reps)


def _pipeline(rng, k, deltas, m_dev, m_hold, fwd, reps):
    """deltas: true dSR of each of the k hypotheses (both candidates share it). Returns acceptance stats."""
    deltas = np.asarray(deltas, float)
    z = rng.standard_normal((reps, k, 2))
    z[:, :, 1] = 0.8 * z[:, :, 0] + 0.6 * z[:, :, 1]                     # correlated candidates
    dev = deltas[None, :, None] + se(DEV_Y) * z
    best_per_h = dev.max(axis=2)                                         # each hypothesis' best candidate
    eligible = best_per_h >= m_dev[None, :]
    masked = np.where(eligible, best_per_h, -np.inf)
    pick = masked.argmax(axis=1)
    any_elig = eligible.any(axis=1)
    true_pick = deltas[pick]
    hold = true_pick + se(HOLD_Y) * rng.standard_normal(reps)
    acc = any_elig & (hold >= m_hold)
    if fwd:
        acc &= true_pick + se(FWD_Y) * rng.standard_normal(reps) >= 0
    return dict(p_reach_holdout=float(any_elig.mean()), p_accept=float(acc.mean()),
                p_accept_real=float((acc & (true_pick > 0)).mean()),
                p_accept_null=float((acc & (true_pick <= 0)).mean()))


def main():
    rng = np.random.default_rng(SEED)
    out = dict(assumptions=dict(rho=RHO, dev_years=DEV_Y, holdout_years=HOLD_Y, forward_years=FWD_Y,
                                se_dev=se(DEV_Y), se_holdout=se(HOLD_Y), se_forward=se(FWD_Y), reps=REPS, seed=SEED,
                                note="other development gates not modelled: false acceptance figures are upper bounds"))
    # 1. single hypothesis, no edge vs a real edge: effect of the development margin and the holdout gate
    tab = {}
    for m_dev in (0.0, 0.10, 0.20, 0.30):
        for m_hold in (0.0, 0.10, 0.20):
            row = {}
            for d in (0.0, 0.2, 0.3, 0.5):
                row[f"delta={d}"] = pipeline(rng, 1, [d], m_dev, m_hold)["p_accept"]
            tab[f"m_dev={m_dev},m_hold={m_hold}"] = row
    out["single_hypothesis"] = tab
    # 2. research over K hypotheses, all without edge: false acceptance of the programme
    fa = {}
    for k in (1, 3, 5, 10, 20):
        fa[f"K={k}"] = {f"m_dev={m},m_hold={h}": pipeline(rng, k, [0.0] * k, m, h)["p_accept"]
                        for m, h in ((0.20, 0.0), (0.20, 0.10), (0.30, 0.10), (0.40, 0.10))}
        fa[f"K={k}"]["m_dev=0.20,m_hold=0.10,+2y forward"] = pipeline(rng, k, [0.0] * k, 0.20, 0.10, fwd=True)["p_accept"]
    out["programme_false_acceptance_all_null"] = fa
    # 3. one real edge among K hypotheses
    pw = {}
    for d in (0.2, 0.3, 0.5):
        for k in (1, 5, 10):
            r = pipeline(rng, k, [d] + [0.0] * (k - 1), 0.20, 0.10)
            pw[f"delta={d},K={k}"] = dict(accept_real=r["p_accept_real"], accept_null_instead=r["p_accept_null"])
    out["one_real_edge_among_K"] = pw
    # 4. proposed safeguard: at most 3 hypotheses per Holdout, development margin rising 0.20 / 0.30 / 0.40
    sched = {}
    for k in (1, 2, 3):
        m = [0.20, 0.30, 0.40][:k]
        sched[f"K={k} (margins {m})"] = dict(
            all_null=pipeline(rng, k, [0.0] * k, m, 0.10)["p_accept"],
            all_null_plus_2y_forward=pipeline(rng, k, [0.0] * k, m, 0.10, fwd=True)["p_accept"],
            real_0_3_first=pipeline(rng, k, [0.3] + [0.0] * (k - 1), m, 0.10)["p_accept_real"],
            real_0_5_first=pipeline(rng, k, [0.5] + [0.0] * (k - 1), m, 0.10)["p_accept_real"])
    out["proposed_hypothesis_budget"] = sched
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
