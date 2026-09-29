# E901-06 — B901 v1.0 (benchmark)

Benchmark: equal-weight eligible >= $2B universe, monthly rebalance, 25% band. Official 2010 scheme (D034), with the D029 (NaN volume) and D030 (US-common rule) fixes; replaces E901-01. Re-run of E901-03 under the D051 no-borrowing execution model. | D057/D059 harness re-verification (replaces E901-05)

- **Status:** completed_with_warnings
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `feda4060ad1659ed7b715f0f6faea8ff95dda769` · **QC backtest:** `95d79e396063db5f661173ae66d8583d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T13:34:42Z · **runtime:** 592s
- **Parameters:** `{'band': 0.25, 'shard_count': 1, 'shard_index': 0}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 13.50% |
| Annualised volatility | 17.81% |
| Sharpe (rf = 0) | 0.80 |
| Sortino | 1.11 |
| Max drawdown | -37.73% |
| Longest drawdown (trading days) | 282 |
| Calmar | 0.36 |
| Worst year | -8.39% |
| Worst month | -18.63% |
| Closed trades | 3785 |
| Win rate | 21.29% |
| Average winner | 40.26% |
| Average loser | -16.45% |
| Expectancy per trade | -4.38% |
| Profit factor | 0.59 |
| Average holding (calendar days) | 382.0 |
| Average exposure | 94.08% |
| Turnover (1-way, per year) | 0.35 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.95% |
| Annualised volatility | 15.49% |
| Sharpe (rf = 0) | 0.92 |
| Sortino | 1.30 |
| Max drawdown | -22.34% |
| Longest drawdown (trading days) | 282 |
| Calmar | 0.62 |
| Worst year | -2.25% |
| Worst month | -8.68% |
| Average exposure | 93.91% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 12.44% |
| Annualised volatility | 21.73% |
| Sharpe (rf = 0) | 0.65 |
| Sortino | 0.88 |
| Max drawdown | -37.73% |
| Longest drawdown (trading days) | 210 |
| Calmar | 0.33 |
| Worst year | -9.06% |
| Worst month | -18.63% |
| Average exposure | 94.42% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 22.09% |
| 2011 | -0.24% |
| 2012 | 16.83% |
| 2013 | 35.46% |
| 2014 | 10.55% |
| 2015 | -2.25% |
| 2016 | 14.51% |
| 2017 | 18.88% |
| 2018 | -8.39% |
| 2019 | 27.34% |
| 2020 | 18.44% |
| 2021 | 16.48% |

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
| no_leverage | pass | min cash/equity 0.034332; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 446 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 23108 orders vs QuantConnect Total Orders 23108 |
| fills_match_harness_count | pass | downloaded fill events 23099 vs harness-recorded fills 23099 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | warn | 4 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 4 mirrored |
| commission_fixed_per_order | pass | 23103 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ea7e706eeea0f4fc59e4078d7737385573efac1e407cbebee72c7bad3f9fe2ea`
- fills_sha256: `1650a25a1fbdf4af1424a596323cfb3023c4b0e5fcf3cf70ba1301a2233dc09a`
- trades_sha256: `62152f122e3403153cd39d0d768566f6d07b5b9728634a56a02bf6f6b8b02024`
