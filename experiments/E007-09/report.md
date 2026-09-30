# E007-09 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): plateau: ATR10/ATR100 ratio 0.6 -> 0.72 (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `890f4da89ab6f1b936579dbe6ab4dd7a7e92f9a5` · **QC backtest:** `e2e9de3f1db620e589e47a1359e3ad04` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T04:57:16Z · **runtime:** 1115s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.72, 'use_trend': True, 'time_stop': 40, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 5.39% |
| Annualised volatility | 8.13% |
| Sharpe (rf = 0) | 0.69 |
| Sortino | 0.99 |
| Max drawdown | -19.15% |
| Longest drawdown (trading days) | 739 |
| Calmar | 0.28 |
| Worst year | -6.47% |
| Worst month | -4.88% |
| Closed trades | 565 |
| Win rate | 42.65% |
| Average winner | 6.26% |
| Average loser | -3.39% |
| Expectancy per trade | 0.73% |
| Profit factor | 1.34 |
| Average holding (calendar days) | 26.2 |
| Average exposure | 49.43% |
| Turnover (1-way, per year) | 6.87 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -7.95% | 0.25 | 0.44 |
| E901-07 | -8.54% | 0.24 | 0.46 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 2.46% |
| 2011 | -4.53% |
| 2012 | 4.01% |
| 2013 | 33.58% |
| 2014 | -4.93% |
| 2015 | -6.47% |
| 2016 | 4.49% |
| 2017 | 20.43% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96042.67 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.030272; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 29 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 1133 orders vs QuantConnect Total Orders 1133 |
| fills_match_harness_count | pass | downloaded fill events 1133 vs harness-recorded fills 1133 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 1133 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `3924f7101a67050324777dbc250f9b2308b42e80320228dcde7f8dd46f0bea05`
- fills_sha256: `572f99d28dfc9e1d281bb0eef2c1d50df99c13b8f72f393f8f98401ef5a3a51f`
- trades_sha256: `aedffa467bd20f6dda24c1f5ffa39da027729f06746421cc4647dfd50b3969eb`
