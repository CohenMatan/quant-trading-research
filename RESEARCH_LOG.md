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

## 2026-10-05: P6-CP1 Sector / ETF Rotation Evidence and Validation Architecture (design only); STOP (D159)

- **Owner direction:** a new unit of prediction — sectors instead of stocks. Evidence, data feasibility and signal-validation design only.
- **Evidence:**
  - Industry momentum is a strong pre-1999 US result.
  - It is mostly a short-horizon, no-skip effect, and its mechanism is debated.
  - The best post-2000 sector-ETF test found no momentum.
- **Data (E988-01 availability probe, no returns):**
  - the nine original Select Sector SPDRs have complete QuantConnect history from 1998-12-22 with no backfill;
  - XLRE starts in 2015 and XLC in 2018, so both are excluded;
  - iShares and Vanguard sector ETFs start later and are less clean.
- **Power (synthetic):**
  - with about 6 effective sectors, only long samples help;
  - the 50% detectable top-3 edge is about +3.3%/yr with 2000–2017 (needs a D035 amendment) and about +5.3%/yr with 2010–2017 alone;
  - that is above a realistic 0–2.5%/yr.
- **Recommendation:** NO-GO. Alternatively, one pre-registered falsification test (H021-A: 6-month total-return relative momentum, monthly, 9 SPDRs, 2000–2017).
- **Untouched:** nothing real computed; no 2018–2021 data; Holdout locked; no purchase.

**STOP:** awaiting the owner (H020 closure; Phase 6 GO / NO-GO; if GO, the decisions in P6-CP1 §39).

## 2026-10-06: H021-A sector relative-momentum falsification test; P6-CP2; STOP (D160–D164)

- **Owner decisions (D160):**
  - H020 closed as Rejected.
  - D035 amended for Phase 6 only: 2000-01 → 2017-11, nine Select Sector SPDRs.
  - Limited GO for ONE falsification test, H021-A: 6-month total-return relative momentum, monthly, next-month sector-relative total return, rank IC, gates P1–P4, R = 5,000 derangement null.
- **Frozen spec v1** (`research/phase6/H021A_spec.md`) and module `qr_h021`, hash-pinned in `qresearch.p6h021`. Host: X989 / S022.
- **Canary:**
  - E989-01 failed on a plumbing KeyError, fixed (D161).
  - E989-02 passed 10/12 check groups; every signal and response was reproduced day by day to 1e-15.
  - The two tolerance failures are explained by QuantConnect's dividend feed rounding distributions to the cent (probe E990-02: 757/757 within half a cent of ADJUSTED). They were assessed as not a fidelity defect; the construction is unchanged (D162).
- **Null E022-01..05:** 5,000/5,000 worlds, no failures, retries or recoveries.
  - c = 2.658, pinned in commit ea284cb before the real run (D163).
  - False qualification of the whole procedure under the null: 0.2%.
- **Real evaluation E022-06, once:**
  - IC −0.011 (t −0.35), p 0.64.
  - Top 3 +0.16%/yr; middle +0.80; bottom −0.97.
  - Halves + / −; IC sum negative.
  - **P1–P4 all FAIL → H021-A DID NOT QUALIFY.**
  - The non-gating diagnostics agree: 2010–2017 t −1.36; 3-month t 0.22; 6-month t 0.71.
- **Interpretation:** "No sector-relative momentum edge large and robust enough to meet the project's pre-registered statistical and economic requirements was detected. The study has only about 50% power around a +3.3%/yr top-3 edge. A small real edge may therefore remain undetectable."
- **Untouched:** no tuning, no other lookback, no H021-B, no portfolio, no 2018–2021, Holdout locked, nothing purchased.

**STOP:** awaiting the owner (recommendation: close H021-A and Phase 6).

## 2026-10-06: Phase 6 closed; P7-CP1 Multi-Factor Conviction Score data & fidelity readiness audit; STOP (D165–D168)

- **Owner (D165):** H021-A rejected and Phase 6 closed. Phase 7 = a multi-factor stock conviction score (technical + fundamental + sector per stock; the market regime controls exposure). P7-CP1 = a data / point-in-time / fidelity / feasibility audit only.
- **Audits** (infrastructure; 2010–2017; no returns, no score):
  - X991: fundamentals, universe, sector, alignment (E991-01, E991-02);
  - X992: prices, technical features, breadth, corporate actions (E992-01, E992-02, E992-03);
  - an SEC sample check;
  - 18 new offline tests (feature fidelity, leakage canaries, host pipelines).
- **Results:**
  - technical features recomputed independently: 380/380 agree;
  - fundamental leakage checks all 0; 0 of 268 sampled records usable before the SEC filing;
  - non-financial full-core fundamental coverage 77–89%;
  - SEC SIC sector ≥ 92% from 2011; Morningstar sector codes are current-status;
  - breadth computable without survivorship bias (survivors-only would err by up to 3.2 points);
  - cross-domain alignment: 0 violations.
- **Defects:**
  - re-used ticker ids joining two companies → security-life rule (D167);
  - corporate-event mis-adjustments → disqualifier needed;
  - blank Morningstar company id;
  - duplicate share classes;
  - 2 unexplained moves.

  No earlier result is affected or re-run.
- **Mechanical development window:** 2011-01 → 2017-12.
- **Verdict:** READY TO DESIGN SCORE.

**STOP:** awaiting the owner (P7-CP1 item 40).

## 2026-10-06: P7-CP2 conviction score v1 architecture and pre-registration; STOP (D169, D170)

- **Owner (D169):** P7-CP1 accepted. Adopted:
  - the 2011–2017 window and the seven approved fields;
  - Financials / REITs excluded (no technical-only route);
  - the same-universe missing-data rule;
  - mechanical corporate-event exclusion and the security-life rule;
  - the price-series rules and one share class per company;
  - $100K, 10% cap, cash allowed;
  - portfolio size not yet chosen.
- **Score v1** (frozen candidate, hash-pinned):
  - **Technical 40:** trend state 15 / 8 / 0; 12-1 momentum quintile 15; volatility quintile 10.
  - **Fundamental 45:** GP/A 15 and equity/assets 10 (both sector-relative); cash conversion 10; revenue growth 10.
  - **Sector 15:** breadth vs market.
  - **Seven hard disqualifiers.**
  - **Market regime** (SPY trend × PIT breadth): caps positions only.
  - **Monthly review**, plus a weekly disqualifier check of holdings.
  - **Hysteresis and replacement buffer;** no time stop, no forced filling.
- **Deferred to P7-CP3** (returns-blind): entry, exit, buffer, max positions, regime ceilings.
- **Tests:** 20 synthetic sanity tests (cases A–E, regime cases, hysteresis) and 3 pin tests.
- **Synthetic difficulty:** median ≈ 43; ≈ 1–3% of scorable names ≥ 80.
- **Verdict:** READY FOR AVAILABILITY / MECHANICS STUDY.
- **Untouched:** no market data, no returns, no 2018–2021, Holdout locked.

**STOP:** awaiting the owner (P7-CP2 item 49).


## 2026-10-06: P7-CP3 score availability, capacity, churn and cost mechanics; STOP (D171, D172)

- **Owner (D171):** P7-CP2 accepted.
  - Score v1 is frozen exactly as specified; disqualifiers, data and price-series rules are frozen.
  - Monthly review plus a weekly disqualifier check of holdings.
  - 10% is the maximum initial position (no trimming); no forced filling.
  - The automatic selection rules are rejected.
  - Mechanics only: no returns of any kind.
- **Built:**
  - X993 v1.0 non-trading export host (`qr_p7_export`: exact sliced technical inputs, verified against the full computation);
  - runner / config rule;
  - tests;
  - pre-registered conventions (whipsaw within 3 reviews, ties score → ADV20 → id, cost notional $100K × min(10%, 1/K)).
- **Run:** E993-01 (0 orders, 712 s) exported 84 monthly reviews (2011-01 → 2017-12) and 325 weekly checks, with no price and no return.
- **Offline mechanics:** `research/phase7/P7_CP3_mechanics.py`, covering 4 entries × 3 profiles × 4 sizes.
- **Findings:**
  - **Rarity** among about 425 eligible stocks a month: 75+ 3.7% (about 15.6 a month); 80+ 1.4% (about 6.1); 85+ 0.4% (about 1.6); 90+ 0.13% (about 0.5). The maximum score was 94.
  - **Breadth across layers:** every 80+ stock had Technical ≥ 23, Fundamental ≥ 25 and Sector ≥ 8.
  - **Persistence:** high scores are short-lived (median 1 month above any threshold). The causes are the trend / sector 7-point steps and the volatility rank.
  - **Holding periods:** median implied holding 1–3 months (H3 Patient longest).
  - **Capacity:** 80+ fills 6 slots in 46% of months and 10 slots in 21%; 75+ fills 10 slots in 76%; 85–90 leave the book mostly in cash.
  - **Costs:** 0.1% (90+) to 1.7% a year (75 / H1 / 12); 80+ costs 0.55–1.04%.
  - **Regime:** STRONG 75% of months, RISK_OFF 6% (3 short episodes).
  - **Weekly checks:** 1.5–7.5% of orders, mostly acquisitions.
  - **Exclusions:** H2 is the dominant disqualifier. The baseline-ledger reading (eligible-only) is put to the owner.
  - **Sector clustering** (technology, utilities) is material; candidate caps are proposed.
- **Report:** `docs/checkpoints/P7_CP3_score_availability_capacity_churn_cost_mechanics.md`. Nothing is chosen. No 2018–2021 data, Holdout locked, nothing purchased.

**STOP:** awaiting the owner's selection of the mechanics (P7-CP3 section 12).

## 2026-10-06: P7-CP3R revenue-baseline correction and final mechanics confirmation; STOP (D173, D174)

- **Owner (D173):** the YoY revenue baseline becomes the company's PIT revenue from the full store, regardless of past universe eligibility ("fundamental history belongs to the company"). Score v1 is unchanged. Provisional mechanics: 80 / 70 / 5, K = 10, regime limits 10 / 8 / 5 / 2, at most 3 per sector, sticky share class, 20% grown-winner cap (rule only), no ladder.
- **Built:**
  - `RevenueLedger`, recorded live for every store company, with same-life / same-registrant / chronology checks;
  - X993 v1.1;
  - the provisional planner `qr_p7_mech`;
  - PIT tests A–E.
- **Run:** E993-02 (0 orders).
- **Result:**
  - 6,282 rescued stock-months (8.9% of non-financial rows; 96% had been below $2B), all point-in-time; SEC sample of 160 quarters all public before the baseline day.
  - The change is exactly isolated (0 H2 mismatches vs E993-01; regime identical).
  - Fully scorable stocks +13%; 80+ mean 6.1 → 7.0 and still rare (1.47%); persistence and the score distribution unchanged.
  - Provisional mechanics: 47 orders a year, 0.80% a year, 69% utilisation.
- **Verdict:** MECHANICS CONFIRMED — READY TO FREEZE FOR PREDICTIVE TEST DESIGN. Decisions for the owner are in section 10 of the report.

**STOP:** awaiting the owner.

## 2026-10-06: P7-CP4 frozen mechanics and predictive-test architecture (H022); STOP (D175, D176)

- **Owner (D175):** P7-CP3R approved. Frozen:
  - the store-wide revenue baseline and CIK Option A;
  - Score v1;
  - mechanics 80 / 70 / 5, K = 10, regime limits 10 / 8 / 5 / 2, ≤ 3 per sector, owner tie-break, sticky share class, weekly sell-only, 20% grown-winner rule;
  - costs.
  Design the predictive test only.
- **Built:**
  - `qr_p7_pred.py`: total-return responses with a delisting rule; one-month demeaned response; monthly Spearman IC with NW t; gates G1–G4; identity-tethered full-procedure null; critical-value floor;
  - `grown_winner_trims`;
  - canaries A–G;
  - frozen spec v1 + H022 + result template, pinned in `qresearch.p7pred` (commit 4c497df).
- **Synthetic power** (real score tables, synthetic returns):
  - false promotion 0.3%;
  - 50% power at IC ≈ 0.033 (80+ group ≈ +6.3%/yr);
  - 80% power at IC ≈ 0.047 (≈ +10.2%/yr).
- **Recommendation:** GO for one real evaluation (canary X994 → null E023-01..05 → pin c_IC → E023-06 once), with the stated limitation that 2–4%/yr edges are usually missed.
- No real return, IC or portfolio; no QuantConnect run; 2018–2021 and the Holdout untouched.

**STOP:** awaiting the owner.

## 2026-10-06: P7-CP5 execution of H022 — canary passed, null pinned, real evaluation BLOCKED by an engine change; STOP (D177–D181)

- **Owner (D177):** one frozen real evaluation of H022, after a wording-only fix in spec C3 (new spec SHA-256 `2c99f962…`; committed 7906b0b).
- **Host:** S023 / X994 (byte copy) built from the X993 v1.1 pipeline plus total-return responses; synthetic host tests.
- **Canary:**
  - E994-01 failed at start-up on its own fingerprint guard (LEAN's runtime copy of a source file is not byte-identical; nothing computed). The check moved to the runner (D178).
  - **E994-02 passed 19 / 19** (timing, fresh-history corporate actions, invariance, truncation, score identical to E993-02, determinism; no real IC).
- **Null E023-01..05:** 5,000 / 5,000 worlds, identical panel everywhere. **c_IC = 2.390976** (floor not binding); full-procedure false promotion 7 / 5,000. Pinned in dbfdcc0 BEFORE any real run (D179).
- **Real evaluation — not computed:**
  - E023-06 never started: QuantConnect refused the engine-pin call (Trading Firm tier now required; D180).
  - E023-07 ran on LEAN 18166 instead of 18131; the host refused because the panel differed ("nothing computed"; D181).
  - No real statistic exists; H022 is neither qualified nor rejected.
- **Options for the owner** (P7-CP5a): A upgrade (≈ $480 / month, over the ceiling), **B** diagnostic canary on the default build after 2026-10-10 (recommended), C data v2 + new null, D stop.
- 2018–2021 and the Holdout untouched; no portfolio; nothing purchased.

**STOP:** awaiting the owner.

## 2026-10-10: P7-CP5b option B result — default build does not reproduce the frozen data (B2); STOP (D182, D183)

- **Owner (D182):** option B. A diagnostic canary on QuantConnect's default build after the 2026-10-10 dataset switch; B1 → real run with the pinned c_IC, B2 → STOP.
- **Runner:** `lean_version_policy: "default_build_digest_verified"` (H022 family and the X993 diagnostic only; the build actually used is recorded).
- **E994-03** (LEAN 18178): canary crashed; no decision date had ≥ 20 population stocks.
- **E993-03** (frozen X993 export, LEAN 18178) vs E993-02 (18131):
  - reports with unknown filing timing 608 → 31,538;
  - usable revenue baselines 78,633 → 2,269;
  - H2 on 99% of eligible rows;
  - eligible universe −18%;
  - H022 population 0–14 a month (was 196–612);
  - 0 point-in-time violations.
- **Result: B2.** The frozen data infrastructure v1 is not reproducible on the default dataset. No real H022 statistic exists; c_IC unchanged.
- **Options** (P7-CP5b): C data v2 starting with a timing probe (recommended, step 1 only), A Trading Firm tier (over ceiling), D close H022.
- 2018–2021 and the Holdout untouched; nothing purchased.

**STOP:** awaiting the owner.

## 2026-10-10: P7-CP5c new-dataset fundamental-timing probe — PARTIAL / NO-GO; STOP (D184, D185)

- **Owner (D184):** option C step 1 only, an investigation of whether the new QuantConnect dataset has a safe, verifiable point-in-time source for report availability dates.
- **Pre-registered sample:** the X971 sample (406 companies) + S2 (74; `research/phase7/cp5c/sample_s2.py`), fixed before any probe.
- **QuantConnect blocked the probe:**
  - 50-file project limit (E995-01; runner fixed to delete stale files first, E995-03);
  - E995-04 stopped mid-run ("Deleted by request"; partial output unused);
  - E995-05 rejected at build: "Data cannot be exported for any purposes, including data probing or validation".
- **Public LEAN source:** the timing fields still exist (not retired).
- **Vendor docs:** pre-2013 statements lack filing dates (45-day nominal fallback).
- **Offline public-SEC evidence:**
  - 10-K filed more than 45 days after period end in 87.5% of cases;
  - 12–16% of revenue periods are later re-reported with a different value;
  - an SEC-only layer passes H2 for 24.3% of non-financial eligible stock-months (2011: 1.3%), vs 74.9% on data v1 and 1.2% on the new vendor data; ≤ 49.3% even with a gross-profit derivation.
- **Verdict:** NO-GO. No trustworthy PIT timing for the new vendor data; the only trustworthy source (SEC) covers too little for Score v1.
- No returns, no H022 statistic, no portfolio, no 2018–2021 research, Holdout untouched, nothing purchased.

**STOP:** awaiting the owner.

## 2026-10-10: P7-CP5d Score v1 migration feasibility — NO-GO; STOP (D186, D187)

- **Owner (D186):** test whether the frozen Score v1 can run on the new feed using the historical stream's first-seen time (M1), optionally gated by the SEC filing date (M2); M3 assessed only. In-cloud validation only; no H022, no returns.
- **Built:**
  - SEC reference table (complete populations, fixed before any run, fc49027);
  - X996 v1.0 first-seen ledger host (frozen X993 v1.1 pipeline; aggregates and SHA-256 digests only);
  - synthetic host tests.
- **Runs (LEAN 18178, all accepted by QuantConnect's compliance review, 0 orders):**
  - E996-01: M1, full window;
  - E996-02: M1, truncated at 2013-12-31;
  - E996-03: M2, full window.
- **PASS:**
  - truncation invariance (identical ledger, eligibility and 35/35 review score digests to 2013-12-31);
  - determinism (identical stream in independent runs);
  - SEC timing (96–99% of 41,312 matched reports first seen the day after the SEC filing, pre-2013 included);
  - vintage (no backfill: restated periods show the original value in 88% revenue / 98.5% assets; residual 0.26%);
  - compliance / export.
- **FAIL — universe PIT safety:**
  - the new feed lacks market cap for ~18% of data-v1 eligible stock-months (560 securities);
  - 50% of them are still in the universe at end-2017, vs 92% retained → survivorship bias.
- **Conflict before 2013:**
  - M1 makes 277 reports usable before their SEC filing (46 without an earnings release);
  - M2 removes them but leaves 2011–2012 nearly unscorable.
- **Coverage M1:** H2 28.5%; 291–677 scored a month (mean 486); 80+ 5.9 a month.
- **Verdict:** NO-GO — Score v1 cannot be migrated safely on the available QuantConnect infrastructure (requirement 6).
- No returns, no H022 statistic, no portfolio, no 2018–2021, Holdout untouched, nothing purchased.

**STOP:** awaiting the owner — (a) close H022, (b) universe-repair feasibility study only, or (c) dormant.

## 2026-10-10: P7-CP5e universe repair feasibility — GO; STOP (D188, D189)

- **Owner (D188):** option (b) of P7-CP5d. Can the new feed's universe be repaired PIT-safely (SEC market cap where QuantConnect has none)? Can SEC identity be verified before the first XBRL filing so M2 works in 2011–2012? Score v1 and M2 frozen; infrastructure only.
- **Pre-registered before any repair result (0e63a03):**
  - frozen target population: 560 securities / 18,915 stock-months;
  - success criteria MC1–MC9 and ID1–ID5.
- **Offline, public SEC data only:**
  - identity evidence from EDGAR submissions: 1,333 SAFE, 474 bounded, 105 REJECT;
  - target fates: 221 still in the universe at end-2017, 266 acquired, 52 fell below a filter;
  - SEC share counts fresh for 87% of target stock-months;
  - 2013-start power study.
- **QuantConnect (LEAN 18178; all accepted; 0 orders; aggregates only):**
  - E997-01: repair + identity extension;
  - E997-02: repair only;
  - E997-03: exact rerun of E997-01 + security counts.
- **Market cap:** every pre-registered criterion passes.
  - 86% of missing-cap target months get a fresh SEC cap;
  - splits 223/224 continuous;
  - $2B agreement 98.4% away / 95.7% near;
  - 68.9% of lost stock-months recovered (371 securities);
  - survivor share 84.1% vs data v1 83.3% (delivered feed 90.0%).
- **Identity:** extension-mapped reports match SEC values like v2-mapped ones. Fully scored stocks per month:
  - 2011: 304–378 (10 without the extension);
  - 2012: 359–406;
  - 2013+: 407–734.

  A 2013 start is not forced; it would raise the 50%-power IC from 0.033 to 0.050.
- **Verdict:** GO — universe can be repaired PIT-safely and Data v2 design can proceed. Proposed Data v2 architecture in the checkpoint; nothing built or frozen.
- No returns, no H022 statistic, no portfolio, no 2018–2021, Holdout untouched, nothing purchased.

**STOP:** awaiting the owner (approve / amend Data v2; confirm window 2011–2017; authorise the Data v2 build and freeze checkpoint).


## 2026-10-10: P7-CP5f Data Infrastructure v2 build and freeze — NOT FROZEN (gate K); STOP (D190, D191)

- **Owner (D190):** build and freeze Data Infrastructure v2, which covers:
  - the P7-CP5e section-50 architecture;
  - window 2011-01 → 2017-12;
  - M2 timing;
  - SEC market-cap repair;
  - the verified identity extension;
  - the restatement guard.

  Infrastructure only; STOP before any H022 null or real evaluation.
- **Built:**
  - consolidated reference table `qr_data_v2*.py` (16 files, lzma + base85, loader v2-lzma-b85-1, table SHA-256 107b6b55…);
  - `qr_v2.py`;
  - host X998 (data-v1-pinned modules untouched);
  - `datafreeze_v2` (candidate manifest);
  - tests.

  33 project files. The 25–28 target is not reachable without dropping rule data.
- **Gate thresholds fixed before any output:** commit 43e26ec.
- **QuantConnect runs** (LEAN 18178 default, recorded; compliance accepted; 0 orders; aggregates only):
  - E998-01: export;
  - E998-02: independent repeat;
  - E998-03: truncated at 2013-12-31;
  - E998-04: export + in-cloud synthetic power study.
- **Results:**
  - PIT audit 0 in every run;
  - determinism: every digest identical;
  - truncation: all 35 shared months identical (the whole-year 2013 digest differs only because a run ending 2013-12-31 never reaches its December review; analysis corrected);
  - splits 223/224;
  - P7-CP5e residuals reproduced exactly (69% recovery, +0.79-point gap, 98.4% agreement);
  - fully scored stocks a month 304–728;
  - 80+ 7.07 a month;
  - mechanics: 46.6 orders a year, 0.79% cost, 69% utilisation, no rule violations;
  - restatement guard blocked 114 reports (0.16%);
  - synthetic power essentially unchanged (main: 50% at IC 0.034, 80% at 0.049, false promotion 0.1%, synthetic c_IC 2.53).
- **Identity sanity check (owner item 7):**
  - 161 REJECT / no-identity securities, 3.4% → 6.9% of eligible stock-months a year (pre-set limit ≤ 3%: fail);
  - implied survivorship tilt 0.47 points (limit ≤ 1.0: pass);
  - survival 82.4% vs 87.5%.

  Material by the pre-set criteria → gate K fails.
- **Verdict:** NOT FROZEN — Data Infrastructure v2 failed one or more freeze gates. Every other gate (A–J, L–P) passes. Manifest written as an unpinned candidate.
- Old c_IC 2.390976216956 labelled DATA_V1_ONLY / UNUSED_ON_V2.
- No real return, IC, H022 gate or portfolio. No 2018–2021; Holdout untouched; nothing purchased.

**STOP:** awaiting the owner. Options:
1. accept the identity residual and freeze as built (recommended);
2. identity feasibility study;
3. close H022.

## 2026-10-10: P7-CP5g owner acceptance of identity residual — Data Infrastructure v2 FROZEN; STOP (D192, D193)

- **Owner (D192):** Option 1 of P7-CP5f item 56. The identity residual is accepted as an explicit **owner-approved exception to Gate K**:
  - 161 securities: 105 REJECT + 56 without an identity row;
  - 3.4% → 6.9% of eligible stock-months a year, so the pre-registered 3% criterion FAILED;
  - survivorship tilt +0.47 points, so the 1.0-point limit passed.

  Gate K stays recorded as FAILED under the original criterion. Nothing is relabelled, and no threshold, code, data or rule is changed.
- **Freeze:** the P7-CP5f candidate manifest (d09f20fc…) is finalised without regenerating any input.
  - Added: status "FROZEN — OWNER-APPROVED GATE K EXCEPTION", the exception record and the candidate hash.
  - Unchanged: file hashes, rules and the original gate results.
  - `MANIFEST_SHA256` = cf833f6f… pinned in `qresearch.datafreeze_v2`; tests updated.
- **CP5f evidence referenced, not recomputed:**
  - PIT 0; determinism and truncation pass; splits 223/224; compliance pass;
  - 90,370 stock-months; fully scored 304–728 a month; 80+ 7.07 a month;
  - synthetic power 50% IC 0.034 / 80% IC 0.049.
- No QuantConnect run; no E998 rerun. No real return, IC or null; old c_IC stays DATA_V1_ONLY / UNUSED_ON_V2. No 2018–2021; Holdout untouched; nothing purchased.

**Permanent record:** Data v2 did not technically pass every original freeze criterion. Gate K failed because the identity-affected population exceeded the pre-registered 3%-per-year incidence threshold. The owner knowingly accepts this residual without changing the threshold because the measured survivorship effect is only +0.47 percentage points, below the 1.0-point materiality bound, every PIT/integrity gate passed, and no real H022 result has yet been observed.

**STOP:** awaiting the owner on whether to authorise H022 on Data v2:
1. canary;
2. 5,000 null worlds;
3. new c_IC pinned;
4. owner review;
5. one real evaluation.

## 2026-10-10: P7-CP6 H022 / Data v2 canary and null calibration — CALIBRATED; STOP (D194, D195, D196)

- **Owner (D194):** H022 on frozen Data v2, steps 1–3 only: canary, 5,000 null worlds, new c_IC pinned. No real evaluation.
- **Host S024 v1.0** (X999 = byte copy):
  - a subclass of the frozen X998 Data v2 host, uploaded byte-identically as `qr_x998.py` (= frozen manifest);
  - adds market caps, the raw open and the split × dividend multiplier;
  - H022 population / response / null / real / canary steps verbatim from S023 v1.1;
  - `qr_p7_pred` unchanged.
- **Canary E999-02: 25/25.**
  - Score side identical to frozen E998-01 in all 84 reviews; populations 163–585 a month; regimes identical.
  - Response timing: 0 violations; 120/120 fresh corporate-action recomputations agree.
  - Response and score invariance pass.
  - Null plumbing, Newey-West and the full G1–G4 procedure pass, on synthetic responses only.
  - PIT audit 0.
  - E999-01 had the same digests but did not export the PIT counters (24/25).
- **Panel digest** 09b1de41… pinned before the nulls.
- **Null runs:**
  - E024-01..05: 5,000/5,000 worlds, seeds exact, identical panel, LEAN 18178, 0 orders.
  - E024-06 rerun of seeds 1–25: identical.
- **New Data-v2 c_IC = 2.3798883324991866**, the 50th largest of 5,000 null t_IC (same rule as Data v1; floor not binding). Pinned in `qresearch.p7pred_v2` and merged (PR #75) before any real run.
- **Null t_IC:** mean 0.181, SD 0.937, p95 1.724, p99 2.377, max 4.354.
- **Gate passes:** G1 49, G2 1,231, G3 255, G4 279; all four 5, so false promotion 0.10%. Data v1: c_IC 2.391, false promotion 0.14%.
- No unpermuted real H022 statistic exists. Old c_IC stays DATA_V1_ONLY. No 2018–2021; Holdout untouched; nothing purchased.

**STOP:** awaiting the owner. Options:
- authorise exactly one real H022 evaluation (E024-07, pinned provenance);
- keep H022 sealed.

## 2026-10-11: P7-CP7 — the one real H022 evaluation on Data v2 (E024-07): NOT QUALIFIED; STOP (D197, D198)

- **Owner (D197, committed before the run):** exactly one real H022 evaluation on frozen Data v2 with the pinned c_IC 2.3798883324991866 and panel digest 09b1de41….
- **Pre-run gate:** 17/17 pass.
- **E024-07:** LEAN 18178, 0 orders, panel reproduced exactly, PIT audit 0.
- **Result: NOT QUALIFIED, all four gates fail.**
  - G1: mean IC 0.0076, t_IC 0.477 vs c 2.380 (null percentile 63%).
  - G2: 80+ group −12.6% a year vs the population (floor +3%).
  - G3: quintile Spearman −0.40, Q5 − Q1 −1.3% a year.
  - G4: second-half IC −0.0002; largest block 111%.
- **Non-gating diagnostics all null:** sector-demeaned t 0.87; Fama-MacBeth increment beyond momentum and size t 0.49; 2-month t 0.09; 3-month t −0.23.
- No rerun, no tuning, no portfolio, no 2018–2021; Holdout untouched; nothing purchased.

**STOP:** awaiting the owner. Recommendation: close H022 as Rejected; Phase 7 No Production Candidate Found.

## 2026-10-11: Phase 8 — H023 Score v2 weight optimisation: pre-registration frozen (D199)

- **Owner (D199):** H022 / Score v1 stays permanently Rejected exactly as tested. H023 is a new hypothesis that re-weights only the three frozen Score v1 layers (Technical /40, Fundamental /45, Sector /15).
- **2011–2017 is now TRAINING / DEVELOPMENT data for H023.** 2018–2021 is sealed as its first external validation; the Holdout stays locked.
- **Frozen before any run:**
  - spec `research/phase8/H023_spec.md`;
  - hypothesis `research/hypotheses/H023.md`;
  - grid module `qr_h023`;
  - host S025 (a subclass of the pinned S024);
  - pins `qresearch.p8h023`.
- **The search:**
  - grid of 92 weightings; control 40/45/15;
  - 5,000-world optimiser null (whole grid per world), giving c_SEARCH;
  - filters D1–D5;
  - robust plateau of ≥ 4 configurations, then the medoid selection rule;
  - walk-forward diagnostic.
- **Pre-registered 2018–2021 validation:** gates V1–V4. Prerequisite: an owner-approved extension of the Data v2 reference layers to 2018–2021.
- **Verification:** the grid statistics equal the frozen H022 procedure to < 1e-12 for every configuration, in real and null worlds. A null world costs about 0.1 s, so 5,000 worlds are feasible.
- **Next:** canary E025-01.

## 2026-10-11: P8-CP1 — H023 Score v2 weight optimisation: NO ROBUST SCORE V2 CANDIDATE; STOP (D200)

- **Canary E025-01: 16/16.** The panel equals the pinned H022 panel, the layer subtotals equal Score v1, and the grid equals the frozen procedure.
- **Optimiser null E025-02..06: 5,000 worlds; rerun E025-07 identical.** Every control column equals the H022 null world of the same seed.
- **c_SEARCH = 2.9226**, pinned and merged before the real search (PR #79). The full-procedure false-promotion rate is 0.54%.
- **Real search E025-08 (once): no candidate.**
  - The best configuration is 80/10/10 with t_IC 0.97 (null p = 0.41).
  - No configuration passes D1, D3 or D4.
  - There is no robust plateau: only 7 configurations meet the base conditions, in 4 regions of at most 3.
  - The control 40/45/15 equals H022 exactly.
- **Surface:** ranking strength rises with Technical weight and falls with Fundamental weight; Sector weight does not matter. No configuration has monotone quintiles or stable blocks, and 2016 is negative throughout.
- **Walk-forward:** pseudo-out-of-sample IC 0.001 (t 0.05). The fold selections do not cluster.
- **Boundary flag:** wT = 80, reported only; no expanded search is recommended.
- Nothing was frozen; 2018–2021 and the Holdout are untouched; no portfolio; nothing purchased.

**STOP:** awaiting the owner. Recommendation: close H023 / Phase 8 as No Production Candidate Found.

## 2026-10-11: Phase 9 — H024 Feature Redesign and Selection: pre-registration frozen (D201)

- **Owner (D201):** H023 closed as NO ROBUST SCORE V2 CANDIDATE; H022 stays rejected. New hypothesis H024: redesign the score's feature composition under a tight pre-registered search. 2011–2017 is development data; 2018–2021 and the Holdout stay sealed.
- **Inventory:** the eight Score v1 features were read from the frozen code (`research/phase9/P9_feature_inventory.md`).
- **Library (11 features, chosen without returns):** momentum, low volatility, gross profitability, accruals, book-to-market, asset growth, 1-month reversal, cash profitability, 52-week-high proximity, cash-flow yield, equity/assets.
  - Revenue growth is excluded because its direction is ambiguous.
  - Sector breadth and trend state are removed by the 500-model budget rule.
- **Models:** up to 415, with 2–4 features each, at most one per family, and equal-weighted percentiles.
- **Procedure:** 5,000 null worlds for feature-level and model-level thresholds; gates D1–D6 and the neighbourhood rule; deterministic selection; walk-forward diagnostic.
- **Disclosure recorded:** 2018–2021 is not pristine for low volatility (H005 was validated there) or for GP/A, trend and earnings ideas (Phase 2 developed on 2010–2021).
- **Verification:** the module and host tests pass; every column equals the frozen H022 procedure.
- **Next:** canary E026-01.

## 2026-10-11: H024 canary E026-01 (D202)

- **Canary: 16/17.**
  - All 11 features retained: coverage ≥ 99.9%.
  - 0 recomputation mismatches.
  - No redundancy links: the largest cross-family median |ρ| is 0.58.
  - **415 models**; the library hash and the population digest (34,831 stock-months) are pinned.
- **Check 6 (explained):** QuantConnect's data snapshot changed today between 07:58Z and 08:10Z. Score v1 rows outside the analysed population differ for 12 reviews in 2011. The pinned H022 panel and every population used by H022, H023 and H024 reproduce exactly, so no statistic is affected.
- **Next:** null runs E026-02..07.

## 2026-10-11: P9-CP1 — H024 Feature Redesign and Selection: NO ROBUST H024 FEATURE MODEL; STOP (D203)

- **Null E026-02..06: 5,000 worlds; rerun identical.** c_FEATURE = 3.45 and c_MODEL = 4.37, pinned and merged (PR #82) before the real search.
- **Real search E026-08, once:**
  - best model CBOP + CFP + HI52 + REV1M, t 2.48 (null p 0.35);
  - best feature LOWVOL, t 1.24;
  - no model passes D1, so none qualifies and nothing is frozen.
- **Walk-forward:** no strict fold candidate; pseudo-out-of-sample IC −0.001.
- **Controls:** Score v1 t 0.47; H023 80/10/10 t 0.97.
- No 2018–2021, Holdout untouched, no portfolio, nothing purchased.

**STOP:** awaiting the owner. Recommendation: close H024 / Phase 9 as No Production Candidate Found.


## 2026-10-11: Phase 10 — H025 Insider Cluster Buying pre-registered and built (D204)

- **Owner (D204):** H024 / Phase 9 closed; H025 approved. Event study on SEC Form 4 filings, not a score.
- **Definition (frozen before any count):**
  - Who: ≥ 2 distinct directors or officers.
  - What: open-market purchases (code P) of common stock, direct ownership; each ≥ $25K, together ≥ $100K.
  - When: inside 10 calendar days of SEC acceptance time; online trigger; 20-session issuer cooldown.
  - Universe and identity: frozen Data v2 universe, verified identity.
  - Trade window: next-open entry, 20-session hold.
  - Statistic: monthly excess vs SPY, Newey-West lag 2; 5,000 matched null worlds.
- **SEC ledger:** 29 quarterly SEC data sets + 53,567 EDGAR acceptance timestamps, 0 missing; 3,587 pre-universe clusters; brute-force rebuild identical.

## 2026-10-11: P10-CP1 — H025 REJECTED — NO ROBUST INSIDER-CLUSTER EDGE; STOP (D205)

- **Audit (E027-01/02, identical):** 605 events in the ≥ $2B universe, 59–110 a year → sample gate PASS. Ledger hash pinned.
- **Canary (E027-03):** 17/17.
- **Null (E027-04/05, identical):** c_EVENT = 2.47, pinned and merged (PR #84) before the real run.
- **Real (E027-06, once):**
  - t −0.93; mean excess +0.07% per 20 sessions; median +0.02%; win 50.4%.
  - 2011–14 −0.69%; 2015–17 +0.75%.
  - G1, G2 and G4 fail; null p 0.93.
- **Controls:** matched random stocks +0.30%; single-insider purchases +0.38%. No diagnostic is robust.
- No 2018–2021, Holdout untouched, no portfolio, nothing purchased.

**STOP:** awaiting the owner. Recommendation: close H025 / Phase 10 as Rejected.


## 2026-10-11: Phase 11 — H026 Learned Stock Score Portfolio: REJECTED; STOP (D206–D210)

- **Owner (D206):** H025 / Phase 10 closed. H026 approved: Ridge over the 11 H024 features → Top-15 portfolio → beat SPY on terminal wealth. 2011–2021 is H026 development data; the Holdout stays sealed.
- **Data v2.1 (D207):** Data v2 extended through 2021-12-31 with the same rules (X801 runs E801-01..04).
  - Point-in-time audit 0; determinism, future invariance and truncation all pass.
  - 2011–2017 eligibility matches 84/84 reviews; the H022 population differs by −0.05% (restatement guard).
  - One own-gate specification error (NEW_YEARS_MAPPING) is kept as FAILED and disclosed.
- **Canary E028-01 (D208):** 13/13. Coverage ≥ 99.8%; label purge and timing exact; feature panel pinned.
- **Null (D209):** 5,000 full-pipeline worlds; the rerun of seeds 1–25 is identical. c_WEALTH = 0.2245 was pinned and merged (PR #86) before the real run.
- **Real run E028-05, once (D210):**
  - wealth $311,397 vs SPY $262,325 (1.19×), CAGR +2.85 points a year, with lower volatility and drawdown;
  - **S_WEALTH 0.171 < c_WEALTH 0.225, so D1 fails** (p = 0.020);
  - **D3 fails:** ahead of SPY in 3 of 7 years, with 2015–2017 negative;
  - D2, D4 and D5 pass.
- **Status:** H026 REJECTED — LEARNED SCORE PORTFOLIO DOES NOT ROBUSTLY BEAT SPY. No candidate frozen; Holdout untouched; nothing purchased.

**STOP:** awaiting the owner. Recommendation: close H026 / Phase 11 as REJECTED.


## 2026-10-11: P11-CP2 — H026 post-mortem: H026 REMAINS REJECTED; H027 feasibility B; STOP (D211, D212)

- **Owner (D211):** H026's REJECTED result accepted as recorded. A descriptive post-mortem only, from committed artifacts: no rerun, no tuning, no new null worlds, no QuantConnect run, no Holdout.
- **Where the $49K came from:** market declines.
  - Log-relative +0.202 over the 24 SPY-down months, −0.030 over the 60 up months.
  - March 2020 = 64% of S_WEALTH; 2018 + 2020 = 78% of the positive yearly total.
  - Beta 0.80, down-capture 0.78.
- **What Ridge learned:** a stable shrunk defensive tilt from 2016 (λ = 100 at the grid boundary).
  - Low volatility, low book-to-market, high profitability, near the 52-week high.
  - The same formula lost in 2016, 2019 and 2021 and won in 2017, 2018 and 2020.
- **Null comparison** (existing worlds, post-hoc only):
  - wealth at the 98th percentile;
  - volatility below all 5,000 worlds and MaxDD shallower than 4,999 (a low-volatility tilt the permutation null cannot produce);
  - 0 of the 99 richer null worlds had as shallow a drawdown.
- **H027 feasibility: B** (interesting but concentrated; a defensive exposure, with selection skill beyond it unproven). Three concepts listed, none chosen.
- **Not computed:** security-, sector- and exposure-level items (not exported by E028-05).
- **Governance:** D207 is still Claude's own judgement, not an owner exception (unresolved).

**STOP:** awaiting the owner — D207 decision; H027 direction or close Phase 11; optional non-trading export run (needs memory work first).



## 2026-10-12: Phase 12 — H027 Exposure-Controlled Learned Stock Score: REJECTED; STOP (D213–D216)

- **Owner (D213):**
  - Data v2.1 frozen as an OWNER-APPROVED EXCEPTION; NEW_YEARS_MAPPING still failed as written; the manifest is unchanged.
  - H026 permanently rejected; no H026 export run.
  - H027 approved: the frozen H026 procedure, tested against a LOWVOL-conditional null and the LV15_CONTROL, with gates A1–A6.
- **Infrastructure:**
  - Host S029 (a subclass of the pinned S028) with memory reduction.
  - Peak memory 7.7–7.8 GB vs H026's 7.9–8.2 GB; the owner's 6.5 GB target was not met.
- **Canary E029-01 (D214): 17/17.**
  - Exact equivalence with H026: panels equal the pins; H026 null worlds 1–25 equal E028-04.
  - LOWVOL never moves and the other ten features move as one donor vector.
  - LV15 picks are verified.
  - Synthetic A (LOWVOL only) does not beat the null; B (LOWVOL + GPA) beats it in every replicate.
- **Null (D215):** 5,000 conditional worlds; the rerun of seeds 1–25 is exact (coefficients included).
  - Adequacy: ADEQUATE. Worlds at least as defensive: volatility 98.7%, MaxDD 20%, beta 96.4%, down-capture 87.6%.
  - c_WEALTH_CONDITIONAL = 0.0577, pinned and merged (PR #89) before the real run.
- **Real run E029-05 (D216):** H026 reproduced exactly.
  - A1 PASS (S 0.171, p 0.0006); A2, A3, A5 and A6 PASS.
  - **A4 FAIL:** behind LV15 over 2015–2017 (−0.058), although ahead in 5 of 7 years and +0.405 over 2018–2021.
  - LV15 itself lost to SPY (−2.8 points a year).
  - LOWVOL-factor alpha t = 0.90; sector-neutral t = 1.05.
- **Status:** H027 REJECTED — NO ROBUST STOCK-SELECTION EDGE BEYOND LOWVOL EXPOSURE. Development evidence only; nothing frozen; Holdout untouched; nothing purchased.

**STOP:** awaiting the owner. Recommendation: close H027 / Phase 12 as REJECTED.


## 2026-10-12: Phase 13 — H028 Fixed Strong Shrinkage Learned Stock Score: REJECTED; STOP (D217–D220)

- **Owner (D217):** H027 closed as REJECTED. H028 approved as explicitly post-hoc development research: the frozen H027 architecture with λ = 100 fixed for every Ridge fit (no λ selection or search). It is the final λ-specific experiment for this architecture.
- **Infrastructure:**
  - Host S030 is a subclass of the pinned S029, plus `qr_h028`, which has three parts:
    - the fixed-λ world;
    - an exact replica of the portfolio simulation;
    - the 2016–2021 equality analysis.
  - 50 project files (the limit); peak memory 7.7–7.8 GB.
- **Canary E030-01 (D218): 18/18.**
  - λ = 100 in all 7 fits, with no inner selection.
  - The real H027 is reproduced bit for bit through the fixed path.
  - The H027 null rows 1–25 match the committed run.
  - The 2016–2021 tolerance was calibrated on 100 null pairs, all exact, and pinned before any null world.
  - Synthetic A does not beat the null; B does.
- **Null (D219):** 5,000 λ-100 conditional worlds; the rerun of seeds 1–25 is exact.
  - Adequacy step 1: ADEQUATE.
  - c_WEALTH_H028 = 0.0561, pinned and merged (PR #91) before the real run.
- **Real run E030-05 (D220):**
  - H027 is reproduced exactly; 2016–2021 is identical in coefficients, scores and holdings, with return differences within tolerance; adequacy step 2 passes.
  - B1 PASS (S 0.224, p 0.0004); B2, B3, B5 and B6 PASS (wealth $328,295 = 1.25× SPY).
  - **B4 FAIL:** behind LV15 over 2015–2017 (−0.006). λ = 100 improved 2015 vs LV15 from −0.171 to −0.126, and 2016 (−0.052) was already λ = 100.
- **Status:** H028 REJECTED — FIXED STRONG SHRINKAGE DOES NOT ROBUSTLY SOLVE THE TEMPORAL-STABILITY PROBLEM. Development evidence only; nothing frozen; Holdout untouched; nothing purchased.

**STOP:** awaiting the owner. Recommendation: close H028 / Phase 13 as REJECTED; no H029 without explicit instruction.


## 2026-10-12: P13-CP2 — H028 2015–2016 descriptive post-mortem: POST-MORTEM C; STOP (D221, D222)

- **Owner (D221):** descriptive post-mortem only, from committed artifacts. H028 stays REJECTED; no H029; no QuantConnect run; no Holdout.
- **2015 (broad shortfall):**
  - H028 −3.5% vs LV15 +9.5%; behind in 10 of 12 months, in both rising and falling months.
  - LV15 had better up-capture *and* down-capture.
  - Low-volatility stocks broadly outperformed that year.
  - λ = 100 recovered only about a quarter of H027's 2015 gap (−0.171 → −0.126): downside improved, upside participation did not.
- **2016 (down-month shortfall; λ already 100):**
  - H028 +6.2% vs LV15 +11.8%; level with LV15 in the 8 up months.
  - All of the gap came in the 4 down months (October 2016 = 58%); down-capture 0.90 vs 0.07.
  - Not a low-volatility rally: the lowest-volatility quintile lagged in 2016.
- **Costs:** at most about 7–15% of the gaps.
- **2016 vs 2017:** the same model (cosine 0.91) lost with down months and won with none.
- **Not available:** holdings, feature, sector and stock-level items, because the hosts export aggregates only.
- **Clarification:** P13-CP1's "reproduced H027 exactly" applies to the in-run H027 recomputation. The H028 2016–2021 coefficients, scores and holdings matched H027, with small, documented path differences in returns.
- **Status:** POST-MORTEM C — 2015 AND 2016 FAILED FOR MATERIALLY DIFFERENT REASONS. H028 REMAINS REJECTED; Holdout sealed.

**STOP:** awaiting the owner. Recommendation: close Phase 13 and the learned-score line.


## 2026-10-12: P13-CP3 — H028 long-horizon synthetic path robustness: HIGHLY SENSITIVE TO PATH / REGIME COMPOSITION; STOP (D223, D224)

- **Owner (D223):** a descriptive bootstrap of the 84 observed 2015–2021 paired monthly returns (H028, LV15, SPY). H028 stays REJECTED; no QuantConnect run; no Holdout.
- **Method:** fixed and committed before any aggregate. The terminal liquidation is excluded by construction (month-end marks are pre-liquidation).
- **Primary (complete-year blocks, 10,000 × 30 years):**
  - H028 > SPY in 78 / 89 / 97 / 99% of paths at 5 / 10 / 20 / 30 years; > LV15 in 88 / 95 / 99 / 99.8%.
  - Typical path: a 5-year losing streak against SPY, a −21% relative drawdown, and 7.6 years below a previous relative high.
- **12- and 24-month blocks:** more favourable.
- **Leave-one-year-out:** 2018 (82%) and 2020 (88%) matter most.
- **Without 2018 and 2020:** H028 beats SPY in only 9% of 30-year paths, but LV15 in 94%.
- **7-year resampling interval of the observed edge:** vs SPY −2.4% to +9.3% a year; vs LV15 −2.2% to +13.2%.
- **Status:** SYNTHETIC ROBUSTNESS RESULT — H028 IS HIGHLY SENSITIVE TO PATH / REGIME COMPOSITION (pre-registered rule). FORMAL STATUS: H028 REJECTED. Seeds 1–100 reproduced exactly.

**STOP:** awaiting the owner. Recommendation: close Phase 13 and the learned-score line.

## 2026-10-12: P13-CP4 — H028 30-year objective alignment: PARTIALLY OBJECTIVE-ALIGNED; H028 REJECTED; STOP (D225, D226)

- **Owner (D225):** compare H028's observed behaviour with the clarified 30-year objective (keep up in rising markets, lose less in falling markets, compound to more wealth than SPY). Descriptive only; H028 stays REJECTED; the objective applies prospectively from H029.
- **Method:** rules committed before any statistic (006f417). Inputs are the committed 2015–2021 panel and the P13-CP3 outputs. The P13-CP3 primary worlds were regenerated with an identical digest, only for patience statistics in winning paths.
- **Rising markets:** up-capture 0.97 (near-full), but 0.87 in SPY's strongest months; H028 beat SPY in half of the up months.
- **Falling markets:** down-capture 0.69, and 0.65 in falls of 5% or more.
- **Where the edge comes from:** down months supplied 127% of the relative log-wealth and up months −27%; March 2020 alone supplied 49%.
- **Without 2018 and 2020:** −1.4 points a year vs SPY; up / down capture 0.90 / 0.81.
- **Rolling windows ahead of SPY:** 12-month 58%, 36-month 92%, 60-month 100%, but every 60-month window contains 2018.
- **Synthetic:** H028 beats SPY in 98.7% of 30-year paths. Winning paths typically have a 5-year losing streak and 7.5 years below a previous relative high. Without 2018 and 2020: 9.3%.
- **Dimensions:** A ACCEPTABLE, B STRONG, C STRONG, D ACCEPTABLE, E WEAK, F WEAK → **PARTIALLY OBJECTIVE-ALIGNED** (pattern C: edge from the 2018 and 2020 episodes).
- **Missing capability:** regime-independent relative return and temporal consistency.
- **Prospective standard for H029 onward:** recorded (D226).

**STOP:** awaiting the owner. Recommendation: close Phase 13 and the learned-score line, or authorise a design-only H029 pre-registration under the new standard.

## 2026-10-12: P14-CP1 — H029 Business Improvement data-feasibility audit: PASS (data quality only); STOP (D227, D228)

- **Owner (D227):** audit whether frozen Data v2.1 supports eight Business Improvement families (F1–F8). No returns or performance of any kind; H028 frozen; Holdout sealed.
- **Method:**
  - specification pre-registered before any data (d2b6b54); analysis committed before results (5cd5ef3);
  - ONE infrastructure run, E802-01 (X802 = frozen X801 + qr_h029a; 0 orders; aggregates only);
  - universes identical to E028-01 (131/131); all PIT checks 0.
- **Classes:**
  - **B:** F1 (same-quarter YoY acceleration, 85.8%), F2 (73.8%), F4 (OCF/assets, 80.9%), F5 (ROA change, 78.7%), F7 (SEC share-count issuance, 83.7%), F8 (asset turnover, 76.8%);
  - **C:** F3 (operating income not approved; 37 months < 50%) and F6 (total debt not approved; zero = missing; no cash field).
- **Why no A:** coverage 13–20 points lower in 2011–2014; gross profit / OCF / NI are not field-guarded against restatements.
- **Gate:** 6 of 8 A/B; combined score coverage 81.6% (≥ 3 of 6) / 80.1% (≥ 4) / 75.7% (≥ 5); all 6 required = 64.6% → **H029 DATA FEASIBILITY — PASS**.
- **Signal properties:**
  - the six are largely non-redundant (max ρ 0.39) and distinct from H028's features (max 0.47, F8 vs asset growth; LOWVOL ≈ 0, F7 +0.18);
  - staleness median 50 days; quarterly signals.
- This is a data-quality result only. No evidence on H029 profitability.

**STOP:** awaiting the owner's decisions for H029-B (families, forms, missing-data rule, universe, 2011–2014 handling, outlier rules, host).

## 2026-10-12: P14-CP2 — Fundamental PIT Data v3 hardening: DATA V3 PASS; Data v3 frozen; continuing to H029 / H030 pre-registration (D229, D230)

**Owner (D229):** a new immutable Data v3 layer for H029 only; Data v2.1 and H028 are untouched.
- **Method:**
  - spec pre-registered before any build (a43d706);
  - the guard-v3 table and the SEC validation reference were built offline from public SEC data (a second rebuild was byte-identical);
  - the analysis was committed before the run (c5b3b21);
  - ONE audit run, E803-01 (X803 = frozen X801 + qr_v3; 0 orders; aggregates only; LEAN 18179, the new default build; universes = E802-01, 131/131).
- **Guard v3:**
  - 45,450 restated SEC values (> 1.5%) of quarterly revenue, gross profit, net income, OCF and total assets;
  - 1,018 of 116,639 fed vendor versions (0.9%) carried a not-yet-public restated value and are excluded from the H029 v3 view (their periods are removed; nothing imputed).
- **SEC validation** (275 stratified registrants), share of percentile moves > 0.20:
  - F1 3.5%, F2 1.9%, F4 1.5%, F5 0.2%, F8 1.7%;
  - composite 4.8% (2011–2014: 6.5%);
  - all ≤ 5% → PASS.
- **F7 split test:** disagreement 6.4% in split windows vs 2.7% without (limit +5 points) → PASS.
- **Coverage:** ≥ 5 of 6 median 76.1% (2015–2021: 77.6%). Families 74–86%.
- **PIT checks:** all 0.
- **Outcome:** all six families usable → **DATA V3 PASS**. Manifest `data_freeze_v3.json` (601d0062…) pinned.
- **Next (owner run order, no stop):** H029 / H030 pre-registration. The H029 host must first reproduce H026's panels and H028's committed result on the current QuantConnect build.

## 2026-10-13: P14-CP3a — H029 / H030: STOP — NULL INADEQUATE before any threshold or real result (D231, D232)

- **Pre-registration:** H029 / H030 frozen before any value (7bdbcf7). Standalone host S031, with the frozen S028 / S029 methods verbatim.
- **Canary E031-01:** PASS 17/17. Frozen H028 ($328,294.908) and LV15 reproduced exactly on LEAN 18179. Synthetic A / B behave as designed.
- **Null:** 5,000 worlds (E031-02 / 03), all finite. Seeds 1–25 rerun (E031-04) identical.
- **Adequacy (pre-registered, score-only):**
  - H029's real Top-15 selections are more sector-concentrated (HHI 0.163) than the null allows (99.5th percentile 0.160; reached by only 2 of 5,000 worlds) → **STOP — H029/H030 NULL INADEQUATE**;
  - all other measures pass.
- **Not done:** thresholds not pinned; no real run; no H029 / H030 performance computed.
- **Owner options:** sector-stratified tether (recommended), exception, or close. Holdout sealed.

## 2026-10-13: P14-CP3b — H029 / H030 sector-stratified null amendment (D233)

- **Owner decision (D233):** approved option 1 of P14-CP3a, before any real H029 / H030 performance existed.
- **Amendment 1** (`research/phase14/H029_H030_amendment1_sector_null.md`): the donor of a six-signal vector must come from the recipient's FF12 sector at the review. Nothing else changes (H029, H030, H028, Data v3, gates, costs, mechanics, adequacy rule).
- **Status:** an owner-approved pre-performance methodological amendment following a pre-registered adequacy failure. Significance under this null = within-sector / conditional stock selection; sector-allocation alpha is not tested.
- **Committed before any run:** S031 v1.1 (canary sector checks: constructibility, same-sector donors, recipient sector / returns / eligibility / H028 unchanged; a within-sector synthetic B) and new run ids E031-06 (canary), E031-07 / 08 (null), E031-09 (rerun), E031-10 (real, only after pinned thresholds).
- **Records:** P14-CP3a and its runs E031-01..04 stay the permanent record; 0.2696 / 0.0059 are permanently invalid.

## 2026-10-13: P14-CP3b — sector-stratified null ALSO INADEQUATE → H029 / H030 BLOCKED (D234)

- **Canary E031-06:** PASS 23/23 (same-sector donors, no self-matches, recipients unchanged; synthetic A null, within-sector synthetic B p = 1/51).
- **Null:** 5,000 sector-stratified worlds (E031-07 / 08); seeds 1–25 rerun (E031-09) identical.
- **Adequacy (unchanged rule):**
  - sector concentration is now matched by construction;
  - H029's real Top-15 turns over fewer names (0.357 a month) than every one of the 5,000 sector-null worlds (minimum 0.362) → **H029/H030 BLOCKED — SECTOR-STRATIFIED NULL ALSO INADEQUATE**.
- **Not done:** no thresholds computed or pinned; no real run; no H029 / H030 performance exists. No third null designed.
- **Recommendation to the owner:** close H029 / H030 as not evaluable. Holdout sealed.

## 2026-10-13: P14-CP4 — H029 structural turnover post-mortem → TURNOVER POST-MORTEM B (D235)

- **Scope:** structural only. Committed artifacts only; no return read, no QuantConnect run, Holdout sealed.
- **Finding:** the sector null is an exact relabelling of the real selection (proved, and verified with the frozen code on synthetic panels). Its turnover can differ from the real turnover only where a donor pair is re-formed.
- **Re-pairing rate:**
  - 5.3% of stocks get a new donor every month, almost all because the eligible universe changes;
  - P14-CP3b's 99.85% "persistence" counted only pairs whose donor was still eligible.
- **Size:** re-pairing alone predicts about 92% of the 0.016 turnover gap. The sector cap is ruled out. H029's own quarterly persistence is natural, and the null carries it except at re-pairings.
- **Plain English:** the real H029 replaces 5.36 names a month vs the null median of 5.60, about 3 names a year.
- **Not available:** the month-level and per-stock items (only aggregates were exported).
- **Status:** no bug. H029 / H030 remain BLOCKED; awaiting the owner (close, or a design-only third-null review).

## 2026-10-13: P14-CP5 — third-null design review (design only) → one preferred design (D236)

- **Scope:** design only. No code, no QuantConnect run, no null world, no returns; Holdout sealed. H029 / H030 remain BLOCKED.
- **Core result:** any null in which each stock *points to* another company's current vector every month (Null #2) must hand vectors to new owners whenever stocks enter or leave the universe. That is the CP4 artifact. Avoiding it offline would require knowing future exits, which are largely price-driven.
- **Candidates:** A, B1, C, D and E rejected.
- **Recommended: B2, the Event-Copy Relay.**
  - A stock's six-signal vector is rewritten only at its own events (filing update, entry, sector change), using a same-sector, same-review vector chosen by rank-coupling.
  - Between events the copy is held, so other stocks' churn cannot move it.
- **Proposed adequacy:**
  - existing gates plus continuing-name persistence gates P1 and P2;
  - a pre-registered, score-only rule deciding whether total H029 turnover stays a gate (exits and entries are partly price-driven);
  - an anti-fork rule (no Null #4).
- **Status:** awaiting the six owner approvals in P14-CP5 item 44.

## 2026-10-13: P14-CP6a — Null #3 (B2) synthetic feasibility → STOP before any real-data world (D237)

- **Owner approval (D237):** B2 approved with amendments (cross-sectional gates S1–S4; fallback ≤ 5% with reporting; q rule for G-TURN-29; P1 / P2; anti-fork rule).
- **Built:** Amendment 2 written (now marked DRAFT — NOT FROZEN); Null #3 implemented offline in `qr_h029n3` with guarantee tests (all pass).
- **Synthetic feasibility study** (no market data, no returns):
  - The panels are calibrated to the H029 universe; the frozen Null #2 reproduces its real gap of +0.016.
  - **B2 as approved changes 0.10–0.15 more names a month than a no-signal real selection.** A continuation refinement is also far off.
  - In every realistic panel, the real value lies below every null world.
- **Why:** rank coupling cascades under churn; off-cycle events become full replacements; continuing paths still change owner.
- **Also:** even Null #2 fails the turnover rule in no-signal panels, so these adequacy failures say nothing about H029.
- **Not done:** no QuantConnect run, no pin, no worlds, no thresholds, no returns; Holdout sealed.
- **Recommendation to the owner:** close H029 / H030 as NOT EVALUABLE.

## 2026-10-13: P13-CP5 — H028 conditional-null structural audit → FAIL / structurally suspect (D238)

- **Scope:** audit of the already-rejected H028 only. Synthetic panels, frozen code unchanged, committed structural fields only. No QuantConnect run, no real H028 performance, no new null; Holdout sealed; H029 / H030 untouched.
- **Mechanism:** the H028 null uses the same pointer tether as H029 Null #2, for the ten non-LOWVOL features (YES). On the real population about 17.6% of recipient-months re-pair every review (about 84 of 475 stocks), 3.3 times H029's rate.
- **Synthetic audit** (pre-registered; Amendment 1 before results): no-signal panels calibrated to the real population; frozen null + λ = 100 pipeline; S2 5 × 200 worlds per regime, S1 / S3 / S4 / S5 3 × 100.
  - Score-rank persistence fails the rule: real above the null band in 3 of 5 moderate seeds → **B, structurally suspect**. The first wording (both regimes) would have given C.
  - With coefficients fixed: null turnover +0.02 to +0.08 names a month at realistic churn, 0 without churn, +0.05 to +0.11 at double churn.
  - LOWVOL anchoring helps only about 20% on rank instability; the sector cap is not material; refitting masks the effect rather than amplifying it.
  - Extra null cost is about 0.5–2.5% of final wealth.
- **Committed artifacts:** null turnover / trades / costs NOT AVAILABLE. Null coefficients for seeds 1–25 are stable (cosine 0.96).
- **Consequence:** H028 remains REJECTED; its p ≈ 0.0004 is no longer reliable evidence of stock-selection alpha. No corrected p-value, no replacement null.
- **Status:** STOPPED awaiting the owner (recommendation: close Phase 13 / the learned-score line).

## 2026-10-18: P13-CP6 — H028 repaired null, synthetic validation only → B, R1 not feasible (D239)

- **Scope:** synthetic panels and offline code only. No real-data run, no QuantConnect run, no H028 holdings or returns; Holdout untouched; H028 unchanged.
- **Built:**
  - a synthetic generator (`qresearch.r1synth`);
  - an H028-style portfolio, matching methods M1–M4, twin worlds in Mode A (controlled cost schedule) and Mode B (investable), and R3 (`qresearch.r1twin`);
  - tests: exact self-match identity in both modes, accounting, truncation, matching rules.
- **Feasibility gate failed** (development fixture):
  - an H028-like Top-15 sits in the joint tail of LOWVOL, growth and profitability, so matched twins are always less extreme;
  - no method reaches |SMD| < 0.10 with credible coverage;
  - a 4× larger universe raises coverage but not balance;
  - so **R1 is not feasible at the current universe size**, and the problem is structural for concentrated portfolios.
- **Final synthetic validation not run:** no method could be frozen.
- **R3 synthetic diagnostic:** 14% false rejections at nominal 1% when growth and profitability are priced; power 29% against a strong signal. Not a substitute.
- **Classification:** **B — METHOD NOT VALIDATED.** H028 remains REJECTED.
- **Status:** STOPPED awaiting the owner (recommendation: close the H028 null-repair line).

## 2026-10-18: Phases 13–14 closed; research cycle complete — No Production Candidate Found; long-term roadmap (design only) (D240)

- **Owner decision D240** (verbatim in `docs/owner/2026-10-18_close_phases_13_14_roadmap.md`): closure approved, roadmap design approved, **no approval for further research**.
- **Closures:**
  - P13-CP6 accepted (B — METHOD NOT VALIDATED); H028 null-repair workstream closed; **H028 REJECTED** (unchanged).
  - **PHASE 13 — CLOSED — NO QUALIFIED PRODUCTION CANDIDATE.**
  - **PHASE 14 — CLOSED — H029/H030 NOT EVALUABLE** (historical BLOCKED; never REJECTED; no performance ever computed; no third null; Data v3 kept).
  - **Research cycle completed — No Production Candidate Found.**
- **Documents:**
  - closure checkpoint `docs/checkpoints/RC1_research_cycle_closure_phases_13_14.md`;
  - roadmap `docs/checkpoints/RM1_long_term_defensive_offensive_equity_roadmap.md` (design only);
  - status index `research/hypotheses/STATUS.md`; outcome notes in `H029.md` / `H030.md`.
- **Nothing run:** no backtest, null, synthetic experiment or QuantConnect run; nothing purchased; Holdout sealed; no frozen artifact changed.
- **Recommendation:** next, if any, is a synthetic-only inference-validity study for a signal-first OF-A design (alternative: desk-only pre-2010 data feasibility, needs a D124 revisit; stopping defensible).
- **Status:** STOPPED awaiting the owner.

## 2026-10-18: H028 Defensive Reference + Offensive Companion — long-horizon architecture design (D241)

- **Owner decision D241** (verbatim in `docs/owner/2026-10-18_h028_defensive_reference_offensive_companion.md`): DESIGN ONLY. H028 = "Frozen Defensive Research Reference" (descriptive; **still REJECTED**).
- **Checkpoint:** `docs/checkpoints/RM2_h028_defensive_reference_offensive_companion_design.md` (25 items).
- **Main findings:**
  - H028's development profile verified (E030-05), plus two fragility facts: Top-10 / Top-20 give S 0.095 / 0.062 vs 0.224; turnover about 7.5× a year.
  - Defensive value splits into a cheap profile (D-1, available from ETFs) and asymmetric capture beyond it (D-2), which only independent data could support; the Holdout can contradict but not confirm a modest D-2.
  - OF-A (accounting surprise) is distinct from H017 / H016 / H022–H028, but its acceleration form overlaps H029 F1, and the combination question repeats H030's; prior is low in large caps (Martineau 2022).
  - Recommended architecture to investigate first: C (offensive alone, signal-first) with E (defensive ETF + offensive) as the wrapper; H028 stays a reference comparator only.
- **Created:** selection ledger `research/longhorizon/SELECTION_LEDGER.md` (no entries).
- **Nothing run:** no backtest, synthetic experiment, null, QuantConnect run, H028 recalculation or purchase; Holdout sealed.
- **Status:** STOPPED awaiting the owner (recommended next: Stage B synthetic validation of the signal-inference method).

## 2026-10-18: Long-horizon Stage C — OF-A data and PIT feasibility audit (D242) → C as written (chain rule mis-specified)

- **Scope:** non-return offline audit; protocol frozen first (SHA-256 ff97789b…, commit df6e7fe); cache-only SEC data filed ≤ 2021-12-31; E981-01 point-in-time eligible universe; no QuantConnect run, no returns, no surprise values.
- **Coverage (non-financial eligible stock-months, 2013–2021):** C1 SUE-NI 79–85%, C2 SUE-REV 74–81%, C6 73–81%, C3 / C4 83–92%, C5 43–47% (gross profit untagged for about half). 13-quarter histories barely exist in 2011–2012 (14–52%).
- **Timing (42,620 quarter events):**
  - an Item 2.02 earnings release definitely preceded the 10-Q / 10-K in 85.8%; release → filing median 1 day;
  - release values are never numeric XBRL (0 / 41,369);
  - monthly reviews add a median 14 sessions, giving 18 sessions from release to the first monthly trade (daily decisions: 1).
- **Integrity:** PIT 0 violations; Q4 derived from FY − 9M in about 6%; recasts known before D in 21–24% of 13-quarter chains, later restatements 11–14% (guard v3 covers the fields).
- **Missingness not random:** leavers 64% and newcomers 37% vs 78–79% (C1).
- **Classification:** frozen result **C — NOT FEASIBLE**, driven by the fiscal-year-end label criterion (8–15% FAIL), which a post-hoc metadata diagnostic shows is mostly 52/53-week drift (criterion mis-specified). A residual 1.3% of chains is unexplained. Without that criterion: A; on the whole evidence: closer to B. Not reclassified.
- **Status:** STOPPED awaiting the owner (LH-CP1 §26).

## 2026-10-18: LH-CP2 — fiscal-calendar anomaly resolution (D243) → C — INSUFFICIENT EVIDENCE

- **Scope:** offline SEC metadata only, cut-off ≤ 2021-12-31 enforced inside the loaders and tested; protocol frozen first (SHA-256 f7cbac94…); no returns, signals, QuantConnect or Holdout. Stage C stays C — NOT FEASIBLE.
- **Reproduction:**
  - committed diagnostic bit-identical (unexplained 'other' shifts 890 / 69,182 unique chains = 1.29%);
  - Stage C coverage reproduced exactly;
  - the 1.3% is not on the Stage C gate's denominator (unique chains of all registrants vs repeated eligible stock-months, 14.4% changed).
- **The 1.3%:** 91% are SEC fiscal-year-end metadata inconsistencies with fully consistent fiscal-quarter labels (valid comparisons); about 2% label breaks; 6.5% unresolved. Fiscal labels themselves carry tagging errors.
- **Coverage effects:**
  - excluding demonstrably invalid histories keeps C1 / C2 / C6 ≥ 72% every year;
  - excluding histories with unknown labels (13.4%; mostly pre-XBRL quarters, some missing index rows) drops 2013–2014 below the floor and deepens the bias against leavers, entrants, young firms and utilities.
- **Frozen classification:** C — INSUFFICIENT EVIDENCE.
- **Proposed rule P** (period / label / transition based, no codes): a proposal only, coverage not computed.
- **Status:** STOPPED awaiting the owner (LH-CP2 §19).

## 2026-10-18: LH-CP3 — missing fiscal labels recovery & validation (D244) → B — PARTIAL RECOVERY

- **Scope:** SEC accounting-period metadata ≤ 2021-12-31 only; protocol frozen first (SHA-256 38d790e5…); rules frozen unchanged after development (9a72c5c8…); EDGAR header sample manifest committed before any request (ce09012e…). No returns, signals, QuantConnect, Stage B or Holdout. Stage C (C) and LH-CP2 (C) unchanged.
- **Part A (local):** of 3,796 unknown registrant-periods in the Stage C chains, 444 (11.7%) recovered and verified from local submissions; 3,288 are genuinely non-XBRL. Label-unknown C1-complete stock-months 13.36% → 11.43%.
- **Reconstruction R*:** form-sequence brackets (M-SEQ) and later XBRL comparatives (M-CMP) must agree.
- **Held-back validation** (1,911 registrants, 97,082 hidden-label trials, run once):
  - precision 99.95%, error upper bound 0.069% (V1 pass);
  - registrants with an error 1.93% vs 2.0% (V2 pass, narrow);
  - all 27 disagreements fall on mislabelled truth filings (Addendum 1, non-gating);
  - first-year XBRL tags no worse (V4 pass).
- **EDGAR headers:** 120 requests, all HTTP 200, no block; 1 of 94 usable genuine pre-XBRL filings disagrees with the header-implied quarter (V5 pass). Headers prove period, form and fiscal-year-end code, never the quarter label. A parser format defect was fixed and the headers re-parsed from cache with 0 extra requests.
- **Not testable:** whether genuine fiscal changes hidden in pre-XBRL stretches are caught (V3 insufficient: 10 held-back registrants, minimum 20).
- **Coverage:**
  - strictly verified histories meet the 70% floor in every year 2015–2021 (C1 / C2 / C6), not 2013–2014;
  - adding validated reconstructions lifts C1 above the floor every year, but C2 / C6 stay at 68.7% / 68.5% in 2013;
  - recovery reduces the bias of verified-only (entrants, leavers, 2013) but leaves young firms and energy behind.
- **Rule P:** its boundary tolerance would accept genuine re-basings (11 of 148 boundary cases); P-assume would accept 134 truly invalid held-back histories. It stays a proposal.
- **Frozen classification:** B — PARTIAL RECOVERY (resolution 88.4%; V3 insufficient).
- **Recommendation:** option 3, restrict to 2015–2021 verified histories (still needs an owner decision on Stage C).
- **Status:** STOPPED awaiting the owner (LH-CP3 §24).

## 2026-10-18: LH-CP4 — OF-A statistical feasibility and research-horizon assessment (D245) → B — UNDERPOWERED FOR MODEST EFFECTS

- **Owner decisions:**
  - LH-CP3 accepted as B;
  - a narrow, prospective Stage C exception: 2015–2021, verified L0 / L1 labels only, rule V (record `research/longhorizon/STAGE_C_EXCEPTION_D245.json`);
  - an analytical-only power assessment.
- **Earlier results unchanged:** LH-CP1 (C), LH-CP2 (C) and LH-CP3 (B).
- **Population** (metadata only; equals LH-CP3 Scenario A 2015–2021):
  - 83 monthly reviews, about 830 C1 stocks a month, coverage ≥ 72.7% every year, 1,500 securities;
  - signals refresh in 34% of stock-months, mostly in four earnings seasons (about 28 information bursts).
- **Power** (equations on labelled assumptions; no returns, no simulation):
  - main-case 80% MDE IC 0.031–0.041, about 2.6–7.4% a year top-quintile excess under a normal-theory conversion;
  - the illustrative +3% a year effect has 80% power only under favourable assumptions and about 10–46% under dependence, a 1% threshold, two hypotheses and a realistic-structure factor;
  - effects of +5% a year or more are usually detectable;
  - 3-month or earnings-season designs raise MDEs by about 75–80%.
- **Economics:** costs 0.4–2.5% a year for 15–30-name books at $100K; a full quintile is uneconomic; portfolio-level evidence over 7 years is weak (t 0.88 for 2% at 6% TE).
- **Classification:** B — UNDERPOWERED FOR MODEST EFFECTS.
- **Recommendation:** no Stage B now unless a large-effect objective is pre-declared; monthly decisions as the baseline, event-time / daily review as the timing to evaluate later.
- **Status:** STOPPED awaiting the owner (LH-CP4 §22).

## 2026-10-18: OC-CP1 — H028 offensive complement: existing-data candidate selection and test design (D246)

- **Scope:** design only; committed evidence only; no new returns, backtests, nulls, curves, models, purchases or Holdout; no new active hypothesis.
- **H028 weakness map** (verified):
  - low beta (0.76) / LOWVOL tilt, with a modest upside shortfall (up-capture 0.97; 0.87 in strong months);
  - the serious problems are an unvalidated edge, episode dependence (2018 / 2020), Top-K fragility and turnover, none of which an offensive sleeve can fix.
- **Hypothesis audit:**
  - momentum / trend / leadership and quality-growth families are exhausted or duplicative in this universe and period;
  - H017 rejected;
  - H029 / H030 NOT EVALUABLE (the only untested mechanism, data- and power-limited).
- **Selection:**
  - preferred OC-1 = SPY (market-exposure completion);
  - backup OC-B = H029 frozen F1–F8 signal test (conditional; Stage B; verified 2015–2021; underpowered).
- **Proposed test SYS-1** (not run):
  - account-level 2015–2021 system test: H028 + SPY 50/50 versus SPY, versus 90/10 SPY + cash (beta-matched) and versus transparent defensive + SPY;
  - gates P-1..P-5; no significance claim; falsification-oriented.
- **Recommendation:** proceed with SYS-1 only; stop the stock-selection offensive search on existing data.
- **Status:** STOPPED awaiting the owner (OC-CP1 §23).

## 2026-10-18: OC-CP2 — Independent offensive stock-selection candidate review (D247)

- **Scope:** candidate discovery and design only; committed non-return aggregates, literature and analytical equations; SYS-1 not run; no backtest, returns, real-stock signals, synthetic experiments, purchases or Holdout; no new active hypothesis.
- **Re-examination of OC-CP1:**
  - price leadership: exhausted (H019 valid signal-level null; H002–H011, H014, H018, H021-A, H024);
  - profitability / growth levels: exhausted (H016, H022, H024);
  - business improvement: overstated — H029 failed on null methodology only, and Data v3 signals use no fiscal labels, so D245's 2015–2021 window does not apply (window 2012-02 → 2021-11, 118 reviews).
- **Preferred candidate:** OC-2 = profitability improvement ΔROA (Data v3 F5), chosen on literature, data quality (best vendor-vs-SEC agreement) and distinctness (max |ρ| 0.18 with H024 / H028 features).
- **Test (proposed, not run):** universe-wide monthly Fama–MacBeth with controls; one-sided 1%; SE method fixed by a frozen Stage B-OC2 synthetic calibration; gates G1–G4.
- **Power** (`research/longhorizon/oc_cp2/OC_CP2_power.json`): main 80% MDE 3.2% naive / 4.3% realistic a year; power at +3% 45–74%; +2% undetectable.
- **Backup:** none (justified STOP → SPY). Combination feasibility: two stock sleeves infeasible at $100K under D044.
- **Status:** STOPPED awaiting the owner (OC-CP2 §14).

## 2026-10-18: OC-CP3 / OC-CP4 — OC-2 data integrity and synthetic inference calibration (D248)

- **Scope:** Stage 1 offline metadata-only PIT / fiscal-period audit; Stage 2 synthetic-only calibration. No real signal, return, QuantConnect run, purchase or Holdout.
- **Stage 1** (protocol frozen in 819a7a1; `docs/checkpoints/OC_CP3_oc2_stage1_data_integrity.md`): F5 compares adjacent twelve-month windows, so fiscal labels are not needed.
  - non-comparable risk ≤ 0.03%; FY-change / transition windows 0.2–0.5% (still valid);
  - SEC-verified quarter durations ≥ 96.9%; PIT violations 0; vendor–SEC agreement 94–99.9%;
  - window 2012-02 → 2021-11 (118 reviews); vendor-side cross-section 447 → 1,019 a review.
  - **PASS — PIT-SAFE AND SUFFICIENT.**
- **Stage 2** (protocol frozen in f4dca7e; Addendum 1 crash fix 9da492d; `docs/checkpoints/OC_CP4_oc2_stage2_synthetic_calibration.md`):
  - 9 of 14 gating nulls fail the size criteria through a mean shift of t (control functional-form and measurement-error leakage); standard errors themselves are calibrated (sd t ≈ 1.04);
  - synthetic power is not credible (implied IC sd ≈ 0.03);
  - diagnostic N13 failed (NaN).
  - **D — INSUFFICIENT EVIDENCE** (protocol §6.1); the method as specified is not validated.
- **Status:** STOPPED awaiting the owner (OC-CP4 §10: stop OC-2 → SPY, or one Stage B-OC2 v2 revision).

## 2026-10-18: OC-CP5a — OC-2 synthetic calibration v2, pre-run STOP (D249)

- **Scope:** one controlled methodological repair attempt; synthetic only (no real F5 / return / Fama–MacBeth, QuantConnect, backtest, portfolio, purchase or Holdout). v1 artifacts and classification D preserved unchanged.
- **Failure-mode audit** (`research/longhorizon/oc2/v2/OC2_V2_audit.json`; frozen-v1 reproduction + population algebra, no returns):
  - functional defects: N7 noise-free world (systematic variance above the total), N13 NaN (returns generated only for live slots), driver ≠ protocol;
  - nonlinear leakage from linear-rank controls (+0.04–0.10 %/yr population bias) — removed by restricted cubic splines;
  - identification: measurement error (+0.22 / +0.39 %/yr) and latent factor (≈ +0.23 %/yr per +1% latent premium) — not removable by any observed-control method (oracle removes it);
  - quiet market = missing signal-payoff component, not an SE scaling problem.
- **v2 method and generator** (`qresearch.oc2synth_v2`): spline controls, NW lag 7 by a stated lag rule, fixed-b critical values; AR(1) signal payoff at IC sd 0.06 / 0.09 / 0.12 (verified 0.061 / 0.090 / 0.118); variance-budget guard; id-tracked returns (N13 finite at 39–1,019 stocks); 39 null worlds + oracle + 16 power cells; locked driver; engineering record on DEV seeds (no rejection rate or power simulated).
- **Pre-run STOP:** the strict size criterion cannot coherently address the identification family (analytic projection: N5a 5% rejection 7.5–11%, N2L 17–39% in every regime). Options: 1 strict (projected C), 2 identification gate on full-rule false promotion ≤ 2% with a scoped claim (recommended if OC-2 continues), 3 stop → SPY.
- Protocol `research/longhorizon/oc2/v2/OC2_V2_protocol.md` DRAFT — NOT FROZEN; checkpoint `docs/checkpoints/OC_CP5a_oc2_synthetic_calibration_v2_prerun_stop.md`.
- **Status:** STOPPED awaiting the owner (OC-CP5a §25). No v2 classification; v1 stays D.

## 2026-10-18/19: OC-CP5 — OC-2 synthetic calibration v2, confirmatory result (D250)

- **Owner decision D250:** Option 2 with safeguards.
  - Tier 1: 30 ordinary null worlds under the strict size gates.
  - Tier 2: 13 confounded worlds (noisy controls / hidden factor, including the severe N5b / N2L5 at all three noise regimes) gated by complete-decision-rule false approval ≤ 2%.
  - Two power types (test vs complete rule); classification A needs both ≥ 0.80.
- **Freeze:** protocol frozen and committed before the run (3adf5b4; `FROZEN.json`); 60 worlds; 153,000 replications.
- **One run** (fb49fb8; 0 failures):
  - **Tier 1:** 30 / 30 pass (bias gone; spline controls and fixed-b NW7 work).
  - **Tier 2:** 12 / 13 pass. **N2L5 at IC sd 0.12 fails** (hidden +5% factor, high-noise market): 4.40% false approval (CI 3.59–5.39%). N2L at 0.12 sits exactly at the 2.00% limit.
  - **Power** at +3% central: test 84.6%, complete rule 43.5% (complete-rule MDE80 ≈ 4% a year).
  - **Result: C — NOT VALIDATED** (otherwise B).
- **Recommendation:** close OC-2 on current data and methods; SPY remains the offensive baseline. Checkpoint `docs/checkpoints/OC_CP5_oc2_synthetic_calibration_v2.md`.
- **Status:** STOPPED awaiting the owner.

## 2026-10-19: OC-CP6 — OC-2 closure and corrected SYS-1 design (D251)

- **Scope:** documentation, feasibility and design only. No backtest, QuantConnect run, return analysis or simulation.
- **OC-2: CLOSED — STATISTICAL METHOD NOT VALIDATED UNDER CURRENT RESEARCH CONSTRAINTS.** Stage 1 PASS, v1 D, v2 C preserved. OC-2 was never tested on real returns, and its economic hypothesis was not disproven. SPY is now the preferred simple offensive baseline.
- **Constraint audit:**
  - The 15-position limit counts every holding, ETFs included.
  - The 10% cap applies to every holding, relative to the account.
  - The $5,000 minimum applies to every new position.
  - Frozen H028 used its own shadow-book mechanics, not the D051 execution model.
- **Feasibility:** the original 50 / 50 H028 + SPY is **infeasible** at $100K and at $200K under the rules as written.
- **Corrected SYS-1:** proposed, not frozen. It needs an ETF rule (not counted among the 15 positions, exempt from the 10% cap) and $200K capital, which gives the H028 sleeve its exact frozen $100K basis. Arms: SPY, LV15 + SPY, SPLV + SPY, ex-ante beta-matched SPY + cash controls; falsification screens only.
- **Disclosed:** the main wealth comparison is largely predictable from the known components.
- Checkpoint `docs/checkpoints/OC_CP6_oc2_closure_corrected_sys1_design.md`; protocol `research/longhorizon/sys1/SYS1_protocol_PROPOSED.md`.
- **Status:** STOPPED awaiting owner decisions OD-1 to OD-7.

## 2026-10-19: SYS-1 controlled development experiment approved and frozen (D252)

- **Owner approval:** OD-1 to OD-7 (ETF exception, $200K for SYS-1 only, E1 idealised execution, SPLV gating / USMV diagnostic, 50% equity basis for new stock tickets with SPY absorbing residual cash, FS-1..FS-6 with three permitted classifications, one canary + one evaluation + at most two infrastructure retries).
- **Pre-freeze clarifications resolved** in the frozen protocol `research/longhorizon/sys1/SYS1_protocol.md` (pinned in `qresearch.sys1`):
  - exact standalone H028 reproduction plus quantified combined-account differences;
  - a deterministic cash ledger with no borrowing;
  - prospective BM-X betas, clamped to [0, 1];
  - total-return accounting with no double counting;
  - the known-history interpretation.

  No strategy, benchmark, historical rule or gate changed.
- **Built:**
  - engine `qr_sys1`, which reproduces `qr_h026.simulate` and `spy_simulate` bit for bit;
  - host S032 (subclass of the pinned S030; 49 project files);
  - offline rules `SYS1_canary.py` / `SYS1_eval.py`, committed before any run;
  - tests on synthetic data: engine, host on the fake QuantConnect environment, STOP conditions, offline rules, pins.
- **Next:** canary E032-01. E032-02 runs only if every mandatory check passes. H028 remains REJECTED; the Holdout stays sealed.

## 2026-10-19: SYS-1 canary E032-01 not started — QuantConnect terms of service (D252)

- **What happened:** the runner's pre-start check (`backtests/list`) was refused by QuantConnect: "You must accept the latest terms of service to continue using QuantConnect API."
- **Effect:** nothing was uploaded, compiled or run. No backtest exists, no result exists, and nothing was recorded in `experiments/INDEX.csv`. No infrastructure retry was used (E032-03 / E032-04 are untouched). The frozen protocol, code and config (c0b53e4) are unchanged.
- **Needed:** the owner must accept QuantConnect's latest terms of service in their QuantConnect account. That is a legal agreement only the account holder can accept.
- **Status:** STOPPED awaiting the owner. After acceptance, E032-01 runs exactly as frozen.

## 2026-10-19: QuantConnect access restored; $1,000 ETF minimum trade owner-approved (D253)

- The owner accepted QuantConnect's latest terms of service. The API was verified accessible (no running backtest).
- The $1,000 ETF minimum trade, already part of the frozen protocol, is now owner-approved for SYS-1 only.
- Nothing in the frozen experiment changed. Next: canary E032-01 exactly as frozen.

## 2026-10-19: SYS-1 canary E032-01 refused at upload — compressed / encoded project files no longer allowed (STOP)

- **What happened:** E032-01 (commit 62b623b) failed at the upload stage. QuantConnect refused `qr_p7_export.py` because it imports `zlib`; its Terms of Service now forbid compressed, encoded or embedded-binary project files.
- **Scope:** the whole frozen chain is affected.
  - The Data v2.1 reference table is packed (21 files, 1.27M characters).
  - Unpacked it is about 5.48M characters, more than the 3.2M a 50-file project can hold.
- **Not done:** no backtest was created, no result exists, and E032-02 was not run. No retry was used, since an identical retry would be refused the same way.
- **Checkpoint:** `docs/checkpoints/SYS1_CP0_e032_01_upload_refused.md`. Options:
  - A — plain-text rebuild (does not fit as it stands);
  - B — reference table in QuantConnect's Object Store (availability and cost unknown);
  - C — stop SYS-1 as NOT RUN — PLATFORM BLOCKED.

  Recommendation: a no-run feasibility study of A and B first.
- **Status:** STOPPED awaiting the owner. H028 remains REJECTED; the Holdout stays sealed.

## 2026-10-19: SYS1-CP1 — platform recovery feasibility, Options A and B (D255; read-only)

- **Scope:** read-only, documentation-only. Nothing uploaded, moved, deleted, run or exported. QuantConnect was read only (plan metadata, Object Store listing, project names).
- **Option B (Object Store):**
  - technically feasible: the S-MICRO tier (50 MB, 1,000 files, $0) is active, with 8 bytes used;
  - the table is about 5.5 MB of plain JSON, built from public SEC data;
  - exact H028 reproduction is checkable to the cent.
  - **Compliance UNCERTAIN:** the re-upload of QuantConnect-derived identifier keys / membership lists, and the result-export channel and content, are unsettled. Terms v1.5 count derivatives that reconstruct or approximate original values as Platform Data. The frozen SYS-1 output includes SPY / ETF daily paths, sent as compressed chunks.
- **Option A (plain-text files):** NO (5.48M characters needed vs about 1.41M available) and BLOCKED (splitting data across files to get around limits).
- **Legacy projects:** 91 projects. 35 of 83 recorded last uploads carry packed modules. Some locally committed exports (benchmark daily paths, per-stock score tables) may fall under v1.5.
- **Recommendation:** conclusion 3, request explicit platform clarification; four questions are listed. If supportive → prepare the Object Store migration (separate freeze, output amendment, canary). Otherwise close SYS-1 as PLATFORM BLOCKED.
- **Checkpoint:** `docs/checkpoints/SYS1_CP1_platform_recovery_feasibility.md`.
- **Status:** STOPPED awaiting the owner.

## 2026-10-19: SYS1-CP2 — Object Store migration assessment; exact H028 reproduction not achievable (D257 / D258; STOP)

- **QuantConnect Support (recorded D257):**
  - SEC data may be stored as plain JSON in the Object Store;
  - QuantConnect identifiers and universe membership must be generated inside the cloud, not reused;
  - Platform Data stays in the cloud;
  - results go through the official export.
- **Finding:** the frozen identity table (3,958 security ids → dated CIK / SIC) was assembled offline from earlier QuantConnect exports, mostly on build 18131 and the old dataset. 88% of its securities depend on vendor CIK or QuantConnect-derived evidence.
  - It cannot be reused.
  - Cloud regeneration cannot use the same inputs: the build is gated and the old dataset is retired 2026-10-31.
  - So the pinned H026 panel digests and the E030-05 result cannot be expected to reproduce.
- **Migratable:** the SEC-only components.
- **Inventory:** compressed modules and packed result blocks identified.
- **Options:** A close SYS-1 as PLATFORM BLOCKED (recommended); B one identity-regeneration feasibility canary (C0 / C1 exact only); C a new cloud-native successor (new research decision).
- **Not done:** no upload, run, legacy change or purchase. Holdout sealed.
- **Status:** STOPPED awaiting the owner.

## 2026-10-19: RR1 — Research Reset: QuantConnect migration impact and updated roadmap (D259 / D260; planning only; STOP)

- **Owner direction (D259):** pause strategy research; planning review only. Recorded verbatim before the investigation.
- **Sources:**
  - official QuantConnect documentation;
  - committed repository evidence;
  - one read-only LEAN version-list call: `master` is 18194 (2026-10-19), and a `morningstar-legacy` branch 18184 exists.
  - The Migration Atlas could not be read: the proxy refuses `cdn.quantconnect.com`.
- **Documented changes:**
  - fundamental history rebuilt from 1998;
  - about one third of common values differ;
  - sign convention changes;
  - 1,251 retired properties;
  - ratios dated by filing;
  - pre-2013 statements lack filing dates (nominal 45 days);
  - old dataset retired 2026-10-31;
  - Terms v1.5 §2.6;
  - engine selection gated to the Trading Firm tier;
  - Object Store contents count as Platform Data.

  No price or Security Master change is documented.
- **Our own evidence:**
  - the September beta (18131) and the October default (18178) are different data;
  - market cap is missing for about 18% of stock-months on the current data;
  - exact reproduction held from 10-10 to 10-13;
  - price data was never compared across datasets, so that question is open.
- **Impact:** all conclusions stand as historical evidence. The frozen chain is not reproducible. SEC-only components and the pure libraries can be reused. 2010–2021 is exhausted as a confirmation window.
- **Recommendation:** Option 3 (licensed point-in-time data and a local engine), gated by a desk-only verification and an owner decision on D123 / D001. The fallback is Option 1 (QuantConnect, price-first), or stopping.
- **Not done:** nothing run, bought or activated. Holdout sealed.
- **Checkpoint:** `docs/checkpoints/RR1_research_reset_qc_migration_impact_roadmap.md`.
- **Status:** STOPPED awaiting the owner.

## 2026-10-19: RR1 decisions recorded; SYS-1 closed; RR2 programme proposal (D261 / D262; documentation only; STOP)

- **Owner (D261):**
  - RR1 accepted;
  - **Option 1, QuantConnect-only price-first research** selected;
  - Option 3 deferred, with D123 / D001 kept in force;
  - RR1 §6 simplification principles approved;
  - **SYS-1 closed as NOT RUN — PLATFORM BLOCKED — NO STRATEGY VERDICT**; H028 remains REJECTED;
  - Support questions deferred.
- **RR2 proposal** (`docs/checkpoints/RR2_qc_price_first_research_programme_proposal.md`):
  - **Universe blocker:** the ≥ $2B PIT universe on current data is survivorship-biased as delivered (about 18% of stock-months missing market cap, D187). Proposed answer: one aggregate-only baseline run that measures the gap, tests an in-cloud share-count × adjusted-price cap and checks pre-2010 coverage. The SEC repair is the fallback.
  - **Engine:** the existing plain-text harness plus signal plug-ins, with in-host scalar evaluation.
  - **Tranche 1:** at most 3 hypotheses. Candidate categories: K1 dividend-event drift, K2 market-state exposure control, K3 long-horizon reversal, K4 equal-weight structure.
  - **Screening and confirmation:** a "Promising" screen on the exposed 2010–2021 window. Confirmation uses the unchanged Amendment 3 gates on 1999–2009 (if available and approved) or the Holdout.
  - **Stopping rules:** stop when none of the 3 is Promising, on any platform blocker, and no rescue variants.
- **Not done:** nothing run, bought or implemented. Holdout sealed.
- **Status:** STOPPED awaiting the owner (RR2 §10).

## 2026-10-20: RR3 — Universe Baseline Audit UB-1 (E804-01) (D263 / D264; STOP)

- **Owner (D263):**
  - RR2 architecture approved in principle;
  - ONE aggregate-only infrastructure run authorised;
  - in-cloud SPY-relative metrics approved;
  - K1 / K2 preferred but not registered.
- **Before the run:** the protocol, host X804, `qr_ub`, `UB_eval`, pins and config were frozen in 0f11c81. A runner upload guard (plain text, at most 50 files, at most 64k characters) was added.
- **E804-01:** LEAN 18194, 257 s, 0 orders, 274 month-end points 1999-02 … 2021-11, aggregates only. Accepted by QuantConnect's compliance review.
- **Outcome:**
  - **W1 2010–2021 = PASS-A.** The vendor market cap alone suffices: gap ≤ 2.2% a year, survivorship bias upper bound ≤ 0.34 points; 2021 not assessable.
  - **W0 1999–2009 = FAIL.** Vendor caps cover only survivors before late 2009; the U-B rebuild is invalid (vendor agreement 82–86%; share counts lead the vendor's cap in 21% of changes).
- **Limits:**
  - names without any fundamentals object cannot be classified;
  - names with blank classification fields are counted as non-common;
  - the few excluded names do exit more often.
- **Data change measured:** 2011–2017 eligible stock-months are 88,773, against 76,915 on 18178 and 93,687 in Data v1.
- **Not done:** no strategy, no SEC fallback, no D033 / D035 amendment. Holdout sealed.
- **Status:** STOPPED awaiting the owner (RR3 §6).

## 2026-10-20: RR4 — RR3 review: universe risk, screen proposal, K1 / K2 feasibility (D265 / D266; offline; STOP)

- **Owner (D265):** RR3 W1 PASS-A accepted for the measured population only; W0 FAIL; U-B retired; the no-fundamentals / unclassified population not accepted as harmless; offline design of the screen, K1 and K2; no runs.
- **Universe risk (offline, committed aggregates):**
  - E804 is 5.2% short of Data v1 in 2011–2017 (2.8–8.6% a year); RR3 measured about a third of that.
  - The known no-fundamentals group on 18178 (68 securities, 67 later disappearing) would put 2011–2015 above the 3% gate if still missing; from 2016 the bound is ≤ 2%.
  - Not resolvable offline; a narrow in-cloud SEC classification check is feasible (not implemented). Owner decision UR-1.
- **Screen:** P1–P6 unchanged; new D2 stage (Amendment 3 evidence test on development data, Holm across the tranche); Holdout once; forward reviews to +36 months. Proposed, not frozen.
- **K1:** conditionally feasible (ex-date signal, filters, ≈ 89+ events a year, 126-session hold). **K2:** not feasible as broad-market under current rules; recommend dropping.
- **Not done:** no run, upload, hypothesis, purchase or Holdout access.
- **Status:** STOPPED awaiting the owner (RR4 §6).

## 2026-10-20: RR5 — UR-1 SEC classification audit SCA-1 (E805-02) (D267 / D268; STOP)

- **Owner (D267):** UR-1 option A (narrow free SEC classification check: one aggregate run + ≤ 1 retry, no repair); D1 / D2 with clarifications (one Holdout candidate for the whole programme; exposed-data caveat; run budget); K1 conditional GO (H031 preparation; canary after the universe is accepted); K2 dropped.
- **Frozen before any upload or run (c350dfc):** protocol, X805, `qr_sca`, SEC builder, eval rule, pins, SEC object SHA. Public SEC JSON uploaded once to the Object Store.
- **E805-01:** infrastructure failure (object not yet visible 29 s after upload). **E805-02:** the single retry, completed (155 s, 0 orders, compliance-accepted, aggregates only).
- **Outcome:** W1 2010–2021 **FAIL** — 2010–2015 confirmed-missing ≥ $2B US common stocks 3.5–6.1% of stock-months, mostly no-fundamentals names that later disappear (exit +7..+21 points; bias up to 0.78 points). 2016–2021 **INCONCLUSIVE** (confirmed ≤ 2.9%, but possible + unresolved up to 8.2%). Instrument agreement 99.3–99.7%.
- **Also:** screen / confirmation protocol v2 (ready to freeze); H031 spec drafted but not presented (universe not passed).
- **Status:** STOPPED awaiting the owner (UR-2: A scoped SEC-cap inclusion + re-audit recommended / B 2016–2021 with exception / C pause / D accept).

## 2026-10-20: RR6 — UR-2 strictly point-in-time SEC universe repair + re-audit (E806-01) (D269 / D270 / D271; STOP)

- **Owner (D269):** UR-2 option A: one narrow strictly-PIT SEC-based repair and one re-audit, ≤ 1 retry, aggregates only; hard stop on FAIL / INCONCLUSIVE.
- **Frozen before upload or run (a539555):** protocol UCR-1, X806, `qr_ucr`, PIT SEC builder, eval rule, pins; new per-filing PIT SEC object (`rr/ucr_sec_v1.json`, same public SEC cache; D270); float-age rule 650 days fixed before the freeze (returns-blind check).
- **E806-01:** completed first time (default build 18198; snapshot identical to E805-02; 0 orders).
- **Outcome:** 8,191 stock-months repaired (caps 99.78% agree with vendor caps); confirmed gap 3.5–6.1% → 0.2–0.8%, confirmed bias → ~0; but **W1 INCONCLUSIVE** in every year (possible + unresolved keep Gap_max at 3.2–4.4% and the survivorship upper bound at 0.56–1.26 points). Repaired counts 1.7–3.1% above Data v1 (not independently explained).
- **Status:** STOPPED awaiting the owner (D269 §4: no further repair; programme protocol not frozen; H031 DRAFT).

## 2026-10-20: RR7 — research path design review (D272 / D273; design only; STOP)

- **Owner (D272):** RR6 accepted as INCONCLUSIVE — HARD STOP; no reclassification or further repair; H031 DRAFT; design review of Path A (exploratory stock discovery on the SEC-repaired universe) vs Path B (ETFs); no purchases, runs, uploads or implementation.
- **RR7:** Path A feasible only as explicitly exploratory (EDP-1: two-universe pass, P1–P6 unchanged, +1.0 pt/yr margin, both halves, no search, stop rule; a PASS only justifies paying for independent validation). H031 moderately exposed (initiations most). Path B needs several scope amendments, has its own selection biases and no credible route to beating SPY (drawdown tool only).
- **Recommendation:** Path A exploratory with H031 only; next step = freeze EDP-1 + H031, one host from existing parts, ONE event canary, STOP. D270 disclosed (new SEC object needs ratification; 650-day rule).
- **Status:** STOPPED awaiting the owner (RR7 §6).

## 2026-10-20: OS-CP1 — Offensive Score Research: candidate selection and first experiment design (D274 / D275; design only; STOP)

- **Owner (D274):** new direction — offensive stock-selection score (characteristics → score → Top N), offensive component first; H028 stays REJECTED; DESIGN ONLY.
- **OS-CP1:** lessons (past SPY-beating results were defensive exposure or one episode; searches / learned weights used up the power; familiar factors exhausted); three mechanisms compared; **recommended OS-1 = Net Share Repurchase Score** (fixed rule from SEC cover-page share counts already in the Object Store; Top 15 monthly, buffer 2N); no learned score; honest caveat that no bull-specific alpha exists and OS-1 may prove value-like; exploratory gates O1–O9 with beta-matched controls and a vendor-universe shadow; canary C-OS1 without returns; ≈ 2 sessions, 3 runs, $0.
- **Status:** STOPPED awaiting the owner (OS-CP1 §10: D270 ratification, EDP-1, OS-1, gates, run authorisation). Nothing registered, run or uploaded; H031 DRAFT; Holdout sealed.
