# E962-17 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series B: breadth beyond the $100K limit: 30 slots at $250K, hold 20, seed 2. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `dd54e66ea2f3bbb0e563fad472ad22253df6e0e1` · **QC backtest:** `65c498fd25a421da52020006ff81ab26` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T10:17:45Z · **runtime:** 295s
- **Parameters:** `{'slots': 30, 'hold': 20, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 30, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.62% |
| Annualised volatility | 14.49% |
| Sharpe (rf = 0) | 0.58 |
| Sortino | 0.81 |
| Max drawdown | -22.39% |
| Longest drawdown (trading days) | 578 |
| Calmar | 0.34 |
| Worst year | -10.29% |
| Worst month | -7.22% |
| Closed trades | 2704 |
| Win rate | 55.51% |
| Average winner | 6.06% |
| Average loser | -6.12% |
| Expectancy per trade | 0.64% |
| Profit factor | 1.20 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 82.88% |
| Turnover (1-way, per year) | 9.98 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -5.72% | 0.93 | 0.91 |
| E901-07 | -6.30% | 0.89 | 0.95 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.46% |
| 2011 | -0.67% |
| 2012 | 8.23% |
| 2013 | 28.88% |
| 2014 | 1.41% |
| 2015 | -10.29% |
| 2016 | 5.51% |
| 2017 | 17.08% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 238076.76 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.082767; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 10 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3862034721872065e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 5438 orders vs QuantConnect Total Orders 5438 |
| fills_match_harness_count | pass | downloaded fill events 5438 vs harness-recorded fills 5438 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 5438 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `675256d7454c13e6425c0ef0b971cd4dc6ebd966fa90bdf24e324c78bec778e3`
- fills_sha256: `ffc8a74f5e5a2a6f93ef24cd993092615efdff433cf612d7fb6adf4329d82f42`
- trades_sha256: `117aa34c343835763466712266dced03ce5289fabc45d24f1c2397603da22695`
