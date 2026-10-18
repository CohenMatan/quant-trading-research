"""OC-2 synthetic calibration v2 (owner D249): the scenario set, mapped to the owner's section-7 null-world list and
to the v1 identifiers. Defined BEFORE any v2 scenario statistic was computed; used by the engineering script and by
the (not yet authorised) confirmatory driver. Synthetic only."""
from __future__ import annotations

from dataclasses import replace

from qresearch import oc2synth_v2 as V

CTRL = V.CONTROLS
N4 = V.World("N4", priced=CTRL)                     # every control priced at 3%/yr, normal-linear (v1 N4)

# owner section-7 item -> scenarios (v1 id in the comment; 'new' = no v1 counterpart)
NULLS = {
    1: [V.World("N0i", iid=True),                                   # v1 N0i
        V.World("N0")],                                             # v1 N0
    2: [V.World("N1m", priced=("size", "beta"))],                   # new: market (beta) / size premia
    3: [V.World("N1", priced=("lowvol",))],                         # v1 N1
    4: [V.World("N3", priced=("gpa",)),                             # v1 N3 (profitability level)
        V.World("N2", priced=("ag",))],                             # v1 N2 (asset growth)
    5: [N4,                                                         # v1 N4
        replace(N4, name="N4r", form="rank"),                       # new: premia linear in the uniform rank
        replace(N4, name="N4q", form="tail")],                      # new: premia only in the extreme deciles
    6: [replace(N4, name="N5a", reliability=0.80),                  # v1 N5a
        replace(N4, name="N5b", reliability=0.60)],                 # v1 N5b (diagnostic in v1)
    7: [replace(N4, name="N2L1", latent=0.01),                      # new: weak latent growth premium
        replace(N4, name="N2L", latent=0.03),                       # v1 N2L (diagnostic in v1)
        replace(N4, name="N2L5", latent=0.05)],                     # new: strong latent growth premium
    8: [replace(N4, name="N6", tv_premia=True),                     # v1 N6
        replace(N4, name="N9", signal_ar=0.90, payoff_rho=0.30)],   # v1 N9 (own-payoff persistence)
    9: [replace(N4, name="N7", sigma_sector=0.035, sigma_factor=0.011)],   # v1 N7 (defect repaired: budget-safe)
    10: [replace(N4, name="N12", tails=3.0, hetero=0.60)],          # v1 N12
    11: [replace(N4, name="N13", horizon=3)],                       # v1 N13 (3-month overlapping response)
    12: [replace(N4, name="N8a", churn=0.0),                        # v1 N8a
         replace(N4, name="N8b", churn=2.0),                        # v1 N8b
         replace(N4, name="N11", mnar=True)],                       # v1 N11
    13: [replace(N4, name="N14", n_scale=0.5),                      # new: half-size cross-section
         replace(N4, name="N14s", n_scale=0.25)],                   # new: quarter-size cross-section
    14: [replace(N4, name="N15", irregular=True)],                  # new: irregular filing timing
}
# identification family (Tier 2, owner D250): no observed-control estimator can remove these by construction (audit
# section C); each world, at every regime run, is gated by complete-decision-rule false approval <= 2%
IDENT = ("N5a", "N5b", "N2L1", "N2L", "N2L5")
SEVERE = ("N5b", "N2L5")
CENTRAL = 0.09
# also run at IC sd 0.06 and 0.12; N5b / N2L5 added at the freeze (owner D250 section 3: the severe-confounding
# robustness gate applies in every regime, including the high-IC regime of the 4.4% N2L5 projection)
REGIME_SET = ("N0", "N4", "N4q", "N12", "N14", "N5a", "N2L", "N5b", "N2L5")
ORACLE = replace(N4, name="N2L-oracle", latent=0.03, oracle=True)    # non-gating diagnostic

EFFECTS = (0.02, 0.03, 0.04, 0.05)
POWER = ([replace(N4, name=f"P{int(e * 100)}-{r}", planted=e, ic_sd=r) for r in (0.06, 0.09, 0.12) for e in EFFECTS]
         + [replace(N4, name="P3-c0", planted=0.03, corr_scale=0.0),          # correlation regimes
            replace(N4, name="P3-c2", planted=0.03, corr_scale=2.0),
            replace(N4, name="P3-fresh", planted=0.03, fresh_only=True),       # quarterly-arrival payoff
            replace(N4, name="P3-n50", planted=0.03, n_scale=0.5)])            # sample-size dependence


def all_nulls():
    out = [w for ws in NULLS.values() for w in ws]
    out += [replace(w, name=f"{w.name}@{r}", ic_sd=r) for w in out if w.name in REGIME_SET for r in (0.06, 0.12)]
    return out
