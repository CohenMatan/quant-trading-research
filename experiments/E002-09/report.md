# E002-09 — S002 v1.0 (research)

C01 H002 S002 v1.0 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E002-01 under D051 with the D054 harness fix (replaces E002-05)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `ec6ce393ea18bd1a3a0d86057fec447ab63aca8c` · **QC backtest:** `d34896b1f082c058a9e6e5e14c3da3ad` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T08:21:46Z · **runtime:** 394s
- **Parameters:** `{'lookback': 252, 'skip': 21, 'every_months': 1, 'slots': 15, 'band': 0.25, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.57% |
| Annualised volatility | 21.53% |
| Sharpe (rf = 0) | 0.45 |
| Sortino | 0.61 |
| Max drawdown | -37.15% |
| Longest drawdown (trading days) | 606 |
| Calmar | 0.20 |
| Worst year | -6.42% |
| Worst month | -13.86% |
| Closed trades | 349 |
| Win rate | 55.01% |
| Average winner | 19.90% |
| Average loser | -16.12% |
| Expectancy per trade | 3.70% |
| Profit factor | 1.30 |
| Average holding (calendar days) | 90.5 |
| Average exposure | 70.00% |
| Turnover (1-way, per year) | 2.75 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.77% | 1.00 | 0.67 |
| E901-05 | -6.17% | 1.01 | 0.72 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 13.72% |
| 2011 | -3.32% |
| 2012 | 28.28% |
| 2013 | 18.31% |
| 2014 | -6.42% |
| 2015 | 1.80% |
| 2016 | 3.05% |
| 2017 | 9.34% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 88112.97 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.116468; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 19 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.955482056239172e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 789 orders vs QuantConnect Total Orders 789 |
| fills_match_harness_count | pass | downloaded fill events 789 vs harness-recorded fills 789 |
| commission_fixed_per_order | pass | 789 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `61cb7400e5e1d7d27ba9b93ce8359cbc5835acb0e7413d7ce571ecac038508d8`
- fills_sha256: `31d58f3257b548c63c8a6377240efa2b00534d7e0a2404d7a27eb56bf587c2d8`
- trades_sha256: `6b8560295136f570ca0d303be311bd99534acbdebf1accb24ea8baeb30973446`
