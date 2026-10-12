# P13-CP1 — H028 Fixed Strong Shrinkage Learned Stock Score

**Date:** 2026-10-12. **Decisions:** D217 (owner approval), D218 (canary and tolerance), D219 (null and c_WEALTH_H028), D220 (this checkpoint).
**Status:** STOPPED, awaiting the owner.

```
H028 REJECTED —
FIXED STRONG SHRINKAGE DOES NOT
ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM
```

## Short answer

H028 asked one narrow question: if the learned score uses the same strong shrinkage (λ = 100) in every year, with no year-by-year λ selection, does it beat the plain low-volatility portfolio (LV15) robustly over time?

**Almost, but not by the frozen rules.** Five of the six gates pass. The temporal gate B4, which H027 failed, fails again by a small margin.

- **The fix worked where expected.** The only year that changed is 2015, as required.
  - The 2015 model became about 17 times "smaller" (coefficient size 0.009 vs 0.154). H027's 2015 model was dominated by large bets on cash-flow yield, book-to-market and CBOP, and λ = 100 shrank those.
  - The 2015 return improved from −7.7% to −3.5%.
- **But it was not enough.** Holding the 15 calmest stocks (LV15) earned +9.5% in 2015. H028 was still behind LV15 that year (log-relative −0.126) and in 2016 (−0.052).
  - Over 2015–2017 combined, H028 was still slightly behind LV15: **−0.006** (about −0.6%).
  - The rule requires that block to be positive.
- **Everything else passed:**
  - B1: 1 of 5,000 exposure-controlled null worlds did as well (p = 0.0004).
  - B2: H028 ended with $328,295, against $220,156 for LV15.
  - B3: 1.25× SPY and +3.74 points a year.
  - B5: lower risk than SPY.
  - B6: still ahead at doubled slippage.

The gate is not weakened, and no other λ is tried (owner D217, section 31). H028 is preserved exactly as tested. No final score was fitted. The Holdout (2022-01-01 → 2026-08-31) was not touched.

All of this is **development evidence only**. H028 is explicitly post-hoc, designed after seeing the H026/H027 results on the same 2011–2021 data.

| Gate | Requirement | Result | |
|---|---|---|---|
| B1 | S_WEALTH > c_WEALTH_H028 and p ≤ 0.01 | 0.2243 vs 0.0561; p = 0.0004 | ✔ |
| B2 | wealth and CAGR above LV15 | $328,295 vs $220,156; 18.52% vs 11.94% | ✔ |
| B3 | ≥ 1.15 × SPY and ≥ +2 pts (economic requirement) | 1.251× and +3.74 pts | ✔ |
| B4 | ≥ 5 of 7 years ahead of LV15; 2015–17 > 0; 2018–21 > 0 | 5 / 7; **−0.0060**; +0.405 | ✘ |
| B5 | \|MaxDD\| and volatility ≤ 1.25 × SPY | 0.77× and 0.92× | ✔ |
| B6 | 0.20% slippage: above SPY and above LV15 | $310,771 vs $261,801 and $205,500 | ✔ |

## What this means in plain terms

- **Annual λ selection was part of the problem, but not all of it.** Removing it cut the 2015 shortfall against LV15 by about a quarter (−0.171 → −0.126). It turned H028 into a better portfolio overall: more wealth, a higher Sharpe ratio and a lower beta.
- **The deeper problem remains.** In 2015 and 2016, simply holding the calmest stocks beat the learned score, even with its strongest shrinkage.
  - The learned formula already used λ = 100 in 2016 and still lost to LV15 that year.
  - So the instability is not explained by the shrinkage hyperparameter alone. That is the interpretation the owner pre-registered for a failure (D217 section 45).
- **The miss is small, and that does not change the verdict.** −0.006 over three years is less than 1%. It is still a failure under the frozen rule. With one already-seen year carrying the whole difference, a pass would have been fragile evidence anyway.

## Required items

### Governance

1. **Owner decision ID:** D217 (`docs/owner/2026-10-12_p13cp1_h028_fixed_strong_shrinkage.md`, verbatim, recorded before any H028 work). Run decisions: D218, D219 and D220.
2. **H027 permanent status:** REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE. Its pins (`qresearch.p12h027`), null (E029-02/03) and result (`P12_CP1_result.json`) are unchanged, and the pin test checks this.
3. **H028 hypothesis** (`research/hypotheses/H028.md`): one strong-shrinkage rule (λ = 100) fixed from the beginning makes the learned 11-feature score a more temporally stable stock-selection process. It adds robust value beyond LV15 while beating SPY after costs.
4. **Post-hoc / development-only disclosure:**
   - H028 was motivated directly by H026/H027 results on 2011–2021.
   - That data is fully seen. Nothing here is validation, confirmation or out-of-sample proof.
   - The strongest possible status would have been a development candidate.
5. **Data v2.1 manifest:** SHA-256 ef0a7a66… (`research/phase11/data_v21/data_freeze_v21.json`), unchanged and not rebuilt.
6. **D207 owner exception:** NEW_YEARS_MAPPING failed as written. The OWNER-APPROVED EXCEPTION applies (`research/phase11/data_v21/owner_exception_D213.json`). No PIT rule changed.

### Frozen procedure

7. **Frozen features:** MOM, LOWVOL, GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP and EQA. The formulas (`qr_h024`) and the x = 2 × percentile − 1 transform are unchanged; the feature-panel digest equals the H026 pin.
8. **Frozen target:** 63-session TSR minus SPY TSR, cross-sectionally rank-transformed. The label-availability rule is unchanged, and the response-panel digest equals the H026 pin.
9. **Fixed λ = 100:** one Ridge fit per outer year at λ = 100. It was not claimed to be optimal; it is a pre-declared representative of strong shrinkage from the frozen grid.
10. **Proof no λ selection exists:**
    - `qr_h028.run_world_fixed` contains no inner-year loop or λ comparison (unit test on the source).
    - The canary's instrumented call counts show exactly 7 `Fitter.fit` calls, all at λ = 100, and 1 portfolio simulation per world.
    - All 5,000 null worlds and the real run record λ = 100 for all 7 years.
11. **Outer folds:** labels before 2015-01 → test 2015; … ; labels before 2021-01 → test 2021. Each cutoff is the year's first decision review.
12. **Portfolio mechanics:**
    - $100,000 start; Top-15 with equal target allocation and a 10% initial cap;
    - at most 3 per FF12 sector; long only, no leverage;
    - monthly rebalance at the next session's open;
    - no threshold, buffer, stop, regime rule or market timing.
13. **Costs:** $7 per buy and per sell, 0.10% slippage per side.
14. **LV15 definition:** exactly H027 (`qr_h027.lv15`): each month, the 15 eligible stocks with the lowest 60-day volatility, with the same sector cap, sizing, execution and costs. It was not optimised.

### Conditional null

15. **Conditional-null method:**
    - It is H027's null unchanged (`qr_h027.conditional_permuted`).
    - Each stock keeps its own LOWVOL, returns, prices, identity and corporate actions.
    - The ten other features come together from a persistent identity-tether donor.
    - Every world reruns the complete H028 pipeline at λ = 100: seven fits, scores, Top-15 with the sector cap, trading, costs and the SPY comparison.
16. **Null world count:** 5,000 (E030-02: seeds 1–2,500; E030-03: 2,501–5,000), with 0 non-finite values. Panels equal the pins, PIT audit 0, LEAN 18178.
17. **Null determinism:** E030-04 reran seeds 1–25. Every row value (S_WEALTH, wealth, risk, the 7 yearly returns, the 7 λ, the coefficient digest) and every full coefficient vector was identical.
18. **Null adequacy: ADEQUATE in both pre-registered steps.** Worlds at least as defensive as the reference:

    | Measure | Step 1 (vs the real H027) | Step 2 (vs the real H028) |
    |---|---|---|
    | Volatility | 99.2% | 98.0% |
    | MaxDD | 20.5% | 20.5% |
    | Beta | 97.0% | 90.0% |
    | Down-capture | 89.2% | 55.9% |

    Each must be ≥ 1%.
19. **c_WEALTH_H028 = 0.056125732120069** (the 50th largest of 5,000).
    - Null result SHA-256: f5c1401b…
    - Pinned at commit 76f172e and merged in PR #91 before the real run.
    - The 2016–2021 tolerance table (SHA-256 a754d355…) was pinned from the canary before any null world.
    - Null S_WEALTH: median −0.240, 99th percentile +0.056, maximum +0.296.

### 2015: the only year that should change

20. **H028 2015 coefficients (λ = 100):**
    - MOM +0.00089, LOWVOL −0.00240, GPA +0.00247, ACC +0.00219, BM −0.00241, AG −0.00317;
    - REV1M −0.00203, CBOP +0.00082, HI52 +0.00063, CFP +0.00498, EQA −0.00451.
    - Intercept +0.0000041; coefficient norm 0.0091.
21. **H027 2015 coefficients (λ = 0.01):**
    - MOM +0.00596, LOWVOL −0.00690, GPA +0.04008, ACC +0.00396, BM −0.08154, AG −0.01497;
    - REV1M −0.01786, CBOP −0.06693, HI52 +0.00778, CFP +0.09950, EQA +0.01675.
    - Intercept +0.0000098; coefficient norm 0.1537.
22. **2015 coefficient difference** (absolute change; sign change):

    | Feature | Change | Sign change |
    |---|---|---|
    | CFP | 0.0945 | no |
    | BM | 0.0791 | no |
    | CBOP | 0.0678 | **yes** |
    | GPA | 0.0376 | no |
    | EQA | 0.0213 | **yes** |
    | REV1M | 0.0158 | no |
    | AG | 0.0118 | no |
    | HI52 | 0.0072 | no |
    | MOM | 0.0051 | no |
    | LOWVOL | 0.0045 | no |
    | ACC | 0.0018 | no |

    **In plain language:** H027's weakly regularised 2015 model made large bets on a few features (cash-flow yield +, book-to-market −, CBOP −, profitability +). λ = 100 shrank the whole vector about 17-fold and evened it out, and flipped two small signs (CBOP and EQA). The rankings stayed fairly similar: the mean Spearman correlation of the two scores across the 12 months of 2015 is 0.85 (0.82–0.87). The portfolios shared on average 5.4 of 15 holdings (2–8 by month), so most picks still differed.
23. **H028 2015 return:** −3.47%, against −7.72% for H027.
24. **H027 2015 return:** −7.72% (unchanged from E029-05).
25. **2015 difference vs SPY** (SPY +0.73%): log-relative H028 −0.043, against H027 −0.088.
26. **2015 difference vs LV15** (LV15 +9.46%): log-relative H028 **−0.126**, against H027 −0.171. Change caused by λ = 100: +0.045.
    - Also changed in 2015:
      - 2015 MaxDD: H028 −11.8%, H027 −15.9%;
      - 2015 turnover: H028 9.95, H027 8.08 (sum of monthly turnover);
      - year-end 2015 wealth: H028 $96,528, H027 $92,278.

### 2016–2021 equality with H027 (spec section 6)

**EXACT parts: all identical** (bit for bit), for every 2016–2021 month:
- λ = 100 in both;
- intercept and 11 coefficients;
- score vectors and target lists;
- held name sets;
- order counts after the transition month;
- the exact replay reproduces both terminal wealths.

**Transition month** (the 2015-12-31 review, executed in January 2016): H028 needed 14 orders and turnover 0.88 to reach the 2016 targets, against 24 orders and 1.55 for H027. The difference comes from the different December-2015 holdings, as expected.

**PATH-DEPENDENT parts:** the yearly-return differences and the turnover differences (ex transition month) are all within the pinned tolerance. They come only from carried-over position weights and fixed-dollar commissions. The largest weight difference fell from 9.7% of the portfolio (L1) in 2016 to below 0.01% by 2019.

| Item | Year | H028 | H027 | Difference | Tolerance | Result |
|---|---|---|---|---|---|---|
| 27 | 2016 | 6.153% | 5.423% | +0.73 pts | 0.90 pts | ✔ |
| 28 | 2017 | 31.816% | 31.819% | −0.003 pts | 0.42 pts | ✔ |
| 29 | 2018 | 11.631% | 11.593% | +0.04 pts | 0.39 pts | ✔ |
| 30 | 2019 | 27.883% | 27.850% | +0.03 pts | 0.31 pts | ✔ |
| 31 | 2020 | 34.356% | 34.326% | +0.03 pts | 0.33 pts | ✔ |
| 32 | 2021 | 26.890% | 26.879% | +0.01 pts | 0.27 pts | ✔ |

Turnover differences (ex transition): 2016 −0.070 (tolerance 0.184), 2017 +0.005 (0.071), and 2018–2021 below 0.001 (0.025).

### Results

33. **H028 terminal wealth:** $328,294.91.
34. **SPY terminal wealth:** $262,325.46.
35. **LV15 terminal wealth:** $220,156.03.
36. **H028 CAGR:** 18.52%.
37. **SPY CAGR:** 14.78%.
38. **LV15 CAGR:** 11.94%.
39. **S_WEALTH:** 0.22433.
40. **Conditional-null p:** (1 + 1) / 5,001 = **0.0004**. 4,999 of 5,000 worlds are below (99.98th percentile).
41. **B1: PASS.**
42. **B2: PASS.**
43. **B3: PASS** (1.251× and +3.74 pts; an economic requirement carried forward, not new independent evidence).
44. **Years H028 > LV15:** 5 of 7 (2017–2021). Behind in 2015 (−0.126) and 2016 (−0.052).
45. **2015–2017 H028/LV15 compounded:** log-relative **−0.0060** (−0.126 − 0.052 + 0.172).
46. **2018–2021 H028/LV15 compounded:** +0.405.
47. **B4: FAIL** (the 2015–2017 block is negative). The pre-registered "repaired via 2015" disclosure therefore does not apply.
48. **Volatility:** H028 16.23% vs SPY 17.68% (0.92×).
49. **MaxDD:** H028 −26.11% vs SPY −33.72% (0.77×).
50. **B5: PASS.**
51. **Doubled-cost H028 wealth:** $310,771.41 (0.20% slippage per side, same selections, no refit).
52. **Doubled-cost SPY wealth:** $261,801.31.
53. **Doubled-cost LV15 wealth:** $205,499.80.
54. **B6: PASS.**

### Comparison and diagnostics (non-gating; they never rescue a result)

55. **H027 / H028 comparison** (descriptive; neither is chosen after the fact):

    | Metric | H027 | H028 |
    |---|---:|---:|
    | Terminal wealth | $311,397 | $328,295 |
    | CAGR | 17.63% | 18.52% |
    | Excess CAGR vs SPY | +2.85 pts | +3.74 pts |
    | S_WEALTH | 0.1715 | 0.2243 |
    | Null p (own null) | 0.0006 | 0.0004 |
    | MaxDD | −26.12% | −26.11% |
    | Volatility | 16.39% | 16.23% |
    | Beta / down-capture | 0.80 / 0.78 | 0.76 / 0.69 |
    | Years > SPY | 3 | 3 |
    | Years > LV15 | 5 | 5 |
    | 2015–17 vs LV15 | −0.058 | −0.006 |
    | 2018–21 vs LV15 | +0.405 | +0.405 |
    | Mean monthly turnover | 0.619 | 0.632 |
    | Trades | 809 | 827 |

56. **LOWVOL-factor diagnostic** (84 periods, H028 − SPY on the lowest-volatility-quintile factor):
    - α = +0.275% a month (+3.30% a year);
    - Newey-West t(α) = **1.26**, not significant;
    - γ = 0.56; R² = 0.29.

    Other diagnostics:
    - sector-neutral +0.36% a month, t = 1.29 (not significant);
    - regimes (monthly H028 − SPY): STRONG +0.22% (54 months), NORMAL +0.56% (14), WEAK +1.80% (10), RISK_OFF −1.11% (6);
    - $200K: S_WEALTH 0.246. Top-10: 0.095. Top-20: 0.062.
57. **March-2020 diagnostic** (nothing removed):
    - March 2020 returns: H028 −2.26%, LV15 −4.08%, SPY −12.49%.
    - Against SPY: log-relative +0.111 = 49% of S_WEALTH.
    - Against LV15: +0.019 = 5% of H028's lead over LV15.
    - 2020 reproduces H027 within the tolerance (March: H028 −2.257% vs H027 −2.259%).
58. **Memory peak** (the < 6.5 GB engineering target is not met; it is not a gate):

    | Run | Peak |
    |---|---|
    | Canary | 7,789 MB |
    | Null E030-02 | 7,741 MB |
    | Null E030-03 | 7,694 MB |
    | Real | 7,696 MB |

### Confirmations

59. **No λ search after results.** λ = 100 was the only value ever fitted for H028, and no other value was tried after the result.
60. **No other parameter changed.** The `qr_h026`, `qr_h027`, `qr_h024`, `qr_p7_pred`, S028, S029 and X801 hashes equal their pins. Features, target, folds, K, sector cap, mechanics, costs and LV15 are unchanged.
61. **Holdout untouched.** Nothing from 2022-01-01 → 2026-08-31 was read; `holdout_unlocked` is false in every run.

### Outcome

62. **All-gate result: FAIL.** B1, B2, B3, B5 and B6 pass; **B4 fails** →
    **H028 REJECTED — FIXED STRONG SHRINKAGE DOES NOT ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM.**
    The instability was not adequately explained by annual λ selection; the problem is deeper than the shrinkage hyperparameter.
63. **Final coefficients:** none. Not qualified, so no final model was fitted (the host fits one only when every gate passes).
64. **Candidate hash:** none. Not qualified.
65. **Exact next owner decision:** see below.

## Integrity summary

| Item | Value |
|---|---|
| Hypotheses tested in Phase 13 | 1 (H028) |
| Strategies | 1 (S030 v1.0, a subclass of the pinned S029) |
| Experiments | 5 (E030-01 canary; E030-02/03 null; E030-04 rerun; E030-05 real) |
| Orders placed | 0 in every run |
| PIT audit | 0 in every run |
| Engine | LEAN 18178 default build (digest-verified policy) |
| Pre-registered before output | spec + code + canary / null / real scripts (f16b8d2); tolerance table (cefc8d3); c_WEALTH_H028 (76f172e, merged in PR #91 before E030-05) |
| Real run | commit c1cfe24, QC backtest f03e3bdb… |

## Next owner decision

H028 is rejected under the frozen rules. By D217 section 31 it is the final λ-specific experiment for this architecture: no other λ, no wider grid and no automatic H029. Please choose one:

1. **Close H028 / Phase 13 as REJECTED** (recommended).
   - The learned-score line (H026 → H027 → H028) has now reached the point where every further variant would be tuned on already-seen 2015–2021 behaviour.
   - Across Phases 1–13 no production candidate has been found, and the Holdout remains sealed and unused.
2. **A descriptive post-mortem only** (committed artifacts; no new run). For example, why LV15 beat every learned variant in 2015–2016.
3. **A fundamentally different, separately pre-registered direction**, not motivated by these results. Any 2011–2021 test would again be development evidence only.

Do not start H029 and do not open the Holdout without the owner's explicit instruction.
