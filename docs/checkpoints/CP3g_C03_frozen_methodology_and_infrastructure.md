# C03: frozen methodology (D082) and H012/H013 infrastructure (checkpoint)

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **STOP. Awaiting owner authorisation of the C03 strategy backtests.** No C03 strategy backtest, Validation, Walk-Forward or Holdout run has been made. |
| Runs made in this phase | 4 infrastructure canaries (E963-01, E963-02, E963-03, E964-01): not trials, and all use non-candidate settings. |
| Registry totals | 195 runs, 191 experiment IDs, 11 hypotheses tested (H001–H011), 11 research strategies (S001–S011). H012/H013 (S012/S013) are built but have never run. |
| Tests | **371 pass** (330 before this phase; 41 new). |

## 1. Summary

1. **D082 is recorded as approved and frozen**, with both clarifications written into one specification: `research/cycles/C03_statistical_spec.md`.
   - A test fails if a single byte of the specification changes.
2. **The trial counts are now a deterministic registry formula**, implemented and tested:
   - official N = 37 now, **43** after the committed runs;
   - conservative N = 64 now, **76** after the committed runs, and at most **120**.
3. **The DSR calculation and the Validation procedure are frozen**, implemented in one module (`qresearch.c03stats`) and tested against an independent re-implementation.
4. **S012 (H012) and S013 (H013) are built**, together with the configurations of all 32 committed C03 runs. None of them has run.
5. **The canaries passed**, after they found and we fixed one real S012 defect: an empty basket during the universe's warm-up.
   - S013 reproduces the random null run E962-22 exactly: 975 of 975 fills.
6. **One issue needs an owner decision before H012 runs (§8A).** H012 will almost certainly fail the unchanged IS screen item "≥ 100 closed trades" by construction.

## 2. The final frozen D082

Full text: `research/cycles/C03_statistical_spec.md`. Decision log: D082 (final) in `DECISIONS.md`.

- **PBO:** a diagnostic only. It is calculated and reported with its limitations, and it never selects or rejects anything. The C01/C02 conclusions are unchanged.
- **DSR ≥ 0.90 at both the official and the conservative N**, on every deployable book:
  - an H012 variation run;
  - **each H013 seed separately**, never averaged for acceptance.
- **H013:** all three fixed seeds must pass every stage (screen, 2× slippage, robustness, Validation, DSR at both N).
- **Unchanged:**
  - the IS screen and robustness thresholds, and the Validation gates (the PBO item is dropped from them for C03 only, per D082);
  - $100K primary, with $200K S1/S2 as sensitivity only;
  - controls and random nulls are diagnostics;
  - budget 82, and the stopping rule;
  - no Validation outcome is used before Validation; the Holdout stays locked.

## 3. The trial counts (Clarification A)

**Formulas:**

- **official N = number of selection candidates;**
- **conservative N = selection candidates + H013 replicate seeds + robustness configurations + Validation configurations.**

Both are cumulative over all cycles, taken from the append-only registry.

| Category | What it contains | Official | Conservative |
|---|---|---|---|
| Selection candidate | Each IS variation at base costs. For an H013 variation, only its first started seed. | ✔ | ✔ |
| Replicate | Seeds 2 and 3 of each H013 variation (6 in total) | | ✔ |
| Robustness | The 2× slippage item, 4×/6× costs and plateau perturbations. Each H013 seed separately. | | ✔ |
| Validation | Every run outside IS. E005-28 (C01) counts 1. Each H013 seed separately. | | ✔ |
| Not counted | Technical retries and recoveries of the same configuration; runs that never started; canaries, controls, random nulls, $200K sizing runs, 1999–2009 stress runs | | |

**Other rules:**

- A run counts once it has **started**, even if it failed.
- Future conditional runs are counted **automatically** when registered.
- The C03 evaluation is taken once, after all authorised Validation runs. It is repeated if any later C03 run is registered, and the repeat can only turn a pass into a fail.
- If the official N is not exactly 43 at that evaluation, the evaluation stops with an error.

| Moment | Official N | Conservative N |
|---|---|---|
| Now (verified on the registry) | 37 | 64 (37 + 0 + 26 + 1) |
| After the 12 committed selection runs (verified by simulating their registration) | 43 | 76 |
| If every conditional run happens | 43 | **120** |

**Correction:** CP3f said the conservative N would reach "at most about 104". That missed the conditional 2× slippage items and the Validation runs. **The correct bound is 120.** At N = 120 the DSR requires an observed annual Sharpe over IS + VAL of about 1.67, against 1.48 at N = 43.

## 4. DSR calculation and Validation procedure (Clarification B)

**Calculation:**

- **Data:** daily net returns (after costs) of the IS run followed by the VAL run of the same frozen book. They are concatenated without any return across the gap: about 3,020 daily returns.
- **Formula:** per-day Sharpe (sample standard deviation), pandas skewness, and kurtosis (pandas + 3). The benchmark Sharpe SR* is the expected best Sharpe of N skill-less tries, using the registry's Sharpe dispersion (0.0010013; for H013, the mean of its seeds).
- **Pass:** DSR ≥ 0.90 at **both** N, compared unrounded. An undefined value fails.

**IS + VAL combined is the gate** (as approved in D036). The IS-only and VAL-only figures are reported and never gate.

**Can a strong IS hide a weak VAL?** Partly. The unchanged Validation gates bound it:

- VAL Sharpe ≥ 0.4 and ≥ 0.5 × IS;
- above the equal-weight benchmark;
- drawdown, trade count and the 2020 check.

Together they mean the weakest VAL that can still pass is a Sharpe of about **0.89–1.00**, and only with an IS Sharpe of about 1.8–2.0.

A VAL-only DSR would demand an annual VAL Sharpe of 1.76–1.94. That would be a new threshold, and it is not adopted.

**Validation stays genuinely out of sample:**

- the chosen variation (with its three H013 seeds) is frozen by a promotion record before any VAL run;
- one VAL run per book, and only with separate approval;
- VAL results only accept or reject.

**Correlated H013 seeds:**

- The seeds correlate about 0.86. Three of them are worth about **1.1 independent portfolios**.
- So "all three pass" is not three independent confirmations. It guards against a result that depends on a lucky random draw, and it is never weaker than judging one seed.

## 5. Automated tests

**371 pass.** The 41 new tests cover:

| Area | Tests |
|---|---|
| Trial accounting | Every category and each item the owner listed: seeds as replicates; the first started seed as the candidate; failed runs count; not_started runs don't; robustness and VAL per seed; the pinned pre-C03 counts 37/64; the committed runs giving 43/76. |
| DSR | Concatenation without a bridging return; agreement with an independent scipy implementation; the DSR falls as N rises; both counts required; 0.90 passes and NaN fails; every seed must pass; the official-N guard; the frozen specification hash. |
| S012 | RV against numpy; the exposure cap; band; Control B (only previous targets, and a first year from pre-start history only); largest-15 with ties; quarterly reconstitution; weekly and monthly rescale days (including the New Year week); the rebalance window; Control A; the warm-up basket fix; **look-ahead truncation** of RV and of the whole decision sequence. |
| S013 | MAX/MAX5; the top-fraction exclusion (floor, ties, short histories never excluded); **look-ahead truncation**; the paired order equal to the null's; `nullorder.py` a byte copy of X962's code; the algorithm equal to the null at q = 0. |
| Canaries | The canary code copies are byte-identical to the strategies; the E963-03 and E964-01 results; E964-01 reproduces E962-22's fills and equity exactly. |

All earlier tests still pass, including execution timing, metrics, portfolio accounting, data integrity, reproducibility and the holdout lock.

## 6. H012/H013 infrastructure and canary results

**Strategies:**

- **S012** (`strategies/S012_vol_managed`) has three modes: timing, Control A and Control B.
- **S013** (`strategies/S013_lottery_avoid`) is X962's code with the excluded names skipped.
- Implementation choices are in D083 and D083a.

**Committed configurations** (written by `research/cycles/C03_make_configs.py`, not run):

- 12 selection runs: E012-01..03 and E013-01..09;
- 4 controls: E012-04..07;
- 10 $200K sizing runs: E012-08..11 and E013-10..15;
- 6 $200K nulls: E962-25..30.

**Evaluation script:** `research/cycles/C03_eval.py`, written and committed before any C03 run.

**Canaries** (verification runs, not trials; all with non-candidate settings):

| Run | Result |
|---|---|
| E963-01 (X963 v1.0) | **Stopped on a canary-code bug.** At the 2010-11-26 half-day close, the fresh SPY history was shorter than the window. S012 was not involved. Annotated as bugged. |
| E963-02 (X963 v1.1) | **Completed, and all mechanical checks passed. It found a real S012 defect:** during the universe's 20-session warm-up no stock is eligible, so the basket formed at the first close was empty and the book stayed in cash until April 2010. **Fixed (D083a)** with a regression test. The run is annotated as superseded. |
| **E963-03 (X963 v1.2)** | **Pass.** (1) SPY RV from the harness equals RV from fresh point-in-time history in 103 checks (largest relative difference 0.02%). (2) The basket equals the 15 largest by the universe filter's own market cap in 8 of 8 reconstitutions, always from a selection dated on or before the decision day. (3) No order was placed outside an event or rebalance window. (4) Zero timing violations: every fill was at the next open. (5) Control B's pre-start targets come only from history before 2010. |
| **E964-01 (X964 v1.0)** | **Pass.** S013's code with nothing excluded **reproduces the null E962-22 exactly**: 975 of 975 fills and an identical equity curve. Over 201 audits of the exclusion at q = 0.25 (MAX and MAX5), there were zero errors in count, ordering or pairing, and no short-history name was ever excluded. MAX/MAX5 matched fresh history in 9,898 checks (largest difference 0.00023), and every window ended on the day's own bar. |

**What the canaries showed about H012's mechanics** (non-candidate parameters RV(10), weekly, 2010–2011):

- The **$5K minimum for new positions** skipped entries 13 times. This happens when exposure is below about 0.77 and a new stock joins the basket.
- After completed rebalances, the invested fraction was on average 1.9 points below target e × 98% (worst −7.4 points, i.e. one basket stock missing).
- This affects the H012 variations and Control B alike, never Control A. It is counted and will be reported for every run.

## 7. Prerequisites for the C03 strategy backtests

| Prerequisite | Status |
|---|---|
| D082 frozen, with both clarifications | ✔ Specification with pinned hash |
| Deterministic trial accounting and DSR, with tests | ✔ |
| S012/S013 built and tested (look-ahead, timing, point-in-time selection) | ✔ |
| Canaries passed; reproducibility shown | ✔ E963-03, E964-01 (E964-01 = E962-22 exactly) |
| Configurations of the committed runs and the evaluation script committed before any run | ✔ |
| Budget | ⚠ See §8C |
| H012 compatible with the unchanged screen | ✖ See §8A: an owner decision is needed |

## 8. Issues for the owner

### A. H012 and the trade-count screen items (decision needed before H012 runs)

**The issue.** The unchanged IS screen requires ≥ 100 closed trades, and Validation requires ≥ 50. H012 holds the 15 largest stocks and changes only about 1–3 of them per quarter. Its exposure changes resize positions but do not close them.

- The canary closed **8 trades in 2 years**.
- Over IS 2010–2017 that means roughly 30–40 closed trades, and about 15–20 in Validation.
- This depends on basket turnover, not on the timing parameters. It comes from the canary, not from any candidate result.

**Why it matters.** H012 will almost certainly **fail the screen by construction**, whatever its timing value. The trade-level items (expectancy confidence interval, expectancy without the best 5%) also have little meaning with so few trades. The same applies to Controls A and B, so the controls comparison is unaffected.

**Options:**

1. **Run H012 as approved and accept the likely rejection.**
   - It costs 11 of the committed runs (3 selection, 4 controls, 4 sizing; about 45 minutes of node time, no extra money).
   - The timing value against Controls A/B is still measured and reported as a diagnostic.
2. **Pre-declare now an H012-specific replacement for the trade-level items.** This is a change to an approved threshold. It needs your explicit approval before any H012 result, and any replacement must be at least as strict.
3. **Remove H012 from C03** and run H013 only.
   - This saves 11 committed and up to 15 conditional runs (2× slippage ≤ 3, robustness ≤ 10, S1 ≤ 2).
   - The frozen official N would stay at 43 (conservative), which needs your confirmation.

**Recommendation: Option 1.** It keeps every threshold exactly as you froze it, and costs node time but no money. It still answers the question H012 was chosen for: does volatility timing beat the controls? It does so as a diagnostic. Option 3 is reasonable if you prefer not to spend the node time.

### B. The $5K minimum under exposure scaling (information)

Reported in §6. No change is proposed: the approved minimum-position rule stays as it is.

### C. Budget accounting (small)

- The plan had 2 canary runs. 4 were needed (one canary bug, one S012 defect found).
- The cap of 82 was exactly 34 committed + 48 conditional, so the maximum would now be 84 if every conditional run happened.

**Recommendation:** count canary re-runs as technical verification outside the strategy cap, reported as here. Alternatively, lower the conditional maximum to 46.

## 9. Remaining limitations

- **Low power by design.**
  - At N = 43 the DSR needs an observed Sharpe of about 1.48 over 12 years, and 1.59–1.67 at the conservative N.
  - A genuine but moderate edge will usually be rejected. "No Production Candidate Found" remains the most likely outcome.
- **Strong IS and weak VAL:** the combined DSR can borrow from IS. The protection against VAL decay then rests on the Validation gates (§4).
- **Correlated seeds and variations:** they are not independent evidence. N overstates the number of independent tries, which errs strict.
- **Sharpe dispersion** is estimated from C01–C03 candidates, and will include C03's own IS Sharpes. This follows the frozen formula; it may move either way.
- **Data precision:**
  - Point-in-time dividend adjustment differs from a fresh history by up to about 0.02% in price. That is negligible for RV. In MAX/MAX5 it gives differences up to 0.00023, which can move a stock that sits exactly at the exclusion cut-off.
  - QuantConnect may revise dividend data between days (a known quirk).
- **H012 implementation effects:**
  - the $5K entry skips;
  - the 5-session rebalance window under D051 settled-cash rules;
  - the 15% gap reserve, which keeps invested exposure slightly below target.

  All three apply equally to Control B, so the timing comparison is fair. They lower absolute exposure.
- **Universe warm-up:** every strategy is in cash for the first 19 sessions of 2010 (20-session dollar-volume filter). This is common to all runs and benchmarks it trades against.

## 10. Decision requested

1. **Authorise the C03 committed strategy runs (32):**
   - 12 selection runs, 4 controls and 16 sizing/null runs;
   - then the conditional runs strictly as pre-declared.
2. **Choose an option for H012 (§8A).** Recommended: Option 1.
3. **Confirm the canary budget treatment (§8C).**

Until then: **STOP.** No C03 strategy backtest, Validation, Walk-Forward or Holdout.
