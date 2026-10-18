"""OC-2 v2 (owner D249 section 3): failure-mode audit of the v1 synthetic calibration.

Synthetic / analytical only. It uses (i) the frozen v1 code `qresearch.oc2synth` to reproduce the two defects, (ii)
committed v1 summaries / per-replication rows, and (iii) large-sample POPULATION algebra on synthetic characteristics
(no returns are simulated, no rejection rate or power is computed here) to measure the bias of the Fama-MacBeth signal
slope implied by each v1 null mechanism under candidate control specifications.

    PYTHONPATH=src python research/longhorizon/oc2/v2/OC2_V2_audit.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
sys.path[:0] = [str(ROOT / "src")]
from qresearch import oc2synth as O  # noqa: E402  (frozen v1, never modified here)
from qresearch import oc2synth_v2 as V  # noqa: E402

OUT = HERE / "OC2_V2_audit.json"
POP_N = 400_000
SEED = 20261018


def defect_n7():
    w = O.World("N7", priced=O.CONTROLS, sigma_sector=0.05, sigma_factor=0.02)
    k = len(O.CHARS)
    var_sys = w.sigma_sector ** 2 + (k - 1) * w.sigma_factor ** 2 + (0.3 * w.sigma_market) ** 2
    idio = math.sqrt(max(O.SD_TOTAL ** 2 - var_sys, 1e-6))
    return dict(total_var=O.SD_TOTAL ** 2, systematic_var=round(var_sys, 6), idio_sd=round(idio, 5),
                note="systematic variance exceeds the fixed total, so the idiosyncratic sd hit the 1e-6 floor "
                     "(0.1% a month instead of about 5%); the world was nearly noise-free")


def defect_n13():
    """Reproduce v1's N13 NaN on the frozen code: count NaN 3-month responses in one replication."""
    w = O.World("AUDIT-N13", priced=O.CONTROLS, horizon=3, churn=0.0)
    P = O.Panel(w, 1)
    for t in range(-O.WARMUP, 0):
        _s, live = P.step(t)
        P.returns(live)
    R, samples = [], []
    for t in range(O.T + 2):
        sample, live = P.step(t)
        full = np.full(P.S, np.nan)
        full[live] = P.returns(live)
        R.append(full)
        if t < O.T:
            samples.append(sample)
    nan_months = 0
    for t, s in enumerate(samples):
        r = R[t][s] + R[t + 1][s] + R[t + 2][s]
        nan_months += int(np.isnan(r).any())
    shrink = int(np.sum(np.diff(O.n_by_month()) < 0))
    return dict(months_with_nan_response=nan_months, months_where_cross_section_shrinks=shrink,
                root_cause="returns were generated only for live slots; when the cross-section shrinks, stocks "
                           "leave `alive` and their next-month returns are NaN, so any 3-month response spanning "
                           "a shrink month is NaN and the whole slope series becomes NaN")


def population(premia, rho_scale=1.0, reliability=1.0, latent=0.0, ctrl="rank", oracle=False, form="normal",
               n=POP_N, seed=SEED):
    """Population bias of the signal coefficient: regress the expected return mu (no noise) on the design
    [signal rank, controls(spec), intercept]. Returns the coefficient in slope units and the implied annual
    top-quintile effect (12 * 0.8 * b * E[rank | top quintile] - mean, rank units -> top-minus-universe)."""
    rng = np.random.default_rng(seed)
    C = O.corr_matrix()
    L = np.linalg.cholesky(C)
    Z = rng.standard_normal((n, len(O.CHARS))) @ L.T
    rho = np.array([O.RHO_F5[c] for c in O.CHARS]) * rho_scale
    beta = np.linalg.solve(C, rho)
    s = Z @ beta + math.sqrt(1 - beta @ C @ beta) * rng.standard_normal(n)
    th = np.zeros(len(O.CHARS))
    for c in O.CONTROLS:
        th[O.CHARS.index(c)] = O.PREMIA_SIGN[c] * O.theta_from_annual(premia)
    if latent:
        th[O.CHARS.index("growth")] = O.theta_from_annual(latent)
    if form == "normal":
        F = Z
    elif form == "rank":                     # premia linear in the uniform rank (sd-matched)
        F = (norm.cdf(Z) - 0.5) * math.sqrt(12)
    elif form == "tail":                     # premia only in the top / bottom deciles (sd-matched)
        F = (np.where(Z > norm.ppf(0.9), 1.0, 0.0) - np.where(Z < norm.ppf(0.1), 1.0, 0.0)) / math.sqrt(0.2)
    mu = F @ th
    Zc = Z[:, :8]
    if reliability < 1:
        Zc = math.sqrt(reliability) * Zc + math.sqrt(1 - reliability) * rng.standard_normal(Zc.shape)
    if oracle:
        Zc = np.column_stack([Zc, Z[:, O.CHARS.index("growth")]])
    X = V.design_controls(s, Zc, ctrl)
    X = np.column_stack([X, np.ones(n)])
    b = np.linalg.lstsq(X, mu, rcond=None)[0][0]
    return dict(b=float(b), annual_top_quintile=float(12 * b * 0.4))     # centred rank: top quintile mean 0.4


def quiet_market():
    """Why v1's implied IC sd was ~0.03: the slope noise had no signal-payoff component."""
    rows = json.loads((ROOT / "data/oc2_stage2_parts/N4.json").read_text())["rows"]
    sd_ic = float(np.mean([r["sd_slope"] for r in rows])) / math.sqrt(12) / float(np.mean([r["ret_sd"] for r in rows]))
    n = O.n_by_month()
    floor = float(np.mean(1 / np.sqrt(n - 21)))
    lev = np.array([O.RHO_F5[c] for c in O.CONTROLS])
    factor_part = float(np.sqrt(np.sum((lev * 0.010) ** 2)) / O.SD_TOTAL)
    return dict(v1_implied_ic_sd=round(sd_ic, 4), sampling_scale_mean_1_over_sqrt_n_minus_k=round(floor, 4),
                factor_shock_ic_sd_if_uncontrolled=round(factor_part, 4),
                signal_payoff_component=0.0,
                explanation="v1 slope noise was essentially cross-sectional sampling noise (order 1/sqrt(N); the "
                            "v1 'implied' figure divides by the TOTAL return sd, so it sits slightly below that "
                            "scale). Control-factor shocks would add about 0.045 to a univariate IC through the "
                            "signal's 0.05-0.18 correlations, but the multivariate FM absorbs them in the control "
                            "coefficients; sector shocks are absorbed by the sector dummies. v1 had NO time-varying "
                            "payoff on the signal itself, which is what makes a real IC vary month to month "
                            "(LH-CP4's 0.06-0.12 range). The quiet market is therefore a missing DGP component, "
                            "not an SE scaling problem: cross-sectional dispersion (6.5%/month) was realistic, IC "
                            "dispersion and its serial correlation were not (no signal payoff), premium variability "
                            "existed only in N6 / N9, and residual noise was realistic except in N7 (defect)")


def main():
    v1 = json.loads((ROOT / "research/longhorizon/oc2/stage2/OC2_S2_classification.json").read_text())
    res = dict(kind="OC-2 v2 failure-mode audit (v1 code reproduction + population algebra; no returns simulated)",
               decision="D249", v1_classification=v1["outcome"], v1_driver_outcome=v1["driver_outcome"],
               A_defects=dict(N7=defect_n7(), N13=defect_n13(),
                              classifier="the v1 driver applied only the adequacy part of protocol 6.1 (four "
                                         "worlds) and not 'any failed or incomplete scenario -> D'; v2 computes "
                                         "the classification with one function tested against the written rule"))
    pop = {}
    for name, kw in {
        "N4 normal-linear premia": dict(premia=0.03, form="normal"),
        "N4r rank-linear premia": dict(premia=0.03, form="rank"),
        "N4q tail (decile) premia": dict(premia=0.03, form="tail"),
        "N5a reliability 0.8": dict(premia=0.03, reliability=0.8),
        "N5b reliability 0.6": dict(premia=0.03, reliability=0.6),
        "N2L latent growth +3%": dict(premia=0.03, latent=0.03),
        "N2L latent growth +3% (oracle control)": dict(premia=0.03, latent=0.03, oracle=True),
        "N2L latent growth +1%": dict(premia=0.03, latent=0.01),
        "N2L latent growth +5%": dict(premia=0.03, latent=0.05),
    }.items():
        pop[name] = {spec: population(ctrl=spec, **kw) for spec in ("rank", "rcs")}
    res["B_C_population_bias"] = pop
    res["D_quiet_market"] = quiet_market()
    OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    for k, v in pop.items():
        print(k, {s: round(x["annual_top_quintile"] * 100, 3) for s, x in v.items()})
    print(json.dumps(res["A_defects"], indent=1)[:900])
    print(res["D_quiet_market"])


if __name__ == "__main__":
    main()
