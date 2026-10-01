# Fundamental infrastructure readiness checkpoint (P2-CP5)

- **Date:** 2026-10-01.
- **Status: INFRASTRUCTURE ONLY** (D108). No H016 defined; no profitability formula, ranking, portfolio or return computed; no hypothesis slot used; the Holdout untouched. **STOP:** awaiting owner approval.

## Verdict (item 14)

**The data is not yet safe enough to define H016.**

**Built and verified:**
- The point-in-time fundamentals layer, the field whitelist with hard failure, the +90-day rule, the accession quarantine, the Visa correction and a point-in-time-safe financial classification.
- The canary found **zero rule violations in 3.42 million stock-days**.

**Two required items remain unresolved, and you said to stop rather than work around them:**
1. **SEC independent verification (§5): not performed.**
   - The environment's network policy still blocks `data.sec.gov` and `www.sec.gov` (connection refused by the proxy, 2026-10-01).
   - Allowlist changes take effect only in a **new** session.
2. **The survivorship gap (§7): not repaired.**
   - Large companies that later disappeared still have **no fundamentals and no market cap** in QuantConnect's data. So they never enter the universe: about 14% of true large companies in 2010, falling to about 1% in 2021.
   - They underperformed badly: those ending in distress averaged −28% a year (D043).
   - **The only point-in-time source for repairing them is SEC EDGAR**, which is blocked here.

Both blockers have the same cause, and the same fix (§15, decision 1).

## 1. Point-in-time fundamentals-layer design

**Code:** `src/qresearch/lean/qr_fundamentals.py`. It is uploaded with every QuantConnect project and is reusable by any fundamental hypothesis. Its pure logic is tested offline.

**Feeding:** each day the strategy feeds the vendor's latest report per eligible stock into `PITStore.observe(...)`. It reads only through `record()` and `get()`, which return what was **historically available on that date**.

| Behaviour | Rule |
|---|---|
| Availability | Visible only from the day **after** the filing date (and never before it, even if queried out of order) |
| Estimated filing dates | File date exactly period end + 45 days (the documented vendor approximation): visible only from **period end + 90 calendar days** |
| Accession anomaly | Accession year later than the decision year: **quarantined**, never exposed. The previous clean report stays in use |
| Amendments / restatements | Same period, later file date: replaces the earlier record only from its own availability date |
| Stale-but-current | A record stays usable while ≤ 200 days past its period end (a quarterly filer refreshes about every 91 days). Strategy specs may only tighten this |
| Missing values | NaN or 0 is returned as None. Nothing is filled |
| Impossible or unknown timing | File date before period end, or a missing date: never exposed |
| Field enforcement | Only whitelisted fields can be requested. Anything else raises `FundamentalFieldError` (hard failure) |
| Universe | Unchanged harness point-in-time universe (≥ $2B market cap, D057/D059/D065 safeguards), plus the dated Visa correction |
| Delistings and acquisitions | Handled by the universe. A delisted company stops being eligible, so the layer is not consulted for it |

## 2. Approved field whitelist

All are statement totals, quarter and/or trailing twelve months:
- revenue (ttm, q), gross profit (ttm, q), cost of revenue (ttm), operating income (ttm, q), net income (ttm, q);
- total assets, stockholders' equity, total debt (quarter-end);
- operating cash flow (ttm, q), free cash flow (ttm);
- **plus point-in-time `market_cap`.**

## 3. Unsafe-field blacklist (hard failure if requested)

| Category | Fields |
|---|---|
| Share counts | `shares_outstanding`, `share_class_level_shares_outstanding`, `ordinary_shares_number`, `share_issued`, `basic_average_shares`, `diluted_average_shares` |
| Per-share values | `basic_eps`, `diluted_eps`, `book_value_per_share` |
| Vendor ratios | `roa`, `roe`, `roic`, `gross_margin`, `operation_margin`, `pe_ratio`, `pb_ratio` |
| Provenance | `accession_number` |
| Current-status metadata | `fiscal_year_end`, `morningstar_sector_code`, `morningstar_industry_code` |

Any field not on the whitelist is also refused.

## 4. Estimated filing-date handling

- **Rule:** an estimated date (exactly period end + 45 days) makes a report visible only from **period end + 90 days**.
- Annual and quarterly reports are treated the same:
  - 90 days is the latest regular 10-K deadline (non-accelerated filers);
  - every 10-Q deadline is 40–45 days.
- **Measured over 2010–2021:**
  - 1,060 estimated reports;
  - 993 were delayed beyond the vendor's date;
  - 0 exposed before period end + 90.
- **Residual risk:** a late filer using an NT 10-K extension may file up to 105 days after year end, so an estimated annual report could still be about 15 days early. This cannot be demonstrated or ruled out without SEC dates. If SEC data shows it, the rule tightens to +105 for annual reports.

## 5. SEC verification results

**Not performed. Blocked by the network policy.** Every planned check is therefore **unresolved**.

| Sample type | Planned check | Status |
|---|---|---|
| Normal quarterly filing (e.g. a 10-Q) | Period, filing date, value, layer exposure date | Unresolved |
| Normal annual filing (10-K) | Same | Unresolved |
| Amended filing (10-Q/A, 10-K/A) | Original vs amended value and dates | Unresolved |
| Delayed filing (e.g. Kraft Heinz's 2018 10-K) | Late date honoured | Vendor/documentation-supported (the date matches; not verified externally) |
| Restatement | Originally filed vs restated value | Unresolved |
| Stock split | Statement totals unaffected; share levels restated (vendor) | Our own measurement confirmed share-level restatement; totals vs SEC unresolved |
| Acquisition/delisting | Last filing vs last eligibility | Eligibility confirmed in data (Monsanto, DirecTV); SEC side unresolved |
| 2010–2012 estimated filing date | True filing date vs period end + 90 | Unresolved |

**What is required:** `data.sec.gov` and `www.sec.gov` allowed in the environment's network settings, and a new session.
- SEC asks for a contact identifier in the request header. I'll use a project identifier (`QuantTradingResearch PIT-audit`), plus an email only if you supply one for this purpose.
- The EDGAR XBRL "company facts" data lists every filing that reported each value, with its filing date. That gives original-vs-restated values directly.

## 6. Restatement and accession anomaly resolution

- **Quarantined:** 213 reports (0.35% of 60,008 new reports) from 168 companies. They are never exposed, and the previous clean report is used if it is still fresh.
- **By year:**

| Year | Quarantined reports |
|---|---|
| 2010 | 159 |
| 2011 | 39 |
| 2012 | 9 |
| 2013 | 5 |
| 2014 | 1 |
| 2015–2021 | 0 |

- Stock-months withheld by the timing rules (quarantine or the +90 wait): 2 to 19 per year.
- **Whether those values are originals or later restatements cannot be determined without EDGAR.**
  - Under your rule they are **excluded, not silently admitted**.
  - The quarantine is conservative: it may also drop some valid originals.
- No silent overwrites in either audit; amendments arrive as later filings (23 seen by the layer).

## 7. Survivorship-gap status: UNRESOLVED (blocker)

**Measured (D043, two independent methods agreeing within about 2 points):**

| Year | Missing share of true ≥ $2B companies | Year | Missing share |
|---|---|---|---|
| 2010 | 14.1% | 2016 | 4.4% |
| 2011 | 11.5% | 2017 | 4.8% |
| 2012 | 12.4% | 2018 | 3.7% |
| 2013 | 10.5% | 2019 | 4.4% |
| 2014 | 8.3% | 2020 | 3.3% |
| 2015 | 6.7% | 2021 | 1.2% |

**Which companies:** examples include Time Warner, Heinz, Precision Castparts, SanDisk, old DuPont, BB&T, old Alcoa, Sears Holdings, JCPenney, old Chesapeake, Weatherford and old Hertz (`docs/data/survivorship_gap_2010.md`).
- The canary reconfirms Time Warner was never eligible.

**Why they are missing:** QuantConnect's Morningstar data has **no fundamental record (and so no market cap)** for securities that stopped trading before the vendor snapshot. Their prices are present; their eligibility is not.

**Bias (D043, measured on 2010–2017):**
- The missing names returned −28.4% a year (later distress) and +7.5% (later merged), against +11.3% for the universe.
- This flatters the equal-weight universe by about +1.4 points a year.

**For quality research the direction relative to equal-weight is ambiguous:**
- Both the candidate and the benchmark lose the later-failing companies.
- But avoiding exactly such companies is what a quality strategy claims to do, so its measured advantage over equal-weight could be **understated or overstated**, depending on how many of the missing names it would have held. This cannot be settled without the missing data.

**Within the data we do have:** missingness is concentrated in companies that delist within 12 months (83.7% usable vs 99.0% for others). That is small in count (652 stock-months), but it points the same way.

**Can it be repaired without future information? Yes, from SEC filings only.**
- Point-in-time market cap = shares on the cover page of each filing (as filed, on its filing date) × the raw price we already have.
- Statement totals = XBRL values as first filed, dated by filing date.
- This is a **dated historical correction** that uses no current-company status.
- It is blocked here (§5).

## 8. Visa correction implementation

- **What:** a dated `EXCHANGE_OVERRIDES` entry in the harness: Visa Class A (`V U12VRGLO8PR9`) is NYSE from **2008-03-19** (its NYSE IPO). The vendor label `OTCM` is ignored only from that date.
- **Scope:** future runs only. C01–C03, H014 and all earlier benchmarks remain as recorded.
- **Documentation and tests:** `docs/data/universe_overrides.md`; a unit test covers both sides of the date and confirms no other security is affected.
- **Canary:** Visa is eligible in **143 of 144** months; the first is the universe's liquidity warm-up.

## 9. Historical financial-sector exclusion method

**Vendor classification is not point-in-time.** Across 2,525 companies over 12 years:
- the Morningstar sector code changed **8** times;
- the statement template code changed **0** times.

That reflects present-day labels, so they are **not used**.

**Method: a point-in-time "financial-format" rule from each filing's own structure.** A report is financial-format if it shows revenue but **no gross profit, no cost of revenue and no operating income**, the bank/insurer statement layout.
- It is evaluated on each report as filed, so it is point-in-time by construction.
- **Agreement with vendor templates:** 98.1% of financial-format reports carry the bank or insurance template. 98.3% of bank/insurance-template reports are classified financial-format.
- It keeps financial companies with comparable operating accounts (asset managers, exchanges, payment networks) in the universe.
- **Excluded share: 9–12% of eligible stock-months a year.**
- **Fairness:** the rule is a universe filter. Any H016 candidate, its equal-weight benchmark and all controls must be computed on the same non-financial universe.

## 10. Updated 2010–2021 coverage

Eligible stock-months, after the layer's rules.
- **Usable** = a point-in-time record with revenue, net income, assets and equity.
- **Missing** = any reason a usable record is not available.

| Year | Eligible | Usable | Usable % | Withheld (unsafe timing) | No filing data | Missing fields | Stale | Financial-format (excluded) |
|---|---|---|---|---|---|---|---|---|
| 2010 | 8,261 | 8,207 | 99.3% | 7 | 0 | 0 | 47 | 922 |
| 2011 | 10,112 | 9,848 | 97.4% | 19 | 0 | 4 | 241 | 1,049 |
| 2012 | 10,307 | 10,270 | 99.6% | 12 | 0 | 3 | 22 | 1,117 |
| 2013 | 11,831 | 11,773 | 99.5% | 13 | 1 | 14 | 30 | 1,212 |
| 2014 | 13,451 | 13,362 | 99.3% | 4 | 3 | 40 | 42 | 1,409 |
| 2015 | 14,031 | 13,891 | 99.0% | 3 | 8 | 83 | 46 | 1,534 |
| 2016 | 13,618 | 13,548 | 99.5% | 0 | 0 | 26 | 44 | 1,511 |
| 2017 | 14,860 | 14,730 | 99.1% | 4 | 2 | 66 | 58 | 1,727 |
| 2018 | 15,672 | 15,527 | 99.1% | 3 | 3 | 92 | 47 | 1,877 |
| 2019 | 15,493 | 15,394 | 99.4% | 1 | 1 | 69 | 28 | 1,836 |
| 2020 | 15,493 | 15,268 | 98.6% | 3 | 6 | 165 | 51 | 1,606 |
| 2021 | 19,492 | 19,014 | 97.6% | 2 | 90 | 281 | 105 | 1,925 |

**The table omits the survivorship-gap companies (§7).** They are absent from "eligible" itself, which is exactly the problem: an estimated 1–14% of true large companies a year are missing.

**Where the measurable missingness concentrates:**
- **Later-delisted firms:** 83.7% usable vs 99.0%.
- **Small companies** (bottom tercile of the universe): 98.3% vs 99.3% for the top tercile.
- **Early years:** 2011 has a stale-record cluster (97.4%).
- **By vendor sector:** financials 99.5% vs others 98.8% usable, before the financial-format exclusion.

## 11. Data canary results (E969-01, 2010–2021, 3.42 million stock-days, no orders)

| Check | Result |
|---|---|
| A filing never appears before its availability date | ✔ 0 violations (0 before filing, 0 before availability) |
| Estimated filings respect +90 days | ✔ 0 violations (1,060 estimated, 993 delayed) |
| Amendments visible only when filed | ✔ 0 early (23 amendments) |
| Unsafe share counts inaccessible | ✔ every blacklisted name is rejected; no share, EPS or ratio path on the whitelist |
| Unapproved fields fail hard | ✔ rejected (`FundamentalFieldError`) |
| Visa enters the universe on the corrected dates | ✔ 143/144 months eligible (first month = warm-up) |
| Known acquired/delisted companies available while appropriate | ✔ Monsanto until 2018-06 (deal 2018-06-07); DirecTV until 2015-07 (deal 2015-07-24). ✘ Time Warner never (D043 gap) |
| Financial-company exclusion historically correct | ✔ point-in-time rule; 98% agreement with bank/insurance templates; vendor sector shown to be current-status |
| Stale statements only under the freshness policy | ✔ 0 stale records exposed |
| Quarantine of accession anomalies | ✔ 213 reports (168 companies) never exposed |

Earlier audit runs (D107) also stand: E967-02 and E968-01.

## 12. Automated test results

**All 449 tests pass.** New or extended this round:
- `tests/test_pit_fundamentals.py` (12 tests):
  - whitelist and blacklist hard failures;
  - visibility only after filing;
  - +90 for estimated dates, with the previous report kept meanwhile;
  - quarantine counted once and never exposed;
  - amendment timing;
  - freshness;
  - unknown or impossible timing;
  - missing values;
  - whitelist-only reads;
  - the financial-format rule;
  - accession parsing.
- `tests/test_universe_classification.py`: the dated Visa correction.
- `tests/test_fundamental_audit.py`: audit helpers.

## 13. Remaining unresolved risks

1. **Survivorship gap (blocker):** about 1–14% of true large companies missing a year, disproportionately later failures. The bias direction relative to equal-weight is ambiguous for quality research.
2. **SEC verification (blocker):** the vendor's "as originally reported" claim, true filing dates and estimated dates are unverified.
3. **Quarantine is conservative but blind:** 213 reports are excluded without knowing whether they are original or restated.
4. **Late filers with extensions:** an estimated annual date could still be up to about 15 days early.
5. **The universe still relies on current-status company flags** for D057 classification (partly corrected by dated overrides, D065).
6. **Early-year concentration:** quarantine and the estimated-date approximation cluster in 2010–2012, where the survivorship gap is also largest.

## 14. Is the data safe enough to define H016?

**No, not yet.** Timing semantics, field safety, financial classification and the Visa correction are ready and verified.

Two items you set as preconditions remain unresolved:
- the survivorship gap;
- SEC verification.

Both can be resolved **only with SEC EDGAR access**. As instructed, I stop here rather than work around them.

## 15. Owner decisions still required

1. **Enable SEC EDGAR access.** Add `data.sec.gov` and `www.sec.gov` to the environment's allowed network domains, then start a new session. Optionally provide a contact email for the SEC User-Agent; otherwise the project identifier is used. **This unblocks both open items.**
2. **Approve the next infrastructure step under that access** (no slot; no strategy):
   - (a) SEC verification of the sample in §5;
   - (b) a dated, EDGAR-based **survivorship correction**: point-in-time market cap and statement totals as first filed, for the missing large companies, fed into the same layer and universe.
   - I would report whether the correction covers the gap sufficiently before any H016 design.
3. **Alternative, if you prefer not to repair:** decide whether quality research may proceed with the gap disclosed and bounded. I do **not** recommend this, because the bias direction for a quality strategy is ambiguous. The other option is to stop fundamental research.
4. **Confirm the policies built here:**
   - the 200-day freshness limit (specs may only tighten it);
   - quarantine of accession anomalies;
   - the filing-based financial-format exclusion as the point-in-time-safe financial rule.

**STOP.** No H016, no profitability formula, no strategy or factor backtest, no slot used, Holdout locked.
