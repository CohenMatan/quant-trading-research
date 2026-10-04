# P4-CP4 — H019 Cross-Sectional Technical Signal Validation Results (STOP)

- **Date:** 2026-10-04.
- **Owner authorisation:** "H019 — Authorise Final Cross-Sectional Signal Validation Run" (2026-10-04, D145; summary `docs/owner/2026-10-04_phase4_h019_authorisation.md`).
- **Specification:** `research/phase4/P4_xs_spec.md` v2, SHA-256 `15fb0451…` (unchanged, pinned in `qresearch.p4xs`).
- **Executed in the exact authorised order:** plumbing / fidelity canary → 5,000 null worlds → family threshold → commit, hash and pin → clean tree → ONE real evaluation → this checkpoint → **STOP**.

## Final verdict (item 36)

# **NO SIGNAL QUALIFIED FOR PORTFOLIO RESEARCH**

**No technical stock-selection signal large enough to satisfy the project's detection and economic-significance requirements was found.**

| | S1 plain momentum (reference) | S2 smooth momentum (ID) | S3 Han-Zhou-Zhu trend factor |
|---|---|---|---|
| Top-decile excess vs the cross-sectional average (annualised) | **−2.18%** | **−1.20%** | **−2.85%** |
| Top − bottom decile (annualised) | +1.47% | +3.56% | −1.33% |
| Mean rank IC (t, Newey-West lag 2) | 0.0038 (0.22) | 0.0058 (0.34) | 0.0011 (0.12) |
| Incremental over S1: mean within-momentum-quintile partial IC (t) | — | 0.0120 (1.31) | 0.0007 (0.09) |
| Frozen threshold c | 2.8715 | 2.8715 | 2.8715 |
| Promotion | **FAIL** (all four criteria) | **FAIL** (all five) | **FAIL** (all five) |

- **Real family statistic F = 1.31 against c = 2.87.** Family empirical p = 0.231; F sits at the 76.9th percentile of the 5,000 no-information worlds.
- **Every signal fails every criterion:** the economic floor, monotonicity, the 1% statistical test, sub-period stability and, for S2 and S3, the incremental test.
- **The three top deciles all trailed the average eligible stock.** Under the frozen rule the economic floor is +3% a year above that average.

---

## 1. Execution summary

| Step | Run(s) | Outcome |
|---|---|---|
| 1. Plumbing / fidelity canary | E985-01 … E985-05 (X985) | E985-01 to -04 found technical defects, fixed (section 2); **E985-05 passed 14 / 14 on the final code** |
| 2. Null worlds | E020-01 … E020-05 (S020 = byte copy of X985) | **5,000 / 5,000 completed**, first attempt |
| 3. Family threshold | `H019_eval.py null` | c = 2.8714967 |
| 4. Commit, hash, pin | commit `1dc6b07` (threshold, hashes, test), commit `ec87a43` (threshold-commit record + E020-06 config) | pushed before the real run |
| 5. Clean tree | `git status` empty at `ec87a43`; S020 byte-identical to X985 | verified |
| 6. **One** real evaluation | **E020-06** (QC backtest 9b53a282…, commit `ec87a43`, `--owner-approved D145`) | completed once; no rerun |
| 7. This checkpoint | — | STOP |

**Totals.**
- **This phase:** 1 hypothesis-procedure (H019), 2 hosts (X985 canary, S020), and 11 registered runs: E985-01…05, E020-01…05 (infrastructure) and E020-06 (the research run).
- **Not registered:** one scratch diagnostic (E985-99), which published only split / price-factor ratios.
- **Programme registry:** 467 rows (303 original runs), 17 hypotheses with registered runs, 18 strategies.

## 2. Plumbing result (item 2)

**PASSED** on the final code (E985-05, `research/phase4/H019_canary_report.json`). **No real-signal statistic was published by any canary.**

| Check | Result |
|---|---|
| Calendar ends 2017-12-29; no history row after it | PASS (3,062 sessions 2005-11-01 → 2017-12-29) |
| Point-in-time month-end universe for every month 2010-01 … 2017-12 | PASS (96 months) |
| Each month's universe dated on that month's last session | PASS (0 mismatches) |
| 83 decisions 2011-01-31 … 2017-11-30 | PASS |
| Primary response of the last decision ends 2017-12-29; 3-month diagnostic ends 2017-12-29 | PASS |
| Independent slow recomputation of PRET, ID and all 11 A_L (150 stock-months) | PASS: max differences 0 / 0 / 3e-13 |
| Trend-factor regressions vs independent normal equations | PASS: max 1.6e-10 (14 months) |
| S3 recomputed independently (slow regressions, 12-month mean, score) | PASS: max 2.0e-10 |
| S2 grouping: integer part = PRET quintile, within-quintile order = ID key; ID in [−1, 1] | PASS: 0 violations |
| Regression chronology: s = 2010-01 … 2017-10 (the last decision averages s = 2016-11 … 2017-10) | PASS |
| Truncation (no future leakage): panel cut at the 2014-07 close gives identical signals and coefficients for 42 decisions | PASS: max difference **0** |
| Planted response (signal := next-month return): IC = 1 at every date, h = 1 and h = 3 | PASS (min 0.9999999) |
| Placebo random features: \|t\| < 3.5 | PASS (max \|t\| 1.73) |
| Determinism: the same null seed twice | PASS (identical digests) |
| Price construction cross-check vs QuantConnect's SCALED_RAW factors | PASS (0 large disagreements; 6 small steps among 42,531 dividend events) |

**Technical defects found and fixed before any null or real statistic (D146, D147).** No signal definition or statistical rule changed.

1. **E985-01 regression-span check.** It was a mis-specified check, not a pipeline fault. The spec's formula s = t−12 … t−1 makes 2017-10 the last regression used, not 2017-11.

2. **E985-01 S3 prices at spin-offs.**
   - *Finding:* 74 large non-split price-factor events, mostly spin-offs (ABT → ABBV, MO → PM, KFT, MRO, …), plus a few splits that QuantConnect records as price factors.
   - *Background:* CRSP's `cfacpr` price-adjusts spin-offs.
   - *E985-02:* showed that QuantConnect's dividend feed carries every non-split price factor, spin-offs included, without labelling them.
   - *Decision:* reproducing CRSP's spin-off factor would require an invented classification rule, so it was not done. S3 closes stay literally "split-adjusted, not dividend-adjusted" (raw closes × QuantConnect's split feed).
   - *Exposure, disclosed:* 1.46% of regression-set observations (1,493 of 102,049; 53 stocks) have such an event inside their 1,000-bar window.

3. **E985-03 / E985-04: one vendor inconsistency.**
   - *Finding:* Peabody (BTU) 1-for-15 reverse split on 2015-10-01. QuantConnect's own price factor (12.9) contradicts its split feed (15), with no distribution that day. This made S3 prices and total-return prices disagree for 5 observations (1 stock).
   - *Fix:* every price is now built from raw bars × QuantConnect's own split and dividend feeds, which is QuantConnect's adjustment method applied to its own event feeds. S1, S2, S3 and the returns are therefore consistent by construction, and SCALED_RAW is only a cross-check.
   - The same change also removes a constant factor that LEAN attached to 11 stocks for ex-dates after 2017. It cancelled in every ratio anyway.

## 3. Null completion count (item 3)

**5,000 of 5,000 worlds** (seeds 1–5,000; 1,000 per run). Every run saw identical inputs: feature digest `40c2a181…`, the same as the passing canary and the real run.

## 4. Null failures / retries (item 4)

**None.** 0 failed worlds and 0 retried runs.

| Run | Seeds | QC backtest | Commit | Runner time |
|---|---|---|---|---|
| E020-01 | 1–1,000 | 059b4d79… | ee8647b | 1,194 s |
| E020-02 | 1,001–2,000 | 14395712… | 23d7aa6 | 1,543 s |
| E020-03 | 2,001–3,000 | f96b206e… | 4ff51fe | 1,447 s |
| E020-04 | 3,001–4,000 | 5fcaddd8… | 5b4ecc7 | 1,376 s |
| E020-05 | 4,001–5,000 | 1c2f8943… | 1e0b3dc | 1,171 s |

## 5. Frozen threshold (item 5)

**c = 2.8714967**, the 50th largest of the 5,000 null values of F = max(t_S1, t_S2, t_S3, t_inc,S2, t_inc,S3) (α = 1%).

| | 50% | 90% | 95% | 99% | 99.9% | max |
|---|---|---|---|---|---|---|
| Null F | 0.717 | 1.798 | 2.150 | 2.868 | 3.981 | 4.335 |

**Empirical calibration on the 5,000 null worlds:**
- F > c in 0.98%.
- Full-rule promotion of S2 / S3: **0 / 5,000**.
- S1 replication pass: 0 / 5,000.
- Economic floor alone: S1 0% / S2 0% / S3 0.08%.

Full detail is in `research/phase4/H019_null_report.md`.

## 6–8. Threshold commit, null-result hash, spec hash (items 6–8)

| Item | Value |
|---|---|
| Threshold commit | **`1dc6b070b7e3bae2d5f67ce9e20dae5dd4cab615`** |
| Null result `H019_null_result.json` | SHA-256 **`6d5ea4a0056728d116c6b96e3524d8be45bf3dc4e88fb54eb080db9ce44f883c`** |
| Per-world table `H019_null_worlds.csv` | SHA-256 `59a6cfb70fd49fc7d7b741a39225a8025aea6ef8f4692ada5735625971be94fd` |
| Specification v2 | SHA-256 **`15fb0451d535ae31d234822ad60f58230f580b23a6683f2df67936429a47ca1e`** |

## 9. The threshold was frozen first (item 9)

**Confirmed.** The order of events:
1. c and both hashes were committed and pushed in `1dc6b07` (tests check the hashes and that c is the 50th largest F).
2. `ec87a43` recorded that commit in `qresearch.p4xs.THRESHOLD_COMMIT` and wrote the E020-06 config carrying c, the threshold commit, the null hash and the spec hash.
3. E020-06 then ran from the clean tree at `ec87a43`. Its host echoed the pins.

The evaluation verifies all of the following:
- the run commit descends from `1dc6b07`;
- the run's committed config holds the exact c;
- the null and spec hashes match;
- the input digest equals the null runs' digest;
- the approval is D145.

The host's echo of c is rounded to 6 digits (2.8715). That is formatting only: c is never used inside QuantConnect.

## 10. Window (item 10)

- Decisions: month-ends **2011-01 → 2017-11: 83 non-overlapping monthly evaluation periods.** Synthetic calibration indicates the effective sample size is close to the full 83 months. The realised IC autocorrelation gives estimates of 104 / 112 / 217 for S1 / S2 / S3; this does not make the 83 periods independent.
- Trend-factor regressions: s = 2010-01 → 2017-10 for the decisions evaluated.
- Look-back prices: from 2005-11, used as inputs only.
- Last response: ends 2017-12-29.
- 3-month diagnostic: 81 decisions, 2011-01 → 2017-09.

## 11. Universe counts over time (item 11)

Eligible stocks with a bar at the month-end (min – max per year), and the mean of those with PRET and ID defined:

| Year | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|---|
| Eligible with a bar | 746–924 | 842–970 | 905–955 | 986–1,161 | 1,158–1,240 | 1,154–1,267 | 1,093–1,250 | 1,250–1,327 |
| Mean with PRET and ID | 800 | 904 | 913 | 1,048 | 1,160 | 1,193 | 1,158 | 1,251 |

The evaluation cross-section per decision ranged from 827 to 1,282 stocks. Over the whole period 1,950 distinct stocks were eligible at some month-end.

## 12. Partial moving-average history (item 12)

Share of observations with fewer than L bars (mean over months; first → last month in brackets):

| L | 3–20 | 50 | 100 | 200 | 400 | 600 | 800 | 1,000 |
|---|---|---|---|---|---|---|---|---|
| Regression set | 0% | 0.2% | 0.7% | 1.6% | 3.5% | 5.5% | 7.6% | **9.6%** (6.8% → 11.0%) |
| Evaluation set | 0% | 0% | 0% | 0% | 1.6% | 3.8% | 5.9% | **8.0%** (5.9% → 8.7%) |

These follow the frozen Chen-Zimmermann convention: a moving average uses all available bars when fewer than L exist.

## 13–15. Full result per signal (items 13–15)

| Signal | Top decile (ann.) | Bottom decile (ann.) | Top − bottom (ann.) | Mean rank IC | IC t (NW 2) | Percentile in family null | Empirical p (family) | p vs its own null (reporting) | Monotonicity ρ (Q5 − Q1, ann.) | Halves IC | Max block share |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S1** | −2.18% | −3.64% | +1.47% | 0.0038 | 0.22 | 25.3 | 0.747 | 0.181 | 0.00 (+1.07%) | 0.0078 / −0.0001 | 1.36 |
| **S2** | −1.20% | −4.76% | +3.56% | 0.0058 | 0.34 | 31.5 | 0.685 | 0.166 | 0.00 (+1.07%) | 0.0083 / 0.0034 | 0.85 |
| **S3** | −2.85% | −1.52% | −1.33% | 0.0011 | 0.12 | 21.5 | 0.785 | 0.424 | −0.10 (−1.54%) | 0.0057 / −0.0033 | 3.82 |

**Promotion criteria (frozen):**

| Signal | P1 economic (top ≥ +3%/yr and spread > 0) | P2 monotonic (ρ ≥ 0.90 and Q5 > Q1) | P3 statistical (t > c) | P4 stable (both halves IC > 0, no block > 50%) | P6 incremental (t_inc > c) | **Overall** |
|---|---|---|---|---|---|---|
| S1 | FAIL | FAIL | FAIL | FAIL | — | **FAIL** |
| S2 | FAIL | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| S3 | FAIL | FAIL | FAIL | FAIL | FAIL | **FAIL** |

**S2's quintiles are identical to S1's by construction.** S2 = PRET quintile + a within-quintile refinement, so its quintile ranks are the PRET quintiles. P2 therefore judges the momentum backbone, and the refinement is tested by P6 (spec section 7).

## 16. Quantile tables (item 16)

Mean demeaned next-month return, annualised (D1 = lowest signal):

| Signal | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | −3.6% | −0.5% | +1.6% | +1.8% | +1.6% | +1.0% | +1.4% | −1.3% | +0.2% | −2.2% |
| S2 | −4.8% | +0.7% | +1.1% | +2.3% | +0.7% | +1.9% | −0.9% | +1.0% | −0.8% | −1.2% |
| S3 | −1.5% | +0.8% | −0.1% | +0.3% | +1.0% | +1.6% | +0.3% | +1.2% | −0.9% | −2.8% |

| Signal | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|
| S1 | −2.1% | +1.7% | +1.3% | +0.1% | −1.0% |
| S2 | −2.1% | +1.7% | +1.3% | +0.1% | −1.0% |
| S3 | −0.3% | +0.1% | +1.3% | +0.8% | −1.9% |

**The pattern is hump-shaped, not monotonic.** Both signal extremes underperformed the middle of the cross-section, most strongly the lowest-momentum decile.

## 17. Rank ICs (item 17)

| Signal | Mean IC | NW se | t | IC sd | Effective-sample estimate | IC detectable at c (c × se) |
|---|---|---|---|---|---|---|
| S1 | 0.0038 | 0.0175 | 0.22 | 0.156 | 104 | 0.050 |
| S2 | 0.0058 | 0.0172 | 0.34 | 0.155 | 112 | 0.049 |
| S3 | 0.0011 | 0.0095 | 0.12 | 0.096 | 217 | 0.027 |

The realised ICs are about one-tenth or less of the IC that would have been detectable at c.

## 18. Top-minus-bottom spreads (item 18)

S1 +1.47%, S2 +3.56% and S3 −1.33% a year, annualised from monthly decile means. None comes with a usable top decile: every top decile is negative.

## 19. Economic effect sizes (item 19)

Top-decile excess over the cross-sectional average: S1 **−2.18%**, S2 **−1.20%**, S3 **−2.85%** a year. Each is below zero, so each is far below the frozen +3% floor.

## 20. Monotonicity (item 20)

| Signal | Spearman(quintile, mean) | Q5 − Q1 (ann.) | Rule (≥ 0.90 and Q5 > Q1) |
|---|---|---|---|
| S1 | 0.00 | +1.07% | FAIL |
| S2 | 0.00 | +1.07% | FAIL |
| S3 | −0.10 | −1.54% | FAIL |

## 21. Sub-period stability (item 21)

**The frozen gate (P4)** uses halves of 41 / 42 decisions and blocks 2011–12, 2013–14, 2015–16, 2017.
- S1: second half IC −0.0001; max block share 1.36.
- S2: positive halves but max block share 0.85.
- S3: second half −0.0033; max block share 3.82.
- **All three fail.**

**Calendar sub-periods requested by the owner** (reporting only):

| Signal | 2011–2013 IC (t) | 2011–2013 top / spread (ann.) | 2014–2017 IC (t) | 2014–2017 top / spread (ann.) |
|---|---|---|---|---|
| S1 | 0.0166 (0.71) | +1.13% / +6.72% | −0.0060 (−0.24) | −4.71% / −2.56% |
| S2 | 0.0172 (0.74) | +0.68% / +8.12% | −0.0029 (−0.12) | −2.64% / +0.07% |
| S3 | −0.0007 (−0.05) | −4.14% / −3.20% | 0.0025 (0.19) | −1.86% / +0.10% |
| S2 incremental | 0.0127 (0.81) | | 0.0114 (1.08) | |
| S3 incremental | 0.0106 (0.72) | | −0.0068 (−0.71) | |

**Year diagnostics** (mean IC; t in brackets; top decile annualised):

| Signal | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|
| S1 | −0.014 (−0.4); −6.0% | 0.037 (0.9); +6.8% | 0.027 (1.1); +2.6% | 0.009 (0.2); −7.1% | 0.062 (1.0); −2.1% | −0.087 (−1.7); −8.6% | −0.007 (−0.2); −0.7% |
| S2 | −0.003 (−0.1); −3.1% | 0.031 (0.7); +4.4% | 0.023 (0.9); +0.8% | 0.011 (0.3); +0.6% | 0.064 (1.0); +1.6% | −0.084 (−1.6); −12.5% | −0.003 (−0.1); −0.0% |
| S3 | 0.013 (0.5); −6.7% | −0.032 (−1.4); −6.4% | 0.017 (0.7); +0.6% | 0.013 (0.6); +1.3% | 0.036 (0.9); −4.9% | −0.038 (−1.2); −1.7% | −0.002 (−0.1); −2.2% |

**Concentration and later-period behaviour:**
- **Sign reversals:** S1 and S2 have positive mean IC in 4 of 7 years; S3 in 4 of 7.
- **2016 dominates the momentum signals' weakness:** S1 IC −0.087; S2 top decile −12.5%.
- **The 2011–2013 S1 / S2 spreads (+6.7% / +8.1%) collapse in 2014–2017.**
- **No year is individually significant.**

## 22. Incremental S2 over S1 (item 22)

> **"Among stocks with similar Plain Momentum, does Information Discreteness add predictive information?"**
> **Not detectably.**

- Mean within-momentum-quintile partial IC = **0.0120** (NW t = **1.31**; family p = 0.231; p against its own null = 0.106). Per quintile: 0.021 / 0.001 / 0.021 / 0.018 / −0.001.
- The point estimate has the published sign (smoother, continuous-information momentum ranks slightly better within momentum quintiles), and its 2011–2013 and 2014–2017 halves are similar (t 0.81 and 1.08).
- It is less than half the frozen threshold (1.31 vs 2.87), and it would not reach even a conventional one-sided 5% level (1.645).
- **Result: FAIL.**

## 23. Incremental S3 over S1 (item 23)

Mean within-momentum-quintile partial IC = **0.0007** (t = **0.09**; family p = 0.794; p against its own null = 0.451). **Result: FAIL.**

**"Trend Factor predicts returns" vs "merely repackages momentum":** neither holds in this sample.
- S3 is not a repackaging of momentum. Its mean cross-sectional rank correlation with S1 is only 0.23 (S1–S2: 0.97), it turns over much faster (month-to-month rank autocorrelation 0.41 vs 0.89), and it is 0.07 negatively correlated with the trailing 1-month return.
- But **it did not predict returns either**, on its own (IC 0.001, t 0.12) or beyond momentum (t 0.09).

## 24–25. Family-null percentiles and empirical p-values (items 24–25)

| Statistic | Real value | Percentile in the family null | Empirical p (family, the gate) | p vs its own null (reporting) |
|---|---|---|---|---|
| t_S1 | 0.22 | 25.3 | 0.747 | 0.181 |
| t_S2 | 0.34 | 31.5 | 0.685 | 0.166 |
| t_S3 | 0.12 | 21.5 | 0.785 | 0.424 |
| t_inc,S2 | 1.31 | 76.9 | 0.231 | 0.106 |
| t_inc,S3 | 0.09 | 20.6 | 0.794 | 0.451 |
| **F (family)** | **1.31** | **76.9** | **0.231** | — |

**A property of the frozen null (reported, not acted on):**
- In the tethered null, t_S1 and t_S2 are centred below zero (median −0.60 and −0.55; mean null S1 IC −0.0022), while S3 and both incremental statistics are centred at zero.
- **A plausible but unverified explanation:**
  - stocks that newly enter the ≥ $2B universe, and the partners freed when stocks leave it, are re-matched among themselves;
  - so the null partly preserves an "entry cohort" link between high past returns and the subsequent returns of new entrants.
- **This does not affect the conclusion:**
  - every real statistic is below c;
  - the largest (1.31) is below the null family's 95th percentile (2.15);
  - against each statistic's own null distribution no p-value is below 0.10.

## 26. Promotion decisions (item 26)

| Signal | Decision |
|---|---|
| S1 (reference) | **Not reproduced.** No replication: momentum's known effect did not appear in this universe and window |
| S2 | **Not promoted** (fails P1, P2, P3, P4 and P6) |
| S3 | **Not promoted** (fails P1, P2, P3, P4 and P6) |
| Outcome | **none** (no candidate, no replication) |

## 27. 3-month diagnostic — NON-GATING DIAGNOSTIC (item 27)

This was computed after the primary result, on 81 decisions with NW lag 6. **It cannot promote, rescue, veto or alter the interpretation.**

| Signal | IC | t | Top decile (ann.) | Top − bottom (ann.) | t_inc |
|---|---|---|---|---|---|
| S1 | 0.0009 | 0.04 | −2.34% | +3.49% | — |
| S2 | 0.0021 | 0.10 | −1.95% | +2.94% | 0.43 |
| S3 | −0.0146 | −0.93 | −3.60% | −3.35% | −0.84 |

## 28. Trend-factor horizon diagnostic (item 28)

**This is explanatory only.** It removes no horizon, defines no variant, and promotes or rescues nothing.

| Component Σ E[β_L] A_L | IC (t) | Incremental over S1 (t) |
|---|---|---|
| Short, L = 3–20 | 0.0116 (0.91) | 0.0094 (0.88) |
| Mid, L = 50–200 | −0.0201 (−1.38) | −0.0046 (−0.36) |
| Long, L = 400–1,000 | 0.0105 (0.73) | −0.0022 (−0.20) |

- No component is significant. The fitted factor's horizons partly offset one another.
- The monthly path of the 12-month averaged coefficients E[β_L] is in `research/phase4/H019_real_result.json` (`diagnostics.tf_expected_beta_path`).

**Other diagnostics** (spec section 8; `H019_tables.md`):

| Diagnostic | S1 | S2 | S3 |
|---|---|---|---|
| Sector-neutral IC, FF12 from point-in-time SEC SIC (t) | 0.0059 (0.37) | 0.0072 (0.46) | 0.0086 (0.95) |
| IC small-cap / large-cap half | 0.0073 / 0.0004 | 0.0078 / 0.0039 | 0.0043 / −0.0040 |
| Correlation with log market cap | 0.017 | 0.026 | 0.023 |
| Top-decile / top-quintile retention month to month | 0.72 / 0.76 | 0.68 / 0.76 | 0.35 / 0.42 |

- The spec's "top decile vs SPY" diagnostic was **not computed**, because the owner's message forbids any SPY comparison (D145).
- **Disclosed data limitation:** the S3 spin-off exposure is 1.46% of regression observations (section 2).

## 29–33. Discipline confirmations (items 29–33)

| Item | Confirmation |
|---|---|
| 29. No post-result tuning | **Confirmed.** Nothing about signals, horizons, groups, zero-day handling, frequency, universe, rules or threshold changed after any result; there was no rerun. After E020-06 only the evaluation's pinned-state verification was adjusted (the 6-digit echo, section 9) and reporting-only p-values against each statistic's own null were added. Neither changes any gate input. |
| 30. 2018–2021 untouched | **Confirmed.** Every run ends 2017-12-31 (enforced by the config rules and the algorithm). The last bar loaded is 2017-12-29. The canary verified that no history row lies after it. |
| 31. Holdout untouched | **Confirmed.** 2022-01-01 → 2026-08-31 locked; `HOLDOUT_UNLOCK.md` absent. |
| 32. No portfolio | **Confirmed.** No holdings, rebalancing, exits, commissions, terminal wealth or SPY comparison; the hosts place no orders. |
| 33. No paid data | **Confirmed.** Existing QuantConnect subscription only; nothing purchased. |

## 34. Interpretation under the pre-registered wording (item 34)

**"No technical stock-selection signal large enough to satisfy the project's detection and economic-significance requirements was found."**

**What this does mean:**
- On the frozen 2011–2017 development sample of US common stocks ≥ $2B:
  - 12-1 momentum and its two best-documented technical refinements carried no cross-sectional predictive information that the frozen procedure could distinguish from a structure-preserving no-information world;
  - none came close to the +3% economic floor.
- **Momentum was not reproduced as a replication check.** This is consistent with the documented weakening of US momentum after 2002, but that context is not a test result.

**What it does not mean:**
- It is **not** a finding that "technical analysis does not work".
- It is **not** a finding that "there is no 1–3% edge". Effects of that size are below what 83 monthly evaluation periods can detect (P4-CP3R2: 50% detectable top-decile edges ≈ 4–15% a year).

**Consequence under spec section 9 for "none":**
- technical stock-selection research in this universe stops;
- no RSI / MACD / ADX / Bollinger / volume / breakout follow-ups;
- no simplified trend-score substitute.

## 35. Recommended next action (owner approval required) (item 35)

1. **Close H019 as "No Production Candidate Found".** Close Phase 4's technical stock-selection line with it, and do not run any further technical-signal search in this universe.
2. **Keep everything locked:**
   - the 2018–2021 data stays unused;
   - the Holdout stays locked;
   - S020 and all results are preserved exactly as run.
3. **Any further research direction is a new owner decision.** Possibilities include a different signal family or data, or stopping the programme, which remains an honest outcome. No new hypothesis is proposed here, as the authorisation requires.

## 36. Final verdict

# **NO SIGNAL QUALIFIED FOR PORTFOLIO RESEARCH**

**STOPPED** awaiting the owner. Nothing further will be run.

### Files

- **Evaluation and tables:**
  - `research/phase4/H019_eval.py`
  - `H019_tables.py`
  - `H019_make_configs.py`
- **Results:**
  - `H019_canary_report.json`
  - `H019_null_report.md`
  - `H019_null_result.json`
  - `H019_null_worlds.csv`
  - `H019_real_result.json`
  - `H019_tables.md`
- **Host and modules:**
  - `strategies/X985_h019_xs/main.py` = `strategies/S020_h019_xs/main.py`
  - `src/qresearch/lean/qr_xs_panel.py`
  - `qr_xs_diag.py`
- **Pins:** `src/qresearch/p4xs.py`
- **Tests:**
  - `tests/test_xs_host.py`
  - `tests/test_p4xs_spec.py`
