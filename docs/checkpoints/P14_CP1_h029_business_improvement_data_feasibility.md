# P14-CP1 — H029 Business Improvement Data Feasibility Audit

**Date:** 2026-10-12. **Decisions:** D227 (owner request), D228 (this checkpoint).
**Status:** STOPPED, awaiting the owner.
- **Run:** ONE in-cloud audit run, E802-01 (host X802, 0 orders).
- **Exported:** aggregates only (counts, percentiles and correlations between input values).
- **Not computed:** no return, IC, Sharpe, wealth or feature-return statistic was computed, requested or inspected.

```
H029 DATA FEASIBILITY — PASS
```

**This is a data-quality result only. No evidence regarding H029 profitability has been generated.**

## Direct answers

**Q1 — Do we have enough point-in-time fundamental data to build a Business Improvement Score?**
**Yes, with documented handling.**
- 6 of the 8 families can be built cleanly enough. All 6 are class B; none is class A.
- Requiring at least 3 of those 6 signals gives a median of 81.6% of eligible stocks per month (the pre-set minimum is 70%).
- Coverage is clearly weaker in 2011–2014.

**Q2 — Which of F1–F8 are cleanly feasible?**
- **None is class A** (cleanly feasible).
- **Six are class B** (feasible with documented data handling):
  - F1 revenue growth acceleration (same-quarter year-on-year form);
  - F2 gross margin improvement;
  - F4 cash generation (operating cash flow / assets);
  - F5 profitability (return on assets);
  - F7 share dilution (from SEC cover-page share counts);
  - F8 asset turnover.
- **Why none reaches A:**
  - every one has much lower coverage in 2011–2014;
  - five of the six have coverage below 85%;
  - the F2, F4 and F5 inputs (gross profit, operating cash flow, net income) are not individually protected by the restatement guard;
  - F7 needs split adjustment of SEC share counts.

**Q3 — Which are problematic, and why?**
- **F3 operating margin (class C):**
  - operating income failed the programme's SEC value validation (D113: only 48% agreement, because of vendor standardisation);
  - 37 of the 131 months have coverage below 50%.
- **F6 leverage (class C):**
  - total debt was never validated against SEC filings and is not approved;
  - the vendor's zero debt is read as "missing", so debt-free companies cannot be told apart from missing data;
  - net debt is impossible because cash is not a Data v2.1 field.
- Neither is "not feasible" (class D). Both are a material data-quality concern.

**Q4 — How many stocks per month would get a usable H029 Score?**
Over the 6 class-B families (median eligible non-financial universe: 934 stocks, range 644–1,379):

| Missing-data rule | Median stocks | Minimum | 2011–14 | 2015–17 | 2018–21 |
|---|---|---|---|---|---|
| All 6 present | 622 | 0 | 358 | 624 | 693 |
| At least 5 of 6 | 720 | 286 | 433 | 722 | 816 |
| At least 4 of 6 | 773 | 340 | 471 | 775 | 849 |
| At least 3 of 6 | 781 | 372 | 477 | 784 | 864 |

The all-6 rule reaches zero in early 2011, because F7 has no share-count history yet.

**Q5 — Does coverage materially worsen in the earlier years?**
**Yes.**
- Every fundamental form is 13–20 points lower in 2011–2014 than in 2015–2021. For example, F2 gross margin covers 55% in 2011–2014 against 75–76% later.
- Causes:
  - the long history requirement (six to nine consecutive quarters);
  - the Data v2 rule that a report must match an SEC filing, which is sparser in 2009–2011.
- F7 is unavailable from January to June 2011 and partial in July 2011.
- This is flagged ("AVAILABILITY TREND") and was not fixed, as instructed.

**Q6 — Are restatements or publication timing a serious leakage risk?**
**Timing: no. Restatements: small but not zero for some fields.**
- **Timing:**
  - every value is built from reports as they were visible on the decision date;
  - the run's checks found 0 reports used before their SEC filing or first appearance, 0 records dated after the decision date, and 0 share-count filings not yet public.
- **Restatements:**
  - the existing guard blocked 214 report versions (0.2%) that already carried a later, not-yet-public revenue or total-assets value;
  - comparison quarters are always the version known at the decision date.
- **Remaining risk:** gross profit, net income, operating cash flow, operating income and debt are not checked field by field. A vendor version that restates only those fields would not be caught. This is flagged as **PIT RESTATEMENT RISK (partial)** for F2, F3, F4, F5 and F6.

**Q7 — Are any proposed signals essentially duplicates?**
- **Within the six class-B families: no.** The largest median correlation is 0.39 (F2 with F5).
- **Two near-duplicates exist only among the alternatives:**
  - the two cash-generation forms (F4-A vs F4-B, 0.82);
  - gross profit / assets change vs revenue / assets change (F5-B vs F8, 0.80).
- Gross margin and operating margin overlap strongly (F2 vs F3, 0.65).

**Q8 — How different are these signals from H028's information?**
**Mostly different.**
- The largest overlap with any H028 feature is F8 asset turnover vs asset growth (AG), median ρ 0.47. Also F5-B vs AG 0.39 and F7 vs AG 0.35.
- Every other pair is within ±0.30.
- **LOWVOL:**
  - every candidate is within ±0.08;
  - except F7 (+0.18): companies shrinking their share count tend to be less volatile.

**Q9 — Can H029 be built without machine learning, λ or optimised weights?**
**Yes.**
- Each class-B signal is a simple, deterministic change in an accounting ratio.
- The monthly percentile-rank → [−1, +1] transform works: even the thinnest signal has at least about 300 valued stocks in 95% of months.
- Ranking also neutralises the extreme values found.
- An equal-weight average of the approved signals needs no fitted parameter.

**Q10 — What exact decisions must the owner make before any backtest is allowed?** See item 50:
- which families are approved;
- the F1 / F4 / F5 forms;
- the missing-data rule;
- the universe (excluding financials or not);
- the 2011–2014 handling;
- outlier and denominator rules;
- the F7 handling;
- a standalone host;
- and then a separate H029-B pre-registration with its gates.

## Required items

### Context

1. **Owner objective:**
   - roughly 30-year terminal wealth above SPY;
   - strong upside participation;
   - materially better downside protection;
   - isolated losing years acceptable (D226 prospective standard).
2. **H028 frozen status:** ORIGINAL RESEARCH STATUS: H028 REJECTED; 30-year alignment PARTIALLY OBJECTIVE-ALIGNED. Unchanged, unused here, never refit.
3. **H029 rationale:** "Companies whose underlying business fundamentals are improving may subsequently outperform companies whose fundamentals are stagnant or deteriorating."
   - It targets independent upside information in ordinary and rising markets.
   - It is standalone: no H028 score, LOWVOL overlay, coefficients or regime logic.
4. **No return analysis:**
   - X802 forms no return and builds no open-price or total-return matrix. A test checks this, and the host source contains no return function.
   - The export and analysis contain counts, percentiles and correlations between input values only.
   - The analysis refuses to load an export containing return-like keys.
   - No feature was judged by profitability.
5. **Data v2.1 reference:** frozen manifest `research/phase11/data_v21/data_freeze_v21.json` (owner exception D213 preserved), read through the byte-identical X801 host.
   - E802-01's 131 review universes equal the H026 canary E028-01 digest for digest (131/131).
   - Nothing was rebuilt; nothing was purchased.
6. **Holdout confirmation:** 2022-01-01 → 2026-08-31 not accessed in any form. The run ends 2021-12-31, and the Holdout lock refuses any 2022+ configuration (tested).
7. **Universe:**
   - **Base:** Data v2.1 eligible stocks at each of the 131 month-end reviews (2011-01 → 2021-11): US common stock (NYSE / Nasdaq), point-in-time market cap ≥ $2B (QuantConnect's or the D111 SEC repair), price ≥ $5 and ADV20 ≥ $5M; no survivor requirement.
   - **Primary (gated) universe, U_NF:** the base minus SEC-SIC 6000–6999 financials and REITs (the owner-approved P7-CP1 exclusion).
     - Median 934 stocks per month.
     - Stocks without a SEC SIC stay in U_NF (4.0% of stock-months) and count as missing when they lack data.
   - **U_ALL (with financials):** reported per signal.

### The eight families (exact constructions; "+" = improvement; all values as known on the decision day)

**Notation:**
- k = fiscal quarters before the latest visible report q0 (at most 200 days old), on one consecutive chain.
- R, GP, OI, NI, OCF = True trailing-twelve-month values from the frozen rules.
- TA and D = total-assets and total-debt snapshots.

8. **F1 Revenue growth acceleration.**
   - **Primary (chosen by the coverage rule), F1-Q:** (r0 / r4 − 1) − (r1 / r5 − 1), where r is quarterly revenue. This is same-quarter year-on-year growth this quarter minus the same measure last quarter.
   - **Alternative, F1:** (R0 / R4 − 1) − (R1 / R5 − 1) on trailing twelve months.
9. **F2 Gross margin improvement:** GP0 / R0 − GP4 / R4.
10. **F3 Operating margin improvement:** OI0 / R0 − OI4 / R4.
11. **F4 Cash generation.**
    - **Primary, F4-B:** OCF0 / TA0 − OCF4 / TA4.
    - **Alternative, F4-A:** OCF0 / R0 − OCF4 / R4.
    - **Structurally cleaner: F4-B.**
      - Coverage is 80.9% vs 76.4%.
      - Tails are far lighter: p1 / p99 of −0.17 / 0.20 vs −0.42 / 0.44, and min / max of −0.8 / 3.0 vs −1,448 / 2,249.
      - Total assets is never near zero, whereas revenue sometimes is.
12. **F5 Profitability improvement.**
    - **Primary, F5-A:** return-on-assets change, NI0 / TA0 − NI4 / TA4.
    - **Alternative, F5-B:** gross profit / assets change.
    - F5-A has 78.7% coverage vs 73.9%. F5-B is a near-duplicate of F8 (ρ 0.80).
13. **F6 Leverage improvement:** −(D0 / TA0 − D4 / TA4).
    - Net debt is not constructible: cash is not in Data v2.1.
14. **F7 Net share issuance:** −(S0 / S1 − 1).
    - S0 = the latest usable SEC cover-page share count (filed + 1 ≤ T, cover ≤ 135 days old).
    - S1 = the count whose cover date is closest to one year earlier (±45 days).
    - Both are restated to T's share basis using only splits dated on or before T (the frozen D111 rule).
    - The vendor's split-adjusted-to-today share fields are never used.
15. **F8 Asset turnover improvement:** R0 / TA0 − R4 / TA4.

### Data mapping, timing, restatements, history

16. **Raw-field mapping:**

    | Signal | Required raw fields | Available in Data v2.1? | PIT timestamp? | History depth |
    |---|---|---|---|---|
    | F1-Q | quarterly revenue (q0, q1, q4, q5) | yes | yes: first seen in stream / SEC filing + 1 | 6 consecutive quarters |
    | F1 (alt.) | revenue TTM at q0, q1, q4, q5 | yes (approved) | yes | 9 quarters |
    | F2 | gross profit TTM, revenue TTM (q0, q4) | yes (approved) | yes | 8 quarters |
    | F3 | operating income TTM, revenue TTM | operating income stored but **not approved** (D113) | yes | 8 quarters |
    | F4-B / F4-A | operating cash flow TTM; total assets (or revenue TTM) | yes (approved) | yes | 8 quarters |
    | F5-A / F5-B | net income (or gross profit) TTM; total assets | yes (approved) | yes | 8 quarters |
    | F6 | total debt, total assets snapshots | debt stored but **not approved**; a zero reads as missing; **cash absent** | yes | 8 quarters (snapshots q0, q4) |
    | F7 | SEC cover-page shares + filing / cover dates; split events | yes (Data v2 reference table, 103,209 cover counts) | yes (filed + 1) | two counts about a year apart |
    | F8 | revenue TTM, total assets | yes (approved) | yes | 8 quarters |

17. **PIT timing audit:**
    - **Period end:** the report's fiscal quarter end.
    - **Availability used by Data v2.1:** max(first seen in QuantConnect's historical stream, original SEC periodic filing + 1 day). There is no vendor file date and no +90-day rule.
    - **When the feature is computed:** on the universe-selection day, which is the calendar day after the review session.
    - **Earliest permissible trade:** the next session's open.
    - **Run checks, all 0:**
      - reports fed before their SEC filing or before first seen;
      - store records dated after the decision day;
      - universe rows without live values;
      - records older than 200 days;
      - share counts stale or not yet public;
      - F7 filings dated on or after the decision day.
    - **Splits:** applied only if dated on or before the decision day (by construction, and unit-tested).
    - **Conclusion:** H029 could never use a filing before the market could see it.
18. **Restatement audit:**
    - **What an investor believed at T is reconstructible.** On the decision day the store holds, for every period, the latest version visible that day.
      - A comparison quarter is therefore as known at T: revisions public before T are used, revisions made after T never are.
      - Feature windows containing a period revised after its first observed version: 0.01–0.17% of valid values. This is a lower bound, since it is only tracked at month ends.
    - **Look-ahead in first-seen versions:**
      - the Data v2.1 guard blocked 214 versions (0.20% of 105,289 fed) whose revenue or total assets already equalled a later, not-yet-public SEC value;
      - vendor revisions seen: 748; amendments: 241.
    - **PIT RESTATEMENT RISK (partial) — flagged, not silent:**
      - gross profit (F2), operating cash flow (F4), net income (F5), operating income (F3) and total debt (F6) are not checked field by field;
      - such a version is still blocked if its revenue or total assets carry a later value.
    - **Fully covered:** F1 and F8 (revenue and total assets are guarded).
    - **F7:** uses original SEC filings only, so each count belongs to its own filing.
19. **Warm-up / history requirements:**

    | Signal | Requirement |
    |---|---|
    | F1-Q | 6 consecutive visible quarters |
    | F1 (TTM form) | 9 |
    | F2–F6, F8 | 8 (the trailing twelve months ending at q4 needs q4..q7) |
    | F7 | two SEC cover counts about a year apart |

    - Every True-TTM window also needs a fiscal-year reconciliation (1%).
    - Missing quarters are never interpolated: a gap makes the value missing (unit-tested).
    - F7 is unavailable from January to June 2011, because the reference table holds no cover count a year earlier.

### Coverage and data behaviour (U_NF; the median over 131 months)

20. **Monthly coverage by feature** (the full monthly series is in `P14_CP1_audit.json`):

    | Form | Median | Mean | Minimum | Months < 50% | Level | U_ALL median |
    |---|---|---|---|---|---|---|
    | **F1-Q** | 85.8% | 82.3% | 62.3% | 0 | STRONG | 86.7% |
    | F1 (alt.) | 75.1% | 70.6% | 42.4% | 4 | USABLE | 76.0% |
    | **F2** | 73.8% | 68.3% | 40.9% | 8 | USABLE | 64.9% |
    | F3 | 71.6% | 65.6% | 38.1% | 37 | USABLE | 64.4% |
    | F4-A (alt.) | 76.4% | 71.7% | 48.3% | 1 | USABLE | 76.7% |
    | **F4-B** | 80.9% | 76.2% | 52.3% | 0 | USABLE | 82.4% |
    | **F5-A** | 78.7% | 74.9% | 50.2% | 0 | USABLE | 80.5% |
    | F5-B (alt.) | 74.0% | 69.0% | 41.4% | 2 | USABLE | 65.5% |
    | F6 | 79.6% | 75.9% | 58.1% | 0 | USABLE | 81.5% |
    | **F7** | 83.7% | 78.2% | 0.0% | 7 (2011-01 → 07) | USABLE | 85.4% |
    | **F8** | 76.8% | 72.4% | 48.3% | 1 | USABLE | 77.5% |

    **Breadth:** U_NF median 934. Valid count per month (median / minimum / 5th percentile):

    | Form | Median | Minimum | 5th percentile |
    |---|---|---|---|
    | F1-Q | 810 | 416 | 478 |
    | F2 | 694 | 293 | 355 |
    | F4-B | 776 | 372 | 411 |
    | F5-A | 753 | 360 | 401 |
    | F7 | 793 | 0 | 300 |
    | F8 | 730 | 346 | 397 |

    No form is flagged SMALL CROSS-SECTION.
21. **Early / middle / late coverage (medians):**

    | Form | 2011–14 | 2015–17 | 2018–21 |
    |---|---|---|---|
    | F1-Q | 73.3% | 87.1% | 85.8% |
    | F2 | 55.2% | 74.8% | 76.0% |
    | F3 | 48.9% | 72.9% | 75.2% |
    | F4-B | 63.2% | 83.1% | 81.9% |
    | F5-A | 62.6% | 81.5% | 79.5% |
    | F6 | 64.0% | 81.6% | 81.3% |
    | F7 | 82.1% | 85.6% | 81.6% |
    | F8 | 60.4% | 78.2% | 78.7% |

    **AVAILABILITY TREND** is flagged for every fundamental form, but not F7. Any later result for 2011–2014 must be read with this in mind.
22. **Sector coverage** (pooled, by SEC SIC at the review):
    - **No FF12 sector** holding at least 3% of U_NF falls below 50% on any primary form.
    - **Weakest sectors:**
      - Energy: F2 56%, F8 67%;
      - Health: F2 62%;
      - Telecom: F7 58%;
      - Shops: about 72–81%.
    - **Stocks without a SEC SIC** (4.0% of U_NF stock-months) are almost entirely missing (6–8%). This is the Data v2 identity residual (the D192 / D213 owner exceptions), not a sector effect.
    - **Financials (excluded):** F2 / F5-B are only about 33% (banks have no gross profit), while F1-Q / F4-B / F5-A / F7 are 84–88%.
23. **Staleness** (days from the latest underlying disclosure to the decision day, valid values, all periods):
    - **F1–F8 forms:** median 49–50, 75th percentile 66, 90th 87–88, 95th 92, maximum 166–168.
    - **F7:** median 50, 95th 92, maximum 133.
    - **Fiscal-period age:** median 91 days, 95th percentile 124, maximum 200 (the freshness cap).
    - The same in 2011–2014 and 2018–2021.
    - **Conclusion:** information is about 1.5–3 months old, as expected for quarterly filings; nothing is used beyond the 200-day cap.
24. **Update frequency:**
    - Every form changes in about 33% of consecutive month pairs (F7 31.7%).
    - The median constant run is 3 months (25th–75th percentile 3–3).
    - These are quarterly signals: a monthly portfolio would reuse each value for about three reviews.
25. **Outlier audit** (pooled oriented values, U_NF):

    | Form | p1 | p5 | Median | p95 | p99 | Minimum | Maximum |
    |---|---|---|---|---|---|---|---|
    | F1-Q | −0.90 | −0.24 | 0.000 | 0.27 | 1.03 | −20,457 | 20,458 |
    | F1 (alt.) | −0.32 | −0.11 | −0.001 | 0.13 | 0.37 | −384 | 251 |
    | F2 | −0.24 | −0.055 | 0.001 | 0.057 | 0.18 | −35 | 54 |
    | F3 | −0.42 | −0.090 | 0.002 | 0.095 | 0.45 | −1,928 | 2,848 |
    | F4-A (alt.) | −0.42 | −0.10 | 0.004 | 0.11 | 0.44 | −1,448 | 2,249 |
    | F4-B | −0.17 | −0.081 | 0.001 | 0.081 | 0.20 | −0.78 | 2.97 |
    | F5-A | −0.22 | −0.092 | 0.001 | 0.098 | 0.26 | −21.6 | 3.19 |
    | F5-B (alt.) | −0.27 | −0.12 | −0.002 | 0.080 | 0.18 | −1.78 | 1.02 |
    | F6 | −0.31 | −0.15 | 0.000 | 0.089 | 0.19 | −14.9 | 1.56 |
    | F7 | −0.77 | −0.16 | −0.001 | 0.076 | 0.15 | −3.5 × 10⁸ | 1.0 |
    | F8 | −0.63 | −0.28 | −0.006 | 0.17 | 0.36 | −2.86 | 8.06 |

    **Pathologies (share of U_NF stock-months):**
    - equity ≤ 0: 3.9% (2018–2021: 4.7%);
    - net-income sign flip year on year: 8.3%;
    - operating-income sign flip: 3.1%;
    - revenue jump > 50%: 3.3%;
    - total-assets jump > 50% (M&A or discontinuity): 5.9%;
    - tiny revenue base (< $10M): 0.17%;
    - tiny asset base (< $50M): 0.06%;
    - total assets ≤ 0: none.

    **Extreme values:** the F1-Q, F3 and F4-A extremes come from near-zero revenue quarters. The F7 minimum (−3.5 × 10⁸) is an implausible share-count ratio (unit or split mismatch); about 1% of F7 values are below −0.77. The F7 share-count jump flag was defined in the host but not computed.
    **Recommendations only, not implemented:** a rank transform; treat |S0/S1 − 1| > 0.5 as missing for F7; consider a minimum quarterly revenue for F1-Q.
26. **Seasonality:**
    - Quarter-over-quarter revenue changes repeat strongly a year later: the median monthly Spearman between the change ending at q0 and the one ending at q4 is **0.61**.
    - The median |QoQ| change is 6.4%, against 9.4% year on year. Gross margin shows a weaker pattern (0.33).
    - **Quarter-over-quarter comparisons are therefore unacceptable.** All constructions here are comparable-period: same-quarter YoY (F1-Q), or TTM vs the prior TTM (all others).
    - For F1 both comparable-period forms are feasible; F1-Q has more coverage, F1 (TTM) lighter tails.
27. **TTM feasibility** (frozen rules, at q0, U_NF):

    | Base | TTM available | Missing quarterly value | No fiscal-year reconciliation |
    |---|---|---|---|
    | Revenue | 81.5% | 1.2% | 4.9% |
    | Gross profit | 78.3% | 3.2% | 6.2% |
    | Operating income | 77.3% | 3.5% | 6.7% |
    | Net income | 83.4% | 0.2% | 4.0% |
    | Operating cash flow | 84.0% | 0.6% | 3.0% |

    - Common failures across all bases: no fresh report 5.9%, fewer than 4 quarters 2.7%, non-consecutive quarters 3.9%.
    - Given a TTM at q0, a TTM four quarters earlier also exists in about 95% of cases.
    - No interpolation; missing quarters stay missing; amendments enter only from their own availability.
28. **Denominator / pathology risks:**
    - Ratios require positive denominators (revenue, total assets): otherwise the value is missing. That affects < 0.1% of stock-months, so no PATHOLOGY flag is raised.
    - No form divides by equity or by net income (the unstable near-zero cases are avoided by construction).
    - **Recommended deterministic handling:**
      - (a) keep "denominator ≤ 0 → missing";
      - (b) use cross-sectional ranks, so extreme ratios cannot dominate;
      - (c) for F7, treat implausible ratios (|S0/S1 − 1| > 0.5) as missing;
      - (d) disclose M&A-driven jumps (5.9% of stock-months) rather than remove them.
    - None of this was chosen by performance.

### Redundancy and overlap

29. **Candidate correlation matrix** (median over 131 months of the monthly Spearman, U_NF):

    |  | F1 | F1-Q | F2 | F3 | F4-A | F4-B | F5-A | F5-B | F6 | F7 | F8 |
    |---|---|---|---|---|---|---|---|---|---|---|---|
    | **F1** | 1 | 0.46 | 0.00 | 0.01 | −0.08 | −0.13 | 0.00 | −0.10 | −0.07 | −0.07 | −0.11 |
    | **F1-Q** | | 1 | −0.02 | −0.06 | −0.05 | −0.13 | −0.08 | −0.18 | −0.06 | −0.01 | −0.22 |
    | **F2** | | | 1 | 0.65 | 0.23 | 0.22 | 0.39 | 0.47 | 0.10 | −0.05 | 0.05 |
    | **F3** | | | | 1 | 0.31 | 0.34 | 0.59 | 0.44 | 0.14 | −0.05 | 0.20 |
    | **F4-A** | | | | | 1 | **0.82** | 0.21 | 0.13 | 0.17 | −0.02 | 0.04 |
    | **F4-B** | | | | | | 1 | 0.32 | 0.44 | 0.26 | 0.05 | 0.36 |
    | **F5-A** | | | | | | | 1 | 0.47 | 0.26 | 0.02 | 0.32 |
    | **F5-B** | | | | | | | | 1 | 0.29 | 0.08 | **0.80** |
    | **F6** | | | | | | | | | 1 | −0.20 | 0.26 |
    | **F7** | | | | | | | | | | 1 | 0.10 |

    - **High redundancy** (median |ρ| ≥ 0.80): F4-A–F4-B (two forms of the same family) and F5-B–F8 (cross-family near-duplicate).
    - **Among the six class-B primaries:** the maximum is 0.39 (F2–F5-A), so they are largely complementary.
30. **Correlation with H028 features** (median monthly Spearman on the H026 population, 270–723 stocks a month; H028 features oriented in H028's own direction):
    - **F8:** AG +0.47.
    - **F5-B:** AG +0.39.
    - **F7:** AG +0.35, CBOP +0.25, CFP +0.23, MOM −0.14.
    - **F4-B:** CBOP +0.30, ACC +0.28, AG +0.21, CFP +0.19.
    - **F1:** AG −0.22.
    - **All other pairs:** |ρ| ≤ 0.20.
    - No pair approaches the 0.80 duplicate threshold. H029 is a different information family; its closest neighbour is H028's asset-growth (investment) feature.
31. **Correlation with LOWVOL:** F1 −0.02, F1-Q −0.00, F2 −0.05, F3 −0.08, F4-A −0.03, F4-B −0.06, F5-A −0.05, F5-B −0.05, F6 −0.05, **F7 +0.18**, F8 −0.01.
    - Essentially independent of H028's defensive dimension. The exception is a mild link for share shrinkers.

### Score design feasibility

32. **Transformation:**
    - **Feasible:** the monthly cross-sectional percentile rank, mapped to [−1, +1], within U_NF.
    - **Breadth:** at least about 300 valued stocks per signal in 95% of months.
    - **Tails:** ranks remove the heavy tails documented in item 25, so no winsorisation is needed for a rank score.
    - **Signs:** fixed by economic definition (+ = improvement; F7 inverted so that dilution scores low; F6 likewise).
    - **Not decided:** sector-relative ranking is possible (the main sectors hold hundreds of stocks).
    - No machine learning, λ, fitted weights or feature selection is needed.
33. **Missing-data alternatives** (over the six class-B families; median monthly U_NF coverage, minimum in brackets):

    | Rule | Median | Minimum | 2011–14 | 2015–17 | 2018–21 |
    |---|---|---|---|---|---|
    | (A) all 6 present | 64.6% | 0% | 47.8% | 66.8% | 65.7% |
    | (B) ≥ 5 of 6 | 75.7% | 39.9% | 58.2% | 77.1% | 77.5% |
    | (B) ≥ 4 of 6 | 80.1% | 47.4% | 62.9% | 82.6% | 81.4% |
    | (B) ≥ 3 of 6 | 81.6% | 51.9% | 64.2% | 83.6% | 82.4% |

    **Trade-off:**
    - (A) is the purest, with every stock scored on identical information, but fails 70% and empties early 2011.
    - (B) with ≥ 4 or ≥ 5 keeps 76–80%, at the price of scores built from different subsets.
34. **Minimum feature count** (all eight primary forms F1-Q, F2, F3, F4-B, F5-A, F6, F7, F8; share of U_NF stock-months with at least k available):

    | k | 8/8 | 7/8 | 6/8 | 5/8 | 4/8 |
    |---|---|---|---|---|---|
    | Share | 54.9% | 68.8% | 71.6% | 76.0% | 77.4% |

    Median monthly versions: 61.2%, 73.0%, 75.6%, 79.7% and 81.0%.
35. **Universe bias** (contemporaneous characteristics only; rule ≥ 3 of 6; scored minus unscored stock-months):

    | Period | Log market cap | Log ADV | Log price |
    |---|---|---|---|
    | 2011–14 | −0.11 | −0.11 | +0.16 |
    | 2015–17 | +0.17 | +0.29 | +0.25 |
    | 2018–21 | +0.32 | +0.33 | +0.49 |

    - **Size and liquidity:** since 2015 the scored set tilts towards larger, more liquid, higher-priced companies (about 1.2–1.4× the market cap of unscored ones). There is no consistent tilt in 2011–2014.
    - **Sectors:** unscored stocks are dominated by the no-SIC identity residual (10–21 points more common among them). Otherwise sector mixes differ by at most about 10 points (e.g. "Other" +10 in 2018–2021).
    - **Per-signal patterns** are similar (e.g. F1-Q in 2018–2021: log market cap +0.34; F7: +0.10).

### Feasibility classes (pre-registered rules, `research/phase14/H029A_audit_spec.md` section 7)

36. **F1 (primary F1-Q): B.** STRONG coverage (85.8%), revenue is approved and guarded; AVAILABILITY TREND. The alternative F1 (TTM) is also B.
37. **F2: B.**
    - USABLE coverage (73.8%);
    - gross profit not field-guarded: PIT RESTATEMENT RISK (partial);
    - AVAILABILITY TREND.
38. **F3: C.** Operating income not approved by D113; LOW-MONTH (37 months below 50%).
39. **F4 (primary F4-B): B.**
    - USABLE (80.9%);
    - operating cash flow not field-guarded (partial restatement risk);
    - AVAILABILITY TREND.
    - F4-A is also B.
40. **F5 (primary F5-A): B.**
    - USABLE (78.7%);
    - net income not field-guarded (partial restatement risk);
    - AVAILABILITY TREND.
    - F5-B is also B.
41. **F6: C.**
    - Total debt is not approved (never SEC-validated);
    - a reported zero is read as missing, so about 4% of U_NF stock-months (debt-free companies) cannot be distinguished from missing;
    - net debt is impossible (no cash field).
42. **F7: B.**
    - USABLE (83.7%);
    - documented handling: split restatement, 4-significant-digit storage, cover-date matching;
    - no data in the first half of 2011;
    - implausible extreme ratios need a rule (item 28).
43. **F8: B.** USABLE (76.8%); AVAILABILITY TREND. Revenue and total assets are approved and guarded.
44. **Combined feasibility gate:**
    - **Condition 1 holds:** 6 of 8 families are A or B (minimum 5).
    - **Condition 2 holds:** the combined score keeps a median ≥ 70% under transparent rules (≥ 3 of 6: 81.6%; ≥ 4: 80.1%; ≥ 5: 75.7%). "All 6" (64.6%) would not pass.
    - **Result: PASS.**
    - **Caveat:** the gate uses U_NF (financials excluded). U_ALL is reported per signal only.

### Engineering

45. **Memory:**
    - E802-01 peaked at **7.64 GB** (the B2-8 node limit is about 8 GB).
    - The frozen X801 panel alone reached 7.54 GB. The H029 additions (live candidate arrays, H024 overlap, aggregation) cost about 0.1 GB and 52 s.
    - A future H029 backtest host also needs open-price / total-return matrices for the scored stocks (S028 hosts peaked at 7.6–8.2 GB). This is feasible only with S029-style memory discipline: release the run-time store and the high / low matrices, and build return arrays only for the scored population.
46. **50-file limit:**
    - X802 uploads 46 files.
    - A future standalone H029 host (X801 module + one H029 module + an evaluation / portfolio module) would need about 47–48.
    - Three of the current files (qr_chart, qr_h020_panel, qr_h020_diag) are uploaded only because of a runner keyword rule and are not needed. Narrowing that rule would leave about 44–45.
    - The limit is not a blocker. S030's 50-file chain is avoided entirely.
47. **Host recommendation:**
    - **Start Phase 14 from a standalone host** that subclasses only the frozen, byte-identical X801 Data v2.1 module (as X802 does), plus one H029 module.
    - Do **not** extend the S028 → S029 → S030 chain.
    - Reuse frozen components by import only: qr_h029a candidate constructions, plus the H026 portfolio simulator functions if the owner wants identical mechanics.
    - Narrow the runner's chart-module rule before implementation.

### Confirmations

48. **No backtest:** E802-01 placed 0 orders and formed no portfolio, return or equity path. It was an infrastructure audit with aggregates only.
49. **No H029 strategy result:**
    - no score was formed;
    - no stock was ranked for selection;
    - no performance of any kind was computed;
    - nothing was frozen as an H029 rule.
    - H028 is untouched, H030 not started, and the Holdout is sealed.

## Integrity summary

| Item | Value |
|---|---|
| New hypotheses / strategies / experiments | 0 / 0 (X802 is an infrastructure audit host) / 1 (E802-01) |
| Owner record / spec (before any data) | D227; `research/phase14/H029A_audit_spec.md` (commit d2b6b54, SHA-256 dcb689a3…) |
| Analysis committed before results | 5cd5ef3 (`research/phase14/cp1/P14_CP1_analysis.py`) |
| Run | E802-01, QuantConnect backtest 73cb6fc8…, LEAN 18178 (default build, recorded), commit 2c8b5ee, 1,102 s, 0 orders |
| Data v2.1 universe | 131/131 review-eligibility digests = E028-01 |
| PIT checks | all 0 |
| Output | `research/phase14/cp1/P14_CP1_audit.json` (reproduced by `tests/test_p14_h029a.py`) |

## 50. Exact owner decisions required for H029-B

1. **Which families enter H029:** the six class-B families (F1, F2, F4, F5, F7, F8), and whether F3 and F6 (class C) are excluded. No replacement families may be added (owner section 42).
2. **Forms:**
   - F1: same-quarter year-on-year (F1-Q, more coverage) vs TTM (lighter tails).
   - F4-B (recommended as structurally cleaner) vs F4-A.
   - F5-A vs F5-B (F5-B nearly duplicates F8).
3. **Missing-data rule:** all present (64.6%, fails 70%) vs average of available with a minimum count (≥ 5: 75.7%; ≥ 4: 80.1%; ≥ 3: 81.6%).
4. **Universe:** U_NF (financials and REITs excluded, as in Score v1) vs U_ALL; and the treatment of no-SIC stocks.
5. **2011–2014:** accept the lower early coverage and disclose it, or start the H029 evaluation later (e.g. 2013 or 2015). This must be decided before any return is seen.
6. **Outlier and denominator rules:**
   - rank transform without winsorisation;
   - "denominator ≤ 0 → missing";
   - F7 implausible-ratio rule;
   - optional minimum revenue for F1-Q.
7. **Whether the partial restatement risk is accepted** for gross profit, operating cash flow and net income, or a field-level guard is requested (this would be a Data v2.1 change: v3, separately approved).
8. **Score form:**
   - equal-weight average of percentile ranks mapped to [−1, +1];
   - market-wide vs sector-relative ranks;
   - signs as fixed here.
9. **Host:** a standalone X801-based host (recommended), with memory discipline.
10. **The H029-B pre-registration** (portfolio rules, gates under the D226 standard, null design, benchmarks SPY / H028 / LV15), approved before any return is computed.

---

```
H029 DATA FEASIBILITY — PASS
```

> This is a data-quality result only. No evidence regarding H029 profitability has been generated.
