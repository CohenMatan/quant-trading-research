# P7-CP5b — Option B result: QuantConnect's new default build does NOT reproduce the frozen data (case B2) — STOP

**Date:** 2026-10-10. **Decisions:** D182 (owner chose option B), D183. **Status:** STOPPED awaiting the owner.

**Short version.** As the owner asked, I re-ran the H022 diagnostic canary after QuantConnect's 2026-10-10 dataset switch.

- QuantConnect now runs everything on LEAN build **18178**.
- On that build the frozen point-in-time fundamentals layer can no longer date most company reports.
- So almost every stock fails the "fundamentals missing or stale" disqualifier (H2).
- The H022 population collapses from **196–612 stocks a month** (calibration build 18131) to **0–14**.

This is **case B2**: the prepared panel is not identical, so the real evaluation **cannot** be run with the pinned c_IC. Following the rule the owner approved, I stopped.

**No real H022 statistic has been computed at any point** (no IC, gate, quintile or 80+ figure). c_IC = 2.390976 stays pinned and unused.

## 1. What was run (all infrastructure, no returns analysed)

| Run | What | Engine | Result |
|---|---|---|---|
| E994-03 | The H022 canary (X994 v1.1, unchanged) on the default build | **18178** | Crashed in its last step: its null-timing check (on synthetic responses) found no decision date with ≥ 20 population stocks. Nothing exported; no real IC |
| E993-03 | The frozen X993 v1.1 score export (E993-02's exact configuration), scores and flags only | **18178** | Completed. Compared row by row with E993-02 (18131) below |

## 2. What differs between the calibration build (18131) and the default build (18178)

| Measure | 18131 (E993-02) | 18178 (E993-03) |
|---|---|---|
| Month-end reviews / weekly checks (calendar) | 84 / 325 | 84 / 325 (identical calendar) |
| Eligible stock-months (data-v1 universe) | 93,687 | 76,915 (−18%) |
| Securities in the price panel | 1,917 | 1,459 |
| Fundamental reports with **unknown timing** (cannot be dated point-in-time) | 608 | **31,538** |
| Reports with an estimated file date (+90-day rule) | 12,714 | 4,320 |
| Usable 12-month revenue baselines | 78,633 | **2,269** |
| Rows disqualified by H2 (fundamentals missing / stale) | 32,999 | **76,172 (99% of eligible)** |
| H022 population (eligible, kept class, fully scorable) | 40,351 stock-months; 196–612 a month | **485 stock-months; 0–14 a month (median 5)** |
| Rows identical in every score field | — | 109 of 74,772 common rows |
| Point-in-time violations | 0 | 0 |

**Interpretation.**
- The frozen fundamentals layer (data infrastructure v1, D108–D114) only uses a report after its filing date. When the vendor's file date is missing or earlier than the period end, the timing is "unknown" and the report is never used. That rule is the protection against look-ahead.
- On the new default dataset, most reports fail that test, so the safety rule blocks nearly all fundamentals. This is the safe failure mode: no look-ahead, just no data.
- The universe also shrinks by about 18%, so prices, market caps or eligibility data differ as well.

The differences are in the **data**, not in our code: the same frozen code, configuration and calendar give different inputs.

## 3. What this means

- **H022 cannot be evaluated on the current QuantConnect default dataset without changing the data infrastructure.** The frozen score needs point-in-time fundamentals.
- **The whole frozen data infrastructure v1 is affected, not just H022.** It was built and verified on build 18131. That build can no longer be selected on our $24 / month tier (P7-CP5a), and the default dataset behaves differently. Any future research that uses fundamentals faces the same problem.
- Nothing is lost scientifically, because no real H022 statistic has been seen. A re-freeze on new data would still be a clean pre-registration. But it would have to be built and verified first.

## 4. Options for the owner

| Option | What | Cost | Comment |
|---|---|---|---|
| **C. Data infrastructure v2 (re-audit), then H022 on v2** | (1) A small fundamentals-field probe (infrastructure) to learn how the new dataset reports filing dates. (2) Adapt the point-in-time timing rule only if a safe, verifiable source exists (e.g. SEC filing dates we already hold for repaired securities). (3) Re-run the P7-CP1-style audits: timing vs SEC, coverage, universe. (4) Re-run the X993 score export and re-confirm mechanics. (5) Owner re-freeze. (6) New canary, new 5,000-world null, new c_IC, then the ONE real run | $0; several sessions of work; about 10 QuantConnect runs | The only way to finish H022 at the current budget. The score, spec and gates would be unchanged, but data v2 is an owner decision (D114 rule). It may also fail if the new dataset has no reliable filing dates |
| **A. Trading Firm tier** | Restore build selection and run on 18131 | ≈ $480 / month (over the $200 ceiling) | Not recommended. It is also uncertain whether 18131's data will stay available once the old dataset is retired on 2026-10-31 |
| **D. Close H022 as "not evaluable on the available infrastructure"** | Preserve everything as is; no verdict | $0 | Honest. Phase 7 would end without a result |

**Recommendation: C, starting with only step (1), the probe.**
- It is cheap and shows quickly whether the new dataset still carries usable filing dates.
- If it does not, D becomes the honest outcome, and so does a review of whether fundamentals-based research is still feasible on QuantConnect at this budget.
- Every later step of C would return to the owner before it runs.

## 5. Records

- **Experiments added:**
  - E994-03 (failed: default-build canary crashed, nothing about the real assignment computed);
  - E993-03 (completed, scores only).
- **H022 experiments so far:** 11 (E994-01..03, E023-01..07, E993-03).
- **Comparison file:** `research/phase7/P7_CP5b_engine_diagnosis.json`, from `P7_CP5b_engine_diagnosis.py`.
- **Runner:** config key `lean_version_policy: "default_build_digest_verified"` (D182). Allowed only for X994 canaries, the digest-guarded S023 real run and the X993 diagnostic export; the build actually used is recorded.
- **Confirmations:**
  - no change to the score, spec, mechanics, gates or c_IC;
  - no real statistic computed;
  - 2018–2021 and the Holdout untouched;
  - no portfolio, 0 orders;
  - nothing purchased.

## 6. Exact owner decision needed

Choose **C** (and authorise step 1, the fundamentals-timing probe, only), **A** or **D**.

Until then: STOP. No further H022 QuantConnect run.
