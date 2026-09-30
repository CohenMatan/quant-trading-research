# E962-30 — X962 v1.0 (infrastructure)

C03 S2 null ($200K, 20 slots, hold 60, seed 3). Not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `1c76e5130aeaaeb6211d05bd1a60387b7d9fec14` · **QC backtest:** `cd641c5d8682da5cee890edfd00b6eac` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T19:08:43Z · **runtime:** 282s
- **Parameters:** `{'slots': 20, 'hold': 60, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 20, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.48% |
| Annualised volatility | 15.33% |
| Sharpe (rf = 0) | 0.90 |
| Sortino | 1.28 |
| Max drawdown | -23.25% |
| Longest drawdown (trading days) | 249 |
| Calmar | 0.58 |
| Worst year | 0.22% |
| Worst month | -9.35% |
| Closed trades | 641 |
| Win rate | 62.87% |
| Average winner | 11.64% |
| Average loser | -10.54% |
| Expectancy per trade | 3.40% |
| Profit factor | 1.83 |
| Average holding (calendar days) | 88.1 |
| Average exposure | 85.09% |
| Turnover (1-way, per year) | 3.61 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 0.14% | 0.97 | 0.91 |
| E901-07 | -0.45% | 0.93 | 0.94 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.99% |
| 2011 | 0.22% |
| 2012 | 11.25% |
| 2013 | 32.07% |
| 2014 | 19.90% |
| 2015 | 2.10% |
| 2016 | 15.43% |
| 2017 | 16.72% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 187844.76 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.026590; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1302 orders vs QuantConnect Total Orders 1302 |
| fills_match_harness_count | pass | downloaded fill events 1302 vs harness-recorded fills 1302 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1302 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `887a54a6a287ac6c6a7ac718fcfdd1d9d14fc834c1a5e5e9748af9c9df49bba7`
- fills_sha256: `9d0adc1648bdbb9252e7e007e9d8eb95fe86555c657937ac76f8dc3b63396a50`
- trades_sha256: `9d6ef1ba3852f18917967fc4314f25723812f7434bd5c8fdc099402716f35fb8`
