# E901-03 — B901 v1.0 (benchmark)

Benchmark: equal-weight eligible >= $2B universe, monthly rebalance, 25% band. Official 2010 scheme (D034), with the D029 (NaN volume) and D030 (US-common rule) fixes; replaces E901-01. Re-run of E901-02 on the final D049 harness (forced-liquidation \$7 debit, verified-complete order download).

- **Status:** completed
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `5ed55205bd432720c27443c09f44d0ef37d07bab` · **QC backtest:** `194e6cf0e5ebac57db4ca94b1cea4a54` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T11:02:54Z · **runtime:** 438s
- **Parameters:** `{'band': 0.25, 'shard_count': 1, 'shard_index': 0}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 13.78% |
| Annualised volatility | 18.24% |
| Sharpe (rf = 0) | 0.80 |
| Sortino | 1.11 |
| Max drawdown | -38.59% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.36 |
| Worst year | -8.43% |
| Worst month | -19.23% |
| Closed trades | 4051 |
| Win rate | 22.59% |
| Average winner | 35.65% |
| Average loser | -16.02% |
| Expectancy per trade | -4.35% |
| Profit factor | 0.56 |
| Average holding (calendar days) | 378.4 |
| Average exposure | 96.53% |
| Turnover (1-way, per year) | 0.41 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 14.15% |
| Annualised volatility | 15.76% |
| Sharpe (rf = 0) | 0.92 |
| Sortino | 1.30 |
| Max drawdown | -22.40% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.63 |
| Worst year | -3.21% |
| Worst month | -8.70% |
| Average exposure | 96.25% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 12.85% |
| Annualised volatility | 22.40% |
| Sharpe (rf = 0) | 0.65 |
| Sortino | 0.89 |
| Max drawdown | -38.59% |
| Longest drawdown (trading days) | 210 |
| Calmar | 0.33 |
| Worst year | -9.14% |
| Worst month | -19.23% |
| Average exposure | 97.08% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 23.85% |
| 2011 | 0.03% |
| 2012 | 16.99% |
| 2013 | 36.13% |
| 2014 | 10.53% |
| 2015 | -3.21% |
| 2016 | 14.87% |
| 2017 | 18.66% |
| 2018 | -8.43% |
| 2019 | 27.19% |
| 2020 | 19.94% |
| 2021 | 16.93% |

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
| fills_after_signal_date | pass | 0 violations, 465 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 22058 orders vs QuantConnect Total Orders 22058 |
| fills_match_harness_count | pass | downloaded fill events 22042 vs harness-recorded fills 22042 |
| commission_fixed_per_order | pass | 22042 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `572877ab3dbaafb1cc1167bad93d904e184a461dd3c12bbcfda48fd7870d23a0`
- fills_sha256: `22135bf55338f0a708341e535db0a5ab2acd6481c8f51c5323c0b7ada25821d9`
- trades_sha256: `ac5ae641c166cce41257380495ef054b8e9f5abbe5a2425b501f26792475a6a1`
