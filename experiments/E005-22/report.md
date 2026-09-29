# E005-22 — S005 v1.2 (research)

C01 robustness of E005-12: plateau slots 8 (base 15) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `3c3a760777f41d3533ccb8e76b73a4b442f1c656` · **QC backtest:** `87893d15b9d87928dabacb0867fa3685` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T11:01:32Z · **runtime:** 371s
- **Parameters:** `{'vol_days': 63, 'slots': 8, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 7.36% |
| Annualised volatility | 5.16% |
| Sharpe (rf = 0) | 1.40 |
| Sortino | 2.09 |
| Max drawdown | -5.03% |
| Longest drawdown (trading days) | 161 |
| Calmar | 1.46 |
| Worst year | 3.54% |
| Worst month | -3.55% |
| Closed trades | 328 |
| Win rate | 63.11% |
| Average winner | 4.04% |
| Average loser | -3.25% |
| Expectancy per trade | 1.35% |
| Profit factor | 2.30 |
| Average holding (calendar days) | 63.1 |
| Average exposure | 63.38% |
| Turnover (1-way, per year) | 3.47 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.98% | 0.26 | 0.73 |
| E901-05 | -6.38% | 0.23 | 0.70 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.60% |
| 2011 | 9.23% |
| 2012 | 3.94% |
| 2013 | 14.72% |
| 2014 | 6.12% |
| 2015 | 9.37% |
| 2016 | 3.54% |
| 2017 | 3.75% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 98205.42 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.197078; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 68 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 746 orders vs QuantConnect Total Orders 746 |
| fills_match_harness_count | pass | downloaded fill events 746 vs harness-recorded fills 746 |
| commission_fixed_per_order | pass | 746 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `57c5d8b8958005a76c3913f4c849be622752fb7dc6d435db9611160f4c4f36b5`
- fills_sha256: `5f02bc2e5231eaf4e346f0d3278c63a228dcf7eed50ffa6424707eb75819b109`
- trades_sha256: `c1db434d59a60eef0e77ed6cd59202a8da70f45ee8df62a48eeb14879e9d2553`
