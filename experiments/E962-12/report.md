# E962-12 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series A: account size: 15 slots at $250K, hold 20, seed 3. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `6954954e92cfed011ac28b9ec31213b3f8b75465` · **QC backtest:** `dca968e4c159fcb7d22c5c7fdb4538ce` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:44:12Z · **runtime:** 265s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.79% |
| Annualised volatility | 14.56% |
| Sharpe (rf = 0) | 0.78 |
| Sortino | 1.10 |
| Max drawdown | -16.79% |
| Longest drawdown (trading days) | 280 |
| Calmar | 0.64 |
| Worst year | 2.65% |
| Worst month | -9.45% |
| Closed trades | 1352 |
| Win rate | 57.03% |
| Average winner | 5.96% |
| Average loser | -5.84% |
| Expectancy per trade | 0.89% |
| Profit factor | 1.31 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 82.42% |
| Turnover (1-way, per year) | 9.96 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.55% | 0.89 | 0.88 |
| E901-07 | -3.14% | 0.86 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.82% |
| 2011 | 3.23% |
| 2012 | 6.92% |
| 2013 | 29.09% |
| 2014 | 6.21% |
| 2015 | 5.17% |
| 2016 | 2.65% |
| 2017 | 16.72% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 241254.18 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.056818; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.174388296080242e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2719 orders vs QuantConnect Total Orders 2719 |
| fills_match_harness_count | pass | downloaded fill events 2719 vs harness-recorded fills 2719 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 2719 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `f5f8ee1a02e54033bf6a50c200ea567df918afd1b33df735932c374c70f6f84d`
- fills_sha256: `3b1cd141cc6659b382d632378e2a6dc63eedcbbac509ead0ac7a70460c3bf9e0`
- trades_sha256: `43453ed634e8aea8527985674445414e83c883735ab62f71fca4dbc3b556daf8`
