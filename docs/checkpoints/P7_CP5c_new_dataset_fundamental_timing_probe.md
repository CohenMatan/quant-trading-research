# P7-CP5c — New Dataset Fundamental-Timing Probe

**Date:** 2026-10-10. **Owner decision:** D184 (option C, step 1 only). **Result decision:** D185. **Status:** STOPPED awaiting the owner.

## Short answer

The question was whether we can establish, point in time and independently verifiably, when each fundamental report became public on QuantConnect's new dataset.

**Answer: PARTIAL, and not enough for Score v1. Recommendation: NO-GO for Data Infrastructure v2.**

1. **QuantConnect's own timing cannot be used.**
   - The new default dataset (LEAN 18178) leaves most reports without a usable filing date: timing unknown in 31,538 reports, against 608 on the old build.
   - QuantConnect documents that for statements before 2013 the new feeds "lack actual filing dates" and apply "a nominal 45-day delay" where no old date exists. SEC data show 87.5% of 10-Ks are filed more than 45 days after period end, so that rule would expose most annual reports before they were public.
   - **QuantConnect now forbids exactly the verification that would be needed.** Its build step rejected our probe: "Data cannot be exported for any purposes, including data probing or validation". It had already stopped the previous attempt mid-run.
   - So the vendor's dates cannot be independently verified within the vendor's terms.
2. **SEC EDGAR is a trustworthy source** (filing date plus values as first filed, public). But the full point-in-time coverage it supports is too low:
   - with the frozen rules, only **24% of the H022 fundamental population passes H2** (2011: 1%; 2013–2017: 28–32%), against 75% on the old data;
   - even an un-approved gross-profit derivation reaches only **49%**.
3. **Restatements make any "SEC date + current vendor value" shortcut unsafe.** 12–16% of revenue periods are later re-reported with a different value. Morningstar's value vintage can no longer be checked inside QuantConnect.

**Stop conditions met** (owner item 20): no trustworthy timing source for the vendor's values; values cannot be tied to their vintage; coverage too low for Score v1; any workaround needs assumptions we cannot validate.

---

## 1. Actual LEAN build used

| Run | Purpose | LEAN build | Outcome |
|---|---|---|---|
| E993-03 (D183) | X993 score export, default build | **18178** | completed (aggregate store statistics only) |
| E994-03 (D183) | H022 canary, default build | **18178** | crashed (no date with ≥ 20 population stocks) |
| E995-01 | X995 probe | — | failed at upload (new 50-file project limit) |
| E995-03 | X995 probe | — | failed at upload (stale files from E995-01; runner fixed) |
| E995-04 | X995 probe | **18178** | stopped by QuantConnect at simulated 2009-10-08 ("Deleted by request"; no error from our code) |
| E995-05 | X995 probe | — | **rejected at build by QuantConnect's compliance check: "Data cannot be exported for any purposes, including data probing or validation"** |
| E995-02 | truncation repeat | — | never run (probing is prohibited) |

Every run records the build actually used. **The partial E995-04 output is not analysed anywhere in this report**, out of respect for the vendor's terms (see section 31).

## 2. Schema inspected

The in-platform schema scan could not run: X995 was stopped or rejected (section 1). Instead, the schema was read from the **public LEAN source**, which QuantConnect says generates the data tree. These fields still exist, all as multi-period fields with windows 1M / 2M / 3M / 6M / 9M / 12M:

- `EarningReports.PeriodEndingDate` (Morningstar DataId 20001);
- `EarningReports.FileDate` (20002: "Specific date on which a company released its filing to the public");
- `EarningReports.AccessionNumber` (20003), `EarningReports.FormType`, `EarningReports.PeriodType`;
- the same five fields under `FinancialStatements`;
- `FinancialStatements.BalanceSheet.BSFileDate`.

**No timing field is retired** (no `NotSupportedException` member). The old-dataset schema of every object was recorded in P2-CP4 (`research/phase2/fundamental_audit/schema_probe_2015-02.txt`).

## 3. Candidate timing fields

- earning-report and financial-statement period end, file date, accession number, form type and period type (every window);
- balance-sheet file date;
- the security's first appearance in the data stream, which is implicit in a backtest.

## 4. Field semantics (vendor documentation; not verifiable in-platform)

- **Ratio, growth, per-share and average properties** are now dated by the filing date of the statement they come from, a median of 63 days later than the old feed.
- **Statements before 2013:** "the new feeds lack actual filing dates. Dates from the previous dataset are kept where available. Otherwise, a nominal 45-day delay is applied."
- **Restatements:** older documentation says values are loaded "As Original Reported". The migration posts say nothing on restatements or vintages.

## 5–8. Old-vs-new comparison, sample, reports inspected, 10-Q / 10-K coverage

- **Method and sample (fixed before any probe result, D184, commit 49649d6):**
  - the P2-CP6 X971 SEC sample: 406 companies, seed 20261004, fixed on 2026-10-01; its old-build report-level record is E971-02;
  - plus the pre-registered supplementary sample S2 of 74 companies (`research/phase7/cp5c/sample_s2.py`, salt "P7CP5c-S2"): 44 that became H2 only after the migration (4 per FF12 group), 10 continuous, 10 that grew into the universe, 10 SEC-repaired.
- **Reports inspected on the new build: none.** The probe was rejected (section 1).
- **Old-vs-new at aggregate level** (E993-02 vs E993-03, the same frozen X993 code, store counters only):
  - new reports observed 153,871 → 140,033;
  - timing unknown 608 → 31,538;
  - estimated (+90-day rule) 12,714 → 4,320;
  - usable revenue baselines 78,633 → 2,269;
  - H2 on 25.1% → 98.8% of non-financial eligible stock-months.
- The pattern (estimated dates fell, unknown timing rose) means the new feed supplies most reports **without a valid file date** rather than with a dated or nominal one. Which window or field now carries the date cannot be checked in-platform.

## 9–13. SEC comparison, early dates, earnings releases, value consistency

Not performed on vendor data, because QuantConnect prohibits the in-platform comparison (section 1). What public data alone establishes:

- **SEC filing delays** (1,512 universe companies, 2009–2017, `sec_only_coverage.json`):

  | Form | Filings | Median | 90th pct | 99th pct | Max | > 45 days | > 90 days |
  |---|---|---|---|---|---|---|---|
  | 10-Q | 28,790 | 35 d | 40 d | 68 d | 991 d | 1.7% | 0.7% |
  | 10-K | 9,786 | 56 d | 61 d | 198 d | 846 d | **87.5%** | 1.8% |

- **Earnings releases** (item 10): 8-K Item 2.02 releases often precede the 10-Q / 10-K. However, the press-release exhibits are not XBRL-tagged in 2010–2017, so no specific Score v1 value can be verified as public on the release date. The release date is **not usable**. The filing date is conservative (equal or later).
- **Value consistency** (item 13): see section 21.

## 14–16. Revision, truncation and point-in-time invariance tests

- **On vendor data:** not possible (prohibited). Vendor claims ("As Original Reported") remain unverified.
- **On the SEC-only path (offline):** values are as first filed by construction (`sec_pit.build_company`). Fed in filing order into the frozen PIT store, a restated value is invisible before its own filing date, and the store state at t does not depend on later filings. Test: `tests/test_p7_cp5c_probe.py::test_sec_only_store_is_vintage_correct_and_truncation_invariant`.

## 17–19. SEC-based timing feasibility

- **Source:** SEC EDGAR submissions (filing date, form, accession, report date) and XBRL company facts (every fact with the accession and filing date that reported it). Public and free.
- **Existing coverage:**
  - identity v2 maps **4,391 securities** to SEC-dated CIKs (successors handled by dated rows);
  - 1,512 securities form the non-financial eligible universe of 2011–2017, and only 13 lack a CIK (0.7% of stock-months);
  - all company facts are already cached (1.1 GB, outside Git; 13 new requests).
- **Expansion, cost and runtime:** $0; ≤ 8 requests a second; the offline build takes about 25 minutes.
- **Packing constraint:** the 495-security correction table already takes 19 project files. A universe-wide SEC table (about 1,500 companies) would exceed QuantConnect's new **50-file project limit** unless it is compacted or uploaded to the Object Store (read inside backtests; export remains blocked).
- **Remaining limit: history.** XBRL detail tagging phased in during 2009–2011, so True TTM plus a 12-month baseline (about seven quarters of tagged history) is rarely available in 2011.

## 20. Revenue True-TTM feasibility

- SEC-only revenue True TTM (four consecutive quarters, reconciled to the fiscal year) is available for **≈ 74%** of non-financial eligible stock-months.
- Values and dates come from the same filing (same vintage), so the combination is point-in-time safe.
- The binding gaps are 2011 (XBRL history) and the other score inputs (section 23).

## 21. Restatement-vintage risk

From the SEC versions of 480 sample companies' periods, 2009–2017 (`restatement_vintages.json`), the share of periods that a **later** filing re-reports with a different value:

| Field | Differs > 0.5% | Differs > 5% |
|---|---|---|
| Revenue, quarter | 12.5% | 6.7% |
| Revenue, fiscal year | 15.7% | 8.9% |
| Net income, quarter | 6.7% | 4.1% |
| Operating cash flow, fiscal year | 15.2% | 5.0% |
| Total assets | 3.1% | 0.3% |
| Equity | 2.6% | 1.0% |

**Consequence:** attaching SEC filing dates to vendor values is unsafe unless each vendor value is shown to be the first-filed vintage. That check is exactly what QuantConnect now forbids. **This is a stop condition for every "vendor value + SEC date" method.**

## 22. Estimated-date fallback

**Not defensible:**
- a +45-day rule would expose 87.5% of 10-Ks early;
- even the old +90-day rule is early for 1.8% of 10-Ks and 0.7% of 10-Qs (99th percentile of 10-K delays: 198 days; maximum 846 days).

A conservative fallback would have to exceed about 200 days, which makes the data stale under the frozen 200-day freshness rule anyway. **Recommendation: no estimated-date fallback in any v2.**

## 23–25. Coverage per viable method (non-financial eligible stock-months, 2011-01 → 2017-12)

| Method | Stock-months passing H2 (frozen Score v1 inputs) |
|---|---|
| Old Morningstar (18131, data v1) | **74.9%** of 70,804 |
| New Morningstar (18178), frozen layer | **1.2%** of 57,502 |
| SEC-only, frozen rules (`sec_only_coverage.py`) | **24.3%** of 57,502 (2011 1.3%, 2012 13.9%, 2013 28.2%, 2014 28.1%, 2015 28.5%, 2016 31.6%, 2017 30.1%) |
| SEC-only + gross profit derived as revenue − cost of revenue (upper bound; NOT a frozen rule) | **49.3%** |

- **Why SEC-only H2 fails** (first missing input):
  - gross profit, 21,929 rows (companies that do not tag `GrossProfit`; Morningstar derives it);
  - revenue True TTM, 14,430 (quarter chain broken);
  - revenue baseline, 3,776;
  - operating cash flow, 1,903;
  - net income, 1,059.
- **Revenue baseline:**
  - new vendor: 2,269 usable baselines (was 78,633);
  - SEC-only: the baseline is the binding input for 3,776 otherwise complete rows; 2011 has almost none.

## 26. Method comparison

| Method | PIT safety | Independent verification | Coverage | Complexity | Recommendation |
|---|---|---|---|---|---|
| New QuantConnect / Morningstar file-date fields | Unknown; pre-2013 nominal 45-day dates are unsafe | **Prohibited** in-platform | ≈ 1% (frozen layer) | — | **Reject** |
| Other Morningstar metadata (accession, form, period type) | Unknown | **Prohibited** | Unknown | — | **Reject** |
| SEC filing dates + vendor values | Unsafe unless the vintage is proven; 12–16% of revenue periods are restated later | Vintage check prohibited | — | Medium | **Reject** (restatement stop condition) |
| Full SEC fundamental reconstruction | **Safe** (filing date + as first filed) | Yes, public data, offline | 24% (frozen rules); ≤ 49% with GP derivation; ≈ 0% in 2011 | High (extraction rules, packing, new data version) | Not for Score v1 now; a possible future research base (see 27) |
| Conservative estimated delay | Unsafe below ~200 days; useless above | No | — | Low | **Reject** |

## 27. Is Data Infrastructure v2 technically feasible?

- **Not on the new QuantConnect / Morningstar fundamentals**, under the vendor's terms.
- **An SEC-only v2 is PIT-feasible but not adequate for Score v1** as frozen: 24% coverage, about 0% in 2011. Reaching v1-like coverage would need new extraction rules (gross-profit derivation, broken-quarter repair), which are new owner-approved definitions on a different data version, plus compaction or Object Store packing. The 2011–2012 shortfall is structural (XBRL history).
- The universe itself also changed (−18% eligible; vendor market caps). That part was not investigable in-platform.

## 28. Proposed v2 rule

**None.** If the owner ever wants an SEC-only fundamentals base, it needs its own design checkpoint, at minimum:
- timing = SEC filing date + 1 day;
- values as first filed;
- no estimated dates;
- a new, pre-registered score definition (not Score v1 retro-fitted).

## 29. What v2 would regenerate

Everything downstream of the data:
- universe membership;
- fundamental availability and H2;
- Score v1 distributions and revenue growth;
- candidate counts;
- breadth and regime (eligible-set based);
- P7-CP3R mechanics and the H022 population;
- the synthetic power study (built on E993-02 tables);
- the 5,000 null worlds and **c_IC**.

**The old null and c_IC = 2.390976216956 cannot be reused on any changed panel.** They remain valid records of data v1 / LEAN 18131, together with E993-02, P7-CP3R, P7-CP4 and P7-CP5a. Nothing in v1 was overwritten.

## 30. Cost and runtime

- **This probe:** $0. Five QuantConnect launch attempts, none producing analysable probe output; offline SEC work ≈ 30 minutes; 13 new SEC requests.
- **A future SEC-only v2:** about 10 QuantConnect runs (export, canary, five null batches, the real run, re-runs), several sessions of engineering, and Object Store or packing work.

## 31–36. Confirmations

- **31.** No future return was analysed.
- **32.** No H022 statistic was computed (no IC, gate, quintile or 80+ figure).
- **33.** No portfolio was run (0 orders everywhere).
- **34.** 2018–2021 untouched for research. SEC version lists include later filings' values for pre-2018 periods; these were used only for the restatement-frequency count.
- **35.** Holdout untouched.
- **36.** Nothing purchased.

**Vendor terms.** E995-04 delivered some per-report records from 2009 before QuantConnect stopped it. They were **not used**. Whether to purge that payload from the repository (`experiments/E995-04/result.json`) is an owner decision (item 38).

**Other platform changes found** (recorded in CLAUDE.md):
- 50-file project limit;
- compile-time compliance review that forbids data probing / validation exports;
- the runner now deletes stale project files before uploading.

## 37. Recommendation

**NO-GO — no trustworthy PIT timing source was found** for the new QuantConnect fundamental data.

The only trustworthy source (SEC EDGAR, as first filed) covers too little of the population (24%; ~0% in 2011) for the frozen Score v1. Fundamentals-based Phase 7 should stop rather than introduce look-ahead.

## 38. Owner decisions needed

1. **Close H022** as "not evaluable on the available infrastructure". It stays preserved as frozen; c_IC is never used. Alternatively, keep it dormant.
2. **Fundamentals-based research going forward:**
   - (a) stop it; or
   - (b) authorise a separate design checkpoint for an SEC-only fundamentals base. This is a new data version and a new pre-registered score; it will not rescue Score v1.
3. **Vendor-terms hygiene:** whether to purge E995-04's partial payload from the repository. A history rewrite is irreversible; my recommendation is to redact it from the current tree and keep the registry row.
4. **Programme risk acknowledgement.** QuantConnect's new compliance review may also challenge future result exports (score tables, statistics). The research methodology relies on exporting derived statistics. Confirm whether to continue on QuantConnect at all.

STOP. No v2 implementation, no Score v1 change, no P7-CP3R re-run, no H022 canary / null / c_IC / real run, no portfolio.
