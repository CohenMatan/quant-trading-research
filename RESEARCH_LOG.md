# RESEARCH_LOG.md

Append-only chronological diary. The newest entry is at the bottom. Never delete entries.

Totals so far: hypotheses **0** · research strategies **0** · research experiments **0** (plus 14 registered infrastructure, benchmark and demo runs)

---

## 2026-09-27 — Session 1: Checkpoint 1 (Architecture & Data Plan)

**Done:**

- Reviewed the project brief.
- Researched data and engine options: QuantConnect Cloud/LEAN, Sharadar, Norgate, EODHD and free sources.
- Wrote the CP1 report (`docs/checkpoints/CP1_architecture_and_data_plan.md`).
- Created the project memory files: CLAUDE.md, README.md, RESEARCH_PLAN.md (draft), DECISIONS.md and this log.

**Findings:**

- QuantConnect provides survivorship-free daily prices, corporate actions and Morningstar point-in-time `MarketCap` from January 1998. That gives about 27.7 usable years.
- Morningstar replaced QC's entire fundamentals history with a new feed on 2026-09-23. Market-cap data must be audited at CP2.
- QC's licence prohibits exporting raw data, so everything runs inside QC Cloud and only derived results are stored.
- `www.quantconnect.com` and most vendor sites are **blocked by this environment's network egress policy**. The owner must allowlist the host before CP2.
- QC API access requires a paid tier. Public sources give conflicting prices ($8–$60/month), so the owner must confirm the price at signup.

**No experiments run. No money spent.**

**Next:** wait for owner approval of CP1 and the decisions in its §8.

---

## 2026-09-27 — CP1 approved; CP2 blocked on environment access

**Owner approvals:**

- CP1 approved.
- QuantConnect Cloud approved as the data source and engine.
- Split approved: IS 1999-01-04 → 2014-12-31; VAL 2015-01-01 → 2021-12-31; HOLDOUT 2022-01-01 → 2026-08-31.
- Market-cap threshold approved: $2B nominal.
- Simulated account size approved: $100,000.
- Checkpoints are approved by PR merge into `main`.

**Subscription:** QuantConnect Researcher seat ($10/month) plus B2-8 backtest node ($14/month), $24/month total.

**Owner's precondition for CP2:** verify QC API authentication and dataset access before implementing anything.

**Check result in the current session (the session that wrote CP1):**

- `QC_USER_ID` and `QC_API_TOKEN` are **not present** in this session's environment.
- `www.quantconnect.com` is **still denied** by the egress proxy (403 on CONNECT).
- Likely cause: environment settings only apply to newly started sessions.

**Consequence:** CP2 implementation has **not** started, per the owner's precondition.

**Next:** in a new session, run the session-start checklist in CLAUDE.md, then verify authentication and data access, then build CP2.

---

## 2026-09-27 — Session 2: CP2 precondition verified (QC API + dataset access)

**Session-start checklist:** `QC_USER_ID` and `QC_API_TOKEN` are present (values not displayed). `www.quantconnect.com` is reachable (HTTP 200).

**Authentication:** QuantConnect REST API v2 with hashed-timestamp auth → `authenticate` returned success. The organization reads back as tier `researcher`, billing `paid`, with a Researcher Seat ($10) and one B2-8 backtest node ($14) as the only paid subscriptions.

**Dataset access, via five tiny throwaway cloud backtests (scratch code, not part of the repo):**

| Dataset | Check | Result |
|---|---|---|
| US Equities daily, incl. delisted | Enron (ENE) daily closes 2001-11-20 → 12-10 ($6.90 → $0.26 → $0.81) | ✅ |
| Morningstar fundamentals / MarketCap | 2001-11-20: 7,017 securities, 408 with MarketCap ≥ $2B; top 3 = GE $361B, MSFT $313B, XOM $270B | ✅ (see finding 1) |
| US Equity Security Master | AAPL 2:1 split on 2005-02-28 (warning the day before, then "split occurred"); SPY dividend $0.47 on 2005-03-18 | ✅ |
| SPY | Daily bars 1999-01-04 → 2021-12-31 (5,788 trading days) | ✅ |
| Execution | Market-on-open order placed at the T close filled on T+1 at a price different from the T close; IB fees applied | ✅ (full canary to follow) |

**Findings that affect the design:**

1. **Enron's MarketCap reads $0** in Nov 2001 while the stock still traded, so MarketCap has gaps. The data audit must measure how often this happens.
2. **ObjectStore export is blocked** for non-Institutional accounts (data licensing), so it cannot carry results out of QC.
3. **Logs are capped** at 100 KB per backtest and about 3 MB/day, so they are only suitable for small summaries.
4. **The orders API** returns every order with fill events, fees and times. **Custom chart series** return full daily resolution (5,788 points, no downsampling). These become the result channels.
5. The B2-8 node reports an "assets: 500" figure, but a 900-security universe ran without error. Full-scale memory and runtime will be measured.
6. The LEAN version is available per backtest in `serverStatistics` (currently v2.5.0.0.18130).
7. The product list shows a "Tradier" module line at $1 that does not appear among the active subscriptions. Flagged for the owner to check.

**Conclusion:** the owner's precondition is **met**, and CP2 implementation starts now.

---

## 2026-09-27 — Session 2 (continued): CP2 built. STOP for owner approval.

**Built:**

- QuantConnect API client.
- Shared LEAN harness: universe, market-on-open execution, cash planning, fill self-check, holdout lock, equity export.
- Experiment runner: clean-tree check, holdout lock, LEAN build pinning, provenance, reproduce mode.
- Append-only registry.
- Metrics module; PSR/DSR/PBO statistics; split-aware trade builder; integrity checks; truncation look-ahead checker.
- Data-audit algorithm and renderer; execution-timing canary; corporate-action and delisting check.
- SPY and equal-weight ≥ $2B benchmarks; the S000 pipeline demo.
- 81 tests, all passing.

**Runs (registered):**

| Experiments | Result |
|---|---|
| E951-01/02/03 | Audit |
| E950-01 | Canary: integrity-failed, chart read race |
| E950-02 | Canary: ✅ 4,628 fills, 0 timing violations |
| E952-01 | Corporate actions: check bug |
| E952-02 | Corporate actions: ✅ |
| E900-01 | SPY: integrity-failed, chart read race |
| E900-02 | SPY: ✅ |
| E901-01 | Equal-weight benchmark, 2010–2021 |
| E000-01 | Demo, 2010–2014 |
| Reproductions | E950-02 identical; E000-01 one failed read race, then identical |

In addition, 14 unregistered infrastructure development runs: 11 API/data probes and 3 harness scratch runs. None were research.

**Key finding: universe data blocker.**

- Old Morningstar dataset: MarketCap from 1999, but never for companies that later failed or were acquired (Enron, WorldCom, Lehman, Bear, Merrill, Countrywide, Lucent, …). That is survivorship bias.
- New dataset (the only one after 2026-10-31): almost no MarketCap before 2009 (4–27 names ≥ $2B per year); good from 2010; 9 of 12 companies that disappeared later in 2013–2020 are present.
- Options and recommendation are in CP2 §7.

**Throughput:** about 20 s for small backtests; 3–7 min for full-universe backtests; one at a time. That is about 150–300 universe backtests per day.

**Cost:** $24/month, unchanged.

**Proposed for approval:** tradability filters, base slippage, portfolio constraints and gates (D023–D026); data remedy (D027).

**Status:** STOPPED at CP2. No research campaign started. Waiting for the owner.

---

## 2026-09-27 — Session 3: CP2 approved; size-proxy addendum started

**Owner decisions:**

- CP2 infrastructure is approved.
- Do not contact QuantConnect support.
- Build and evaluate a survivorship-free size proxy from price and volume only, compared against MarketCap ≥ $2B in at least 2010–2014.
- Compare several variants; do not over-optimise.
- Stop after the evaluation.

**Checklist:** credentials present (values not displayed); QuantConnect reachable.

**Done before any result:** evaluation plan, variants and decision thresholds pre-registered in `docs/data/size_proxy_plan.md`.

---

## 2026-09-28 — Size proxy: provisional report written

**Runs:**

- E953-01 (2010–14) and E953-02 (2015–21) completed, X953 v1.0.
- E953-03 (1999–2009, old dataset) **failed**: QuantConnect's daily log allowance of about 3 MB ran out.

**Findings:**

- **The reference is survivorship-biased even in 2010–14.** Later-ended companies (Alcoa, Time Warner, DuPont, SanDisk, …) have no fundamentals in either dataset.
- **Wrong primary-share flags.** The new dataset flags many US companies (GE, BAC, V, …) as non-primary. Fixed in D030; the fix requires v1.1 re-runs E953-04..07.
- **Provisional result, C20 + E5 proxy:** F1 0.75 measured; about 0.80 estimated against a complete reference; 0.85 on known-type names; 2015–21 F1 0.80. The universe return gap is −0.2%/year, not significant.
- **Provisional verdict:** APPROVE WITH LIMITATIONS.

**Operational issue:** the log allowance did not reset at 00:00 UTC (still 0 at 05:00 UTC). The v1.1 runs start automatically when it returns.

Report: `docs/data/size_proxy_evaluation.md`, marked PROVISIONAL.

---

## 2026-09-28 — CP2 amendment: 2010 scheme and $7/order commissions

**Owner decisions:**

- D033: research from 2010 only, MarketCap ≥ $2B; size proxy rejected.
- D035: 1999–2009 is an optional finalist stress test only.
- D039: commission of $7 per executed order.

**Implemented:**

- Split scheme `2010`: IS 2010–17, VAL 2018–21, WF 2014–21 folds; holdout unchanged. Date rules for research, benchmark and stress runs.
- Fixed per-order fee model and its integrity check.
- Runner log-allowance pre-flight (D040).
- New benchmark configs E900-03 and E901-02, and canary config E950-03.
- Tests: 102 of 102 pass.

**Proposed:** the split (D034), adjusted gates (D036), and a minimum position of $5,000 with ≤ 15 positions (D041).

**Queued:** QuantConnect verification runs E950-03, E900-03 and E901-02. They wait for the daily log allowance, which was still exhausted at 05:23 UTC.

**No strategy research started.** Report: `docs/checkpoints/CP2_amendment_2010_split.md`.

---

## 2026-09-28 — D039 commission verification: first attempt FAILED; fixed; re-verifying

**Owner instructions applied:**

- D046: no dependency on QuantConnect logs. Results travel as summary statistics, plus the Orders API and charts.
- D048: Claude merges its own work into `main` (PR #6 merged).

**Container restart.** It interrupted the queue during E901-02. That QuantConnect backtest (created 2026-09-28 10:38:49) finished but was never downloaded or registered. It was replaced by a fresh E901-02 run.

**Verification results:**

- E950-03 (canary): ✅ 2,412 executed orders, all $7.
- E900-03 (SPY): ✅ 100 orders, all $7.
- **E901-02 (equal-weight benchmark): ✗ FAIL.**
  - Diagnosis (read-only re-download of the same backtest):
    - The runner's first orders read returned **0 orders** (a timing race), so the commission check was silently skipped.
    - The re-download showed 21,572 harness orders at exactly $7, but **465 LEAN delisting liquidations at $0**.
    - 15 orders never executed ($0, correct).
  - Fixes:
    - D049: $7 is debited on forced liquidations.
    - D050: downloads must match QuantConnect's order count; two new integrity checks; the commission check can no longer be skipped.
  - Proven on QuantConnect by a scratch X952 run (Enron, WorldCom, Bear Stearns, Lehman: 4 of 4 debited; 11 of 11 orders at $7).

**Research Cycle 1 NOT started.** All three verification runs are repeated on the final harness (E950-04, E900-04, E901-03). C01 starts only if all pass.

---

## 2026-09-28 — C01 first pass: incidents diagnosed; corrected re-runs prepared

**First pass (19 IS runs, E001-01 … E005-03):**

- 13 completed, one of them bugged (E004-04: zero trades).
- 2 failed on the QuantConnect side (E002-03, E003-03).
- 3 failed the no-leverage check (E004-01, E004-02, E005-02).

**Diagnosis** (confirmed from order records; `research/cycles/C01_incidents.md`):

- **Leverage cause A:** LEAN cancelled sells on ticker changes (MATX, MDLZ) while the buys they funded executed.
- **Leverage cause B:** opening gaps of +5.5% to +12.9% on OPEC day (2016-11-30).
- **E002-03:** a QuantConnect event-publication delay; the events later arrived complete.
- **E003-03:** QuantConnect transient "Compile id not found".
- **E004-04:** S004 kept too little history for the 200-day filter.

**Fixes:**

- D051: no-borrowing execution model (global).
- D052: runner resilience; S004 window fix.
- Tests: 173 pass.

**Registry:** annotation rows mark each original as superseded, invalid, bugged or failed. No original row is changed.

**Re-runs:**

- Verification under D051: E950-05, E900-05, E901-04, fail-fast per run.
- 19 corrected C01 variations (map in `research/cycles/C01_rerun_map.json`).

**X954 (survivorship gap) analysis completed** (`docs/data/survivorship_gap_2010.md`):

- Missing share 14% (2010) → 5% (2017) → 1% (2021).
- Bias optimistic: about +1.4 points per year on the IS universe; dip-buyers most exposed.

**Not started:** gates and robustness (they wait for the corrected runs), Checkpoint 3, and any VAL, WF or HOLDOUT run.

## 2026-09-29: C01 completed in-sample; Checkpoint 3 STOP

**Operational failures (2026-09-28, 16:01–17:12 UTC).** E003-04 and E003-05 were hit by QuantConnect orders-API errors. E003-06 stalled at 97% for 6 hours, which blocked 7 runs from starting.

- The owner approved deleting E003-06; its metadata was preserved first.
- Diagnosis: a platform outage plus a runner that did not retry. It was not S003-specific.
- Fixed by D053 (retries, stall detection, node pre-flight, failure metadata). `not_started` runs are excluded from the trial count (owner).

**Retries** E003-07..09, E004-09..12 and E005-07..09 were all integrity-clean.

**D054.** The order audit showed the D051 sell re-issue never fired: LEAN rewrites the order tag and leaves the message empty. E004-09 and E005-08 are bugged.

- Fixed.
- Verification re-run as E950-06, E900-06 and E901-05, all passing.
- All 19 variations re-run as E001-11..E005-12. 16 reproduced the previous runs exactly; the differences are explained (fixed exits; QuantConnect dividend revisions).

**IS screen (final, comparable):**

- H005 v1.0, v1.1 and v1.2 PASS, including 2× slippage.
- All 16 H001–H004 variations fail.

**Robustness of E005-12, pre-declared as E005-13..27:**

- Sharpe 1.12 at 4× slippage;
- plateau 10 of 10;
- all IS thirds positive.

**Multiple testing:**

- PBO for H005 is 0.71, which fails the ≤ 0.30 Validation-gate item as defined.
- DSR on IS alone is 0.80, with 76 trials.

**Other findings:**

- The no-borrowing rule leaves the monthly strategies about 30–50% in cash.
- A spin-off distorts trade-level statistics (convention D018).

**Checkpoint 3 written.** It recommends freezing S005 v1.2 as the only candidate, with owner decisions on PBO and cash drag.

**STOP.** No VAL, WF or HOLDOUT run.

## 2026-09-29: Validation of S005 v1.2 (H005); Checkpoint 4 part 1 STOP

**Setup.**

- The owner approved S005 v1.2 for Validation only.
- It was frozen by `research/promotions/S005_v1.2.json`.
- The gate and the exposure-aware evaluation were committed before the run (D056).

**E005-28** (2018–2021, one run) passed all integrity checks.

- Results: CAGR 4.4%, Sharpe 0.89, max drawdown −6.5%, 174 trades.
- Benchmarks: equal-weight 12.3% / 0.65 / −37.8%; SPY 17.0% / 0.87 / −33.1%.

**Validation gate:**

- The 6 performance checks pass.
- **Deflated Sharpe 0.68 (< 0.90) fails.**
- The known PBO 0.71 fails.
- **Formal FAIL.**

**Exposure-aware comparison.**

- The low drawdown survives exposure matching (−6.5% vs −20.8% for EW and −18.1% for SPY at the same cash).
- The Sharpe edge does not hold against SPY (1.02 exposure-matched).
- Alpha vs EW: +2.4% a year, t = 1.2 (IS: +4.4%, t = 3.2).

**Where the return came from.** The trades lost money on price. Distributions made about 4.7% of equity a year.

**New finding D057.** Closed-end funds and partnership units pass the common-stock filter: 23% of S005's VAL capital (6% in IS). All affected runs are flagged; nothing is fixed yet.

**Recommendation.** "No Production Candidate Found" for C01. Fix the universe before any new research.

**STOP.** No Walk-Forward or Holdout.

## 2026-09-29: E005-28 accounting reconciliation (owner request); CP4 report finalised

**Gate statement corrected.** All 8 Validation checks are now shown individually: 6 PASS, 2 FAIL (Deflated Sharpe 0.68, PBO 0.71). Overall FAIL.

**Cash-event audit E955-01** (X955, D058; no orders, not a trial).

- All $20,188.82 of E005-28's non-trade cash was matched to dividend events on held positions. The residual is $0.003; no day is off by more than $0.01.
- Classification:
  - ordinary dividends: $8,410.33 (179 events);
  - special distributions: $6,383.49 (MIC, EQC, NVG);
  - merger cash consideration: $5,395.00 (DPS/KDP);
  - spin-off cash: $0. 21st Century Fox/New Fox: no credit; possible under-count.
- No double counting: raw-price valuation; equity is continuous on each large event.
- Equity reconciles exactly: $100,000 − $297.80 closed price P&L + $1,610.64 open price P&L − $2,618 commissions + $20,188.82 distributions = $118,883.66.
- 58% of the gain came from two one-off payouts (KDP, MIC).
- 47 of 174 trades were takeover cash-outs (+$3,018). Strategy-closed trades lost −$5,836.

**D059 (new).** OAK and BPL were acquired without delisting events. Their sells never filled, and the positions stayed frozen from late 2019 to 2021 (about 11% of equity).

- Economic exposure in March 2020 was about 30%, not 42%.
- Exposure-matched benchmark crash drawdowns at economic exposure: about −16% (EW) and −15% (SPY), against S005's −6.5%.
- No IS run is affected; the EW benchmark is affected negligibly.

**Recommendation unchanged:** "No Production Candidate Found" for C01; fix D057 and D059 first.

**STOP.**

## 2026-09-29: owner closes C01; D057 / D059 fixed; D063 found and fixed; CP4b STOP

**Owner decision (D060).** The CP4 Validation result is final. C01 outcome: No Production Candidate Found. H005 is not promoted further.

**D057 fix (D061).**

- The universe excludes partnership and LLC units, funds and BDCs, royalty trusts and SPACs.
- Morningstar's current-status flags are handled so acquired corporations stay eligible.
- A dated override table corrects known cases.
- The probe E956-02 shows 90 securities removed and none added.

**D059 fix (D062).**

- A holding with no real price bar for more than 10 sessions is closed at its last real close. The run is marked with a warning.
- The run fails on a never-filling order or an unresolvable dead holding.
- The canary E957-01 caught all 9 known dead securities correctly.

**D063 (found in the audit).**

- Price windows were deleted while a buy was pending, so S001's exits never saw those positions. Every H001 run had 7–15 of 15 slots stranded.
- Fixed and unit-tested.
- **H001's C01 verdict changes to INCONCLUSIVE.**

**Regression.** E950-07 passes. E900-07 is unchanged. E901-06 passes, with 4 fallback exits as warnings. The EW IS Sharpe moves 0.915 → 0.921.

**C01 audit** (`research/audits/C01_D057_D059_D063_audit.csv`):

- Every run held some D057-excluded securities (1–20% of capital). Conclusions are unchanged for H002–H005.
- D059 affected no in-sample run.
- 62 annotations were appended; nothing was deleted.

**D064.** The D063 code was committed under an E956-02 run label (queue auto-commit); this is documented.

**STOP.** Waiting for the owner before any C02 design. No new hypotheses and no strategy backtests.

## 2026-09-29: D057 finalised; D063 verified end to end; H001 remedial re-test; CP4c STOP

**D057 finalised (D065).** Dated overrides, each verified from filings:

- KKR partnership units until 2018-07-01; Apollo LLC shares until 2019-09-05; Ares partnership units until 2018-11-26.
- MIC was a corporation from 2015-05-21 (this corrects CP4).
- KFN excluded; Texas Pacific Land a trust until 2021-01-11.
- Probe E956-03 confirms each switches on its date.

**D063 canary E958-01.** 23 of 23 cycles passed: removed while the buy was pending, history kept, buy filled, history-based exit after 3 closes. 4 of 4 safety-net restores. Nothing stuck.

**H001 remedial re-test (E001-16..20).**

- All integrity checks pass; no stuck positions.
- All five fail the original screen at 4/12 gates each:
  - Sharpe −0.82 to 0.20;
  - profit factor 0.69–0.99;
  - costs 7–14% a year.
- **H001 is rejected on a valid test.**
- No robustness runs, because none passed.

**Trial accounting.** 35 genuine trials; 46 technical repeats; 7 not started; 37 verification or benchmark runs.

**STOP.** Waiting for the owner. C02 is not designed.

## 2026-09-29: owner approves CP4c; C02 plan proposed; STOP

**Owner decision.** CP4c is approved. C01 is closed: No Production Candidate Found.

**C02 plan written** (`research/cycles/C02_plan.md`):

- Six hypotheses in six distinct families:
  - H006 breakout with volume;
  - H007 volatility squeeze;
  - H008 residual relative strength;
  - H009 high-volume return premium;
  - H010 gap-and-hold;
  - H011 calendar-month seasonality.
- 3 pre-declared variations each: 18 selection trials, with a cap of 56 strategy backtests.
- Unchanged gates, with new diagnostics. The trial-count definition is fixed before any result.

**No C02 strategy backtest has been run.** Waiting for the owner's approval.


## 2026-09-29: C02 approved in principle; prerequisites complete; CP5pre STOP

**Owner decision.** The C02 plan is approved in principle (D070): H006–H011, 18 variations, 10 slots, daily refill, the 56-backtest cap. H011's pre-2010 look-back is allowed as warm-up only. Three clarifications were required before any strategy backtest.

**Done** (report: `docs/checkpoints/CP5pre_C02_prerequisites.md`):

- **Trial accounting frozen (D069).**
  - Official DSR N = cumulative distinct IS selection candidates: 19 now, 37 after C02.
  - Conservative S + R + V = 35, reported separately and never mixed into the official figure.
- **Takeovers.** The H006 jump exclusion and the H010 15% gap cap were removed; only the general data-integrity rules apply.
- **H010 timing.** Stated in the spec and verified by tests and on QuantConnect.
- **Infrastructure built; 305 tests pass.** S008 v1.1 scoring bug fixed before any run (D071).
- **Canaries** (infrastructure, not trials):
  - E960-01 (month-end store) passes.
  - E959-01/02 found a volume-scaling inconsistency after dividends and spin-offs (D072). It is fixed, and E959-03 passes (all OHLCV within 0.013% of fresh history; 0 timing violations).
- **The 18 C02 configs** (E006-01 … E011-03) validate and dry-run. **None has been run.**

**STOP.** Waiting for owner approval to run the 18 selection trials.

## 2026-09-29: owner's two final checks; H008 defect found; CP5pre addendum STOP

The owner approved the prerequisite checkpoint except for two checks. Report: `docs/checkpoints/CP5pre_addendum_signal_equivalence_PBO.md`.

**1. Signal equivalence (E961-01, verification canary, no orders).** The harness's dividend factor differs from QuantConnect's by ≤ 0.1% per event.

- For H006, H007, H009, H010 and H011 this changes nothing material: 21 borderline flips in about 2.9 million decisions (11 one way, 10 the other) and no change to any top-10 selection.
- **It exposed a real H008 defect** (D074): the score sums least-squares residuals over the regression's own window, which is always zero, so the ranking is random. Options A/B/C are proposed; A is recommended.

**2. PBO** (D073, proposed). With 3 variations, PBO measures sibling dominance, not overfitting (null 2/3, very noisy). Proposed: a cycle-level PBO ≤ 0.30 gate over the 18 candidates, with the threshold unchanged.

**STOP.** Owner decisions needed on D073 and D074. The 18 C02 runs have not been started.

## 2026-09-30: C02 in-sample results; CP3b STOP

**What ran.** All 18 C02 selection trials, once each, plus the pre-declared robustness procedure for the one screen pass. Report: `docs/checkpoints/CP3b_C02_IS_results.md`.

- **17 of 18 fail the IS screen**, every one on Sharpe ≥ EW + 0.10. The equal-weight benchmark's IS Sharpe is 0.92.
- **E007-02 (H007 v1.1)** passes the screen and 2× slippage, then **fails robustness**: 3 of 8 plateau perturbations fall below 70% of its base Sharpe. It is also only 21% invested on average.
- Cycle-level PBO is 0.268 (the gate passes); the best IS DSR is 0.54 (N = 37).
- **Proposed C02 outcome: No Production Candidate Found** (D076).

**Operational.**

- Three container restarts lost the runner mid-backtest. The affected runs are recorded as failed, with identical technical repeats.
- E007-16 is stuck on QuantConnect; deleting it awaits owner approval. E007-13 and E007-14 have not run; they cannot change the verdict.

**STOP.** No Validation run.

## 2026-09-30: C02 completed; C01–C02 review; C03 proposed; STOP

**C02 completion (owner-approved steps).**

- **E007-16:** stuck "In Queue" on QuantConnect and never ran. Its metadata and runner output were preserved, then it was deleted with owner approval.
- **E007-12** (time stop 32): its completed QuantConnect backtest was **recovered and verified** with the new `--recover` mode (D077). Sharpe 1.17, all integrity checks pass.
- **E007-13 and E007-14** (time stops 48 and 60) ran: Sharpe 1.12 and 1.13.
- **Final robustness for H007 v1.1:** plateau 5 of 8 (at least 7 required), so it **fails**.
- **C02 closed: No Production Candidate Found** (D078). Final report: `docs/checkpoints/CP3c_C02_final_report.md`.

**C01–C02 review** (IS evidence only; no Validation result used for design):

- Median net IR −0.14 (gross +0.12); the screen needs about 0.5.
- Costs cost about 0.25 of IR.
- One common factor explains 61% of all 37 variations' returns.
- The only high-IR profiles were defensive and low-exposure, and both later failed.
- Method limitations to measure (not relax): 10–15-stock concentration, and the $5K minimum position at $100K.

**C03 proposal** (`research/cycles/C03_review_and_plan.md`): matched-null and breadth measurements first; then 3 new-family hypotheses; a stopping rule.

**STOP.** Awaiting owner review.

## 2026-09-30: C02 closed by owner; structural review; portfolio diagnostics; revised C03 proposal; CP3d STOP

**Owner decision.** C02 is closed (No Production Candidate Found). C03 preparation is authorised, starting with a structural review and portfolio diagnostics.

**Diagnostics.** 24 pre-registered no-skill random-pick runs (X962, E962-01..24; D079). All completed; they are not trials. Key readings:

- The C02-structure no-skill Sharpe is 0.75, against EW's 0.92.
- Holding period dominates: at hold 5 costs are 8% a year and Sharpe is −0.13; at hold 60 costs are 1.2% a year and Sharpe is 0.81.
- A $1M account adds +0.11 Sharpe through lower commissions.
- 19 slots is infeasible at $100K.
- The seed alone moves Sharpe by up to ±0.2.

**Conclusion.** C01/C02 failed mainly for lack of edge. The structure imposes a known handicap. Gates are kept unchanged.

**Revised C03 proposal** (report: `docs/checkpoints/CP3d_structural_review_and_C03_proposal.md`):

- H012, volatility-managed exposure;
- H013, lottery-stock avoidance;
- the turn-of-month family is not recommended.

**STOP.** Awaiting owner decisions.

## 2026-09-30: C03 final plan (CP3e) proposed; STOP

**Owner clarifications incorporated** into `docs/checkpoints/CP3e_C03_final_plan.md`:

- **Capital:** $100K is primary; $200K is a pre-declared S1/S2 sensitivity check.
- **H012:** two controls (fully invested, and a causal exposure-matched control).
- **H013:** paired random selection, per-seed reporting.
- **SPY:** used as an indicator only.
- **H014:** deferred.

**PBO analysis (synthetic and semi-real, no C03 data).** The 6-candidate cycle PBO is weak:

- 27–29% false pass under the null;
- it fails two genuinely good hypotheses about 80% of the time;
- pooling with C02 is too lenient (79% false pass).

Proposed P1: keep D073 and add a stricter dual-count DSR requirement.

**DSR and budget.** N goes from 37 to 43. Budget: 34 committed runs, cap 82 (owner approval needed).

**STOP.** No C03 strategy backtest has run.

## 2026-09-30: C03 statistical methodology (CP3f) proposed; STOP

**Owner decisions.** The owner approved H012, H013, the $100K/$200K capital design and the budget of 82 (34 committed + ≤ 48 conditional). They rejected PBO options P1 and P2 and asked for a statistically justified framework.

**Evidence.** A synthetic simulation of the full C03 pipeline (9 scenarios × 1,000 repetitions, IS-calibrated only) found:

- PBO as a gate gives no protection against a spurious edge in one hypothesis: 7.5% false acceptance, the same as without PBO.
- Its apparent protection elsewhere comes from the two-similar-hypotheses artefact.
- It strongly cuts power when both ideas are good.
- A DSR required at both the official and the conservative count lowers false acceptance in those cases (to 3.5%); the worst case is 4.9%.

**Proposed (D082):** PBO diagnostic only; dual-count DSR on each deployable book (H013 per seed); all three seeds must pass every stage; no exceptions; other gates unchanged.

**STOP.** No C03 strategy backtest has run.

## 2026-09-30: C03 methodology frozen (D082 final); H012/H013 infrastructure and canaries; CP3g STOP

**Owner decision.** The owner approved the C03 statistical methodology (D082), with two clarifications: a precise conservative trial count (A), and a frozen DSR calculation and Validation procedure (B).

**Done:**

- **Frozen specification** `research/cycles/C03_statistical_spec.md` (hash pinned by a test).
- **Counts:**
  - official N = selection candidates;
  - conservative N = selection + H013 replicate seeds + robustness + Validation.
  - Now 37/64; 43/76 after the committed runs; at most 43/120. CP3f's "about 104" is corrected to 120.
- **DSR:**
  - daily net returns of the IS run then the VAL run, with no bridging return;
  - DSR ≥ 0.90 at both N, per book (each H013 seed);
  - IS+VAL is the gate; IS-only and VAL-only are diagnostics.
- **Code:** `registry.trial_accounting` (replicate groups) and `qresearch.c03stats`.
- **Strategies:** S012 (H012, with Controls A/B) and S013 (H013, the null's order with excluded names skipped).
- **Committed-run configurations** (32 C03 runs, not run) and the evaluation script `C03_eval.py`.

**Canaries:**

- **E963-01** stopped on a canary-code bug at the 2010-11-26 half-day (annotated bugged).
- **E963-02** passed its checks but revealed an S012 defect: an empty basket during the universe's 20-session warm-up. Fixed (D083a) with a regression test; the run is annotated superseded.
- **E963-03 passed:**
  - RV matches fresh history (103 checks, 0.02% maximum difference);
  - basket 8/8;
  - no orders outside rebalance windows;
  - zero timing violations.
- **E964-01 passed:**
  - S013 with nothing excluded reproduces the null E962-22 exactly (975/975 fills, identical equity);
  - 201 exclusion audits with zero errors.

**Tests:** 371 pass.

**Issues raised:**

1. **H012 and the trade count.** H012 closes only about 4 trades a year, so it will almost certainly fail the unchanged "≥ 100 closed trades" screen item by construction. Options are given; the recommendation is to run it as approved, as a diagnostic of timing value.
2. **$5K minimum under exposure scaling.** It skips entries when exposure is low. This is counted and reported.
3. **Canary re-runs.** There were two more than planned, relevant to the budget cap of 82.

**STOP.** No C03 strategy backtest has run. Report: `docs/checkpoints/CP3g_C03_frozen_methodology_and_infrastructure.md`.

## 2026-09-30: H012 alternative screening proposed (D084); budget accounting (D085); STOP

**Owner decisions.** CP3g approved in principle, with Option 2 for H012: a statistically justified replacement for the trade-level screen items, to be proposed before any C03 run. Canaries and retries are separated from the research budget, with two counts kept.

**Proposal (D084, H012 only, not in force).** The four trade-level IS items are replaced by five timing items, all measured against H012's own controls:

- **T1** at least 8 exposure decisions;
- **T2** bootstrap lower bound of Sharpe(V) − Sharpe(Control B) > 0;
- **T3** Sharpe(V) − Sharpe(Control A) > 0.05;
- **T4** leave-one-year-out;
- **T5** 2 of 3 thirds.

Validation's trade count is replaced by at least 4 decisions and VAL Sharpe(V) > Sharpe(B). Everything else is unchanged.

**Calibration (synthetic plus a semi-real null; no C03 or Validation data).**

- False pass 0.3–0.7%; 0 of 72 on the real-return null.
- Power only 2–4% even with a genuine timing effect. H012's no-leverage rule gains about 0 to +0.04 Sharpe over its control, which is below 8-year noise (0.06–0.11). H012 is expected to be rejected, now for a legitimate statistical reason.

**Budget ledger (D085).** Research budget used 0 of 82 (32 configs written). Operational executions: 4, all canaries.

**STOP.** Awaiting owner approval of D084. No C03 strategy backtest has run.

## 2026-09-30: H012 power reassessment (D086); STOP

**Owner decision.** The owner did not approve D084, because its power was low even for genuine timing value, and asked for a statistical reassessment. There was no H012 run and no change to H012.

**Study.** `research/cycles/C03_h012_power_study.py/.json` (synthetic regime and GARCH markets, plus a semi-real null, all with the unchanged H012 rule and controls).

**Findings.**

- **The effect is small.** H012's capped rule (no leverage, about 92% invested on average) can only produce a small true Sharpe gain over its exposure-matched control: at most about +0.05 in GARCH-type markets. Larger gains need crash-like turbulent regimes.
- **The noise is large.** Over 8 years the standard deviation of the estimated gain is about 0.1.
- **The D084 combination is not the cause.** T3–T5 never reject after T2.
- **Power stays low whatever the test:**
  - D084: 14% (moderate effect) and 36% (strong);
  - T2 at 5%: 25% and 47%;
  - Ledoit–Wolf: 27% and 56%.
- **Data needed.** 80% power needs about 50 years of data for a moderate effect and 14 for a strong one.
- **False acceptance is controlled.** All tests stay near nominal with no edge, with a favourable market, after a lucky crash, and with lower exposure. A drawdown comparison, by contrast, rewards lower exposure 100% of the time.

**Conclusion.** H012 cannot be evaluated with adequate power on our data.

**Recommendation.** Remove H012 from C03 as "not evaluable with available data", and run H013 only. Keep the DSR official N at a floor of 43.

**STOP.** Report: `docs/checkpoints/CP3h_H012_power_reassessment.md`. No C03 strategy backtest has run.

## 2026-09-30: owner decisions after CP3h (D087); prerequisites for the C03 runs

**Owner decisions (D087).**

- **H012 removed from C03.** It is "not evaluable with sufficient statistical power using the currently available data", which is not a failed hypothesis. Its configs are withdrawn, and the runner refuses them.
- **Statistical specification Amendment 1** (the original text is unchanged): official N = 40, with N = 43 reported as a sensitivity only.
- **H013 is the only active hypothesis.**
- **Committed research runs: 21.**

**D088.** H013's exclusion perturbation is fixed as the base ± 5 points.

**Prerequisites.**

- **Evaluation code:** updated to H013 only. It checks robustness for every seed and reports the N = 43 sensitivity.
- **Tests: 381 pass.** They cover:
  - the H013, sizing and null configs against their specification;
  - the all-three-seeds rule, missing seeds, no seed averaging, and ties;
  - robustness for every seed;
  - N = 40/73 after the committed runs;
  - the withdrawn configs;
  - both frozen hashes.
- **Budget ledger:** 0 of 21 committed research runs used; 4 canary executions.
- **Canaries:** no strategy or harness code changed, so they were not re-run.

## 2026-09-30: C03 queue stopped: E013-06 stuck "In Queue" on QuantConnect; STOP

**Progress.** E013-01..05 completed.

**E013-06 (H013 v1.1, seed 3).** Its QuantConnect backtest has sat "In Queue…" at 0% since 16:11 UTC, which blocks the only node. The runner recorded it as failed (server-side read timeouts), and the queue stopped as designed.

**E013-03.** QuantConnect later labelled it "Runtime Error", but the message comes from QuantConnect's own infrastructure (websocat). The run itself is complete and valid.

**Incident file:** `research/cycles/incidents/E013-06_incident.md`.

**STOP.** Owner approval is needed to delete the stuck backtest (CLAUDE.md), then re-run it as a technical repeat and resume.

## 2026-09-30: C03 complete: H013 rejected; no qualifying candidate; STOP

**Runs.**

- E013-06's stuck QuantConnect backtest was deleted with owner approval, after its metadata was committed. The identical configuration ran as E013-16 (technical repeat).
- The queue resumed in the approved order. All 21 committed runs completed: the 9 selection seeds, 6 at $200K, and 6 paired nulls at $200K.
- E013-03's post-completion QuantConnect "Runtime Error" label was checked by a reproduction run, which gave identical equity, fills and trades. E013-03 is retained.

**Results.**

- All 9 H013 seed books fail the IS screen: best Sharpe 0.944 against the 1.02 required.
- No conditional run was triggered.
- Against the paired nulls, the mean Sharpe difference is −0.015 / −0.053 / −0.024, and profit per trade is lower in all 9 books. The pre-declared falsification test refutes the effect.
- $200K S1: the same relative standing. S2: noisy, driven by one weak null.
- PBO 0.93 (diagnostic). IS-only DSR 0.08–0.36 (diagnostic).
- Counts: official 40, conservative 73, sensitivity 43.

**Budget.** Research: 21 of 82. Operational: 27 executions.

**Report:** `docs/checkpoints/CP3i_C03_results.md`.

**Stopping rule.** No further cycle. A programme review is proposed as the next deliverable.

**STOP.**

## 2026-09-30: C03 closed; research-programme review (CP3j); STOP

**Owner decision.** C03 is closed: No Production Candidate Found. The owner approved the programme review.

**Review.** `docs/checkpoints/CP3j_programme_review_C01_C03.md` covers all 40 selection candidates. It uses in-sample data only, with official verdicts unchanged.

**Outcomes.**

- 5 lost money: high-turnover H001/H004, all profitable before costs.
- 29 were profitable but below equal-weight.
- 6 had a Sharpe above equal-weight but failed a requirement: H005 failed Validation or was not chosen, H007 v1.1 failed robustness, and H009 missed the bar by 0.01–0.02.
- H012 was not evaluable.

**Causes.**

- Costs: a $7 fixed commission plus slippage at the swing horizon.
- Portfolio structure: random no-skill portfolios trail equal-weight.
- Short data and a DSR hurdle that grows with every candidate.

**Recommendation.** Close or pause (cancel the QuantConnect node). Continue only with a reconsidered objective: lower turnover or a lower cost basis, as a new pre-registered phase.

**STOP.**

## 2026-09-30: Phase 2 research proposal (P2-CP0); STOP

**Owner request.** A new programme on a low-turnover, technical trend + pullback + recovery strategy, at the design stage only.

**Delivered.**

- Proposal: `docs/checkpoints/P2_CP0_research_proposal.md`.
- Literature review, which keeps evidence, conventions and our own hypotheses apart.
- Feasibility analysis: costs against holding period, DSR hurdles, and statistical power.
- H014 draft.

**H014.** Two candidates, differing only in the exit rule. Three controls isolate whether the entry timing adds value: trend-only, pullback without recovery, and random uptrend stocks (3 seeds).

**Key constraints found before any backtest.**

- **Costs:** the target of 1.0–1.5% a year needs an average hold of at least about 55–60 sessions.
- **Power:** showing that the pullback entry beats the trend-only control has only about 20–60% power over 8 years.
- **Trial count:** the choice largely decides feasibility. The Sharpe needed is about 1.2 with a separate P2 registry and about 1.45 if the 40 earlier trials are inherited.

**STOP.** Nothing implemented or run. No Validation, Walk-Forward or Holdout used.

## 2026-09-30: Phase 2 revised evaluation methodology (P2-CP0b); STOP

**Owner request.**

- DSR becomes a diagnostic rather than a gate.
- 2010–2021 is development data.
- One frozen candidate goes to the untouched 2022–2026 Holdout.
- The criteria are practical and multi-dimensional.

**Delivered.** `docs/checkpoints/P2_CP0b_revised_evaluation_methodology.md` and a pipeline simulation.

**Proposed rules.**

- Gates G1–G4: practical superiority over EW and SPY, beating the controls, consistency, and robustness plus costs. Everything else is a diagnostic.
- Holdout criteria HO1–HO3, including a post-2022 guard.

**Concerns flagged, with numbers.**

- A 4.7-year Holdout lets a no-edge strategy pass about 30% of the time.
- Without DSR as a gate, false acceptance grows with each hypothesis screened: about 27% after 5 hypotheses and 35% after 10.
- Proposed fix: at most 3 hypotheses per Holdout, a development margin rising 0.20 → 0.30 → 0.40, and a 2-year forward test. This gives at most about 12% false acceptance (about 6% with the forward test), while a genuine +0.3 edge is still accepted 53–57% of the time.

**STOP.** H014 not implemented; no backtest run; the Holdout untouched.

## 2026-09-30: Phase 2 methodology amendment (P2-CP0c); STOP

**Owner decision.** The Phase 2 evaluation philosophy is approved in principle, with three items left to amend.

**Proposed amendment.**

1. **Data categories.** Four categories are defined, and the forward-test clock starts at the freeze timestamp. Data from 2026-09-01 up to the freeze is historical unseen data: it is locked, opened together with the Holdout, and reported but not gated.
2. **Hypothesis budget.** At most 3 hypotheses, each with a fixed margin of +0.25 Sharpe over EW. The simulation shows rising margins mainly cut power for later ideas; a fixed margin with the budget treats every idea equally. No-edge acceptance is at most about 15% after 3 hypotheses (an upper bound).
3. **G1.** A combined return-risk rule: Sharpe margin, a CAGR floor, Calmar no worse than EW, and drawdown at most 5 points deeper than EW. It replaces the drawdown veto that rejected genuinely better, slightly riskier strategies.

**STOP.** Nothing implemented or run; the Holdout untouched.

## 2026-09-30: Phase 2 approved; H014 development specification frozen (D094, D095)

**Owner decision.** The Phase 2 methodology is finally approved (with the amendments), and H014 development is authorised.

**Done before any H014 backtest.**

- Froze `research/phase2/P2_spec.md`. The hash is pinned by a test. It includes the exact A/B selection metric, the gates, the conditional robustness trigger and the run IDs.
- Added the `DEV` split (P2 only), which counts as selection in trial accounting.
- Updated CLAUDE.md to the weeks-to-months horizon.
- Built S014, one code path covering H014, C1, C2 and random-uptrend.
- Built the canary X965.
- Wrote the configs for E014-01..14 and E965-01..03.
- Added tests `tests/test_p2_s014.py` and `tests/test_p2_spec.py`. The full suite passes.

**Next:** canaries, `P2_eval.py`, then the committed development runs.

## 2026-09-30: Phase 2 canaries pass; development runs start (D096–D098)

**Canaries (X965, non-candidate settings, 2010–2012).**

- **E965-01** stopped on its first close because of a defect in the canary's own audit (D096). It was fixed in v1.1.
- **E965-04, E965-02 and E965-03** passed every check:
  - look-ahead and indicator history against fresh point-in-time data;
  - ranking;
  - the time stop;
  - MA200 exits;
  - horizon rolls;
  - next-open fills;
  - fees and the $5,000 minimum.
- **E965-03** reproduced byte-identically.

**Dividend-factor difference (D097).**

- The strict 1e-6 feature comparison flagged 24% of samples.
- The diagnostic run X966 (E966-02) traced this to a last-digits difference between the harness's dividend factor and QuantConnect's factor file. It amounts to at most 0.07% on bars older than a dividend.
- There was no bar misalignment and no signal difference.
- Documented, not hidden.

**Operational.** A container restart interrupted E965-04's download, after QuantConnect had delayed publishing its fill events. It was recovered from the same backtest (D077).

**Next.** `P2_eval.py` is committed. The committed development runs E014-01..14 start.

## 2026-10-01: P2-CP1 H014 development checkpoint; STOP (D099, D100)

**Runs.** The committed development runs E014-01..12 and the $200K sensitivity runs are complete. E014-13 and E014-14 never started because QuantConnect's node ran out of disk; they were re-run once as E014-24 and E014-25.

**Selection.** Under the frozen rule, Candidate A (63-session exit) was chosen.

**Outcome.** A is profitable (12.1% a year) but fails:
- G1: Sharpe 0.64 vs EW 0.80;
- G2: below the median random-uptrend seed;
- G3: beats EW in 1 of 6 blocks.

The conditional robustness runs were therefore not made (§9), and G4 fails.

**Diagnostics.**
- DSR is 0.91 at N = 2 and 0.07 at cumulative N = 42.
- Random selection among uptrend stocks beat both momentum-ranked trend-only and H014.

**Conclusion.** H014 is not development-qualified. The Holdout is untouched; the hypothesis budget stands at 1 of 3 used.

**STOP:** awaiting the owner.

## 2026-10-01: H014 closed as Rejected; H015 pre-registration proposed (D101, D102); STOP

**Owner decision.** H014 is closed as Rejected and preserved exactly as tested. Its classification: profitable, not benchmark-beating, not control-beating, not development-qualified. The Holdout was not opened. Budget: 1 of 3 hypotheses used.

**H015 proposal** (`docs/checkpoints/P2_CP2_H015_preregistration_proposal.md`).

- **Design:**
  - 15 equal slots.
  - A monthly check of Close > SMA200.
  - Seeded random selection among qualifying stocks.
  - Exit on trend failure at a monthly review; no time stop.
- **Expected costs:** about 0.4–0.7% a year.
- **New controls:**
  - K1, a random portfolio without the trend filter;
  - K2, the whole trend-filtered population.
- **Supporting work:** a literature review and a feasibility study. The feasibility study used only already-observed outputs and ran no backtest.

**Disclosed.**

- H014's random-uptrend controls had already measured something close to H015 on 2010–2021: median Sharpe about +0.03 above EW, against the +0.25 required.
- So the development test is not independent, and a pass is unlikely.
- The proposal recommends spending slot 2 on H015 only if the trend-filter question itself is the goal.

**STOP.** Nothing implemented or run; the Holdout untouched.

## 2026-10-01: H015 viability review; STOP (D103)

**Owner decision.** The owner did not approve H015 implementation and asked for a viability review.

**Review** (`docs/checkpoints/P2_CP2b_H015_viability_review.md`). It used only committed results and simulations; nothing was run.

- **Independence:** H015 shares its entire development path with H014's random-uptrend books. Its predicted result is about +0.03 ± 0.16 Sharpe vs EW.
- **Chance of reaching +0.25:** about 1–10% under any defensible seed rule; about 4% for the recommended rule.
- **Deterministic selection:** no rule is both trend-relevant and uncontaminated.
- **Controls:** the 6-month K1 is unfair; a fairer K1′ is defined.
- **Population question:** K2 answers it without needing a hypothesis slot.

**Recommendation.** Do not adopt H015; preserve Phase 2 slot 2; propose no replacement now.

**STOP.**

## 2026-10-01: H015 not adopted; Phase 2 opportunity review; STOP (D104, D105)

**Owner decision.** H015 was not adopted before implementation, and no hypothesis slot was used. The averaged-across-seeds result construction is withdrawn. The population diagnostic K2 was not run.

**Phase 2 capacity:** 1 of 3 slots consumed.

**Opportunity review** (`docs/checkpoints/P2_CP3_opportunity_review.md`). It is research only; nothing was defined, implemented or run.

- Technical families are exhausted.
- The only distinct, well-evidenced families are fundamental:
  - profitability/quality;
  - net share issuance;
  - quality + value.
- They need a scope change and a point-in-time fundamentals audit first.
- About +0.35–0.40 true Sharpe edge over EW is needed to pass the +0.25 margin reliably.

**Conclusion.** Either one final, well-founded attempt (profitability/quality), or close Phase 2 with "No Production Candidate Found" and keep the passive alternative.

**STOP:** awaiting the owner.

## 2026-10-01: Fundamental-data scope expansion; integrity audit; STOP (D106, D107)

**Owner decision.** The owner approved point-in-time fundamental data for stock selection, with profitability/quality first, and authorised an audit only.

**Audit** (`docs/checkpoints/P2_CP4_fundamental_data_audit.md`; runs E967-02 and E968-01; nothing strategy-related was computed).

- **Timing is point-in-time.** Over 3.42 million stock-days there were no early file dates and no silent overwrites. New reports are seen within 1 day of filing.
- **Coverage** of the core profitability set is 86–89%.
- **Share counts and per-share values are restated for later splits**, including Holdout-era splits. They are unsafe as levels; market cap is safe.
- **Open risks:**
  - possible later-filing values on 0.28% of report-days;
  - approximated file dates;
  - current-status metadata;
  - the D043 survivorship gap.
- **New finding:** Visa was excluded from all of 2010–2021 by a vendor exchange error.
- **EDGAR verification** is blocked by the network policy.

**Conclusion.** Feasible, with handling rules.

**STOP:** awaiting the owner.

## 2026-10-01: Fundamental infrastructure remediation; readiness checkpoint; STOP (D108, D109)

**Built.**

- A point-in-time fundamentals layer (`qr_fundamentals.py`):
  - field whitelist with hard failure;
  - visibility only after filing, with estimated dates waiting until period end + 90 days;
  - quarantine of accession anomalies;
  - amendment timing;
  - a 200-day freshness limit.
- A dated Visa exchange correction (future runs only).
- A point-in-time financial-format classification derived from each filing's own statements. Vendor sector metadata was shown to be current-status.

**Verification.** Canary E969-01 found zero rule violations over 3.42 million stock-days. Usable coverage is 97.4–99.6% a year. 449 tests pass.

**Verdict: not yet safe to define H016.**

- SEC verification is blocked by the network policy.
- The D043 survivorship gap needs EDGAR to repair.

**STOP:** awaiting the owner (enable SEC access in a new session).

## 2026-10-01: SEC verification and survivorship remediation approved; blocked by SEC access; STOP (D110)

- The owner approved SEC verification, the accession-anomaly resolution and the D043 repair (H016 still not approved).
- `data.sec.gov` and `www.sec.gov` are still refused by the environment's network policy in this session.
- Every item needs SEC data, and approximation is not allowed, so nothing was built or run (`docs/checkpoints/P2_CP6a_sec_access_blocked.md`).

**STOP:** awaiting the owner (allow both SEC hosts, then start a new session).

## 2026-10-01: SEC verification and survivorship remediation; P2-CP6; STOP (D111)

- **SEC access:** `data.sec.gov` works with the project identifier; `www.sec.gov` refuses requests without a contact email.
- **Verified against the SEC:**
  - **Timing:** 99.8% of matched vendor reports become visible only after a public SEC source. 55 early ones are now held to the SEC date. The +90-day rule for estimated dates holds.
  - **Values:** 91–99% match the as-first-filed SEC values. On interim reports, the vendor's "twelve-month" fields are the last fiscal year's totals.
  - **Restatements:** 479 vendor reports (0.8%) carried later restated values and are now blocked. 20 quarantined reports were verified and released; the rest stay quarantined.
- **Survivorship repair:**
  - 163 securities without vendor fundamentals were linked to SEC registrants. This adds a dated, opt-in correction layer.
  - The estimated missing share falls from 14.1% to 11.4% (2010), from 11.5% to 5.9% (2011) and from 1.2% to 0.5% (2021).
  - Recovered names under-performed (8.5% vs 13.8% a year).
- **Final canary (E972-02):** all point-in-time checks are 0. 466 tests pass.
- **Verdict: not yet safe to design H016.** Two items remain: the residual survivorship gap in 2010–2014 and the definition of the twelve-month fields.

**STOP:** awaiting the owner. Decisions requested: an SEC contact email, the twelve-month definition and the residual-gap policy.

## 2026-10-02: Continue SEC repair / True TTM approved; blocked at the SEC contact email; STOP (D112)

- The owner approved:
  - further SEC repair, using SEC ticker/company-history evidence;
  - a True TTM layer built from quarterly filings;
  - a re-audit of coverage and residual bias;
  - a final readiness checkpoint.
- This was conditional on a project-specific SEC contact email.
- **No project email is available, and I will not invent one.** `www.sec.gov` still refuses the project-only User-Agent (HTTP 403); `data.sec.gov` works.
- Nothing was built or run (`docs/checkpoints/P2_CP7a_sec_contact_blocked.md`).

**STOP:** awaiting the owner (a project contact email, or permission to proceed with True TTM on `data.sec.gov` only).

## 2026-10-02: SEC repair continued, True TTM, final data re-audit; P2-CP7; STOP (D113, D113a)

- **SEC access:** the owner authorised their own email as the SEC contact (after P2-CP7a). It is used at run time only and never committed. `www.sec.gov` works.
- **Filing index:** monthly XBRL RSS archives for 2009-06 to 2021-12. They give the SEC-assigned SIC at each filing and the ticker in each instance name.
  - A parser defect (2019-11 to 2021 silently missing) was found and fixed, and everything downstream rebuilt (D113a).
- **Identity v2:** links rest on SEC-dated ticker evidence, with new rules P and F2.
  - 489 registrants linked.
  - Correction table v3.2: **495 repaired securities** (P2-CP6: 163; none of those contradicted).
  - Runs: E977-01 and E978-01 (float fingerprints).
- **Survivorship gap, measured directly SEC-side:** about 0.5–1.2% of companies with float ≥ $2B a year (P2-CP6 estimate: up to 11%). A pre-XBRL blind spot remains: about six US companies acquired in 2010.
- **True TTM:** built from the four latest visible quarters with a Q4 reconciliation gate.
  - Validated against the SEC as first filed (E975-01, 403 companies).
  - Approved: revenue, gross profit, net income and operating cash flow (95–97% within 0.5%).
  - Excluded: operating income and free cash flow.
- **Financial/REIT policy:** SEC SIC at filing time (`qr_industry.py`), with REIT conversions dated.
- **Final canary E976-04:**
  - X976 v1.1, observing the full universe with a 2008-07 warm-up.
  - All 11 checks are 0, including the two new TTM checks.
  - E976-03 reproduces identically.
  - E976-01 and E976-02 are superseded and annotated.
- **Coverage:** final usable non-financial coverage is 81–89% a year, except 2011 (70%: quarantine holes).
- **Data-availability bias:** about +1 pp/yr in absolute levels for a usable-only universe.
- **Checkpoint:** `docs/checkpoints/P2_CP7_fundamental_data_final_readiness.md`. **Verdict: safe enough to begin H016 design** (pre-registration only), subject to 8 owner decisions.
- **Programme status:** no H016, no strategy or factor backtest, no slot used (1 of 3 consumed), Holdout locked.

**STOP:** awaiting the owner.

## 2026-10-02: Final data policies approved; 2011 cleanup; data infrastructure frozen; H016 pre-registration proposed; STOP (D114, D114a)

- **Owner approval:** P2-CP7 and its verdict, plus the final data policies:
  - same universe for every book;
  - July 2008 history-only warm-up;
  - frozen field set and exclusions;
  - conditional acceptance of the ~1% residual gap.
- **2011 cleanup:**
  - E979-01 verified the 135 held-back reports field by field against the SEC originals. Only verified flows are released, through the new field-level release; balance sheets and the 22 non-matching fields stay quarantined.
  - 2011 usable coverage: 69.6% → 76.8%.
  - Final canary E976-06 on the frozen files: C1–C12 all 0.
- **Warm-up:** built into the harness and proven by 9 tests plus the live run (first equity exactly $100,000 after 380 warm-up sessions).
- **Freeze:** data infrastructure **frozen as v1** (43 files, hash-pinned, test).
- **H016 proposal (design only):** gross profits-to-assets, chosen from the literature; top 20; quarterly; EW-H016, SPY and random controls; 8 committed runs plus a canary.
  - `docs/checkpoints/P2_CP8_2011_cleanup_and_H016_preregistration_proposal.md`;
  - `research/hypotheses/H016.md`;
  - `research/phase2/H016_literature_review.md`.
- **Not done:** no H016 implementation or run, no returns, no slot, Holdout locked.

**STOP:** awaiting the owner.

## 2026-10-02: H016 pre-registration approved; prerequisite 7 failed before any run; STOP (D115)

- **Owner approval:** the H016 pre-registration (GP/A, 20 equal positions, $4,500 minimum, March 2010 common start, quarterly, same-universe EW, SPY, 5 random seeds, survivorship sensitivity). Execution is authorised if every prerequisite passes.
- **Built:**
  - decision logic `qr_h016` (tested incl. truncation);
  - S016 for every book;
  - evaluation `p2h016` (common window, gates, G2 median of 5, DSR, frozen survivorship sensitivity);
  - an S016-only portfolio rule;
  - the spec draft.
- **Prerequisite 7 failed:** with D051's 15% gap reserve, every ~$4,900 first entry is scaled to ~$4,250, below the $4,500 minimum, so the $100K portfolio never forms. Options A/B/C are in `docs/checkpoints/P2_CP9a_H016_prerequisite_position_rule.md`.
- **Not done:** nothing run on QuantConnect; slot 2 unused; Holdout locked.

**STOP:** awaiting the owner's choice of §6.3.

## 2026-10-02: H016 sizing option A approved; one-time top-up built and verified offline; spec frozen (D116)

- **Owner approval:** option A — $4,000 minimum new position, the 15% gap reserve kept, at most one top-up per new position toward its original target, a pre-declared minimum top-up, no other resizing.
- **Built:**
  - `qr_h016.plan_topups` with `MIN_TOPUP_USD` = $250 (2 × $7 / 6% ≈ $233, rounded up);
  - the S016 one-time top-up step plus canary counters;
  - an offline simulation with the harness's actual order planner (12 tests): at $100K, first fills ~$4,250, top-ups ~$500, ~95% invested; at $200K ~96%; no negative cash; no repeated top-ups.
- **Spec frozen:** `research/phase2/H016_spec.md` §6.3, hash-pinned.
- **Configs:** canary E980-01 (X980 = byte copy of S016, random seed 0) and E016-01..08.
- **Next:** run the canary; run E016-01 (slot 2) onward only if every check passes.

## 2026-10-02: H016 canary E980-01 passes; candidate run authorised

- **Canary E980-01** (X980 = byte copy of S016, random book seed 0, 2010-03-01 → 2021-12-31): all 20 offline checks (`research/phase2/H016_canary_check.json`) and the harness integrity checks pass.
- **Mechanics:**
  - equity starts 2010-03-01 in cash; first fills 2010-03-02, with 20 positions that day;
  - 48 quarterly rebalances;
  - pit_violations 0; no financial or REIT company in the universe;
  - minimum planned entry $4,153 (≥ $4,000); minimum entry fill $4,180.
- **Top-ups:**
  - 88 positions opened, 83 topped up exactly once, 5 not topped up (below threshold or unfunded);
  - top-ups: minimum planned $309 (≥ $250), median fill $643, never above target;
  - 7 top-up orders a year, top-up commissions $581 in total.
- **Cash and costs:**
  - no negative cash, maximum gross exposure 98.0%; $7 on every order;
  - cash reconciles with the fills, and the remaining credits (dividends) are non-negative;
  - mean invested 96.4%. Below 90% on 0.7% of days: rebalance transitions while D051 waits for sale proceeds to settle.
- **Two minor issues:**
  - two entries were never filled before the next rebalance (`pending_left_at_rebalance` 2);
  - the checker's position reconstruction miscounted across a share split (GIS, 2010). It was fixed to delimit positions at each entry buy; the algorithm's own counter was 1 throughout.
- **Freeze test:** passes.
- **No candidate (GP/A) performance was computed.** Every prerequisite holds, so the H016 development runs start (E016-01 consumes Phase 2 slot 2).

## 2026-10-02: H016 development runs complete; H016 NOT development-qualified; STOP (D117)

- **Runs:** E016-01..08 completed on the common window 2010-03-01 → 2021-12-31. Slot 2 is consumed.
- **Result:**

  | Book | Sharpe |
  |---|---|
  | H016 (CAGR 12.8%, MaxDD −40.5%) | 0.69 |
  | EW-H016 | 0.85 |
  | SPY | 0.92 |
  | Random median (range 0.62–0.98) | 0.75 |

  **G1, G2 and G3 fail; G4 fails by rule.** The conditional robustness runs were not run.
- **Diagnostics:** the survivorship and low-coverage views make it worse (−0.21 / −0.26 vs EW). DSR 0.83 (N 3) / 0.09 (N 43). The ranking adds no measurable value over random selection.
- **Mechanics:** behaved as designed. Top-ups cost 0.06% a year; about 95% invested; no leverage.
- **Checkpoint:** `docs/checkpoints/P2_CP9_H016_development_checkpoint.md`. No Holdout request.
- **Phase 2:** 2 of 3 slots used.

**STOP:** awaiting the owner.

## 2026-10-02: H016 closed as Rejected; final-slot review and H017 proposal; STOP (D118, D119)

- **Owner:** H016 closed as Rejected and preserved as tested. Phase 2 has used 2 of 3 slots. The objective is made explicit: beat S&P 500 buy-and-hold after costs.
- **Review (no backtests, no factor returns):**
  - literature review of the remaining families;
  - a power analysis from completed control books only;
  - an alignment review of the gates.
- **Findings:**
  - A "beat SPY" hard gate (G1.5 in development, HO4 in the Holdout) is proposed. The development gates already block SPY-trailing passes in practice, but not by rule, and the Holdout criteria allow them.
  - Any 20-stock book needs about a 7% a year true edge over its universe to pass half the time.
  - Value (B/M) is the only ready and credible family, but its chance of qualifying is about 1–4%.
- **Recommendation:** approve Amendment 2 and preserve slot 3. H017 = Value is specified in case the owner chooses to spend it.
- **Checkpoint:** `docs/checkpoints/P2_CP10_final_hypothesis_opportunity_H017_proposal.md`.

**STOP:** awaiting the owner.

## 2026-10-02: Research architecture and final-slot review (design only); STOP (D120)

- **Owner:** keep slot 3, do not approve H017 = Value, and redesign around terminal wealth vs S&P 500 total return.
- **Done (no strategy or factor runs, no candidate returns):**
  - rolling-horizon luck profiles and gate operating characteristics from completed controls (`research/phase2/architecture/P2_arch_power.*`);
  - an SEC 8-K earnings-timestamp metadata probe (`sec_8k_earnings_probe.*`): coverage from 2003–04, survivorship-safe;
  - a literature review by period (`P2_arch_literature_review.md`).
- **Findings:**
  - The proposed terminal-wealth framework (Amendment 3) has about a 2.5% false-pass rate and about 5× the power of the current gates. It would still reject H014 and H016.
  - Extending history to about 2000 is not feasible with current data: market cap is absent before October 2009, and fundamentals are missing for companies that died before 2009.
  - Earnings-event continuation is the leading new family, but it has a documented large-cap decay.
- **Recommendation:** preserve slot 3; approve the framework, a priced data study and an earnings-event audit; then pre-register one hypothesis.
- **Checkpoint:** `docs/checkpoints/P2_CP11_research_architecture_final_slot_review.md`.

**STOP:** awaiting the owner.

## 2026-10-03: Amendment 3 frozen; data-extension options; SEC earnings-event audit; STOP (D121, D122)

- **Amendment 3 frozen** with both refinements:
  - W2 uses SE = max(iid, exact stationary bootstrap with 126-day blocks) and a calibrated critical value of 2.15, giving ≤ 5% false passes under plausible persistence;
  - R2 tolerance 0.15.
  - Honest consequence: with 12 years and 20 positions, about a 6.3% a year true edge is needed for an even chance.
- **Data extension:** Sharadar is the best-fitting option (≈ $69/mo, to verify). Nothing bought.
- **Earnings-event audit (no returns):**
  - 85,537 events; coverage 93.9% (≈ 96.7% for domestic filers with predecessor linking);
  - an SEC time-zone inconsistency was found and corrected (timestamp canary 204/204);
  - 13 leakage tests pass.
- **Runs:** E981-01 (identifier export) only.
- **Checkpoint:** `docs/checkpoints/P2_CP12_amendment3_freeze_data_extension_earnings_audit.md`.
- Slot 3 unused; Holdout locked.

**STOP:** awaiting the owner.

## 2026-10-03: H017 earnings-event continuation pre-registration proposed; STOP (D123, D124)

- **Owner decisions:** Event Data v1 approved; no data purchase until a promising result; H017 = earnings-event continuation (proposal only).
- **Proposal** (no returns of any kind):
  - the top decile of 2-session SPY-adjusted reactions to SEC 8-K earnings releases;
  - entry at E+2; 60-session hold;
  - 10 slots ranked by reaction;
  - controls: SPY, EW-H017, day-matched random-event seeds 1–5;
  - a pre-declared event-level diagnostic;
  - a frozen "Promising but Not Qualified" rule and decision tree.
- **Mechanics from event timing only:** ≈ 40 entries/yr, ≈ 1.36%/yr costs at $100K, ≈ 90% invested.
- **Power:** low (a +3%/yr true edge qualifies 4%, or reaches PbNQ / qualifies 18%).
- **Checkpoint:** `docs/checkpoints/P2_CP13_H017_earnings_event_preregistration_proposal.md`.

**STOP:** awaiting the owner. Slot 3 unused; Holdout locked.

## 2026-10-03: H017 implemented; canary E982 passed; READY FOR E017-01; STOP (D125, D126)

- **Owner:** H017 specification approved exactly as proposed; implementation and the non-candidate canary only.
- **Built:**
  - event table v1 (88,723 events, 2,549 verified securities; hash-pinned; integrity canary 10/10 incl. EDGAR 50/50);
  - `qr_h017`;
  - S017 (candidate / random / EW, one code path) and the X982 byte-copy canary;
  - X983 diagnostic (prepared, not run);
  - frozen spec `research/phase2/H017_spec.md`;
  - evaluation (`p2h017`, `H017_eval.py`: Amendment 3, PbNQ, decision tree);
  - all configs, with a runner owner-approval gate.
- **Canary:**
  - E982-01 completed; two checker definitions were too narrow (forced-exit evidence, cap measured at fill), plus the matching R4 limit flaw in the evaluation, all fixed;
  - planned-weight logging added;
  - **E982-02: 25/25 checks pass**; trades identical to E982-01.
- **Tests:** 583 pass.
- **Checkpoint:** `docs/checkpoints/P2_CP14_H017_implementation_canary_readiness.md`: **READY FOR E017-01**.

**STOP:** E017-01 (slot 3) and every other H017 run await explicit owner approval. No candidate performance computed; Holdout locked; no data purchase.

## 2026-10-03: H017 development runs; H017 REJECTED; Phase 2 slots exhausted; STOP (D127, D128)

- **Owner authorised** E017-01..08 under the frozen decision tree (D127). **Slot 3 consumed** at E017-01's start.
- **All 8 runs completed**, no reruns.
- **H017 vs SPY:** final $671,629 vs $516,514; CAGR 17.46% vs 14.88% (W1 pass).
- **W2 fails:** g/SE = 0.71.
- **W3 passes:** H017 beat EW-H017 (13.03%) and all five random-event seeds (10.26–13.62%).
- **R1, R2, R4 pass; R3 fails:** 74% of the excess came from 2014–15; H017 trailed SPY in every block from 2016–21.
- **Classification:** PbNQ rules 3 and 5 fail → **Case A: Rejected**. No conditional runs, no E983-01, no data purchase.
- **Checkpoint:** `docs/checkpoints/P2_CP15_H017_development_result_phase2_final.md`.

**STOP:** all three Phase 2 slots used, all three hypotheses rejected; Phase 2 ends with "No Production Candidate Found" unless the owner decides otherwise. Holdout untouched.

## 2026-10-04: Phase 2 closed (No Production Candidate Found); Phase 3 architecture proposed; STOP (D129, D130)

- **Owner:** Phase 2 closed as No Production Candidate Found; H017 Rejected as tested; Holdout locked; no data purchase. New direction: a systematic multi-indicator technical strategy search, design only.
- **P3-CP1 proposed** (`docs/checkpoints/P3_CP1_systematic_technical_search_architecture.md`):
  - constrained grammar: 1,533 + ≤ 24 configurations, coarse literature grids, information-family redundancy rules;
  - search 2010-03 → 2017-12, procedure walk-forward 2014–17, internal OOS 2018–21 once, Holdout locked;
  - fold-median log excess vs SPY; plateau (neighbourhood 25th percentile); one-standard-error simplicity rule;
  - permutation search-null of the whole procedure (R = 39) as the primary multiple-testing control;
  - in-cloud shadow-book engine with LEAN verification;
  - promotion ≤ 3 → ≤ 2 → 1 → 1.
- **Supporting studies** (no strategy returns):
  - cost feasibility: holdings < ≈ 56 sessions break R4 at 10 slots;
  - search-space counts;
  - calibration on control books only: fake training winners are certain without a null; the chain's false pass ≈ 1%; realistic edges ≤ 4%/yr undetectable; the universe EW trailed SPY by 4.1%/yr in 2018–21.

**STOP:** awaiting the owner's decisions (P3-CP1 §31). Nothing implemented or run; Holdout locked.

## 2026-10-04: Phase 3 engine implemented and fidelity-verified; search spec frozen; P3-CP2; STOP (D131–D135)

- **Owner:**
  - approved the architecture direction;
  - authorised implementation and fidelity work only (no real search, no technical returns, no Holdout, no purchase);
  - required the search to be frozen first.
- **Built:**
  - grammar (1,533 configurations with hashed ids and a one-step neighbour graph);
  - point-in-time indicators;
  - shadow-book engine (harness-identical sizing and mechanics);
  - selection pipeline (gates, fold-median score, plateau, clusters, the cluster-level statistic T, one-standard-error rule, walk-forward);
  - LEAN host X984 (fidelity / canary / gated search; finalist trace);
  - null tooling (`p3spec`, `P3_eval.py`);
  - tests.
- **Fidelity** (tolerances committed before any run):
  - E984-01 matched equity and cash exactly but did not report forced-exit fills (a reporting defect) → fix;
  - **E984-04 passes every tolerance for all 6 control books** (RMSE 0, terminal difference 0, forced exits equal).
- **Canaries** (dummy configurations only):
  - E984-02 (5 worlds) and E984-03 (100 worlds, 31 min, 4.3 GB);
  - E984-05 (100 worlds + full search-mode output, 2.26 MB returned intact);
  - identical seeds give identical books across runs.
- **Batch independence:**
  - E984-06 (1 world) found that the real masks differed slightly from the 100-world run (holdings-dependent subscription and reload cycles) → fix: every stock stays subscribed from first eligibility until delisting, and history is loaded without fill-forward;
  - after the fix, E984-07 (100 worlds) and E984-08 (1 world) have identical digests; E984-09 re-verified fidelity on the final code (all pass).
- **Null design:**
  - within-date signal permutation as the primary null, with R = 500 (R = 39 cannot bracket the 95th percentile);
  - τ = the 25th largest null T (⇔ p ≤ 0.05);
  - synthetic demonstration: search-stage false pass 17/500 = 3.4% (CI 2.0–5.4%);
  - SPA dropped (24.5% size at AR(0.3));
  - block null, PBO and DSR as diagnostics.
- **Spec frozen:** `research/phase3/P3_spec.md` (hash-pinned).
  - Stage 2 and 126/20 removed.
  - Promotion ≤ 3 → ≤ 2 → 1 → 1.
  - Configs E018-01..07 written and gated.
- **Tests:** 621 pass.
- **Checkpoint:** `docs/checkpoints/P3_CP2_engine_null_fidelity_readiness.md`: **READY FOR PHASE 3 SEARCH**.

**STOP:** no real search or null run until the owner explicitly approves. No 2018+ data; Holdout locked; nothing bought.

## 2026-10-04: Phase 3 search run: 500 null worlds, threshold frozen, real search; NO ROBUST TECHNICAL EDGE FOUND; STOP (D136–D138)

- **Owner authorised** E018-01..07 only (D136): null first; threshold committed before the real search; no 2018–2021, no Holdout, no S019.
- **Null** (E018-01..05, 500 within-date permutation worlds; E018-06, 100 block-null worlds as a diagnostic):
  - τ = 0.0284;
  - search-stage false pass 8/500 = 1.6% (CI 0.69–3.13%);
  - fake winners: every no-edge world's best configuration beat SPY, median +6.8%/yr excess CAGR (wealth ratio 1.57); a median of 8 apparent clusters per world.
- **Threshold frozen** in commit 3a1c915 (D137; pinned hash and τ, tested) **before** E018-07 started.
- **Real search E018-07** (1,533 configurations):
  - 90 eligible; 0 clusters above τ; T = 0.0127, p = 0.31 → **Q1 FAIL**;
  - walk-forward −6.8% vs SPY → **Q2 FAIL**;
  - the real best raw winners are weaker than in most fake worlds.
- **No reruns.** Total node time ≈ 3 h 45 min; $0 extra.
- **Checkpoint:** `docs/checkpoints/P3_CP3_systematic_search_stage1_result.md`: **NO ROBUST TECHNICAL EDGE FOUND**.

**STOP:** nothing promoted; no S019, no 2018–2021, no Holdout. Recommendation: close Phase 3 Stage 1 / H018 as No Production Candidate Found.

## 2026-10-04: H018 / Phase 3 Stage 1 CLOSED: No Production Candidate Found; P3-CP4; STOP (D139)

- **Owner closed** H018 / Phase 3 Stage 1 as No Production Candidate Found. The conclusion is limited to the frozen architecture tested; it is not proof that technical analysis fails in general.
- **Recorded:**
  - T 0.0127 vs τ 0.0284 (frozen in 3a1c915), p 0.31;
  - no cluster passed; walk-forward −6.8% vs SPY;
  - no finalist, no S019;
  - 2018–2021 and the Holdout untouched; no purchase;
  - search history preserved unchanged.
- **Permanent lesson:** no-edge fake worlds always produced a SPY-beating best configuration (median +6.8%/yr) and about 8 apparently robust clusters. The best historical configuration is not evidence of an edge.
- **Checkpoint:** `docs/checkpoints/P3_CP4_phase3_closure.md`, with programme status across Phases 1–3 and a context-only list of open directions (none authorised).
- Hypothesis status headers for H016–H018 now cite their recorded outcomes.

**STOP:** awaiting the owner's explicit instruction on the next research direction. No new phase, hypothesis, search, 2018–2021 or Holdout access, or purchase.

## 2026-10-04: Phase 4 Weekly trend/momentum architecture PROPOSED (design only); STOP (D140)

- **Owner direction:** design a Weekly multi-indicator trend / momentum stock-selection architecture. It is not a rescue of H018, and no Weekly backtest is allowed.
- **P4-CP1** (`docs/checkpoints/P4_CP1_weekly_trend_momentum_architecture.md`):
  - ISO-week bars with leakage canaries;
  - 240 configurations (trend-state primary that also defines the exit, entry-only confirmation, volatility filter, fixed relative-strength ranking);
  - N = 12 from mechanics;
  - tethered within-week permutation null with R = 1,000;
  - duration-matched random twins;
  - partition A (one-shot 2018–2021) preferred.
- **Studies** (`research/phase4/`, synthetic / combinatorial only):
  - literature review;
  - grammar count;
  - mechanical portfolio-size study: 20 positions break the D051 mechanics at $100K and 15 degrades with turnover;
  - power study: ≈ 6–8%/yr selection edge needed for the search gates and ≈ 12%/yr for the full pre-Holdout chain, against ≈ 0–3%/yr plausible.
- **Recommendation:** do not implement as a candidate search. The design is ready if the owner wants a definitive low-cost test.

**STOP:** awaiting the owner's go / no-go. No engine implementation, no Weekly returns, no 2018–2021 or Holdout access, no purchase.

## 2026-10-04: P4-CP2 Deep Technical Indicator & Strategy Evidence Review (research only); STOP (D141)

- **Owner direction:** evidence-first review of technical concepts A–N (trend, cross-sectional and time-series momentum, 52-week high, breakout, RSI, MACD, ADX, volatility, Bollinger, volume, pullbacks, volatility contraction, multi-timeframe) before any new backtest.
- **Sources:** about 50 references with a source level and verification status (`research/phase4/P4_CP2_references.md`). Post-2017 papers (†) are used only to caution. SEO statistics were rejected.
- **Findings (`docs/checkpoints/P4_CP2_technical_evidence_review.md`):**
  - only intermediate cross-sectional momentum is Tier A, and it is Tier B in large US caps after 2002;
  - smooth (frog-in-the-pan) momentum and a multi-horizon trend score are credible refinements, new to the project;
  - long-term trend, time-series momentum, volatility and market state are risk / exit / exposure tools, not selection alpha;
  - RSI, MACD, ADX, Bollinger, squeeze, volume confirmation, pullback timing and short breakouts are Tier D for our universe, and most already failed here;
  - multi-timeframe daily timing has practitioner support only.
- **Archetypes:** 9; worth considering: AR2 smooth momentum, AR3 trend score, AR1 trend-filtered momentum with trend exit. AR6–AR9 are mostly tested and not recommended.
- **Timeframe:** slow decisions (weekly / monthly), daily only for inputs and execution.
- **Next architecture:** stop, or a universe-wide signal-level pre-test of at most 3 pre-registered signals followed by at most one book (recommended if continuing).
- **Nothing computed or run:** no indicator returns, no QC run, no 2018–2021, no Holdout, no H019, no purchase.

**STOP:** awaiting the owner's decisions (P4-CP2 §33).

## 2026-10-04: P4-CP3 Cross-Sectional Technical Signal Validation Architecture (design only); STOP (D142)

- **Owner:** accepted P4-CP2. Next step = validate whether three pre-registered technical signals carry cross-sectional information **before** any portfolio is built. Design only.
- **Signals:**
  - S1 12-1 momentum (reference);
  - S2 smooth momentum (Da-Gurun-Warachka sequential sort: momentum quintile, then net up-day share);
  - S3 trend score (mean log distance above the 50/100/200-day averages; Han-Zhou-Zhu measurement, unweighted).
- **Design** (draft pre-registration `research/phase4/P4_xs_spec.md`):
  - monthly ranking, 92 decisions 2010-02 → 2017-09, 3-month forward demeaned returns;
  - deciles, rank IC, monotonicity, raw-primary / sector-neutral and size diagnostics;
  - Newey-West t, within-momentum-quintile incremental test;
  - identity-tethered within-date permutation null (R = 5,000); max-statistic at α = 1% (prior momentum looks counted);
  - multi-part promotion rule; pre-registered consequences.
- **Built (synthetic only):** `qr_xs.py` (16 tests) and a power study (`P4_xs_power.json`). Findings:
  - about 40 effective observations;
  - the naive test over-rejects about 3×;
  - 50%-power top-decile edge ≈ 4% / 7% / 10% a year depending on IC noise, so a 1–3% edge is essentially undetectable;
  - weekly ranking gives no power gain;
  - 1-month horizon somewhat more powerful than 3 months (owner choice offered).
- **Caveat:** paper PDFs blocked by the network policy; formulas to be confirmed against the full texts before freezing.
- **Nothing real computed:** no real signal, return, IC or null; no QC run; no 2018–2021; Holdout locked; no purchase.

**STOP:** awaiting the owner's GO / NO-GO and choices (P4-CP3 §40).

## 2026-10-04: P4-CP3R corrected H019 specification v1 (frozen candidate; nothing run); STOP (D143)

- **Owner:** conditional GO toward H019 after corrections. Primary horizon 1 month (3 months diagnostic only); exact published signal definitions; α = 1% described honestly; no real validation yet.
- **Verification:**
  - Paper PDFs still blocked; only GitHub reachable.
  - Frog-in-the-pan ID, PRET (12-1), counting rule and sequential sort verified from several independent records.
  - Han-Zhou-Zhu trend factor verified against the complete Chen-Zimmermann open-source reproduction (11 MA lags, monthly regressions, 12-month average of past coefficients).
- **Frozen candidate v1** (`research/phase4/P4_xs_spec.md`, SHA-256 3a0e3643…, pinned):
  - S1 12-1 momentum (reference);
  - S2 exact ID with the sequential sort;
  - S3 exact trend factor, point-in-time, estimated within the ≥ $2B universe;
  - 82 monthly decisions 2011-02 → 2017-11, next-month demeaned returns, NW lag 2;
  - quintile monotonicity (changed before any data after the synthetic study exposed S2's decile zig-zag);
  - within-momentum-quintile incremental test; tethered null R = 5,000; max-statistic at 1%.
- **Synthetic power:**
  - effective sample ≈ 82 (vs ≈ 35 at 3 months);
  - full-rule false promotion 0%;
  - 50% detectable top-decile edge ≈ 4.5–11% a year; a 1–3% edge is almost certainly not confirmable.
- **Verdict:** READY FOR H019 SIGNAL VALIDATION, subject to the owner's explicit approval (including S3 = exact HZZ, a broader multi-horizon model than P4-CP3's simplified score).
- **Nothing real computed:** no real signal, return, IC or null; no QC run; no 2018–2021; Holdout locked.

**STOP:** awaiting explicit approval of the corrected frozen specification.

## 2026-10-04: P4-CP3R2 H019 implementation fidelity and null readiness (nothing run); STOP (D144)

- **Owner:** conditional approval; one more fidelity checkpoint before any H019 run, focused on the published signal mechanics and the null.
- **Trend factor, verified against the Chen-Zimmermann replication code:**
  - partial moving-average windows for young stocks (the author notes the paper is silent);
  - Stata-style omission of collinear regressors;
  - a 12-month average of past coefficients. We require all 12, as in the paper; OSAP's start-up exception is disclosed.
  - QuantConnect's 1998+ history gives established stocks full 1,000-day windows.
- **Frog-in-the-pan conventions** (independent records): zero-return days count in the denominator; PRET quintiles then ID; the invented 200-day minimum is removed.
- **Window fixed mechanically:** 83 decisions, 2011-01 → 2017-11 (the first trend-factor score needs 12 regressions starting 2010-01).
- **Built:**
  - a complete point-in-time pipeline (`qr_xs.Panel/Features/run_world`), checked against a slow reference;
  - leakage canaries (future prices, next-month returns, truncation, late entrants, coefficient chronology);
  - a null that permutes each stock's whole feature vector within history strata and **re-estimates the trend factor in every world**.
- **End-to-end synthetic study:**
  - false-promotion rates about 0–1%;
  - about 83 effective monthly observations;
  - 50% detectable top-decile edges: about 4–12% a year (S1), 4–15% (S3);
  - a 1–3% edge stays undetectable.
- **Spec v2** (`research/phase4/P4_xs_spec.md`, SHA-256 15fb0451…) pinned. Verdict: READY FOR H019 RUNS, subject to owner approval.
- **Nothing real:** no real signal, return, IC or null; no QC run; no 2018–2021; Holdout locked.

**STOP:** awaiting explicit approval before any H019 execution.

## 2026-10-04: H019 executed — plumbing canary, 5,000 null worlds, frozen threshold, ONE real evaluation; P4-CP4: NO SIGNAL QUALIFIED; STOP (D145–D149)

- **Owner (D145):** authorised the final H019 run under the frozen spec v2, in a fixed order, with S1 as a replication check and prescribed wording.
- **Plumbing / fidelity canary (X985):** E985-01..04 found technical defects, fixed without touching any signal definition or rule:
  - a mis-specified regression-span check;
  - S3 prices at spin-offs (QuantConnect's dividend feed carries spin-offs unlabelled, so CRSP's spin-off factor cannot be reproduced without an invented rule: split-feed prices kept, exposure 1.46% disclosed);
  - one vendor split / price-factor inconsistency (BTU 2015), fixed by building every price from raw bars and QuantConnect's own split and dividend feeds.
  - **E985-05 passed 14 / 14** (truncation exact, slow recomputation exact, planted response IC = 1, placebo |t| ≤ 1.73, determinism).
- **Null:** E020-01..05, 5,000 / 5,000 worlds, none failed or retried. **c = 2.8715**, committed and pinned in 1dc6b07 before the real run (F > c 0.98%; full-rule false promotion 0 / 5,000).
- **Real evaluation E020-06, once:** outcome **none**.
  - Top decile vs the average stock: S1 −2.2%, S2 −1.2%, S3 −2.9% a year.
  - IC t 0.22 / 0.34 / 0.12.
  - S2's smoothness adds nothing detectable within momentum quintiles (t 1.31); S3 neither predicts nor adds (t 0.09) and is not merely momentum (correlation 0.23).
  - F = 1.31 vs c = 2.87. Momentum not reproduced.
- **Verdict: NO SIGNAL QUALIFIED FOR PORTFOLIO RESEARCH.** "No technical stock-selection signal large enough to satisfy the project's detection and economic-significance requirements was found."
- **Untouched:** no 2018–2021, no Holdout, no portfolio, no paid data.

**STOP:** awaiting the owner (recommendation: close H019 and the technical stock-selection line as No Production Candidate Found).

## 2026-10-05: P5-CP1 Structured Historical Chart Analysis Architecture (design only); STOP (D150)

- **Owner direction:** continue technical stock-selection research through structured chart analysis (Weekly structure → Daily setup → fixed checklist → chart-quality score), reconstructed point-in-time. Design only.
- **Design reference (synthetic data only):**
  - deterministic point-in-time algorithms for weekly bars, confirmed swing points, HH/HL structure, support / resistance zones, support trendlines, bases, breakouts, volume, extension and risk;
  - a proposed four-category checklist (5 binary conditions each, total 0–20) with four disqualifiers;
  - a dependency-free, byte-reproducible chart renderer;
  - 35 tests, including future-perturbation pixel canaries.
- **Two demo-driven design fixes, made before any real data:**
  - anchored support / resistance clustering;
  - active levels kept on screen.
- **Key findings:**
  - Every needed feature is reconstructable point-in-time inside QuantConnect.
  - AI visual scoring of historical charts is blocked by the data licence and the protocol, is not reproducible enough and is over budget. It is at most a synthetic-chart consistency study.
  - The trend part of the rubric re-tests ideas that already failed; the geometry part is new.
  - Power is similar to H019 (≈ 5%/yr detectable).
- **Recommendation:** one pre-registered deterministic rubric (H020) tested at the signal level if research continues; otherwise stop.
- **Untouched:** no historical chart scored or viewed, no AI call, no backtest, no 2018–2021, Holdout locked.

**STOP:** awaiting owner decisions (P5-CP1 §42).

## 2026-10-05: H020 implementation + synthetic canaries; P5-CP2 READY FOR H020 REAL SCORE VALIDATION; STOP (D151–D153)

- **Owner authorisation (D151):** implementation, reproducibility, leakage testing and canary validation only. No real chart scores, no returns by score, no real-universe null, no AI.
- **Built:**
  - the deterministic chart-score pipeline (`qr_chart`): Daily + Weekly bars, confirmed swings, structure states, anchored zones, support / resistance trendlines, one base and one breakout definition, volume in three roles, contraction, entry risk, the 20-condition checklist (0–20, no weights) and 5 disqualifiers;
  - the frozen renderer;
  - the statistics / null / gates module;
  - the threshold-provenance table (A–E);
  - the frozen spec v1 (hash-pinned with the code and the scenario table).
- **Canaries (synthetic):** every leakage canary passes, including byte-identical Daily and Weekly PNGs whatever follows t. All 12 synthetic scenarios match their frozen expectations exactly. Results are byte-reproducible across runs and processes. 95 tests.
- **Fixed before any real data (D152):** the null's momentum strata made it self-match and then too narrow (6% false significance at 1%). The null is now an unstratified, no-self-match identity tether, calibrated at 0.3–0.8%. Each test statistic has its own critical value, and promotion needs both (intersection-union).
- **Power (synthetic):** the +3%/yr economic floor binds before significance. The realistic 50% detectable High-group edge is ≈ 3–5%/yr.
- **Runtime:** ≈ 8–9 h of QuantConnect node time for the full future sequence, $0 extra.
- **Verdict:** READY FOR H020 REAL SCORE VALIDATION, subject to explicit approval.
- **Untouched:** no real data, no QuantConnect run, no 2018–2021, Holdout locked.

**STOP:** awaiting the owner's explicit approval before step 1 (E987-01 plumbing / fidelity canary).

## 2026-10-05: H020 real validation — canary, 5,000 null worlds, pinned thresholds, ONE real evaluation; P5-CP3: NO CHART SCORE QUALIFIED; STOP (D154–D158)

- **Owner authorisation (D154).** The real H020 validation under the frozen spec. Pre-run addendum 1 fixed two things before any real computation: the response is total shareholder return, and a NON-GATING point-in-time sector diagnostic was added.
- **Canary E987-01: 12 / 14 checks.**
  - The independent point-in-time recomputation was identical in 120 / 120 samples.
  - The total-return recomputation agreed to 7e-16, and dividends are included.
  - The two failures were not fidelity defects: 2010 industry coverage of 69%, and a mis-specified planted-null criterion (D155).
- **Null E021-01..05: 5,000 / 5,000 worlds.**
  - Two download recoveries after a QuantConnect status quirk and a container restart (D156); no world was re-run.
  - c_ic = 2.33 and c_inc = 2.26, pinned in commit 55bf663 before the real run (D157).
- **Real evaluation E021-06, once.** Every gate fails.
  - IC t = 0.27; incremental t = 0.22.
  - The high-score group returned −0.4%/yr vs the average stock; the top group (16–20 points) −1.3%/yr.
  - Monotonicity −0.3.
  - The sector-adjusted and 13-week results (both non-gating) agree.
- **Verdict: NO CHART SCORE QUALIFIED FOR PORTFOLIO RESEARCH.** "The frozen structured chart-analysis rubric did not demonstrate predictive information large enough and robust enough to qualify for portfolio research." This does not mean that chart analysis does not work, nor that no 1–2% edge exists.
- **Untouched:** no 2018–2021, Holdout locked, no portfolio, no AI, no data purchase, no tuning, no rerun.

**STOP:** awaiting the owner (recommendation: close H020 as Rejected).
