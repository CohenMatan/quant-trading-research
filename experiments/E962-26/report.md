# E962-26 — X962 v1.0 (infrastructure)

C03 S1 null ($200K, 15 slots, hold 60, seed 2). Not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `b1f7ba3455f13575354afc232b499ee9b49b1c84` · **QC backtest:** `3bdeb82b463ac88115389af6369ec8fa` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T18:48:20Z · **runtime:** 314s
- **Parameters:** `{'slots': 15, 'hold': 60, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 12.13% |
| Annualised volatility | 15.00% |
| Sharpe (rf = 0) | 0.84 |
| Sortino | 1.17 |
| Max drawdown | -25.74% |
| Longest drawdown (trading days) | 373 |
| Calmar | 0.47 |
| Worst year | -9.52% |
| Worst month | -10.96% |
| Closed trades | 481 |
| Win rate | 61.95% |
| Average winner | 11.16% |
| Average loser | -10.66% |
| Expectancy per trade | 2.86% |
| Profit factor | 1.65 |
| Average holding (calendar days) | 87.9 |
| Average exposure | 84.21% |
| Turnover (1-way, per year) | 3.57 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.21% | 0.93 | 0.89 |
| E901-07 | -1.80% | 0.89 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 23.19% |
| 2011 | -9.52% |
| 2012 | 17.65% |
| 2013 | 26.65% |
| 2014 | 10.35% |
| 2015 | 2.87% |
| 2016 | 24.72% |
| 2017 | 6.06% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 194141.50 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.096374; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 7 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 977 orders vs QuantConnect Total Orders 977 |
| fills_match_harness_count | pass | downloaded fill events 977 vs harness-recorded fills 977 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 977 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `aeaf50649066f5209a8481d43bd6d7196ccb0bc6847b606b2f048698485e4e30`
- fills_sha256: `14c918c68732d4f023f9cdf3f5e13ddc4f8a6bcb1acb6e4f5f03be2faf164d15`
- trades_sha256: `10f1790c14686ae00fc719b709c85f3af126c118353c45c1e3b68b52faadf81d`
