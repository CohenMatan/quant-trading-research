# E005-27 — S005 v1.2 (research)

C01 robustness of E005-12: plateau band 0.375 (base 0.25) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `a7fc87381ddda4662c4436b5d0d3220b96788692` · **QC backtest:** `6c9809f9b6b03621f390bc93a2dae483` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T11:37:31Z · **runtime:** 374s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.375, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.52% |
| Annualised volatility | 5.80% |
| Sharpe (rf = 0) | 1.44 |
| Sortino | 2.17 |
| Max drawdown | -5.28% |
| Longest drawdown (trading days) | 165 |
| Calmar | 1.61 |
| Worst year | 2.23% |
| Worst month | -3.52% |
| Closed trades | 408 |
| Win rate | 62.99% |
| Average winner | 5.22% |
| Average loser | -3.52% |
| Expectancy per trade | 1.98% |
| Profit factor | 2.33 |
| Average holding (calendar days) | 74.9 |
| Average exposure | 67.67% |
| Turnover (1-way, per year) | 3.22 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -4.82% | 0.31 | 0.77 |
| E901-05 | -5.22% | 0.28 | 0.74 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 11.65% |
| 2011 | 12.38% |
| 2012 | 5.15% |
| 2013 | 16.47% |
| 2014 | 5.34% |
| 2015 | 10.08% |
| 2016 | 2.23% |
| 2017 | 5.47% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98059.30 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.075545; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 71 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3862034721872065e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 827 orders vs QuantConnect Total Orders 827 |
| fills_match_harness_count | pass | downloaded fill events 827 vs harness-recorded fills 827 |
| commission_fixed_per_order | pass | 827 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `ade7e1934348b7c520eb1b31502ca4c13f4d6e9782b4043990c603ed5cb61e83`
- fills_sha256: `1faf4b8f368dccb8047a73ec5c85bc44a83d71f93401d0c4272abb12786e9f9c`
- trades_sha256: `4764e64cafc5eab4dd5f2bcc7f4de5c3ba223fa34a45dfb9afca58e90b8c1b2e`
