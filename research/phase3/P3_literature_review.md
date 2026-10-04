# Phase 3 literature review: systematic technical-rule search and data-snooping control (P3-CP1, 2026-10-04)

- **Purpose:** choose the search architecture, the multiple-testing controls and the indicator families for a systematic multi-indicator technical strategy search, **before** any technical-rule return is computed on project data.
- **Citations:** from memory, with year and venue. **Verify before quoting any magnitude.** Where unsure I state the direction only.
- **Not used:**
  - no project technical-rule result (none exists);
  - no Holdout-period knowledge;
  - no H017 result (owner instruction 26).

## 1. Technical trading rules and data snooping

| Source | Finding | Design consequence |
|---|---|---|
| Brock, Lakonishok & LeBaron (1992), JF | Moving-average and trading-range-break rules appeared to predict Dow Jones returns 1897–1986 | The classic indicator families (MA, breakout) |
| Sullivan, Timmermann & White (1999), JF, "Data-snooping, technical trading rule performance, and the bootstrap" | Searched ≈ 7,800 rules on the DJIA with White's Reality Check. The best rule looked significant in the original sample, but its performance did **not** persist in the later out-of-sample decade | A search over thousands of rules **must** be judged against the distribution of the best rule under no edge, and needs a genuine out-of-sample test |
| White (2000), Econometrica, "A reality check for data snooping" | Bootstrap test of whether the best of many models beats a benchmark, accounting for the search | Search-level null |
| Hansen (2005), JBES, "A test for superior predictive ability" | Studentised, less conservative than White's test when poor models are included | Secondary search-level test (SPA) |
| Romano & Wolf (2005), Econometrica (StepM) | Step-down control of the family-wise error, identifies **which** models beat the benchmark | Optional; not needed if only one candidate is promoted |
| Aronson (2006), *Evidence-Based Technical Analysis* (book) | Applied White's Reality Check to several thousand rules on the S&P 500: no rule significant after the data-mining adjustment | Prior: low |
| Hsu & Kuan (2005), J. Financial Econometrics; Park & Irwin (2007), J. Economic Surveys (review) | Profitability of simple technical rules in mature US markets largely disappears after the 1980s and after costs; some evidence remains in less efficient markets | Prior for large-cap US equities after 2010: small edges at best |
| Bajgrowicz & Scaillet (2012), JFE, "Technical trading revisited: false discoveries, persistence tests, and transaction costs" | With false-discovery control and realistic costs, no technical rule shows persistent out-of-sample outperformance on the DJIA in recent decades | Costs and persistence are the binding constraints |
| Harvey, Liu & Zhu (2016), RFS | After hundreds of tested factors, a t-statistic above ≈ 3 is needed | A single "significant" backtest after a large search is not evidence |
| Novy-Marx (2016, working paper / later published), "Testing strategies based on multiple signals" | Selecting the best k of n signals and **combining** them inflates backtested performance far beyond single-signal data mining. Standard critical values are badly wrong for multi-signal composites | **Answer to question A:** stacking 7–8 selected indicators is the worst case for data mining. Limit the number of conditions per strategy and fix the combination grammar in advance |

## 2. Overfitting diagnostics and validation design

| Source | Finding | Design consequence |
|---|---|---|
| Bailey, Borwein, López de Prado & Zhu (2014 / 2017), "The probability of backtest overfitting" (J. Computational Finance) | Combinatorially symmetric cross-validation (CSCV) estimates how often the in-sample best configuration ranks below the median out of sample | PBO as a **diagnostic** of the search |
| Bailey & López de Prado (2014), J. Portfolio Management, "The deflated Sharpe ratio" | Sharpe hurdle rises with the number of trials, skewness and kurtosis | Diagnostic only (Amendment 3 already makes DSR a diagnostic) |
| López de Prado (2018), *Advances in Financial Machine Learning* (book) | Purged k-fold, embargo, combinatorial purged CV for overlapping labels | Overlapping holding periods need purging / embargo of at least the maximum holding period |
| Pardo (2008), *The Evaluation and Optimization of Trading Strategies* (practitioner) | Walk-forward analysis; prefer broad, stable parameter regions ("plateaus") to isolated optima | Plateau principle; procedure-level walk-forward |
| Breiman, Friedman, Olshen & Stone (1984); Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning* | The "one-standard-error rule": choose the simplest model whose error is within one standard error of the best | **Complexity rule without arbitrary weights** |
| Nyholt (2004), AJHG; Li & Ji (2005), Heredity | The effective number of independent tests from the eigenvalues of the correlation matrix | Reporting the effective trial count of the correlated configuration set |
| Politis & Romano (1994), JASA | Stationary bootstrap | Already frozen in Amendment 3 (W2); reused for SE in the 1-SE rule and SPA |

## 3. Evidence on the indicator families (large-cap US equities)

| Family | Representative evidence | Horizon / note |
|---|---|---|
| Cross-sectional momentum | Jegadeesh & Titman (1993), JF; Asness, Moskowitz & Pedersen (2013), JF | 3–12 months, skip the most recent month; weaker and crash-prone in recent decades |
| Time-series momentum / trend | Moskowitz, Ooi & Pedersen (2012), JFE (futures); Faber (2007), JWM (10-month SMA timing); Zhu & Zhou (2009), JFE | Monthly-to-annual horizons; mostly an asset-class timing result |
| 52-week high / breakout proximity | George & Hwang (2004), JF | Proximity to the 52-week high predicts returns, partly subsuming momentum |
| Moving averages in the cross-section | Han, Yang & Zhou (2013), JFQA, "A new anomaly: the cross-sectional profitability of technical analysis" | MA timing works mainly in high-volatility (small, illiquid) portfolios: weaker in a ≥ $2B universe |
| Short-term reversal / oscillators (RSI(2), Bollinger) | Jegadeesh (1990), JF; Lehmann (1990), QJE; practitioner RSI(2) rules | Weekly-to-monthly horizon: **excluded by our cost model** (P3_cost_feasibility: holding < ≈ 45 sessions breaks R4 at $100K) |
| Volume | Gervais, Kaniel & Mingelgrin (2001), JF; Lee & Swaminathan (2000), JF | Volume interacts with momentum; secondary |
| Low volatility | Ang, Hodrick, Xing & Zhang (2006), JF; Frazzini & Pedersen (2014), JFE | Useful as a risk filter. Note: Phase 1 H005 (low-volatility) failed Validation, so this family has been tested on this data before |
| Technical pattern recognition | Lo, Mamaysky & Wang (2000), JF | Some patterns carry information; effect sizes small |

## 4. Design choices that follow [ours]

1. **A constrained grammar** (one primary setup, at most one confirmation from a different information family, at most one risk filter) instead of free combinations (§1 Novy-Marx; Sullivan et al.).
2. **Coarse, literature-anchored grids** (3–5 values per parameter).
3. **The search is judged against a search-level null** of the *entire* procedure, plateau rule included (White; Hansen; Sullivan et al.). This is implemented as a permutation null that preserves the configurations' correlation structure.
4. **Plateau, not peak** (Pardo), formalised as a neighbourhood lower-quantile score.
5. **Simplicity by the one-standard-error rule** (Breiman et al.), not by a weighted penalty.
6. **Procedure-level walk-forward** plus one untouched internal out-of-sample period (Sullivan et al.: the decisive test is persistence in later data).
7. **Holding periods ≥ about 63 sessions**, a consequence of the frozen cost model, not of performance.
8. **Prior expectation (honest):** the literature points to small or no robust edges for technical stock selection in liquid US large caps after costs since 2000. The architecture is designed to make a fair test **and** to stop a lucky configuration from passing. It is not designed to find something.
