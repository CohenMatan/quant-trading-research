# E001-13 — S001 v1.2 (research)

C01 H001 S001 v1.2 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E001-03 under D051 with the D054 harness fix (replaces E001-08)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `ea5cde7139530ea51bb934122aad4b568ae8f630` · **QC backtest:** `1b64c1b91b1d5bd5d80727070a35dcc2` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T08:00:06Z · **runtime:** 434s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'time', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 4.29% |
| Annualised volatility | 14.83% |
| Sharpe (rf = 0) | 0.36 |
| Sortino | 0.49 |
| Max drawdown | -29.25% |
| Longest drawdown (trading days) | 622 |
| Calmar | 0.15 |
| Worst year | -10.86% |
| Worst month | -11.13% |
| Closed trades | 1640 |
| Win rate | 51.89% |
| Average winner | 3.87% |
| Average loser | -4.02% |
| Expectancy per trade | 0.07% |
| Profit factor | 1.02 |
| Average holding (calendar days) | 15.8 |
| Average exposure | 87.04% |
| Turnover (1-way, per year) | 12.44 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-06 | -9.06% | 0.87 | 0.84 |
| E901-05 | -9.46% | 0.85 | 0.88 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 14.22% |
| 2011 | -10.86% |
| 2012 | 7.27% |
| 2013 | 29.37% |
| 2014 | 9.18% |
| 2015 | -5.60% |
| 2016 | -7.47% |
| 2017 | 3.76% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 94830.62 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.029343; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 4 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 3296 orders vs QuantConnect Total Orders 3296 |
| fills_match_harness_count | pass | downloaded fill events 3295 vs harness-recorded fills 3295 |
| commission_fixed_per_order | pass | 3295 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `475a0249c14708b2950588bb6dd82ffec916280b43816b3cf5e6a423b63b1cea`
- fills_sha256: `5534ac1bb9d2585700c471367604c04b54a778a423476a728c265f27057ecbd6`
- trades_sha256: `35181805dab5eb700658d3d5f9fb780b5e1bd812fb252b522a8cc4e0b69d39c9`
