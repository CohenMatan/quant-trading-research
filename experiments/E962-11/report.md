# E962-11 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series A: account size: 15 slots at $250K, hold 20, seed 2. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `1ee96fa1450d8bb83856522328a2d057e1b6c70e` · **QC backtest:** `9bda3214791f530bce61c357bf99016b` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:32:46Z · **runtime:** 654s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.91% |
| Annualised volatility | 15.04% |
| Sharpe (rf = 0) | 0.64 |
| Sortino | 0.90 |
| Max drawdown | -23.13% |
| Longest drawdown (trading days) | 478 |
| Calmar | 0.39 |
| Worst year | -7.95% |
| Worst month | -6.08% |
| Closed trades | 1351 |
| Win rate | 56.62% |
| Average winner | 6.01% |
| Average loser | -5.93% |
| Expectancy per trade | 0.83% |
| Profit factor | 1.29 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 81.16% |
| Turnover (1-way, per year) | 9.76 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.43% | 0.92 | 0.88 |
| E901-07 | -5.02% | 0.89 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 19.06% |
| 2011 | -4.72% |
| 2012 | 9.07% |
| 2013 | 32.84% |
| 2014 | -1.77% |
| 2015 | -7.95% |
| 2016 | 5.66% |
| 2017 | 25.84% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 242702.52 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.111145; 0 closes with negative cash |
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

- equity_sha256: `6c931546be7fd47a9f7b27a7564812ec3dd4985b3fb090cc1aeb6c559c482580`
- fills_sha256: `a72dc2e141bd57251cb512964037d357f10a0942e2090611bca25999ed9416d3`
- trades_sha256: `38728600217cd2db8de993a4316e00878af47cba89dff4627f938a03dee86ad2`
