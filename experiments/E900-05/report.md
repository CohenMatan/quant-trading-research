# E900-05 — B900 v1.0 (benchmark)

Benchmark: SPY buy-and-hold, dividends reinvested monthly. Official 2010 scheme (D034): IS+VAL 2010-01-04..2021-12-31. Re-run of E900-04 under the D051 no-borrowing execution model.

- **Status:** completed
- **Split:** FULL (2010-01-04 → 2021-12-31)
- **Commit:** `8d502d52ac3647a7ea5e2567be7ea1f6631247b7` · **QC backtest:** `db94c1480047fb991e6ea40db585be76` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-28T14:44:50Z · **runtime:** 23s
- **Parameters:** `{'weight': 0.98}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': "D039: $7 per executed buy or sell order (owner's broker); slippage separate"}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 1.0, 'cash_buffer': 0.02, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 14.59% |
| Annualised volatility | 16.57% |
| Sharpe (rf = 0) | 0.91 |
| Sortino | 1.26 |
| Max drawdown | -33.06% |
| Longest drawdown (trading days) | 192 |
| Calmar | 0.44 |
| Worst year | -4.45% |
| Worst month | -12.26% |
| Closed trades | 0 |
| Win rate | n/a |
| Average winner | n/a |
| Average loser | n/a |
| Expectancy per trade | n/a |
| Profit factor | n/a |
| Average holding (calendar days) | n/a |
| Average exposure | 97.73% |
| Turnover (1-way, per year) | 0.03 |

### Segment IS

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 13.34% |
| Annualised volatility | 14.33% |
| Sharpe (rf = 0) | 0.95 |
| Sortino | 1.34 |
| Max drawdown | -18.30% |
| Longest drawdown (trading days) | 192 |
| Calmar | 0.73 |
| Worst year | 1.27% |
| Worst month | -7.76% |
| Average exposure | 97.66% |
| Turnover (1-way, per year) | n/a |

### Segment VAL

| Metric | Value |
|---|---|
| Period | 2018-01-02 → 2021-12-31 (1008 trading days) |
| CAGR | 16.96% |
| Annualised volatility | 20.33% |
| Sharpe (rf = 0) | 0.87 |
| Sortino | 1.20 |
| Max drawdown | -33.06% |
| Longest drawdown (trading days) | 139 |
| Calmar | 0.51 |
| Worst year | -5.12% |
| Worst month | -12.26% |
| Average exposure | 97.88% |
| Turnover (1-way, per year) | n/a |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 13.25% |
| 2011 | 1.79% |
| 2012 | 15.68% |
| 2013 | 31.37% |
| 2014 | 13.15% |
| 2015 | 1.27% |
| 2016 | 11.71% |
| 2017 | 21.18% |
| 2018 | -4.45% |
| 2019 | 30.48% |
| 2020 | 17.96% |
| 2021 | 28.05% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 91488.42 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.018100; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.729208065967196e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 90 orders vs QuantConnect Total Orders 90 |
| fills_match_harness_count | pass | downloaded fill events 90 vs harness-recorded fills 90 |
| commission_fixed_per_order | pass | 90 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `234a8596128d9077102fb2e46ddf19f5c0493db35304142cfbdb1a27f7374721`
- fills_sha256: `aa09044fef961cfdf0337fb5ab5849cb16e020a4fdd7b7639f4377d9e4a2e65d`
- trades_sha256: `d633ec70b0db0556abada3c97fb5baedf38b4061b29fa5d6019a8c61bc282903`
