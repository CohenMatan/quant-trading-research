# P12-CP1 — H027 Exposure-Controlled Learned Stock Score

**Date:** 2026-10-12. **Decisions:** D213 (owner approval), D214 (canary), D215 (null, adequacy, c_WEALTH_CONDITIONAL), D216 (this checkpoint).
**Status:** STOPPED, awaiting the owner.

```
H027 REJECTED —
NO ROBUST STOCK-SELECTION EDGE
BEYOND LOWVOL EXPOSURE
```

## Short answer

H027 asked one question: does the learned 11-feature score (the frozen H026 procedure) pick better stocks than its low-volatility tilt alone would explain, while still ending with more money than SPY?

**Partly, but not robustly enough.** Five of the six pre-registered gates pass. One fails.

- **A1 passes clearly.** The real wealth statistic S_WEALTH = 0.171 is far above the new exposure-controlled threshold c_WEALTH_CONDITIONAL = 0.058.
  - Only 2 of 5,000 worlds did at least as well (p = 0.0006).
  - In those worlds LOWVOL stays with its own stock and only the other ten features are shuffled.
- **A2, A3, A5 and A6 pass.**
  - H027 ended with far more than the pure low-volatility control LV15 ($311,397 vs $220,156).
  - H027 beat SPY by 1.19× in wealth and +2.85 points a year, with less risk.
  - It survives doubled slippage.
- **A4 fails.** H027 was ahead of LV15 in 5 of 7 years, but it was **behind LV15 over 2015–2017** (log-relative −0.058).
  - 2015: −0.171. 2016: −0.059. 2017: +0.172.
  - The rule requires both sub-periods to be positive.

Any failed gate means rejection. Nothing is frozen as a candidate, and no final score was fitted. H026 stays permanently rejected and unchanged. The Holdout (2022-01-01 → 2026-08-31) was not touched.

All of this is **development evidence only**. The 2011–2021 data was already fully seen through H026 and its post-mortem.

| Gate | Requirement | Result | |
|---|---|---|---|
| A1 | S_WEALTH > c_WEALTH_CONDITIONAL and p ≤ 0.01 | 0.1715 vs 0.0577; p = 0.0006 | ✔ |
| A2 | wealth and CAGR above LV15_CONTROL | $311,397 vs $220,156; 17.63% vs 11.94% | ✔ |
| A3 | wealth ≥ 1.15 × SPY and excess CAGR ≥ +2 pts (*a carried-forward economic requirement, not new independent evidence*) | 1.187× and +2.85 pts | ✔ |
| A4 | ahead of LV15 in ≥ 5 of 7 years; 2015–17 > 0; 2018–21 > 0 | 5 / 7; **−0.058**; +0.405 | ✘ |
| A5 | \|MaxDD\| and volatility ≤ 1.25 × SPY | 0.77× and 0.93× | ✔ |
| A6 | at 0.20% slippage, no retraining: above SPY and above LV15 | $295,028 vs SPY $261,801, LV15 $205,500 | ✔ |

## What this means in plain terms

- **The learned score is more than a low-volatility tilt.** A portfolio that simply holds the 15 calmest stocks (LV15) earned 11.9% a year and *lost* to SPY by 2.8 points a year.
  - The exposure-controlled null worlds keep each stock's LOWVOL and shuffle everything else. Almost all of them also lost to SPY (median S_WEALTH −0.24).
  - The real H026/H027 portfolio beat 4,998 of those 5,000 worlds.
  - So the other ten features, as Ridge combined them, did add something during 2015–2021.
- **But the extra edge was not steady over time.**
  - In 2015 and 2016 the learned score did clearly worse than simply holding low-volatility stocks.
  - All of its advantage over LV15 came from 2017 onward.
  - The pre-registered rule asked for an edge in *both* halves, and the first half is negative.
- **The result is concentrated in a period we have already studied.**
  - H027 was designed after seeing H026's 2015–2021 behaviour, so even a full pass could only have been development evidence.
  - The one clean test left is the sealed Holdout, and H027 does not qualify for it.
- **The A1 pass needs context.** The conditional null worlds are calmer than the real portfolio:
  - 98.7% had lower volatility;
  - 96.4% had lower beta.

  They are essentially "LOWVOL plus noise" portfolios, which lagged a strongly rising market. A1 shows that the real combination of the ten other features beat random substitutes. It does not show that this combination works in every period, and A4 shows it did not.

## Required items

### Governance and status

1. **Owner decision ID:** D213 (`docs/owner/2026-10-12_p12cp1_h027_exposure_controlled_score.md`, verbatim, recorded before any H027 work). Run decisions: D214, D215 and D216.
2. **Explicit D207 owner exception:** Data v2.1 is frozen as an **OWNER-APPROVED EXCEPTION** (`research/phase11/data_v21/owner_exception_D213.json`).
   - The failed criterion used an incorrect denominator.
   - No underlying data row was changed by the issue.
   - The SEC-identity denominator gives about 0.95–0.97 mapping coverage in 2018–2021.
3. **Original failed criterion preserved:** "NEW_YEARS_MAPPING failed AS WRITTEN" (threshold 0.90, FAILED).
   - The manifest is unchanged (SHA-256 ef0a7a66…, status "FROZEN — NEW_YEARS_MAPPING FAILED AS WRITTEN (SPECIFICATION ERROR, D207)").
   - Data v2.1 was not rebuilt.
4. **Corrected-denominator explanation:** the gate's counter divided by all vendor reports, including companies with no SEC identity row.
   - The same counter is 0.51–0.60 even in the frozen Data v2 years.
   - Among reports *with* an SEC identity the mapped share is 0.95–0.97 (2018–2021) vs 0.96–0.98 (2011–2017).
   - The 2011–2017 H022 population differs from Data v2 by −0.046% (34,847 vs 34,863 stock-months), caused by the restatement guard.
   - All of this is preserved (D207).
5. **H026 permanently rejected:** "H026 REJECTED — LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY". None of the following changed:
   - its pins (`qresearch.p11h026`; C_WEALTH 0.2245; CANDIDATE None);
   - its null (E028-02/03);
   - its result (`P11_CP1_result.json`).
6. **H027 hypothesis** (`research/hypotheses/H027.md`): the learned 11-feature score contains stock-selection information beyond the LOWVOL exposure, while still producing more terminal wealth than SPY.
   - H0: LOWVOL may matter, but the other ten features carry no stock-specific information beyond it.
7. **Development period:** decisions 2011–2021, outer test years 2015–2021. This data is fully seen, so the result is development evidence only.
8. **Holdout status:** 2022-01-01 → 2026-08-31 is SEALED. Nothing was read: no prices, fundamentals, SPY, SEC filings, features or benchmarks.

### Frozen procedure (unchanged from H026)

9. **Frozen 11 features:** MOM, LOWVOL, GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP and EQA. The point-in-time formulas in `qr_h024` are unchanged.
10. **Frozen target:** 63-session SPY-relative return after the next open, with the label-availability rule (labels must exit before the training cutoff).
11. **Frozen Ridge grid:**
    - λ ∈ {0.01, 0.1, 1, 10, 100}, with monthly-equal-weighted Ridge;
    - annual refit at each December review;
    - inner λ selection on 2013..Y−1 by Σ ln(W/SPY).
12. **Frozen portfolio mechanics:**
    - Top-15, at most 3 per FF12 sector, 10% initial cap;
    - monthly rebalance at the next open;
    - $7 per order and 0.10% slippage per side;
    - long only, no leverage, $100,000 start.

### Memory reduction (infrastructure)

13. **Memory before (H026 host S028):** peak 7,873 MB (canary E028-01), 7,965 / 8,224 MB (nulls E028-02/03) and 7,933 MB (real E028-05).
14. **Memory after (H027 host S029):** peak 7,785 MB (canary E029-01), 7,683 / 7,728 / 7,715 MB (nulls E029-02/03/04) and 7,751 MB (real E029-05).
    - That is 90–500 MB lower, but **the owner's < 6.5 GB target was NOT met**.
    - The process already holds 5.5 GB when the end-of-run analysis starts, and the Data v2.1 build adds about 2 GB.
    - The canary's stage-by-stage memory is in `P12_CP1_canary_E029-01.json`.
15. **Memory equivalence result: PASS, exact** (canary E029-01, D214).
    - The feature-panel digest equals the H026 pin 10a54163… and the response panel equals e1503f9c….
    - The H022 / H024 per-decision population counts equal the P11-CP1 canary.
    - H026's unconditional null worlds 1–25, rerun inside S029, equal the committed E028-04 rows exactly. This covers Ridge coefficients, λ choices, portfolio and costs on real data.
    - The real run then reproduced H026 exactly as well (item 34).

### Conditional null

16. **Conditional-null definition** (spec section 4, `qr_h027.conditional_permuted`):
    - For each seed, each stock keeps its own LOWVOL value, returns, prices, corporate actions, sector and universe membership.
    - It receives the complete vector of the ten other features from one donor stock on the same review date.
    - The complete H026 procedure is rerun in every world: λ selection, annual fits, scores, Top-15, trading, costs and SPY comparison.
17. **Proof LOWVOL remains attached:** canary check 6 — LOWVOL changed in 0 of 186,864 rows over 393 seed-months. A unit test confirms the same.
18. **Proof the other ten move as one vector:** canary check 7.
    - In 0 rows does the recipient's ten-vector differ from its donor's row.
    - The permuted multiset equals the original exactly, with no row lost or duplicated.
19. **Persistent-tether implementation:** the frozen identity tether `qr_p7_pred.Tether(seed)`:
    - one stratum, no self-matching;
    - a pair is kept while both stocks remain in the population;
    - new or orphaned stocks are paired, with the documented fixed-point splice changing at most one pair per month.

    On real data: 0 self-matches, and 153,249 of 153,249 continuing pairs kept (no splice was needed).
20. **Canary result:** E029-01 **PASSED 17 of 17** (checks committed before the output was read; D214).
21. **Synthetic LOWVOL-only canary (world A):** returns driven by LOWVOL only. The real-style model sat at percentiles 0.05 / 0.84 / 0.21 / 0.84 / 0.84 among 19 conditional-null worlds each.
    - Median 0.84 < 0.90 → **PASS** (it does not beat the null).
22. **Synthetic LOWVOL + incremental-signal canary (world B):** LOWVOL plus GPA → percentile 1.00 in all three replicates → **PASS** (it beats the null). Every replicate was repeat-identical.
23. **Null-world count:** 5,000 (E029-02: 2,500; E029-03: 2,500), with 0 non-finite values.
24. **Seeds:** 1–5,000, with 1–2,500 in E029-02 and 2,501–5,000 in E029-03. E029-04 reran seeds 1–25.
25. **Null determinism: exact.** E029-04 reproduced seeds 1–25 bit for bit, including:
    - S_WEALTH, wealth, the risk measures, the 7 yearly returns, the 7 λ and the coefficient digest;
    - the full Ridge coefficients.

    All three runs carried the pinned panels, PIT audit 0 and the same LEAN build (18178).
26. **Conditional-null S_WEALTH distribution:**

    | Statistic | Value |
    |---|---|
    | Mean | −0.237 |
    | SD | 0.128 |
    | 1st percentile | −0.540 |
    | 5th percentile | −0.449 |
    | Median | −0.236 |
    | 95th percentile | −0.025 |
    | 99th percentile | +0.056 |
    | Max | +0.205 |
    | Share positive | 3.4% |
    | Median excess CAGR | −3.8 pts |

    For comparison, the H026 unconditional null: median −0.230, c 0.2245.
27. **Volatility distribution:** 1st percentile 0.134, median 0.149, 99th 0.164 (min 0.128, max 0.176). Real 0.164.
28. **MaxDD distribution:** 1st percentile −0.366, median −0.290, 99th −0.211 (deepest −0.403, shallowest −0.182). Real −0.261.
29. **Beta distribution:** 1st percentile 0.592, median 0.705, 99th 0.825. Real 0.795.
30. **Down-capture distribution:** 1st percentile 0.488, median 0.678, 99th 0.874. Real 0.776.
    - Up-capture: median 0.717, 99th 0.862. Real 0.986.
31. **Null adequacy conclusion: ADEQUATE** (pre-registered rule: each measure ≥ 1% of worlds at least as defensive). Worlds at least as defensive as the real portfolio:

    | Measure | Worlds | Share |
    |---|---|---|
    | Volatility | 4,935 | 98.7% |
    | MaxDD | 1,000 | 20.0% |
    | Beta | 4,820 | 96.4% |
    | Down-capture | 4,379 | 87.6% |

    Unlike the H026 null, this null *does* reproduce the real portfolio's defensiveness. In fact it is mostly more defensive.
32. **c_WEALTH_CONDITIONAL = 0.05770235251912147** (the 50th largest of 5,000).
    - Null result SHA-256: 613aa1e2…
    - Pinned in commit 7793223 and merged in PR #89 before the real run.

### Real run E029-05 (the one real H027 development run)

The real run used commit 1fb0f2f, LEAN 18178, QC backtest 8ae14926…, and placed 0 orders.

33. **Real H027 terminal wealth:** $311,396.77, CAGR 17.63%, volatility 16.39%, MaxDD −26.12%, Sharpe 1.07.
34. **H026 reproduction check: PASS, exact.** Wealth, SPY wealth, S_WEALTH, all 7 yearly returns, all 7 λ and all 7 × 11 coefficients equal the committed E028-05 / P11-CP1 values. The real risk values equal the adequacy reference.
35. **Real SPY wealth:** $262,325.46, CAGR 14.78%, volatility 17.68%, MaxDD −33.72%.
36. **S_WEALTH_real:** 0.17148 (= ln 1.187).
37. **Conditional-null percentile:** 4,998 of 5,000 worlds below the real value (99.96th percentile).
38. **Conditional-null empirical p:** (1 + 2) / 5,001 = **0.0006**.
39. **A1: PASS** (0.1715 > 0.0577 and p ≤ 0.01).
40. **LV15_CONTROL terminal wealth:** $220,156.03.
41. **LV15 CAGR:** 11.94%. That is 2.84 points a year *below* SPY, and S vs SPY is −0.175.
42. **LV15 volatility:** 10.97%.
43. **LV15 MaxDD:** −16.48%.
44. **LV15 beta:** 0.526.
45. **LV15 up / down capture:** 0.619 / 0.413 (H027: 0.986 / 0.776).
46. **H027 vs LV15:** wealth $311,397 vs $220,156, log-relative +0.347, CAGR +5.69 points. LV15 has the higher Sharpe (1.09 vs 1.07) at much lower risk.
47. **A2: PASS.**
48. **H027 / SPY wealth ratio:** 1.187.
49. **H027 / SPY excess CAGR:** +2.85 points.
50. **A3: PASS.** This is a CARRIED-FORWARD ECONOMIC REQUIREMENT, NOT NEW INDEPENDENT EVIDENCE: the same numbers were already seen in H026.
51. **H027 vs LV15 by year** (calendar-year returns; L = ln((1 + H027) / (1 + LV15))):

    | Year | H027 | LV15 | SPY | L vs LV15 | λ |
    |---|---|---|---|---|---|
    | 2015 | −7.7% | +9.5% | +0.7% | **−0.171** | 0.01 |
    | 2016 | +5.4% | +11.8% | +12.0% | **−0.059** | 100 |
    | 2017 | +31.8% | +11.0% | +21.7% | +0.172 | 100 |
    | 2018 | +11.6% | +4.2% | −4.6% | +0.069 | 100 |
    | 2019 | +27.9% | +19.3% | +31.2% | +0.069 | 100 |
    | 2020 | +34.3% | +11.9% | +18.3% | +0.183 | 100 |
    | 2021 | +26.9% | +16.7% | +29.1% | +0.083 | 100 |

52. **2015–2017 H027 / LV15 result:** −0.058 (negative).
53. **2018–2021 H027 / LV15 result:** +0.405 (positive).
54. **A4: FAIL.** 5 of 7 years is enough, but 2015–2017 is negative, against a requirement of > 0.
55. **H027 / SPY risk ratios:** |MaxDD| 0.77×, volatility 0.93×, monthly beta 0.80, down-capture 0.78.
56. **A5: PASS.**
57. **2× slippage H027 wealth:** $295,027.95 (0.20% per side, same selections, no retraining).
58. **2× slippage LV15 wealth:** $205,499.80.
59. **2× slippage SPY wealth:** $261,801.31.
60. **A6: PASS.**

### Diagnostics (non-gating; they never rescue a result)

61. **LOWVOL-factor regression alpha** (84 monthly periods): α = +0.217% a month (+2.60% a year), Newey-West t (lag 2) = **0.90**, which is not significant.
    - The dependent variable is H027 minus SPY.
    - The factor is the lowest-LOWVOL quintile's return minus the population's equal-weight return.
62. **LOWVOL-factor gamma:** γ = 0.51, R² = 0.23. The factor's mean was −0.03% a month over the period.
63. **Sector-neutral diagnostic:** holdings minus their FF12 sector's equal-weight return, +0.30% a month, t = 1.05 (84 months), which is not significant.
    - By market regime (monthly H027 − SPY): STRONG +0.26% (54 months), NORMAL +0.35% (14), WEAK +1.50% (10), RISK_OFF −1.22% (6).
    - $200K: S_WEALTH 0.194. Top-10: −0.054. Top-20: +0.082.
64. **March 2020 attribution** (included as recorded; nothing removed or winsorised):
    - March 2020 returns: H027 −2.26%, LV15 −4.08%, SPY −12.49%.
    - Against SPY: log-relative +0.111 = **64% of S_WEALTH**.
    - Against LV15: +0.019 = only 5% of H027's lead over LV15.
    - So March 2020 explains most of the SPY advantage but little of the advantage over pure low volatility.
    - Context: February 2020 H027 −8.73% vs SPY −7.92%; April 2020 +9.86% vs +12.70%.

### Confirmations

65. **No feature changed.** The `qr_h024` / `qr_h026` hashes equal the H026 pins (tested), and the feature panel equals the H026 pin in every run.
66. **No target changed.** The response-panel digest equals the H026 pin in every run.
67. **λ grid unchanged:** (0.01, 0.1, 1, 10, 100) (tested). The real λ choices equal H026's.
68. **No regime filter.** There is no regime, crash, trend or SPY filter and no intentional cash. The market regime appears only as a reporting label (item 63).
69. **No H026 result rewritten.** The `p11h026` pins, the E028 runs and `P11_CP1_result.json` are unchanged. The H026 null is not overwritten; the H027 null is separate (E029-02/03).
70. **Holdout untouched.** Nothing from 2022-01-01 → 2026-08-31 was read. `holdout_unlocked` is false in every run.

### Outcome

71. **All-gate result: FAIL.** A1, A2, A3, A5 and A6 pass; **A4 fails** →
    **H027 REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE.**
72. **Final score coefficients:** none. Not qualified, so no final model was fitted (the host fits one only when every gate passes).
73. **Final candidate hash:** none. Not qualified.
74. **Exact next owner decision:** see below.

## Integrity summary

| Item | Value |
|---|---|
| Hypotheses tested in Phase 12 | 1 (H027) |
| Strategies | 1 (S029 v1.0, a subclass of the pinned S028) |
| Experiments | 5 (E029-01 canary; E029-02/03 null; E029-04 rerun; E029-05 real) |
| Orders placed | 0 in every run |
| PIT audit | 0 in every run |
| Engine | LEAN 18178 default build (digest-verified policy) |
| Pre-registered before output | spec + code (577c337); canary checks (577c337); null aggregation (0d39c13); real assessment (a3d3095); c_WEALTH_CONDITIONAL (7793223, merged in PR #89 before E029-05) |
| Disclosure | the real S_WEALTH was already known from H026 when the conditional null was designed; the null procedure, adequacy rule and gates were fixed by the owner (D213) and frozen before any null world |

## Next owner decision

H027 is rejected under the frozen rules. Nothing can be rerun, tuned or relabelled. Please choose one:

1. **Close H027 / Phase 12 as REJECTED** (recommended), and decide whether the programme continues.
   - Across Phases 1–12 no production candidate has been found.
   - The Holdout remains sealed and unused.
2. **A descriptive post-mortem only**, as was done for H026. For example, why 2015–2016 went against the learned score relative to LV15.
   - This would use committed artifacts only: no tuning, no new null and no Holdout.
3. **A new, separately pre-registered hypothesis (H028).**
   - It would need new reasoning that is not motivated by the 2015–2021 results already seen.
   - Any test on 2011–2021 would again be development evidence only.

Do not begin H028 and do not open the Holdout without the owner's explicit instruction.
