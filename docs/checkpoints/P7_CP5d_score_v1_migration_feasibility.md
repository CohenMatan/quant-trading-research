# P7-CP5d — Score v1 Migration Feasibility on New QuantConnect Data

**Date:** 2026-10-10. **Decisions:** D186 (owner request), D187. **Status:** STOPPED awaiting the owner.

## Short answer

The owner asked whether the frozen Score v1 can run safely on QuantConnect's new Morningstar feed. The idea: date each company report by the day it first appears in the historical stream ("first seen"), instead of by the vendor's file date.

I built an in-cloud prototype (X996) and ran it three times on QuantConnect's default build 18178. Vendor values never left QuantConnect: only counts, distributions and SHA-256 digests did. QuantConnect accepted and completed all three runs.

**What works — the fundamentals timing is better than expected:**
- **The stream is point-in-time in timing.**
  - Of 41,312 company reports matched to an SEC filing, 96–99% are first seen exactly one day after the SEC filing date.
  - This holds before 2013 as well (95.7% of 10-Qs, 96.8% of 10-Ks).
  - That is despite the vendor's file-date field, which is unusable for most reports.
- **It is not backfilled with today's values.**
  - Some periods were later restated in SEC filings, but the restatement had not yet been filed on the day the report was first seen.
  - For those periods, 88% of revenue values and 99% of total-assets values first seen are the originally filed figures.
  - Only 0.27% of all first-seen revenue values equal a figure that was filed only later. Data v1's restatement guard blocked a similar share (0.3%).
- **Truncation invariance: PASS.** A run ending 2013-12-31 and a run ending 2017-12-31 have identical digests up to 2013-12-31 for:
  - the report ledger;
  - the eligible universe;
  - all 35 shared reviews' score tables.
- **Determinism: PASS.** Two independent full runs (M1 and M2) observed an identical stream in every year 2008–2017.
- **Coverage with M1 is comparable to data v1.**
  - About 486 fully scored stocks a month (min 291), vs data v1's 479 (min 196).
  - About 5.9 stocks at 80+ a month (data v1: 7.0).

**What fails — the universe:**
- The new feed loses about 18% of data v1's eligible stock-months. About 85% of those losses are securities whose market cap is **missing** on the new feed.
- The lost securities are mostly companies that **later disappear**:
  - only 50% of the lost stock-months belong to securities still in the universe at end-2017;
  - for the retained stock-months the figure is 92%.
- **This is a survivorship bias in universe membership.** The universe as delivered is not point-in-time safe (requirement 6).
- There is a second weakness:
  - M1 makes 277 reports usable before their SEC filing (0.67%); 46 of these coincide with no 8-K earnings release.
  - The SEC gate (M2) removes all of them.
  - But M2 then leaves 2011 almost empty (about 11 scorable stocks a month), because our SEC identity table only starts with each company's first XBRL filing.

**NO-GO — Score v1 cannot be migrated safely on the available QuantConnect infrastructure.**
- Failed requirement: **6 — universe membership is not PIT-safe on the new feed.**
- Partly failed: 5 and 7 cannot both be met before 2013 (see section 30).

No return, IC, gate or H022 statistic was computed.

## 1. Actual LEAN builds

| Run | What | Build | Outcome |
|---|---|---|---|
| E996-01 | X996 M1, 2011-01-03 → 2017-12-31 (warm-up 2008-07-01) | **18178** (default; recorded) | completed, 0 orders, 616 s |
| E996-02 | X996 M1, truncated at 2013-12-31 | **18178** | completed, 0 orders |
| E996-03 | X996 M2, full window | **18178** | completed, 0 orders, 560 s |

- One extra attempt of E996-02 was refused locally by the runner before upload: an untracked file left the working tree dirty. Nothing reached QuantConnect.
- All three runs passed QuantConnect's build-time compliance review and ran to completion. None was stopped ("Deleted by request").

## 2–6. Score v1 dependency map and migration classes

Classes:
- **A** — unchanged / mechanically equivalent;
- **B** — values or history changed;
- **C** — timing semantics changed;
- **D** — calculation changed;
- **E** — renamed or moved;
- **F** — retired;
- **G** — unknown / needs testing.

Evidence comes from:
- the public LEAN source (fetched 2026-10-10);
- QuantConnect's dataset documentation;
- E993-02 vs E993-03;
- X996 (this checkpoint).

| Score v1 use | Internal field | QuantConnect / Morningstar path (window) | History / baseline | Source | Exists on new feed | Class | Evidence |
|---|---|---|---|---|---|---|---|
| Profitability (GP/A) | gross profit True TTM | `financial_statements.income_statement.gross_profit` (`three_months` quarters + `twelve_months` FY check) | 4 quarters | fundamentals | yes | **C** (+B) | Timing: vendor file date unusable (P7-CP5b); first seen = SEC + 1 in 96–99%. Values: vendor restandardised (docs) |
| Profitability, Balance sheet, Cash conversion (÷ assets) | total assets | `financial_statements.balance_sheet.total_assets` (`three_months`) | latest report | fundamentals | yes | **C** | 98.9% of compared first-seen values = SEC first-filed |
| Balance sheet, H7 | stockholders' equity | `balance_sheet.stockholders_equity` (`three_months`) | latest report | fundamentals | yes | **C** (G for values) | Not SEC-vintage-tested in-cloud (only revenue and assets were) |
| Cash conversion, H7 | net income True TTM | `income_statement.net_income` (3M, 12M) | 4 quarters | fundamentals | yes | **C** (G for values) | Same |
| Cash conversion, H7 | operating cash flow True TTM | `cash_flow_statement.operating_cash_flow` (3M, 12M) | 4 quarters | fundamentals | yes | **C** (G for values) | Same |
| Growth, H2 | revenue True TTM and its 12-month-old baseline | `income_statement.total_revenue` (3M, 12M) | 4 quarters + the value recorded 12 months earlier | fundamentals | yes | **C** | 91.4% of compared first-seen quarterly values = SEC first-filed; the rest mostly vendor standardisation |
| Report identity | period end | `earning_reports.period_ending_date.three_months` | — | fundamentals | yes | **A/G** | Present on every observed report (459k company-days had no current report at all) |
| Report timing | file date | `earning_reports.file_date.three_months` | — | fundamentals | yes, but **unusable** | **C** | In 9,819 matched reports it is before the period end; otherwise = SEC date (31,007 of 31,493 dated) |
| Quarantine | accession number (year only) | `earning_reports.accession_number` | — | fundamentals | yes | **A** | 0 future-year accessions seen |
| Universe | market cap | `market_cap` | daily | fundamentals | yes, but **missing for many securities** | **B** | About 85% of the 18% universe loss; survivorship-biased (section 24) |
| Universe | price, dollar volume (ADV20) | `price`, `dollar_volume` | 20 days | coarse | yes | **A** | No old-member loss attributed to price or ADV |
| Universe | US common, depositary receipt, primary share, country, LP/LLC flags, exchange | `security_reference.*`, `company_reference.*` | daily | fundamentals | yes | **A** (current-status, as before) | 12–36 old-member stock-reviews a year lost to "not common type" |
| Universe | has fundamentals | `has_fundamental_data` | daily | fundamentals | yes | **B** | 42–445 old-member stock-reviews a year lost (fewer later) |
| H1, FF12 sector, Sector layer | SIC | SEC (identity v2, `qr_industry`), not Morningstar | PIT rows | SEC | n/a | **A** | Own data |
| Share class, baseline check | CIK | SEC identity v2 dated rows | PIT rows | SEC | n/a | **A** | Own data |
| Trend, H6, breadth, SPY regime | split-adjusted close | RAW daily bars × QuantConnect split feed (SCALED_RAW verifies) | 221 bars | prices | yes | **A/G** | Not part of the Morningstar change; slice check 168/168 exact; not compared value by value with 18131 (that would need a price export) |
| Momentum, volatility | total-return close | RAW × split × dividend feeds | 253 / 61 bars | prices | yes | **A/G** | As above |
| H4 | split / distribution events | Split, Dividend history | — | prices | yes | **A** | 634 H4 rows (same mechanism) |
| H3, H5 | bar counts / staleness | prices | — | prices | yes | **A** | H5 = 0 |
| SEC-repaired securities | SEC filings + SEC cover-page shares | own SEC table (D111/D113) | — | SEC | n/a | **A** | 8,127 SEC feeds, as in E993-03 |

- **Unchanged (A):**
  - SEC SIC / CIK;
  - prices and corporate-action feeds (G for value identity across builds);
  - price / ADV filters and reference flags;
  - accession-year quarantine.
- **Changed:**
  - **all six fundamental values: timing (C)** — the vendor file date can no longer date them; first-seen can (sections 9–19);
  - **market cap (B): missing history** for a survivorship-biased subset.
- **Unavailable (F):** none. Every Score v1 property still exists with its 3M/12M windows (LEAN source). The data are also observed in-run.

**Conceptually, Score v1 can still be computed (requirement 1 passes). The failure is in what the universe contains, not in what the score reads.**

## 7–8. First-seen architecture and in-cloud ledger (X996 v1.0)

**The rule.** The frozen X993 v1.1 pipeline is unchanged, except for the data-delivery rule:
- **M1:** a report (security, period end) is usable from the first selection day on which it appears in the stream.
- **M2:** usable from max(first seen, SEC original 10-Q/10-K filing date + 1 day). A report with no matched SEC filing is never used.

**The ledger.** For each security and period it keeps:
- first-seen day;
- a fingerprint of the ten Score v1 report fields;
- the revision count.

**Revisions.** Every week the current report's ten fields are re-read. A change enters the PIT store as an amendment, usable only from its own first-seen day. The value captured at first sight is never rewritten.

**Rules that are gone:**
- the vendor file date;
- the +90-day estimated-date rule;
- the data-v1 holds, blocks and releases (they are keyed to old vendor reports).

Kept unchanged: quarantine, 200-day freshness, True TTM, the store-wide revenue baseline and its life / CIK / PIT checks, and every Score v1 rule.

**Everything stays inside QuantConnect.** That includes the SEC reference table (`p5d_ref`): public SEC data plus our own E993-02 membership, fixed before any run (commit fc49027).

**Outputs:**
- counts and histograms;
- SHA-256 digests (ledger by year, eligible set by year, every review's score rows).

Tests: `tests/test_p7_cp5d_ledger.py` — synthetic M1/M2, timing, earnings-release explanation, vintage contamination detection, revisions, truncation invariance, aggregate-only output, file limit.

## 9. Truncation invariance — PASS

E996-02 (end 2013-12-31) vs E996-01 (end 2017-12-31):

| Comparison | Result |
|---|---|
| Ledger digest, all events to 2013-12-31 | **identical** |
| Ledger digests by year (2008–2013) | **identical (6/6)** |
| Eligible-universe digest (security ids + market caps, daily) to 2013-12-31 | **identical** |
| Score rows of every review in both runs (2011-01 → 2013-11) | **35 of 35 identical** |

- The truncated run cannot hold the 2013-12-31 review: its selection day is after its end date.
- Its in-host calendar check flagged 35 reviews against 36 expected. That is a check artefact:
  - history requests end at midnight, so the panel's last row was 2013-12-30, which the check counted as a month-end;
  - the 35 reviews equal the full run's first 35 exactly.

## 10. Determinism — PASS

E996-01 (M1) and E996-03 (M2) are independent full runs. They observed exactly the same ledger and the same eligible set in every year 2008–2017 (10/10 digests each).

The stream itself is deterministic within the current data snapshot.

## 11. Restatement-vintage result — PASS with a small residual

For every first-seen report matched to an SEC period, the vendor value at first sight was compared in-cloud with:
- the SEC value as first filed;
- the first later value that differs by more than 0.5% (with its filing date).

The comparison tolerance is 0.5%.

| | Quarterly revenue | Total assets |
|---|---|---|
| Compared (SEC reference present, vendor value present) | 34,289 | 41,039 |
| = SEC first-filed (incl. "both") | 31,343 (**91.4%**) | 40,604 (**98.9%**) |
| = a LATER SEC value that was already public | 21 | 3 |
| = a LATER SEC value **not yet filed** on the day seen | **93 (0.27%)** | **13 (0.03%)** |
| = neither | 2,832 (8.3%) | 419 (1.0%) |
| **Periods restated later, restatement still in the future when seen** | 3,914 | 1,210 |
| … of which = original value | **3,452 (88.2%)** | **1,192 (98.5%)** |
| … of which = the future restated value | **93 (2.4%)** | **13 (1.1%)** |

- **If the feed had been backfilled with today's (restated) values, the restated value would dominate among restated periods. It does not.** The historical stream is a vintage stream.
- Revisions inside the stream are rare: 450 in 131,113 reports. They do not change the past (section 9).
- **Residual:** 106 first-seen values (0.26% of reports) equal a figure first published later. Two possible causes:
  - genuine look-ahead;
  - vendor standardisation that happens to equal the later presentation.

  Distinguishing them would need an export of report-level values, which QuantConnect prohibits. **Not verifiable report by report.** Data v1 had the same order of risk (its SEC restatement guard blocked 0.3%).
- **"Neither" (8.3% of revenue)** is the vendor's revenue standardisation (excise taxes, gross/net). It is consistent with the data-v1 field validation (D113). It is not a timing problem.
- **3,039 revenue values (9%)** equal the SEC first-filed value "before" its SEC date. These are almost all fourth quarters:
  - 11.5% of SEC quarterly revenue values are first tagged only as comparatives a year later (`ref_first_filed_lag.py`; total assets 0.12%);
  - the figure was nevertheless derivable from the 10-K (fiscal year minus nine months).

  Total assets (no such artefact) shows 223 — the same order as the 277 genuinely early reports.

## 12–13. SEC comparison methodology and sample

- **Complete populations, no sample.**
  - Every SEC periodic filing (10-K / 10-Q / 10-KT and amendments; period end 2008-06-30 → 2017-12-31) of every SEC registrant mapped to a security eligible at any review under E993-02 or E993-03. That is 1,903 registrants and 49,351 filings.
  - SEC quarterly-revenue and total-assets vintages for every such period (88,200 values; 6,059 later differing).
  - Every 8-K Item 2.02 earnings release (Event Data v1; 51,360).
  - Fixed and committed before any run (fc49027, `build_x996_ref.py`).
- **Matching:**
  - security → SEC CIK through identity v2's dated rows (never Morningstar's current-status CIK);
  - vendor period end ↔ SEC period end within 6 days;
  - the original filing is the earliest 10-Q / 10-K for that period (amendment-only periods counted separately: 214).
- **Measure:** first-seen day − original SEC filing day.
- **Censoring:** reports already present on the first day of the run, or on a security's first day in the feed, are excluded (4,743).
- **Unmapped:**
  - 66,406 reports with no SEC identity row at the time — mostly companies never in our universe;
  - 18,650 with no matching SEC period.

## 14–17. Timing summaries (M1 first-seen − SEC original filing)

| Form | Era | Reports | First seen on/before the SEC filing | Exactly the next day | ≤ 5 days after | > 90 days after |
|---|---|---|---|---|---|---|
| 10-Q | 2009–2012 | 9,995 | **134 (1.34%)** | 95.67% | 98.02% | 185 |
| 10-Q | 2013–2017 | 21,453 | **48 (0.22%)** | 99.33% | 99.74% | 9 |
| 10-K | 2009–2012 | 2,725 | **67 (2.46%)** | 96.81% | 99.71% | 3 |
| 10-K | 2013–2017 | 7,139 | **28 (0.39%)** | 98.89% | 99.62% | 8 |

Early share by filing year:

| Year | Early share |
|---|---|
| 2009 | 0.65% |
| 2010 | 1.96% |
| 2011 | 1.84% |
| 2012 | 1.29% |
| 2013 | 0.37% |
| 2014 | 0.25% |
| 2015 | 0.33% |
| 2016 | 0.15% |
| 2017 | 0.24% |

Late appearance is conservative, not a leak. The 153 reports seen more than 90 days late in 2010 are reports that reached the feed late.

- **Pre-2013 (item 16).** QuantConnect documents nominal 45-day file dates before 2013. Even so, the stream makes 95.7% of 10-Qs and 96.8% of 10-Ks visible exactly the day after the real SEC filing. Streaming availability is far safer than the vendor's file date.

  The residual early share before 2013 (1.3–2.5%) is about six times the 2013+ share.
- **2013+ (item 17).** 99% next-day; early ≤ 0.4%.

## 18–19. Early-first-seen cases and earnings releases

277 reports were first seen on or before their SEC filing day (0.67% of 41,312).

| | Coincide with an 8-K earnings release between period end and first-seen | No earnings release |
|---|---|---|
| 10-Q 2009–2012 | 119 | 15 |
| 10-Q 2013–2017 | 33 | 15 |
| 10-K 2009–2012 | 59 | 8 |
| 10-K 2013–2017 | 20 | 8 |
| **Total** | **231** | **46 (0.11%)** |

- Most early 10-Ks are 6–30 days early, after the earnings press release. The vendor appears to load press-release figures before the 10-K.
- Under the owner's rule (section 13 of D186), an earnings release on the same dates does not prove that the **specific** values were public. Checking that would need the release figures against the vendor values, report by report — prohibited in-platform.
- **So all 277 are treated as not verified safe.** The 46 with no release at all are unexplained early availability.

## 20–23. Candidate architectures

| | PIT timing | Validation | Coverage (non-financial eligible stock-months passing H2) | Verdict |
|---|---|---|---|---|
| **M1** first seen | 0.67% of matched reports usable before the SEC filing (46 unexplained); unmatched reports not validated | Timing validated for matched reports | **71.5%** (2011 57.6%, 2012 58.8%, 2013 60.6%, 2014 74.2%, 2015 79.8%, 2016 81.9%, 2017 78.9%) | Not acceptable alone: early availability before 2013 |
| **M2** first seen + SEC gate | No report before its SEC filing + 1 (277 delayed; 90,183 unmapped reports never used) | Every used report validated | **57.9%** (2011 **2.0%**, 2012 23.3%, 2013 52.3%, 2014 70.1%, 2015 76.3%, 2016 79.7%, 2017 76.8%) | Safe timing, but 2011–2012 nearly empty |
| **M3** hybrid (assessed only) | Vendor value where SEC-verified, else SEC-only value | Mixed | ≥ M2 | **Not recommended.** It mixes vendor and SEC values in one score (different revenue and gross-profit definitions; P7-CP5c: SEC-only 24% coverage, gross profit often untagged). It changes Score semantics by source. |

- **Why M2 collapses in 2011–2012:** our SEC identity rows start at each company's first XBRL filing (2009–2011 phase-in). Earlier vendor reports cannot be mapped, so the True-TTM chains and 12-month baselines start late.
- Backdating CIKs would remove the collapse. But it is an untested identity assumption, and the owner's rules exclude loosening to restore coverage.
- **Recommended timing architecture, if the universe problem were solved: M2.** It is the only variant that meets requirement 5. The research window would have to start in 2013 for full coverage, which is an owner decision.

For comparison, data v1 (E993-02, LEAN 18131) passed H2 on 74.9% of non-financial stock-months. The frozen layer on the new build passes on 1.2%.

## 24–25. Universe migration and PIT universe safety — FAIL

Why E993-02 members are not eligible in E996-01 at the same review (stock-reviews; X996 in-cloud reasons):

| Year | Retained | Lost: **market cap missing** | Lost: no fundamentals object | Lost: cap < $2B (1.5–2B / < 1.5B) | Lost: not common type | New only |
|---|---|---|---|---|---|---|
| 2011 | 8,542 | **1,984** | 400 | 33 / 98 | 12 | 238 |
| 2012 | 8,819 | **1,829** | 378 | 43 / 101 | 12 | 218 |
| 2013 | 10,052 | **2,191** | 416 | 65 / 121 | 15 | 269 |
| 2014 | 11,249 | **2,463** | 445 | 56 / 137 | 30 | 314 |
| 2015 | 11,603 | **2,478** | 339 | 68 / 149 | 30 | 355 |
| 2016 | 11,518 | **2,205** | 192 | 57 / 151 | 33 | 386 |
| 2017 | 12,989 | **2,085** | 42 | 41 / 180 | 36 | 363 |

No loss is due to price, ADV, exchange or depositary flags.

**Survivorship test** (`universe_survivorship.py`; own membership tables only). The test asks what share of stock-months belong to securities still in the data-v1 universe at the last review (2017-12-29):

| | Stock-months | Still in the universe at 2017-12 |
|---|---|---|
| Retained by the new feed | 74,772 | **91.7%** |
| **Lost on the new feed** (560 securities) | 18,915 | **49.9%** (2011: 33%; 2013: 40%; 2015: 50%) |
| New only | 2,143 | 30.3% |

**Interpretation.**
- The new feed is missing market-cap history mainly for companies that later leave the universe through delisting, acquisition or decline. The concentration is greatest in the early years.
- A universe drawn from it under-represents later losers. That is survivorship bias, which is a form of look-ahead in membership.
- It does not implement the conceptual universe ("US common, NYSE/Nasdaq, **PIT** market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M").

**Market cap where present.** Across 170 splits of eligible securities (2011–2017):
- 166 market caps were continuous while the raw price jumped by the split factor (point-in-time shares);
- 4 jumped with the price.

So the market cap that exists is PIT-consistent. The problem is what is missing.

**Requirement 6 fails.**
- A repair route exists in principle: extend the SEC market-cap layer (D111: SEC cover-page shares × raw price) to securities whose vendor market cap is missing.
- It is unbuilt and unverified for these 560 securities.
- Building it is a data-infrastructure change for the owner to decide (section 47).

## 26–29. Coverage

| | Data v1 (E993-02) | **M1 (E996-01)** | M2 (E996-03) |
|---|---|---|---|
| Eligible stock-months | 93,687 | 76,915 | 76,915 |
| Non-financial | 70,804 | 57,682 | 57,682 |
| H2 (non-financial) | 25.1% | **28.5%** | 42.1% |
| Fully scored (kept class, all inputs) per month: min / median / mean / max | 196 / 516 / 479 / 612 (H022 population) | **291 / 541 / 486 / 677** | 0 / 514 / 394 / 659 |
| Candidates (no hard disqualifier) per month | — | 373.5 | 301.2 |
| 80+ per month (mean); months with none | 7.0; 2 | **5.9; 1** | 4.6; **15** |

Per-input presence (non-financial eligible; M1):

| Year | Revenue TTM | GP TTM | NI TTM | OCF TTM | Total assets | Equity | Valid baseline |
|---|---|---|---|---|---|---|---|
| 2011 | 67.2% | 63.3% | 68.7% | 68.9% | 97.1% | 97.1% | 80.3% |
| 2013 | 85.6% | 79.9% | 89.3% | 89.7% | 99.3% | 99.3% | 70.9% |
| 2015 | 89.8% | 85.3% | 93.1% | 93.1% | 99.4% | 99.4% | 87.7% |
| 2017 | 90.9% | 87.9% | 90.0% | 93.5% | 99.1% | 99.0% | 87.4% |

H2 among non-financial stocks by year:

| Year | M1 | M2 |
|---|---|---|
| 2011 | 42.4% | 98.0% |
| 2012 | 41.3% | 76.7% |
| 2013 | 39.4% | 47.7% |
| 2014 | 25.9% | 29.9% |
| 2015 | 20.2% | 23.7% |
| 2016 | 18.1% | 20.4% |
| 2017 | 21.1% | 23.2% |

Baseline checks (M1): 61,892 store baselines; 0 life rejects, 0 CIK rejects, **0 PIT violations**. The in-host slice check was exact (168/168).

## 30–32. Score distribution and operational meaning (M1; no returns)

- **Total score of candidates:** 31,376 stock-months.
  - Mean 47.5, median 48, sd 15.6, p10 26, p90 68, max 94.
- **Counts:**

  | Threshold | Stock-months | Per month |
  |---|---|---|
  | ≥ 75 | 1,224 | 14.6 |
  | ≥ 80 | 498 | 5.9 |
  | ≥ 85 | 121 | 1.4 |
  | ≥ 90 | 36 | 0.4 |

  P7-CP3R on data v1: 80+ about 7.0, 75+ about 15.6 per month.
- **Layer means (scored rows):**
  - Technical 17.9 / 40 (sd 11.9);
  - Fundamental 18.0 / 45 (sd 10.1);
  - Sector 7.6 / 15 (sd 4.3).
- **Layer correlations:** T–F 0.005, T–S 0.22, F–S −0.006.
- **Hard-disqualifier rows (M1):**

  | Code | Rows |
  |---|---|
  | H1 financial | 16,344 |
  | H1 no SIC | 2,889 |
  | H2 | 29,580 |
  | H3 | 1,689 |
  | H4 | 634 |
  | H5 | 0 |
  | H6 | 15,320 |
  | H7 | 1,610 |
  | Duplicate class | 264 |

- **Regimes:** STRONG 63, NORMAL 9, WEAK 7, RISK_OFF 5.
- **Operational meaning.** Under M1, Score v1 would be as usable as on data v1. Under M2 it would be usable only from 2013. But the population is drawn from a survivorship-biased universe (section 24), so coverage alone does not make it usable.

## 33–34. Compliance and export feasibility (programme-wide)

- **Encountered limits:**
  - 50 files per project (X996 uses 49);
  - 64,000 characters per file;
  - E995-05 earlier: build-time rejection of per-report data probing / validation export.
- **X996 was accepted.**
  - It does vendor/SEC validation inside QuantConnect and exports only aggregates and digests.
  - All three runs compiled and completed.
- **Derived statistics leave the platform today.** Each run exported:
  - score distributions and candidate counts;
  - SHA-256 digests;
  - a labelled **synthetic** IC / t-statistic block (seeded numbers, no market data: mean IC 0.023, t 4.27).

  Earlier, E993-03 exported full score tables, and the P7-CP5 null exported IC-type statistics on 18131.
- **Categories:**
  - IC, t-statistics, gate PASS/FAIL, CAGR, Sharpe, candidate counts and aggregate distributions are all aggregate derivatives, which QuantConnect currently lets out;
  - report-level vendor values or ratios are not.
- **Residual risk.** QuantConnect's review is opaque and can change; it has stopped runs mid-way before (E995-04).
- **Requirement 8: PASS. Requirement 9: PASS, empirically, as of 2026-10-10.**

## GO / NO-GO conditions

| # | Condition | Result |
|---|---|---|
| 1 | Every Score v1 concept has a defensible input | **PASS** (all fields exist; timing from first-seen) |
| 2 | First-seen is truncation invariant | **PASS** |
| 3 | Restatements do not retroactively contaminate snapshots | **PASS with residual** (vintage stream; 0.26% of reports carry a figure first filed later, comparable to data v1) |
| 4 | Timing can be validated against SEC | **PASS** for matched reports (41,312; 96–99% next day) |
| 5 | No unacceptable early availability | **M1 FAIL** (277 early, 46 unexplained, concentrated before 2013); **M2 PASS** |
| 6 | Universe membership PIT-safe | **FAIL** (missing market cap for later-disappearing companies; survivorship bias) |
| 7 | Coverage meaningful | **M1 PASS**; **M2 FAIL for 2011–2012**, PASS 2013+ |
| 8 | Complies with QuantConnect's restrictions | **PASS** |
| 9 | Derived statistics exportable | **PASS** (empirically, today) |

## 35. Data v2 changes that would be required (for information; nothing built or frozen)

1. Availability = M2: max(first seen, SEC original filing + 1). Vendor file date and the +90 rule removed. Ledger with never-rewritten first-seen snapshots; revisions only from their own first-seen day.
2. An in-cloud SEC restatement guard: block a report whose first-seen revenue or total assets equals only a not-yet-filed later SEC value. This is the D111 analogue.
3. **A universe repair (the failed requirement):** SEC market cap (cover-page shares × raw price, D111 method) for securities whose vendor market cap is missing. It would need its own verification: coverage of the 560 lost securities, timing, split handling.
4. Either an earlier SEC identity mapping (CIK rows before the first XBRL filing, verified) or a research window starting in 2013. Without one of these, M2 leaves 2011–2012 empty.
5. A new data-freeze manifest (v2), with v1 preserved unchanged.

## 36. What would have to be regenerated

If Data v2 were ever approved:
- the X993 score / mechanics export (P7-CP3R equivalent);
- candidate and mechanics statistics;
- the synthetic power study on v2 score tables;
- a new H022 canary;
- 5,000 new null worlds;
- a new c_IC;
- then one real evaluation.

The old c_IC (2.390976216956) and the old null worlds stay records of data v1 / LEAN 18131, and are never used on a new panel.

## 37–39. Effort, runs, cost (only if the owner pursued the repair route)

- **Engineering:** about 3–5 sessions:
  - universe market-cap repair and its verification;
  - identity backdating study or window decision;
  - restatement guard;
  - re-audit;
  - v2 freeze.
- **QuantConnect runs:** about 15:
  - 3–4 repair / verification runs;
  - 1–2 score exports;
  - canary;
  - 5 null batches;
  - 1 real evaluation;
  - reserves.
- **Cost:** $0 beyond the existing $24 / month. No data purchase, no upgrade.

## 40–45. Confirmations

40. **No future return of any kind was computed.**
41. **No H022 statistic** (IC, t, gate, quintile, 80+ performance) was computed. The only IC-type numbers are the labelled synthetic export check (seeded random numbers).
42. **No portfolio was run:** 0 orders in E996-01/02/03.
43. **2018–2021 untouched.** Every run ends on or before 2017-12-31.
44. **Holdout untouched.**
45. **Nothing purchased; no upgrade.**

Also preserved unchanged as records of data infrastructure v1 / LEAN 18131:
- E993-02;
- P7-CP3R, P7-CP4, P7-CP5a, P7-CP5b, P7-CP5c;
- the old null worlds and c_IC.

Score v1, its spec and its mechanics are unchanged. No PIT rule was loosened.

**Records:**
- experiments E996-01, E996-02, E996-03 (total H022-family infrastructure experiments: 18 including E995-01..05);
- `research/phase7/cp5d/`:
  - `build_x996_ref.py`;
  - `x996_analysis.py` and `x996_summary.json`;
  - `universe_survivorship.py` / `.json`;
  - `ref_first_filed_lag.py` / `.json`;
- host `strategies/X996_first_seen_ledger/`.

## 46. Final recommendation

```
NO-GO — Score v1 cannot be migrated safely on the available QuantConnect infrastructure
```

- **Failed requirement: 6, universe membership PIT safety.**
  - The new feed has no market cap for about 18% of data v1's eligible stock-months.
  - Those securities are disproportionately later-disappearing companies: 50% vs 92% still in the universe at end-2017.
- **Secondary: requirements 5 and 7 conflict before 2013.**
  - The SEC gate that removes early availability leaves 2011–2012 nearly unscorable.
- The first-seen fundamentals stream itself passed the timing, truncation, determinism and vintage tests. It is not the reason for NO-GO.

As instructed: no Score redesign, no move to SEC-only, no Score v2.

## 47. Exact next owner decision

Choose one:

- **(a) Close H022 as "not evaluable on the available infrastructure"**, with Phase 7 ending without a result.
- **(b) Authorise a universe-repair feasibility study only** (infrastructure). That means:
  - test whether an SEC market cap can restore the 560 securities PIT-safely;
  - test whether an earlier, verified SEC identity mapping (or a 2013 start) resolves M2's 2011–2012 gap.

  Then return with a new GO / NO-GO. Nothing about Score v1 would change.
- **(c) Keep H022 dormant** and decide later.

Until then: STOP. No Data v2, no P7-CP3R rerun, no H022, no null worlds, no threshold, no returns, no portfolio, no 2018–2021, no Holdout.
