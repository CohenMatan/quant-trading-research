# P11-CP2 — H026 Post-Mortem and Performance Attribution

**Date:** 2026-10-11. **Decisions:** D211 (owner: descriptive post-mortem only), D212 (this checkpoint).
**Status:** STOPPED, awaiting the owner.

```
H026 FORMAL RESULT:
REJECTED
```

This post-mortem cannot alter H026's status. The attractive wealth result does not turn D1 or D3 into passes. The 1% threshold is unchanged, and p ≈ 0.02 is not a pass.

## Short answer

**Where the $49K came from.**

- **Market declines.** All of H026's lead over SPY was earned in the 24 months when SPY fell (log-relative +0.202). In the 60 months when SPY rose, H026 lost slightly relative to SPY (−0.030).
- **Two episodes.** March 2020 alone is worth +0.111, which is 64% of the final S_WEALTH of 0.171. February–July 2020 is worth +0.173, more than the whole seven-year total. 2018 (a year SPY fell) and 2020 together are 78% of the positive yearly log-relative wealth.
- **Steady outside those episodes.** Outside them H026 roughly tracked SPY or lagged it. It trailed SPY in 2015, 2016, 2019 and 2021, and was 14% behind at the end of 2016.

**What Ridge learned.**

- A stable, heavily shrunk, defensive tilt: low volatility, low book-to-market (growth), high gross profitability, low equity/assets, and prices near the 52-week high.
- From 2016 on the formula hardly changed: adjacent-year correlation 0.88–0.98, and λ = 100 (the largest allowed) in every year.
- The same formula lost to SPY in some years and beat it in others. That pattern fits an exposure that pays off in sell-offs better than a stock-picking effect that grew over time.

**How it compares with the 5,000 null worlds.**

- **Wealth:** at the 98th percentile (99 worlds at least as rich). This is the pre-registered statistic, and it fails.
- **Risk:** far outside the null. Every null world had higher volatility than H026, and only 1 of 5,000 had a MaxDD as shallow. None of the 99 null worlds that matched H026's wealth had a MaxDD as shallow.

The likely reason is mechanical. The null shuffles feature vectors between stocks, so it cannot reproduce a deliberate low-volatility tilt. The risk result therefore shows the model reliably picked steadier stocks. It is not evidence of return-predicting skill. These are post-hoc descriptive counts, not a new test.

**H027 feasibility: B.** The effect is interesting but concentrated. Any further work needs a materially different formulation, above all one that separates stock-selection skill from a defensive low-beta exposure. Three concepts are listed in item 53; none is chosen or built.

**What could not be computed.** E028-05 did not export security-level holdings, trades, scores or the feature percentiles of the selected stocks. The items that need them are marked NOT COMPUTED, because D211 does not authorise a new QuantConnect run to obtain them. They are items 16–21, 26–28, 36–38, parts of 39–40, and the per-security parts of 45–46.

All numbers come from `research/phase11/cp2/P11_CP2_postmortem.json`, produced by `research/phase11/cp2/P11_CP2_postmortem.py` from committed artifacts only:
- the E028-05 result;
- the E028-02/03 null rows;
- the Data v2.1 audit summary;
- the H024 canary's 2011–2017 feature correlations, used for one approximation.

---

## The 60 items

### Status and governance

1. **Owner decision:** D211 (`docs/owner/2026-10-11_p11cp2_h026_postmortem.md`, verbatim).
2. **H026 formal status:** **REJECTED — LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY** (P11-CP1, D210). Unchanged.
3. **D1–D5 as originally recorded:**

   | Gate | Result | |
   |---|---|---|
   | D1 | S_WEALTH 0.1715 vs c_WEALTH 0.2245 (p 0.020) | **FAIL** |
   | D2 | 1.187× wealth, +2.85 points CAGR | PASS |
   | D3 | 3 of 7 years ahead; 2015–17 log-relative −0.068 | **FAIL** |
   | D4 | MaxDD 0.77×, volatility 0.93× SPY's | PASS |
   | D5 | $295,028 vs $261,801 at 0.20% slippage | PASS |
4. **Data v2.1 governance note.** One Data v2.1 integrity criterion, NEW_YEARS_MAPPING, failed as written. The failure came from the criterion's denominator, not from the data. Claude froze Data v2.1 anyway under D207, as its own judgement. Nothing in Data v2.1 was changed or rebuilt for this checkpoint; `tests/test_p11_cp2_postmortem.py` checks the pinned manifest hash.
5. **D207 status.** The manifest status is "FROZEN — NEW_YEARS_MAPPING FAILED AS WRITTEN (SPECIFICATION ERROR, D207)". **No owner approval exists.** D207 is Claude's decision, not an owner-approved exception, and the issue is unresolved (item 60, decision 1). The original failed criterion is preserved, and so is D207.
6. **Original criterion:**
   - Measured: share of new vendor fundamental reports whose period maps to an SEC filing, out of **all** new reports.
   - Required: at least 0.90 in each of 2018–2021.
7. **Intended denominator:** the same share, but out of new reports of companies that **have** an SEC identity row.
   - A company with no SEC identity row can never map.
   - Under Data v2 such companies never feed fundamentals, so they are outside the scope the criterion was meant to check.
8. **Impact of the denominator error:**

   | Year | As written | With SEC identity | Frozen Data v2 (E998-01) |
   |---|---|---|---|
   | 2011 | 0.511 | 0.983 | 0.511 / 0.983 |
   | 2014 | 0.580 | 0.964 | identical |
   | 2017 | 0.590 | 0.976 | identical |
   | 2018 | 0.584 | **0.969** | (not covered) |
   | 2019 | 0.583 | **0.972** | |
   | 2020 | 0.581 | **0.972** | |
   | 2021 | 0.521 | **0.948** | |

   The as-written share is about 0.5–0.6 even in the frozen Data v2 years, with values identical to E998-01. So 0.90 could never have been met on that denominator. On the intended denominator the 2018–2021 shares are within 0.015–0.035 of the 2011–2017 range.

   **Real impact: none on data.** The criterion is a counter. It does not filter, move or alter any data row.
9. **2011–2017 population change:**
   - The H022 population is 34,847 stock-months vs the frozen 34,863: −16, or **−0.046%**.
   - The change falls in the 12 decisions 2016-12 … 2017-11, 1–3 per review.
   - Cause: the restatement guard now sees 2018–2021 restatements. It holds back a vendor value that equals a later restated figure until that restatement is public. Same rule, more knowledge.
   - The H024 population moves 34,831 → 34,815.
   - Score digests also differ for 2011-02 … 2012-01. That is the QuantConnect snapshot change documented in D202; population counts there are identical.
10. **Were H026 holdings affected?**
    - **Denominator error: no.** It changed no data.
    - **Population change: not determinable from committed artifacts.** The 16 removed stock-months sit inside the 2017 outer test year. Holdings were not exported, and Data v2 cannot run 2018–2021, so no counterfactual exists. Measuring it would need a new counterfactual run, which was not done.
    - **Rough scale (an expectation, not a measurement):** if those 16 stock-months had ranked like typical members of a ~550-stock population, they would have filled about 16 × 15/550 ≈ 0.4 of the 180 position-months in 2017.
    - Their removal also changes the 2017-and-later training sets by fewer than 0.05% of observations.

### Where the advantage came from

11. **Monthly relative wealth** (H026 wealth ÷ SPY wealth; start = 1.0; quarter-ends shown, all 84 months in the JSON):

    | | Mar | Jun | Sep | Dec |
    |---|---|---|---|---|
    | 2015 | 1.035 | 1.018 | 0.960 | 0.916 |
    | 2016 | 0.932 | 0.958 | 0.893 | 0.862 |
    | 2017 | 0.874 | 0.886 | 0.901 | 0.934 |
    | 2018 | 0.941 | 0.979 | 1.014 | 1.092 |
    | 2019 | 1.040 | 1.054 | 1.095 | 1.064 |
    | 2020 | 1.192 | 1.233 | 1.250 | 1.208 |
    | 2021 | 1.150 | 1.198 | 1.159 | 1.187 |

12. **Annual table:**

    | Year | H026 | SPY | Relative (arith.) | Relative (log) | Start rel. | End rel. | Vol H026 / SPY | MaxDD H026 / SPY |
    |---|---|---|---|---|---|---|---|---|
    | 2015 | −7.7% | +0.7% | −8.5 pts | −0.088 | 1.000 | 0.916 | 15.8% / 15.5% | −15.9% / −11.9% |
    | 2016 | +5.4% | +12.0% | −6.6 | −0.060 | 0.916 | 0.862 | 12.2 / 13.1 | −9.4 / −10.2 |
    | 2017 | +31.8% | +21.7% | +10.1 | +0.080 | 0.862 | 0.934 | 7.2 / 6.7 | −2.0 / −2.6 |
    | 2018 | +11.6% | −4.6% | +16.2 | +0.156 | 0.934 | 1.092 | 14.5 / 17.0 | −12.7 / −19.4 |
    | 2019 | +27.9% | +31.2% | −3.4 | −0.026 | 1.092 | 1.064 | 12.0 / 12.5 | −4.8 / −6.6 |
    | 2020 | +34.3% | +18.3% | +16.0 | +0.127 | 1.064 | 1.208 | 29.0 / 33.4 | −26.1 / −33.7 |
    | 2021 | +26.9% | +29.1% | −2.2 | −0.017 | 1.208 | 1.187 | 15.2 / 13.0 | −9.5 / −5.1 |

13. **Annual contribution to S_WEALTH = ln(311,397 / 262,325) = 0.17148:**

    | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | Final liquidation costs | **Sum** |
    |---|---|---|---|---|---|---|---|---|
    | −0.0877 | −0.0605 | +0.0798 | +0.1564 | −0.0260 | +0.1267 | −0.0170 | −0.0003 | **0.17148** (exact, tested) |

14. **Winning and losing years:**
    - Verified from the committed result: winning years are **2017, 2018, 2020**; losing years are **2015, 2016, 2019, 2021**.
    - **Same mechanics every year:**
      - always 15 holdings;
      - cash utilisation 98.6–100%;
      - turnover 7.2–9.1× a year (4.6× in 2021, which has 11 rebalances in-window);
      - λ = 100 in every year except 2015 (λ = 0.01).
    - **Market environment:**
      - The winning years were two in which SPY fell or had a sharp drawdown (2018: SPY −4.6%, MaxDD −19.4%; 2020: MaxDD −33.7%), plus 2017.
      - The losing years include the two strongest SPY up-years (2019 +31%, 2021 +29%) and 2016's rebound.
    - **H026 volatility vs SPY:** lower in 2016, 2018, 2019 and 2020; higher in 2015, 2017 and 2021.
    - **Characteristics of selected stocks: NOT COMPUTED** (selected-stock features were not exported; see item 21). The yearly coefficients are in item 22.
15. **Rolling H026 minus SPY returns** (month-end marks; descriptive only, no gates):

    | Window | Windows | Median | % > 0 | p10 | p25 | p75 | p90 | Min | Max |
    |---|---|---|---|---|---|---|---|---|---|
    | 3 months | 82 | +1.4% | 59% | −5.1% | −1.9% | +3.5% | +4.5% | −10.9% | +13.9% |
    | 6 months | 79 | +2.0% | 61% | −6.8% | −3.1% | +5.7% | +9.3% | −11.8% | +19.3% |
    | 12 months | 73 | +5.0% | 56% | −8.5% | −5.7% | +11.9% | +16.1% | −11.7% | +22.7% |
    | 24 months | 61 | +17.4% | 79% | −14.4% | +2.7% | +24.4% | +27.9% | −18.6% | +34.5% |

### Security level (not available)

16. **Top 20 positive securities:** NOT COMPUTED — not in the committed E028-05 artifacts. E028-05 exported no security-level holdings, trades or P&L; its order and trade files are empty because the host simulates the portfolio in-memory. Obtaining these would need a new QuantConnect export run of the frozen pipeline, which D211 does not authorise.
17. **Top 20 negative securities:** NOT COMPUTED, same reason.
18. **Profit concentration by security or holding episode:** NOT COMPUTED, same reason.
    - Period concentration (computed instead):
      - best month (2020-03) = 64% of S_WEALTH and 13% of the sum of positive monthly contributions;
      - best 3 months = 118% of S and 24% of positive months;
      - best 6 months = 183% of S and 37% of positive months;
      - best consecutive 6 months (2020-02 … 2020-07) = +0.173;
      - best year 2018 = 43% of positive years; best two years (2018 + 2020) = 78%.
    - Worst periods: worst month 2021-01 (−0.052); worst 3 consecutive months 2020-11 … 2021-01 (−0.101); worst year 2015 (−0.088).
    - 45 of 84 months were positive. Positive months sum to +0.860 and negative months to −0.688.
19. **Holding win/loss distribution:** NOT COMPUTED (no holding ledger was exported).
20. **Monthly breadth of success:** NOT COMPUTED (per-holding returns were not exported).
    - Portfolio-level substitute: H026 beat SPY in 45 of 84 months.
    - The non-gating sector-neutral diagnostic from E028-05: holdings beat their own FF12 sector's equal-weight return by +0.30% a month, t 1.05.

### What Ridge learned

21. **Feature exposures of selected stocks vs the universe:** NOT COMPUTED (selected-stock feature percentiles were not exported). Coefficients are the only committed view of the model's tilt (items 22 and 39–40).
22. **Annual Ridge coefficients:**
    - λ, intercept and the 11 coefficients by year are in the P11-CP1 table and the JSON.
    - **L2 norm:** 2015 0.154; 2016 0.0099; 2017 0.0105; 2018 0.0109; 2019 0.0137; 2020 0.0156; 2021 0.0180. The 2015 vector is about 10× larger because its λ was 0.01.
    - Intercepts are all below 1e-5, as expected with centred labels.
    - **Per-feature statistics (2015–2021):**

      | Feature | Mean | Median | SD | Min | Max | + years | − years | Sign flips | Mean \|β\| |
      |---|---|---|---|---|---|---|---|---|---|
      | BM | −0.0176 | −0.0073 | 0.0284 | −0.0815 | −0.0036 | 0 | 7 | 0 | 0.0176 |
      | CFP | +0.0133 | +0.0012 | 0.0382 | −0.0081 | +0.0995 | 4 | 3 | 1 | 0.0170 |
      | CBOP | −0.0080 | +0.0015 | 0.0260 | −0.0669 | +0.0030 | 6 | 1 | 1 | 0.0112 |
      | GPA | +0.0097 | +0.0060 | 0.0135 | +0.0022 | +0.0401 | 7 | 0 | 0 | 0.0097 |
      | LOWVOL | −0.0061 | −0.0067 | 0.0013 | −0.0078 | −0.0040 | 0 | 7 | 0 | 0.0061 |
      | EQA | −0.0011 | −0.0041 | 0.0079 | −0.0046 | +0.0168 | 1 | 6 | 1 | 0.0059 |
      | AG | −0.0035 | −0.0019 | 0.0054 | −0.0150 | +0.0019 | 1 | 6 | 1 | 0.0040 |
      | REV1M | −0.0040 | −0.0019 | 0.0061 | −0.0179 | −0.0009 | 0 | 7 | 0 | 0.0040 |
      | HI52 | +0.0035 | +0.0029 | 0.0021 | +0.0017 | +0.0078 | 7 | 0 | 0 | 0.0035 |
      | MOM | −0.0007 | −0.0018 | 0.0034 | −0.0045 | +0.0060 | 2 | 5 | 1 | 0.0027 |
      | ACC | +0.0011 | +0.0012 | 0.0016 | −0.0010 | +0.0040 | 6 | 1 | 2 | 0.0014 |

    - **Rank by mean |β|** (descriptive, not feature selection): BM, CFP, CBOP, GPA, LOWVOL, EQA, AG, REV1M, HI52, MOM, ACC. The ranking is dominated by the 2015 λ = 0.01 fit.
    - **Scale-free view (2016–2021, unit-normalised weights):** BM −0.51, LOWVOL −0.47, GPA +0.35, EQA −0.33, HI52 +0.22, AG −0.16, CBOP +0.14, REV1M −0.14, MOM −0.12, ACC +0.06, CFP −0.03.
    - Features are raw and unoriented. A negative LOWVOL coefficient means preferring lower 60-day volatility; a negative BM coefficient means preferring a lower book-to-market ratio.
23. **Coefficient stability** (adjacent years):

    | | 2015–16 | 2016–17 | 2017–18 | 2018–19 | 2019–20 | 2020–21 |
    |---|---|---|---|---|---|---|
    | Pearson | 0.50 | 0.91 | 0.88 | 0.91 | 0.98 | 0.89 |
    | Spearman | 0.61 | 0.88 | 0.85 | 0.90 | 0.97 | 0.90 |
    | Cosine | 0.50 | 0.91 | 0.89 | 0.91 | 0.96 | 0.90 |
    | L2 distance | 0.149 | 0.0044 | 0.0050 | 0.0060 | 0.0044 | 0.0078 |

    - **Each year vs the mean of unit-normalised vectors (Pearson):** 2015 0.50, 2016 0.95, 2017 0.86, 2018 0.94, 2019 0.96, 2020 0.92, 2021 0.74.
    - Against the plain mean vector, the correlation falls steadily from 0.94 to 0.37. That trend is an artefact: the 2015 vector dominates the plain mean.
    - **Reading:** 2016–2021 is a **stable formula with mild parameter movement**. 2015 (λ = 0.01) is a materially different model.
24. **λ frequency:**

    | λ | 0.01 | 0.1 | 1 | 10 | 100 |
    |---|---|---|---|---|---|
    | Folds | 1 (2015) | 0 | 0 | 0 | 6 (2016–2021) |

25. **Inner objective** (Σ inner-year ln(W/SPY) after costs):

    | Outer year | 0.01 | 0.1 | 1 | 10 | 100 | Chosen | Margin over runner-up |
    |---|---|---|---|---|---|---|---|
    | 2015 | **0.122** | 0.103 | 0.061 | 0.064 | 0.086 | 0.01 | 0.019 |
    | 2016 | 0.034 | 0.005 | −0.075 | −0.028 | **0.042** | 100 | 0.009 (effectively tied with 0.01) |
    | 2017 | −0.062 | −0.072 | −0.206 | −0.088 | **−0.013** | 100 | 0.049 |
    | 2018 | −0.121 | −0.131 | −0.210 | −0.056 | **0.068** | 100 | 0.124 |
    | 2019 | −0.051 | −0.055 | −0.139 | 0.069 | **0.222** | 100 | 0.153 |
    | 2020 | −0.112 | −0.125 | −0.183 | −0.013 | **0.194** | 100 | 0.206 |
    | 2021 | −0.051 | −0.098 | −0.181 | 0.108 | **0.317** | 100 | 0.209 |

    - From 2018 onward λ = 100 wins clearly, and the objective rises from λ = 1 to λ = 100. The optimum sits **at the upper boundary of the grid** every time.
    - In 2016 the choice was effectively a tie.
    - **Context from the null:** shrinkage at the boundary is also the most common choice in no-signal worlds. λ = 100 wins 27–32% of null folds each year, and 13% of null worlds choose λ = 100 in at least 6 of 7 years. So boundary behaviour is not distinctive of a real signal.
    - Not extended above 100 and not rerun.
26. **Score dispersion:** exact per-review dispersion NOT COMPUTED (raw predictions were not exported).
    - **Approximation** (labelled as such): prediction SD = √(βᵀCβ/3), with C = the H024 canary's 2011–2017 median feature correlation matrix.
      - 2015: SD 0.044, p90–p10 ≈ 0.11.
      - 2016–2021: SD 0.0064–0.0137, p90–p10 ≈ 0.016–0.035, on a label scale of −1…+1.
    - The implied share of label variance explained is 0.01–0.06%.
    - **Reading:** ranks are scale-free, so small coefficients do not by themselves make ranks arbitrary, and differences of about 1e-3 are far above numerical noise. But the predicted separation is tiny relative to the noise in 63-session outcomes. Exact Top-15 cutoffs: NOT COMPUTED.
27. **Score rank stability:** NOT COMPUTED (scores were not exported).
28. **Top-15 overlap / Jaccard / implied holding duration:** NOT COMPUTED. The committed indirect evidence:
    - turnover averaged 62% of equity a month;
    - each rebalance trades sells plus buys (about 0.5× + 0.5×), so roughly 30% of the book is replaced monthly;
    - the implied mean holding duration is about 3 months.
    
    This is an inference from turnover, not a measured overlap.

### Costs and risk

29. **Turnover:** 0.62 of equity traded per monthly rebalance (mean), 7.4× a year. Per year: 2015 8.1, 2016 9.1, 2017 7.2, 2018 7.6, 2019 7.7, 2020 7.8, 2021 4.6 (11 rebalances).
30. **Gross vs net wealth:**
    - Net terminal wealth: $311,397.
    - Gross wealth before costs: NOT COMPUTED — WOULD REQUIRE A NEW COUNTERFACTUAL RUN.
    - **Indicative only.** Linear extrapolation from the committed 0.10% and 0.20% slippage results of the same selections gives about $327,766 without slippage. That is not a run.
31. **Commission drag:** $5,663 nominal (809 orders × $7). About 0.5% a year of average equity.
32. **Slippage drag:**
    - $7,830 nominal at 0.10% per side.
    - At 0.20% (approved diagnostic): $295,028 vs SPY's $261,801. The extra 0.10% costs $16,369 of terminal wealth, including compounding.
    - **Total nominal cost drag:** about 1.24% a year of average equity.
33. **Beta to SPY:** 0.82 (daily) / 0.80 (monthly).
    - Descriptive CAPM fit on monthly returns: alpha +0.46% a month (+5.5% annualised), iid t 1.70, R² 0.67.
    - Descriptive only: not a gate, and not adjusted for the search.
34. **Correlation with SPY:** 0.88 daily, 0.82 monthly. Tracking error 8.4% a year.
35. **Up/down capture** (monthly):

    | SPY months | Count | Mean H026 | Mean SPY | Capture | Log-relative sum |
    |---|---|---|---|---|---|
    | SPY up | 60 | +3.15% | +3.20% | 0.99 (geometric 0.98) | **−0.030** |
    | SPY down | 24 | −2.83% | −3.65% | 0.78 (geometric 0.78) | **+0.202** |

    - H026 beat SPY in 62.5% of SPY-down months and 50% of SPY-up months.
    - **Risk-advantage reading** (only what committed evidence supports):
      - Cash is ruled out: 99.6% invested.
      - Diversification is not distinctive: always 15 holdings, the same as every null world.
      - The consistent negative LOWVOL coefficient points to a deliberate low-volatility tilt.
      - The null comparison (item 41) shows that permuted features never produce this low volatility.
      - Sector allocation and timing: NOT COMPUTED (no sector-by-period data).
36. **Sector exposure:** only total pick counts over 84 rebalances were exported:
    - Shops 18.7%, Other 18.3%, BusEq 15.3%, Manuf 12.9%, Hlth 11.5%, Chems 10.1%, NoDur 9.0%, Telcm 1.9%, Durbl 1.4%, Utils 0.7%;
    - Enrgy (energy) and Money (finance) absent. Financials are excluded by the universe; energy was never picked.
    - Average weight and months represented by period, and the universe sector distribution: NOT COMPUTED (not exported).
37. **Sector P&L:** NOT COMPUTED (not exported).
38. **Universe-relative allocation/selection attribution:** NOT COMPUTED. It needs per-period holdings and universe sector returns, and neither was exported. A SPY Brinson attribution is in any case impossible without point-in-time SPY constituent sector weights, and none were invented.

### Specific tilts

39. **LOWVOL:**
    - Mean coefficient −0.0061, negative in all 7 years, SD 0.0013. It is the most stable coefficient.
    - About 0.47 of the unit-normalised weight in 2016–2021.
    - **By year type:** winning years 2017, 2018, 2020 average −0.0067; losing years 2015, 2016, 2019, 2021 average −0.0056. Essentially the same tilt in both.
    - Selected-stock LOWVOL percentiles: NOT COMPUTED.
    - **History:** H005 (pure low volatility, C01) failed its own 2018–2021 Validation (E005-28: Deflated Sharpe 0.68 < 0.90, PBO 0.71 > 0.30). Its shallow 2020 drawdown was largely explained by low exposure and two dead positions (CP4).
    - **H026 does not validate LOWVOL.** It shows that a learned score leaning on it produced lower volatility, and lost less in down months, over 2015–2021.
40. **HI52 / profitability / growth / asset growth / leverage** (coefficients; selected-stock percentiles NOT COMPUTED):
    - **HI52** (near 52-week high): +0.0035 mean, positive 7 of 7 years, stable (SD 0.0021).
    - **GPA** (gross profitability): +0.0097 mean, positive 7 of 7.
    - **BM** (book-to-market): negative 7 of 7, i.e. a growth tilt. The opposite of the value orientation H024 had pre-assigned.
    - **AG** (asset growth): negative 6 of 7 (prefers lower asset growth).
    - **EQA** (equity/assets): negative 6 of 7 (prefers lower equity/assets).
    - **CBOP:** positive 6 of 7. **CFP:** mixed (4+, 3−).
    - **Stable from 2016:** HI52, GPA, BM, LOWVOL and REV1M keep their sign in every year.

### Null post-mortem

41. **Null distribution** (5,000 existing worlds; none new):

    | Statistic | Null p5 | Null median | Null p95 | Null p99 | Null max | Real | Share of null ≥ real |
    |---|---|---|---|---|---|---|---|
    | S_WEALTH | −0.549 | −0.230 | +0.094 | +0.223 | +0.438 | **+0.171** | 1.98% |
    | Wealth ratio | 0.58 | 0.79 | 1.10 | 1.25 | 1.55 | **1.187** | 1.98% |
    | Excess CAGR | −8.7 | −3.7 | +1.6 | +3.7 | +7.4 pts | **+2.85** | 1.98% |
    | MaxDD | −45.2% | −38.4% | −32.0% | −29.5% | −24.9% | **−26.1%** | 0.02% as shallow |
    | Volatility | 18.9% | 19.9% | 20.9% | 21.4% | 22.2% (min 18.0%) | **16.4%** | 0% as low |
    | Years beating SPY | 0 | 2 | 4 | 5 | 7 | **3** | 36.9% ≥ 3 |

    - Years-beating histogram 0–7: 356, 1,184, 1,617, 1,173, 516, 137, 16, 1.
    - No null world had volatility at or below SPY's 17.7%.
    - 576 null worlds had a MaxDD no worse than SPY's.
42. **Real result's position:**
    - S_WEALTH and wealth: 98.0th percentile.
    - Volatility: lower than all 5,000.
    - MaxDD: shallower than 4,999.
    - Post-hoc CAGR / volatility: 1.08 vs a null median of 0.56; 4 null worlds at or above.
43. **The 99 null worlds with S_WEALTH ≥ real:**
    - median S_WEALTH 0.225, wealth ratio 1.25, excess CAGR +3.7 points;
    - median MaxDD −35.2%, and **none** as shallow as H026's −26.1%;
    - median volatility 19.9%, and **none** as low as 16.4%;
    - years beating SPY: 2 (2 worlds), 3 (13), 4 (29), 5 (46), 6 (8), 7 (1). Most were **more** consistent than H026's 3 of 7.
    - λ profile like the whole null: λ = 100 in about a third of folds; 24 of 99 choose λ = 100 in at least 6 years; none has exactly H026's λ sequence.
    - Turnover and coefficient stability of null worlds: NOT COMPUTED (not stored).

    **Answer:** on wealth, H026 looks like a member of the null tail. Several noise worlds got as rich with better consistency. On risk, H026 is structurally different from every tail member: lower volatility and shallower drawdown. The mechanical reason is above (a deliberate low-volatility tilt the permutation null cannot reproduce), so this difference describes the portfolio's risk, not its return skill.
44. **Joint null counts** (post-hoc, descriptive; no new p-value or rule):

    | Condition | Null worlds of 5,000 |
    |---|---|
    | wealth ≥ real | 99 |
    | wealth ≥ real and MaxDD no worse | **0** |
    | wealth ≥ real, MaxDD no worse, volatility no higher | **0** |
    | D1 (S > c_WEALTH) | 49 |
    | D2 | 144 |
    | D4 | 4,107 |
    | D3: necessary part only (≥ 5 years ahead) | 154 |
    | D3 full / D5 | NOT COMPUTED (yearly log-relatives and 0.20% wealth not stored) |
    | D2 + D4 | 140 |
    | D2 + D4 and not D1 | 92 |
    | D2 + D4 + (≥ 5 years) | 73 |
    | D1 + D2 + D4 + (≥ 5 years) | 32 |
    | D2 + D4 with ≤ 3 years ahead (like H026) | 27 |

### Failure analysis

45. **D3 failure:** H026 was ahead in 3 of 7 years because its relative result followed the market's direction, not a steady selection edge.
    - **Losing years:**
      - 2015: SPY flat; H026 −7.7%, deeper drawdown −15.9% vs −11.9%, λ = 0.01 (the one differently shaped model).
      - 2016: SPY +12% rebound; H026 +5.4%.
      - 2019 and 2021: SPY +31% and +29%; H026 3.4 and 2.2 points behind.
    - **Winning years:**
      - 2018: SPY −4.6%, H026 +11.6%, positive in 10 of 12 months, strongest in March, October and November.
      - 2020: dominated by March, when H026 fell far less than SPY.
      - 2017: a low-volatility year (both under 7.2% volatility), H026 +31.8%.
    - **Same in every year:** turnover 7.2–9.1×, λ = 100 from 2016.
    - **Market regime** (non-gating diagnostic, all months): RISK_OFF months −1.22% a month relative (6 months), WEAK +1.50% (10), NORMAL +0.35% (14), STRONG +0.26% (54).
    - Per-year sector and security contributions and selected-stock exposures: NOT COMPUTED.
46. **2015–2017 vs 2018–2021:**

    | | 2015–2017 | 2018–2021 |
    |---|---|---|
    | Wealth ratio (period) | **0.934** | **1.271** |
    | Excess CAGR | −2.5 pts (8.7% vs 11.2%) | +7.3 pts (24.9% vs 17.6%) |
    | Volatility ratio | 1.00 | 0.91 |
    | MaxDD H026 / SPY | −19.0% / −12.9% (ratio 1.47) | −26.1% / −33.7% (ratio 0.77) |
    | Years ahead | 1 of 3 | 2 of 4 |
    | λ | 0.01, 100, 100 | 100 × 4 |
    | Coefficients | 2015 differs; 2016–17 ≈ the later formula | stable (adjacent corr 0.89–0.98) |
    | Turnover | 8.1, 9.1, 7.2× | 7.6, 7.7, 7.8, 4.6× |
    | Exposures, sector weights, top contributors | NOT COMPUTED | NOT COMPUTED |

    **What the data support:**
    - From 2016 the formula was nearly the same, while results swung with the market: behind in 2016 and 2019/2021, ahead in 2017/2018/2020.
    - In 2015–2017 H026 had a **deeper** drawdown than SPY. The drawdown advantage appears only in 2018–2021, through its two sell-offs.
    - This fits an investment environment that rewarded the model's defensive style in 2018–2021, more than a general effect that strengthened. The data cannot rule out a small genuine selection component (descriptive alpha t 1.70, sector-neutral t 1.05), but they do not demonstrate one.
47. **2018 contribution:** +0.1564 log-relative = 91% of S_WEALTH and **43.1%** of the positive yearly total (0.3629).
48. **2020 contribution:** +0.1267 = 74% of S_WEALTH and **34.9%** of the positive yearly total. March 2020 alone is +0.1105 (64% of S_WEALTH).

### Context and conclusion

49. **Comparison:**

    | | H022 | H023 | H024 | H026 |
    |---|---|---|---|---|
    | Model | Score v1, fixed weights | 92 layer weightings of Score v1 | 415 equal-weight 2–4 feature models, pre-assigned signs | Ridge, learned signed weights, 11 features |
    | Target | 1-month TSR, demeaned | same | same | 63-session TSR minus SPY, cross-sectional rank |
    | Test | signal (rank IC) | signal search (IC) | signal search (IC) | portfolio wealth vs SPY (Top-15, costs) |
    | Development period | 2011–2017 | 2011–2017 | 2011–2017 | 2011–2021; walk-forward test 2015–2021 |
    | Best economic result | 80+ group −12.6%/yr | not a portfolio test | not a portfolio test (best feature LOWVOL t 1.24) | $311K vs $262K (1.19×), +2.85 pts/yr |
    | Statistical result | t_IC 0.48 vs c 2.38 | best t 0.97, p 0.41 | best t 2.48, p 0.35 | S_WEALTH 0.171 vs c 0.225, p 0.020 |
    | Stability | second half negative; largest block 111% | no plateau; walk-forward IC 0.001 | walk-forward IC −0.001 | 3 of 7 years; formula stable 2016–21 |
    | Conclusion | REJECTED | NO ROBUST CANDIDATE | NO ROBUST MODEL | REJECTED |

50. **What H026 changed** (association, not demonstrated causality):
    1. **Signs were learned**, and they disagreed with H024's pre-assigned orientation on value: Ridge preferred **low** book-to-market.
    2. **The target was 63 sessions, relative to SPY**, not 1 month.
    3. **It was judged as a 15-stock portfolio** against SPY wealth, not by rank IC.
    4. **The evaluation years differ.** H022–H024 used 2011–2017 only. H026's test years run to 2021 and include the two sell-offs that produced most of its advantage. **In the overlapping years 2015–2017, H026 also trailed SPY** (−0.068), consistent with the earlier null results for that period.
51. **Broad or concentrated:** concentrated in time.
    - All of the advantage is in SPY-down months.
    - 2018 and 2020 make up 78% of the positive yearly total.
    - March 2020 alone is 64% of S_WEALTH.
    - Across stocks: NOT DETERMINABLE from committed artifacts.
52. **H027 feasibility: B — an interesting but concentrated effect.**
    - **Why not A:**
      - the formal wealth statistic is in the null's top 2%, not beyond its 1% line;
      - the advantage is concentrated in two market episodes;
      - H026 trailed SPY in 4 of 7 years, including both strong up-years;
      - the 2015–2017 overlap with earlier work shows no advantage.
    - **Why not C:**
      - the model learned a coherent, stable formula from 2016;
      - its risk profile (volatility, drawdown, down-capture 0.78) is far outside what permuted features produce;
      - the descriptive alpha is positive (t 1.70).
    - It is plausibly a real defensive exposure rather than noise. Whether there is any stock-selection skill **beyond** that exposure is unproven.
53. **Up to 3 H027 concepts** (none chosen, nothing built; each would be a new pre-registration). One caveat applies to all three: development data would again be 2011–2021, which is now fully seen (H026, and H022–H025 for 2011–2017). A new test on it can at best give development evidence, not confirmation. Confirmation would need data never used. This checkpoint does not recommend opening the Holdout.
    - **H027-1: exposure-adjusted test of a learned score.**
      - *Changes:* the hypothesis and the benchmark. It asks for return **beyond** market and low-volatility exposure, e.g. wealth vs a beta-matched or low-volatility-matched benchmark, or an alpha statistic against SPY plus a low-volatility factor. The features, target and model class would be fixed in advance.
      - *Why the post-mortem supports it:* the whole H026 advantage is down-month and beta-like (beta 0.80; down-capture 0.78). This test separates selection skill from the defensive exposure.
      - *Why it is not tuning:* it tightens the question rather than adjusting parameters, and it can only make passing harder.
      - *Frozen:* features, target, Top-15, costs, mechanics, null method.
      - *Overfitting control:* a full-pipeline permutation null calibrated on the exposure-adjusted statistic; one real run.
    - **H027-2: fixed-shrinkage or sign-only weighting** (no λ selection).
      - *Changes:* weights are estimated with a pre-declared fixed rule, either sign-only with equal magnitudes or one fixed strong shrinkage. The inner λ search is removed.
      - *Why the post-mortem supports it:* λ sat at the grid boundary in 6 of 7 folds, the objective rose monotonically towards it, and the formula was stable. The λ search added a degree of freedom without visible benefit.
      - *Why it is not tuning:* it removes a choice instead of adding one. The risk is that "sign-only" is chosen because the post-mortem saw stable signs, so it must be declared before any new result.
      - *Frozen:* features, target, K, sector cap, costs, mechanics.
      - *Overfitting control:* a full null on the new procedure; one run.
    - **H027-3: defensive objective declared openly.**
      - *Changes:* the hypothesis itself becomes "a learned quality / low-risk score delivers SPY-like wealth with lower drawdown and down-capture". Gates would be on drawdown, down-capture and wealth ≥ SPY, and evaluated against a low-risk benchmark, not only SPY.
      - *Why the post-mortem supports it:* this is what H026 actually delivered.
      - *Why it is the most at risk of post-hoc fitting:* its motivation comes directly from H026's 2018 and 2020 behaviour. It is listed for completeness and would need the strictest pre-registration and an honest "development only" label.
      - *Frozen:* features, model, mechanics, costs.
      - *Overfitting control:* the same, plus the benchmark choice fixed in advance.
54. **No H027 was run.** No H027 code, configuration, backtest or selection exists.
55. **No H026 tuning.** No retraining, no change to features, formulas, target, λ grid, Top-15, sector cap, costs, folds, mechanics, null or gates. No H026 rerun.
56. **No new null worlds.** Only the 5,000 committed worlds were read.
57. **No new QuantConnect run.** Everything is offline, from committed artifacts. The session-start check of the QuantConnect credentials and reachability made no project call.
58. **Holdout untouched:**
    - No 2022–2026 price.
    - No 2022–2026 fundamental.
    - No 2022–2026 benchmark result.
    - No 2022–2026 SEC information.
    - No Holdout-derived decision.

    Every month analysed is at or before 2021-12, and a test asserts it.
59. **Memory and capacity:**
    - The S028 hosts peaked at 7.6–8.2 GB on QuantConnect's B2-8 node.
    - A future H027 that keeps S028's structure and adds anything (another benchmark, factor series, or an export of holdings and scores) would very likely exceed the node. It **needs memory reduction first**: for example float32 price matrices, freeing the X801 build intermediates before the model stage, and streaming null worlds without retaining months twice.
    - An export run to fill the NOT COMPUTED items (decision 3 below) carries the same risk.
    - The 5,000-world pipeline itself is cheap (0.14 s a world); memory, not time, is the constraint.
60. **Exact next owner decision:**
    1. **Data v2.1 governance (D207).** Either approve the Data v2.1 freeze as an explicit owner exception for the NEW_YEARS_MAPPING specification error, or reject it. Rejecting it would make H026 "BLOCKED" retroactively and require a fixed audit.
    2. **H027 direction** (classification B). Choose one:
       - (a) close Phase 11 with no H027 (stopping is defensible);
       - (b) ask for a design-only pre-registration of **one** of H027-1, -2 or -3 (recommended if continuing: **H027-1**, because it tests the open question directly).
    3. **Optional, needs explicit authorisation:** a non-trading export run of the frozen H026 pipeline (0 orders, infrastructure) to fill the NOT COMPUTED security, sector, exposure and rank items. It is recommended **only** if you want the stock-level concentration answer before deciding on H027, and only after memory reduction (item 59).

---

```
H026 REMAINS REJECTED
POST-MORTEM COMPLETE
NO NEW CANDIDATE CREATED
HOLDOUT SEALED
```

## Files

- Owner decision: `docs/owner/2026-10-11_p11cp2_h026_postmortem.md`.
- Analysis: `research/phase11/cp2/P11_CP2_postmortem.py` → `research/phase11/cp2/P11_CP2_postmortem.json`.
- Tests: `tests/test_p11_cp2_postmortem.py`.

## Totals

Programme: 26 hypotheses (H001–H026). This checkpoint ran no experiment; no strategy or hypothesis was added.
