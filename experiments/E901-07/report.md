# E901-07 — B901 v1.0 (benchmark)

Benchmark: equal-weight eligible >= $2B universe, monthly rebalance, 25% band. Official 2010 scheme (D034), with the D029 (NaN volume) and D030 (US-common rule) fixes; replaces E901-01. Re-run of E901-03 under the D051 no-borrowing execution model. | final D057 (dated overrides) harness (replaces E901-06 as the C01 IS comparison benchmark for the H001 remedial re-test)

- **Status:** completed_with_warnings
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `e8c99813d1bc50a1229b46b424cb759660489eaa` · **QC backtest:** `6996126bb441f2a7e04b7a7e624b5ea0` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T15:14:45Z · **runtime:** 691s
- **Parameters:** `{'band': 0.25, 'shard_count': 1, 'shard_index': 0}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 13.48% |
| Annualised volatility | 17.80% |
| Sharpe (rf = 0) | 0.80 |
| Sortino | 1.10 |
| Max drawdown | -37.72% |
| Longest drawdown (trading days) | 282 |
| Calmar | 0.36 |
| Worst year | -8.42% |
| Worst month | -18.61% |
| Closed trades | 3777 |
| Win rate | 21.34% |
| Average winner | 40.19% |
| Average loser | -16.51% |
| Expectancy per trade | -4.41% |
| Profit factor | 0.58 |
| Average holding (calendar days) | 383.2 |
| Average exposure | 94.09% |
| Turnover (1-way, per year) | 0.35 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.93% |
| Annualised volatility | 15.48% |
| Sharpe (rf = 0) | 0.92 |
| Sortino | 1.30 |
| Max drawdown | -22.29% |
| Longest drawdown (trading days) | 282 |
| Calmar | 0.62 |
| Worst year | -2.24% |
| Worst month | -8.65% |
| Average exposure | 93.91% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 12.43% |
| Annualised volatility | 21.72% |
| Sharpe (rf = 0) | 0.65 |
| Sortino | 0.88 |
| Max drawdown | -37.72% |
| Longest drawdown (trading days) | 210 |
| Calmar | 0.33 |
| Worst year | -9.09% |
| Worst month | -18.61% |
| Average exposure | 94.43% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 22.05% |
| 2011 | -0.22% |
| 2012 | 16.80% |
| 2013 | 35.43% |
| 2014 | 10.59% |
| 2015 | -2.24% |
| 2016 | 14.52% |
| 2017 | 18.74% |
| 2018 | -8.42% |
| 2019 | 27.26% |
| 2020 | 18.52% |
| 2021 | 16.44% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 9663475.20 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.034308; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 445 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 23131 orders vs QuantConnect Total Orders 23131 |
| fills_match_harness_count | pass | downloaded fill events 23123 vs harness-recorded fills 23123 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | warn | 4 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 4 mirrored |
| commission_fixed_per_order | pass | 23127 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c8b5920aa3e3d358d0ce510b469a8bdd588d8c74b5638084590b79dfc77bff85`
- fills_sha256: `112e97d5ae8bd41026a90d2dfe09261ed33a0eb46e7fc989b2357c14cb71d375`
- trades_sha256: `84c0db80c7f92a7ea7f2290dfd72f6d6c3e197d84b6762d2f4a7e337d326f66c`
