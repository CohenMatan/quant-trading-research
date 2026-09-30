# E962-20 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series H: holding period: 15 slots at $100K, hold 5, seed 2. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `c0bd10e6209d28bec77c165d016870a45d97d688` · **QC backtest:** `5fb7a70311ea7a87718c951ac78751f0` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:34:04Z · **runtime:** 277s
- **Parameters:** `{'slots': 15, 'hold': 5, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -0.83% |
| Annualised volatility | 7.53% |
| Sharpe (rf = 0) | -0.07 |
| Sortino | -0.10 |
| Max drawdown | -26.16% |
| Longest drawdown (trading days) | 1939 |
| Calmar | -0.03 |
| Worst year | -16.68% |
| Worst month | -11.31% |
| Closed trades | 1585 |
| Win rate | 48.14% |
| Average winner | 3.24% |
| Average loser | -3.20% |
| Expectancy per trade | -0.10% |
| Profit factor | 0.93 |
| Average holding (calendar days) | 8.6 |
| Average exposure | 28.00% |
| Turnover (1-way, per year) | 12.90 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -14.18% | 0.21 | 0.40 |
| E901-07 | -14.76% | 0.21 | 0.43 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -16.68% |
| 2011 | -2.28% |
| 2012 | 0.00% |
| 2013 | 0.00% |
| 2014 | 5.81% |
| 2015 | -1.07% |
| 2016 | 17.34% |
| 2017 | -6.49% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 80336.42 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.059180; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.160079701089563e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 3187 orders vs QuantConnect Total Orders 3187 |
| fills_match_harness_count | pass | downloaded fill events 3185 vs harness-recorded fills 3185 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 3185 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `01f457cf8cd995590597555219a31785c1602c7c1a0ab88e4884b7f4d2c876b8`
- fills_sha256: `16fd87419701eb9c8c6a5dda8349711ce855346115cdaa2d5862fce6a6296c4c`
- trades_sha256: `c09098d43a4db728878a5d4ca5df642a0b4d4c6adfcdce00fb591251819d8ba7`
