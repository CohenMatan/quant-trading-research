# E962-16 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series B: breadth beyond the $100K limit: 30 slots at $250K, hold 20, seed 1. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `ffb0caa5aad0e1ca83c2056b6b39f3327f05580e` · **QC backtest:** `93e60b7e4abc43eb05f689246075d125` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:09:20Z · **runtime:** 478s
- **Parameters:** `{'slots': 30, 'hold': 20, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 30, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 9.43% |
| Annualised volatility | 13.88% |
| Sharpe (rf = 0) | 0.72 |
| Sortino | 1.01 |
| Max drawdown | -19.13% |
| Longest drawdown (trading days) | 334 |
| Calmar | 0.49 |
| Worst year | -6.95% |
| Worst month | -7.22% |
| Closed trades | 2703 |
| Win rate | 55.16% |
| Average winner | 6.12% |
| Average loser | -5.77% |
| Expectancy per trade | 0.79% |
| Profit factor | 1.27 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 82.76% |
| Turnover (1-way, per year) | 9.98 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -3.91% | 0.89 | 0.92 |
| E901-07 | -4.49% | 0.85 | 0.95 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 23.79% |
| 2011 | -2.46% |
| 2012 | 13.28% |
| 2013 | 17.19% |
| 2014 | 4.90% |
| 2015 | -6.95% |
| 2016 | 10.96% |
| 2017 | 18.30% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 242102.67 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.082459; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 8 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.357374496191288e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 5437 orders vs QuantConnect Total Orders 5437 |
| fills_match_harness_count | pass | downloaded fill events 5436 vs harness-recorded fills 5436 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 5436 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `a31e88acd9c7f1115db18bd6809c7b6e534a264e02331f6a4beefbcebcea38a2`
- fills_sha256: `a610a2492c4d09f08cedc59b37ec9ef074c9d837edfa78c43f5a6992d42801e4`
- trades_sha256: `300df4e4074c0545564c3b87b126011ecce2b93ea38c5890acc1e185f28cd811`
