# C02 prerequisite checkpoint, addendum: signal equivalence, PBO definition, and an H008 defect

| Field | Value |
|---|---|
| Date | 2026-09-29 |
| Status | **STOP. Three owner decisions needed** (§4) before any of the 18 C02 strategy runs. |
| Requested by | Owner, 2026-09-29: (1) a signal-equivalence check; (2) the PBO definition with three variations |
| C02 strategy backtests run | **None.** |
| New runs | **E961-01**, a verification canary with no orders; not a trial |

## 1. Summary

1. **Signal equivalence.** The harness adjusts past prices for dividends slightly differently from QuantConnect (up to 0.1% per dividend, up to 0.3% accumulated). This **does not change the decisions of H006, H007, H009, H010 or H011** in any meaningful way.
   - Across about 203,000 stock-days (every 10th session of 2010–2017, whole universe) and all 96 monthly ranking dates, entry signals and top-10 selections were identical.
   - The only exceptions are a handful of borderline cases in both directions (§2).
2. **H008 defect (new, serious).** The check exposed that **H008's score, as specified and implemented, is always zero.**
   - The rule regresses a stock's returns on SPY over the 12-1 month window, then sums the residuals over *the same* window. Least-squares residuals with an intercept always sum to exactly zero, so every score is floating-point noise (about 10⁻¹⁶) and the ranking is random.
   - Nothing has run, so nothing is contaminated. But the approved H008 rule must be corrected, and that is your decision (§3, options).
3. **PBO.** With three variations, "PBO ≤ 0.30" does not measure overfitting. It measures whether one variation happens to dominate its siblings.
   - With three equally good variations it averages 0.66, and passes only 13–14% of the time whatever the edge.
   - Proposed (D073): keep the threshold, the method and the median rule, but apply the hard gate to the **whole cycle of 18 candidates**. The 3-variation figure stays in reports as a diagnostic.
   - Full analysis: `research/cycles/C02_pbo_definition.md`.

## 2. Signal-equivalence check (E961-01)

**Method.**

- The canary keeps two copies of every price history for every eligible stock:
  - **H**, exactly what the strategies read;
  - **R**, a reference adjusted with QuantConnect's *exact* factor at every dividend and split (21,986 corporate actions).
- The reference was proven equal to fresh QuantConnect history:
  - 1,520,000 daily values: largest difference 0.00003%;
  - 16,944 month-end values: largest difference 10⁻¹³ %.
- The difference between H and R is what the harness actually introduces:
  - up to 0.16% on daily prices and 0.28% on month-end prices;
  - at most 0.099% at any single event.
- The **unchanged** C02 signal code runs on both copies. The code files are byte-identical copies of the strategies' own signal files, and a test enforces that.
- It uses each strategy's own filters and ranking rules and the pre-declared variations.
- Coverage:
  - event strategies: every 10th session of 2010–2017 (201 days × about 1,000 stocks = 203,142 stock-days; 35% of them had identical H and R inputs);
  - monthly strategies: all 96 ranking dates each.

**Results** ("only H" = a signal on the harness input but not the reference; "only R" = the reverse):

| Strategy / decision | Signals (H / R) | Only H | Only R | Days the top-10 list differs | Names bought under one input only |
|---|---|---|---|---|---|
| H006 v1.0 breakout | 2,899 / 2,899 | 0 | 0 | 1 of 201 (order only) | 0 |
| H006 v1.1 (52-week) | 2,037 / 2,037 | 0 | 0 | 1 of 201 (order only) | 0 |
| H006 v1.2 (no volume) | 11,974 / 11,973 | 1 | 0 | 1 of 201 (order only) | 0 |
| H007 v1.0 / v1.1 / v1.2 | 567 / 31 / 627 (identical) | 0 | 0 | 0 | 0 |
| H009 v1.0–v1.1 / v1.2 | 3,444 / 1,783 (identical) | 0 | 0 | 0 | 0 |
| H010 v1.0–v1.1 / v1.2 | 319 / 588 (identical) | 0 | 0 | 0 | 0 |
| H011 v1.0 / v1.1 (monthly rank) | 84,976 / 74,491 scored | 0 | 0 | 0 of 96 | 0 |
| H011 v1.2 (with SMA200 filter) | 61,309 / 61,311 scored | 1 | 3 | 0 of 96 | 0 |
| Exit: H006 chandelier stop | 37,017 / 37,015 of 203,142 | 3 | 1 | — | — |
| Exit: H007 close < SMA20 | 81,222 / 81,225 | 2 | 5 | — | — |
| Exit: H010 gap filled | 64,865 / 64,861 | 5 | 1 | — | — |
| H008 (all variations) | see §3: the score is defective | | | | |

**Reading.**

- **Entry selections:** zero differences in which stocks would be bought, for every event strategy and every H011 month.
- **Order of candidates:** it changed on 1 of 201 days for H006, among the same names, when several breakouts were nearly equal in size.
- **Borderline cases:** 21 decisions out of about 2.9 million evaluated (10 entry variants and 3 exit rules × 203,142 stock-days, plus 3 × 96,951 H011 scores; about 0.0007%), all stocks sitting right at a threshold on the day.
- **Why this cannot create a systematic bias:**
  - The flips go both ways: 11 "only H" against 10 "only R".
  - A difference in the dividend factor rescales *all* earlier prices of that stock by the same tiny amount. Price levels, averages, ranges and ATR move together by at most 0.1%. The only thing that changes is the one-day return across the ex-dividend date, by at most 0.1%.
  - No C02 rule depends on that single return in a consistent direction. A decision can only change when a stock is already within about 0.1% of a threshold, and whether it lands on one side or the other is effectively random.
- **Scores near zero:** the "relative score difference" column in the raw data can look large (e.g. H011 up to 419%). That happens only where a score is almost exactly zero, where a relative figure is meaningless. It never reached a top-10 position.

**Conclusion.** For H006, H007, H009, H010 and H011, the harness inputs give the same decisions as QuantConnect-exact inputs, except for a negligible, unbiased number of borderline cases. No fix is needed. H008 must be re-checked after its correction (§3).

## 3. H008 defect: the score is always zero

- **What.** H008.md says: "regress daily returns on SPY daily returns over the window T−252 … T−22; score = sum of the residuals ÷ the residual standard deviation, following Blitz et al." S008 implements exactly that.
  - A regression with an intercept makes the residuals *over the estimation window* sum to exactly zero. That is a mathematical identity.
  - Demonstration: for simulated stocks with true yearly alpha from −50% to +50%, S008 returns scores between −10⁻¹⁵ and +10⁻¹⁵.
  - The canary confirms it on real data: H008's top-10 differs between two near-identical inputs on 94 of 96 dates, with names jumping up to 1,200 places, because the ranking is noise.
- **Why it was not caught before.** The unit test compared S008 with an independent least-squares calculation. Both gave zero, so the test passed. That test is being corrected so that it requires a non-degenerate score.
- **Why it matters.** Run as written, H008 would have been a random stock picker. Its three trials would count in N (D069) and waste 3 of 18 runs. A pass would have been luck, and a fail would have wrongly "rejected" residual momentum.
- **What Blitz, Huij & Martens (2011) actually do.** They estimate the market (factor) exposure over a **36-month** window, then sum the residuals over only the **12-1 month** part and scale by those residuals' standard deviation. The residuals over the shorter window do not sum to zero. H008's rule shortened the estimation window to the formation window, and that shortening caused the defect.

**Options (no C02 data seen; each is decided before any run):**

| Option | Rule | Data need | Assessment |
|---|---|---|---|
| **A (recommended)** | As in Blitz et al.: estimate alpha and beta on SPY over the **756 sessions (36 months) ending T−1**. Score = sum of residuals over T−252 … T−22 (v1.1: T−126 … T−22) ÷ their standard deviation (v1.2: not divided). Needs 36 months of history, with at least 600 valid days. | About 760 daily bars per stock. At the 2010 start this reads 2007–2009 prices as **warm-up only**, the same principle you approved for H011. | Faithful to the paper the hypothesis cites; variations unchanged. Stocks with less than 3 years of history cannot be scored (disclosed bias). |
| B | Keep only the 12-1 window. Score = sum of the *beta-adjusted* returns (r − β × SPY return, i.e. alpha is kept) ÷ residual standard deviation. | Unchanged (400 bars) | Simpler, no extra history. Closer to Grundy & Martin's "stock-specific return" than to Blitz et al. |
| C | Drop H008 from C02 | — | C02 becomes 15 selection trials (DSR N 34, cap 47 backtests). Loses the only market-adjusted (residual) ranking idea. *(Terminology corrected 2026-09-29: H008's score is market-adjusted; its long-only portfolio is not market-neutral.)* |

After the chosen fix, and before any run, I would:

- correct the unit test against a reference with a known, non-zero answer;
- re-run the equivalence check for H008 alone (verification, not a trial);
- report both.

## 4. Decisions needed

1. **PBO (D073, proposed):** approve the cycle-level PBO ≤ 0.30 as the hard Validation gate for C02 candidates, with the 3-variation PBO reported as a diagnostic. Or keep the per-hypothesis gate knowingly (§4 of the PBO note).
2. **H008:** choose option A (recommended), B or C. For A, confirm that 2007–2009 prices may be read as warm-up only, as for H011.
3. **After 1 and 2:** I apply the H008 fix, re-verify it, and report once more before the 18 runs. Or, if you prefer, approval of 1 and 2 also authorises the runs once the H008 re-check passes; I will do whichever you say.

## 5. Record

- **Run E961-01:** kind infrastructure, AUDIT split with IS dates 2010-01-04 → 2017-12-29, no orders. Report: `experiments/E961-01/`.
- **Totals:** 11 hypotheses; 11 research strategies; D069 counts unchanged (19 selection candidates, 15 robustness, 1 Validation). Verification runs rise to 42 with E961-01.
- **Tests:** full suite passes (§ commit).
