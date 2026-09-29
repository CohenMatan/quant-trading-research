# E005-25 — S005 v1.2 (research)

C01 robustness of E005-12: plateau band 0.2 (base 0.25) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `2b0bd8470d31506429e58a0fc51868698f65cf99` · **QC backtest:** `f7de9bf94db4cd2a3e8e961d6893572c` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T11:22:26Z · **runtime:** 445s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.2, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.51% |
| Annualised volatility | 5.81% |
| Sharpe (rf = 0) | 1.44 |
| Sortino | 2.17 |
| Max drawdown | -5.29% |
| Longest drawdown (trading days) | 165 |
| Calmar | 1.61 |
| Worst year | 2.19% |
| Worst month | -3.52% |
| Closed trades | 408 |
| Win rate | 62.99% |
| Average winner | 5.22% |
| Average loser | -3.51% |
| Expectancy per trade | 1.99% |
| Profit factor | 2.33 |
| Average holding (calendar days) | 74.9 |
| Average exposure | 67.68% |
| Turnover (1-way, per year) | 3.22 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -4.83% | 0.31 | 0.77 |
| E901-05 | -5.23% | 0.28 | 0.74 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 11.54% |
| 2011 | 12.43% |
| 2012 | 5.15% |
| 2013 | 16.48% |
| 2014 | 5.33% |
| 2015 | 10.07% |
| 2016 | 2.19% |
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
| no_leverage | pass | min cash/equity 0.075202; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 71 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.3862034721872065e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 829 orders vs QuantConnect Total Orders 829 |
| fills_match_harness_count | pass | downloaded fill events 829 vs harness-recorded fills 829 |
| commission_fixed_per_order | pass | 829 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `79d21f79f6f0572c9925a8e05a4f9ea042654b147f557f05e634cfe1e3f7b50d`
- fills_sha256: `07a72a5a4b1a1d8cd60df89013a1aff831b3741b978948adf09c32718d3b4ba1`
- trades_sha256: `a54ccf51f9968ab7f41ea2bf44fbf67f92aa8227bb54493104c2de2230678545`
