# E950-03 — X950 v1.0 (infrastructure)

Execution-timing canary under the 2010 scheme and the fixed $7/order commission (D039): verifies T+1 open fills, slippage, and that every executed order is charged exactly $7.

- **Status:** completed
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `2519cc67908fd80f68e175cbdc1827e009a03551` · **QC backtest:** `7253827e2c560391040adc561db65a37` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T10:37:46Z · **runtime:** 19s
- **Parameters:** `{'weight': 0.24}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.25, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 4.98% |
| Annualised volatility | 17.31% |
| Sharpe (rf = 0) | 0.37 |
| Sortino | 0.52 |
| Max drawdown | -41.26% |
| Longest drawdown (trading days) | 1502 |
| Calmar | 0.12 |
| Worst year | -25.47% |
| Worst month | -15.94% |
| Closed trades | 1204 |
| Win rate | 51.99% |
| Average winner | 3.32% |
| Average loser | -3.31% |
| Expectancy per trade | 0.14% |
| Profit factor | 1.06 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 96.03% |
| Turnover (1-way, per year) | 24.14 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.02% |
| Annualised volatility | 14.68% |
| Sharpe (rf = 0) | 0.41 |
| Sortino | 0.58 |
| Max drawdown | -21.06% |
| Longest drawdown (trading days) | 675 |
| Calmar | 0.24 |
| Worst year | -7.85% |
| Worst month | -8.96% |
| Average exposure | 96.00% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 4.81% |
| Annualised volatility | 21.63% |
| Sharpe (rf = 0) | 0.33 |
| Sortino | 0.45 |
| Max drawdown | -37.34% |
| Longest drawdown (trading days) | 792 |
| Calmar | 0.13 |
| Worst year | -25.81% |
| Worst month | -15.94% |
| Average exposure | 96.08% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 2.08% |
| 2011 | 7.32% |
| 2012 | 14.46% |
| 2013 | 15.38% |
| 2014 | 7.62% |
| 2015 | -7.85% |
| 2016 | -2.14% |
| 2017 | 5.30% |
| 2018 | -25.47% |
| 2019 | 26.92% |
| 2020 | 0.27% |
| 2021 | 27.77% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 83292.04 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.0022 |
| cash_never_negative | pass | min cash/equity 0.0022 |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.9465308380415215e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| commission_fixed_per_order | pass | 2412 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `338d015ed4817ddea5676fb825261816e695ffe4ee35a79cabea75f7d09e9958`
- fills_sha256: `aa5a9b734dd4061732bd79df060e61ebcdfccd0781f5bb74e603e837b99d592d`
- trades_sha256: `8b40058e602b42e4edc5457b5eca92f01625fd2cab617436ff3fd26ef266b954`
