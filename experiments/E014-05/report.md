# E014-05 — S014 v1.0 (benchmark)

P2 control R random uptrend seed 1, exit A (same code, universe, slots, costs and exit as E014-01). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `f215a9a319957829bace622591d08ef59dabf845` · **QC backtest:** `fa422508e500ae637cf9ac3bb11bfd38` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T00:11:05Z · **runtime:** 1335s
- **Parameters:** `{'mode': 'rand', 'exit': 'A', 'limit': 63, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 10.39% |
| Annualised volatility | 16.70% |
| Sharpe (rf = 0) | 0.68 |
| Sortino | 0.92 |
| Max drawdown | -28.05% |
| Longest drawdown (trading days) | 552 |
| Calmar | 0.37 |
| Worst year | -10.41% |
| Worst month | -12.59% |
| Closed trades | 351 |
| Win rate | 39.03% |
| Average winner | 22.61% |
| Average loser | -7.27% |
| Expectancy per trade | 4.39% |
| Profit factor | 1.56 |
| Average holding (calendar days) | 143.8 |
| Average exposure | 94.40% |
| Turnover (1-way, per year) | 2.15 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -4.19% | 0.80 | 0.79 |
| E901-07 | -3.09% | 0.73 | 0.78 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 20.23% |
| 2011 | 18.72% |
| 2012 | 10.67% |
| 2013 | 45.31% |
| 2014 | 1.49% |
| 2015 | 5.63% |
| 2016 | 4.03% |
| 2017 | 16.92% |
| 2018 | -10.41% |
| 2019 | 19.29% |
| 2020 | 2.92% |
| 2021 | -0.61% |

## Integrity checks

| Check | Result | Detail |
|---|---|---|
| equity_nonempty | pass | 3021 rows |
| equity_dates_increasing | pass | strictly increasing dates |
| equity_within_dates | pass | 2010-01-04..2021-12-31 |
| equity_no_nan | pass | no missing values |
| equity_positive | pass | min 96901.20 |
| equity_complete | pass | chart rows 3021 vs algorithm days 3021 |
| equity_matches_qc_tradeable_dates | pass | chart rows 3021 vs QuantConnect tradeableDates 3021 |
| no_leverage | pass | min cash/equity 0.025035; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 12 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.6887609956713753e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 714 orders vs QuantConnect Total Orders 714 |
| fills_match_harness_count | pass | downloaded fill events 714 vs harness-recorded fills 714 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 714 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `c124317f518e53c97fe63a1321265875b53123338812da6b7a4cc02aaaf18473`
- fills_sha256: `f7fbf0f479bf137b4f84e8393ee3fcef2956561457cee54331f8a10b8e722d9f`
- trades_sha256: `c60c580436d49e35db2aee8c8d3969be27d7b6af23301a71943ca612004e598a`
