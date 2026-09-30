# E007-12 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): plateau: time stop 40 -> 32 (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `9253eef87577e465a41bf586a38b28d0dc043f38` · **QC backtest:** `bfb8f1a30366d664e86858366b5de54f` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T05:56:47Z · **runtime:** 0s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 32, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.51% |
| Annualised volatility | 4.68% |
| Sharpe (rf = 0) | 1.17 |
| Sortino | 1.88 |
| Max drawdown | -5.02% |
| Longest drawdown (trading days) | 271 |
| Calmar | 1.10 |
| Worst year | 0.92% |
| Worst month | -1.71% |
| Closed trades | 224 |
| Win rate | 46.43% |
| Average winner | 6.78% |
| Average loser | -2.33% |
| Expectancy per trade | 1.90% |
| Profit factor | 2.47 |
| Average holding (calendar days) | 26.4 |
| Average exposure | 20.07% |
| Turnover (1-way, per year) | 2.74 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -7.83% | 0.09 | 0.27 |
| E901-07 | -8.42% | 0.09 | 0.30 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 9.03% |
| 2011 | 0.92% |
| 2012 | 10.32% |
| 2013 | 4.22% |
| 2014 | 8.35% |
| 2015 | 1.25% |
| 2016 | 2.35% |
| 2017 | 7.98% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 99884.84 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.031024; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 29 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.116719661283175e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 449 orders vs QuantConnect Total Orders 449 |
| fills_match_harness_count | pass | downloaded fill events 448 vs harness-recorded fills 448 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 448 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `e37a43567ed066675ff0ac2425c0df6ef8dd5591b5507ec78b26e097d20fd293`
- fills_sha256: `6efc4f95525996821803684395c1d4d3ced425da7d963ebe995f1a0c8a6dc7a2`
- trades_sha256: `2e6a3546a417f3c7783f5d2002283067c9fc8bee195bb17a3e19481617a0d235`
