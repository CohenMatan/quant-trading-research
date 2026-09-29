# Checkpoint 3: first research cycle (C01), in-sample only

| Field | Value |
|---|---|
| Status | **STOPPED. Awaiting owner approval.** No Validation, Walk-Forward or Holdout run has been made. |
| Period used | IS only: 2010-01-04 → 2017-12-29 |
| Settings | $100K account; $7 per order; 10 bps slippage per side; ≤ 15 positions; ≤ 10% per position; ≥ $5K per position; no borrowing (D051) |
| Benchmarks | Equal-weight ≥ $2B universe **E901-05** (IS: CAGR 13.7%, Sharpe 0.91, max drawdown −22.1%); SPY **E900-06** (IS: CAGR 13.3%, Sharpe 0.95, max drawdown −18.3%) |
| Engine | QuantConnect LEAN build 18131, pinned; one harness version for all final results (D054) |

## 0. Summary

1. **Five hypotheses, 19 pre-declared variations.** After fixing every infrastructure problem found, all 19 were run cleanly under one execution model and one harness version.
2. **One hypothesis passes the approved in-sample screen: H005 (low volatility).** All three of its variations pass. The other 16 variations (H001–H004) fail.
3. **The best H005 variation, S005 v1.2 (E005-12), passes the whole in-sample robustness gate:**
   - costs up to 4× (Sharpe 1.12; 6× still 0.91);
   - 10 of 10 parameter perturbations keep ≥ 70% of its Sharpe;
   - positive in every third of IS;
   - much smaller drawdowns than the benchmark in every IS stress episode.
4. **Two serious caveats** need your decision before anything moves to Validation:
   - **PBO is 0.71.** The approved Validation-gate limit is ≤ 0.30. With only three near-identical variations this number carries little information, but as defined at CP2 it **fails** (§8).
   - **Under the no-borrowing rule, H005 sits in about 32% cash** between monthly rebalances. Returns are lower (CAGR 8.5% versus the benchmark's 13.7%); risk-adjusted return is higher (Sharpe 1.44 versus 0.91) (§9.2).
5. **Recommendation:** freeze S005 v1.2 as C01's only candidate, but promote it to Validation **only if you decide how the PBO requirement applies** (§10). If PBO stays a hard gate as computed, the honest C01 outcome is "no candidate".

## 1. What was run: the accounting

| | Count |
|---|---|
| Hypotheses | 5 (H001–H005), all registered before any C01 data was seen |
| Strategies | 5 (S001–S005) |
| Pre-declared variations | 19 |
| Research runs in the registry | **82**: 19 original + 19 first corrected (D051) + 10 retries + 19 final (D054) + 15 robustness |
| **Trials for multiple-testing statistics** | **76** in the registry count: 75 research runs + 1 demo. This includes every research run that started (or tried to compile), failed and superseded ones included. The 7 attempts that never started are excluded (your instruction). |
| Of which final and comparable | 19 variations + 15 robustness runs |
| Integrity checks | Every final run passes all of them (list in §6) |

Every run, including failed and bugged ones, is kept in `experiments/INDEX.csv`. Later findings are appended as annotation rows; nothing is edited or deleted.

## 2. Original runs (first pass, pre-D051 execution model), 2026-09-28

Portfolio rules as approved; buys could be funded by same-morning sale proceeds.

| Hypothesis | Runs | Outcome |
|---|---|---|
| H001 short-term reversal | E001-01..05 | Completed. Superseded by D051. |
| H002 12-1 momentum | E002-01, 02, 04 | Completed. Superseded. |
| | E002-03 | **Operational failure** (§3) |
| H003 52-week high | E003-01, 02 | Completed. Superseded. |
| | E003-03 | **Operational failure** (§3) |
| H004 momentum pullback | E004-01, 02 | **Invalid: borrowed cash** (§4) |
| | E004-03 | Completed. Superseded. |
| | E004-04 | **Bugged** (§4) |
| H005 low volatility | E005-01, 03 | Completed. Superseded. |
| | E005-02 | **Invalid: borrowed cash** (§4) |

None of these results is used for any decision. They stay on record.

## 3. Operational failures (platform or runner; no valid result)

| Run | What happened | Counts as a trial? |
|---|---|---|
| E002-03 | QuantConnect published fill events late; the runner stopped waiting after 30 minutes. The data later proved complete. | Yes (a backtest ran) |
| E003-03 | QuantConnect rejected a fresh compile ("Compile id not found") | Yes (conservative; no backtest ran) |
| E003-04, E003-05 | Backtests completed, but the orders endpoint failed during a QuantConnect outage (16:01–17:12 UTC). The runner gave up instead of retrying. | Yes |
| E003-06 | Backtest stalled at 97% for 6 hours and blocked the only node. Its metadata is preserved; it was deleted with your approval. | Yes |
| E004-05..08, E005-04..06 | Never started ("no spare nodes"), because of E003-06 | **No** (your instruction) |

- **H003 was investigated, not declared blocked** (`research/cycles/C01_incidents.md` §6). Order volume, payload size, memory and strategy logic were all in line with the other runs.
- The cause was a platform outage window combined with the runner not retrying.
- **Fixed (D052, D053):**
  - retries inside the completeness window;
  - stall detection after 45 minutes;
  - failure records that keep the backtest ID and stage;
  - no start while the node is busy.
- A clean H003 re-run then completed normally.

## 4. Bugged and integrity-failed runs

| Run | Problem | Fix |
|---|---|---|
| E004-01, E005-02 | **Borrowed cash (cause A).** LEAN cancelled a sell on a ticker change (MATX, MDLZ) while the buys it was meant to fund executed: 16 positions and negative cash. | D051 no-borrowing model |
| E004-02 | **Borrowed cash (cause B).** Opening gaps of +5.5% to +12.9% on buys sized at the prior close (2016-11-30). | D051: buys use settled cash only, with a 15% gap reserve |
| E004-04 | **Bug:** the regime filter needed 200 days of history but the window held 140, so the filter was never active and no trade happened | Window 210 |
| E004-09, E005-08 | **Bug (found at CP3):** the D051 sell re-issue never fired, because LEAN rewrites the order tag and leaves the message empty. MATX exit 1 day late; **MDLZ exit 1 month late**. | D054: re-issue any LEAN-cancelled harness sell |

Details: `C01_incidents.md` §1–2 and §7. The cancellation audit covered the full order records of every run (`incidents/C01_cancelled_orders_audit.txt`).

## 5. Corrected runs that were later superseded

| Batch | Runs | Status |
|---|---|---|
| D051 first corrected pass | E001-06..10, E002-05..08 | Clean, but pre-D054 harness: **superseded** |
| | E003-04..06, E004-05..08, E005-04..06 | Operational failures (§3) |
| D053 retries | E003-07..09, E004-09..12, E005-07..09 | Clean except E004-09 and E005-08 (bugged, §4); all **superseded** by D054 |
| Verification | E950-05, E900-05, E901-04 | Passed, but pre-D054 harness: **superseded** |

**Reproducibility check.** The final D054 runs were compared with these:

- **16 of 19 variations reproduced exactly:** identical equity, fill and trade hashes, as did the canary and SPY.
- **E004-13 and E005-11 changed as expected** (the fixed exits).
- **E005-10, E005-12 and the equal-weight benchmark changed by a few dollars.** QuantConnect revised a few dividend amounts between 2026-09-28 and 09-29 (for example Beckman Coulter, June 2011: $0.342 → $0.367 per share).
  - Sharpe is unchanged to three decimals.
  - This is a platform data revision, not our code. Byte-exact reproduction is only guaranteed within one data snapshot.

## 6. Final comparable C01 results (IS, net of all costs)

**Consistency.** All 19 ran on 2026-09-29 between 07:40 and 09:55 UTC, with the same harness, execution model (D051 + D054), LEAN build and settings. The benchmarks were re-run with the same harness.

**Integrity (every run):**

- $7 exactly per executed order;
- orders download complete versus QuantConnect's count;
- fills match the harness count;
- no close with negative cash;
- every fill after its signal date (T+1 open);
- the harness timing self-check passes;
- equity rows match QuantConnect's trading days;
- forced liquidations charged $7;
- all cancellation counters present.

**Results** (EW = equal-weight benchmark, Sharpe 0.91, max drawdown −22.1%):

| Run | Variation | CAGR | Sharpe | Max DD | Closed trades | Avg invested | IS screen |
|---|---|---|---|---|---|---|---|
| **H001 short-term reversal in an uptrend** | | | | | | | |
| E001-11 | v1.0 RSI(2) ≤ 10, exit above 5-day mean | 1.7% | 0.19 | −31.1% | 1,638 | 67% | fail |
| E001-12 | v1.1 RSI(2) ≤ 5 | 1.7% | 0.19 | −30.9% | 1,371 | 65% | fail |
| E001-13 | v1.2 time exit (10 days) | 4.3% | 0.36 | −29.2% | 1,640 | 87% | fail |
| E001-14 | v1.3 + market regime filter | −4.7% | −0.45 | −36.7% | 2,248 | 51% | fail |
| E001-15 | v1.4 entry on a 3-day drop ≥ 6% | 13.5% | 0.69 | −30.4% | 316 | 93% | fail |
| **H002 12-1 momentum** | | | | | | | |
| E002-09 | v1.0 12-1, monthly | 7.6% | 0.45 | −37.2% | 349 | 70% | fail |
| E002-10 | v1.1 6-1 | 6.7% | 0.44 | −31.1% | 458 | 63% | fail |
| E002-11 | v1.2 + regime filter | 9.2% | 0.56 | −30.8% | 342 | 62% | fail |
| E002-12 | v1.3 every 2 months | 5.7% | 0.38 | −37.8% | 225 | 63% | fail |
| **H003 near the 52-week high** | | | | | | | |
| E003-10 | v1.0 monthly | 5.6% | 0.73 | −12.5% | 659 | 49% | fail |
| E003-11 | v1.1 every 10 days | 0.8% | 0.14 | −17.0% | 1,370 | 48% | fail |
| E003-12 | v1.2 + positive momentum | 5.7% | 0.74 | −12.5% | 658 | 49% | fail |
| **H004 pullbacks in momentum leaders** | | | | | | | |
| E004-13 | v1.0 5% pullback, 10-day hold | 4.6% | 0.32 | −52.4% | 2,581 | 81% | fail |
| E004-14 | v1.1 8% pullback | −1.4% | 0.03 | −53.3% | 1,988 | 64% | fail |
| E004-15 | v1.2 20-day hold | 8.2% | 0.46 | −44.1% | 1,395 | 88% | fail |
| E004-16 | v1.3 + regime filter | 3.0% | 0.25 | −39.0% | 2,296 | 72% | fail |
| **H005 low volatility** | | | | | | | |
| **E005-10** | v1.0 15 lowest 63-day volatility, monthly | 8.1% | **1.37** | −5.3% | 396 | 69% | **PASS** |
| **E005-11** | v1.1 252-day volatility | 10.4% | **1.23** | −9.4% | 164 | 83% | **PASS** |
| **E005-12** | v1.2 63-day + positive 12-1-month momentum | 8.5% | **1.44** | −5.3% | 408 | 68% | **PASS** |

**Why H001–H004 fail.** Every one fails "Sharpe ≥ EW + 0.1", and most also fail maximum drawdown. Per-gate detail: `research/cycles/C01_is_gates.json`.

- **H001 and H004** (short-term dip-buying) lose most of their edge to costs (§7) and have 30–53% drawdowns.
- **H002** (momentum) is positive but no better than simply owning the universe, with deeper drawdowns.
- **H003** has the right risk profile (−12.5% drawdown) but only a 0.73 Sharpe. It sits at about 49% invested (§9.2).

**The 2× slippage item of the screen** (pre-declared, `C01_robustness_plan.md`) needs Sharpe ≥ 0.4:

| Run | Sharpe at 2× slippage |
|---|---|
| E005-13 (v1.0) | 1.27 ✅ |
| E005-14 (v1.1) | 1.20 ✅ |
| E005-15 (v1.2) | 1.33 ✅ |

## 7. Cost impact

Annual cost as a share of average equity. Slippage is already inside the fill prices; the figure is its estimated cost.

| Hypothesis | Commissions per year | Slippage per year | Total cost per year | Comment |
|---|---|---|---|---|
| H001 (5–10-day trades) | 0.3–4.9% | 0.3–3.8% | **4.4–8.8%** for 4 of 5 variations | Before costs, only v1.4 (14.1%) would reach the benchmark's 13.7% CAGR |
| H002 (monthly) | 0.3–0.6% | 0.3–0.7% | ~1% | |
| H003 | 0.9–2.4% | 1.0–2.1% | 2–4.5% | The 10-day variant pays 4.5% |
| H004 | 1.8–3.8% | 2.2–4.1% | **4–7.5%** | Before costs 5–12%, still below the benchmark |
| H005 | 0.2–0.5% | 0.3–0.6% | **≤ 1.1%** | Monthly, few trades |

- The fixed $7 per order ($14 per round trip, about 0.2% of a $6.5K position) plus 10 bps per side is decisive for the short-horizon ideas (H001, H004).
- For H005, costs are small. Its Sharpe falls from 1.44 to 1.33 / 1.12 / 0.91 at 2× / 4× / 6× slippage.

## 8. Robustness of the best passing variation, E005-12 (S005 v1.2)

All criteria were approved at CP2/D036 and the runs were pre-declared before running.

| Test | Result | Criterion | |
|---|---|---|---|
| Slippage 4× (40 bps per side), E005-16 | Sharpe **1.12** | > 0 | ✅ |
| Slippage 6× (60 bps per side), E005-17 | Sharpe 0.91 | reported only | |
| Plateau: volatility window 32 / 50 / 76 / 95 days (base 63) | Sharpe 1.35 / 1.47 / 1.29 / 1.22 | each ≥ 1.007 | ✅ 4/4 |
| Plateau: positions 8 / 12 (base 15; more than 15 is not allowed) | 1.40 / 1.36 | ≥ 1.007 | ✅ 2/2 |
| Plateau: rebalance band 0.125 / 0.2 / 0.3 / 0.375 (base 0.25) | 1.44 / 1.44 / 1.44 / 1.44 | ≥ 1.007 | ✅ 4/4 |
| **Plateau overall** | **10 of 10** | ≥ 80% | ✅ |
| Thirds of IS | Sharpe 1.44 / 1.79 / 1.21 | all > 0 | ✅ |
| 2010 flash crash / 2011 downgrade / 2015–16 China-oil | drawdown −4.7% / −5.3% / −4.0% (EW −15.3% / −22.0% / −18.4%) | ≤ EW + 5 points | ✅ |

**Caveats on these results:**

- **The band perturbation was inert.** With equal target weights and monthly replacement, the band never changed an order: identical trades in all four runs. The informative plateau is therefore the 6 volatility-window and position-count runs, and all 6 pass.
- **H005 also passes the 2× and 4× cost tests in every variation checked.** The result does not hinge on one parameter.

**Multiple-testing statistics** (Validation-gate items, reported now):

| Measure | Value | Approved requirement | Note |
|---|---|---|---|
| Deflated Sharpe, IS only, 76 trials | E005-12: 0.80; E005-10: 0.75; E005-11: 0.61 | ≥ 0.90 on **IS + VAL combined** | Not decidable yet. Needs VAL. |
| **PBO across H005's 3 variations** (CSCV, 16 blocks, IS) | **0.71** | **≤ 0.30** | **Fails as defined** (see below) |

**Why the PBO number carries little information here, stated plainly and not as a change of rule:**

- PBO asks how often the in-sample winner ranks at or below the median out of sample.
- With three variations, two of which (v1.0 and v1.2) are almost the same portfolio, the winner is v1.0 or v1.2 in most splits. Their out-of-sample ranking is then close to a coin toss, and the CP2 definition counts a tie at the median as overfit.
- The result sits near 0.5–0.7 whether or not anything is overfit.
- All three variations pass every screen item, including cost stress, which is the opposite of the usual overfitting pattern (one lucky peak).
- **But the rule was fixed before the data, and I am not reinterpreting it.** Whether it stands as a hard gate for H005 is your decision (§10).

For comparison, the other hypotheses' PBO: H001 0.14, H002 0.69, H003 0.97, H004 0.25.

## 9. Limitations you must know

### 9.1 Survivorship gap (D043, X954: complete)

- The universe misses about **5–14% of eligible companies in IS**: companies that later ended and have no fundamentals in QuantConnect's data.
- It flatters universe-level returns by about **+1.4 points per year** (range 0.6–2.3). Full analysis: `docs/data/survivorship_gap_2010.md`.
- The missing companies are mostly **later-distressed**, typically high-volatility falling stocks. **Low-volatility selection (H005) is the least exposed** of the five hypotheses: such names would rarely have been among the 15 lowest-volatility stocks.
- The equal-weight benchmark is flattered by the same gap, which makes H005's relative advantage slightly *understated* rather than overstated.

### 9.2 Cash drag under the no-borrowing rule (D051)

- A stock sold at a monthly rebalance frees its slot only after the sale executes, and the strategy only acts again at the next monthly rebalance. The freed money sits in cash for up to a month.
- The monthly strategies therefore hold **30–50% cash on average**: H005 v1.0/v1.2 about 32%, H003 about 51%, H002 30–38%.
- Under the old model (E005-01/03, now superseded) H005 was 93% invested:

| | Old model (E005-03) | No-borrowing (E005-12) |
|---|---|---|
| CAGR | 11.0% | 8.5% |
| Sharpe | 1.32 | 1.44 |
| Max drawdown | −7.9% | −5.3% |

- So **H005's pass does not depend on the cash**, but its absolute return does, and part of its small drawdown is simply the cash.
- A possible change: "buy into freed slots at the close after the sale executes" (still no borrowing). It changes results after they have been seen, so I have **not** made it. It needs your decision, and would have to be applied to all 19 variations as a new execution-model version before any Validation run.

### 9.3 Other items

- **Trade statistics exclude dividends** (convention D018; portfolio figures include them). For a spin-off this makes one trade look much worse. MDLZ/Kraft 2012 shows −24.6% at trade level; the portfolio correctly received the distribution.
- The trade-based gates are therefore slightly *conservative* for H005, which holds dividend-rich stocks.
- **QuantConnect data revisions** (§5): results reproduce exactly within a data snapshot; across days, small dividend revisions can change a run by a few dollars.
- **H005 underperforms in raw return** (8.5% versus the benchmark's 13.7% CAGR in a strong bull market). Its case is risk-adjusted: Sharpe, drawdown, and stress episodes.
- **The gates are risk-adjusted by design** (approved), but this matters for your goals.

## 10. Proposal and decisions needed

**My recommendation.** Freeze **S005 v1.2** (the 15 lowest 63-day-volatility stocks among those with positive 12-1-month momentum, rebalanced monthly; E005-12) as C01's only candidate. Promote it to Validation only after you decide:

1. **PBO:**
   - (a) Keep PBO ≤ 0.30 as a hard gate for H005. Then **C01 ends with "No Production Candidate Found"**, and H005 does not go to Validation.
   - (b) Record the PBO failure and its low information content with three variations, and let Validation (4 genuinely out-of-sample years) decide. The DSR ≥ 0.90 on IS + VAL and all other Validation gates still apply unchanged.
   - I recommend **(b)**, because the IS evidence (all variations pass; plateau; cost stress) is the opposite of an overfitting pattern. But it is a rule decision after seeing data, so it is yours.
2. **Cash drag (§9.2):**
   - (a) Validate S005 v1.2 exactly as tested (about 32% cash).
   - (b) First approve an execution-model change: fill freed slots after sales execute, still with no borrowing. Then re-run all 19 IS variations under it and re-screen before any Validation.
   - I recommend **(a)** for this cycle, so nothing seen is changed. (b) could be a separate, pre-declared change for the next cycle.
3. **Next research cycle (C02):** Only after the Validation outcome. Any new hypothesis must again be justified from pre-2018 knowledge.

**What happens on approval (not started):**

- A promotion record freezes code and parameters (D042).
- One Validation run follows (2018–2021), then the Validation gates. Walk-forward and Holdout wait for their own checkpoints.

## 11. Changes in this cycle (decisions)

| Decision | Change |
|---|---|
| D049 | Forced liquidations are charged $7 |
| D050 | Downloads must be verifiably complete |
| D051 | No-borrowing execution model |
| D052 / D053 | Runner resilience (compile retry, order-event wait, orders API retries, stall detection, node pre-flight, failure metadata, `not_started` runs are not trials) |
| D054 | LEAN-cancelled sells are re-issued |

Tests: 181 passing.

## 12. Where everything is

| Item | Location |
|---|---|
| Hypotheses | `research/hypotheses/H001–H005.md` |
| Cycle plan | `research/cycles/C01_plan.md` |
| Robustness plan | `research/cycles/C01_robustness_plan.md` |
| Results table | `research/cycles/C01_is_results.csv` |
| Gate detail | `C01_is_gates.json` |
| PBO | `C01_pbo.json` |
| Incidents and fixes | `research/cycles/C01_incidents.md` (+ `incidents/`) |
| ID maps | `C01_rerun_map.json` (D051), `C01_retry_map.json` (D053), `C01_d054_map.json` (D054) |
| Survivorship | `docs/data/survivorship_gap_2010.md` |
| Registry | `experiments/INDEX.csv` |
| Per-run records | `experiments/E###-##/` |
