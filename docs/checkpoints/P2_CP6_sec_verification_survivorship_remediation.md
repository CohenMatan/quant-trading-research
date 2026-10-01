# P2-CP6 — SEC Verification and Survivorship Remediation Checkpoint

- **Date:** 2026-10-01.
- **Scope:** infrastructure only. The owner approved this phase on 2026-10-01; the message is recorded in `docs/owner/2026-10-01_SEC_verification_survivorship_approval.md`.
- **Not done in this phase:**
  - H016 was not defined.
  - No profitability or quality metric was chosen or compared.
  - No ranking, portfolio, strategy backtest or factor return was computed.
  - No hypothesis slot was used; Phase 2 is still at 1 of 3 slots consumed, with 2 remaining.
  - The Holdout was not accessed: every run ends on 2021-12-31.
- **Earlier results:** none were rewritten. The new layer is opt-in, and earlier runs stay exactly as recorded.
- **Status:** STOP, awaiting owner approval.

## Summary in plain words

**Verdict (item 17): NOT YET SAFE to design H016**, although most of the data is now independently verified.

What is now verified against the SEC and protected in code:

- **Filing timing.**
  - 56,045 vendor reports could be matched to SEC filings.
  - 55,928 of them become visible only after the SEC 10-Q or 10-K was public.
  - 62 become visible after the company's earnings release (an 8-K) but before the 10-Q or 10-K.
  - **55 reports (0.1%) would have been visible before any public SEC source.** These are now held back to the SEC date ("timing holds").
- **Statement values.** Balance-sheet totals, quarterly figures and fiscal-year figures match the SEC "as first filed" values in 91–99% of cases, field by field.
- **Restated values (look-ahead found and blocked).**
  - 479 vendor reports (0.8%) carry a figure that was only published later, in a restatement. Kraft Heinz-style delays are handled; KBR's 2012 quarters, for example, carried values from its 2014 restatement.
  - These reports are now blocked.
- **Market-cap method.** The method rebuilds market cap from SEC share counts × QuantConnect price. Tested on 406 companies, it matches the vendor's own figure exactly in the median. It gives the same answer at the $2B line 99.8% of the time.

Why not yet:

1. **The survivorship gap is reduced, not closed.**
   - 163 securities that QuantConnect had no fundamentals for are now repaired from SEC filings. 108 of them enter the ≥$2B universe.
   - The estimated share of missing large companies falls as follows:

     | Year | Before repair | After repair |
     |---|---|---|
     | 2010 | 14.1% | 11.4% |
     | 2011 | 11.5% | 5.9% |
     | 2012 | 12.4% | 8.0% |
     | 2015 | 6.7% | 4.2% |
     | 2021 | 1.2% | 0.5% |

   - Roughly 26–62% of the gap is repaired, depending on the year.
   - The rest cannot be reliably identified without SEC ticker histories. Those live on `www.sec.gov`, which refuses requests from a client that gives no contact email (see item 1).
2. **New finding: a definitional issue with the vendor's twelve-month fields.**
   - On a quarterly report, the vendor's "twelve-month" values (revenue, net income, operating cash flow, …) are **the last completed fiscal year's totals**, not rolling twelve months. They can be up to about 15 months old.
   - This is not look-ahead. But any profitability measure would silently use annual data refreshed once a year.
   - You should decide how the data is to be read before H016 is written (item 18).

---

## 1. SEC-access status

| Host | Result | What it means |
|---|---|---|
| `data.sec.gov` | **Works** (HTTP 200) with the project User-Agent `QuantTradingResearch PIT-audit private-research-project` | Company facts (every XBRL value with the filing that reported it), filing histories and frames: everything used here |
| `www.sec.gov` | Reachable through the network. But the SEC answers **403 "undeclared automated tool"** to every request whose User-Agent has no contact email | EDGAR archives (filing documents, XBRL instance files, Form 4 ticker histories) and the financial-statement data sets are **not available** with a project-only identifier |
| `www.quantconnect.com` | Works | Unchanged |

**How the data was fetched:**
- About 10,700 SEC responses were cached under `data/sec_cache/`, which is outside Git and can be re-downloaded by running the scripts again.
- Each URL was fetched once, at no more than 8 requests per second; the SEC limit is 10.

**Disclosure:** my very first reachability probe this session (three requests: QuantConnect, `data.sec.gov` and `www.sec.gov`) mistakenly put your account email in the User-Agent. All later requests used the project identifier only. No email is stored in code (a test checks this).

## 2. Verification-sample results

**Sample** (fixed seed; `research/phase2/sec/x971_sample.json`): 406 companies.
- All 168 companies with a quarantined report, and every company with an amendment.
- 80 companies with estimated filing dates, and 150 random eligible companies.
- Named cases:
  - stock splits: AAPL, NVDA, TSLA;
  - multi-class: Alphabet, Berkshire;
  - acquisitions: Monsanto, DirecTV;
  - a delayed filing: Kraft Heinz;
  - a bank, an insurer, Visa and Microsoft.
- 16,810 vendor reports were compared on QuantConnect (run E971-02).

**How the QuantConnect value is shown:** as a ratio to the SEC value. The licence forbids exporting the vendor's raw values; a ratio of 1.0 means equal.

| Case | Company | Period | SEC form | SEC filing date | Field | SEC value (as first filed) | QC value ÷ SEC | QC availability | PIT-layer exposure | Match | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Normal 10-Q | Microsoft | 2016-03-31 | 10-Q | 2016-04-21 | quarterly revenue | 20,531,000,000 | 1.000 | 2016-04-21 | 2016-04-22 | match | confirmed |
| Normal 10-Q | Microsoft | 2016-03-31 | 10-Q | 2016-04-21 | total assets | 181,869,000,000 | 1.000 | 2016-04-21 | 2016-04-22 | match | confirmed |
| Normal 10-K | Microsoft | FY to 2016-06-30 | 10-K | 2016-07-28 | annual revenue | 85,320,000,000 | 1.000 | 2016-07-28 | 2016-07-29 | match | confirmed |
| Normal 10-K | Microsoft | FY to 2016-06-30 | 10-K | 2016-07-28 | annual net income | 16,798,000,000 | 1.000 | 2016-07-28 | 2016-07-29 | match | confirmed |
| Amended filing | Marriott | 2012-09-07 | 10-Q (re-filed by the vendor 2012-11-14) | 2012-10-04 | total assets | 5,865,000,000 | 1.000 | 2012-11-14 | 2012-11-15 (only from the amendment's own date) | match | confirmed |
| Delayed filing | Kraft Heinz | FY 2018 | 10-K | **2019-06-07** (about 5 months late) | annual revenue | 26,268,000,000 | 1.000 | 2019-06-07 | 2019-06-08 | match | confirmed |
| Delayed filing | Kraft Heinz | FY 2018 | 10-K | 2019-06-07 | total assets | 103,461,000,000 | 1.000 | 2019-06-07 | 2019-06-08 | match | confirmed |
| Accounting restatement | KBR | 2012-06-30 | 10-Q | 2012-07-25 | quarterly revenue | 2,062,000,000 | 0.984 (equals the **2014 restated** figure: 10-K 2014-02-27 / 10-K/A 2014-05-30) | 2012-07-25 | 2012-07-26 → **now blocked** | mismatch | **unsafe (fixed: restatement guard)** |
| Stock split | Apple (7:1 on 2014-06-09) | 2014-06-28 | 10-Q | 2014-07-23 | quarterly revenue | 37,432,000,000 | 1.000 | 2014-07-23 | 2014-07-24 | match | confirmed (totals are unaffected by splits; cover count 5,987,867,000, after the split) |
| Acquisition / delisting | Monsanto (deal 2018-06-07) | 2018-02-28 | 10-Q | 2018-04-05 | total assets | 22,687,000,000 | 1.000 | 2018-04-05 | 2018-04-06 | match | confirmed (eligibility ends at the last trade) |
| Acquisition / delisting | DirecTV (deal 2015-07-24) | 2015-03-31 | 10-Q | 2015-05-08 | quarterly revenue | 8,143,000,000 | 1.000 | 2015-05-08 | 2015-05-09 | match | confirmed |
| Estimated filing date (vendor date = period end + 45) | Hospira | 2009-06-30 | 10-Q | 2009-07-29 | total assets | 5,288,900,000 | 1.000 | 2009-08-14 (estimated) | 2009-09-29 (period end + 90) | match | confirmed (exposure after the true filing) |
| Quarantined, valid | Analog Devices | FY to 2010-10-30 | 10-K | 2010-11-22 | total assets | 4,328,831,000 | 1.000 | 2010-11-22 | never → **released** | match | confirmed |
| Quarantined, restated | Emerson | 2010-06-30 | 10-Q | 2010-08-04 | total assets | 22,958,000,000 | 0.946 | 2010-08-04 | never | mismatch | unsafe (kept quarantined) |
| Quarantined, mixed period | Exelon | 2010-06-30 | 10-Q | 2010-07-22 | total assets | 49,173,000,000 | 1.032 (equals the **previous** quarter's balance sheet) | 2010-07-22 | never | mismatch | vendor-supported but not independently confirmed (kept quarantined) |

**Status classes across the whole sample:**

- **Confirmed:** values equal the SEC original and are exposed after the SEC filing date. This covers about 92–99% of the balance-sheet, quarterly and fiscal-year comparisons (item 4).
- **Vendor-supported but not independently confirmed:**
  - About 4.5% of all reports could not be tied to an SEC filing. The causes:
    - the vendor's CIK is the company's present-day successor (1,434 reports, e.g. Disney, Dow, Cigna);
    - the company is a foreign filer with no 10-Q or 10-K (924 reports, e.g. Check Point, Qiagen);
    - the period was not found under that CIK (325 reports).
  - The vendor's own operating-income definition also falls here: it matches the SEC tag for only 48%.
- **Unresolved:** 34 quarantined records in pre-XBRL periods (there is no SEC XBRL data to compare).
- **Unsafe:**
  - 479 reports carrying later restated values: now **blocked**;
  - 55 reports with a vendor date before any SEC source: now **held**;
  - 20 quarantined records with restated values: **kept quarantined**.

## 3. QuantConnect-vs-SEC timing results (all 60,008 vendor reports, 2010–2021)

**How the comparison was made:**
- Every report was matched to the company's SEC filing history.
- "Public" means the earlier of the EDGAR acceptance date and the filing date. Filings accepted after 17:30 carry the next day's filing date.

| Report type | Matched | Visible after the 10-Q/10-K was public | Visible after an earnings-release 8-K, before the 10-Q/10-K | **Visible before any SEC source** |
|---|---|---|---|---|
| Normal | 56,045 | 55,928 | 62 | **55** |
| Estimated date (period end + 45) | 988 | **988 (all)** | 0 | 0 |
| Amendment | 24 | 24 | 0 | 0 |
| Quarantined | 192 | never visible | – | – |

**The 55 early reports:**
- Most are a few companies where the vendor's date precedes both the earnings release and the 10-Q by 1–11 days:
  - Willis Towers Watson, 2016–2021;
  - Safehold, 2019–2021;
  - Healthcare Trust of America;
  - a few IPO-period reports.
- **Fix:** an explicit, dated list (55 reports, 19 securities). Each report becomes visible only from the day after its first public SEC source. This can only delay data, never advance it.

**Estimated filing dates:**
- The true filing lag was at most 90 days for all 991 estimated reports: 116 within 30 days, 875 within 90 days.
- The existing +90-day rule therefore **never exposed an estimated report before its filing**.
- The late-filer risk noted at P2-CP5 (12b-25 extensions to 105 days) did not occur in this data.

**Not checkable:** 2,759 reports. These are mostly vendor CIK metadata problems or foreign filers (item 2).

## 4. QuantConnect-vs-SEC value results (E971-02; non-quarantined sample reports)

Share of vendor values within 0.5% of the SEC as-first-filed value:

| Field | 10-K reports | 10-Q reports |
|---|---|---|
| Total assets | 98.9% | 98.8% |
| Stockholders' equity | 96.5% | 96.4% |
| Quarterly revenue | 90.9% | 93.5% |
| Quarterly net income | 94.6% | 96.7% |
| "Twelve-month" revenue | 90.9% | 93.1%* |
| "Twelve-month" net income | 96.9% | 96.7%* |
| "Twelve-month" operating cash flow | 97.0% | 96.9%* |
| "Twelve-month" gross profit | 94.6% | 96.4%* |
| "Twelve-month" operating income | 48.2% | 48.1% (the vendor's own operating-income standardisation) |

\* **Definitional finding.** On a 10-Q, the vendor's "twelve-month" value equals the **last completed fiscal year's total** as filed in the 10-K, not a rolling four-quarter total. Compared with a rolling total, only 8% match within 0.5%. This is old information, so it is point-in-time safe, but it changes only once a year.

**Which SEC filing do vendor values correspond to?** In the sample: 55,692 field values equal the first filing that reported them; 112 equal only a later filing; 2,560 equal no SEC figure.

**Universe-wide restatement check** (X973, run E973-01):
- Every 2010–2021 vendor report was compared with SEC filings wherever filings for that period disagree (an original against a restatement or recast); 12,618 company-periods qualified.
- **479 reports (0.80%, 179 companies) carried a value first filed after the vendor's date.**
- Those reports are now **blocked**; the previous clean report stays in use.
- Of the 26,726 fields compared: 24,167 equalled the original and 1,908 matched no filing.

## 5. Restatement / accession-anomaly findings

The question: does a quarantined report's value come from a later filing? There were 230 quarantined observations in the sample (all 213 E970 records, plus the sample's non-eligible days and mid-2009).

| Verdict | Count | Action |
|---|---|---|
| Valid: all values equal the original filing; only the accession reference is later | 20 | **Released** (explicit list; never automatic) |
| Restated: a value equals a later filing's figure | 20 | Kept quarantined (unsafe) |
| Mixed period: the income statement equals the original, but the balance sheet equals the **previous** quarter's (already public) | 135 | Kept quarantined (historically available but inconsistent) |
| Unresolved: balance-sheet values match no SEC filing | 5 | Kept quarantined |
| Unresolved: other mismatches or too few values | 16 | Kept quarantined |
| Unresolved: no XBRL data for the period | 34 | Kept quarantined |

- **Coverage lost to quarantine:** 39 / 195 / 11 / 9 eligible stock-months in 2010 / 2011 / 2012 / 2013 (at most 0.2% of a year), and none from 2014 on.
- **In most cases the previous clean report stays in use.** The counts above are months with no usable report at all.

## 6. Share-count reconstruction policy

| Question | Answer |
|---|---|
| SEC/XBRL concept | `dei:EntityCommonStockSharesOutstanding`: the share count printed on the cover of each 10-K or 10-Q |
| Snapshot or weighted average? | A **snapshot**: shares outstanding on a stated date. Weighted-average basic or diluted shares from the income statement are **never** used |
| Exact date | The cover date (the "latest practicable date", usually 1–6 weeks after the period end and before filing). It is used only from the day after the filing date |
| Split-adjusted? | **No.** Each filing keeps the number as reported then. Verified: Apple's cover count was 861 million in April 2014 and 5.99 billion in July 2014, after the 7:1 split |
| Can later corporate actions change its meaning? | A split after the cover date is applied only when observed live on its ex-date (see item 7). Mergers, issuance and buybacks are not extrapolated; the next filing's count replaces the old one |
| Multiple share classes | Multi-class registrants report one count per class, and the SEC API omits those. A filing with zero or several different non-class counts gives **no market cap** (left unresolved, e.g. CBS/Paramount, Alphabet, Berkshire) |
| Carry forward? | Only until a newer count is usable, and for at most **135 days** after its cover date (a quarterly cadence of about 91 days plus allowance for late filing). Older counts give no market cap: never extrapolated |
| Validity window | From the day after filing until a newer count replaces it, the count passes 135 days, or the security stops trading |

## 7. Historical market-cap reconstruction policy

**Market cap on day T** = the latest usable cover count × a split multiplier × QuantConnect's raw (unadjusted) close.

**Split multiplier:**
- It covers only splits that QuantConnect delivered as events (live) with an ex-date after the cover date and on or before T.
- The correction layer subscribes the repaired securities so that their split events arrive.
- **The split factor file is never applied backward.**
- A split between the cover date and the filing date is ambiguous: some companies already report the post-split count (Freeport-McMoRan, 10-K 2011). Such a split is applied only if the previous filing's count shows the new count does not already reflect it.

**Validation** (run E971-02): 406 sample companies, 40,351 company-months, compared with the vendor's own point-in-time market cap.

| Measure | Result |
|---|---|
| Median ratio | **1.000** (5th–95th percentile 0.998–1.002) |
| Within 2% / within 5% | 96.2% / 97.1% |
| Same answer at the $2B line | **99.8%** (84 disagreements in 40,351) |
| Live split adjustments agreeing with the vendor's split factors | 158 of 159 |

**The outliers** (2.9% outside ±5%) come from three causes:
- the vendor CIK pointing at a successor company;
- multi-class registrants where the SEC shows one class;
- splits between the cover date and the filing date, now handled.

## 8. D043 repair method

1. **Population.**
   - From QuantConnect: 2,928 liquid securities without fundamentals (price ≥ $5 and 20-day dollar volume ≥ $5M), with tickers and dates (run E970-01).
   - From the SEC: 1,179 registrants that file 10-K/10-Q, had a public float ≥ $0.5B at some point, and whose CIK is not among QuantConnect's companies.
2. **Identity: a QuantConnect security is linked to an SEC registrant only if all of the following hold**, using historical data only:
   - **E1 (public float).** At each 10-K public-float date, float ÷ (cover shares × QuantConnect close) must be consistent. Float can never exceed market cap. Every date must fall in [0.45, 1.05], or at least 75% in [0.45, 1.30] with a stable ratio.
   - **E2 (lifetime).** The security's trading ended within −45 to +200 days of the registrant's equity end (the exchange's Form 25, a Form 15, or the last equity report).
   - **E3 (ticker).** A ticker the security used is an in-order letter subsequence of the registrant's name **in force at the time**, with the same first letter (e.g. PCP ↔ Precision Castparts). The current name is never used; this rescued Time Warner, now "Warner Media, LLC".
   - **E4.** At least two float dates, or one plus a Form 25/15 within 30 days of the last trade.
   - **Uniqueness both ways.** A security may serve successive registrants only if their listed periods do not overlap (holding-company successions, e.g. Mylan Inc. → Mylan N.V.).
   - **Exclusions.** Partnership, LLC, trust and fund names, and fund, blank-check and royalty SIC codes, are excluded.
3. **Weaker evidence tiers, accepted only when nothing stronger exists:**
   - **Tier 2:** one ticker letter may be missing (TWX ↔ Time Warner), but only with a Form 25/15 within 30 days of the last trade.
   - **Tier 3:** registrants still listed after 2021 (no equity end). These need ≥ 6 float dates, ≥ 75% inside the window and a very stable ratio (median log deviation ≤ 0.035). This cut-off separates true matches (≤ 0.035) from coincidental pairings with stable-priced ETFs (e.g. Exxon ↔ EMB 0.092, Bunge ↔ BND 0.126). Those pairings were rejected.
4. **The correction layer** (`qr_sec_corrections.py` plus the packed table `qr_sec_data*.py`). It is explicit and dated, and **opt-in only**: an experiment must set `universe.sec_corrections`. Corrected names are listed separately (`qr_corrected`).
   - **Every correction carries:**
     - the security id and the CIK(s);
     - every source filing (accession, form, filing date, period end);
     - the cover date and share count;
     - the statement totals as first filed;
     - the method and the confidence/status.
   - **Audit copy:** `research/phase2/sec/corrections.json`.
   - **Statement totals** are rebuilt from each filing's own XBRL facts, using only filings made on or before that date. They follow the vendor's field semantics (item 4); total debt is not reconstructed.
   - **The same table also carries:**
     - the 55 timing holds;
     - the 20 quarantine releases;
     - the 479 restatement blocks.

## 9. Companies and periods repaired

- **163 securities (164 registrant links).**
  - Confidence: 81 high, 14 medium, 15 tier-2, 53 tier-3 ("no equity end").
  - **108** of them are eligible (≥ $2B, liquid, NYSE/Nasdaq) in at least one month of 2010–2021.
  - Primary exchange of repaired names while eligible: NYSE 3,021 and Nasdaq 1,345 company-months; none OTC.
- **Examples:**
  - Time Warner (2010–2018), Heinz, Genzyme, SanDisk, Precision Castparts, old DuPont, Chubb, Sigma-Aldrich, BMC;
  - Family Dollar, Computer Sciences, Progress Energy, Goodrich;
  - J.C. Penney, Bed Bath & Beyond, Mylan, FLIR;
  - Ally Financial, New York Community Bancorp, Old National, Umpqua.
- **Outcomes of the 108 eligible companies** (from their own SEC filings):
  - 74 acquired or otherwise ended;
  - 17 failed (a bankruptcy 8-K, item 1.03);
  - 17 still trading at the end of 2021.
- **Full list with evidence:** `research/phase2/sec/corrections.json`.

## 10. Companies still unresolved

Of the 1,179 candidate SEC registrants, 1,016 stay unresolved and are **never used** (`research/phase2/sec/unresolved.json`):

| Reason | Registrants |
|---|---|
| No QuantConnect security passes all identity rules | 767 (215 with a float ≥ $2B) |
| Not an operating-company common stock (name or SIC) | 149 |
| No usable single-class float observation (multi-class, XBRL unit errors) | 92 |
| Ambiguous | 8 |

Many of the 767 are companies QuantConnect **does** cover under a successor CIK (e.g. old Medtronic, Walgreen, Apache, Cigna, Xerox Corp). A separate market-cap fingerprint (run E971-02, "Q") flags these, so they are not truly missing. The rest are mainly:

- **Companies acquired before mid-2011.** Their first XBRL filing came after they had already ended: smaller large-accelerated filers were tagged from mid-2010, others from mid-2011. **The early-2010 gap is structurally hard to repair from XBRL.**
- **Securities whose ticker bears no relation to the company name.**
- **Multi-class companies.**

**Estimated remaining gap:** the D043 estimate minus the companies recovered (item 11).

## 11. Coverage before and after repair

Per month, eligible ≥ $2B names. "Missing" uses the D043 estimate, which is precise to about ±15–20% of its value.

| Year | Native (vendor data) | Recovered by SEC repair | D043 estimate of missing | Share of gap repaired | Missing share before → after | Usable statement records: native / recovered |
|---|---|---|---|---|---|---|
| 2010 | 688 | 33 | 126 | 26% | 14.1% → **11.4%** | 99.1% / 47% |
| 2011 | 843 | 56 | 113 | 50% | 11.5% → **5.9%** | 97.5% / 66% |
| 2012 | 859 | 47 | 126 | 37% | 12.4% → **8.0%** | 99.1% / 78% |
| 2013 | 986 | 45 | 120 | 37% | 10.5% → **6.8%** | 99.0% / 81% |
| 2014 | 1,121 | 43 | 105 | 41% | 8.3% → **5.1%** | 98.8% / 77% |
| 2015 | 1,169 | 34 | 87 | 39% | 6.7% → **4.2%** | 98.6% / 82% |
| 2016 | 1,135 | 21 | 53 | 40% | 4.4% → **2.7%** | 98.9% / 87% |
| 2017 | 1,238 | 22 | 65 | 34% | 4.8% → **3.3%** | 98.3% / 80% |
| 2018 | 1,306 | 21 | 51 | 42% | 3.7% → **2.2%** | 98.0% / 59% |
| 2019 | 1,291 | 16 | 61 | 27% | 4.4% → **3.3%** | 98.5% / 65% |
| 2020 | 1,291 | 12 | 45 | 28% | 3.3% → **2.4%** | 98.3% / 84% |
| 2021 | 1,624 | 13 | 20 | 62% | 1.2% → **0.5%** | 97.3% / 80% |

**By size:** recovered names sit mostly in the lower and middle terciles of the universe's market cap (1,724 / 1,788 / 854 stock-months in T1 / T2 / T3). The remaining gap is therefore concentrated in companies near the $2B line.

**Why recovered names have fewer usable records:** "usable" needs revenue, net income, assets and equity. For recovered names, the fiscal-year figures exist only after the first XBRL 10-K, and some revenue tags are company-specific.

## 12. Remaining survivorship-bias assessment

**Direction.** The recovered companies under-performed: equal-weight 8.5% a year against 13.8% for native names, 2010–2021. This measures who is in the universe, not a factor.

**Effect.** Adding them changes the equal-weight universe return by between −0.65 and +0.33 points a year (about −0.2 points on average). That is the same direction D043 found: without the repair, the benchmark is **slightly optimistic**.

**What is still missing.** The remaining names (11% of the universe in 2010, 6–8% in 2011–2013, 2–5% afterwards) are, by construction, the hardest to identify:
- pre-XBRL terminations;
- companies with unrelated tickers;
- multi-class companies.

D043 measured missing names that later failed at −28% a year. If the remaining gap looks like the measured one, the equal-weight benchmark is still overstated by roughly 0.3–1.0 points a year in 2010–2014, and by less later.

**Is the remaining universe representative enough for a profitability/quality backtest? Uncertain, leaning no, for 2010–2014.**
- The direction relative to a quality strategy is **ambiguous**. A quality strategy claims to avoid exactly the later-failing companies, and those are the ones still missing.
- The remaining distortion is below the +0.25 Sharpe margin: a 1-point bias is roughly 0.07 Sharpe.
- But it is concentrated in the early years and near the $2B line, where a quality screen would act.
- From 2015 the residual is ≤ 4% and the result would be credible.

## 13. Financial-company exclusion audit

**Disagreement level** (run E970-01): the filing-structure rule and the vendor's bank/insurance template disagree on **630 of 160,861 eligible usable stock-months (0.39%)**. That is about 2% of financial-template stock-months.

**It is not random.** It is concentrated in 13 companies and three groups:

- **Managed-care insurers.**
  - Cigna is classified financial-format (excluded) in 2010–2020, because the vendor reports no cost or operating lines for it.
  - Aetna is classified operating-format (kept) under an insurance template.
  - Their filings disagree too: Cigna tags a cost-of-revenue line and Aetna does not.
- **Mortgage REITs (Two Harbors, Chimera, ARMOUR).** They have a bank template but operating lines, so they are kept.
- **Equity REITs and two financial-services firms (Alexandria, Camden, Taubman, EPR, LaSalle, HTA; Lazard, Ocwen).**
  - They are classified financial-format only in 2010–2013/14, because the vendor's early records lack operating income.
  - They are classified operating-format later.
  - This is a vendor-completeness artifact, not a change in the companies.

**Stability:** 13 companies change classification at least once (14 changes in total).

**Exception policy (proposed; no override implemented):**
- Keep the per-report rule. It is point-in-time by construction.
- Do **not** resolve cases with current sector metadata.
- Any future override must be dated, evidence-based from the company's own filings, listed explicitly, and applied identically to the candidate, the benchmark and the controls.
- Whether REITs (and mortgage REITs) belong in a profitability universe is a design choice for H016. The academic convention excludes SIC 6000–6999. This is flagged in item 18 and not decided here.

**Details:** `research/phase2/sec/fin_audit.json`.

## 14. Canary results

**Final canary: run E972-02** (X972 v1.1).
- 2010–2021, 3.47 million stock-days, no orders.
- The universe includes the SEC correction layer, the timing holds, the releases and the restatement blocks.

| Check | Result |
|---|---|
| An SEC filing is never visible before the day after its filing date | ✔ 0 |
| Amendments are visible only after their own filing | ✔ 0 (48 amendments) |
| Quarantined values stay hidden (172 quarantined; 20 released by list only) | ✔ 0 |
| Restatement-blocked reports are never exposed (479 blocked) | ✔ 0 |
| Timing holds are respected (55) | ✔ 0 |
| A corrected company enters only with a usable, recent, filed count and a reconstructed market cap ≥ $2B | ✔ 0 |
| No future share information (count filed before T; only splits already observed) | ✔ 0 |
| Split handling: market-cap continuity across split dates of corrected companies | ✔ 0 jumps |
| No corrected company is eligible after its last trading day | ✔ 0 |
| Visa correction | ✔ 143/144 months (the first is warm-up) |
| Financial-format stability | 13 companies with a change (14 changes): known groups (item 13) |
| Coverage reports reproduce deterministically | ✔ E972-02 was re-run from its original commit (reproduction 2026-10-01T23:16Z). The summary is identical: every check, every coverage table and the composition returns. The 4,366 per-company monthly lines are identical as a set; only their print order differs (Python set iteration order). |

**Other runs this phase:**

| Run | Purpose | Result |
|---|---|---|
| E970-01 | Identifier export | Completed |
| E971-01 | First verification run | Canary-code defect (division by zero); annotated, not counted |
| E971-02 | Verification | Completed |
| E973-01 | Restatement guard | Completed |
| E974-01 | Second identity pass | Completed |
| E972-01 | Earlier canary, with 99 repaired securities and before the restatement guard | All checks 0 |

## 15. Automated tests

**All 466 tests pass.** New this phase:

- `test_sec_pit.py`:
  - values as first filed;
  - twelve-month semantics;
  - no later restatement leaks into an earlier record;
  - cover counts come only from a filing's own cover.
- `test_sec_corrections.py`:
  - visibility only after filing;
  - the 135-day limit;
  - split handling, including the cover-to-filing case;
  - unrepaired statuses never used;
  - feeding the point-in-time store.
- `test_pit_fundamentals.py`:
  - timing holds only delay;
  - releases only from the explicit list;
  - restatement blocks.
- `test_sec_wiring.py`:
  - the packed table round-trips with a hash check;
  - the SEC data is uploaded only for opted-in configs;
  - the harness default is unchanged;
  - the client caches and throttles;
  - no email is sent in the User-Agent.

## 16. Remaining risks

1. **Survivorship.** The residual gap is 11% (2010), 6–8% (2011–2013), 2–5% (2014–2020) and 0.5% (2021), concentrated near the $2B line and in pre-XBRL terminations (item 12).
2. **Identity matching** relies on float, lifetime and ticker-name evidence. On manual review of all 163 matched names, every identity looked correct. But no SEC ticker history was available to confirm them. The 53 tier-3 links ("no equity end") are the least certain.
3. **Vendor twelve-month semantics** (latest fiscal year, not rolling) affect any profitability definition (item 18).
4. **About 4.5% of vendor reports cannot be verified** (successor CIKs, foreign filers). Their timing and values are vendor-supported only, and the restatement guard cannot check them.
5. **Vendor operating income** follows its own standardisation (48% match with the SEC tag).
6. **Multi-class companies** get no reconstructed market cap.
7. **Statement totals for recovered names:** total debt is not reconstructed, and revenue tags vary by company.
8. **The financial-format rule** is a vendor-line artifact for some REITs in 2010–2013.

## 17. Decision

**Not safe enough yet to design H016.**
- Timing, values, restatements, quarantine and the market-cap method are now verified and protected.
- But the survivorship gap is only partly repaired (about 26–62% a year), leaving up to 11% of large companies missing in 2010.
- And a definitional choice about the vendor's twelve-month fields must be made first.

These are the two conditions you set before H016, and I am reporting the limitation rather than approximating it away.

## 18. Owner decisions required

1. **SEC contact email** (recommended).
   - Give a contact email for the SEC User-Agent (it may be a project mailbox). It unlocks `www.sec.gov`: XBRL instance names and Form 4 issuer ticker histories.
   - That gives ticker-based identity for the 767 unmatched registrants. It should repair much of the remaining gap at no cost, and confirm the tier-3 links.
   - No new session is needed; the network already allows the host.
2. **Twelve-month definition for any fundamental hypothesis.** Choose one:
   - **(a)** Use the vendor's "fiscal-year" values as they are. They are up to about 15 months old and refresh annually.
   - **(b)** Build rolling twelve-month values from the last four point-in-time quarterly reports, which match the SEC at 93–97%. Recommended.
3. **Residual-gap policy**, if remaining unrepaired after (1). Choose one:
   - **(a)** Accept it, disclosed, with a pre-declared survivorship stress on the H016 result. For example, the result must survive assigning the missing names D043's measured returns.
   - **(b)** Restrict H016's development window to 2015–2021, where the residual is ≤ 4%. This costs statistical power.
   - **(c)** Stop fundamental research.
4. **Confirm the new protections:**
   - SEC timing holds (55);
   - quarantine releases only by explicit SEC-verified list (20);
   - the restatement guard (479 blocked);
   - the opt-in correction layer and its identity rules and confidence tiers;
   - the 135-day share-count validity;
   - the financial-format exception policy (item 13), including whether REITs belong in a profitability universe. That last point is an H016 design question, flagged only.

**STOP.** No H016, no strategy or factor backtest, no slot used, Holdout locked.
