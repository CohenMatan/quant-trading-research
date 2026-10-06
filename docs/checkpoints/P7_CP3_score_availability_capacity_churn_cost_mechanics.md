# P7-CP3 — Score Availability, Capacity, Churn and Cost Mechanics

- **Status:** checkpoint report, 2026-10-06. Owner decision D171 authorised this study; this report is D172.
- **What it is:** the frozen Conviction Score v1, computed on real 2011–2017 data. It measures how many stocks qualify, how long they stay qualified, how full a portfolio could be, how many orders the mechanics would generate and what those orders would cost.
- **What it is NOT:** a backtest. No future return, strategy return, SPY return, IC, CAGR, Sharpe, drawdown, win rate or profit factor was computed, and none was used for anything.
- **Who decides:** nothing is chosen here. The owner selects the entry threshold, exit threshold, replacement buffer, maximum positions, regime exposure ceilings, any relaxation ladder and the grown-winner cap (section 12).
- **Data:**
  - QuantConnect export E993-01: X993 v1.0, non-trading, 0 orders.
  - Offline mechanics: `research/phase7/P7_CP3_mechanics.py`, which writes `P7_CP3_mechanics.json` and `P7_CP3_tables.md`.
  - Raw score tables: `research/phase7/P7_CP3_E993_payload.json.gz`, holding integer points, disqualifier flags, ADV20 and sector codes. There are no prices.

## 0. The answer in brief

1. **High scores are genuinely rare.** Among about 425 fully eligible stocks per month:
   - 75+: 3.7% of scored stock-months (about 15.6 stocks a month);
   - 80+: 1.4% (about 6.1 a month);
   - 85+: 0.4% (about 1.6);
   - 90+: 0.13% (about 0.5).
   - This is almost exactly what the P7-CP2 synthetic estimate predicted: median 43, with 1.4–3.0% at 80+.
2. **High scores need broad strength.** No 80+ stock-month had a weak layer:
   - Technical ≥ 23 / 40;
   - Fundamental ≥ 25 / 45;
   - Sector ≥ 8 / 15.
3. **High scores are short-lived.** At every threshold, the median spell above the threshold is **1 month**:
   - only 20% of 80+ spells survive 3 months;
   - only 5% survive 6 months.
   - The usual cause is a 7-point step in the trend state (strong → moderate) or the sector state (supportive → neutral), or a volatility-quintile drop.
4. **Consequence: holdings would last weeks to a few months, not a year.** Even the Patient profile (exit 15 points below entry, buffer 10) gives a median implied holding of about **3 months**. Fewer than 6% of positions last 12 months.
5. **Strictness trades against fullness:**
   - 90+ almost never fills more than 1–2 slots;
   - 85+ leaves most of a 6–12-slot book in cash;
   - 80+ fills 6 slots in 46% of months but 10 slots in only 21%;
   - 75+ fills 10 slots in 76% of months.
6. **Mechanical costs** at $100K range from about 0.1% a year (90+) to 1.7% (75+, Tight, 12 slots).
   - At 80+ they are 0.55–1.04%.
   - The Patient profile is consistently cheapest at the same entry and size.
7. **The market regime was STRONG in 63 of 84 months (75%).**
   - RISK_OFF occurred in 5 months, in 3 short episodes (2011-08/09, 2015-09, 2016-01/02).
   - The regime never alters a score or the ranking.
8. **Hard-disqualifier exclusions are dominated by fundamental-data availability (H2).**
   - H2 removes about a third of non-financial stocks each month.
   - 29–51% of non-financial H2 cases (depending on the year) are only a missing 12-month revenue baseline. Of those, 39–71% had a revenue history in the PIT store but were not in the eligible universe a year earlier.
   - This is an implementation reading of the frozen spec that the owner should confirm (decision 9).

## 1. Integrity of the run (items 1–5, 48–51)

| # | Item | Result |
|---|---|---|
| 1 | Score v1 fingerprint | `qr_p7_score.py` uploaded from commit `09dafb5` = SHA-256 `84b673…1572` = the P7-CP2 pin (`qresearch.p7score`; pin tests pass). QuantConnect stores the file with one appended newline; the in-host hash `430ce2…6c9d` equals the pinned bytes + `\n`, nothing else. `qr_p7.py` likewise unchanged. No weight, threshold or disqualifier changed |
| 2 | QuantConnect run | E993-01, backtest `d9be90c88086ab8f46cd3a04c452a723`, project 37430499, LEAN 2.5.0.0.18131, commit `09dafb54`, runtime 712 s (end-of-run pipeline 549 s, peak memory 6.2 GB) |
| 3 | Orders | **0** (QuantConnect Total Orders 0; harness orders 0; all 23 runner integrity checks pass). The runner's standard report shows its usual metric template for an untouched $100K cash account (all zeros); no strategy or return figure exists |
| 4 | Dates | Official 2011-01-03 → 2017-12-31; history-only warm-up from 2008-07-01 (2010 month-ends used only as the revenue-baseline ledger); price history 2007-01-03 → 2017-12-29. Nothing after 2017-12-29 was requested (late rows 0, late events 0) |
| 5 | Score dates | **84 monthly reviews** (last session of each month, 2011-01-31 → 2017-12-29) + **325 weekly checks**; both match the SPY session calendar exactly (in-host check) |
| — | Exact technical computation | The fast sliced computation equals the full-history computation on 336 in-host spot checks (0 mismatches) and in offline tests; 2,109 short-history cases used the full history automatically |
| 48 | No return / performance | No return-like field exists in the export or the offline outputs (checked by the extract script and by `tests/test_p7_cp3_mechanics.py`). The shadow book uses no price, equity or P&L: a constant mechanical notional |
| 49 | 2018–2021 | Untouched (the host refuses an end after 2017-12-31; the run's last session is 2017-12-29) |
| 50 | Holdout | Untouched (`HOLDOUT_UNLOCK.md` unchanged; no 2022+ data) |
| 51 | Purchases | None. QuantConnect $24/month subscription only |

## 2. Universe, funnel and disqualifiers (items 6–8)

**Item 6 — base eligible universe** (data-v1: ≥ $2B, ≥ $5, ADV20 ≥ $5M, NYSE/Nasdaq; mean per review, min–max): 2011 922 (834–983), 2012 932, 2013 1,072, 2014 1,198, 2015 1,222, 2016 1,180, 2017 1,281 (1,249–1,320).

**Item 7 — exclusion funnel** (sequential; each row = stocks remaining after that step; mean per monthly review):

| Stage (stock count after the step; mean per review) | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | All |
|---|---|---|---|---|---|---|---|---|
| base eligible universe | 922.4 | 931.8 | 1071.7 | 1198.3 | 1222.2 | 1179.7 | 1281.1 | 1115.3 |
| duplicate share class | 919.4 | 928.8 | 1068.5 | 1193.9 | 1216.9 | 1174.1 | 1272.8 | 1110.6 |
| Financial / REIT (H1) | 758.3 | 759.5 | 867.8 | 954 | 953.9 | 906.2 | 979.8 | 882.8 |
| insufficient history (H3) | 743.6 | 742.2 | 845.6 | 922.8 | 929.1 | 891.2 | 953.8 | 861.2 |
| fundamental data (H2) | 414.2 | 477 | 544.9 | 633.8 | 679 | 668 | 665.9 | 583.3 |
| sector data: no SIC (H1) | 393.5 | 460.2 | 529.6 | 622.8 | 664.5 | 654.4 | 652.8 | 568.3 |
| corporate event (H4) | 392 | 456.7 | 524.3 | 616.8 | 659.1 | 652.1 | 650.5 | 564.5 |
| stale price (H5) | 392 | 456.7 | 524.3 | 616.8 | 659.1 | 652.1 | 650.5 | 564.5 |
| technical DQ: broken trend (H6) | 296 | 366.6 | 475.8 | 519.9 | 445.8 | 465.4 | 527.2 | 442.4 |
| fundamental DQ: impairment (H7) | 287 | 355.8 | 462.2 | 504.7 | 423.3 | 441.7 | 501.3 | 425.2 |
| fully scorable and eligible (no hard disqualifier) | 287 | 355.8 | 462.2 | 504.7 | 423.3 | 441.7 | 501.3 | 425.2 |
| score >= 75 | 13 | 14.5 | 9.2 | 14.2 | 20.4 | 15.2 | 22.9 | 15.6 |
| score >= 80 | 5.6 | 4.8 | 2.8 | 5.5 | 7.2 | 6.2 | 10.5 | 6.1 |
| score >= 85 | 1 | 0.9 | 0.2 | 1.6 | 3.4 | 1.6 | 2.6 | 1.6 |
| score >= 90 | 0.6 | 0.1 | 0 | 0.5 | 1.3 | 0.5 | 0.8 | 0.5 |

The funnel shows exactly why the candidate set is small:
- About 21% of the universe is financial / REIT.
- About a third of the remaining stocks fail the fundamental-data rule (H2).
- About 20% of the rest are in a broken long-term trend (H6), and in 2015 this reached about a third.

**Item 8 — hard-disqualifier counts and overlaps:**

| Flag | Share of kept-class rows | Rows where it is the only flag |
|---|---|---|
| H1 financial / REIT | 20.5% | 3,987 |
| H1 no SEC SIC | 3.6% | 1,044 |
| **H2 fundamentals missing / stale** | **41.9%** | 17,692 |
| H3 < 253 bars | 2.3% | 0 (always with another) |
| H4 corporate event | 0.8% | 126 |
| H5 stale price | 0.0% | 0 |
| **H6 broken trend** | **19.9%** | 9,841 |
| H7 impairment | 2.1% | 1,446 |

- The base is 93,293 kept-class stock-months; 35,713 (38%) carry no flag.
- Largest overlaps:
  - H1-financial & H2: 13,884 (financials often lack the industrial fields);
  - H2 & H6: 6,698;
  - H1-financial & H6: 3,785.
- **Is one disqualifier responsible for most exclusions? Yes: H2.** It is dominant mainly among financials, and also among non-financial stocks (about 26–43% of non-financial rows a year).
- **Not relaxed.** Breakdown of non-financial H2 rows by year:

| Year | Non-financial rows | H2 | of which only the 12-month revenue baseline is missing | of those, a revenue history existed in the PIT store 12 months earlier |
|---|---|---|---|---|
| 2011 | 8,286 | 3,564 (43%) | 1,040 | 735 |
| 2012 | 8,591 | 3,068 (36%) | 1,334 | 521 |
| 2013 | 9,929 | 3,574 (36%) | 1,521 | 867 |
| 2014 | 11,018 | 3,544 (32%) | 1,817 | 798 |
| 2015 | 11,028 | 3,054 (28%) | 1,335 | 636 |
| 2016 | 10,560 | 2,707 (26%) | 1,314 | 608 |
| 2017 | 11,392 | 3,559 (31%) | 1,577 | 1,054 |

The frozen spec says the revenue baseline is "the True TTM recorded at the review 12 months earlier". D171 implemented this as recorded **for the securities eligible at that review** (the ledger construction audited in P7-CP1).
- A stock that was below $2B, or not yet listed, a year earlier therefore has no baseline and is excluded (H2) for its first 12 months in the universe.
- A store-wide ledger could rescue up to about 6–9% of non-financial rows a year.
- This is a definition choice, not a bug. It is **not** changed here and is listed as owner decision 9. Missing-data protection stays in force: every excluded stock stays out of every rank and denominator.

## 3. Score distributions (items 9–15)

**Items 9–10 — total score, share of stock-months by bin** (fully eligible stocks, no hard disqualifier; 35,713 stock-months):

| Year | 0–49 | 50–59 | 60–69 | 70–74 | 75–79 | 80–84 | 85–89 | 90–94 | 95–100 | ≥ 75 | ≥ 80 | ≥ 85 | ≥ 90 | Median / p99 / max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2011 | 52.4% | 22.5% | 16.0% | 4.6% | 2.6% | 1.6% | 0.1% | 0.2% | 0.0% | 4.53% | 1.95% | 0.35% | 0.20% | 48 / 81 / 93 |
| 2012 | 55.8% | 21.2% | 14.5% | 4.5% | 2.7% | 1.1% | 0.2% | 0.0% | 0.0% | 4.07% | 1.36% | 0.26% | 0.02% | 47 / 80 / 93 |
| 2013 | 54.3% | 25.4% | 14.9% | 3.4% | 1.4% | 0.5% | 0.1% | 0.0% | 0.0% | 2.00% | 0.59% | 0.05% | 0.00% | 48 / 78 / 87 |
| 2014 | 56.3% | 23.5% | 14.1% | 3.3% | 1.7% | 0.8% | 0.2% | 0.1% | 0.0% | 2.82% | 1.09% | 0.31% | 0.10% | 47 / 80 / 90 |
| 2015 | 52.3% | 23.2% | 15.6% | 4.0% | 3.1% | 0.9% | 0.5% | 0.3% | 0.0% | 4.82% | 1.69% | 0.81% | 0.31% | 48 / 83 / 93 |
| 2016 | 54.8% | 21.9% | 15.8% | 4.1% | 2.0% | 1.0% | 0.2% | 0.1% | 0.0% | 3.43% | 1.40% | 0.36% | 0.11% | 48 / 81 / 90 |
| 2017 | 50.6% | 24.3% | 15.5% | 4.9% | 2.5% | 1.6% | 0.4% | 0.2% | 0.0% | 4.57% | 2.09% | 0.52% | 0.17% | 49 / 82 / 94 |
| all | 53.8% | 23.3% | 15.2% | 4.1% | 2.2% | 1.1% | 0.2% | 0.1% | 0.0% | 3.68% | 1.43% | 0.38% | 0.13% | 48 / 80 / 94 |

All data-scorable stocks (including those later removed by H6 / H7; 47,417 stock-months):

| Year | 0–49 | 50–59 | 60–69 | 70–74 | 75–79 | 80–84 | 85–89 | 90–94 | 95–100 | ≥ 75 | ≥ 80 | ≥ 85 | ≥ 90 | Median / p99 / max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2011 | 63.0% | 17.8% | 12.2% | 3.5% | 1.9% | 1.2% | 0.1% | 0.1% | 0.0% | 3.38% | 1.45% | 0.26% | 0.15% | 43 / 80 / 93 |
| 2012 | 63.6% | 17.8% | 11.7% | 3.7% | 2.1% | 0.9% | 0.2% | 0.0% | 0.0% | 3.21% | 1.06% | 0.20% | 0.02% | 42 / 80 / 93 |
| 2013 | 58.1% | 23.4% | 13.6% | 3.1% | 1.2% | 0.5% | 0.1% | 0.0% | 0.0% | 1.76% | 0.52% | 0.05% | 0.00% | 46 / 77 / 87 |
| 2014 | 62.6% | 20.2% | 12.0% | 2.8% | 1.5% | 0.6% | 0.2% | 0.1% | 0.0% | 2.38% | 0.89% | 0.26% | 0.08% | 44 / 79 / 90 |
| 2015 | 66.2% | 17.1% | 10.8% | 2.8% | 2.1% | 0.6% | 0.3% | 0.2% | 0.0% | 3.15% | 1.10% | 0.52% | 0.20% | 41 / 80 / 93 |
| 2016 | 65.9% | 17.1% | 11.5% | 3.0% | 1.5% | 0.7% | 0.2% | 0.1% | 0.0% | 2.43% | 0.97% | 0.24% | 0.08% | 41 / 79 / 90 |
| 2017 | 59.9% | 19.9% | 12.7% | 4.0% | 2.0% | 1.2% | 0.3% | 0.1% | 0.0% | 3.59% | 1.61% | 0.40% | 0.13% | 45 / 81 / 94 |
| all | 62.9% | 19.0% | 12.0% | 3.2% | 1.7% | 0.8% | 0.2% | 0.1% | 0.0% | 2.83% | 1.08% | 0.29% | 0.10% | 43 / 80 / 94 |

- **Are 80+ / 85+ / 90+ genuinely difficult? Yes.** Only about 1 eligible stock-month in 70 reaches 80, 1 in 260 reaches 85, and 1 in 780 reaches 90. No stock ever reached 95 (maximum 94).
- 2013 had no 90+ stock at all.
- 2015 and 2017 were the richest years.

**Items 11–14 — layers** (data-scorable stock-months):

| Layer | Mean | p10 | p25 | Median | p75 | p90 | Max |
|---|---|---|---|---|---|---|---|
| Technical (0–40) | 17.6 | 0 | 7 | 18 | 28 | 33 | 40 |
| Fundamental (0–45) | 18.0 | 6 | 10 | 17 | 25 | 32 | 45 |
| Sector (0 / 8 / 15) | 7.6 | 0 | 8 | 8 | 8 | 15 | 15 |
| Total (0–100) | 43.2 | 21 | 31 | 43 | 55 | 65 | 94 |

- Sector state shares: weak 18%, neutral 67%, supportive 15%.
- Pairwise correlations (pooled Pearson; the mean per-review Spearman is very close):

| | Technical | Fundamental | Sector |
|---|---|---|---|
| Fundamental | −0.04 | | |
| Sector | 0.22 | −0.02 | |
| Total | 0.76 | 0.57 | 0.41 |

- Technical and Fundamental are almost independent (−0.04), so a high total really needs both.

**Item 15 — composition of high scores** (pooled eligible stock-months at or above the threshold):

| | 75+ | 80+ | 85+ | 90+ |
|---|---|---|---|---|
| Stock-months / distinct stocks | 1,314 / 256 | 510 / 148 | 136 / 50 | 46 / 19 |
| Mean Technical / Fundamental / Sector | 33.4 / 34.4 / 11.3 | 34.3 / 36.9 / 12.0 | 35.7 / 39.2 / 13.0 | 35.5 / 41.3 / 14.1 |
| Minimum Technical / Fundamental / Sector | 18 / 20 / 0 | **23 / 25 / 8** | 28 / 30 / 8 | 30 / 35 / 8 |
| Share with a weak layer (Tech < 20, Fund < 22.5 or Sector 0) | 3.7% | **0%** | 0% | 0% |
| Trend state strong | 93% | 98% | 99% | 98% |
| Sector supportive / neutral | 47% / 52% | 57% / 43% | 72% / 28% | 87% / 13% |
| Momentum at maximum (Q5) | 74% | 83% | 85% | 96% |
| GP/A at maximum (Q5 in sector) | 64% | 76% | 73% | 91% |
| Low volatility at maximum (Q5) | 32% | 34% | 44% | 41% |
| Median ADV20 | $68M | $69M | $65M | $80M |

- **An 85 cannot be built from one strong category.** The maxima without a layer are:
  - without Technical: 60;
  - without Fundamental: 55;
  - without Sector: 85, and that would need a perfect 40 + 45.
- In the data, 80+ always had at least 23 / 40 Technical and 25 / 45 Fundamental.
- Typical 85+ profile: strong trend, top-quintile momentum and sector-relative GP/A, above-median balance sheet and cash conversion, in a supportive or neutral sector.

## 4. Candidates at each threshold (items 16–21)

**Items 16–21 — candidates per monthly review** (eligible, one class per company):

| Entry | Mean | Median | Min | Max | p10 | p25 | p75 | p90 | 0 | 1–2 | 3–5 | 6–8 | 9–10 | >10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 90 | 0.5 | 0 | 0 | 4 | 0 | 0 | 1 | 2 | 64% | 32% | 4% | 0% | 0% | 0% |
| 85 | 1.6 | 1 | 0 | 8 | 0 | 0 | 2 | 5 | 37% | 40% | 15% | 7% | 0% | 0% |
| 80 | 6.1 | 5 | 0 | 18 | 1 | 3 | 9 | 12 | 2% | 21% | 30% | 18% | 11% | 18% |
| 75 | 15.6 | 13.5 | 2 | 36 | 8 | 10 | 21 | 26 | 0% | 1% | 2% | 10% | 18% | 69% |

**Per year** (mean / median / min–max / months with zero candidates, out of 12):

| Entry | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|
| 90 | 0.6 / 0.5 / 0–2 / 6 | 0.1 / 0 / 0–1 / 11 | 0.0 / 0 / 0–0 / 12 | 0.5 / 0 / 0–2 / 8 | 1.3 / 1 / 0–4 / 3 | 0.5 / 0 / 0–4 / 9 | 0.8 / 1 / 0–2 / 5 |
| 85 | 1.0 / 1 / 0–3 / 5 | 0.9 / 1 / 0–2 / 4 | 0.2 / 0 / 0–1 / 9 | 1.6 / 0.5 / 0–8 / 6 | 3.4 / 3.5 / 0–8 / 2 | 1.6 / 1 / 0–5 / 4 | 2.6 / 2 / 0–7 / 1 |
| 80 | 5.6 / 4.5 / 1–11 / 0 | 4.8 / 4 / 1–9 / 0 | 2.8 / 2.5 / 0–6 / 1 | 5.5 / 5.5 / 1–17 / 0 | 7.2 / 7 / 0–15 / 1 | 6.2 / 5.5 / 1–12 / 0 | 10.5 / 10.5 / 4–18 / 0 |
| 75 | 13.0 / 12 / 9–21 / 0 | 14.5 / 13.5 / 8–23 / 0 | 9.2 / 9 / 6–16 / 0 | 14.2 / 12 / 2–32 / 0 | 20.4 / 21.5 / 8–32 / 0 | 15.2 / 15.5 / 5–25 / 0 | 22.9 / 21 / 13–36 / 0 |

- The month-to-month correlation of the counts is 0.30 (90+) and about 0.57 (75–85+), so availability drifts slowly with the market.
- Counts are lowest in 2013 and highest in 2015 and 2017.

## 5. Persistence and crossings (items 22–23)

**Spells above the threshold** (consecutive monthly reviews eligible with score ≥ E; open spells at 2017-12 are counted as observed):

| Entry | Runs | Median | p25 | p75 | p90 | Longest | Survive ≥ 2 m | ≥ 3 m | ≥ 6 m | ≥ 12 m | Re-entries (per yr) | Re-entries within 3 reviews | Median gap (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 90 | 27 | 1 | 1 | 1 | 2.4 | 11 | 15% | 12% | 9% | 0% | 8 (1.1) | 6 | 2.5 |
| 85 | 76 | 1 | 1 | 2 | 3 | 11 | 32% | 16% | 4% | 0% | 26 (3.7) | 13 | 3.5 |
| 80 | 267 | 1 | 1 | 2 | 4 | 12 | 40% | 20% | 5% | 0% | 119 (17.0) | 64 | 3 |
| 75 | 611 | 1 | 1 | 2 | 5 | 16 | 46% | 25% | 7% | 1% | 355 (50.7) | 193 | 3 |

**Patience band** (months from the first month ≥ E while the stock stays eligible and ≥ the exit level; median [p25–p75], p90; no portfolio constraint):

| Entry | Exit E−5 | Exit E−10 | Exit E−15 |
|---|---|---|---|
| 90 | 1 [1–2.5], p90 3.4 | 2 [1–4.5], p90 8 | 3 [2–6.5], p90 8.8 |
| 85 | 2 [1–3], p90 5.5 | 2 [1.75–5], p90 9 | 3 [2–8], p90 11.5 |
| 80 | 2 [1–3], p90 5.4 | 3 [2–5], p90 8 | 4 [2–7], p90 11 |
| 75 | 2 [1–4], p90 6 | 3 [2–6], p90 10 | 5 [2–8], p90 12 |

**Why high scores are short-lived** (month-to-month change of the total for 80+ stocks):
- Median change −4; 10th percentile −17.
- Half of the 80+ stocks are below 80 the next month.
- Among those that fell, the dimensions that lost points were:
  - trend state: 59%, mostly strong → moderate (−7);
  - sector state: 44% (supportive → neutral, −7);
  - volatility quintile: 30%;
  - momentum quintile: 25%;
  - cash conversion: 15%;
  - balance sheet: 9%;
  - growth: 8%;
  - GP/A: 7%.
- The fundamental layer is stable. Most churn comes from the technical and sector **step levels** and from the volatility rank.
- This is a property of the frozen score; nothing is changed.

**Item 23 — crossings above → below → above:**

| Threshold | Re-entries a year | Within 3 reviews of leaving | Median gap |
|---|---|---|---|
| 80 | 17 | 54% | 3 months |
| 75 | 51 | 54% | 3 months |

## 6. Sector concentration (item 24)

**Mean candidates per review by FF12 sector at 80+:**

| Sector | Candidates |
|---|---|
| Business equipment / technology | 1.8 |
| Other | 0.9 |
| Health | 0.9 |
| Utilities | 0.8 |
| Shops | 0.6 |
| Manufacturing | 0.4 |
| Non-durables | 0.2 |
| Telecom | 0.2 |
| Durables | 0.1 |
| Energy | 0.1 |
| Chemicals | 0.05 |

**Composition vs the universe:**
- Technology is 29% of 80+ names against 20% of the universe.
- Health is 15% against 9%.
- Utilities is 13% against 7%.
- Manufacturing is 6% against 13%.

**Concentration** in reviews with at least 5 candidates:

| Threshold | Median largest-sector share | Reviews where one sector exceeds 50% |
|---|---|---|
| 80+ | 50% | 18 of 45 |
| 75+ | 38% | 17 of 82 |
| 85+ | 50% | 5 of 11 |

**Changes through time:**
- Shops dominated in 2011.
- Utilities dominated in 2014 and 2016 (38% of 80+ names).
- Technology dominated in 2017 (55%).

**In the shadow books** at 80+ with K = 10, the most-held sector typically holds 40–50% of positions and sometimes 100%.

**Assessment:** this is a real mechanical concentration. The architecture ranks technology and utilities together whenever their sectors are broad. It is not proof of a problem with returns. Candidate rules for owner approval (not optimised, not run) are in item 47.

## 7. Market regime (items 25–28)

**Item 25 — frequency:**

| Regime | Months | Share |
|---|---|---|
| STRONG | 63 | 75.0% |
| NORMAL | 9 | 10.7% |
| WEAK | 7 | 8.3% |
| RISK_OFF | 5 | 6.0% |

- Inputs: SPY trend up 69 / mixed 6 / down 9 months; breadth high 66 / mid 12 / low 6. Median breadth 0.72 (min 0.19, max 0.94).

**By year:**

| Year | STRONG | NORMAL | WEAK | RISK_OFF |
|---|---|---|---|---|
| 2011 | 6 | 1 | 3 | 2 |
| 2012 | 10 | 2 | 0 | 0 |
| 2013 | 12 | 0 | 0 | 0 |
| 2014 | 11 | 1 | 0 | 0 |
| 2015 | 5 | 3 | 3 | 1 |
| 2016 | 7 | 2 | 1 | 2 |
| 2017 | 12 | 0 | 0 | 0 |

**Item 26 — duration:**

| Regime | Spells | Mean | Longest |
|---|---|---|---|
| STRONG | 5 | 12.6 months | 27 months (2012-06 → 2014-08) |
| NORMAL | 7 | 1.3 months | 2 months |
| WEAK | 5 | 1.4 months | 3 months (2011-10 → 2011-12) |
| RISK_OFF | 3 | 1.7 months | 2 months (2011-08/09; 2016-01/02) |

- 19 state changes in 7 years (2.7 a year), concentrated in 2011, 2015 and 2016.

**Item 27 — transition matrix** (from row to column, monthly):

| From \ to | STRONG | NORMAL | WEAK | RISK_OFF |
|---|---|---|---|---|
| STRONG | 58 | 4 | 0 | 0 |
| NORMAL | 4 | 2 | 2 | 1 |
| WEAK | 0 | 3 | 2 | 2 |
| RISK_OFF | 0 | 0 | 3 | 2 |

- STRONG never jumped directly to WEAK or RISK_OFF; it always passed through NORMAL first.

**Item 28 — independence of the score and ranking: confirmed.**
- The frozen `score_date(stocks, sector_context)` has no regime input.
- The regime is computed after scoring, from SPY and market breadth only.
- A test on the real review tables shows that changing the regime cap only shortens the same ordered buy list (cap 0 / 3 / 6 / 9 → the first 0 / 3 / 6 / 9 names of the uncapped list); it never re-orders or substitutes (`tests/test_p7_cp3_mechanics.py`).
- Exposure ceilings are **not** set here.

## 8. Capacity by portfolio size (items 29–33)

**Items 29–32 — share of the 84 monthly reviews** in which the eligible candidates at or above the entry threshold fill all slots, ≥ 80%, ≥ 50% or < 50% of K slots:

| Entry | Max 6: all / ≥80% / ≥50% / <50% | Max 8 | Max 10 | Max 12 |
|---|---|---|---|---|
| 90 | 0% / 0% / 4% / 96% | 0% / 0% / 2% / 98% | 0% / 0% / 0% / 100% | 0% / 0% / 0% / 100% |
| 85 | 7% / 13% / 23% / 77% | 2% / 5% / 14% / 86% | 0% / 2% / 13% / 87% | 0% / 0% / 7% / 93% |
| 80 | 46% / 54% / 76% / 24% | 30% / 38% / 68% / 32% | 21% / 30% / 54% / 46% | 14% / 21% / 46% / 54% |
| 75 | 96% / 98% / 99% / 1% | 93% / 95% / 99% / 1% | 76% / 93% / 98% / 2% | 64% / 76% / 96% / 4% |

**Item 33 — the 10% initial cap is a structural constraint:**

| Max positions | Position size at entry | Maximum initial gross exposure |
|---|---|---|
| 6 | 10% | **60%**: 40% is always cash at entry, even when all slots are full |
| 8 | 10% | **80%**: 20% is always cash |
| 10 | 10% | 100% |
| 12 | 10% cap → 8.33% each (100% / 12) | 100% |

- A 6- or 8-position book can never be fully invested under the current rules.
- Its cash comes on top of any empty slots shown above. For example, 80+ with Max 6 has 90% mean slot utilisation in the shadow book, which is about 54% of capital at entry.

**Strictness vs portfolio size** (share of reviews with all slots fillable / mean slot utilisation of the H2 Balanced shadow book / orders a year):

| Entry | Max 6 | Max 8 | Max 10 | Max 12 |
|---|---|---|---|---|
| 90 | 0% / 16% / 6 | 0% / 12% / 6 | 0% / 9% / 6 | 0% / 8% / 6 |
| 85 | 7% / 44% / 17 | 2% / 34% / 18 | 0% / 28% / 18 | 0% / 23% / 18 |
| 80 | 46% / 90% / 42 | 30% / 83% / 50 | 21% / 74% / 54 | 14% / 68% / 59 |
| 75 | 96% / 100% / 54 | 93% / 100% / 68 | 76% / 99% / 82 | 64% / 99% / 97 |

Reading the table:
- **90+:** never fills even 6 slots. Typically 0–2 names; a 90+ book is mostly cash.
- **85+:** fills 6 slots in 7% of months. Typical holdings are 2–4, i.e. 70–80% of a 10-slot book is empty.
- **80+:** 6 slots are normally close to full (90% utilisation). At 10 slots about a quarter stays empty on average, more in 2013–2014 (about 50–60% utilisation).
- **75+:** any size up to 12 is essentially full (≥ 99% utilisation).

## 9. Churn profiles (items 34–39)

**Shadow book: mechanics only.**
- Frozen `plan_review` at each monthly review; frozen `weekly_check` at each week-end.
- Ties broken by score, then ADV20, then id. Replacement requires candidate ≥ held + buffer.
- Disqualifier exits are independent; a freed slot may be refilled at the next monthly review.
- No time exit, no regime cap, no prices.
- Positions open at 2017-12-29 are censored and excluded from the holding statistics.
- Months = calendar days / 30.44.

### H1 — Tight (exit E − 5, buffer 3)

| Entry | Exit | Buffer | K | Entries/yr | Normal exits/yr | DQ exits/yr (of which weekly) | Universe exits/yr | Replacements/yr | Orders/yr | Sell/rebuy: total; per yr; % of sells | Holding median [p25–p75] (m) | Held ≥ 3 / 6 / 12 m | Longest (m) | Mean utilisation | Cost $100K (commission + slippage) | Cost $200K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 90 | 85 | 3 | 6 | 3.4 | 2.9 | 0.4 (0.3) | 0.0 | 0.0 | 6.7 | 3; 0.4; 13% | 1.0 [1.0–2.5] | 17% / 9% / 0% | 11.0 | 11% | 0.11% ($47 + $67) | 0.09% |
| 90 | 85 | 3 | 8 | 3.4 | 2.9 | 0.4 (0.3) | 0.0 | 0.0 | 6.7 | 3; 0.4; 13% | 1.0 [1.0–2.5] | 17% / 9% / 0% | 11.0 | 8% | 0.11% ($47 + $67) | 0.09% |
| 90 | 85 | 3 | 10 | 3.4 | 2.9 | 0.4 (0.3) | 0.0 | 0.0 | 6.7 | 3; 0.4; 13% | 1.0 [1.0–2.5] | 17% / 9% / 0% | 11.0 | 7% | 0.11% ($47 + $67) | 0.09% |
| 90 | 85 | 3 | 12 | 3.4 | 2.9 | 0.4 (0.3) | 0.0 | 0.0 | 6.7 | 3; 0.4; 13% | 1.0 [1.0–2.5] | 17% / 9% / 0% | 11.0 | 6% | 0.10% ($47 + $56) | 0.08% |
| 85 | 80 | 3 | 6 | 9.0 | 8.3 | 0.6 (0.3) | 0.0 | 0.4 | 18.7 | 6; 0.9; 9% | 1.1 [1.0–3.0] | 20% / 11% / 0% | 11.0 | 33% | 0.32% ($131 + $187) | 0.25% |
| 85 | 80 | 3 | 8 | 9.7 | 9.0 | 0.6 (0.3) | 0.0 | 0.0 | 19.3 | 6; 0.9; 9% | 1.1 [1.0–3.0] | 19% / 10% / 0% | 11.0 | 26% | 0.33% ($135 + $193) | 0.26% |
| 85 | 80 | 3 | 10 | 9.7 | 9.0 | 0.6 (0.3) | 0.0 | 0.0 | 19.3 | 6; 0.9; 9% | 1.1 [1.0–3.0] | 21% / 10% / 0% | 11.0 | 21% | 0.33% ($135 + $193) | 0.26% |
| 85 | 80 | 3 | 12 | 9.7 | 9.0 | 0.6 (0.3) | 0.0 | 0.0 | 19.3 | 6; 0.9; 9% | 1.1 [1.0–3.0] | 21% / 10% / 0% | 11.0 | 17% | 0.30% ($135 + $161) | 0.23% |
| 80 | 75 | 3 | 6 | 19.3 | 16.0 | 2.3 (1.1) | 0.1 | 5.1 | 48.0 | 29; 4.1; 18% | 1.8 [1.0–3.0] | 22% / 8% / 1% | 16.0 | 84% | 0.82% ($336 + $480) | 0.65% |
| 80 | 75 | 3 | 8 | 24.7 | 20.9 | 2.7 (1.4) | 0.1 | 3.9 | 56.1 | 35; 5.0; 18% | 1.9 [1.0–3.0] | 22% / 8% / 2% | 16.0 | 74% | 0.95% ($393 + $561) | 0.76% |
| 80 | 75 | 3 | 10 | 27.6 | 23.6 | 2.9 (1.4) | 0.1 | 3.4 | 61.0 | 38; 5.4; 18% | 1.9 [1.0–3.0] | 23% / 9% / 2% | 16.0 | 66% | 1.04% ($427 + $610) | 0.82% |
| 80 | 75 | 3 | 12 | 30.4 | 26.1 | 3.1 (1.7) | 0.1 | 2.7 | 65.3 | 42; 6.0; 19% | 1.9 [1.0–3.0] | 23% / 8% / 2% | 16.0 | 59% | 1.00% ($457 + $544) | 0.77% |
| 75 | 70 | 3 | 6 | 15.3 | 11.4 | 2.9 (1.6) | 0.1 | 16.6 | 62.9 | 44; 6.3; 20% | 1.1 [1.0–2.9] | 18% / 7% / 0% | 16.0 | 99% | 1.07% ($440 + $629) | 0.85% |
| 75 | 70 | 3 | 8 | 22.3 | 17.7 | 3.3 (1.9) | 0.1 | 18.3 | 80.0 | 59; 8.4; 21% | 1.9 [1.0–3.0] | 21% / 7% / 1% | 16.0 | 99% | 1.36% ($560 + $800) | 1.08% |
| 75 | 70 | 3 | 10 | 29.4 | 24.0 | 3.7 (1.9) | 0.3 | 19.4 | 96.3 | 79; 11.3; 24% | 1.9 [1.0–3.0] | 25% / 7% / 2% | 16.0 | 98% | 1.64% ($674 + $963) | 1.30% |
| 75 | 70 | 3 | 12 | 37.1 | 30.9 | 4.3 (2.3) | 0.3 | 19.1 | 110.9 | 97; 13.9; 25% | 1.9 [1.0–3.0] | 25% / 7% / 2% | 16.0 | 96% | 1.70% ($776 + $924) | 1.31% |

### H2 — Balanced (exit E − 10, buffer 5)

| Entry | Exit | Buffer | K | Entries/yr | Normal exits/yr | DQ exits/yr (of which weekly) | Universe exits/yr | Replacements/yr | Orders/yr | Sell/rebuy: total; per yr; % of sells | Holding median [p25–p75] (m) | Held ≥ 3 / 6 / 12 m | Longest (m) | Mean utilisation | Cost $100K (commission + slippage) | Cost $200K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 90 | 80 | 5 | 6 | 3.1 | 2.6 | 0.4 (0.3) | 0.0 | 0.0 | 6.1 | 1; 0.1; 5% | 1.9 [1.0–5.0] | 43% / 24% / 0% | 11.0 | 16% | 0.10% ($43 + $61) | 0.08% |
| 90 | 80 | 5 | 8 | 3.1 | 2.6 | 0.4 (0.3) | 0.0 | 0.0 | 6.1 | 1; 0.1; 5% | 1.9 [1.0–5.0] | 43% / 24% / 0% | 11.0 | 12% | 0.10% ($43 + $61) | 0.08% |
| 90 | 80 | 5 | 10 | 3.1 | 2.6 | 0.4 (0.3) | 0.0 | 0.0 | 6.1 | 1; 0.1; 5% | 1.9 [1.0–5.0] | 43% / 24% / 0% | 11.0 | 9% | 0.10% ($43 + $61) | 0.08% |
| 90 | 80 | 5 | 12 | 3.1 | 2.6 | 0.4 (0.3) | 0.0 | 0.0 | 6.1 | 1; 0.1; 5% | 1.9 [1.0–5.0] | 43% / 24% / 0% | 11.0 | 8% | 0.09% ($43 + $51) | 0.07% |
| 85 | 75 | 5 | 6 | 8.0 | 7.0 | 0.7 (0.4) | 0.0 | 0.4 | 16.6 | 1; 0.1; 2% | 2.0 [1.1–4.1] | 32% / 19% / 4% | 14.9 | 44% | 0.28% ($116 + $166) | 0.22% |
| 85 | 75 | 5 | 8 | 9.0 | 7.9 | 0.9 (0.6) | 0.0 | 0.0 | 17.7 | 1; 0.1; 2% | 2.0 [1.1–4.0] | 30% / 18% / 5% | 14.9 | 34% | 0.30% ($124 + $177) | 0.24% |
| 85 | 75 | 5 | 10 | 9.0 | 7.9 | 0.9 (0.6) | 0.0 | 0.0 | 17.7 | 1; 0.1; 2% | 2.0 [1.1–4.1] | 31% / 18% / 5% | 14.9 | 28% | 0.30% ($124 + $177) | 0.24% |
| 85 | 75 | 5 | 12 | 9.0 | 7.9 | 0.9 (0.6) | 0.0 | 0.0 | 17.7 | 1; 0.1; 2% | 2.0 [1.1–4.1] | 31% / 18% / 5% | 14.9 | 23% | 0.27% ($124 + $148) | 0.21% |
| 80 | 70 | 5 | 6 | 14.3 | 11.0 | 2.1 (1.0) | 0.3 | 7.3 | 42.3 | 19; 2.7; 13% | 2.0 [1.0–3.9] | 31% / 12% / 2% | 16.0 | 90% | 0.72% ($296 + $423) | 0.57% |
| 80 | 70 | 5 | 8 | 19.4 | 15.1 | 2.9 (1.6) | 0.3 | 6.3 | 50.3 | 27; 3.9; 16% | 2.0 [1.0–4.0] | 33% / 11% / 3% | 16.0 | 83% | 0.85% ($352 + $503) | 0.68% |
| 80 | 70 | 5 | 10 | 22.1 | 17.3 | 3.3 (1.7) | 0.3 | 5.7 | 54.4 | 27; 3.9; 15% | 2.0 [1.1–4.0] | 33% / 13% / 4% | 16.0 | 74% | 0.93% ($381 + $544) | 0.73% |
| 80 | 70 | 5 | 12 | 24.3 | 19.1 | 3.6 (2.0) | 0.3 | 5.7 | 58.7 | 31; 4.4; 15% | 2.0 [1.1–4.0] | 36% / 12% / 3% | 16.0 | 68% | 0.90% ($411 + $489) | 0.69% |
| 75 | 65 | 5 | 6 | 8.7 | 4.9 | 2.7 (1.4) | 0.3 | 18.6 | 53.7 | 30; 4.3; 16% | 2.0 [1.0–3.0] | 26% / 9% / 2% | 16.0 | 100% | 0.91% ($376 + $537) | 0.73% |
| 75 | 65 | 5 | 8 | 12.1 | 7.4 | 3.3 (1.9) | 0.3 | 22.3 | 67.7 | 39; 5.6; 17% | 2.0 [1.0–3.1] | 31% / 9% / 2% | 16.0 | 100% | 1.15% ($474 + $677) | 0.91% |
| 75 | 65 | 5 | 10 | 16.6 | 10.4 | 4.4 (2.4) | 0.3 | 25.1 | 82.0 | 55; 7.9; 20% | 2.0 [1.0–3.9] | 32% / 9% / 2% | 16.7 | 99% | 1.39% ($574 + $820) | 1.11% |
| 75 | 65 | 5 | 12 | 21.7 | 14.7 | 5.0 (2.9) | 0.3 | 27.9 | 97.4 | 67; 9.6; 20% | 2.0 [1.0–3.9] | 31% / 10% / 2% | 16.7 | 99% | 1.49% ($682 + $812) | 1.15% |

### H3 — Patient (exit E − 15, buffer 10)

| Entry | Exit | Buffer | K | Entries/yr | Normal exits/yr | DQ exits/yr (of which weekly) | Universe exits/yr | Replacements/yr | Orders/yr | Sell/rebuy: total; per yr; % of sells | Holding median [p25–p75] (m) | Held ≥ 3 / 6 / 12 m | Longest (m) | Mean utilisation | Cost $100K (commission + slippage) | Cost $200K |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 90 | 75 | 10 | 6 | 3.0 | 2.1 | 0.6 (0.4) | 0.0 | 0.0 | 5.7 | 0; 0.0; 0% | 3.0 [1.5–7.4] | 47% / 37% / 5% | 14.9 | 21% | 0.10% ($40 + $57) | 0.08% |
| 90 | 75 | 10 | 8 | 3.0 | 2.1 | 0.6 (0.4) | 0.0 | 0.0 | 5.7 | 0; 0.0; 0% | 3.0 [1.5–7.4] | 47% / 37% / 5% | 14.9 | 15% | 0.10% ($40 + $57) | 0.08% |
| 90 | 75 | 10 | 10 | 3.0 | 2.1 | 0.6 (0.4) | 0.0 | 0.0 | 5.7 | 0; 0.0; 0% | 3.0 [1.5–7.4] | 47% / 37% / 5% | 14.9 | 12% | 0.10% ($40 + $57) | 0.08% |
| 90 | 75 | 10 | 12 | 3.0 | 2.1 | 0.6 (0.4) | 0.0 | 0.0 | 5.7 | 0; 0.0; 0% | 3.0 [1.5–7.4] | 47% / 37% / 5% | 14.9 | 10% | 0.09% ($40 + $48) | 0.07% |
| 85 | 70 | 10 | 6 | 6.9 | 5.3 | 0.9 (0.6) | 0.1 | 1.0 | 15.1 | 1; 0.1; 2% | 2.9 [2.0–5.1] | 41% / 24% / 10% | 14.9 | 50% | 0.26% ($106 + $151) | 0.20% |
| 85 | 70 | 10 | 8 | 8.0 | 6.0 | 1.0 (0.6) | 0.1 | 0.7 | 16.6 | 1; 0.1; 2% | 3.0 [2.0–5.1] | 40% / 24% / 9% | 14.9 | 42% | 0.28% ($116 + $166) | 0.22% |
| 85 | 70 | 10 | 10 | 8.4 | 6.3 | 1.0 (0.6) | 0.1 | 0.1 | 16.1 | 0; 0.0; 0% | 3.0 [2.0–5.1] | 43% / 23% / 11% | 14.9 | 35% | 0.27% ($113 + $161) | 0.22% |
| 85 | 70 | 10 | 12 | 8.6 | 6.4 | 1.0 (0.6) | 0.1 | 0.0 | 16.1 | 0; 0.0; 0% | 3.0 [2.0–5.1] | 43% / 23% / 11% | 14.9 | 29% | 0.25% ($113 + $135) | 0.19% |
| 80 | 65 | 10 | 6 | 9.6 | 5.9 | 2.7 (1.6) | 0.1 | 7.0 | 32.3 | 9; 1.3; 8% | 3.0 [1.5–5.7] | 46% / 23% / 6% | 16.7 | 96% | 0.55% ($226 + $323) | 0.44% |
| 80 | 65 | 10 | 8 | 13.3 | 8.1 | 3.7 (2.4) | 0.3 | 8.1 | 41.7 | 13; 1.9; 9% | 3.0 [1.5–5.7] | 46% / 23% / 5% | 16.7 | 92% | 0.71% ($292 + $417) | 0.56% |
| 80 | 65 | 10 | 10 | 16.4 | 10.4 | 4.3 (2.9) | 0.3 | 7.0 | 45.4 | 13; 1.9; 8% | 3.0 [1.9–5.7] | 48% / 24% / 6% | 16.7 | 86% | 0.77% ($318 + $454) | 0.61% |
| 80 | 65 | 10 | 12 | 18.9 | 12.1 | 4.7 (3.0) | 0.3 | 6.4 | 48.9 | 13; 1.9; 8% | 3.0 [1.9–6.0] | 52% / 24% / 6% | 16.7 | 79% | 0.75% ($342 + $407) | 0.58% |
| 75 | 60 | 10 | 6 | 5.9 | 2.3 | 2.6 (1.6) | 0.1 | 13.1 | 37.1 | 13; 1.9; 10% | 2.0 [1.1–5.1] | 39% / 19% / 5% | 16.7 | 100% | 0.63% ($260 + $371) | 0.50% |
| 75 | 60 | 10 | 8 | 8.4 | 3.7 | 3.3 (2.0) | 0.3 | 16.6 | 48.9 | 17; 2.4; 10% | 2.1 [1.7–5.5] | 43% / 21% / 4% | 16.7 | 100% | 0.83% ($342 + $489) | 0.66% |
| 75 | 60 | 10 | 10 | 11.1 | 5.4 | 4.0 (2.6) | 0.3 | 18.1 | 57.1 | 19; 2.7; 10% | 3.0 [1.9–5.1] | 48% / 21% / 4% | 16.7 | 100% | 0.97% ($400 + $571) | 0.77% |
| 75 | 60 | 10 | 12 | 14.3 | 7.3 | 5.0 (3.1) | 0.3 | 20.7 | 68.3 | 24; 3.4; 10% | 3.0 [1.9–5.1] | 48% / 21% / 3% | 16.7 | 99% | 1.05% ($478 + $569) | 0.81% |

**Item 37 — sell-then-rebuy (whipsaw):** pre-registered before counting as re-bought at one of the 3 monthly reviews after the sale.
- **H1 Tight:** 18–25% of sells at entry 75–80.
- **H2 Balanced:** 13–20% of sells.
- **H3 Patient:** 8–10% of sells.
- At 85–90 there are only a handful of events in total.

**Item 38 — median implied holding:**

| Profile | Median holding |
|---|---|
| H1 | 1.0–1.9 months |
| H2 | 1.9–2.0 months |
| H3 | 2.0–3.0 months |

- H3 at entry 80–90 holds 46–48% of positions for 3+ months, 21–37% for 6+ months, and 5–11% for 12+ months.
- The longest holding is 16.7 months.

**Item 39 — orders a year:**
- **90+:** 6–7.
- **85+:** 15–19.
- **80+:** 32–65.
- **75+:** 37–111.
- Within an entry threshold, H3 < H2 < H1. Order counts rise with K while candidates are plentiful.

## 10. Mechanical costs (items 40–43)

**Notional:**
- Every order (buy or sell) is charged $7 plus 10 bps of a fixed notional: $100K × min(10%, 1 / K), i.e. $10,000 per order at K ≤ 10 and $8,333 at K = 12.
- The $200K sensitivity doubles the notional; the commission is unchanged.
- Annual cost = orders a year × cost per order ÷ capital. Commission and slippage are listed per configuration in the profile tables above.

**Cost classes** (annual mechanical cost as % of capital; configurations written as entry / profile / K):

| Capital | Class | Configurations | Entry / profile / K |
|---|---|---|---|
| $100K | < 0.5% | 24 | 90/H1/6, 90/H1/8, 90/H1/10, 90/H1/12, 90/H2/6, 90/H2/8, 90/H2/10, 90/H2/12, 90/H3/6, 90/H3/8, 90/H3/10, 90/H3/12, 85/H1/6, 85/H1/8, 85/H1/10, 85/H1/12, 85/H2/6, 85/H2/8, 85/H2/10, 85/H2/12, 85/H3/6, 85/H3/8, 85/H3/10, 85/H3/12 |
| $100K | 0.5–1.0% | 14 | 80/H1/6, 80/H1/8, 80/H2/6, 80/H2/8, 80/H2/10, 80/H2/12, 80/H3/6, 80/H3/8, 80/H3/10, 80/H3/12, 75/H2/6, 75/H3/6, 75/H3/8, 75/H3/10 |
| $100K | > 1.0% | 10 | 80/H1/10, 80/H1/12, 75/H1/6, 75/H1/8, 75/H1/10, 75/H1/12, 75/H2/8, 75/H2/10, 75/H2/12, 75/H3/12 |
| $200K | < 0.5% | 25 | 90/H1/6, 90/H1/8, 90/H1/10, 90/H1/12, 90/H2/6, 90/H2/8, 90/H2/10, 90/H2/12, 90/H3/6, 90/H3/8, 90/H3/10, 90/H3/12, 85/H1/6, 85/H1/8, 85/H1/10, 85/H1/12, 85/H2/6, 85/H2/8, 85/H2/10, 85/H2/12, 85/H3/6, 85/H3/8, 85/H3/10, 85/H3/12, 80/H3/6 |
| $200K | 0.5–1.0% | 18 | 80/H1/6, 80/H1/8, 80/H1/10, 80/H1/12, 80/H2/6, 80/H2/8, 80/H2/10, 80/H2/12, 80/H3/8, 80/H3/10, 80/H3/12, 75/H1/6, 75/H2/6, 75/H2/8, 75/H3/6, 75/H3/8, 75/H3/10, 75/H3/12 |
| $200K | > 1.0% | 5 | 75/H1/8, 75/H1/10, 75/H1/12, 75/H2/10, 75/H2/12 |

- **Example:** 80 / H2 / 10 = 54 orders a year → $381 commission + $544 slippage = **$925 = 0.93%** of $100K. At $200K it is 0.73%, because the commission is diluted.
- No configuration is chosen.

## 11. Weekly checks, share classes, relaxation and concentration (items 44–47)

**Item 44 — weekly hard-disqualifier activity:**

*Shadow books.* Weekly checks caused:
- 0.3–0.6 exits a year at 85–90;
- 1.0–3.1 exits a year at 75–80;
- that is **1.5–7.5% of all orders**.

The categories are mostly:
- **H5 stale price**, i.e. the stock stopped trading after a takeover or delisting. Names in the 80 / H2 / 10 book:
  - ARBA (SAP, 2012), LSI (2014), CYPR (2014), AGN (Actavis, 2015), SWI (2016), TWC (2016), N (NetSuite, 2016), LLTC (2017);
  - GPRO (2012), a re-used ticker id.
- **H6 broken trend** between reviews: FDS 2016-01, IDTI 2016-02.
- **H2:** FDS 2011-06, a filing gap.

Requalification:
- **80 / H2 / 10:** 9 of 23 disqualifier exits (weekly or monthly) requalified later as 80+ candidates, after a median of 6 reviews; 14 never did, mostly acquisitions.
- **75 profiles:** requalification after a median of 2–4 reviews.

*Universe-wide.* Among every stock that was ever an eligible 75+ candidate and was eligible at the latest review, the weekly checks registered per year:
- H6 onsets: 124–263;
- H2 onsets: 28–125 (the most in 2011);
- H5 onsets: 1–7;
- H7 onsets: 2–4.

Almost none of these were holdings, because candidates are in strong trends. **Weekly monitoring therefore adds little turnover. Its main function is to exit acquired or delisted stocks promptly.**

**Item 45 — one share class per company:**
- 11 companies had two eligible classes, giving 394 company-reviews, at least one in every review.
- Each time, exactly one class was kept: 394 of 394 follow the frozen rule (highest PIT ADV20, then the smallest id). Examples:

| Company | Kept |
|---|---|
| Berkshire | BRK.B |
| Discovery | DISCA |
| News Corp | NWSA |
| Liberty Media | the class with higher ADV, switching over time |
| Alphabet | GOOG / GOOGL, switching |
| Zillow | Z |
| HEICO | HEI |
| Under Armour | UA |
| Brown-Forman | BF.B |
| Liberty Broadband | LBRDK |

- One pairing (BYA / EQR under Equity Residential's CIK) joins a REIT with another security. Both are financial / REIT (H1), so it has no effect on any score.
- When the liquidity choice switches class while one class is held, the held class leaves the scorable set and is sold at the next monthly review. This happened 3 times across all 48 shadow books (75+ only). The owner may prefer a "keep the held class" rule (decision 11).

**Item 46 — relaxation ladder (design only; not activated):**

*Availability evidence.*
- At 85–90, a ladder would fill the book almost entirely from the lower rung. It would become a lower entry threshold under another name.
- At 80, the 2013–2014 shortfall (utilisation about 50–60% at K = 10) is the only period where a ladder would matter.
- At 75, no ladder is needed.

*Assessment.* **A ladder is not mechanically necessary.** Cash is an acceptable outcome: the owner's principle that quality comes before fullness is honoured by every threshold.

*If the owner wants one, the simplest architecture is:*
1. **Primary threshold E:** fill free slots, best first.
2. **One secondary rung, E − 5, only for slots still free:**
   - at most ⌊K / 2⌋ secondary positions at any time;
   - a secondary position is subject to the same exit and buffer rules as any other holding.
3. **Hard floor = E − 5**, never lower.
4. **Otherwise cash.**

No "keep relaxing until full" is possible by construction. Optionally, the secondary rung could apply only in STRONG / NORMAL regimes. Nothing was run with a ladder.

**Item 47 — concentration caps (candidates for owner decision; not optimised, not backtested):**

*Grown-winner cap* (10% stays the initial maximum and winners are not trimmed below the cap). Three options:

| Option | Rule |
|---|---|
| G0 | No hard cap |
| G1 | 15% of equity hard ceiling; trim back to 15% when exceeded at a monthly review |
| G2 | 20% of equity hard ceiling, same mechanics |

- *Risk-based rationale:* a 15% position is 1.5 initial slots and 20% is two. With median holdings of 2–3 months, drift above 15% requires a large relative move, so the cap should bind rarely.
- Only the owner's risk preference decides. No historical winner was examined.

*Sector concentration (item 24 found real clustering).* Three options:

| Option | Rule |
|---|---|
| S0 | None |
| S1 | At most 3 holdings per FF12 sector (2 if K = 6) |
| S2 | At most 40% of initial gross exposure per FF12 sector |

- A capped candidate is skipped and the next-ranked name is taken; free slots stay in cash if none qualifies.
- These are proposals only.

## Compact table 1 — availability and capacity

"Filled" = share of the 84 monthly reviews in which candidates fill **all** slots.

| Entry | Median candidates | Zero months | Median persistence | Max 6 filled | Max 8 filled | Max 10 filled | Max 12 filled |
|---|---|---|---|---|---|---|---|
| 90 | 0 | 54 / 84 (64%) | 1 month | 0% | 0% | 0% | 0% |
| 85 | 1 | 31 / 84 (37%) | 1 month | 7% | 2% | 0% | 0% |
| 80 | 5 | 2 / 84 (2%) | 1 month | 46% | 30% | 21% | 14% |
| 75 | 13.5 | 0 / 84 | 1 month | 96% | 93% | 76% | 64% |

**Note on persistence:** this is the median consecutive months at or above the entry level. Allowing the exit band (E − 5 / E − 10 / E − 15) raises it to 1–2 / 2–3 / 3–5 months (section 5).

## Compact table 2 — churn and cost (Max 10 positions, $100K; other sizes in section 9)

| Entry | Churn profile | Exit | Replacement buffer | Orders/yr | Median holding | Sell / rebuy (total, per yr) | Est. cost ($100K / $200K) |
|---|---|---|---|---|---|---|---|
| 90 | H1 Tight | 85 | 3 | 6.7 | 1.0 months | 3 (0.4/yr) | 0.11% ($114) / 0.09% |
| 90 | H2 Balanced | 80 | 5 | 6.1 | 1.9 months | 1 (0.1/yr) | 0.10% ($104) / 0.08% |
| 90 | H3 Patient | 75 | 10 | 5.7 | 3.0 months | 0 (0.0/yr) | 0.10% ($97) / 0.08% |
| 85 | H1 Tight | 80 | 3 | 19.3 | 1.1 months | 6 (0.9/yr) | 0.33% ($328) / 0.26% |
| 85 | H2 Balanced | 75 | 5 | 17.7 | 2.0 months | 1 (0.1/yr) | 0.30% ($301) / 0.24% |
| 85 | H3 Patient | 70 | 10 | 16.1 | 3.0 months | 0 (0.0/yr) | 0.27% ($274) / 0.22% |
| 80 | H1 Tight | 75 | 3 | 61.0 | 1.9 months | 38 (5.4/yr) | 1.04% ($1,037) / 0.82% |
| 80 | H2 Balanced | 70 | 5 | 54.4 | 2.0 months | 27 (3.9/yr) | 0.93% ($925) / 0.73% |
| 80 | H3 Patient | 65 | 10 | 45.4 | 3.0 months | 13 (1.9/yr) | 0.77% ($772) / 0.61% |
| 75 | H1 Tight | 70 | 3 | 96.3 | 1.9 months | 79 (11.3/yr) | 1.64% ($1,637) / 1.30% |
| 75 | H2 Balanced | 65 | 5 | 82.0 | 2.0 months | 55 (7.9/yr) | 1.39% ($1,394) / 1.11% |
| 75 | H3 Patient | 60 | 10 | 57.1 | 3.0 months | 19 (2.7/yr) | 0.97% ($971) / 0.77% |

## Strictness vs churn (the owner's key table; H2 Balanced, Max 10)

| Entry | Median candidates | Median run ≥ E (m) | Still ≥ E after 3 m | Entries/yr | Replacements/yr | Mean empty slots (of 10) | Orders/yr | Cost $100K |
|---|---|---|---|---|---|---|---|---|
| 90 | 0 | 1 | 12% | 3.1 | 0.0 | 9.1 | 6.1 | 0.10% |
| 85 | 1 | 1 | 16% | 9.0 | 0.0 | 7.2 | 17.7 | 0.30% |
| 80 | 5 | 1 | 20% | 22.1 | 5.7 | 2.6 | 54.4 | 0.93% |
| 75 | 13.5 | 1 | 25% | 16.6 | 25.1 | 0.1 | 82.0 | 1.39% |

Moving from 75 to 90:
- the candidate count falls about 30-fold;
- entries per year first rise (75 → 80, because at 75 the book is full and churns by *replacement*) and then fall;
- replacements disappear;
- empty slots rise from about 0 to about 9 of 10;
- costs fall from 1.39% to 0.10%.

Persistence barely changes: high scores are short-lived at every threshold.

## A–L — the owner's questions

**A. How rare are 75 / 80 / 85 / 90 in the real universe?**
- Among fully eligible stock-months:
  - 75+: 3.7% (about 15.6 stocks a month, out of about 425 eligible and about 1,115 in the universe);
  - 80+: 1.4% (about 6.1);
  - 85+: 0.38% (about 1.6);
  - 90+: 0.13% (about 0.5).
- No stock ever reached 95.

**B. Does 80+ / 85+ require strength across all three layers?**
- **Yes.** Every 80+ stock-month had Technical ≥ 23 / 40, Fundamental ≥ 25 / 45 and Sector ≥ 8.
- 98% were in a strong trend, and 83% were in the top momentum quintile.
- Technical and Fundamental are nearly uncorrelated (−0.04), so a high total cannot come from one layer. The maximum without Technical is 60; without Fundamental it is 55.

**C. How many stocks normally qualify?**
- Median per month: 90+: 0 (p90 2); 85+: 1 (p90 5); 80+: 5 (p10–p90 1–12); 75+: 13.5 (8–26).
- 2013 was the leanest year, and 2015 and 2017 the richest.

**D. How often would a strict portfolio be partially empty?**
- **90+:** always (in 96–100% of months it fills fewer than half of 6–12 slots).
- **85+:** fewer than half of 6 slots in 77% of months.
- **80+:** 6 slots fully fillable in 46% of months and 10 slots in 21%. The shadow book averages 2.6 empty slots out of 10 (5–6 in 2013).
- **75+:** essentially never partially empty up to 10 slots.

**E. How persistent are high scores?**
- **Not very.** The median spell above any threshold is 1 month.
- Survival to 3 months is 12–25%, and to 12 months 0–1%.
- About half of the re-entries happen within 3 months.
- The exit band helps: median 2–5 months above E − 10 / E − 15.
- The usual cause is the 7-point trend and sector steps and the volatility rank. The fundamentals are stable.

**F. Which hysteresis profile most reduces mechanical churn?**
- **H3 Patient reduces churn most** at every entry and size:
  - fewer orders (at 80 / 10: 45 vs 54 for H2 and 61 for H1);
  - half the whipsaw (8% vs 15% and 18% of sells);
  - the longest holdings (median 3.0 vs 2.0 vs 1.9 months);
  - the lowest cost (0.77% vs 0.93% vs 1.04%).
- **Its trade-off:** it keeps stocks whose score has fallen up to 15 points below entry (e.g. holding a 66 when the entry is 80), so the average held score is lower:
  - 80 / H3 / 10: median held score 80;
  - 80 / H2 / 10: 81;
  - 80 / H1 / 10: 82.
- Its buffer of 10 means a clearly better newcomer waits longer.
- **H1 Tight:** keeps the book closest to the current score ranking but trades the most.
- **Not chosen.**

**G. How do 6 / 8 / 10 / 12 positions differ?**
- **Fill rate:** smaller books fill far more often. At 80+: all slots 46% / 30% / 21% / 14%; H2 utilisation 90% / 83% / 74% / 68%.
- **Concentration:** each position is 10% for 6–10 and 8.3% for 12. Sector clustering is similar: the most-held sector is 40–50% of holdings.
- **Order burden:** at 80 / H2: 42 / 50 / 54 / 59 orders a year (85+ and 90+ are capacity-bound, so K hardly matters).
- **Structural cash:** at full slots, 6 → 40% and 8 → 20% cash under the 10% initial cap; 10 and 12 → 0%.

**H. Consequences of fewer than 10 positions under the 10% cap:**
- The book can never be fully invested at entry: 60% or 80% maximum.
- Its cash comes on top of empty slots: 80+ with K = 6 is about 54% invested on average.
- It does cost less in commissions and has fewer orders, and the slots are filled by the highest-ranked names only.
- Whether that is desirable is the owner's choice. This study cannot say whether it earns more.

**I. How often are the regimes active, and for how long?**
- STRONG 75% of months (spells of 3–27 months), NORMAL 11%, WEAK 8%, RISK_OFF 6%.
- Non-STRONG spells last 1–3 months. There are 2.7 changes a year, clustered in 2011, 2015 and 2016.
- STRONG always steps down through NORMAL.

**J. Is a relaxation ladder necessary?**
- **Mechanically, no.** Cash is a workable outcome at every threshold.
- A ladder would matter only for an 80+ book with 8–12 slots in lean years (2013–2014).
- At 85–90 a ladder would effectively become a lower threshold.
- If wanted: one secondary rung E − 5 for at most half the slots, hard floor E − 5, then cash (item 46).

**K. Do weekly hard-disqualifier checks meaningfully increase turnover?**
- **No.** They cause 0.3–3.1 exits a year (1.5–7.5% of orders).
- Most of these are stocks that stopped trading after an acquisition, which would otherwise wait up to a month.

**L. Which decisions must be frozen before any predictive test?** See section 12.

## 12. Decisions required from the owner (item 52; nothing is chosen here)

1. **Entry threshold:** 90 / 85 / 80 / 75. Trade-off: strictness vs empty slots (sections 4 and 8).
2. **Exit threshold:** E − 5 / E − 10 / E − 15, or another fixed gap.
3. **Replacement buffer:** 3 / 5 / 10, or another fixed value. Items 2–3 may be taken as one of the profiles H1 / H2 / H3.
4. **Maximum positions:** 6 / 8 / 10 / 12, and confirmation that sizing is min(10%, 1 / K) at entry, accepting 60% / 80% maximum initial exposure for 6 / 8.
5. **Regime exposure ceilings** for STRONG / NORMAL / WEAK / RISK_OFF, expressed as maximum positions. For reference: STRONG 75% of months, RISK_OFF 6%.
6. **Relaxation ladder:** none (cash), or the one-rung design in item 46 with its exact rung, cap and hard floor.
7. **Grown-winner hard cap:** G0 none, G1 15% or G2 20% (item 47).
8. **Sector concentration rule:** S0 none, S1 at most 3 per FF12, or S2 at most 40% per FF12 (item 47).
9. **Revenue-baseline ledger:**
   - (a) keep the implemented reading: the baseline is recorded only for stocks eligible 12 months earlier;
   - (b) record it for every company in the PIT store. This would change the score's eligible population (about 6–9% more non-financial rows), so it needs an explicit owner decision under the frozen-spec rule. It was **not** changed.
10. **Pre-registered mechanics conventions to confirm or replace:**
    - whipsaw = re-bought within 3 monthly reviews;
    - ties = score, ADV20, id;
    - weekly check = holdings only, with H4-frozen holdings skipping H3 / H4 / H6;
    - a disqualified slot is refilled only at the next monthly review.
11. **Share-class switching:** sell the held class when liquidity favours the other class (current behaviour, 3 events), or keep the held class while it stays eligible.
12. **Cost assumptions for the predictive test:** $7 per order + 10 bps; capital $100K (with $200K as sensitivity).

**Not authorised and not done:** future returns; IC; bucket returns; backtests; CAGR; SPY comparisons; tuning Score v1, its weights or disqualifiers; 2018–2021; the Holdout; purchases.

**STOP:** awaiting the owner's selection of the mechanics above. The first predictive test will be designed only after they are frozen.

## Files

| Path | Content |
|---|---|
| `strategies/X993_p7_score_mechanics_export/main.py` (v1.0), `src/qresearch/lean/qr_p7_export.py` | Non-trading export host and exact sliced technical computation |
| `experiments/E993-01/` | Run record (0 orders) |
| `research/phase7/P7_CP3_extract.py` → `P7_CP3_E993_stats.json`, `P7_CP3_E993_payload.json.gz` | Host checks and score tables (hash-verified) |
| `research/phase7/P7_CP3_mechanics.py` → `P7_CP3_mechanics.json`, `P7_CP3_tables.md` | All availability, capacity, churn and cost figures in this report |
| `docs/owner/2026-10-06_p7cp3_mechanics.md` | Owner record (D171) with the pre-registered conventions |
| `tests/test_p7_export.py`, `tests/test_p7_cp3_mechanics.py` | Slice exactness, mock-QuantConnect pipeline, runner / config rules, whipsaw, cost formula, weekly exits, regime independence, score-only outputs |

**Totals since the programme began** (from `experiments/INDEX.csv`, including E993-01):

| Measure | Count |
|---|---|
| Experiments logged | 494 (research 279, infrastructure 156, benchmark 42, sizing 14, demo 3) |
| Hypotheses with runs | 19 |
| Strategy / host ids | 64 |

- P7-CP3 added one infrastructure run (E993-01) and no hypothesis.
- The registry row of E993-01 shows the runner's standard columns for an untouched cash account (trades 0, CAGR 0, Sharpe blank, drawdown 0). They describe no strategy and were not used.
