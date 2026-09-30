# E962-07 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 19 slots at $100K, hold 20, seed 1. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `6a0f89f82a9bcc12b5b585caa1ec95d55bd47d53` · **QC backtest:** `e062bb34eb07efde4ff031ab6c225b85` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:07:07Z · **runtime:** 407s
- **Parameters:** `{'slots': 19, 'hold': 20, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 19, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 0.60% |
| Annualised volatility | 8.63% |
| Sharpe (rf = 0) | 0.11 |
| Sortino | 0.16 |
| Max drawdown | -16.51% |
| Longest drawdown (trading days) | 598 |
| Calmar | 0.04 |
| Worst year | -5.63% |
| Worst month | -6.31% |
| Closed trades | 473 |
| Win rate | 50.32% |
| Average winner | 5.87% |
| Average loser | -5.85% |
| Expectancy per trade | 0.05% |
| Profit factor | 1.01 |
| Average holding (calendar days) | 30.1 |
| Average exposure | 24.16% |
| Turnover (1-way, per year) | 2.98 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -12.74% | 0.32 | 0.53 |
| E901-07 | -13.32% | 0.29 | 0.53 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 0.89% |
| 2011 | 0.36% |
| 2012 | -0.08% |
| 2013 | 0.14% |
| 2014 | 7.41% |
| 2015 | 0.27% |
| 2016 | -5.63% |
| 2017 | 1.89% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 92356.85 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.027903; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.6303945933115617e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 946 orders vs QuantConnect Total Orders 946 |
| fills_match_harness_count | pass | downloaded fill events 946 vs harness-recorded fills 946 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 946 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `da30ceb98173d2af048c7103b77ffe79c096d07ad9df3a3f535cfeee337d8007`
- fills_sha256: `639baf9f4f8dff00bc634c49e5b44016b5baa2b46352371fa4322fba4eb159c9`
- trades_sha256: `86d7b45162b2dbe7d88a9d4fe28d2a48c76b7bb30385a863282f5c396fdc9754`
