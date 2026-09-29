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
