# E004-09 — S004 v1.0 (research)

C01 H004 S004 v1.0 (pre-declared variation) on IS 2010-2017 | CORRECTED re-run of E004-01 under D051 (no borrowing); retry of E004-05 (operational failure, D053)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `7432456794196ade92e157aa82403a038e369f9a` · **QC backtest:** `ee2e9b19388b434d69f875fcab42ed27` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T06:11:10Z · **runtime:** 461s
- **Parameters:** `{'leader_frac': 0.2, 'drop': 0.05, 'hold_days': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 4.45% |
| Annualised volatility | 21.63% |
| Sharpe (rf = 0) | 0.31 |
| Sortino | 0.43 |
| Max drawdown | -52.43% |
| Longest drawdown (trading days) | 965 |
| Calmar | 0.08 |
| Worst year | -21.86% |
| Worst month | -15.22% |
| Closed trades | 2580 |
| Win rate | 49.84% |
| Average winner | 6.55% |
| Average loser | -6.05% |
| Expectancy per trade | 0.23% |
| Profit factor | 1.04 |
| Average holding (calendar days) | 14.5 |
| Average exposure | 81.09% |
| Turnover (1-way, per year) | 20.56 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-05 | -8.89% | 1.11 | 0.74 |
| E901-04 | -9.29% | 1.11 | 0.79 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 27.83% |
| 2011 | -8.80% |
| 2012 | 21.77% |
| 2013 | 28.96% |
| 2014 | -21.86% |
| 2015 | -20.11% |
| 2016 | 1.74% |
| 2017 | 21.76% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 92246.77 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.028905; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 5181 orders vs QuantConnect Total Orders 5181 |
| fills_match_harness_count | pass | downloaded fill events 5174 vs harness-recorded fills 5174 |
| commission_fixed_per_order | pass | 5174 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `b2629bf92a7ab1dcc26cd053e07332463aea8ff40e2d0e1b3f5299290084ee96`
- fills_sha256: `0e654b56a1a2f7f69482893804b52438b38da257af6f5b9827367524ff1bebac`
- trades_sha256: `5b5bc5b9678856e0d075a79eb4f3a99f35ed80f80a0a8f67790c4bbe78260443`
