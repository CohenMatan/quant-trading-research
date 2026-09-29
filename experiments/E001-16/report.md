# E001-16 — S001 v1.0 (research)

H001 remedial re-test after infrastructure correction (D057/D059/D063): S001 v1.0 exactly as pre-registered; identical to E001-11 except ID and harness

- **Status:** completed
- **Split:** IS (2010-01-04 → 2017-12-29)
- **Commit:** `866a731706dbd5044ff7ab238fe138743b137915` · **QC backtest:** `2db172693cd48f3a55d4f43fe7d879c3` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-09-29T15:27:48Z · **runtime:** 509s
- **Parameters:** `{'entry': 'rsi', 'rsi_max': 10, 'exit': 'sma5', 'max_hold': 10, 'slots': 15, 'regime_filter': False}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2017-12-29 (2013 trading days) |
| CAGR | -7.70% |
| Annualised volatility | 9.29% |
| Sharpe (rf = 0) | -0.82 |
| Sortino | -1.08 |
| Max drawdown | -49.24% |
| Longest drawdown (trading days) | 1945 |
| Calmar | -0.16 |
| Worst year | -12.01% |
| Worst month | -7.38% |
| Closed trades | 3262 |
| Win rate | 54.08% |
| Average winner | 1.47% |
| Average loser | -2.40% |
| Expectancy per trade | -0.31% |
| Profit factor | 0.72 |
| Average holding (calendar days) | 4.8 |
| Average exposure | 37.34% |
| Turnover (1-way, per year) | 30.23 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -21.04% | 0.40 | 0.62 |
| E901-07 | -21.63% | 0.38 | 0.63 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | -9.82% |
| 2011 | -10.57% |
| 2012 | -10.33% |
| 2013 | -0.03% |
| 2014 | -3.35% |
| 2015 | -12.01% |
| 2016 | -11.62% |
| 2017 | -2.96% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 2013 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2017-12-29 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 51829.07 |
| equity_complete | pass | chart rows 2013 vs algorithm days 2013 |
| equity_matches_qc_tradeable_dates | pass | chart rows 2013 vs QuantConnect tradeableDates 2013 |
| no_leverage | pass | min cash/equity 0.037100; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 0 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=3.2692361674484425e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 6527 orders vs QuantConnect Total Orders 6527 |
| fills_match_harness_count | pass | downloaded fill events 6527 vs harness-recorded fills 6527 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 6527 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `d53421d77b8f283ae5f137cd4f84ed1cca431d7f81af02fe9a8b796c9b59323c`
- fills_sha256: `958981064de084e668c87782e7db8128d60083d55c448981cf43b15a2de7b3b9`
- trades_sha256: `345eac7d70f52c015d69610ce63fd50692360c966b79214c3dbba14da84a26f4`
