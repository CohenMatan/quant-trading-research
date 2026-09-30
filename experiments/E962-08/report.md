# E962-08 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 19 slots at $100K, hold 20, seed 2. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `1f3d5b1ff156719e81e988e85443c5c79327d450` · **QC backtest:** `2086b69f2147523c549a39fbb6add55b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:14:23Z · **runtime:** 373s
- **Parameters:** `{'slots': 19, 'hold': 20, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 19, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 4.78% |
| Annualised volatility | 9.86% |
| Sharpe (rf = 0) | 0.52 |
| Sortino | 0.74 |
| Max drawdown | -20.71% |
| Longest drawdown (trading days) | 618 |
| Calmar | 0.23 |
| Worst year | -1.28% |
| Worst month | -7.83% |
| Closed trades | 978 |
| Win rate | 52.25% |
| Average winner | 6.25% |
| Average loser | -5.37% |
| Expectancy per trade | 0.70% |
| Profit factor | 1.23 |
| Average holding (calendar days) | 30.4 |
| Average exposure | 50.14% |
| Turnover (1-way, per year) | 6.53 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -8.56% | 0.36 | 0.53 |
| E901-07 | -9.15% | 0.35 | 0.55 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 5.36% |
| 2011 | -0.07% |
| 2012 | 0.00% |
| 2013 | 13.40% |
| 2014 | 9.16% |
| 2015 | -1.28% |
| 2016 | 3.10% |
| 2017 | 9.44% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98241.41 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.032640; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 3 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1976 orders vs QuantConnect Total Orders 1976 |
| fills_match_harness_count | pass | downloaded fill events 1975 vs harness-recorded fills 1975 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1975 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c03834c12dd4710c9ff4f7485d4a6b6064b4d96108d04d8192c0f3ad1c966fee`
- fills_sha256: `e1fb539dc9fc646d9b585a34bf431d34a82a900a16027701f8c9eca01a8178e2`
- trades_sha256: `0a3740daab52044b617ffc439d66dbb2aac8b64dcb7a997e08b8f5e3fd59153c`
