"""LH-CP4 (owner D245): analytical power / minimum-detectable-effect equations and the approved-population rule of the
narrow Stage C exception. Pure functions, no data, no simulation, no returns.

Notation: T = monthly cross-sections; rho = first-order autocorrelation of the monthly statistic (IC_t or the
Fama-MacBeth slope); sigma = time-series standard deviation of the monthly statistic; alpha = two-sided size;
m = number of hypotheses (Bonferroni)."""
from __future__ import annotations

import math

from scipy.stats import norm, t as student_t

YEARS = tuple(range(2015, 2022))
VERIFIED_SOURCES = ("L0", "L1")


# ----------------------------------------------------------------------------------------------- Stage C exception (D245)
def approved(rec, chain, candidate):
    """Narrow Stage C exception (D245): decision year 2015-2021; every one of the 13 quarters carries a directly verified
    L0 / L1 fiscal label; LH-CP2 rule V valid (consistent labels, no transition form, no mapping failure); no identity
    flag; and the candidate's inputs complete (C1 net income, C2 revenue, C6 both)."""
    if rec["year"] not in YEARS:
        return False
    if candidate == "C1":
        ok = rec["ok1"]
    elif candidate == "C2":
        ok = rec["ok2"]
    elif candidate == "C6":
        ok = rec["ok1"] and rec["ok2"]
    else:
        raise ValueError(candidate)
    return bool(ok and chain["rule_v_v"] == "valid" and not chain["identity"]
                and all(s in VERIFIED_SOURCES for s in chain["srcs_v"]) and None not in chain["labels_v"])


# ----------------------------------------------------------------------------------------------- effective sample
def t_eff_ar1(T, rho):
    """Effective number of independent observations of a mean under AR(1) dependence (large-T approximation)."""
    return T * (1 - rho) / (1 + rho)


def t_eff_overlap(T, h):
    """Non-overlapping equivalent of T monthly observations of an h-month forward horizon."""
    return T / h


# ----------------------------------------------------------------------------------------------- critical values
def crit(alpha, m=1, df=None):
    """Two-sided critical value at Bonferroni-adjusted size alpha / m (normal, or Student-t with df)."""
    q = 1 - alpha / (2 * m)
    return float(norm.ppf(q) if df is None else student_t.ppf(q, df))


def mde(sigma, T_eff, alpha=0.05, power=0.80, m=1, use_t=True):
    """Minimum detectable mean of the monthly statistic: (c + z_power) * sigma / sqrt(T_eff)."""
    df = max(T_eff - 1, 1) if use_t else None
    z_p = float(student_t.ppf(power, df) if use_t else norm.ppf(power))
    return (crit(alpha, m, df) + z_p) * sigma / math.sqrt(T_eff)


def power_at(mu, sigma, T_eff, alpha=0.05, m=1, use_t=True):
    """Approximate power (one tail, the other tail negligible) of a test of mean mu."""
    df = max(T_eff - 1, 1) if use_t else None
    c = crit(alpha, m, df)
    ncp = mu * math.sqrt(T_eff) / sigma
    return float(student_t.sf(c - ncp, df) if use_t else norm.sf(c - ncp))


# ----------------------------------------------------------------------------------------------- effect-size mapping
QUINTILE_TOP_MEAN_Z = float(norm.pdf(norm.ppf(0.8)) / 0.2)       # E[Z | Z > z_0.8] = 1.39983...


def top_quintile_excess_annual(ic, sigma_cs):
    """Annualised top-quintile minus universe-mean return implied by a monthly IC under the stated assumptions:
    bivariate-normal signal / return with Pearson correlation = IC (rank IC ~ Pearson for normal data), constant IC
    and cross-sectional return standard deviation sigma_cs per month, equal weights, no compounding."""
    return 12 * ic * sigma_cs * QUINTILE_TOP_MEAN_Z


def ic_for_top_quintile_excess(excess_annual, sigma_cs):
    return excess_annual / (12 * sigma_cs * QUINTILE_TOP_MEAN_Z)


def fresh_dilution(ic_fresh, f):
    """Full-cross-section IC when only a fraction f of stocks carries an informative (fresh) signal and stale signals
    are uninformative with the same variance: Cov scales by f, variances unchanged -> IC_all = f * IC_fresh."""
    return f * ic_fresh


# ----------------------------------------------------------------------------------------------- costs
def annual_cost(capital, positions, turnover, commission=7.0, slippage=0.001):
    """Annual trading cost as a fraction of capital for an equal-weight book of `positions` names replaced at one-way
    annual turnover `turnover` (fraction of the book sold and re-bought per year). Each replaced position costs one
    sell and one buy order (2 * commission) and slippage on both sides (2 * slippage * traded value)."""
    orders = 2 * turnover * positions
    return orders * commission / capital + 2 * slippage * turnover


def min_trade_size(capital, positions):
    return capital / positions
