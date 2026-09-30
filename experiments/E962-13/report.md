# E962-13 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series A: account size: 15 slots at $1000K, hold 20, seed 1. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `7a38996594d7707231dba85c3b1bb5be7fcf1065` · **QC backtest:** `7dad2673ff6c944a1ecf3c0e83efa23e` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T09:48:58Z · **runtime:** 481s
- **Parameters:** `{'slots': 15, 'hold': 20, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 11.08% |
| Annualised volatility | 14.58% |
| Sharpe (rf = 0) | 0.79 |
| Sortino | 1.13 |
| Max drawdown | -18.21% |
| Longest drawdown (trading days) | 243 |
| Calmar | 0.61 |
| Worst year | -3.49% |
| Worst month | -7.80% |
| Closed trades | 1352 |
| Win rate | 55.40% |
| Average winner | 6.14% |
| Average loser | -5.42% |
| Expectancy per trade | 0.98% |
| Profit factor | 1.36 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 83.94% |
| Turnover (1-way, per year) | 10.15 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.27% | 0.90 | 0.88 |
| E901-07 | -2.85% | 0.86 | 0.91 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 16.39% |
| 2011 | 2.29% |
| 2012 | 19.15% |
| 2013 | 19.92% |
| 2014 | 5.97% |
| 2015 | -3.49% |
| 2016 | 9.64% |
| 2017 | 21.26% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 974739.92 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.043706; 0 closes with negative cash |
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

- equity_sha256: `c0f56552b019e86b96ba6757c1cfe61fcf38a9a3852a1c7f9eac814ca2287353`
- fills_sha256: `cd6b9ec844ede6961b6c4832b04618facd07c551f7e78e204a90dde1eaabe08f`
- trades_sha256: `0de9baf7574bccd6226fb7c203bf709de34144aa37a1c0e9710702e523d3e04c`
