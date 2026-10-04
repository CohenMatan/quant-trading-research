# Phase 4 — Cross-Sectional Technical Signal Validation: Pre-Registration (H019) — DRAFT

**Status: DRAFT, proposed at P4-CP3 (2026-10-04). Not frozen. Not run.**

**Freezing:**
- After the owner approves it, and **before** any real signal or forward return is computed, this file is frozen and pinned:
  - its SHA-256 goes into `qresearch.p4xs.SPEC_SHA256`, tested by `tests/test_p4xs_spec.py`;
  - the constants of `src/qresearch/lean/qr_xs.py` are pinned by the same test.
- **Nothing below may change after any real-data statistic is seen.**
- A genuine code defect found by a canary is a technical repeat: fix it, re-run the whole affected stage, record it. It is never a reason to change a rule.

**Hypothesis H019 is this procedure:**

> At least one of two pre-registered refinements of momentum — smooth (frog-in-the-pan) momentum, or a multi-horizon trend score — contains cross-sectional information about the next three months' relative returns of US stocks ≥ $2B (2010–2017) that is
> - economically meaningful;
> - monotonic;
> - stable;
> - exceptional against a structure-preserving null;
> - **additional to plain 12-1 momentum.**

**Plain momentum is the reference.** Its result is reported as replication of a known effect, never as a discovery.

---

## 1. Data, universe and period

| Item | Value |
|---|---|
| Engine and data | QuantConnect Cloud LEAN, build 18131 (pinned per experiment); data infrastructure v1 (`research/phase2/data_freeze_v1.json`), unchanged |
| Universe (each decision close) | Harness eligibility of data v1: US common stock, point-in-time market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M, SEC correction layer on (`universe.sec_corrections: true`). Financials included (no fundamentals used). No present-day lists |
| Prices | Daily bars as known at each close, `SCALED_RAW` (split- and dividend-adjusted as of that close; rescaled on later splits and dividends): the X984 / S018 convention |
| History-only warm-up | Harness warm-up from 2009-07-01, plus a 280-bar history request when a stock enters the subscription set (the X984 method). No statistic exists before the first decision |
| Decision dates | The close of the last exchange session of each calendar month |
| Primary decisions (H = 3) | 2010-02 → 2017-09: **92 decision dates**. The last 3-month return ends at the 2017-12-29 close |
| Diagnostic decisions | H = 1: 2010-02 → 2017-11 (94). H = 6: 2010-02 → 2017-06 (89) |
| Hard limits in code | Every run ends on or before 2017-12-31 (`experiment.validate` and the algorithm both refuse otherwise). No 2018-01-01 → 2021-12-31 data. Holdout 2022-01-01 → 2026-08-31 locked (harness lock) |

**Why the first decision is 2010-02-26.** Returns then start on 2010-03-01, the start of the Phase 3 search window. That start was set by universe and ADV20 availability under data v1, not by performance.

## 2. Signals (exact)

For a decision at the close of month m (session d), with adjusted closes P:

| Signal | Definition |
|---|---|
| **S1 MOM** (reference) | P(last session of m−1) / P(last session of m−12) − 1 |
| **NUD** (S2's component) | (number of up days − number of down days) / number of valid daily returns. Window: from the first session after the last session of m−12, through the last session of m−1. A zero return counts only in the denominator. At least 200 valid returns. NUD = −sgn(PRET) × ID of Da, Gurun & Warachka (2014) |
| **S2 SMOOTH** | Sequential sort. MOM quintile index q ∈ {1..5} (equal-count, by ordinal rank) plus the within-quintile percentile of NUD in (0, 1]. Every stock in a higher MOM quintile ranks above every stock in a lower one; within a quintile, a higher NUD ranks higher |
| **S3 TREND** | (1/3) Σ ln(P_d / SMA_L,d) over L ∈ {50, 100, 200} sessions. SMA_L,d = the mean of the last L adjusted closes ending at d. Needs 200 valid closes. No skip month (Han-Zhou-Zhu normalise by the decision close) |

**Common sample.**
- A stock enters the date's cross-section only if it is eligible **and** S1, NUD and S3 can all be computed.
- Every statistic of that date uses exactly this set.

**Ties.**
- Average ranks are used for correlations.
- Ordinal ranks, with ties broken by security id order, are used for equal-count buckets.

## 3. Response

- **Forward total return.**
  - Start: the open of the first session after d.
  - End: the close of the last session of month m + H.
  - Adjusted for splits and dividends.
- **Delisted or stale stocks** (harness D059 / D062 rules). The proceeds are taken at the last real close, and the return is 0 after that. The stock is kept in the cross-section (no survivorship).
- **Primary response:** the forward return minus the equal-weighted mean forward return of the same date's common sample (**cross-sectionally demeaned**).

## 4. Statistics per decision date

| Statistic | Definition |
|---|---|
| Rank IC (S1, S2, S3) | Spearman correlation between the signal and the demeaned response over the common sample |
| Deciles | 10 equal-count buckets by signal (ordinal rank); the mean demeaned response per decile |
| Incremental (S2, S3) | Mean over the five MOM quintiles of the within-quintile partial Spearman correlation between the candidate's own component (NUD for S2, S3 for S3) and the response, controlling for MOM: (ρ_yc − ρ_ym ρ_cm) / √((1 − ρ_ym²)(1 − ρ_cm²)) |

## 5. Time-series inference

- For each series (three ICs and two incremental statistics):
  - the time-series mean over the 92 dates;
  - a Newey-West (Bartlett) HAC standard error with a **fixed lag of 6 months**;
  - t = mean / SE.
- Annualised decile figures = the mean 3-month demeaned decile return × 4.
- **Years and subperiods** are defined by decision date:
  - 2010 (11 dates), 2011–2016 (12 each), 2017 (9);
  - subperiods 2010–2013 (47 dates) and 2014–2017 (45);
  - two-year blocks 2010–11, 2012–13, 2014–15, 2016–17.

## 6. Null (structure-preserving) and the critical value

**Identity-tethered within-date permutation** (`qr_xs.Tether`).
- In null world r (seed r), each receiving stock gets the **joint** signals (S1, NUD, S2, S3) of a random partner stock.
- It keeps that partner while both remain in the common sample. Stocks that lose a partner, or enter, are re-matched at random among that date's unmatched stocks.
- Each date's null signal vector is an exact permutation of the real one over the same stocks. So real returns, dates, universe composition, cross-sectional dependence, signal persistence and the correlation between the signals are all preserved.
- The only thing broken is the link between a stock's signals and its own future return.

**The entire procedure of §§4–5 runs on every null world.**

**Family statistic:** F = max(t_S1, t_S2, t_S3, t_inc,S2, t_inc,S3).

**Critical value:**
- **c = the 50th largest F over R = 5,000 null worlds** (seeds 1–5,000; family-wise level α = 1%).
- The null runs first. c and the per-world null table are committed and SHA-256-pinned **before** the real evaluation run, exactly as Phase 3's τ was.
- **Full-rule check:** the share of null worlds in which the complete promotion rule (§7) promotes any of S2 / S3 is reported. It is ≤ 1% by construction.

**Why α = 1%.**
- It is 0.05 / (1 + 4).
- The 4 prior looks at the past-return ranking family on 2010–2017 in this project are H002, H003, H008 and H018's momentum family.
- One Bonferroni share is given to each look, including this one.

## 7. Promotion rule (all conditions, per signal)

| Code | Condition |
|---|---|
| P1 Economic | Top-decile mean demeaned excess ≥ **3.0% a year** (annualised) **and** D10 − D1 > 0 |
| P2 Monotonic | Spearman(decile index 1..10, mean decile excess) ≥ **0.70** **and** mean(D6..D10) > mean(D1..D5) |
| P3 Statistical | t (rank IC) > c |
| P4 Stable | Mean IC > 0 in **both** subperiods (2010–13, 2014–17) **and** no two-year block contributes more than **50%** of the total IC sum (and that sum is > 0) |
| P5 Exceptional vs null | Satisfied through c (§6); the full-rule null rate is reported |
| P6 Incremental (S2, S3 only) | t_inc > c |

**Outcomes:**
- **candidate:** S2 and / or S3 pass. If both pass, the one with the larger t_inc is selected.
- **replication_only:** only S1 passes. Momentum is reproduced; no new signal.
- **none:** nothing passes.

## 8. Diagnostics (reported, never gated, never used to change a rule)

1. **Horizons:** H = 1 and H = 6 months (same statistics; NW lags 2 and 12).
2. **Per-year table:** mean IC, IC t-statistic, top-decile excess, and sign for each year 2010–2017.
3. **Sector-neutral IC:** Spearman within Fama-French 12 sectors, mapped from point-in-time SEC SIC (`qr_industry`, data v1; stocks without an SIC form an "unclassified" group). It is averaged across sectors with at least 20 stocks, weighted by count.
4. **Size:**
   - IC within the larger and the smaller half by point-in-time market cap (median split per date);
   - the mean Spearman correlation of each signal with log market cap.
5. **Signal characteristics:** mean cross-sectional Spearman correlations S1–S2, S1–S3, S2–S3, NUD–S1, and each signal with its own trailing 1-month return.
6. **Incremental detail:** the within-quintile partial IC per MOM quintile (Q5 is the long-only-relevant one).
7. **Top decile vs SPY:** the top decile's mean 3-month return minus SPY's total return over the same window, annualised.
8. **Turnover:**
   - month-to-month rank autocorrelation of each signal (stocks present on both dates);
   - top-decile and top-quintile retention (the share of this month's top names still in the top next month).
9. **Realised power:** the realised IC volatility, the realised effective sample size, and the IC that would have been detectable with 50% / 80% power at c.

## 9. Pre-registered consequences

- **none:** stop technical stock-selection research in this universe.
  - No RSI / MACD / ADX / Bollinger / volume / breakout follow-ups.
  - A future technical direction would need a genuinely different hypothesis and a new owner decision.
- **replication_only:**
  - No automatic portfolio. A plain-momentum portfolio would overlap H002 and P4-CP1's AR1.
  - The owner decides whether anything follows.
- **candidate:** design **one** portfolio implementation around the selected signal. Conceptually: monthly ranking, weekly trend management, next-open execution. It is a separate pre-registration with its own approval.
  - 2018–2021 stays untouched until that portfolio is frozen.
  - The Holdout stays locked.

## 10. Runs (each only after explicit owner approval)

| Run | Purpose | Publishes |
|---|---|---|
| E985-01 (X985) | Plumbing canary: placebo signals (seeded random, persistent) and a planted signal (the forward return + noise, known IC); universe counts, date alignment, horizon end ≤ 2017-12-29, runtime and output size | Canary statistics only |
| E020-01..05 (S020) | Null worlds, 1,000 per run (seeds 1–1,000, …, 4,001–5,000); real signals permuted | Null F and per-world statistics only, **never** the real-world statistics |
| — | Commit c and the null table (SHA-256 pin) | — |
| E020-06 (S020) | Real evaluation: §§4–8 for the real world | Real statistics |

S020 is a byte copy of X985 once the canary passes.
