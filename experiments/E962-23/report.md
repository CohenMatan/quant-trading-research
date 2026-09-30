# E962-23 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series H: holding period: 15 slots at $100K, hold 60, seed 2. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `d8f81bf07424c62ba585142bf170b53a345d8bb5` · **QC backtest:** `d1006b72a118138dec95e169f214b65a` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:49:51Z · **runtime:** 264s
- **Parameters:** `{'slots': 15, 'hold': 60, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.80% |
| Annualised volatility | 14.98% |
| Sharpe (rf = 0) | 0.82 |
| Sortino | 1.15 |
| Max drawdown | -25.76% |
| Longest drawdown (trading days) | 373 |
| Calmar | 0.46 |
| Worst year | -9.80% |
| Worst month | -10.94% |
| Closed trades | 481 |
| Win rate | 61.54% |
| Average winner | 11.15% |
| Average loser | -10.63% |
| Expectancy per trade | 2.77% |
| Profit factor | 1.62 |
| Average holding (calendar days) | 87.9 |
| Average exposure | 84.08% |
| Turnover (1-way, per year) | 3.56 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -1.54% | 0.93 | 0.89 |
| E901-07 | -2.12% | 0.89 | 0.92 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 22.74% |
| 2011 | -9.80% |
| 2012 | 17.21% |
| 2013 | 26.28% |
| 2014 | 10.06% |
| 2015 | 2.58% |
| 2016 | 24.45% |
| 2017 | 5.86% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97028.07 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.097298; 0 closes with negative cash |
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

- equity_sha256: `d44ed5f13dbb0fb1cb8667628487ccbc40deb1373afa02356eedc9acdb590ad8`
- fills_sha256: `c711bad1bb766520b9581da25c7b37b6e610abac2996e5ea0ae569fddc1c62c3`
- trades_sha256: `2f5763a4fa6cad592a95bd4e52e796b3a7f70ad478ffc9972382d4d033694f6b`
