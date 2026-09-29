# E901-05 — B901 v1.0 (benchmark)

Benchmark: equal-weight eligible >= $2B universe, monthly rebalance, 25% band. Official 2010 scheme (D034), with the D029 (NaN volume) and D030 (US-common rule) fixes; replaces E901-01. Re-run of E901-03 under the D051 no-borrowing execution model. | D054 harness fix re-verification (replaces E901-04)

- **Status:** completed
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `a5720ce954ee4835e6c8bc3fb84a812830c700f2` · **QC backtest:** `0f6d5d4e1beffdfc3e36ceb78dc30fa7` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T07:35:27Z · **runtime:** 600s
- **Parameters:** `{'band': 0.25, 'shard_count': 1, 'shard_index': 0}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 13.30% |
| Annualised volatility | 17.67% |
| Sharpe (rf = 0) | 0.80 |
| Sortino | 1.10 |
| Max drawdown | -37.78% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.35 |
| Worst year | -8.38% |
| Worst month | -18.78% |
| Closed trades | 4051 |
| Win rate | 21.85% |
| Average winner | 38.03% |
| Average loser | -16.41% |
| Expectancy per trade | -4.52% |
| Profit factor | 0.58 |
| Average holding (calendar days) | 378.4 |
| Average exposure | 94.03% |
| Turnover (1-way, per year) | 0.35 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.74% |
| Annualised volatility | 15.37% |
| Sharpe (rf = 0) | 0.91 |
| Sortino | 1.29 |
| Max drawdown | -22.12% |
| Longest drawdown (trading days) | 288 |
| Calmar | 0.62 |
| Worst year | -2.87% |
| Worst month | -8.57% |
| Average exposure | 93.84% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 12.25% |
| Annualised volatility | 21.56% |
| Sharpe (rf = 0) | 0.65 |
| Sortino | 0.87 |
| Max drawdown | -37.78% |
| Longest drawdown (trading days) | 210 |
| Calmar | 0.32 |
| Worst year | -9.06% |
| Worst month | -18.78% |
| Average exposure | 94.42% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 22.11% |
| 2011 | 0.01% |
| 2012 | 16.59% |
| 2013 | 35.28% |
| 2014 | 10.40% |
| 2015 | -2.87% |
| 2016 | 14.45% |
| 2017 | 18.26% |
| 2018 | -8.38% |
| 2019 | 27.01% |
| 2020 | 17.58% |
| 2021 | 16.85% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 9679273.90 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.036449; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 465 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 24393 orders vs QuantConnect Total Orders 24393 |
| fills_match_harness_count | pass | downloaded fill events 24378 vs harness-recorded fills 24378 |
| commission_fixed_per_order | pass | 24378 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `8e888aa080056aaf5e869b2bfbc14434c89b3c3f5521ba4fdbe2a48a9cac1957`
- fills_sha256: `685477987c7c17740c056d139db55d3cfbcb882e20ad5dac1dafe45021c21204`
- trades_sha256: `14ea3db154cbf923bea8749b43c53d957e48ce823b5137c668443ff2421839bf`
