# E001-18 — S001 v1.2 (research)

H001 remedial re-test after infrastructure correction (D057/D059/D063): S001 v1.2 exactly as pre-registered; identical to E001-13 except ID and harness

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `b321876b523b784e7607c93bc483df263d2c03c2` · **QC backtest:** `46e4742d4f66670e5c1461b1b2285daf` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T15:51:25Z · **runtime:** 546s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'time', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 1.76% |
| Annualised volatility | 13.84% |
| Sharpe (rf = 0) | 0.20 |
| Sortino | 0.27 |
| Max drawdown | -30.02% |
| Longest drawdown (trading days) | 701 |
| Calmar | 0.06 |
| Worst year | -16.13% |
| Worst month | -10.65% |
| Closed trades | 2705 |
| Win rate | 51.39% |
| Average winner | 3.82% |
| Average loser | -3.97% |
| Expectancy per trade | 0.03% |
| Profit factor | 0.99 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 83.12% |
| Turnover (1-way, per year) | 21.00 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -11.58% | 0.81 | 0.84 |
| E901-07 | -12.17% | 0.77 | 0.86 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 14.19% |
| 2011 | -11.99% |
| 2012 | 3.10% |
| 2013 | 20.77% |
| 2014 | 12.99% |
| 2015 | -16.13% |
| 2016 | -13.34% |
| 2017 | 11.87% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 93708.89 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.045404; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 5428 orders vs QuantConnect Total Orders 5428 |
| fills_match_harness_count | pass | downloaded fill events 5423 vs harness-recorded fills 5423 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 5423 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `12782933ab50f841d9a1c4fe66d5d7469898c6679f60f0a66481ff0d1caec798`
- fills_sha256: `3a37c2d3f7db561c0739f1d1b6770c62bbbba550b03c7deee23061951c933d3b`
- trades_sha256: `d5d276bc0e46bf92e2833387052ea69ecaa670a631b21011c8d33189581c0b80`
