# Phase 4 — Cross-Sectional Technical Signal Validation: Pre-Registration of H019 (v2)

**Status: FROZEN CANDIDATE v2 (P4-CP3R2, 2026-10-04). Awaiting the owner's explicit approval of the H019 runs. Not run.**

**Pinning**
- The SHA-256 of this file is pinned in `qresearch.p4xs.SPEC_SHA256`.
- Every constant of `src/qresearch/lean/qr_xs.py` named here is pinned in `qresearch.p4xs.CONSTANTS`.
- Both are checked by `tests/test_p4xs_spec.py`.

**Code and tests**
- The procedure is implemented end to end by `qr_xs.Panel`, `qr_xs.Features` and `qr_xs.run_world`.
- `tests/test_xs.py` and `tests/test_xs_pipeline.py` cover it on synthetic data, including the leakage canaries.

**Change control**
- **Nothing may change after any real signal, return or statistic is computed.**
- A genuine code defect found by a canary is a technical repeat: fix, re-run the whole affected stage, record. It never changes a rule.

**Changes from v1 (P4-CP3R):**
1. **The research window is fixed mechanically.**
   - The first research month-end is 2010-01 (D034: research data from 2010-01-04).
   - The first trend-factor regression is therefore s = 2010-01.
   - The first decision is 2011-01, so there are **83 decisions, 2011-01 → 2017-11**.
2. **Smooth momentum.**
   - The invented 200-day minimum is removed.
   - ID uses all daily returns observed in the formation window, whenever PRET is defined.
   - The zero-day and quintile conventions are now source-verified.
3. **Trend factor.**
   - Missing-history handling and collinearity handling follow the Chen-Zimmermann code exactly.
4. **Null.**
   - The **stratified identity-tethered permutation acts on the stocks' input features**.
   - **Every null world re-runs the complete procedure**, including the trend-factor regressions and rolling coefficients.

**Hypothesis H019 is this procedure.**
- At least one of two published refinements of momentum carries cross-sectional information about next-month relative returns of US stocks ≥ $2B (2011–2017).
  - The two refinements are Da-Gurun-Warachka information discreteness and the Han-Zhou-Zhu trend factor.
- The information must be:
  - economically meaningful;
  - monotonic;
  - stable;
  - exceptional against a structure-preserving null;
  - **additional to plain 12-1 momentum**.
- **Plain momentum is the reference.** Its result is a replication or sanity check, never a discovery.

---

## 1. Data, universe and period

| Item | Value |
|---|---|
| Engine and data | QuantConnect Cloud LEAN, build 18131 (pinned per experiment); data infrastructure v1 (`research/phase2/data_freeze_v1.json`), unchanged |
| Universe (each month-end close) | Harness eligibility of data v1: US common stock, point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, SEC correction layer on. Financials included. No present-day lists |
| Prices for S1, S2 and returns | Split- and dividend-adjusted (total-return) closes and opens as known at each session |
| Prices for S3 | **Split-adjusted, not dividend-adjusted** closes (the published construction uses \|prc\| / cfacpr) |
| History | Up to the 1,000 most recent daily bars before each research month-end. QuantConnect US equity daily data starts in 1998, so the full 1,000-bar window exists for every stock listed by early 2006. Pre-2010 prices serve **only** as look-back inputs to signals. No pre-2010 return is a test observation or an estimation input |
| **Research month-ends** | 2010-01 → 2017-12. 2010-01 is the first month-end on or after the research start 2010-01-04 (D034) |
| Trend-factor regressions | s = 2010-01 → 2017-11. Each uses month-(s+1) returns; the last uses December 2017 |
| **Primary decisions** | **2011-01 → 2017-11: 83 month-ends.** 2011-01 is the first month with 12 completed regressions (s = 2010-01 … 2010-12). The last next-month return ends at the 2017-12-29 close |
| 3-month diagnostic decisions | 2011-01 → 2017-09: 81 month-ends |
| Hard limits in code | Every run ends on or before 2017-12-31. No 2018-01-01 → 2021-12-31 data in any form. Holdout 2022-01-01 → 2026-08-31 locked |

**One common decision window.** It is the window in which all three signals exist, fixed mechanically by the formulas.

## 2. Signals (exact)

**Notation.** For month k, d = the row of its last session.
- P = total-return closes; Q = split-adjusted closes.
- A stock's price "at" a month-end is its last bar at or before that session. That bar may be at most 5 sessions earlier; otherwise the price is missing.

### S1 — Plain momentum (reference)

```
S1 = PRET = P(month-end k−1) / P(month-end k−12) − 1
```

This is the Jegadeesh-Titman 11-month return skipping the most recent month (the Fama-French "prior 2–12").

### S2 — Information discreteness (Da, Gurun & Warachka 2014, RFS 27(7))

```
ID = sgn(PRET) × (%neg − %pos)
```

- **PRET** = S1: "the past twelve months after skipping the most recent month".
- **%pos / %neg:** "the percentages of days during the formation period with positive / negative returns".
  - Numerator: the number of positive (negative) daily returns.
  - Denominator: **all daily returns observed in the window.** A daily return runs from one bar's close to the next bar's close. The window covers the bar at month-end k−12 to the bar at month-end k−1.
- **Zero returns:** neither positive nor negative; they count in the denominator only.
- **Missing sessions:** no return is recorded for a session without a bar.
- **sgn(0) = 0.**
- **No additional minimum:** ID is defined whenever PRET is defined.

**Sequential sort (the paper's double sort: PRET quintiles first, then ID within).**

```
key = −sgn(PRET) × ID      (low ID = continuous information; continuity in the direction of PRET)
S2  = PRET quintile index (1..5) + within-quintile percentile of key in (0, 1]
```

- Quintiles are equal-count, by ordinal rank, with ties broken by stock order.
- Average ranks are used within the quintile.

### S3 — Trend factor (Han, Zhou & Zhu 2016, JFE 122(2)), as implemented by Chen & Zimmermann

**Moving averages at the month-end close of month t:**

```
A_L,t = (mean of the last L split-adjusted closes ending at the stock's month-end bar) / (that close)
L ∈ {3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000}
```

- If fewer than L closes exist, the mean is taken over those available (at least 1).
- This follows Stata `asrol` / OSAP `TrendFactor.py`, `min_samples=1`. The replicator notes the paper does not discuss a minimum.

**Monthly regressions (s = 2010-01 → 2017-11).**
- Once month s+1 has ended, run a cross-sectional OLS **with an intercept**:
  - dependent variable: each stock's month-(s+1) total return, from P at month-end s to P at month-end s+1 (a delisted stock is valued at its last real close);
  - regressors: A_L,s;
  - sample: every eligible stock at month-end s with a bar at that close, **including stocks without a 12-month history**.
- **Collinearity:** regressors are taken in order. One that does not raise the rank is omitted with coefficient 0 (Stata `regress` / OSAP `omit_collinear`, zero for omitted variables).
- **Under-identified regressions** give no coefficients.

**Expected coefficients and signal.**

```
E[β_L]_t = mean of β_L,s over s = t−12 … t−1      (all 12 required; the paper's 12-month average)
S3_t     = Σ_L E[β_L]_t × A_L,t
```

### Point-in-time guarantees (tested)

- **S1 and S2** use closes up to month-end k−1.
- **S3** uses closes up to the decision close, and coefficients from returns realised by the decision close (`qr_xs.TrendFactor` refuses look-ahead).
- **Leakage canaries** (`tests/test_xs_pipeline.py`):
  - future prices cannot change past signals;
  - the next month's returns cannot change the score that predicts them;
  - truncating after the decision leaves it unchanged;
  - late entrants cannot change earlier regressions;
  - the vectorised features equal a slow reference computation.

### Common sample

- **Evaluation set:** a stock enters the date's evaluation set only if it is eligible with a month-end bar **and** PRET, ID and S3 are defined.
- **Regression set:** stocks that are eligible but lack PRET / ID (shorter histories) still enter the trend-factor regressions.

## 3. Response

| Item | Definition |
|---|---|
| **Primary** | Total return from the **open of the first session after the decision** to the stock's last bar at or before the **close of month-end k+1**, minus the equal-weighted mean of the same quantity over the date's evaluation set (cross-sectionally demeaned). If there is no bar after the decision, the return is 0 |
| **Diagnostic** | The same to month-end k+3 |

## 4. Statistics per decision date

- **Rank IC** of S1, S2 and S3: the Spearman correlation with the demeaned response (average ranks).
- **Deciles and quintiles:** 10 and 5 equal-count buckets by signal (ordinal rank); the mean demeaned response per bucket.
- **Incremental statistic (S2, S3):** the mean over the five S1 quintiles of the within-quintile partial Spearman correlation between the candidate component and the response, controlling for S1:
  - S2's component is the key;
  - S3's component is S3 itself.

## 5. Time-series inference

- **Primary:** the mean over the 83 dates.
  - Newey-West (Bartlett) HAC standard error, **lag 2**.
  - t = mean / SE.
  - Annualised decile figures = the mean monthly figure × 12.
- **3-month diagnostic:** NW lag 6, figures × 4.
- **Halves:** the first 41 and the last 42 dates.
- **Blocks:** calendar 2011–12, 2013–14, 2015–16, 2017.

## 6. Null and the family critical value

**Stratified identity-tethered within-date permutation of the input features** (`qr_xs.Tether`, `qr_xs.run_world`):

1. **Each month-end, two strata.** The stocks in the regression set split into:
   - **full**: PRET and ID defined;
   - **partial**: moving averages only.
2. **Partner assignment.**
   - Each stock (the receiver) gets the **complete feature vector** (PRET, ID, A_3 … A_1000) of a random partner of the same stratum.
   - It keeps that partner while both remain in the set and in the same stratum.
   - Unmatched stocks are re-matched at random within their stratum.
3. **Everything downstream is recomputed** from the mapped features and the receivers' **real** returns:
   - the monthly trend-factor regressions;
   - the 12-month coefficient averages;
   - S3;
   - S2's two-stage sort;
   - every statistic and the promotion inputs.

**What is preserved and what is broken.**
- **Preserved:**
  - real dates, real returns and their distribution;
  - market, sector and style shocks;
  - universe composition and the evaluation set;
  - each date's feature distribution within each stratum;
  - feature persistence (a receiver's features are a real stock's history);
  - the joint dependence of PRET, ID and the moving averages, which come from one partner's price path. So the S1 → S2 two-stage structure is intact.
- **Broken:** only the link between a stock's features and its own subsequent returns. That includes the returns used to fit the trend factor, so the null factor is fitted to noise exactly as the real procedure would be.

**Family critical value.**
- F = max(t_S1, t_S2, t_S3, t_inc,S2, t_inc,S3) per world.
- **c = the 50th largest F over R = 5,000 worlds** (seeds 1–5,000; α = 1%).
- The null runs first. c and the per-world table are committed and SHA-256-pinned **before** the real run.

**α = 1%** is a conservative pre-registered research threshold. It reflects the project's earlier experimentation with momentum-type signals on 2010–2017 (H002, H003, H008, H018). It is not a formally derived correction.

## 7. Promotion rule (all conditions, per signal)

| Code | Condition |
|---|---|
| P1 Economic | Top-decile annualised demeaned excess ≥ **3.0% a year** **and** D10 − D1 > 0 |
| P2 Monotonic | Spearman(quintile index 1..5, mean quintile excess) ≥ **0.90** (at most one adjacent inversion) **and** Q5 > Q1. For S2 the quintiles are its PRET backbone; its within-quintile refinement is judged by P6 |
| P3 Statistical | t (rank IC) > c |
| P4 Stable | Mean IC > 0 in **both** halves **and** no block contributes more than **50%** of the total IC sum (and that sum is > 0) |
| P5 Exceptional | Through c; the full-rule null rate is reported |
| P6 Incremental (S2, S3 only) | t_inc > c |

**Outcomes:**
- **candidate:** S2 and / or S3 pass; if both, the larger t_inc is selected.
- **replication_only:** only S1 passes.
- **none:** nothing passes.

**The 3-month diagnostic never promotes, rescues or vetoes anything.**

## 8. Diagnostics (reported, never gated, never used to change a rule or a signal)

1. **3-month horizon:** the same statistics, NW lag 6.
2. **Per-year table:** IC, t, top-decile excess and sign.
3. **Sector-neutral IC:** within Fama-French 12 sectors from point-in-time SEC SIC; "unclassified" is its own group.
4. **Size:** IC by market-cap half; each signal's correlation with log market cap.
5. **Signal characteristics:** mean cross-sectional correlations among S1–S3 and with the trailing 1-month return.
6. **Incremental detail:** the partial IC per S1 quintile.
7. **S3 decomposition (explanatory only):**
   - IC and incremental IC of the three components Σ E[β_L] A_L over L ≤ 20, 50 ≤ L ≤ 200 and L ≥ 400;
   - the E[β_L] path.
   - **It can never remove horizons, define a new factor variant, or promote or rescue anything.**
8. **History coverage:** the share of the regression set and of the evaluation set with fewer than L bars, for each L.
9. **Top decile vs SPY.**
10. **Turnover:** rank autocorrelation; top-decile and top-quintile retention.
11. **Realised power:** realised IC volatility, effective sample size, and the IC detectable at c.

## 9. Pre-registered interpretation

**none:**
- *"No technical stock-selection signal large enough to satisfy the project's detection and economic-significance requirements was found."* Not "no 1–3% technical edge exists".
- Technical stock-selection research in this universe stops: no RSI / MACD / ADX / Bollinger / volume / breakout follow-ups.
- No simplified trend-score substitute (that would need a v3 specification and owner approval).

**replication_only:**
- Momentum is reproduced; no new signal. The owner decides.

**candidate:**
- Means only that credible cross-sectional predictive information exists on 2011–2017 under the frozen test.
- It does **not** mean a production strategy, beating SPY, portfolio viability, or 2018–2021 validation.
- Next: **one** portfolio design (a separate pre-registration and approval). 2018–2021 stays untouched until then; the Holdout stays locked.

## 10. Runs (each only after explicit owner approval; configs carry `owner_approval_required`)

| Run | Purpose | Publishes |
|---|---|---|
| E985-01 (X985) | **Plumbing / fidelity canary.** Checks: placebo features (seeded random), so IC ≈ 0; a planted response-based signal with a known IC; independent slow recomputation of PRET / ID / A_L / regressions for a fixed sample (digest and maximum difference only); trend-factor look-ahead guard; universe and history-coverage counts; horizon end ≤ 2017-12-29; runtime, memory and output | Canary statistics only; no real-signal statistic |
| E020-01..05 (S020 = byte copy of X985) | Null worlds 1–5,000 (1,000 per run): full procedure per world | Null F and per-world statistics only |
| — | Commit and pin c + the null table (SHA-256); verify a clean working tree | — |
| E020-06 (S020) | The real evaluation, once | Real statistics and diagnostics |
| — | H019 checkpoint (P4-CP4); STOP | — |
