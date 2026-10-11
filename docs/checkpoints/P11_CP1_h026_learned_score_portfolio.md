# P11-CP1 — H026 Learned Stock Score Portfolio

**Date:** 2026-10-11. **Decisions:** D206 (owner approval), D207 (Data v2.1 freeze), D208 (canary), D209 (null and c_WEALTH), D210 (this checkpoint).
**Status:** STOPPED, awaiting the owner.

## Short answer

H026 asked whether a Ridge-learned, interpretable ranking of the 11 H024 stock characteristics can pick a monthly 15-stock, long-only portfolio that ends 2015–2021 with more money than SPY after costs, without much extra risk.

**Not robustly.** The learned portfolio did end ahead of SPY, with less risk:

- terminal wealth $311,397 vs SPY's $262,325, a ratio of 1.19×;
- CAGR 17.6% vs 14.8%;
- volatility 16.4% vs 17.7%;
- MaxDD −26.1% vs −33.7%.

But two of the five pre-registered gates fail:

- **D1 fails.** The wealth statistic S_WEALTH = ln(1.187) = **0.171** is below the null threshold c_WEALTH = **0.225**. 99 of the 5,000 permuted-feature worlds did at least as well (p ≈ 0.020, against the 1% level set in advance).
- **D3 fails.** H026 beat SPY in only **3 of 7** years, and was behind SPY over 2015–2017 (log-relative −0.068).

```
H026 REJECTED — LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY
```

This is the closest any hypothesis in the programme has come; it is still a rejection under the frozen rules, and no diagnostic can rescue it. Nothing is frozen as a candidate; H026 is preserved exactly as tested. The Holdout (2022-01-01 → 2026-08-31) was not touched.

| Gate | Requirement | Result | |
|---|---|---|---|
| D1 | S_WEALTH > c_WEALTH and > 0 | 0.171 vs 0.225 | ✘ |
| D2 | wealth ≥ 1.15 × SPY and excess CAGR ≥ +2 pts | 1.187× and +2.85 pts | ✔ |
| D3 | ≥ 5 of 7 years ahead; 2015–17 > 0; 2018–21 > 0; no year > 50% of positive | 3 / 7; −0.068; +0.240; 43% | ✘ |
| D4 | \|MaxDD\| and vol ≤ 1.25 × SPY | 0.77× and 0.93× | ✔ |
| D5 | same picks at 0.20% slippage still beat SPY | $295,028 vs $261,801 | ✔ |

## What this means in plain terms

- **The result is not distinguishable from luck at the level we set.** When the 11 characteristics are shuffled between stocks and the whole procedure is rerun, about 2% of those meaningless worlds beat SPY by at least as much. The pre-registered bar was 1%.
- **The excess return is concentrated.** Almost all of it comes from 2017, 2018 and 2020. H026 trailed SPY in 2015, 2016, 2019 and 2021.
- **Ridge mostly chose the strongest penalty.** λ = 100 was chosen for 2016–2021, so the model is a heavily shrunk tilt rather than a sharp formula. It consistently favoured:
  - lower volatility;
  - lower book-to-market (growth);
  - higher gross profitability;
  - prices near the 52-week high;
  - recent one-month losers;
  - lower asset growth.

  Over 2015–2021 that tilt resembles a "quality-growth, low-volatility" portfolio, a style that did well in those years. A style bet that paid off in one seven-year window is exactly what the null and D3 are designed to catch.
- **Two diagnostics point the same way:**
  - the Top-10 version of the same coefficients trailed SPY (S_WEALTH −0.054);
  - the sector-neutral relative return is small and not significant (+0.30%/month, t 1.05).

## The 77 items

### Status and data

1. **Owner decision:** D206 (`docs/owner/2026-10-11_p11cp1_h026_learned_score_portfolio.md`, verbatim).
2. **H022–H025 remain closed.** H022 is REJECTED (E024-07), H023 has NO ROBUST SCORE V2 CANDIDATE (E025-08), H024 has NO ROBUST FEATURE MODEL (E026-08), and H025 is REJECTED (E027-06). None was rerun or modified.
3. **Data v2.1 extension method:**
   - The frozen Data v2 builder is reused with one parameter changed, the cut-off moved from 2017-12-31 to 2021-12-31 (`research/phase11/data_v21/build_data_v21.py`).
   - It produces the packed table `qr_data_v21*.py`: 22 files; 3,941 SEC registrants; 148,378 filings; 103,209 cover-page share counts; 168 SEC requests.
   - Cached SEC snapshots are filtered to dates ≤ 2021-12-31 before use.
   - Host X801 is the frozen X998 with five line-level changes only, asserted by `tests/test_p11_data_v21.py`.
   - Every Data v2 rule is unchanged.
4. **Data v2.1 manifest:**
   - Manifest `research/phase11/data_v21/data_freeze_v21.json`, SHA-256 **ef0a7a66…**, pinned in `qresearch.datafreeze_v21`.
   - Status: "FROZEN — NEW_YEARS_MAPPING FAILED AS WRITTEN (SPECIFICATION ERROR, D207)".
   - Table SHA-256 07884f7b…; review calendar 59616e42… (131 reviews, 2011-01-31 … 2021-11-30).
   - LEAN build 18178 for every run.
5. **2011–2017 reproduction:**
   - Eligibility digests equal the frozen Data v2 (E998-01) on **84/84** reviews.
   - H022 population 34,847 vs frozen 34,863 stock-months (**−16, −0.05%**). The difference sits in the 12 decisions 2016-12 … 2017-11, 1–3 per review. Its cause is the restatement guard, which now sees 2018–2021 restatements and holds back vendor values that equal a later restated figure. Same rule, more knowledge. Judged not material.
   - H024 population 34,815 vs 34,831 (−0.05%). The exact frozen digests differ for that reason.
   - Score-row digests also differ for the 12 reviews 2011-02 … 2012-01. That is the documented QuantConnect snapshot change (D202); population counts there are identical.
   - **Disclosed own-gate error (D207).** Gate NEW_YEARS_MAPPING (threshold 0.90) failed as written. Its counter includes vendor reports for companies with no SEC identity, so it reads 0.51–0.60 even in the frozen years, with identical values in E998-01 and E801-01. Among reports with an SEC identity, the mapped share is 0.95–0.97 in 2018–2021 vs 0.96–0.98 in 2011–2017. The gate is kept as FAILED, not relabelled. **If you do not accept this, Data v2.1, and therefore this result, is invalid and would be H026 BLOCKED.**
6. **2018–2021 coverage:**

   | Period | Eligible per review | Fully scored per review | H022 population per review | SEC-repaired per review | Survivor share |
   |---|---|---|---|---|---|
   | 2011–2017 | 1,076 | 551 | 422 | 160 | 0.71–0.83 |
   | 2018 | 1,320 | 770 | 528 | 128 | 0.85 |
   | 2019 | 1,325 | 784 | 531 | 93 | 0.90 |
   | 2020 | 1,322 | 783 | 478 | 72 | 0.93 |
   | 2021 | 1,667 | 944 | 768 | 63 | 0.94 |

   Survivor share is the share of stock-months whose security is still in the universe at the final review. It naturally rises towards the end.
7. **PIT audit:** 0 on every counter in all 9 QuantConnect runs (E801-01..04, E028-01..05).
8. **Identity audit:**
   - The identity residual (no SEC identity, or rejected identity) is 3.4–6.9% of eligible stock-months a year in 2011–2017, identical to the frozen Data v2 and accepted under D192.
   - In 2018–2021 it is 5.4–6.8%, inside the accepted range.
9. **Corporate-action audit:**
   - SEC split check: 352 continuous, 1 ambiguous, 53 without SEC identity, 14 without SEC market cap.
   - 300 sampled feature rows recomputed from full histories: 0 mismatches.
   - The SPY total-return series carries 60 dividends and has no missing session since 2010.
   - Delistings are held at the last real close and become cash, as in the frozen conventions.
   - Market cap from the SEC method agrees with QuantConnect within 2% for 141,202 of 166,311 records.

### Model

10. **Features:** MOM, LOWVOL, GPA, ACC, BM, AG, REV1M, CBOP, HI52, CFP, EQA, exactly as in H024.
11. **Feature-formula hashes:**
    - `qr_h024.py` f9b1c87e… (unchanged since H024);
    - `qr_p7_pred.py` bc6fd8e8…;
    - `qr_h026.py` 3b6249d4…;
    - host S028 c49902d9…;
    - X801 dc75e9fd…;
    - spec 3c292885….
12. **Feature coverage (all 11 valid, share of the H022 population):** 99.82–99.98% every year from 2011 to 2021. The 25% STOP rule was not triggered.
13. **Target:** total shareholder return from the next session's open to the close of the 63rd session, minus SPY's total return over the same rows. It is converted to a within-review percentile y = 2p − 1.
14. **Label availability:** an observation trains a model with cutoff T only if its label exit date is strictly before T. This was checked at all 9 cutoffs with 0 violations; training months per cutoff run 20 (2013) … 117 (2021).
15. **Ridge:** minimise Σ_t Σ_i w_ti (y_ti − β0 − x_ti·β)² + λ Σ_j β_j², with w_ti = 1/N_t. The intercept is not penalised. It is solved in closed form on weighted-centred data.
16. **λ grid:** {0.01, 0.1, 1, 10, 100}.
17. **Weighting:** every review month carries equal total weight (1/N_t per stock).
18. **Outer folds:** test years 2015…2021. Year Y covers the 12 reviews December Y−1 … November Y. Coefficients are fitted once at the December Y−1 review and frozen for the year.
19. **Inner folds:** inner test years 2013 … Y−1, each simulated as a Top-15 portfolio from $100,000 cash and liquidated at year end.
20. **Selection objective:** Σ_k ln(W_k(λ) / SPY_k) after costs. Ties go to (1) the better worst year, (2) the larger λ, (3) numeric order.

### Canary and null

21. **Canary E028-01:** 13/13 checks pass (D208). The checks and tolerances were committed before the output.
    - Synthetic planted world S_WEALTH +1.47 vs zero-coefficient world −1.41.
    - Peak memory 7.87 GB.
22. **Null method:** the identity tether (`qr_p7_pred.Tether`) reassigns each stock the complete 11-feature vector of a partner stock at every review. Every world reruns inner λ selection, the annual fits, scores, the Top-15 portfolio, costs and the SPY comparison. Labels and prices stay with the stock.
23. **Null worlds:** 5,000 (E028-02 seeds 1–2,500, E028-03 seeds 2,501–5,000).
24. **Determinism:** the independent rerun E028-04 (seeds 1–25) reproduces every value exactly. All runs share the same feature panel (10a54163…) and response panel (e1503f9c…).
25. **Null S_WEALTH distribution:**
    - mean −0.228, median −0.230, SD 0.194;
    - 95th percentile +0.094, 99th +0.223, maximum +0.438;
    - 11.7% of worlds end above SPY;
    - median null excess CAGR −3.7 points.
26. **c_WEALTH = 0.22454658**, the 50th largest of 5,000 (about 1.25× SPY wealth). It was pinned and merged (PR #86, threshold commit 8024d90) before the real run.

### Real run E028-05 (the one 2015–2021 evaluation)

27–28. **λ and coefficients by year** (raw, unoriented feature percentiles; a negative LOWVOL coefficient means preferring low volatility):

| Year | λ | MOM | LOWVOL | GPA | ACC | BM | AG | REV1M | CBOP | HI52 | CFP | EQA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2015 | 0.01 | +0.006 | −0.007 | +0.040 | +0.004 | −0.082 | −0.015 | −0.018 | −0.067 | +0.008 | +0.099 | +0.017 |
| 2016 | 100 | +0.001 | −0.004 | +0.004 | +0.001 | −0.005 | −0.003 | −0.001 | +0.001 | +0.002 | +0.002 | −0.004 |
| 2017 | 100 | −0.001 | −0.006 | +0.002 | +0.002 | −0.004 | −0.004 | −0.003 | +0.001 | +0.002 | +0.003 | −0.004 |
| 2018 | 100 | −0.002 | −0.007 | +0.003 | −0.001 | −0.005 | −0.002 | −0.002 | +0.002 | +0.003 | +0.001 | −0.004 |
| 2019 | 100 | −0.002 | −0.007 | +0.006 | +0.002 | −0.007 | −0.002 | −0.001 | +0.003 | +0.004 | −0.002 | −0.003 |
| 2020 | 100 | −0.004 | −0.008 | +0.006 | 0.000 | −0.009 | −0.001 | −0.002 | +0.002 | +0.003 | −0.003 | −0.005 |
| 2021 | 100 | −0.003 | −0.005 | +0.007 | 0.000 | −0.012 | +0.002 | −0.001 | +0.003 | +0.002 | −0.008 | −0.004 |

29. **Coefficient stability:**
    - The same sign every year: LOWVOL (−), BM (−), REV1M (−), GPA (+), HI52 (+).
    - MOM, AG, ACC, CBOP, CFP and EQA flip sign once or twice.
    - Adjacent-year coefficient correlation: 0.50 for 2015→16 (λ changed from 0.01 to 100), then 0.88–0.98.

30–32. **Annual returns** (L = log of H026 relative to SPY):

| Year | H026 | SPY | L |
|---|---|---|---|
| 2015 | −7.7% | +0.7% | −0.088 |
| 2016 | +5.4% | +12.0% | −0.061 |
| 2017 | +31.8% | +21.7% | +0.080 |
| 2018 | +11.6% | −4.6% | +0.156 |
| 2019 | +27.9% | +31.2% | −0.026 |
| 2020 | +34.3% | +18.3% | +0.127 |
| 2021 | +26.9% | +29.1% | −0.017 |

33. **H026 terminal wealth:** $311,397 (from $100,000, after all costs and the final liquidation).
34. **SPY terminal wealth:** $262,325.
35. **Wealth ratio:** 1.187.
36. **H026 CAGR:** 17.63%.
37. **SPY CAGR:** 14.78%.
38. **Excess CAGR:** +2.85 points a year.
39. **S_WEALTH_real:** 0.1715.
40. **Null percentile:** 98.0%. 99 of 5,000 worlds are ≥ 0.1715, p ≈ 0.020.
41. **D1: FAIL.** 0.171 < 0.225.
42. **Years beating SPY:** 3 of 7 (2017, 2018, 2020).
43. **2015–2017 relative:** Σ L = −0.068.
44. **2018–2021 relative:** Σ L = +0.240.
45. **Largest single year (2018):** 43% of the positive log-relative total.
46. **D2: PASS.** 1.187 ≥ 1.15, and +2.85 ≥ +2.0 points.
47. **D3: FAIL.** 3 < 5 years, and the 2015–2017 sum is negative.
48. **H026 volatility:** 16.4%.
49. **SPY volatility:** 17.7%.
50. **H026 MaxDD:** −26.1%.
51. **SPY MaxDD:** −33.7%.
52. **Time underwater:** H026 spent 85.4% of sessions below its running peak (longest spell 410 sessions). SPY spent 83.3% (longest 187 sessions). H026's longest spell runs 2015-07-15 → 2017-02-28 (SPY's 2015-07-21 → 2016-04-15).
53. **D4: PASS.** MaxDD 0.77× SPY's and volatility 0.93× SPY's.
54. **Turnover:** 62% of equity traded per monthly rebalance, about 7.4× a year.
55. **Trades:** 809 (407 buys, 402 sells).
56. **Commissions:** $5,663.
57. **Slippage cost:** $7,830.
58. **At 0.20% slippage:** H026 ends at $295,028 vs SPY's $261,801.
59. **D5: PASS.**
60. **Average holdings:** 15.0.
61. **Cash utilisation:** 99.6% (mean cash 0.4%).
62. **Sector concentration** (FF12 picks over 84 rebalances):
    - largest sector Shops at 18.7%, then Other 18.3%, BusEq 15.3%, Manuf 12.9%, Hlth 11.5%;
    - the cap of 3 per sector was always respected.
63. **$200K diagnostic:** wealth $636,695 vs $524,676 (S_WEALTH +0.194, CAGR 18.0%).
64. **Top-10 diagnostic:** $248,475 vs $262,325. S_WEALTH −0.054; it trails SPY.
65. **Top-20 diagnostic:** $284,884 vs $262,325 (S_WEALTH +0.082).
    - **Sector-neutral:** +0.30% a month vs sector peers, t 1.05.
    - **Market regime** (mean monthly relative return): STRONG +0.26% (54 months), NORMAL +0.35% (14), WEAK +1.50% (10), RISK_OFF −1.22% (6).
    - These diagnostics are non-gating and cannot rescue the result.
66. **Final all-gate result:** FAIL (D1 and D3).
67. **Final λ:** none (not qualified).
68. **Final coefficients:** none (not qualified; the final-model step was not run).
69. **Candidate hash:** none.
70. **No retraining after development.** The yearly coefficients are the walk-forward fits; nothing was refitted after the result.
71. **No new feature.** The 11 H024 features only, formulas unchanged.
72. **Target unchanged.** 63 sessions throughout.
73. **No K optimisation.** K = 15. Top-10 and Top-20 are diagnostics only.
74. **Holdout untouched.** No 2022+ price, fundamental, SEC filing or benchmark value was read. The table holds nothing after 2021-12-31, and the host refuses later history.
75. **Nothing purchased.** QuantConnect $24/month only.
76. **Final status:**

```
H026 REJECTED —
LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY
```

77. **Exact next owner decision.** Please choose one:
    - **(A) Recommended: close H026 / Phase 11 as REJECTED**, preserved exactly as tested.

      Per D206 §53, no λ, feature, sign, target, K, sector cap or model class changes, and no Holdout.

      Note on the near miss: any variant would be a new hypothesis (H027+). It would be tuned on the same 2011–2021 data that has now been seen. Its first-year weakness and its concentration in three years are the usual signature of a style tilt, not of a robust selection edge.
    - **(B) Reject the D207 Data v2.1 freeze** (the NEW_YEARS_MAPPING specification error). In that case this result is void and the status becomes H026 BLOCKED. You would then decide whether to rebuild the audit.
    - **(C) A new research direction** (a new phase, with its own pre-registration). The Holdout stays sealed in every option.

## What is new in the infrastructure (kept for later work)

- **Data Infrastructure v2.1:** the frozen Data v2 rules through 2021-12-31, pinned (D207).
- **Pure module `qr_h026`:** weighted Ridge from per-month sufficient statistics, nested walk-forward, the Top-15 portfolio simulator with costs, and SPY comparison.
- **Full-pipeline null:** about 0.14 s per world.
- **Host S028:** subclass of the X801 host, with canary, null and real modes.
- **Memory:** peaks were 7.6–8.2 GB, at the backtest node's limit. Any heavier host needs memory work first.

## Files

- **Owner decision:** `docs/owner/2026-10-11_p11cp1_h026_learned_score_portfolio.md`.
- **Spec and hypothesis:** `research/phase11/H026_spec.md`, `research/hypotheses/H026.md`.
- **Pins:** `src/qresearch/p11h026.py`, `src/qresearch/datafreeze_v21.py`.
- **Data v2.1:** `research/phase11/data_v21/` (builder, configs, audit analysis, summary, manifest), `src/qresearch/lean/qr_data_v21*.py`, `strategies/X801_data_v21_export/main.py`.
- **Model and host:** `src/qresearch/lean/qr_h026.py`, `strategies/S028_h026_learned_score/main.py`.
- **Analysis:** `research/phase11/cp1/P11_CP1_{configs,canary,null,result}.py` and their JSON outputs.
- **Tests:** `tests/test_p11_*.py`, `tests/test_data_freeze_v21.py`.

## Totals

- **Programme:** 26 hypotheses (H001–H026).
- **This phase:**
  - 1 hypothesis (H026);
  - 2 hosts (X801 data export, S028);
  - 9 experiments: E801-01..04 and E028-01..04 are infrastructure, E028-05 is research.
- All runs are logged in `experiments/INDEX.csv`.
