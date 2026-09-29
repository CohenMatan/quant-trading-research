# E005-21 — S005 v1.2 (research)

C01 robustness of E005-12: plateau vol_days 95 (base 63) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `2e1dbd0d993657c9c304f7403ab3b30f41617cba` · **QC backtest:** `ed5b34455cfb9ea34a4fa92be2399c26` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T10:54:39Z · **runtime:** 403s
- **Parameters:** `{'vol_days': 95, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.99% |
| Annualised volatility | 6.49% |
| Sharpe (rf = 0) | 1.22 |
| Sortino | 1.79 |
| Max drawdown | -6.49% |
| Longest drawdown (trading days) | 149 |
| Calmar | 1.23 |
| Worst year | 3.01% |
| Worst month | -3.95% |
| Closed trades | 350 |
| Win rate | 61.43% |
| Average winner | 5.93% |
| Average loser | -4.55% |
| Expectancy per trade | 1.89% |
| Profit factor | 1.93 |
| Average holding (calendar days) | 90.9 |
| Average exposure | 71.25% |
| Turnover (1-way, per year) | 2.80 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.35% | 0.35 | 0.77 |
| E901-05 | -5.76% | 0.31 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 7.63% |
| 2011 | 9.48% |
| 2012 | 5.71% |
| 2013 | 19.09% |
| 2014 | 6.87% |
| 2015 | 6.88% |
| 2016 | 5.80% |
| 2017 | 3.01% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97159.43 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.049517; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 49 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.196725525139577e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 713 orders vs QuantConnect Total Orders 713 |
| fills_match_harness_count | pass | downloaded fill events 713 vs harness-recorded fills 713 |
| commission_fixed_per_order | pass | 713 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `03da56304370934aabecd59ab76be4f91b86cbf3bdb31a391f4304e45e782c9d`
- fills_sha256: `777e75dd7a418d9f4b7f5d1272b890ab7cb2be79898d455225d8a8ee08d2e22a`
- trades_sha256: `05fd6a9ed9b84a876b33011a0e69cc7a2b8c29ecd14d8e16f77f248092eb3a42`
