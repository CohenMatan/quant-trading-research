# E004-10 — S004 v1.1 (research)

C01 H004 S004 v1.1 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E004-02 under D051 (no borrowing); retry of E004-06 (operational failure, D053)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `c579e8b5fff7cda426a1f11b2bdc00c0d88499d6` · **QC backtest:** `d3a88fa8621ca17ed98a15598e6fa79e` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T06:19:10Z · **runtime:** 503s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.08, 'hold_days': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -1.39% |
| Annualised volatility | 20.22% |
| Sharpe (rf = 0) | 0.03 |
| Sortino | 0.05 |
| Max drawdown | -53.30% |
| Longest drawdown (trading days) | 1112 |
| Calmar | -0.03 |
| Worst year | -25.86% |
| Worst month | -16.09% |
| Closed trades | 1988 |
| Win rate | 48.94% |
| Average winner | 6.59% |
| Average loser | -6.45% |
| Expectancy per trade | -0.07% |
| Profit factor | 0.95 |
| Average holding (calendar days) | 14.4 |
| Average exposure | 63.48% |
| Turnover (1-way, per year) | 16.04 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-05 | -14.73% | 0.98 | 0.69 |
| E901-04 | -15.13% | 0.99 | 0.75 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 18.51% |
| 2011 | -16.71% |
| 2012 | 22.06% |
| 2013 | 15.63% |
| 2014 | -25.86% |
| 2015 | -20.88% |
| 2016 | 2.20% |
| 2017 | 7.09% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 69807.08 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.027846; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3084730965147665e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 3989 orders vs QuantConnect Total Orders 3989 |
| fills_match_harness_count | pass | downloaded fill events 3989 vs harness-recorded fills 3989 |
| commission_fixed_per_order | pass | 3989 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ed79468daa5ad43f029230cda45a13cba392a17a60ab3c2281248d2755aa8e25`
- fills_sha256: `6dc70e8c67a4bfbaf7e0b361aab091f93dcc2a2a1e8b76853cc6aa84ecee3d1e`
- trades_sha256: `3f7e89a9ac3566d9efa4909ca3cd9c84c2e8c50219671c7e4260a134a10d9ad2`
