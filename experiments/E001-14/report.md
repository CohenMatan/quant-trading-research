# E001-14 — S001 v1.3 (research)

C01 H001 S001 v1.3 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E001-04 under D051 with the D054 harness fix (replaces E001-09)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `b8b5630d1a8efa5d392aa7ecdcfb2a67619043f2` · **QC backtest:** `4030c64fc003e74a9cdb86d89c962d6d` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T08:07:37Z · **runtime:** 405s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -4.70% |
| Annualised volatility | 9.70% |
| Sharpe (rf = 0) | -0.45 |
| Sortino | -0.60 |
| Max drawdown | -36.71% |
| Longest drawdown (trading days) | 1945 |
| Calmar | -0.13 |
| Worst year | -15.49% |
| Worst month | -8.60% |
| Closed trades | 2248 |
| Win rate | 52.49% |
| Average winner | 1.46% |
| Average loser | -2.21% |
| Expectancy per trade | -0.28% |
| Profit factor | 0.73 |
| Average holding (calendar days) | 4.8 |
| Average exposure | 51.29% |
| Turnover (1-way, per year) | 19.22 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -18.04% | 0.49 | 0.73 |
| E901-05 | -18.45% | 0.48 | 0.76 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -10.79% |
| 2011 | -12.25% |
| 2012 | 0.06% |
| 2013 | 6.33% |
| 2014 | 5.63% |
| 2015 | -15.49% |
| 2016 | -7.72% |
| 2017 | -0.79% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 64374.71 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.043615; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.757220605304979e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 4509 orders vs QuantConnect Total Orders 4509 |
| fills_match_harness_count | pass | downloaded fill events 4507 vs harness-recorded fills 4507 |
| commission_fixed_per_order | pass | 4507 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `7309bcccdfa307b48edc9b5feb1500af6d5111ce429b076e25c091c50be43fb3`
- fills_sha256: `e1aced2fdfd3f26fba12175e7c69357014048eeef3ef1087f3a8cd9cf45b41e7`
- trades_sha256: `4295f79b12a4e445738f4c7e7f6c60d4fb7394ea1bf7068616f5a746a20f1d84`
