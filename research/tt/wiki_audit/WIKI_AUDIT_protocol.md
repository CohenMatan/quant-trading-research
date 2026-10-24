# WIKI Prices data-quality and composition audit — protocol (FROZEN before any WIKI data exists)

**Owner direction:** D298. **Framework:** TT-CP1b Addendum 1 §3 (gates A1–A6), with the D298 corrections below. **Status:** frozen at commit; its SHA-256 is pinned in `research/tt/wiki_audit/PROTOCOL_PIN.json` and checked by `tests/test_wiki_audit.py`. Thresholds are not changed after any WIKI aggregate is computed. A genuine definitional error found later is recorded as a dated, disclosed amendment, never silently fixed.

## 1. Scope and handling rules

- **Window:** session dates 2010-01-04 → 2017-12-29 only.
  - Rows dated outside the window are discarded when the file is read. Only the total file row count is kept, for the manifest.
  - No 1999–2009 row is analysed or viewed. Nothing after 2017 is analysed.
- **Handling:** the audit is programmatic. Outputs are aggregates (counts, shares, quantiles) only. No raw rows, ticker-level price series or charts are printed, committed or placed in an AI model's context.
- **Raw data location:** under `data/wiki/` (git-ignored). The manifest `research/tt/wiki_audit/WIKI_MANIFEST.json` records source URL, acquisition date, file size, format, row count and SHA-256. The audit refuses to run if the file's SHA-256 differs from the manifest.
- **Expected input:** the WIKI_PRICES table with columns `ticker, date, open, high, low, close, volume, ex-dividend, split_ratio, adj_open, adj_high, adj_low, adj_close, adj_volume`. A different schema stops the audit with an error.

## 2. Independent SEC reference frame (no QuantConnect data, no WIKI data)

### 2.1 Sources (cached)

- **R1:** XBRL frames `dei:EntityPublicFloat` (USD), CY2009Q1I–CY2021Q4I. Each entry gives cik, accession, float date and value.
- **R2:** `data/sec_derived/xbrl_filings.json.gz`, an index of every XBRL 10-K / 10-Q filing from 2009-06 to 2021-12. Fields used: cik, accession, form, filed date, SIC at filing, registrant name, and `prefix` (the instance-document prefix, which is the registrant's own ticker in about 98% of filings).
- **R3:** cached SEC submissions JSON (about 8,000 files, about 4,944 registrants). Used for exit type only.

### 2.2 Eligibility rule (point-in-time)

- A registrant is **eligible for month m** if a 10-K / 10-K405 / 10-KT XBRL filing with reported public float ≥ $2,000,000,000 was **filed before the first session of m**, and that filing is its most recent such 10-K, filed within the previous 15 months.
- The float is joined to the filing by accession number, and the filed date comes from R2.
- **This uses only information public at the time.**
- Public float is at most market capitalisation, so the frame is a conservative subset of the ≥ $2B universe.

### 2.3 Exclusions (applied as known at filing)

- SIC codes 6726, 6770, 6792, 6221 (funds, blank-check, royalty, commodity).
- Names matching the non-common pattern of `identity_v2.NON_COMMON_NAME` (partnerships, LLCs, funds, trusts of those kinds).

### 2.4 Categories (reported, not excluded)

- **Financial / REIT:** SIC 6000–6799.
- **Foreign-style name:** the `identity_v2.FOREIGN` pattern.
- **Multiple frame registrants sharing one prefix in the same month.**

### 2.5 Size and liquidity

- **Size stratum:** float tercile within each month's frame. This is labelled **size (public float)**; it is never called liquidity.
- **Liquidity:** comes only from WIKI, as the median over 63 sessions of raw close × raw volume. It is defined only for matched names. Liquidity terciles are computed among matched names per year. **Public float is never used as liquidity.**

### 2.6 Leavers

- A registrant **left** if its last R2 10-K / 10-Q filing is dated before 2018-01-01 and after its first eligible month.
- Its exit month is the month of that last filing.
- Exit type is taken from R3 forms in the 24 months up to 6 months after the exit:
  - **ACQUIRED:** DEFM14A, DEFM14C, PREM14A, SC 14D9, SC TO-T or 425 filed by the registrant;
  - **FAILED:** an 8-K carrying item 1.03, or a Form 15 within 12 months of an 8-K 1.03;
  - **DELISTED-OTHER:** a Form 25 / 25-NSE without an acquisition form;
  - **UNKNOWN:** no R3 file, or none of the above.
- When more than one type applies, priority is FAILED, then ACQUIRED, then DELISTED-OTHER.

### 2.7 Survivors and leavers in the frame

- **Non-leavers:** registrants that still file in 2018 or later.
- **Leaver months:** the 24 frame months before the exit.

## 3. Linking WIKI to the reference, and identity classes

For each frame registrant-month (cik, m):

1. **Expected ticker:** the R2 prefix of the registrant's most recent filing filed on or before m's first session (point-in-time), upper-cased.
2. **Identity class:**
   - **AMBIGUOUS:** the prefix is carried by two or more frame registrants in the same month, **or** the WIKI ticker's 2010–2017 history is attached in R2 to two or more different CIKs (ticker reuse). The ticker is excluded from the sample frame.
   - **MATCHED:** the prefix equals a WIKI ticker that has bars on at least 90% of month m's reference sessions.
   - **MISSING-HISTORY:** the prefix equals a WIKI ticker but its bars in month m are below 90%. Sub-cases: no bars at all in m (out of life), or partial.
   - **UNRESOLVED-IDENTITY:** the prefix is not any WIKI ticker. The name may still be in WIKI under a different ticker. This class is not counted as "missing price history". It is reported separately, with an upper and lower bound on coverage.
3. **Coverage, two definitions:**
   - **strict** = MATCHED / all non-AMBIGUOUS registrant-months;
   - **resolved** = MATCHED / (MATCHED + MISSING-HISTORY).
   The gates use **strict** coverage. **Resolved** coverage is reported as an upper bound. The gap between the two is the identity-mapping uncertainty, not missing data.

## 4. Reference trading calendar

- **Reference sessions:** dates on which at least 50% of the WIKI tickers with any bar in that calendar year have a bar.
- **Cross-check:** the per-year session count is compared with the published NYSE session counts: 2010 252, 2011 252, 2012 250, 2013 252, 2014 252, 2015 252, 2016 252, 2017 251. Any difference is reported. More than 2 sessions off in any year means the calendar FAILS, and then gate A5 is INCONCLUSIVE.

## 5. Measurements

### 5.1 Inventory

- Unique tickers, rows, and rows per ticker by year.
- Share of rows with any missing (NaN) field.

### 5.2 Bar integrity

Measured inside each ticker's life, from first to last bar in the window, on reference sessions:

| Item | Definition |
|---|---|
| (i) Missing sessions | Share of ticker-sessions with no bar |
| (ii) Spike | \|ln(adj_close_t / adj_close_{t−1})\| > 0.40, followed next session by a move of the opposite sign with \|ln\| > 0.30, and no split ≠ 1 and no ex-dividend > 0 on t or t+1 |
| (iii) Invalid OHLC | high < max(open, close) or low > min(open, close) or high < low, on raw or adjusted values; any price ≤ 0; volume < 0 |
| (iv) Adjustment consistency | Let ratio_t = adj_close_t / close_t. A "ratio change" is a relative change > 1e-4 between consecutive bars. Explained if split_ratio_t ≠ 1 or ex-dividend_t > 0. Share explained = explained ratio changes / all ratio changes. Also reported: events (split or dividend) with no ratio change. |
| (v) Dividend factor check | For dividend events without a split, implied factor = 1 − div_t / close_{t−1}. Share of events where the observed ratio change agrees within 0.002. |

### 5.3 Split cross-check against the SEC

- A random sample (seed 20261024) of up to 100 WIKI split events in the window on MATCHED tickers whose registrant has cached companyfacts.
- **SEC ratio** = `dei:EntityCommonStockSharesOutstanding` from the nearest cover after the split ÷ the nearest cover before it. Both must be within 400 days of the split, with no other WIKI split in between.
- **Agreement:** |SEC ratio / WIKI split_ratio − 1| ≤ 0.15.

### 5.4 End-of-curation decay

Coverage and bar-integrity rates for 2017 compared with the mean of 2014–2016.

### 5.5 Chart readiness

A MATCHED registrant-month is **chart-eligible** if the ticker has at least 252 bars in the 252 reference sessions before m's first session, and no internal gap longer than 5 sessions. All 252 sessions must be on or after 2010-01-04, so the earliest chart-eligible month is 2011-01.

## 6. Gates (pre-registered; never changed after measurement)

| Gate | Measure | PASS | FAIL | Otherwise |
|---|---|---|---|---|
| **A1** frame coverage | Strict coverage, overall and by year | ≥ 90% overall and ≥ 85% every year | < 75% overall or any year < 70% | INCONCLUSIVE |
| **A2** leavers | Strict coverage of leaver months by exit type (FAILED, ACQUIRED, DELISTED-OTHER, UNKNOWN) | Every type with ≥ 20 registrants ≥ 80%, **and** overall leaver coverage within 10 points of non-leavers | Any type with ≥ 20 registrants < 65%, **or** gap > 20 points | INCONCLUSIVE. A type with < 20 registrants is reported and never counts as PASS. If no type reaches 20, A2 is INCONCLUSIVE. |
| **A3** strata | Strict coverage by year × size tercile, and by category (financial / REIT; foreign-style name) | No stratum with ≥ 50 registrants below 70% | Any stratum with ≥ 50 registrants below 50% | INCONCLUSIVE |
| **A4** identity | AMBIGUOUS share of non-excluded frame registrant-months; UNRESOLVED-IDENTITY share | AMBIGUOUS ≤ 2% **and** UNRESOLVED ≤ 10% | AMBIGUOUS > 5% **or** UNRESOLVED > 20% | INCONCLUSIVE |
| **A5** bar integrity (on MATCHED tickers) | (i) missing ≤ 0.5%; (ii) spikes ≤ 0.1% of ticker-sessions; (iii) invalid ≤ 0.01%; (iv) ≥ 99.5% explained; (v) ≥ 95% of dividend events agree; split cross-check ≥ 95 / 100 agree (pro-rata if fewer than 100) | All met | Any of (i)–(v) worse than 5× its PASS bound (for (iv) and (v): unexplained / disagreeing share > 5× the allowed share); or split agreement < 85% | INCONCLUSIVE, including when the calendar check fails or the split sample has fewer than 30 events |
| **A6** curation decay | 2017 vs 2014–2016 strict coverage | 2017 within 2 points | Worse by > 5 points | INCONCLUSIVE |
| **A7** chart sufficiency | Chart-eligible MATCHED registrant-months per year (2011–2017) × size tercile cell; and chart-eligible leaver months, pooled | Every cell ≥ 20 distinct registrants **and** ≥ 30 distinct leaver registrants pooled | Any year with < 10 distinct registrants in any size tercile, or < 10 leaver registrants pooled | INCONCLUSIVE |

**Overall classification:**
- **SUFFICIENT FOR EXPLORATORY CHART RESEARCH** if A1–A7 all PASS.
- **INSUFFICIENT** if any gate FAILS.
- **INCONCLUSIVE** otherwise.
- **INCONCLUSIVE / ACCESS BLOCKED** if no WIKI file was acquired.

These are the TT-CP1b Addendum 1 bounds for A1–A6. A7 was added under D298 item 3. A4 now splits identity into AMBIGUOUS and UNRESOLVED, also under D298.

## 7. What the audit cannot establish (fixed in advance)

- **It does not show WIKI is survivorship-free.** Leaver coverage is measured only inside an SEC frame that itself starts with XBRL, from mid-2009 to 2011.
- **Price accuracy beyond internal consistency and the split cross-check is not verified.** No independent price source is available.
- **R1 misses some registrants:** most 20-F / 40-F filers, registrants with no public float tag, and large-cap names whose float is below $2B.
- **Exit types are UNKNOWN** for registrants outside the R3 cache.
- **Coverage of UNRESOLVED-IDENTITY names cannot be measured.** It is bounded, not known.

## 8. Sampling method (reported if the audit passes; not executed by this audit)

- About 300 (registrant, month) draws from the chart-eligible MATCHED set, stratified by year (2011–2017) × size tercile × leaver status.
- Cell targets are proportional to the **SEC frame's** registrant-months, not to WIKI's own list.
- Seed fixed before drawing. Cells that cannot be filled are reported as unfilled.
- No outcome or forward return is used.
