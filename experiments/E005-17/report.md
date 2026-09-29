# E005-17 — S005 v1.2 (research)

C01 robustness of E005-12: slippage 6x (60 bps/side) (pre-declared in research/cycles/C01_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `478932226e81debf73bfad0c8a91a972d63f86a8` · **QC backtest:** `c6930aaed43e90a07aceb847e89fd5f0` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T10:27:27Z · **runtime:** 372s
- **Parameters:** `{'vol_days': 63, 'slots': 15, 'band': 0.25, 'require_positive_mom': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate', 'slippage_stress_multiple': 6}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.34% |
| Annualised volatility | 5.92% |
| Sharpe (rf = 0) | 0.91 |
| Sortino | 1.33 |
| Max drawdown | -5.87% |
| Longest drawdown (trading days) | 327 |
| Calmar | 0.91 |
| Worst year | -0.67% |
| Worst month | -3.78% |
| Closed trades | 408 |
| Win rate | 54.17% |
| Average winner | 5.03% |
| Average loser | -3.67% |
| Expectancy per trade | 1.04% |
| Profit factor | 1.53 |
| Average holding (calendar days) | 74.9 |
| Average exposure | 67.73% |
| Turnover (1-way, per year) | 3.21 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -8.00% | 0.31 | 0.75 |
| E901-05 | -8.40% | 0.28 | 0.73 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 8.85% |
| 2011 | 9.46% |
| 2012 | 1.80% |
| 2013 | 12.95% |
| 2014 | 1.84% |
| 2015 | 6.37% |
| 2016 | -0.67% |
| 2017 | 2.79% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 97565.02 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.075532; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 71 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.2089979175426485e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 828 orders vs QuantConnect Total Orders 828 |
| fills_match_harness_count | pass | downloaded fill events 828 vs harness-recorded fills 828 |
| commission_fixed_per_order | pass | 828 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2702f921b0efd782079ae687209173fabebbbbb63bffc917807b1783e7fd383e`
- fills_sha256: `70b68857c27331bc2f17bb5f9dfce613a19206ad9dc4f36b2f77824009c215b9`
- trades_sha256: `96c91fe1516d3a66aa912b8bea2e96a372e2e46e0ecfd550f8f43334083df8b6`
