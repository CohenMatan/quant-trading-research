# H029-A — Business Improvement data-feasibility audit: pre-registered specification

**Owner decision:** D227 (`docs/owner/2026-10-12_p14cp1_h029a_data_feasibility.md`).
**Written and committed** before any H029 candidate value, coverage figure or distribution was computed.
**Scope:** data quality only. The following are never computed, requested or inspected:
- forward or past returns, IC, Sharpe, CAGR or wealth;
- any SPY-relative or portfolio statistic;
- any feature-return relationship.

The in-cloud host (X802) exports aggregates only.

## 1. Data and window

- **Data:** frozen Data Infrastructure v2.1 (`research/phase11/data_v21/data_freeze_v21.json`, owner exception D213), read through the frozen X801 host. X802 subclasses X801 and uploads it byte-identical as `qr_x801`.
- **Frozen rules preserved unchanged:** M2 timing, the restatement guard, identity, the 200-day freshness rule, True TTM and SEC market-cap repair. Nothing in Data v2.1 is rebuilt or changed.
- **Run window:**
  - 2011-01-03 → 2021-12-31, with a warm-up from 2008-07-01 (history only).
  - Nothing after 2021-12-31 is requested. The Holdout (2022-01-01 → 2026-08-31) is never touched.
- **Reviews:** the 131 Data v2.1 month-end reviews 2011-01-31 → 2021-11-30.
  - Every value is computed on the universe-selection day that reflects the review session, i.e. the calendar day after it.
  - It is computed from the PIT store as known that day.
  - The earliest permissible trade is the next session's open.
- **Periods:** 2011–2014 (48 reviews), 2015–2017 (36), 2018–2021 (47), and overall (131).

## 2. Universe (denominators)

- **U_ALL:** the Data v2.1 eligible universe of each review, i.e. X801's `mon[t]` after the SEC market-cap repair. Its filters are:
  - US common stock on NYSE or Nasdaq;
  - PIT market cap ≥ $2B (QuantConnect's, otherwise the D111 SEC cover-share market cap);
  - price ≥ $5 and ADV20 ≥ $5M;
  - point-in-time membership, with no survivorship requirement.
- **U_NF (primary, gated):** U_ALL minus financials and REITs. These are companies whose SEC SIC at the review is 6000–6999 (the owner-approved P7-CP1 exclusion; Score v1 rule H1).
  - Stocks without a SEC SIC stay in U_NF and count as eligible; they are disclosed separately.
  - Reason for using U_NF: the gross-profit, margin and asset-turnover concepts do not apply to banks and insurers. U_ALL is reported alongside for every coverage figure.
- **H026 population:** the H022 population with all 11 H024 features valid (the frozen S028 construction). It is used only for the overlap correlations with the H028 features (section 9).

## 3. Candidate constructions

**Notation:**
- q0 is the latest visible full report at T, and must be the store's current record, at most 200 days old.
- qk is the report exactly k fiscal quarters earlier on one consecutive chain of visible full reports. Consecutive means a gap of 80–100 days, the frozen True-TTM rule.
- X_k is the True TTM of base X for the window ending at qk. It uses the exact frozen `PITStore.ttm_detail` rules applied at that window: four consecutive visible quarters, each with a quarterly value, and a fiscal-year reconciliation within 1% inside the window. There is no interpolation or back-filling.
- TA_k and D_k are the total-assets and total-debt snapshots on the report for qk.
- All values are as known at T. A period revised before T enters in its latest version visible at T.

**Orientation:** "+" always means improvement, as an economic definition fixed here.

| Id | Family | Construction (oriented) | Required span | Validity |
|---|---|---|---|---|
| F1 | Revenue growth acceleration (TTM) | (R0/R4 − 1) − (R1/R5 − 1) | 9 quarters (q0..q8) | R4 > 0, R5 > 0 |
| F1-Q | Same, quarterly same-quarter YoY | (r0/r4 − 1) − (r1/r5 − 1), with r = quarterly revenue | 6 quarters | r4 > 0, r5 > 0 |
| F2 | Gross margin improvement | GP0/R0 − GP4/R4 | 8 quarters | R0, R4 > 0 |
| F3 | Operating margin improvement | OI0/R0 − OI4/R4 | 8 quarters | R0, R4 > 0 |
| F4-A | Cash generation: OCF / revenue change | OCF0/R0 − OCF4/R4 | 8 quarters | R0, R4 > 0 |
| F4-B | Cash generation: OCF / assets change | OCF0/TA0 − OCF4/TA4 | 8 quarters | TA0, TA4 > 0 |
| F5-A | Profitability: ROA change | NI0/TA0 − NI4/TA4 | 8 quarters | TA0, TA4 > 0 |
| F5-B | Profitability: GP / assets change | GP0/TA0 − GP4/TA4 | 8 quarters | TA0, TA4 > 0 |
| F6 | Leverage improvement (debt / assets) | −(D0/TA0 − D4/TA4) | 8 quarters (snapshots q0, q4) | TA0, TA4 > 0; D0, D4 present |
| F7 | Net share issuance (lower dilution = +) | −(S0/S1 − 1) | two SEC cover counts about a year apart | S0, S1 > 0 |
| F8 | Asset turnover improvement | R0/TA0 − R4/TA4 | 8 quarters | TA0, TA4 > 0 |

**F7 rule:**
- S0 is the latest SEC cover-page share count usable at T. Usable means filed + 1 ≤ T and the cover date at most 135 days old. This is the frozen D111 / Data v2 market-cap share rule.
- S1 is the usable count whose cover date is closest to (cover date of S0 − 365 days), within ±45 days. Ties go to the later filing.
- Both counts are restated to T's share basis with the security's own split events dated on or before T. The frozen D111 split rule applies, including the check for a count that already reflects a split between its cover date and its filing date.
- The vendor's share-count fields are never used: they are blacklisted and split-adjusted to today (D107).

**Net debt:** not constructible. Cash is not a Data v2.1 field (`qr_fundamentals.WHITELIST`), and adding a field would rebuild the frozen data. The F6 debt / assets form is therefore audited instead.

**Primary form per family (rule fixed now, data criteria only):**
- F2, F3, F6, F7 and F8 have one form each.
- F1 chooses between F1 and F1-Q, F4 between F4-A and F4-B, and F5 between F5-A and F5-B. The primary form is the one with the higher overall median monthly U_NF coverage.
- If the two are within 1.0 percentage point, the primary is the form with the smaller tail ratio (p99 − p1) / (p75 − p25) of its pooled oriented values.
- The other form is reported as the alternative. This is a structural-cleanliness choice, never a return-based one.

## 4. Field status (fixed facts from earlier audits)

| Field | Data v2.1 source | D113 SEC value validation | Restatement guard (Data v2.1) |
|---|---|---|---|
| revenue (quarterly + TTM) | vendor stream, M2 timing | approved (True TTM) | **guarded** (`revenue_q`) |
| gross profit | vendor | approved (True TTM) | not field-guarded (version blocked only via revenue / total assets) |
| net income | vendor | approved (True TTM) | not field-guarded |
| operating cash flow | vendor | approved (True TTM) | not field-guarded |
| total assets | vendor snapshot | approved | **guarded** |
| operating income | vendor | **NOT approved** (48% agreement, vendor standardisation) | not field-guarded |
| total debt | vendor snapshot | **NOT approved** (never validated); a reported 0 is read as missing (`clean`) | not field-guarded |
| cash | **not in Data v2.1** | — | — |
| SEC cover-page shares | SEC original filings (Data v2 reference table), filed + 1 | used by the approved D111 / D189 market-cap method; stored at 4 significant digits | original filings only (no later value) |

## 5. Statistics computed (aggregates only)

1. **Coverage:** per review, |U| and the number with a valid value, for U_NF and U_ALL, for every form.
2. **Breadth:** per form, the median, minimum and 5th percentile of the monthly valid count (U_NF), plus the median eligible count.
3. **Sector:** pooled coverage per FF12 sector (SEC SIC at the review) and per period, U_ALL.
4. **Staleness:**
   - days from the latest underlying disclosure to T, i.e. T − the q0 report's file date in the store (its usable day − 1, which is the SEC filing day or the vendor first-seen day − 1); for F7, T − the S0 filing date;
   - period age, T − q0 period end;
   - for each: median, 75th, 90th, 95th percentile and maximum, overall and per period.
5. **Update frequency:**
   - over pairs of consecutive reviews where the stock is in U_NF with a valid value in both: the share of pairs in which the value changed;
   - the median length (months) of completed constant runs.
6. **Distribution:** the pooled oriented values per form: p1, p5, p25, p50, p75, p95, p99, minimum and maximum, overall and per period.
7. **Pathology counts (U_NF stock-months):**
   - revenue ≤ 0 or missing at a needed quarter;
   - total assets ≤ 0;
   - equity ≤ 0 on q0;
   - R4 < $10M (tiny revenue base) and TA4 < $50M (tiny asset base);
   - |R0/R4 − 1| > 0.5 and |TA0/TA4 − 1| > 0.5 (M&A / discontinuity proxies);
   - NI sign flips (NI0 · NI4 < 0) and OI sign flips;
   - F7: |S0/S1 − 1| > 0.5.
8. **Seasonality** (revenue and quarterly gross margin):
   - the median absolute quarter-over-quarter change vs the median absolute same-quarter YoY change;
   - the median over reviews of the cross-sectional Spearman between the QoQ change ending at q0 and the QoQ change ending at q4 (a high positive value means a repeating seasonal pattern).
9. **TTM feasibility:**
   - for each base (revenue, gross profit, operating income, net income, operating cash flow), the frozen `ttm_detail` outcome at q0, counted by reason per period (U_NF);
   - the share with TTM also available at q4.
10. **PIT and restatement:**
    - in-host checks that no record with availability > T, no SEC filing with filing date ≥ T and no split dated > T enter any value (each must be 0);
    - the share of feature windows containing a period whose version at T was revised after its first visible version (tracked from month-end snapshots, so a lower bound);
    - the frozen X801 guard and revision counters.
11. **Redundancy:**
    - per review, the Spearman correlation of every pair of the 11 forms (pairwise complete, n ≥ 30, U_NF);
    - the median, mean, 10th and 90th percentile over reviews, and the median of |ρ|;
    - high redundancy = median |ρ| ≥ 0.80.
12. **Overlap with H028:** the same Spearman statistics between the 11 forms and the 11 H024 features, oriented by `qr_h024.DIRECTION`, on the H026 population. LOWVOL is reported explicitly.
13. **Missing-data patterns:**
    - per review, the U_NF count of each validity pattern over the 11 forms;
    - per period and pattern: the sum of log market cap, log price and log ADV20, and FF12 counts.
    - From these, any combined rule's coverage and its contemporaneous size, liquidity and sector bias are computed offline.

## 6. Coverage levels and flags (owner section 18, verbatim thresholds)

On the median over the 131 reviews of U_NF coverage:

| Level | Median coverage |
|---|---|
| STRONG | ≥ 85% |
| USABLE | 70–85% |
| WEAK | 50–70% |
| UNUSABLE | < 50% |

| Flag | Condition |
|---|---|
| LOW-MONTH | more than 10% of reviews (more than 13.1) below 50% |
| SMALL CROSS-SECTION | 5th percentile of the monthly valid count < 100 |
| WEAK SECTOR | an FF12 sector holding ≥ 3% of U_NF stock-months has pooled coverage < 50% |
| AVAILABILITY TREND | median coverage 2018–2021 exceeds 2011–2014 by ≥ 10 percentage points |
| PATHOLOGY | more than 2% of U_NF stock-months are invalid only because of a non-positive or missing denominator |

## 7. Classification (owner section 37), applied to the primary form of each family

- **D — NOT FEASIBLE:** a required field is not in Data v2.1, or coverage is UNUSABLE.
- **C — MATERIAL DATA QUALITY CONCERN** (not D), if any of:
  - a required field is not approved by D113 (operating income, total debt), or zero cannot be told apart from missing;
  - coverage is WEAK;
  - LOW-MONTH;
  - SMALL CROSS-SECTION.
- **A — CLEANLY FEASIBLE** (not C or D), only if all of:
  - coverage STRONG;
  - every required field approved and field-guarded (revenue, total assets);
  - no WEAK SECTOR, AVAILABILITY TREND or PATHOLOGY flag.
- **B — FEASIBLE WITH DOCUMENTED DATA HANDLING:** everything else.
  - F7 is at best B: split restatement rule, 4-significant-digit storage, cover-date matching.
  - Any family using gross profit, net income or operating cash flow is at best B: not field-guarded, so **PIT RESTATEMENT RISK (partial)** is flagged.

## 8. Gate (owner section 38)

**PASS** only if both hold:
1. At least 5 of the 8 families (primary forms) are A or B.
2. The combined score over the n A/B families has median monthly U_NF coverage ≥ 70% under at least one transparent rule:
   - **(i)** all n present; or
   - **(ii)** at least m of the n present, for some m ≥ ceil(n / 2).

Every rule's coverage is reported. Otherwise **FAIL**. A PASS starts nothing: STOP, then owner review, then H029-B.

## 9. Not decided here

- weights;
- the final feature list;
- transformations;
- the missing-data rule;
- winsorisation;
- the universe choice between U_NF and U_ALL.

All of these go to the owner at H029-B. No feature is replaced or added after results (owner section 42).
