# P13-CP3 — H028 Long-Horizon Synthetic Path Robustness

**Date:** 2026-10-12. **Decisions:** D223 (owner request), D224 (this checkpoint).
**Status:** STOPPED, awaiting the owner. Descriptive only.

```
SYNTHETIC ROBUSTNESS RESULT —
H028 IS HIGHLY SENSITIVE TO PATH / REGIME COMPOSITION

FORMAL RESEARCH STATUS:
H028 REJECTED
```

> **Synthetic 30-year paths do NOT equal 30 years of new historical evidence.** Every path below is built only from the seven already-seen development years 2015–2021, reshuffled and repeated. The study cannot:
> - validate H028;
> - repair B4;
> - make H028 a candidate;
> - estimate the chance that H028 beats SPY in the real future;
> - create new market regimes;
> - replace the sealed Holdout.
>
> Because H028 was designed after seeing 2011–2021 and was evaluated repeatedly on it, **these frequencies are conditional robustness statistics, not unbiased probabilities.** For example, "H028 beat SPY in 98.7% of synthetic paths generated from the observed 2015–2021 return blocks" must never be read as "a 98.7% chance".

## Why the verdict is "highly sensitive"

The rule was fixed before any result (commit 0176090).
- "Favorable across most paths" required two things:
  - all three resampling methods beat SPY in at least 80% of 30-year paths (and the primary method beat LV15 in at least 80%);
  - **every** stress exclusion still beat SPY in at least 50%.
- **The first part holds:** 98.7%, 99.6% and 100% against SPY, and 99.8% against LV15.
- **The second fails on one stress:** with 2018 and 2020 removed from the donor years, H028 beat SPY in only **9.3%** of 30-year paths.

The favourable picture against SPY rests on a few donor years. H028 beat SPY in only 3 of the 7 real years (2017, 2018 and 2020). Without 2018 and 2020 recurring, it finishes behind SPY in most remixed histories. **Against LV15 the picture is much sturdier:** it stays ahead in 94% of 30-year paths even without 2018 and 2020.

## Direct answers

**Q1 — How often does H028 finish above SPY?** Complete-year remixes of 2015–2021:

| Horizon | Above SPY | Below SPY |
|---|---|---|
| 5 years | 78.1% | 21.9% |
| 10 years | 89.2% | 10.8% |
| 20 years | 96.5% | 3.5% |
| 30 years | 98.7% | 1.3% |

The median 30-year wealth ratio is 2.58× SPY, with a median excess CAGR of +3.7 points a year.

**Q2 — How often does H028 finish above LV15?** 87.9% / 95.2% / 99.2% / 99.8% of paths after 5 / 10 / 20 / 30 years; the median 30-year ratio is 5.5×.

**Q3 — How long can H028 look broken against SPY?**
- **Losing streaks:** the median path contains a run of **5 consecutive years** behind SPY. 10% of paths have 8 or more; 3.5% have 10 or more; the longest is 21.
- **Losing years overall:** H028 is behind SPY in a median of 17 of the 30 years (it wins a median 13 years). That mirrors the real record of 3 winning years out of 7.
- **Five-year windows:** 97% of paths contain at least one 5-year window behind SPY; 77% trail by 10% or more over some 5-year window, and 32% by 20% or more.
- **Time below the previous relative peak:** the median longest stretch is 91 months (7.6 years); the 90th percentile is 15 years. In 17% of paths H028 is still below its earlier relative peak at the end of the 30 years.

**Q4 — How bad can the relative drawdown become?** The largest fall in wealth relative to SPY is:

| Percentile | Relative drawdown |
|---|---|
| Median | −21% |
| 95th | −34% |
| 99th | −40% |
| Worst | −57% |

Against LV15: median −23%, 95th percentile −39%.

**Q5 — Does it stay favourable under 12- and 24-month blocks? Yes, and more so.** 30-year paths ahead of SPY:
- 12-month blocks: 99.6%;
- 24-month blocks: 100%.

Losing streaks are shorter (median 3 years) and drawdowns smaller. Calendar-year blocks are the harshest of the three methods.

**Q6 — How much does it depend on 2018?** A lot. Leaving 2018 out:
- paths ahead of SPY at 30 years: 98.7% → 82.0%;
- median ratio: 2.58× → 1.40×;
- 5th percentile ratio: 1.27× → 0.77×;
- median excess CAGR: +3.7 → +1.35 points.

The number of times 2018 is drawn correlates +0.63 with the 30-year outcome, the strongest of any year.

**Q7 — How much does it depend on 2020?** Also substantially. Leaving 2020 out:
- paths ahead of SPY: 88.3%;
- median ratio: 1.63×;
- 5th percentile: 0.84×;
- median excess CAGR: +1.9 points;
- correlation with the 30-year outcome: +0.48.

**Q8 — What happens when both are removed?** The edge against SPY disappears. At 30 years:
- H028 is ahead of SPY in only **9.3%** of paths;
- median ratio 0.69× (H028 ends about 31% behind);
- median excess CAGR **−1.45 points** a year;
- median longest losing streak 10 years, and in 91% of paths H028 is still below its earlier relative peak at the end.

**Against LV15 it still wins** in 93.6% of paths (median 2.38×). This stress is deliberately harsh (owner section 25) and is not a realistic probability model.

**Q9 — Does this strengthen the case for an economically interesting development signal?**
- **Partly, and only against LV15.** In the observed years the learned score's lead over the pure low-volatility portfolio is broad and durable under every remix:
  - every single-year exclusion still beats LV15 in ≥ 98% of paths;
  - removing both 2018 and 2020 still leaves 94%;
  - the observed 7-year annualised log edge over LV15 is +5.7%, with a resampling interval of −2.2% to +13.2%.
- **Its lead over SPY is not robust:** it depends on two defensive years recurring. The observed 7-year annualised edge over SPY is +3.2%, with a resampling interval of −2.4% to +9.3% (negative in 15% of resamples).
- **Nothing here changes H028's status:** it remains **REJECTED** under its original B4 failure.

**Q10 — What can this study NOT tell us?**
- Whether 2015–2021-like environments will recur, or in what proportions.
- Anything about market regimes not seen in those seven years.
- Whether H028's development-period edge is real rather than fitted. The design already used these years, so selection bias is not removed.
- Any probability of future success.
- Anything about the 2022–2026 Holdout. The resampling also treats years as interchangeable and ignores dependence between consecutive years beyond 24 months.

## Required items

### Governance

1. **H028 status:** permanently **REJECTED** — FIXED STRONG SHRINKAGE DOES NOT ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM. B4 is not repaired, no gate is changed, and there is no candidate.
2. **Study purpose:** conditional on the 2015–2021 behaviour, how sensitive is H028's long-run result against SPY and LV15 to the order and repetition of those observed environments (owner D223)?
3. **Synthetic-data limitation:** stated in the box at the top and in Q10.

### Donor data

4. **Donor period:** 2015-01 → 2021-12 (development data only). Nothing after 2021-12-31 exists in the source. The Holdout is untouched.
5. **Donor months:** 84 paired months (H028, LV15, SPY always taken together).

   Donor calendar years:

   | Year | H028 | LV15 | SPY | H028 vs SPY | H028 vs LV15 |
   |---|---|---|---|---|---|
   | 2015 | −3.5% | +9.5% | +0.7% | behind | behind |
   | 2016 | +6.2% | +11.8% | +12.0% | behind | behind |
   | 2017 | +31.8% | +11.0% | +21.7% | **ahead** | ahead |
   | 2018 | +11.6% | +4.2% | −4.6% | **ahead** | ahead |
   | 2019 | +27.9% | +19.3% | +31.2% | behind | ahead |
   | 2020 | +34.4% | +11.9% | +18.3% | **ahead** | ahead |
   | 2021 | +26.9% | +16.7% | +29.1% | behind | ahead |

6. **Monthly-series reconciliation:**
   - **Source and method:** month-end marks of the committed E030-05 daily equity paths. Compounding the 84 monthly returns reproduces each path's final mark to 1e-12.

   | Series | Reconstructed (pre-liquidation) | Committed (after liquidation) | Difference = liquidation |
   |---|---|---|---|
   | H028 | $328,728.64 | $328,294.91 | $433.73 |
   | LV15 | $220,479.26 | $220,156.03 | $323.22 |
   | SPY | $262,595.05 | $262,325.46 | $269.60 |

7. **Final-liquidation audit: the artifact is excluded by construction.** The daily paths are mark-to-market *before* the terminal liquidation. The frozen simulator applies the liquidation only to the reported terminal wealth, so the donor December-2021 return contains no liquidation and nothing had to be removed. The difference between the two wealth figures is exactly the liquidation:
   - **SPY:** committed = last mark × 0.999 − $7, exactly.
   - **H028:** implied $433.73 = expected 0.1% × last mark × (1 − cash 0%) + $7 × 15 holdings, exactly.
   - **LV15:** implied $323.22 vs expected $323.12 (tolerance $51).

   Not altered (disclosed only): the January 2015 entry costs. H028's first month cost $105 in commissions plus $100 in slippage; SPY's entry cost is 0.107%. These are part of the recorded first-month returns, so each time 2015 is drawn the same small entry cost recurs.

### Method and results

8. **Primary algorithm (complete calendar years):**
   - Each world draws 30 of the 7 calendar years uniformly with replacement.
   - Each year keeps its 12 months in order.
   - The same block applies to H028, LV15 and SPY.
   - The blocks are concatenated into 360 months starting at $100,000, compounded in logs.
9. **World counts:**
   - 10,000 each: primary, 12-month, 24-month, and 2018+2020 exclusion;
   - 5,000 per leave-one-year-out;
   - 100,000 seven-year resamples.
10. **Seeds:** 1 → 10,000 (1 → 5,000 for leave-one-out). The generator is numpy `default_rng(SeedSequence([method code, seed]))`, with codes year 1, 12-month 2, 24-month 3, leave-Y-out 10–16, 2018+2020 exclusion 20, and the 7-year resampling 30 with seed 1.

11–14. **Horizon results** (primary; the share of paths, then the median and 5th–95th percentile ratio):

| Horizon | > SPY | > LV15 | ≥ 1.15 × SPY | Excess CAGR ≥ +2 pts | H028/SPY median (5–95%) | H028/LV15 median (5–95%) | Excess CAGR median (5–95%) |
|---|---|---|---|---|---|---|---|
| 5 y | 78.1% | 87.9% | 53.2% | 64.0% | 1.16 (0.87–1.59) | 1.32 (0.88–1.95) | +3.5 (−3.5 to +10.6) pts |
| 10 y | 89.2% | 95.2% | 75.0% | 70.7% | 1.36 (0.91–2.10) | 1.80 (1.01–3.01) | +3.6 (−1.1 to +8.7) |
| 20 y | 96.5% | 99.2% | 91.9% | 78.8% | 1.88 (1.06–3.45) | 3.14 (1.44–6.63) | +3.7 (+0.3 to +7.2) |
| 30 y | 98.7% | 99.8% | 97.1% | 83.4% | 2.58 (1.27–5.37) | 5.50 (2.15–13.73) | +3.7 (+0.9 to +6.5) |

Paths ending **below** SPY: 21.9% / 10.8% / 3.5% / 1.3%. Below LV15: 12.1% / 4.9% / 0.8% / 0.2%.

15. **H028/SPY distribution:** interquartile range at 30 years 1.92–3.49; at 5 years 1.02–1.33.
16. **H028/LV15 distribution:** interquartile range at 30 years 3.75–8.11; at 5 years 1.14–1.58.
17. **Excess CAGR:** see the table above. It is stable at about +3.5 to +3.7 points in the median, with a wide spread at short horizons.
18. **Longest losing-year streaks (primary):**

    | Benchmark | Median | p75 | p90 | p95 | p99 | Max | ≥ 3 yrs | ≥ 5 yrs | ≥ 10 yrs |
    |---|---|---|---|---|---|---|---|---|---|
    | SPY | 5 | 6 | 8 | 9 | 12 | 21 | 97.2% | 56.7% | 3.5% |
    | LV15 | 2 | 3 | 4 | 4 | 5 | 11 | 40.5% | 3.7% | 0.01% |

    Winning years out of 30, median (5–95%): vs SPY 13 (8–17); vs LV15 21 (17–25).
19. **Relative drawdowns** (worse-tail percentiles):

    | Benchmark | Median | p75 | p90 | p95 | p99 | Worst |
    |---|---|---|---|---|---|---|
    | SPY | −21.3% | −25.5% | −30.3% | −33.7% | −40.4% | −56.8% |
    | LV15 | −23.2% | −28.5% | −34.9% | −39.0% | −47.3% | −64.2% |

20. **Rolling 5-year underperformance** (paths with at least one such 5-year window):

    | Benchmark | Behind | ≥ 10% behind | ≥ 20% behind |
    |---|---|---|---|
    | SPY | 97.0% | 76.7% | 31.6% |
    | LV15 | 80.3% | 56.1% | 29.0% |

21. **Longest time below a relative high** (months; years in brackets):
    - **SPY:** median 91 (7.6), p90 185 (15.4), p95 222 (18.5), p99 304 (25.3); 17.0% of paths still below at month 360.
    - **LV15:** median 66 (5.5), p90 131 (10.9), p95 162 (13.5), p99 229 (19.1); 11.0% still below.
22. **12-month moving blocks** (73 donor blocks, no wrap):
    - Ahead of SPY at 5 / 10 / 20 / 30 years: 85.3% / 93.9% / 98.8% / 99.6%; ahead of LV15 at 30 years: 100%.
    - 30-year median ratio 3.00×; 5th percentile 1.52×; median excess CAGR +4.3 pts.
    - SPY losing streak: median 3 years, ≥ 5 years in 19.7%.
    - Relative drawdown vs SPY: median −19.7%, 95th percentile −30.6%.
23. **24-month moving blocks** (61 donor blocks, no wrap):
    - Ahead of SPY: 92.5% / 98.0% / 99.8% / 100%; ahead of LV15 at 30 years: 100%.
    - Median ratio 4.38×; 5th percentile 2.22×; median excess CAGR +5.8 pts.
    - SPY streak ≥ 5 years in 9.6%.
    - Relative drawdown vs SPY: median −17.2%, 95th percentile −26.2%.
24. **Method sensitivity** (30 years, vs SPY):

    | Method | > SPY | Median ratio | 5th percentile | Median excess CAGR | 5-year losing streak | 95th percentile relative MaxDD |
    |---|---|---|---|---|---|---|
    | Calendar years | 98.7% | 2.58 | 1.27 | +3.7 pts | 56.7% | −33.7% |
    | 12-month blocks | 99.6% | 3.00 | 1.52 | +4.3 pts | 19.7% | −30.6% |
    | 24-month blocks | 100% | 4.38 | 2.22 | +5.8 pts | 9.6% | −26.2% |

    **The direction is robust to the block construction.** Moving blocks are *more* favourable because they break the calendar-year pattern in which H028 lagged SPY in 4 of 7 years.

25–31. **Leave-one-year-out** (5,000 worlds each; 30 years):

| Excluded | > SPY | Median ratio | 5th percentile | Median excess CAGR | > LV15 |
|---|---|---|---|---|---|
| 2015 | 99.9% | 3.77 | 1.87 | +5.3 pts | 100% |
| 2016 | 100% | 4.02 | 2.01 | +5.5 | 100% |
| 2017 | 94.5% | 2.05 | 0.98 | +2.8 | 98.1% |
| 2018 | **82.0%** | 1.40 | 0.77 | +1.35 | 99.5% |
| 2019 | 99.8% | 3.48 | 1.68 | +4.8 | 99.6% |
| 2020 | **88.3%** | 1.63 | 0.84 | +1.9 | 98.0% |
| 2021 | 99.5% | 3.35 | 1.57 | +4.6 | 99.4% |

32. **Leave 2018 and 2020 out** (10,000 worlds):

    | Horizon | > SPY | > LV15 | Median H028/SPY | Median excess CAGR |
    |---|---|---|---|---|
    | 5 y | 27.0% | 73.5% | 0.94 | −1.5 pts |
    | 10 y | 21.1% | 80.6% | 0.88 | −1.5 |
    | 20 y | 13.5% | 89.4% | 0.78 | −1.5 |
    | 30 y | **9.3%** | 93.6% | 0.69 | −1.45 |

    - At 30 years: 5th–95th percentile 0.46–1.09; median ratio vs LV15 2.38.
    - SPY losing streak: median 10 years, ≥ 10 years in 50%.
    - Relative drawdown vs SPY: median −41%.
    - 91% of paths are still below their earlier relative peak at the end.
33. **7-year resampling interval** (100,000 samples; descriptive, *not* a confidence interval for future alpha):

    | Annualised log-relative | Observed | Median | 2.5–97.5% | Share negative |
    |---|---|---|---|---|
    | vs SPY | +3.21% | +3.18% | −2.37% to +9.34% | 14.9% |
    | vs LV15 | +5.71% | +5.76% | −2.21% to +13.15% | 8.0% |

34. **Regime frequency** (primary):
    - Each year is drawn 14.1–14.4% of the time (uniform 14.3%), so the sampling is uniform.
    - Correlation between a year's count and the 30-year log(H028/SPY):
      - positive: 2018 **+0.63**, 2020 **+0.48**, 2017 +0.25;
      - negative: 2016 −0.45, 2015 −0.36, 2019 −0.29, 2021 −0.25.
    - Median 30-year ratio when 2018 is drawn at most twice: 1.75×; 3–5 times: 2.47×; 6 or more times: 3.75×. For 2020: 1.92×, 2.47×, 3.45×.
35. **2018/2020 dependence:** quantified in Q6–Q8 and items 28, 30 and 32.
    - Each year alone carries a large part of the SPY edge: excluded alone, the median ratio falls from 2.58× to 1.40× (2018) or 1.63× (2020).
    - Together they carry all of it, and more.
    - The LV15 edge does not depend on them.

### Reproducibility and confirmations

36. **Reproducibility.**
    - Seeds 1–100 of every method (all 11 simulation sets) were rerun independently; every per-world metric is identical.
    - Per-world metric digests are in the output.
    - The methodology was committed before any aggregate (0176090). One serialisation-only fix (ec071bb) followed a crash before any result was printed.
    - `tests/test_p13_cp3_bootstrap.py` checks the mechanics on synthetic data and the committed output. During development it caught one bug: exclusions were not applied when the sampler was called directly. That was fixed before the commit and before any result.
37. **No parameter changes:** λ, features, weights, target, Top-15, sector cap, rebalancing, costs, execution and the LOWVOL definition are untouched. Nothing was retrained.
38. **No new QuantConnect run.**
39. **No new data:** no external or purchased data. The only source is the committed E030-05 output.
40. **Holdout untouched** (2022-01-01 → 2026-08-31).
41. **Direct answers Q1–Q10:** at the top of this report.

## Integrity summary

| Item | Value |
|---|---|
| New hypotheses / strategies / experiments | 0 / 0 / 0 |
| Source | E030-05 QRHR block (SHA-256 in the output JSON) |
| Methodology commit (before any aggregate) | 0176090 (+ ec071bb serialisation fix) |
| Output | `research/phase13/cp3/P13_CP3_bootstrap.json` |

## 42. Next owner decision

H028 remains REJECTED; this study changes no status.

**What it adds:** within the observed environments, H028's advantage over LV15 is durable. Its advantage over SPY depends heavily on two defensive years (2018, 2020) recurring. Even when favourable, an investor would typically have faced a 5-year losing streak against SPY and a 7- to 15-year stretch below a previous relative high.

Please choose one:

1. **Close Phase 13 and the learned-score line** (recommended). Any further work on this score would keep re-using the same seven years.
2. **Record the study as context only**, and define a genuinely new, separately pre-registered direction. Any such direction must not be motivated by the 2018/2020 dependence shown here, since that would be hindsight.
3. **Consider, as a separate owner decision, whether a frozen version of any learned score should ever face the sealed Holdout.** Nothing in this study authorises that; H028 itself is rejected.

Do not start H029 and do not open the Holdout without the owner's explicit instruction.
