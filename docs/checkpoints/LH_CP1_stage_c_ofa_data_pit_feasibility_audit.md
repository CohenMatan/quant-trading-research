# Long-Horizon Stage C — OF-A Data and Point-in-Time Feasibility Audit

**Owner decision D242, 2026-10-18.** The message is recorded verbatim in `docs/owner/2026-10-18_lh_stage_c_ofa_data_pit_feasibility.md`.

**Checkpoint ID:** LH-CP1, the first checkpoint of the long-horizon programme (RM1 / RM2).

**Result in one line:** under the frozen protocol the classification is **C — NOT FEASIBLE**, but only because of one chain-integrity criterion that I mis-specified in the protocol (§8, §24). On every other frozen criterion, C1, C2 and C6 pass. No reclassification is made. **The decision belongs to the owner.**

**This was a non-return data audit:**
- no price, no return, no wealth, no QuantConnect run;
- no surprise value, percentile, ranking or predictive statistic was computed (§27);
- Holdout sealed (§28).

**Labels:** [V] = measured here or in a committed record; [I] = interpretation; [P] = proposal.

---

## 1. Repository state and owner approval [V]

**State before work:**
- `main` was `dc02789` (merge of PR #106, D241).
- Last decision D241; experiments unchanged (580 rows, last E031-09); no `HOLDOUT_UNLOCK.md`.
- QuantConnect checks passed (credentials present, values never printed; site reachable). No QuantConnect call was made.

**Confirmed:**
- H028 REJECTED;
- H029 / H030 NOT EVALUABLE (`research/hypotheses/STATUS.md`);
- no active hypothesis;
- Holdout sealed;
- no frozen experiment, data version or result changed.

**Approved:** Stage C only (D242). Stage B is not approved. Stage A was completed by D241.

**Commits:**

| Commit | Content |
|---|---|
| `df6e7fe` | Owner record and frozen protocol, before any aggregate |
| `612e8d6` | Audit script and tests |
| `d70946c` | Aggregates and the post-hoc diagnostic |

## 2. Audit protocol and protocol hash [V]

- **Protocol:** `research/longhorizon/stage_c/LH_StageC_protocol.md`, **SHA-256 `ff97789b02007599f9e4bdb914dc8b56f50566c1d61e4015c2383a829a195a97`**.
  - Pinned in `tests/test_lh_stage_c.py` and recorded in the output JSON.
  - Committed in `df6e7fe` before the audit script existed. It was not changed afterwards.
- **Disclosed pre-protocol slip:** while checking the cached submissions row layout, two sample rows were printed. They were 2026 Apple 8-K / 10-Q metadata: dates and accession numbers, no values.
  - They enter no statistic.
  - Every SEC row filed after 2021-12-31 is now dropped at load; a test checks that no 2022+ date appears in the outputs.
- **Script:** `research/longhorizon/stage_c/LH_StageC_audit.py` (cache-only SEC client with networking disabled; network requests made: **0**).
- **Output:** `LH_StageC_audit.json`, aggregates only.

## 3. Sources and Data v3 manifest [V]

| Source | Use | SHA-256 (in JSON) |
|---|---|---|
| E981-01 universe export (frozen data-v1 universe: ≥ $2B, price ≥ $5, ADV ≥ $5M, US common; month starts 2010–2021) | Eligible stock-month denominator: 2,719 securities | recorded |
| Data v2.1 reference table (D207; manifest `ef0a7a66…`) | PIT identity (dated CIK + SIC), filing tables (period ends, original 10-Q / 10-K filing days) | recorded |
| Data v3 manifest `data_freeze_v3.json` (D230, "DATA V3 PASS") and `data_v3_reference.json` | Value rules (`qresearch.data_v3`, unchanged); guard counts | recorded |
| SEC company facts (local cache; facts filed ≤ 2021-12-31) | As-known quarterly revenue / NI / GP / total assets | — |
| SEC submissions (local cache; rows filed ≤ 2021-12-31) | 8-K Item 2.02 dates / acceptance times / XBRL flags; periodic-filing rows | — |
| `tz_conventions.json` (D122) | Acceptance-time conventions | recorded |
| E981-01 session calendar | Trading-session counts | recorded |

**Denominator:**
- 159,717 eligible stock-months (131 reviews, 2011-01 … 2021-11). 126,173 are non-financial (U_NF), between 9,110 (2011) and 14,603 (2021) a year.
- **Limitation:** this is the **Data v1 universe**. The Data v2.1 per-stock-month universe exists only in-host and was never exported. Rebuilding it would need prices or a QuantConnect run, which are not approved. The difference is disclosed, not repaired (protocol §2.6).

## 4. Existing Data v3 field coverage [V]

Share of U_NF stock-months whose anchor quarter (the newest visible quarterly or annual filing, at most 200 days old) has a known value:

| Field | 2011 | 2013 | 2015 | 2017 | 2019 | 2021 | 2011–14 | 2015–17 | 2018–21 | Anchor periods covered |
|---|---|---|---|---|---|---|---|---|---|---|
| Revenue (quarterly) | 83.3% | 89.1% | 89.1% | 90.1% | 94.5% | 92.1% | 87.5% | 89.8% | 92.9% | 2010-09 → 2021-10 |
| Net income (quarterly) | 89.3% | 94.0% | 95.0% | 94.9% | 95.5% | 94.3% | 92.8% | 95.1% | 95.0% | 2010-09 → 2021-10 |
| Gross profit (quarterly) | 41.8% | 45.8% | 46.0% | 46.8% | 48.1% | 48.8% | 44.6% | 46.5% | 48.3% | 2010-09 → 2021-10 |

- **Anchors:** 95.1% of U_NF stock-months have a fresh one (91.0% in 2011, about 95–96% after).
- **Gross profit is missing for about half the universe.** Many registrants never tag `GrossProfit`: energy, utilities, telecom, services and financial-like industries.
- **Identity (SEC registrant at the decision date):** 97.4% of all eligible stock-months (96.5–97.8% by year). Sources: identity-v2 rows 154,537, extension rows 1,008, none 4,172. E981-01's own CIK agrees with the frozen identity for 98.3% of stock-months with both.
- **Cached SEC files:** companyfacts and submissions exist for 100% of the 2,096 identity CIKs.

## 5. Quarterly continuity results [V]

Share of U_NF stock-months with k consecutive quarters (gaps of 80–100 days) all carrying a known value:

| Field | k = 5 (2011–14 / 15–17 / 18–21) | k = 9 | k = 13 | k = 17 |
|---|---|---|---|---|
| Revenue | 78.4 / 85.6 / 87.5% | 72.5 / 82.1 / 83.6% | 55.1 / 77.9 / 79.0% | 34.1 / 74.1 / 74.6% |
| Net income | 83.6 / 91.2 / 90.2% | 77.2 / 87.6 / 86.5% | 58.9 / 83.1 / 82.5% | 36.7 / 79.0 / 78.9% |
| Gross profit | 39.6 / 44.3 / 45.4% | 35.9 / 42.5 / 43.4% | 26.6 / 40.3 / 41.2% | 15.9 / 38.3 / 39.1% |

- **Gaps between consecutive periods (70,732 gaps):**
  - 0.83% fall outside 80–100 days. Those are chain breaks (fiscal-year changes, transition periods, missing filings).
  - 0.99% are 14-week quarters (95–100 days, from 52/53-week years). These are accepted by the frozen rule.
- **Long chains are short of history in 2011–2012.** XBRL tagging began mid-2009 for the largest filers and 2011 for the rest, so 13-quarter histories barely exist before 2013 (§7).

## 6. Candidate C1–C6 input sufficiency [V]

Exact RM2 §11 requirements on one contiguous chain, all values known at the decision date:

| Candidate | Inputs | Quarters | Earliest complete history |
|---|---|---|---|
| C1 SUE-NI | NI q0 … q12: the current seasonal difference (q0 − q4) plus **8 prior seasonal differences**, each needing two quarters four apart | **13** | First fiscal quarter with 12 earlier XBRL quarters: about 2012 for 2009 XBRL starters, about 2014 for 2011 starters |
| C2 SUE-REV | Revenue q0 … q12 | 13 | Same |
| C3 Price-scaled | NI q0, q4 + PIT market cap | 5 | About 2010 |
| C4 Acceleration | X q0, q1, q4, q5 (revenue = the H029 F1 form; NI) | 6 | About 2010–2011 |
| C5 GP / assets | GP q0, q4 + total assets q4 > 0 | 5 | About 2010 |
| C6 Dual | C1 and C2 | 13 | As C1 |

**"Eight prior seasonal differences" needs 13 quarters, not 8.** Each difference Δ_k = X_{q_k} − X_{q_{k+4}} (k = 1 … 8) reaches back to q12.

**Missing reasons (U_NF stock-months, first applicable reason):**

| Reason | C1 | C2 | C3 | C5 |
|---|---|---|---|---|
| No SEC identity | 4,172 | 4,172 | 4,172 | 4,172 |
| Extension identity without a dated SIC (protocol rule; conservative) | 1,008 | 1,008 | 1,008 | 1,008 |
| No fresh anchor | 965 | 965 | 965 | 965 |
| Chain too short or broken | 18,488 | 18,488 | 6,110 | 6,110 |
| Value missing at a required quarter | 6,704 | 11,837 | 374 | 58,976 |
| Total assets ≤ 0 | — | — | — | 9 |

**Accounting surprise vs market surprise [I]:** C1, C2, C5 and C6 measure a surprise **relative to a time-series forecast built from the firm's own earlier filings**, not relative to market expectations.
- Without analyst consensus (not available without purchase, D124; P2-CP11) or the release's own numbers (§19), the two are **not interchangeable**.
- C4 measures a change in growth (H029 F1), not a forecast error.
- C3's denominator is price-based, but its numerator is still a time-series change.

**Sensitivity to restatements, negative values and seasonality:** see §10 and §21.
- Every candidate uses same-quarter comparisons (q0 vs q4), so seasonality is handled by construction, and period-end contiguity keeps 52/53-week quarters aligned.
- C1 / C2 scale by the firm's own variance and handle negative earnings.
- C3 and C5 have positive denominators (market cap ≥ $2B; total assets ≤ 0 in only 9 cases).
- Growth-rate forms with NI denominators are excluded (RM2 §10).

## 7. Coverage by year and historical period [V]

Input-complete share of U_NF stock-months (the denominator is the full point-in-time eligible non-financial universe, never survivors):

| | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2011–14 | 2015–17 | 2018–21 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **C1** | 15.0 | 51.8 | 78.7 | 81.4 | 81.3 | 84.1 | 83.9 | 84.1 | 85.0 | 83.1 | 78.6 | 58.9 | 83.1 | 82.5 |
| **C2** | 14.0 | 48.5 | 73.5 | 76.1 | 76.4 | 78.9 | 78.5 | 78.7 | 80.2 | 80.5 | 77.0 | 55.1 | 77.9 | 79.0 |
| C3 | 85.7 | 88.1 | 89.3 | 90.1 | 90.8 | 92.1 | 91.2 | 91.3 | 91.4 | 91.2 | 87.8 | 88.4 | 91.4 | 90.3 |
| C4-REV | 76.9 | 82.4 | 83.4 | 83.4 | 84.0 | 85.7 | 85.6 | 86.2 | 89.1 | 88.4 | 84.9 | 81.7 | 85.1 | 87.0 |
| C4-NI | 82.5 | 87.2 | 88.4 | 88.9 | 89.7 | 91.2 | 90.6 | 90.5 | 90.5 | 90.1 | 86.7 | 86.9 | 90.5 | 89.3 |
| **C5** | 29.5 | 42.2 | 43.3 | 43.3 | 43.9 | 44.8 | 45.1 | 45.0 | 45.6 | 46.6 | 45.4 | 39.9 | 44.6 | 45.6 |
| **C6** | 13.8 | 48.2 | 73.4 | 75.9 | 76.3 | 78.9 | 78.5 | 78.7 | 80.2 | 80.5 | 77.0 | 54.8 | 77.9 | 79.0 |

(Percent; protocol §4; `LH_StageC_audit.json` → `candidates`.)

**Company coverage** (securities with at least one input-complete U_NF stock-month in the period):
- C1: 74 / 84 / 75%;
- C2 and C6: 69 / 78 / 72%;
- C5: 49 / 52 / 48%.

Securities complete in at least half their months: C1 62 / 78 / 69%, C2 57 / 72 / 65%.

**Descriptive sensitivities (not substitutes, protocol §4):**

| C1 coverage | 2013 | 2015 | 2021 |
|---|---|---|---|
| 4 prior differences (9 quarters) | 85% | 86% | 83% |
| 12 prior differences (17 quarters) | 48% | 78% | 75% |
| Up to 2 of 13 values missing | 82% | 82% | 79% |

- C3 / C5 without contiguity: within about 1 point of the contiguous version.
- Shorter lookbacks raise coverage, mainly in 2011–2013. **They are not adopted:** any lookback change is a design option for a later pre-registration.

## 8. Fiscal-calendar irregularities [V / I]

**Facts:**
- 444 of 2,083 registrants carry more than one fiscal-year-end code in the SEC XBRL filing index (2009–2021).
- Chain breaks (gaps outside 80–100 days): 0.83%. 14-week quarters: 0.99%.

**Frozen chain-integrity criterion (protocol §8):** PASS if at most 1% of input-complete chains show a fiscal-year-end code change between q0 and its comparison quarters. **Measured:**

| Candidate | C1 | C2 | C3 | C4-NI | C4-REV | C5 | C6 |
|---|---|---|---|---|---|---|---|
| Chains with codes | 82,802 | 78,644 | 107,369 | 104,284 | 99,741 | 53,180 | 78,587 |
| Code changed | 14.4% | 15.0% | 8.3% | 9.5% | 9.9% | 10.9% | 15.1% |
| Frozen verdict | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** |

**Post-hoc diagnostic** (`LH_StageC_fye_diagnostic.py` / `.json`). It was written **after** this result, uses metadata only, and is **not** used for the classification. Over contiguous 13-quarter chains of the filing tables, 2011–2021:

| Code shift | Share of 13-quarter chains | Meaning |
|---|---|---|
| Changed at all | 10.4% | — |
| ≤ 7 days | 7.4% | **52/53-week drift.** The fiscal-year-end date moves by a few days each year (e.g. 0926 → 0925); the fiscal calendar is not changed |
| 8–31 days | 0.8% | — |
| > 31 days | 2.3% | ≈ 3 or 6 months: 0.9% (quarter-aligned shifts that keep calendar quarters intact); other: 1.3% (unexplained offline: a genuine change or metadata error) |

For 5-quarter chains the shares are 5.7% / 4.3% / 0.4% / 1.0%.

**Interpretation [I]:**
- **The criterion as written was mis-specified.** It measures the fiscal-year-end *label*, which 52/53-week filers change every year.
- All candidates compare quarters by **period end** on chains whose gaps are 80–100 days. A genuine fiscal-year change normally creates a transition period, which breaks the chain and removes the comparison.
- **A residual 1.3% of 13-quarter chains** with unexplained shifts of more than a month **cannot be resolved offline**. Even a corrected label rule with a 1% limit would not obviously pass, so the frozen FAIL is kept as written.

## 9. Quarter-four derivation [V]

Among anchor quarters with a known value, the share derived as **fiscal year minus nine months** (no direct three-month fact):
- revenue 5.8%;
- NI 5.7%;
- GP 6.2%.

Most Q4 values are tagged directly: 10-Ks carry quarterly-data notes with three-month contexts.

**Derivation rule (frozen `Facts.q_known`):** only the latest-filed YTD fact plus a shorter YTD fact with the same start (±7 days). **A year-to-date value is never taken as a quarter** (unit tests: Q2 = H1 − Q1, Q4 = FY − 9M, no value before the 10-K is filed).

Q4 derivation breaks only if the YTD start changes, e.g. at a fiscal-year change. That case is then undefined, never mis-computed.

## 10. Restatement and vintage controls [V]

**Existing (frozen):**
- **Data v3 guard v3:** values restated by more than 1.5% for revenue, GP, NI, OCF and total assets. 45,450 restated values over 141,451 periods of 3,941 registrants (2,931 with at least one). In-host it blocked 1,018 of 116,639 vendor versions (E803-01, D230).
- **Data v2.1 guard** for revenue and total assets (D207).

**Measured here, on input-complete chains:**

| | C1 (NI, 13 quarters) | C2 (revenue, 13 quarters) |
|---|---|---|
| Complete chains | 94,836 | 89,703 |
| At least one value recast (> 1.5%) and public **before** the decision date (PIT-legal; the comparison uses the as-known value) | 20.6% | 24.4% |
| At least one value restated **after** the decision date (≤ 2021) | 11.2% | 14.1% |

- The second row is the vendor look-ahead risk the in-host guard exists for. Guard v3 covers all four C1–C6 flow fields and total assets.
- The offline SEC-side values are PIT by construction.

**Prospective design decision [P]:**
- whether q4 … q12 use the first-reported or the as-known (recast) value (RM2 §10.1).
- Recasts are common (about 1 in 5 chains), so the choice matters and must be pre-registered.

## 11. SEC identity consistency [V]

- **Identity at the decision date:** 97.4% of eligible stock-months. Missing: 2.6% (no row) plus 0.6% extension-only rows without a dated SIC.
  - The protocol counted the latter as missing (conservative).
  - Existing Data v2 practice takes the SIC from submissions; that difference is disclosed.
- **Registrant agreement:** E981-01's vendor / corrected CIK matches the frozen identity for 152,885 of 155,545 stock-months (98.3%). The 1.7% disagreements are successor / predecessor registrants (Morningstar CIKs are current-status, D111).
- **Known residuals (frozen exceptions):**
  - Gate K identity residual, 3.4–6.9% of eligible stock-months a year in Data v2 (D192);
  - P7-CP5e REJECT / no-identity securities.

## 12. 8-K Item 2.02 matching methodology [V]

**Events:** each distinct (registrant, anchor quarter) used by at least one U_NF stock-month: **42,620 events**.

**Periodic filing:** the original 10-Q / 10-K / 10-KT submissions row with the same filing date and a report date within ±7 days. **Matched for 100% of events.**

**Release candidates:**
- 8-K (not 8-K/A, as in Event Data v1) with item 2.02;
- filed after the period end and on or before the periodic-filing day.
- **Unambiguous** = exactly one; **ambiguous** = two or more (earliest used, reported separately).

**Zero candidates:**
- "release after filing" if an Item 2.02 8-K follows within 10 days;
- otherwise "no release found".

**Times** come from the registrant's measured convention (D122). An unknown convention means date-only matching.

## 13. Earnings-release matching coverage [V]

| Class | Events | Share |
|---|---|---|
| Unambiguous | 38,489 | 90.3% |
| Ambiguous (two or more Item 2.02 8-Ks in the window) | 2,880 | 6.8% |
| Release after filing (within 10 days) | 463 | 1.1% |
| No release found | 788 | 1.8% |
| Not determinable (no cached submissions) | 0 | 0% |

- **Missing-event rate:** 2.9%. **Ambiguous rate:** 6.8%.
- **Same day:** 35.1% of unambiguous releases fall on the periodic-filing day (13,494). With known times:
  - the release was accepted first in 11,564;
  - the filing first in 1,757;
  - unknown order in 173.

## 14. Release-to-filing delay [V]

Unambiguous matches, n = 38,489. Ambiguous matches (n = 2,880) in brackets.

| Delay | Median | Mean | p10 | p25 | p75 | p90 | p95 |
|---|---|---|---|---|---|---|---|
| **A** period end → release, days | 31 (16) | 32.1 | 21 | 26 | 37 | 43 | 52 |
| A, sessions | 22 (11) | 22.2 | 15 | 18 | 26 | 30 | 35 |
| **B** release → 10-Q / 10-K, days | **1** (23) | 5.7 | 0 | 0 | 9 | 17 | 22 |
| B, sessions | 1 (17) | 4.0 | 0 | 0 | 6 | 12 | 15 |

**Median B by availability year** (days): 2011 7 · 2012 6 · 2013 4 · 2014 2 · 2015 2 · 2016–2021 1. Filers increasingly file the 10-Q with or a day after the release.

## 15. Filing-to-Data-v3 delay [V]

- **C** filing → availability: exactly **+1 calendar day by the frozen rule** (filing day + 1, the SEC side of the M2 availability rule), for all 42,620 events.
- In-host, availability is max(SEC filing + 1, first seen in QuantConnect's stream). Its first-seen side was measured as the day after filing in 96–99% of cases (P7-CP5d, D187).
- The offline figure is therefore a lower bound, and is not recomputed here.

## 16. First legal execution availability [V]

**Convention:** a filing dated d is usable at the selection stamped after the session on or after d. The earliest order is the open of the first session strictly after d (frozen Data v3 / universe-selection convention; no intraday).

| Delay (unambiguous; ambiguous in brackets) | Median | Mean | p10 | p25 | p75 | p90 | p95 |
|---|---|---|---|---|---|---|---|
| **E1** daily decisions: sessions after the release's own earliest trade | 1 (17) | 4.0 | 0 | 0 | 6 | 12 | 15 |
| E1: sessions from the release date | 2 (18) | 5.0 | 1 | 1 | 7 | 13 | 16 |
| **E2** monthly reviews: sessions from release date to the first review trade | **18** (30) | 16.4 | 3 | 7 | 22 | 27 | 30 |
| E2, calendar days | 26 (44) | 24.1 | 5 | 11 | 33 | 40 | 43 |

**Median E2 by year** (sessions): 2011 20 · 2012 19 · 2013 18 · 2014 17 · 2015 17 · 2016 18 · 2017 18 · 2018 18 · 2019 17 · 2020 16 · 2021 17.

## 17. Monthly-review waiting times [V]

**D:** availability → first review, over first-use-timely events (n = 40,951).

| | Median | Mean | p10 | p25 | p75 | p90 | p95 |
|---|---|---|---|---|---|---|---|
| Days to the selection day | 20 | 16.3 | 1 | 4 | 25 | 28 | 29 |
| Sessions to the trade | **14** | 11.3 | 1 | 3 | 17 | 19 | 20 |

**Traded within 5 / 10 / 20 / 30 sessions of availability:** 35.2% / 44.9% / 95.0% / 98.5%.

**Window-start effect:** 630 events became available in late 2010 and waited for the first review (2011-01). They are 1.5% of n, and their by-year median is 58 sessions. From 2011 onward the by-year medians are 11–14 sessions.

**[I]** The monthly calendar, not the filing lag, causes most of the delay: about 14 of the median 18 sessions from release to trade.

## 18. Data freshness at review [V]

Over U_NF stock-months with any visible filing (120,993):
- **stale under the RM2 one-quarter rule** (availability more than 91 days before the decision): **4.9%**;
- beyond the frozen 200-day period-age rule (no anchor): 0.8%.

## 19. Whether information was previously disclosed [V / I]

| Category (protocol §6.8) | Events | Share |
|---|---|---|
| 1 Definitely known earlier (disclosure event): an unambiguous Item 2.02 release accepted before the periodic filing | 36,559 | **85.8%** |
| 2 Potentially known earlier: ambiguous candidates, or same day with unknown order | 3,053 | 7.2% |
| 3 First verifiable through the structured filing: no Item 2.02 8-K up to 10 days after | 788 | 1.8% |
| 4 Cannot be determined: release after the filing, or no cached submissions | 2,220 | 5.2% |

**Machine-readability:**
- **0 of 41,369** matched Item 2.02 8-Ks carry numeric XBRL (submissions `isXBRLNumeric`). Release exhibits are unstructured text.
- Whether the release contained the same revenue / NI values is **not verified**. It would need an unstructured exhibit-extraction system, which was not built (owner §10).

**Answer to the owner's question [I]:**
- For about 86% of quarters an earnings release **definitely** preceded the structured filing, usually by about 1 day (median) and by up to 17 days at the 90th percentile.
- An OF-A signal built from Data v3 is therefore **necessarily a delayed accounting-information signal relative to the first public disclosure**, though not necessarily relative to the **structured** values.
- Whether prices had already absorbed the information **cannot be established without returns**, which this audit does not study.

## 20. Point-in-time integrity evidence [V]

- **Coded PIT assertion:** every fact used at decision day D was filed before D. **0 violations in 120,028 stock-month checks.**
- **Unit tests** (`tests/test_lh_stage_c.py`):
  - `q_detail` equals the frozen `Facts.q_known`;
  - truncation (removing every fact filed after d leaves every value as known at d unchanged);
  - the cut-off (a 2022 filing is invisible);
  - YTD and Q4 derivation;
  - release matching and the disclosure categories;
  - session arithmetic;
  - outputs contain no post-2021 date.
- **Committed audits:** Data v3 PIT audit 0 (P14-CP2); Data v2.1 PIT 0, truncation and future-invariance (E801-01..04); SEC timing 96–99% day after filing (D187).
- **Can later values replace earlier ones before they are public?**
  - **SEC side:** no, by construction (§10 table, row 1 = legal recasts only).
  - **Vendor side:** the guard v3 / v2.1 restatement guards block versions carrying a later, not-yet-public value above 1.5% (1,018 blocked).
  - **Residual:** restatements of 1.5% or less pass (by design).
  - **No new issue was found.**

## 21. Survivorship and missingness risks [V / I]

**Input-complete share by group (U_NF stock-months):**

| Group | n | C1 | C2 | C3 | C5 |
|---|---|---|---|---|---|
| Stayers (eligible in 2021-12) | 99,530 | 78.1% | 74.6% | 90.7% | 46.1% |
| **Leavers** (left the universe before 2021-12) | 26,643 | **64.2%** | **58.2%** | 87.3% | 34.1% |
| Not newcomers | 114,561 | 79.0% | 74.9% | 93.0% | 45.0% |
| **Newcomers** (first 12 eligible months, first eligible after 2011-01) | 11,612 | **37.0%** | **34.0%** | 60.1% | 29.0% |
| Size tercile 1 (smallest, by SEC total assets) | 39,824 | 71.3% | 67.8% | 93.2% | 55.7% |
| Size tercile 3 (largest) | 39,781 | 85.4% | 80.3% | 96.0% | 32.7% |
| Amendment-only or late (> 90 days) filers | 9,183 | 73.3% | 68.3% | 92.1% | 47.7% |

**By FF12 sector:**
- C2: Energy 58.7%, Utilities 65.8%, Health 66.7%, Shops 71.9% vs Chemicals 82.8%.
- C5: Energy 3.4%, Utilities 8.0%, Telecom 8.4%, Other 23.1%.

**[I] Missing data are not random.**
- The 13-quarter requirement systematically excludes **recent entrants (IPOs, spin-offs)** and **firms that later leave the universe**: about 14–16 points less coverage, the survivorship-type direction.
- It also under-covers some sectors.
- An OF-A signal restricted to complete histories would tilt toward long-listed, surviving, larger firms. That tilt must be controlled (e.g. by sector, size and age) in any later signal test.
- C5 is structurally unusable for energy, utilities and telecom.

**Existing known limitations (committed):**
- residual survivorship gap 0.5–1.2% a year (D113);
- market-cap gaps repaired by the SEC method (D189);
- Gate K identity residual (D192);
- the Data v2.1 NEW_YEARS_MAPPING exception (D213);
- this audit's Data v1 denominator (§3).

## 22. Candidate-by-candidate feasibility matrix

The frozen rules (protocol §8) applied mechanically:

| Attribute | C1 SUE-NI | C2 SUE-REV | C3 price-scaled | C4-REV / C4-NI | C5 GP / assets | C6 dual |
|---|---|---|---|---|---|---|
| PIT correctness | PASS | PASS | UNKNOWN (market cap in-host only) | PASS | PASS | PASS |
| Input coverage 2013–2021 (min year) | 78.6% | 73.5% | 87.8% | 83.4% / 86.7% | 43.3% | 73.4% |
| Historical-depth sufficiency (≥ 70% each year 2013–21) | PASS | PASS | PASS | PASS | **FAIL** | PASS |
| Data timestamp quality | PASS | PASS | PASS | PASS | PASS | PASS |
| Earnings-release delay | E2 median 18 sessions (p90 27); release precedes filing in 86% | same | same | same | same | same |
| Quarterly-chain integrity (frozen label rule) | **FAIL** (14.4%) | **FAIL** (15.0%) | **FAIL** (8.3%) | **FAIL** (9.9% / 9.5%) | **FAIL** (10.9%) | **FAIL** (15.1%) |
| Restatement risk | NI recast in 21% of chains (pre-D); later restated 11%; guard v3 covers NI | Revenue 24% / 14%; guard v2.1 + v3 | NI as C1 | As C1 / C2 | GP guard v3; GP missing for half | Union of C1 and C2 |
| Look-ahead risk | Low: SEC side PIT by construction; vendor side guarded above 1.5%; ≤ 1.5% restatements pass | Low (same) | Market cap PIT in-host (`market_cap` PIT, D107; repaired D189); not verifiable offline | Low | Low | Low |
| Ability without purchase | YES | YES | CONDITIONAL (in-host input) | YES | YES | YES |
| Suitability (frozen) | **NOT FEASIBLE** | **NOT FEASIBLE** | NOT FEASIBLE | NOT FEASIBLE | NOT FEASIBLE | **NOT FEASIBLE** |
| Suitability ignoring only the chain-label criterion (counterfactual; **not adopted**) | FEASIBLE | FEASIBLE | CONDITIONAL | FEASIBLE (H029-related) | NOT FEASIBLE (depth) | FEASIBLE |

**Information timeliness (frozen rule):**
- 85.8% of events have an earlier release (≥ 50%), and the median E2 is **18 sessions**, under the provisional 20-session limit.
- So timeliness is **not** a MATERIAL DESIGN ISSUE under the provisional rule, **but only by 2 sessions**. Label: PROVISIONAL — OWNER REVIEW REQUIRED.

**No candidate is declared predictive or profitable.** No final formula is chosen.

## 23. Comparison with the provisional 70% floor

**PROVISIONAL FEASIBILITY THRESHOLD — OWNER REVIEW REQUIRED:** ≥ 70% of U_NF stock-months input-complete in each year 2013–2021.

| Floor | 60% | 65% | **70%** | 75% | 80% |
|---|---|---|---|---|---|
| C1 | ✔ | ✔ | **✔** | ✔ | ✘ |
| C2 | ✔ | ✔ | **✔** | ✘ | ✘ |
| C3 | ✔ | ✔ | **✔** | ✔ | ✔ |
| C4-REV, C4-NI | ✔ | ✔ | **✔** | ✔ | ✔ |
| C5 | ✘ | ✘ | **✘** | ✘ | ✘ |
| C6 | ✔ | ✔ | **✔** | ✘ | ✘ |

- C2 and C6 pass the floor narrowly: their minimum is 73.4–73.5%, in 2013.
- **2011–2012 fail for every 13-quarter candidate** (14–52%). This is outside the "after 2012" floor, but it shortens usable history to **2013–2021 (9 years)** for C1 / C2 / C6.

## 24. Feasibility classification

**Frozen protocol result: C — NOT FEASIBLE.**
- Every candidate fails the frozen quarterly-chain-integrity criterion.
- C5 also fails historical depth.
- C3's market cap is only verifiable in-host.

**Why this result needs owner judgement [I] (stated, not acted on):**
1. **The criterion was mis-specified by me.** It tests the fiscal-year-end *label*, which 52/53-week filers change by a few days each year. About 70% of flagged chains are such drift. Genuine fiscal-year changes normally break the 80–100-day chain rule and are excluded anyway (§8).
2. **Without that one criterion, under the other frozen criteria:**
   - C1, C2 and C6 are FEASIBLE;
   - timeliness is not material (provisional);
   - the identity, submissions and companyfacts evidence is sufficient (97–100%);
   - so the class would be **A — DATA FEASIBLE**.
3. **But a residual is unresolved.** 1.3% of 13-quarter chains carry a fiscal-year-end code shift of more than a month that is not quarter-aligned. It cannot be resolved offline and is above the frozen 1% limit.
4. **Other material issues stand regardless of the chain rule:**
   - only 9 years (2013–2021) of 13-quarter history;
   - non-random missingness against leavers and newcomers;
   - the earnings release precedes the structured filing in 86% of quarters, and its values are not machine-readable;
   - monthly reviews add a median 14 sessions;
   - surprises are relative to a time-series forecast, not market expectations.

**[I]** On the evidence as a whole, the honest description is closer to **B — CONDITIONALLY FEASIBLE**. Under the frozen protocol it is **C**.

**I do not reclassify.** Precedent for owner handling of a failed criterion recorded as written: D207 / D213 (NEW_YEARS_MAPPING) and D192 (Gate K).

## 25. What remains unknown about economic usefulness

**NOT TESTED.** This audit shows only that the inputs exist, their timing, and their gaps. It cannot show whether:
- a time-series surprise predicts returns in ≥ $2B US stocks after 2013;
- the release-to-filing and monthly-review delays (median 18 sessions) remove the effect;
- the effect survives costs, or differs from momentum, profitability and growth exposures (RM2 §9).

The literature's large-cap prior is low (Martineau 2022: drift absent in large stocks since 2006; RM2 §8). Answering any of these needs Stage B (method validation) and, after that, an approved Stage D. Neither is authorised.

## 26. Required next owner decision

Choose one:

1. **Accept C — NOT FEASIBLE as recorded** and stop OF-A (C1–C6) with existing data.
2. **Accept the criterion as mis-specified (an owner-approved exception; the frozen FAIL stays recorded)** and treat Stage C as **B — CONDITIONALLY FEASIBLE**, with these blockers carried into any pre-registration:
   - a fiscal-calendar rule defined on period ends;
   - exclusion or flagging of the 1.3% unexplained chains;
   - a vintage choice;
   - controls for missingness (sector, size, firm age);
   - history 2013–2021;
   - C5 dropped;
   - C3 only in-host.

   Stage B (synthetic validation) would then be the next step to approve separately, together with the review frequency question (monthly vs. filing-event timing; §17).
3. **Request a resolution study** of the 1.3% unexplained fiscal-year-end shifts (offline SEC metadata only), before deciding between 1 and 2.

**Recommendation [I]:** option 3 if the owner wants an evidence-based resolution (cheap, offline); otherwise option 2, given that the failure comes from a measurement design error rather than from the data. **Nothing proceeds automatically.**

## 27. Confirmation: no return or performance analysis

No price, stock return, SPY return, benchmark, wealth, CAGR, Sharpe or predictive relationship was computed or read. No surprise value, standard deviation, percentile or ranking of any company was computed. No model was trained. No QuantConnect run was started (0 network requests of any kind). H028 was not run.

## 28. Confirmation: Holdout sealed

- No 2022-01-01 → 2026-08-31 data entered any computation; every SEC row filed after 2021-12-31 was dropped at load.
- The one disclosed format-inspection print of two 2026 metadata rows (§2) entered nothing.
- `HOLDOUT_UNLOCK.md` does not exist.
- No data were purchased.

---

**Files:**
- `research/longhorizon/stage_c/LH_StageC_protocol.md` (frozen);
- `LH_StageC_audit.py` / `.json`;
- `LH_StageC_fye_diagnostic.py` / `.json` (post-hoc);
- `tests/test_lh_stage_c.py`.
