# E007-11 — S007 v1.1 (research)

C02 robustness of E007-02 (H007 v1.1): plateau: time stop 40 -> 20 (pre-declared in research/cycles/C02_robustness_plan.md)

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `d372dd29662496de2593dd9f67e16994109f863d` · **QC backtest:** `574966e82974f382ecc5eb8a93ca632f` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-30T05:36:54Z · **runtime:** 1173s
- **Parameters:** `{'setup': 'atr', 'pct': 0.1, 'atr_ratio': 0.6, 'use_trend': True, 'time_stop': 20, 'slots': 10}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | 4.58% |
| Annualised volatility | 4.18% |
| Sharpe (rf = 0) | 1.09 |
| Sortino | 1.79 |
| Max drawdown | -5.21% |
| Longest drawdown (trading days) | 272 |
| Calmar | 0.88 |
| Worst year | 0.68% |
| Worst month | -3.02% |
| Closed trades | 236 |
| Win rate | 45.76% |
| Average winner | 6.23% |
| Average loser | -2.46% |
| Expectancy per trade | 1.51% |
| Profit factor | 2.06 |
| Average holding (calendar days) | 21.9 |
| Average exposure | 17.46% |
| Turnover (1-way, per year) | 2.91 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -8.76% | 0.07 | 0.26 |
| E901-07 | -9.34% | 0.08 | 0.28 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 7.48% |
| 2011 | 0.68% |
| 2012 | 8.24% |
| 2013 | 3.83% |
| 2014 | 8.59% |
| 2015 | 2.29% |
| 2016 | 0.84% |
| 2017 | 4.98% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 99884.84 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.030848; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 26 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.116719661283175e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 472 orders vs QuantConnect Total Orders 472 |
| fills_match_harness_count | pass | downloaded fill events 472 vs harness-recorded fills 472 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 472 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `7c109a2e4be732c68baad8f3b0170aa7cc62fdc21a6fed0d58f2b29e787d679c`
- fills_sha256: `ba43f6f8b5c44ffbaab8e9d8f602b3edaedbc24979b3061be9af3f64689f8952`
- trades_sha256: `daab046c2c44cf4d58451e65c4ce0d3b59a5d2ced2a9512616d08419fb9c76a8`
