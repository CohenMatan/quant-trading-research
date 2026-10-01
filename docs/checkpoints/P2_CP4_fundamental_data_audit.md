# Fundamental-data integrity audit (P2-CP4)

- **Date:** 2026-10-01.
- **Status: AUDIT ONLY** (D106). No H016; no profitability formula or threshold; no portfolio, ranking or return of any kind; no hypothesis slot; Holdout untouched. **STOP:** awaiting owner approval.
- **Runs:** all infrastructure, never trials (`experiments/INDEX.csv`).
  - **E967-01:** stopped on a bug in the audit code; annotated.
  - **E967-02:** the full audit, 2010–2021, 3,021 days, 3.42 million stock-days.
  - **E968-01:** universe-exclusion diagnostic.
  - Two unregistered schema probes (scratch).
- **Evidence:** `research/phase2/fundamental_audit/`:
  - `E967_tables.json`;
  - `E967_analyse.py`;
  - `E968_universe_exclusions.json`;
  - `schema_probe_2015-02.txt` (field names only).
- **Code:** `strategies/X967_fundamental_audit`, `strategies/X968_universe_exclusions`; tests in `tests/test_fundamental_audit.py`.
- **Licence:** no raw Morningstar value is stored. Outputs are counts, dates, SEC accession years and ratios only.

**Labels used below:**
- **[confirmed]**: measured by us;
- **[doc]**: QuantConnect documentation claim;
- **[assumption]**;
- **[unresolved]**.

## Bottom line

**Profitability/quality research can be done reliably on this data, under specific handling rules.**

Safe:
- income-statement, balance-sheet and cash-flow **totals**;
- point-in-time **market cap**;
- the **filing date** as the availability date.

Not safe:
- **share counts and per-share values as levels** (they are restated for all later splits, including splits inside the Holdout);
- **company metadata** (fiscal-year end and probably sector; current status, not historical);
- **SEC accession numbers** for timing.

Four issues remain open:
1. About 0.3% of report-days carry an accession number from a filing made **after** the simulated date. These may contain later (possibly restated) values. Independent SEC verification is blocked in this environment.
2. File dates are **approximated** (period end + 45 days) for 0.3–7.6% of reports, mostly in 2010–2012. These need a conservative availability rule.
3. The known **survivorship gap** (D043) persists: later-delisted companies often have no fundamentals and never enter the universe.
4. **Visa** is excluded from the whole 2010–2021 universe by a Morningstar exchange error (OTCM).

## 1. QuantConnect fundamental-data architecture

- **Source:** Morningstar US fundamentals, delivered with QuantConnect's coarse/fine `Fundamental` object to the universe-selection function each day.
  - **[confirmed]** One object per security per day, about 8,000 a day. Around 1,100 a day pass our ≥ $2B eligibility.
- **Storage:** **[confirmed]** one parquet file per *field × period × year range*, e.g. `2015_2020_FinancialStatements.<Field>.NineMonths`.
  - Reading a property whose file does not exist is **fatal** to the backtest (a probe hit this for rarely populated fields).
  - **Infrastructure rule:** strategy code must read only an approved, tested field list.
- **Generation:** **[doc]** since 2026-09-23 QuantConnect serves the new generation of Morningstar fundamentals for the whole history.
  - Ratios, growth, per-share and average properties are dated by the filing that produced them, about 63 days after period end.
  - About one third of values differ from the previous generation (recalculations, sign conventions).
  - Our LEAN build 18131 carries this generation. **[assumption]** We read the same files; consistent with what we observe.
- **Reporting basis:** **[doc]** "As Original Reported". Mistakes are not fixed later.
- **Coverage start:** **[doc]** January 1998.
- **Fill-forward:** **[doc] [confirmed]** without an update, the same values repeat daily.

## 2. Available profitability/quality fields

All exist with `three_months` (quarter) and `twelve_months` (trailing year) periods. Coverage is over eligible stock-months, 2010–2021.

| Concept | Field | Coverage |
|---|---|---|
| Revenue | `income_statement.total_revenue` | 98–100% |
| Gross profit | `income_statement.gross_profit` (also `cost_of_revenue`) | 86–89% (not reported by most financials) |
| Operating income | `income_statement.operating_income` | 88–89% |
| Net income | `income_statement.net_income` (also `net_income_common_stockholders`) | ≈ 100% |
| Total assets | `balance_sheet.total_assets` | ≈ 100% |
| Shareholders' equity | `balance_sheet.stockholders_equity`, `common_stock_equity` | ≈ 100% |
| Debt | `balance_sheet.total_debt` | ≈ 92% |
| Operating cash flow | `cash_flow_statement.operating_cash_flow` | 99–100% |
| Free cash flow | `cash_flow_statement.free_cash_flow` | 99–100% |
| Shares | `company_profile.shares_outstanding`, `share_class_level_shares_outstanding`, `balance_sheet.ordinary_shares_number`, `earning_reports.basic_average_shares` | ≈ 100% (**restated for later splits**, §6) |
| Market cap | `market_cap` (= `company_profile.market_cap`) | universe-defining |
| Vendor ratios | `operation_ratios.roa`, `roe`, `gross_margin`, `operation_margin` | ≈ 100% (vendor-derived; not used as primary, §13) |
| Timing | `earning_reports.period_ending_date`, `.file_date`, `.period_type`, `.accession_number`; `financial_statements.period_ending_date` / `.file_date` | see §3–4 |

**Core profitability set** (revenue, gross profit, operating income, net income TTM; assets and equity; operating cash flow) is present for **86–89%** of eligible stock-months in every year.

## 3. Exact point-in-time semantics [confirmed]

**Each day the object exposes the latest report available on that day:**
- the period end and filing date;
- the quarterly and trailing-year values for that period.

**Look-ahead checks on file dates:**
- **No report file date after the simulated date: 0 of 3.42 million stock-days.**
- **No financial-statement file date after the simulated date: 0.**

**When a new period appears:**
- **94.4%** of 57,265 new periods are first seen **within 1 day of the filing date**.
- The rest are seen later, when a stock enters the universe late. **None earlier.**

**Consistency of the two blocks:**
- The earnings-report block and the financial-statements block point to the same period on 99.75% of stock-days.
- The default period equals the quarterly period on 99.99%.

**Revisions:**
- **Silent overwrites:** within the same filing, values never changed (**0**) over 12 years, checked monthly on the latest period's revenue, net income, assets and equity.
- **Amendments:** a new filing for an already-delivered period occurred **18 times**, each with a new, later file date. That is point-in-time behaviour.
- **Periods moving backwards:** 71 cases, negligible.

## 4. Publication-date handling

| Days from period end to file date | Share of new periods |
|---|---|
| ≤ 30 | 21% |
| 31–44 | 56% |
| exactly 45 (**approximation**) | 1.7% |
| 46–60 | 19% |
| > 60 | 2% |

This matches SEC deadlines: about 40–45 days for 10-Qs and 60–90 days for 10-Ks.

**Normal filers** (AAPL, MSFT, JNJ, XOM, KO): **[confirmed]**
- every quarter for 12 years (49 periods each) is first seen within 1 day of its file date;
- file dates fall 18–60 days after period end.

**Kraft Heinz restatement year:** **[confirmed]** its delayed 2018 10-K appears with file date 2019-06-07 (160 days after period end) and is first seen the next day.
- **[unresolved]** That matches the public record of the delayed, restated 10-K as I recall it, but it is unverified here (§12).
- The earlier quarters are not re-served with restated values: the latest-period stream never revisits old periods.

**Approximated file dates** (exactly period end + 45 days; **[doc]** "for older symbols the file date is approximated 45 days after the as-of date"):

| Year | Share |
|---|---|
| 2010 | 3.4% |
| 2011 | 7.6% |
| 2012 | 4.5% |
| 2013–2014 | ≈ 1.7% |
| 2015–2021 | 0.3–1.3% |

- An approximation is **too early** if the real filing came later than 45 days. This is likely for annual reports, whose deadline is 60–90 days.
- **Handling required** (§15).

**Earnings announcement vs filing:**
- The file date is the SEC filing (10-Q/10-K), typically on or after the earnings press release.
- So values are never available before the public announcement **[assumption]**.
- They may lag it by days, which is conservative.

## 5. Restatement behaviour

- **[doc]** "As Original Reported".
- **[confirmed]** No in-place value changes. Amendments arrive as new filings with later dates.
- **[confirmed, unresolved meaning]** The accession number for the quarterly figure is **not reliable**.
  - For December fiscal years, the derived Q4 quarter carries the previous filing's accession: 540,852 stock-days where the accession year ≠ the file-date year. That pattern is benign.
  - On **9,600 stock-days (0.28%)** the accession belongs to a filing made **after** the simulated date (e.g. a June-2010 quarter with a 2011 accession). Those values **may** come from a later filing that re-reported the quarter. That is a possible restatement leak for roughly 0.3% of report-days.
  - It cannot be resolved without SEC data (§12).
- **[unresolved]** Whether the 2026-09 regeneration ("one third of values differ", "recalculated") reproduces originally-reported numbers for **all** historical periods is a vendor claim we cannot test without EDGAR.

## 6. Split and share-count behaviour [confirmed: a material defect for levels]

**Every share-count field is restated for all later splits, up to today**, including splits inside the locked Holdout and after it. Measured as market cap ÷ (raw price × shares):

| Company | Date | Ratio | Implied split factor |
|---|---|---|---|
| Apple | Jan 2010 | **0.0357 = 1/28** | 7:1 (2014) × 4:1 (2020) |
| Apple | after June 2014 | 0.25 | the remaining 2020 split |
| NVIDIA | 2010 | **0.025 = 1/40** | 4:1 (2021) × **10:1 (2024)** |
| Tesla | 2010 | **0.0667 = 1/15** | 5:1 (2020) × **3:1 (2022)** |
| Amazon | 2015 | 0.05 | **20:1 (2022)** |

**Universe-wide:**
- Market cap equals price × shares within 2% for only **70–89%** of stock-months, depending on the share field.
- **4–9%** are off by more than a factor of 2.2.
- The share falls from 2010 to 2021, as expected when fewer future splits remain.
- This holds for `shares_outstanding`, the share-class count, `ordinary_shares_number` (balance sheet) and `basic_average_shares` (earnings reports).

**Per-share values:**
- Net income TTM ÷ (EPS TTM × average shares) is within 2% for 84–87% of stock-months.
- So EPS is restated consistently with the share counts.
- **EPS and other per-share values are therefore split-adjusted to today as well [inference].** Never compare them with raw prices.

**Market cap itself is point-in-time [confirmed].** It equals the raw price × the true historical share count. Examples:
- Apple's 1/28 ratio implies a market cap consistent with the true 2010 share count.
- Kraft Heinz and Chesapeake ratios return to 1.00 within days of merger or restructuring share changes.

## 7. Historical market-cap integrity

- **Point-in-time and consistent** (§6). Already audited at CP2 (E951).
- **Transient inconsistencies around large share changes** last a few days. Example: the Kraft Heinz merger, August 2015.
- The universe uses market cap as known at the T−1 close (D017). Unchanged.

## 8. Missing data and coverage

**Core profitability set present, by year (eligible stock-months):**

| Year | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eligible stock-months | 8,964 | 10,100 | 10,295 | 11,819 | 13,439 | 14,019 | 13,606 | 14,848 | 15,660 | 15,481 | 15,481 | 19,480 |
| Core set present | 88.5% | 89.2% | 89.1% | 89.4% | 88.9% | 87.8% | 88.0% | 86.8% | 86.1% | 86.2% | 86.7% | 85.9% |

**Missingness of the core set by dimension:**

| Dimension | Missing share |
|---|---|
| **Financial Services** (sector 103) | **75.8%** (banks and insurers report no gross profit or operating income) |
| Real Estate | 8.3% |
| Healthcare | 9.1% (pre-revenue biotech) |
| All other sectors | ≤ 6% |
| Size terciles (small / mid / large) | 14.8% / 11.3% / 11.4% |
| Listing age < 3 years / 3–10 years / ≥ 10 years | 17.1% / 11.1% / 12.4% |
| Exchange: NYSE / Nasdaq | 12.5% / 12.5% |
| Distress (adjusted price down > 50% over 12 months) | 5.3%, vs 12.1% for others: distressed names are **not** more often missing |

**Reading:**
- Missingness is **structural** (business model), not a survivorship artefact inside the universe.
- A profitability measure that requires gross profit **mechanically excludes most financials**. That is a design choice for a future spec, and it must be disclosed.

## 9. Survivorship-bias risks

- **Inside the universe [confirmed]:** delisted, acquired and bankrupt companies are present while they traded.
  - 784 of the 2,524 companies ever eligible disappear before 2021.
  - Monsanto was eligible until 2018-06-07 (acquired June 2018); DirecTV until 2015-07-25 (acquired July 2015).
- **The known gap persists (D043) [confirmed]:** some large companies that later stopped trading have **no fundamentals and no market cap**, so they **never** enter the universe.
  - Examples: Time Warner, Chesapeake before 2021, old Hertz.
  - Estimated missing share: 15.9% (2010) falling to 1.2% (2021). See `docs/data/survivorship_gap_2010.md`.
  - **For fundamental research this matters more than for technical research.** The missing names are disproportionately companies that later failed or were acquired, so a quality strategy could look better than it would have been.
  - It must be disclosed in any future result. EW and SPY are affected equally in our benchmarks.
- **New finding [confirmed]: Visa is excluded for all of 2010–2021.**
  - Morningstar labels its exchange **OTCM** in every month, so the harness exchange rule drops it.
  - It was never in our EW benchmark or any strategy. Visa ranked about the 39th–90th largest US company.
  - No other top-300 US company is affected, apart from one small name (AAMC).
  - The other large exclusions are deliberate: foreign secondary listings (Canadian banks, etc.) and partnerships/LLCs (D030/D057).
- **Company metadata [confirmed]:** **0** fiscal-year-end changes across 2,524 companies and 12 years. That is implausible historically, so `company_reference.fiscal_year_end` is **current-status metadata**, like the D061 company flags. Morningstar sector codes are **probably** current-status too **[assumption]**.

## 10. Data freshness

- Latest-report age at the monthly check: ≤ 100 days for **98.2–99.4%** of stock-months; 100–130 days for 0.5–1.6%; > 130 days for ≤ 0.5%.
- **Implementable rule** for any future spec: use the latest report whose file date is strictly before the decision date.
  - The object already provides exactly that. A filing on day T is first seen on T+1, and the harness decides at the T close with T−1-close fundamentals.
  - Plus a **staleness limit** to be fixed in the spec (e.g. ignore reports older than about 130 days), and the approximation guard (§15).

## 11. Canary results

| Case | Company | Result |
|---|---|---|
| Normal quarterly filer | AAPL, MSFT, JNJ, XOM, KO | ✔ 49 quarters each, seen within 1 day of filing, no gaps |
| Split | AAPL 2014/2020, NVDA, TSLA, NFLX, AMZN | ✘ share levels restated for all later splits; ✔ market cap point-in-time; ✔ statement totals unaffected |
| Share-class event | GOOGL 2014 | Share fields inconsistent; market cap consistent |
| Acquisition | MON, DTV | ✔ eligible until the deal; fundamentals not used afterwards (not eligible) |
| Bankruptcy | CHK, HTZ | Pre-bankruptcy entities **missing** (D043 gap); post-reorganisation listings OTC, so excluded |
| Restatement | KHC 2018/19 | ✔ delayed 10-K appears at its late file date; no backward overwrite seen; [unresolved] original-vs-restated values |
| Missing data | Financial-sector companies | ✔ detected and quantified (75.8% lack the core set) |
| Fiscal-year change | universe-wide detection | ✘ untestable: the field is current-status metadata |
| Universe exclusion | V | ✘ excluded by a vendor exchange error |

Look-ahead checks over 3.42 million stock-days:
- 0 file dates after the simulated date;
- 0 silent overwrites;
- 0 read errors.

## 12. External verification

**Planned:** compare our values and dates with SEC EDGAR's XBRL "company facts". Those list every filing that reported each value, with its filing date, so originally-reported vs restated values can be checked directly.

**Blocked:** this environment's network policy denies `data.sec.gov` and `www.sec.gov`. To enable it, add both hosts to the environment's allowed network domains. SEC also requires a contact string in the request header, and you choose what it says.

**What we could check instead:**
- **[doc]** QuantConnect documentation, quoted above.
- **[confirmed]** Internal consistency:
  - file dates within SEC deadlines;
  - no early availability;
  - amendments arriving as later filings;
  - a delayed 10-K appearing at its late date (Kraft Heinz).
- Publication dates for a few cases I recall (Facebook's 10-K on 2015-01-29; Kraft Heinz's delayed 10-K on 2019-06-07) match the data. **These recollections are unverified here.**

**[unresolved]:**
- whether stored values are exactly the originally-filed figures (vendor claim only);
- the source of the 0.28% future-accession report-days.

## 13. Fields considered safe (with §15 handling)

- **Statement totals:** revenue, gross profit, cost of revenue, operating income, net income, total assets, stockholders'/common equity, total debt, operating cash flow, free cash flow.
  - Quarterly and trailing-year.
  - Available from the file date.
  - Ratios built **from these totals** (e.g. gross profit ÷ assets) are safe.
- **`market_cap`:** point-in-time.
- **`earning_reports.file_date` / `period_ending_date`,** and the financial-statement equivalents, as availability and period stamps.

## 14. Fields considered unsafe

- **Share counts as levels:** `company_profile.shares_outstanding`, `share_class_level_shares_outstanding`, `balance_sheet.ordinary_shares_number`, `earning_reports.basic_average_shares` / `diluted_average_shares`. They are restated for later splits, including Holdout-era splits (2022–2024).
- **Per-share values** (EPS, book value per share and similar), and any combination with raw prices (P/E, P/B computed by us).
- **Accession numbers** for timing or provenance.
- **Company metadata:** `fiscal_year_end` (current status). Sector/industry classification: treat as current-status unless separately verified.
- **Vendor-derived ratios** (`roa`, `roe`, margins, valuation ratios) as primary signals. Their definitions and dating changed in the regeneration, and they cannot be audited field by field. Prefer our own ratios from audited totals.

## 15. Fields requiring special handling

1. **Approximated file dates** (exactly period end + 45 days). Proposed guard for any future spec: do not treat such a report as available before **period end + 90 days** (the latest 10-K deadline).
2. **Possible later-filing values** (0.28% of report-days). Cannot be detected cleanly without EDGAR; disclose. Optionally exclude reports whose accession year is after the decision date, a cheap, conservative filter **[proposal]**.
3. **Share changes** (for issuance research only, not profitability). Use **ratios of the same restated series at two dates**: the restatement factor cancels. Never use levels.
4. **Financials:** a gross-profit-based measure excludes them. Any spec must state this choice up front.
5. **Fatal unpopulated fields:** read only a fixed, tested field list.

## 16. Required infrastructure changes (none implemented yet)

1. **A point-in-time fundamentals snapshot layer in the harness.**
   - Record at each decision close, per eligible stock, the approved fields with their period end and file date.
   - Apply the availability rules (file date before the decision date; the approximation guard; a staleness limit).
   - Expose only approved fields.
   - Test it with a truncation-style look-ahead test and a canary that reproduces this audit's checks.
2. **A field allow-list and a guard** that refuses unapproved or unsafe fields (§14), because of the fatal-read behaviour.
3. **Visa:** a dated universe override for the exchange error (Visa Class A has been NYSE-listed since its 2008 IPO), as with D065. It would apply only to **future** runs. Past results stay as recorded and should carry this disclosure.
4. **Optional:** EDGAR verification tooling once the network allows it (§12).

## 17. Can profitability/quality research be performed reliably?

**Yes, with the handling above**, for measures built from statement totals and point-in-time market cap.

What makes this credible:
- timing semantics are point-in-time and verifiable in the data (0 early file dates in 3.4 million stock-days);
- coverage is high outside financials;
- revisions arrive as later filings.

**The residual risks are bounded and disclosable:**
- the vendor's "originally reported" claim is unverified externally;
- about 0.3% of report-days may come from a later filing;
- the survivorship gap: 16% (2010) falling to about 1% (2021) of true large companies missing.

**Not reliable:**
- anything using share-count or per-share levels;
- current-status metadata;
- accession-based timing.

## 18. Owner decisions required before defining H016

1. **Accept** this audit's conclusion and the safe / unsafe / special-handling field classification (§13–15).
2. **Approve the infrastructure work in §16** (snapshot layer, field allow-list, tests and a canary) as a next infrastructure step. This is not a strategy and not a hypothesis slot. It also creates **no** profitability ranking or return analysis.
3. **Visa:** approve a dated universe override for future runs, or keep the universe as is and disclose.
4. **External verification:** either
   - enable `data.sec.gov` and `www.sec.gov` in the environment's network settings (and choose the contact string for SEC requests), so a sample of values and dates can be checked against EDGAR before H016 is frozen; or
   - accept the vendor claim with the disclosed residual risk.
5. **Financials:** confirm that a future profitability spec may exclude companies without gross profit (mostly financials), disclosed. Alternatively, require a measure that covers them. Decide before H016 is designed, not after results.
6. **Approximation guard:** confirm the conservative "period end + 90 days" availability rule for reports with approximated file dates.

**STOP.** No H016, no profitability formula, no backtest, no factor comparison, no slot used. The Holdout is locked.
