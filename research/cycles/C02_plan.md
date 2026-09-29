# Research Cycle 2 (C02): plan for owner approval

| Field | Value |
|---|---|
| Status | **PROPOSED. Awaiting owner approval.** No C02 strategy backtest has been run or will be run before approval. |
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
- **No gate or threshold changes.** C01's screening and robustness rules apply unchanged. I propose only extra *diagnostics* (§7), and one clarification of the trial-count definition for Deflated Sharpe (§6), which needs your approval.

## 1. The six hypotheses at a glance

| ID | Family | Entry | Exit | Expected hold | Selection | Slots | Rebalance | Est. cost per year |
|---|---|---|---|---|---|---|---|---|
| **H006** | Breakout / price expansion | Close above the prior 55-day high, volume ≥ 1.5× average, above SMA200, not a takeover-style jump | Trailing stop: highest close − 3 × ATR20; time stop 60 | 20–50 days | Breakout size in ATR units | 10 | Daily scan | 2.1–2.8% |
| **H007** | Volatility contraction → expansion | Bandwidth in the lowest 10% of the last 250 days, then close above the upper band with range ≥ 1.5 × ATR and volume ≥ 1.2× | Close below SMA20 (after 5 days); time stop 40 | 10–30 days | Tightest prior contraction | 10 | Daily scan | 2.8–4.2% |
| **H008** | Relative strength (residual) | Monthly: top 10 by 12-1 month *market-residual* return ÷ residual volatility | Leaves the top 20 at the monthly re-rank | 2–6 months | Residual score | 10 | Monthly + daily refill | 1.4–1.7% |
| **H009** | Volume anomaly | Volume ≥ 2.5 × 50-day median with a price move ≤ 1 ATR | Time: 20 days | 20 days | Volume ratio | 10 | Daily scan | ~4.2% (2.1% at 40 days) |
| **H010** | Gap / price structure | Overnight gap ≥ max(2%, 1.5 × ATR%) and ≤ 15%, closes at or above the open, volume ≥ 2× | Close below the gap day's low; time stop 40 | ≤ 40 days | Gap size in ATR units | 10 | Daily scan | ~2% |
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
| H002 12-1 total-return momentum | **H008** (closest; acknowledged) | H008 ranks on the *stock-specific* part of returns, beta-neutral and scaled by its own noise, so it picks different, lower-beta names. It tests under-reaction to firm news, not factor trend. |
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
- **Takeover-target defences.** Pinned acquisition targets contaminated C01's low-volatility results. Each event rule excludes price jumps typical of takeover bids (H006 jump cap, H010 15% gap cap) or requires a real range expansion (H007, H009). The share of trades that end in a takeover cash-out is reported for every run.

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

**Categories.** These follow the D066 definitions, with robustness now separated out:

1. **Strategy-selection trials:** each distinct pre-declared variation run on IS (C01: 19; C02: 18).
2. **Robustness checks:** cost-stress and plateau runs of an already-chosen variation (C01: 15). Never used to select.
3. **Technical retries:** re-runs of an identical configuration after infrastructure fixes, operational failures or reproductions (C01: 46, including the 5 H001 remedial runs).
4. **Verification / canary / benchmark / probe runs:** infrastructure, never trials (37 so far).

**Deflated Sharpe (Validation gate, DSR ≥ 0.90 on IS + VAL).**

- **N = all genuine trials across the project** = selection trials + robustness checks + Validation runs (D066's `genuine_trials`), counted at the time of evaluation.
  - Today N = 35.
  - After C02's selection trials it will be at least 53.
- *Why count robustness runs:* a plateau perturbation is still a configuration someone looked at. Counting it is conservative, and it is the definition C01 already reported under D066.
- **This changes the number used at C01's Validation (E005-28).** That evaluation used every started research run, 77 including technical repeats. Technical retries re-run the *same* configuration, so they add no selection opportunity. Counting them inflated N without statistical basis.
- **I propose the D066 count as the official N from C02 on. It needs your approval.** Both numbers will be reported side by side, so the change is always visible.
- **Sharpe dispersion** (the variance input to DSR) = variance of daily Sharpe across the latest valid run of every selection trial counted in N.

**PBO (Validation gate, PBO ≤ 0.30).**

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

## 10. Decisions needed from you

1. Approve the six hypotheses and their 18 pre-declared variations as written.
2. Approve **10 slots** as the C02 standard (within the approved ≤ 15), and the **daily refill** logic for the monthly strategies.
3. Approve the **Deflated Sharpe trial count** from C02 on: N = all genuine trials (selection + robustness + Validation), with technical retries and verification excluded (§6).
4. Confirm that **H011 v1.1** may read 2000–2009 prices as signal look-back only (no selection), or choose the fallback L = 3.
5. Approve the experiment budget (**at most 56 C02 strategy backtests**; robustness for at most 2 hypotheses) and the §4 infrastructure work.
