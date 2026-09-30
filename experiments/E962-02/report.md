# E962-02 — X962 v1.0 (infrastructure)

C03 portfolio-structure diagnostic (no-skill random pick), series S: portfolio size: 10 slots at $100K, hold 20, seed 2. Pre-registered in research/cycles/C03_portfolio_diagnostics_plan.md. Verification; not a trial.

- **Status:** completed
- **Split:** AUDIT (2010-01-04 → 2017-12-29)
- **Commit:** `cdcdabac66bed80be0579c2d5dfd67f16286577f` · **QC backtest:** `0bb89aa5c10de8d1bb0bb570d73715c7` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T08:36:27Z · **runtime:** 287s
- **Parameters:** `{'slots': 10, 'hold': 20, 'seed': 2}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 10, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.60% |
| Annualised volatility | 15.42% |
| Sharpe (rf = 0) | 0.61 |
| Sortino | 0.86 |
| Max drawdown | -22.03% |
| Longest drawdown (trading days) | 757 |
| Calmar | 0.39 |
| Worst year | -5.45% |
| Worst month | -7.23% |
| Closed trades | 900 |
| Win rate | 57.00% |
| Average winner | 5.85% |
| Average loser | -5.85% |
| Expectancy per trade | 0.82% |
| Profit factor | 1.32 |
| Average holding (calendar days) | 30.3 |
| Average exposure | 80.57% |
| Turnover (1-way, per year) | 9.67 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.75% | 0.92 | 0.85 |
| E901-07 | -5.33% | 0.88 | 0.88 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 13.22% |
| 2011 | -5.45% |
| 2012 | 8.05% |
| 2013 | 33.17% |
| 2014 | -4.23% |
| 2015 | -4.75% |
| 2016 | 7.80% |
| 2017 | 27.52% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96659.03 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.120340; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3717273618679165e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1810 orders vs QuantConnect Total Orders 1810 |
| fills_match_harness_count | pass | downloaded fill events 1810 vs harness-recorded fills 1810 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1810 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c49cdc2cfc1bbea9f870ab0da662e7c8cb711d8fa77582898faf208f3b8017f7`
- fills_sha256: `27d4058a755bd3de823d1b26b68b1af03f82bf03a3c59bc57adc319b59f95d99`
- trades_sha256: `837563dc9b7f5881619ca1fd969961d8425ce8c38711b682b17f08165d925ca7`
