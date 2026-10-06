# P7-CP3R — Revenue-Baseline Correction and Final Mechanics Confirmation

- **Status:** checkpoint report, 2026-10-06. Owner decision D173; this report is D174.
- **Scope:** mechanics and data only. No future, strategy or SPY return was computed. No IC, CAGR, Sharpe, drawdown, win rate or alpha. No backtest.
- **Data:**
  - QuantConnect export E993-02 (X993 v1.1, non-trading, 0 orders) against P7-CP3's E993-01.
  - Offline scripts:
    - `research/phase7/P7_CP3_mechanics.py` (the same metrics as CP3, plus the provisional planner);
    - `P7_CP3R_compare.py` (CP3 vs CP3R);
    - `P7_CP3R_sec_check.py` (independent SEC check of the rescued sample).

## Conclusion

**MECHANICS CONFIRMED — READY TO FREEZE FOR PREDICTIVE TEST DESIGN**

The correction changes the numbers moderately and in the expected direction. It does not change the operational picture:

| Measure | CP3 | CP3R | Change |
|---|---|---|---|
| Fully scorable stocks per month | 425 | 480 | +13% |
| 80+ candidates per month: mean | 6.1 | 7.0 | +16% |
| 80+ candidates per month: median | 5 | 6.5 | |
| 80+ share of eligible stock-months | 1.43% | 1.47% | still rare |
| 80+ zero-candidate months | 2 | 2 | |
| Median spell above 80 | 1 month | 1 month | |
| 80+ spells surviving 3 months | 19.8% | 20.5% | |
| Median total score | 48 | 48 | |

- Layer correlations are within ±0.03, and 80+ still needs strength in all three layers.
- Sector concentration is not worse (median largest share 0.50 → 0.43).
- Market regime: **identical** in all 84 months.

**Under the owner's provisional mechanics** (80 / 70 / 5, K = 10, regime limits, at most 3 per sector):

| Measure | CP3 | CP3R |
|---|---|---|
| Orders a year | 43.1 | 47.1 (+9%) |
| Mechanical cost ($100K) | 0.73% a year | 0.80% a year |
| Mean capital utilisation | 63% | 69% |
| Median holding | 2.0 months | 2.0 months |

None of the owner's stop conditions occurred:
- 80+ did not become common;
- churn did not jump;
- concentration did not jump;
- costs did not jump;
- the score distribution did not shift.

**Two facts the owner should still see before freezing:**
1. Under the **frozen P7-CP2 planner** (no sector cap, old tie-break), 80 / H2 / 10 rises from 0.93% to 1.02% a year. That crosses the 1% line by 0.02 points; two other grid points also cross it (section 6).
2. About 17% of the rescued baselines cannot be checked for a change of SEC registrant, because no registrant is on record at one of the two dates (item 6).

Nothing is tuned and nothing in Score v1 changed.

## 1. The change (items 1–3)

**Item 1 — exact revenue-baseline change:**

| | Rule |
|---|---|
| Before (CP3, D171 reading) | The revenue True TTM recorded at the month-end review 12 months earlier, **only for securities in the eligible universe at that review** |
| After (CP3R, D173) | The **company's** revenue True TTM recorded live at the month-end review session 12 calendar months earlier (same calendar month, prior year), **for every company in the PIT fundamental store**, eligible or not |

The lookup rule:
1. At every month-end review session t (from 2010-01), the host asks the frozen PIT store for each company's revenue True TTM on the universe-selection day reflecting t, and records the value with its four quarter period-ends and filing dates (`qr_p7_export.RevenueLedger`).
2. The baseline for a review in month M of year Y is the value recorded at the review of month M, year Y − 1.
3. **If no value was recorded then** (fewer than four visible consecutive quarters, failed fiscal-year reconciliation, or older than 200 days), the stock is **H2**. No other date is searched, nothing is interpolated, and no later filing is used.
4. **Valid only if:**
   - (a) the security's current price life started on or before that baseline review session (security-life rule D167: no gap of more than 60 missing sessions in between);
   - (b) the SEC registrant CIK of the security's filings (PIT SIC table) did not change between the two dates, where it is known at both;
   - (c) every component quarter was usable (filing date + 1) on or before the baseline selection day. This is checked in-host for every rescued row.
5. **Weekly checks** use the baseline of the score in force (the latest monthly review), validated the same way.
6. **SEC-repaired securities** are now fed into the store on every day a further filing of theirs becomes usable, not only while eligible. This is idempotent: the same filings with the same availability dates.

**Everything else is unchanged:** Score v1 (40 / 45 / 15), features, bands, weights, lookbacks, the sector and volatility definitions, and every other H2 condition. The score code `qr_p7_score.py` is byte-identical to the P7-CP2 pin; QuantConnect again stored it with one appended newline.

**Item 2 — why this is methodologically correct.**
- Revenue growth describes the company: did revenue grow over the year?
- Whether the company happened to be inside our ≥ $2B universe a year ago says nothing about that.
- Tying the baseline to past eligibility excluded every company that grew into the universe for its first 12 months there. That is a survivorship-style artefact of the strategy's own filter, not a data-quality rule.
- The corrected rule asks only whether trustworthy PIT revenue existed a year earlier.

**Item 3 — no future information is introduced:**
- Every baseline value was recorded live at the earlier review by the same frozen PIT store, which applies availability (filing + 1, estimated dates + 90), quarantine, restatement blocks, SEC timing holds and freshness.
- The value is never recomputed later, so a later restatement or filing cannot reach it (test A shows a recomputation after a restatement would differ; the ledger does not).
- In-host: **0 of 6,287 rescued baselines** had any component quarter filed on or after its baseline selection day, or a period end after the baseline session.

## 2. Point-in-time tests (items 4–6)

`tests/test_p7_cp3r.py` and `tests/test_p7_export.py` all pass.

| Test | Result |
|---|---|
| **A. Future-filing invariance** | A restatement of an old quarter filed after review t does not change the baseline recorded at t; the review 12 months later uses exactly that recorded value. A recomputation from the same store after the restatement would give a different value, which is why the ledger is recorded live |
| **B. Truncation** | A store fed only up to t gives exactly the same baseline (value, quarters, filing dates) as the full stream; all quarters were filed before the selection day |
| **C. Eligibility independence** | The ledger records every store company. On the mock QuantConnect host, a company outside the universe in 2010 (market cap < $2B) gets exactly the same 2011 score as when it was eligible in 2010 (only the audit bits differ) |
| **D. Same-company continuity** | The baseline is rejected if the price life began after the baseline review (re-used ids, e.g. GDI / GPRO, D167) or the SEC CIK changed (where known at both dates). Mock host: a 100-session gap makes the next 12 months' baselines H2 |
| **E. Determinism** | Two runs give identical ledgers and a byte-identical payload |

**Item 6 — the real data:**
- 5 baselines were rejected by the security-life rule and 11 by a registrant change.
- **Limitation (disclosed):** of the 6,282 rescued kept-class rows,
  - 5,197 have the same CIK at both dates;
  - 756 have no CIK on record at the baseline date;
  - 329 have no CIK now.
  The registrant check cannot judge those 1,085 rows (17%); the security-life rule still applies to them.
- In the SEC sample, the one such case was Zillow Group (Z, CIK 1617640). Its 2014 quarters were filed by the predecessor Zillow, Inc. (CIK 1334814) on exactly the vendor's dates. That is a legitimate holding-company succession, not a mistake.
- **Owner option (decision 3):** require a known and identical CIK at both dates. This would keep up to 1,085 more rows in H2.

## 3. Rescued rows (items 7–10)

**Item 7:** **6,282** stock-months (kept class; 6,287 including 5 non-chosen classes) became free of H2 only because of the correction. That is **8.9%** of the 70,804 non-financial stock-months.
- 4,638 of them are now fully eligible (no other hard disqualifier).
- 399 reach 75+, **173 reach 80+**, 32 reach 85+ and 12 reach 90+.
- **No row lost its baseline:** every row valid under the CP3 rule is also valid under the new rule.

**Item 8 — by year:**

| Year | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|
| Rescued stock-months | 1,012 | 603 | 978 | 961 | 747 | 775 | 1,206 |
| Share of non-financial rows | 12.2% | 7.0% | 9.9% | 8.7% | 6.8% | 7.3% | 10.6% |
| Of which now fully eligible | 646 | 424 | 824 | 721 | 579 | 536 | 908 |
| Of which 80+ | 25 | 34 | 10 | 19 | 25 | 19 | 41 |

**Item 9 — why they were outside the old ledger** (the reason the company was not eligible at the review 12 months earlier, recorded live):

| Reason | Stock-months | Share |
|---|---|---|
| **Market cap below $2B** | 6,034 | 96.1% |
| ADV20 below $5M or fewer than 20 days of ADV history | 186 | 3.0% |
| Price below $5 | 51 | 0.8% |
| Not US common stock / exchange | 11 | 0.2% |
| Not in QuantConnect's universe list then | 0 | 0% |

- 27 rescued rows were companies first seen less than a year before the baseline date (recent listings with four quarters of filings).
- The rescued population is overwhelmingly **companies that grew into the $2B universe**, exactly the case the owner described.

**Item 10 — independent verification sample** (40 rescued baselines, chosen deterministically by salted hash before any result was seen; 160 quarters):
- Every quarter's 10-Q / 10-K was found on SEC EDGAR, under the security's registrant or its predecessor (Zillow, above).
- **Every one of the 160 was filed with the SEC before the baseline selection day: 0 violations.** The revenue really was public when the baseline was recorded.
- In 1 quarter (NPS Pharmaceuticals, Q4 2012), the vendor file date (2013-02-14) is 7 days before the 10-K (2013-02-21). That is consistent with the earnings-release date, the same vendor pattern P7-CP1 found once. The baseline was recorded on 2013-06-01, long after both dates, so the baseline is unaffected.
- Values were not re-derived from SEC data; dates only. Vendor values were verified generally in P2-CP6 / CP7, and SEC-repaired securities' values come from the SEC itself.

## 4. Funnel and availability (items 11–18)

**Items 11–12 — H2:**
- Kept-class stock-months with H2: **39,043 → 32,761** (−16%).
- Non-financial H2 rows: 23,070 → 17,778, i.e. 32.6% → 25.1% of non-financial rows.
- **Consistency check:** E993-02 also evaluated the old rule. It reproduces E993-01's H2 flag on **every** kept-class row (0 mismatches). The eligible universe and the share-class choices are identical in all 84 reviews (0 differences). The change is therefore exactly isolated.

**Item 13 — funnel** (mean stocks per monthly review remaining after each step):

| Stage | CP3 | CP3R | Abs. diff | % diff |
|---|---|---|---|---|
| Base universe | 1,115.3 | 1,115.3 | 0 | 0% |
| After duplicate share classes | 1,110.6 | 1,110.6 | 0 | 0% |
| After Financial / REIT exclusion | 882.8 | 882.8 | 0 | 0% |
| After price-history exclusion (H3) | 861.2 | 861.2 | 0 | 0% |
| **After H2 fundamental exclusion** | **583.3** | **650.2** | **+66.9** | **+11.5%** |
| After sector exclusion (no SIC) | 568.3 | 631.3 | +63.0 | +11.1% |
| After corporate-event exclusion (H4) | 564.5 | 627.1 | +62.6 | +11.1% |
| After stale price (H5) | 564.5 | 627.1 | +62.6 | +11.1% |
| After broken-trend exclusion (H6) | 442.4 | 502.6 | +60.2 | +13.6% |
| After impairment exclusion (H7) | 425.2 | 480.4 | +55.2 | +13.0% |
| **Fully scorable** | **425.2** | **480.4** | **+55.2** | **+13.0%** |
| 75+ | 15.6 | 18.4 | +2.8 | +17.9% |
| 80+ | 6.1 | 7.0 | +0.9 | +14.8% |
| 85+ | 1.6 | 1.6 | 0.0 | 0% |
| 90+ | 0.5 | 0.5 | 0.0 | 0% |

- H7 (impairment) rises slightly, from 2.1% to 2.6% of rows. Some rescued companies are loss-making with negative operating cash flow, which H7 now sees because their fundamentals are complete.

**Item 14 — scorable change:** +55 stocks per review (+13%). By year:

| Year | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|
| CP3 | 287 | 356 | 462 | 505 | 423 | 442 | 501 |
| CP3R | 341 | 391 | 531 | 565 | 472 | 486 | 577 |

**Items 15–18 — candidates per monthly review:**

| Entry | | Mean | Median | Min | Max | p10 | p25 | p75 | p90 | Zero months |
|---|---|---|---|---|---|---|---|---|---|---|
| 75 | CP3 | 15.6 | 13.5 | 2 | 36 | 8 | 10 | 21 | 26 | 0 |
| | CP3R | 18.4 | 18 | 3 | 37 | 9 | 11 | 24 | 30 | 0 |
| **80** | CP3 | 6.1 | 5 | 0 | 18 | 1 | 3 | 9 | 12 | 2 |
| | **CP3R** | **7.0** | **6.5** | 0 | 21 | 2 | 3 | 9 | 13 | **2** |
| 85 | CP3 | 1.6 | 1 | 0 | 8 | 0 | 0 | 2 | 5 | 31 |
| | CP3R | 1.6 | 1 | 0 | 11 | 0 | 0 | 2 | 5 | 34 |
| 90 | CP3 | 0.55 | 0 | 0 | 4 | 0 | 0 | 1 | 2 | 54 |
| | CP3R | 0.50 | 0 | 0 | 4 | 0 | 0 | 1 | 1.7 | 56 |

**Yearly mean, CP3 → CP3R:**

| Entry | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|
| 75 | 13.0 → 16.5 | 14.5 → 17.6 | 9.3 → 11.4 | 14.3 → 15.9 | 20.4 → 22.9 | 15.2 → 18.6 | 22.9 → 25.8 |
| 80 | 5.6 → 6.4 | 4.8 → 7.1 | 2.8 → 3.1 | 5.5 → 6.3 | 7.2 → 8.4 | 6.2 → 6.6 | 10.5 → 11.4 |

- **Zero-candidate months at 80:** 2 in both (2013 and 2015 in CP3; 2013 and 2014 in CP3R).
- **85 and 90 are essentially unchanged:** rescued stocks enter, and slightly more stocks share the top quintiles, so a few former 85 / 90 scores step down.

## 5. Score distribution, correlations, composition (items 19–21)

**Item 19 — distribution:**

| Population | Stock-months | Median | ≥ 75 | ≥ 80 | ≥ 85 | ≥ 90 |
|---|---|---|---|---|---|---|
| All data-scorable, CP3 | 47,417 | 43 | 2.83% | 1.08% | 0.29% | 0.10% |
| All data-scorable, CP3R | 52,676 | 44 | 3.01% | 1.14% | 0.26% | 0.08% |
| Eligible, CP3 | 35,713 | 48 | 3.68% | 1.43% | 0.38% | 0.13% |
| Eligible, CP3R | 40,351 | 48 | 3.83% | 1.47% | 0.33% | 0.10% |

The maximum score is 94 in both. **No distribution shift:** 80+ stays a 1-in-70 event.

**Item 20 — layer correlations** (pooled Pearson, CP3 → CP3R):

| Pair | CP3 | CP3R |
|---|---|---|
| Technical vs Fundamental | −0.04 | −0.02 |
| Technical vs Sector | 0.22 | 0.22 |
| Fundamental vs Sector | −0.02 | −0.02 |
| Total vs Technical | 0.76 | 0.76 |
| Total vs Fundamental | 0.57 | 0.59 |
| Total vs Sector | 0.41 | 0.40 |

Layer means: Technical 17.6 → 17.9; Fundamental 18.0 → 18.0; Sector 7.6 → 7.7.

**Item 21 — composition of high scores:**

| | 80+ CP3 | 80+ CP3R | 85+ CP3 | 85+ CP3R |
|---|---|---|---|---|
| Stock-months / distinct stocks | 510 / 148 | 592 / 167 | 136 / 50 | 135 / 51 |
| Mean Technical / Fundamental / Sector | 34.3 / 36.9 / 12.0 | 33.3 / 37.8 / 11.8 | 35.7 / 39.2 / 13.0 | 34.5 / 39.8 / 13.5 |
| Any weak layer | 0% | 0% | 0% | 0% |
| Strong trend | 98% | 97% | 99% | 99% |
| Supportive sector | 57% | 54% | 72% | 79% |
| Top sectors | Tech 29%, Other 15%, Health 15%, Utilities 13% | Tech 30%, Health 17%, Other 17%, Shops 9%, Utilities 9% | Tech 30%, Health 23%, Utilities 13% | Health 32%, Tech 30%, Shops 11% |

80+ still requires broad strength. The sector mix moves slightly from utilities towards health care and "other", the growth companies that entered the universe.

## 6. Persistence, churn, orders and costs (items 22–28)

**Item 22 — persistence:**

| Entry | Median spell | Survive 3 m | Survive 6 m | Re-entries a year | Median months ≥ exit E−10 |
|---|---|---|---|---|---|
| 75 | 1 → 1 | 24.7% → 25.0% | 7.4% → 6.2% | 50.7 → 60.0 | 3 → 3 |
| 80 | 1 → 1 | 19.8% → 20.5% | 5.0% → 3.5% | 17.0 → 20.6 | 3 → 3 |
| 85 | 1 → 1 | 15.8% → 19.4% | 4.3% → 4.4% | 3.7 → 3.1 | 2 → 3 |
| 90 | 1 → 1 | 11.5% → 18.2% | 8.7% → 5.0% | 1.1 → 0.7 | 2 → 3 |

Persistence is unchanged: high scores remain short-lived.

**Items 23–26 — churn, frozen P7-CP2 planner, K = 10, CP3 → CP3R:**

| Entry / profile | Orders a year | Entries a year | Normal exits | DQ exits | Replacements | Sell / rebuy | Median holding | Utilisation | Cost $100K |
|---|---|---|---|---|---|---|---|---|---|
| 90 / H1 | 6.7 → 6.4 | 3.4 → 3.3 | 2.9 → 3.1 | 0.4 → 0.0 | 0 → 0 | 3 → 3 | 1.0 → 1.1 | 7% → 6% | 0.11% → 0.11% |
| 90 / H2 | 6.1 → 5.6 | 3.1 → 2.9 | 2.6 → 2.6 | 0.4 → 0.1 | 0 → 0 | 1 → 1 | 1.9 → 3.0 | 9% → 9% | 0.10% → 0.09% |
| 90 / H3 | 5.7 → 5.6 | 3.0 → 2.9 | 2.1 → 2.6 | 0.6 → 0.1 | 0 → 0 | 0 → 1 | 3.0 → 3.1 | 12% → 11% | 0.10% → 0.09% |
| 85 / H1 | 19.3 → 18.0 | 9.7 → 9.1 | 9.0 → 8.3 | 0.6 → 0.4 | 0 → 0 | 6 → 3 | 1.1 → 2.0 | 21% → 21% | 0.33% → 0.31% |
| 85 / H2 | 17.7 → 17.0 | 9.0 → 8.6 | 7.9 → 7.4 | 0.9 → 0.6 | 0 → 0.1 | 1 → 3 | 2.0 → 2.1 | 28% → 28% | 0.30% → 0.29% |
| 85 / H3 | 16.1 → 16.0 | 8.4 → 7.7 | 6.3 → 5.7 | 1.0 → 0.7 | 0.1 → 0.7 | 0 → 1 | 3.0 → 3.0 | 35% → 33% | 0.27% → 0.27% |
| 80 / H1 | 61.0 → 69.0 | 27.6 → 29.4 | 23.6 → 25.6 | 2.9 → 0.9 | 3.4 → 5.7 | 38 → 49 | 1.9 → 2.0 | 66% → 72% | 1.04% → 1.17% |
| **80 / H2** | **54.4 → 60.3** | 22.1 → 22.4 | 17.3 → 17.6 | 3.3 → 1.4 | 5.7 → 8.4 | 27 → 30 | 2.0 → 2.0 | 74% → 80% | **0.93% → 1.02%** |
| 80 / H3 | 45.4 → 49.4 | 16.4 → 15.7 | 10.4 → 10.1 | 4.3 → 2.3 | 7.0 → 9.7 | 13 → 16 | 3.0 → 3.0 | 86% → 89% | 0.77% → 0.84% |
| 75 / H1 | 96.3 → 99.7 | 29.4 → 26.9 | 24.0 → 21.1 | 3.7 → 2.1 | 19.4 → 23.7 | 79 → 82 | 1.9 → 1.9 | 98% → 99% | 1.64% → 1.70% |
| 75 / H2 | 82.0 → 87.7 | 16.6 → 14.9 | 10.4 → 9.0 | 4.4 → 2.1 | 25.1 → 29.7 | 55 → 60 | 2.0 → 2.0 | 99% → 100% | 1.39% → 1.49% |
| 75 / H3 | 57.1 → 60.0 | 11.1 → 11.4 | 5.4 → 5.3 | 4.0 → 2.3 | 18.1 → 19.3 | 19 → 23 | 3.0 → 3.0 | 100% → 100% | 0.97% → 1.02% |

The full grid at K = 6 / 8 / 10 / 12 is in `research/phase7/P7_CP3R_compare.json`. Across all 48 configurations, **orders change by −10% to +13%** (80: +4% to +13%) and the cost by −0.03 to +0.14 percentage points.

**Why the changes:**
- **Fewer disqualifier exits:** held stocks no longer lose their baseline.
- **More replacements and more universe exits** (80 / H2 / 10: 0.3 → 2.0 a year): newly scorable companies near the $2B line also drop back below it more often.

**Items 27–28 — costs:**
- Three configurations move from the 0.5–1.0% class to > 1.0%, all by at most 0.04 points:

| Configuration | CP3 | CP3R |
|---|---|---|
| 80 / H1 / 8 | 0.95% | 1.05% |
| 80 / H2 / 10 | 0.93% | 1.02% |
| 75 / H3 / 10 | 0.97% | 1.02% |

- The $200K sensitivity for 80 / H2 / 10 is 0.73% → 0.81%.

## 7. Sector, capacity, regime (items 29–31)

**Item 29 — sector concentration** (reviews with at least 5 candidates):
- **80+:** median largest-sector share 50% → 43%; reviews where one sector exceeds 50%: 18 of 45 → 20 of 59 (more reviews qualify).
- **75+:** 38% → 40%.
- **85+:** unchanged.

**Item 30 — capacity** (share of reviews where all slots are fillable; mean fill in parentheses):

| Entry | Max 6 | Max 8 | Max 10 | Max 12 |
|---|---|---|---|---|
| 80 | 46% → 56% (71% → 79%) | 30% → 42% (62% → 71%) | 21% → 24% (55% → 62%) | 14% → 15% (48% → 55%) |
| 75 | 96% → 99% | 93% → 92% | 76% → 88% | 64% → 74% |
| 85 / 90 | essentially unchanged | | | |

**Item 31 — market regime: unchanged.** All 84 monthly states are identical in E993-01 and E993-02 (STRONG 63, NORMAL 9, WEAK 7, RISK_OFF 5), as are SPY trend and market breadth. This is expected: the regime uses no fundamental data.

## 8. The owner's provisional mechanics (items 32–38)

**Rules, as implemented in the separate planner `qr_p7_mech.py`** (the frozen P7-CP2 `plan_review` is untouched):

| Rule | Setting |
|---|---|
| Entry / exit / buffer | 80 / 70 / 5 (H2 Balanced) |
| Positions | K = 10, 10% each at entry |
| Relaxation ladder | None |
| Regime limits | 10 / 8 / 5 / 2 positions; the excess is exited lowest-ranked first at the monthly review |
| Sector cap | At most 3 holdings per PIT FF12 sector; skip and take the next |
| Share class | One class per company; a held class is kept on its own score |
| Weekly hard-disqualifier exits | Cash until the next monthly review |
| Ties | Total → Fundamental → Technical → ADV20 → id |

| Mechanics (CP3R data; CP3 data in brackets) | **Item 32: provisional, no regime limits** | **Item 33: provisional with regime limits 10 / 8 / 5 / 2** | Reference: frozen P7-CP2 planner 80 / 70 / 5 / 10 |
|---|---|---|---|
| Orders a year | 48.3 [45.1] | **47.1** [43.1] | 60.3 [54.4] |
| Entries a year | 21.0 | 19.9 | 22.4 |
| Replacements a year | 3.9 | 4.4 | 8.4 |
| Normal exits (score < 70) a year | 16.9 | 14.9 | 17.6 |
| Disqualifier exits a year (of which weekly) | 1.6 (1.3) | 1.1 (1.0) | 1.4 (1.1) |
| Regime-limit exits a year | — | 1.4 | — |
| Universe exits a year | 1.1 | 1.0 | 2.0 |
| Sell / rebuy within 3 reviews | 20 (12% of sells) | 23 (14%) | 30 (15%) |
| Median holding [p25–p75] | 2.1 [1.1–4.9] months | 2.0 [1.1–4.3] months | 2.0 [1.1–4.0] months |
| Held ≥ 3 / 6 / 12 months | 40% / 15% / 4% | 39% / 14% / 3% | 35% / 10% / 3% |
| Longest holding | 18.0 months | 18.0 months | 18.0 months |
| Mean capital utilisation (holdings ÷ 10) | 74% [69%] | **69%** [63%] | 80% [74%] |
| Utilisation of the regime limit | 74% | 79% | — |
| Reviews with all 10 slots full | 31% | 24% | 44% |
| Mechanical cost, $100K | 0.82% ($338 commission + $483 slippage) | **0.80%** ($330 + $471) [0.73%] | 1.02% |
| Mechanical cost, $200K | 0.65% | 0.64% | 0.81% |
| Median held score | 80 | 81 | 81 |
| Most-held sector's share of holdings (median / p90) | 35% / 57% | 38% / 60% | 44% / 69% |
| Reviews where the sector cap skipped a candidate | 38 (124 candidates skipped) | 32 (106) | — |
| Reviews where the regime limit was below holdings | — | 8 | — |

**Utilisation by year, provisional with regime limits:**

| Year | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|---|---|
| Utilisation | 53% | 85% | 50% | 68% | 74% | 58% | 93% |

2011 and 2016 include the RISK_OFF / WEAK months.

**Item 34 — no relaxation ladder: confirmed.** The planner buys only candidates with score ≥ 80 (tested: a 79 is never bought); empty slots stay in cash.

**Item 35 — grown-winner cap 20%:** recorded as a future risk rule only (`qr_p7_mech.GROWN_WINNER_CAP = 0.20`; trim back to 20% at the next monthly review). It needs prices, so it was **not** simulated or performance-tested. No historical winner was examined.

**Item 36 — sector cap of 3 per FF12:**
- Implemented in the mechanics planner on the PIT FF12 sector, as a mechanics rule only.
- Its operating effect: it skipped 124 candidates in 38 reviews and lowered the median largest-sector share from 44% to 35%.
- It changes which candidates are held, so the ranking-to-holding path differs from the frozen P7-CP2 planner; it was not evaluated on returns.

**Item 37 — held share classes are not switched for liquidity.**
- The planner skips any candidate whose company is already held (company skips: 0 in these runs).
- It evaluates a held non-chosen class on its own score; the host now scores non-chosen classes with the class substituted.
- In the provisional runs no held class ever became the non-chosen class (0 reviews). Under the old rule, CP3 had found 3 such switches across 48 books.

**Item 38 — weekly disqualifier exits leave cash until the monthly review: confirmed.** Weekly checks only sell (frozen `weekly_check`); entries happen only at monthly reviews. Weekly exits are 1.0–1.3 a year, mostly H5 (stopped trading after an acquisition).

**Tie-break (owner rule 26), difference documented before the change:**

| | Rule |
|---|---|
| P7-CP2 `plan_review` | Total → ADV20 → id |
| Owner's rule, used in `qr_p7_mech` | Total → Fundamental subtotal → Technical subtotal → ADV20 → id |

Among eligible 80+ candidates (CP3R data):
- the order differs in 52 of 84 reviews (276 adjacent equal-score pairs);
- the set of the 10 best differs in only 8 reviews.

## 9. Confirmations (items 39–43)

| # | Confirmation |
|---|---|
| 39 | No return of any kind was computed. The export and all offline outputs contain no return-like field (checked by the extract script and tests). The runner's registry columns for E993-02 show its standard template for an untouched cash account (trades 0, CAGR 0); they describe no strategy and were not used |
| 40 | No backtest was run. E993-02 placed **0 orders** (QuantConnect Total Orders 0; 23 / 23 runner integrity checks pass); the shadow books use a constant mechanical notional and no prices |
| 41 | 2018–2021 untouched: the run ends 2017-12-31 and the last session is 2017-12-29 |
| 42 | Holdout untouched |
| 43 | Nothing purchased. SEC EDGAR is free public data |

**Run record:**
- E993-02: backtest `13c9b21d4b0a574c61009027ab0579cc`, commit `5805c497`, LEAN 18131, runtime 687 s, peak memory 6.2 GB.
- 84 reviews and 325 weekly checks, both matching the session calendar.
- Sliced technical computation: 336 / 336 spot checks exact.

## 10. Decisions for the owner

1. **Approve the conclusion:** the mechanics are confirmed and can be frozen for predictive-test design, with the provisional settings above.
2. **Confirm the store-wide revenue baseline as implemented** (sections 1–3). Score v1 itself is unchanged.
3. **Registrant check strictness:**
   - (a) keep it as implemented: reject only a known CIK change;
   - (b) also require the CIK to be known and identical at both dates. This keeps up to 1,085 more rescued rows (17%) in H2 and would also exclude legitimate successors such as Zillow.
4. **Planner for the predictive test:** the provisional planner `qr_p7_mech` (sector cap, regime limits, sticky share class, owner tie-break) replaces the frozen P7-CP2 `plan_review` as the portfolio rule. Its specification and code would be frozen at the next checkpoint.
5. **Costs:** at the provisional settings the mechanical cost is about 0.80% a year at $100K (0.64% at $200K). The frozen-planner variant without the sector cap would be 1.02%.

**STOP.** No predictive test, no future returns, no backtest, no 2018–2021, no Holdout. Waiting for explicit owner approval.

## Files

| Path | Content |
|---|---|
| `docs/owner/2026-10-06_p7cp3r_revenue_baseline.md` | Owner record (D173) and implementation readings |
| `src/qresearch/lean/qr_p7_export.py` | `RevenueLedger`, `baseline_check`, alternate-class scoring |
| `src/qresearch/lean/qr_p7_mech.py` | Provisional mechanics planner |
| `strategies/X993_p7_score_mechanics_export/main.py` | v1.1 host |
| `experiments/E993-02/` | Run record |
| `research/phase7/P7_CP3R_extract.py` → `P7_CP3R_E993_stats.json`, `P7_CP3R_E993_payload.json.gz` | Host statistics and score tables |
| `research/phase7/P7_CP3_mechanics.py` → `P7_CP3R_mechanics.json`, `P7_CP3R_tables.md` | CP3R metrics. `P7_CP3_mechanics.json` was regenerated from E993-01: identical except for the added provisional section |
| `research/phase7/P7_CP3R_compare.py` → `P7_CP3R_compare.json` | CP3 vs CP3R comparison |
| `research/phase7/P7_CP3R_sec_check.py` → `P7_CP3R_sec_check.json` | Independent SEC check of the rescued sample |
| `tests/test_p7_cp3r.py`, `tests/test_p7_export.py` | Tests A–E, the planner, host-level rescue / life / eligibility independence / determinism, committed outputs |

**Totals:**
- Experiments logged: 495 (E993-02 added; infrastructure).
- Hypotheses: 19, unchanged. Phase 7 has not consumed a research hypothesis slot.
