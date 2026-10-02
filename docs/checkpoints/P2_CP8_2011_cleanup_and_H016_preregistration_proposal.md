# P2-CP8 — Final 2011 Data Cleanup (A) and H016 Pre-Registration Proposal (B)

- **Date:** 2026-10-02.
- **Approval:** the owner approved this stage on 2026-10-02 ("Approve Final Fundamental Data Policies, Complete 2011 Cleanup, Then Design H016 Only"); see `docs/owner/2026-10-02_final_data_policies_2011_cleanup_H016_design.md`.
- **Not done:**
  - **H016 is not implemented and was never run**, nor were its controls.
  - No candidate or factor returns were computed, and no fundamental metrics were compared by performance.
  - Phase 2 slot 2 is not consumed: 1 of 3 slots used, 2 remaining.
  - The Holdout was not accessed: every run ends 2021-12-31.
- **Status:** STOP, awaiting the owner's explicit approval.

## Summary in plain words

**A. The 2011 cleanup is complete, and the data verdict is unchanged (still acceptable).**
- **Released, field by field:** all 135 held-back 2010–2011 reports were checked against the SEC's original filings.
  - Their verified income and cash-flow figures are now usable for twelve-month values.
  - Their stale balance sheets, and every figure that did not match exactly, stay quarantined.
- **Coverage:** usable coverage in 2011 rises from 70% to 77%, and in 2012 from 81% to 84%. No other year falls.
- **Leakage checks:** all twelve are at zero.
- **Freeze:** the data infrastructure is now **frozen as version v1**: a hash-pinned manifest of 43 files, checked by a test.
- **Warm-up:** the history-only warm-up from July 2008 is built into the harness and proven by tests and a live run. The first reported day shows exactly the starting $100,000.

**B. H016 proposal: one measure, gross profits-to-assets (GP/A), chosen from the literature, not from our data.**
- **Rule:** hold the 20 highest-GP/A stocks of the same non-financial universe the benchmark uses, rebalanced quarterly just after the filing deadlines.
- **Candidates:** one pre-registered rule, no A/B selection.
- **Run plan:** 8 committed runs plus 1 canary; at most 9 more only if the first three gates pass.

**Candid expectation.**
- The development bar (Sharpe +0.25 over equal weight) is demanding for a single, already published factor in large caps.
- Published effects typically lose about half their strength after publication.
- I estimate H016 has roughly a 15–30% chance of passing G1. It would still give a clean, pre-registered answer to the question you posed.
- **Whether to spend slot 2 on it is your decision (B17).**

---

# Part A — Final 2011 Data Cleanup

## A1. What was verified

**Run E979-01** (X979, infrastructure, ratios only; 2009-06 → 2012-12) observed **all 135** quarantined "mixed-period" vendor reports. These are 2010–2012 quarters whose income statement matched the original filing while the balance sheet belonged to an earlier quarter.
- Each was observed on the day the vendor first showed it.
- Each was quarantined when observed.
- They belong to 119 companies.

**Release rule** (owner item 6; `research/phase2/sec/x979_analyse.py`). A **field** is released only if all of these hold:

1. It is one of the **approved flows**: quarterly or fiscal-year revenue, gross profit, net income or operating cash flow. **Balance-sheet fields are never released.**
2. The SEC **original** filing (the first non-amendment 10-Q/10-K for the period) was filed **no later than the vendor's file date**, so the value was public at the historical date. Its availability still follows every PIT rule (vendor date + 1, +90 fallback, timing holds).
3. The vendor value **equals the SEC as-first-filed value within 0.5%**. It is therefore the original figure, so no later restatement is introduced.
4. The report is not restatement-blocked. Blocks always win: this keeps Pitney Bowes' Q3 2010 report fully hidden.

Each flow was compared on its own, so the mismatched balance sheet cannot reach a released value.

## A2. Results

| | Count |
|---|---|
| Records verified (observed and compared) | **135 / 135** |
| Records with at least one released field | 135 (134 effective; Pitney Bowes Q3 2010 stays fully hidden by its restatement block) |
| Records with all three core quarterly flows released (revenue, net income, OCF) | **112** |
| Balance sheets released | **0** (all 135 stay quarantined) |
| Fields released | revenue_q 117, net_income_q 132, operating_cash_flow_q 133, gross_profit_q 48; fiscal-year: revenue 105, net income 103, OCF 113, gross profit 41 |
| Fields **not** released because they **differ** from the SEC original (possible later figures) | 22: revenue_q 7, net income FY 7, OCF FY 3, net_income_q 2, revenue FY 1, gross_profit_q 1, OCF_q 1 |
| Fields not released because they cannot be compared (no SEC value, mostly gross profit; or no vendor value) | 266 (of 1,080 field-records: 792 released, 22 differing, 266 not comparable) |

**How the release works** (`qr_fundamentals.py`, D114):
- A released report enters the store as a **partial record** carrying only its verified fields.
- It feeds the quarterly history used by True TTM.
- It is **never** the current report, so its balance sheet and other fields stay invisible.
- It never replaces an existing report, and it is invisible to any field it does not carry. **A release can therefore only add information**; the canary confirms this year by year.

**Tests** (`tests/test_field_release.py`, 9): no TTM through the hole without a release; released fields complete it; the balance sheet is never released and never current; no release before availability; restatement blocks win; a partial never replaces a report; no false fiscal-year end; unreleased fields unchanged; the shared observation step.

## A3. Updated yearly coverage

Non-financial eligible names with final usable data (approved TTM revenue, net income and OCF, plus assets and equity). Final canary **E976-06**, on the frozen infrastructure.

| Year | Non-financial eligible (names/month) | Final usable before (E976-04) | **Final usable after (E976-06)** | Native / repaired after | TTM values using a field release (stock-months: revenue / net income / OCF / gross profit) |
|---|---|---|---|---|---|
| 2010 | 615 | 84.2% | **84.2%** | 89% / 5% | 156 / 177 / 187 / 60 |
| 2011 | 758 | 69.6% | **76.8%** | 83% / 15% | 1185 / 1390 / 1417 / 494 |
| 2012 | 755 | 81.1% | **83.9%** | 87% / 45% | 68 / 73 / 68 / 39 |
| 2013 | 854 | 84.6% | **84.6%** | 86% / 61% | – |
| 2014 | 951 | 86.7% | **86.7%** | 88% / 68% | – |
| 2015 | 961 | 87.0% | **87.0%** | 88% / 65% | – |
| 2016 | 903 | 89.1% | **89.1%** | 90% / 67% | – |
| 2017 | 979 | 85.5% | **85.5%** | 86% / 53% | – |
| 2018 | 1,032 | 87.6% | **87.6%** | 88% / 52% | – |
| 2019 | 1,013 | 88.9% | **88.9%** | 90% / 49% | – |
| 2020 | 1,031 | 89.2% | **89.2%** | 89% / 72% | – |
| 2021 | 1,314 | 85.0% | **85.0%** | 85% / 74% | – |

**Approved-field availability** (share of non-financial eligible names; coverage only, no returns):

| Year | GP/A computable | OCF/A | NI/A | NI/E (equity > 0) | Revenue TTM | Total assets > 0 | Equity > 0 |
|---|---|---|---|---|---|---|---|
| 2010 | 82% | 90% | 87% | 85% | 87% | 99% | 97% |
| 2011 | 71% | 82% | 81% | 79% | 79% | 98% | 95% |
| 2012 | 81% | 89% | 89% | 87% | 87% | 99% | 96% |
| 2013 | 81% | 91% | 90% | 88% | 87% | 99% | 96% |
| 2014 | 84% | 91% | 91% | 89% | 88% | 99% | 96% |
| 2015 | 85% | 92% | 93% | 89% | 89% | 99% | 95% |
| 2016 | 87% | 94% | 93% | 89% | 91% | 99% | 94% |
| 2017 | 87% | 92% | 89% | 86% | 90% | 99% | 94% |
| 2018 | 88% | 92% | 91% | 87% | 90% | 99% | 94% |
| 2019 | 87% | 92% | 92% | 88% | 90% | 99% | 94% |
| 2020 | 87% | 93% | 92% | 88% | 90% | 99% | 94% |
| 2021 | 83% | 89% | 88% | 84% | 86% | 99% | 93% |

## A4. Updated bias assessment

- **The cleanup does not touch identity or survivorship.** The residual survivorship gap is unchanged:
  - 4–11 unresolved registrants with float ≥ $2B a year (about 0.5–1.2%), plus about six pre-XBRL acquisitions in 2010;
  - all still documented in `research/phase2/sec/residual_audit.json` and P2-CP7 item 4;
  - **not zero, not random**: mostly multi-class, non-listed and ADS issuers.
- **Data-availability bias is essentially unchanged** (E976-06):

| Year | Effect of the repair on the EW universe (pp/yr) | Non-financial names without usable data | Availability bias of a usable-only universe (pp/yr) |
|---|---|---|---|
| 2010 | +0.52 | 15.3% | -0.63 |
| 2011 | -0.39 | 23.1% | +0.81 |
| 2012 | -0.81 | 16.7% | +0.14 |
| 2013 | -0.40 | 15.3% | -0.06 |
| 2014 | -0.32 | 13.5% | +1.05 |
| 2015 | -0.22 | 13.0% | +0.75 |
| 2016 | -0.45 | 11.1% | +0.36 |
| 2017 | -0.54 | 14.1% | +0.44 |
| 2018 | -0.52 | 12.7% | +1.59 |
| 2019 | -0.58 | 11.1% | +0.74 |
| 2020 | -0.38 | 10.6% | -0.41 |
| 2021 | +0.06 | 14.6% | +4.05 |

2010–2021 equal-weight: native 13.8%/yr vs repaired 4.9%/yr; non-financial names with usable data 14.8%/yr vs without 8.3%/yr.

**Usable data by later outcome:**

| Later outcome | Securities | Eligible months | Usable months | Usable share |
|---|---|---|---|---|
| acquired/other | 606 | 21,898 | 17,529 | 80.0% |
| failed (bankruptcy 8-K item 1.03) | 32 | 952 | 405 | 42.5% |
| still trading | 1,661 | 111,156 | 97,282 | 87.5% |

**Reading:**
- The 2011 availability bias falls from +1.6 to +0.8 points a year, because the cleanup restores usable data in that year.
- Elsewhere nothing moves.
- A universe restricted to usable data still flatters **absolute** returns by about +1 point a year on average. This is neutral for relative tests only because candidate, benchmark and controls share it (owner item 2).
- Later-failed companies remain the least covered (43% usable). They are mostly repaired names whose XBRL history starts in 2011–2012.

**Verdict: the assessment has not materially changed. Part B proceeds.**

## A5. Tests and canaries

**Canaries:**

| Run | Purpose | Result |
|---|---|---|
| E979-01 | Field-level SEC verification of the 135 reports | Completed; 135/135 observed |
| E976-05 | Canary v1.2 after the cleanup; first live use of the harness warm-up | Completed; C1–C12 all 0; superseded by E976-06 (one later fix, see below) |
| **E976-06** | **Final canary on the frozen infrastructure v1** (exact frozen files) | **Completed; C1–C12 all 0**; first recorded equity $100,000.00 after 380 warm-up sessions; QuantConnect trading days 3,021 = chart rows; 134 field releases applied |

**Checks (all zero in E976-06):**
- SEC filing visible early;
- amendment early;
- quarantine exposed;
- restatement block exposed;
- timing hold violated;
- unjustified repaired entry;
- future share information;
- split jumps;
- eligible after last trade;
- TTM component before availability (C10);
- TTM component quarantined or blocked, other than through a verified field release of that very field (C11);
- **partial record ever current (C12, new)**.

**The one fix between E976-05 and E976-06.**
- In E976-05, a released quarter lacking an unverified field (e.g. gross profit) cut off that field's previous valid twelve-month window, lowering 2010 coverage by 0.25 points.
- True TTM now ignores a partial record for any field it does not carry.
- E976-06 confirms no year falls below its pre-cleanup level.

**Warm-up** (owner item 3; harness `warmup_start`, earliest 2008-07-01). Tests in `tests/test_warmup.py` (9) prove:
- the strategy close hook, and therefore every decision, never runs before the official start;
- no equity or cash record exists before it;
- orders are impossible during warm-up (two independent guards);
- eligibility statistics exclude warm-up days;
- the integrity checks fail any run whose equity or fills precede the start, or whose first equity differs from the initial cash;
- QuantConnect's trading-day count is compared without warm-up sessions;
- config validation;
- earlier runs' generated parameters stay byte-identical.

**All 501 tests pass** (480 at P2-CP7; new: 9 field-release, 9 warm-up, 3 freeze).

## A6. Infrastructure freeze (owner item 8)

**Frozen version v1:** `research/phase2/data_freeze_v1.json`.
- It lists 43 files with SHA-256 hashes. Combined hash `1e98a816c0c7214ad1b0b583380c60b08f7cf400df4a759fcf90b20d713bed09`; manifest hash pinned in `qresearch.datafreeze.MANIFEST_SHA256`; checked by `tests/test_data_freeze.py`.
- The final canary E976-06 ran on exactly these files.

**What is frozen:**

| Owner-listed component | Where |
|---|---|
| SEC identity mappings, correction table, survivorship repair layer | `qr_sec_corrections.py`, `qr_sec_data*.py` (table v3.2, 495 securities), audit copies `corrections.json`, `corrections_v2.json`, `identity_v2.json` |
| Identity matching priority rules | `identity_v2.py` (rules T, U, S, P, F, F2), `build_table_v2.py` (tiers A/B), `build_corrections.py` (v1 tiers) |
| Visa correction and universe rules | `qr_harness.py` (dated exchange override, US-common rule, NYSE/Nasdaq/AMEX, ≥ $2B, liquidity) |
| Filing-timing rules, +90-day fallback, 200-day freshness, field whitelist/blacklist | `qr_fundamentals.py` |
| Restatement blocking, quarantine/release rules (list and field-level), SEC timing holds | `qr_fundamentals.py`, `restatement_blocks.json`, `quarantine_release.json`, `field_releases.json`, `timing_holds.json` |
| True TTM construction | `qr_fundamentals.py` (`ttm_detail`, `observe_vendor`) |
| Financial/REIT classification | `qr_industry.py`, SEC SIC history in the table |
| History-only warm-up | `qr_harness.py` (`warmup_bounds`, guards) |

**Rule from now on:**
- Nothing in v1 may change because of H016 results.
- A genuine bug means: stop the research, document it, ask the owner, and issue **v2** before re-running anything affected.
- The test makes any silent change fail.

**Exception logic documented:**
- the Host Hotels SIC exception (kept as coded);
- Pitney Bowes Q3 2010 (blocked, not released);
- the 22 non-matching fields (kept quarantined);
- health insurers, real-estate services, exchanges, brokers and asset managers (excluded with all SIC 6000–6999, as approved).

---

# Part B — H016 Pre-Registration Proposal (design only)

**Supporting files:**
- `research/hypotheses/H016.md` (the hypothesis, PROPOSED);
- `research/phase2/H016_literature_review.md`;
- `research/phase2/H016_feasibility.py/.json` (assumption-only arithmetic, no project returns).

## B1. Exact hypothesis

**Universe.** Point-in-time eligible US common stocks: NYSE/Nasdaq/AMEX, market cap ≥ $2B, price ≥ $5, 20-day ADV ≥ $5M, with the SEC repair layer. They must be **non-financial and non-REIT** by the approved historical SEC classification, and have a **computable gross profitability**.

**Claim.** In that universe, the **20 stocks with the highest gross profits-to-assets**, chosen quarterly from information public at the time and held to the next rebalance, earn a better risk-adjusted return than the **equal-weight portfolio of the same universe**.
- Measured over 2010–2021, net of $7 per order and 10 bps slippage.
- The required size is the unchanged Phase 2 bar: G1–G4, including Sharpe(H) − Sharpe(EW) ≥ +0.25.

## B2. Economic rationale

1. **Profitability is a signal of value.** With price and book fixed, a firm with higher expected profits must carry a higher expected return (valuation logic; Fama & French 2006).
2. **Gross profit is the cleanest profitability measure available to us.**
   - It sits at the top of the income statement, before R&D, advertising and sales costs. Those are economically investments, but GAAP expenses them.
   - It is less exposed to accruals, one-offs, taxes and financing than net income.
3. **Assets as the denominator** measure the capital deployed and keep leverage out. Equity is distorted by buybacks and is negative for 3–7% of our names.
4. **Why the market might under-price it:**
   - High gross profitability is persistent, but it looks "expensive" on value metrics.
   - The literature documents a premium that hedges value.

## B3. External literature

Full review: `research/phase2/H016_literature_review.md`. In brief:

| Group | Sources |
|---|---|
| **Known before 2010** | Haugen & Baker (1996); Sloan (1996); Piotroski (2000); Fama & French (2006, 2008) |
| **Canonical GP/A evidence** (circulated April 2010, published 2013) | Novy-Marx (2013, JFE): GP/A predicts returns as strongly as value, also among large caps and within industries |
| **Later reassessment (2014–2017)** | Fama & French (2015) RMW; Ball et al. (2015, 2016): operating and cash-based profitability (not buildable from our validated fields); McLean & Pontiff (2016): about 58% post-publication decay; Novy-Marx & Velikov (2016): profitability survives costs; Harvey, Liu & Zhu (2016): multiple-testing discipline |
| **After 2017** | Hou, Xue & Zhang (2020): reported for context only; **not used** to choose (hindsight rule) |
| **Practitioner convention** | Exclude financials; quarterly-to-annual rebalancing; tens of names or more in long-only quality products |
| **Our own hypothesis** | That the effect is still large enough, post-publication, in a 20-stock large-cap long-only portfolio to clear +0.25 Sharpe over EW. That is the part being tested. |

## B4. Chosen measure

**Gross profits-to-assets (GP/A), and only GP/A.**

**Why it beats the alternatives on rationale, literature and data:**
- It has dedicated top-journal evidence, including in large caps and after costs.
- Both inputs were independently validated against the SEC (gross profit TTM 95.3% within 0.5%; total assets 98.8%).
- It has low turnover.

**Not chosen:**
- **ROA and ROE:** older and mixed evidence; accrual and leverage pollution.
- **Operating profitability:** stronger in later papers, but not buildable (operating income failed validation).
- **Cash flow-to-assets (OCF/A):** distinct rationale, but only a component in the literature and noisier. It is offered as the owner's alternative (B17.1), never as a second candidate.

**Coverage cost** (disclosed): GP/A is computable for 82% (2010), 71% (2011) and 81–88% (2012–2021) of non-financial eligible names. That is about 5–8 points fewer than OCF/A, because some companies report no gross-profit line.

## B5. Formula, using only approved fields

  **GP/A(T) = gross_profit_ttm4q(T) / total_assets(T)**

- **gross_profit_ttm4q:** the True TTM. It is the sum of the four most recent visible consecutive quarters, with Q4 validated against the fiscal-year total, and is available only after the newest quarter's filing.
- **total_assets:** the snapshot of the current point-in-time report.
  - It must belong to the **same fiscal quarter** as the newest TTM quarter; otherwise GP/A is not computable (no mixed periods).
  - It must exist and be **> 0**. A zero or negative denominator means the name is excluded.
- **Negative gross profit** is allowed and ranks low. No winsorising is needed for a rank.
- **Freshness:** the frozen 200-day rule (newest quarter at most 200 days old on T). No extra rule.
- **Missing values:** a name without a computable GP/A on T is **outside the universe** for the candidate, the EW benchmark and the controls alike (owner item 2).
- **Never used:** operating income, free cash flow, EPS, share counts, vendor ratios, or any non-whitelisted field. The frozen whitelist enforces this with a hard failure.

## B6. Universe

- **Eligibility:** the harness rules above, with the SEC layer on (table v3.2).
- **Exclusions:** `qr_industry.excluded()` at T. The SEC SIC at filing decides: REIT 6798, financial 6000–6999 (banks, credit, brokers, exchanges, asset managers, insurers incl. health insurers, real estate incl. real-estate services). The filing-structure rule applies only where no SIC is visible.
- **Data requirement:** GP/A computable at T.
- **Sharing:** the identical universe function serves the candidate, the EW benchmark and every control.
- **Reporting:** yearly coverage and the availability-bias table are reported with every result.

**Expected size** (coverage only):

| Year | Non-financial eligible names | GP/A computable |
|---|---|---|
| 2010 | about 615 | about 500 |
| 2011 | about 760 | about 540 |
| 2021 | about 1,310 | about 1,090 |

## B7. Portfolio construction

| Item | Proposal | Reason |
|---|---|---|
| Positions | **20**, equal weight at entry (each about 4.9% of $100K) | See below |
| Selection | The top 20 by GP/A; ties by security id, ascending | Deterministic |
| Weighting | Equal; continuing holdings are not resized at a rebalance | Fewer orders; weights drift within the quarter |
| Cash rules | D051 unchanged: settled cash only, 2% buffer, 15% gap reserve, max 10% weight, no leverage | Approved execution model |
| Minimum position | **$4,500** (approved rule: $5,000) | Needed for 20 slots at $100K; requires your approval |
| Primary / sensitivity | $100,000 / $200,000 (same 20 names; about $9.8K positions) | As instructed |

**Why 20 positions, decided on principle and not on returns:**
- **Diversification.** A profitability ranking is a weak per-stock signal, so idiosyncratic noise must be diversified. With about 28% idiosyncratic volatility, the idiosyncratic tracking against the factor falls from 7.2% (15 names) to 6.3% (20) and 5.1% (30).
- **Cost.** $7 per order is fixed, so more names cost more. At 20 names and a plausible 15–35% quarterly replacement, costs are about **0.3–0.7% a year**, far below G4(c)'s 1.5% cap. At 30 names they rise to 0.4–0.9% for little extra diversification.
- **Rules.** 20 is the largest count that keeps positions near the approved minimum size. It needs only the minimum-position change. The alternative, 15 under the existing rules, is noisier.

## B8. Rebalance schedule

**Timing:**
- **Quarterly.** The signal is taken at the close of the **first trading day of March, June, September and December**, and executed at the next open.
- **Why these months:** they follow the SEC deadlines for our large-accelerated filers.
  - 10-K: 60 days after fiscal year-end (about 1 March for calendar years).
  - 10-Q: 40 days after quarter-end (about 10 May, 9 August, 9 November).
  - The fresh information of most of the universe is therefore available at each rebalance.
  - Non-calendar fiscal years simply use their latest visible TTM.

**Between rebalances:**
- Hold. There is no stop-loss, no timing rule, and no exit on leaving the universe.
- Delistings and untradeable holdings are handled by the frozen harness (data handling, not strategy exits).
- Acquisition proceeds wait in cash for the next rebalance.

**At each rebalance:**
- Holdings that are not in the new top 20, including any that left the universe or lost a computable GP/A, are sold.
- New entrants are bought at the slot weight. D051 funds buys from settled cash, so some buys may execute a session after the sells.

**Warm-up:** history only from 2008-07-01 (approved, D114). The first decision is on 2010-03-01.
- **Assumption on Jan–Feb 2010:** the account holds cash from 2010-01-04 to the first rebalance, which is two months of cash drag.
- **Alternative (owner decision B17.3):** an initial formation on the first trading day of 2010.

## B9. Expected turnover and costs

These are from assumptions, not our data (`H016_feasibility.json`).

| Quarterly replacement (share of the 20 names) | Orders a year | Commission | Slippage | Total cost a year |
|---|---|---|---|---|
| 15% | 24 | 0.17% | 0.12% | **0.29%** |
| 25% | 40 | 0.28% | 0.20% | **0.48%** |
| 35% | 56 | 0.39% | 0.27% | **0.67%** |

- At $200K the totals are 0.20–0.47%. Acquisitions and delistings add a few orders.
- GP/A is persistent (the literature classifies it as low-turnover), so the low-to-middle rows are expected.
- **Concentration:**
  - 20 names at about 5% each; the maximum weight of 10% only binds after strong drift.
  - Expect a sector tilt towards asset-light industries (software, consumer brands, health-care products). It is reported as a diagnostic, not constrained.

## B10. Controls

All use the **identical H016 universe** at each date, the same costs, $100K, and the same harness and warm-up.

| Book | Role | Mechanics |
|---|---|---|
| **EW-H016** (benchmark) | G1, G3, G4(a/b) comparator | Equal weight of the **entire** H016 universe. The approved B901 benchmark mechanics (monthly rebalance, 25% band, D051, large paper notional) apply, with only the universe changed. |
| **SPY** | G1.1(b) passive reference | Existing E900-07, unchanged |
| **R1–R5** (random) | G2 control | The same 20 slots, quarterly schedule, holding rules and costs, but with the GP/A ranking replaced by a **fixed seeded random key per security** (seeds 1–5). |

**Why the random control isolates the profitability ranking:**
- It holds the universe, mechanics and position count fixed, and changes **only** the ranking.
- Its persistent key makes its turnover come from universe changes, similar to the candidate's. A redrawn-every-quarter control would differ in turnover too.
- Turnover, cost drag, exposure and slot usage are reported for every book to show comparability.

**No further control is proposed.**
- A "lowest GP/A" book would amount to a long-short factor test and add a degree of freedom.
- Sector-neutral variants change several things at once.

## B11. Candidate count

- **One** candidate (a single pre-registered rule). There is no A/B choice, no parameter grid, and no alternative measure.
- **DSR diagnostic views:** Phase 2 selection configurations = 3 (H014's 2 + H016's 1); cumulative = 43 (40 + 3); plus the robustness view.
- **Gates (unchanged G1–G4, with the universe-consistent benchmark):**
  - **G1:** vs EW-H016 (+0.25 Sharpe, CAGR within 2 points, Calmar ≥, drawdown within 5 points) and vs SPY (+0.10).
  - **G2:** Sharpe(H) > the median of R1–R5.
  - **G3:** six two-year blocks vs EW-H016 (positive in ≥ 4; no block > 50% of the excess).
  - **G4:** see B14; (c) cost drag ≤ 1.5% a year.

**The one structural adaptation:**
- G1, G3 and G4 use the **H016-universe EW** instead of E901-07, because you required the benchmark to share the universe exactly.
- E901-07 (the full eligible EW) is still reported for reference.

## B12. Statistical feasibility

Assumption-based: T = 12 years, EW Sharpe about 0.8; `H016_feasibility.json`.

**Precision of the test.**
- The standard error of Sharpe(H) − Sharpe(EW) is about **0.18** if the two return streams correlate at 0.90, and about 0.22 at 0.85.
- The +0.25 margin is therefore about 1.2–1.4 standard errors.

| True Sharpe advantage | Chance the estimate clears +0.25 (ρ 0.85–0.90) |
|---|---|
| 0.00 (no effect) | 6–11% (false-pass risk) |
| 0.10 | 19–23% |
| 0.20 | 39–41% |
| 0.25 | 50% |
| 0.40 | 74–78% |

**Plausible true size.**
- The published high-minus-low GP/A spread translates into a much smaller long-only, large-cap, top-20 advantage over EW.
- After about 50% post-publication decay (McLean & Pontiff) I expect a true advantage of roughly **0.0–0.2**.
- So **P(pass G1) is about 15–30%**, and lower for passing G1–G4 together.
- The bar is not weakened (owner item 15). The value of the test is a clean, pre-registered answer.

## B13. Relationship to previous research

- C01–C03 and H014 were all **price-based swing/trend rules**, and all were rejected (No Production Candidate). H015 (trend portfolio) was not adopted.
- H016 is the **first fundamental hypothesis**. It is a slow-moving characteristic, rebalanced quarterly, with holdings of months (not days to weeks). It is economically unrelated to the earlier signals.
- It follows the programme review (CP3j) and the opportunity review (P2-CP3), which put profitability/quality first.
- **Scope note:** quarterly rebalancing means some names may be held for more than a year if they stay in the top 20. That is within "weeks to months" only loosely (B17.6).

## B14. Overfitting risks and safeguards

| Risk | Safeguard |
|---|---|
| Choosing the measure from our data | Chosen from literature and field validation only; no metric was ever computed on returns |
| Data snooping through infrastructure changes | Data infrastructure frozen (v1, hash-pinned); no change because of results |
| Free parameters (N, schedule, freshness) | Fixed from principles (diversification and cost, filing deadlines, the frozen 200-day rule) before any run |
| Robustness after the fact | **G4(a)** perturbations pre-declared now (run only if G1–G3 pass): P1 N = 15; P2 N = 25; P3 rebalance in Jan/Apr/Jul/Oct; P4 Feb/May/Aug/Nov; P5 semiannual (Jun/Dec); P6 freshness limit 120 days. At least 5 of 6 must keep Sharpe − Sharpe(EW-H016) ≥ +0.10. **G4(b):** 2× slippage. Also reported: 4× and 6×. No other perturbation may be added. |
| Post-publication decay | Expected and disclosed; the bar is unchanged |
| Sector concentration | Reported per year (diagnostic); not "fixed" after results |
| Availability bias (about +1 point a year in levels) | Same universe for every book; reported per year |
| Seed choice in controls | Seeds 1–5 fixed now; G2 uses the median |

## B15. Expected QuantConnect run count

| ID | Kind | Book | When |
|---|---|---|---|
| X980 canary | infrastructure | H016 construction canary: GP/A inputs, timing, universe counts and ranking determinism, without returns | Before any committed run |
| E016-01 | research | Candidate, $100K | Committed |
| E016-02 | benchmark | EW-H016 | Committed |
| E016-03 … E016-07 | benchmark | R1–R5 | Committed |
| E016-08 | sizing | $200K sensitivity | Committed |
| E016-09 … E016-11 | research | 2×, 4×, 6× slippage | Only if G1–G3 pass |
| E016-12 … E016-17 | research | Perturbations P1–P6 | Only if G1–G3 pass |

**Totals:** 1 canary plus 8 committed runs, plus up to 9 conditional, so at most **18** runs.

## B16. Runtime and cost estimate

- **Runtime.** Each run observes every company daily from July 2008, like the canaries, which took 12–16 minutes. Trading books add order handling, so allow about 15–20 minutes each.
  - Committed: about 2.5–3 hours of backtest node time.
  - Maximum: about 5–6 hours.
- **Cost.** **No additional cost**: everything runs within the existing $24/month QuantConnect subscription.
- **Registry and budget.** The runs are logged in `experiments/INDEX.csv`. The D085 research budget is not reached.

## B17. Exact decisions requiring your approval

1. **The measure:** GP/A as the single H016 measure (recommended). The only alternative with a distinct rationale is OCF/A (cash flow-to-assets). Choose one; they are never both tested.
2. **The portfolio:** 20 positions with the minimum position lowered to $4,500, all other D051 rules unchanged (recommended); or 15 positions under the current rules.
3. **The schedule:** quarterly, first trading day of Mar/Jun/Sep/Dec (recommended). For the start, choose:
   - **(a)** the first decision on 2010-03-01, with cash until then (recommended: no off-schedule rule); or
   - **(b)** an extra initial formation on 2010-01-04.
4. **Controls:** EW-H016 (B901 mechanics on the H016 universe), SPY (E900-07), and random R1–R5 with persistent seeded keys.
5. **The gate adaptation:** G1/G3/G4 use EW-H016 instead of E901-07; G2 is "beat the median random"; the G4(a) perturbations P1–P6 and the G4(b) 2× slippage, as listed in B14. Everything else in G1–G4 is unchanged; DSR and PBO stay diagnostic.
6. **Scope:** holdings may last more than one quarter, possibly over a year. Please confirm this fits the Phase 2 "weeks to months" scope.
7. **The run plan:** the X980 canary first, then E016-01…08, and E016-09…17 only if G1–G3 pass. This approval would **consume Phase 2 slot 2**.
8. **After approval, implementation will:**
   - write the frozen H016 spec (hash-pinned, like `P2_spec.md`), the S016 strategy, the B9xx benchmark and the controls, using the frozen data infrastructure v1 unchanged;
   - run the canary;
   - **stop before the committed runs** if anything in the canary fails.

**STOP.** H016 is not implemented and was never run. No candidate or factor returns, no slot used, Holdout locked.
