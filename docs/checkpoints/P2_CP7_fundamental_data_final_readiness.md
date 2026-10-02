# P2-CP7 — Fundamental Data Final Readiness Checkpoint

- **Date:** 2026-10-02.
- **Scope:** infrastructure only. The owner approved this stage on 2026-10-02 ("Continue SEC Repair, Build True TTM, Then Re-Audit Before H016"); the message is summarised in `docs/owner/2026-10-02_continue_SEC_repair_true_TTM.md`.
- **Not done in this stage:**
  - H016 was not defined.
  - No profitability or quality metric, ratio, ranking, top-N, rebalance rule or portfolio size was chosen or compared.
  - No strategy backtest and no factor return was computed.
  - No hypothesis slot was used. Phase 2 stays at 1 of 3 slots consumed, 2 remaining. H014 rejected; H015 not adopted.
  - The Holdout was not accessed: every run ends on 2021-12-31, and no SEC data after 2021-12-31 was used.
  - The development window was not shortened.
- **Earlier results:** none were rewritten. The SEC layer stays opt-in (`universe.sec_corrections`), and every earlier run reproduces as recorded.
- **Status:** STOP, awaiting owner approval.

## Summary in plain words

**Verdict (item 17): SAFE ENOUGH TO BEGIN H016 DESIGN**, which means writing the hypothesis and its pre-registration, not running it. This holds under the conditions in item 18. One item (the 2011 quarantine gap, item 18.6) should be settled before the first H016 backtest.

**What changed since P2-CP6:**

1. **The survivorship gap is now measured directly, and it is small.**
   - The new SEC access gave the ticker each company filed under, on each filing.
   - **The repair now covers 495 securities** (P2-CP6: 163). Each link is backed by SEC-filed, dated ticker evidence, or by the earlier float/lifetime evidence where tickers say nothing.
   - **Direct measurement.** Every SEC registrant with a public float ≥ $2B was checked. **0.5–1.2% of large companies a year remain unresolved** (P2-CP6 estimate: 11% in 2010, 0.5–8% later). They are mostly multi-class companies, issuers not listed on NYSE/Nasdaq, and ADS listings.
   - **Pre-XBRL blind spot.** About six US companies ≥ $2B that were acquired in 2010 before their first XBRL filing remain invisible, about 0.3% of the 2010 universe.
   - **Why P2-CP6 overstated the gap.** The earlier D043 estimate was a statistical extrapolation. Most of the liquid securities it counted turn out to be ETFs, funds, ADRs and foreign filers (item 3).
2. **True twelve-month values (True TTM) are built and validated.**
   - Each value is the sum of the four most recent point-in-time quarters, and is accepted only if those quarters reconcile with the 10-K's fiscal-year total.
   - Against the SEC's own figures, 95–97% are within 0.5% for revenue, gross profit, net income and operating cash flow. **These four fields are approved.**
   - Operating income (48%) and free cash flow (74%) fail the bar and are excluded.
3. **Financials and REITs are classified from the SEC industry code in force at each filing**, never from today's labels. Tower, data-centre, prison and timber REITs, for example, are excluded only from the date they became REITs.
4. **The final canary passes every leakage check** (11 of 11 at zero), and it reproduces exactly.

**What still limits the data (and why the verdict carries conditions):**

- **Missing usable data is not random.**
  - About 11–30% of non-financial eligible companies lack a usable True TTM in a given month (11–15% in most years). These are recent listings, late filers, quarters that do not reconcile, and quarantined vendor reports.
  - Companies that later went bankrupt have usable data in 43% of their months, against 87% for companies still trading.
  - An equal-weight universe restricted to companies with usable data therefore looks about **+1 percentage point a year better** than the full non-financial universe.
  - This is manageable only if the candidate, the benchmark and the controls all use exactly the same "usable" universe, as you required. The absolute-return optimism must then be disclosed with every result (item 13).
- **The repaired (formerly missing) companies are mostly unusable for fundamentals in 2010–2012.**
  - Smaller US companies only began filing machine-readable (XBRL) statements for periods after mid-2011.
  - So in 2010–2011 a fundamental screen still cannot see most of the companies the repair added back, many of which later failed.
  - This cannot be fixed from SEC structured data. It is measured (item 12).
- **2011 coverage dip.**
  - 135 vendor reports for 2010 quarters stay quarantined, because their balance sheets belong to an earlier quarter.
  - This leaves holes in the four-quarter chains, and usable coverage falls to 70% in 2011 (81–89% in other years).
  - Their income figures are verified as correct; a narrowly scoped, verified release is proposed (item 18.6).

---

## 1. SEC contact and access status

| Host | Status | Used for |
|---|---|---|
| `www.sec.gov` | **Works** with a User-Agent that carries a contact email. You authorised your own address on 2026-10-02, after P2-CP7a. It is read at run time only, from a local file outside the repository or an environment variable. **It is not in any repository file, document or commit**; a test checks the code. | Monthly XBRL RSS archives, 2009-06 to 2021-12 (151 files). For every XBRL filing they give: CIK, form, filing date, period, the **SEC-assigned industry code (SIC) at that filing**, fiscal-year end, and the XBRL instance document's name. The name starts with the ticker the company filed under. |
| `data.sec.gov` | Works (project identifier) | Company facts (every XBRL value with the filing that reported it), filing histories, public-float frames |
| `www.quantconnect.com` | Works | Unchanged |

**Request volume.**
- This stage made about 990 SEC requests: 151 monthly archives, 605 company-facts files and 232 filing histories. Everything else came from the cache.
- Requests run at no more than 8 per second (SEC limit: 10).
- Everything is cached outside Git (`data/sec_cache/`) and can be re-downloaded by re-running the scripts.

**The P2-CP7a blocker is resolved**, by your authorisation of the contact email.

**A defect found and fixed during the stage (D113a).**
- The first archive parser silently dropped every filing from late 2019 to 2021, because the SEC changed the archive's XML namespace and moved to inline XBRL.
- The parser now handles both formats, and fails loudly if any month parses to nothing.
- Everything downstream was rebuilt; four new parser tests cover it.

## 2. Additional SEC identity and ticker-history repair

**Evidence used** (all historical, all from SEC filings; `research/phase2/sec/identity_v2.py`).

| Rule | What it requires |
|---|---|
| **T (ticker)** | At least 2 periodic filings whose instance name starts with a ticker that the QuantConnect security carried within ±3 months of the filing date. Calibration: on 2,688 securities whose identity is known, the instance name equals the QuantConnect ticker on 97.9% of 59,265 filings. |
| **U (uniqueness)** | One security per registrant, and one registrant per security, at any time. Successive securities or registrants are allowed only if their periods do not overlap (e.g. C&J Energy's pre- and post-bankruptcy stocks). |
| **S (share count)** | The registrant reports a public cover share count of at least 1 million. This excludes subsidiaries that file under the parent's ticker. |
| **P (publicly traded, new, D113a)** | A registrant that filed 10-Ks during the evidence period must report a positive public float, dated within that period, on a 10-K cover. This removed utility subsidiaries filing with their parents (Tucson Electric Power under UNS, Black Hills Power under BHP), Hertz Corp (the subsidiary of Hertz Global), a non-traded REIT, and Golden Grain Energy. Golden Grain is an unlisted ethanol company whose file prefix "gold" collided with Randgold's ADR ticker GOLD. |
| **Exclusions** | Partnership, LLC or fund names in force at the matching filings; fund, blank-check and royalty SIC codes. |
| **F (float fingerprint)** | Where measurable, SEC public float ÷ (SEC cover shares × QuantConnect close) must lie in [0.1, 1.5]: float can never exceed market cap. XBRL thousand-scale tagging errors are tolerated. Runs E971-02, E974-01, E977-01 and E978-01. |
| **F2 (new, D113a)** | Eligible links with no fingerprint are checked against the final canary's reconstructed market cap: SEC float must be at least 10% of it. |

**Results.**

| | Count |
|---|---|
| SEC registrants examined (10-K/10-Q filers, not covered by QuantConnect's own data) | 9,980 |
| No QuantConnect security with ≥ 2 matching dated tickers | 9,306 |
| Excluded: non-common name 93; fund/blank-check SIC 28; no cover count ≥ 1M 27; no public float (rule P) 11 | 159 |
| **Linked** | **489 registrants** |
| Ambiguous (never used) | 7 |
| Rejected: float contradicts | 19 |

**Final correction table (v3.2, `research/phase2/sec/corrections_v2.json`; packed into `src/qresearch/lean/qr_sec_data*.py`).**

**495 securities, 501 links**, by tier of evidence:
- **Tier A (SEC ticker evidence): 494.**
  - 156 confirm one of P2-CP6's links; 338 are new.
  - Float evidence is consistent for 469, and absent for 25.
- **Tier B (P2-CP6 evidence only, no contradiction): 7.**
- **None of P2-CP6's 163 links was contradicted.**
  - One apparent contradiction (C&J Energy) was an artefact of comparing date ranges loosely. The comparison now uses the security's actual trading period.

**Manual review of eligible repaired links without float evidence** (the weakest tier that actually enters the universe).
- These are correct: Brigham Exploration, Baldor Electric, Continental Airlines, Dionex, Lions Gate (class A), Novell, Pactiv; and, from P2-CP6, CF Corp, C&J Energy, Life Storage.
- The one wrong link found (Golden Grain/Randgold) is removed by rule P.

**What the repair covers.**
- 194 repaired securities are eligible (≥ $2B, liquid, NYSE/Nasdaq) in at least one month of 2010–2021.
  - Company-months: NYSE 4,348; Nasdaq 2,311; AMEX 21; Arca 15.
  - Outcomes (from their own SEC filings): 112 acquired or otherwise ended, 32 failed (bankruptcy 8-K), 50 still trading.

## 3. Survivorship gap: before and after

**Three measurements:**

- **D043 (2026-09):** a statistical estimate. Liquid securities without fundamentals were scaled by a hand-classified US-common share and a size probability.
- **P2-CP6 (2026-10-01):** the D043 estimate minus the 163 repaired names.
- **Now: a direct SEC-side count.**
  - Every registrant filing 10-K/10-Q with an XBRL public float ≥ $2B, in that year or the previous one, is classified.
  - Categories: native (QuantConnect has it, possibly under a successor CIK); repaired; or missing.
  - Floats with unit errors and non-common vehicles are filtered out (`research/phase2/sec/residual_audit.py`).
  - Float is never above market cap, so this captures every ≥ $2B company **that filed XBRL**. The $1–2B "possible" band is added as an upper bound.

| Year | Native (vendor) | SEC-repaired | SEC-side unresolved registrants ≥ $2B float (+ $1–2B 'possible') | Missing share: D043 estimate → P2-CP6 → **now** (upper bound) |
|---|---|---|---|---|
| 2010 | 688 | 42 | 4 (+3) | 14.1% → 11.4% → **0.9%** |
| 2011 | 843 | 81 | 8 (+1) | 11.5% → 5.9% → **1.0%** |
| 2012 | 859 | 67 | 6 (+1) | 12.4% → 8.0% → **0.8%** |
| 2013 | 986 | 67 | 5 (+5) | 10.5% → 6.8% → **0.9%** |
| 2014 | 1,121 | 70 | 7 (+4) | 8.3% → 5.1% → **0.9%** |
| 2015 | 1,169 | 58 | 7 (+3) | 6.7% → 4.2% → **0.8%** |
| 2016 | 1,135 | 37 | 5 (+3) | 4.4% → 2.7% → **0.7%** |
| 2017 | 1,238 | 36 | 9 (+2) | 4.8% → 3.3% → **0.9%** |
| 2018 | 1,306 | 33 | 8 (+3) | 3.7% → 2.2% → **0.8%** |
| 2019 | 1,291 | 24 | 6 (+4) | 4.4% → 3.3% → **0.8%** |
| 2020 | 1,291 | 17 | 6 (+7) | 3.3% → 2.4% → **1.0%** |
| 2021 | 1,624 | 24 | 11 (+9) | 1.2% → 0.5% → **1.2%** |

*"Now" divides unresolved registrants (counted per year) by eligible names per month. It is an upper bound: a registrant missing for part of a year counts as a full year.*

**Why the D043 estimate was too high** (`research/phase2/sec/gap_reconciliation.py`). QuantConnect has 2,928 liquid securities without fundamentals:

| Group | Securities |
|---|---|
| Repaired | 495 |
| No XBRL filer ever used the ticker while the security carried it: ETFs, funds, notes, ADRs of non-filers, and the pre-XBRL blind spot below | 1,839 |
| Only foreign private issuers (20-F/40-F) filed under the ticker: ADRs, not US common stock | 292 |
| A 10-K/10-Q filer used the ticker but no link was made | 302 |

The 302 unlinked break down as:
- 94: the registrant is already covered by QuantConnect under another security;
- 210: fewer than 2 dated matching filings, or excluded as non-common;
- 26: ambiguous or contradicted.

The SEC-side count above shows that only 4–11 registrants a year with float ≥ $2B are truly missing.

**Pre-XBRL blind spot.**
- 73 liquid securities stopped trading before 2011-07 with no XBRL filer behind their ticker.
- **This group cannot be sized from SEC structured data.**
- By name, only about six are US common stocks ≥ $2B, all acquired in 2010: Affiliated Computer Services, PepsiAmericas, Black & Decker, Millipore, Sybase and Interactive Data. The rest are ADRs, foreign issuers and smaller companies.
- Together that is about 2 company-months per month in 2010 (about 0.3%). Acquisitions usually happen at a premium, so their absence does not flatter returns.
- *The size judgement uses names, as characterisation only.*

## 4. Remaining unresolved companies

**22 registrants with a public float ≥ $2B are unresolved** (`research/phase2/sec/residual_audit.json`; never used).

| Group | Registrants | Examples |
|---|---|---|
| Multi-class or tracking-stock companies (no single share count; tickers not unique) | 6 | CBS, Liberty Media, Liberty Expedia, Sinclair, Forest City, Gray Television |
| Not listed on NYSE/Nasdaq in the period (outside the universe anyway) | 5 | Fannie Mae (OTC from July 2010), Federal Home Loan Banks (unlisted), Trulieve and Green Thumb (Canadian exchange/OTC) |
| ADS listings of foreign companies filing 10-Ks | 2 | BeiGene, Zai Lab |
| Recent listings QuantConnect does not carry under their ticker | 3 | KnowBe4, Cricut (2021), Zillow (2014–15 class change) |
| Other / not identifiable | 6 | BGC Partners, Allied World, Medicis, Noble Corp (co-filing subsidiary), Brooklyn Federal and Blast Energy (probable float unit errors) |

**Outcomes** (from their own filings; the classifier is a heuristic):
- 15 still filing after 2021;
- 6 acquired or otherwise ended;
- 1 flagged with a bankruptcy 8-K. That is Liberty Media, whose flagged 8-Ks (item 1.03) were filed in 2026, outside the research period. It did not fail in 2010–2021.

**Other characteristics:**
- 7 financial (excluded from a profitability universe in any case);
- 13 at $2–5B, 7 at $5–20B, 2 above $20B (CBS, Fannie Mae).

**Not a distressed-company residual.** The residual is mostly multi-class and non-listed companies, not companies that later failed.

## 5. Share-count reconstruction rules

These are the D111 rules, unchanged. They apply only to repaired securities; native securities use the vendor's point-in-time market cap, audited in D107/D111.

| Question | Rule |
|---|---|
| Concept | `dei:EntityCommonStockSharesOutstanding`: the share count printed on each 10-K/10-Q cover. **Never** weighted-average basic/diluted shares, and **never** the vendor's share fields, which are split-restated to today (D107 blacklist, enforced by a hard failure). |
| Observation date | The cover date, kept with each record together with the filing date, accession, form and period. |
| Available from | The day after the filing date. |
| Split convention | As reported. Never restated. Splits are applied only when observed live (ex-date ≤ T). |
| Share classes | A filing with several class counts gives **no** count, so the market cap stays unresolved. Multi-class companies are therefore not repaired (item 4). |
| Validity | Until a newer count is usable, at most **135 days** after the cover date. Never extrapolated. |
| Confidence | Each link carries its evidence tier (A/B), float-check result, evidence span and equity end. |

## 6. Historical market-cap reconstruction rules

These are unchanged from D111 (validated in E971-02: median ratio to the vendor's point-in-time cap 1.000; same side of $2B in 99.8% of cases).

**Market cap on day T** = the latest usable cover count × split multiplier × QuantConnect raw close on T.
- The split multiplier comes only from splits that QuantConnect delivered live with an ex-date after the cover date and on or before T.
- A split between the cover date and the filing date is applied only if the count does not already reflect it.

**When there is no market cap:**
- If no usable count exists (no count yet, more than 135 days old, multi-class, or the security has stopped trading), there is **no market cap and no eligibility**. The value is left unresolved, never estimated.
- The canary re-derives each repaired name's eligibility from first principles every day: check C4 at 0, check C5 at 0.

## 7. True TTM implementation

`src/qresearch/lean/qr_fundamentals.py` (`PITStore.ttm_detail`), field names `<base>_ttm4q`.

1. **Inputs: point-in-time quarterly records only.**
   - These are the vendor's three-month values for native names, and the SEC as-first-filed three-month values for repaired names (Q2 and Q3 are derived from year-to-date facts in the same filing).
   - A record enters the quarterly history only when it is visible on the decision date. That means it passed every protection in item 9.
   - An amendment replaces its quarter only from its own availability date.
2. **Window: the four most recent visible quarters.**
   - They must be consecutive: 80–100 days apart, which covers 13- and 14-week quarters.
   - The newest must be at most 200 days old.
   - No interpolation, no backward filling, no carrying forward.
3. **Q4 validity gate.**
   - The fourth fiscal quarter is the 10-K's three-month value (vendor), or the fiscal year minus the nine-month year-to-date (SEC).
   - It is accepted only if the fiscal year's four quarters sum to the 10-K's fiscal-year total within 1%.
   - Otherwise there is **no TTM**, which prevents double counting and mixed bases (for example, a 10-K restated for discontinued operations while the 10-Qs were not).
4. **Availability.** A TTM exists from the day after the filing date of the **newest** of its four quarters. No component may be newer than that.
5. **Fields.**
   - Built: revenue, gross profit, operating income, net income, operating cash flow and free cash flow (operating cash flow − capex).
   - Approved for use: see item 8.
   - Balance-sheet fields (total assets, stockholders' equity) are **snapshots** of the latest visible report, never summed.
6. **Warm-up.**
   - A TTM needs up to seven quarters of history (four for the window, plus the fiscal year that validates Q4).
   - The canary therefore observes vendor reports from 2008-07-01, for **history only**; nothing is counted before 2010-01-04.
   - It also observes **every** company with fundamentals daily, not only eligible ones, so a company entering the universe already has its history.
   - E976-01, which lacked both, had TTM for only 2% of names in 2010. Item 18.3 asks you to approve this warm-up.

## 8. TTM validation results by field

**Sample and method.**
- Sample: 403 companies (run E975-01; the P2-CP6 verification sample, which covers every named case).
- Reference: a TTM built from the SEC's **as-first-filed** quarterly values for the same four quarters, each in the version public when the newest quarter was filed.
- **Approval rule, fixed before any strategy work and evaluated on the population it would serve** (companies not excluded by the financial/REIT policy): at least 90% within 0.5%, at least 95% within 2%, and no value exposed before a public SEC source.

| Field | Compared (non-financial) | Within 0.5% | Within 2% | All companies incl. financial (0.5% / 2%) | Exposed before SEC 10-Q/10-K | Decision |
|---|---|---|---|---|---|---|
| Revenue | 8,440 | **95.1%** | **96.0%** | 92.6% / 94.3% | 20, all after an earnings 8-K or the company's own filing | **Approved** |
| Gross profit | 3,882 | **95.3%** | **96.4%** | 95.1% / 96.1% | 8 (same) | **Approved** |
| Net income | 9,253 | **96.5%** | **97.5%** | 95.2% / 96.3% | 22 (same) | **Approved** |
| Operating cash flow | 8,383 | **97.4%** | **98.3%** | 96.8% / 97.6% | 20 (same) | **Approved** |
| Operating income | 8,023 | 48.0% | 56.1% | 48.1% / 56.1% | 19 | **Excluded**: vendor standardisation differs from the SEC tag |
| Free cash flow | 5,381 | 74.0% | 78.6% | 74.9% / 79.1% | 9 | **Excluded**: capex definitions differ |

- **Disclosure.** On the full sample including financial companies, revenue reaches 92.6% / 94.3%, just below the 2% bar. The rule is evaluated on non-financial companies because financials are excluded from the universe the fields would serve.
- **Early exposures.** All 98 values available before the SEC 10-Q/10-K were public by then through an earnings-release 8-K (item 2.02) or the company's own periodic filing. **0 values were exposed before any public SEC source.**

**Required cases** (core fields, share within 0.5%):

| Case | Values | Within 0.5% | Example (TTM ÷ SEC) |
|---|---|---|---|
| Calendar-year filer | 23,125 | 94.0% | Kraft Heinz 2016: revenue 1.000, net income 1.000; available 2017-02-24, same day as the SEC |
| Non-calendar fiscal year | 13,294 | 96.6% | Microsoft FY June 2010: 1.000 / 1.000 |
| Company with amended filings | 15,034 | 94.9% | FirstEnergy 2009: 1.000 / 1.004 |
| Company with restatement-blocked reports | 5,455 | 90.7% | Dover 2010: 1.000 / 1.000 (the blocked reports never enter) |
| Stock split | 458 | 98.7% | Apple 2014: 1.000 / 1.000 |
| Acquisition/delisting | 150 | 100% | Monsanto FY Aug 2010: 1.000 / 1.000 |
| Early 2010–2012 window | 5,528 | 95.5% | FirstEnergy 2009 (first XBRL year) |
| Changed fiscal year | 8,236 | 96.0% | Omnicom 2010 |
| Missing quarter | 866 per field | n/a | Costco 2009 (fiscal periods of 12 and 16 weeks): **no TTM produced**, correctly |

Detail: `research/phase2/sec/x975_results.json`, `strategies/X975_true_ttm_validation/`.

**Approved H016 field set** (`APPROVED_H016_FIELDS`): revenue, gross profit, net income and operating cash flow (True TTM); total assets and stockholders' equity (snapshots); point-in-time market cap.

**Not approved:**
- operating income TTM and free cash flow TTM;
- total debt (never validated against SEC filings);
- the vendor's `*_ttm` fields used as twelve-month measures (they hold the last fiscal year, D111).

## 9. Restatement protections for derived data

**True TTM can only be built from records that have passed every existing protection.** It reads only the store's visible quarterly history:

| Protection (inherited) | How it reaches TTM | Canary check (E976-04) |
|---|---|---|
| Visible only after the filing date (+90 days for vendor-estimated dates) | A quarter enters the history only on its availability date | C1 = 0 (SEC filings); **C10 = 0**: no TTM uses a component filed on or after the decision date |
| Quarantine (accession anomaly) | Quarantined reports never enter the history; only the 20 SEC-verified releases do | C3 = 0; **C11 = 0**: no TTM uses a quarantined or blocked component |
| Restatement guard (479 blocked reports) | Never enter the history | C3 = 0; C11 = 0 |
| SEC timing holds (55) | Delay the quarter's availability | C3 = 0 |
| Amendments | Replace their quarter only from their own availability | C2 = 0; unit test `test_amendment_changes_ttm_only_from_its_filing` |
| Freshness (200 days) | The newest quarter must be fresh | — |

**Unit tests** (`tests/test_true_ttm.py`):
- TTM appears only after the 10-K;
- an inconsistent Q4 gives no TTM;
- a missing or blocked quarter gives no TTM;
- snapshots are never summed;
- the whitelist is enforced;
- amendments apply only from their own filing.

**No derived value is ever back-filled.**

## 10. Financial/REIT exclusion policy

**Policy** (`src/qresearch/lean/qr_industry.py`; it uses no current-status metadata). On decision date T, take the **SEC-assigned SIC carried by the latest periodic filing visible on T**, from the RSS archive and effective the day after filing:

- **REIT** if it is 6798;
- **financial** if it is 6000–6999: banks, brokers, insurers including health insurers (6324), real estate, holding and investment offices;
- **otherwise, if no SEC SIC is visible yet** (foreign filers; pre-XBRL months), the filing-structure rule (D108) decides: a bank or insurer layout means **financial-format**;
- otherwise **kept**.

**Candidate, benchmark and controls must apply the same function to the same universe.**

**Whose filings give the SIC:**
- **The vendor CIK's own filings:** 3,425 securities. Check: for 3,354 securities, the vendor CIK's filings carry the security's own ticker. The 84 that do not are share-class variants (FOXA/FOX, LEN.B/LEN), custom prefixes (NET/CLOUD, PEG/PSEG) and SPAC-to-company successions.
- **A predecessor registrant:** 38. This needs market-cap evidence. D113a: prefix evidence alone had attached shells to real securities, e.g. "Global Gard" to GG.
- **Repaired links:** 495.
- **No SEC filing (structure rule only):** 433.

**Audit** (stock-months, E976-04):

| SEC SIC at filing | Bank/insurer layout | Operating layout |
|---|---|---|
| REIT (6798) | 988 | 10,521 |
| financial (6000-6999) — banks | 7,784 | 97 |
| financial (6000-6999) — brokers/asset managers | 1,142 | 2,676 |
| financial (6000-6999) — credit (non-bank) | 897 | 292 |
| financial (6000-6999) — holding/investment offices | 0 | 292 |
| financial (6000-6999) — insurance agents | 57 | 676 |
| financial (6000-6999) — insurers incl. health | 6,751 | 767 |
| financial (6000-6999) — real estate | 0 | 1,098 |
| operating | 157 | 123,196 |

- **Health insurers** (UnitedHealth, Anthem, Cigna, Aetna, Humana, Centene; SIC 6324) are **excluded** as financial. The vendor's templates had split them: Cigna "financial-format", Aetna operating.
- **Mortgage REITs** (Two Harbors, Chimera, ARMOUR) are excluded as REITs. The old structure rule had kept them.
- **Other operating-layout companies the SIC rule excludes** (the academic convention):
  - real-estate services such as CBRE (6500) and Jones Lang LaSalle (6531): about 1,100 stock-months;
  - exchanges and asset managers such as CME, ICE, Nasdaq (6200) and BlackRock (6211): about 2,700 stock-months.
  - Payment networks (Visa, Mastercard) and MSCI are SIC 7389, so they are kept.
- **Equity REITs that the structure rule had kept** are now excluded consistently: about 10,500 stock-months carry the REIT SIC with an operating layout.
- **REIT conversions** are dated by the SEC's own code change (19 moves):
  - Weyerhaeuser 2011, American Tower 2012, W. P. Carey, Ryman and GEO Group 2013;
  - Lamar, Corrections Corp and Crown Castle 2014;
  - Outfront, Iron Mountain and Equinix 2015;
  - SBA 2017, Alexander & Baldwin 2018.
  - Before conversion these companies are kept as operating companies.
- **Known exception: Host Hotels.** It stayed a REIT but has been coded 7011 (hotels) since 2013, so the policy keeps it. Moves out of 6798 also include genuine de-REITings: Walter Investment 2013, Drive Shack 2019.
- **SIC overrides the layout.** 157 stock-months (oil and gas, airlines, services) have a financial-looking layout but an operating SIC; SIC decides.
- **Detail:** `research/phase2/sec/industry_audit.json`.

## 11. Final yearly coverage tables

Final canary E976-04. The universe is ≥ $2B, liquid, NYSE/Nasdaq, with the opt-in SEC layer. Names per month are yearly averages.

| Year | Usable PIT record (any) | Excluded: financial / REIT / financial-format | Non-financial eligible | True TTM present (revenue / net income / OCF) | **Final usable** (count, share of non-financial) | Final usable: native / repaired | Quarantine-lost stock-months |
|---|---|---|---|---|---|---|---|
| 2010 | 95.8% | 70 / 23 / 22 | 615 | 86% / 87% / 90% | **518 (84.2%)** | 89% / 5% (of 37) | 39 |
| 2011 | 94.4% | 113 / 50 / 2 | 758 | 71% / 73% / 73% | **528 (69.6%)** | 75% / 15% (of 73) | 196 |
| 2012 | 97.4% | 114 / 56 / 1 | 755 | 84% / 87% / 87% | **612 (81.1%)** | 84% / 45% (of 61) | 14 |
| 2013 | 97.9% | 129 / 69 / 1 | 854 | 86% / 91% / 91% | **722 (84.6%)** | 86% / 61% (of 59) | 10 |
| 2014 | 97.7% | 158 / 82 / 1 | 951 | 87% / 91% / 91% | **825 (86.7%)** | 88% / 68% (of 58) | 0 |
| 2015 | 97.8% | 172 / 94 / 1 | 961 | 88% / 92% / 93% | **836 (87.0%)** | 88% / 65% (of 45) | 0 |
| 2016 | 98.3% | 167 / 101 / 1 | 903 | 91% / 94% / 94% | **805 (89.1%)** | 90% / 67% (of 26) | 0 |
| 2017 | 97.7% | 190 / 105 / 2 | 979 | 90% / 90% / 93% | **837 (85.5%)** | 86% / 53% (of 24) | 0 |
| 2018 | 97.1% | 201 / 104 / 3 | 1,032 | 90% / 92% / 93% | **904 (87.6%)** | 88% / 52% (of 22) | 0 |
| 2019 | 97.9% | 197 / 102 / 2 | 1,013 | 90% / 93% / 93% | **901 (88.9%)** | 90% / 49% (of 15) | 0 |
| 2020 | 98.1% | 188 / 88 / 2 | 1,031 | 91% / 93% / 93% | **919 (89.2%)** | 89% / 72% (of 9) | 0 |
| 2021 | 97.0% | 233 / 99 / 2 | 1,314 | 87% / 89% / 90% | **1,118 (85.0%)** | 85% / 74% (of 15) | 0 |

**Definitions:**
- **"Usable PIT record"** means a point-in-time report with revenue, net income, assets and equity (P2-CP6 definition).
- **"Final usable"** means: non-financial under item 10; True TTM revenue, net income and operating cash flow; plus assets and equity snapshots.

**Why non-financial names lack final usable data:**

| Year | fewer than four visible quarters | quarters not consecutive | no fiscal-year reconciliation inside the window | missing quarterly value | stale | no balance-sheet snapshot |
|---|---|---|---|---|---|---|
| 2010 | 28 | 16 | 46 | 3 | 5 | 0 |
| 2011 | 35 | 118 | 54 | 9 | 15 | 0 |
| 2012 | 12 | 33 | 76 | 16 | 5 | 0 |
| 2013 | 13 | 32 | 67 | 13 | 6 | 0 |
| 2014 | 20 | 29 | 59 | 13 | 5 | 0 |
| 2015 | 17 | 26 | 58 | 20 | 4 | 0 |
| 2016 | 9 | 20 | 54 | 7 | 8 | 0 |
| 2017 | 18 | 28 | 71 | 16 | 11 | 0 |
| 2018 | 17 | 29 | 56 | 16 | 11 | 0 |
| 2019 | 19 | 23 | 48 | 13 | 9 | 0 |
| 2020 | 23 | 20 | 47 | 18 | 4 | 0 |
| 2021 | 78 | 26 | 65 | 24 | 4 | 0 |

**Reading the reasons:**
- "Fewer than four visible quarters" covers new listings and spin-offs; it is high in 2021.
- "Quarters not consecutive" is mostly quarantine holes (2011) and irregular fiscal calendars.
- "No fiscal-year reconciliation" is the Q4 gate refusing a mixed or restated basis. It is conservative: in validation, the SEC could have built 594 of the 1,031 revenue values the gate refused.

## 12. Residual missingness characteristics

**A. Survivorship residual** (companies with no data at all). This is item 4: 22 registrants, mostly multi-class, non-listed or ADS; one false bankruptcy flag; 6 acquired. There is also the pre-XBRL group of about six companies acquired in 2010.
- **By size:** 13 at $2–5B, 7 at $5–20B, 2 above $20B.
- **By industry:** 7 financial, 4 media/telecom, 5 manufacturing/pharma, others.
- **By year:** concentrated in 2010–2011 and 2021 (new listings).

**B. Data-availability residual** (companies in the universe without usable True TTM). This is new, and the larger effect:

| Outcome (from the company's own SEC filings) | Securities | Eligible months | Usable months | Usable share |
|---|---|---|---|---|
| acquired/other | 606 | 21,898 | 17,454 | 79.7% |
| failed (bankruptcy 8-K item 1.03) | 32 | 952 | 405 | 42.5% |
| still trading | 1,661 | 111,156 | 96,446 | 86.8% |

**By size tercile** (final usable share; T1 = smallest third of the eligible universe):

| Year | T1 (smallest) | T2 | T3 (largest) |
|---|---|---|---|
| 2010 | 84.4% | 82.5% | 85.7% |
| 2011 | 75.0% | 70.1% | 63.8% |
| 2012 | 80.3% | 80.4% | 82.5% |
| 2013 | 83.8% | 86.5% | 83.4% |
| 2014 | 84.7% | 85.6% | 89.8% |
| 2015 | 81.8% | 86.9% | 91.8% |
| 2016 | 88.6% | 88.8% | 89.8% |
| 2017 | 83.9% | 85.7% | 86.8% |
| 2018 | 85.5% | 86.2% | 91.0% |
| 2019 | 84.8% | 89.2% | 92.7% |
| 2020 | 84.9% | 90.5% | 91.9% |
| 2021 | 78.8% | 85.3% | 90.8% |

**What drives B:**
- **Early years and repaired names.** Repaired names have usable data in 5% (2010), 15% (2011) and 44% (2012) of their months, against 75–89% for native names. Their statements exist in XBRL only from mid-2011 (smaller filers), so four XBRL quarters exist only from 2012. This is why 32 later-bankrupt companies show 43% usable.
- **Distress.** Late filers trip the 200-day freshness limit, and restating companies fail the Q4 gate. This is real-world unavailability or protective refusal, not a bug.
- **Size.** From 2014 on, the smallest tercile is 1–12 points less usable than the largest.
- **New listings (2021).**
- **Industry:** financials are excluded by policy; no other industry concentration was detected in the reasons.

## 13. Remaining bias assessment

Measured with the survivorship audit's outcome classification and the equal-weight universe composition (as in D043 and P2-CP6). This characterises the universe and is not a factor.

| Year | Repaired share of eligible | Effect of the repair on the EW universe (pp/yr) | Non-financial names without usable data | Availability bias of a usable-only universe (pp/yr) |
|---|---|---|---|---|
| 2010 | 5.5% | +0.52 | 15.3% | -0.63 |
| 2011 | 8.9% | -0.39 | 29.5% | +1.58 |
| 2012 | 7.4% | -0.81 | 20.2% | -0.55 |
| 2013 | 6.4% | -0.40 | 15.3% | -0.06 |
| 2014 | 6.0% | -0.32 | 13.5% | +1.05 |
| 2015 | 4.9% | -0.22 | 13.0% | +0.75 |
| 2016 | 3.3% | -0.45 | 11.1% | +0.36 |
| 2017 | 2.9% | -0.54 | 14.1% | +0.44 |
| 2018 | 2.5% | -0.52 | 12.7% | +1.59 |
| 2019 | 1.9% | -0.58 | 11.1% | +0.74 |
| 2020 | 1.3% | -0.38 | 10.6% | -0.41 |
| 2021 | 1.5% | +0.06 | 14.6% | +4.05 |

2010–2021 equal-weight: native 13.8%/yr vs repaired 4.9%/yr; non-financial names with usable data 14.8%/yr vs without 8.4%/yr.

1. **Survivorship (repair).**
   - Repaired names returned much less than native names over 2010–2021 (see the line under the table).
   - Adding them changes the equal-weight universe by about −0.2 to −0.8 points a year, and +0.5 in 2010.
   - **With the repair in place**, the remaining survivorship residual (about 1% of large companies, mostly not distressed) is **not material**: well under 0.1 points a year at the D043 measured spreads.
2. **Data availability.**
   - Names without usable data returned about 6.5 points a year less than names with usable data.
   - An equal-weight universe restricted to usable names is therefore **optimistic by about +1 point a year on average**, from −0.6 to +4.1 by year. 2021 is extreme: that year's new listings fell sharply.
   - **This is the main remaining distortion. It affects levels, not the comparison, if and only if the candidate, the EW benchmark and the controls are all drawn from the same usable universe** (owner rule; item 18.2).
   - **Direction for a quality strategy:** the benchmark is itself pre-cleaned of many later-failing names. So a profitability strategy's measured advantage over it would be, if anything, **understated** (conservative for G1/G2).
   - Absolute CAGR and drawdown are slightly flattered, and that must be disclosed.
3. **Is the repaired universe still materially optimistic?**
   - On survivorship: **no**.
   - On data availability: **yes for absolute levels, by about 1 point a year**. Under the same-universe rule, not for relative tests.
   - A 1-point-a-year shift is about 0.07 Sharpe, below the +0.25 margin.
4. **Defensible?** Yes, for design.
   - The residual is measured, disclosed and bounded.
   - It is not approximated away: no missing value is estimated, filled or inferred.

## 14. Infrastructure canaries

**Final canary E976-04** (X976 v1.1).
- 2010-01-04 to 2021-12-31, with observation-only warm-up from 2008-07-01.
- The universe includes the SEC layer v3.2, the timing holds, the releases, the restatement blocks and the SEC SIC history.
- Every company with fundamentals is observed daily. No orders.

| Check | Result |
|---|---|
| C1 An SEC filing is never visible before the day after its filing date | ✔ 0 |
| C2 Amendments are visible only after their own filing | ✔ 0 (99 amendments) |
| C3 Quarantined values stay hidden (637 quarantined; 20 released by list only), restatement blocks (479) and timing holds (55) are respected | ✔ 0 / 0 / 0 |
| C4 A repaired company enters only with a usable, recent, filed count and a reconstructed market cap ≥ $2B | ✔ 0 |
| C5 No future share information | ✔ 0 |
| C6 Market-cap continuity across split dates | ✔ 0 jumps |
| C7 No repaired company is eligible after its last trading day | ✔ 0 |
| **C10** No True TTM uses a component filed on or after the decision date | ✔ 0 |
| **C11** No True TTM uses a quarantined or blocked component | ✔ 0 |
| Visa dated exchange correction | ✔ 143/143 months |
| Financial-format stability | 15 companies with a change (16 changes): the known groups |
| Reproducibility | E976-03 (same canary code; table v3.1, differing from v3.2 by one removed link) re-run from its commit: **identical** (every line, its order, and the summary) |

**Runs this stage:**

| Run | Purpose | Result |
|---|---|---|
| E977-01 | Float fingerprints for identity v2 links | Completed |
| E975-01 | True TTM validation against the SEC (403 companies) | Completed |
| E976-01 | Canary v1.0 | All checks 0; **superseded for coverage**: pre-fix filing index, and it observed only eligible names with no warm-up (annotated) |
| E978-01 | Fingerprints for links found after the parser fix | Completed |
| E976-02 | Canary v1.1 on table v3 | All checks 0 |
| E976-03 | Canary v1.1 on table v3.1, plus reproduction | All checks 0; identical |
| **E976-04** | **Final canary, table v3.2** | **All checks 0** |

None of these is a strategy or a trial. Totals across the programme are in `experiments/INDEX.csv`.

## 15. Automated test results

**All 480 tests pass** (`python -m pytest tests`; 466 at P2-CP6). New this stage:

- `test_true_ttm.py` (6):
  - TTM available only after the filing that completes it;
  - an inconsistent Q4 gives no TTM;
  - a missing or blocked quarter gives no TTM;
  - snapshot fields are never summed, and the `_ttm4q` names are whitelisted;
  - an amendment changes TTM only from its own filing;
  - the approved field set is the validated one.
- `test_industry_policy.py` (2):
  - the SIC lookup is point-in-time (only on or after the effective date);
  - classification order: REIT before financial; structure fallback only without a SIC; exclusions.
- `test_rss_index.py` (5):
  - both archive namespaces;
  - inline-XBRL schema prefix;
  - the instance file preferred over the schema;
  - loud failure on an unknown format.
- `test_sec_wiring.py` (+1):
  - the contact email is read at run time only, and no email appears in the code.

## 16. Remaining risks

1. **Data-availability bias** (item 13). About +1 point a year in absolute levels for a usable-only universe. It is neutral for relative tests only under the same-universe rule.
2. **Early-year blindness to repaired names.** In 2010–2011 a fundamental screen sees only 5–15% of repaired names, a structural XBRL limit. The survivorship repair mainly protects the **benchmark and eligibility counts** in those years, not the fundamental universe.
3. **2011 coverage dip** (70%), from 135 quarantined mixed-period reports (item 18.6).
4. **The Q4 gate is strict.** It refuses some valid TTMs (594 of 1,031 refusals had an SEC value). It is conservative, but it lowers coverage, more so for restating or reorganising companies.
5. **Identity.**
   - 25 tier-A links have no float evidence. All eligible ones were reviewed by hand.
   - Prefix collisions are the main failure mode. Rules P and F2 and uniqueness catch the known cases, but an undetected collision on a never-eligible name is harmless only because eligibility needs a reconstructed cap ≥ $2B.
6. **Industry classification.**
   - The SIC code can lag a REIT election or never change (Host Hotels).
   - 433 native securities without SEC filings (foreign filers) rely on the filing-structure rule.
7. **The vendor CIK is current-status.** For SIC it is verified by ticker evidence (3,354 of 3,438 consistent). The 84 inconsistent cases are explained but not individually corrected.
8. **Multi-class companies** are never repaired. They are the largest residual group.
9. **SEC contact.** Re-building the filing index needs `www.sec.gov` with your email. All derived tables are committed, so research does not need it again unless the inputs are rebuilt.

## 17. Final verdict

**SAFE ENOUGH TO BEGIN H016 DESIGN.** That means writing the hypothesis, its pre-registration and its frozen specification. It is **not** approval to run it.

**Why:**
- Point-in-time timing, values, restatements, quarantine and market caps are verified against the SEC and enforced in code. Eleven canary checks are at zero, and the run reproduces.
- The survivorship gap you made a precondition is now **directly measured at about 1%** of large companies a year (P2-CP6 estimate: up to 11%). The remainder is characterised and not distressed.
- A validated True TTM replaces the vendor's fiscal-year fields, with a fixed approved field set.
- The financial/REIT policy is historical and auditable.

**Conditions:** the decisions in item 18. The data-availability bias is real, and it is acceptable only with the same-universe rule and disclosure.

**Not safe to run H016** until the warm-up mechanism is in the harness for development configs (item 18.3), and you have decided on the 2011 quarantine release (item 18.6).

## 18. Owner decisions still required

1. **Accept the verdict:** begin H016 design (pre-registration only). No backtest until the design is approved.
2. **Universe rule for the first profitability hypothesis** (recommended).
   - The candidate, the EW benchmark and every control are drawn from the same universe: eligible (≥ $2B, liquid, NYSE/Nasdaq, SEC layer on), non-financial under item 10, **with all approved fields usable on the decision date**.
   - Every report also states the yearly availability bias (Table D) and the full non-financial EW for reference.
   - The alternative, an EW benchmark on all non-financial names, is not recommended: it would credit the candidate for simply avoiding names without data.
3. **Approve the fundamentals warm-up** (recommended).
   - Vendor and SEC reports from 2008-07-01 are observed as **history only**: no eligibility, signals, selection or returns before 2010-01-04. All names with fundamentals are observed, not only eligible ones.
   - The harness needs a small, tested change so that development configs can do this.
   - Without it, 2010 True TTM coverage is about 2%.
4. **Confirm the approved field set:** revenue, gross profit, net income and operating cash flow True TTM; assets and equity snapshots; market cap. Confirm the exclusions: operating income, free cash flow, total debt, and vendor `*_ttm` as twelve-month values.
5. **Financial/REIT policy.** Confirm the SIC-at-filing rule with the structure fallback, and choose:
   - **(a)** Exclude health insurers (6324) with financials (recommended: it is the rule as written, and their statements have no cost-of-goods layout).
   - **(b)** Carve them out as operating companies.
   - The same choice applies to real-estate services (CBRE, JLL) and exchanges and asset managers (CME, ICE, BlackRock). Recommended: exclude all of 6000–6999 alike.
   - Also accept that SIC-coded exceptions such as Host Hotels stay as coded (recommended: no hand overrides without dated filing evidence).
6. **2011 quarantine gap.** Choose:
   - **(a)** Approve one more SEC verification run (infrastructure, no slot) for operating cash flow and gross profit of the 135 mixed-period 2010 reports. Then release **only their verified quarterly income and cash-flow values into the TTM history**, never their stale balance sheets.
   - **(b)** Accept the dip, disclosed.
   - Recommended: (a), before the first H016 backtest.
7. **Residual survivorship policy.**
   - Accept the measured residual (about 1% a year, plus about six acquired pre-XBRL names in 2010) as disclosed. Keep the 2010–2021 development window.
   - Recommended; no shortening is needed on survivorship grounds.
8. **Freeze the correction table v3.2 and the identity rules** (T, U, S, P, F, F2; tiers A/B) for H016, plus the D113a fixes. Any later change to them would be a new infrastructure version, recorded before any H016 result.

**STOP.** No H016, no strategy or factor backtest, no slot used, Holdout locked.
