# E003-01 — S003 v1.0 (research)

C01 H003 S003 v1.0 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `e5afdcf5911d9cf3c627b2fd0e3454c8db54bdb3` · **QC backtest:** `11d908b4f2ecab23ffedaafddb9f8939` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T13:05:42Z · **runtime:** 341s
- **Parameters:** `{'rebalance': 'monthly', 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.23% |
| Annualised volatility | 14.13% |
| Sharpe (rf = 0) | 0.76 |
| Sortino | 1.06 |
| Max drawdown | -20.61% |
| Longest drawdown (trading days) | 432 |
| Calmar | 0.50 |
| Worst year | -2.16% |
| Worst month | -7.72% |
| Closed trades | 1242 |
| Win rate | 54.27% |
| Average winner | 5.50% |
| Average loser | -4.81% |
| Expectancy per trade | 0.79% |
| Profit factor | 1.35 |
| Average holding (calendar days) | 34.1 |
| Average exposure | 95.68% |
| Turnover (1-way, per year) | 10.16 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | -3.05% | 0.80 | 0.81 |
| E901-03 | -3.92% | 0.75 | 0.84 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.97% |
| 2011 | -2.16% |
| 2012 | 5.81% |
| 2013 | 26.30% |
| 2014 | 2.64% |
| 2015 | 4.66% |
| 2016 | 10.90% |
| 2017 | 23.72% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 95033.00 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0113 |
| cash_never_negative | pass | min cash/equity 0.0113 |
| fills_after_signal_date | pass | 0 violations, 27 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.092280125712233e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2502 orders vs QuantConnect Total Orders 2502 |
| fills_match_harness_count | pass | downloaded fill events 2500 vs harness-recorded fills 2500 |
| commission_fixed_per_order | pass | 2500 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `fde7a7bef369ff315131fe5402bc65a64bfcd4d6068fb25b1e6203b284bb320f`
- fills_sha256: `efdbad04ee19682e9a7865b68605a4a77cb1f72b1ceb652cff0558a756dc5499`
- trades_sha256: `b5d357d89cc9da88bcf64da9fdc6136815d6d5d3fe86e4728067eeaef3defb89`
