# TT-CP1b Addendum 1 — WIKI licensing and access, revised composition audit, PR #137 test review

**Date:** 2026-10-24 · **Owner review:** D296 (`docs/owner/2026-10-24_tt_cp1b_review_corrections.md`) · **Decision record:** D297
**Scope:** documentation and review only. Nothing was downloaded, no market-data API was called, no chart was rendered, no code was written, no test was changed, nothing was bought, and the Holdout was not touched.
**Owner decisions already given (D296 §3), recorded and not re-opened:** WIKI visual development is limited to 2010–2017; 1999–2009 is never inspected visually; the Holdout stays sealed; any future validation uses separately approved, unexamined evidence.

---

## 0. Bottom line

1. **Licensing is not settled.** The WIKI page's public-domain statement covers the *data*. The Nasdaq Data Link *platform terms* bind whoever downloads it.
   - As far as they could be read, those terms limit use to "internal business purposes", restrict passing data or "Derived Data" outside the client without written approval, and pass through third-party provider terms.
   - They are being replaced on **1 November 2026**, and the new text is not public.
   - Whether sending chart images to Anthropic is allowed is therefore **ambiguous**. **An explicit written confirmation from Nasdaq Data Link is required** (draft email in §2).
2. **Current access is unverified.** A free account and API key still exist, and the dataset page still lists an export endpoint. The page also says "log in to view pricing", and no 2025–2026 evidence shows that a free key can still download WIKI Prices.
3. **The composition audit is redesigned** (§3).
   - It now measures WIKI against **independent SEC references** we already hold: public-float frames for 2009–2021, and dated tickers from XBRL filings.
   - It covers how companies left the market, missingness strata, identity and bar integrity, with pre-registered PASS / FAIL / INCONCLUSIVE rules.
   - Two things change from TT-CP1b: the sample is drawn **from the reference population, not from WIKI's own list**, and the result can only ever be "adequate for exploratory sampling", never "survivorship-free".
4. **PR #137 test changes** (§4).
   - Three of the four were genuinely stale filters; their expected numbers did not change.
   - One (the OC-CP1 / OC-CP2 H031 assertion) was a **changed, weaker expectation**, and this is disclosed.
   - The failures had entered with PRs #131 / #132 and went unnoticed until #137.
   - Full-suite status on the merged head: §4.4.
5. **Recommendation** (§5): **do not approve data access or chart analysis yet.** Approve sending the email, then decide once Nasdaq has replied and the 1 November terms can be read.

## 1. Remaining WIKI licensing and access uncertainties

### 1.1 What the two documents say, as far as they could be read

Vendor hosts (data.nasdaq.com, nasdaq.com) are still refused by this environment's proxy, so the excerpts below come from search-engine copies of the pages. The owner has read the WIKI page directly (D296).

| Document | Relevant wording (excerpted) | Effect |
|---|---|---|
| WIKI Prices page (`data.nasdaq.com/databases/WIKIP`) | "curated by the Quandl community and **released into the public domain**"; "no longer actively supported … as of April 11, 2018"; "we do not recommend using it for investment or analysis"; availability: "log in with your Nasdaq Data Link account to view pricing information" | The data itself carries no copyright-style restriction. The page does not say which platform terms govern access. |
| Nasdaq Data Link Terms (`data.nasdaq.com/terms`), current version | Licence "to receive, use, process and store the Data … **as set out in an Order Form**", limited to "**internal business purposes** unless the Order Form says otherwise". | Contractual limits on the downloader, whatever the data's copyright status. |
| | "Client shall comply with the applicable **third party provider terms** … Third party providers shall be deemed third party beneficiaries". | |
| | "**Derived Data cannot be distributed outside of Client** except as otherwise detailed in the Order Form or without Licensor's prior written approval". Derived data must not allow the underlying data to be reverse-engineered or substituted. | |
| | "All rights not granted hereunder are expressly reserved". | |
| Same page, update notice | Updated terms "**take effect on November 1, 2026**"; "continued use of the Data / Nasdaq Information after such date will constitute acceptance"; a summary table of changes is "available upon request". | Any reading today may be outdated within days. |
| Nasdaq Data AI Policy (DN2025-2) | Use "including for training of AI models must strictly adhere to the terms of the license"; dissemination through LLMs must be entitlement-controlled; third-party AI tools are covered. | Written for Nasdaq exchange data. Whether it reaches community-curated data hosted on Data Link is unclear. |

### 1.2 Each proposed use against those terms

| Proposed use | Assessment | Why |
|---|---|---|
| (a) Download historical WIKI Prices for personal research | **Probably permitted** | This is the dataset's stated purpose on a free account. Two open points: the licence wording is written for organisations ("internal business purposes", "Order Form"), and free datasets have no Order Form. |
| (b) Render OHLCV as candlestick charts, locally | **Probably permitted** | Internal processing ("use, process and store"). Nothing leaves the licensee. |
| (c) Send anonymised chart images to Anthropic's Claude | **Ambiguous; confirmation needed** | A candlestick chart lets the underlying OHLCV be read back, so it fails the "Derived Data" test and counts as the data itself. Sending it to Anthropic is disclosure outside the client. It is unclear whether this is allowed because the data is public domain, or because Anthropic acts as a service provider processing on our behalf. Neither is stated. The 1 November terms may change this. |
| (d) Claude identifies patterns and turns them into deterministic rules | **Permitted once (c) is settled** | Rules, definitions and written observations are our own work product, not the data, and they do not reproduce prices. |
| (e) Model training at Anthropic | **Avoidable** | On consumer plans (Free / Pro / Max, including Claude Code), sessions are used for training unless the owner opts out. Retention is 5 years with training, 30 days without. If (c) is confirmed, the owner should switch "Help improve Claude" **off** before any chart is sent. The email asks about training explicitly. |

### 1.3 The conflict, stated plainly

- **The public-domain statement** settles who owns rights in the WIKI data.
- **The platform terms** are a contract with Nasdaq. A contract can restrict how a downloader uses even public-domain material obtained through the service.
- **The "third party provider terms"** clause plausibly points back to the public-domain dedication, which would favour our use. "Plausibly" is not enough for a disclosure to an AI provider.
- **The Kaggle mirror** lists its licence as "Unknown" and would not remove the problem. It is not an alternative.

### 1.4 Access in 2026 (unverified)

- **Confirmed by search:**
  - free Nasdaq Data Link accounts with an API key still exist;
  - the WIKIP page still lists a datatable endpoint (`/api/v3/datatables/WIKI/PRICES…`).
- **Not confirmed:**
  - whether a free key can still export the full table (about 15 million rows). Third-party sources disagree on free-tier limits, from 10,000 rows per call to 50,000 calls a day.
  - whether the "log in to view pricing" wording means the table now sits behind a paid entitlement.
- This can only be settled by the owner logging in, or by Nasdaq's reply. Nothing was attempted from here. The hosts are blocked in this environment anyway, so condition C4 still applies.

## 2. Draft clarification email to Nasdaq Data Link (for the owner to send; Claude has not contacted Nasdaq)

> **Subject:** Permitted use of the WIKI Prices dataset (WIKIP) with an AI assistant — personal research
>
> Hello,
>
> I hold a free Nasdaq Data Link account for personal, non-commercial investment research. Before downloading anything, I would like to confirm that the following use of the WIKI Prices dataset (WIKI/PRICES, described on your site as "curated by the Quandl community and released into the public domain") is permitted under your Terms and Conditions, including the updated terms effective 1 November 2026:
>
> 1. Downloading the historical WIKI Prices table once, for personal research, using my free API key. Is the full table still available to free accounts, and what is the recommended method (bulk export or paginated calls)?
> 2. Rendering daily price and volume data for 2010–2017 as candlestick chart images on my own computer.
> 3. Submitting a limited number (about 300) of those chart images, without tickers or dates, to Anthropic's Claude AI assistant for my own internal analysis of price patterns. The images would not be published or shared with anyone else. I would disable the provider's option to use my data for model training.
> 4. Keeping the trading rules and written observations that result. These would not include the data itself.
>
> Specifically:
> - (a) Do the Nasdaq Data Link Terms impose any restriction on these uses for a public-domain dataset?
> - (b) Does sending such chart images to a third-party AI service count as distribution of "Data" or "Derived Data" requiring your prior written approval? If so, could you provide that approval?
> - (c) Could you send me the summary table of changes in the terms effective 1 November 2026?
>
> Thank you,
> [Owner name]

The owner's name, email and account details go in only when sending. None of them is stored in the repository.

## 3. Revised historical chart-composition audit protocol (PROPOSED, not frozen, not run)

### 3.1 Purpose and what it can and cannot conclude

- **Purpose:** decide whether WIKI Prices can supply a **sufficiently representative exploratory chart sample** of the US large-cap universe for 2010–2017.
- **Possible outcomes:** "ADEQUATE FOR EXPLORATORY SAMPLING" (PASS), "NOT ADEQUATE" (FAIL) or "INCONCLUSIVE".
- **It cannot certify** WIKI as survivorship-free or as accurate in price. Nothing found on WIKI is evidence about returns. It produces ideas for deterministic rules only.

### 3.2 Reference populations, in order of independence

| Ref | Source (already cached unless stated) | Independence from QuantConnect and WIKI | Limits |
|---|---|---|---|
| **R1** | SEC XBRL frames `dei:EntityPublicFloat`, quarterly 2009Q1–2021Q4: 52 frames in `data/sec_cache`, covering **every** XBRL filer that reported the fact, including companies that later vanished | Fully independent | Public float is less than or equal to market cap, so float ≥ $2B is a conservative subset of the ≥ $2B universe. Annual and lagged. Misses non-filers, most 20-F / 40-F foreign issuers, and float-less share classes. |
| **R2** | SEC dated ticker evidence from XBRL filings (identity v2; `data/sec_derived/xbrl_filings.json.gz`) | Independent | Starts in 2009 / XBRL; ticker tags are sometimes missing or wrong |
| **R3** | SEC exit evidence per registrant: Form 25 / 25-NSE, 15-12B / 15-12G, DEFM14A / merger 8-Ks, 8-K Item 1.03 | Independent | Cached only for the about 4,944 registrants already in `data/sec_cache/submissions`. Classifying R1 registrants outside that set needs **new SEC retrieval**, a separate owner approval (public, free, data.sec.gov). |
| R4 | Data v1 eligible list (E981-01, identifiers only) | Not independent (QuantConnect-derived) | **Secondary cross-check only**, with known completeness and survivorship limits (RR3–RR6) |
| R5 (optional) | Public S&P 500 change history (Wikipedia) | Independent of both | New retrieval; crowd-sourced. Only a sanity check on well-known large caps and index deletions. |

**Frame definition:**
- The **reference frame** is the set of R1 registrants with public float ≥ $2B in any 10-K whose float date falls in 2009–2017.
- Each registrant enters the frame for the twelve months after that float date.
- Registrants classified as financial / REIT by SEC SIC at filing are flagged but not removed, because charts are not limited to non-financials.
- WIKI tickers are linked to frame registrants **only through R2 dated tickers** (ticker + date range → CIK). They are never linked by ticker alone.

### 3.3 Measurements and pre-registered gates

The thresholds below are proposals. The owner approves or changes them **before** anything is measured; after measurement they are not changed. They apply to frame registrant-months for 2010-01 → 2017-12.

| Gate | What is measured | PASS | FAIL | Otherwise | Why these bounds |
|---|---|---|---|---|---|
| **A1** Coverage of the independent frame | Share of R1 frame registrant-months with WIKI bars on ≥ 90% of sessions in that month | ≥ 90% overall **and** ≥ 85% in every year | < 75% overall **or** any year < 70% | INCONCLUSIVE | Sampling works on reference strata, so 85–90% coverage costs precision but not validity. Below 75%, the missing quarter could follow its own pattern. |
| **A2** Leavers, using SEC exit evidence | Coverage of the registrant-months in the **last 24 months before exit**, by exit type: acquisition / merger, bankruptcy or distress (8-K Item 1.03, Form 15 after distress), other delisting (Form 25 without a merger) | Each type with n ≥ 20 registrants: ≥ 80%, **and** the gap to non-leavers ≤ 10 points | Any type with n ≥ 20 below 65%, **or** a gap > 20 points | INCONCLUSIVE. Types with n < 20 are reported, never PASS. | Dying companies are what survivorship hides. A 10-point gap still lets re-weighting by reference strata restore their share without extreme weights. |
| **A3** Missingness by stratum | Coverage by year × liquidity tercile (public float tercile within the frame, since WIKI volume is unknown for absent names) × security type (domestic 10-K filer / foreign or ADR / multiple share classes / financial or REIT) | No stratum with ≥ 50 registrants below 70% | Any stratum with ≥ 50 registrants below 50%, unless the owner approves **removing** that stratum from the sampling frame beforehand (disclosed) | INCONCLUSIVE | Finds structural holes, for example "WIKI lacks most ADRs". Those become explicit frame exclusions instead of hidden bias. |
| **A4** Identity and ticker reuse | Share of linked WIKI histories that map to exactly one CIK over the linked span; concatenated histories, where one ticker carries two companies (date gap > 20 sessions or a CIK change in R2) | ≥ 98% of linked registrant-months unique; ambiguous ones excluded from the frame | > 5% of linked registrant-months ambiguous | INCONCLUSIVE | Ticker-only keys are WIKI's main identity risk. Reused tickers can glue two charts together. |
| **A5** Bar integrity, inside linked lives | (i) missing sessions against a market calendar built from dates on which ≥ 50% of linked tickers trade; (ii) suspicious spikes: \|daily log return\| > 0.40 reversed by > 0.30 the next session, with no split / dividend row; (iii) high / low / open / close inconsistencies or prices ≤ 0; (iv) adjustment consistency: the adjusted / raw ratio changes only on split or dividend rows; (v) split cross-check: a pre-registered random sample of 100 WIKI split rows against SEC cover-share jumps (D111 method) | (i) ≤ 0.5% of stock-days; (ii) ≤ 0.1%; (iii) ≤ 0.01%; (iv) ≥ 99.5% of ratio changes explained; (v) ≥ 95 / 100 agree | Any of (i)–(iv) worse than 5× its PASS bound, or (v) < 85 / 100 | INCONCLUSIVE | Spikes and broken adjustments look like real price action on a chart. Stock-months with any (ii)–(iv) defect are removed from the sampling frame in any case. |
| **A6** End-of-curation decay | Coverage and A5 rates in 2017 vs 2014–2016 | 2017 within 2 points of 2014–2016 | Worse by > 5 points | INCONCLUSIVE | Community curation stopped in April 2018; quality may have decayed before that. |

**Overall result:**
- **PASS** only if A1–A6 all pass.
- **FAIL** if any gate fails.
- **INCONCLUSIVE** otherwise. The owner then decides: a restricted frame with documented exclusions, or stop.
- R4 (Data v1) and R5 coverage are reported as cross-checks only and never decide the result.

### 3.4 How the sample is drawn if the audit passes (for the later sampling protocol)

- **Stratified by the reference frame, not by WIKI's list:** year × float tercile × exit status, with cell targets from R1 / R3.
- Leavers are kept in proportion to their reference share. Cells that WIKI cannot fill are reported as **unfilled**, not back-filled from other cells.
- Seed, cell targets and frame exclusions are committed before any chart is rendered.

### 3.5 Biases that cannot be removed with existing resources

1. **Companies absent from WIKI.** Coverage can be measured, but no free source exists to fill the gap.
2. **No independent price check.** QuantConnect prices cannot leave QuantConnect, and no other licensed price source is held. Errors that pass the internal checks in A5 stay undetected.
3. **No point-in-time market cap.** The frame relies on public float, which is annual, lagged and below market cap. Mid-size names near $2B and most foreign issuers are under-represented.
4. **Selection of WIKI's ticker list.** It was chosen by the community; we can measure its effects, not undo them.
5. **Claude's prior knowledge.** I may recognise famous 2010–2017 charts or know how they ended, even when blinded.
6. **Period character.** 2010–2017 was mostly a rising market with low volatility. Patterns seen there may be specific to that regime.
7. **Exit classification.** R3 covers only cached registrants unless a new SEC retrieval is approved, so A2 may be INCONCLUSIVE on existing data alone.

### 3.6 Limits of WIKI for chart-based hypothesis discovery (whatever the audit result)

- **Discovery only.** Observations are inputs to deterministic rule definitions. They are never evidence that a rule earns money.
- **Rule tests happen elsewhere.** Every rule is coded and tested on separately approved, unexamined data. WIKI-only performance is never reported as a result. The goal stays the same: beat SPY in long-term after-tax wealth, using measurable price and volume rules.
- **Data artefacts.** A pattern that depends on a WIKI artefact (adjustment, missing bars) would vanish on other data. A5 reduces this risk but cannot remove it.
- **Sample size.** About 300 charts is a small sample. It can suggest behaviours but cannot rank them.

## 4. Review of the PR #137 test changes

### 4.1 What failed and why

The four tests did not fail because of TT-CP1b. They failed because of earlier, legitimate records:
- **E033-01**, the H032 R1 run (cycle "H032", programme "OS"), was registered in **PR #131**.
- The **H031 / H032 rows** were added to `research/hypotheses/STATUS.md` in **PR #132**.

These are snapshot tests written for earlier checkpoints. PRs #131–#136 were merged without a completed full-suite run that would have caught them; that was a process lapse on my part. The first completed full run, during the #137 work, found them.

### 4.2 Each change

| Test | Change | Necessary? | Weakened? |
|---|---|---|---|
| `test_c03_stats.py::test_real_registry_before_c03` | Added "H032" to the list of later cycles excluded from the **pre-C03** selection count | Yes. The test pins the frozen pre-C03 count (37); E033-01 is a 2026-10-22 run, not pre-C03. | **No.** The pinned numbers 37 / 0 / 26 / 1 are unchanged; the filter now matches its own stated purpose. |
| `test_c03_stats.py::test_committed_c03_runs_give_40_and_73` | Added programme "OS" to the programmes that "count on top" when rebuilding the pre-C03 registry | Yes, same reason | **No.** The pinned 37 / 64 and 40 / 73 are unchanged. |
| `test_registry.py::test_d069_counts_on_the_real_registry` | Added "H032" to the later-cycle list | Yes, same reason | **No.** Pinned counts unchanged. |
| `test_oc_cp1.py` / `test_oc_cp2.py::test_records_and_no_new_active_hypothesis` | Replaced `"| H031 |" not in STATUS` with "every H031 row says *never registered*". "Still no active hypothesis" is kept. | The original assertion recorded a fact true at OC-CP1 / OC-CP2 time that later became false legitimately: H031 was drafted under D268, H032 registered under D278. | **Yes, the expectation changed and is weaker** than the original literal: it no longer forbids an H031 row, and it does not check H032's row. I judge the intent preserved: no *registered or active* hypothesis came out of OC-CP1 / OC-CP2. But it is a changed expectation, not a pure correction. |

**Design weakness, not fixed:** the three registry tests exclude later cycles by an explicit list, so every new programme needs another edit. That is brittle, and it is easy to hide a real miscount inside such an edit. A sturdier form would include only C01 / C02 explicitly. Per D296, no further test change is made without the owner's separate authorisation.

### 4.3 What was claimed in PR #137

- PR #137 said the four tests "now pass". That was a **subset** run (the four affected files).
- The full suite was **not** run to completion on PR #137's final head before merge.
  - The first full run stopped at its first failure (`-x`).
  - A second full run, after the three registry fixes but before the OC-CP1 / OC-CP2 fix, completed and reported only those two OC tests as failing.
- My PR #137 summary did not overstate this, but it also did not present a full-suite pass.

### 4.4 Full suite on the merged head

- **Run:** the complete suite on commit **a7a38f3** (main after PR #137, tests unmodified since), in this session, with `-o addopts=""` so the summary is not hidden. One owner record (D296) was committed while it ran.
- **Result: 1,463 passed, 3 skipped, 0 failed, 0 errors** (exit code 0; 15 min 34 s).
- The 3 skips are conditional by design. Two identified examples: the "not yet frozen" branch of the Data v2 freeze test, which is skipped because Data v2 is frozen, and a short-fixture case in the H020 chart tests.
- This addendum changes documentation only, so the result applies to its head as well.

## 5. Recommendation

| Question | Recommendation |
|---|---|
| Approve WIKI data access now? | **No.** First send the §2 email, wait for Nasdaq's reply, and read the terms in force from 1 November 2026. |
| Approve Claude's analysis of historical charts now? | **No.** It depends on a written answer to question (b). |
| Approve the revised composition audit (§3) thresholds now? | **Yes, if the owner agrees with them.** Approving thresholds before any measurement is what makes the audit honest. Running it still needs access approval and possibly the R3 SEC retrieval. |
| Model-training setting | Switch "Help improve Claude" off before any licensed or third-party data is sent, whatever Nasdaq answers |

**Order once Nasdaq confirms in writing:**
1. Owner approves access and C4 (network allowlist plus API key, new session).
2. Download.
3. Composition audit, metadata only.
4. Frozen sampling protocol.
5. Owner approves chart viewing.

**If Nasdaq refuses or does not answer:** the choice in TT-CP1b §8 applies (quantitative-only TP-1, or pause). Synthetic charts are not a substitute.

**STOPPED for owner review.**

## Sources (search-engine excerpts, 2026-10-24; Nasdaq hosts are refused by this environment's proxy)

- Nasdaq Data Link Terms and update notice: https://data.nasdaq.com/terms
- WIKI Prices page: https://data.nasdaq.com/databases/WIKIP
- Nasdaq Data Link API docs (free key, datatables): https://docs.data.nasdaq.com/docs, https://docs.data.nasdaq.com/docs/data-organization
- Free-tier limits (third-party, conflicting): https://www.dataquest.io/blog/exploring-financial-data-using-the-nasdaq-data-link-api/, https://blog.quantinsti.com/nasdaq-data-link/
- Nasdaq Data AI Policy: https://www.nasdaqtrader.com/TraderNews.aspx?id=DN2025-2
- Nasdaq Global Data Agreement (derived-data definition, comparison only): https://www.nasdaq.com/docs/2025/11/18/Nasdaq-Global-Data-Agreement-Form_3.pdf
- Anthropic consumer terms update: https://www.anthropic.com/news/updates-to-our-consumer-terms
