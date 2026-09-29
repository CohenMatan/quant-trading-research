# E005-18 — S005 v1.2 (research)

C01 robustness of E005-12: plateau vol_days 32 (base 63) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `dba79cdb9098bc6cefa930dfbd32789f4172e32a` · **QC backtest:** `1c99d9f86d6b2fed8c6028cb5d3e6e88` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T10:33:49Z · **runtime:** 342s
- **Parameters:** `{'vol_days': 32, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 6.60% |
| Annualised volatility | 4.83% |
| Sharpe (rf = 0) | 1.35 |
| Sortino | 2.04 |
| Max drawdown | -4.78% |
| Longest drawdown (trading days) | 223 |
| Calmar | 1.38 |
| Worst year | 3.01% |
| Worst month | -2.39% |
| Closed trades | 509 |
| Win rate | 61.30% |
| Average winner | 3.92% |
| Average loser | -3.03% |
| Expectancy per trade | 1.23% |
| Profit factor | 1.98 |
| Average holding (calendar days) | 55.7 |
| Average exposure | 62.27% |
| Turnover (1-way, per year) | 3.94 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -6.74% | 0.25 | 0.74 |
| E901-05 | -7.14% | 0.23 | 0.72 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.02% |
| 2011 | 8.12% |
| 2012 | 7.22% |
| 2013 | 11.54% |
| 2014 | 5.01% |
| 2015 | 6.72% |
| 2016 | 3.01% |
| 2017 | 3.31% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98525.73 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.093947; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 116 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.057976964382307e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1031 orders vs QuantConnect Total Orders 1031 |
| fills_match_harness_count | pass | downloaded fill events 1030 vs harness-recorded fills 1030 |
| commission_fixed_per_order | pass | 1030 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3e219d9233fbe70f09a28bf5f51e526694f9e2a011b0e156aa43dce2c12f8a79`
- fills_sha256: `fed1655b5ba44b1fd1662dc474a62b8cfd20051cc6756ec3c213659e07a3d754`
- trades_sha256: `847cb2d0dae38d497639bec5eeb1874c9aade6f1a8cc2d9d89bfd7a1c9f5aebb`
