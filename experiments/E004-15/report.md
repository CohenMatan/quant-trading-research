# E004-15 — S004 v1.2 (research)

C01 H004 S004 v1.2 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E004-03 under D051 with the D054 harness fix (replaces E004-11)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `533181d8536888f1cec493d7d71608127b8b846e` · **QC backtest:** `deec6b492681f212d6fac63bd720593c` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T09:21:39Z · **runtime:** 369s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.05, 'hold_days': 20, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 8.22% |
| Annualised volatility | 22.80% |
| Sharpe (rf = 0) | 0.46 |
| Sortino | 0.65 |
| Max drawdown | -44.09% |
| Longest drawdown (trading days) | 926 |
| Calmar | 0.19 |
| Worst year | -15.46% |
| Worst month | -13.50% |
| Closed trades | 1395 |
| Win rate | 52.33% |
| Average winner | 9.42% |
| Average loser | -8.77% |
| Expectancy per trade | 0.75% |
| Profit factor | 1.14 |
| Average holding (calendar days) | 29.0 |
| Average exposure | 88.00% |
| Turnover (1-way, per year) | 11.16 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -5.12% | 1.21 | 0.76 |
| E901-05 | -5.53% | 1.21 | 0.82 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 15.66% |
| 2011 | -9.62% |
| 2012 | 20.75% |
| 2013 | 30.96% |
| 2014 | -15.46% |
| 2015 | -8.71% |
| 2016 | 17.74% |
| 2017 | 25.05% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 88100.14 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.025175; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 2 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 2805 orders vs QuantConnect Total Orders 2805 |
| fills_match_harness_count | pass | downloaded fill events 2805 vs harness-recorded fills 2805 |
| commission_fixed_per_order | pass | 2805 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `8c820c0b1b1983d297373f1ee20f89a9edba974a2a5a7868e81c763161206f86`
- fills_sha256: `056f491e4157ced7c3c581b2a305a1dbb1064f90f87e92a0164eca6abf1939aa`
- trades_sha256: `157260845752281a30b5d74c8bea9f08551d90945041e27b4b28648714292a26`
