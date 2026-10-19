# Research Reset — QuantConnect Migration Impact and Updated Long-Term Research Roadmap

**Checkpoint:** RR1.
**Date:** 2026-10-19.
**Decisions:**
- D259: the owner direction, verbatim in `docs/owner/2026-10-19_research_reset_direction.md`.
- D260: this checkpoint.

**Status:** planning review only. **STOPPED awaiting the owner.**

**Not done:**
- No QuantConnect backtest or project change, and no Platform Data exported or downloaded.
- No new hypothesis, implementation, optimisation or frozen-experiment change.
- No H028 recovery, no reopening of SYS-1, no purchase or subscription, no Holdout access.
- Nothing in this document is activated. Every proposal needs a separate owner decision.

**Sources:**
- **Official QuantConnect documentation**, read 2026-10-19:
  - [Morningstar Migration](https://www.quantconnect.com/docs/v2/writing-algorithms/universes/equity/morningstar-migration);
  - [migration announcement](https://www.quantconnect.com/announcements/21449/migrating-to-morningstar-039-s-new-equity-data-feeds);
  - [US Fundamental Data](https://www.quantconnect.com/docs/v2/writing-algorithms/datasets/morningstar/us-fundamental-data);
  - [US Equity Security Master](https://www.quantconnect.com/docs/v2/writing-algorithms/datasets/quantconnect/us-equity-security-master);
  - [AlgoSeek US Equities](https://quantconnect.com/docs/v2/writing-algorithms/datasets/algoseek/us-equities);
  - [LEAN engine versions](https://www.quantconnect.com/docs/v2/cloud-platform/projects/lean-engine-versions);
  - [Object Store](https://www.quantconnect.com/docs/v2/cloud-platform/object-store);
  - [Change log](https://www.quantconnect.com/docs/v2/meta/change-log);
  - [Terms v1.5](https://www.quantconnect.com/terms).
- **Committed repository evidence**, cited by decision or checkpoint.
- **One read-only metadata call:** the LEAN version list (`lean/versions/read`; no data, no project touched).

**The Migration Atlas could not be read.** It is hosted at `cdn.quantconnect.com/i/tu/qc_migration_atlas_v3.html`, and this environment's network proxy refuses that host. Its per-property and per-year statistics are therefore unknown here (U1, §8). The owner can open it in a browser. Allowlisting the host would also make it readable in a new session.

---

## 0. Summary

1. **What changed**, in three kinds:
   - **Documented by QuantConnect:** the whole fundamental history (1998 on) was rebuilt from a new Morningstar feed. Coverage, values, signs, field lists and dating rules changed.
   - **Platform rules:**
     - engine selection is gated to the Trading Firm tier;
     - code is reviewed for data probing;
     - exports are prohibited by any means, with derivatives counted as Platform Data;
     - project files must be plain, uncompressed source.
   - **Demonstrated by our own runs:** frozen Data v1 does not reproduce. On the current dataset, market cap is missing for about 18% of eligible stock-months, concentrated in companies that later disappear.
   - **Not documented, and not demonstrated by us either way:** any change to **price data**. It is an open question, not an assumed change.
2. **What it does to the completed research:**
   - **No conclusion changes.** All rejections stand as historical evidence.
   - **Almost nothing can be re-run exactly.** Every frozen data layer is packed, and it is either built on retired data or carries an identity table assembled from earlier QuantConnect exports.
3. **What remains feasible on QuantConnect alone:** research on 2010–2021 with a market-cap universe that has a survivorship gap unless it is repaired with SEC data.
   - The window has been used heavily: 30 hypotheses and 581 logged experiment records.
   - No 20–30-year test with the approved point-in-time ≥ $2B universe is possible on QuantConnect's current data.
4. **Recommended roadmap: Option 3.** A licensed point-in-time dataset (with delisted companies) and a small local engine, gated by a desk-only verification first.
   - It is the only option found that gives the approved universe over about 1999–2021 plus the sealed Holdout. It also takes the research off a platform that broke the frozen chain five times in 13 days.
   - It requires the owner to revisit D123 (no data subscription until a promising result) and D001 (QuantConnect as the single engine).
   - **Fallbacks:** Option 1 (QuantConnect, price-first, modest expectations) or stopping.

## 1. Verified QuantConnect change inventory

### 1a. Documented platform changes (official text)

| # | Area | What the documentation says | Source |
|---|---|---|---|
| Q1 | Morningstar feed | Morningstar retired its Global Equity Data Feeds; QuantConnect rebuilt the **entire history** (from January 1998) from the new Equity Data Feeds | migration page; US Fundamental page |
| Q2 | Timeline | New data opt-in until 2026-10-10, default from 10-10/11; old dataset on a separate branch during October; **retired for backtesting and live trading 2026-10-31**; no option to keep old and new values side by side, "so old backtests will not reproduce" | migration page; announcement; change log 09-22 / 09-24 / 09-25 |
| Q3 | Coverage | 8,717 → 9,705 companies in the comparison; `HasFundamentalData` true for more securities; a larger dataset changes universe selection even where values are unchanged | announcement; US Fundamental page |
| Q4 | Values | About **one third** of values present in both generations differ, "usually by more than 20%"; historical series recalculated | US Fundamental page; announcement |
| Q5 | Signs | Sign convention changed for some expenses and outflows (e.g. cost of revenue, operating expenses) | announcement |
| Q6 | Fields | **535 new and 1,251 retired properties.** Retired members still compile but throw `NotSupportedException` when read, naming a replacement where one exists (e.g. `DividendCoverageRatio.ThreeMonths` → `.TwelveMonths`; `NormalizedDilutedEPSGrowth`: none) | US Fundamental page; migration page |
| Q7 | Dating | Ratio, growth, per-share and average properties are now dated by the **filing** (median **63 days** later than before); previously they were dated at period end, so old backtests could read them early. Price multiples (P/E, P/B) now daily, not monthly | migration page; announcement |
| Q8 | Before 2013 | **The new feeds lack actual filing dates for statements before 2013**: earlier dates are kept where available, otherwise a nominal **45-day** delay is applied | announcement; US Fundamental page ("file date estimated as about 45 days after the as-of date for older symbols") |
| Q9 | Point in time | Fundamentals are loaded "As Original Reported"; history requests cover all US equities "including delisted companies" | US Fundamental page |
| Q10 | Not documented | Market-cap methodology changes; CIK / company-id changes; whether sector codes are point-in-time; any price or Security Master change | (absence noted on all pages read) |
| Q11 | Prices / corporate actions | AlgoSeek US Equities: survivorship-bias-free, about 27,500 securities since 1998. Security Master: about 27,500 equities from January 1998, with splits, dividends, delistings, mergers and ticker changes (map / factor files). **No 2026 change is documented** | dataset pages |
| Q12 | Engine | Default = latest `master`; older or custom versions only for **Trading Firm / Institution** tiers. Read-only metadata today: `master` = **18194** (created 2026-10-19), `morningstar-legacy` = 18184 (2026-10-15; its note: delisted securities now stay in the algorithm until sale proceeds settle) | engine page; `lean/versions/read` |
| Q13 | Terms | **v1.5, last updated 2026-10-08.** §2.6 (key points): | Terms |
| | | (a) Platform Data includes any "transformation or derivative from which the original values can be reconstructed or approximated" | |
| | | (b) storing and reusing it on the Site (incl. Object Store) is allowed; export only through permitted channels | |
| | | (c) prohibited: logs, charts, statistics or order tags carrying data; encoding / compressing / splitting; getting around limits on logs, output, storage or downloads; designing outputs that reveal data | |
| | | (d) the account holder is responsible for AI agents | |
| | | (e) permitted exports: own source code and **summary results** (statistics, equity curves, own orders), not designed to convey Platform Data | |
| | | (f) no small-amount or verification exceptions | |
| | | (g) monitoring | |
| Q14 | Policies (change log) | 10-06 data-use policy and ban on code obfuscation; 10-07 AI-agent rule "stop and report when compliance is uncertain"; 10-08 "no export by any means"; 10-15 new endpoints export own orders / closed trades as CSV | change log |
| Q15 | Object Store | Paid organisations: 50 MB / 1,000 files free (we have S-MICRO, $0); paid tiers $12–$120 / month. Downloads only for Institution tier with a derived-data agreement; **all contents are Platform Data**; contents are monitored | Object Store page |

### 1b. Platform enforcement observed directly (refusal messages, not in the pages read)

| # | Date | Observation | Record |
|---|---|---|---|
| O1 | 2026-10-06 | Engine pin refused ("migrate your organization to trading firm"); a pinned project then ran on 18166 | D180 / D181 |
| O2 | 2026-10-10 | Compile-time compliance review rejects data probing / validation code; one run stopped mid-way ("Deleted by request") | E995-05 / E995-04, D185 |
| O3 | 2026-10-10 | 50 files per project; 64,000 characters per file | E995-01, D111a |
| O4 | 2026-10-19 | Terms acceptance required before any API run | D252 / D253 |
| O5 | 2026-10-19 | **Project files that import a compression or encoding package are refused** ("all project files must be saved as readable plain-text source") | E032-01, D254 |
| O6 | 2026-10-19 | Support (written): SEC EDGAR data may go to the Object Store as plain JSON; QuantConnect identifiers and universe membership must be **generated in-cloud**, never reused from earlier extractions; results only via the official export | D257 |

That is **five research-blocking platform events in 13 days** (O1, the dataset switch, O2, O5, plus O4's interruption).

### 1c. Effects demonstrated by our own research

| # | Effect | Evidence | Strength |
|---|---|---|---|
| R1 | The September opt-in branch (18131, which our CP2–P7 work used) and the October default (18178) are **different data**: | E993-02 vs E993-03 (D183) | strong (same frozen code) |
| | – reports with unknown filing timing 608 → 31,538 | | |
| | – usable revenue baselines 78,633 → 2,269 | | |
| | – eligible stock-months 93,687 → 76,915 | | |
| R2 | On the current dataset, **market cap is missing for about 18%** of Data-v1 eligible stock-months 2011–2017, concentrated in later-disappearing companies (a survivorship bias). The SEC cover-share method rebuilds 68.9% of the lost stock-months | X996 (D187); X997 (D189) | strong |
| R3 | On the current dataset the fundamental *stream* is point-in-time in timing: 96–99% of reports first appear the day after the SEC filing, including pre-2013, even though `file_date` is unusable | X996 (D187) | strong |
| R4 | **No market cap before October 2009** (4–27 names ≥ $2B a year vs about 700 from 2010); dead pre-2009 firms lack fundamentals in the old dataset | D027, P2-CP11 (measured on 18131 / old dataset) | strong for 18131; **not re-measured on the current default** (U2) |
| R5 | Within the current dataset, exact reproduction held 2026-10-10 → 10-13: | E998-01 / E801-01 (D207); E031-01 / E031-06 (P14-CP3a) | strong |
| | – Data v2 eligibility digests matched (84 / 84) | | |
| | – frozen H028 and LV15 reproduced to the cent on 18179 after being produced on 18178 | | |
| R6 | QuantConnect's data snapshot changed within one day once (12 reviews of 2011 Score v1 rows outside the analysed population) | D202 | strong (single event) |
| R7 | **Price data was never compared value by value across datasets**, because that would need a price export. Indirect consistency only: | P7-CP5d §91, P7-CP5e, P7-CP5f | **inconclusive** — neither change nor stability is shown |
| | – technical recomputation 168 / 168 | | |
| | – no lost universe member attributed to price or ADV | | |
| | – regime shares unchanged (75% / 6%) | | |
| | – split continuity 223 / 224 | | |
| R8 | Older price-side quirks, all on 18131 and not re-verified since: | D062, D162, D167 | carried forward as assumptions |
| | – acquisitions without delisting events | | |
| | – dividends rounded to the cent | | |
| | – ticker ids joining two companies' histories | | |
| R9 | Vendor CIK and sector codes are current-status, not point-in-time | D111, P7-CP1 | strong (old data; current data unknown) |

## 2. Data availability and integrity matrix by period

Key:
- **OK**: usable as approved.
- **GAP**: usable with a known, disclosed bias.
- **NO**: not usable for the approved universe.
- **?**: not verified.

"Our exposure" counts what this programme has already looked at.

| Period | QC prices & corporate actions | PIT market cap ≥ $2B (QC current) | QC fundamentals, PIT | SEC structured data (XBRL) | Our exposure | Usable for |
|---|---|---|---|---|---|---|
| 1998–2003 | documented OK (from 1998-01); not audited by us | **NO** (R4, measured on 18131; current ?) | values exist; filing dates nominal (Q8) | none (text filings only) | benchmarks / size proxy only (E900-02, E950–E952); no strategy returns | price-only work with a non-approved universe, or the D035 stress test only |
| 2004–2008 | as above | **NO** | as above | none | as above | as above |
| 2009 | as above | from October only | as above | phase-in (large filers from mid-2009) | infrastructure audits only (no returns) | warm-up only |
| 2010 | OK (used since CP2) | **GAP** (R2; about 6 pre-XBRL acquisitions, D113) | stream PIT (R3); dates nominal (Q8) | partial | H001–H021 development | development |
| 2011–2012 | OK | **GAP** (R2; SEC repair possible) | as above; SEC-only gates very thin (D187) | most large filers | heavily used | development (exposed) |
| 2013–2017 | OK | **GAP** (R2) | as above; actual filing dates | complete | heaviest use: H001–H030 | development (exposed) |
| 2018–2021 | OK | **GAP** (R2) | as above | complete | H005 validation; H026–H030 development (since D206) | development (exposed); **no longer untouched** |
| 2022-01-01 → 2026-08-31 | — | — | — | — | **SEALED, never accessed** | the one untouched test (owner approval at CP5) |
| 2026-09-01 → freeze | — | — | — | — | locked (D094 category U) | locked |
| After a future freeze | — | — | — | — | — | forward evidence only |

**Integrity facts that cut across periods:**
- **Reproducibility:** within one data snapshot and build. Exact reruns hold over days (R5) but not across the September → October datasets (R1). After 2026-10-31 there is one dataset, and its snapshot can still move (R6).
- **Engine:** we cannot choose it (Q12, O1). Every run now executes on whatever `master` is (18178 → 18179 → … → 18194 in 9 days).
- **Fundamental values:** re-measured against SEC only for the fields and years Data v2 / v2.1 / v3 audited (2011–2021). Other fields are unverified on the current data, and in-cloud validation exports are refused (O2).

## 3. Impact on completed research

The categories follow the owner's list.
- **Valid** = still valid as historical evidence.
- **Not repro** = not reproducible on the current platform.
- **Changed data** = dependent on discontinued or materially changed data.
- **Reusable** = potentially reusable in a new implementation.
- **Unknown** = requires future verification.

No status, result or conclusion is changed by this table.

| Component | Valid | Not repro | Changed data | Reusable | Notes |
|---|---|---|---|---|---|
| H001–H014 (C01–C03, Phase 2 price / trend) | **yes** | yes | yes: universe from 18131 market cap | hypotheses no (rejected); harness ideas yes | results were on 18131; the universe composition differs today (R1, R2) |
| H016 (GP/A), H017 (8-K continuation) | **yes** | yes | yes: Data v1 fundamentals / universe | SEC Event Data v1 (public SEC) reusable | rejections stand |
| H018–H021 (technical search, cross-sectional signals, chart score, sector ETFs) | **yes** | yes | H018–H020 universe yes; H021-A (sector ETFs) prices only | null / engine code reusable | H021-A depends only on ETF prices and is closest to reproducible, but the engine version differs |
| H022 on Data v1 (c_IC DATA_V1_ONLY) | n/a (never computed) | yes | yes | no | superseded by H022 on Data v2 |
| H022 (Data v2), H023–H025 | **yes** | yes: packed tables (O5) + identity (O6) | partly: identity inputs from 18131 exports | SEC components, Form 4 ledger reusable | built on 18178, so values are current-dataset values |
| H026–H027 | **yes** | yes | partly (identity) | pure modules (Ridge, LV15, account engine) reusable | |
| **H028** | **yes, REJECTED**; its conditional-null p-value is structurally suspect (D238) | **yes: exact reproduction not achievable** (SYS1-CP2) | partly (identity) | descriptive "Frozen Defensive Research Reference" only | no recovery attempted (per D259) |
| H029 / H030 | yes: NOT EVALUABLE | yes | partly | Data v3 SEC-only components reusable | |
| OC-2 (synthetic only) | **yes** | n/a (offline) | no | method lessons | never touched QuantConnect data |
| **SYS-1** | never run; **no evidence** | yes (SYS1-CP0 / CP2) | yes | `qr_sys1` account engine (pure code) reusable | the SYS1-CP2 decision is still with the owner; RR1 does not reopen it. The recommendation is unchanged: close as NOT RUN — PLATFORM BLOCKED |
| Data v1 (frozen D114) | as a record | **yes** (D183) | **yes** | SEC correction methods (D111 / D113) reusable | |
| Data v2 / v2.1 / v3 | as records | **yes**: packed (O5); identity table 88% from QC-derived evidence (O6) | partly | SEC-only parts (filing dates, cover shares, restatement guard, first-filed values) reusable as plain JSON | about 5–6M characters of SEC JSON fits in the free 50 MB Object Store |
| Event Data v1, Form 4 ledger, SEC cache, timezone conventions | yes | n/a | no (public SEC) | **yes** | keyed by CIK; joining to securities needs a new identity map |
| Pure libraries (metrics, stats, nulls, synthetic studies, `qr_h026.simulate`, `qr_sys1`) | yes | n/a | no | **yes** | deterministic, data-free |
| Permanent methodological lessons: | **yes** | n/a | no | **yes** | independent of the platform |
| – D139: no-edge worlds yield SPY-beating "best" configurations | | | | | |
| – D238: pointer-tether nulls mislead | | | | | |
| – power limits (P4-CP3, LH-CP4, OC-CP5) | | | | | |
| Locally committed exports (benchmark daily paths, per-stock tables) | as records | — | — | **Unknown**: whether they are "summary results" under §2.6(e) or Platform Data under §2.6(a) | SYS1-CP1 §7 / U6; nothing is reused until this is clarified |
| Holdout 2022-01-01 → 2026-08-31 | **sealed, never accessed** | — | — | **yes**: the only untouched data | |

**Bottom line:** the evidence base stands. The infrastructure does not. The frozen chain cannot be re-uploaded or regenerated, and the 2010–2021 window is used up as a source of independent confirmation.

## 4. Feasible future research approaches

Common to all approaches:
- The universe filters stay as approved: US common, NYSE / Nasdaq, PIT market cap ≥ $2B, price ≥ $5, ADV20 ≥ $5M.
- Price ≥ $5 and ADV20 ≥ $5M are enforceable point-in-time from price bars wherever bars exist (QC from 1998).
- **The binding constraint is the PIT market cap.**

| Attribute | A. Price & volume on QC | B. QC fundamentals only | C. Hybrid on QC (prices + SEC JSON in the Object Store) | D. Any of A–C on a licensed PIT dataset, local engine |
|---|---|---|---|---|
| Earliest defensible date (approved universe) | **2010** (market cap from October 2009; 1998 only with an owner-approved non-cap universe, which D033 rejected) | **2013** by QC's own documentation (Q8); 2011 is supportable only with an SEC filing gate, which is approach C | **2011** (Data v2.1 start; 2010 thin) | **about 1999** if the vendor's claims hold (P2-CP12: Sharadar, from 1998, about 9,000 delisted companies, daily market caps, as-reported fundamentals keyed by filing date) — **unverified (U8)** |
| Listed / delisted coverage | prices survivorship-free (Q11); **the cap filter loses about 18% of stock-months, mostly disappearing firms (R2)** | as A, plus field coverage per field | cap gap repaired for 68.9% of lost stock-months; residual identity gap 3.4–6.9% a year (Gate K, D192) | vendor claim includes delisted firms; to audit |
| Cap / price / ADV enforceable PIT | price, ADV yes; cap with a GAP | as A | yes, with residuals | yes if verified |
| Survivorship / look-ahead risks | survivorship through the cap gap; engine drift | as A + pre-2013 nominal dates (Q8); 1/3 of values recalculated (Q4) | identity mapping; SEC timing solid (D111 / D122) | vendor data quality, delisting returns, identity / corporate actions: all to audit |
| Dependence on current QC data | high (prices + market cap) | very high | high (prices, symbols) + SEC (ours) | none (QC optional) |
| 20–30-year testing credible | **no** (12 years + Holdout) | **no** (9 years) | **no** (11 years) | **plausibly yes**: about 23 years 1999–2021 + Holdout |
| Complexity | low (no reference data) | medium (field re-audit without in-cloud validation, O2) | **high** (in-cloud identity pipeline, Object Store loader, audits; SYS1-CP2 §2) | medium once (ingest, audit, freeze), then low per test |
| Rigorous OOS validation | weak: 2010–2021 exposed; price / technical families already failed there (H001–H014, H018–H021) | weak: the same window, fundamentals exposed by H016 and H022–H030 | weak: same window | **better**: 1999–2009 has had no strategy returns computed (only benchmarks), then the Holdout |
| Terms of Service | cleanest (no uploads; summary outputs) | clean if outputs are summary only | Support-endorsed path (O6), but contents become Platform Data (Q15) and validation exports are refused (O2) | outside QC's Terms; governed by the vendor's licence (personal use, no redistribution; to verify) |

**Caveats on D:**
- 1999–2009 is unexamined by *our strategies*, but not by the world. The dot-com bust and the 2008 crisis are well known, and much published anomaly evidence was estimated on those years. A hypothesis drawn from a paper whose sample covers 1999–2009 is in-sample there.
- Pre-registration must therefore state the economic rationale independently of those episodes, and report sub-period results.

## 5. Proposed research and validation architecture (PROPOSAL — needs separate owner approval)

**Exposure ledger.** The programme has tested:
- H001–H030;
- 581 logged experiment records (371 completed);
- more than 2,000 strategy variants, including the 1,533-configuration H018 search, 415 H024 models and 92 H023 weightings;
- all on 2010–2021 (2011–2021 since Phase 11).

Any new hypothesis evaluated on 2010–2021 inherits that search. **2010–2021 can serve as development and engineering data, not as confirmation.**

**Proposed separation** (Option 3 data; under Options 1 / 2 only steps 1, 4 and 5 exist):
1. **Development (exposed):** 2010–2021, for designing and debugging rules. No result from it counts as evidence.
2. **Confirmatory validation (pre-registered, run once per hypothesis):** 1999–2009, the first window on which no strategy returns have been computed.
   - Gates follow the D226 standard: terminal wealth vs SPY after costs, up / down capture, rolling multi-year windows, regime concentration, cost robustness.
   - Thresholds are fixed before any run.
3. **Full-span check:** the same frozen rule over 1999–2021. Reported together with the per-window results; it never rescues a failed window.
4. **Holdout (unchanged, sealed):** 2022-01-01 → 2026-08-31.
   - Used once, for at most one programme candidate, after written owner approval in `HOLDOUT_UNLOCK.md`.
   - At about 4.7 years it is a falsification check, not proof of an edge.
5. **Forward:** paper / forward period only after a full freeze (D094 category F).

**Multiple testing:**
- A fixed hypothesis budget per programme (proposal: at most 3).
- The confirmatory gate is adjusted across that budget (Holm–Bonferroni on the pre-registered primary statistic).
- The cumulative trial count is carried forward as a reported diagnostic (deflated Sharpe), as in D069 / D082.
- A hypothesis that fails confirmation is closed. It is never re-tuned and re-confirmed on the same window.

**Unchanged:**
- **Costs:** $7 per order (D039), 10 bps slippage per side (D024), forced-liquidation fee (D049), D044 sizing. Changes only with separate approval.
- No change to the Holdout or to any frozen experiment.

**Without Option 3:** a credible separation exists only as "2010–2021 development → Holdout". That puts the entire confirmatory burden on 4.7 years. It is honest, but statistically weak.

## 6. Infrastructure simplification recommendations

1. **No data in source code.** Plain-text code only; no packed tables or encoded output blocks (this is now a platform rule anyway, O5).
2. **Never build identifiers from platform exports.** External data stays keyed by its own identifiers (e.g. CIK). Any mapping is computed inside the environment that holds the prices.
3. **One small standing engine per programme.** One host or engine with a fixed universe, account and cost model; each hypothesis is a short plug-in. This replaces a new host plus a new data layer per phase (S016 … S032).
4. **One platform baseline canary per engine or dataset change**, not one per hypothesis. It checks fixed digests (universe counts, SPY, a control book). Per-hypothesis correctness moves to offline synthetic tests.
5. **A run budget per hypothesis:** at most 3 cloud runs or local equivalents (real run, determinism rerun, one documented retry).
6. **Simpler inference by default.** Benchmark-relative tests on the strategy's own monthly excess returns (pre-registered block bootstrap, as in Amendment 3 W2) instead of 5,000-world in-cloud permutation nulls.
   - Two of the last four phases ran into null-construction problems: H029 / H030 blocked (D234), and the H028 null structurally suspect (D238).
   - Custom nulls only when validated offline first.
7. **Outputs:** own-strategy summary results only. No benchmark daily paths or per-stock tables; benchmark comparisons computed inside the engine (relevant on QC, Q13(e)).
8. **Fewer interruptions.**
   - The owner approves a programme protocol once: hypothesis budget, gates, stop rules and run budget.
   - STOPs only at programme gates: design freeze, each confirmatory result, a Holdout request, or a platform / compliance incident.
   - Minor engineering decisions are recorded, not escalated.
9. **Under Option 3:**
   - one frozen local data snapshot (hash manifest, stored outside git, re-acquisition documented);
   - the existing pure modules (`metrics`, `qr_h026.simulate`-style account engine, `qr_sys1`) reused;
   - deterministic, reproducible runs, with no remote compliance review or engine drift.

## 7. Roadmap options with effort and cost

A **session** here means one working session of this agent. Costs are monthly and exclude nothing already paid. No option claims any strategy will beat SPY.

| | **Option 1: QC-only, price-first** (approach A) | **Option 2: QC hybrid** (approach C, "Data v4 — cloud-generated identity") | **Option 3: licensed PIT data + local engine** (approach D, A–C possible) |
|---|---|---|---|
| Historical depth | 2010–2021 (12 years) + Holdout | 2011–2021 (11 years) + Holdout | about 1999–2021 (23 years) + Holdout, if verified |
| Data quality | prices good (documented); cap gap disclosed or repaired | best achievable on QC; residual identity gap | unknown until audited; vendor claims fit the approved universe |
| Statistical credibility | low: exposed window, Holdout-only confirmation | low–moderate: same window, better universe | **highest available**: an unexamined confirmatory window plus the Holdout |
| Effort before the first test | 2–4 sessions (minimal compliant host, baseline canary) | 6–10 sessions (SEC JSON rebuild, in-cloud identity, audits, freeze) | 1 desk session (licence, price, coverage, no purchase) → owner decision → 4–6 sessions (ingest to 2021-12-31 only, audit, freeze, local engine) |
| Effort per test | 1–2 sessions | 2–3 sessions | about 1 session |
| Infrastructure stability | moderate–low: five blocking events in 13 days; default engine changing weekly | low–moderate: also exposed to Object Store and compliance-review rules | **high**: a frozen local snapshot; risk moves to the vendor licence |
| Budget | $24 / month (unchanged) | $24 / month (Object Store free tier) | about $69 / month or $499 / year (P2-CP12 figure, **to re-verify**), plus $24 if QC is kept: about $93 / month, within the $100 target |
| Testing efficiency | good, but little left to test credibly in the window | poor (heavy fixed cost) | good once built |
| Owner decisions needed | approve programme protocol (§5 reduced) | approve Data v4 build | revisit D123 (purchase) and D001 (engine); approve §5; authorise a purchase only after the desk check |

**Recommendation: Option 3, gated.**
1. **Step 1:** a desk-only verification (no purchase, no data download), returned as a short checkpoint. It covers:
   - the vendor licence (personal research use, local storage, no redistribution);
   - current price;
   - documented coverage of delisted companies, point-in-time shares / market cap, as-reported timing, price-adjustment and delisting-return conventions, and history start;
   - the ingestion cut-off at 2021-12-31 to keep the Holdout sealed.
2. **Step 2:** the owner decides on a purchase. If declined, **Option 1** remains the realistic fallback, with modest expectations, or stopping.
3. **Option 2 is not recommended.** Its large fixed cost buys no new history and no unexamined data.

## 8. Remaining unknowns and the minimum future tests

None of these tests is authorised by this checkpoint.

| # | Unknown | Why it matters | Minimum test | Needs |
|---|---|---|---|---|
| U1 | Migration Atlas statistics by year, property and reason | size of fundamental changes per field and year | owner views the Atlas; or allowlist `cdn.quantconnect.com` for a later session's read | network setting |
| U2 | Market-cap coverage before October 2009 on the **current** dataset | decides whether approach A could start before 2010 on QC | one aggregate-only count of names with cap ≥ $2B per year, 1998–2009 (counts only) | owner approval + a QC run; compliance acceptance not guaranteed (O2) |
| U3 | Whether QC price data changed between 18131 and today | R7: never measured; it affects any comparison with old results | not testable compliantly by value export. Only indirectly: a frozen price-only control book rerun vs its committed summary results | owner approval + QC run |
| U4 | Stability of the current dataset and engine after 2026-10-13 (last exact reproduction) and after the 10-31 retirement | reproducibility of any new QC work | the standing baseline canary (§6.4) once after 10-31 | as U3 |
| U5 | Whether in-cloud aggregate audits remain accepted | all of approaches B / C rely on them | none possible without a run; ask Support in writing | owner contact |
| U6 | Whether yearly / monthly benchmark-relative results and our committed benchmark paths count as summary results | output design and the status of local files | written question to Support (SYS1-CP1 §7 list) | owner contact |
| U7 | Whether the engine change in 18184 (delisted securities held until settlement) is also in `master` and alters the harness's delisting handling (D054 / D062) | trade accounting on delistings | read LEAN release notes / source (public) | desk only |
| U8 | Licensed dataset: licence terms, price, delisted coverage, PIT market cap, as-reported timing, adjustments, delisting returns | gates Option 3 | the desk verification in §7, then (after purchase approval) an audit protocol frozen before any return is computed | owner approvals |
| U9 | Whether a vendor-sourced universe reproduces the QC-era universe closely enough to compare to past results | interpretation only; the conclusions of past phases do not depend on it | aggregate overlap of 2011–2021 eligibility counts (no returns) | Option 3 only |

## 9. Owner decisions requested

1. Accept this reset assessment (inventory, matrix, impact classification).
2. Choose a programme option: **3 (recommended; starts with the desk-only verification)**, 1, 2, or stop.
3. If Option 3: confirm that D123 (no subscription until a promising result) and D001 (QuantConnect as the single engine) may be revisited. **No purchase follows without a further explicit approval.**
4. Approve in principle the validation architecture (§5) and simplifications (§6), or ask for changes. The Holdout stays sealed either way.
5. SYS-1: decide the pending SYS1-CP2 option. Recommended: A, close as NOT RUN — PLATFORM BLOCKED.
6. Optional: written questions to QuantConnect Support (U5, U6).
