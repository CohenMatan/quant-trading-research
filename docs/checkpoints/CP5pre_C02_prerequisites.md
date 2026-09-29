# C02 prerequisite checkpoint: infrastructure, tests, canaries and the frozen trial count

| Field | Value |
|---|---|
| Date | 2026-09-29 |
| Status | **STOP. Awaiting owner approval before any of the 18 C02 strategy backtests.** |
| Scope | The work the owner required before C02 strategy runs: infrastructure, tests, canaries, the three clarifications, and the finalized trial accounting |
| Strategy backtests run | **None.** The 18 C02 configurations exist and pass validation and dry runs; none has been sent to QuantConnect. |

## 1. Summary

1. **The trial count for the Deflated Sharpe Ratio is defined and frozen (D069).** Official N = distinct in-sample selection candidates, cumulative over all cycles: **19 today, 37 after C02.** A conservative count (selection + robustness + Validation = **35 today**) is reported beside it, never mixed in (§2).
2. **Takeovers:** no rule derived from the H005 Validation remains. The H006 "takeover-style jump" exclusion and the H010 "gap ≤ 15%" cap were removed. Only the general data-integrity rules apply, to every strategy (§3).
3. **H010 timing:** the signal needs day T's close, so it exists only after T is complete; the buy executes at the T+1 open at the earliest. This is stated in `H010.md` and proven by unit tests and on QuantConnect (§4).
4. **Infrastructure:** built and unit-tested (305 tests pass), and verified on QuantConnect by canaries X959 and X960. The canaries found **one real defect**, now fixed and re-verified: volume histories mixed two scaling conventions after dividends and spin-offs (D072) (§5).
5. **One strategy bug caught before any run:** S008 v1.1 (6-1 month) would never have produced a score (D071) (§6).

**Everything the owner listed as a prerequisite passes** (table in §7). Next step, on approval only: run the 18 selection trials.

## 2. Trial accounting (D069), frozen before any C02 result

Every run in the registry falls into exactly one category. A "configuration" means the same hypothesis, strategy version, parameters, data period and cost level.

| # | Category | What it is | Selects a candidate? | Count now |
|---|---|---|---|---|
| S | **Selection candidates** | Distinct in-sample configurations at normal costs: the pre-declared variations | **Yes** | **19** (all C01) |
| R | Robustness perturbations | Higher-cost and "nearby parameter" runs of a variation already chosen | No, can only reject it | 15 |
| V | Validation runs | One out-of-sample test of a frozen candidate | No, accept/reject only | 1 (E005-28) |
| T | Technical repeats | The same configuration run again (fixes, retries, reproductions, the H001 remedial re-test) | No new candidate | 46 |
| X | Verification / canary / benchmark | Infrastructure checks, not strategies | — | 41 (incl. the 4 canaries of this checkpoint) |
| – | Not started | QuantConnect never ran the backtest | — | 7 |

**Official N for DSR = S, cumulative across cycles.**

- *Why.* DSR asks how high the best Sharpe ratio would be by pure luck if N candidates with no skill were compared. The candidates compared to pick a winner are exactly the selection candidates.
  - Robustness runs are made only after a variation is chosen; they can reject it but never pick another.
  - A Validation run tests one frozen candidate.
  - Repeats add no new candidate; canaries are not strategies.
- *Why cumulative.* C02's design uses lessons from C01's in-sample results (10 positions, multi-week holds, daily refill), so C01's candidates are part of the same search.
- *Direction of error.* The three variations of a hypothesis are related, so N overstates the number of truly independent tries. That makes the test stricter, not looser.
- **Conservative count = S + R + V** (35 now). Every report shows a second DSR on this count, clearly labelled. It never decides a gate.
- **Sharpe dispersion** (the other DSR input) = the spread of daily Sharpe across the latest valid run of every selection candidate (19 values now).
- The C01 Validation report (E005-28) used N = 77 (every started run). It stays as published; D069 applies from C02 on.

Implemented in code (`registry.trial_category`, `registry.trial_accounting`, `registry.dsr_trial_count`, `cycle.dsr_inputs`). The counts above are pinned by a test, so any accidental change fails the test suite.

## 3. Takeover handling (clarification 2)

- **Removed:** the H006 exclusion of "takeover-style jumps" and the H010 cap "gap ≤ 15%". Both were motivated by what the H005 Validation showed, so keeping them would have used 2018–2021 information.
- **What remains**, for every strategy, using only information available on the decision date:
  - LEAN's liquidation at a delisting;
  - re-issuing sells that LEAN cancels on ticker changes (D054);
  - closing a holding at its last real price after 10 sessions with no data (D062).
- H007's range and volume expansion and H009's "no big price move" condition stay. They define the event each hypothesis is about, as in the cited literature; they are not takeover filters.
- The share of trades ending in a takeover cash-out is still **reported** for every run, as a diagnostic only.

## 4. H010 timing (clarification 3)

- **Rule** (`research/hypotheses/H010.md`, "Timing"): the gap day is T. The signal uses T's open, close, low and volume, so it can only be computed after T closes. The order is a next-open order for T+1. The baselines (ATR, average volume) use bars ending T−1.
- **Unit tests** (`tests/test_c02_signals.py`):
  - the same gap gives a signal if T closes above its open and none if it closes below, so the decision needs close_T;
  - with data only up to T−1 there is never a signal;
  - the strategy places orders only through the harness's next-open mechanism, from the daily close hook;
  - look-ahead truncation tests pass for all C02 signals.
- **On QuantConnect** (canary X959, a toy gap signal of the same kind): 0 timing violations. Every fill is after its signal day and at the next open's price.

## 5. Infrastructure and canaries

**Built** (all opt-in; the C01 strategies are unaffected):

- open/high/low price histories;
- a store of month-end closes;
- tracking of each position's entry day;
- a daily "sell exits, refill free slots" step (exiting positions keep their slot until sold, the approved no-borrowing rule);
- a last-trading-day-of-month flag;
- a shared module of indicator formulas.

**Canaries on QuantConnect** (IS dates only; infrastructure, not trials):

| Run | What it checked | Result |
|---|---|---|
| E960-01 | Month-end closes for 8 stocks, 2010–2014, vs fresh QuantConnect history | **Pass.** 63,840 months compared: every month present and correct. The current month never leaks into the store (no look-ahead). 134 months available at the 2010 start (120 needed for H011's 10-year look-back). Largest value difference 0.058%, from tiny dividend rounding (see note). |
| E959-01 | OHLC histories vs fresh history (incl. AAPL 7:1 split, 2014); signal timing; entry tracking; month-end flag | Timing, entry tracking and month-end flag **pass**. History comparison found differences to explain. |
| E959-02 | Same, with a per-column diagnosis | Prices: at most 0.013% off, no misalignment. **Volume: a real defect** (below). |
| E959-03 | Same, after the fix | **Pass.** 53,990 values compared (open, high, low, close and volume), with no misalignment. Every value within 0.013% of fresh history (dividend rounding only). Timing: 0 violations. Entry day: 203/203. Gap-day low: 812/812. Month-end flag: 0 errors. AAPL split handled. |

**The defect (D072).**

- *What:* QuantConnect's history scales old volumes after dividends and spin-offs, but the harness scaled volume only after splits. A volume history could therefore mix two scales: older bars loaded from QuantConnect's history, and newer bars added day by day.
  - Dividends cause differences of under 1%.
  - A spin-off can cause a large one: Agilent/Keysight in 2014 was 29%.
- *Why it matters:* H006, H007, H009 and H010 compare today's volume with a recent average, so the two scales could bias those comparisons for stocks with a recent spin-off.
- *Fix:* the harness now scales volume exactly as QuantConnect's history does, so both parts of every history share one scale. It is unit-tested and re-verified on QuantConnect (E959-03).
- No research result is affected: no C02 strategy has run, and C01 strategies did not use volume ratios.

**Note on dividend rounding (accepted, no change).** The harness adjusts prices for each dividend with the standard factor (1 − dividend ÷ previous close). QuantConnect's own factor differs in the fifth decimal place. After 5 years of dividends the difference is at most 0.06%. That is far below any threshold in the C02 rules (the smallest is a 2% gap), so it cannot change a signal. It is disclosed, not fixed.

## 6. Strategy review before any run

- **S008 v1.1 bug fixed (D071).** A fixed minimum of 200 observations would have made the 6-1 month variation (105 observations) never score a stock. The minimum now scales with the window, and a test checks v1.1 against a reference regression.
- **Entry-day counting made robust (D071).** "Days held" is 0 on the fill day whatever the order in which QuantConnect delivers the fill and the day's price bar. X959 confirmed this on 203 of 203 entries, and the gap-day low was read back correctly 812 of 812 times.
- **All 18 configurations** (E006-01 … E011-03) pass config validation and dry runs from a committed tree:
  - IS 2010-01-04 → 2017-12-29;
  - $100K; the approved no-borrowing portfolio rules; 10 slots;
  - $7 per order; 10 bps slippage; LEAN build 18131.

## 7. Prerequisite checklist

| Owner requirement | Status |
|---|---|
| Trial accounting finalized, categories separated, N defined and frozen before C02 results | **Done** (§2, D069; test-pinned) |
| No takeover filter from the H005 Validation; only general data-integrity rules | **Done** (§3) |
| H010 timing verified in spec and tests | **Done** (§4) |
| H011 10-year look-back only as warm-up; eligibility and evaluation from 2010 | **Done.** Recorded in `H011.md`; the config starts 2010-01-04; E960-01 confirms 134 months of warm-up history. |
| Infrastructure built and tested | **Done.** 305 tests pass. |
| Canaries | **Pass** after the D072 fix (§5) |
| No C02 strategy backtest run | **Confirmed.** 0 of 18. |

## 8. Totals (for the record)

- **Hypotheses:** 11 written (H001–H011). 5 were tested in C01 (all rejected); 6 are approved for C02 and not yet tested.
- **Strategies:** 11 research strategies (S001–S011); S006–S011 have not been run.
- **Registry:** 132 recorded runs (129 experiment IDs): 88 research, 27 infrastructure, 14 benchmark, 3 demo.
  - Research runs: 19 selection candidates, 15 robustness runs, 1 Validation run, 46 technical repeats and 7 not started.

## 9. Decision needed

**Approve starting the 18 C02 selection trials** (E006-01 … E011-03), once each, under the approved plan and the frozen D069 trial accounting. I will stop again at the C02 checkpoint report.
