# E001-05 — S001 v1.4 (research)

C01 H001 S001 v1.4 (pre-declared variation) on IS 2010-2017

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `26f1908f1ac79160a4cf08027757948c118b1bfa` · **QC backtest:** `180bcbf43eb44a01b25232ba05eb16a9` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T12:05:02Z · **runtime:** 338s
- **Parameters:** `{'entry': 'ret3', 'ret3_max': -0.06, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 14.26% |
| Annualised volatility | 22.66% |
| Sharpe (rf = 0) | 0.70 |
| Sortino | 1.03 |
| Max drawdown | -30.15% |
| Longest drawdown (trading days) | 606 |
| Calmar | 0.47 |
| Worst year | -10.74% |
| Worst month | -14.12% |
| Closed trades | 425 |
| Win rate | 56.47% |
| Average winner | 3.75% |
| Average loser | -4.08% |
| Expectancy per trade | 0.34% |
| Profit factor | 1.07 |
| Average holding (calendar days) | 20.7 |
| Average exposure | 94.86% |
| Turnover (1-way, per year) | 1.92 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-04 | 0.97% | 1.22 | 0.77 |
| E901-03 | 0.10% | 1.16 | 0.81 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 37.79% |
| 2011 | -0.11% |
| 2012 | 25.89% |
| 2013 | 34.85% |
| 2014 | 24.31% |
| 2015 | 6.21% |
| 2016 | -10.74% |
| 2017 | 5.24% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97673.97 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.0156 |
| cash_never_negative | pass | min cash/equity 0.0156 |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.6887609956713753e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 866 orders vs QuantConnect Total Orders 866 |
| fills_match_harness_count | pass | downloaded fill events 865 vs harness-recorded fills 865 |
| commission_fixed_per_order | pass | 865 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `fac661e9870f3644c3fad3c019ed222b3369d544ba96c0ca28a9ad86eefbf50b`
- fills_sha256: `b4f17b5c073ab6ddbefa1e5ec42c8277a0205d77d8db2ba6380ef6c20d6c32c9`
- trades_sha256: `20e687955beadc7b525a2026b884a9980473625df5c45922a256daee2301aff9`
