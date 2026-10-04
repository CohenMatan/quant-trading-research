# Phase 4 — Cross-Sectional Technical Signal Validation: Pre-Registration of H019 (v1)

**Status: FROZEN CANDIDATE v1 (P4-CP3R, 2026-10-04). Awaiting the owner's explicit approval. Not run.**

- **Pinning:**
  - The SHA-256 of this file is pinned in `qresearch.p4xs.SPEC_SHA256`.
  - Every constant of `src/qresearch/lean/qr_xs.py` named here is pinned in `qresearch.p4xs.CONSTANTS`.
  - Both are checked by `tests/test_p4xs_spec.py`.
- **Changes:**
  - Any change before approval produces v2, with a new hash.
  - **Nothing may change after any real signal, return or statistic is computed.**
  - A genuine code defect found by a canary is a technical repeat: fix it, re-run the whole affected stage, record it. It never changes a rule.
- **Supersedes:** the P4-CP3 draft (3-month primary horizon; simplified trend score; unsigned "net up-day" smoothness proxy).

**Hypothesis H019 is this procedure.**
- At least one of two published refinements of momentum carries cross-sectional information about next-month relative returns of US stocks ≥ $2B (2011–2017) that is:
  - economically meaningful;
  - monotonic;
  - stable;
  - exceptional against a structure-preserving null;
  - **additional to plain 12-1 momentum.**
- The two refinements:
  - Da-Gurun-Warachka information discreteness (frog-in-the-pan);
  - the Han-Zhou-Zhu trend factor.
- **Plain momentum is the reference.** Its result is a replication or sanity check, never a discovery.

---

## 1. Data, universe and period

| Item | Value |
|---|---|
| Engine and data | QuantConnect Cloud LEAN, build 18131 (pinned per experiment); data infrastructure v1 (`research/phase2/data_freeze_v1.json`), unchanged |
| Universe (each decision close) | Harness eligibility of data v1: US common stock, point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, SEC correction layer on. Financials included. No present-day lists |
| Prices for S1, S2 and returns | Split- and dividend-adjusted closes as known at each close (`SCALED_RAW`, the X984 convention); total returns |
| Prices for S3 | **Split-adjusted, not dividend-adjusted** closes (the published construction uses price / split factor). A window rescaled only on splits |
| History | Harness warm-up from 2009-07-01, plus a history request of up to 1,000 daily bars when a stock enters the subscription set. Pre-2010 prices serve **only** as look-back inputs to signals; they are never test observations and are never used to estimate anything |
| Trend-factor regressions | The first regression uses the signals at the 2010-02-26 close and the March 2010 returns. No pre-2010 return is used to estimate anything |
| **Primary decisions** | The close of the last session of each month, **2011-02 → 2017-11: 82 dates**. The first date is the first month with 12 completed trend-factor regressions. The last next-month return ends at the 2017-12-29 close |
| 3-month diagnostic decisions | 2011-02 → 2017-09: 80 dates |
| Hard limits in code | Every run ends on or before 2017-12-31. No 2018-01-01 → 2021-12-31 data in any form. Holdout 2022-01-01 → 2026-08-31 locked |

**One common decision window for all three signals.** It is the window in which all three exist, so the family test and the incremental tests compare like with like.

## 2. Signals (exact)

**Setup.** Decision at the close of month m (session d).
- P = the adjusted close.
- Q = the split-adjusted close.
- Daily returns = adjusted close-to-close returns.

### S1 — Plain momentum (reference)

```
S1 = PRET = P(last session of m−1) / P(last session of m−12) − 1
```

This is the Jegadeesh-Titman 11-month return skipping the most recent month (the Fama-French "prior 2–12").

### S2 — Information discreteness (Da, Gurun & Warachka 2014, "Frog in the Pan", RFS 27(7))

```
ID = sgn(PRET) × (%neg − %pos)
```

- **PRET** = S1, i.e. the twelve-month formation period skipping the most recent month.
- **%pos / %neg** = the number of positive / negative daily returns divided by the number of valid trading-day returns in the formation window.
- **Window:** from the first session after the last session of m−12 through the last session of m−1.
- **Zero returns** count in the denominator only.
- **sgn(0) = 0.**
- **At least 200 valid daily returns** are required.

**Sequential sort, as in the paper.**
1. Sort on PRET into **quintiles**: equal-count, by ordinal rank, ties broken by security id.
2. Within each quintile, order by continuity in the direction of PRET:

   ```
   key = −sgn(PRET) × ID      (low ID = continuous information)
   S2  = quintile index (1..5) + within-quintile percentile of key in (0, 1]
   ```

**How the ordering reads in the tails:**
- In the winner quintiles, **continuous winners (low ID) rank highest.**
- In the loser quintiles, **continuous losers (low ID) rank lowest.**
- This matches the paper's prediction that continuous information produces stronger, more persistent continuation.

### S3 — Trend factor (Han, Zhou & Zhu 2016, "A trend factor", JFE 122(2))

**Moving-average signals at month-end t:**

```
A_L,t = (mean of the last L split-adjusted closes ending at the decision close) / (the decision close)
L ∈ {3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000}
```

- If fewer than L closes exist, the mean uses those available, with at least 1 (the Chen-Zimmermann convention; the paper is silent).

**Monthly regressions.**
- For each month s from 2010-02, once month s+1 has ended, run a cross-sectional OLS **with an intercept**:
  - the dependent variable is each stock's month-(s+1) total return (close of s → close of s+1; a delisted stock's proceeds at its last real close);
  - the regressors are A_L,s;
  - the sample is the H019 eligible universe at s.
- Rank-deficient or under-identified regressions give no coefficients.

**Expected coefficients.**
- E[β_L]_t = the mean of β_L,s over the **12 most recent completed regressions**, s = t−12 … t−1.
- The last of these uses month-t returns, known at the decision close.
- If any of the 12 is missing, S3 is undefined.

**Signal:**

```
S3_t = Σ_L E[β_L]_t × A_L,t
```

### Point-in-time guarantees

- **S1 and S2** use closes and returns up to the end of m−1.
- **S3** uses closes up to the decision close. Its coefficients come only from returns realised by the decision close. There are no full-sample coefficients and no future cross-sections (`qr_xs.TrendFactor` refuses look-ahead).
- **The universe** uses point-in-time market cap, price and ADV.

### Common sample

- On each date, a stock counts only if it is eligible **and** S1, ID and S3 are all defined.
- Every statistic of that date uses exactly this set.

## 3. Response

| Item | Definition |
|---|---|
| **Primary** | Total return from the **open of the first session after d** to the **close of the last session of month m+1**, minus the equal-weighted mean of the same quantity over the date's common sample (**cross-sectionally demeaned**) |
| **Diagnostic** | The same to the close of month m+3 (3-month) |
| Delisted or stale stocks (D059 / D062) | Proceeds at the last real close, 0 thereafter; kept in the sample |

## 4. Statistics per decision date

| Statistic | Definition |
|---|---|
| Rank IC (S1, S2, S3) | Spearman correlation (average ranks) between the signal and the demeaned response |
| Deciles | 10 equal-count buckets by signal (ordinal rank, ties by security id); the mean demeaned response per decile |
| **Incremental (S2, S3)** | Mean over the five S1 (PRET) quintiles of the within-quintile **partial Spearman correlation** between the candidate component (S2: key; S3: S3) and the response, controlling for S1: (ρ_yc − ρ_ym ρ_cm) / √((1 − ρ_ym²)(1 − ρ_cm²)) |

## 5. Time-series inference

**Primary:**
- For each series, the mean over the 82 dates.
- Newey-West (Bartlett) HAC standard error, **lag 2** (non-overlapping returns).
- t = mean / SE.
- Annualised decile figures = the mean monthly demeaned decile return × 12.

**3-month diagnostic:** NW lag 6, figures × 4.

**Halves:** the first and second 41 dates (2011-02 → 2014-06; 2014-07 → 2017-11).

**Blocks:** calendar 2011–12, 2013–14, 2015–16, 2017.

## 6. Null and the family critical value

**Identity-tethered within-date permutation** (`qr_xs.Tether`).
- In null world r (seed r), each stock receives the **joint** vector (S1, ID, key, S2, S3) of a random partner stock.
- It keeps that partner while both remain in the common sample. Stocks that lose a partner, or enter, are re-matched at random among that date's unmatched stocks.
- **Preserved:**
  - real dates, real returns and their distribution;
  - common market and sector shocks;
  - universe composition and size;
  - each date's cross-sectional signal distribution;
  - signal persistence;
  - the joint distribution of the signals.
- **Broken:** only the link between a stock's signals and its own next-month return.
- **The entire procedure of §§4–7 runs on every null world.**

**Family statistic:** F = max(t_S1, t_S2, t_S3, t_inc,S2, t_inc,S3).

**Critical value:**
- **c = the 50th largest F over R = 5,000 null worlds** (seeds 1–5,000; α = 1%).
- The null runs first. c and the per-world null table are committed and SHA-256-pinned **before** the real run.
- **Full-rule null rate:** the share of null worlds in which the complete rule (§7) promotes S2 or S3 is reported. It is ≤ 1% by construction.

**α = 1%** is a **conservative pre-registered research threshold.** It reflects the project's prior experimentation with momentum-type signals on 2010–2017: H002, H003, H008 and H018's momentum and trend families. It is not a formal correction derived from a count of earlier tests.

## 7. Promotion rule (all conditions, per signal)

| Code | Condition |
|---|---|
| P1 Economic | Top-decile annualised mean demeaned excess ≥ **3.0% a year** **and** D10 − D1 > 0 |
| P2 Monotonic | Spearman(decile index 1..10, mean decile excess) ≥ **0.70** **and** mean(D6..D10) > mean(D1..D5) |
| P3 Statistical | t (rank IC) > c |
| P4 Stable | Mean IC > 0 in **both** halves **and** no block contributes more than **50%** of the total IC sum (and the sum is > 0) |
| P5 Exceptional | Through c (§6); the full-rule null rate is reported |
| P6 Incremental (S2, S3 only) | t_inc > c |

**Outcomes:**
- **candidate:** S2 and / or S3 pass. If both pass, the larger t_inc is selected.
- **replication_only:** only S1 passes.
- **none:** nothing passes.

**The 3-month diagnostic can never promote, rescue or veto anything.**

## 8. Diagnostics (reported, never gated, never used to change a rule)

1. **3-month horizon:** the same statistics, NW lag 6.
2. **Per-year table:** mean IC, t, top-decile excess, sign.
3. **Sector-neutral IC:** within Fama-French 12 sectors, from point-in-time SEC SIC (`qr_industry`); "unclassified" is its own group; sectors with at least 20 stocks; count-weighted.
4. **Size:** IC within the larger and the smaller half by point-in-time market cap; each signal's correlation with log market cap.
5. **Signal characteristics:** mean cross-sectional Spearman correlations among S1, S2 and S3, and of each with the trailing 1-month return.
6. **Incremental detail:** the partial IC per S1 quintile (Q5 = long-only relevant).
7. **S3 decomposition:** the IC and incremental IC of the three components Σ E[β_L] A_L over L ≤ 20, 50 ≤ L ≤ 200 and L ≥ 400 (short reversal / intermediate trend / long reversal horizons). Also the mean E[β_L] path.
8. **Top decile vs SPY:** total return over the same windows, annualised.
9. **Turnover:** month-to-month rank autocorrelation; top-decile and top-quintile retention.
10. **Realised power:** realised IC volatility, effective sample size, and the IC detectable with 50% / 80% power at c.

## 9. Pre-registered interpretation

**none:**
- **"No technical stock-selection signal large enough to satisfy the project's detection and economic-significance requirements was found."** Not "no 1–3% technical edge exists": the test cannot detect edges that small.
- Stop technical stock-selection research in this universe. No RSI / MACD / ADX / Bollinger / volume / breakout follow-ups. A future technical direction needs a genuinely different hypothesis and a new owner decision.

**replication_only:**
- Momentum is reproduced; no new signal is found.
- No automatic portfolio. The owner decides.

**candidate:**
- **Only** "credible cross-sectional predictive information exists on 2011–2017 under the frozen test".
- **Not** a production strategy, SPY-beating, portfolio viability or 2018–2021 validation.
- Next: design **one** portfolio implementation around the selected signal (a separate pre-registration and approval). 2018–2021 stays untouched until that portfolio is frozen. The Holdout stays locked.

## 10. Runs (each only after explicit owner approval; configs carry `owner_approval_required`)

| Run | Purpose | Publishes |
|---|---|---|
| E985-01 (X985) | Plumbing and fidelity canary: seeded random persistent placebo signals (IC ≈ 0); a planted signal (response + noise, known IC); a second, slow, independent computation of S1 / ID / A_L / regressions for a fixed sample of stocks and dates compared inside QuantConnect (digest and maximum difference only); trend-factor look-ahead guard; universe counts; every horizon ends ≤ 2017-12-29; runtime, memory, output | Canary statistics only; no real-signal statistic |
| E020-01..05 (S020 = byte copy of X985) | Null worlds 1–5,000 (1,000 per run) | Null F and per-world statistics only, never real-world statistics |
| — | Commit and pin c + the null table | — |
| E020-06 (S020) | Real evaluation, once | Real statistics and diagnostics |
| — | H019 checkpoint (P4-CP4); STOP | — |
