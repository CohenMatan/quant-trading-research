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
