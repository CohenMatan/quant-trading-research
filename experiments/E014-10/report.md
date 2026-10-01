# E014-10 — S014 v1.1 (benchmark)

P2 control R random uptrend seed 1, exit B (same code, universe, slots, costs and exit as E014-02). Benchmark, never a candidate. Pre-declared in research/phase2/P2_spec.md (frozen, D094).

- **Status:** completed
- **Split:** DEV (2010-01-04 → 2021-12-31)
- **Commit:** `ae9469247dcb5e5c1bc19406d16c1cbf662c6efd` · **QC backtest:** `c61dec462f22ee3de4ce0052852e6381` · **LEAN:** v2.5.0.0.18131 · **run:** 2026-10-01T02:00:04Z · **runtime:** 1379s
- **Parameters:** `{'mode': 'rand', 'exit': 'B', 'limit': 126, 'rsi_pullback': 40, 'window': 5, 'rsi_recovery': 45, 'slots': 12, 'seed': 1}`
- **Costs:** `{'slippage_bps': 10, 'commission_model': 'fixed_per_order', 'commission_per_order': 7.0, 'note': 'D039: $7 per executed buy or sell order; slippage separate'}` · **Universe:** `{'min_market_cap': 2000000000.0, 'min_price': 5.0, 'min_avg_dollar_volume': 5000000.0, 'adv_days': 20}` · **Portfolio:** `{'max_position_weight': 0.1, 'cash_buffer': 0.02, 'min_position_usd': 5000, 'max_positions': 15, 'buy_funding': 'settled_cash_only', 'gap_reserve': 0.15}`

## Metrics

| Metric | Value |
|---|---|
| Period | 2010-01-04 → 2021-12-31 (3021 trading days) |
| CAGR | 12.43% |
| Annualised volatility | 16.05% |
| Sharpe (rf = 0) | 0.81 |
| Sortino | 1.13 |
| Max drawdown | -28.50% |
| Longest drawdown (trading days) | 569 |
| Calmar | 0.44 |
| Worst year | -10.24% |
| Worst month | -10.29% |
| Closed trades | 492 |
| Win rate | 41.26% |
| Average winner | 19.56% |
| Average loser | -7.69% |
| Expectancy per trade | 3.56% |
| Profit factor | 1.56 |
| Average holding (calendar days) | 102.8 |
| Average exposure | 93.63% |
| Turnover (1-way, per year) | 3.16 |

## Relative to benchmarks

| Benchmark | Excess CAGR | Beta | Correlation |
|---|---|---|---|
| E900-07 | -2.16% | 0.76 | 0.79 |
| E901-07 | -1.05% | 0.72 | 0.80 |

## Calendar-year returns

| Year | Return |
|---|---|
| 2010 | 20.87% |
| 2011 | 9.60% |
| 2012 | 9.42% |
| 2013 | 37.54% |
| 2014 | 5.16% |
| 2015 | 10.55% |
| 2016 | 19.75% |
| 2017 | 12.93% |
| 2018 | -10.24% |
| 2019 | 18.37% |
| 2020 | 16.42% |
| 2021 | 5.09% |

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
| no_leverage | pass | min cash/equity 0.024223; 0 closes with negative cash |
| fills_after_signal_date | pass | 0 violations, 15 LEAN-generated fills |
| fills_within_dates | pass | fill dates inside the backtest window |
| harness_timing_selfcheck | pass | violations=0 max_fill_dev=2.6887609956713753e-16 |
| harness_no_short | pass | negative_qty=0 |
| no_invalid_orders | pass | invalid=0 |
| summary_present | pass | QRSUMMARY log line parsed |
| orders_download_complete | pass | downloaded 998 orders vs QuantConnect Total Orders 998 |
| fills_match_harness_count | pass | downloaded fill events 996 vs harness-recorded fills 996 |
| no_stale_open_orders | pass | 0 orders still open more than 10 days before the end: [] |
| harness_no_stale_open_orders | pass | harness orders open > 5 sessions at the end: 0 |
| no_unresolved_stale_holdings | pass | held positions without a real price bar that the fallback could not close: 0 |
| windows_restored | pass | 0 holdings found without a price window and restored |
| stale_exits | pass | 0 holdings taken out at their last real close after > 10 sessions without data (D059 fallback): 0 mirrored |
| commission_fixed_per_order | pass | 996 executed orders; 0 not charged exactly $7 |

## Result hashes (SHA-256 of canonical CSV)

- equity_sha256: `9869cb9edaed03da99167b8b2efa53decf51cd534d801cea603963065893b554`
- fills_sha256: `01ddcc620a90a054db077a08e8b392f3f0851054135c456c284ce3f544d732ca`
- trades_sha256: `9d02778bc2bb5c48d8691ff81a4ea602250536e6854d4c07909309e15ef15e4a`
