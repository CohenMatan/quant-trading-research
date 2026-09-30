# E962-21 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series H: holding period: 15 slots at $100K, hold 5, seed 3. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `a477e87490c0c24236323b13674383559e9be897` · **QC backtest:** `dac2f067b78f2bfda8e01c1071a9b61e` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:39:04Z · **runtime:** 321s
- **Parameters:** `{'slots': 15, 'hold': 5, 'seed': 3}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -2.58% |
| Annualised volatility | 8.92% |
| Sharpe (rf = 0) | -0.25 |
| Sortino | -0.33 |
| Max drawdown | -27.97% |
| Longest drawdown (trading days) | 1949 |
| Calmar | -0.09 |
| Worst year | -11.21% |
| Worst month | -12.58% |
| Closed trades | 1529 |
| Win rate | 48.46% |
| Average winner | 3.24% |
| Average loser | -3.50% |
| Expectancy per trade | -0.23% |
| Profit factor | 0.86 |
| Average holding (calendar days) | 8.7 |
| Average exposure | 27.88% |
| Turnover (1-way, per year) | 12.42 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -15.92% | 0.36 | 0.58 |
| E901-07 | -16.51% | 0.34 | 0.59 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -8.44% |
| 2011 | -11.21% |
| 2012 | -1.62% |
| 2013 | 7.62% |
| 2014 | 2.99% |
| 2015 | -10.56% |
| 2016 | 1.04% |
| 2017 | 1.29% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 76793.67 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.029514; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.4962832304260223e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 3059 orders vs QuantConnect Total Orders 3059 |
| fills_match_harness_count | pass | downloaded fill events 3058 vs harness-recorded fills 3058 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 3058 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `0dd3688e094b745565542ee505cdf91b146e7c2a2a228789399fab4cf8ced1f6`
- fills_sha256: `431099a2ddcdd214e9336c2479b8ceb7499c6fcb7b8fd926ad27ee9ba3b55c78`
- trades_sha256: `94a1790ad1877c64b8bbe7783e1e0de61779e9cb85718022e02f32897aa96308`
