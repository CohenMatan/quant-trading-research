# E005-16 — S005 v1.2 (research)

C01 robustness of E005-12: slippage 4x (40 bps/side) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `92d4121bd3eb8876f9842900f521b7ef33ecf778` · **QC backtest:** `87eb973b67f73d9d15dd0f0f5d7d2ff5` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T10:21:33Z · **runtime:** 343s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate', 'slippage_stress_multiple': 4}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 6.60% |
| Annualised volatility | 5.86% |
| Sharpe (rf = 0) | 1.12 |
| Sortino | 1.67 |
| Max drawdown | -5.59% |
| Longest drawdown (trading days) | 229 |
| Calmar | 1.18 |
| Worst year | 0.45% |
| Worst month | -3.68% |
| Closed trades | 408 |
| Win rate | 56.86% |
| Average winner | 5.17% |
| Average loser | -3.53% |
| Expectancy per trade | 1.42% |
| Profit factor | 1.81 |
| Average holding (calendar days) | 74.9 |
| Average exposure | 67.71% |
| Turnover (1-way, per year) | 3.21 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -6.74% | 0.31 | 0.76 |
| E901-05 | -7.14% | 0.28 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 9.96% |
| 2011 | 10.63% |
| 2012 | 3.12% |
| 2013 | 14.33% |
| 2014 | 3.22% |
| 2015 | 7.87% |
| 2016 | 0.45% |
| 2017 | 3.85% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97810.53 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.075011; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 71 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.2071164453680688e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 828 orders vs QuantConnect Total Orders 828 |
| fills_match_harness_count | pass | downloaded fill events 828 vs harness-recorded fills 828 |
| commission_fixed_per_order | pass | 828 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `81dd2275fcdedf175cbb449690f80f2f1dca84cc26511fd1b779e9f7773033bd`
- fills_sha256: `9620c42cb8a8169d138b89701dbf8d5ab074ba536628fe36e9076805f2c577b1`
- trades_sha256: `b523bcdc2a35c7e5a4cd706d8b65ab513ce7634062dd3b387448e69b74528497`
