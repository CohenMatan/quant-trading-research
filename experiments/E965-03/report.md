# E965-03 — X965 v1.1 (infrastructure)

P2 canary: trend-only mode with a 20-session horizon (frequent horizon rolls and MA200 exits), $100K. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2011-12-30)
- **Commit:** `7d3fcbb5a0135ef9e97aaf1d127f46290b28b3f0` · **QC backtest:** `fc2d56e896ba42379dceb72bc4be92dd` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T22:26:37Z · **runtime:** 202s
- **Parameters:** `{'mode': 'c1', 'exit': 'A', 'limit': 20, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2011-12-30 (504 trading days) |
| CAGR | 10.80% |
| Annualised volatility | 30.39% |
| Sharpe (rf = 0) | 0.49 |
| Sortino | 0.69 |
| Max drawdown | -30.17% |
| Longest drawdown (trading days) | 128 |
| Calmar | 0.36 |
| Worst year | -7.40% |
| Worst month | -12.01% |
| Closed trades | 67 |
| Win rate | 32.84% |
| Average winner | 28.46% |
| Average loser | -10.80% |
| Expectancy per trade | 2.09% |
| Profit factor | 1.08 |
| Average holding (calendar days) | 110.0 |
| Average exposure | 90.70% |
| Turnover (1-way, per year) | 2.41 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | 3.38% | 1.22 | 0.80 |
| E901-07 | 0.36% | 1.17 | 0.85 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 32.38% |
| 2011 | -7.40% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 504 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2011-12-30 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 88853.97 |
| equity_complete | pass | chart rows 504 vs algorithm days 504 |
| equity_matches_qc_tradeable_dates | pass | chart rows 504 vs QuantConnect tradeableDates 504 |
| no_leverage | pass | min cash/equity 0.023987; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.0058560358130133e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 146 orders vs QuantConnect Total Orders 146 |
| fills_match_harness_count | pass | downloaded fill events 146 vs harness-recorded fills 146 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 146 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ed7c30334d6c569510f5a97bb208da1c6fa44dc74fca6b8f33a543e01577f292`
- fills_sha256: `f6a3c4354bfdce818ffef384ec4821e52df54e05169a9a215e8fca39d238f5f6`
- trades_sha256: `810aa5595a432df3eb3ae77c9ca856d8b1063fabb5ca4dadd91c84939b25acf4`
