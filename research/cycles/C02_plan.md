# Research Cycle 2 (C02): plan for owner approval

| Field | Value |
|---|---|
| Status | **APPROVED in principle by the owner on 2026-09-29, with three clarifications (trial accounting, takeover handling, H010 timing), incorporated below and marked "Amended 2026-09-29".** No C02 strategy backtest may run before the prerequisite checkpoint (`docs/checkpoints/CP5pre_C02_prerequisites.md`) is approved. |
| Written | 2026-09-29, after C01 closed (No Production Candidate Found) and before any C02 data was examined |
| Period | IS only: 2010-01-04 → 2017-12-29. Validation (2018–2021) and Holdout (2022-01-01 → 2026-08-31, locked) are not used. |
| Hypotheses | 6 (H006–H011), in 6 distinct families; details in `research/hypotheses/H006.md` … `H011.md` |
| Planned trials | **18 strategy-selection trials** (3 pre-declared variations each), plus a capped number of robustness runs (§6) |

## 0. Summary

- **Six new, genuinely different ideas.**
  - Four are event-driven swing trades that enter on a specific daily event and exit on a rule: breakout (H006), volatility squeeze (H007), volume shock (H009), gap-and-hold (H010).
  - Two are monthly cross-sectional rankings of kinds not tested before: residual relative strength (H008) and calendar-month seasonality (H011).
- **Designed for our costs.**
  - Every idea uses **10 positions** (about $9.8K each), so the $7 commission is about 0.07% per side instead of 0.11%.
  - Holding periods are 3 weeks to several months. Nothing resembles H001's 5-day churn.
  - Each hypothesis states its expected cost drag in advance: 1.4–4.2% of equity a year.
- **Fixed in advance.**
  - Every rule, parameter and variation, and every robustness perturbation.
  - The trial count used for Deflated Sharpe, and how PBO is computed.
- **No gate or threshold changes.** C01's screening and robustness rules apply unchanged. Only extra *diagnostics* are added (§7), plus the frozen trial-count definition for Deflated Sharpe (§6, D069).

## 1. The six hypotheses at a glance

| ID | Family | Entry | Exit | Expected hold | Selection | Slots | Rebalance | Est. cost per year |
|---|---|---|---|---|---|---|---|---|
| **H006** | Breakout / price expansion | Close above the prior 55-day high, volume ≥ 1.5× average, above SMA200 | Trailing stop: highest close − 3 × ATR20; time stop 60 | 20–50 days | Breakout size in ATR units | 10 | Daily scan | 2.1–2.8% |
| **H007** | Volatility contraction → expansion | Bandwidth in the lowest 10% of the last 250 days, then close above the upper band with range ≥ 1.5 × ATR and volume ≥ 1.2× | Close below SMA20 (after 5 days); time stop 40 | 10–30 days | Tightest prior contraction | 10 | Daily scan | 2.8–4.2% |
| **H008** | Relative strength (residual, market-adjusted) | Monthly: top 10 by 12-1 month *market-residual* return ÷ residual volatility (alpha/beta from 36 months; D074) | Leaves the top 20 at the monthly re-rank | 2–6 months | Residual score | 10 | Monthly + daily refill | 1.4–1.7% |
| **H009** | Volume anomaly | Volume ≥ 2.5 × 50-day median with a price move ≤ 1 ATR | Time: 20 days | 20 days | Volume ratio | 10 | Daily scan | ~4.2% (2.1% at 40 days) |
| **H010** | Gap / price structure | Overnight gap ≥ max(2%, 1.5 × ATR%), closes at or above the open, volume ≥ 2×; signal after the T close, buy at the T+1 open | Close below the gap day's low; time stop 40 | ≤ 40 days | Gap size in ATR units | 10 | Daily scan | ~2% |
| **H011** | Seasonality | Monthly: top 10 by average return in the coming calendar month over the past 5 years | Monthly re-rank | ~1 month | Seasonal score | 10 | Monthly + daily refill | 3.4–4.0% |

**Pre-declared variations.** Three per hypothesis, each changing one substantive thing:

| Hypothesis | v1.0 | v1.1 | v1.2 |
|---|---|---|---|
| H006 | base | 52-week-high breakout | no volume condition |
| H007 | bandwidth contraction | ATR-ratio contraction | no trend filter |
| H008 | 12-1, volatility-scaled | 6-1 | unscaled |
| H009 | 1-day shock, hold 20 | hold 40 | weekly formation |
| H010 | hold 40 | hold 60 | no "hold" condition |
| H011 | 5-year lags | 10-year lags | 5-year lags + SMA200 filter |

## 2. Why these are genuinely different

**From H001–H005:**

| C01 hypothesis | Nearest C02 idea | Why it is different |
|---|---|---|
| H001 short-term reversal (buy oversold, exit in days) | none | No C02 idea buys weakness. All hold for weeks to months. |
| H002 12-1 total-return momentum | **H008** (closest; acknowledged) | H008 ranks on the *stock-specific* (market-adjusted, residual) part of returns, scaled by its own noise; the long-only portfolio is not beta-hedged, so it picks different, lower-beta names. It tests under-reaction to firm news, not factor trend. |
| H003 proximity to the 52-week high (monthly ranking) | H006 v1.1 | H006 buys only on the *day of a fresh break* with volume, and exits on a trailing stop. It is an event trade, not a monthly ranking of whatever sits near its high. |
| H004 buying pullbacks in leaders | none | No C02 idea buys dips. |
| H005 low volatility (monthly ranking) | H007 | H007 buys the *end* of low volatility (the expansion) and exits within weeks. H005 held low-volatility stocks. |

**Among the C02 ideas:**

| Pair | Distinction |
|---|---|
| H006 vs H007 | New high, versus contraction then expansion anywhere in the range; different exits |
| H006 vs H010 | New high with no gap, versus gap with no new high; different exits |
| H009 vs H010 | Volume *without* a price move, versus a price gap *with* volume |
| H008 vs H011 | Trailing-year firm-specific return, versus same-calendar-month history (uncorrelated with momentum in the literature) |

The **overlap** of H006/H007/H010 trades (shared names and days) and the correlation of daily returns between all 18 variations will be reported.

**The trend + volatility family is deliberately not included** as a separate hypothesis. Its simple forms, for example "the lowest-volatility stocks in an uptrend", are what H005 v1.2 already tested, and pullback-in-trend forms are H004. A re-labelled version of a rejected idea would not be a new test.

## 3. Rules common to all C02 strategies

- **Account and portfolio (approved rules, unchanged).**
  - $100K; long only; no leverage or borrowing (D051); at most 10% per position; at least $5K per position; $7 per executed order; 10 bps slippage per side.
  - US common stocks only (point-in-time, including D057/D065); MarketCap ≥ $2B; price ≥ $5; ADV20 ≥ $5M.
  - Signal on completed day T; execution at the T+1 open.
- **10 slots** instead of the maximum 15. This is a strategy parameter within the approved rules.
  - At $100K a slot is then about $9.8K instead of $6.5K.
  - The $7 commission falls from about 0.11% to 0.07% per side, which cuts the round-trip cost from about 0.41% to about 0.34%.
  - C01 showed trading costs decide short-horizon ideas.
- **Daily slot refill.** Event-driven ideas scan every day. The monthly ideas (H008, H011) refill any slot freed between rebalances from the current ranking the next day. This removes the idle-cash drag C01's monthly strategies suffered under the no-borrowing rule; it is strategy logic, not an execution change.
- **Deterministic ranking.** Ties go by security identifier. Signals are code only.
- **Takeovers: no strategy-specific rules** *(amended 2026-09-29, owner clarification 2)*.
  - The draft's H006 jump exclusion and H010 15% gap cap were motivated by the H005 Validation findings, so they are **removed**. No C02 rule uses anything learned from 2018–2021.
  - Takeovers and delistings are handled only by the general data-integrity rules, applied identically to every strategy and using only information available on the decision date: LEAN's delisting liquidation, the re-issue of LEAN-cancelled sells (D054) and the dead-position fallback (D062).
  - H007's range/volume expansion and H009's price-move cap stay: they define the event each hypothesis is about (as in the cited literature), not a takeover filter.
  - The share of trades ending in a takeover cash-out is still **reported** for every run, as a diagnostic only.

## 4. Infrastructure needed before any C02 strategy run

These are **verification work, not trials**, each with tests plus a canary run.

1. **Open/high/low price windows.** The harness keeps only adjusted close and volume today. H006, H007 and H010 need open, high and low, adjusted and point in time. Tests: the look-ahead truncation test extended to OHLC; a canary checking a gap signal uses only T and T−1 data and executes at T+1.
2. **Long look-backs (H011).** Monthly returns over 5–10 years per stock. A memory and runtime check, plus a truncation test.
3. **Residual computation (H008).** Rolling regression on SPY, unit-tested against a reference calculation.
4. **A shared "event slot manager"** (entry ranking, daily refill, time and trailing stops), unit-tested including no-borrowing interaction.

The engine stays pinned to LEAN build 18131. QuantConnect moves master to the new dataset on 2026-10-10 and retires the old dataset on 2026-10-31. Build 18131 already carries the new dataset. If QuantConnect retires the build itself, I will stop and report before switching.

## 5. Experiment budget (fixed now)

| Category | Planned | Cap |
|---|---|---|
| Strategy-selection trials (6 hypotheses × 3 variations, IS) | **18** | 18 (no additions) |
| 2× slippage screen runs (only for variations passing all other screen items) | 0–18 | 18 |
| Robustness battery (best passing variation of at most **2** hypotheses: 4× and 6× slippage + 8 plateau perturbations) | 0–20 | 20 |
| **Total C02 strategy backtests** | **18–56** | **56** |
| Technical retries (operational failures, reproductions) | as needed, reported separately | — |
| Verification / canary runs (§4) | as needed | — |

- If more than two hypotheses pass the screen, the two with the highest net IS Sharpe get the robustness battery; the others are reported as passing the screen only.
- Hitting a cap means stop and report, not extend.

## 6. Trial accounting and statistics (fixed before any C02 result)

*(Amended 2026-09-29, owner clarification 1. Frozen as **D069** before any C02 result; implemented in `registry.trial_accounting`, `registry.dsr_trial_count` and `cycle.dsr_inputs`, and pinned by tests.)*

**Categories.** Every run in `experiments/INDEX.csv` falls into exactly one. A "configuration" is the D066 key: hypothesis, strategy, version, parameters, split, dates and cost-stress multiple.

| # | Category | Definition | Count before C02 |
|---|---|---|---|
| S | **Selection candidates** | Distinct IS configurations at base costs: the pre-declared variations from which a candidate could be chosen | **19** (C01) |
| R | Robustness perturbations | Cost-stress (2×/4×/6× slippage) and plateau runs of an already-chosen variation; they can only reject it, never choose | 15 |
| V | Validation runs | Out-of-sample evaluations of a frozen candidate (accept/reject only) | 1 (E005-28) |
| T | Technical repeats | Further runs of an identical configuration: re-runs after infrastructure fixes, operational retries, reproductions, the H001 remedial re-test | 46 |
| X | Verification / canary / benchmark / probe | Infrastructure runs; not strategies | 37 |
| – | Not started | Annotated `not_started`: no backtest ran | 7 |

**Deflated Sharpe (Validation gate, DSR ≥ 0.90 on IS + VAL).**

- **Official N = S, cumulative over all cycles** (19 today; 37 after the 18 C02 selection trials).
- *Why S and only S.* DSR asks: "how high would the best Sharpe be by luck, if we compared N candidates with no real skill?" The selection candidates are exactly the set compared to choose a winner.
  - Robustness perturbations are run only on a variation that has already been chosen; they can reject it but never pick a different one. Counting them would also add near-duplicates of the chosen strategy.
  - A Validation run tests one frozen candidate; it selects nothing.
  - Technical repeats re-run the same configuration, so they add no new candidate.
  - Verification and canary runs are not strategies.
- *Why cumulative.* C02's design uses what C01's IS results taught (10 slots, multi-week holds, daily refill), so C01's candidates are part of the same search.
- *Direction of error.* The 3 variations of a hypothesis are correlated, so S overstates the number of *independent* tries. That makes N conservative; no correction for correlation is applied.
- **Conservative count = S + R + V** (35 today). It is reported beside every DSR, with a DSR computed on it, but it is **never mixed** into the official figure and never decides a gate.
- **Change from C01, disclosed.** The C01 Validation (E005-28) used every started research run as N (77). That report stays as published. D069 applies from C02 on.
- **Sharpe dispersion** (the variance input to DSR) = the variance of the daily Sharpe across the latest valid (not retired) run of every selection candidate counted in N.

**PBO (Validation gate, PBO ≤ 0.30).** *(Frozen 2026-09-29, D073/D075, owner-approved before any C02 result: the hard gate is PBO ≤ 0.30 computed across all 18 C02 selection candidates; the per-hypothesis 3-variation PBO below is a diagnostic only. See `C02_pbo_definition.md`.)*

- **Per hypothesis:** combinatorially symmetric cross-validation (16 blocks) on the IS daily returns of that hypothesis's 3 variations, exactly as in C01 (definition unchanged: at or below the median counts as overfit).
- *C01 lesson:* with near-identical variations, PBO is uninformative. C02's variations are therefore designed to differ in one *substantive* dimension each. If two variations of a hypothesis still have daily-return correlation above 0.95, this is reported next to the PBO.
- **Cycle level (diagnostic, not a gate):** PBO across all 18 C02 variations, which measures the risk of picking the best of the whole cycle.

**No change after results.** These definitions are frozen with the plan's approval and recorded as a decision.

## 7. Gates (unchanged) and new diagnostics (not gates)

**Unchanged.**

- The C01 IS screen (D036), including Sharpe ≥ 0.4 at 2× slippage.
- The robustness gate: at least 80% of perturbations keep at least 70% of the base Sharpe; Sharpe > 0 at 4× costs; every third of IS positive.
- The Validation gates, including DSR and PBO.

**New diagnostics**, reported for every variation from C02 on. They exist to make failure modes visible early and never decide pass or fail:

| Diagnostic | Why |
|---|---|
| Average invested % and cash % | C01/H005: low exposure flattered drawdown |
| Beta, alpha and alpha t-stat versus equal-weight; equal-weight at the same exposure | CP4 method, applied at IS already |
| Share of trades ending in a takeover cash-out; share of return from dividends | CP4: takeover-pinned names and distributions drove H005 |
| Commission and slippage drag per year; average profit per trade vs. round-trip cost | C01: costs decided H001/H004 |
| Trade overlap and return correlation between variations and hypotheses | Distinctness check |

## 8. Procedure and stopping rules

1. On approval: build and verify the §4 infrastructure (tests + canaries). Report any problem before any strategy run.
2. Run the 18 selection trials once each, from a committed tree, with the corrected harness. All results are recorded, including failures.
3. Apply the IS screen to all 18. Run 2× slippage only for variations passing every other item.
4. Run the robustness battery for at most 2 hypotheses (§5), with the pre-declared perturbations from each hypothesis file.
5. **STOP at a C02 checkpoint report.** No Validation, Walk-Forward or Holdout access. No promotion without your approval.
6. **Reject rather than tune.**
   - Each hypothesis file states what result falsifies it.
   - A falsified hypothesis is closed. No new filters, parameters, stops or variations may be added in C02 after seeing results.
   - Any new idea belongs to a later cycle, with its own written hypothesis, and counts as a new trial.

## 9. Hindsight and data statement

- All six ideas come from literature or reasoning published before 2018. None is motivated by events or results after 2017.
- Nothing from 2018–2026 was looked at to design them. No Validation or Holdout data was accessed.
- **Disclosed:** two design choices use knowledge from **C01's in-sample results**:
  - 10 slots and multi-week holds, because costs killed short holds;
  - daily refill, because of the cash drag.
- That is legitimate in-sample learning, but it means C02 is not independent of C01. This is why the trial count for DSR is cumulative across cycles.

## 10. Owner decisions (2026-09-29)

**Approved:**

1. H006–H011 and their 18 pre-declared variations.
2. **10 slots** as the C02 standard and **daily slot refill**.
3. $100K, long-only, no leverage, with the existing cost and universe rules.
4. The budget of **at most 56 C02 strategy backtests**.
5. The §4 infrastructure work and canary tests.
6. **H011 v1.1:** the 10-year look-back reading 2000–2009 prices is approved **only as signal warm-up/history**. It may not be used for parameter selection, hypothesis selection or tuning. Universe eligibility and the IS evaluation still begin in 2010.

**Clarifications required before any strategy backtest** (all incorporated above):

1. Trial accounting for DSR: categories separated, N defined and frozen before any C02 result (§6, D069).
2. Takeovers: no alpha filter derived from the H005 Validation outcome; only general data-integrity rules, applied to all strategies with information available on the decision date (§3).
3. H010 timing: the signal needs the close of gap day T, so it is known only after T completes, and execution is no earlier than the T+1 open (H010.md "Timing"; tests in `tests/test_c02_signals.py`).

**Order of work:** infrastructure, tests and canaries first → prerequisite checkpoint with the finalized trial accounting → owner approval → only then the 18 selection trials.
