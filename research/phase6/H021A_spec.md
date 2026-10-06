# H021-A — Sector relative-momentum falsification test: frozen specification v1

- **Status:** FROZEN 2026-10-06, before any null world or real statistic is computed. The SHA-256 is pinned in `qresearch.p6h021`.
- **Authority:** owner message 2026-10-06 (`docs/owner/2026-10-06_h021a_authorisation.md`, D160).
- **Design reference:** P6-CP1 (`docs/checkpoints/P6_CP1_sector_etf_rotation_evidence_and_validation_architecture.md`).
- **Code:** `src/qresearch/lean/qr_h021.py`. Its SHA-256 is pinned with this file.
- **Change rule:** nothing here may change after any null world or real result exists. A technical fix found by the canary may change only plumbing, never the definitions below. Any fix is recorded in `DECISIONS.md`.

## 1. Question

Do US equity sectors with stronger 6-month total-return relative momentum subsequently earn higher sector-relative total returns over the next month?

This is **one bounded falsification test**. It is not a search:

- no optimizer, no grid and no alternative lookback;
- no absolute-trend overlay and no filters;
- no portfolio.

## 2. Universe (fixed for the whole experiment)

The nine original Select Sector SPDRs: **XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY** (`qr_h021.UNIVERSE`, in this order).

- XLRE, XLC and every other ETF family are excluded.
- **XLF 2016:** XLF distributed XLRE shares on 2016-09-19 (QuantConnect dividend-feed event, about 18.8% of the reference price). The distribution is treated like any other distribution in the total-return accounting (§4). It changes neither the universe nor the hypothesis.
- SPY is used only for the session calendar and for one NON-GATING diagnostic (§9).

## 3. Data and the D035 amendment

- **Development data:** decisions 2000-01 → 2017-11, which D160 amends D035 to allow, for Phase 6 and these nine ETFs only. 1999–2009 stays closed for the stock-level programme.
- **History requested:** 1998-12-01 → 2017-12-31. The last bar is the 2017-12-29 session; every ETF's first bar is 1998-12-22 (E988-01).
- **Never requested:** 2018-01-01 → 2021-12-31 for any purpose, and the Holdout (2022-01-01 → 2026-08-31).
- **Session calendar:** SPY's daily RAW bars (NYSE sessions).

## 4. Prices (total shareholder return)

These follow the H019 / D148 construction (`qr_xs_panel`).

- **Total-return close / open:** P = RAW close × split factors × dividend-feed factors, and O = RAW open × the same factors.
  - A split factor f multiplies every row before the split's first row (QuantConnect's convention, verified against SCALED_RAW).
  - A distribution with amount a and reference price ref multiplies every row before its ex-row b by (1 − a / ref). The ex-row b is the first session on or after the event day.
  - This covers cash dividends, capital-gain distributions and the XLF / XLRE distribution.
- **Point in time.** Every quantity used is a ratio of one ETF's prices inside a window that ends on or before the time it is used. A factor dated after the window multiplies both ends equally, so adjusting with the events up to 2017-12-31 gives exactly what was known at each date.
- **Missing bars:**
  - If an ETF has no bar on a session, its last total-return close is carried forward (no trade, no price change).
  - The entry open of a response is the open of the ETF's **first bar after the decision row**.
  - A response window with no entry bar is a fidelity defect: the canary fails and the run stops.
- **No ETF before launch.** The earliest row used is the signal base of the first decision (the last session of 1999-07), which is after every first bar.

## 5. Calendar and decisions

- **Decision date t:** the last NYSE session of each calendar month (`qr_h021.month_end_rows`).
- **Decisions:** month-ends 2000-01 → 2017-11 inclusive, which is **215 monthly decisions**.
  - First decision: 2000-01-31. Last decision: 2017-11-30. The last response ends at the 2017-12-29 close.

## 6. Signal

S_i(t) = P_i(month-end t) / P_i(month-end t − 6) − 1.

- This is the trailing **6-month** total shareholder return, close to close between the month-end sessions six months apart.
- There is **no skip month**.
- Ranks are highest S first. A tie, which has probability zero for continuous returns, is broken by universe order.

## 7. Response

- **Raw response:** F_i(t) = P_i(month-end t + 1) / O_i(first session after month-end t) − 1.
  - This is the total shareholder return from the **open of the first session after the decision** to the **close of the next month-end**.
  - It is consistent with the T+1-open execution rule; the decision-day close is never used as an entry.
- **Primary response:** Y_i(t) = F_i(t) − mean over the nine sectors of F_j(t), i.e. sector-relative to the equal-weight average.
- No fills, no commissions and no portfolio are involved.

## 8. Statistics and gates

**Statistics:**

- **Per decision:** IC(t) = Spearman(S(t), Y(t)) over the nine sectors, with average ranks.
- **Primary statistic:** IC̄, the mean of IC(t) over the 215 decisions.
- **t_IC** = IC̄ / (σ / √T), where σ is the population standard deviation of IC(t). This is the Newey-West estimate with lag 0, because monthly responses do not overlap (the P6-CP1 inference framework).
- **Terciles:** each month, the 3 highest-signal sectors are Top, the next 3 are Middle and the 3 lowest are Bottom.
  - For each group: the mean over decisions of the group's mean Y, × 12. This is the annualised return relative to the 9-sector average.
- **Halves:** decisions 1–107 and 108–215.
- **Blocks** (by decision year): 2000–2005, 2006–2011 and 2012–2017.
  - Block share = the block's sum of IC(t) / the total sum of IC(t).
  - If the total ≤ 0, the shares are undefined and P4 fails.

**Gates (all required):**

| Gate | Rule |
|---|---|
| **P1 statistical** | t_IC **>** c (§10) |
| **P2 economic** | Top annualised ≥ **+0.030** (+3.0%/yr vs the 9-sector average) |
| **P3 monotonic** | Top > Middle > Bottom (strict, annualised means) |
| **P4 stable** | mean IC of the first half > 0 **and** of the second half > 0, **and** total IC sum > 0, **and** no block share > 0.50 |

**Verdict:** exactly "**H021-A QUALIFIED FOR PORTFOLIO-DESIGN RESEARCH**" if P1–P4 all pass, otherwise exactly "**H021-A DID NOT QUALIFY**".

**Also reported (descriptive, not gates):**

- the null percentile of t_IC and the empirical p = (1 + #{null t_IC ≥ t_IC}) / 5,001;
- Top − Bottom annualised;
- each block's IC sum.

## 9. NON-GATING diagnostics

These are computed in the real run **after** the primary result, and are labelled "NON-GATING DIAGNOSTIC". They can neither rescue nor veto the verdict, and no c is calibrated for them.

| Diagnostic | Definition |
|---|---|
| D1: 2010–2017 | The primary evaluation restricted to decisions 2010-01 → 2017-11 (95 decisions) |
| D2: 2005–2017 | Decisions 2005-01 → 2017-11 (155 decisions) |
| D3: 3-month response | F over 3 months: P(month-end t + 3) / O(entry) − 1, demeaned. Decisions 2000-01 → 2017-09 (213). Newey-West lag 2; annualised × 4 |
| D4: 6-month response | The same over 6 months. Decisions 2000-01 → 2017-06 (210). Lag 5; annualised × 2 |
| D5: sector average vs SPY | Mean over the 215 decisions of (equal-weight mean of F_i(t) − F_SPY(t)) × 12, and its lag-0 t. SPY's total return is built exactly as in §4 |

## 10. Null and threshold

- **Identity-tethered derangement.** World w (seed w = 1 … 5,000) draws one fixed permutation p_w of the nine positions with no fixed point. It uses `numpy.random.default_rng(w).permutation(9)` repeatedly until there is no fixed point (`qr_h021.derangement`).
  - Sector i receives the **entire signal history** of sector p_w(i), i.e. S_world = S[:, p_w].
  - Returns, co-movement, volatility, persistence, dates and composition are untouched. Only the link between a sector's own signal and its own future relative return is broken. There is no global shuffle.
  - The complete §8 evaluation is re-run in every world.
- **R = 5,000 worlds**, in five batches of 1,000: E022-01 … E022-05 (seeds 1–1,000, …, 4,001–5,000).
- **c** = the 50th largest of the 5,000 null t_IC values (α = 1%, k = ⌈0.01 × 5,000⌉; `qr_h021.critical_value`).
- **What is recorded:**
  - worlds completed, failures and any retries / recoveries;
  - per-world statistics;
  - the null distribution and c;
  - the hashes of the null result and the per-world table;
  - the signal / response panel digests of every batch, which must equal the canary's;
  - the seeds.
- **Pinning.** c, the null result hash and the panel digests are pinned in `qresearch.p6h021` and committed **before** the one real evaluation E022-06. c is immutable once pinned.
  - The real run refuses to compute anything without the pins, or if its panel digests differ from the pinned ones.

## 11. Mandatory sequence

1. **Canary E989-01** (X989, infrastructure). It publishes no real IC or any other signal–response statistic. Checks:
   - all 9 histories exist for the period, with their first bars and missing sessions;
   - no ETF is used before launch;
   - the monthly calendar is correct: 215 decisions, 2000-01-31 → 2017-11-30, and the last response ends 2017-12-29;
   - 6-month signals and 1-, 3- and 6-month responses are reproduced day by day from RAW prices and the event lists (`qr_h021.slow_total_return`), worst error < 1e-9;
   - the distribution accounting is checked against QuantConnect's own ADJUSTED series: the ratio of the panel to ADJUSTED is constant within 1e-4 per session step for every ETF;
   - the XLF 2016-09-19 distribution is handled: the raw close falls about 19%, while the total-return step equals the ADJUSTED step within 1e-4;
   - future-price perturbation leaves earlier signals unchanged;
   - a fresh history request truncated at t reproduces the panel signal at t (sample of decisions);
   - placebo ranks (seeded random signals) give |t_IC| < 4 (reported);
   - planted ranks (S := Y) are recovered (IC = 1 on every date; Top > Middle > Bottom);
   - the null mapping is deterministic and fixed-point free, and repeated worlds reproduce (digests only, seeds outside 1–5,000).

   A real fidelity defect means **STOP before the null**.
2. **Null:** E022-01 … E022-05.
3. **Compute c** (`research/phase6/H021A_eval.py null`).
4. **Commit** c, the null outputs and their hashes (the threshold commit).
5. **Verify a clean tree.**
6. **ONE real evaluation, E022-06,** run with `--owner-approved D160` → P6-CP2 → STOP.

## 12. Interpretation (frozen wording)

- **Failure:** "No sector-relative momentum edge large and robust enough to meet the project's pre-registered statistical and economic requirements was detected. The study has only about 50% power around a +3.3%/yr top-3 edge. A small real edge may therefore remain undetectable."
- **Success:** "6-month sector relative momentum demonstrated sufficiently strong cross-sectional predictive information over the frozen 2000–2017 development period to qualify for portfolio-design research."
- **Never say** "sector momentum does not exist", "there is no 1–2.5% sector edge", "production ready", "SPY beating", "out-of-sample validated" or "investable".

## 13. Not done (even if H021-A qualifies)

- **No portfolio:** no top-3 rotation, $100K wealth, SPY wealth, CAGR, turnover, costs or drawdown.
- **No H021-B variants:** no absolute trend, cash, T-bill, breadth, RSI, MACD, ADX, Bollinger, breakout, volatility, moving-average or regime filter.
- **No alternative definitions:** no other lookback (3, 9, 12 or 12-1 months), no weekly version, no price-only version, no blend, no top-2.
- **No other universe:** no iShares, Vanguard, Fama-French or SEC-SIC sectors; no XLC or XLRE.
- **No locked data:** no 2018–2021 and no Holdout.
- **No paid data.**
- **No post-result rescue.**
