# P7-CP5 — H022 Predictive Evaluation of Conviction Score v1 (TEMPLATE; filled only after the one real run)

This template is frozen with the specification (`research/phase7/P7_predictive_spec.md`, pinned in `qresearch.p7pred`). Each field is filled from the real evaluation's exported statistics, exactly as defined. Nothing is added, removed or re-ordered after the result is seen.

## 1. Provenance

| Item | Value |
|---|---|
| Spec SHA-256 | (must equal `p7pred.SPEC_SHA256`) |
| Code hashes | (must equal `p7pred.CODE_SHA256`) |
| Canary X994 run id and result | |
| Null runs E023-01 … 05 (run ids) | |
| Null result hash | |
| c_IC | value and the commit that pinned it before the real run |
| Real run E023-06 | run id, commit (clean tree), LEAN version, 0 orders |

## 2. Population and coverage

- Dates used (expected 83).
- Stocks per date (min / median / max).
- 80+ stocks per date (mean; months with none).
- Response status counts by year and score quintile: `ok` / `truncated` / `no_bar_after_t` / `unverified_split`.

## 3. Gates (in this order)

| Gate | Statistic | Threshold | Result |
|---|---|---|---|
| G1 Significance | t_IC = …; mean IC = … | > c_IC = … and IC > 0 | PASS / FAIL |
| G2 Economic | 80+ excess = … % / yr (months with an 80+ stock) | ≥ +3.0% / yr | PASS / FAIL |
| G3 Monotonicity | quintile means Q1 … Q5 = …; Spearman = … | ≥ 0.90 and Q5 > Q1 | PASS / FAIL |
| G4 Stability | half 1 IC = …, half 2 IC = …; largest block share = … | both > 0 and ≤ 50% | PASS / FAIL |

**Verdict:** H022 QUALIFIED (all four pass) / NOT QUALIFIED.

## 4. Pre-registered diagnostics (non-gating)

- **Sector-demeaned IC and t-statistic:** flagged "substantially sector-driven" if t_sector < ½ t_IC.
- **Mean IC by regime state:** STRONG / NORMAL / WEAK / RISK_OFF, with month counts.
- **Incremental test:** slope on the score, its t-statistic and its null quantile.
- **2- and 3-month horizons:** mean IC and NW t-statistic.
- **Per-year mean IC.**

## 5. Null and procedure

- Null t_IC distribution: mean, sd, 95th / 99th percentiles.
- Full-procedure false-promotion rate among the null worlds.

## 6. Confirmations

- No change to the score, mechanics, horizon, thresholds or gates after the result.
- 2018–2021 untouched.
- Holdout untouched.
- No portfolio run.
- Nothing purchased.

## 7. Owner decisions

- **If QUALIFIED:** design the frozen-mechanics portfolio stage (Part B of the spec) on 2011–2017. Then, with separate approval, run the 2018–2021 internal out-of-sample.
- **If NOT QUALIFIED:** reject H022 and preserve it as tested; any further direction is a new decision.
