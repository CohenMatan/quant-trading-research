# E001-19 — S001 v1.3 (research)

H001 remedial re-test after infrastructure correction (D057/D059/D063): S001 v1.3 exactly as pre-registered; identical to E001-14 except ID and harness

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `938e267c5f8b5cdd6fff1016f04a7d4eb09fc00e` · **QC backtest:** `f08ac932543e1323eaa73f6e39b41999` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T16:01:06Z · **runtime:** 518s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': True}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -3.74% |
| Annualised volatility | 5.45% |
| Sharpe (rf = 0) | -0.67 |
| Sortino | -0.90 |
| Max drawdown | -29.01% |
| Longest drawdown (trading days) | 1945 |
| Calmar | -0.13 |
| Worst year | -12.16% |
| Worst month | -8.16% |
| Closed trades | 1679 |
| Win rate | 52.59% |
| Average winner | 1.42% |
| Average loser | -2.29% |
| Expectancy per trade | -0.34% |
| Profit factor | 0.69 |
| Average holding (calendar days) | 4.8 |
| Average exposure | 17.58% |
| Turnover (1-way, per year) | 13.91 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -17.08% | 0.14 | 0.37 |
| E901-07 | -17.67% | 0.14 | 0.39 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -12.16% |
| 2011 | -5.93% |
| 2012 | -4.59% |
| 2013 | 0.80% |
| 2014 | 3.13% |
| 2015 | -2.12% |
| 2016 | -1.97% |
| 2017 | -6.21% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 72483.01 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.056901; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 1 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.428316362507815e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 3370 orders vs QuantConnect Total Orders 3370 |
| fills_match_harness_count | pass | downloaded fill events 3359 vs harness-recorded fills 3359 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 3359 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `2dd3c923d3b74e4a327cbaa1a9be82d8cea6906ceaf66e9f48a333d9e5226f86`
- fills_sha256: `a53c5597b81c5ff794461ac0f5e20f3838598adb7173d41258e3aabd68a24bf7`
- trades_sha256: `6d631166baaa7f4d3674446ea791dbe6911961502bf7142854f8bbf7024d469b`
