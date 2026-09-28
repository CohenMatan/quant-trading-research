# Size proxy evaluation — pre-registered plan (CP2 addendum)

Written **before** any proxy result was computed (2026-09-27). The design and the decision thresholds below are fixed. The results report must not change them after the fact; any deviation is documented as such.

## Goal

A universe rule that uses **only historical price and volume**, so it is survivorship-free back to 1999. It must approximate the approved universe: US common stock with point-in-time MarketCap ≥ $2B that passes the tradability filters.

## Reference universe (the "truth")

The harness's eligible set on QuantConnect's new Morningstar dataset (LEAN 18131):

- common stock, primary share, not a depositary receipt, NYSE/Nasdaq/AMEX;
- MarketCap ≥ $2B;
- raw price ≥ $5;
- 20-day average dollar volume ≥ $5M.

It is evaluated on the first trading day of each month.

## Evaluation windows

| Window | Role |
|---|---|
| 2010–2014 | **Primary comparison**, where MarketCap is reliable. All judgements are made here. |
| 2015–2021 | **Out-of-period stability check.** Membership agreement only; no forward returns are computed (validation years), and nothing is tuned on it. |
| 1999–2009 | **Old dataset** (LEAN 18130, retired by QuantConnect on 2026-10-31, so this is a one-time measurement). Its MarketCap covers survivors only. Used for (a) recall against surviving large companies and (b) evidence that the proxy includes later-failed companies. Precision is not meaningful there. |

## Candidate pool (price and volume only)

Every security in QuantConnect's daily coarse universe with:

- raw prior-close price ≥ $5;
- 20-day average dollar volume ≥ $5M;
- at least 63 days of history.

Exclusion variants:

- **E0:** no type filter.
- **E1** (base): drop securities whose fundamentals exist *and* say they are not a primary common share or are a depositary receipt. Missing fundamentals means the security is kept, so dead companies are not dropped.
- **E2:** E1, plus drop securities whose fundamentals exist *and* show a non-major exchange.
- **E4:** E1, plus a price-only ETF detector: drop if the 63-day correlation of daily returns with SPY is ≥ 0.90.
- **E3:** require fundamentals. Diagnostic only; not survivorship-safe before 2010.

## Size rules (all on 63-day average dollar volume, ADV63)

| Family | Values | Idea |
|---|---|---|
| A. Top-N by ADV63 | N = 500, 750, **1000**, 1250, 1500 | fixed-size liquid universe |
| B. Dollar-volume coverage | the most liquid names that together make up c = 80, 85, **90**, 95% of pool ADV63 | adapts to concentration and market-wide volume |
| C. Absolute ADV63 floor | $5M (pool only), $10M, **$20M**, $40M | simplest; drifts with market-wide volume |

The **primary variants** are chosen a priori, as the middle of each grid: A-1000, B-90 and C-20M. They get the full characterisation, plus the E0, E2 and E4 exclusion variants.

## Metrics

- Per month: TP, FP, FN, precision, recall, F1 and Jaccard. These are pooled over months into yearly figures, micro-averaged.
- Characterisation (2010–2014), for the primary variants:
  - false positives by type: no fundamentals (ETF/ADR/other or dead), non-common, other exchange, MarketCap < $2B with its size bucket, MarketCap missing;
  - false negatives by MarketCap bucket;
  - turnover (ADV/MarketCap) and volatility of true positives, false negatives and false positives;
  - sector mix of the reference vs the proxy;
  - exchange mix;
  - the most-traded false positives without fundamentals.
- Different-bias test:
  - equal-weight forward 1-month return of the reference, the proxy, the proxy-only names and the reference-only names;
  - computed for 2010–2014 and for 1999–2009 on the old data;
  - never for 2015 or later.
- Survivorship evidence: were companies known to have failed or been acquired (Enron, WorldCom, Lehman, …) inside the proxy while they were large?

## Decision thresholds (fixed in advance)

| Verdict | Condition on the chosen primary variant |
|---|---|
| **APPROVE** | 2010–14 F1 ≥ 0.85; every year's F1 ≥ 0.80; 2015–21 F1 within 0.05 of 2010–14; neighbouring thresholds within 0.05 F1 (a plateau); forward-return gap between the proxy and the reference ≤ 2%/year in 2010–14; the proxy captures the known failed companies |
| **APPROVE WITH LIMITATIONS** | F1 0.70–0.85, or one of the other conditions fails in a way that can be measured and described |
| **REJECT** | F1 < 0.70, instability across years or thresholds, or a large unexplained bias |

The primary variant used for the verdict is the one of A-1000, B-90 and C-20M with the best **2010–14** F1. That is the only selection step. It is made among three a-priori variants, not by tuning a threshold.

## Deviations recorded before the official runs (2026-09-27, after a 3-month scratch test of 2010)

1. **Added exclusion E5, an "ETF twin detector".**
   - The scratch test showed that about 80% of false positives were securities without fundamentals, led by ETFs.
   - The pre-registered SPY-correlation detector (E4) removed few of them.
   - E5 drops a security without fundamentals if its 63-day daily returns have |correlation| ≥ 0.95 with any other pool member. Index, leveraged, inverse and commodity ETFs have near-duplicates; companies rarely do.
   - 0.90 and 0.98 are also reported for stability. The primary variants are evaluated under E5_95 as well as E1.
2. **The reference is itself survivorship-biased in 2010–14.**
   - A probe showed that large companies whose securities later ended (Alcoa pre-2016, DuPont, Time Warner, Chesapeake, JCPenney, BB&T, SanDisk, Genzyme, …) have *no* fundamentals in 2010, in both datasets.
   - Proxy "false positives" therefore include genuine ≥ $2B companies.
   - Added: every June, a deterministic sample of up to 60 false positives without fundamentals is logged with ADV, twin correlation and SPY correlation.
   - The sample is classified by type in the report (ETF/ETN, ADR/foreign, US common stock, other). The classification is evaluation-only and is never used by any rule.
3. **Consequence for the decision thresholds.** F1 against the as-is reference is a *lower bound* on true agreement. The report shows it next to the known-type agreement (E3) and the sample-based estimate. The verdict states which figure it relies on and why.
