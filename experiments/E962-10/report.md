# E962-10 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series A: account size: 15 slots at $250K, hold 20, seed 1. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `cd444d6ec3d29ffb747103c6b3779e673de76402` · **QC backtest:** `69fcd11237eb3358e64a2a06532f2707` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:26:09Z · **runtime:** 378s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.53% |
| Annualised volatility | 14.57% |
| Sharpe (rf = 0) | 0.76 |
| Sortino | 1.08 |
| Max drawdown | -18.42% |
| Longest drawdown (trading days) | 367 |
| Calmar | 0.57 |
| Worst year | -3.86% |
| Worst month | -7.83% |
| Closed trades | 1352 |
| Win rate | 55.18% |
| Average winner | 6.12% |
| Average loser | -5.45% |
| Expectancy per trade | 0.93% |
| Profit factor | 1.34 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 83.87% |
| Turnover (1-way, per year) | 10.13 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.81% | 0.90 | 0.88 |
| E901-07 | -3.39% | 0.86 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.65% |
| 2011 | 1.68% |
| 2012 | 18.48% |
| 2013 | 19.33% |
| 2014 | 5.50% |
| 2015 | -3.86% |
| 2016 | 9.19% |
| 2017 | 20.82% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 243611.59 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.044186; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.209735034398567e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2720 orders vs QuantConnect Total Orders 2720 |
| fills_match_harness_count | pass | downloaded fill events 2719 vs harness-recorded fills 2719 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 2719 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `a3a92c08899936fe354a193002003ae8839f4093a775e1dacb056d3d3838ec20`
- fills_sha256: `8fdd624eb3491ee0b5e1dc4b08250aabb858524f457a86875d1505009ff93007`
- trades_sha256: `fa49ff44d5d8d39ed80200c2426896261336428ad8911820272998a46219fdfc`
