# P13-CP4 — H028 30-Year Objective Alignment Review

**Date:** 2026-10-12. **Decisions:** D225 (owner request), D226 (this checkpoint).
**Status:** STOPPED, awaiting the owner. Descriptive only.

```
ORIGINAL RESEARCH STATUS:
H028 REJECTED

30-YEAR OBJECTIVE ALIGNMENT:
PARTIALLY OBJECTIVE-ALIGNED
```

These two lines answer different questions.
- **The research status** records whether H028 passed its pre-registered gates. It did not: B4 failed. That is unchanged and final.
- **The alignment label** describes how H028's observed 2015–2021 behaviour compares with the 30-year objective the owner has now clarified. It is not a gate, a pass or a repair.

> Every number below comes from the seven already-seen development years 2015–2021.
> - The synthetic numbers reuse only those years (P13-CP3). **They are not 30 years of new evidence.**
> - Synthetic frequencies are written as "H028 beat SPY in x% of synthetic paths generated from the observed 2015–2021 return blocks". They are never chances of future success.

## Direct answers

**Q1 — When SPY goes up, does H028 generally keep up?**
**Nearly, on average.**
- Its up-capture is 0.97, which the owner's thresholds call near-full participation.
- It beat SPY in only half of the 60 up months.
- It lags more as the rise gets stronger: capture is 0.94 in months where SPY rose at least 2%, and 0.87 where SPY rose at least 5%. In those strong months it beat SPY only 4 times in 12.
- Compounded over all up months: H028 +510%, SPY +549%.

**Q2 — When SPY falls, does H028 generally lose less?**
**Yes, clearly.**
- Down-capture is 0.69. H028 lost less than SPY in 18 of the 24 down months.
- The protection grows a little as losses grow: down-capture 0.69 in all down months, 0.67 when SPY fell at least 2%, and 0.65 when SPY fell at least 5% (beat SPY in 5 of 6).
- Compounded over all down months: H028 −46%, SPY −60%.

**Q3 — Up-capture and down-capture?**
- Up-capture 0.969, down-capture 0.685, so the asymmetry ratio is 1.42.
- On a compounded basis the figures are 0.93 and 0.77 (ratio 1.20).
- LV15 for context: 0.62 / 0.41 (ratio 1.50).

**Q4 — Is the advantage produced in rising or falling markets?**
**Entirely in falling markets.**
- Down months contributed +0.286 of relative log-wealth, which is 127% of the total of +0.225.
- Up months contributed −0.061 (−27%).
- March 2020 alone supplied 49% of the total.

**Q5 — Without 2018 and 2020, does the desirable up/down behaviour remain?**
**Only weakly, and it no longer pays.**
- Over the remaining 60 months, up-capture is 0.90 (just under the near-full threshold) and down-capture is 0.81, giving an asymmetry ratio of 1.10.
- H028 earned 16.99% a year against SPY's 18.38%, or −1.39 points a year.

**Q6 — How consistently does H028 beat SPY over rolling 1-, 3- and 5-year periods?**
- **12-month windows:** H028 was ahead in 58% (median +5.0 points; worst −9.4).
- **36-month windows:** ahead in 92%.
- **60-month windows:** ahead in 100% (worst wealth ratio 1.11).
- **Caveat:** every 60-month window contains all of 2018, and 24 of the 25 contain part of 2020.

**Q7 — How long can H028 remain behind SPY before recovering?** In the synthetic 30-year paths where H028 ends ahead of SPY:
- the median longest losing streak is **5 consecutive years**, with a 90th percentile of 8;
- the median longest stretch below a previous relative high is **90 months (7.5 years)**, with a 90th percentile of about **15 years**;
- 16% of these paths are still below an earlier relative peak at the end of the 30 years;
- the median worst relative drawdown is −21%.

**Q8 — Over synthetic 30-year paths, how often does it beat SPY?**
- H028 beat SPY in 98.7% of synthetic 30-year paths generated from the observed 2015–2021 return blocks.
- The median wealth ratio is 2.58×; the 5th to 95th percentile range is 1.27× to 5.37×.

**Q9 — How dependent is that on environments like 2018 and 2020?**
**Heavily.**

| Years removed from the donor set | H028 beat SPY in 30-year paths | Median excess per year |
|---|---|---|
| None | 98.7% | +3.68 pts |
| 2018 | 82.0% | +1.35 pts |
| 2020 | 88.3% | +1.88 pts |
| 2018 and 2020 | **9.3%** | **−1.45 pts** |

**Q10 — Is H028 aligned with the 30-year objective?**
**PARTIALLY OBJECTIVE-ALIGNED.**
- **What fits the objective:**
  - near-full average upside;
  - clearly smaller losses in falling markets, stronger in larger falls;
  - a large long-run compounding advantage within the observed environments.
- **What does not fit:**
  - the whole advantage over SPY comes from sell-off months, mostly two episodes (2018 and March 2020);
  - outside them H028 trails SPY, especially in strongly rising months;
  - even in the synthetic paths where it wins, it typically looks broken against SPY for 5 years in a row and spends about 7.5 years below a previous relative high.
- **Pre-registered rule result:** two of six dimensions are WEAK (regime dependence and patience burden). The "edge from one or two episodes" pattern (Pattern C) is the best-supported description.

## Required items

### Status, objective, sources

1. **H028 original research status: REJECTED.**
   - B4 failed: 2015–2017 behind LV15 (−0.006).
   - Recorded in P13-CP1 (D220) and unchanged by P13-CP2, P13-CP3 and this review.
2. **The owner's clarified 30-year objective (D225):**
   - over roughly 30 years, participate at least as well as SPY in rising markets, preferably better;
   - lose less than SPY in falling markets;
   - compound to materially more wealth than SPY;
   - isolated losing years are acceptable.
   This applies prospectively. It does not turn B4 into a pass.
3. **Data and artifact sources:**
   - **Monthly panel:** the 84 paired monthly total returns 2015-01 → 2021-12 for H028, LV15 and SPY, after each one's actual costs. This is the committed P13-CP3 donor panel.
     - It was rebuilt from the committed E030-05 output with the P13-CP3 loader, and the rebuild is identical (QRHR SHA-256 dd4be72c…).
     - Month-end marks are before the final liquidation (P13-CP3 audit).
   - **Synthetic numbers:** copied from the committed `P13_CP3_bootstrap.json`.
   - **One statistic was not saved by P13-CP3:** patience in paths that end ahead of SPY (owner item 22).
     - I regenerated the 10,000 primary worlds with the committed P13-CP3 code and seeds.
     - Their world-metric digest equals the committed one (8a178da4…), so they are the same paths.
   - **Code and output:** `research/phase13/cp4/P13_CP4_alignment.py` → `P13_CP4_alignment.json`.
   - **Methodology commit:** every rule and threshold was committed in 006f417, before the script was run.
4. **Holdout:** untouched.
   - No data after 2021-12-31 exists in any source used.
   - 2022-01-01 → 2026-08-31 was not accessed in any form.
   - No QuantConnect run.

### Part A — rising markets

5. **Up months (SPY > 0): 60.** No month had SPY exactly 0.
6. **Down months (SPY < 0): 24.**
7. **Up-capture: 0.969** (mean H028 / mean SPY over up months; the P11-CP2 definition).
   - Compounded up-capture: 0.930.
   - Classification (owner thresholds, fixed beforehand): **NEAR-FULL PARTICIPATION** (0.90 ≤ 0.969 < 1.00).
8. **Down-capture: 0.685.** Compounded down-capture: 0.775.
9. **Up-month relative return:**

   | Up months (60) | H028 | SPY | H028 − SPY |
   |---|---|---|---|
   | Mean | +3.10% | +3.20% | −0.10% |
   | Median | +2.63% | +2.39% | +0.06% |
   | Compounded over up months only | +509.9% | +548.6% | |

   H028 > SPY in 50.0% of up months.
10. **Down-month relative return:**

    | Down months (24) | H028 | SPY | H028 − SPY |
    |---|---|---|---|
    | Mean | −2.50% | −3.65% | +1.15% |
    | Median | −1.94% | −2.64% | +1.08% |
    | Compounded over down months only | −46.1% | −59.5% | |

    H028 > SPY in 75.0% of down months.
11. **Strongly rising months:**

    | SPY | n | Mean H028 | Mean SPY | Mean relative | Up-capture | H028 > SPY |
    |---|---|---|---|---|---|---|
    | > 0 | 60 | +3.10% | +3.20% | −0.10% | 0.969 | 50.0% |
    | ≥ +2% | 37 | +4.29% | +4.57% | −0.28% | 0.939 | 45.9% |
    | ≥ +5% | 12 | +6.54% | +7.52% | −0.98% | 0.870 | 33.3% |

    **H028 keeps up less well the more strongly the market rises.** In SPY's 12 strongest months it captured 87% and beat SPY only 4 times. Compounded over those 12 months: H028 +113%, SPY +138%.

### Part B — falling markets

12. **Severe down months:**

    | SPY | n | Mean H028 | Mean SPY | Mean relative | Median rel. | Down-capture | H028 > SPY | Compounded H028 / SPY |
    |---|---|---|---|---|---|---|---|---|
    | < 0 | 24 | −2.50% | −3.65% | +1.15% | +1.08% | 0.685 | 75.0% | −46.1% / −59.5% |
    | ≤ −2% | 15 | −3.54% | −5.25% | +1.72% | +1.39% | 0.673 | 80.0% | −42.0% / −55.8% |
    | ≤ −5% | 6 | −5.23% | −8.10% | +2.86% | +1.99% | 0.646 | 83.3% | −27.7% / −39.9% |

    **Does protection get stronger as losses get larger? Yes, modestly** (0.685 → 0.673 → 0.646; the pre-set monotonic test holds). The mean relative gain per month is about 2.5 times larger in the ≤ −5% months (+2.86%) than across all down months (+1.15%).
13. **Asymmetry ratio** (up-capture ÷ down-capture; descriptive, never a gate; no denominator was near zero):

    | Series and period | Up-capture | Down-capture | Ratio |
    |---|---|---|---|
    | H028, 2015–2021 | 0.969 | 0.685 | **1.42** |
    | H028, compounded captures | 0.930 | 0.775 | 1.20 |
    | LV15, 2015–2021 (context) | 0.619 | 0.413 | 1.50 |
    | H028 excluding 2018 | 0.913 | 0.676 | 1.35 |
    | H028 excluding 2020 | 0.975 | 0.777 | 1.25 |
    | H028 excluding 2018 and 2020 | 0.898 | 0.814 | 1.10 |

    LV15 has the higher ratio by lowering both captures (it gives up a third of the upside). H028 keeps most of the upside, but its asymmetry shrinks sharply once 2018 and 2020 are removed.

### Part C — calendar years

14. **Calendar-year classification:**

    | Year | SPY | H028 | H028 − SPY | SPY year |
    |---|---|---|---|---|
    | 2015 | +0.7% | −3.5% | −4.2 pts | UP (barely) |
    | 2016 | +12.0% | +6.2% | −5.8 pts | UP |
    | 2017 | +21.7% | +31.8% | +10.1 pts | UP |
    | 2018 | −4.6% | +11.6% | +16.2 pts | DOWN |
    | 2019 | +31.2% | +27.9% | −3.3 pts | UP |
    | 2020 | +18.3% | +34.4% | +16.0 pts | UP (with a crash inside) |
    | 2021 | +29.1% | +26.9% | −2.2 pts | UP |

15. **SPY-up years (6):**
    - Mean H028 − SPY was +1.76 points.
    - H028 kept up or beat SPY in only 2 of the 6 (2017 and 2020).
    - It trailed in 2015, 2016, 2019 and 2021, by 2–6 points each.
    - The 2020 gain came from the February–March crash months inside an up year.
    - **So in up years H028 did not generally keep up. It lagged modestly in most of them and won big in two.**
16. **SPY-down years (1):**
    - 2018: H028 +11.6% against SPY −4.6% (+16.2 points). It protected capital, and in fact gained.
    - **This is one year; do not overinterpret it.**

### Part D — rolling horizons

17. **Rolling 12 months** (73 overlapping windows):
    - H028 > SPY in **57.5%**.
    - Excess return (H028 − SPY total return):

      | Statistic | Excess |
      |---|---|
      | 5th percentile | −8.7 pts |
      | 25th percentile | −3.9 pts |
      | Median | +5.0 pts |
      | 75th percentile | +11.9 pts |
      | 95th percentile | +17.5 pts |

    - Worst window: 2020-10 → 2021-09, −9.4 pts (H028 +20.5% vs SPY +30.0%).
    - Best window: 2019-08 → 2020-07, +22.7 pts (H028 +34.7% vs SPY +12.0%).
    - H028 / SPY relative wealth ranges from 0.924 to 1.203 (median 1.041).
18. **Rolling 36 months** (49 windows):
    - H028 > SPY in **91.8%**.
    - Wealth ratio: median 1.201, minimum 0.952, maximum 1.437.
    - Annualised excess: median +6.9 points a year; worst −1.8 (2015-03 → 2018-02).
    - 25 of the 49 windows contain all of 2018, and 24 contain part of 2020.
19. **Rolling 60 months** (25 windows):
    - H028 > SPY in **100%**.
    - Wealth ratio: median 1.297, worst 1.110 (2015-03 → 2020-02), best 1.384 (2017-01 → 2021-12).
    - Annualised excess distribution:

      | Statistic | Points a year |
      |---|---|
      | Minimum | +2.3 |
      | 5th percentile | +2.6 |
      | 25th percentile | +4.8 |
      | Median | +6.0 |
      | 75th percentile | +7.0 |
      | 95th percentile | +7.7 |
      | Maximum | +7.8 |

    - **Caveat:** all 25 windows contain the whole of 2018 and 24 contain part of 2020. The real 5-year record cannot show how H028 does over 5 years without those episodes; P13-CP3 can (item 22).
20. **10-year windows:** NOT AVAILABLE FROM REAL DEVELOPMENT HISTORY. The real period is only seven years. For 10, 20 and 30 years, see the synthetic items 26–32.

### Part E — where the wealth advantage comes from

21. **Up-month contribution to relative log-wealth:**
    - Over the 60 SPY-up months, Σ log((1 + H028) / (1 + SPY)) = **−0.061**, which is **−27%** of the total.
    - Up months were positive only in 2017 (+0.080), 2018 (+0.090) and 2021 (+0.064). They were negative in 2015, 2016, 2019 and 2020.
22. **Down-month contribution:**
    - Over the 24 SPY-down months the sum is **+0.286**, which is **+127%** of the total (+0.225, a wealth ratio of 1.25).
    - **The two largest months:**

      | Month | SPY | H028 | Relative log | Share of total |
      |---|---|---|---|---|
      | March 2020 | −12.5% | −2.3% | +0.111 | 49% |
      | August 2019 | −1.7% | +3.3% | +0.050 | 22% |

    - **Pattern assessment** (rule fixed beforehand):
      - Pattern A's criteria also hold: up-capture ≥ 0.90 and down-capture ≤ 0.85.
      - **Pattern C holds as well and takes precedence:** removing the two best calendar years (2018 and 2020) leaves −0.059.
      - Removing only the two best months still leaves +0.064, so the edge is not just two months. It is two **years** of sell-off behaviour.
    - **Best-supported description: Pattern C** — the edge over SPY comes from the 2018 and 2020 episodes. It has an "A-like" monthly profile, but that profile is itself mostly produced by those episodes (see item 25).

### Part F — real history without 2018 and 2020

These figures drop the recorded months and join up the rest. There is no retraining, and this is not an independent test.

| Period | Months | H028 a year | SPY a year | Difference | Up-capture | Down-capture | Monthly win rate |
|---|---|---|---|---|---|---|---|
| Full 2015–2021 | 84 | 18.53% | 14.79% | +3.74 pts | 0.969 | 0.685 | 57.1% |

23. **Excluding 2018:**

    | Months | H028 a year | SPY a year | Difference | Up-capture | Down-capture | Monthly win rate |
    |---|---|---|---|---|---|---|
    | 72 | 19.72% | 18.38% | +1.35 pts | 0.913 | 0.676 | 52.8% |

24. **Excluding 2020:**

    | Months | H028 a year | SPY a year | Difference | Up-capture | Down-capture | Monthly win rate |
    |---|---|---|---|---|---|---|
    | 72 | 16.08% | 14.21% | +1.87 pts | 0.975 | 0.777 | 56.9% |

25. **Excluding 2018 and 2020:**

    | Months | H028 a year | SPY a year | Difference | Up-capture | Down-capture | Monthly win rate |
    |---|---|---|---|---|---|---|
    | 60 | 16.99% | 18.38% | **−1.39 pts** | **0.898** | **0.814** | 51.7% |

    - **Outside the two favourable years, the desired asymmetry mostly fades.**
    - Up-capture drops just below near-full, and the protection weakens (down-capture 0.81, against LV15's 0.26 in the same months).
    - The result trails SPY.
    - A small asymmetry remains (ratio 1.10), but in these years it was not enough to compound ahead.

### Part G — synthetic 30-year context (P13-CP3, complete-year blocks, 10,000 paths)

26. **5 years:** H028 beat SPY in 78.1% of synthetic paths generated from the observed 2015–2021 return blocks. Median ratio 1.16; 5th–95th percentile 0.87–1.59.
27. **10 years:** 89.2%. Median ratio 1.36; 5th–95th percentile 0.91–2.10.
28. **20 years:** 96.5%. Median ratio 1.88; 5th–95th percentile 1.06–3.45.
29. **30 years:** 98.7%. Median ratio **2.58**; 5th percentile 1.27; 95th percentile 5.37. Median excess CAGR +3.68 points.
30. **Losing streaks** (consecutive years behind SPY):

    | Statistic | All paths | Paths where H028 ends ahead |
    |---|---|---|
    | Median longest streak | 5 years | 5 years |
    | 90th percentile | 8 years | 8 years |
    | Share with ≥ 5 years | 56.7% | 56.1% |
    | Share with ≥ 10 years | 3.5% | 3.0% |

    H028 beat SPY in a median of 13 of the 30 years. The longest streak in any path was 21 years.
31. **Recovery** (longest stretch below a previous relative high):

    | Statistic | All paths | Paths where H028 ends ahead |
    |---|---|---|
    | Median | 91 months (7.6 years) | 90 months (7.5 years) |
    | 90th percentile | 185 months | 179 months (≈ 15 years) |
    | Still below an earlier peak at 30 years | 17.0% | 16.1% |

32. **Relative drawdown** against SPY:
    - All paths: median −21.3%, 95th percentile −33.7%, worst −56.8%.
    - Paths where H028 ends ahead: median −21.2%, 5th percentile −32.9%.
    - 97% of the winning paths contain at least one 5-year window behind SPY.

    **Patience analysis (owner item 22):**
    - In the synthetic paths where H028 ultimately wins, the typical experience is a run of about **5 consecutive losing years** against SPY.
    - It also includes a stretch of about **7.5 years** below its previous best relative position, and a fall of about **21%** relative to SPY at the worst point.
    - One path in ten has an 8-year losing run and a 15-year wait.
    - About 1 in 6 winning paths ends the 30 years still below an earlier relative peak.

### Part H — regime dependence

33. **2018 dependence:**
    - Removing 2018 from the donor years lowers the share of 30-year paths beating SPY from 98.7% to **82.0%**.
    - The median excess falls from +3.68 to **+1.35 points**, and the median ratio to 1.40.
    - In the primary paths, the number of 2018 draws correlates +0.63 with the 30-year outcome. That is the strongest of the seven years.
34. **2020 dependence:**
    - Removing 2020 gives **88.3%**, a median excess of +1.88 points and a median ratio of 1.63.
    - The correlation with the 30-year outcome is +0.48.
35. **Combined 2018 and 2020 dependence:**
    - Without both years, H028 beat SPY in only **9.3%** of synthetic 30-year paths. The median ratio is 0.69 and the median excess −1.45 points.
    - Against LV15 it still wins 93.6%.

    **Interpretation (owner item 24):**
    - **H028 is not robustly asymmetric across many environments.**
    - Its long-run success against SPY requires sell-off environments like 2018 and/or early 2020 to keep recurring with roughly their 2015–2021 frequency (2 in 7 years).
    - In the remaining environments H028 behaves like a slightly defensive portfolio that trails a strong market.
    - Whether such episodes recur often enough over 30 years cannot be learned from these data.

### Part I — the six objective dimensions

The thresholds were fixed beforehand (006f417). Dimensions C, E and F were effectively determined by numbers already published in P13-CP1 and P13-CP3. They are descriptive labels, not combined into a score.

| # | Dimension | Evidence | Label |
|---|---|---|---|
| 36 | **A. Upside participation** | Up-capture 0.969 (STRONG ≥ 1.00; ACCEPTABLE 0.90–1.00). Strong-up months 0.87 | **ACCEPTABLE** |
| 37 | **B. Downside protection** | Down-capture 0.685, and 0.646 in SPY ≤ −5% months (STRONG needs both ≤ 0.75) | **STRONG** |
| 38 | **C. Long-run compounding** | Real excess +3.74 points a year; 30-year synthetic 98.7%; median ratio 2.58 (STRONG ≥ 2 pts, ≥ 80%, ≥ 1.5) | **STRONG** |
| 39 | **D. Temporal consistency** | Windows ahead: 12-month 57.5%, 36-month 91.8%, 60-month 100% (STRONG ≥ 65 / 80 / 90%; ACCEPTABLE ≥ 50 / 60 / 75%) | **ACCEPTABLE** |
| 40 | **E. Regime dependence** | Without 2018 and 2020: 9.3% of 30-year paths; real excess −1.39 points a year (ACCEPTABLE needs ≥ 50% and a positive real excess) | **WEAK** |
| 41 | **F. Relative drawdown / patience burden** | Median losing streak 5 years, longest recovery 91 months, relative MaxDD −21% (ACCEPTABLE ≤ 4 years, ≤ 60 months, ≥ −20%) | **WEAK** |

**Caveats:**
- **D:** the 36- and 60-month consistency is largely carried by the same 2018 and 2020 episodes that every long window contains.
- **C:** the compounding advantage is real inside the observed years, but E shows what it rests on.

42. **Overall: PARTIALLY OBJECTIVE-ALIGNED.**
    - Pre-registered rule: ALIGNED needs no WEAK dimension and no Pattern C. NOT ALIGNED applies if C is WEAK, if A and B are both WEAK, or if 3 or more dimensions are WEAK.
    - H028 has 2 WEAK dimensions (E and F), C is STRONG, and the pattern is C, so the label is PARTIAL.
    - It sits close to the NOT-ALIGNED boundary: one more WEAK dimension would change the label, and D's ACCEPTABLE rating rests largely on windows that contain 2018 and 2020.

### Part J — what a future independent signal should contribute

43. **Missing capability.** This identifies the gap only; there is no design, no weights and no rule.
    - **Downside protection is already adequate.** Down-capture is clearly below 1 and strengthens in larger falls.
    - **What is missing:**
      - **regime-independent relative return**, i.e. a source of advantage over SPY in ordinary and strongly rising markets, where H028 lags (capture 0.87 when SPY rises 5% or more; up months net −27% of the edge);
      - **temporal consistency**, i.e. shorter relative drawdowns. Today the whole edge depends on recurring sell-off episodes.
    - In the owner's wording: *"H028's upside is acceptable on average, but the edge is excessively regime dependent."* More crash protection would not fix this.
    - **Hindsight warning:** this gap is visible only through 2018–2021 events. Under the research protocol, a future hypothesis must not be motivated or tuned by those specific episodes. It needs its own economic rationale and must be pre-registered before any data.

### Part M — prospective research standard

44. **Recorded for future hypotheses from H029 on (D226; prospective only):**

    > *Maximize long-term wealth relative to SPY over an approximately 30-year horizon while seeking strong upside participation and materially better downside protection.*

    - **Not required:** SPY outperformance in every calendar year, or zero multi-year relative drawdowns.
    - **Future pre-registered gates should evaluate:**
      - up-market participation;
      - down-market protection;
      - rolling multi-year performance;
      - terminal wealth;
      - risk;
      - cost robustness;
      - regime concentration;
      - long-horizon synthetic robustness.
    - **Specific gate thresholds** must be fixed in each future pre-registration, before any data, and approved by the owner. **None of these gates is applied retroactively to H028.**

### Confirmations

45. **No strategy change:**
    - H028 is exactly as tested: λ = 100, the 11 frozen features, Top-15, at most 3 per sector, monthly rebalance, next-open execution, long-only, no leverage, $100,000, $7 per order and 0.10% slippage per side.
    - Nothing was retrained, and no new parameters were introduced.
46. **H028 remains REJECTED.** B4 is unchanged. The alignment label does not replace the research status.
47. **Holdout untouched** (2022-01-01 → 2026-08-31). No QuantConnect run; no new, external or purchased data.

## Integrity summary

| Item | Value |
|---|---|
| New hypotheses / strategies / experiments | 0 / 0 / 0 |
| Sources | E030-05 (via the P13-CP3 donor panel, rebuilt identically); `P13_CP3_bootstrap.json` (SHA-256 in the output) |
| Synthetic regeneration (patience in winning paths only) | 10,000 primary worlds; digest equals the committed P13-CP3 digest |
| Methodology commit (before any statistic) | 006f417 |
| Output | `research/phase13/cp4/P13_CP4_alignment.json` |
| Tests | `tests/test_p13_cp4_alignment.py` (synthetic mechanics + committed-output consistency) |

## 48. Next owner decision

H028 remains REJECTED. This review changes no status.

Please choose one:

1. **Close Phase 13 and the learned-score line** (recommended). Recorded as: H028 REJECTED; 30-year alignment PARTIAL; the edge is regime-dependent and comes from sell-off episodes.
2. **Authorise a design-only H029 pre-registration checkpoint** under the prospective standard (item 44).
   - It would have a new, economically motivated hypothesis.
   - Its gates for participation, protection, rolling and regime concentration would be fixed before any data.
   - The 2018/2020 findings must not shape it (hindsight).
   - No implementation or data until you approve the pre-registration.
3. **Stop the programme here.**

Any use of the sealed Holdout is a separate owner decision. Nothing in this review supports one.

---

ORIGINAL RESEARCH STATUS:
H028 REJECTED

30-YEAR OBJECTIVE ALIGNMENT:
PARTIALLY OBJECTIVE-ALIGNED

- **Upside participation:** near-full on average (up-capture 0.97), but it lags in strongly rising months (0.87). Up months as a whole subtracted from the relative result.
- **Downside protection:** strong (down-capture 0.69), and stronger in larger falls (0.65).
- **Long-term compounding:** large within the observed years (+3.7 points a year; 2.58× SPY over the median synthetic 30-year path).
- **Regime dependence:** severe. The entire advantage over SPY comes from sell-off months, mostly 2018 and March 2020. Without those two years H028 trails SPY (−1.4 points a year), and only 9.3% of synthetic 30-year paths generated from the remaining years beat SPY.
