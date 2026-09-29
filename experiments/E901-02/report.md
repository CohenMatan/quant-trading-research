# E901-02 — B901 v1.0 (benchmark)

Benchmark: equal-weight eligible >= $2B universe, monthly rebalance, 25% band. Official 2010 scheme (D034), with the D029 (NaN volume) and D030 (US-common rule) fixes; replaces E901-01.

- **Status:** completed
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `b0d70764c3564723beb0e491c6c895f664fd1fe2` · **QC backtest:** `89177ad299287567680d52ccbbbad01d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T10:49:14Z · **runtime:** 476s
- **Parameters:** `{'band': 0.25, 'shard_count': 1, 'shard_index': 0}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 13.77% |
| Annualised volatility | 18.24% |
| Sharpe (rf = 0) | 0.80 |
| Sortino | 1.11 |
| Max drawdown | -38.59% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.36 |
| Worst year | -8.46% |
| Worst month | -19.24% |
| Closed trades | 0 |
| Win rate | n/a |
| Average winner | n/a |
| Average loser | n/a |
| Expectancy per trade | n/a |
| Profit factor | n/a |
| Average holding (calendar days) | n/a |
| Average exposure | 96.53% |
| Turnover (1-way, per year) | 0.00 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 14.16% |
| Annualised volatility | 15.76% |
| Sharpe (rf = 0) | 0.92 |
| Sortino | 1.30 |
| Max drawdown | -22.40% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.63 |
| Worst year | -3.18% |
| Worst month | -8.70% |
| Average exposure | 96.25% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 12.82% |
| Annualised volatility | 22.40% |
| Sharpe (rf = 0) | 0.65 |
| Sortino | 0.88 |
| Max drawdown | -38.59% |
| Longest drawdown (trading days) | 210 |
| Calmar | 0.33 |
| Worst year | -9.17% |
| Worst month | -19.24% |
| Average exposure | 97.08% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 23.85% |
| 2011 | 0.03% |
| 2012 | 16.98% |
| 2013 | 36.15% |
| 2014 | 10.54% |
| 2015 | -3.18% |
| 2016 | 14.87% |
| 2017 | 18.64% |
| 2018 | -8.46% |
| 2019 | 27.18% |
| 2020 | 19.91% |
| 2021 | 16.90% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 9658458.43 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.0185 |
| cash_never_negative | pass | min cash/equity 0.0185 |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ed22b4ca012aff950ab587aaa4621783f4a0f3cae2f6ac82cf2b94247ccedfba`
- fills_sha256: `78a0962b9b70b6901d01d783a235cdae962b1dffa5be70026c022bbbddabc973`
- trades_sha256: `7099cb2261e2e834b28abe20af9c8e05779781d921eadddafc5db983545e4c35`
