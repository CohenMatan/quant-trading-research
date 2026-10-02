"""H016 development evaluation (research/phase2/H016_spec.md): the only implementation of the spec's gates and
diagnostics. Reuses the frozen Phase 2 definitions (qresearch.p2spec: Sharpe, CAGR, Calmar, drawdown, G1 thresholds,
G3 blocks, G4 thresholds, DSR, bootstrap) with the owner-approved H016 adaptations (2026-10-02):
  * common evaluation window: every comparative metric uses the same dates, from the first H016 portfolio decision
    (COMMON_START, first trading day of March 2010) to 2021-12-31 — candidate, same-universe EW, random controls and
    SPY alike;
  * G1/G3/G4 compare with the same-universe equal-weight benchmark EW-H016 (E016-02), not E901-07;
  * G2: Sharpe(H) > median Sharpe of the five frozen random controls (each reported individually; never averaged into
    one return stream);
  * a pre-declared survivorship sensitivity diagnostic (frozen inputs below, from the completed data audit).
Nothing here may change after an H016 result."""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from . import config, metrics, p2spec

SPEC = "research/phase2/H016_spec.md"
SPEC_SHA256 = "PENDING"            # pinned when the spec is frozen (before the canary); tests/test_p2h016.py
COMMON_START, END = "2010-03-01", "2021-12-31"
CANDIDATE, EW_H016, SIZING_200K = "E016-01", "E016-02", "E016-08"
RANDOM = ("E016-03", "E016-04", "E016-05", "E016-06", "E016-07")          # seeds 1..5, frozen
SLIP_2X, SLIP_4X, SLIP_6X = "E016-09", "E016-10", "E016-11"
PERTURBATIONS = ("E016-12", "E016-13", "E016-14", "E016-15", "E016-16", "E016-17")   # P1..P6
SPY_ID, EW_BROAD_ID = p2spec.SPY_ID, p2spec.EW_ID
N_P2_SELECTION = 3                 # Phase 2 selection configurations: H014 A and B, H016's single candidate
N_CUMULATIVE = 40 + N_P2_SELECTION  # programme-1 official N (D087) + Phase 2

# ---- survivorship sensitivity (frozen before any H016 result; inputs from the completed data audit)
# (1) availability bias of a usable-only equal-weight universe vs the full non-financial universe, pp a year
#     (final canary E976-06, research/phase2/sec/e976_results_E976-06.json; only positive values are applied)
AVAILABILITY_BIAS_PP = {2010: -0.63, 2011: 0.81, 2012: 0.14, 2013: -0.06, 2014: 1.05, 2015: 0.75, 2016: 0.36,
                        2017: 0.44, 2018: 1.59, 2019: 0.74, 2020: -0.41, 2021: 4.05}
# (2) SEC-side unresolved share of registrants with public float >= $2B (research/phase2/sec/residual_audit.json):
#     missing / (native + repaired + missing)
UNRESOLVED = {2010: (4, 659), 2011: (8, 829), 2012: (6, 852), 2013: (5, 919), 2014: (7, 1050), 2015: (7, 1141),
              2016: (5, 1110), 2017: (9, 1134), 2018: (8, 1216), 2019: (6, 1227), 2020: (6, 1211), 2021: (11, 1415)}
# (3) worst-case return gap of a missing company: the D043-measured gap of later-distressed missing names vs the
#     universe, 39.7 points a year (docs/data/survivorship_gap_2010.md §5)
DISTRESS_GAP = 0.397
LOW_COVERAGE_YEARS = (2010, 2011)  # repaired names mostly unusable before 2012 (XBRL phase-in; P2-CP7/CP8)


def spec_hash() -> str:
    return hashlib.sha256((config.REPO_ROOT / SPEC).read_bytes()).hexdigest()


def window_eq(eq: pd.Series, a: str = COMMON_START, z: str = END) -> pd.Series:
    """Equity on the common evaluation dates (identical for every book)."""
    return eq[(eq.index >= a) & (eq.index <= z)]


def rets(eq: pd.Series) -> pd.Series:
    return p2spec.returns(window_eq(eq))


def g1(eq_h, eq_ew, eq_spy) -> dict:
    return p2spec.g1(window_eq(eq_h), window_eq(eq_ew), window_eq(eq_spy))


def g2(sharpe_h: float, sharpe_random: list[float]) -> dict:
    """Sharpe(H) strictly above the median Sharpe of the five random controls (all five reported)."""
    vals = [float(x) for x in sharpe_random]
    med = float(np.median(vals)) if len(vals) == 5 and all(np.isfinite(vals)) else float("nan")
    return dict(random_sharpes=vals, median_random=med, dispersion=dict(min=min(vals), max=max(vals)) if vals else {},
                ok=bool(np.isfinite(med) and sharpe_h > med))


def g3(eq_h, eq_ew) -> dict:
    return p2spec.g3(rets(eq_h), rets(eq_ew))


def d_ew(eq_x, eq_ew) -> float:
    return p2spec.sharpe(rets(eq_x)) - p2spec.sharpe(rets(eq_ew))


def g4(perturbation_d_ew, d_ew_2x, drag_pa) -> dict:
    return p2spec.g4(perturbation_d_ew, d_ew_2x, drag_pa)


def robustness_triggered(g1_ok, g2_ok, g3_ok) -> bool:
    return p2spec.robustness_triggered(g1_ok, g2_ok, g3_ok)


def survivorship_penalty_pp(year: int) -> float:
    """Frozen yearly penalty (pp a year) charged against the candidate's relative performance: the positive part of
    the measured availability bias plus the worst case that every unresolved large company was a later-distressed
    name the candidate would have held at its universe share."""
    miss, base = UNRESOLVED[year]
    return max(0.0, AVAILABILITY_BIAS_PP[year]) + 100.0 * miss / (base + miss) * DISTRESS_GAP


def survivorship_sensitivity(eq_h, eq_ew) -> dict:
    """Diagnostic only (never a gate, never an optimisation path). (S1) charge each day of year y with
    penalty_y / 252 against the candidate and recompute Sharpe(H) - Sharpe(EW-H016) and G3's block view;
    (S2) the same difference excluding the low-coverage years 2010-2011."""
    r_h, r_ew = rets(eq_h), rets(eq_ew)
    years = pd.Index(r_h.index).str[:4].astype(int)
    pen = np.array([survivorship_penalty_pp(int(y)) / 100.0 / 252.0 for y in years])
    r_adj = r_h - pen
    base = p2spec.sharpe(r_h) - p2spec.sharpe(r_ew)
    s1 = p2spec.sharpe(r_adj) - p2spec.sharpe(r_ew)
    a = f"{max(LOW_COVERAGE_YEARS) + 1}-01-01"
    s2 = p2spec.sharpe(p2spec.window(r_h, a, END)) - p2spec.sharpe(p2spec.window(r_ew, a, END))
    blocks = p2spec.g3(r_adj, r_ew)
    return dict(base_d_ew=base, s1_penalised_d_ew=s1, s1_clears_margin=bool(s1 >= p2spec.MARGIN_EW),
                s1_g3_ok=blocks["ok"], s2_from=a, s2_d_ew=s2, s2_clears_margin=bool(s2 >= p2spec.MARGIN_EW),
                penalty_pp={y: round(survivorship_penalty_pp(y), 3) for y in sorted(UNRESOLVED)})


def cost_drag(fills, eq, slippage_rate) -> dict:
    return p2spec.cost_drag(fills, window_eq(eq), slippage_rate)


def dsr_views(r: np.ndarray, n_robustness_configs: int) -> dict:
    return p2spec.dsr_views(r, N_P2_SELECTION, N_P2_SELECTION + int(n_robustness_configs), N_CUMULATIVE)


def classify(cagr, g1_ok, g2_ok, all_ok) -> dict:
    c = p2spec.classify(cagr, g1_ok, g2_ok, all_ok)
    c["random-control-beating"] = c.pop("control-beating")
    return c
