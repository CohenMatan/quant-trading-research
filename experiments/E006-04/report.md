# E006-04 — S006 v1.0 (research)

H006X Control A (D304): H006 v1.0 exactly (55-day high, volume >= 1.5x, SMA200, chandelier K 3.0, 60-session time stop, 10 slots) on QuantConnect's default build, DEV 2010-01-04 .. 2021-12-31. EXPLORATORY; H006 stays REJECTED.

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `82d76ccab7bb9541e0e6b084ac0c8c94afc3e236` · **QC backtest:** `eb51a7a049b7fedbe257b372ef5802c4` · **LEAN:** v2.5.0.0.18203 · **run:** 2026-10-24T17:47:19Z · **runtime:** 1016s
- **Parameters:** `{'n': 55, 'vol_mult': 1.5, 'use_volume': True, 'k': 3.0, 'slots': 10, 'time_stop': 60, 'h006x_spec_sha256': 'ae016962e71686aacc383b4da7336fe166ecc9c14b68eb17bbcba5192d42fb5e', 'h006x_code_sha256': {'main.py': 'da3e810179df7288892a2b8210c85471b3659beed89cac5aaa2be7d5f6efd65e', 'signals.py': '91ada940e221f3aa558e29223ccd92f4cbb83f3c16935e21cf86f96487c46a0f'}}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 12.29% |
| Annualised volatility | 20.20% |
| Sharpe (rf = 0) | 0.67 |
| Sortino | 1.06 |
| Max drawdown | -31.63% |
| Longest drawdown (trading days) | 493 |
| Calmar | 0.39 |
| Worst year | -9.11% |
| Worst month | -12.04% |
| Closed trades | 809 |
| Win rate | 45.49% |
| Average winner | 11.94% |
| Average loser | -7.20% |
| Expectancy per trade | 1.51% |
| Profit factor | 1.35 |
| Average holding (calendar days) | 51.3 |
| Average exposure | 90.98% |
| Turnover (1-way, per year) | 6.34 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-08 | -2.30% | 0.61 | 0.50 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 19.23% |
| 2011 | -7.32% |
| 2012 | 14.75% |
| 2013 | 35.33% |
| 2014 | 5.80% |
| 2015 | 8.13% |
| 2016 | 16.65% |
| 2017 | 21.39% |
| 2018 | -9.11% |
| 2019 | 15.76% |
| 2020 | 7.68% |
| 2021 | 27.42% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96315.08 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.006037; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 18 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.8068399965528896e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1631 orders vs QuantConnect Total Orders 1631 |
| fills_match_harness_count | pass | downloaded fill events 1628 vs harness-recorded fills 1628 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1628 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `0fa9b003483948a07c5a0f90c6d40fa522b98fc4a486761cbcc5b38ead624de3`
- fills_sha256: `50fd1a07f5b29f75d9167425fc162736f2861d3f749887276a437b9cdf9bfd6f`
- trades_sha256: `c12fce6a3f1ba794460c942228487404c7e4b787b06cda2a838eda7d10be054b`
