# C01 — run incidents, diagnoses and fixes

All original runs stay in `experiments/INDEX.csv`. This file records why some of them are invalid and what changed before the corrected re-runs. Every diagnosis below was confirmed from QuantConnect API data (order records, order events, backtest statistics), not inferred.

## 1. Leverage (cash below zero): E004-01, E004-02, E005-02

The integrity check failed because cash fell below −1% of equity at a daily close. There are **two distinct confirmed causes**.

### Cause A — LEAN cancels open orders on a ticker change

| Run | Signal day | Order | What the order records show |
|---|---|---|---|
| E004-01 | 2012-06-29 | id 1659, **sell MATX** −113 | submitted 06-29; *cancelPending → canceled* 2012-07-02, "Open order cancelled on symbol changed event". Alexander & Baldwin became Matson (MATX) on 2012-07-02. |
| E005-02 | 2012-10-01 | id 121, **sell MDLZ** −232 | submitted 10-01; *canceled* 2012-10-02, "Open order cancelled on symbol changed event". Kraft Foods (KFT) became Mondelez (MDLZ) on 2012-10-01/02. |

**Mechanism.**

- The harness sized that day's buys counting the proceeds of *all* same-batch sells.
- The ticker-change sell was cancelled by LEAN at the open; the buys it funded executed.
- Result: 16 positions (the cap is 15) and negative cash:
  - E004-01: −1.1% for one day; the strategy re-sold MATX the next day.
  - E005-02: −1.8% for 21 trading days, until the next monthly rebalance.

### Cause B — overnight gap-up on buys sized at the prior close

| Run | Day | Evidence |
|---|---|---|
| E004-02 | 2016-11-30 (OPEC production-cut deal) | No order was cancelled; all 2 sells and 7 buys filled. |

- **Cash reconciles exactly:** 29,251.51 + 11,344 (sells) − 41,812 (buys) − 63 (9 × $7) = −1,279, against a recorded −1,278.26.
- **Measured opening gaps**, open on 11-30 vs close on 11-29 (probe run, derived ratios only):

| Stock | Gap | Stock | Gap |
|---|---|---|---|
| CLR | +11.4% | EGN | +12.9% |
| GLNG | +10.6% | LPI | +11.0% |
| RSPP | +8.8% | ENLC | +5.9% |
| PE | +5.5% | SPY (reference) | +0.3% |

The buys were sized on the 11-29 close. They cost about 9% more at the open, which exceeded the 2% cash buffer.

### Fix (D051, global execution-model change; all 19 variations re-run)

1. **Buys use only cash already available.** Proceeds of sells in the same batch cannot fund buys; they become available after the sells have actually executed, from the next close. **Cause A cannot recur.**
2. **Slots are the same.** A position being exited still counts toward the 15-position cap until its sell has executed.
3. **Gap reserve.** Planned buy cost × (1 + 15%) + $7 per order must fit within cash − 2% × equity. This covers every gap observed, including the OPEC day, with margin.
4. **Integrity is now strict.** Any negative cash at any close fails the run; the old tolerance was −1%. A gap bigger than the reserve cannot be ruled out in advance with orders at the opening auction, but it can never pass silently.
5. **Sells cancelled by a ticker change are resubmitted** at the next close as market-on-open orders, so a position is not held unintentionally until the next rebalance.

## 2. E004-04 — BUGGED (zero orders in 8 years)

- S004 v1.3's SPY filter needs a 200-day average, but S004 kept only 140 days of history (`WINDOW_BARS = 140`).
- So the filter was never satisfied, and the strategy never traded.
- **Fix:** `WINDOW_BARS = 210`. The other S004 variations' signals don't use more than 132 bars, so their logic is unchanged.

## 3. E002-03 — FAILED (QuantConnect delayed publishing fill events)

- The runner waited 30 minutes; 1,020 of 1,076 orders still had no fill events.
- **Re-checked hours later:** the same backtest returns all 1,076 orders with complete events. So it was a publication **delay**, not missing data.
- **Fix:** the wait is raised to 2 hours. The download stays count-verified (D050), so nothing incomplete can be accepted.
- The variation is re-run under a new ID.

## 4. E003-03 — FAILED (QuantConnect "Compile id not found" at backtest start)

- The compile had reported success. `backtests/create` then rejected its compile ID.
- No backtest ran, and there is no indication of a cause on our side.
- **Fix:** on this specific error the runner recompiles once and retries.
- The variation is re-run under a new ID.

## 5. Also observed (harmless, recorded for completeness)

- **End-of-period orders:** orders submitted on the last IS day (2017-12-29) stay "submitted", because there is no next open inside the period. They have no fill and no fee.
- **Cancelled buys:** a buy cancelled on a ticker change (E004-01: WCN, 2016-06-01) had no fill and no fee. The strategy re-selects on later days.

## 6. Corrected-run queue, 2026-09-28: operational failures (E003-04/05/06; E004-05..08, E005-04..06)

**What happened.**

| Run | QuantConnect state | Runner outcome |
|---|---|---|
| E003-04 (S003 v1.0) | Backtest **completed** (1,329 orders) | Orders endpoint answered "Error retrieving orders result, please try again later". The runner treated this as fatal and stopped. |
| E003-05 (S003 v1.1) | Backtest **completed** (2,749 orders) | Orders endpoint returned HTTP 500 beyond the client's ~1-minute retry budget; runner stopped. |
| E003-06 (S003 v1.2) | Backtest **stalled at 97%**. QuantConnect's server clock froze at 6 min 31 s uptime (about 17:12 UTC). No summary statistics; every chart empty. | The runner waited its full 6-hour ceiling, then failed. The backtest kept the organisation's only node busy. |
| E004-05..08, E005-04..06 | Nothing ran | `backtests/create` refused: "no spare nodes available". **Not started. Not trials.** |

**Investigation: why all three H003 attempts failed.**

- **Not order or fill volume.** Order counts: H003 1,329 / 2,749 / ≈1,246 (stalled). Completed runs of other strategies: 508 to 4,509 (E001-09), and the original S003 run E003-02 had 5,168.
- **Not result payload size.** The harness's summary statistics are 1.3 KB for H003 versus 0.8–2.5 KB elsewhere. RAM was 2.6 GB, within the other runs' 1.0–3.0 GB.
- **Not S003's rebalance behaviour.** S003 is a 36-line monthly or 10-day rebalance with no loops that could hang. v1.2 differs from v1.0 only by a momentum filter, and v1.0 finished its backtest normally in 7 minutes.
- **It was a time window, not a strategy.** Every failure fell between 16:01 and 17:12 UTC. H003 was simply what the queue was running then. E002-08 finished at 16:00 without trouble.
- **The orders API itself is healthy.** On 2026-09-29, with no code change:
  - the first request for *any* backtest's orders (also E001-10 and E002-08) returns `status: loading`, and the full data follows about 50 seconds later;
  - E003-04 and E003-05 now download **completely**: 1,329 of 1,329 and 2,749 of 2,749 orders, every filled order with its fill event.
- **Our share of the blame (runner bugs):**
  1. A transient error on the orders endpoint aborted the run instead of being retried inside the existing 2-hour completeness window.
  2. A `loading` reply was read as an empty page. The count check stopped it being accepted, but only when QuantConnect's order count was known.
  3. A backtest that stopped progressing was waited on for 6 hours.
  4. The failure record omitted the QuantConnect backtest ID and how far the run had got.
  5. Runs were attempted while the node was still busy.

**Conclusion.** A transient QuantConnect-side outage (orders endpoint errors, plus one engine stall), made worse by the runner not retrying. H003 is **not** blocked: nothing is wrong with the strategy code.

**Fixes (D053).**

- The orders download retries transient errors and `loading` replies within its 2-hour window. It still accepts only a download whose distinct-order count equals QuantConnect's "Total Orders" and in which every filled order has its fill event.
- A backtest whose progress has not moved for 45 minutes is declared **stalled**. Normal IS runs take 5–10 minutes.
- A failed run records its QuantConnect project and backtest ID, the backtest start time and the failure stage.
- **Pre-flight:** if any backtest is still running, the runner refuses to start. Like the clean-tree check, it registers nothing, so no attempt is wasted.
- Stalled backtests are **not** deleted automatically; deletion needs the owner.
- Regression tests cover every fix.

**Records.**

- E003-06's QuantConnect metadata was preserved in `research/cycles/incidents/E003-06_qc_backtest_metadata.json`. The stalled backtest was then deleted, with owner approval, on 2026-09-29.
- All ten attempts stay in `experiments/INDEX.csv`, with annotation rows:
  - `failed` for E003-04/05/06;
  - `not_started` for the seven that never started, which `registry.trial_count` excludes.
- **No result is taken from the E003-04/05 backtests** even though their data is now complete. They are re-run cleanly, so every accepted result comes from one uninterrupted, fully checked run.

**Retries under fresh IDs** (`C01_retry_map.json`):

| Failed attempt | Retry |
|---|---|
| E003-04 | E003-07 |
| E003-05 | E003-08 |
| E003-06 | E003-09 |
| E004-05..08 | E004-09..12 |
| E005-04..06 | E005-07..09 |

## 7. D051 resubmission never fired (found while auditing the retries), and the D054 fix

**Finding.**

- The retry E004-09 held MATX across its 2012-07-02 ticker change, like the invalid E004-01.
- LEAN again cancelled the exit (order 1535), yet the harness counted **0** symbol-change cancellations and re-issued nothing.
- **Cause:** QuantConnect's order record shows LEAN **rewrites the order tag** to "Open order cancelled on symbol changed event" and leaves the **event message empty**. The D051 handler looked for "symbol changed" in the message, so it never matched.
- **No borrowing resulted.** Under settled-cash funding the unsold position kept its slot and no buy used its proceeds, so every integrity check stayed clean.
- **But an intended exit was not executed** until the strategy re-signalled it.

**Audit of all 19 corrected runs** (full order records from QuantConnect: `incidents/C01_cancelled_orders_audit.txt`):

| Run | Cancelled harness order | Effect |
|---|---|---|
| E004-09 | MATX sell, ticker change 2012-07-02 | Exit 1 trading day late (the strategy's own next-day signal) |
| E005-08 | MDLZ sell, ticker change 2012-10-01 | Monthly strategy: **exit a month late** (sold 2012-11-02) |
| E001-10 (SII), E003-07/09 (SYA), E003-08 (LZ) | Sells cancelled at the name's delisting (acquisitions) | None: LEAN liquidated the holding itself (forced fills, charged $7) |
| E002-06 (KITE), E003-08 (PPO), E004-09/12 (WCN) | Buys | None: the entry did not happen and the strategy re-selects later; no fee |
| The other 12 runs | — | None |

**Fix (D054).**

- The harness never cancels its own orders, so **any** cancellation of a harness order is LEAN's.
- Cancelled harness **sells** are re-issued at the next close, capped at the quantity held, unless the name has a delisting warning. In that case LEAN liquidates it and a re-issued sell could create a short.
- Cancelled **buys** are not re-issued.
- Every case is counted: `cancelled_harness_sells`, `cancelled_harness_buys`, `cancelled_on_symbol_change`, `cancelled_sells_delisting` and `resubmitted_sells`. All counters now start at 0, so a missing counter is itself a failure.
- Regression tests replay the exact E004-09 event: tag rewritten, empty message.

**Consequence.**

- To keep one harness version in the final comparison, the verification trio and all 19 variations are re-run under new IDs:
  - E950-06, E900-06, E901-05 (verification);
  - E001-11..15, E002-09..12, E003-10..12, E004-13..16, E005-10..12 (`C01_d054_map.json`).
- In the registry, E004-09 and E005-08 are annotated `bugged` and the other 17 `superseded`.
- Runs with no affected exit should reproduce their equity curves exactly, which gives an extra reproducibility check.

**Also found (a reporting convention, not a bug): spin-offs.**

- On the Kraft spin-off (2012-10-01), LEAN credited the distributed Kraft Foods Group value as a **cash distribution** (+$14.4 per share, confirmed from the cash series), so equity is correct.
- Trade PnL excludes dividends by the approved convention D018. The MDLZ trade therefore shows −24.6% although the holding gained overall.
- Portfolio metrics are unaffected. Trade-based gates (profit factor, expectancy) are made slightly **more conservative** for strategies that hold spin-off parents. Disclosed in CP3.
