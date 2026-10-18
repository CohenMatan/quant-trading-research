# Long-Horizon Stage C — OF-A Data and Point-in-Time Feasibility Audit: PROTOCOL (frozen before any new aggregate)

**Owner decision:** D242 (`docs/owner/2026-10-18_lh_stage_c_ofa_data_pit_feasibility.md`).

**Nature:** a NON-RETURN data audit. It uses no price, no return, no wealth and no QuantConnect run. It computes no surprise value, percentile, ranking or predictive statistic. Its outputs are counts, shares and delay distributions.

**Hash rule:** this file's SHA-256 is pinned in `tests/test_lh_stage_c.py` and recorded in the output JSON. It was committed before the audit script produced any aggregate. If the protocol changes after that commit, the change must be disclosed as an amendment, with the reason.

**Pre-protocol inspection (disclosed):**
- Only file formats and structures were inspected before this protocol: the E981-01 export layout, the Data v2.1 table keys and form codes, the companyfacts / submissions row layout, and the timezone-convention counts.
- While checking the submissions row layout, two sample rows were printed (Apple 8-K and 10-Q metadata dated 2026: dates and accession numbers, no values). This was post-2021 metadata. It enters no statistic, and rule 1.2 below removes every such row at load.

## 1. Scope and sources

1. **Decision reviews:** the 131 monthly reviews 2011-01 … 2021-11 (`qresearch.data_v3.review_days()`).
   - T = the review's month-end session.
   - D = the selection day, the calendar day after T.
   - Year of a review = year of T.
   - Periods: 2011–2014, 2015–2017, 2018–2021.
2. **Time cut-off:** every SEC fact, filing or submissions row with a filing date after **2021-12-31** is discarded **at load**, before any use. No 2022+ value, date or metadata enters any computation. The Holdout is never touched.
3. **Sources (read-only; SHA-256 recorded in the output):**
   - **Universe:** E981-01 (X981) universe export (`experiments/E981-01/result.json`). Every security ever eligible at a month start 2010–2021 in the frozen data-v1 universe (≥ $2B market cap, price ≥ $5, ADV ≥ $5M, US common stock, SEC correction layer): eligible-month bitmask, dated tickers, CIKs.
   - **Data v2.1 reference table** (`qr_data_v21.load_table()`; frozen D207, manifest `ef0a7a66…`):
     - identity rows (`sec_v1.sic_history`: security → dated (SIC, CIK)) and verified extension rows (`ext`);
     - per-registrant filing tables `f` (period ends, original 10-Q / 10-K filing days; form codes 1 = 10-Q, 2 = 10-K / 10-KT, 3 / 4 = amendments).
   - **Data v3** frozen manifest (`research/phase14/data_v3/data_freeze_v3.json`, D230) and its reference (`data_v3_reference.json`): guard counts (descriptive). The value rules are in `qresearch.data_v3`, used unchanged.
   - **SEC company facts** (cached under `data/sec_cache`, cache-only client with networking disabled), through `qresearch.data_v3.Facts` (filed ≤ 2021-12-31). If a CIK has no cached file, it is counted as missing, never fetched.
   - **SEC submissions** (same cache, cache-only): 8-K rows with items, filingDate, acceptanceDateTime, isXBRLNumeric; and periodic-filing rows.
   - **Time-zone conventions** `research/phase2/earnings_audit/tz_conventions.json` (D122), via `qresearch.sec_events.acceptance_et`.
   - **Session calendar:** dates of `experiments/E981-01/equity.csv.gz` (2010-01-04 … 2021-12-31), plus 2022-01-03 as the next session (a date only; the same convention as `earnings_event_audit.calendar`).
   - **Event Data v1** (`research/phase2/h017/event_table_v1.csv.gz`): count cross-check only.

## 2. Population denominator

1. **Eligible stock-month:** (security s, review r) where s is eligible in E981-01 at the **month start following T_r**, the start of the trade month.
2. **Registrant (PIT):**
   - the CIK of s's latest Data v2.1 identity row with effective date ≤ D;
   - otherwise the extension row if its start ≤ D;
   - otherwise **no SEC identity** (a missing reason; the stock-month stays in the denominator).
3. **Sector:** the SIC of that identity row. Financials are SIC 6000–6999.
4. **Primary denominator (U_NF):** eligible stock-months that are not financial. Stock-months with no identity or no SIC stay in U_NF and count as missing (conservative). **Secondary (U_ALL):** every eligible stock-month.
5. **Company-level coverage:** a security counts as covered in a period if at least one of its U_NF stock-months in that period is input-complete. Also reported: the share of securities input-complete in ≥ 50% of their U_NF stock-months.
6. **Known limitation:** this is the **Data v1 universe**. The Data v2.1 per-stock-month universe (repaired market caps on QuantConnect's current dataset) exists only in-host and was never exported. Reconstructing it offline would need price data or a QuantConnect run, which are not approved. The difference is disclosed, not repaired (P7-CP5e: survivor share v1 83.3% vs v2 84.1%).

## 3. Anchor, availability and values (frozen Data v3 rules, unchanged)

1. **Visible periods at D:** periods p of the registrant's Data v2.1 filing table that have an original 10-Q / 10-K with filing day fd and fd + 1 ≤ D. Amendment-only periods are not visible.
2. **Anchor p0** = the latest visible period. It is **fresh (Data v3 rule)** if D − p0 ≤ 200 days. Otherwise there is no anchor (missing reason "stale or none").
3. **Values as known at D:**
   - quarterly flows: `Facts.q_known(con, p, D − 1)` (direct three-month fact, else the year-to-date difference; never a year-to-date value as a quarter);
   - total assets: `Facts.ta_known(p, D − 1)`.
   - Concepts and tags are the frozen `sec_pit.TAGS`: revenue, gross_profit, net_income (operating_cash_flow and total_assets as in Data v3).
4. **Chain:** `data_v3.chain_back(visible, i0, n)`, i.e. n visible periods with consecutive gaps of 80–100 days. q_k = the period k quarters before p0.
5. **Availability day** of a filing = fd + 1 (the SEC side of the frozen M2 rule).
   - The QuantConnect-stream first-seen day (the other side of max(...)) is not available offline. P7-CP5d measured it as the day after filing in 96–99% of cases.
   - Offline availability is therefore a **lower bound**.

## 4. Candidate input sufficiency (exact RM2 §11 formulas; no value is combined into a surprise)

| Candidate | Required inputs (all known at D on one chain) | Chain length |
|---|---|---|
| C1 SUE-NI | NI at q0 … q12. The current seasonal difference needs q0 and q4; the 8 prior seasonal differences Δ_k = NI_{q_k} − NI_{q_{k+4}}, k = 1 … 8, need q1 … q12 | 13 |
| C2 SUE-REV | Revenue at q0 … q12 | 13 |
| C3 price-scaled | NI at q0 and q4 (5-quarter chain), plus PIT market cap at the prior month-end | 5 |
| C4 acceleration | X at q0, q1, q4, q5 (6-quarter chain). Counted for X = revenue (C4-REV, the H029 F1 form) and X = NI (C4-NI). The scaling input is unspecified in RM2, so total assets at q4 > 0 is reported as an add-on | 6 |
| C5 GP surprise / assets | GP at q0 and q4, plus total assets at q4 > 0 (5-quarter chain) | 5 |
| C6 dual | C1 and C2 both input-complete | 13 |

- **Not computed, by design:** the standard deviation, the drift and the surprise. A zero-variance history is therefore not detected; this is stated as a limitation.
- **C3 market cap:** it exists by construction for every eligible stock-month (eligibility requires ≥ $2B), but its value is in-host only. C3 is therefore "CONDITIONAL — in-host input".

**Descriptive sensitivities (never a substitute for the primary rule):**
- C1 / C2 with 4 prior differences (chain 9) and 12 prior differences (chain 17);
- C1 / C2 allowing up to 2 of the 13 values missing on a contiguous 13-period chain;
- C3 / C5 without contiguity: q4 = the visible period whose end is 350–380 days before p0, no intermediate chain required.

**Missing-reason hierarchy** (first reason that applies):
1. financial (U_ALL only);
2. no SEC identity;
3. no filing table;
4. no fresh anchor;
5. chain too short or broken (insufficient history);
6. value missing at a required quarter;
7. invalid denominator (total assets ≤ 0 for C5 and the C4 add-on).

## 5. Data-quality and integrity metrics (descriptive)

1. **Per field** (revenue_q, net_income_q, gross_profit_q):
   - earliest / latest period end with a known value among population registrants;
   - share of U_NF stock-months whose anchor value is known;
   - k-quarter chain availability for k = 1, 5, 6, 9, 13, 17;
   - company coverage;
   - all by year and by period.
2. **Q4 derivation:** among anchor periods with a known value, the share obtained from a year-to-date difference instead of a direct three-month fact.
3. **Quarter duration:** among consecutive visible-period gaps of population registrants:
   - the share outside 80–100 days (chain breaks);
   - the share at 95–100 days (14-week quarters, 52/53-week years).
4. **Fiscal-year changes:**
   - registrants with more than one fiscal-year-end code in `xbrl_filings.json.gz` (filing-time metadata, filings ≤ 2021);
   - among input-complete C1 / C2 chains, the share whose q0 and q4 (or q12) filings carry different fiscal-year-end codes.
5. **Vintage and restatement:**
   - among input-complete C1 / C2 chains, the share with any value as known at D different (> 1.5%) from that period's first-filed value: recasts known by D, PIT-legal;
   - the share with any value later restated (> 1.5%, filed after D and ≤ 2021-12-31): a value that a vendor feed might carry early;
   - Data v3 guard counts reported from the frozen reference.
6. **PIT assertion:** every fact used at D has a filing date < D (asserted in code; violations counted and expected to be 0).
7. **Non-comparable cases** (descriptive):
   - anchor quarters with NI ≤ 0, and with any NI ≤ 0 in a C1 chain;
   - anchor quarters with a non-zero discontinued-operations fact (`IncomeLossFromDiscontinuedOperationsNetOfTax` or `IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity`) ending within ±7 days, as known at D;
   - C1 / C2 chains containing a period ending 2017-10-01 … 2018-01-31 (the US tax-reform remeasurement quarter for most filers).
8. **Identity:**
   - share of U_ALL stock-months with an SEC identity (v2 row or extension);
   - share of identity CIKs with a cached companyfacts / submissions file;
   - E981-01 CIK vs Data v2.1 identity CIK agreement (descriptive).

## 6. Earnings-release matching and delays

1. **Event set:**
   - the distinct (registrant, anchor period p0) pairs that are the anchor of at least one U_NF stock-month;
   - with **first use** = the first review r at which p0 is the anchor while s is eligible;
   - an event is "first-use timely" if r is the first review with fd + 1 ≤ D_r (otherwise eligibility, not timing, delayed it; counted, and excluded from the wait statistics);
   - year of an event = year of its availability day.
2. **Periodic filing:**
   - the submissions row of form 10-Q / 10-K / 10-KT (not amendments) with filingDate = fd and reportDate within ±7 days of p0;
   - acceptance time from that row (`acceptance_et` with the registrant's measured convention; UNRESOLVED / UNMEASURED → time unknown);
   - if no row matches, the time is unknown and only the date is used.
3. **Item 2.02 candidates:**
   - submissions rows of form **8-K** (8-K/A ignored, as in Event Data v1) whose items contain "2.02";
   - with filingDate in the window **(p0, fd]**: after the period end, on or before the periodic filing day.
4. **Classification:**
   - **unambiguous** = exactly one candidate;
   - **ambiguous** = two or more (reported separately; delays computed with the earliest);
   - **none in window** = zero. Sub-classified as "release after filing" if an Item 2.02 8-K is filed in (fd, fd + 10], else "no release found".
   - **Not determinable** = no cached submissions for the registrant.
5. **Delays** (each in calendar days, and in trading sessions where marked; sessions(a, b) = number of sessions s with a < s ≤ b):
   - **A** period end → release date (days, sessions);
   - **B** release date → periodic filing date (days, sessions). Same-day pairs are ordered by acceptance time when both are known (release first / filing first / unknown order);
   - **C** periodic filing → Data v3 availability: by rule exactly +1 calendar day offline (fd + 1). The in-host first-seen distribution is cited from P7-CP5d, not recomputed;
   - **D** availability → first review: days from availability to the first selection day D_r ≥ availability; sessions from the first session ≥ availability to the review's trade session (the first session after T_r);
   - **E1** release → first possible trade using the filing (daily decisions): the first session strictly after fd, measured in sessions from the release's own earliest trade (the first session strictly after the release date). Sessions are also reported from the release date;
   - **E2** release → first monthly-review trade using the filing: the trade session of the first review with D_r ≥ fd + 1, in sessions from the release date.
6. **Execution convention:**
   - a filing (or release) dated d is usable at the selection stamped after the session on or after d;
   - the earliest order is the open of the first session strictly after d;
   - this is the frozen Data v3 / universe-selection convention (selection is stamped the calendar day after the session; CLAUDE.md quirks). No intraday execution.
7. **Statistics for every delay:** n, median, mean, p10, p25, p75, p90, p95, plus the missing-event rate (none in window or not determinable) and the ambiguous rate. Reported overall, by period and by year (median and n).
8. **Disclosure categories (Part C §10)** for each event:
   - **1 "definitely known earlier (disclosure event)":** an unambiguous Item 2.02 8-K accepted before the periodic filing (an earlier date, or the same date with an earlier known time). The release's numeric content is **not verified**: release exhibits are unstructured, and this audit does not parse them;
   - **2 "potentially known earlier":** ambiguous candidates before the filing, or the same date with unknown order;
   - **3 "first verifiable through the structured filing":** no Item 2.02 8-K in (p0, fd + 10] while the registrant's submissions are cached;
   - **4 "cannot be determined":** no cached submissions, or the release filed after the periodic filing.
   - **Machine-readability check:** the share of matched Item 2.02 8-Ks flagged `isXBRLNumeric = 1` in submissions metadata.
9. **Wait and freshness metrics** (Part B §7):
   - median and p90 wait (days, sessions) from availability to the first review;
   - the share of first-use-timely events traded within 5, 10, 20 and 30 sessions after availability (the first session ≥ availability = session 0);
   - **freshness at review over U_NF stock-months with an anchor:** the share whose anchor's availability is more than 91 days before D (stale under the RM2 one-quarter rule), alongside the Data v3 200-day period-age rule.

## 7. Survivorship and missingness (descriptive)

C1, C2, C3 and C5 input-completeness over U_NF stock-months is split by:
1. **Size tercile within the review:** SEC total assets as known at D on the anchor (unknown → its own group). No market data is used.
2. FF12 sector.
3. **Leavers vs stayers:** securities whose last E981-01 eligible month is before 2021-12 vs those eligible in 2021-12.
4. **Newcomers:** stock-months within the first 12 eligible months of a security first eligible after 2011-01 vs all others.
5. Securities with any amendment-only or late (filed > 90 days after period) periodic filing in the window vs others.

Existing survivorship limitations are cited from committed records (D113, D187, D189, D192, P7-CP5e, D207 / D213).

## 8. Judgements and provisional thresholds (fixed now; labelled)

**Coverage floor:** input-complete in ≥ 70% of U_NF stock-months in **each** year 2013–2021. Label: **PROVISIONAL FEASIBILITY THRESHOLD — OWNER REVIEW REQUIRED**. A sensitivity at 60 / 65 / 75 / 80% is descriptive only.

**Per candidate:**

| Attribute | Rule |
|---|---|
| PIT correctness | PASS if the PIT assertion has 0 violations, the inputs come only from frozen Data v3 rules (filed ≤ D − 1, fd + 1 ≤ D) and the in-host guard covers the input fields (revenue, GP, NI, TA: guard v3); else FAIL. C3: UNKNOWN for its market-cap input (in-host only) |
| Historical-depth sufficiency | PASS if the floor holds in every year 2013–2021; FAIL if not |
| Timestamp quality | PASS if ≥ 95% of U_NF anchors have an original filing day in the Data v2.1 filing table (by construction) and ≥ 90% of events have a matched periodic-filing submissions row; else UNKNOWN |
| Quarterly-chain integrity | PASS if, among input-complete chains, ≤ 1% have a fiscal-year-end code change between q0 and its comparison quarter; FAIL if > 1%; UNKNOWN if fewer than 50% of chains have fiscal-year-end codes |
| Ability without purchase | YES for C1, C2, C4, C5, C6; CONDITIONAL for C3 (in-host market cap) |

**Suitability for later signal research:**
- **FEASIBLE:** PIT PASS, depth PASS, timestamps PASS and chain PASS.
- **CONDITIONAL:** no FAIL other than depth, with every year 2013–2021 ≥ 60%; or an UNKNOWN that a known in-host input explains.
- **NOT FEASIBLE:** otherwise.

**Information timeliness:**
- Over unambiguous events: if ≥ 50% have an earlier Item 2.02 release **and** the median E2 (release → first monthly-review trade) exceeds **20 trading sessions**, timeliness is a **MATERIAL DESIGN ISSUE**.
- The 20 sessions are one third of the 60-session drift window of the committed H017 design (Bernard & Thomas). The threshold is **PROVISIONAL — OWNER REVIEW REQUIRED**.
- It is a statement about delay, **not** about profitability.

**Classification:**

| Class | Rule |
|---|---|
| D — INSUFFICIENT EVIDENCE | Any one of: identity coverage of U_ALL stock-months < 80%; cached submissions for < 80% of event registrants; cached companyfacts for < 80% of identity CIKs |
| A — DATA FEASIBLE | Not D, and at least one of the independently justified surprise families C1, C2, C5 or C6 is FEASIBLE, and timeliness is not a MATERIAL DESIGN ISSUE. C4 counts as H029-related; C3 is conditional by construction |
| B — CONDITIONALLY FEASIBLE | Not D or A, and at least one of C1, C2, C5 or C6 is FEASIBLE or CONDITIONAL (including the case where timeliness is a MATERIAL DESIGN ISSUE) |
| C — NOT FEASIBLE | Otherwise |

**Economic usefulness: NOT TESTED** (no returns).

## 9. Known limitations (stated in advance)

- The denominator is the Data v1 universe (§2.6).
- Offline availability is a lower bound (§3.5).
- Release contents are not parsed (§6.8).
- σ and surprises are not computed (§4).
- Submissions acceptance-time conventions are unresolved for some registrants (time unknown → date-level only).
- Some identities are not dated before a registrant's first XBRL filing (D189 extension); missing identities are counted, not imputed.
- Using a newer cached companyfacts snapshot can only add facts filed ≤ 2021 that a contemporaneous snapshot would also have held (filing dates are fixed). Facts withdrawn later are a residual unknown.

## 10. Outputs

- `research/longhorizon/stage_c/LH_StageC_audit.py` (script);
- `research/longhorizon/stage_c/LH_StageC_audit.json` (aggregates only: counts, shares, distribution quantiles; no per-company values);
- `tests/test_lh_stage_c.py`;
- the checkpoint `docs/checkpoints/LH_CP1_stage_c_ofa_data_pit_feasibility_audit.md`.
