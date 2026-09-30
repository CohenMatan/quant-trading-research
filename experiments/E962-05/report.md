# E962-05 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 15 slots at $100K, hold 20, seed 2. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `a9565cc6afddecec68e03af25210abeeafa9d20f` · **QC backtest:** `178483863af9ceb97c8d345fafba6bd2` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T08:53:51Z · **runtime:** 440s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.65% |
| Annualised volatility | 15.02% |
| Sharpe (rf = 0) | 0.57 |
| Sortino | 0.79 |
| Max drawdown | -23.33% |
| Longest drawdown (trading days) | 636 |
| Calmar | 0.33 |
| Worst year | -8.83% |
| Worst month | -6.16% |
| Closed trades | 1351 |
| Win rate | 55.88% |
| Average winner | 5.97% |
| Average loser | -5.95% |
| Expectancy per trade | 0.71% |
| Profit factor | 1.24 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 80.94% |
| Turnover (1-way, per year) | 9.73 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -5.69% | 0.92 | 0.88 |
| E901-07 | -6.27% | 0.88 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 17.54% |
| 2011 | -5.90% |
| 2012 | 7.70% |
| 2013 | 31.31% |
| 2014 | -2.93% |
| 2015 | -8.83% |
| 2016 | 4.47% |
| 2017 | 24.60% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96765.66 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.112949; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3717273618679165e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2717 orders vs QuantConnect Total Orders 2717 |
| fills_match_harness_count | pass | downloaded fill events 2717 vs harness-recorded fills 2717 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 2717 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `395076acd159fac065d84436db1eb6ba877b6e1ae104464adcad3b0eacac8ad3`
- fills_sha256: `115b7af8ddbd080f50d1ccde5c1fce4accf063be2d83a22b43acff0bfe26e1e9`
- trades_sha256: `d74207d70cc43333cc313e85b051231f40d0a7b520f32d7d630804b2c9c217eb`
