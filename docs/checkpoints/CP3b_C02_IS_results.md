# Research Cycle 2 (C02): in-sample results checkpoint

> **Superseded by `CP3c_C02_final_report.md` (2026-09-30), which includes the three time-stop runs completed afterwards (E007-12 recovered, E007-13, E007-14). The verdict is unchanged.**

| Field | Value |
|---|---|
| Date | 2026-09-30 |
| Status | **STOP. Awaiting owner review.** No Validation, Walk-Forward or Holdout run was made or is planned without approval. |
| Period | IS only: 2010-01-04 → 2017-12-29. The first ~20 sessions of January 2010 have no eligible stocks because the universe's liquidity filter needs 20 days of history. The same was true in C01. |
| Recommended outcome | **C02: No Production Candidate Found** (§1) |
| Open item | One QuantConnect backtest (E007-16) is stuck and blocks the only backtest node. Deleting it needs your approval (§6). |

## 1. Summary

1. **All 18 pre-declared selection trials ran once each**, under the approved plan, harness and costs.
2. **17 of 18 fail the IS screen.** Every one fails "Sharpe ≥ equal-weight Sharpe + 0.10" (the benchmark's IS Sharpe is 0.92), and most fail further items.
3. **One passes the screen: H007 v1.1 (E007-02)**, entering at a volatility-contraction breakout with contraction measured as ATR10/ATR100 ≤ 0.6.
   - Sharpe 1.12, max drawdown −5.1%.
   - But it is only **21% invested** on average, and its CAGR is 5.4%.
   - It also passes the 2× slippage item (Sharpe 1.01).
4. **It fails the robustness gate** (pre-declared battery, approved criteria).
   - 3 of the 8 parameter perturbations fall below 70% of the base Sharpe; at most 1 may fail.
   - The result depends sharply on the contraction threshold. As the ATR ratio goes from 0.3 to 0.9, trades go from 30 to 897, exposure from 2% to 77%, and Sharpe from −0.10 up to 0.86 (base 1.12). That is a peak, not a plateau.
   - The three still-missing time-stop runs cannot change this (§6).
5. **Frozen cycle-level PBO (D073) = 0.268, which passes ≤ 0.30.** This only says the cycle's in-sample winner was not a pure artefact of selection. It does not rescue a candidate that fails robustness.
6. **Recommendation: C02 ends with "No Production Candidate Found".** Nothing goes to Validation, and nothing is tuned or added.

## 2. The 18 selection trials (IS 2010–2017, $100K, 10 slots, $7/order, 10 bps slippage)

Equal-weight ≥ $2B benchmark (E901-07): Sharpe 0.92, CAGR 13.9%, max drawdown −22.3%. SPY: Sharpe 0.95, CAGR 13.3%.

| Run | Variation | Sharpe | CAGR | Max DD | Trades | Profit factor | Invested | DSR (N = 37) | Screen |
|---|---|---|---|---|---|---|---|---|---|
| E006-01 | H006 v1.0 breakout 55-day | 0.88 | 12.2% | −19.3% | 529 | 1.46 | 91% | 0.28 | fail |
| E006-02 | H006 v1.1 52-week high | 0.74 | 9.8% | −24.3% | 519 | 1.39 | 91% | 0.17 | fail |
| E006-03 | H006 v1.2 no volume | 0.90 | 12.3% | −22.7% | 517 | 1.53 | 91% | 0.31 | fail |
| E007-01 | H007 v1.0 bandwidth squeeze | 0.56 | 6.0% | −16.8% | 911 | 1.14 | 77% | 0.07 | fail |
| **E007-02** | **H007 v1.1 ATR-ratio squeeze** | **1.12** | **5.4%** | **−5.1%** | **223** | **2.46** | **21%** | **0.54** | **PASS** |
| E007-03 | H007 v1.2 no trend filter | 0.50 | 5.4% | −19.0% | 941 | 1.10 | 78% | 0.05 | fail |
| E008-01 | H008 v1.0 residual 12-1 | 0.57 | 9.2% | −26.2% | 429 | 1.36 | 89% | 0.07 | fail |
| E008-02 | H008 v1.1 residual 6-1 | 0.69 | 10.6% | −26.0% | 566 | 1.33 | 86% | 0.14 | fail |
| E008-03 | H008 v1.2 unscaled | 0.67 | 14.9% | −33.6% | 287 | 1.47 | 91% | 0.12 | fail |
| E009-04* | H009 v1.0 volume shock, hold 20 | 0.67 | 9.1% | −20.4% | 907 | 1.23 | 89% | 0.12 | fail |
| E009-02 | H009 v1.1 hold 40 | 1.01 | 14.4% | −20.7% | 482 | 1.57 | 91% | 0.41 | fail |
| E009-03 | H009 v1.2 weekly formation | 1.00 | 13.4% | −16.6% | 901 | 1.52 | 89% | 0.41 | fail |
| E010-01 | H010 v1.0 gap-and-hold, hold 40 | 0.59 | 6.9% | −19.1% | 711 | 1.18 | 83% | 0.08 | fail |
| E010-02 | H010 v1.1 hold 60 | 0.68 | 8.6% | −21.7% | 534 | 1.25 | 85% | 0.13 | fail |
| E010-03 | H010 v1.2 no hold condition | 0.51 | 6.1% | −21.5% | 871 | 1.19 | 86% | 0.06 | fail |
| E011-01 | H011 v1.0 seasonality 5 y | 0.17 | 1.3% | −43.3% | 885 | 1.03 | 80% | 0.01 | fail |
| E011-02 | H011 v1.1 seasonality 10 y | 0.67 | 11.2% | −43.0% | 887 | 1.25 | 80% | 0.12 | fail |
| E011-03 | H011 v1.2 5 y + SMA200 | 0.25 | 2.9% | −41.7% | 882 | 1.06 | 80% | 0.01 | fail |

\*E009-04 is the identical re-run of E009-01. E009-01's local runner was lost in a container restart, so its result was never downloaded; it is recorded as an operational failure (§6).

Gate-by-gate results are in `research/cycles/C02_is_gates.json`; the full table is in `research/cycles/C02_is_results.csv`.

**Items failed (besides Sharpe vs EW, which all 17 fail):**

- **H006:** max drawdown (v1.1, v1.2); expectancy without the best 5% of trades (v1.0, v1.1).
- **H007 v1.0 / v1.2:** profit factor, expectancy confidence interval, largest-year share, expectancy without the best 5%; v1.2 also Sharpe < 0.5.
- **H008:** max drawdown in all three; stress episodes (v1.0, v1.2); expectancy without the best 5%.
- **H009:** v1.1 and v1.2 fail **only** Sharpe vs EW + 0.10 (1.01 and 1.00 against a required 1.02). v1.0 also fails expectancy without the best 5%.
- **H010:** profit factor or expectancy items in all three.
- **H011:** max drawdown of about 43% (in 2015–16) in all three, plus many other items.

## 3. Statistics (definitions frozen before any C02 result)

- **Deflated Sharpe, N = 37** (19 C01 + 18 C02 selection candidates, D069).
  - The best IS DSR is E007-02 at 0.54, well below the 0.90 Validation gate. That gate is computed on IS + Validation and was not reached.
  - Conservative count N = 62: DSR 0.46.
- **Cycle-level PBO (hard gate, D073): 0.268**, which passes ≤ 0.30.
- **Per-hypothesis 3-variation PBO (diagnostic only):** H006 0.91, H007 0.12, H008 0.97, H009 0.97, H010 0.71, H011 0.06. As analysed before C02, these mostly reflect how different the three siblings are.
- **Return correlations within each hypothesis:** H006 0.82–0.87, H008 0.72–0.83, H009 0.74–0.76, H010 0.81–0.86, H011 0.81–0.90. H007 v1.1 correlates only 0.34–0.37 with its siblings, because it is a very different, mostly-cash portfolio.

## 4. H007 v1.1 (E007-02): the only screen pass

**Diagnostics (not gates):**

- **Exposure:** 21% invested on average. The equal-weight benchmark held at the same daily exposure earns Sharpe 0.64 and CAGR 2.3%, against E007-02's 1.12 and 5.4%.
- **Market sensitivity:** beta to equal-weight 0.10; annual alpha +4.0% (t = 2.48).
- **Takeovers:** 13.5% of trades end in a forced cash-out at delisting; they carry 10.5% of trade profit. A contraction followed by a jump on heavy volume is also what a takeover announcement looks like. Per owner clarification 2, nothing was filtered; this is reported only.
- **Overlap:** trades barely overlap H006 or H010 (5–6 shared stock-weeks); correlation with other C02 variations about 0.3.
- **Profit per trade:** 1.87% on average, about 0.34% round-trip cost.

**Robustness battery** (pre-declared in `research/cycles/C02_robustness_plan.md` before any run):

| Test | Run | Sharpe | Trades | Invested | Criterion | Result |
|---|---|---|---|---|---|---|
| 2× slippage | E007-04 | 1.01 | 223 | 21% | ≥ 0.4 (screen item) | pass |
| 4× slippage | E007-15 (repeat of E007-05) | 0.80 | 223 | 21% | > 0 | pass |
| 6× slippage | E007-06 | 0.59 | 223 | 21% | reported only | — |
| ATR ratio 0.3 | E007-07 | −0.10 | 30 | 2% | ≥ 0.782 | **fail** |
| ATR ratio 0.48 | E007-08 | 0.41 | 51 | 4% | ≥ 0.782 | **fail** |
| ATR ratio 0.72 | E007-09 | 0.69 | 565 | 49% | ≥ 0.782 | **fail** |
| ATR ratio 0.9 | E007-10 | 0.86 | 897 | 77% | ≥ 0.782 | pass |
| Time stop 20 | E007-11 | 1.09 | 236 | 18% | ≥ 0.782 | pass |
| Time stop 32 | E007-12 → E007-16 | not available (§6) | | | ≥ 0.782 | — |
| Time stop 48 | E007-13 | not run (§6) | | | ≥ 0.782 | — |
| Time stop 60 | E007-14 | not run (§6) | | | ≥ 0.782 | — |
| Thirds of IS | E007-02 | 1.19 / 1.06 / 1.17 | | | each > 0 | pass |

**Verdict:** the plateau criterion needs at least 7 of 8 perturbations to keep Sharpe ≥ 0.782. Three have failed, so at most 5 of 8 can pass. **The robustness gate fails.**

**Reading.** The base setting (0.6) sits on a narrow peak.

- Loosen the threshold and the portfolio becomes an ordinary, mostly invested momentum-like book with a Sharpe below the benchmark's.
- Tighten it and almost no trades occur.
- The attractive base result mostly comes from being in cash about 80% of the time and picking a few quiet stocks that break out, some of them takeover targets. That is not a robust edge.

## 5. Hypothesis-level falsification (as written before C02)

| Hypothesis | Pre-declared test | Outcome |
|---|---|---|
| H006 breakout | Reject if v1.0 and v1.1 fail the screen **and** have profit factor < 1.2 or expectancy CI ≤ 0 | Both fail the screen, but profit factors are 1.46 / 1.39 and CI lower bounds are +0.66% / +0.43%, so **not formally rejected**. Its two claims are falsified: *volume* (v1.2 without volume has a higher Sharpe, 0.90 vs 0.88) and *52-week anchor* (v1.1 0.74 < v1.0 0.88). No candidate. |
| H007 squeeze | Reject if all three fail the screen | v1.1 passed the screen but **fails robustness**. No candidate. |
| H008 residual RS | Reject if all three fail the screen | **Rejected.** |
| H009 volume shock | Reject if all three fail the screen | **Rejected.** v1.1 and v1.2 missed only the benchmark-plus-0.10 Sharpe item, by 0.01–0.02. That is recorded as a near miss, and per protocol it is not revisited. |
| H010 gap-and-hold | Reject if all three fail the screen | **Rejected.** The "acceptance" story is not falsified (v1.2 without the hold condition 0.51 < v1.0 0.59), but no variation is viable. |
| H011 seasonality | Reject if all three fail the screen | **Rejected.** |

## 6. Operational incidents (no effect on any recorded result)

- **Container restarts (3).** The container running the local runner restarted three times. Each time the runner process was lost mid-backtest.
  - E009-01, E007-05 and E007-12 are recorded as operational failures, with their QuantConnect backtest IDs kept (not deleted).
  - Identical re-runs: E009-04, E007-15, E007-16. These are technical repeats under D069, not extra trials.
- **Stuck backtest (open).** E007-16 (time stop 32) has been stuck at 0% on QuantConnect since 06:19 UTC.
  - Reading its status hangs, while other API calls work. The runner recorded it as failed (API read timeouts).
  - It occupies the only backtest node, so E007-13 and E007-14 could not start.
  - **Deleting it needs your approval (D053).** The three missing time-stop runs cannot change the robustness verdict.
- **Late fill data.** QuantConnect published fill details late twice (E007-01 and E007-07, 71–77 minutes). The runner waited, as designed, and the downloads were complete.
- **Warnings.** Two runs (E009-02, E009-03) ended `completed_with_warnings`: holdings closed at their last real price after 10 sessions with no data. That is the approved general rule (D062), applied to all strategies.

## 7. Totals

- **Hypotheses:** 11 (H001–H011), all tested; 0 production candidates.
- **Research strategies:** 11 (S001–S011).
- **Registry:** 164 runs, 161 experiment IDs (research 118, infrastructure 29, benchmark 14, demo 3).
- **Trial accounting (D069):**
  - 37 selection candidates (DSR N);
  - 24 robustness runs;
  - 1 Validation run;
  - 49 technical repeats;
  - 7 not started;
  - 43 verification/benchmark runs.
- **C02 strategy backtests:** 18 selection + 11 robustness, 29 in total, within the 56 cap (repeats of lost runs are counted separately).

## 8. Decisions needed

1. **Accept the C02 outcome: No Production Candidate Found.** Nothing is promoted to Validation.
2. **E007-16:** approve deleting the stuck QuantConnect backtest to free the node. Or wait longer. The remaining time-stop runs (E007-16, E007-13, E007-14) are then either completed for the record, or formally recorded as not run. They cannot change the verdict.
3. **Next step:** close the research phase with a final report, or authorise planning a further cycle (C03). Any new idea would need its own written hypothesis and would add to the cumulative trial count (N = 37 so far).
