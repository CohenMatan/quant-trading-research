# E005-08 — S005 v1.1 (research)

C01 H005 S005 v1.1 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E005-02 under D051 (no borrowing); retry of E005-05 (operational failure, D053)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `fda30491048c652245b31bd435cb0f2780fe1f9e` · **QC backtest:** `1104360712cc9f8d1fb62e4f83761322` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T06:47:29Z · **runtime:** 356s
- **Parameters:** `{'vol_days': 252, 'slots': 15, 'band': 0.25, 'require_positive_mom': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 10.52% |
| Annualised volatility | 8.31% |
| Sharpe (rf = 0) | 1.25 |
| Sortino | 1.83 |
| Max drawdown | -9.39% |
| Longest drawdown (trading days) | 154 |
| Calmar | 1.12 |
| Worst year | 2.44% |
| Worst month | -5.40% |
| Closed trades | 163 |
| Win rate | 63.80% |
| Average winner | 12.09% |
| Average loser | -6.23% |
| Expectancy per trade | 5.46% |
| Profit factor | 2.96 |
| Average holding (calendar days) | 222.7 |
| Average exposure | 82.82% |
| Turnover (1-way, per year) | 1.37 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-05 | -2.82% | 0.45 | 0.77 |
| E901-04 | -3.23% | 0.40 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 12.57% |
| 2011 | 12.61% |
| 2012 | 4.61% |
| 2013 | 18.77% |
| 2014 | 14.07% |
| 2015 | 2.44% |
| 2016 | 8.97% |
| 2017 | 10.79% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98066.82 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.044871; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 5 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.6796259073508613e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 343 orders vs QuantConnect Total Orders 343 |
| fills_match_harness_count | pass | downloaded fill events 342 vs harness-recorded fills 342 |
| commission_fixed_per_order | pass | 342 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `6cb33fb0ac062beb78eaa469703c618e4ba90b151f90b470ba1dbf29d813ff18`
- fills_sha256: `a493f01b6b8fe684d3956abfd9f10cd4c49255fd7405420e76e684ba61fe88f1`
- trades_sha256: `f3cf2bcd06e3a193b7dba7689ce91f5fbcf29beea2dbadf76bb52e1d77bb0e72`
