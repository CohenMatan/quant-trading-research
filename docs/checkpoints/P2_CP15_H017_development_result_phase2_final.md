# P2-CP15 — H017 Development Result and Phase 2 Final Checkpoint (STOP)

- **Date:** 2026-10-03.
- **Programme:** Phase 2, hypothesis 3 of 3.
- **Authorisation:** owner message 2026-10-03, "Authorise H017 Development Runs Under the Frozen Decision Tree" (D127; `docs/owner/2026-10-03_authorise_H017_development_runs.md`).
- **Frozen inputs, verified unchanged at evaluation:**
  - spec `research/phase2/H017_spec.md` (SHA-256 `975baacb…`);
  - event table v1 (`ebb28753…`);
  - Amendment 3 (`10fe4cbe…`).
- **Evaluation:** `research/phase2/H017_eval.py` (committed before any result), output `research/phase2/H017_results.json`.
  - After the runs and before reading any result, a prepared patch added **reporting only** (no gate change): the W2 standard-error components, wealth tables and rolling reports for every book.

## Verdict

**H017 is REJECTED (Case A).**

- **What it achieved:**
  - it beat SPY in terminal wealth (W1);
  - it beat the same-universe equal-weight book and every one of the five random-event books (W3);
  - it passed R1, R2 and R4.
- **Why it is rejected:**
  - **the evidence test fails:** the excess growth over SPY is only 0.71 standard errors, below both the full W2 requirement (2.15) and the PbNQ minimum (1.0);
  - **the result is concentrated:** 74% of the total excess over SPY comes from one two-year block (2014–2015), against a frozen limit of 50% (R3 fails). From 2016 to 2021 H017 trailed SPY in every two-year block.
- **PbNQ rules 3 and 5 fail**, so H017 is neither Development Qualified nor Promising but Not Qualified. The pre-registered tree therefore stops here:
  - E017-09 and E983-01 were **not** run;
  - E017-10 … 17 were **not** run.

| Class | Result |
|---|---|
| Beats SPY in terminal wealth (W1) | **Yes**: $671,629 vs $516,514 (ratio 1.30) |
| Statistical evidence (W2) | **No**: g / SE = 0.71 (needs 2.15) |
| Beats EW-H017 and the median random book (W3) | **Yes** |
| Risk / cost safeguards (R1, R2, R3, R4) | R1 yes, R2 yes, **R3 no**, R4 yes |
| Promising but Not Qualified | **No** (rules 3 and 5 fail) |
| **Final classification** | **Rejected** |

---

## 1. Slot 3 consumption record

**Phase 2 slot 3 = CONSUMED** at the successful start of E017-01:
- QuantConnect backtest `322b89c1…`, started 2026-10-03 18:13:50 UTC;
- commit `34747300`, `--owner-approved D127`;
- the commit that recorded the run reads "Phase 2 slot 3 CONSUMED".

**Phase 2 budget: 3 of 3 slots used** (H014, H016, H017; H015 was never adopted and used no slot).

## 2. Every run executed

All eight ran from the frozen code, spec and configs, in order, one at a time, and every one completed. Common window: 2010-03-01 → 2021-12-31 (history-only warm-up from 2009-07-01).

| Run | Book | QuantConnect backtest | Compute | Status |
|---|---|---|---|---|
| E017-01 | **Candidate**, $100K | `322b89c1…` | 783 s | Completed |
| E017-02 | EW-H017, $10M paper | `534cd35e…` | 901 s | Completed with the standard D059 warning (11 holdings closed at their last real close after > 10 sessions without data) |
| E017-03 | Random-event seed 1 | `9080db45…` | 838 s | Completed |
| E017-04 | Random-event seed 2 | `a9a4a2ed…` | 1,057 s | Completed |
| E017-05 | Random-event seed 3 | `394617c3…` | 767 s | Completed |
| E017-06 | Random-event seed 4 | `901f745b…` | 848 s | Completed |
| E017-07 | Random-event seed 5 | `618e845a…` | 796 s | Completed |
| E017-08 | Candidate, $200K (sensitivity) | `6c85aace…` | 1,099 s | Completed |

**Not run:**
- E017-09 and E983-01: Case B prerequisites not met;
- E017-10 … E017-17: Case C prerequisites not met.

**Mechanics of the candidate run** (the canary's offline checker applied to E017-01, `research/phase2/H017_E017-01_mechanics_check.json`):
- **Entries:** all 471 at the open of E+2.
- **Exits:**
  - all 458 normal exits exactly 60 sessions after entry;
  - 3 forced delisting exits (Burger King 2010, Spansion 2015, WebMD 2017, all acquired);
  - 10 positions open at the end.
- **Portfolio:**
  - at most 10 holdings;
  - planned weight at most 9.80%;
  - $7 per order, 10 bps slippage;
  - no top-ups, queued signals or early replacements;
  - 7 events of held stocks ignored.
- **Data and timing:** 0 look-ahead counters; the breakpoint sample was ≥ 1,692 events on every day.
- **Result:** every mechanics check passes. The one canary-specific assertion, "random book, seed 0", does not apply to the candidate.

**Controls equivalence** (`research/phase2/H017_controls_equivalence.json`): on all 2,842 event days, every book saw identical values for:
- the events;
- the eligible universe;
- the valid reactions;
- the breakpoint sample and threshold;
- the day's signal count k_t.

This covers the candidate, $200K, EW, the five random seeds and the canary. The books differ only in which stocks they selected.

## 3. Technical reruns

**None.** No run failed or was repeated. (Before this authorisation, the infrastructure canary was run twice: E982-01 and E982-02, P2-CP14.)

## 4–8. Terminal wealth, CAGR and excess (2010-03-01 → 2021-12-31, $100,000 start)

| Item | H017 (E017-01) | SPY (E900-07) |
|---|---|---|
| Initial capital | $100,000 | $100,000 |
| **Final value** | **$671,629** | **$516,514** |
| Total return | +571.6% | +416.5% |
| CAGR | **17.46%** | **14.88%** |
| **Terminal-wealth ratio (H017 / SPY)** | **1.300** | — |
| **Excess CAGR** | **+2.58 points a year** | — |

## 9. W1

**Pass.** CAGR(H017) 17.46% > CAGR(SPY) 14.88%.

## 10. W2: statistic, SE components, result

| Item | Value |
|---|---|
| g = 252 × mean(ln(1+r_H) − ln(1+r_SPY)), annualised log growth of the wealth ratio | 2.22% a year |
| SE (iid) | 3.14% |
| SE (stationary bootstrap, mean block 126 sessions) | 2.33% |
| SE used = the larger | 3.14% |
| g / SE | **0.71** |
| Required: g ≥ 2.15 × SE | 6.75% |
| **Result** | **Fail** |

g / SE = 0.71 is also below the PbNQ minimum of 1.0 (rule 3).

## 11. EW-H017 (E017-02)

- **Returns:** CAGR 13.03%; Sharpe 0.77; maximum drawdown −38.0%.
- **Wealth:** final value $426,247 per $100K, ratio to SPY 0.83.
- **Universe:** equal weight of the exact H017 universe, on average 1,132 stocks.

## 12. The five random-event books (each individually)

| Seed | Run | CAGR | Sharpe | Max drawdown | Final value | Ratio to SPY |
|---|---|---|---|---|---|---|
| 1 | E017-03 | 13.11% | 0.73 | −37.0% | $429,457 | 0.83 |
| 2 | E017-04 | 13.62% | 0.73 | −42.0% | $453,027 | 0.88 |
| 3 | E017-05 | 11.14% | 0.64 | −45.0% | $349,164 | 0.68 |
| 4 | E017-06 | 10.26% | 0.58 | −47.0% | $317,607 | 0.61 |
| 5 | E017-07 | 13.09% | 0.71 | −33.2% | $428,558 | 0.83 |
| **Median** | | **13.09%** | | | | |

- **All five:** same events, timing, sizing, cash, costs and day-matched k_t as the candidate; never averaged.
- **None beat SPY.**
- **Costs:** 0.99%–1.10% a year.
- **Investment:** about 89% invested, about 9.4 of 10 slots used.

## 13. W3

**Pass.**
- CAGR(H017) 17.46% > EW-H017 13.03%.
- CAGR(H017) 17.46% > the median random-event book 13.09%.
- H017 also beat every individual seed, by between 3.84 and 7.20 points a year.

## 14. R1–R4

| Gate | Frozen rule | H017 | SPY | Result |
|---|---|---|---|---|
| R1 | MaxDD ≥ SPY's − 10 points | −36.8% | −33.1% | **Pass** |
| R2 | Sharpe ≥ SPY's − 0.15 | 0.883 | 0.920 | **Pass** |
| R3 | Total log excess > 0 and no two-year block > 50% of it | Total +0.263; largest block 2014–15 = 74.3% | — | **Fail** |
| R4 | Realised costs ≤ 1.5% a year; no leverage; limits | Costs 0.93% a year (commission 0.18%, slippage 0.74%); gross ≤ 0.97, cash ≥ 0; ≤ 10 holdings; planned weight ≤ 9.80% | — | **Pass** |

**R3 detail: log excess over SPY by two-year block**

| Block | Excess |
|---|---|
| 2010–11 | +0.018 |
| 2012–13 | +0.105 |
| **2014–15** | **+0.195** |
| 2016–17 | −0.033 |
| 2018–19 | −0.015 |
| 2020–21 | −0.008 |
| **Total** | **+0.263** |

All of H017's excess over SPY was earned in 2010–2015.

**Calendar-year returns (diagnostic)**

| Year | 2010* | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H017 | 18.9% | −0.4% | 24.6% | 35.5% | 30.2% | 7.0% | 5.9% | 23.6% | 4.7% | 17.4% | 26.3% | 18.6% |
| SPY | 14.3% | 1.8% | 15.7% | 31.4% | 13.2% | 1.3% | 11.7% | 21.2% | −4.5% | 30.5% | 18.0% | 28.0% |
| EW-H017 | 17.8% | −0.4% | 16.1% | 35.0% | 10.5% | −2.3% | 13.9% | 18.1% | −8.8% | 26.4% | 17.9% | 17.4% |

\*From 2010-03-01.

## 15. Rolling 1/3/5/10-year comparison with SPY (diagnostic only, never a gate)

| Book | Horizon | Share of start dates beating SPY | Mean excess CAGR | Median | 10th pct | 90th pct | Worst | Best | Independent windows |
|---|---|---|---|---|---|---|---|---|---|
| **H017** | 1 y | 64% | +3.6% | +4.7% | −8.5% | +14.9% | −21.3% | +35.6% | 11.8 |
| | 3 y | 76% | +3.4% | +2.5% | −2.1% | +10.1% | −5.5% | +12.3% | 3.9 |
| | 5 y | 75% | +3.4% | +4.2% | −1.2% | +7.5% | −4.3% | +9.8% | 2.4 |
| | 10 y | 100% | +2.9% | +3.0% | +2.2% | +3.5% | +1.6% | +3.9% | 1.2 (not evidence) |
| **EW-H017** | 1 y | 40% | −0.9% | −1.4% | −6.6% | +5.7% | −15.5% | +31.6% | 11.8 |
| | 3 y | 23% | −1.7% | −1.7% | −4.6% | +1.1% | −7.5% | +2.1% | 3.9 |
| | 5 y | 10% | −1.7% | −1.5% | −4.1% | −0.0% | −5.7% | +1.3% | 2.4 |
| | 10 y | 0% | −1.8% | −1.9% | −2.3% | −1.3% | −2.5% | −0.9% | 1.2 |
| Random seed 1 | 3 y / 5 y | 22% / 16% | −2.2% / −2.2% | | | | | | |
| Random seed 2 | 3 y / 5 y | 32% / 15% | −2.5% / −2.7% | | | | | | |
| Random seed 3 | 3 y / 5 y | 10% / 2% | −3.9% / −3.4% | | | | | | |
| Random seed 4 | 3 y / 5 y | 26% / 11% | −4.9% / −5.1% | | | | | | |
| Random seed 5 | 3 y / 5 y | 19% / 17% | −3.0% / −3.2% | | | | | | |

- Every random book's full 1/3/5/10-year table is in `H017_results.json` (`rolling_all_vs_spy`).
- The 10-year windows (1.2 independent windows on 12 years) are **not evidence**, per Amendment 3.
- The rolling view shows the same picture as R3:
  - 3-year windows beat SPY in 100% of start dates from 2010–2013, 82% from 2014–2016 and 20% from 2017–2019;
  - 5-year windows beat SPY in 100% of starts from 2010–2013 and 43% from 2014–2016.

## 16. $200K sensitivity (E017-08; never decides, never rescues)

| | $100K (E017-01) | $200K (E017-08) |
|---|---|---|
| CAGR | 17.46% | 17.64% |
| Sharpe | 0.883 | 0.890 |
| Max drawdown | −36.8% | −36.8% |
| Realised costs | 0.93% a year | 0.83% a year |
| Ratio to SPY wealth | 1.300 | 1.323 |

The larger account lowers the commission share as expected; its trades are otherwise nearly the same. It changes nothing in the classification.

## 17. Event-level diagnostic (E983-01)

**Not triggered**, so not run. PbNQ rules 1–5 did not hold (rules 3 and 5 fail), and the owner's instruction authorises E983-01 only in Case B or C. No post-event event-level return was computed.

## 18. Robustness (E017-09 … 17)

**Not triggered**, so not run (Case C prerequisites not met: W2 and R3 fail).

## 19. PbNQ evaluation (frozen order)

| Rule | Condition | Result |
|---|---|---|
| 1 | W1 passes | **Pass** |
| 2 | Excess CAGR ≥ +1.0 point a year | **Pass** (+2.58) |
| 3 | g / SE ≥ 1.0 while W2 fails | **Fail** (0.71) |
| 4 | W3 passes | **Pass** |
| 5 | R1–R4 all pass | **Fail** (R3) |
| 6 | W1 at 2× slippage | Not evaluated (E017-09 not authorised once rules 1–5 fail) |
| 7 | Event-level top decile | Not evaluated (E983-01 not authorised) |

**PbNQ: not met.**

## 20. Final classification

**Rejected.**

- H017 is closed exactly as tested: frozen spec, code, event table and runs preserved unchanged.
- No tuning, no variation, no rescue.

## 21. Is an additional-data purchase justified under the pre-registered tree?

**No.**
- Case A specifies no data purchase to rescue H017.
- Only Case B (PbNQ) would have allowed you to consider buying longer history to re-test the same frozen strategy, and H017 did not reach Case B.
- Nothing was purchased.

## 22. Holdout

**Untouched.**
- Every H017 run, the canary and the evaluation used only 2010-03-01 → 2021-12-31 (warm-up history from 2009-07-01).
- No config ends after 2021-12-31.
- The event table holds nothing after 2021-12-31.
- `HOLDOUT_UNLOCK.md` does not exist.
- No data from 2022-01-01 → 2026-08-31 was read.

## 23. Exact next owner decision

1. **Confirm H017 closed as Rejected** (preserved exactly as tested).
2. **Phase 2 outcome.** All three hypothesis slots are used:
   - H014 rejected;
   - H016 rejected;
   - H017 rejected.

   Under the pre-registered tree (P2-CP13 §24, Case A), **Phase 2 ends with "No Production Candidate Found" unless you decide otherwise.** Please confirm that conclusion, or state a different direction.

   I propose no new hypothesis, phase or data purchase here; any of those is your decision in a separate instruction.

---

## Phase 2 summary (programme record)

| Slot | Hypothesis | Outcome |
|---|---|---|
| 1 | H014: trend with pullback entry | Rejected (P2-CP1) |
| — | H015: diversified low-turnover trend | Not adopted before implementation; no slot used |
| 2 | H016: gross profitability (GP/A) | Rejected (P2-CP9) |
| 3 | **H017: earnings-event continuation** | **Rejected (this checkpoint)** |

**Programme totals to date (both phases):**
- **Hypotheses:** 17 (H001–H017). H012 was removed as not evaluable; H015 was not adopted.
- **Research strategies:** 16 (S001–S014, S016, S017).
- **Experiment IDs registered:** 276 originals in `experiments/INDEX.csv`, across all kinds:
  - research 275 rows;
  - infrastructure 106;
  - benchmark 42;
  - sizing 14;
  - demo 3.

  The rows also include 7 reproductions and 2 recoveries (plus annotation rows).
- **H017 runs in this step:** 8 (E017-01 … 08); no reruns.

**STOP.** Holdout locked. No tuning, no new hypothesis, no new phase, no data purchase. Waiting for the owner.
